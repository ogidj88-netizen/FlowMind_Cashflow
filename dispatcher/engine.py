"""
FlowMind Cashflow
Production Orchestrator v2
Deterministic Dispatcher with Hard Lock
"""

import json
import sys
from pathlib import Path


ALLOWED_PHASES = [
    "TOPIC",
    "SCRIPT",
    "SCENE",
    "VISUAL",
    "THUMBNAIL",
    "QA",
    "UPLOAD",
    "DONE"
]


def load_state(project_path: Path):
    state_file = project_path / "PROJECT_STATE.json"
    if not state_file.exists():
        raise Exception("PROJECT_STATE.json not found")

    with open(state_file, "r") as f:
        return json.load(f)


def save_state(project_path: Path, state: dict):
    state_file = project_path / "PROJECT_STATE.json"
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)


def next_phase(current_phase: str):
    if current_phase not in ALLOWED_PHASES:
        raise Exception(f"Unknown phase: {current_phase}")

    index = ALLOWED_PHASES.index(current_phase)

    if index + 1 >= len(ALLOWED_PHASES):
        return "DONE"

    return ALLOWED_PHASES[index + 1]


def main():
    if len(sys.argv) != 2:
        print("Usage: python -m dispatcher.engine <PROJECT_PATH>")
        sys.exit(1)

    project_path = Path(sys.argv[1])

    if not project_path.exists():
        raise Exception("Project path does not exist")

    state = load_state(project_path)

    if state.get("locked") is True:
        raise Exception("Project is locked. Phase change not allowed.")

    current_phase = state.get("phase")

    if not current_phase:
        raise Exception("Missing phase in PROJECT_STATE.json")

    if current_phase == "DONE":
        print("Project already completed.")
        return

    new_phase = next_phase(current_phase)
    state["phase"] = new_phase

    save_state(project_path, state)

    print(f"Phase advanced: {current_phase} -> {new_phase}")


if __name__ == "__main__":
    main()
