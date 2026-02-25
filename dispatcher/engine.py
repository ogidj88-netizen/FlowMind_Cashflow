#!/usr/bin/env python3
"""
FlowMind — Dispatcher Engine (Cashflow Mode) v1.7
Immutable state + Crash Recovery + Semantic Audit + Real Loop Guard
"""

from __future__ import annotations
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from typing import Any, Dict

MAX_HALT_ATTEMPTS = 3


class PhaseError(RuntimeError):
    pass


def _project_root(project_id: str) -> str:
    return os.path.join("projects", project_id)


def _state_path(project_id: str) -> str:
    return os.path.join(_project_root(project_id), "PROJECT_STATE.json")


def _audit_path(project_id: str) -> str:
    return os.path.join(_project_root(project_id), "phase_history.log")


def _out_dir(project_id: str) -> str:
    return os.path.join(_project_root(project_id), "out", project_id)


def _halt_reason_path(project_id: str) -> str:
    return os.path.join(_out_dir(project_id), "halt_reason.txt")


def _force_lock_state(path: str) -> None:
    if os.path.exists(path):
        os.chmod(path, 0o444)


def _read_state(path: str, project_id: str) -> Dict[str, Any]:
    if not os.path.isfile(path):
        return {
            "project_id": project_id,
            "phase": "INIT",
            "qa_passed": False,
            "mode": "NORMAL",
            "halt_count": 0
        }
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _minimal_state(state: Dict[str, Any]) -> Dict[str, Any]:
    allowed = {
        "project_id",
        "phase",
        "qa_passed",
        "mode",
        "halted",
        "halt_phase",
        "resume_from",
        "halt_count",
        "hard_stop"
    }
    return {k: v for k, v in state.items() if k in allowed}


def _write_state(path: str, state: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if os.path.exists(path):
        os.chmod(path, 0o644)

    fd, tmp = tempfile.mkstemp(prefix=".tmp.", suffix=".json", dir=os.path.dirname(path))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(_minimal_state(state), f, ensure_ascii=False, indent=2, sort_keys=True)
            f.write("\n")

        with open(tmp, "r", encoding="utf-8") as f:
            json.load(f)

        os.replace(tmp, path)
        os.chmod(path, 0o444)

    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def _write_audit(project_id: str, from_phase: str, to_phase: str, status: str) -> None:
    ts = datetime.now(timezone.utc).isoformat()
    line = f"{ts} | {from_phase} -> {to_phase} | {status}\n"
    with open(_audit_path(project_id), "a", encoding="utf-8") as f:
        f.write(line)


def _run_pre_qa_runner(project_id: str) -> None:
    runner = os.path.join("engine", "qa", "pre_qa_gate_runner_v1.sh")
    proc = subprocess.run([runner, project_id], capture_output=True, text=True)

    if proc.stdout:
        sys.stdout.write(proc.stdout)
    if proc.stderr:
        sys.stderr.write(proc.stderr)

    if proc.returncode != 0:
        raise PhaseError("PRE_QA_FAIL")


def advance_phase(project_id: str, next_phase: str) -> None:
    next_phase = next_phase.upper().strip()
    path = _state_path(project_id)

    _force_lock_state(path)
    state = _read_state(path, project_id)

    current = state.get("phase", "INIT")
    halt_count = state.get("halt_count", 0)

    if state.get("hard_stop") is True:
        raise PhaseError("[HARD STOP] Too many HALT attempts. Manual intervention required.")

    print(f"[DISPATCHER] Current phase: {current}")

    # ---- QA ----
    if next_phase == "QA":
        try:
            _run_pre_qa_runner(project_id)

            # Only successful QA resets halt counter
            state["halt_count"] = 0

        except PhaseError:
            halt_count += 1
            state["halt_count"] = halt_count
            state["halted"] = True
            state["halt_phase"] = "QA"
            state["resume_from"] = "ASSEMBLY"

            if halt_count >= MAX_HALT_ATTEMPTS:
                state["hard_stop"] = True
                _write_state(path, state)
                _write_audit(project_id, current, next_phase, "HARD_STOP")
                raise PhaseError("[HARD STOP] Max HALT attempts reached.")

            _write_state(path, state)
            _write_audit(project_id, current, next_phase, "HALT")

            hr = _halt_reason_path(project_id)
            if os.path.isfile(hr):
                print("\n[HALT_REASON]")
                with open(hr, "r", encoding="utf-8") as f:
                    print(f.read())

            raise PhaseError("[RECOVERY] QA failed. resume_from=ASSEMBLY")

    # ---- UPLOAD ----
    if next_phase == "UPLOAD":
        if state.get("qa_passed") is not True:
            raise PhaseError("[GATE FAIL] qa_passed != true")

    status = "OK"

    if state.get("halted") is True and state.get("resume_from") == next_phase:
        status = "RESUME"

    state.pop("halted", None)
    state.pop("halt_phase", None)
    state.pop("resume_from", None)

    state["phase"] = next_phase
    state["project_id"] = project_id

    _write_state(path, state)
    _write_audit(project_id, current, next_phase, status)

    print(f"[DISPATCHER] Phase now: {next_phase}")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("Usage: dispatcher/engine.py <PROJECT_ID> <NEXT_PHASE>")
        return 2

    try:
        advance_phase(argv[1], argv[2])
        return 0
    except PhaseError as e:
        print(str(e), file=sys.stderr)
        return 70


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
