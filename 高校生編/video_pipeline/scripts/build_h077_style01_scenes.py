#!/usr/bin/env python3
"""Create H077 dense Style01 crops from accepted masters."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "H077/scenes/character_refs"
OUT = ROOT / "H077/scenes/final_style01"

F = None
WL = "1420x799+0+20"
WR = "1420x799+252+20"
MR = "1320x743+352+55"
L = "1180x664+0+90"
R = "1180x664+492+90"
C = "1180x664+246+90"

MASTERS = (
    ("morning_information_flood_master.png", "morning_information"),
    ("newspaper_report_master.png", "newspaper_report"),
    ("television_report_master.png", "television_report"),
    ("online_article_master.png", "online_article"),
    ("social_posts_master.png", "social_posts"),
    ("accuracy_question_master.png", "accuracy_question"),
    ("advertisement_production_master.png", "advertisement_production"),
    ("purchase_persuasion_master.png", "purchase_persuasion"),
    ("propaganda_archive_master.png", "propaganda_archive"),
    ("public_publishing_master.png", "public_publishing"),
    ("rumor_forwarding_master.png", "rumor_forwarding"),
    ("misleading_crop_master.png", "misleading_crop"),
    ("sensational_headline_master.png", "sensational_headline"),
    ("belief_reflection_master.png", "belief_reflection"),
    ("source_trace_master.png", "source_trace"),
    ("publisher_process_master.png", "publisher_process"),
    ("evidence_chain_master.png", "evidence_chain"),
    ("statistics_method_master.png", "statistics_method"),
    ("sampling_context_master.png", "sampling_context"),
    ("multi_source_compare_master.png", "multi_source_compare"),
    ("perspective_witnesses_master.png", "perspective_witnesses"),
    ("biased_conclusion_master.png", "biased_conclusion"),
    ("critical_toolkit_master.png", "critical_toolkit"),
    ("lateral_reading_master.png", "lateral_reading"),
    ("correction_editorial_master.png", "correction_editorial"),
    ("media_literacy_workshop_master.png", "media_literacy_workshop"),
    ("responsible_sharing_finale_master.png", "responsible_sharing_finale"),
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
            crops = (F, WL, C)
        elif master_index == 1:
            crops = (F, WR, C)
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
    if actual != expected or len(actual) != 106:
        raise RuntimeError(f"H077 scene mismatch actual={len(actual)} expected=106")
    print("H077 final_style01 files verified: 106")


if __name__ == "__main__":
    main()
