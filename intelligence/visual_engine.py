"""
FlowMind Cashflow Mode
S4 — Visual Engine (Deterministic, Audio-Slave)

Rules:
- Must run only in VISUAL phase
- Cannot modify duration
- Cannot modify scene count
- Generates visual_plan.json only
"""

from pathlib import Path
import json
import sys


def load_state(project_path: Path):
    with open(project_path / "PROJECT_STATE.json", "r") as f:
        return json.load(f)


def save_state(project_path: Path, state: dict):
    with open(project_path / "PROJECT_STATE.json", "w") as f:
        json.dump(state, f, indent=2)


def run(project_path: Path):
    state = load_state(project_path)

    if state["phase"] != "VISUAL":
        raise Exception("Visual Engine can run only in VISUAL phase")

    scene_plan_path = project_path / state.get("scene_plan_path", "")
    if not scene_plan_path.exists():
        raise Exception("Missing scene_plan.json")

    with open(scene_plan_path, "r") as f:
        scene_plan = json.load(f)

    scenes = scene_plan["scenes"]
    visual_plan = {"scenes": []}

    for scene in scenes:
        visual_plan["scenes"].append({
            "scene_id": scene["scene_id"],
            "duration_seconds": scene["duration_seconds"],
            "visual_prompt": f"Stock footage representing: {scene['summary']}",
            "asset_type": "stock",
            "status": "pending"
        })

    output_path = project_path / "assets"
    output_path.mkdir(exist_ok=True)

    visual_file = output_path / "visual_plan.json"

    with open(visual_file, "w") as f:
        json.dump(visual_plan, f, indent=2)

    state["visual_plan_path"] = "assets/visual_plan.json"

    save_state(project_path, state)

    print("S4 Visual plan generated.")
    print("Scenes:", len(visual_plan["scenes"]))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise Exception("Usage: python -m intelligence.visual_engine <PROJECT_PATH>")

    run(Path(sys.argv[1]))
