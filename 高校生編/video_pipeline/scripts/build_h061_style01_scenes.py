#!/usr/bin/env python3
"""Create H061 dense Style01 crops from the seventeen accepted master images."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "H061" / "scenes" / "character_refs"
OUT = ROOT / "H061" / "scenes" / "final_style01"


@dataclass(frozen=True)
class Series:
    master: str
    start: int
    prefix: str
    crops: tuple[str | None, ...]


SERIES = (
    Series("brno_abbey_1856_master.png", 1, "brno_1856", (
        None, "1320x743+0+32", "1320x743+352+32", "1180x664+0+48",
        "1180x664+492+48", "1040x585+180+92", "1040x585+520+92",
        "920x518+250+130", "920x518+580+130", "1320x743+176+80",
        "1180x664+246+115",
    )),
    Series("mendel_investigator_master.png", 12, "mendel_identity", (
        None, "1320x743+352+40", "1180x664+492+60", "1040x585+550+105",
        "1040x585+0+100", "1320x743+176+55",
    )),
    Series("pea_traits_master.png", 18, "pea_traits", (
        None, "1180x664+0+95", "1040x585+0+145", "920x518+90+160",
        "920x518+376+165", "1040x585+520+140", "920x518+680+155",
        "1320x743+176+70", "1180x664+246+125",
    )),
    Series("cross_pollination_master.png", 27, "cross_pollination", (
        None, "1040x585+180+120", "1040x585+632+110",
    )),
    Series("nine_years_scale_master.png", 30, "nine_years", (
        None, "1180x664+0+110", "1180x664+492+95", "1320x743+176+50",
    )),
    Series("true_breeding_parents_master.png", 34, "true_breeding", (
        None, "1040x585+0+120", "920x518+376+120", "1040x585+632+120",
        "1320x743+176+60",
    )),
    Series("first_generation_tall_master.png", 39, "first_generation", (
        None, "1180x664+246+95",
    )),
    Series("second_generation_reappearance_master.png", 41, "second_generation", (
        None, "1040x585+0+150", "920x518+80+190", "1040x585+632+145",
        "920x518+650+180", "1320x743+176+85", "1180x664+246+130",
    )),
    Series("ratio_counting_master.png", 48, "ratio_counting", (
        None, "1040x585+0+175", "920x518+300+165", "1040x585+632+160",
        "1320x743+176+105",
    )),
    Series("paired_elements_reasoning_master.png", 53, "paired_elements", (
        None, "1040x585+0+155", "920x518+170+175", "920x518+376+175",
        "920x518+580+175", "1040x585+632+155", "1180x664+246+110",
        "1320x743+176+75", "1040x585+316+185",
    )),
    Series("dominant_recessive_relation_master.png", 62, "dominance_relation", (
        "1320x743+176+90", "1180x664+0+140", "1040x585+140+175",
        "920x518+376+190", "1040x585+632+170", "1180x664+246+135",
    )),
    Series("brno_presentation_1865_master.png", 68, "presentation_1865", (
        None, "1040x585+0+105", "920x518+190+125", "1040x585+632+105",
        "1320x743+176+65",
    )),
    Series("publication_limited_attention_master.png", 73, "publication_1866", (
        None, "1040x585+0+115", "920x518+360+140", "1040x585+632+105",
        "1320x743+176+70",
    )),
    Series("decades_limited_attention_master.png", 78, "decades_unnoticed", (
        None, "1040x585+0+125", "920x518+180+145", "1040x585+632+125",
    )),
    Series("three_researchers_1900_master.png", 82, "researchers_1900", (
        None, "1040x585+0+90", "920x518+0+130", "920x518+376+100",
        "920x518+752+120", "1040x585+632+90", "1320x743+176+55",
        "1180x664+246+105",
    )),
    Series("modern_genetics_foundation_master.png", 90, "modern_genetics", (
        None, "1040x585+0+135", "920x518+80+155", "1040x585+300+145",
        "920x518+420+160", "1040x585+632+140", "1320x743+176+85",
        "1180x664+246+135",
    )),
    Series("quiet_monastery_finale_master.png", 98, "quiet_finale", (
        None, "1320x743+0+45", "1320x743+352+45", "1180x664+0+80",
        "1180x664+492+80", "1040x585+140+115", "1040x585+500+115",
        "920x518+260+145", "920x518+580+145", "1040x585+0+130",
        "1040x585+632+130", "1180x664+246+105", "1320x743+176+70",
        "920x518+376+175", "1040x585+316+155", "1180x664+246+150",
        "1320x743+176+100",
    )),
)

TINTS = ("#223955", "#67472f", "#39515f")


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
    if len(actual) != 114 or actual != expected:
        raise RuntimeError(f"H061 scene mismatch: actual={len(actual)} expected=114")
    for path in actual:
        size = subprocess.run(
            ["magick", "identify", "-format", "%wx%h", str(path)],
            check=True, capture_output=True, text=True,
        ).stdout
        if size != "1672x941":
            raise RuntimeError(f"unexpected size {size}: {path}")
    print("H061 final_style01 files verified: 114")


if __name__ == "__main__":
    main()
