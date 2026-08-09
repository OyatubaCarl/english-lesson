#!/usr/bin/env python3
"""Create H072 dense Style01 crops from the accepted masters."""
from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "H072/scenes/character_refs"
OUT = ROOT / "H072/scenes/final_style01"


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
    Series("japan_plate_context_master.png", "plate_intro", (F, WL, C)),
    Series("seismograph_network_master.png", "seismo_intro", (F, WL, MR, R, C)),
    Series("japan_plate_context_master.png", "quake_prone", (F, WR, C)),
    Series("japan_plate_context_master.png", "plate_complex", (F, ML, DC)),
    Series("seismograph_network_master.png", "tremor_observation", (F, WL, MR, C)),
    Series("tohoku_before_quake_master.png", "tohoku_before", (F, WL, C)),
    Series("quake_drop_cover_master.png", "quake_safe", (F, MR, C)),
    Series("magnitude_seismogram_master.png", "magnitude", (F, WL, R, C)),
    Series("tsunami_offshore_master.png", "tsunami_offshore", (F, C)),
    Series("coastal_family_uphill_master.png", "uphill_evacuation", (F, WL, C)),
    Series("tsunami_aftermath_memorial_master.png", "tsunami_memorial", (F, C)),
    Series("fukushima_plant_exterior_master.png", "plant_exterior", (F, C)),
    Series("fukushima_power_loss_master.png", "power_loss", (F, WL, MR, C)),
    Series("fukushima_control_room_master.png", "control_room", (F, WL, MR, C)),
    Series("evacuation_bus_master.png", "evacuation_bus", (F, MR, C)),
    Series("evacuation_shelter_master.png", "evacuation_shelter", (F, WL, C)),
    Series("responders_search_master.png", "responders_begin", (F, WL, C)),
    Series("rescue_hands_master.png", "rescue_hands", (F, DL, DR, C)),
    Series("responders_search_master.png", "responders_continue", (F, MR, C)),
    Series("international_aid_master.png", "international_aid", (F, WL, MR, C)),
    Series("family_preparedness_master.png", "preparedness_family", (F, MR, C)),
    Series("community_drill_master.png", "preparedness_shared", (F, WL, C)),
    Series("emergency_supplies_close_master.png", "emergency_supplies", (F, DL, DC)),
    Series("school_evacuation_drill_master.png", "school_drill", (F, WL, MR, C)),
    Series("eew_phone_master.png", "eew_phone", (F, DL, C)),
    Series("eew_limit_action_master.png", "eew_action", (F, WL, MR, DR, C)),
    Series("reconstruction_coast_master.png", "reconstruction_begin", (F, WL, C)),
    Series("ongoing_memory_master.png", "reconstruction_unfinished", (F, MR, C)),
    Series("reconstruction_coast_master.png", "reconstruction_step", (F, C)),
    Series("ongoing_memory_master.png", "wounds_remain", (F, MR, C)),
    Series("next_generation_memorial_master.png", "next_generation", (F, WL, MR, C)),
    Series("next_generation_memorial_master.png", "lessons_passed", (F, WR, R, C)),
    Series("reconstruction_coast_master.png", "outro_coast", (F, MR, C)),
    Series("next_generation_memorial_master.png", "outro_final", (F, R, C)),
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
        raise RuntimeError(f"H072 scene mismatch actual={len(actual)} expected={EXPECTED}")
    print(f"H072 final_style01 files verified: {EXPECTED}")


if __name__ == "__main__":
    main()
