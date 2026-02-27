#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FlowMind Cashflow — DELIVERY PACK v1
Builds a deterministic delivery package JSON after FINAL_QA.

Outputs:
  projects/<PROJECT_ID>/DELIVERY_PACK.json

Usage:
  python -m engine.delivery_pack_v1 FM_TEST
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _file_meta(path: Path) -> Dict[str, Any]:
    st = path.stat()
    return {
        "path": str(path.resolve()),
        "bytes": st.st_size,
        "sha256": _sha256(path),
    }


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: python -m engine.delivery_pack_v1 <PROJECT_ID>", file=sys.stderr)
        return 2

    project_id = argv[1]
    project_dir = (Path("projects") / project_id).resolve()
    out_dir = (Path("out") / project_id).resolve()

    state_path = project_dir / "PROJECT_STATE.json"
    if not state_path.exists():
        print(f"[FAIL] missing PROJECT_STATE.json: {state_path}", file=sys.stderr)
        return 3

    state = _read_json(state_path)
    if state.get("phase") != "FINAL_QA" or not state.get("qa_passed", False):
        print(f"[FAIL] Not ready. Need phase=FINAL_QA qa_passed=true. Got: {state.get('phase')} qa_passed={state.get('qa_passed')}", file=sys.stderr)
        return 4

    final_mp4 = out_dir / "final.mp4"
    ffprobe_json = out_dir / "ffprobe.json"
    final_qa_json = project_dir / "FINAL_QA.json"
    audio_plan = project_dir / "AUDIO_PLAN.json"
    audio_render = project_dir / "AUDIO_RENDER.json"
    assembly_marker = project_dir / "ASSEMBLY_FROM_AUDIO.json"

    required = [final_mp4, ffprobe_json, final_qa_json, audio_plan, audio_render, assembly_marker]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        print("[FAIL] Missing required files:\n- " + "\n- ".join(missing), file=sys.stderr)
        return 5

    rep = _read_json(final_qa_json)
    duration = None
    for c in rep.get("checks", []):
        if c.get("name") == "duration_matches_master_wav":
            duration = (c.get("details") or {}).get("actual")

    pack: Dict[str, Any] = {
        "project_id": project_id,
        "generated_at": _utc_now_iso(),
        "phase": "DELIVERY_PACK",
        "summary": {
            "duration_sec": duration,
            "mode": "CASHFLOW_DUMMY_MOTION_BG",
            "notes": "Audio is master clock. Video is motion dummy background (no text).",
        },
        "artifacts": {
            "final_video": _file_meta(final_mp4),
            "ffprobe": _file_meta(ffprobe_json),
            "final_qa": _file_meta(final_qa_json),
            "audio_plan": _file_meta(audio_plan),
            "audio_render": _file_meta(audio_render),
            "assembly_marker": _file_meta(assembly_marker),
        },
        "next_gate": {
            "name": "TELEGRAM_APPROVAL",
            "required": True,
            "message": "Approve DELIVERY_PACK to proceed (upload disabled in current SAFE MODE).",
        },
    }

    out_path = project_dir / "DELIVERY_PACK.json"
    out_path.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[DELIVERY_PACK PASS] written: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
