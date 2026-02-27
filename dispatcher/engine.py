#!/usr/bin/env python3

"""
FlowMind Cashflow
Dispatcher Engine (Strict PASS/FAIL)

Phases:
- TOPIC
- SCRIPT
- SCENES
- SCENES_QA
- ASSETS
- ASSET_MANIFEST
- STOCK_MOCK
- ASSEMBLY_PLAN
- RENDER_DUMMY

Rule:
- Phase changes only on successful module execution.
"""

import sys
import subprocess
from engine.state_manager import get_phase, set_phase


def run_module(module_path: str, project_id: str):
    print(f"[DISPATCHER] Running {module_path} module...")
    subprocess.run(["python", "-m", module_path, project_id], check=True)


def main():
    if len(sys.argv) < 3:
        print("Usage: python -m dispatcher.engine <PROJECT_ID> <PHASE>")
        sys.exit(1)

    project_id = sys.argv[1]
    target_phase = sys.argv[2].strip().upper()

    current_phase = get_phase(project_id)
    print(f"[DISPATCHER] Current phase: {current_phase}")

    if target_phase == "TOPIC":
        set_phase(project_id, "TOPIC")
        print("[DISPATCHER] Phase now: TOPIC")
        return

    if target_phase == "SCRIPT":
        if current_phase != "TOPIC":
            print("[DISPATCHER] Cannot run SCRIPT before TOPIC")
            sys.exit(1)
        try:
            run_module("engine.script_generator", project_id)
        except subprocess.CalledProcessError:
            print("[DISPATCHER] SCRIPT FAILED — phase not updated")
            sys.exit(1)
        set_phase(project_id, "SCRIPT")
        print("[DISPATCHER] Phase now: SCRIPT")
        return

    if target_phase == "SCENES":
        if current_phase != "SCRIPT":
            print("[DISPATCHER] Cannot run SCENES before SCRIPT")
            sys.exit(1)
        try:
            run_module("engine.scene_planner_v1", project_id)
        except subprocess.CalledProcessError:
            print("[DISPATCHER] SCENES FAILED — phase not updated")
            sys.exit(1)
        set_phase(project_id, "SCENES")
        print("[DISPATCHER] Phase now: SCENES")
        return

    if target_phase == "SCENES_QA":
        if current_phase != "SCENES":
            print("[DISPATCHER] Cannot run SCENES_QA before SCENES")
            sys.exit(1)
        try:
            run_module("engine.scene_plan_qa", project_id)
        except subprocess.CalledProcessError:
            print("[DISPATCHER] SCENES_QA FAILED — phase not updated")
            sys.exit(1)
        set_phase(project_id, "SCENES_QA")
        print("[DISPATCHER] Phase now: SCENES_QA")
        return

    if target_phase == "ASSETS":
        if current_phase != "SCENES_QA":
            print("[DISPATCHER] Cannot run ASSETS before SCENES_QA")
            sys.exit(1)
        try:
            run_module("engine.asset_requests_v1", project_id)
        except subprocess.CalledProcessError:
            print("[DISPATCHER] ASSETS FAILED — phase not updated")
            sys.exit(1)
        set_phase(project_id, "ASSETS")
        print("[DISPATCHER] Phase now: ASSETS")
        return

    if target_phase == "ASSET_MANIFEST":
        if current_phase != "ASSETS":
            print("[DISPATCHER] Cannot run ASSET_MANIFEST before ASSETS")
            sys.exit(1)
        try:
            run_module("engine.asset_manifest_v1", project_id)
        except subprocess.CalledProcessError:
            print("[DISPATCHER] ASSET_MANIFEST FAILED — phase not updated")
            sys.exit(1)
        set_phase(project_id, "ASSET_MANIFEST")
        print("[DISPATCHER] Phase now: ASSET_MANIFEST")
        return

    if target_phase == "STOCK_MOCK":
        if current_phase != "ASSET_MANIFEST":
            print("[DISPATCHER] Cannot run STOCK_MOCK before ASSET_MANIFEST")
            sys.exit(1)
        try:
            run_module("engine.stock_fetcher_mock_v1", project_id)
        except subprocess.CalledProcessError:
            print("[DISPATCHER] STOCK_MOCK FAILED — phase not updated")
            sys.exit(1)
        set_phase(project_id, "STOCK_MOCK")
        print("[DISPATCHER] Phase now: STOCK_MOCK")
        return

    if target_phase == "ASSEMBLY_PLAN":
        if current_phase != "STOCK_MOCK":
            print("[DISPATCHER] Cannot run ASSEMBLY_PLAN before STOCK_MOCK")
            sys.exit(1)
        try:
            run_module("engine.assembly_plan_v1", project_id)
        except subprocess.CalledProcessError:
            print("[DISPATCHER] ASSEMBLY_PLAN FAILED — phase not updated")
            sys.exit(1)
        set_phase(project_id, "ASSEMBLY_PLAN")
        print("[DISPATCHER] Phase now: ASSEMBLY_PLAN")
        return

    if target_phase == "RENDER_DUMMY":
        if current_phase != "ASSEMBLY_PLAN":
            print("[DISPATCHER] Cannot run RENDER_DUMMY before ASSEMBLY_PLAN")
            sys.exit(1)
        try:
            run_module("engine.ffmpeg_dummy_renderer_v1", project_id)
        except subprocess.CalledProcessError:
            print("[DISPATCHER] RENDER_DUMMY FAILED — phase not updated")
            sys.exit(1)
        set_phase(project_id, "RENDER_DUMMY")
        print("[DISPATCHER] Phase now: RENDER_DUMMY")
        return

    print("[DISPATCHER] Unknown phase")
    sys.exit(1)


if __name__ == "__main__":
    main()
