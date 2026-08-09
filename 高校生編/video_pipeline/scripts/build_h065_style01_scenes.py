#!/usr/bin/env python3
"""Create H065 dense Style01 crops from the seventeen accepted master images."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "H065" / "scenes" / "character_refs"
OUT = ROOT / "H065" / "scenes" / "final_style01"


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
    Series("mid1990s_household_connection_master.png", 1, "mid1990s", (FULL, WL, WR, ML, MR, L, R, C)),
    Series("thirty_year_transformation_master.png", 9, "transformation", (FULL, WL, WR, ML, MR, L, R, C)),
    Series("communication_change_master.png", 17, "communication", (FULL, WL, WR, ML, MR, C)),
    Series("international_video_call_master.png", 23, "video_call", (FULL, WL, WR, ML, MR, C)),
    Series("pandemic_remote_work_master.png", 29, "pandemic_remote", (FULL, ML, MR, C)),
    Series("hybrid_work_tradeoffs_master.png", 33, "hybrid_work", (FULL, WL, WR, ML, MR, C)),
    Series("frontline_and_digital_divide_master.png", 39, "work_divide", (FULL, C)),
    Series("privacy_data_choices_master.png", 41, "privacy", (FULL, ML, C)),
    Series("security_everyday_defense_master.png", 44, "security", (FULL, C)),
    Series("misinformation_spread_master.png", 46, "misinformation", (FULL, C)),
    Series("source_verification_master.png", 48, "verification", (FULL, ML, MR, C)),
    Series("algorithm_design_master.png", 52, "algorithm", (FULL, WL, WR, ML, C)),
    Series("late_night_attention_master.png", 57, "attention", (FULL, WL, WR, ML, MR, C)),
    Series("problematic_use_support_master.png", 63, "support", (FULL, ML, MR, C)),
    Series("internet_physical_system_master.png", 67, "physical_system", (FULL, ML, C)),
    Series("shared_responsibility_roundtable_master.png", 70, "shared_responsibility", (FULL, WL, WR, ML, MR, C)),
    Series("balanced_digital_future_master.png", 76, "balanced_future", (FULL, WL, WR, ML, MR, L, R, CL, CR, XC, C)),
)

TINTS = ("#243b57", "#655a63", "#715641")


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
    if len(actual) != 86 or actual != expected:
        raise RuntimeError(f"H065 scene mismatch: actual={len(actual)} expected=86")
    for path in actual:
        size = subprocess.run(
            ["magick", "identify", "-format", "%wx%h", str(path)],
            check=True, capture_output=True, text=True,
        ).stdout
        if size != "1672x941":
            raise RuntimeError(f"unexpected size {size}: {path}")
    print("H065 final_style01 files verified: 86")


if __name__ == "__main__":
    main()
