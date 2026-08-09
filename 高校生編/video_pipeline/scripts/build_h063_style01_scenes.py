#!/usr/bin/env python3
"""Create H063 dense Style01 crops from the eighteen accepted master images."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "H063" / "scenes" / "character_refs"
OUT = ROOT / "H063" / "scenes" / "final_style01"


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
ZL = "1040x585+130+100"
ZR = "1040x585+502+100"
XC = "920x518+376+120"
C = "1180x664+246+65"
ZT = "1040x585+316+55"


SERIES = (
    Series("gombe_arrival_with_mother_master.png", 1, "arrival", (FULL, WL, WR, ML, MR, L, R, CL, CR, XC, C)),
    Series("field_camp_local_team_master.png", 12, "camp_team", (FULL, ML, MR, C)),
    Series("young_woman_leads_fieldwork_master.png", 16, "fieldwork", (FULL, WL, WR, ML, MR, L, R, CL, CR, ZL, ZR, C)),
    Series("leakey_museum_mentorship_master.png", 28, "leakey", (FULL, WL, WR, ML, MR, L, R, CL, CR, C)),
    Series("distant_hillside_observation_master.png", 38, "distant_observation", (FULL, WL, WR, ML, MR)),
    Series("months_of_patient_notes_master.png", 43, "patient_notes", (FULL, L, R)),
    Series("gradual_habituation_master.png", 46, "habituation", (FULL, ML, MR, C)),
    Series("chimp_daily_life_master.png", 50, "daily_life", (FULL, ML, MR, C)),
    Series("termite_mound_selection_master.png", 54, "termite_selection", (FULL, L, C)),
    Series("chimp_toolmaking_close_master.png", 57, "toolmaking", (FULL, L, R)),
    Series("science_reconsiders_boundary_master.png", 60, "science_boundary", (FULL, WL, WR, ML, MR, L, R, XC, C)),
    Series("chimp_family_emotions_master.png", 69, "family_emotions", (FULL, ML, MR, C)),
    Series("chimp_conflict_observed_master.png", 73, "conflict", (FULL, ML, MR)),
    Series("tanzanian_longterm_research_master.png", 76, "longterm_research", (FULL, WL, WR, ML, MR, L, R)),
    Series("older_jane_conservation_master.png", 83, "conservation", (FULL, WL, WR, ML, MR, L, R, C)),
    Series("roots_and_shoots_1991_master.png", 91, "roots_shoots", (FULL, WL, WR, ML, MR, L, R, XC, C)),
    Series("modern_youth_local_action_master.png", 100, "youth_action", (FULL, ML, MR)),
    Series("legacy_hope_in_action_master.png", 103, "legacy", (FULL, WL, WR, ML, MR, L, R, CL, CR, ZL, ZR, XC, C, ZT)),
)

TINTS = ("#233a55", "#4f6962", "#74523b")


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
    if variant >= 10:
        cycle = variant // 10
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
    if len(actual) != 116 or actual != expected:
        raise RuntimeError(f"H063 scene mismatch: actual={len(actual)} expected=116")
    for path in actual:
        size = subprocess.run(
            ["magick", "identify", "-format", "%wx%h", str(path)],
            check=True, capture_output=True, text=True,
        ).stdout
        if size != "1672x941":
            raise RuntimeError(f"unexpected size {size}: {path}")
    print("H063 final_style01 files verified: 116")


if __name__ == "__main__":
    main()
