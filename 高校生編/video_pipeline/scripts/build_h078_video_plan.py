#!/usr/bin/env python3
"""Build the H078 101-cut video plan and verify lyric-to-image alignment."""
from __future__ import annotations

from bisect import bisect_right
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H078"
PLAN = LESSON / "planning/video_plan.json"
SCENE_COUNT = 101
NAME_RE = re.compile(r"^\d{3}_(.+)_\d{2}\.png$")
EXPECTED_AT = {
    89.21: "wildlife_corridor_community",
    92.50: "conservation_breeding_program",
    100.43: "population_monitoring_assessment",
    110.00: "biodiversity_food_agroecology",
    112.00: "biodiversity_medicine_research",
    114.00: "biodiversity_climate_wetland",
    118.00: "biodiversity_supports_people_finale",
    122.00: "connected_wetland_wildlife",
    126.00: "shared_stewardship_sunrise",
}


def purpose(image: Path) -> str:
    match = NAME_RE.match(image.name)
    if not match:
        raise RuntimeError(f"unexpected H078 scene filename: {image.name}")
    return match.group(1)


def main() -> None:
    plan = json.loads(PLAN.read_text())
    duration = float(plan["duration"])
    unit = duration / SCENE_COUNT
    images = sorted((LESSON / "scenes/final_style01").glob("[0-9][0-9][0-9]_*.png"))
    if len(images) != SCENE_COUNT:
        raise RuntimeError(f"H078 scene count: {len(images)} != {SCENE_COUNT}")

    scenes = [
        {
            "start": round(unit * ordinal, 3),
            "image": str(image.relative_to(LESSON)),
            "purpose": purpose(image),
        }
        for ordinal, image in enumerate(images)
    ]
    gaps = [float(b["start"]) - float(a["start"]) for a, b in zip(scenes, scenes[1:])]
    gaps.append(duration - float(scenes[-1]["start"]))
    if min(gaps) < 1.299 or max(gaps) > 1.9:
        raise RuntimeError((len(scenes), min(gaps), max(gaps)))

    scene_starts = [float(scene["start"]) for scene in scenes]
    for time, expected in EXPECTED_AT.items():
        scene = scenes[bisect_right(scene_starts, time) - 1]
        if scene["purpose"] != expected:
            raise RuntimeError(
                f"H078 alignment at {time:.2f}s: {scene['purpose']} != {expected}"
            )

    plan["scenes"] = scenes
    plan["qa_status"] = "READY_TO_RENDER_STYLE01_ENDANGERED_SPECIES_LYRIC_ALIGNED"
    plan["output_name"] = "h078_adopted_song_cinematic_v1.mp4"
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n")
    print(
        f"H078 video plan: {len(scenes)} scenes, min {min(gaps):.3f}s "
        f"max {max(gaps):.3f}s; lyric checkpoints PASS"
    )


if __name__ == "__main__":
    main()
