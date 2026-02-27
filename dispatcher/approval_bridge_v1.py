#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FlowMind Cashflow — Approval Bridge v1

If PROJECT_STATE.phase == APPROVED
→ move to READY_FOR_UPLOAD

This keeps architecture deterministic.
No auto-upload here.
Only phase transition.
"""

import json
from pathlib import Path
from datetime import datetime, timezone


def _utc_now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run(project_id: str):

    state_path = Path("projects") / project_id / "PROJECT_STATE.json"
    if not state_path.exists():
        print("[BRIDGE] No PROJECT_STATE")
        return

    state = json.loads(state_path.read_text())

    if state.get("phase") != "APPROVED":
        print("[BRIDGE] Not in APPROVED state")
        return

    now = _utc_now_iso()

    state["phase"] = "READY_FOR_UPLOAD"
    state["updated_at"] = now

    hist = state.get("phase_history", [])
    hist.append({"at": now, "phase": "READY_FOR_UPLOAD"})
    state["phase_history"] = hist[-50:]

    state_path.write_text(json.dumps(state, indent=2))

    print("[BRIDGE] Moved to READY_FOR_UPLOAD")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python -m dispatcher.approval_bridge_v1 <PROJECT_ID>")
        sys.exit(1)

    run(sys.argv[1])
