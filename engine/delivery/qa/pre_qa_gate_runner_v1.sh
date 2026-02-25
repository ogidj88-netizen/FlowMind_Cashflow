#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="$1"
ROOT="projects/${PROJECT_ID}"
FINAL="${ROOT}/out/${PROJECT_ID}/final.mp4"

fail() {
  echo "[FAIL] $1"
  exit 15
}

if [[ ! -f "$FINAL" ]]; then
  fail "final.mp4 not found"
fi

# ---- ffprobe basic check ----
if ! ffprobe -v error "$FINAL" >/dev/null 2>&1; then
  fail "ffprobe failed (corrupted file)"
fi

# ---- video stream ----
VIDEO_STREAM=$(ffprobe -v error -select_streams v:0 -show_entries stream=codec_type -of csv=p=0 "$FINAL" || true)
if [[ "$VIDEO_STREAM" != "video" ]]; then
  fail "no video stream"
fi

# ---- audio stream ----
AUDIO_STREAM=$(ffprobe -v error -select_streams a:0 -show_entries stream=codec_type -of csv=p=0 "$FINAL" || true)
if [[ "$AUDIO_STREAM" != "audio" ]]; then
  fail "no audio stream"
fi

# ---- duration check (7–9 min) ----
DURATION=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$FINAL")
DURATION_INT=${DURATION%.*}

if (( DURATION_INT < 420 || DURATION_INT > 540 )); then
  fail "duration out of range (must be 7–9 min)"
fi

# ---- pixel format ----
PIX_FMT=$(ffprobe -v error -select_streams v:0 -show_entries stream=pix_fmt -of csv=p=0 "$FINAL")
if [[ "$PIX_FMT" != "yuv420p" ]]; then
  fail "pixel format must be yuv420p"
fi

# ---- fps check (30) ----
FPS=$(ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate -of csv=p=0 "$FINAL")
if [[ "$FPS" != "30/1" && "$FPS" != "30000/1000" ]]; then
  fail "fps must be 30"
fi

echo "[QA PASS] All checks passed."
exit 0
