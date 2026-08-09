#!/usr/bin/env python3
"""Create H074 dense Style01 crops from the accepted masters."""
from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "H074/scenes/character_refs"
OUT = ROOT / "H074/scenes/final_style01"


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
    Series("world_regions_class_master.png", "world_regions", (F, WL, MR, C)),
    Series("local_ritual_preparation_master.png", "ritual_preparation", (F, WL, R, C)),
    Series("nature_season_relationship_master.png", "nature_relationship", (F, WR, R, C)),
    Series("hatsumode_dawn_master.png", "hatsumode", (F, WL, MR, C)),
    Series("setsubun_home_master.png", "setsubun", (F, MR, C)),
    Series("obon_family_memory_master.png", "obon", (F, WL, R, C)),
    Series("regional_festival_preparation_master.png", "regional_festival", (F, WL, MR, C)),
    Series("gion_yamahoko_procession_master.png", "gion_procession", (F, WL, MR, R, C)),
    Series("gion_rope_build_master.png", "gion_rope", (F, DL, DC, C)),
    Series("aomori_nebuta_night_master.png", "nebuta_night", (F, WL, MR, R, C)),
    Series("nebuta_hayashi_haneto_master.png", "nebuta_hayashi", (F, WL, R, C)),
    Series("festival_rehearsal_master.png", "festival_rehearsal", (F, WL, MR, C)),
    Series("community_identity_master.png", "community_identity", (F, WR, R, C)),
    Series("birth_rite_support_master.png", "birth_rite", (F, MR, C)),
    Series("adulthood_marriage_rites_master.png", "adult_marriage", (F, WL, C)),
    Series("death_memorial_rite_master.png", "death_memorial", (F, MR, C)),
    Series("turning_point_support_master.png", "turning_point", (F, WL, R, C)),
    Series("global_exchange_master.png", "global_exchange", (F, WL, MR, C)),
    Series("urban_migration_empty_store_master.png", "urban_migration", (F, WR, R, C)),
    Series("fading_craft_tools_master.png", "fading_craft", (F, DL, C)),
    Series("safeguarding_workshop_master.png", "safeguarding", (F, WL, MR, C)),
    Series("community_inventory_master.png", "community_inventory", (F, WL, R, C)),
    Series("washoku_new_year_master.png", "washoku", (F, WL, MR, C)),
    Series("noh_theatre_master.png", "noh_theatre", (F, WL, R, C)),
    Series("washi_craft_master.png", "washi_craft", (F, DL, DR, C)),
    Series("living_craft_adaptation_master.png", "craft_adaptation", (F, MR, C)),
    Series("intergenerational_handoff_master.png", "handoff", (F, WL, R, C)),
    Series("living_tradition_final_master.png", "living_final", (F, WL, MR, C)),
    Series("living_tradition_final_master.png", "outro_final", (F, WR, L, R, C)),
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
        raise RuntimeError(f"H074 scene mismatch actual={len(actual)} expected={EXPECTED}")
    print(f"H074 final_style01 files verified: {EXPECTED}")


if __name__ == "__main__":
    main()
