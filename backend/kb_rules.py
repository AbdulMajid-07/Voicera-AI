"""Keyword-matched front-desk responses (Python port of frontend/src/kb.js).

Used as a fallback when Ollama is unavailable.  The frontend kb.js remains the
authoritative copy for the browser-side fallback path.
"""

from __future__ import annotations

import re

GREETING = (
    "Hi, I'm NORBEAI, your AI front desk. Ask me about business hours, "
    "appointments, or anything else — I'll answer right here, out loud."
)

_RULES: list[tuple[list[str], str]] = [
    (
        ["hours", "open", "close", "when are you open", "timing"],
        "We're open Monday to Friday, eight a.m. to six p.m., and Saturdays from "
        "nine to one. After hours I answer every call, take a message, or book an "
        "appointment for the next business day.",
    ),
    (
        ["appointment", "book", "booking", "reserve", "slot", "schedule",
         "meet the doctor", "see the doctor"],
        "Booking is easy. Tell me your preferred day and time and I'll check the "
        "calendar, grab a slot, and confirm it right here by voice. What day works "
        "best for you?",
    ),
    (
        ["price", "pricing", "cost", "how much", "plan", "month", "trial", "free"],
        "Pilot plans start well below the cost of a single missed customer. In this "
        "demo I'll connect you with the team for exact numbers — a seven-day pilot "
        "is free.",
    ),
    (
        ["language", "spanish", "french", "hindi", "english", "multilingual",
         "languages"],
        "Absolutely. I detect the caller's language and reply in all major Indian "
        "languages. Right now I'm speaking English, but the real assistant switches "
        "fluently.",
    ),
    (
        ["message", "leave a message", "voicemail", "call back", "someone"],
        "No problem. I'll take your name and number and make sure the right person "
        "gets your message. Who should I say is calling?",
    ),
    (
        ["hello", "hi ", "hey", "good morning", "good afternoon", "good evening",
         "who are you", "help", "what can you do", "start", "demo", "test"],
        "Hello! I'm NORBEAI, your voice front desk. I can share business hours, "
        "book appointments, answer questions, and take messages. What would you "
        "like to know?",
    ),
]

_FALLBACK = (
    "Great question. In this demo I know about our hours, appointments, pricing, "
    "languages, and taking messages. For anything else I'd route you to the right "
    "human. Try another question, or pick a suggestion below the mic."
)


def ANSWER(text: str) -> str:
    """Return a keyword-matched reply, mirroring kb.js answer() behaviour."""
    lower = text.lower()
    for keys, reply in _RULES:
        if any(key in lower for key in keys):
            return reply
    return _FALLBACK
