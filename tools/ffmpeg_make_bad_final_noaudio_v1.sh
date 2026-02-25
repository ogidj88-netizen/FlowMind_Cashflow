#!/usr/bin/env bash
set -euo pipefail

# FlowMind — BAD Final Generator (NO AUDIO) v1
# Purpose: simulate QA gate failure.

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <OUT_MP4> <DURATION_SECONDS>" >&2
  exit 2
fi

OUT_MP4="$1"
DUR="$2"

mkdir -p "$(dirname "$OUT_MP4")"
TMP_MP4="${OUT_MP4}.tmp.$RANDOM.$RANDOM.mp4"

ffmpeg -hide_banner -y \
  -f lavfi -i "color=c=black:s=1920x1080:r=30" \
  -t "$DUR" \
  -c:v libx264 -pix_fmt yuv420p -r 30 -vsync cfr -preset veryfast -crf 23 \
  -movflags +faststart \
  -vf "setsar=1" \
  -threads 2 \
  "$TMP_MP4"

mv -f "$TMP_MP4" "$OUT_MP4"
echo "[OK] BAD final created (no audio): $OUT_MP4"
