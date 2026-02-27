#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FlowMind Cashflow — Step Runner: FINAL_QA
Runs engine.final_qa_v1 and updates PROJECT_STATE phase to FINAL_QA (pass) or HALT (fail).

Usage:
  python tools/step_final_qa.py FM_TEST
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

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
        print("Usage: python tools/step_final_qa.py <PROJECT_ID>", file=sys.stderr)
        return 2

    project_id = argv[1]
    project_dir = (Path("projects") / project_id).resolve()
    if not project_dir.exists():
        print(f"[FAIL] missing project dir: {project_dir}", file=sys.stderr)
        return 3

    state_path = project_dir / "PROJECT_STATE.json"
    state: Dict[str, Any] = {"project_id": project_id}
    if state_path.exists():
        try:
            state = _read_json(state_path)
        except Exception:
            state = {"project_id": project_id}

    try:
        from engine.final_qa_v1 import main as qa_main  # type: ignore
        rc = int(qa_main(["engine.final_qa_v1", project_id]))
    except Exception as e:
        print(f"[FAIL] FINAL_QA crashed: {e}", file=sys.stderr)
        rc = 99

    # read report if exists
    report_path = project_dir / "FINAL_QA.json"
    passed = False
    if report_path.exists():
        try:
            rep = _read_json(report_path)
            passed = bool(rep.get("pass"))
        except Exception:
            passed = False

    now = _utc_now_iso()
    state["project_id"] = project_id
    state["updated_at"] = now

    hist = state.get("phase_history")
    if not isinstance(hist, list):
        hist = []

    if rc == 0 and passed:
        state["phase"] = "FINAL_QA"
        state["qa_passed"] = True
        hist.append({"at": now, "phase": "FINAL_QA"})
        _atomic_write_json(state_path, state)
        print(f"[PASS] FINAL_QA phase set in: {state_path}")
        return 0

    # FAIL -> HALT with reason
    state["phase"] = "HALT"
    state["halted"] = True
    state["halt_reason"] = "FINAL_QA_FAILED"
    state["qa_passed"] = False
    hist.append({"at": now, "phase": "HALT", "reason": "FINAL_QA_FAILED"})
    state["phase_history"] = hist
    _atomic_write_json(state_path, state)
    print(f"[FAIL] FINAL_QA -> HALT. See: {report_path}")
    return 10


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
