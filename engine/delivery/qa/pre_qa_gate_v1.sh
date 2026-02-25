#!/usr/bin/env bash
set -euo pipefail

# FlowMind — Pre-QA Gate v1.1
# Purpose: enforce final.mp4 standard BEFORE switching phase to QA.
#
# Usage:
#   engine/qa/pre_qa_gate_v1.sh <PROJECT_ID>
#
# On FAIL:
# - writes projects/<PROJECT_ID>/out/<PROJECT_ID>/halt_reason.txt
# - exits with code 42

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <PROJECT_ID>" >&2
  exit 2
fi

PROJECT_ID="$1"
FINAL="projects/${PROJECT_ID}/out/${PROJECT_ID}/final.mp4"
OUTDIR="projects/${PROJECT_ID}/out/${PROJECT_ID}"
REASON_FILE="${OUTDIR}/halt_reason.txt"

mkdir -p "$OUTDIR"

if [[ ! -x engine/qa/guard_final_standard_v1.sh ]]; then
  echo "[FAIL] missing: engine/qa/guard_final_standard_v1.sh" >&2
  echo "MISSING_GUARD: engine/qa/guard_final_standard_v1.sh" > "$REASON_FILE"
  exit 42
fi

if [[ ! -f "$FINAL" ]]; then
  echo "[FAIL] missing final: $FINAL" >&2
  echo "MISSING_FINAL: $FINAL" > "$REASON_FILE"
  exit 42
fi

set +e
engine/qa/guard_final_standard_v1.sh "$FINAL"
rc=$?
set -e

if [[ $rc -ne 0 ]]; then
  echo "[FAIL] PRE_QA_GATE blocked. guard_exit=$rc" >&2
  echo "FINAL_STANDARD_FAIL: guard_exit=$rc file=$FINAL" > "$REASON_FILE"
  exit 42
fi

rm -f "$REASON_FILE" >/dev/null 2>&1 || true
echo "[OK] PRE_QA_GATE PASS: $FINAL"
