#!/usr/bin/env bash
set -euo pipefail

# FlowMind — Dummy Final Runner v1 (canonical entry)
# Usage: engine/assembly/dummy_final_runner_v1.sh <PROJECT_ID> <DURATION_SECONDS>

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <PROJECT_ID> <DURATION_SECONDS>" >&2
  exit 2
fi

PROJECT_ID="$1"
DUR="$2"

if [[ ! -x engine/assembly/make_dummy_final_station_v1.sh ]]; then
  echo "[FAIL] missing: engine/assembly/make_dummy_final_station_v1.sh" >&2
  exit 3
fi

engine/assembly/make_dummy_final_station_v1.sh "$PROJECT_ID" "$DUR"

OUT="projects/${PROJECT_ID}/out/${PROJECT_ID}/final.mp4"
echo "[OK] DUMMY_FINAL_RUNNER done: $OUT"
