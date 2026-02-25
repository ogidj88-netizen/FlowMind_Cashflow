"""
FlowMind Cashflow Mode
QA Engine (Minimal Deterministic Gate)
"""

import sys
import json
import subprocess
from pathlib import Path


class QAError(Exception):
    pass


def load_state(project_path: Path):
    with open(project_path / "PROJECT_STATE.json", "r") as f:
        return json.load(f)


def save_state(project_path: Path, state: dict):
    with open(project_path / "PROJECT_STATE.json", "w") as f:
        json.dump(state, f, indent=2)


def get_video_duration(video_path: Path):
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(video_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise QAError("ffprobe failed")

    return float(result.stdout.strip())


def run(project_path: Path):
    state = load_state(project_path)

    video_path = state.get("video_path")

    if not video_path:
        raise QAError("video_path missing in state")

    full_path = project_path / video_path

    if not full_path.exists():
        raise QAError("Final video file not found")

    duration = get_video_duration(full_path)

    if duration < 60:
        raise QAError("Video too short (< 60 seconds)")

    state["qa_passed"] = True
    save_state(project_path, state)

    print("[QA PASS] Video valid. Duration:", round(duration, 2), "seconds")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m intelligence.qa_engine <PROJECT_PATH>")
        sys.exit(1)

    run(Path(sys.argv[1]))
