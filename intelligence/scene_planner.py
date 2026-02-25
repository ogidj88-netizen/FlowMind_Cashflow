"""
FlowMind Cashflow
S3 — Scene Planner v1
Paragraph-based scene segmentation
"""

import json
from pathlib import Path


def load_state(project_path: Path):
    with open(project_path / "PROJECT_STATE.json", "r") as f:
        return json.load(f)


def save_state(project_path: Path, state: dict):
    with open(project_path / "PROJECT_STATE.json", "w") as f:
        json.dump(state, f, indent=2)


def estimate_duration(text: str):
    words = len(text.split())
    # ~160 words per minute average narration
    minutes = words / 160
    seconds = int(minutes * 60)
    return max(3, seconds)


def run(project_path: Path):
    state = load_state(project_path)

    if state.get("phase") != "SCENE":
        raise Exception("Scene Planner can run only in SCENE phase")

    script_path = state.get("script_path")

    if not script_path:
        raise Exception("Missing script_path")

    full_script_path = project_path / script_path

    if not full_script_path.exists():
        raise Exception("Script file not found")

    with open(full_script_path, "r") as f:
        script_text = f.read()

    paragraphs = [p.strip() for p in script_text.split("\n\n") if p.strip()]

    scenes = []

    for idx, paragraph in enumerate(paragraphs, start=1):
        scenes.append({
            "scene_id": idx,
            "text": paragraph,
            "estimated_duration_sec": estimate_duration(paragraph)
        })

    assets_dir = project_path / "assets"
    scene_file = assets_dir / "scene_plan.json"

    with open(scene_file, "w") as f:
        json.dump(scenes, f, indent=2)

    state["scene_plan_path"] = "assets/scene_plan.json"

    save_state(project_path, state)

    print("S3 Scene plan generated.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python -m intelligence.scene_planner <PROJECT_PATH>")
        exit(1)

    run(Path(sys.argv[1]))