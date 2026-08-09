#!/usr/bin/env python3
"""Create H062 dense Style01 crops from the sixteen accepted master images."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "H062" / "scenes" / "character_refs"
OUT = ROOT / "H062" / "scenes" / "final_style01"


@dataclass(frozen=True)
class Series:
    master: str
    start: int
    prefix: str
    crops: tuple[str | None, ...]


SERIES = (
    Series("watershed_to_ocean_master.png", 1, "watershed", (
        None, "1320x743+0+40", "1320x743+352+40", "1180x664+0+85",
        "1180x664+492+85", "1040x585+160+125", "1180x664+246+120",
    )),
    Series("river_mouth_sampling_master.png", 8, "river_sampling", (
        None, "1180x664+0+90", "1040x585+100+125", "1040x585+632+120",
        "1320x743+176+65",
    )),
    Series("truckload_scale_master.png", 13, "truck_scale", (
        None, "1180x664+246+95",
    )),
    Series("north_pacific_sampling_master.png", 15, "north_pacific", (
        None, "1320x743+0+40", "1320x743+352+45", "1180x664+0+80",
        "1180x664+492+80", "1040x585+160+115", "1040x585+632+110",
        "1180x664+246+115",
    )),
    Series("currents_disperse_debris_master.png", 23, "currents", (
        None, "1180x664+0+100", "1180x664+492+95", "1320x743+176+65",
    )),
    Series("weathering_microplastic_master.png", 27, "weathering", (
        None, "1320x743+0+40", "1320x743+352+40", "1180x664+0+75",
        "1180x664+492+80", "1040x585+100+110", "1040x585+532+115",
        "920x518+376+135", "1180x664+246+110",
    )),
    Series("plankton_foodweb_master.png", 36, "foodweb", (
        None, "1180x664+0+85", "1040x585+0+110", "1040x585+316+115",
        "1040x585+632+105", "1320x743+176+55", "1180x664+246+105",
    )),
    Series("seafood_research_uncertainty_master.png", 43, "seafood_research", (
        None, "1180x664+246+90",
    )),
    Series("seabird_rescue_master.png", 45, "seabird_rescue", (
        None, "1180x664+0+90", "1040x585+80+115", "1040x585+552+110",
        "1320x743+176+65",
    )),
    Series("coral_multiple_threats_master.png", 50, "coral_threats", (
        None, "1320x743+0+45", "1320x743+352+45", "1180x664+0+85",
        "1180x664+492+80", "1040x585+130+115", "1040x585+552+110",
        "1180x664+246+110",
    )),
    Series("government_reduction_policy_master.png", 58, "policy_store", (
        None, "1180x664+0+95", "1040x585+100+120", "1040x585+532+115",
        "920x518+376+130", "1320x743+176+60", "1180x664+246+105",
    )),
    Series("reuse_recycling_industry_master.png", 65, "reuse_industry", (
        None, "1180x664+0+95", "1180x664+492+90", "1320x743+176+65",
    )),
    Series("biodegradable_seawater_test_master.png", 69, "materials_test", (
        None, "1180x664+0+90", "1180x664+492+90", "1320x743+176+65",
    )),
    Series("systems_roundtable_master.png", 73, "systems", (
        None, "1180x664+0+90", "1040x585+120+110", "1040x585+512+110",
        "1320x743+176+60",
    )),
    Series("student_reduce_reuse_recycle_master.png", 78, "daily_choices", (
        None, "1180x664+246+90", "1040x585+460+110",
    )),
    Series("ocean_future_system_master.png", 81, "ocean_future", (
        None, "1320x743+0+40", "1320x743+352+40", "1180x664+0+80",
        "1180x664+492+80", "1040x585+100+115", "1040x585+532+110",
        "920x518+376+130", "1320x743+176+65", "1180x664+246+110",
    )),
)

TINTS = ("#203a59", "#526e74", "#765039")


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
    if len(actual) != 90 or actual != expected:
        raise RuntimeError(f"H062 scene mismatch: actual={len(actual)} expected=90")
    for path in actual:
        size = subprocess.run(
            ["magick", "identify", "-format", "%wx%h", str(path)],
            check=True, capture_output=True, text=True,
        ).stdout
        if size != "1672x941":
            raise RuntimeError(f"unexpected size {size}: {path}")
    print("H062 final_style01 files verified: 90")


if __name__ == "__main__":
    main()
