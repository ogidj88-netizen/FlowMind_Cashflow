import json
from pathlib import Path


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
