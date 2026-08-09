#!/usr/bin/env python3
"""Create H059 dense Style01 crops from the fourteen selected master images."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "H059" / "scenes" / "character_refs"
OUT = ROOT / "H059" / "scenes" / "final_style01"


SERIES = [
    ("modern_psychology_intro_master.png", 1, 11, "psychology_intro"),
    ("wundt_leipzig_lab_master.png", 12, 9, "wundt_lab"),
    ("measurement_academic_beginning_master.png", 21, 5, "measurement"),
    ("pavlov_natural_salivation_master.png", 26, 7, "pavlov_food"),
    ("pavlov_conditioning_master.png", 33, 13, "conditioning"),
    ("freud_unconscious_theory_master.png", 46, 8, "freud_theory"),
    ("freud_debate_spread_master.png", 54, 9, "freud_spread"),
    ("milgram_setup_master.png", 63, 5, "milgram_setup"),
    ("milgram_authority_distress_master.png", 68, 5, "milgram_distress"),
    ("milgram_debrief_master.png", 73, 4, "debrief"),
    ("decision_biases_master.png", 77, 7, "decision_bias"),
    ("student_rational_emotion_master.png", 84, 6, "student_decision"),
    ("collaborative_therapy_master.png", 90, 9, "therapy"),
    ("mind_science_finale_master.png", 99, 12, "mind_science"),
]

# Each eight-step cycle moves from establishing view to measured left/right and
# centered detail crops. The renderer then performs only one stable push/pull.
CROPS: list[str | None] = [
    None,
    "1320x743+0+55",
    "1320x743+352+55",
    "1180x664+246+45",
    "1040x585+0+100",
    "1040x585+632+100",
    "920x518+376+78",
    None,
]
TINTS = ["#273c5b", "#6a4b31", "#3d5264"]


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
    if len(actual) != 110 or actual != expected:
        raise RuntimeError(f"H059 scene mismatch: actual={len(actual)} expected=110")
    for path in actual:
        identify = subprocess.run(
            ["magick", "identify", "-format", "%wx%h", str(path)],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        if identify != "1672x941":
            raise RuntimeError(f"unexpected size {identify}: {path}")
    print("H059 final_style01 files verified: 110")


if __name__ == "__main__":
    main()
