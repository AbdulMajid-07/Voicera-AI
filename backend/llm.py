"""Lightweight Ollama client for the NORBEAI chat pipeline.

Provides both streaming and non-streaming chat generation, plus a
sentence-level tokenizer used to split LLM output for progressive
TTS synthesis.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from typing import Generator

OLLAMA_BASE_URL = "http://localhost:11434"

# ── Industry-scoped system prompts ───────────────────────────────────────────
# Each prompt restricts the LLM to a specific role and scope. The Tier 3
# decline instruction is baked into every prompt so the LLM always prefers
# honesty over fabrication.

_HOSPITAL_PROMPT = """\
You are NORBEAI, the AI front-desk assistant at a hospital.

Your scope:
- General hospital information: visiting hours, directions inside the building, parking, cafeteria, pharmacy hours.
- How to book appointments, what to bring, what to expect.
- General descriptions of departments and specialties.
- Emergency contact numbers and basic first-aid guidance.
- General insurance and billing process questions.

Rules:
- Answer concisely in 2-3 short sentences (30-45 words max).
- Be warm, professional, and reassuring — like a helpful hospital receptionist.
- Never fabricate specific facts: do not invent doctor names, prices, room numbers, test results, or specific medical advice.
- If you do not know the answer to a specific question, you MUST say exactly: "I'm sorry, I don't have that information right now. Would you like me to connect you with someone who can help?"
- Never mention being an AI, a language model, or any technology.
- Speak in plain, conversational English — as if speaking on the phone.
- Never use bullet points, markdown, or special characters.
"""

_ENTERPRISE_PROMPT = """\
You are NORBEAI, the AI front-desk assistant for a technology company.

Your scope:
- Business hours, office locations, and contact information.
- Overview of services and solutions offered.
- General pricing and quote inquiry process.
- Scheduling demos, meetings, and consultations.
- Technical support basics: how to raise tickets, account access issues.
- Partnership, careers, and general company information.

Rules:
- Answer concisely in 2-3 short sentences (30-45 words max).
- Be professional, knowledgeable, and helpful — like a corporate receptionist.
- Never fabricate specific facts: do not invent prices, contract terms, employee names, or specific product features you are unsure about.
- If you do not know the answer to a specific question, you MUST say exactly: "I'm sorry, I don't have that information right now. Would you like me to connect you with someone who can help?"
- Never mention being an AI, a language model, or any technology.
- Speak in plain, conversational English — as if speaking on the phone.
- Never use bullet points, markdown, or special characters.
"""

_STORE_PROMPT = """\
You are NORBEAI, the AI front-desk assistant at a retail store.

Your scope:
- Store hours, locations, and directions.
- Return, exchange, and refund policies.
- Order status, tracking, and delivery information.
- Product availability, sizing guidance, and stock queries.
- Payment methods, discounts, offers, and loyalty programs.
- Warranty information and gift wrapping.

Rules:
- Answer concisely in 2-3 short sentences (30-45 words max).
- Be friendly, upbeat, and helpful — like a helpful shop assistant.
- Never fabricate specific facts: do not invent prices, stock levels, specific product details, or promotional codes you are unsure about.
- If you do not know the answer to a specific question, you MUST say exactly: "I'm sorry, I don't have that information right now. Would you like me to connect you with someone who can help?"
- Never mention being an AI, a language model, or any technology.
- Speak in plain, conversational English — as if speaking on the phone.
- Never use bullet points, markdown, or special characters.
"""

_GENERIC_PROMPT = """\
You are NORBEAI, a professional, friendly AI front-desk assistant.

Rules:
- Answer concisely in 2-3 short sentences (30-45 words max).
- Be warm but efficient. Never use bullet points or markdown.
- If you do not know the answer, you MUST say exactly: "I'm sorry, I don't have that information right now. Would you like me to connect you with someone who can help?"
- Never mention being an AI, a language model, or any technology.
- Speak in plain, conversational English — as if speaking on the phone.
"""

INDUSTRY_PROMPTS: dict[str, str] = {
    "hospital": _HOSPITAL_PROMPT,
    "enterprise": _ENTERPRISE_PROMPT,
    "store": _STORE_PROMPT,
    "general": _GENERIC_PROMPT,
}

# ── Sentence tokenizer ────────────────────────────────────────────────────────
# Splits text into sentences for progressive TTS. Handles abbreviations like
# "Mr." / "Dr." / "U.S.A." by requiring a period followed by whitespace + a
# capital or end-of-text.

_SENTENCE_SPLIT_RE = re.compile(r"""
    (?<=[.!?])   # lookbehind: sentence-ending punctuation
    \s+          # one or more whitespace characters
    (?=[A-Z])    # lookahead: next sentence starts with uppercase
    |            #  — OR —
    (?<=[.!?])   # lookbehind: sentence-ending punctuation
    (?=\s*$)     # lookahead: end of string
""", re.VERBOSE)


def is_available() -> bool:
    """Check whether Ollama is reachable at the default address."""
    try:
        req = urllib.request.Request(
            f"{OLLAMA_BASE_URL}/api/tags",
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False


def is_model_available(model: str) -> bool:
    """Check whether a specific model is pulled and available."""
    try:
        req = urllib.request.Request(
            f"{OLLAMA_BASE_URL}/api/tags",
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            names = [m.get("name", "") for m in data.get("models", [])]
            # Ollama model names may include ":latest" suffix
            return model in names or f"{model}:latest" in names
    except Exception:
        return False


def generate(
    model: str,
    messages: list[dict],
    *,
    temperature: float = 0.5,
    max_tokens: int = 80,
) -> str:
    """Non-streaming chat generation. Returns the full response text."""
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        },
    }).encode()

    req = urllib.request.Request(
        f"{OLLAMA_BASE_URL}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = json.loads(resp.read())
    return body.get("message", {}).get("content", "").strip()


def stream(
    model: str,
    messages: list[dict],
    *,
    temperature: float = 0.5,
    max_tokens: int = 80,
) -> Generator[str, None, None]:
    """Streaming chat generation. Yields text tokens as they are produced."""
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "stream": True,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        },
    }).encode()

    req = urllib.request.Request(
        f"{OLLAMA_BASE_URL}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        for raw_line in resp:
            line = raw_line.strip()
            if not line:
                continue
            try:
                chunk = json.loads(line)
            except json.JSONDecodeError:
                continue
            token = chunk.get("message", {}).get("content", "")
            if token:
                yield token
            if chunk.get("done"):
                break


# ── Sentence-level streaming ──────────────────────────────────────────────────
# Accumulates tokens and yields complete sentences as they form, so the caller
# can start TTS synthesis on the first sentence while the LLM is still generating.

def stream_sentences(
    model: str,
    messages: list[dict],
    *,
    temperature: float = 0.5,
    max_tokens: int = 80,
) -> Generator[str, None, None]:
    """Yield complete sentences from a streaming LLM response.

    Each yielded string is a full sentence (ending with punctuation) that is
    ready to be passed to TTS.  The final chunk (if any) is the remaining text
    that didn't end with a sentence boundary.
    """
    buffer = ""
    for token in stream(model, messages, temperature=temperature, max_tokens=max_tokens):
        buffer += token
        # Try to split off complete sentences from the buffer
        parts = _SENTENCE_SPLIT_RE.split(buffer, maxsplit=1)
        if len(parts) == 2:
            yield parts[0].strip()
            buffer = parts[1]

    # Yield whatever remains (the last incomplete sentence)
    remaining = buffer.strip()
    if remaining:
        yield remaining


def build_messages(
    user_message: str,
    history: list[dict] | None = None,
    industry: str = "general",
) -> list[dict]:
    """Format the conversation for Ollama's /api/chat endpoint.

    Keeps at most the last 6 turns (12 entries = 6 user + 6 assistant messages)
    to stay within the LLM context window while preserving recent context.
    The system prompt is selected based on the industry.
    """
    system = INDUSTRY_PROMPTS.get(industry, _GENERIC_PROMPT)
    messages: list[dict] = [{"role": "system", "content": system}]

    if history:
        trimmed = history[-12:] if len(history) > 12 else history
        for turn in trimmed:
            role = turn.get("role", "user")
            content = turn.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": user_message})
    return messages
