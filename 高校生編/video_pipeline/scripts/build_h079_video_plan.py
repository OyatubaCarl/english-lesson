#!/usr/bin/env python3
"""Build the H079 97-cut video plan and verify lyric-to-image alignment."""
from __future__ import annotations

from bisect import bisect_right
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H079"
PLAN = LESSON / "planning/video_plan.json"
SCENE_COUNT = 97
NAME_RE = re.compile(r"^\d{3}_(.+)_\d{2}\.png$")
EXPECTED_AT = {
    31.50: "reusable_booster_landing",
    35.00: "recovered_booster_inspection",
    43.00: "earth_mars_orbital_geometry",
    51.00: "deep_space_transit_spacecraft",
    54.00: "radiation_shielding_dosimeter",
    56.00: "microgravity_exercise",
    59.00: "isolation_crew_support",
    63.00: "closed_loop_life_support",
    68.00: "mars_water_ice_isru_concept",
    71.00: "mars_greenhouse_concept",
    74.00: "mars_habitat_concept",
    78.00: "launch_infrastructure_cost",
    83.00: "public_budget_dialogue",
    86.00: "earth_needs_health_climate",
    89.00: "water_purification_spinoff",
    93.00: "disaster_environment_sensor",
    97.00: "technology_transfer_workshop",
    102.00: "frontier_unknown_boundary",
    108.00: "planetary_protection_cleanroom",
    111.00: "international_governance_roundtable",
    115.00: "philosophical_observatory",
    120.00: "shared_future_earth_mars_finale",
}


def purpose(image: Path) -> str:
    match = NAME_RE.match(image.name)
    if not match:
        raise RuntimeError(f"unexpected H079 scene filename: {image.name}")
    return match.group(1)


def main() -> None:
    plan = json.loads(PLAN.read_text())
    duration = float(plan["duration"])
    if abs(duration - 126.320167) > 0.02:
        raise RuntimeError(f"unexpected H079 adopted duration: {duration}")
    unit = duration / SCENE_COUNT
    images = sorted((LESSON / "scenes/final_style01").glob("[0-9][0-9][0-9]_*.png"))
    if len(images) != SCENE_COUNT:
        raise RuntimeError(f"H079 scene count: {len(images)} != {SCENE_COUNT}")

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
                f"H079 alignment at {time:.2f}s: {scene['purpose']} != {expected}"
            )

    plan["scenes"] = scenes
    plan["qa_status"] = "READY_TO_RENDER_STYLE01_SPACE_FUTURE_LYRIC_ALIGNED"
    plan["output_name"] = "h079_adopted_song_cinematic_v1.mp4"
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n")
    print(
        f"H079 video plan: {len(scenes)} scenes, min {min(gaps):.3f}s "
        f"max {max(gaps):.3f}s; lyric checkpoints PASS"
    )


if __name__ == "__main__":
    main()
