#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${1:-}"
MODE_ARG="${2:-}"

if [[ -z "${PROJECT_ID}" ]]; then
  echo "Usage: engine/qa/pre_qa_router_v1.sh <PROJECT_ID> [SHORT|LONG]"
  exit 1
fi

STATE_PATH="projects/${PROJECT_ID}/PROJECT_STATE.json"

echo "[QA ROUTER] Project: ${PROJECT_ID}"

if [[ ! -f "${STATE_PATH}" ]]; then
  echo "[FAIL] PROJECT_STATE.json not found"
  exit 1
fi

# read mode from state if not passed
if [[ -n "${MODE_ARG}" ]]; then
  MODE="${MODE_ARG}"
  echo "[QA ROUTER] Mode: ${MODE}"
else
  MODE="$(python3 - <<EOF
import json
p="${STATE_PATH}"
with open(p,"r") as f:
    s=json.load(f)
print(s.get("mode","NORMAL"))
EOF
)"
  echo "[QA ROUTER] Mode from STATE: ${MODE}"
fi

case "${MODE}" in
  SHORT)
    engine/qa/pre_qa_gate_short_v1.sh "${PROJECT_ID}"
    ;;
  LONG)
    engine/qa/pre_qa_gate_runner_v1.sh "${PROJECT_ID}"
    ;;
  *)
    echo "[FAIL] Unknown mode in PROJECT_STATE.json: ${MODE}"
    exit 1
    ;;
esac

# If gate passed -> mark qa_passed=true and auto finalize to FINAL_READY
echo "[QA ROUTER] Marking qa_passed=true + auto FINAL_READY"

# We must temporarily unlock state for writing (state_manager will re-lock)
chmod 644 "${STATE_PATH}" 2>/dev/null || true

python3 - <<EOF
import json
from pathlib import Path

state_path = Path("${STATE_PATH}")
s = json.loads(state_path.read_text())

s["qa_passed"] = True

# If already FINAL_READY -> keep
if s.get("phase") == "FINAL_READY":
    state_path.write_text(json.dumps(s, indent=2))
    print("[QA ROUTER] Already FINAL_READY (state updated qa_passed only)")
else:
    # set phase to FINAL_READY (forward move)
    s["phase"] = "FINAL_READY"
    state_path.write_text(json.dumps(s, indent=2))
    print("[QA ROUTER] Phase set to FINAL_READY")
EOF

# Re-lock (we enforce terminal lock even without Python imports)
chmod 444 "${STATE_PATH}" 2>/dev/null || true

echo "[QA ROUTER] DONE"
