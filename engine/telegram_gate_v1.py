#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FlowMind Cashflow — Telegram Gate v1 (DELIVERY_PACK approval)
Reads projects/<PROJECT_ID>/DELIVERY_PACK.json and sends a compact message to Telegram.
Loads .env automatically if present.
Does NOT upload to YouTube (SAFE MODE).
"""

from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Tuple


def _try_load_dotenv() -> None:
    # best-effort; do not crash if missing
    try:
        from dotenv import load_dotenv  # type: ignore
        # load repo root .env
        repo_root = Path(__file__).resolve().parents[1]
        env_path = repo_root / ".env"
        if env_path.exists():
            load_dotenv(dotenv_path=str(env_path), override=False)
    except Exception:
        pass


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _short_hash(h: str) -> str:
    h = (h or "").strip()
    return h[:10] if len(h) >= 10 else h


def _fmt_bytes(n: int) -> str:
    if n >= 1024 * 1024:
        return f"{n / (1024*1024):.1f} MB"
    if n >= 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n} B"


def _send_telegram(text: str) -> Tuple[bool, str]:
    _try_load_dotenv()

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        return False, "Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID in env (.env not loaded?)"

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode(
        {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")

    req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8", errors="replace")
        if '"ok":true' in body:
            return True, "sent"
        return False, f"telegram_error: {body[:200]}"
    except Exception as e:
        return False, f"exception: {e}"


def build_message(project_id: str, pack: Dict[str, Any]) -> str:
    art = pack.get("artifacts") or {}
    fv = art.get("final_video") or {}
    qa = art.get("final_qa") or {}

    dur = (pack.get("summary") or {}).get("duration_sec")
    size = int(fv.get("bytes") or 0)
    sha = _short_hash(str(fv.get("sha256") or ""))
    qa_sha = _short_hash(str(qa.get("sha256") or ""))

    msg = (
        f"✅ <b>FlowMind DELIVERY_PACK готовий</b>\n"
        f"<b>project</b>: {project_id}\n"
        f"<b>duration</b>: {dur}s\n"
        f"<b>final.mp4</b>: {_fmt_bytes(size)} | sha256:{sha}\n"
        f"<b>FINAL_QA</b>: sha256:{qa_sha}\n\n"
        f"Відповідь одним словом у чат:\n"
        f"✅ <b>APPROVE {project_id}</b>  або  ❌ <b>REJECT {project_id}</b>\n\n"
        f"<i>(Upload вимкнено. Це gate для дисципліни пайплайна.)</i>"
    )
    return msg


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: python -m engine.telegram_gate_v1 <PROJECT_ID>", file=sys.stderr)
        return 2

    project_id = argv[1]
    project_dir = (Path("projects") / project_id).resolve()
    pack_path = project_dir / "DELIVERY_PACK.json"
    if not pack_path.exists():
        print(f"[FAIL] missing DELIVERY_PACK.json: {pack_path}", file=sys.stderr)
        return 3

    pack = _read_json(pack_path)
    msg = build_message(project_id, pack)

    ok, info = _send_telegram(msg)
    if not ok:
        print(f"[FAIL] telegram send failed: {info}", file=sys.stderr)
        return 10

    marker = project_dir / "TELEGRAM_GATE.json"
    marker.write_text(
        json.dumps(
            {
                "project_id": project_id,
                "generated_at": _utc_now_iso(),
                "gate": "DELIVERY_PACK",
                "sent": True,
                "info": info,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"[TELEGRAM_GATE PASS] sent. marker={marker}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
