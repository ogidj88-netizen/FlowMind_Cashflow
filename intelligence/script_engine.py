"""
FlowMind Cashflow
S2 — Script Engine v2
File-based output (canonical)
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
    parts = []

    parts.append(hook)

    parts.append(
        f"Most people never notice how small financial decisions slowly cost them ${amount}."
    )

    parts.append(
        "It starts small. Then suddenly you're missing hundreds of dollars."
    )

    parts.append(
        "And the worst part? You think everything is fine."
    )

    parts.append(
        f"Imagine checking your account and realizing you've lost ${amount} because of one tiny oversight."
    )

    parts.append(
        "This is not bad luck. It's a predictable pattern."
    )

    parts.append(
        "Once you understand the pattern, you stop bleeding money."
    )

    return "\n\n".join(parts)


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

    scripts_dir = project_path / "assets"
    scripts_dir.mkdir(exist_ok=True)

    script_file = scripts_dir / "script.txt"

    with open(script_file, "w") as f:
        f.write(script_text)

    state["script_path"] = str(script_file)
    state.pop("script", None)

    save_state(project_path, state)

    print("S2 Script generated and saved to file.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python -m intelligence.script_engine <PROJECT_PATH>")
        exit(1)

    run(Path(sys.argv[1]))