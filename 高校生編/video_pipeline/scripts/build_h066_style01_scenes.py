#!/usr/bin/env python3
"""Create H066 dense Style01 crops from the twenty accepted master images."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "H066" / "scenes" / "character_refs"
OUT = ROOT / "H066" / "scenes" / "final_style01"


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


SERIES = (
    Series("founding_legend_master.png", 1, "founding_legend", (FULL, WL, WR, ML, MR, C)),
    Series("palatine_archaeology_master.png", 7, "palatine_archaeology", (FULL, WL, WR, ML, MR, C)),
    Series("kingdom_to_republic_master.png", 13, "early_republic", (FULL, WL, WR, ML, C)),
    Series("italian_peninsula_expansion_master.png", 18, "italian_expansion", (FULL, WL, WR, C)),
    Series("punic_wars_aftermath_master.png", 22, "punic_aftermath", (FULL, WL, WR, C)),
    Series("republic_institutions_master.png", 26, "institutions", (FULL, ML, MR, C)),
    Series("caesar_rise_master.png", 30, "caesar_rise", (FULL, WL, WR, ML, C)),
    Series("gaul_conquest_cost_master.png", 35, "gaul_cost", (FULL, ML, C)),
    Series("dictator_assassination_aftermath_master.png", 38, "assassination_aftermath", (FULL, WL, WR, ML, MR, L, C)),
    Series("octavian_civil_war_aftermath_master.png", 45, "octavian_aftermath", (FULL, ML, MR, C)),
    Series("augustus_title_senate_master.png", 49, "augustus_title", (FULL, ML, MR, C)),
    Series("principate_power_master.png", 53, "principate", (FULL, WL, WR, ML, C)),
    Series("pax_romana_trade_master.png", 58, "pax_trade", (FULL, WL, WR, ML, C)),
    Series("roads_aqueduct_baths_colosseum_master.png", 63, "infrastructure", (FULL, WL, WR, ML, MR, C)),
    Series("province_society_slavery_master.png", 69, "province_society", (FULL, WL, WR, ML, MR, C)),
    Series("third_century_crisis_recovery_master.png", 75, "third_century", (FULL, WL, WR, ML, MR, L, C)),
    Series("east_west_courts_master.png", 82, "east_west_courts", (FULL, WL, WR, ML, MR, L, R, CL, CR, C)),
    Series("odoacer_476_transition_master.png", 92, "odoacer_transition", (FULL, WL, WR, ML, MR, C)),
    Series("legacy_transmission_master.png", 98, "legacy_transmission", (FULL, WL, WR, ML, MR, L, R, C)),
    Series("critical_legacy_museum_master.png", 106, "critical_legacy", (FULL, WL, WR, ML, MR, L, R, C)),
)

TINTS = ("#273a55", "#6b5746", "#5a5c69")


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
        cycle = variant // 9
        command += [
            "-modulate", f"{100 + cycle},{100 + (cycle % 2)},100",
            "-fill", TINTS[(cycle - 1) % len(TINTS)],
            "-colorize", f"{min(2 + cycle, 4)}%",
        ]
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
    if len(actual) != 113 or actual != expected:
        raise RuntimeError(f"H066 scene mismatch: actual={len(actual)} expected=113")
    for path in actual:
        size = subprocess.run(
            ["magick", "identify", "-format", "%wx%h", str(path)],
            check=True, capture_output=True, text=True,
        ).stdout
        if size != "1672x941":
            raise RuntimeError(f"unexpected size {size}: {path}")
    print("H066 final_style01 files verified: 113")


if __name__ == "__main__":
    main()
