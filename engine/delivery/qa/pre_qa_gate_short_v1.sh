#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="$1"
OUT_PATH="projects/${PROJECT_ID}/out/${PROJECT_ID}/final.mp4"

if [ ! -f "$OUT_PATH" ]; then
  echo "[FAIL] final.mp4 not found"
  exit 1
fi

# Отримуємо тривалість через ffprobe
DURATION=$(ffprobe -v error \
  -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 \
  "$OUT_PATH")

DURATION_INT=${DURATION%.*}

echo "[INFO] Duration: ${DURATION_INT} sec"

# SHORT дозволяємо 30–90 сек
if [ "$DURATION_INT" -lt 30 ] || [ "$DURATION_INT" -gt 90 ]; then
  echo "[FAIL] duration out of range (must be 30–90 sec)"
  exit 1
fi

echo "[PASS] SHORT pre-QA gate passed"
exit 0
