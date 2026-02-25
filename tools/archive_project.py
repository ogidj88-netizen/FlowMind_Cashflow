#!/usr/bin/env python3
"""
FlowMind Cashflow Mode
Archive Project Tool v2 (Idempotent, Safe)

Behavior:
- Ensures projects/_archive exists
- If project folder missing -> prints SKIP and exits 0 (idempotent)
- If destination exists -> appends timestamp suffix
- Moves whole project folder into projects/_archive/<project_name>[_YYYYMMDD_HHMMSS]
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime


class ArchiveError(Exception):
    pass


def ts() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def archive_dir(project_path: Path) -> Path:
    # project_path = projects/<NAME>
    return project_path.parent / "_archive"


def pick_dest(base_dir: Path, name: str) -> Path:
    d = base_dir / name
    if not d.exists():
        return d
    return base_dir / f"{name}_{ts()}"


def run(project_path: Path) -> None:
    project_path = project_path.resolve()

    if not project_path.exists():
        print(f"[ARCHIVE] SKIP: project folder missing: {project_path}")
        return

    if not project_path.is_dir():
        raise ArchiveError("Project path is not a directory")

    # Canonical marker
    if not (project_path / "PROJECT_STATE.json").exists():
        raise ArchiveError("PROJECT_STATE.json missing (not a valid project folder)")

    adir = archive_dir(project_path)
    adir.mkdir(parents=True, exist_ok=True)

    dest = pick_dest(adir, project_path.name)

    shutil.move(str(project_path), str(dest))
    print(f"[ARCHIVE] Project moved to {dest}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 -m tools.archive_project <PROJECT_PATH>")
        raise SystemExit(1)

    run(Path(sys.argv[1]))
