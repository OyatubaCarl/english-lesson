#!/usr/bin/env python3
"""Build H072 dense Style01 video plan."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H072"
PLAN = LESSON / "planning/video_plan.json"


GROUPS = (
    (0.0, 4.5, "plate_intro", 3),
    (4.5, 12.0, "seismo_intro", 5),
    (12.0, 17.12, "quake_prone", 3),
    (17.12, 22.0, "plate_complex", 3),
    (22.0, 28.1, "tremor_observation", 4),
    (28.1, 32.0, "tohoku_before", 3),
    (32.0, 36.96, "quake_safe", 3),
    (36.96, 43.74, "magnitude", 4),
    (43.74, 47.5, "tsunami_offshore", 2),
    (47.5, 51.5, "uphill_evacuation", 3),
    (51.5, 54.78, "tsunami_memorial", 2),
    (54.78, 58.5, "plant_exterior", 2),
    (58.5, 64.2, "power_loss", 4),
    (64.2, 70.02, "control_room", 4),
    (70.02, 74.9, "evacuation_bus", 3),
    (74.9, 79.92, "evacuation_shelter", 3),
    (79.92, 85.0, "responders_begin", 3),
    (85.0, 90.5, "rescue_hands", 4),
    (90.5, 95.734, "responders_continue", 3),
    (95.734, 101.325, "international_aid", 4),
    (101.325, 105.5, "preparedness_family", 3),
    (105.5, 110.7, "preparedness_shared", 3),
    (110.7, 115.6, "emergency_supplies", 3),
    (115.6, 121.4, "school_drill", 4),
    (121.4, 125.4, "eew_phone", 3),
    (125.4, 133.08, "eew_action", 5),
    (133.08, 138.0, "reconstruction_begin", 3),
    (138.0, 143.0, "reconstruction_unfinished", 3),
    (143.0, 146.0, "reconstruction_step", 2),
    (146.0, 150.2, "wounds_remain", 3),
    (150.2, 155.8, "next_generation", 4),
    (155.8, 161.42, "lessons_passed", 4),
    (161.42, 166.0, "outro_coast", 3),
    (166.0, 171.040167, "outro_final", 3),
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
    plan["qa_status"] = "READY_TO_RENDER_STYLE01_FACT_CHECKED"
    plan["output_name"] = "h072_adopted_song_cinematic_v1.mp4"
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n")
    print(
        f"H072 video plan: {len(scenes)} scenes, "
        f"min {min(gaps):.3f}s max {max(gaps):.3f}s"
    )


if __name__ == "__main__":
    main()
