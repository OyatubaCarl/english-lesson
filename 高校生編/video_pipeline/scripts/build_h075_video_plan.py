#!/usr/bin/env python3
"""Build H075 dense Style01 video plan with uniform 1.369-second cuts."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H075"
PLAN = LESSON / "planning/video_plan.json"
PREFIXES = (
    "language_atlas", "multilingual_listening", "signed_language", "worldview_story",
    "translation_desk", "rebuilding_meaning", "replacement_failure", "mottainai",
    "itadakimasu", "otsukaresama", "japanese_sensitivity", "serendipity",
    "nostalgia", "privacy", "cultural_context", "poetry_translation",
    "poetry_rhythm", "poetry_silence", "translator_long_night", "translator_consultation",
    "machine_progress", "ai_translation", "daily_communication", "ambiguity_review",
    "human_literary", "translation_bridge", "translated_performance", "closer_hearts",
)


def main() -> None:
    plan = json.loads(PLAN.read_text())
    duration = float(plan["duration"])
    unit = duration / 113
    scenes: list[dict] = []
    ordinal = 0
    for group_index, prefix in enumerate(PREFIXES):
        count = 5 if group_index == 0 else 4
        images = sorted((LESSON / "scenes/final_style01").glob(f"*_{prefix}_*.png"))
        if len(images) != count:
            raise RuntimeError(f"{prefix}: {len(images)} != {count}")
        for image in images:
            scenes.append({
                "start": round(unit * ordinal, 3),
                "image": str(image.relative_to(LESSON)),
                "purpose": prefix,
            })
            ordinal += 1
    gaps = [float(b["start"]) - float(a["start"]) for a, b in zip(scenes, scenes[1:])]
    gaps.append(duration - float(scenes[-1]["start"]))
    if len(scenes) != 113 or min(gaps) < 1.299 or max(gaps) > 1.9:
        raise RuntimeError((len(scenes), min(gaps), max(gaps)))
    plan["scenes"] = scenes
    plan["qa_status"] = "READY_TO_RENDER_STYLE01_TRANSLATION_REVIEWED"
    plan["output_name"] = "h075_adopted_song_cinematic_v1.mp4"
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n")
    print(f"H075 video plan: {len(scenes)} scenes, min {min(gaps):.3f}s max {max(gaps):.3f}s")


if __name__ == "__main__":
    main()
