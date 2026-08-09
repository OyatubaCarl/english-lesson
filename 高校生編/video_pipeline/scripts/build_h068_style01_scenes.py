#!/usr/bin/env python3
"""Create H068 dense Style01 crops from the twenty-one accepted master images."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "H068" / "scenes" / "character_refs"
OUT = ROOT / "H068" / "scenes" / "final_style01"


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
    Series("bread_finance_crisis_master.png", 1, "bread_finance", (FULL, WL, WR, ML, MR, L, R, CL, CR, XC, C, WL, WR)),
    Series("tax_privilege_gap_master.png", 14, "tax_privilege", (FULL, WL, WR, ML, MR, L, R, CL, CR, XC, C, WL)),
    Series("enlightenment_multiple_causes_master.png", 26, "enlightenment", (FULL, WL, WR, ML, C)),
    Series("estates_general_master.png", 31, "estates_general", (FULL, WL, WR, C)),
    Series("tennis_court_oath_master.png", 35, "tennis_oath", (FULL, WL, WR, ML, C)),
    Series("invalides_arms_master.png", 40, "invalides_arms", (FULL, WL, WR, C)),
    Series("bastille_gunpowder_storm_master.png", 44, "bastille_storm", (FULL, WL, WR, ML, C)),
    Series("bastille_aftermath_master.png", 49, "bastille_aftermath", (FULL, WL, WR, ML, MR, C)),
    Series("declaration_debate_master.png", 55, "declaration", (FULL, WL, WR, C)),
    Series("rights_exclusions_master.png", 59, "rights_exclusions", (FULL, WL, WR, C)),
    Series("republic_proclaimed_1792_master.png", 63, "republic_1792", (FULL, C)),
    Series("louis_trial_execution_master.png", 65, "louis_trial", (FULL, WL, WR, ML, C)),
    Series("terror_committee_war_master.png", 70, "terror_committee", (FULL, WL, WR, ML, MR, C)),
    Series("terror_civil_conflict_master.png", 76, "terror_civil", (FULL, WL, WR, ML, MR, L, R, C)),
    Series("brumaire_coup_master.png", 84, "brumaire_coup", (FULL, WL, WR, ML, C)),
    Series("consulate_continuity_master.png", 89, "consulate", (FULL, ML, C)),
    Series("civil_code_reform_limits_master.png", 92, "civil_code", (FULL, WL, WR, ML, MR, C)),
    Series("napoleon_emperor_master.png", 98, "emperor_1804", (FULL, ML, C)),
    Series("reform_war_occupation_master.png", 101, "reform_occupation", (FULL, WL, WR, ML, C)),
    Series("slavery_haiti_resistance_master.png", 106, "haiti_resistance", (FULL, WL, WR, ML, MR, C)),
    Series("motto_legacy_museum_master.png", 112, "critical_legacy", (FULL, WL, WR, ML, MR, L, R, CL, CR, XC, C, WL)),
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
    if len(actual) != 123 or actual != expected:
        raise RuntimeError(f"H068 scene mismatch: actual={len(actual)} expected=123")
    for path in actual:
        size = subprocess.run(
            ["magick", "identify", "-format", "%wx%h", str(path)],
            check=True, capture_output=True, text=True,
        ).stdout
        if size != "1672x941":
            raise RuntimeError(f"unexpected size {size}: {path}")
    print("H068 final_style01 files verified: 123")


if __name__ == "__main__":
    main()
