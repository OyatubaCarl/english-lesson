#!/usr/bin/env python3
"""Create H064 dense Style01 crops from the seventeen accepted master images."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "H064" / "scenes" / "character_refs"
OUT = ROOT / "H064" / "scenes" / "final_style01"


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


SERIES = (
    Series("malaga_birth_1881_master.png", 1, "malaga_birth", (FULL, WL, WR, ML, MR, L, R, C)),
    Series("prolific_multimedia_studio_master.png", 9, "multimedia", (FULL, WL, WR, ML, MR, L, R, XC, C)),
    Series("blue_period_between_cities_master.png", 18, "blue_period", (FULL, WL, WR, ML, MR, C)),
    Series("rose_period_transition_master.png", 24, "rose_period", (FULL, C)),
    Series("styles_and_media_change_master.png", 26, "media_change", (FULL, C)),
    Series("demoiselles_preparatory_studies_master.png", 28, "preparatory", (FULL, ML, MR, C)),
    Series("geometric_figure_experiment_master.png", 32, "geometry", (FULL, WL, WR, L, R, C)),
    Series("picasso_braque_collaboration_master.png", 38, "braque_collab", (FULL, WL, WR, ML, MR, L, R)),
    Series("single_perspective_tradition_master.png", 45, "single_perspective", (FULL, WL, WR, ML, MR, C)),
    Series("multiple_viewpoints_canvas_master.png", 51, "multiple_views", (FULL, WL, WR, ML, MR, C)),
    Series("guernica_aftermath_master.png", 57, "guernica_aftermath", (FULL, WL, WR, ML, MR, C)),
    Series("picasso_receives_news_master.png", 63, "receives_news", (FULL, C)),
    Series("guernica_creation_documented_master.png", 65, "creation_documented", (FULL, WL, WR, ML, MR)),
    Series("spanish_pavilion_viewers_master.png", 70, "pavilion_viewers", (FULL, WL, WR, ML, MR)),
    Series("later_ceramics_prints_sculpture_master.png", 75, "later_media", (FULL, ML, MR)),
    Series("older_playful_drawing_master.png", 78, "older_drawing", (FULL, WL, WR, ML, MR, C)),
    Series("contemporary_critical_legacy_master.png", 84, "critical_legacy", (FULL, WL, WR, ML, MR, L, R, CL, CR, C)),
)

TINTS = ("#253954", "#665f6d", "#76513e")


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
    if len(actual) != 93 or actual != expected:
        raise RuntimeError(f"H064 scene mismatch: actual={len(actual)} expected=93")
    for path in actual:
        size = subprocess.run(
            ["magick", "identify", "-format", "%wx%h", str(path)],
            check=True, capture_output=True, text=True,
        ).stdout
        if size != "1672x941":
            raise RuntimeError(f"unexpected size {size}: {path}")
    print("H064 final_style01 files verified: 93")


if __name__ == "__main__":
    main()
