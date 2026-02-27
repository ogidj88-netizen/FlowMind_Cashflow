#!/usr/bin/env python3
"""
FlowMind Cashflow
Scene Plan QA Gate (PASS/FAIL)

Input:
- argv[1] = PROJECT_ID
Reads:
- projects/<PROJECT_ID>/SCENE_PLAN.json
Writes:
- projects/<PROJECT_ID>/SCENE_PLAN_QA.json

Rules (minimal strict):
- scenes >= 5
- each scene has non-empty text
- each scene has keywords (>=2)
- estimated_seconds in [4..20]
- total_estimated_seconds in [30..600]
"""

import os
import sys
import json
from datetime import datetime

BASE_DIR = "projects"


def project_dir(project_id: str) -> str:
    return os.path.join(BASE_DIR, project_id)


def scene_plan_path(project_id: str) -> str:
    return os.path.join(project_dir(project_id), "SCENE_PLAN.json")


def qa_out_path(project_id: str) -> str:
    return os.path.join(project_dir(project_id), "SCENE_PLAN_QA.json")


def fail(msg: str) -> int:
    print(f"[SCENE_QA FAIL] {msg}")
    return 1


def main(argv) -> int:
    if len(argv) < 2:
        print("Usage: python -m engine.scene_plan_qa <PROJECT_ID>")
        return 1

    project_id = argv[1].strip()
    if not project_id:
        return fail("Empty PROJECT_ID")

    path = scene_plan_path(project_id)
    if not os.path.exists(path):
        return fail(f"Missing SCENE_PLAN.json at: {path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            plan = json.load(f)
    except Exception as e:
        return fail(f"Invalid JSON: {e}")

    scenes = plan.get("scenes")
    if not isinstance(scenes, list):
        return fail("scenes is not a list")

    if len(scenes) < 5:
        return fail("Too few scenes (<5)")

    total = 0
    issues = []

    for i, s in enumerate(scenes, start=1):
        text = (s.get("text") or "").strip()
        if not text:
            issues.append(f"scene#{i} missing text")

        keywords = s.get("keywords")
        if not isinstance(keywords, list) or len([k for k in keywords if str(k).strip()]) < 2:
            issues.append(f"scene#{i} keywords <2")

        sec = s.get("estimated_seconds")
        if not isinstance(sec, int):
            issues.append(f"scene#{i} estimated_seconds not int")
            continue

        if sec < 4 or sec > 20:
            issues.append(f"scene#{i} estimated_seconds out of range (4..20): {sec}")

        total += sec

    if total < 30 or total > 600:
        issues.append(f"total_estimated_seconds out of range (30..600): {total}")

    verdict = {
        "project_id": project_id,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "input": {"scene_plan": path},
        "pass": len(issues) == 0,
        "total_estimated_seconds": total,
        "issues": issues,
    }

    os.makedirs(project_dir(project_id), exist_ok=True)
    with open(qa_out_path(project_id), "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2, ensure_ascii=False)

    if issues:
        print("[SCENE_QA FAIL] Issues found:")
        for it in issues:
            print(" - " + it)
        return 1

    print(f"[SCENE_QA PASS] total_estimated_seconds={total} written: {qa_out_path(project_id)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
