#!/usr/bin/env python3
"""
FlowMind — Project Control Utility
Supports:
  phase <NEXT_PHASE>
  resume
  unlock
"""

from __future__ import annotations
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict

STATE_FILE = "PROJECT_STATE.json"
AUDIT_FILE = "phase_history.log"


def _project_root(project_id: str) -> str:
    return os.path.join("projects", project_id)


def _state_path(project_id: str) -> str:
    return os.path.join(_project_root(project_id), STATE_FILE)


def _audit_path(project_id: str) -> str:
    return os.path.join(_project_root(project_id), AUDIT_FILE)


def _read_state(path: str) -> Dict[str, Any]:
    if not os.path.isfile(path):
        raise RuntimeError("PROJECT_STATE.json not found.")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_state(path: str, state: Dict[str, Any]) -> None:
    os.chmod(path, 0o644)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    os.chmod(path, 0o444)


def _write_audit(project_id: str, message: str) -> None:
    ts = datetime.now(timezone.utc).isoformat()
    line = f"{ts} | {message}\n"
    with open(_audit_path(project_id), "a", encoding="utf-8") as f:
        f.write(line)


def cmd_resume(project_id: str) -> None:
    path = _state_path(project_id)
    state = _read_state(path)

    resume_from = state.get("resume_from")
    if not resume_from:
        print("[RESUME] Nothing to resume.")
        return

    print(f"[RESUME] Resuming from: {resume_from}")

    from dispatcher.engine import advance_phase
    advance_phase(project_id, resume_from)


def cmd_unlock(project_id: str) -> None:
    path = _state_path(project_id)
    state = _read_state(path)

    if state.get("hard_stop") is not True:
        print("[UNLOCK] No hard_stop present.")
        return

    print("[UNLOCK] Clearing hard_stop and halt counters...")

    state.pop("hard_stop", None)
    state.pop("halted", None)
    state.pop("halt_phase", None)
    state.pop("resume_from", None)
    state["halt_count"] = 0

    _write_state(path, state)
    _write_audit(project_id, "MANUAL_UNLOCK")

    print("[UNLOCK] System unlocked.")


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print("Usage:")
        print("  project_ctl.py <PROJECT_ID> phase <NEXT_PHASE>")
        print("  project_ctl.py <PROJECT_ID> resume")
        print("  project_ctl.py <PROJECT_ID> unlock")
        return 2

    project_id = argv[1]
    cmd = argv[2].lower()

    if cmd == "resume":
        cmd_resume(project_id)
        return 0

    if cmd == "unlock":
        cmd_unlock(project_id)
        return 0

    if cmd == "phase":
        if len(argv) != 4:
            print("Usage: project_ctl.py <PROJECT_ID> phase <NEXT_PHASE>")
            return 2
        from dispatcher.engine import advance_phase
        advance_phase(project_id, argv[3])
        return 0

    print(f"Unknown command: {cmd}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
