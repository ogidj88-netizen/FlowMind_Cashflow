#!/usr/bin/env python3
"""
FlowMind Cashflow — Safe File Writer v1
Atomic write + backups + basic validation.
Usage:
  python3 tools/fm_write.py <path> --from-stdin [--backup] [--mkdir]
Examples:
  printf '%s' 'hello' | python3 tools/fm_write.py README.md --from-stdin --backup
  cat somefile | python3 tools/fm_write.py dispatcher/engine.py --from-stdin --backup --mkdir
"""

import argparse
import hashlib
import json
import os
import py_compile
import shutil
import sys
import tempfile
from pathlib import Path


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def validate_json(path: Path, text: str) -> None:
    try:
        json.loads(text)
    except Exception as e:
        raise SystemExit(f"[fm_write] JSON invalid for {path}: {e}")


def validate_py(path: Path, tmp_path: Path) -> None:
    try:
        py_compile.compile(str(tmp_path), doraise=True)
    except Exception as e:
        raise SystemExit(f"[fm_write] Python syntax invalid for {path}: {e}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="Destination file path (relative or absolute)")
    ap.add_argument("--from-stdin", action="store_true", help="Read file content from stdin")
    ap.add_argument("--backup", action="store_true", help="Create .bak copy if file exists")
    ap.add_argument("--mkdir", action="store_true", help="Create parent directories if needed")
    args = ap.parse_args()

    dst = Path(args.path).expanduser().resolve()

    if not args.from_stdin:
        raise SystemExit("[fm_write] Only --from-stdin is supported in v1 (to avoid terminal paste pitfalls).")

    content = sys.stdin.buffer.read()
    text = content.decode("utf-8", errors="strict")

    if args.mkdir:
        dst.parent.mkdir(parents=True, exist_ok=True)

    # Validate before writing
    if dst.suffix.lower() == ".json":
        validate_json(dst, text)

    # Prepare atomic write
    old_hash = None
    if dst.exists():
        old_hash = sha256_bytes(dst.read_bytes())

    with tempfile.NamedTemporaryFile("wb", delete=False, dir=str(dst.parent), prefix=dst.name + ".tmp.") as tf:
        tmp_path = Path(tf.name)
        tf.write(content)
        tf.flush()
        os.fsync(tf.fileno())

    # Validate Python syntax using tmp file
    if dst.suffix.lower() == ".py":
        validate_py(dst, tmp_path)

    # Backup
    if args.backup and dst.exists():
        bak = dst.with_suffix(dst.suffix + ".bak")
        shutil.copy2(dst, bak)

    # Replace atomically
    os.replace(str(tmp_path), str(dst))

    new_hash = sha256_bytes(dst.read_bytes())
    changed = "CHANGED" if (old_hash is None or old_hash != new_hash) else "UNCHANGED"

    print(f"[fm_write] OK {changed}: {dst}")
    print(f"[fm_write] sha256={new_hash}")


if __name__ == "__main__":
    main()
