#!/usr/bin/env python3
"""Build H073 dense Style01 video plan."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H073"
PLAN = LESSON / "planning/video_plan.json"


GROUPS = (
    (0.0, 5.0, "cell_atlas_intro", 3),
    (5.0, 12.44, "body_cells", 5),
    (12.44, 19.0, "heart_pulse", 4),
    (19.0, 25.14, "lungs_breath", 4),
    (25.14, 29.1, "digestion_meal", 3),
    (29.1, 34.5, "digestive_system", 4),
    (34.5, 39.9, "nutrient_absorption", 4),
    (39.9, 45.4, "nutrient_variety", 4),
    (45.4, 51.1, "tissue_repair", 4),
    (51.1, 56.0, "exercise", 3),
    (56.0, 60.78, "health_three_parts", 3),
    (60.78, 67.38, "social_conditions", 4),
    (67.38, 73.88, "inactivity_risk", 4),
    (73.88, 77.78, "diabetes_risk", 3),
    (77.78, 80.74, "salt_pressure", 2),
    (80.74, 84.646, "sugar_balance", 3),
    (84.646, 90.92, "sleep_immune", 4),
    (90.92, 95.8, "acute_stress", 3),
    (95.8, 100.78, "stress_support", 3),
    (100.78, 106.66, "chronic_stress", 4),
    (106.66, 109.43, "health_screening", 2),
    (109.43, 112.2, "screening_limits", 2),
    (112.2, 117.42, "shared_decision", 3),
    (117.42, 123.25, "body_dignity", 4),
    (123.25, 127.16, "support_environment", 3),
    (127.16, 133.06, "daily_choice", 4),
    (133.06, 139.0, "physical_wellbeing", 4),
    (139.0, 145.0, "social_wellbeing", 4),
    (145.0, 149.32, "daily_fabric", 3),
    (149.32, 153.400167, "outro_final", 3),
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
    plan["qa_status"] = "READY_TO_RENDER_STYLE01_MEDICALLY_REVIEWED"
    plan["output_name"] = "h073_adopted_song_cinematic_v1.mp4"
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n")
    print(
        f"H073 video plan: {len(scenes)} scenes, "
        f"min {min(gaps):.3f}s max {max(gaps):.3f}s"
    )


if __name__ == "__main__":
    main()
