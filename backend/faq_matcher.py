"""Lightweight FAQ matcher — keyword-first scoring + fuzzy refinement.

No LLM or embedding model required. Designed for sub-millisecond matching
on CPU so Tier 1 responses feel instant.

Scoring strategy:
  - Keywords carry the primary signal (65%) — each FAQ has expanded intent
    words and common paraphrase synonyms. A keyword hit is a strong
    indicator of user intent.
  - Fuzzy string similarity is secondary (35%) — it catches near-exact
    phrasings but under-matches paraphrases, so it is down-weighted.
  - A borderline band (0.35–0.50) routes to Tier 2 (LLM) rather than
    risking a wrong FAQ match — precision > recall for Tier 1.
"""

from __future__ import annotations

import re
from difflib import SequenceMatcher

from faq_data import FAQ_DB

# ── Tuning knobs ──────────────────────────────────────────────────────
MATCH_THRESHOLD = 0.50        # scores >= this → confident FAQ match
BORDERLINE_LOW  = 0.35        # scores in [0.35, 0.50) → fall to LLM
KEYWORD_WEIGHT  = 0.65        # keywords are the primary paraphrase signal
FUZZY_WEIGHT    = 0.35        # fuzzy catches exact/near-exact phrasings

# ── Stopwords stripped from queries before keyword matching ────────────
_STOP = frozenset({
    "i", "me", "my", "we", "our", "you", "your", "a", "an", "the",
    "is", "are", "was", "were", "be", "been", "being", "do", "does",
    "did", "have", "has", "had", "will", "would", "can", "could",
    "shall", "should", "may", "might", "must", "to", "of",
    "in", "on", "at", "by", "for", "with", "from", "up", "about",
    "into", "over", "after", "before", "between", "during", "and",
    "or", "but", "not", "so", "if", "then", "than", "too", "very",
    "just", "that", "this", "it", "its", "also", "only", "how",
    "what", "when", "where", "which", "who", "whom", "why", "need",
})


def _tokenize(text: str) -> list[str]:
    """Lowercase, strip punctuation, split into word tokens."""
    return re.findall(r"[a-z0-9]+", text.lower())


def _stem(word: str) -> str:
    """Aggressive suffix stripping for better matching of plural/verb forms.

    Covers common English morphology without a full stemmer:
      medicines → medicine, appointments → appointment, tracking → track, ...
    """
    w = word.lower()
    for suffix in ("ation", "tion", "ment", "ness", "ible", "able",
                    "ies", "ous", "ive", "ing", "ful", "ers", "ist",
                    "ity", "ent", "ant", "ual", "ual", "ly", "ed",
                    "er", "es", "s"):
        if w.endswith(suffix) and len(w) - len(suffix) >= 3:
            return w[:-len(suffix)]
    return w


def _kw_score(query_lower: str, query_tokens: set[str], keywords: list[str]) -> float:
    """Keyword scoring based on hit count with fuzzy single-word matching.

    Uses exact token matching for single words (with stem normalisation)
    and substring matching for multi-word phrases.

    Returns value in [0.0, 1.0]:
      0 hits → 0.0,  1 hit → 0.40,  2 hits → 0.70,  3+ hits → 1.0
    """
    if not keywords:
        return 0.0

    hits = 0
    query_stems = {_stem(t) for t in query_tokens}

    for kw in keywords:
        kw_lower = kw.lower().strip()
        parts = kw_lower.split()
        if len(parts) == 1:
            # Single word — exact token match only (stem matching is too
            # aggressive for single words and causes false positives)
            if kw_lower in query_tokens:
                hits += 1
        else:
            # Multi-word phrase — check substring in query, or all parts
            # present (with stem matching for each part)
            if kw_lower in query_lower:
                hits += 1
            elif all(p in query_tokens or _stem(p) in query_stems for p in parts):
                hits += 1

    if hits == 0:
        return 0.0
    # Scale: 1 hit = 0.40, 2 hits = 0.70, 3+ = 1.0
    return min(1.0, 0.10 + 0.30 * hits)


def match(query: str, industry: str) -> dict | None:
    """Return the best FAQ match for *query* within *industry*, or None.

    Scoring:
      1. Keyword overlap (65%) — how many FAQ keywords appear in the query.
         Keywords are expanded with synonyms/paraphrases and stem-matched,
         so even a single hit is a strong intent signal.
      2. Fuzzy string similarity (35%) — SequenceMatcher ratio against
         stored question phrasings. Catches near-exact matches.

    Borderline scores (0.35–0.50) are NOT returned as FAQ matches.
    They fall through to Tier 2 (LLM) to avoid wrong matches —
    precision matters more than recall at Tier 1.
    """
    faqs = FAQ_DB.get(industry)
    if not faqs:
        return None

    query_lower = query.lower().strip()
    query_tokens = set(_tokenize(query_lower))

    best_score = 0.0
    best_faq: dict | None = None

    for faq in faqs:
        # ── Keyword overlap score (0.0 – 1.0) ────────────────────────────
        kw = faq.get("keywords", [])
        kw_s = _kw_score(query_lower, query_tokens, kw)

        # ── Fuzzy question match (0.0 – 1.0) ─────────────────────────────
        fuzzy_best = 0.0
        for q in faq.get("questions", []):
            ratio = SequenceMatcher(None, query_lower, q.lower()).ratio()
            if ratio > fuzzy_best:
                fuzzy_best = ratio

        # ── Combined score — keywords weighted higher ─────────────────────
        score = KEYWORD_WEIGHT * kw_s + FUZZY_WEIGHT * fuzzy_best

        if score > best_score:
            best_score = score
            best_faq = faq

    # ── Confidence gate ───────────────────────────────────────────────
    if best_score >= MATCH_THRESHOLD and best_faq is not None:
        return best_faq

    return None
