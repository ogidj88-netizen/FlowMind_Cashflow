"""
FlowMind Cashflow Mode
S3 — Canonical Scene Planner (Audio Master Clock)

Rules:
- Scene segmentation 10–18 sec
- No duration loss
- Total duration = S2 estimated duration
"""

import json
from pathlib import Path
from engine.state_manager import load_state, save_state

WPM = 155
TARGET_SCENE_SEC = 14


def estimate_seconds(text: str):
    words = len(text.split())
    return (words / WPM) * 60


def split_into_chunks(text: str, target_sec=14):
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

    # Original duration from S2
    original_minutes = state.get("metrics", {}).get("estimated_duration_minutes")
    if not original_minutes:
        raise Exception("Missing S2 duration metric")

    original_seconds = original_minutes * 60

    chunks = split_into_chunks(script_text, TARGET_SCENE_SEC)

    scenes = []
    recalculated_seconds = 0

    for idx, chunk in enumerate(chunks, start=1):
        sec = estimate_seconds(chunk)

        scenes.append({
            "scene_id": idx,
            "text": chunk.strip(),
            "estimated_duration_sec": round(sec, 2)
        })

        recalculated_seconds += sec

    # Preserve original duration as master clock
    total_seconds = original_seconds

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

    drift = abs(recalculated_seconds - total_seconds)

    print("S3 Scene plan generated.")
    print(f"Scenes: {len(scenes)}")
    print(f"Total duration (master): {round(total_seconds/60,2)} minutes")
    print(f"Drift: {round(drift,2)} seconds")
    

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python -m intelligence.scene_planner <PROJECT_PATH>")
        exit(1)

    run(Path(sys.argv[1]))
