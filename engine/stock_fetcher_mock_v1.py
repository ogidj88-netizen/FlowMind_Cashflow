#!/usr/bin/env python3
"""
FlowMind Cashflow
Stock Fetcher MOCK v1 (SAFE)

Input:
- argv[1] = PROJECT_ID

Reads/Writes:
- projects/<PROJECT_ID>/ASSET_MANIFEST.json  (in-place update, deterministic)

Behavior:
- Does NOT download anything.
- For each item with status PENDING:
  - sets status=FOUND
  - sets selected = mock record with provider + query + mock_url
  - leaves placeholders as-is

Exit:
- PASS => 0
- FAIL => 1
"""

import os
import sys
import json
import hashlib
from datetime import datetime

BASE_DIR = "projects"


def project_dir(project_id: str) -> str:
    return os.path.join(BASE_DIR, project_id)


def manifest_path(project_id: str) -> str:
    return os.path.join(project_dir(project_id), "ASSET_MANIFEST.json")


def fail(msg: str) -> int:
    print(f"[STOCK_MOCK FAIL] {msg}")
    return 1


def deterministic_pick(project_id: str, scene_id: str, queries: list, providers: list):
    q = queries[0] if queries else "generic finance b roll"
    p = providers[0] if providers else "pexels"
    h = hashlib.md5(f"{project_id}:{scene_id}:{q}:{p}".encode("utf-8")).hexdigest()[:10]
    mock_url = f"mock://{p}/{h}"
    return p, q, mock_url, h


def main(argv) -> int:
    if len(argv) < 2:
        print("Usage: python -m engine.stock_fetcher_mock_v1 <PROJECT_ID>")
        return 1

    project_id = argv[1].strip()
    if not project_id:
        return fail("Empty PROJECT_ID")

    mp = manifest_path(project_id)
    if not os.path.exists(mp):
        return fail(f"Missing ASSET_MANIFEST.json at: {mp}")

    try:
        with open(mp, "r", encoding="utf-8") as f:
            man = json.load(f)
    except Exception as e:
        return fail(f"Invalid ASSET_MANIFEST.json: {e}")

    items = man.get("items")
    if not isinstance(items, list) or not items:
        return fail("items missing or empty")

    changed = 0
    for it in items:
        status = it.get("status")
        if status != "PENDING":
            continue

        scene_id = it.get("scene_id") or "unknown"
        providers = it.get("provider_order") or ["pexels", "pixabay"]
        queries = it.get("queries") or []

        provider, query, mock_url, asset_id = deterministic_pick(project_id, scene_id, queries, providers)

        it["status"] = "FOUND"
        it["selected"] = {
            "provider": provider,
            "query": query,
            "asset_id": asset_id,
            "mock_url": mock_url,
            "picked_at": datetime.utcnow().isoformat() + "Z",
            "downloaded": False,
        }
        changed += 1

    man["mock_mode"] = True
    man["updated_at"] = datetime.utcnow().isoformat() + "Z"
    man["stats"] = {
        "found_now": changed,
        "total_items": len(items),
        "pending_remaining": len([x for x in items if x.get("status") == "PENDING"]),
    }

    with open(mp, "w", encoding="utf-8") as f:
        json.dump(man, f, indent=2, ensure_ascii=False)

    print(f"[STOCK_MOCK PASS] found_now={changed} updated: {mp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
