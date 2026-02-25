#!/usr/bin/env python3
"""
FlowMind — Scene Planner v1 (Cashflow Mode)

Paragraph-based scene mapping.
Audio = Master Clock compatible.
"""

from __future__ import annotations
import json
import re
import sys
from typing import List, Dict


WORDS_PER_MINUTE = 150  # conservative narration speed
MIN_SCENE_SECONDS = 5


def _estimate_duration_seconds(text: str) -> int:
    words = len(text.split())
    minutes = words / WORDS_PER_MINUTE
    seconds = int(minutes * 60)
    return max(seconds, MIN_SCENE_SECONDS)


def _extract_keywords(text: str, max_keywords: int = 5) -> List[str]:
    words = re.findall(r"[A-Za-z]{4,}", text.lower())
    unique = []
    for w in words:
        if w not in unique:
            unique.append(w)
        if len(unique) >= max_keywords:
            break
    return unique


def split_into_paragraphs(script: str) -> List[str]:
    parts = [p.strip() for p in script.split("\n") if p.strip()]
    return parts


def build_scene_plan(script: str) -> Dict:
    paragraphs = split_into_paragraphs(script)

    scenes = []
    total_duration = 0

    for idx, paragraph in enumerate(paragraphs, start=1):
        duration = _estimate_duration_seconds(paragraph)
        keywords = _extract_keywords(paragraph)

        scene = {
            "scene_id": f"S{idx:03}",
            "text": paragraph,
            "estimated_duration_seconds": duration,
            "keywords": keywords
        }

        total_duration += duration
        scenes.append(scene)

    return {
        "scenes_count": len(scenes),
        "estimated_total_duration_seconds": total_duration,
        "scenes": scenes
    }


def main(argv: List[str]) -> int:
    if len(argv) != 2:
        print("Usage: scene_planner_v1.py <SCRIPT_JSON_PATH>")
        return 2

    script_path = argv[1]

    with open(script_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    script_text = data.get("script")
    if not script_text:
        print("Script text not found in JSON under 'script' key.")
        return 3

    scene_plan = build_scene_plan(script_text)

    output_path = script_path.replace(".json", "_SCENE_PLAN.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(scene_plan, f, ensure_ascii=False, indent=2)

    print(f"[SCENE PLANNER] Generated: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
