#!/usr/bin/env bash
set -euo pipefail

# FlowMind — Safe Shell Writer v1.1
# Atomic write + bash syntax validation.
#
# Usage:
#   tools/sh_write_safe.sh <path> <<'SH'
#   #!/usr/bin/env bash
#   set -euo pipefail
#   echo "hello"
#   SH
#
# Guarantees:
# - atomic write: temp -> mv
# - bash -n syntax validation
# - chmod +x on the final file

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <path>" >&2
  exit 2
fi

OUT="$1"
DIR="$(dirname "$OUT")"
mkdir -p "$DIR"

TMP="$(mktemp "${DIR}/._tmp_sh_write_safe.XXXXXX")"

# Read stdin into temp
cat > "$TMP"

# Hard guard: must start with shebang
head -n 1 "$TMP" | grep -q '^#!/' || {
  echo "[FAIL] script must start with shebang (#!/...)" >&2
  rm -f "$TMP"
  exit 3
}

# Syntax check (bash)
bash -n "$TMP" || {
  echo "[FAIL] bash syntax invalid: $OUT" >&2
  rm -f "$TMP"
  exit 4
}

chmod +x "$TMP"
mv -f "$TMP" "$OUT"

echo "[OK] sh_write_safe wrote + syntax-validated: $OUT"
