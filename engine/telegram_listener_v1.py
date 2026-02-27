#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FlowMind Cashflow — Telegram Listener v1
Polling-based approval listener.

Reads new Telegram updates and:
- APPROVE <PROJECT_ID>
- REJECT <PROJECT_ID>

Updates PROJECT_STATE.json accordingly.

Usage:
  python -m engine.telegram_listener_v1
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Tuple


STATE_FILE = Path("telegram_listener_state.json")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _load_env():
    try:
        from dotenv import load_dotenv  # type: ignore
        load_dotenv()
    except Exception:
        pass


def _get_updates(offset: int | None) -> Tuple[bool, Dict[str, Any]]:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        return False, {"error": "No TELEGRAM_BOT_TOKEN"}

    url = f"https://api.telegram.org/bot{token}/getUpdates"
    params = {"timeout": 5}
    if offset:
        params["offset"] = offset

    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode()
        return True, json.loads(body)
    except Exception as e:
        return False, {"error": str(e)}


def _load_listener_state() -> Dict[str, Any]:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"last_update_id": None}


def _save_listener_state(data: Dict[str, Any]):
    STATE_FILE.write_text(json.dumps(data, indent=2))


def _update_project_state(project_id: str, new_phase: str):
    state_path = Path("projects") / project_id / "PROJECT_STATE.json"
    if not state_path.exists():
        return

    state = json.loads(state_path.read_text())
    now = _utc_now_iso()

    state["phase"] = new_phase
    state["approval_status"] = new_phase
    state["updated_at"] = now

    hist = state.get("phase_history", [])
    hist.append({"at": now, "phase": new_phase})
    state["phase_history"] = hist[-50:]

    state.pop("halted", None)
    state.pop("halt_reason", None)

    state_path.write_text(json.dumps(state, indent=2))


def _parse_command(text: str) -> Tuple[str | None, str | None]:
    text = text.strip().upper()

    if text.startswith("APPROVE "):
        return "APPROVED", text.split(" ", 1)[1].strip()

    if text.startswith("REJECT "):
        return "REJECTED", text.split(" ", 1)[1].strip()

    return None, None


def main():
    _load_env()

    listener_state = _load_listener_state()
    offset = listener_state.get("last_update_id")

    ok, data = _get_updates(offset)
    if not ok or not data.get("ok"):
        print("[LISTENER] Failed to fetch updates")
        return

    results = data.get("result", [])
    if not results:
        print("[LISTENER] No new messages")
        return

    for upd in results:
        update_id = upd["update_id"]
        message = upd.get("message", {})
        text = message.get("text", "")

        phase, project_id = _parse_command(text)
        if phase and project_id:
            print(f"[LISTENER] {phase} detected for {project_id}")
            _update_project_state(project_id, phase)

        listener_state["last_update_id"] = update_id + 1

    _save_listener_state(listener_state)
    print("[LISTENER] Done.")


if __name__ == "__main__":
    main()
