#!/usr/bin/env python3
"""
FlowMind Cashflow — Assembly v1 (minimal deterministic)

Responsibility:
- Verify final.mp4 exists in out/<PROJECT_ID>/
- Do NOT modify state (dispatcher controls state)
- Raise exception if missing
"""

import os
from pathlib import Path


def run_assembly(project_id: str) -> None:
    base = Path(__file__).resolve().parents[1]
    final_path = base / "out" / project_id / "final.mp4"

    print(f"[ASSEMBLY] Project: {project_id}")
    print(f"[ASSEMBLY] Expected final path: {final_path}")

    if not final_path.exists():
        raise RuntimeError("final.mp4 not found after assembly")

    size = final_path.stat().st_size
    if size < 10000:
        raise RuntimeError("final.mp4 too small — invalid render")

    print("[ASSEMBLY] Final file verified.")
    print("[ASSEMBLY] DONE.")
