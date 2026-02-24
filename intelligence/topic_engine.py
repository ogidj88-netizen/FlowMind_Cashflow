"""
FlowMind Cashflow
S1 — Deterministic Topic Engine
Money Mistakes Mode
"""

import json
import random
from pathlib import Path


TEMPLATES = [
    {
        "topic": "The $1000 Car Repair Mistake Most Drivers Ignore",
        "hook": "This tiny decision can cost you $1000.",
        "numeric_anchor": 1000,
        "trigger_word": "Mistake"
    },
    {
        "topic": "The $500 Subscription Trap Draining Your Bank Account",
        "hook": "You’re losing $500 and don’t even see it.",
        "numeric_anchor": 500,
        "trigger_word": "Trap"
    },
    {
        "topic": "The $300 Insurance Error That Destroys Your Claim",
        "hook": "One small error can erase $300 instantly.",
        "numeric_anchor": 300,
        "trigger_word": "Error"
    }
]


def load_state(project_path: Path):
    with open(project_path / "PROJECT_STATE.json", "r") as f:
        return json.load(f)


def save_state(project_path: Path, state: dict):
    with open(project_path / "PROJECT_STATE.json", "w") as f:
        json.dump(state, f, indent=2)


def run(project_path: Path):
    state = load_state(project_path)

    if state.get("phase") != "TOPIC":
        raise Exception("Topic Engine can run only in TOPIC phase")

    selection = random.choice(TEMPLATES)

    state["topic"] = selection["topic"]
    state["hook"] = selection["hook"]
    state["numeric_anchor"] = selection["numeric_anchor"]
    state["trigger_word"] = selection["trigger_word"]

    save_state(project_path, state)

    print("S1 Topic generated:")
    print(selection["topic"])


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python -m intelligence.topic_engine <PROJECT_PATH>")
        exit(1)

    run(Path(sys.argv[1]))