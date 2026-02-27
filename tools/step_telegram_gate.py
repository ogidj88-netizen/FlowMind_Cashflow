#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FlowMind Cashflow — Step Runner: TELEGRAM_GATE (DELIVERY_PACK)
Loads .env then runs engine.telegram_gate_v1 and updates PROJECT_STATE:
- PASS -> phase=AWAITING_APPROVAL, approval_gate=DELIVERY_PACK
- FAIL -> HALT with halt_reason=TELEGRAM_SEND_FAILED
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


def _try_load_dotenv() -> None:
    try:
        from dotenv import load_dotenv  # type: ignore
        env_path = REPO_ROOT / ".env"
        if env_path.exists():
            load_dotenv(dotenv_path=str(env_path), override=False)
    except Exception:
        pass


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
        print("Usage: python tools/step_telegram_gate.py <PROJECT_ID>", file=sys.stderr)
        return 2

    _try_load_dotenv()

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

    # allow retry from HALT if reason is TELEGRAM_SEND_FAILED and previous phase was DELIVERY_PACK
    phase = state.get("phase")
    if phase not in ("DELIVERY_PACK", "HALT"):
        print(f"[FAIL] phase must be DELIVERY_PACK or HALT, got: {phase}", file=sys.stderr)
        return 4
    if phase == "HALT" and state.get("halt_reason") != "TELEGRAM_SEND_FAILED":
        print(f"[FAIL] HALT reason not TELEGRAM_SEND_FAILED, got: {state.get('halt_reason')}", file=sys.stderr)
        return 5

    # hard precheck env
    if not os.getenv("TELEGRAM_BOT_TOKEN") or not os.getenv("TELEGRAM_CHAT_ID"):
        print("[FAIL] Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID in .env", file=sys.stderr)
        return 6

    try:
        from engine.telegram_gate_v1 import main as gate_main  # type: ignore
        rc = int(gate_main(["engine.telegram_gate_v1", project_id]))
    except Exception as e:
        print(f"[FAIL] TELEGRAM_GATE crashed: {e}", file=sys.stderr)
        rc = 99

    now = _utc_now_iso()
    hist = state.get("phase_history")
    if not isinstance(hist, list):
        hist = []

    if rc == 0:
        state["phase"] = "AWAITING_APPROVAL"
        state["approval_gate"] = "DELIVERY_PACK"
        state["approval_status"] = "PENDING"
        state["updated_at"] = now
        # clear halt flags
        state.pop("halted", None)
        state.pop("halt_reason", None)
        hist.append({"at": now, "phase": "AWAITING_APPROVAL", "gate": "DELIVERY_PACK"})
        if len(hist) > 50:
            hist = hist[-50:]
        state["phase_history"] = hist
        _atomic_write_json(state_path, state)
        print(f"[PASS] TELEGRAM_GATE sent. phase=AWAITING_APPROVAL in: {state_path}")
        return 0

    # FAIL -> HALT
    state["phase"] = "HALT"
    state["halted"] = True
    state["halt_reason"] = "TELEGRAM_SEND_FAILED"
    state["updated_at"] = now
    hist.append({"at": now, "phase": "HALT", "reason": "TELEGRAM_SEND_FAILED"})
    if len(hist) > 50:
        hist = hist[-50:]
    state["phase_history"] = hist
    _atomic_write_json(state_path, state)
    print("[FAIL] TELEGRAM_GATE failed -> HALT (TELEGRAM_SEND_FAILED)", file=sys.stderr)
    return 10


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
