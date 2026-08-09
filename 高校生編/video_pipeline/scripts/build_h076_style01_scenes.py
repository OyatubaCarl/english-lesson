#!/usr/bin/env python3
"""Create H076 dense Style01 crops from accepted masters."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "H076/scenes/character_refs"
OUT = ROOT / "H076/scenes/final_style01"

F = None
WL = "1420x799+0+20"
WR = "1420x799+252+20"
MR = "1320x743+352+55"
L = "1180x664+0+90"
R = "1180x664+492+90"
C = "1180x664+246+90"

MASTERS = (
    ("present_museum_question_master.png", "present_museum"),
    ("forced_flight_master.png", "forced_flight"),
    ("economic_migration_master.png", "economic_migration"),
    ("farewell_decision_master.png", "farewell_decision"),
    ("atlantic_departure_port_master.png", "departure_port"),
    ("steamship_crossing_master.png", "steamship_crossing"),
    ("family_and_solo_passengers_master.png", "family_solo"),
    ("ellis_arrival_master.png", "ellis_arrival"),
    ("language_interpreter_master.png", "language_interpreter"),
    ("newcomer_loneliness_master.png", "newcomer_loneliness"),
    ("passage_cost_master.png", "passage_cost"),
    ("tenement_housing_master.png", "tenement_housing"),
    ("low_wage_work_master.png", "low_wage_work"),
    ("discrimination_barrier_master.png", "discrimination"),
    ("mutual_aid_network_master.png", "mutual_aid"),
    ("adult_language_class_master.png", "adult_language"),
    ("bilingual_school_home_master.png", "bilingual_school"),
    ("gradual_adjustment_master.png", "gradual_adjustment"),
    ("ancestral_language_home_master.png", "ancestral_language"),
    ("food_tradition_master.png", "food_tradition"),
    ("music_tradition_master.png", "music_tradition"),
    ("neighborhood_festival_master.png", "festival"),
    ("shared_contributions_master.png", "contributions"),
    ("multicultural_city_master.png", "multicultural_city"),
    ("active_tolerance_master.png", "active_tolerance"),
    ("countering_prejudice_master.png", "countering_prejudice"),
    ("civic_participation_master.png", "civic_participation"),
    ("inclusive_finale_master.png", "inclusive_finale"),
)


def render(src: Path, dst: Path, crop: str | None) -> None:
    if dst.is_file() and dst.stat().st_size:
        return
    if crop is None:
        shutil.copyfile(src, dst)
        return
    subprocess.run(
        ["magick", str(src), "-crop", crop, "+repage", "-resize", "1672x941^",
         "-gravity", "center", "-extent", "1672x941", str(dst)],
        check=True,
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    expected: list[Path] = []
    number = 1
    for master_index, (master, prefix) in enumerate(MASTERS):
        src = REF / master
        if not src.is_file():
            raise FileNotFoundError(src)
        if master_index == 0:
            crops = (F, WL, C)
        elif master_index == 1:
            crops = (F, WR, C)
        elif master_index % 3 == 0:
            crops = (F, WR, R, C)
        elif master_index % 3 == 1:
            crops = (F, WL, MR, C)
        else:
            crops = (F, WL, L, C)
        for crop_index, crop in enumerate(crops, 1):
            dst = OUT / f"{number:03d}_{prefix}_{crop_index:02d}.png"
            render(src, dst, crop)
            expected.append(dst)
            number += 1
    actual = sorted(OUT.glob("[0-9][0-9][0-9]_*.png"))
    if actual != expected or len(actual) != 110:
        raise RuntimeError(f"H076 scene mismatch actual={len(actual)} expected=110")
    print("H076 final_style01 files verified: 110")


if __name__ == "__main__":
    main()
