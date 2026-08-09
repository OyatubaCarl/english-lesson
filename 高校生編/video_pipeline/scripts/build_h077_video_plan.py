#!/usr/bin/env python3
"""Build H077 dense Style01 video plan with uniform 1.300-second cuts."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H077"
PLAN = LESSON / "planning/video_plan.json"
PREFIXES = (
    "morning_information", "newspaper_report", "television_report", "online_article",
    "social_posts", "accuracy_question", "advertisement_production", "purchase_persuasion",
    "propaganda_archive", "public_publishing", "rumor_forwarding", "misleading_crop",
    "sensational_headline", "belief_reflection", "source_trace", "publisher_process",
    "evidence_chain", "statistics_method", "sampling_context", "multi_source_compare",
    "perspective_witnesses", "biased_conclusion", "critical_toolkit", "lateral_reading",
    "correction_editorial", "media_literacy_workshop", "responsible_sharing_finale",
)


def main() -> None:
    plan = json.loads(PLAN.read_text())
    duration = float(plan["duration"])
    unit = duration / 106
    scenes: list[dict] = []
    ordinal = 0
    for group_index, prefix in enumerate(PREFIXES):
        count = 3 if group_index < 2 else 4
        images = sorted((LESSON / "scenes/final_style01").glob(f"*_{prefix}_*.png"))
        if len(images) != count:
            raise RuntimeError(f"{prefix}: {len(images)} != {count}")
        for image in images:
            scenes.append({
                "start": round(unit * ordinal, 3),
                "image": str(image.relative_to(LESSON)),
                "purpose": prefix,
            })
            ordinal += 1
    gaps = [float(b["start"]) - float(a["start"]) for a, b in zip(scenes, scenes[1:])]
    gaps.append(duration - float(scenes[-1]["start"]))
    if len(scenes) != 106 or min(gaps) < 1.299 or max(gaps) > 1.9:
        raise RuntimeError((len(scenes), min(gaps), max(gaps)))
    plan["scenes"] = scenes
    plan["qa_status"] = "READY_TO_RENDER_STYLE01_MEDIA_LITERACY_REVIEWED"
    plan["output_name"] = "h077_adopted_song_cinematic_v1.mp4"
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n")
    print(f"H077 video plan: {len(scenes)} scenes, min {min(gaps):.3f}s max {max(gaps):.3f}s")


if __name__ == "__main__":
    main()
