#!/usr/bin/env python3
"""Build H076 dense Style01 video plan with uniform 1.304-second cuts."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H076"
PLAN = LESSON / "planning/video_plan.json"
PREFIXES = (
    "present_museum", "forced_flight", "economic_migration", "farewell_decision",
    "departure_port", "steamship_crossing", "family_solo", "ellis_arrival",
    "language_interpreter", "newcomer_loneliness", "passage_cost", "tenement_housing",
    "low_wage_work", "discrimination", "mutual_aid", "adult_language",
    "bilingual_school", "gradual_adjustment", "ancestral_language", "food_tradition",
    "music_tradition", "festival", "contributions", "multicultural_city",
    "active_tolerance", "countering_prejudice", "civic_participation", "inclusive_finale",
)


def main() -> None:
    plan = json.loads(PLAN.read_text())
    duration = float(plan["duration"])
    unit = duration / 110
    scenes: list[dict] = []
    ordinal = 0
    for group_index, prefix in enumerate(PREFIXES):
        count = 3 if group_index < 2 else 4
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
    if len(scenes) != 110 or min(gaps) < 1.299 or max(gaps) > 1.9:
        raise RuntimeError((len(scenes), min(gaps), max(gaps)))
    plan["scenes"] = scenes
    plan["qa_status"] = "READY_TO_RENDER_STYLE01_MIGRATION_REVIEWED"
    plan["output_name"] = "h076_adopted_song_cinematic_v1.mp4"
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n")
    print(f"H076 video plan: {len(scenes)} scenes, min {min(gaps):.3f}s max {max(gaps):.3f}s")


if __name__ == "__main__":
    main()
