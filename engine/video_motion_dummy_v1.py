#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FlowMind Cashflow — Video Motion Dummy v1 (FILTER_COMPLEX, NO DRAWTEXT, NO GRADIENTS)
Generates a motion background video of exact duration based on master.wav:
- base: color source (always available)
- optional: noise (if available)
- motion: zoompan (if available; else fallback to slight blur)

Output:
  assets/cache/<PROJECT_ID>/video/motion_bg.mp4

Usage:
  python -m engine.video_motion_dummy_v1 FM_TEST
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Tuple


def _run(cmd: list[str]) -> Tuple[int, str]:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return p.returncode, p.stdout


def _probe_duration_sec(media: Path) -> float:
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(media)]
    rc, out = _run(cmd)
    if rc != 0:
        raise RuntimeError(f"ffprobe failed rc={rc}\n{out}")
    data = json.loads(out)
    return float(data["format"]["duration"])


def _has_filter(name: str) -> bool:
    rc, out = _run(["ffmpeg", "-hide_banner", "-filters"])
    if rc != 0:
        return False
    return name in out


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: python -m engine.video_motion_dummy_v1 <PROJECT_ID>", file=sys.stderr)
        return 2

    project_id = argv[1]
    project_dir = (Path("projects") / project_id).resolve()
    audio_render = project_dir / "AUDIO_RENDER.json"
    if not audio_render.exists():
        print(f"[FAIL] missing AUDIO_RENDER.json: {audio_render}", file=sys.stderr)
        return 3

    ar = json.loads(audio_render.read_text(encoding="utf-8"))
    master_wav = Path((ar.get("outputs") or {}).get("master_wav") or "").expanduser().resolve()
    if not master_wav.exists():
        print(f"[FAIL] missing master_wav: {master_wav}", file=sys.stderr)
        return 4

    rc, _ = _run(["ffmpeg", "-version"])
    if rc != 0:
        print("[FAIL] ffmpeg not found in PATH", file=sys.stderr)
        return 5

    try:
        dur = _probe_duration_sec(master_wav)
    except Exception as e:
        print(f"[FAIL] ffprobe master_wav: {e}", file=sys.stderr)
        return 6

    out_path = (Path("assets") / "cache" / project_id / "video" / "motion_bg.mp4").resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    has_noise = _has_filter("noise")
    has_zoompan = _has_filter("zoompan")

    # Build filter_complex from [0:v]
    # Base: slight vignette-ish darkening via eq; then optional noise; then motion via zoompan.
    chain = []
    chain.append("format=yuv420p,setsar=1")
    chain.append("eq=contrast=1.05:brightness=-0.02:saturation=1.15")

    if has_noise:
        chain.append("noise=alls=12:allf=t+u")

    if has_zoompan:
        # gentle zoom + sinusoidal pan, 30fps, 1920x1080
        chain.append(
            "zoompan="
            "z='min(1.10,1+0.0007*on)':"
            "x='iw/2-(iw/zoom/2)+30*sin(on/70)':"
            "y='ih/2-(ih/zoom/2)+30*cos(on/65)':"
            "d=1:fps=30:s=1920x1080"
        )
    else:
        # fallback: tiny blur to avoid perfectly static blocks; still larger than 169KB usually with noise
        chain.append("boxblur=2:1")

    chain.append("fps=30")
    chain.append("scale=1920:1080")
    chain.append("format=yuv420p")
    chain.append("setsar=1")

    fc = f"[0:v]{','.join(chain)}[v]"

    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        "color=c=0x101018:s=1920x1080:r=30",
        "-t",
        f"{dur:.3f}",
        "-filter_complex",
        fc,
        "-map",
        "[v]",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(out_path),
    ]

    rc2, out2 = _run(cmd)
    if rc2 != 0:
        print(f"[FAIL] ffmpeg motion dummy rc={rc2}\n{out2}", file=sys.stderr)
        return 7

    print(
        f"[VIDEO_MOTION_DUMMY PASS] out={out_path} duration_sec={dur:.3f} "
        f"noise={has_noise} zoompan={has_zoompan}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
