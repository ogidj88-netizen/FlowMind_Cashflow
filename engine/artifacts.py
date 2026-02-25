"""
FlowMind Cashflow — Artifact Locator v1 (canonical paths)

Rule:
- All stations MUST use this module to locate/write artifacts.
- Canonical OUT root: <repo_root>/out/<PROJECT_ID>/
- Canonical final video: out/<PROJECT_ID>/final.mp4
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Artifacts:
    project_id: str
    repo_root: Path
    out_dir: Path
    final_mp4: Path
    manifest_json: Path
    log_txt: Path


def repo_root() -> Path:
    # Assumption: we run commands from repo root (FlowMind_Cashflow).
    # If not, it still resolves correctly by using current working directory.
    return Path.cwd().resolve()


def artifacts(project_id: str, *, root: Path | None = None) -> Artifacts:
    rr = (root or repo_root()).resolve()
    out_dir = rr / "out" / project_id
    return Artifacts(
        project_id=project_id,
        repo_root=rr,
        out_dir=out_dir,
        final_mp4=out_dir / "final.mp4",
        manifest_json=out_dir / "PROJECT_STATE.json",
        log_txt=out_dir / "run.log",
    )


def ensure_out_dir(project_id: str) -> Path:
    a = artifacts(project_id)
    a.out_dir.mkdir(parents=True, exist_ok=True)
    return a.out_dir
