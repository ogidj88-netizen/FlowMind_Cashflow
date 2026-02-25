#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path


def pack_path(project_id: str) -> Path:
    return Path(f"projects/{project_id}/DELIVERY_PACK.json")


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: approve_delivery_pack.py <PROJECT_ID>", file=sys.stderr)
        return 2

    project_id = sys.argv[1].strip()
    p = pack_path(project_id)

    if not p.exists():
        print(f"[FAIL] DELIVERY_PACK.json not found: {p}", file=sys.stderr)
        return 3

    # Ensure writable during update
    try:
        os.chmod(p, 0o644)
    except Exception:
        pass

    data = json.loads(p.read_text(encoding="utf-8"))

    # Minimal contract enforcement
    data.setdefault("notes", {})
    data["notes"]["telegram_approved"] = True
    data["notes"]["upload_ready"] = True

    # Write back deterministically
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Lock pack (read-only) after approval
    os.chmod(p, 0o444)

    print(f"[APPROVED] {project_id} -> telegram_approved=true, upload_ready=true (DELIVERY_PACK locked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
