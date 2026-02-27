#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FlowMind Cashflow — Step Runner: AUDIO_PLAN
SAFE: validates inputs, runs engine.audio_plan_v1, updates state phase atomically.

Usage:
  python tools/step_audio_plan.py FM_TEST
  python tools/step_audio_plan.py projects/FM_TEST
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Tuple


# --- Ensure repo root is on sys.path (fixes: No module named 'engine') ---
THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[1]  # tools/ -> repo root
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _atomic_write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_fd, tmp_path = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(tmp_path, path)
    finally:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass


def _resolve_project_dir(arg: str) -> Path:
    p = Path(arg).expanduser()
    if p.is_dir() and (p / "ASSEMBLY_PLAN.json").exists():
        return p
    return Path("projects") / arg


def _find_state_file(project_dir: Path) -> Path:
    a = project_dir / "PROJECT_STATE.json"
    if a.exists():
        return a
    b = project_dir / "STATE.json"
    if b.exists():
        return b
    return a  # create canonical if none exists


def _update_state_phase(state: Dict[str, Any], phase: str) -> Dict[str, Any]:
    state = dict(state) if isinstance(state, dict) else {}
    state["phase"] = phase
    state["updated_at"] = _utc_now_iso()

    hist = state.get("phase_history")
    if not isinstance(hist, list):
        hist = []
    hist.append({"at": state["updated_at"], "phase": phase})
    if len(hist) > 50:
        hist = hist[-50:]
    state["phase_history"] = hist
    return state


def _preflight(project_dir: Path) -> Tuple[Path, Path]:
    assembly = project_dir / "ASSEMBLY_PLAN.json"
    script = project_dir / "SCRIPT.json"
    if not assembly.exists():
        raise FileNotFoundError(f"Missing required file: {assembly}")
    if not script.exists():
        raise FileNotFoundError(f"Missing required file: {script}")
    return assembly, script


def _run_audio_plan_module(project_id: str) -> int:
    # Import AFTER sys.path fix
    from engine.audio_plan_v1 import main as audio_plan_main  # type: ignore
    return int(audio_plan_main(["engine.audio_plan_v1", project_id]))


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: python tools/step_audio_plan.py <PROJECT_ID|projects/PROJECT_ID>", file=sys.stderr)
        return 2

    project_dir = _resolve_project_dir(argv[1]).resolve()
    if not project_dir.exists():
        print(f"[FAIL] project_dir not found: {project_dir}", file=sys.stderr)
        return 2

    project_id = project_dir.name
    print(f"[AUDIO_PLAN STEP] project_id={project_id}")

    try:
        _preflight(project_dir)
    except Exception as e:
        print(f"[FAIL] preflight: {e}", file=sys.stderr)
        return 3

    try:
        rc = _run_audio_plan_module(project_id)
    except Exception as e:
        print(f"[FAIL] audio_plan_v1 crashed: {e}", file=sys.stderr)
        return 4

    if rc != 0:
        print(f"[FAIL] audio_plan_v1 returned rc={rc}", file=sys.stderr)
        return rc

    out_path = project_dir / "AUDIO_PLAN.json"
    if not out_path.exists():
        print(f"[FAIL] AUDIO_PLAN.json not found after run: {out_path}", file=sys.stderr)
        return 5

    state_path = _find_state_file(project_dir)
    state: Dict[str, Any] = {}
    if state_path.exists():
        try:
            state = _read_json(state_path)
        except Exception:
            state = {"project_id": project_id}

    state["project_id"] = project_id
    state = _update_state_phase(state, "AUDIO_PLAN")
    _atomic_write_json(state_path, state)

    print(f"[PASS] AUDIO_PLAN ready: {out_path}")
    print(f"[STATE] phase set to AUDIO_PLAN in: {state_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
