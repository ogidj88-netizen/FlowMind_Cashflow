#!/usr/bin/env python3
"""
FlowMind Cashflow — FINAL QA v2 (Artifact-Based)

Strict:
- Uses artifacts() only
- No external path injection
- Checks:
    - file exists
    - size threshold
    - ffprobe video stream
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from engine.artifacts import artifacts


MIN_SIZE_BYTES = 200_000  # 200KB minimal safety threshold


def ffprobe_has_video_stream(path: Path) -> bool:
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=codec_type",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        return "video" in result.stdout.lower()
    except Exception:
        return False


def run_final_qa(project_id: str) -> dict:
    a = artifacts(project_id)
    final_path = a.final_mp4

    report = {
        "pass": False,
        "final_video": {
            "found": False,
            "path": None,
        },
        "checks": {},
        "notes": [],
    }

    if not final_path.exists():
        report["notes"].append("FINAL_VIDEO_NOT_FOUND")
        return report

    report["final_video"]["found"] = True
    report["final_video"]["path"] = str(final_path)

    size_bytes = final_path.stat().st_size
    report["checks"]["exists"] = True
    report["checks"]["size_bytes"] = size_bytes

    if size_bytes < MIN_SIZE_BYTES:
        report["notes"].append("FINAL_VIDEO_TOO_SMALL")
        return report

    has_video = ffprobe_has_video_stream(final_path)
    report["checks"]["ffprobe_video_stream"] = has_video

    if not has_video:
        report["notes"].append("NO_VIDEO_STREAM")
        return report

    report["pass"] = True
    return report
