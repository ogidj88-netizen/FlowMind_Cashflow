#!/usr/bin/env python3
"""
FlowMind Cashflow
Asset Requests v1.1 (Stock-first planning + keyword sanitization)

Input:
- argv[1] = PROJECT_ID

Reads:
- projects/<PROJECT_ID>/SCENE_PLAN.json

Writes:
- projects/<PROJECT_ID>/ASSET_REQUESTS.json

No external APIs here. Deterministic query builder.
"""

import os
import sys
import json
import re
from datetime import datetime

BASE_DIR = "projects"

STOP_TOKENS = {
    # pronouns / helpers / filler
    "you", "your", "you're", "youre", "we", "our", "they", "their", "them", "i", "me",
    "this", "that", "these", "those", "because", "today", "later", "never", "most", "people",
    "then", "into", "from", "with", "over", "just", "been", "when", "what", "where", "why", "how",
    "and", "the", "a", "an", "to", "of", "in", "on", "it", "is", "are", "was", "be", "as", "at", "or", "but",
    # generic finance words that are too broad alone
    "money", "cost", "costs", "pay", "paying", "payment", "lose", "losing", "drain", "draining", "year", "years", "month", "months"
}


def project_dir(project_id: str) -> str:
    return os.path.join(BASE_DIR, project_id)


def scene_plan_path(project_id: str) -> str:
    return os.path.join(project_dir(project_id), "SCENE_PLAN.json")


def out_path(project_id: str) -> str:
    return os.path.join(project_dir(project_id), "ASSET_REQUESTS.json")


def fail(msg: str) -> int:
    print(f"[ASSETS FAIL] {msg}")
    return 1


def sanitize_keywords(keywords):
    if not isinstance(keywords, list):
        return []

    clean = []
    seen = set()
    for k in keywords:
        if not isinstance(k, str):
            continue
        t = k.strip().lower()
        if not t:
            continue
        # keep only letters/numbers/apostrophe -> then drop apostrophe variants
        t = re.sub(r"[^a-z0-9']+", "", t)
        t = t.replace("'", "")
        if len(t) < 3:
            continue
        if t in STOP_TOKENS:
            continue
        if t in seen:
            continue
        seen.add(t)
        clean.append(t)
        if len(clean) >= 6:
            break
    return clean


def build_queries(label: str, keywords: list) -> list:
    # Deterministic, stock-friendly phrases (English).
    base = {
        "hook": [
            "credit card payment close up",
            "bank app balance screen",
            "recurring payment notification"
        ],
        "problem": [
            "subscription bill invoice",
            "bank statement scrolling",
            "overdraft fee warning"
        ],
        "mechanism": [
            "auto renewal settings screen",
            "subscription management menu",
            "billing cycle calendar close up"
        ],
        "why_it_happens": [
            "busy life time lapse city",
            "email inbox clutter scrolling",
            "phone notifications overload"
        ],
        "stakes": [
            "empty wallet close up",
            "rent due calendar",
            "stress looking at expenses"
        ],
        "promise": [
            "cancel subscription button",
            "budget spreadsheet simple",
            "relief after saving money"
        ],
    }

    seed = base.get(label, ["finance b roll", "mobile banking app", "payment notification"])

    kw = sanitize_keywords(keywords)
    extra = []
    for k in kw[:3]:
        # safer templates for stock search
        extra.append(f"{k} app interface")
        extra.append(f"{k} invoice")
        extra.append(f"{k} notification")

    # Deduplicate preserving order
    out = []
    seen = set()
    for q in seed + extra:
        qn = q.strip().lower()
        if not qn or qn in seen:
            continue
        seen.add(qn)
        out.append(q)
        if len(out) >= 10:
            break
    return out


def main(argv) -> int:
    if len(argv) < 2:
        print("Usage: python -m engine.asset_requests_v1 <PROJECT_ID>")
        return 1

    project_id = argv[1].strip()
    if not project_id:
        return fail("Empty PROJECT_ID")

    sp = scene_plan_path(project_id)
    if not os.path.exists(sp):
        return fail(f"Missing SCENE_PLAN.json at: {sp}")

    try:
        with open(sp, "r", encoding="utf-8") as f:
            plan = json.load(f)
    except Exception as e:
        return fail(f"Invalid SCENE_PLAN.json: {e}")

    scenes = plan.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        return fail("No scenes found")

    requests = []
    for s in scenes:
        scene_id = s.get("scene_id")
        label = (s.get("label") or "generic").strip()
        text = (s.get("text") or "").strip()
        keywords = s.get("keywords") or []
        queries = build_queries(label, keywords)

        requests.append({
            "scene_id": scene_id,
            "label": label,
            "intent": "stock_video",
            "queries": queries,
            "must_avoid": ["faces closeup", "logos", "brand names", "explicit gore", "nudity"],
            "notes": {"scene_text": text[:180]},
        })

    payload = {
        "project_id": project_id,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "source": {"scene_plan": sp},
        "provider_order": ["pexels", "pixabay"],
        "requests": requests,
        "safe_mode": True,
        "version": "v1.1_sanitized",
    }

    os.makedirs(project_dir(project_id), exist_ok=True)
    with open(out_path(project_id), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"[ASSETS PASS] Written: {out_path(project_id)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
