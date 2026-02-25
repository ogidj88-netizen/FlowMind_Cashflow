"""
FlowMind Cashflow
S2 — Deterministic Script Engine v1
Money Mistakes Structure
"""

import json
from pathlib import Path


def load_state(project_path: Path):
    with open(project_path / "PROJECT_STATE.json", "r") as f:
        return json.load(f)


def save_state(project_path: Path, state: dict):
    with open(project_path / "PROJECT_STATE.json", "w") as f:
        json.dump(state, f, indent=2)


def build_script(topic: str, hook: str, amount: int):
    script = []

    # Hook (0–15 sec)
    script.append(hook)

    # Context
    script.append(
        f"Most people never notice how small financial decisions slowly cost them ${amount}."
    )

    # Problem escalation
    script.append(
        f"It starts small. Then suddenly you're missing hundreds of dollars."
    )

    # Psychological trigger
    script.append(
        "And the worst part? You think everything is fine."
    )

    # Example block
    script.append(
        f"Imagine checking your account and realizing you've lost ${amount} because of one tiny oversight."
    )

    # Consequence framing
    script.append(
        "This is not bad luck. It's a predictable pattern."
    )

    # Soft resolution (без продажу)
    script.append(
        "Once you understand the pattern, you stop bleeding money."
    )

    return "\n\n".join(script)


def run(project_path: Path):
    state = load_state(project_path)

    if state.get("phase") != "SCRIPT":
        raise Exception("Script Engine can run only in SCRIPT phase")

    topic = state.get("topic")
    hook = state.get("hook")
    amount = state.get("numeric_anchor")

    if not topic or not hook or not amount:
        raise Exception("Missing required fields from S1")

    script_text = build_script(topic, hook, amount)

    state["script"] = script_text

    save_state(project_path, state)

    print("S2 Script generated.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python -m intelligence.script_engine <PROJECT_PATH>")
        exit(1)

    run(Path(sys.argv[1]))