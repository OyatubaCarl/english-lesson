#!/usr/bin/env python3
"""Create H058 dense Style01 crops from the selected master images."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "H058" / "scenes" / "character_refs"
OUT = ROOT / "H058" / "scenes" / "final_style01"


SERIES = [
    ("court_rule_of_law_master.png", 1, 13, "court"),
    ("incident_investigation_master.png", 14, 4, "investigation"),
    ("lawful_arrest_master.png", 18, 3, "arrest"),
    ("prosecution_review_master.png", 21, 7, "prosecution"),
    ("trial_arguments_master.png", 28, 6, "trial"),
    ("witness_testimony_master.png", 34, 5, "witness"),
    ("defendant_attorney_master.png", 39, 6, "defense"),
    ("judge_jury_master.png", 45, 12, "judge_jury"),
    ("presumption_innocence_master.png", 57, 11, "presumption"),
    ("not_guilty_release_master.png", 68, 4, "not_guilty"),
    ("guilty_sentencing_master.png", 72, 5, "sentencing"),
    ("punishment_alternatives_master.png", 77, 5, "alternatives"),
    ("appeal_higher_court_master.png", 82, 7, "appeal"),
    ("justice_refined_master.png", 89, 19, "justice_future"),
]

# Wide, left, center and right crops create deliberate pushes and holds.  Every
# crop remains 16:9 and is expanded back to the common 1672x941 frame.
CROPS: list[str | None] = [
    None,
    "1200x675+0+70",
    "1200x675+472+70",
    "1050x591+310+55",
    "900x506+0+145",
    "900x506+772+145",
    "860x484+406+95",
    None,
]
TINTS = ["#334766", "#6b4b30", "#3c4f63"]


def render(source: Path, target: Path, index: int) -> None:
    if target.is_file() and target.stat().st_size:
        return
    crop = CROPS[(index - 1) % len(CROPS)]
    cycle = (index - 1) // len(CROPS)
    if crop is None and cycle == 0:
        shutil.copyfile(source, target)
        return

    command = ["magick", str(source)]
    if crop:
        command += [
            "-crop", crop, "+repage",
            "-resize", "1672x941^",
            "-gravity", "center",
            "-extent", "1672x941",
        ]
    else:
        command += [
            "-resize", "1672x941^",
            "-gravity", "center",
            "-extent", "1672x941",
        ]
    if cycle:
        command += [
            "-modulate", f"{101 + cycle},{101 + (cycle % 2)},100",
            "-fill", TINTS[(cycle - 1) % len(TINTS)],
            "-colorize", f"{min(2 + cycle, 6)}%",
        ]
    command.append(str(target))
    subprocess.run(command, check=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    expected: list[Path] = []
    for master, start, count, prefix in SERIES:
        source = REF / master
        if not source.is_file():
            raise FileNotFoundError(source)
        for offset in range(count):
            number = start + offset
            target = OUT / f"{number:03d}_{prefix}_{offset + 1:02d}.png"
            render(source, target, offset + 1)
            expected.append(target)

    actual = sorted(OUT.glob("[0-9][0-9][0-9]_*.png"))
    if len(actual) != 107 or actual != expected:
        raise RuntimeError(f"H058 scene mismatch: actual={len(actual)} expected=107")
    for path in actual:
        identify = subprocess.run(
            ["magick", "identify", "-format", "%wx%h", str(path)],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        if identify != "1672x941":
            raise RuntimeError(f"unexpected size {identify}: {path}")
    print("H058 final_style01 files verified: 107")


if __name__ == "__main__":
    main()
