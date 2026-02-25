"""
FlowMind Cashflow Mode
S2 — Duration-Based Script Engine

Policy:
- Min: 7 minutes
- Optimal: 9–11 minutes
- Max: 15 minutes
- Control via estimated duration (155 wpm)
"""

from pathlib import Path
from engine.state_manager import load_state, save_state

WPM = 155
MIN_MINUTES = 7
MAX_MINUTES = 15


def estimate_minutes(text: str):
    words = len(text.split())
    return words / WPM


def build_base_script(topic: str, hook: str, amount: int):

    sections = []

    sections.append(f"""
{hook}

Most people think losing ${amount} happens because of bad luck.
It doesn’t.
It happens because of invisible financial patterns.
""")

    sections.append(f"""
The ${amount} mistake starts small.
A delay.
A shortcut.
An ignored warning.

You assume it's harmless.
But systems compound.
Costs multiply.
""")

    sections.append("""
Humans avoid small discomfort.
We postpone action.
We rationalize delay.

But delay has interest.
And interest compounds.
""")

    sections.append(f"""
Imagine ignoring a small issue worth $120.

Three months later,
it becomes ${amount}.

That is not random.
That is escalation.
""")

    sections.append("""
Most financial damage is silent.
It grows in the background.
Then it hits all at once.
""")

    sections.append(f"""
This is not about cars.
Not about insurance.
Not about maintenance.

It is about behavior.

Fix behavior.
Fix outcome.
""")

    return "\n\n".join(sections).strip()


def expand_to_target(script: str):

    while True:
        minutes = estimate_minutes(script)

        if minutes >= 9:
            break

        script += """

Here is what people miss.

Every small ignored cost becomes a larger forced payment.
Every delay increases leverage against you.
Every rationalization strengthens the pattern.

And patterns repeat until interrupted.
"""

    return script


def run(project_path: Path):

    state = load_state(project_path)

    if state.get("phase") != "SCRIPT":
        raise Exception("Script Engine can run only in SCRIPT phase")

    topic = state.get("topic")
    hook = state.get("hook")
    amount = state.get("numeric_anchor")

    if not topic or not hook or not amount:
        raise Exception("Missing required fields from S1")

    script = build_base_script(topic, hook, amount)
    script = expand_to_target(script)

    minutes = estimate_minutes(script)

    if minutes < MIN_MINUTES:
        raise Exception(f"Script too short: {round(minutes,2)} min")

    if minutes > MAX_MINUTES:
        raise Exception(f"Script too long: {round(minutes,2)} min")

    assets_dir = project_path / "assets"
    assets_dir.mkdir(exist_ok=True)

    script_file = assets_dir / "script.txt"

    with open(script_file, "w") as f:
        f.write(script)

    state["script_path"] = "assets/script.txt"

    if "metrics" not in state:
        state["metrics"] = {}

    state["metrics"]["estimated_duration_minutes"] = round(minutes, 2)
    state["metrics"]["word_count"] = len(script.split())

    save_state(project_path, state)

    zone = "OPTIMAL" if 9 <= minutes <= 11 else "OK"

    print(f"S2 Script generated.")
    print(f"Duration: {round(minutes,2)} minutes ({zone})")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python -m intelligence.script_engine <PROJECT_PATH>")
        exit(1)

    run(Path(sys.argv[1]))

