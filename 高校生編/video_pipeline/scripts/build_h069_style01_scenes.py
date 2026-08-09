#!/usr/bin/env python3
"""Create H069 dense Style01 crops from the twenty-three accepted masters."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "H069" / "scenes" / "character_refs"
OUT = ROOT / "H069" / "scenes" / "final_style01"


@dataclass(frozen=True)
class Series:
    master: str
    start: int
    prefix: str
    crops: tuple[str | None, ...]


FULL = None
WL = "1420x799+0+10"
WR = "1420x799+252+10"
ML = "1320x743+0+35"
MR = "1320x743+352+35"
L = "1180x664+0+65"
R = "1180x664+492+65"
CL = "1100x619+90+85"
CR = "1100x619+482+85"
XC = "920x518+376+120"
C = "1180x664+246+65"

P3 = (FULL, WL, C)
P4 = (FULL, WL, WR, C)
P5 = (FULL, WL, WR, ML, C)
P6 = (FULL, WL, WR, ML, MR, C)
P7 = (FULL, WL, WR, ML, MR, L, C)
P8 = (FULL, WL, WR, ML, MR, L, R, C)
P9 = (FULL, WL, WR, ML, MR, L, R, XC, C)
P10 = (FULL, WL, WR, ML, MR, L, R, CL, CR, C)


SERIES = (
    Series("mount_wilson_night_master.png", 1, "mount_wilson", P5),
    Series("hubble_humason_observing_master.png", 6, "hubble_humason", P8),
    Series("distance_spectra_relation_master.png", 14, "spectra_relation", P4),
    Series("expansion_everywhere_master.png", 18, "expansion_everywhere", P4),
    Series("hot_dense_no_center_master.png", 22, "hot_dense", P4),
    Series("lemaitre_1927_master.png", 26, "lemaitre", P5),
    Series("age_multiple_evidence_master.png", 31, "age_evidence", P6),
    Series("early_universe_cooling_master.png", 37, "early_cooling", P5),
    Series("nucleosynthesis_nuclei_master.png", 42, "nucleosynthesis", P3),
    Series("first_stars_cosmic_dawn_master.png", 45, "first_stars", P4),
    Series("holmdel_horn_master.png", 49, "holmdel_horn", P6),
    Series("penzias_wilson_receiver_master.png", 55, "receiver", P6),
    Series("cmb_all_sky_master.png", 61, "cmb_all_sky", P9),
    Series("big_bang_evidence_master.png", 70, "evidence", P5),
    Series("milky_way_star_count_master.png", 75, "milky_way", P8),
    Series("galaxy_deep_field_master.png", 83, "deep_field", P5),
    Series("cosmic_composition_master.png", 88, "composition", P4),
    Series("dark_matter_lensing_master.png", 92, "dark_matter", P5),
    Series("dark_energy_supernova_master.png", 97, "dark_energy", P5),
    Series("physics_challenge_team_master.png", 102, "physics_team", P4),
    Series("jwst_space_master.png", 106, "jwst", P10),
    Series("jwst_early_galaxy_master.png", 116, "early_galaxy", P7),
    Series("museum_student_outro_master.png", 123, "museum_outro", P10),
)

TINTS = ("#23344d", "#5e4e46", "#4d5363")


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
    if variant >= 9:
        command += ["-fill", TINTS[(variant - 9) % len(TINTS)], "-colorize", "2%"]
    command.append(str(target))
    subprocess.run(command, check=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    expected: list[Path] = []
    for series in SERIES:
        source = REF / series.master
        if not source.is_file():
            raise FileNotFoundError(source)
        for offset, crop in enumerate(series.crops):
            number = series.start + offset
            target = OUT / f"{number:03d}_{series.prefix}_{offset + 1:02d}.png"
            render(source, target, crop, offset + 1)
            expected.append(target)
    actual = sorted(OUT.glob("[0-9][0-9][0-9]_*.png"))
    if len(actual) != 132 or actual != expected:
        raise RuntimeError(f"H069 scene mismatch: actual={len(actual)} expected=132")
    for path in actual:
        size = subprocess.run(
            ["magick", "identify", "-format", "%wx%h", str(path)],
            check=True, capture_output=True, text=True,
        ).stdout
        if size != "1672x941":
            raise RuntimeError(f"unexpected size {size}: {path}")
    print("H069 final_style01 files verified: 132")


if __name__ == "__main__":
    main()
