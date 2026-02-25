"""
FlowMind — Safe Project Cleanup

Usage:
python3 -m tools.cleanup_project <PROJECT_PATH>
"""

import sys
import shutil
from pathlib import Path


class CleanupError(Exception):
    pass


def run(project_path: Path):
    if not project_path.exists():
        raise CleanupError("Project folder does not exist")

    if project_path.name in ["main", "production", "FlowMind"]:
        raise CleanupError("Refusing to delete protected directory")

    if "FM_" not in project_path.name:
        raise CleanupError("Not a valid FlowMind project folder")

    shutil.rmtree(project_path)

    print(f"[CLEANUP] Removed project: {project_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 -m tools.cleanup_project <PROJECT_PATH>")
        sys.exit(1)

    run(Path(sys.argv[1]))
