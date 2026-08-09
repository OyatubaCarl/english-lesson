#!/usr/bin/env python3
"""Create H085 dense Style01 JPEG crops while preserving master PNGs."""
from __future__ import annotations

from bisect import bisect_right
from collections import Counter
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H085"
REF = LESSON / "scenes/character_refs"
OUT = LESSON / "scenes/final_style01"
VISUAL_BIBLE = LESSON / "planning/visual_bible_style01.json"
DURATION = 131.120167
SCENE_COUNT = 102
UNIT = DURATION / SCENE_COUNT

CROP_SEQUENCES = {
    "C": (None, "1460x821+106+28", "1280x720+196+42"),
    "L": (None, "1460x821+0+28", "1280x720+0+42"),
    "R": (None, "1460x821+212+28", "1280x720+392+42"),
}

ANCHORS = {
    "global_paths_to_school_dawn": "C",
    "elementary_classroom_welcoming": "L",
    "out_of_school_learning_barriers": "R",
    "community_enrollment_outreach": "L",
    "child_learning_at_market_break": "R",
    "east_african_attendance_review": "L",
    "south_asian_dropout_prevention": "R",
    "education_access_question_circle": "C",
    "poverty_school_fee_meeting": "L",
    "conflict_temporary_learning_space": "R",
    "remote_mountain_school_path": "C",
    "fee_waiver_counseling": "L",
    "safe_school_transport": "R",
    "girls_attendance_community_dialogue": "L",
    "inclusive_language_disability_class": "R",
    "disadvantages_attendance_records": "L",
    "inequality_empty_desk": "R",
    "education_breaks_poverty_cycle": "C",
    "adult_literacy_vocational_class": "L",
    "educated_woman_graduation": "R",
    "woman_health_professional_income": "L",
    "sdg4_inclusive_local_school": "R",
    "accessible_school_facilities": "C",
    "scholarship_adviser_students": "L",
    "local_teacher_training": "R",
    "books_radio_and_library": "L",
    "teacher_guided_digital_learning": "R",
    "remote_solar_offline_classroom": "C",
    "accessible_digital_textbook": "L",
    "local_language_content_creation": "R",
    "digital_divide_no_signal": "L",
    "teacher_device_repair_support": "R",
    "education_changes_individual_life": "L",
    "former_learner_returns_as_teacher": "R",
    "educated_citizens_community_decision": "C",
    "public_education_budget_roundtable": "L",
    "school_maintenance_teacher_support": "R",
    "future_classroom_human_connection": "C",
    "school_lights_evening_finale": "C",
}


def snap_before(time: float) -> float:
    return int(time / UNIT) * UNIT


def masters() -> tuple[tuple[float, str, str, str], ...]:
    bible = json.loads(VISUAL_BIBLE.read_text(encoding="utf-8"))
    rows = []
    for item in bible["masters"]:
        filename = str(item["file"])
        prefix = filename.removesuffix("_master.png")
        rows.append((snap_before(float(item["time"])), filename, prefix, ANCHORS[prefix]))
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
    if len(rows) != 39:
        raise RuntimeError(f"H085 master count: {len(rows)} != 39")
    OUT.mkdir(parents=True, exist_ok=True)
    if any(OUT.iterdir()):
        raise RuntimeError(f"H085 output directory must be empty before rebuilding: {OUT}")

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
    underused = {prefix: count for prefix, count in usage.items() if count < 2}
    if actual != expected or len(actual) != SCENE_COUNT or missing or underused:
        raise RuntimeError(
            f"H085 scene mismatch actual={len(actual)} expected={SCENE_COUNT} "
            f"missing={missing} underused={underused}"
        )
    print(
        f"H085 final_style01 files verified: {len(actual)}; masters used: {len(usage)}; "
        f"minimum uses: {min(usage.values())}"
    )


if __name__ == "__main__":
    main()
