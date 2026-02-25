#!/usr/bin/env python3
"""
FlowMind Cashflow — Final QA (deterministic)

Checks:
- final.mp4 exists
- size > 10KB
"""

from pathlib import Path


def run_final_qa(project_id: str) -> dict:
    base = Path(__file__).resolve().parents[2]
    project_dir = base / "out" / project_id
    final_path = project_dir / "final.mp4"

    report = {
        "qa_pass": False,
        "qa_report": {
            "pass": False,
            "final_video": {
                "found": final_path.exists(),
                "path": str(final_path),
            },
            "checks": {},
            "notes": [],
        },
    }

    if not final_path.exists():
        report["qa_report"]["notes"].append("final.mp4 missing")
        return report

    size = final_path.stat().st_size
    report["qa_report"]["checks"]["size_bytes"] = size

    if size < 10000:
        report["qa_report"]["notes"].append("file too small")
        return report

    report["qa_pass"] = True
    report["qa_report"]["pass"] = True
    return report
