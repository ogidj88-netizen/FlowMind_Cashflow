#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FlowMind Cashflow — Step Runner: AUDIO_RENDER (SILENT)
Runs engine.audio_render_silent_v1 and updates PROJECT_STATE phase.

Usage:
  python tools/step_audio_render.py FM_TEST
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

# ensure repo root on path
THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[1]
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


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: python tools/step_audio_render.py <PROJECT_ID>", file=sys.stderr)
        return 2

    project_id = argv[1]
    project_dir = (Path("projects") / project_id).resolve()
    if not project_dir.exists():
        print(f"[FAIL] missing project dir: {project_dir}", file=sys.stderr)
        return 3

    # preflight
    ap = project_dir / "AUDIO_PLAN.json"
    if not ap.exists():
        print(f"[FAIL] missing AUDIO_PLAN.json: {ap}", file=sys.stderr)
        return 4

    # run
    try:
        from engine.audio_render_silent_v1 import main as render_main  # type: ignore
        rc = int(render_main(["engine.audio_render_silent_v1", project_id]))
    except Exception as e:
        print(f"[FAIL] audio_render crashed: {e}", file=sys.stderr)
        return 5

    if rc != 0:
        print(f"[FAIL] audio_render returned rc={rc}", file=sys.stderr)
        return rc

    # verify output exists
    marker = project_dir / "AUDIO_RENDER.json"
    if not marker.exists():
        print(f"[FAIL] missing AUDIO_RENDER.json marker: {marker}", file=sys.stderr)
        return 6

    m = _read_json(marker)
    master_wav = Path((m.get("outputs") or {}).get("master_wav") or "")
    if not master_wav.exists():
        print(f"[FAIL] master_wav not found: {master_wav}", file=sys.stderr)
        return 7

    # update state
    state_path = project_dir / "PROJECT_STATE.json"
    state: Dict[str, Any] = {"project_id": project_id}
    if state_path.exists():
        try:
            state = _read_json(state_path)
        except Exception:
            state = {"project_id": project_id}

    state["project_id"] = project_id
    state["phase"] = "AUDIO_RENDER"
    state["updated_at"] = _utc_now_iso()

    hist = state.get("phase_history")
    if not isinstance(hist, list):
        hist = []
    hist.append({"at": state["updated_at"], "phase": "AUDIO_RENDER"})
    if len(hist) > 50:
        hist = hist[-50:]
    state["phase_history"] = hist

    _atomic_write_json(state_path, state)

    print(f"[PASS] AUDIO_RENDER master_wav={master_wav}")
    print(f"[STATE] phase set to AUDIO_RENDER in: {state_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
