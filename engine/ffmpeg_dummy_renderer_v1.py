#!/usr/bin/env python3
"""
FlowMind Cashflow — FFmpeg Dummy Renderer v1 (SAFE)

Goal:
- Build dummy per-scene videos (solid color) based on ASSEMBLY_PLAN.json
- Concatenate them into out/<PROJECT_ID>/final.mp4 with silent audio
- No drawtext dependency (macOS builds may lack drawtext filter)
- Concat list uses absolute paths (ffmpeg resolves relative paths to concat_list location)

Outputs:
- out/<PROJECT_ID>/concat_list.txt
- out/<PROJECT_ID>/final.mp4
- out/<PROJECT_ID>/ffprobe.json
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run(cmd: List[str]) -> None:
    subprocess.run(cmd, check=True)


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
    tmp.replace(path)


def project_root() -> Path:
    # Assume we run from repo root (FlowMind_Cashflow). If not, fallback to cwd.
    return Path(os.getcwd()).resolve()


def resolve_project_id_or_path(arg: str) -> Path:
    """
    Accept:
    - project_id (FM_TEST) -> projects/FM_TEST
    - direct path (projects/FM_TEST) -> as-is
    """
    p = Path(arg)
    if p.exists() and p.is_dir():
        return p.resolve()
    return (project_root() / "projects" / arg).resolve()


def ffmpeg_exists() -> bool:
    from shutil import which
    return which("ffmpeg") is not None and which("ffprobe") is not None


def make_dummy_clip(out_path: Path, duration_sec: float, width: int, height: int, fps: int) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Solid black clip (dummy)
    # IMPORTANT: no drawtext filter — avoids missing drawtext on some mac builds
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=size={width}x{height}:rate={fps}:color=black",
        "-t", f"{duration_sec:.3f}",
        "-r", str(fps),
        "-vf", "setsar=1",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(out_path),
    ]
    run(cmd)


def ffprobe_json(video_path: Path) -> Dict[str, Any]:
    cmd = [
        "ffprobe",
        "-v", "error",
        "-print_format", "json",
        "-show_streams",
        "-show_format",
        str(video_path),
    ]
    out = subprocess.check_output(cmd)
    return json.loads(out.decode("utf-8", errors="replace"))


def main(argv: List[str]) -> int:
    if not ffmpeg_exists():
        print("[RENDER_DUMMY FAIL] ffmpeg/ffprobe not found in PATH", file=sys.stderr)
        return 2

    if len(argv) < 2:
        print("Usage: python -m engine.ffmpeg_dummy_renderer_v1 <PROJECT_ID|PROJECT_PATH>", file=sys.stderr)
        return 2

    project_dir = resolve_project_id_or_path(argv[1])
    project_id = project_dir.name

    assembly_plan_path = project_dir / "ASSEMBLY_PLAN.json"
    if not assembly_plan_path.exists():
        print(f"[RENDER_DUMMY FAIL] Missing: {assembly_plan_path}", file=sys.stderr)
        return 2

    plan = read_json(assembly_plan_path)
    video_spec = plan.get("video_spec", {})
    width = int(video_spec.get("width", 1920))
    height = int(video_spec.get("height", 1080))
    fps = int(video_spec.get("fps", 30))

    timeline = plan.get("timeline", [])
    if not isinstance(timeline, list) or not timeline:
        print("[RENDER_DUMMY FAIL] Empty timeline in ASSEMBLY_PLAN.json", file=sys.stderr)
        return 2

    out_dir = (project_root() / "out" / project_id).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # Build dummy per-scene clips at the exact placeholder paths from ASSEMBLY_PLAN
    abs_video_paths: List[Path] = []
    for item in timeline:
        vid_rel = item.get("video_path")
        dur = float(item.get("duration_sec", 0))
        if not vid_rel or dur <= 0:
            continue
        vid_abs = (project_root() / vid_rel).resolve()
        make_dummy_clip(vid_abs, dur, width, height, fps)
        abs_video_paths.append(vid_abs)

    if not abs_video_paths:
        print("[RENDER_DUMMY FAIL] No valid video clips generated from timeline", file=sys.stderr)
        return 2

    # Write concat list with ABSOLUTE paths (critical fix)
    concat_list_path = out_dir / "concat_list.txt"
    with concat_list_path.open("w", encoding="utf-8") as f:
        for p in abs_video_paths:
            # ffmpeg concat demuxer requires: file '<path>'
            f.write(f"file '{str(p)}'\n")

    total_duration = float(plan.get("total_duration_sec", 0) or 0)
    if total_duration <= 0:
        # fallback: sum durations
        total_duration = sum(float(x.get("duration_sec", 0) or 0) for x in timeline)

    final_path = out_dir / "final.mp4"

    # Concatenate video + add silent audio (48k stereo), enforce canonical output constraints
    cmd_concat = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list_path),
        "-f", "lavfi",
        "-i", "anullsrc=r=48000:cl=stereo",
        "-t", f"{total_duration:.3f}",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-r", str(fps),
        "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
               f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-ar", "48000",
        "-ac", "2",
        "-movflags", "+faststart",
        str(final_path),
    ]
    run(cmd_concat)

    probe = ffprobe_json(final_path)
    probe_out = out_dir / "ffprobe.json"
    write_json(probe_out, {
        "project_id": project_id,
        "generated_at": utc_now_iso(),
        "final_video": str(final_path),
        "ffprobe": probe,
    })

    print(f"[RENDER_DUMMY PASS] final={final_path} ffprobe={probe_out} concat_list={concat_list_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
