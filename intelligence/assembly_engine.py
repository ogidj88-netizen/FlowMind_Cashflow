"""
FlowMind Cashflow Mode
Minimal Assembly Engine (Deterministic)
"""

import sys
import json
import subprocess
from pathlib import Path


def load_state(project_path: Path):
    with open(project_path / "PROJECT_STATE.json", "r") as f:
        return json.load(f)


def save_state(project_path: Path, state: dict):
    with open(project_path / "PROJECT_STATE.json", "w") as f:
        json.dump(state, f, indent=2)


def create_dummy_video(output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg",
        "-y",
        "-f", "lavfi",
        "-i", "color=c=black:s=1920x1080:d=65",
        "-vf", "format=yuv420p",
        str(output_path)
    ]

    subprocess.run(cmd, check=True)


def run(project_path: Path):
    state = load_state(project_path)

    project_id = state["project_id"]
    output_path = project_path / f"out/{project_id}/final.mp4"

    create_dummy_video(output_path)

    state["video_path"] = f"out/{project_id}/final.mp4"
    save_state(project_path, state)

    print("[ASSEMBLY] Dummy video created:", output_path)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m intelligence.assembly_engine <PROJECT_PATH>")
        sys.exit(1)

    run(Path(sys.argv[1]))
