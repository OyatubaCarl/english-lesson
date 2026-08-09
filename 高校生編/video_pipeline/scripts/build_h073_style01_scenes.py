#!/usr/bin/env python3
"""Create H073 dense Style01 crops from the accepted masters."""
from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "H073/scenes/character_refs"
OUT = ROOT / "H073/scenes/final_style01"


@dataclass(frozen=True)
class Series:
    master: str
    prefix: str
    crops: tuple[str | None, ...]


F = None
WL = "1420x799+0+20"
WR = "1420x799+252+20"
ML = "1320x743+0+55"
MR = "1320x743+352+55"
L = "1180x664+0+90"
R = "1180x664+492+90"
C = "1180x664+246+90"
CL = "1100x619+80+110"
CR = "1100x619+492+110"
DL = "920x518+40+130"
DC = "920x518+376+130"
DR = "920x518+712+130"


SERIES = (
    Series("cell_atlas_room_master.png", "cell_atlas_intro", (F, WL, C)),
    Series("cells_microscopy_master.png", "body_cells", (F, WL, MR, R, C)),
    Series("heart_pulse_master.png", "heart_pulse", (F, WL, MR, C)),
    Series("lungs_breath_master.png", "lungs_breath", (F, WR, R, C)),
    Series("digestion_meal_master.png", "digestion_meal", (F, MR, C)),
    Series("digestive_model_master.png", "digestive_system", (F, WL, MR, C)),
    Series("nutrient_absorption_master.png", "nutrient_absorption", (F, WL, R, C)),
    Series("balanced_nutrients_master.png", "nutrient_variety", (F, DL, DC, DR)),
    Series("tissue_repair_master.png", "tissue_repair", (F, WL, MR, C)),
    Series("inclusive_exercise_master.png", "exercise", (F, WL, C)),
    Series("sleep_routine_master.png", "health_three_parts", (F, MR, C)),
    Series("health_social_conditions_master.png", "social_conditions", (F, WL, MR, C)),
    Series("sedentary_risk_master.png", "inactivity_risk", (F, WL, R, C)),
    Series("clinician_risk_discussion_master.png", "diabetes_risk", (F, MR, C)),
    Series("blood_pressure_master.png", "salt_pressure", (F, C)),
    Series("salt_sugar_close_master.png", "sugar_balance", (F, DL, C)),
    Series("sleep_immune_master.png", "sleep_immune", (F, WL, MR, C)),
    Series("study_stress_master.png", "acute_stress", (F, MR, C)),
    Series("stress_support_master.png", "stress_support", (F, WL, C)),
    Series("chronic_stress_care_master.png", "chronic_stress", (F, WL, MR, C)),
    Series("health_screening_master.png", "health_screening", (F, C)),
    Series("screening_limits_master.png", "screening_limits", (F, C)),
    Series("shared_decision_master.png", "shared_decision", (F, MR, C)),
    Series("body_dignity_master.png", "body_dignity", (F, WL, MR, C)),
    Series("health_social_conditions_master.png", "support_environment", (F, WR, C)),
    Series("daily_support_final_master.png", "daily_choice", (F, WL, MR, C)),
    Series("inclusive_exercise_master.png", "physical_wellbeing", (F, WR, R, C)),
    Series("daily_support_final_master.png", "social_wellbeing", (F, WL, R, C)),
    Series("daily_support_final_master.png", "daily_fabric", (F, MR, C)),
    Series("daily_support_final_master.png", "outro_final", (F, R, C)),
)


EXPECTED = sum(len(series.crops) for series in SERIES)


def render(src: Path, dst: Path, crop: str | None) -> None:
    if dst.is_file() and dst.stat().st_size:
        return
    if crop is None:
        shutil.copyfile(src, dst)
        return
    subprocess.run(
        [
            "magick",
            str(src),
            "-crop",
            crop,
            "+repage",
            "-resize",
            "1672x941^",
            "-gravity",
            "center",
            "-extent",
            "1672x941",
            str(dst),
        ],
        check=True,
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    expected: list[Path] = []
    number = 1
    for series in SERIES:
        src = REF / series.master
        if not src.is_file():
            raise FileNotFoundError(src)
        for index, crop in enumerate(series.crops, 1):
            dst = OUT / f"{number:03d}_{series.prefix}_{index:02d}.png"
            render(src, dst, crop)
            expected.append(dst)
            number += 1
    actual = sorted(OUT.glob("[0-9][0-9][0-9]_*.png"))
    if actual != expected:
        raise RuntimeError(f"H073 scene mismatch actual={len(actual)} expected={EXPECTED}")
    print(f"H073 final_style01 files verified: {EXPECTED}")


if __name__ == "__main__":
    main()
