#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FlowMind Cashflow — Autopilot Tick v3 (STRICT FULL PIPE)

1) Telegram Listener
2) Approval Bridge
3) Finalize Bridge

Idempotent.
Safe.
No hidden transitions.
"""

import sys
from pathlib import Path


THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[1]

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def main(argv):

    if len(argv) != 2:
        print("Usage: python tools/autopilot_tick.py <PROJECT_ID>")
        return 1

    project_id = argv[1]

    # LISTENER
    try:
        import engine.telegram_listener_v1 as listener
        listener.main()
    except Exception as e:
        print("[AUTOPILOT] listener error:", e)

    # APPROVAL BRIDGE
    try:
        from dispatcher.approval_bridge_v1 import run as approval_run
        approval_run(project_id)
    except Exception as e:
        print("[AUTOPILOT] approval error:", e)

    # FINALIZE BRIDGE
    try:
        from dispatcher.finalize_bridge_v1 import run as finalize_run
        finalize_run(project_id)
    except Exception as e:
        print("[AUTOPILOT] finalize error:", e)

    print("[AUTOPILOT] DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
