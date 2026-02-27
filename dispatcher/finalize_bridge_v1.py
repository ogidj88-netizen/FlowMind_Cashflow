#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FlowMind Cashflow — Finalize Bridge v2 (STRICT)

READY_FOR_UPLOAD -> ARCHIVED

Terminal state.
No transition allowed from ARCHIVED.
Deterministic.
"""

import json
from pathlib import Path
from datetime import datetime, timezone


def _utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run(project_id: str):

    state_path = Path("projects") / project_id / "PROJECT_STATE.json"

    if not state_path.exists():
        print("[FINALIZE] PROJECT_STATE missing")
        return

    state = json.loads(state_path.read_text())
    phase = state.get("phase")

    if phase == "ARCHIVED":
        print("[FINALIZE] Already ARCHIVED")
        return

    if phase != "READY_FOR_UPLOAD":
        print("[FINALIZE] Not in READY_FOR_UPLOAD")
        return

    now = _utc_now()

    state["phase"] = "ARCHIVED"
    state["updated_at"] = now

    hist = state.get("phase_history", [])
    hist.append({
        "at": now,
        "phase": "ARCHIVED"
    })

    state["phase_history"] = hist[-100:]

    state_path.write_text(json.dumps(state, indent=2))

    print("[FINALIZE] ARCHIVED")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python -m dispatcher.finalize_bridge_v1 <PROJECT_ID>")
        sys.exit(1)

    run(sys.argv[1])
