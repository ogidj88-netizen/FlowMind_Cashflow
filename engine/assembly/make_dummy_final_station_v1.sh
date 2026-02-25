#!/usr/bin/env bash
set -euo pipefail

# FlowMind — Assembly Station: Make Dummy Final v1
# Usage: engine/assembly/make_dummy_final_station_v1.sh <PROJECT_ID> <DURATION_SECONDS>

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <PROJECT_ID> <DURATION_SECONDS>" >&2
  exit 2
fi

PROJECT_ID="$1"
DUR="$2"
OUT="projects/${PROJECT_ID}/out/${PROJECT_ID}/final.mp4"

if [[ ! -x tools/ffmpeg_make_dummy_final_v1.sh ]]; then
  echo "[FAIL] tools/ffmpeg_make_dummy_final_v1.sh missing or not executable" >&2
  exit 3
fi

tools/ffmpeg_make_dummy_final_v1.sh "$OUT" "$DUR"
echo "[OK] ASSEMBLY dummy final ready: $OUT"
