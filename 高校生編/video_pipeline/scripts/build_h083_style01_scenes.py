#!/usr/bin/env python3
"""Create H083 dense Style01 JPEG crops while preserving master PNGs."""
from __future__ import annotations

from bisect import bisect_right
import json
import subprocess
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H083"
REF = LESSON / "scenes/character_refs"
OUT = LESSON / "scenes/final_style01"
VISUAL_BIBLE = LESSON / "planning/visual_bible_style01.json"
DURATION = 138.480979
SCENE_COUNT = 107
UNIT = DURATION / SCENE_COUNT

CROP_SEQUENCES = {
    "C": (None, "1460x821+106+28", "1280x720+196+42"),
    "L": (None, "1460x821+0+28", "1280x720+0+42"),
    "R": (None, "1460x821+212+28", "1280x720+392+42"),
}

ANCHORS = {
    "cinematheque_winter_evening": "R",
    "students_enter_cinematheque": "L",
    "projection_beam_dust_closeup": "L",
    "precinema_optical_devices": "L",
    "motion_lab_team_1891": "R",
    "kinetoscope_public_demo_1893": "L",
    "kinetoscope_parlor_1894": "R",
    "projected_screening_1895": "R",
    "traveling_exhibitor_1901": "L",
    "early_narrative_film_set_1905": "R",
    "neighborhood_picture_house_1910": "R",
    "present_film_set_team_wide": "L",
    "dramatic_bridge_report_scene": "L",
    "audience_moved_closeup": "L",
    "comedy_timing_film_scene": "R",
    "audience_laughter": "R",
    "accessible_station_film_scene": "L",
    "viewer_thinking_after_social_film": "R",
    "historical_archive_research": "L",
    "historian_community_consultation": "R",
    "historical_textile_workers_reenactment": "R",
    "emotional_truth_actor_closeup": "L",
    "film_critics_roundtable": "L",
    "first_awards_banquet_1929": "R",
    "international_film_recognition": "R",
    "dark_theater_students": "L",
    "fictional_caregiver_dawn": "R",
    "students_empathy_reflection": "L",
    "beautiful_image_projection": "R",
    "character_choice_conflict": "L",
    "student_notebook_question": "L",
    "digital_cinema_camera_team": "R",
    "nonlinear_editing_accessibility": "L",
    "home_streaming_family": "R",
    "community_digital_screening": "R",
    "early_projector_restoration": "L",
    "projector_beam_to_digital_screen": "R",
    "students_discuss_story_essence": "L",
    "cinematheque_exit_blue_hour": "R",
    "cinematheque_dawn_finale": "R",
}


def snap_before(time: float) -> float:
    return int(time / UNIT) * UNIT


def masters() -> tuple[tuple[float, str, str, str], ...]:
    bible = json.loads(VISUAL_BIBLE.read_text(encoding="utf-8"))
    rows = []
    for item in bible["masters"]:
        filename = str(item["file"])
        prefix = filename.removesuffix("_master.png")
        rows.append((snap_before(float(item["time"])), filename, prefix, ANCHORS.get(prefix, "C")))
    return tuple(rows)


def render(source: Path, destination: Path, crop: str | None) -> None:
    command = ["magick", str(source)]
    if crop is not None:
        command.extend([
            "-crop", crop, "+repage", "-resize", "1672x941^",
            "-gravity", "center", "-extent", "1672x941",
        ])
    command.extend(["-sampling-factor", "4:2:0", "-quality", "92", str(destination)])
    subprocess.run(command, check=True)


def main() -> None:
    rows = masters()
    if len(rows) != 40:
        raise RuntimeError(f"H083 master count: {len(rows)} != 40")
    OUT.mkdir(parents=True, exist_ok=True)
    if any(OUT.iterdir()):
        raise RuntimeError(f"H083 output directory must be empty before rebuilding: {OUT}")

    for _, filename, _, _ in rows:
        if not (REF / filename).is_file():
            raise FileNotFoundError(REF / filename)

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
        destination = OUT / f"{ordinal + 1:03d}_{prefix}_{crop_number:02d}.jpg"
        render(REF / filename, destination, crop)
        expected.append(destination)

    actual = sorted(OUT.glob("[0-9][0-9][0-9]_*.jpg"))
    missing = [prefix for _, _, prefix, _ in rows if usage[prefix] == 0]
    if actual != expected or len(actual) != SCENE_COUNT or missing:
        raise RuntimeError(
            f"H083 scene mismatch actual={len(actual)} expected={SCENE_COUNT} missing={missing}"
        )
    print(f"H083 final_style01 files verified: {len(actual)}; masters used: {len(usage)}")


if __name__ == "__main__":
    main()
