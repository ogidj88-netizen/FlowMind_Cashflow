#!/usr/bin/env bash
set -euo pipefail

# FlowMind — Safe Python Writer v1.1
# Atomic write + python syntax validation.
#
# Usage:
#   tools/py_write_safe.sh <path> <<'PYFILE'
#   print("hello")
#   PYFILE
#
# Guarantees:
# - atomic write: temp -> mv
# - python3 -m py_compile validation
# - chmod +x if file starts with shebang

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <path>" >&2
  exit 2
fi

OUT="$1"
DIR="$(dirname "$OUT")"
mkdir -p "$DIR"

TMP="$(mktemp)"
cat > "$TMP"

python3 -m py_compile "$TMP" >/dev/null

if head -n 1 "$TMP" | grep -q '^#!'; then
  chmod +x "$TMP"
fi

mv -f "$TMP" "$OUT"
echo "[OK] py_write_safe wrote + syntax-validated: $OUT" >&2
