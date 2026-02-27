#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FlowMind Cashflow — Autopilot Loop v1

Runs Autopilot Tick every N seconds.

Usage:
  python tools/autopilot_loop.py FM_TEST 10
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def main(argv: list[str]) -> int:
    if len(argv) not in (2, 3):
        print("Usage: python tools/autopilot_loop.py <PROJECT_ID> [interval_sec]", file=sys.stderr)
        return 2

    project_id = argv[1]
    interval = int(argv[2]) if len(argv) == 3 else 10

    from tools.autopilot_tick import main as tick_main  # type: ignore

    print(f"[AUTOPILOT] loop start project={project_id} interval={interval}s (Ctrl+C to stop)")
    while True:
        tick_main(["tools.autopilot_tick", project_id])
        time.sleep(interval)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
