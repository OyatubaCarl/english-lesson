#!/usr/bin/env python3
"""Create H075 dense Style01 crops from the accepted masters."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "H075/scenes/character_refs"
OUT = ROOT / "H075/scenes/final_style01"

F = None
WL = "1420x799+0+20"
WR = "1420x799+252+20"
MR = "1320x743+352+55"
L = "1180x664+0+90"
R = "1180x664+492+90"
C = "1180x664+246+90"

MASTERS = (
    ("language_atlas_master.png", "language_atlas"),
    ("multilingual_listening_master.png", "multilingual_listening"),
    ("signed_language_master.png", "signed_language"),
    ("worldview_story_master.png", "worldview_story"),
    ("translation_desk_master.png", "translation_desk"),
    ("rebuilding_meaning_master.png", "rebuilding_meaning"),
    ("word_replacement_failure_master.png", "replacement_failure"),
    ("mottainai_repair_master.png", "mottainai"),
    ("itadakimasu_meal_master.png", "itadakimasu"),
    ("otsukaresama_master.png", "otsukaresama"),
    ("japanese_sensitivity_master.png", "japanese_sensitivity"),
    ("serendipity_master.png", "serendipity"),
    ("nostalgia_master.png", "nostalgia"),
    ("privacy_master.png", "privacy"),
    ("cultural_context_master.png", "cultural_context"),
    ("poetry_translation_master.png", "poetry_translation"),
    ("poetry_rhythm_master.png", "poetry_rhythm"),
    ("poetry_silence_master.png", "poetry_silence"),
    ("translator_long_night_master.png", "translator_long_night"),
    ("translator_consultation_master.png", "translator_consultation"),
    ("machine_translation_progress_master.png", "machine_progress"),
    ("ai_translation_master.png", "ai_translation"),
    ("daily_communication_master.png", "daily_communication"),
    ("ambiguity_review_master.png", "ambiguity_review"),
    ("human_literary_judgment_master.png", "human_literary"),
    ("translation_bridge_master.png", "translation_bridge"),
    ("translated_performance_master.png", "translated_performance"),
    ("closer_hearts_final_master.png", "closer_hearts"),
)


def render(src: Path, dst: Path, crop: str | None) -> None:
    if dst.is_file() and dst.stat().st_size:
        return
    if crop is None:
        shutil.copyfile(src, dst)
        return
    subprocess.run(
        ["magick", str(src), "-crop", crop, "+repage", "-resize", "1672x941^",
         "-gravity", "center", "-extent", "1672x941", str(dst)],
        check=True,
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    expected: list[Path] = []
    number = 1
    for master_index, (master, prefix) in enumerate(MASTERS):
        src = REF / master
        if not src.is_file():
            raise FileNotFoundError(src)
        if master_index == 0:
            crops = (F, WL, MR, R, C)
        elif master_index % 3 == 0:
            crops = (F, WR, R, C)
        elif master_index % 3 == 1:
            crops = (F, WL, MR, C)
        else:
            crops = (F, WL, L, C)
        for crop_index, crop in enumerate(crops, 1):
            dst = OUT / f"{number:03d}_{prefix}_{crop_index:02d}.png"
            render(src, dst, crop)
            expected.append(dst)
            number += 1
    actual = sorted(OUT.glob("[0-9][0-9][0-9]_*.png"))
    if actual != expected or len(actual) != 113:
        raise RuntimeError(f"H075 scene mismatch actual={len(actual)} expected=113")
    print("H075 final_style01 files verified: 113")


if __name__ == "__main__":
    main()
