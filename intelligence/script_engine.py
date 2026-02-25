"""
FlowMind Cashflow
S2 — Script Engine v4
7–9 Minute Longform Generator (Deterministic)
"""

import json
from pathlib import Path


def load_state(project_path: Path):
    with open(project_path / "PROJECT_STATE.json", "r") as f:
        return json.load(f)


def save_state(project_path: Path, state: dict):
    with open(project_path / "PROJECT_STATE.json", "w") as f:
        json.dump(state, f, indent=2)


def build_long_script(topic: str, hook: str, amount: int):
    parts = []

    # HOOK
    parts.append(hook)
    parts.append(
        f"This mistake alone costs people around ${amount} every single year."
    )

    # CONTEXT
    parts.append(
        "Most people think financial damage comes from big disasters. It doesn’t."
    )
    parts.append(
        "It comes from small decisions repeated over time."
    )

    # ESCALATION
    parts.append(
        "At first, nothing feels wrong. You pay. You move on. You forget."
    )
    parts.append(
        "But over months, small leaks become serious financial bleeding."
    )

    # CASE STUDY
    parts.append(
        f"Imagine someone ignoring a small warning sign in their car. A strange sound. A dashboard light."
    )
    parts.append(
        f"They delay fixing it to save money. Three months later? A ${amount} repair bill."
    )
    parts.append(
        "The cost wasn’t random. It was predictable."
    )

    # BREAKDOWN SECTION
    for i in range(1, 5):
        parts.append(
            f"Reason {i}: Small financial signals are easy to ignore."
        )
        parts.append(
            "Your brain prioritizes comfort over prevention."
        )
        parts.append(
            "You convince yourself it’s not urgent."
        )

    # PSYCHOLOGY
    parts.append(
        "This is called normalcy bias. You assume tomorrow will look like today."
    )
    parts.append(
        "So you delay action."
    )

    # LOSS AMPLIFICATION
    parts.append(
        f"If you repeat this pattern five times a year, that’s ${amount * 5} gone."
    )
    parts.append(
        f"In five years? That’s ${amount * 25} lost."
    )

    # PATTERN REVEAL
    parts.append(
        "The real problem isn’t the bill. It’s the pattern behind the bill."
    )
    parts.append(
        "Once you see the pattern, you stop the bleeding."
    )

    # RESOLUTION
    parts.append(
        "The fix is boring. Inspect early. Act early. Prevent early."
    )
    parts.append(
        "Boring decisions build financial stability."
    )

    # RETENTION LOOP
    parts.append(
        "And this isn’t the only invisible cost draining your money."
    )
    parts.append(
        "There are dozens hiding in plain sight."
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

    script_text = build_long_script(topic, hook, amount)

    word_count = len(script_text.split())

    if word_count < 900:
        raise Exception("Generated script too short. Must be longform.")

    scripts_dir = project_path / "assets"
    scripts_dir.mkdir(exist_ok=True)

    script_file = scripts_dir / "script.txt"

    with open(script_file, "w") as f:
        f.write(script_text)

    state["script_path"] = "assets/script.txt"
    state["metrics"]["word_count"] = word_count

    save_state(project_path, state)

    print(f"S2 Long Script generated. Words: {word_count}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python -m intelligence.script_engine <PROJECT_PATH>")
        exit(1)

    run(Path(sys.argv[1]))