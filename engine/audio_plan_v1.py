#!/usr/bin/env python3
"""
FlowMind Cashflow — AUDIO_PLAN v1 (Silent Master Clock)

Purpose:
- Create AUDIO_PLAN.json that becomes the master timeline clock.
- For now: silent audio segments matching ASSEMBLY_PLAN timeline.
- Later: TTS segments will replace silent segments, but durations stay canonical.

Inputs:
- projects/<PROJECT_ID>/ASSEMBLY_PLAN.json
- projects/<PROJECT_ID>/SCRIPT.json (optional; used for metadata + future segmentation)

Outputs:
- projects/<PROJECT_ID>/AUDIO_PLAN.json
- (placeholder) assets/cache/<PROJECT_ID>/audio/master.wav
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def project_root() -> Path:
    return Path(os.getcwd()).resolve()


def resolve_project_dir(arg: str) -> Path:
    p = Path(arg)
    if p.exists() and p.is_dir():
        return p.resolve()
    return (project_root() / "projects" / arg).resolve()


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
    tmp.replace(path)


def load_optional_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    return read_json(path)


def main(argv: List[str]) -> int:
    if len(argv) < 2:
        print("Usage: python -m engine.audio_plan_v1 <PROJECT_ID|PROJECT_PATH>", file=sys.stderr)
        return 2

    project_dir = resolve_project_dir(argv[1])
    project_id = project_dir.name

    assembly_path = project_dir / "ASSEMBLY_PLAN.json"
    if not assembly_path.exists():
        print(f"[AUDIO_PLAN FAIL] Missing: {assembly_path}", file=sys.stderr)
        return 2

    script_path = project_dir / "SCRIPT.json"
    assembly = read_json(assembly_path)
    script = load_optional_json(script_path)

    timeline = assembly.get("timeline", [])
    if not isinstance(timeline, list) or not timeline:
        print("[AUDIO_PLAN FAIL] ASSEMBLY_PLAN has empty timeline", file=sys.stderr)
        return 2

    total_duration = float(assembly.get("total_duration_sec", 0) or 0)
    if total_duration <= 0:
        total_duration = sum(float(x.get("duration_sec", 0) or 0) for x in timeline)

    # Build silent segments aligned to timeline
    segments: List[Dict[str, Any]] = []
    for item in timeline:
        scene_id = item.get("scene_id")
        label = item.get("label")
        start_sec = float(item.get("start_sec", 0) or 0)
        end_sec = float(item.get("end_sec", 0) or 0)
        dur = float(item.get("duration_sec", max(0.0, end_sec - start_sec)) or 0)

        if not scene_id or dur <= 0:
            continue

        segments.append({
            "segment_id": f"seg_{scene_id}",
            "scene_id": scene_id,
            "label": label,
            "type": "SILENCE",
            "start_sec": round(start_sec, 3),
            "end_sec": round(start_sec + dur, 3),
            "duration_sec": round(dur, 3),
            "text": None,
            "audio_path": None,
            "notes": {
                "source": "ASSEMBLY_PLAN",
            }
        })

    if not segments:
        print("[AUDIO_PLAN FAIL] No segments created", file=sys.stderr)
        return 2

    seg_total = round(sum(s["duration_sec"] for s in segments), 3)
    plan_total = round(float(total_duration), 3)

    # Gate: must match within tolerance (dummy pipeline uses exact seconds; keep small tolerance)
    tolerance = 0.25
    if abs(seg_total - plan_total) > tolerance:
        print(f"[AUDIO_PLAN FAIL] Duration mismatch seg_total={seg_total} plan_total={plan_total}", file=sys.stderr)
        return 2

    audio_cache = (project_root() / "assets" / "cache" / project_id / "audio").resolve()
    audio_cache.mkdir(parents=True, exist_ok=True)
    master_wav = audio_cache / "master.wav"

    out = {
        "project_id": project_id,
        "generated_at": utc_now_iso(),
        "mode": "SILENT_CLOCK_V1",
        "source": {
            "assembly_plan": str(assembly_path),
            "script": str(script_path) if script else None,
        },
        "audio_spec": {
            "sample_rate": 48000,
            "channels": 2,
            "format": "wav",
        },
        "master_clock": {
            "total_duration_sec": plan_total,
            "tolerance_sec": tolerance,
            "segments_total_sec": seg_total,
        },
        "outputs": {
            "master_wav_placeholder": str(master_wav),
        },
        "segments": segments,
        "script_meta": {
            "title": (script or {}).get("title") if script else None,
            "hook": (script or {}).get("hook") if script else None,
        },
    }

    out_path = project_dir / "AUDIO_PLAN.json"
    write_json(out_path, out)
    print(f"[AUDIO_PLAN PASS] total_duration_sec={plan_total} written: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
