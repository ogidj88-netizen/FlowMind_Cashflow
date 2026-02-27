#!/usr/bin/env python3
"""
FlowMind Cashflow
Scene Planner v1 (PROJECT_ID in, deterministic out)

Input:
- argv[1] = PROJECT_ID

Reads:
- projects/<PROJECT_ID>/SCRIPT.txt (required)

Writes:
- projects/<PROJECT_ID>/SCENE_PLAN.json

Rules:
- PASS => exit(0)
- FAIL => exit(1)
"""

import os
import sys
import json
import re
from datetime import datetime

BASE_DIR = "projects"


def project_dir(project_id: str) -> str:
    return os.path.join(BASE_DIR, project_id)


def script_txt_path(project_id: str) -> str:
    return os.path.join(project_dir(project_id), "SCRIPT.txt")


def scene_plan_path(project_id: str) -> str:
    return os.path.join(project_dir(project_id), "SCENE_PLAN.json")


def read_script(project_id: str) -> str:
    path = script_txt_path(project_id)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing SCRIPT.txt at: {path}")
    with open(path, "r", encoding="utf-8") as f:
        text = f.read().strip()
    if not text:
        raise ValueError("SCRIPT.txt is empty.")
    return text


def split_sentences(text: str):
    # Deterministic sentence split (simple)
    parts = re.split(r"[.!?]\s+", text.strip())
    return [p.strip() for p in parts if p and p.strip()]


def extract_keywords(text: str, limit: int = 10):
    tokens = re.findall(r"[A-Za-z']{3,}", text.lower())
    stop = {
        "this", "that", "because", "today", "later", "never", "most", "people",
        "your", "you", "will", "then", "into", "from", "with", "over", "just",
        "they", "them", "their", "been", "when", "what", "where", "why", "how",
        "and", "the", "a", "an", "to", "of", "in", "on", "it", "is", "are", "was",
        "be", "as", "at", "or", "but"
    }
    uniq = []
    seen = set()
    for t in tokens:
        if t in stop:
            continue
        if t in seen:
            continue
        seen.add(t)
        uniq.append(t)
        if len(uniq) >= limit:
            break
    return uniq


def build_scene_plan(project_id: str, script_text: str) -> dict:
    sentences = split_sentences(script_text)
    if not sentences:
        raise ValueError("Script has no sentences after splitting.")

    # Minimal deterministic buckets
    buckets = [
        ("hook", 1),
        ("problem", 2),
        ("mechanism", 2),
        ("why_it_happens", 2),
        ("stakes", 2),
        ("promise", 1),
    ]

    scenes = []
    idx = 0
    scene_num = 1

    for label, count in buckets:
        chunk = sentences[idx: idx + count]
        if not chunk:
            break
        idx += count

        chunk_text = " ".join(chunk)
        keywords = extract_keywords(chunk_text, limit=10)

        scenes.append({
            "scene_id": f"{scene_num:02d}_{label}",
            "label": label,
            "text": chunk_text,
            "keywords": keywords,
            "estimated_seconds": max(6, min(12, 3 + len(chunk) * 3)),
        })
        scene_num += 1

    if not scenes:
        raise ValueError("Failed to build any scenes from script.")

    return {
        "project_id": project_id,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "source": {"script_txt": script_txt_path(project_id)},
        "scenes": scenes,
        "notes": {
            "model": "scene_planner_v1",
            "policy": "project_id_in__files_in_projects_dir",
            "estimates_are_placeholders": True,
        },
    }


def main(argv) -> int:
    if len(argv) < 2:
        print("Usage: python -m engine.scene_planner_v1 <PROJECT_ID>")
        return 1

    project_id = argv[1].strip()
    if not project_id:
        print("[SCENES FAIL] Empty PROJECT_ID")
        return 1

    try:
        script_text = read_script(project_id)
        plan = build_scene_plan(project_id, script_text)

        os.makedirs(project_dir(project_id), exist_ok=True)
        out_path = scene_plan_path(project_id)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)

        print(f"[SCENES PASS] Written: {out_path}")
        return 0

    except Exception as e:
        print(f"[SCENES FAIL] {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
