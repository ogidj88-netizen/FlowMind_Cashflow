#!/usr/bin/env python3
"""
FlowMind Cashflow
Assembly Plan v1 (deterministic)

Input:
- argv[1] = PROJECT_ID

Reads:
- projects/<PROJECT_ID>/SCENE_PLAN.json
- projects/<PROJECT_ID>/ASSET_MANIFEST.json

Writes:
- projects/<PROJECT_ID>/ASSEMBLY_PLAN.json

Notes:
- Audio is master clock later. For now we use estimated_seconds.
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


def asset_manifest_path(project_id: str) -> str:
    return os.path.join(project_dir(project_id), "ASSET_MANIFEST.json")


def out_path(project_id: str) -> str:
    return os.path.join(project_dir(project_id), "ASSEMBLY_PLAN.json")


def fail(msg: str) -> int:
    print(f"[ASSEMBLY_PLAN FAIL] {msg}")
    return 1


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main(argv) -> int:
    if len(argv) < 2:
        print("Usage: python -m engine.assembly_plan_v1 <PROJECT_ID>")
        return 1

    project_id = argv[1].strip()
    if not project_id:
        return fail("Empty PROJECT_ID")

    sp = scene_plan_path(project_id)
    am = asset_manifest_path(project_id)

    if not os.path.exists(sp):
        return fail(f"Missing SCENE_PLAN.json: {sp}")
    if not os.path.exists(am):
        return fail(f"Missing ASSET_MANIFEST.json: {am}")

    try:
        scene_plan = load_json(sp)
        asset_man = load_json(am)
    except Exception as e:
        return fail(f"JSON load error: {e}")

    scenes = scene_plan.get("scenes")
    items = asset_man.get("items")

    if not isinstance(scenes, list) or not scenes:
        return fail("SCENE_PLAN scenes missing/empty")
    if not isinstance(items, list) or not items:
        return fail("ASSET_MANIFEST items missing/empty")

    # Build lookup by scene_id
    item_by_scene = {it.get("scene_id"): it for it in items if it.get("scene_id")}

    timeline = []
    t = 0
    for s in scenes:
        scene_id = s.get("scene_id")
        label = s.get("label")
        est = s.get("estimated_seconds")

        if not scene_id:
            return fail("Scene missing scene_id")
        if not isinstance(est, int) or est <= 0:
            return fail(f"{scene_id} invalid estimated_seconds")

        it = item_by_scene.get(scene_id)
        if not it:
            return fail(f"Missing asset manifest item for scene_id={scene_id}")
        if it.get("status") != "FOUND":
            return fail(f"Asset not FOUND for scene_id={scene_id}")

        ph = it.get("placeholders") or {}
        video_path = ph.get("video_path")
        if not video_path:
            return fail(f"Missing placeholders.video_path for scene_id={scene_id}")

        start = t
        end = t + est
        t = end

        timeline.append({
            "scene_id": scene_id,
            "label": label,
            "start_sec": start,
            "end_sec": end,
            "duration_sec": est,
            "video_path": video_path,
            "selected": it.get("selected"),
            "text_hint": (s.get("text") or "")[:140],
        })

    plan = {
        "project_id": project_id,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "source": {
            "scene_plan": sp,
            "asset_manifest": am,
        },
        "video_spec": {
            "width": 1920,
            "height": 1080,
            "fps": 30,
            "format": "mp4",
        },
        "timeline": timeline,
        "total_duration_sec": t,
        "safe_mode": True,
        "version": "v1_estimated_clock",
    }

    os.makedirs(project_dir(project_id), exist_ok=True)
    with open(out_path(project_id), "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)

    print(f"[ASSEMBLY_PLAN PASS] total_duration_sec={t} written: {out_path(project_id)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
