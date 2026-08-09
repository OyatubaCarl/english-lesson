#!/usr/bin/env python3
"""Build the H081 152-cut video plan and verify lyric-to-image alignment."""
from __future__ import annotations

from bisect import bisect_right
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H081"
PLAN = LESSON / "planning/video_plan.json"
SCENE_COUNT = 152
NAME_RE = re.compile(r"^\d{3}_(.+)_\d{2}\.png$")
EXPECTED_AT = {
    13.0: "unseen_places_question",
    18.0: "many_exploration_histories_archive",
    22.0: "maritime_gallery_transition",
    24.0: "columbus_1492_departure",
    27.0: "atlantic_navigation_1492",
    30.0: "caribbean_landfall_inhabited",
    33.0: "taino_perspective_museum",
    36.0: "magellan_five_ship_departure",
    40.0: "strait_of_magellan_navigation",
    44.0: "pacific_crossing_hardship",
    47.0: "fleet_after_magellan_loss",
    50.0: "victoria_elcano_return",
    54.0: "mapmaking_after_circumnavigation",
    60.0: "twentieth_century_exploration_gallery",
    63.0: "polar_exploration_equipment",
    67.0: "high_mountain_exploration",
    71.0: "early_deep_sea_exploration",
    74.0: "early_aviation_exploration",
    77.0: "amundsen_framheim_basecamp",
    80.0: "amundsen_dog_sled_route",
    84.0: "amundsen_five_at_south_pole",
    88.0: "scott_five_arrive_south_pole",
    92.0: "scott_return_hardship",
    96.0: "polar_endurance_sacrifice",
    101.0: "polar_personal_records_archive",
    105.0: "everest_1953_basecamp_team",
    109.0: "everest_period_oxygen_equipment",
    113.0: "hillary_tenzing_ascent",
    117.0: "everest_summit_pair",
    121.0: "everest_safe_descent_support",
    124.0: "determination_obstacle_climb",
    133.0: "shackleton_expedition_departure",
    136.0: "endurance_beset_in_ice",
    141.0: "endurance_crushed_sinking",
    144.0: "endurance_ice_camp_28",
    146.0: "endurance_lifeboats_escape",
    148.0: "elephant_island_camp_22",
    150.0: "james_caird_six",
    153.0: "south_georgia_crossing_three",
    155.0: "yelcho_rescue_22",
    158.0: "collective_leadership_survival",
    162.0: "modern_deep_sea_rov",
    165.0: "space_human_research",
    169.0: "human_limits_training",
    172.0: "boundary_question_museum",
    177.0: "beyond_question_notebook",
    183.0: "shared_human_exploration_gallery",
    189.0: "ocean_horizon_dawn_finale",
}


def purpose(image: Path) -> str:
    match = NAME_RE.match(image.name)
    if not match:
        raise RuntimeError(f"unexpected H081 scene filename: {image.name}")
    return match.group(1)


def main() -> None:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    duration = float(plan["duration"])
    if abs(duration - 197.400979) > 0.02:
        raise RuntimeError(f"unexpected H081 adopted duration: {duration}")
    unit = duration / SCENE_COUNT
    images = sorted((LESSON / "scenes/final_style01").glob("[0-9][0-9][0-9]_*.png"))
    if len(images) != SCENE_COUNT:
        raise RuntimeError(f"H081 scene count: {len(images)} != {SCENE_COUNT}")

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
    if min(gaps) < 1.295 or max(gaps) > 1.302:
        raise RuntimeError((len(scenes), min(gaps), max(gaps)))

    scene_starts = [float(scene["start"]) for scene in scenes]
    for time, expected in EXPECTED_AT.items():
        scene = scenes[bisect_right(scene_starts, time) - 1]
        if scene["purpose"] != expected:
            raise RuntimeError(
                f"H081 alignment at {time:.2f}s: {scene['purpose']} != {expected}"
            )

    plan["title_en"] = "Adventure and Exploration"
    plan["scenes"] = scenes
    plan["qa_status"] = "READY_TO_RENDER_STYLE01_EXPLORATION_HISTORY_REVIEWED"
    plan["output_name"] = "h081_adopted_song_cinematic_v1.mp4"
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"H081 video plan: {len(scenes)} scenes, min {min(gaps):.3f}s "
        f"max {max(gaps):.3f}s; lyric checkpoints PASS"
    )


if __name__ == "__main__":
    main()
