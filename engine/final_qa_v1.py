#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FlowMind Cashflow — FINAL QA v1 (strict, minimal)
Validates out/<PROJECT_ID>/final.mp4 against core invariants:
- exists, size >= min_bytes
- duration ~= expected (from AUDIO_RENDER master_wav)
- video: 1920x1080, 30 fps (or very close), h264, yuv420p
- audio: aac, 48kHz, 2ch
Writes: projects/<PROJECT_ID>/FINAL_QA.json

Usage:
  python -m engine.final_qa_v1 FM_TEST
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Tuple


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _run(cmd: list[str]) -> Tuple[int, str]:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return p.returncode, p.stdout


def _ffprobe_json(path: Path) -> Dict[str, Any]:
    cmd = ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)]
    rc, out = _run(cmd)
    if rc != 0:
        raise RuntimeError(f"ffprobe failed rc={rc}\n{out}")
    return json.loads(out)


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _probe_duration_sec(media: Path) -> float:
    d = _ffprobe_json(media)
    return float(d["format"]["duration"])


def _get_stream(d: Dict[str, Any], codec_type: str) -> Dict[str, Any]:
    for s in d.get("streams", []):
        if s.get("codec_type") == codec_type:
            return s
    return {}


def _approx(a: float, b: float, tol: float) -> bool:
    return abs(a - b) <= tol


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: python -m engine.final_qa_v1 <PROJECT_ID>", file=sys.stderr)
        return 2

    project_id = argv[1]
    project_dir = (Path("projects") / project_id).resolve()
    out_dir = (Path("out") / project_id).resolve()
    final_mp4 = out_dir / "final.mp4"

    # thresholds (cashflow minimal)
    min_bytes = 2_000_000  # 2MB – kills "dead" files like 169KB
    dur_tol = 0.25         # seconds
    fps_tol = 0.5          # fps
    expected_w = 1920
    expected_h = 1080
    expected_sr = 48000
    expected_ch = 2

    report: Dict[str, Any] = {
        "project_id": project_id,
        "generated_at": _utc_now_iso(),
        "inputs": {"final_mp4": str(final_mp4)},
        "checks": [],
        "pass": False,
    }

    def add_check(name: str, ok: bool, details: Any) -> None:
        report["checks"].append({"name": name, "ok": bool(ok), "details": details})

    if not final_mp4.exists():
        add_check("exists_final_mp4", False, "missing")
        _write(project_dir / "FINAL_QA.json", report)
        print("[FAIL] final.mp4 missing", file=sys.stderr)
        return 3

    size = final_mp4.stat().st_size
    add_check("min_size_bytes", size >= min_bytes, {"size": size, "min": min_bytes})

    # Expected duration comes from AUDIO_RENDER master wav
    audio_render = project_dir / "AUDIO_RENDER.json"
    if not audio_render.exists():
        add_check("exists_AUDIO_RENDER", False, "missing AUDIO_RENDER.json")
        _write(project_dir / "FINAL_QA.json", report)
        print("[FAIL] missing AUDIO_RENDER.json", file=sys.stderr)
        return 4

    ar = _read_json(audio_render)
    master_wav = Path((ar.get("outputs") or {}).get("master_wav") or "").expanduser().resolve()
    if not master_wav.exists():
        add_check("exists_master_wav", False, str(master_wav))
        _write(project_dir / "FINAL_QA.json", report)
        print("[FAIL] master.wav missing", file=sys.stderr)
        return 5

    try:
        exp_dur = float(_probe_duration_sec(master_wav))
        d = _ffprobe_json(final_mp4)
        act_dur = float(d["format"]["duration"])
        add_check("duration_matches_master_wav", _approx(act_dur, exp_dur, dur_tol), {"expected": exp_dur, "actual": act_dur, "tol": dur_tol})

        v = _get_stream(d, "video")
        a = _get_stream(d, "audio")

        # video checks
        w = int(v.get("width") or 0)
        h = int(v.get("height") or 0)
        add_check("video_resolution", (w == expected_w and h == expected_h), {"w": w, "h": h, "expected": [expected_w, expected_h]})

        pix = str(v.get("pix_fmt") or "")
        add_check("video_pix_fmt_yuv420p", pix == "yuv420p", {"pix_fmt": pix})

        vcodec = str(v.get("codec_name") or "")
        add_check("video_codec_h264", vcodec in ("h264", "libx264"), {"codec": vcodec})

        # fps (prefer avg_frame_rate)
        fps = 0.0
        afr = v.get("avg_frame_rate") or "0/0"
        try:
            n, dnm = afr.split("/")
            fps = float(n) / float(dnm) if float(dnm) != 0 else 0.0
        except Exception:
            fps = 0.0
        add_check("video_fps_30", abs(fps - 30.0) <= fps_tol, {"fps": fps, "tol": fps_tol})

        # audio checks
        acodec = str(a.get("codec_name") or "")
        add_check("audio_codec_aac", acodec == "aac", {"codec": acodec})

        sr = int(a.get("sample_rate") or 0)
        add_check("audio_sample_rate_48k", sr == expected_sr, {"sr": sr, "expected": expected_sr})

        ch = int(a.get("channels") or 0)
        add_check("audio_channels_2", ch == expected_ch, {"channels": ch, "expected": expected_ch})

    except Exception as e:
        add_check("ffprobe_parse", False, str(e))

    passed = all(c["ok"] for c in report["checks"])
    report["pass"] = passed

    _write(project_dir / "FINAL_QA.json", report)

    if not passed:
        print("[FAIL] FINAL_QA failed. See projects/<PROJECT>/FINAL_QA.json", file=sys.stderr)
        return 10

    print(f"[FINAL_QA PASS] final={final_mp4}")
    return 0


def _write(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
