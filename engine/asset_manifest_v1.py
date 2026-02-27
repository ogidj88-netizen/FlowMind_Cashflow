#!/usr/bin/env python3
"""
FlowMind Cashflow
Asset Manifest v1 (No download, deterministic placeholders)

Input:
- argv[1] = PROJECT_ID

Reads:
- projects/<PROJECT_ID>/ASSET_REQUESTS.json

Writes:
- projects/<PROJECT_ID>/ASSET_MANIFEST.json

Creates dirs (if missing):
- assets/cache/<PROJECT_ID>/
- assets/cache/<PROJECT_ID>/video/
- assets/cache/<PROJECT_ID>/image/
"""

import os
import sys
import json
from datetime import datetime

BASE_DIR = "projects"
CACHE_ROOT = os.path.join("assets", "cache")


def project_dir(project_id: str) -> str:
    return os.path.join(BASE_DIR, project_id)


def asset_requests_path(project_id: str) -> str:
    return os.path.join(project_dir(project_id), "ASSET_REQUESTS.json")


def manifest_path(project_id: str) -> str:
    return os.path.join(project_dir(project_id), "ASSET_MANIFEST.json")


def ensure_dirs(project_id: str):
    base = os.path.join(CACHE_ROOT, project_id)
    os.makedirs(os.path.join(base, "video"), exist_ok=True)
    os.makedirs(os.path.join(base, "image"), exist_ok=True)
    return base


def fail(msg: str) -> int:
    print(f"[ASSET_MANIFEST FAIL] {msg}")
    return 1


def main(argv) -> int:
    if len(argv) < 2:
        print("Usage: python -m engine.asset_manifest_v1 <PROJECT_ID>")
        return 1

    project_id = argv[1].strip()
    if not project_id:
        return fail("Empty PROJECT_ID")

    ar = asset_requests_path(project_id)
    if not os.path.exists(ar):
        return fail(f"Missing ASSET_REQUESTS.json at: {ar}")

    try:
        with open(ar, "r", encoding="utf-8") as f:
            req = json.load(f)
    except Exception as e:
        return fail(f"Invalid ASSET_REQUESTS.json: {e}")

    requests = req.get("requests")
    if not isinstance(requests, list) or not requests:
        return fail("requests missing or empty")

    cache_base = ensure_dirs(project_id)

    items = []
    for r in requests:
        scene_id = r.get("scene_id")
        label = r.get("label")
        queries = r.get("queries") or []
        intent = r.get("intent") or "stock_video"

        if not scene_id:
            return fail("scene_id missing in requests")

        # Deterministic placeholders: one primary video per scene
        video_rel = os.path.join("assets", "cache", project_id, "video", f"{scene_id}.mp4")
        image_rel = os.path.join("assets", "cache", project_id, "image", f"{scene_id}.jpg")

        items.append({
            "scene_id": scene_id,
            "label": label,
            "intent": intent,
            "provider_order": req.get("provider_order", ["pexels", "pixabay"]),
            "queries": queries,
            "status": "PENDING",
            "selected": None,
            "placeholders": {
                "video_path": video_rel,
                "image_path": image_rel
            },
            "cache_policy": {
                "avoid_repeats": True,
                "min_duration_sec": 5,
                "target_duration_sec": 8
            }
        })

    manifest = {
        "project_id": project_id,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "source": {"asset_requests": ar},
        "cache_base": cache_base,
        "items": items,
        "safe_mode": True,
        "version": "v1_placeholders_only"
    }

    os.makedirs(project_dir(project_id), exist_ok=True)
    with open(manifest_path(project_id), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"[ASSET_MANIFEST PASS] Written: {manifest_path(project_id)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
