#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FlowMind Cashflow — Audio Render Silent v1
Creates a real master WAV based on AUDIO_PLAN.json "master_clock.total_duration_sec".

Usage:
  python -m engine.audio_render_silent_v1 FM_TEST
"""

from __future__ import annotations

import json
import os
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Tuple


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _ensure_parent(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)


def _run(cmd: list[str]) -> Tuple[int, str]:
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return proc.returncode, proc.stdout


def _ffmpeg_exists() -> bool:
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except Exception:
        return False


def _render_silence(out_wav: Path, duration_sec: float, sr: int = 48000, ch: int = 2) -> None:
    # deterministic PCM WAV
    _ensure_parent(out_wav)
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"anullsrc=r={sr}:cl={'stereo' if ch == 2 else 'mono'}",
        "-t",
        f"{duration_sec:.3f}",
        "-ac",
        str(ch),
        "-ar",
        str(sr),
        "-c:a",
        "pcm_s16le",
        str(out_wav),
    ]
    rc, out = _run(cmd)
    if rc != 0:
        raise RuntimeError(f"ffmpeg failed rc={rc}\n{out}")


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: python -m engine.audio_render_silent_v1 <PROJECT_ID>", file=sys.stderr)
        return 2

    project_id = argv[1]
    project_dir = (Path("projects") / project_id).resolve()

    audio_plan_path = project_dir / "AUDIO_PLAN.json"
    if not audio_plan_path.exists():
        print(f"[FAIL] missing AUDIO_PLAN.json: {audio_plan_path}", file=sys.stderr)
        return 3

    plan = _read_json(audio_plan_path)
    spec = plan.get("audio_spec") or {}
    clock = plan.get("master_clock") or {}

    sr = int(spec.get("sample_rate") or 48000)
    ch = int(spec.get("channels") or 2)
    total = float(clock.get("total_duration_sec") or 0.0)

    if total <= 0:
        print(f"[FAIL] invalid total_duration_sec={total}", file=sys.stderr)
        return 4

    if not _ffmpeg_exists():
        print("[FAIL] ffmpeg not found in PATH", file=sys.stderr)
        return 5

    # Output path: prefer AUDIO_PLAN.outputs.master_wav_placeholder
    outputs = plan.get("outputs") or {}
    out_wav_str = outputs.get("master_wav_placeholder")
    if not out_wav_str:
        out_wav = (Path("assets") / "cache" / project_id / "audio" / "master.wav").resolve()
    else:
        out_wav = Path(out_wav_str).expanduser().resolve()

    try:
        _render_silence(out_wav, total, sr=sr, ch=ch)
    except Exception as e:
        print(f"[FAIL] render: {e}", file=sys.stderr)
        return 6

    # write a tiny marker file for downstream modules (optional, but useful)
    marker = project_dir / "AUDIO_RENDER.json"
    marker_data = {
        "project_id": project_id,
        "generated_at": _utc_now_iso(),
        "mode": "SILENT",
        "outputs": {"master_wav": str(out_wav)},
        "duration_sec": total,
        "audio_spec": {"sample_rate": sr, "channels": ch, "format": "wav"},
    }
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(json.dumps(marker_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"[AUDIO_RENDER PASS] master_wav={out_wav} duration_sec={total:.3f}")
    print(f"[AUDIO_RENDER PASS] marker={marker}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
