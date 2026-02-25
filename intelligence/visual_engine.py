"""
FlowMind Cashflow Mode
S4 — Visual Engine (Deterministic, Audio-Slave)

Hard rules:
- Runs ONLY in VISUAL phase
- Must NOT modify S2 master duration / scene order
- Reads scene_plan.json (supports both LIST and {"scenes":[...]})
- Writes assets/visual_plan.json
- Updates PROJECT_STATE.json: visual_plan_path only
"""

from pathlib import Path
import json
import sys


def load_state(project_path: Path) -> dict:
    with open(project_path / "PROJECT_STATE.json", "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(project_path: Path, state: dict) -> None:
    with open(project_path / "PROJECT_STATE.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def _load_scene_plan(scene_plan_path: Path):
    with open(scene_plan_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Back-compat:
    # - v1: [ {scene_id, text, estimated_duration_sec}, ... ]
    # - v2+: { "scenes": [ ... ], "total_duration_seconds": ... }
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("scenes"), list):
        return data["scenes"]

    raise Exception("Unsupported scene_plan.json format (expected list or {scenes:[...]})")


def _scene_duration_seconds(scene: dict) -> int:
    # Accept multiple historical keys
    v = (
        scene.get("duration_seconds")
        or scene.get("estimated_duration_sec")
        or scene.get("duration_sec")
        or 0
    )
    try:
        v = int(round(float(v)))
    except Exception:
        v = 0
    return max(1, v)


def _scene_summary(scene: dict) -> str:
    s = scene.get("summary")
    if isinstance(s, str) and s.strip():
        return s.strip()

    t = scene.get("text") or scene.get("voiceover") or ""
    if not isinstance(t, str):
        t = str(t)

    t = " ".join(t.split())
    return (t[:140] + "…") if len(t) > 140 else t


def run(project_path: Path):
    state = load_state(project_path)

    if state.get("phase") != "VISUAL":
        raise Exception("Visual Engine can run only in VISUAL phase")

    scene_plan_rel = state.get("scene_plan_path")
    if not scene_plan_rel:
        raise Exception("Missing scene_plan_path in PROJECT_STATE.json")

    scene_plan_path = project_path / scene_plan_rel
    if not scene_plan_path.exists():
        raise Exception(f"scene_plan.json not found: {scene_plan_path}")

    scenes = _load_scene_plan(scene_plan_path)

    visual_plan = {"scenes": []}

    for scene in scenes:
        sid = scene.get("scene_id")
        if sid is None:
            raise Exception("scene_plan item missing scene_id")

        duration = _scene_duration_seconds(scene)
        summary = _scene_summary(scene)

        visual_plan["scenes"].append(
            {
                "scene_id": sid,
                "duration_seconds": duration,
                "summary": summary,
                "visual_prompt": f"High-quality stock footage that visually matches: {summary}",
                "asset_type": "stock",
                "status": "pending",
            }
        )

    assets_dir = project_path / "assets"
    assets_dir.mkdir(exist_ok=True)

    out_file = assets_dir / "visual_plan.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(visual_plan, f, indent=2)

    # State update (ONLY what S4 owns)
    state["visual_plan_path"] = "assets/visual_plan.json"
    save_state(project_path, state)

    print("S4 Visual plan generated.")
    print("Scenes:", len(visual_plan["scenes"]))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise Exception("Usage: python -m intelligence.visual_engine <PROJECT_PATH>")
    run(Path(sys.argv[1]))
