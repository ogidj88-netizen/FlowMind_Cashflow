#!/usr/bin/env python3
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone


def run(cmd):
    r = subprocess.run(cmd, check=False)
    return r.returncode


def state_path(project_id: str) -> Path:
    return Path(f"projects/{project_id}/PROJECT_STATE.json")


def delivery_pack_path(project_id: str) -> Path:
    return Path(f"projects/{project_id}/DELIVERY_PACK.json")


def final_video_path(project_id: str) -> Path:
    return Path(f"projects/{project_id}/out/{project_id}/final.mp4")


def read_json(p: Path) -> dict:
    return json.loads(p.read_text())


def write_json(p: Path, obj: dict) -> None:
    p.write_text(json.dumps(obj, indent=2))


def show_status(project_id: str) -> int:
    p = state_path(project_id)
    if not p.exists():
        print(f"[FAIL] state not found: {p}")
        return 2

    try:
        s = read_json(p)
    except Exception as e:
        print(f"[FAIL] cannot read JSON: {e}")
        return 3

    phase = s.get("phase")
    mode = s.get("mode")
    qa = s.get("qa_passed")
    locked = s.get("mode_locked")

    try:
        st = p.stat()
        writable = bool(st.st_mode & 0o200)
    except Exception:
        writable = None

    print(f"[STATUS] project_id={project_id}")
    print(f"[STATUS] phase={phase}")
    print(f"[STATUS] mode={mode}")
    print(f"[STATUS] qa_passed={qa}")
    print(f"[STATUS] mode_locked={locked}")
    print(f"[STATUS] state_writable={writable}  (False means read-only)")
    return 0


def help_text() -> None:
    print("FlowMind Cashflow — control panel")
    print("")
    print("Commands:")
    print("  python3 fm.py qa <PROJECT_ID>      # run pre-QA router (SHORT/LONG gate)")
    print("  python3 fm.py status <PROJECT_ID>  # show state summary")
    print("  python3 fm.py done <PROJECT_ID>    # qa + status (one-shot)")
    print("  python3 fm.py pack <PROJECT_ID>    # create DELIVERY_PACK.json (FINAL_READY only)")
    print("  python3 fm.py help                 # show this help")
    print("")
    print("Aliases (if added to ~/.bashrc):")
    print("  fmqa <PROJECT_ID>")
    print("  fmst <PROJECT_ID>")
    print("  fmdone <PROJECT_ID>")
    print("  fmpack <PROJECT_ID>")


def make_pack(project_id: str) -> int:
    sp = state_path(project_id)
    if not sp.exists():
        print(f"[FAIL] state not found: {sp}")
        return 2

    state = read_json(sp)

    if state.get("phase") != "FINAL_READY":
        print(f"[FAIL] phase must be FINAL_READY, got: {state.get('phase')}")
        return 3

    vp = final_video_path(project_id)
    if not vp.exists():
        print(f"[FAIL] final video not found: {vp}")
        return 4

    created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    pack = {
        "project_id": project_id,
        "created_at": created_at,
        "phase": state.get("phase"),
        "mode": state.get("mode"),
        "qa_passed": state.get("qa_passed"),
        "paths": {
            "state": str(sp),
            "final_video": str(vp),
        },
        "notes": {
            "upload_ready": False,
            "telegram_approved": False,
        }
    }

    dp = delivery_pack_path(project_id)
    write_json(dp, pack)
    print(f"[PACK] written: {dp}")
    return 0


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "help":
        help_text()
        sys.exit(0)

    if len(sys.argv) < 3:
        help_text()
        sys.exit(1)

    action = sys.argv[1]
    project_id = sys.argv[2]

    if action == "qa":
        sys.exit(run(["engine/qa/pre_qa_router_v1.sh", project_id]))

    if action == "status":
        sys.exit(show_status(project_id))

    if action == "done":
        code = run(["engine/qa/pre_qa_router_v1.sh", project_id])
        if code != 0:
            print(f"[DONE] QA failed with code={code}")
            sys.exit(code)
        print("[DONE] QA passed. Showing status:")
        sys.exit(show_status(project_id))

    if action == "pack":
        sys.exit(make_pack(project_id))

    print(f"Unknown action: {action}")
    help_text()
    sys.exit(2)


if __name__ == "__main__":
    main()

