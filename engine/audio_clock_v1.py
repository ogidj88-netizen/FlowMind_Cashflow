#!/usr/bin/env python3
"""
FlowMind — Audio Clock v1 (Cashflow Mode)

Audio = Master Clock.
Extracts exact duration from WAV using ffprobe.
Outputs AUDIO_CLOCK.json next to source file.
"""

from __future__ import annotations
import json
import subprocess
import sys
import os
from typing import Dict


def get_audio_duration_seconds(path: str) -> float:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Audio file not found: {path}")

    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError("ffprobe failed to read audio duration")

    try:
        return float(result.stdout.strip())
    except ValueError:
        raise RuntimeError("Invalid duration format from ffprobe")


def build_audio_clock(path: str) -> Dict:
    duration_seconds = get_audio_duration_seconds(path)

    return {
        "audio_path": path,
        "duration_seconds": round(duration_seconds, 3),
        "duration_ms": int(duration_seconds * 1000)
    }


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: audio_clock_v1.py <WAV_PATH>")
        return 2

    audio_path = argv[1]

    try:
        clock = build_audio_clock(audio_path)
    except Exception as e:
        print(f"[AUDIO CLOCK ERROR] {e}")
        return 3

    output_path = audio_path.replace(".wav", "_AUDIO_CLOCK.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(clock, f, ensure_ascii=False, indent=2)

    print(f"[AUDIO CLOCK] Generated: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

