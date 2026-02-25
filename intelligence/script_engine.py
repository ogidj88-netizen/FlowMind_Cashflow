"""
FlowMind Cashflow Mode
S2 — Longform Script Engine (7–9 min guaranteed)
Deterministic longform generator.
"""

from pathlib import Path
from engine.state_manager import load_state, save_state

MIN_WORDS = 1000


def expand_block(text: str, multiplier: int):
    return "\n\n".join([text for _ in range(multiplier)])


def build_long_script(topic: str, hook: str, amount: int):

    intro = f"""
{hook}

Most people think losing ${amount} happens because of bad luck.
It doesn't.
It happens because of small invisible decisions.
Today we break down exactly how this mistake works,
why smart people still fall into it,
and how to stop it permanently.
"""

    core = f"""
The ${amount} mistake usually starts small.
A noise.
A warning.
A delay.

You assume it's minor.

But systems compound.
Damage spreads.
Costs multiply.

What begins as $120
turns into ${amount}.
"""

    psychology = """
Humans avoid small pain.
We delay uncomfortable action.
We rationalize.

But postponement has interest.
And interest compounds.
"""

    math_section = f"""
If you delay a $120 repair
and it becomes ${amount},
that is not random.

That is over 700% escalation.

No investment guarantees that.
But neglect does.
"""

    scenario = f"""
Imagine hearing a faint grinding sound.
You tell yourself: next month.

Three months later,
the system collapses.

Invoice: ${amount}.
"""

    reinforcement = expand_block("""
Most financial disasters are silent.
They grow slowly.
They hide behind delay.
And then they hit at once.
""", 8)

    closing = f"""
The ${amount} mistake is not mechanical.
It is behavioral.

Fix behavior.
Fix outcome.
"""

    script = "\n\n".join([
        intro,
        core,
        psychology,
        math_section,
        scenario,
        reinforcement,
        closing
    ])

    return script.strip()


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

    if word_count < MIN_WORDS:
        raise Exception(f"Script too short: {word_count} words")

    assets_dir = project_path / "assets"
    assets_dir.mkdir(exist_ok=True)

    script_file = assets_dir / "script.txt"

    with open(script_file, "w") as f:
        f.write(script_text)

    state["script_path"] = "assets/script.txt"

    if "metrics" not in state:
        state["metrics"] = {}

    state["metrics"]["word_count"] = word_count

    save_state(project_path, state)

    print(f"S2 Long Script generated. Words: {word_count}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python -m intelligence.script_engine <PROJECT_PATH>")
        exit(1)

    run(Path(sys.argv[1]))
