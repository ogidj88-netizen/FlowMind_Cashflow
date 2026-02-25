#!/usr/bin/env python3
"""
FlowMind — STATE MANAGER v6 (Forward-safe)
- Anti-rollback after ASSEMBLY (but allows forward FINAL_READY)
- Guaranteed re-lock on ASSEMBLY and FINAL_READY
"""

import json
import os
from pathlib import Path


def get_state_path(project_id: str) -> Path:
    return Path(f"projects/{project_id}/PROJECT_STATE.json")


def load_state(project_id: str) -> dict:
    p = get_state_path(project_id)
    if not p.exists():
        raise FileNotFoundError("PROJECT_STATE.json not found")
    with open(p, "r") as f:
        return json.load(f)


def save_state(project_id: str, new_state: dict) -> dict:
    p = get_state_path(project_id)
    if not p.exists():
        raise FileNotFoundError("PROJECT_STATE.json not found")

    with open(p, "r") as f:
        current = json.load(f)

    cur_phase = current.get("phase")
    new_phase = new_state.get("phase")

    # ✅ Forward-safe rule after ASSEMBLY
    if cur_phase == "ASSEMBLY":
        allowed_next = {"ASSEMBLY", "FINAL_READY"}
        if new_phase not in allowed_next:
            # re-lock defensively
            os.chmod(p, 0o444)
            raise RuntimeError("Phase rollback forbidden after ASSEMBLY (only FINAL_READY allowed)")

    try:
        os.chmod(p, 0o644)
        with open(p, "w") as f:
            json.dump(new_state, f, indent=2)
        _apply_locks_if_needed(project_id)
        return new_state
    finally:
        # always enforce lock for terminal-like phases
        with open(p, "r") as f:
            final_state = json.load(f)
        if final_state.get("phase") in {"ASSEMBLY", "FINAL_READY"}:
            os.chmod(p, 0o444)


def _apply_locks_if_needed(project_id: str):
    p = get_state_path(project_id)
    with open(p, "r") as f:
        state = json.load(f)

    # Ensure mode_locked when entering ASSEMBLY
    if state.get("phase") == "ASSEMBLY":
        if not state.get("mode_locked"):
            state["mode_locked"] = True
            os.chmod(p, 0o644)
            with open(p, "w") as wf:
                json.dump(state, wf, indent=2)

    # Lock both ASSEMBLY and FINAL_READY
    if state.get("phase") in {"ASSEMBLY", "FINAL_READY"}:
        os.chmod(p, 0o444)
