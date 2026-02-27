#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FlowMind Cashflow — Production Orchestrator v5
LOCK + RECOVER + PROJECT_ID VALIDATION
"""

import sys
import json
import time
from pathlib import Path


PROJECTS_DIR = Path("projects")


def load_state(project_id):
    path = PROJECTS_DIR / project_id / "PROJECT_STATE.json"

    if not path.exists():
        raise RuntimeError("PROJECT_STATE not found")

    state = json.loads(path.read_text())

    # 🔒 PROJECT ID VALIDATION
    file_project_id = state.get("project_id")
    if file_project_id != project_id:
        raise RuntimeError(
            f"[VALIDATION ERROR] Folder '{project_id}' "
            f"!= PROJECT_STATE.project_id '{file_project_id}'"
        )

    return path, state


def create_lock(project_id):
    lock_path = PROJECTS_DIR / project_id / ".orch.lock"

    if lock_path.exists():
        print("[LOCK] Another orchestrator is running.")
        return None

    lock_path.write_text("LOCKED")
    return lock_path


def release_lock(lock_path):
    if lock_path and lock_path.exists():
        lock_path.unlink()


def run_audio_plan(project_id):
    import tools.step_audio_plan as mod
    mod.main(["step_audio_plan", project_id])


def run_autopilot_tick(project_id):
    import tools.autopilot_tick as mod
    mod.main(["autopilot_tick", project_id])


def run_recover(project_id):
    from dispatcher.recover_bridge_v1 import run as recover_run
    recover_run(project_id)


def orchestrate_once(project_id):

    state_path, state = load_state(project_id)
    phase = state.get("phase")

    print(f"[ORCH] Phase: {phase}")

    if phase == "AUDIO_PLAN":
        run_audio_plan(project_id)
        return

    if phase in (
        "AUDIO_RENDER",
        "ASSEMBLY_FROM_AUDIO",
        "FINAL_QA",
        "DELIVERY_PACK",
        "AWAITING_APPROVAL",
        "APPROVED",
        "READY_FOR_UPLOAD"
    ):
        run_autopilot_tick(project_id)
        return

    if phase == "ARCHIVED":
        print("[ORCH] ARCHIVED — stopping.")
        return "STOP"

    if phase == "HALT":
        print("[ORCH] HALTED — use --recover")
        return "STOP"

    print("[ORCH] Unknown phase.")


def main():

    if len(sys.argv) < 2:
        print("Usage: python fm.py <PROJECT_ID> [--loop|--recover]")
        sys.exit(1)

    project_id = sys.argv[1]
    loop_mode = "--loop" in sys.argv
    recover_mode = "--recover" in sys.argv

    if recover_mode:
        run_recover(project_id)
        return

    lock_path = create_lock(project_id)

    if lock_path is None:
        sys.exit(1)

    try:

        if not loop_mode:
            orchestrate_once(project_id)
            return

        print(f"[ORCH] LOOP START project={project_id}")

        while True:
            result = orchestrate_once(project_id)

            if result == "STOP":
                print("[ORCH] LOOP END")
                break

            time.sleep(5)

    finally:
        release_lock(lock_path)


if __name__ == "__main__":
    main()
