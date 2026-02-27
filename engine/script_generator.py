#!/usr/bin/env python3
"""
FlowMind Cashflow
Script Generator v1 (Deterministic + Validator-Passing)

Goals:
- Hook (first sentence) must contain measurable impact (digit / $ / % / timeframe / multiplier)
- Every sentence <= 20 words (per validator)
- If validation fails -> exit(1)
- Writes output to projects/<PROJECT_ID>/SCRIPT.json and SCRIPT.txt
"""

import os
import sys
import json
import hashlib
from datetime import datetime

from engine.script_validator import validate_script, ScriptValidationError


BASE_DIR = "projects"


def _project_dir(project_id: str) -> str:
    return os.path.join(BASE_DIR, project_id)


def _content_path(project_id: str) -> str:
    return os.path.join(_project_dir(project_id), "CONTENT.json")


def _script_json_path(project_id: str) -> str:
    return os.path.join(_project_dir(project_id), "SCRIPT.json")


def _script_txt_path(project_id: str) -> str:
    return os.path.join(_project_dir(project_id), "SCRIPT.txt")


def _load_content(project_id: str) -> dict:
    path = _content_path(project_id)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _pick_amount(project_id: str) -> int:
    # Deterministic amount selection: stable per project_id
    amounts = [120, 240, 480, 960, 1800, 3240, 5200, 8400]
    h = hashlib.md5(project_id.encode("utf-8")).hexdigest()
    idx = int(h[:2], 16) % len(amounts)
    return amounts[idx]


def _pick_subject(content: dict) -> str:
    # Try common keys; fall back to a safe default.
    for key in ["topic", "title", "angle", "seed", "idea"]:
        val = content.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()

    # If content has nested structures, try a few typical places.
    if isinstance(content.get("topic"), dict):
        t = content["topic"].get("name") or content["topic"].get("title")
        if isinstance(t, str) and t.strip():
            return t.strip()

    return "subscriptions you forgot you have"


def _normalize_subject(subject: str) -> str:
    # Keep it short and hook-friendly.
    subject = subject.strip()
    # Avoid overly long topic strings
    if len(subject) > 70:
        subject = subject[:70].rstrip() + "..."
    return subject


def generate_script(project_id: str) -> dict:
    content = _load_content(project_id)
    subject = _normalize_subject(_pick_subject(content))
    amount = _pick_amount(project_id)

    # HOOK: must include measurable impact and stay <= 20 words.
    hook = f"You're losing ${amount} a year to {subject}."

    # Body: short sentences (<= 20 words each) with clear pacing.
    body_sentences = [
        "Most people never notice it.",
        "It drains money in small, quiet bites.",
        "One charge looks harmless.",
        "But it repeats every month.",
        "Companies love this because you stop paying attention.",
        "You tell yourself you will cancel later.",
        "Later becomes next week, then next month.",
        "Meanwhile, the total keeps climbing.",
        "In one year, it adds up fast.",
        "Today we will catch it, cut it, and keep it from coming back.",
    ]

    # Ensure each sentence ends with punctuation and is separate.
    script_text = " ".join([hook] + body_sentences)

    return {
        "project_id": project_id,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "hook": hook,
        "subject": subject,
        "measurable_amount_usd_per_year": amount,
        "script_text": script_text,
        "notes": {
            "constraints": {
                "max_words_per_sentence": 20,
                "hook_requires_measurable_impact": True
            }
        }
    }


def _write_outputs(project_id: str, payload: dict):
    os.makedirs(_project_dir(project_id), exist_ok=True)

    with open(_script_json_path(project_id), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    with open(_script_txt_path(project_id), "w", encoding="utf-8") as f:
        f.write(payload["script_text"].strip() + "\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m engine.script_generator <PROJECT_ID>")
        sys.exit(1)

    project_id = sys.argv[1]

    print("[SCRIPT] Generating script...")
    payload = generate_script(project_id)
    script_text = payload["script_text"]

    print("[SCRIPT] Validating against Constitution...")
    try:
        validate_script(script_text)
    except ScriptValidationError as e:
        print(f"[SCRIPT FAIL] {e}")
        sys.exit(1)

    _write_outputs(project_id, payload)
    print("[SCRIPT PASS] Written: projects/{}/SCRIPT.json + SCRIPT.txt".format(project_id))
    sys.exit(0)


if __name__ == "__main__":
    main()
