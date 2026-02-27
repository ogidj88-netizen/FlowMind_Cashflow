#!/usr/bin/env python3
"""
FlowMind Cashflow
Script Validator v1 (Cashflow Canon)

Hard rules:
- Every sentence <= 20 words
- Hook (first sentence) must contain measurable impact:
  digit OR $, %, year(s), month(s), day(s), times, double, triple
"""

import re


class ScriptValidationError(Exception):
    pass


MAX_WORDS = 20

MEASURABLE_PATTERNS = [
    r"\d",
    r"\$",
    r"%",
    r"\byear\b|\byears\b",
    r"\bmonth\b|\bmonths\b",
    r"\bday\b|\bdays\b",
    r"\btimes\b",
    r"\bdouble\b",
    r"\btriple\b",
]


def _count_words(s: str) -> int:
    return len(s.strip().split())


def _has_measurable(text: str) -> bool:
    for pat in MEASURABLE_PATTERNS:
        if re.search(pat, text, flags=re.IGNORECASE):
            return True
    return False


def validate_script(script: str) -> bool:
    if not script or not script.strip():
        raise ScriptValidationError("Script is empty.")

    # Split into sentences; keep it simple and deterministic.
    sentences = [s.strip() for s in re.split(r"[.!?]", script) if s.strip()]

    if not sentences:
        raise ScriptValidationError("Script has no sentences.")

    # Sentence length rule
    for s in sentences:
        if _count_words(s) > MAX_WORDS:
            raise ScriptValidationError("Sentence exceeds 20 words.")

    # Hook rule (first sentence)
    hook = sentences[0]
    if not _has_measurable(hook):
        raise ScriptValidationError(
            "Hook must contain measurable impact (number, $, %, timeframe, multiplier)."
        )

    return True
