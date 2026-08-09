#!/usr/bin/env python3
"""Create H081 dense Style01 crops aligned to the exploration lyric timeline."""
from __future__ import annotations

from bisect import bisect_right
import json
import shutil
import subprocess
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H081"
REF = LESSON / "scenes/character_refs"
OUT = LESSON / "scenes/final_style01"
VISUAL_BIBLE = LESSON / "planning/visual_bible_style01.json"
DURATION = 197.400979
SCENE_COUNT = 152
UNIT = DURATION / SCENE_COUNT

CROP_SEQUENCES = {
    "C": (
        None,
        "1460x821+106+30",
        "1280x720+196+45",
        "1100x619+286+60",
        "980x551+346+70",
    ),
    "L": (
        None,
        "1460x821+0+30",
        "1280x720+0+45",
        "1100x619+0+60",
        "980x551+0+70",
    ),
    "R": (
        None,
        "1460x821+212+30",
        "1280x720+392+45",
        "1100x619+572+60",
        "980x551+692+70",
    ),
}

# Choose only the fixed focal side of a master. Each shot then holds or pushes
# straight toward that side; it never wanders, shakes, or changes direction.
ANCHORS = {
    "navigation_objects_closeup": "L",
    "unseen_places_question": "R",
    "many_exploration_histories_archive": "R",
    "caribbean_landfall_inhabited": "R",
    "taino_perspective_museum": "R",
    "atlantic_navigation_1492": "L",
    "pacific_crossing_hardship": "L",
    "fleet_after_magellan_loss": "R",
    "victoria_elcano_return": "R",
    "polar_exploration_equipment": "L",
    "early_deep_sea_exploration": "R",
    "amundsen_framheim_basecamp": "R",
    "amundsen_dog_sled_route": "L",
    "scott_return_hardship": "R",
    "polar_personal_records_archive": "L",
    "everest_period_oxygen_equipment": "L",
    "hillary_tenzing_ascent": "R",
    "everest_safe_descent_support": "R",
    "determination_obstacle_climb": "L",
    "endurance_beset_in_ice": "R",
    "endurance_crushed_sinking": "R",
    "endurance_lifeboats_escape": "L",
    "elephant_island_camp_22": "R",
    "james_caird_six": "L",
    "south_georgia_crossing_three": "R",
    "yelcho_rescue_22": "R",
    "modern_deep_sea_rov": "R",
    "space_human_research": "L",
    "human_limits_training": "R",
    "boundary_question_museum": "R",
    "ocean_horizon_dawn_finale": "R",
}


def snap_before(time: float) -> float:
    return int(time / UNIT) * UNIT


def masters() -> tuple[tuple[float, str, str, str], ...]:
    bible = json.loads(VISUAL_BIBLE.read_text(encoding="utf-8"))
    rows = []
    for item in bible["masters"]:
        filename = str(item["file"])
        prefix = filename.removesuffix("_master.png")
        rows.append(
            (snap_before(float(item["time"])), filename, prefix, ANCHORS.get(prefix, "C"))
        )
    return tuple(rows)


def render(src: Path, dst: Path, crop: str | None) -> None:
    if crop is None:
        shutil.copyfile(src, dst)
        return
    subprocess.run(
        [
            "magick", str(src), "-crop", crop, "+repage", "-resize", "1672x941^",
            "-gravity", "center", "-extent", "1672x941", str(dst),
        ],
        check=True,
    )


def main() -> None:
    rows = masters()
    if len(rows) != 50:
        raise RuntimeError(f"H081 master count: {len(rows)} != 50")
    OUT.mkdir(parents=True, exist_ok=True)
    if any(OUT.iterdir()):
        raise RuntimeError(f"H081 output directory must be empty before rebuilding: {OUT}")

    for _, filename, _, _ in rows:
        source = REF / filename
        if not source.is_file():
            raise FileNotFoundError(source)

    starts = [item[0] for item in rows]
    usage: Counter[str] = Counter()
    expected: list[Path] = []
    for ordinal in range(SCENE_COUNT):
        time = UNIT * ordinal
        master_index = bisect_right(starts, time + 1e-9) - 1
        _, filename, prefix, anchor = rows[master_index]
        usage[prefix] += 1
        crop_number = usage[prefix]
        sequence = CROP_SEQUENCES[anchor]
        crop = sequence[min(crop_number - 1, len(sequence) - 1)]
        destination = OUT / f"{ordinal + 1:03d}_{prefix}_{crop_number:02d}.png"
        render(REF / filename, destination, crop)
        expected.append(destination)

    actual = sorted(OUT.glob("[0-9][0-9][0-9]_*.png"))
    missing = [prefix for _, _, prefix, _ in rows if usage[prefix] == 0]
    if actual != expected or len(actual) != SCENE_COUNT or missing:
        raise RuntimeError(
            f"H081 scene mismatch actual={len(actual)} expected={SCENE_COUNT} missing={missing}"
        )
    print(f"H081 final_style01 files verified: {len(actual)}; masters used: {len(usage)}")


if __name__ == "__main__":
    main()
