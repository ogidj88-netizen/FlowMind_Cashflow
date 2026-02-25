"""
FlowMind Cashflow Mode
Hard PROJECT_ID Guard

Rule:
- Folder name MUST equal PROJECT_STATE["project_id"]
- Otherwise HALT immediately
"""

import json
import sys
from pathlib import Path


class ProjectIDMismatch(Exception):
    pass


def validate_project_identity(project_path: Path):
    state_file = project_path / "PROJECT_STATE.json"

    if not state_file.exists():
        raise FileNotFoundError("PROJECT_STATE.json not found")

    with open(state_file, "r") as f:
        state = json.load(f)

    folder_name = project_path.name
    manifest_id = state.get("project_id")

    if not manifest_id:
        raise ProjectIDMismatch("project_id missing in PROJECT_STATE.json")

    if folder_name != manifest_id:
        raise ProjectIDMismatch(
            f"PROJECT_ID mismatch:\n"
            f"Folder: {folder_name}\n"
            f"Manifest: {manifest_id}"
        )

    return True


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m dispatcher.project_guard <PROJECT_PATH>")
        sys.exit(1)

    path = Path(sys.argv[1])
    validate_project_identity(path)

    print("[GUARD PASS] Project identity validated.")
