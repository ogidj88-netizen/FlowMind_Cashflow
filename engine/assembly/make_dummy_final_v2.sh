#!/usr/bin/env bash
set -euo pipefail

# FlowMind Cashflow — Dummy Final Generator v2.2
# Purpose: generate a definitely "non-tiny" valid mp4 for Delivery selftest.
#
# Output (canonical):
#   out/<PROJECT_ID>/final.mp4
#
# Usage:
#   bash engine/assembly/make_dummy_final_v2.sh <PROJECT_ID>

if [[ $# -ne 1 ]]; then
  echo "Usage: bash engine/assembly/make_dummy_final_v2.sh <PROJECT_ID>" >&2
  exit 2
fi

PROJECT_ID="$1"
REPO_ROOT="$(pwd)"
OUT_DIR="${REPO_ROOT}/out/${PROJECT_ID}"
FINAL_MP4="${OUT_DIR}/final.mp4"

mkdir -p "${OUT_DIR}"

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "[ERR] ffmpeg not found. Install: sudo apt-get update && sudo apt-get install -y ffmpeg" >&2
  exit 3
fi

# Key idea:
# - black compresses too well → tiny files
# - use a test pattern (smptebars) so file size is guaranteed >200KB
# - 60 seconds to be safe
#
# Encoding: 1080p 30fps CFR, h264 yuv420p, AAC 48k stereo, faststart
ffmpeg -y \
  -f lavfi -i "smptebars=size=1920x1080:rate=30" \
  -f lavfi -i "anullsrc=channel_layout=stereo:sample_rate=48000" \
  -t 60 \
  -c:v libx264 -pix_fmt yuv420p -r 30 -vf "setsar=1" \
  -b:v 1500k -maxrate 1500k -bufsize 3000k \
  -c:a aac -ar 48000 -ac 2 -b:a 128k \
  -movflags +faststart \
  "${FINAL_MP4}" >/dev/null 2>&1

if [[ ! -f "${FINAL_MP4}" ]]; then
  echo "[ERR] final.mp4 was not created: ${FINAL_MP4}" >&2
  exit 4
fi

BYTES="$(stat -c%s "${FINAL_MP4}" 2>/dev/null || echo 0)"
echo "[OK] Created ${FINAL_MP4} (${BYTES} bytes)"

if [[ "${BYTES}" -lt 200000 ]]; then
  echo "[WARN] File is still <200KB; investigate ffmpeg build/settings." >&2
fi
