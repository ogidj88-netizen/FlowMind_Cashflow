"""
FlowMind Cashflow
PROJECT STATE LOCK ENGINE
"""

import os
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_DIR = os.path.join(BASE_DIR, "state_data")

os.makedirs(STATE_DIR, exist_ok=True)


def _state_path(project_id: str):
    return os.path.join(STATE_DIR, f"{project_id}.json")


def create_project_state(project_id: str):
    path = _state_path(project_id)

    if os.path.exists(path):
        raise Exception("PROJECT_ALREADY_EXISTS")

    data = {
        "project_id": project_id,
        "status": "CREATED",
        "created_at": datetime.utcnow().isoformat(),
        "approved": False,
        "production_started": False,
        "production_completed": False
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    return data


def load_project_state(project_id: str):
    path = _state_path(project_id)
    if not os.path.exists(path):
        raise Exception("PROJECT_NOT_FOUND")

    with open(path, "r") as f:
        return json.load(f)


def update_project_state(project_id: str, updates: dict):
    data = load_project_state(project_id)
    data.update(updates)

    with open(_state_path(project_id), "w") as f:
        json.dump(data, f, indent=2)

    return data
