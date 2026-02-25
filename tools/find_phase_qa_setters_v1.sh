#!/usr/bin/env bash
set -euo pipefail

# FlowMind — Finder v1: locate code paths that set phase to QA
# Safe: READ-ONLY. No modifications.
#
# Usage:
#   tools/find_phase_qa_setters_v1.sh

ROOT="$(pwd)"

echo "[INFO] Root: $ROOT"
echo "[INFO] Looking for phase setters to QA..."

if command -v rg >/dev/null 2>&1; then
  RG="rg -n --hidden --no-ignore-vcs"
  echo "[INFO] Using ripgrep (rg)"
else
  RG="grep -RIn --exclude-dir=.git"
  echo "[WARN] rg not found, falling back to grep"
fi

# High-signal patterns (most likely in dispatcher/engine/state files)
patterns=(
  'Phase now:\s*QA'
  'phase\s*(now)?\s*[:=]\s*QA'
  '"QA"'
  "update_phase\\(.*QA"
  "set_phase\\(.*QA"
  "PHASE.*QA"
  "NEXT_PHASE.*QA"
  "to\\s*'QA'"
  'QA\b'
)

echo
echo "===================="
echo "[PASS 1] High-signal search (QA setters)"
echo "===================="
for p in "${patterns[@]}"; do
  echo
  echo "----- pattern: $p"
  # shellcheck disable=SC2086
  $RG "$p" dispatcher engine tools 2>/dev/null || true
done

echo
echo "===================="
echo "[PASS 2] Where PROJECT_STATE.json is written/updated"
echo "===================="
# shellcheck disable=SC2086
$RG "PROJECT_STATE\.json|project_state|state\.json|write_state|save_state|commit_phase|phase_transition|HALT|halt_reason" dispatcher engine tools 2>/dev/null || true

echo
echo "[DONE] If you see multiple hits: pick the one that actually prints 'Phase now: QA' (or updates state to QA)."
