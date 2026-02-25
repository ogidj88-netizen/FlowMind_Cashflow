"""
FlowMind Cashflow Mode
S3 — Scene Planner (Duration-Aware)

Policy:
- Target scene length: 10–18 sec
- Avoid ultra-short scenes
- Audio = master clock
"""

import json
from pathlib import Path
from engine.state_manager import load_state, save_state

WPM = 155
MIN_SCENE_SEC = 8
MAX_SCENE_SEC = 20


def estimate_seconds(text: str):
    words = len(text.split())
    return int((words / WPM) * 60)


def split_into_chunks(text: str, target_sec=15):
    words = text.split()
    chunk_size = int(WPM * (target_sec / 60))

    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = words[i:i + chunk_size]
        chunks.append(" ".join(chunk))

    return chunks


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

    chunks = split_into_chunks(script_text, target_sec=14)

    scenes = []
    total_seconds = 0

    for idx, chunk in enumerate(chunks, start=1):
        sec = estimate_seconds(chunk)

        if sec < MIN_SCENE_SEC:
            continue

        scenes.append({
            "scene_id": idx,
            "text": chunk.strip(),
            "estimated_duration_sec": sec
        })

        total_seconds += sec

    assets_dir = project_path / "assets"
    scene_file = assets_dir / "scene_plan.json"

    with open(scene_file, "w") as f:
        json.dump(scenes, f, indent=2)

    state["scene_plan_path"] = "assets/scene_plan.json"

    if "metrics" not in state:
        state["metrics"] = {}

    state["metrics"]["scene_count"] = len(scenes)
    state["metrics"]["estimated_duration_minutes"] = round(total_seconds / 60, 2)

    save_state(project_path, state)

    print("S3 Scene plan generated.")
    print(f"Scenes: {len(scenes)}")
    print(f"Total duration: {round(total_seconds/60,2)} minutes")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python -m intelligence.scene_planner <PROJECT_PATH>")
        exit(1)

    run(Path(sys.argv[1]))
