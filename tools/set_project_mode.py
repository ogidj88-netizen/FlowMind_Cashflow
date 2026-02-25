#!/usr/bin/env python3
import json
import sys
from pathlib import Path

if len(sys.argv) != 3:
    print("Usage: python3 tools/set_project_mode.py <PROJECT_ID> <MODE>")
    sys.exit(1)

project_id = sys.argv[1]
mode = sys.argv[2].upper()

if mode not in ["LONG", "SHORT"]:
    print("Invalid mode. Use LONG or SHORT.")
    sys.exit(1)

state_path = Path(f"projects/{project_id}/PROJECT_STATE.json")

if not state_path.exists():
    print("PROJECT_STATE.json not found.")
    sys.exit(1)

with open(state_path, "r") as f:
    data = json.load(f)

if "mode" in data:
    print(f"[INFO] Previous mode: {data['mode']}")

data["mode"] = mode

with open(state_path, "w") as f:
    json.dump(data, f, indent=2)

print(f"[OK] Mode set to {mode} for {project_id}")
