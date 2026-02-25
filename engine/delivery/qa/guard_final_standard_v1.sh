#!/usr/bin/env bash
set -euo pipefail

# FlowMind — Final Standard Guard v1 (FFmpeg Stability Standard v1.2)
# Enforces:
# - video: 1920x1080, r_frame_rate=30/1, avg_frame_rate=30/1
# - audio: present, sample_rate=48000, channels=2
#
# Usage:
#   engine/qa/guard_final_standard_v1.sh <FINAL_MP4_PATH>

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <FINAL_MP4_PATH>" >&2
  exit 2
fi

P="$1"

if [[ ! -f "$P" ]]; then
  echo "[FAIL] final file not found: $P" >&2
  exit 3
fi

command -v ffprobe >/dev/null || { echo "[FAIL] ffprobe not found" >&2; exit 4; }

vinfo="$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,avg_frame_rate -of default=nw=1 "$P" || true)"
ainfo="$(ffprobe -v error -select_streams a:0 -show_entries stream=sample_rate,channels -of default=nw=1 "$P" || true)"

echo "$vinfo" | grep -q '^width=' || { echo "[FAIL] no video stream" >&2; exit 10; }

echo "$vinfo" | grep -q '^width=1920$' || { echo "[FAIL] width!=1920" >&2; echo "$vinfo" >&2; exit 11; }
echo "$vinfo" | grep -q '^height=1080$' || { echo "[FAIL] height!=1080" >&2; echo "$vinfo" >&2; exit 12; }
echo "$vinfo" | grep -q '^r_frame_rate=30/1$' || { echo "[FAIL] r_frame_rate!=30/1" >&2; echo "$vinfo" >&2; exit 13; }
echo "$vinfo" | grep -q '^avg_frame_rate=30/1$' || { echo "[FAIL] avg_frame_rate!=30/1" >&2; echo "$vinfo" >&2; exit 14; }

echo "$ainfo" | grep -q '^sample_rate=' || { echo "[FAIL] no audio stream" >&2; exit 15; }
echo "$ainfo" | grep -q '^sample_rate=48000$' || { echo "[FAIL] sample_rate!=48000" >&2; echo "$ainfo" >&2; exit 16; }
echo "$ainfo" | grep -q '^channels=2$' || { echo "[FAIL] channels!=2" >&2; echo "$ainfo" >&2; exit 17; }

echo "[OK] FINAL_STANDARD_GUARD PASS: $P"
