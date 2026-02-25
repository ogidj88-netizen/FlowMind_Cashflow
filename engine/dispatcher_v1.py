#!/usr/bin/env python3
"""
FlowMind Cashflow — Dispatcher v1 (deterministic, file-based)

Rules:
- Single source of truth: out/<PROJECT_ID>/PROJECT_STATE.json
- Full file writes only (whole JSON each time)
- State transitions logged in out/<PROJECT_ID>/state_history.log
- No subprocess orchestration; direct Python calls
- .env auto-load from repo root
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


# -----------------------
# ENV AUTO-LOAD (repo/.env)
# -----------------------
def load_env() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    env_path = repo_root / ".env"
    if not env_path.exists():
        return

    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        if not key:
            continue
        # do not override already-exported vars
        os.environ.setdefault(key, value)


load_env()


# -----------------------
# Paths / IO
# -----------------------
def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def project_dir(project_id: str) -> Path:
    return repo_root() / "out" / project_id


def state_path(project_id: str) -> Path:
    return project_dir(project_id) / "PROJECT_STATE.json"


def history_path(project_id: str) -> Path:
    return project_dir(project_id) / "state_history.log"


def final_video_path(project_id: str) -> Path:
    return project_dir(project_id) / "final.mp4"


def write_json_full(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def append_history(project_id: str, frm: str, to: str, reason: str) -> None:
    hp = history_path(project_id)
    hp.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "timestamp": utc_now_iso(),
        "from": frm,
        "to": to,
        "reason": reason,
    }
    with open(hp, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


# -----------------------
# State model
# -----------------------
@dataclass
class ProjectState:
    project_id: str
    status: str
    created_at: str
    last_update: str
    final_video: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "project_id": self.project_id,
            "status": self.status,
            "created_at": self.created_at,
            "last_update": self.last_update,
        }
        if self.final_video:
            d["final_video"] = self.final_video
        return d


def ensure_state(project_id: str) -> ProjectState:
    sp = state_path(project_id)
    if sp.exists():
        data = json.loads(sp.read_text(encoding="utf-8"))
        return ProjectState(
            project_id=data["project_id"],
            status=data.get("status", "CREATED"),
            created_at=data.get("created_at", utc_now_iso()),
            last_update=data.get("last_update", utc_now_iso()),
            final_video=data.get("final_video"),
        )

    # create fresh
    now = utc_now_iso()
    st = ProjectState(project_id=project_id, status="CREATED", created_at=now, last_update=now, final_video=str(final_video_path(project_id)))
    write_json_full(sp, st.to_dict())
    return st


def set_status(project_id: str, new_status: str, reason: str) -> ProjectState:
    st = ensure_state(project_id)
    old = st.status
    st.status = new_status
    st.last_update = utc_now_iso()
    # keep canonical final_video path always present after CREATED
    st.final_video = str(final_video_path(project_id))
    write_json_full(state_path(project_id), st.to_dict())
    append_history(project_id, old, new_status, reason)
    return st


def mark_failed(project_id: str, reason: str) -> None:
    # never crash if state missing — create it
    set_status(project_id, "QA_FAILED", reason)


# -----------------------
# Stations
# -----------------------
def run_assembly(project_id: str) -> None:
    # Local import to avoid circulars at module load
    from engine.assembly_v1 import run_assembly  # type: ignore

    run_assembly(project_id)


def run_delivery(project_id: str) -> Dict[str, Any]:
    from engine.delivery.router import run_delivery  # type: ignore

    return run_delivery(project_id)


# -----------------------
# Dispatcher logic
# -----------------------
def dispatcher_logic(project_id: str) -> int:
    st = ensure_state(project_id)
    print(f"[DISPATCHER] Current status: {st.status}")

    # 1) CREATED -> ASSEMBLY_STARTED
    if st.status == "CREATED":
        set_status(project_id, "ASSEMBLY_STARTED", "Assembly triggered")
        print("[DISPATCHER] Running Assembly...")
        run_assembly(project_id)
        # assembly_v1 should detect final.mp4 and set FINAL_READY itself OR we do it here:
        if final_video_path(project_id).exists():
            set_status(project_id, "FINAL_READY", "Final file detected")
        st = ensure_state(project_id)
        print(f"[DISPATCHER] Current status: {st.status}")

    # 2) FINAL_READY -> Delivery QA
    if st.status == "FINAL_READY":
        print("[DISPATCHER] Running Delivery...")
        qa = run_delivery(project_id)

        # delivery router returns {"qa_pass": bool, ...} — normalize
        qa_pass = bool(qa.get("qa_pass") or qa.get("pass") or qa.get("qa_report", {}).get("pass"))
        if qa_pass:
            set_status(project_id, "QA_PASSED", "Delivery PASS")
            print("[DISPATCHER] Completed.")
            print(json.dumps(qa, ensure_ascii=False, indent=2))
            return 0

        set_status(project_id, "QA_FAILED", "Delivery FAIL")
        print(json.dumps(qa, ensure_ascii=False, indent=2))
        return 2

    # 3) QA_PASSED or QA_FAILED -> no-op
    if st.status in {"QA_PASSED", "QA_FAILED"}:
        print("[DISPATCHER] No action.")
        return 0 if st.status == "QA_PASSED" else 2

    # 4) ASSEMBLY_STARTED -> attempt to continue if final exists
    if st.status == "ASSEMBLY_STARTED":
        if final_video_path(project_id).exists():
            set_status(project_id, "FINAL_READY", "Final file detected")
            print("[DISPATCHER] Detected final.mp4 -> FINAL_READY")
            return dispatcher_logic(project_id)
        print("[DISPATCHER] Assembly in progress / final missing.")
        return 1

    print(f"[DISPATCHER] Unknown status: {st.status}")
    return 1


def resume(project_id: str, status: str) -> int:
    set_status(project_id, status, f"Resumed to {status}")
    print(f"[DISPATCHER] Resumed to {status}")
    st = ensure_state(project_id)
    print(f"[DISPATCHER] Current status: {st.status}")
    if status == "FINAL_READY":
        qa = run_delivery(project_id)
        print(json.dumps(qa, ensure_ascii=False, indent=2))
        return 0 if bool(qa.get("qa_pass") or qa.get("qa_report", {}).get("pass")) else 2
    return 0


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("project_id")
    p.add_argument("--resume", default=None, help="Force status then run minimal continuation (e.g. FINAL_READY)")
    args = p.parse_args()

    try:
        if args.resume:
            code = resume(args.project_id, args.resume)
        else:
            code = dispatcher_logic(args.project_id)
        sys.exit(code)
    except Exception as e:
        msg = str(e) or e.__class__.__name__
        print(f"[DISPATCHER] CRASH: {msg}", file=sys.stderr)
        try:
            mark_failed(args.project_id, f"CRASH: {msg}")
        except Exception:
            pass
        raise


if __name__ == "__main__":
    main()
