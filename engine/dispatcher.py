"""
FlowMind Cashflow Dispatcher
State-Locked + Telegram-Gated + Smart Runtime Lock + Auto-Resume + CLI PROJECT_ID
"""

import os
import time
import sys
import argparse

from engine.alerts.telegram_gate import send_for_approval, wait_for_approval
from engine.state.project_state import (
    create_project_state,
    load_project_state,
    update_project_state,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCK_FILE = os.path.join(BASE_DIR, "runtime.lock")


# ==============================
# Smart Runtime Lock
# ==============================

def is_process_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def acquire_lock():
    if os.path.exists(LOCK_FILE):
        with open(LOCK_FILE, "r") as f:
            old_pid = int(f.read().strip())

        if is_process_alive(old_pid):
            print(f"⛔ Dispatcher already running (PID {old_pid})")
            sys.exit(1)
        else:
            print("⚠ Stale lock detected. Cleaning...")
            os.remove(LOCK_FILE)

    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))


def release_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)


# ==============================
# Project ID
# ==============================

def generate_project_id():
    return f"FM_{int(time.time())}"


# ==============================
# Production
# ==============================

def run_production(project_id: str):
    state = load_project_state(project_id)

    if state["production_completed"]:
        print("⚠ Project already completed. Exiting.")
        return

    update_project_state(project_id, {
        "production_started": True,
        "status": "PRODUCTION_RUNNING"
    })

    print(f"🚀 Production phase started for {project_id}...")

    # ---- Production ядро ----
    time.sleep(2)

    update_project_state(project_id, {
        "production_completed": True,
        "status": "COMPLETED"
    })

    print(f"✅ Production completed for {project_id}.")


# ==============================
# Main
# ==============================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=str, help="Existing PROJECT_ID")
    args = parser.parse_args()

    acquire_lock()

    try:
        if args.project:
            project_id = args.project
            print(f"FlowMind Dispatcher started for existing project {project_id}")
        else:
            project_id = generate_project_id()
            print(f"FlowMind Dispatcher started for new project {project_id}")

        # ------------------------------
        # LOAD OR CREATE STATE
        # ------------------------------

        try:
            state = load_project_state(project_id)
            print("🔁 Existing state detected.")
        except:
            state = create_project_state(project_id)
            print("🆕 New project state created.")

        # ------------------------------
        # AUTO RESUME LOGIC
        # ------------------------------

        if state["approved"] and not state["production_completed"]:
            print("▶ Resuming production without approval...")
            run_production(project_id)
            return

        if state["production_completed"]:
            print("⚠ Project already completed. Nothing to do.")
            return

        # ------------------------------
        # TELEGRAM APPROVAL
        # ------------------------------

        message_id = send_for_approval(project_id)

        print("Waiting for approval button...")

        approved = wait_for_approval(project_id, message_id)

        if not approved:
            update_project_state(project_id, {"status": "REJECTED"})
            print("❌ Project rejected.")
            return

        update_project_state(project_id, {
            "approved": True,
            "status": "APPROVED"
        })

        print(f"✅ Telegram approval received for {project_id}")

        run_production(project_id)

    finally:
        release_lock()


if __name__ == "__main__":
    main()
