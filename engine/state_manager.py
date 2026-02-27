#!/usr/bin/env python3

"""
FlowMind Cashflow
State Manager (Deterministic Phase Control)

Single source of truth: projects/<PROJECT_ID>/PROJECT_STATE.json
"""

import os
import json


BASE_DIR = "projects"


def _state_path(project_id: str) -> str:
    return os.path.join(BASE_DIR, project_id, "PROJECT_STATE.json")


def _ensure_project(project_id: str):
    project_path = os.path.join(BASE_DIR, project_id)
    os.makedirs(project_path, exist_ok=True)

    state_file = _state_path(project_id)

    if not os.path.exists(state_file):
        default_state = {
            "project_id": project_id,
            "phase": "TOPIC"
        }
        with open(state_file, "w") as f:
            json.dump(default_state, f, indent=2)


def get_phase(project_id: str) -> str:
    _ensure_project(project_id)

    with open(_state_path(project_id), "r") as f:
        data = json.load(f)

    return data.get("phase", "TOPIC")


def set_phase(project_id: str, new_phase: str):
    _ensure_project(project_id)

    with open(_state_path(project_id), "r") as f:
        data = json.load(f)

    data["phase"] = new_phase

    with open(_state_path(project_id), "w") as f:
        json.dump(data, f, indent=2)
