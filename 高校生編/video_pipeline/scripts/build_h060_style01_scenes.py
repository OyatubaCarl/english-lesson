#!/usr/bin/env python3
"""Create H060 dense Style01 crops from the fifteen accepted master images."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "H060" / "scenes" / "character_refs"
OUT = ROOT / "H060" / "scenes" / "final_style01"


@dataclass(frozen=True)
class Series:
    master: str
    start: int
    prefix: str
    crops: tuple[str | None, ...]


# All crops keep the 16:9 master ratio.  Their order follows the narrated
# point of attention rather than applying one generic zoom cycle to every image.
SERIES = (
    Series("hiroshima_morning_master.png", 1, "hiroshima_morning", (
        None, "1320x743+0+36", "1320x743+352+36",
        "1040x585+500+80", "1180x664+246+42",
    )),
    Series("hiroshima_rescue_master.png", 6, "hiroshima_rescue", (
        None, "1320x743+0+56", "1180x664+246+42", "1040x585+520+78",
    )),
    Series("nagasaki_aid_master.png", 10, "nagasaki_aid", (
        None, "1320x743+352+40", "1180x664+246+58", "920x518+612+90",
    )),
    Series("months_care_memory_master.png", 14, "months_care", (
        None, "1320x743+0+55", "1040x585+250+75", "920x518+375+92",
        "1040x585+632+78", "1180x664+492+45", "1320x743+176+50",
    )),
    Series("nuclear_weapons_age_master.png", 21, "nuclear_age", (
        None, "1040x585+0+90", "1040x585+632+88", "1180x664+246+50",
    )),
    Series("cold_war_arms_race_master.png", 25, "cold_war", (
        None, "1040x585+0+105", "920x518+376+105", "1040x585+632+105",
        "1180x664+246+48", "1320x743+176+40",
    )),
    Series("worldwide_threat_peace_movement_master.png", 31, "world_threat", (
        None, "1040x585+0+92", "920x518+80+80", "1040x585+632+80",
        "1180x664+440+45",
    )),
    Series("npt_signature_1968_master.png", 36, "npt_signature", (
        None, "1040x585+0+90", "920x518+376+96", "1040x585+632+90",
        "1320x743+176+40",
    )),
    Series("npt_three_part_work_master.png", 41, "npt_three_pillars", (
        None, "1040x585+0+88", "920x518+376+92", "1040x585+632+88",
        "1320x743+176+40",
    )),
    Series("post_cold_war_conflict_master.png", 46, "post_cold_war", (
        None, "1320x743+176+0", "1040x585+0+180", "1040x585+632+180",
        "920x518+376+0", "1180x664+0+150", "1180x664+492+150",
        "1040x585+316+165", "1320x743+0+80", "1320x743+352+80",
    )),
    Series("refugees_victims_master.png", 56, "refugees", (
        None, "1180x664+0+120", "1040x585+160+165", "920x518+330+175",
        "1040x585+632+155", "1320x743+352+65", "1320x743+176+75",
    )),
    Series("un_negotiation_mediation_master.png", 63, "un_mediation", (
        None, "1180x664+0+105", "1040x585+300+145", "920x518+376+165",
        "1040x585+632+145", "1320x743+176+35", "1180x664+246+80",
        "1040x585+316+0", "1320x743+176+90",
    )),
    Series("security_council_limits_master.png", 72, "council_limits", (
        None, "1320x743+176+25", "920x518+620+95", "1040x585+300+120",
        "1180x664+0+70", "1180x664+492+70", "1040x585+316+0",
    )),
    Series("peace_reconciliation_master.png", 79, "reconciliation", (
        None, "1180x664+0+125", "1040x585+0+170", "920x518+80+190",
        "1040x585+316+165", "920x518+430+150", "1040x585+632+140",
        "920x518+700+160", "1180x664+492+90", "1320x743+352+55",
        "1320x743+0+55", "1180x664+246+120", "1040x585+316+100",
        "1320x743+176+55",
    )),
    Series("memory_future_master.png", 93, "memory_future", (
        None, "1320x743+0+30", "1320x743+352+30", "1040x585+180+115",
        "920x518+250+170", "920x518+500+155", "1040x585+632+95",
        "1180x664+0+35", "1180x664+492+35", "920x518+376+0",
        "1040x585+316+70", "1320x743+176+20", "1180x664+246+70",
        "1040x585+316+130",
    )),
)

TINTS = ("#233856", "#674a32", "#3a5061")


def render(source: Path, target: Path, crop: str | None, variant: int) -> None:
    if target.is_file() and target.stat().st_size:
        return
    if crop is None:
        shutil.copyfile(source, target)
        return

    command = [
        "magick", str(source),
        "-crop", crop, "+repage",
        "-resize", "1672x941^",
        "-gravity", "center",
        "-extent", "1672x941",
    ]
    # Extremely light grading prevents adjacent crops from looking like a frozen
    # repeated still, while retaining the accepted master palette.
    if variant >= 8:
        cycle = variant // 8
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
    if len(actual) != 106 or actual != expected:
        raise RuntimeError(f"H060 scene mismatch: actual={len(actual)} expected=106")
    for path in actual:
        size = subprocess.run(
            ["magick", "identify", "-format", "%wx%h", str(path)],
            check=True, capture_output=True, text=True,
        ).stdout
        if size != "1672x941":
            raise RuntimeError(f"unexpected size {size}: {path}")
    print("H060 final_style01 files verified: 106")


if __name__ == "__main__":
    main()
