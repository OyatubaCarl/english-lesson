#!/usr/bin/env python3
"""Build H074 dense Style01 video plan."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H074"
PLAN = LESSON / "planning/video_plan.json"


GROUPS = (
    (0.0, 5.6, "world_regions", 4),
    (5.6, 11.2, "ritual_preparation", 4),
    (11.2, 16.8, "nature_relationship", 4),
    (16.8, 22.4, "hatsumode", 4),
    (22.4, 26.8, "setsubun", 3),
    (26.8, 32.4, "obon", 4),
    (32.4, 38.0, "regional_festival", 4),
    (38.0, 45.0, "gion_procession", 5),
    (45.0, 50.4, "gion_rope", 4),
    (50.4, 57.4, "nebuta_night", 5),
    (57.4, 63.0, "nebuta_hayashi", 4),
    (63.0, 68.6, "festival_rehearsal", 4),
    (68.6, 74.2, "community_identity", 4),
    (74.2, 78.5, "birth_rite", 3),
    (78.5, 82.8, "adult_marriage", 3),
    (82.8, 87.1, "death_memorial", 3),
    (87.1, 92.7, "turning_point", 4),
    (92.7, 98.3, "global_exchange", 4),
    (98.3, 103.9, "urban_migration", 4),
    (103.9, 108.2, "fading_craft", 3),
    (108.2, 113.8, "safeguarding", 4),
    (113.8, 119.4, "community_inventory", 4),
    (119.4, 125.0, "washoku", 4),
    (125.0, 130.6, "noh_theatre", 4),
    (130.6, 136.2, "washi_craft", 4),
    (136.2, 140.5, "craft_adaptation", 3),
    (140.5, 146.1, "handoff", 4),
    (146.1, 151.7, "living_final", 4),
    (151.7, 158.560167, "outro_final", 5),
)


def main() -> None:
    plan = json.loads(PLAN.read_text())
    scenes: list[dict] = []
    for start, end, prefix, count in GROUPS:
        images = sorted((LESSON / "scenes/final_style01").glob(f"*_{prefix}_*.png"))
        if len(images) != count:
            raise RuntimeError(f"{prefix}: {len(images)} != {count}")
        gap = (end - start) / count
        for index, image in enumerate(images):
            scenes.append(
                {
                    "start": round(start + gap * index, 3),
                    "image": str(image.relative_to(LESSON)),
                    "purpose": prefix,
                }
            )
    gaps = [
        float(right["start"]) - float(left["start"])
        for left, right in zip(scenes, scenes[1:])
    ] + [float(plan["duration"]) - float(scenes[-1]["start"])]
    if min(gaps) < 1.299 or max(gaps) > 1.9:
        raise RuntimeError((len(scenes), min(gaps), max(gaps)))
    plan["scenes"] = scenes
    plan["qa_status"] = "READY_TO_RENDER_STYLE01_CULTURALLY_REVIEWED"
    plan["output_name"] = "h074_adopted_song_cinematic_v1.mp4"
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n")
    print(
        f"H074 video plan: {len(scenes)} scenes, "
        f"min {min(gaps):.3f}s max {max(gaps):.3f}s"
    )


if __name__ == "__main__":
    main()
