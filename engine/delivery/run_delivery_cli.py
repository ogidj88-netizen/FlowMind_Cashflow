#!/usr/bin/env python3
"""
FlowMind Cashflow — Delivery CLI v3 (Hard-Gated)

Cannot run unless invoked by Dispatcher.
"""

from __future__ import annotations

import os
import sys
import json
from datetime import datetime, timezone

from engine.artifacts import artifacts
from engine.delivery.qa.qa_finalize_v1 import run_final_qa


if os.getenv("FLOWMIND_ENTRY") != "DISPATCHER":
    raise RuntimeError("Delivery direct execution forbidden. Use Dispatcher.")


def now_utc():
    return datetime.now(timezone.utc).isoformat()


def main():
    if len(sys.argv) != 2:
        raise SystemExit(1)

    project_id = sys.argv[1]
    a = artifacts(project_id)

    with open(a.manifest_json, "r", encoding="utf-8") as f:
        state = json.load(f)

    if state.get("status") != "FINAL_READY":
        raise RuntimeError("Delivery requires FINAL_READY state.")

    qa_result = run_final_qa(project_id)

    if qa_result["pass"]:
        state["status"] = "QA_PASSED"
    else:
        state["status"] = "QA_FAILED"

    state["last_update"] = now_utc()

    with open(a.manifest_json, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

    print(json.dumps({
        "project_id": project_id,
        "qa_pass": qa_result["pass"],
        "qa_report": qa_result,
    }, indent=2))

    if not qa_result["pass"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
