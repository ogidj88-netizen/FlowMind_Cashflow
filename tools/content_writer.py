#!/usr/bin/env python3

import json
import os
import sys


def project_root(project_id: str) -> str:
    return os.path.join("projects", project_id)


def content_path(project_id: str) -> str:
    return os.path.join(project_root(project_id), "CONTENT.json")


def state_path(project_id: str) -> str:
    return os.path.join(project_root(project_id), "PROJECT_STATE.json")


def load_json(path: str) -> dict:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"{path} not found")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def phase_guard(current_phase: str, field: str) -> None:
    rules = {
        "TOPIC": {"topic"},
        "SCRIPT": {"script", "title", "hook"},
        "ASSEMBLY": {"video_path", "thumbnail_path"},
        "QA": {"approved_for_upload"}
    }

    allowed = rules.get(current_phase, set())

    if field not in allowed:
        print(f"[PHASE BLOCK] Cannot write '{field}' during phase '{current_phase}'")
        sys.exit(3)


def main():
    if len(sys.argv) != 4:
        print("Usage: content_writer.py <PROJECT_ID> <FIELD> <VALUE>")
        sys.exit(1)

    project_id = sys.argv[1]
    field = sys.argv[2]
    value = sys.argv[3]

    content = load_json(content_path(project_id))
    state = load_json(state_path(project_id))

    current_phase = state.get("phase", "INIT")

    if field not in content:
        print(f"Field '{field}' not found in CONTENT.json")
        sys.exit(2)

    phase_guard(current_phase, field)

    content[field] = value
    save_json(content_path(project_id), content)

    print(f"[CONTENT] Updated {field} (phase={current_phase})")


if __name__ == "__main__":
    main()
