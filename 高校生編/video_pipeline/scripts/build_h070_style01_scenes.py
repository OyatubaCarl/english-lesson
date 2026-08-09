#!/usr/bin/env python3
"""Create H070 dense Style01 crops from the twenty-three accepted masters."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "H070" / "scenes" / "character_refs"
OUT = ROOT / "H070" / "scenes" / "final_style01"


@dataclass(frozen=True)
class Series:
    master: str
    prefix: str
    crops: tuple[str | None, ...]


FULL = None
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


# Every series corresponds to one continuous passage in the video plan.  The
# crops move from context to the object named by the narration; they never use
# random offsets or synthetic camera shake.
SERIES = (
    Series("britain_long_change_master.png", "britain_intro", (FULL, WL, MR)),
    Series("industrial_dawn_manchester_master.png", "industrial_title", (FULL, WR, C)),
    Series("britain_long_change_master.png", "britain_change", (FULL, WL, MR, L, C)),
    Series("industrial_dawn_manchester_master.png", "industrial_dawn", (FULL, WL, WR, MR, C)),
    Series("watt_newcomen_model_master.png", "newcomen_model", (FULL, R, DR)),
    Series("watt_separate_condenser_master.png", "separate_condenser", (FULL, ML, MR, DC)),
    Series("water_horse_power_master.png", "water_horse", (FULL, L, R)),
    Series("steam_cotton_mill_engine_master.png", "steam_mill", (FULL, WL, WR, C)),
    Series("manchester_cotton_mills_master.png", "manchester_mills", (FULL, MR, C)),
    Series("liverpool_cotton_port_master.png", "liverpool_port", (FULL, WL, WR, C)),
    Series("rural_family_migration_master.png", "rural_migration", (FULL, WL, MR, C)),
    Series("crowded_worker_housing_master.png", "housing_arrival", (FULL, WL, MR, C)),
    Series("crowded_worker_housing_master.png", "urbanization", (FULL, ML, C)),
    Series("spinning_mule_floor_master.png", "factory_condition", (FULL, WR, C)),
    Series("long_shift_mill_master.png", "long_shift", (FULL, ML, CR)),
    Series("wage_paydesk_master.png", "wage_paydesk", (FULL, ML, "920x518+700+300")),
    Series("child_mine_worker_master.png", "child_mine", (FULL, MR, C)),
    Series("child_mill_worker_master.png", "child_mill", (FULL, ML, C)),
    Series("early_union_meeting_master.png", "union_origins", (FULL, WL, C)),
    Series("early_union_meeting_master.png", "union_organize", (FULL, MR, DC)),
    Series("mill_strike_gate_master.png", "strike_gate", (FULL, MR, C)),
    Series("factory_inspector_1833_master.png", "factory_inspector", (FULL, ML, CR)),
    Series("child_mill_worker_master.png", "law_still_limited", (FULL, C)),
    Series("half_time_school_master.png", "half_time_school", (FULL, MR)),
    Series("long_term_living_change_master.png", "living_standard", (FULL, WL, MR, C)),
    Series("half_time_school_master.png", "public_health_factors", (FULL, ML, C)),
    Series("industrial_pollution_inequality_master.png", "pollution_gap", (FULL, ML, MR)),
    Series("enslaved_cotton_labour_master.png", "enslaved_cotton", (FULL, MR, C)),
    Series("industrial_pollution_inequality_master.png", "pollution_return", (FULL, WR, C)),
    Series("museum_student_outro_master.png", "museum_present", (FULL, R, DR)),
    Series("steam_cotton_mill_engine_master.png", "engine_reflection", (FULL, MR, C)),
    Series("mill_strike_gate_master.png", "rights_reflection", (FULL, ML, C)),
    Series("long_term_living_change_master.png", "society_reflection", (FULL, MR, C)),
    Series("museum_student_outro_master.png", "museum_final", (FULL, WL, WR, ML, R, C)),
)

TINTS = ("#253750", "#5a4b43", "#485568")
EXPECTED = 113


def render(source: Path, target: Path, crop: str | None, variant: int) -> None:
    if target.is_file() and target.stat().st_size:
        return
    if crop is None:
        shutil.copyfile(source, target)
        return
    command = [
        "magick", str(source), "-crop", crop, "+repage",
        "-resize", "1672x941^", "-gravity", "center", "-extent", "1672x941",
    ]
    if variant >= 6:
        command += ["-fill", TINTS[(variant - 6) % len(TINTS)], "-colorize", "2%"]
    command.append(str(target))
    subprocess.run(command, check=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    expected: list[Path] = []
    number = 1
    for series in SERIES:
        source = REF / series.master
        if not source.is_file():
            raise FileNotFoundError(source)
        for offset, crop in enumerate(series.crops):
            target = OUT / f"{number:03d}_{series.prefix}_{offset + 1:02d}.png"
            render(source, target, crop, offset + 1)
            expected.append(target)
            number += 1
    actual = sorted(OUT.glob("[0-9][0-9][0-9]_*.png"))
    if len(actual) != EXPECTED or actual != expected:
        raise RuntimeError(f"H070 scene mismatch: actual={len(actual)} expected={EXPECTED}")
    for path in actual:
        size = subprocess.run(
            ["magick", "identify", "-format", "%wx%h", str(path)],
            check=True, capture_output=True, text=True,
        ).stdout
        if size != "1672x941":
            raise RuntimeError(f"unexpected size {size}: {path}")
    print(f"H070 final_style01 files verified: {EXPECTED}")


if __name__ == "__main__":
    main()
