#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FlowMind Cashflow — Recover Bridge v1

HALT -> Resume previous safe phase
"""

import json
from pathlib import Path
from datetime import datetime, timezone


def _utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run(project_id: str):

    state_path = Path("projects") / project_id / "PROJECT_STATE.json"

    if not state_path.exists():
        print("[RECOVER] PROJECT_STATE missing")
        return

    state = json.loads(state_path.read_text())

    if state.get("phase") != "HALT":
        print("[RECOVER] Not in HALT state")
        return

    history = state.get("phase_history", [])

    if len(history) < 2:
        print("[RECOVER] No previous phase found")
        return

    # Last entry is HALT, so take previous
    previous_phase = history[-2].get("phase")

    now = _utc_now()

    state["phase"] = previous_phase
    state["halted"] = False
    state.pop("halt_reason", None)
    state["updated_at"] = now

    history.append({
        "at": now,
        "phase": previous_phase,
        "recovered": True
    })

    state["phase_history"] = history[-100:]

    state_path.write_text(json.dumps(state, indent=2))

    print(f"[RECOVER] Resumed to {previous_phase}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python -m dispatcher.recover_bridge_v1 <PROJECT_ID>")
        sys.exit(1)

    run(sys.argv[1])
