#!/usr/bin/env python3
"""Build the H082 65-cut video plan and verify lyric-to-image alignment."""
from __future__ import annotations

from bisect import bisect_right
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H082"
PLAN = LESSON / "planning/video_plan.json"
MIXED = LESSON / "planning/mixed_ruby.json"
TIMING = LESSON / "planning/word_timing_tacobeat.json"
SCENE_COUNT = 65
NAME_RE = re.compile(r"^\d{3}_(.+)_\d{2}\.jpg$")
EXPECTED_AT = {
    1.6: "regional_city_small_company_dawn",
    3.0: "rented_workshop_exterior_1990s",
    5.5: "founding_team_four_1990s",
    8.0: "capable_founder_engineer_closeup",
    10.6: "commitment_team_prototype",
    12.5: "early_company_debt",
    15.3: "accounts_figures_closeup",
    18.1: "small_revenue_sparse_orders",
    20.7: "investor_pitch_with_prototype",
    23.4: "funding_agreement_handshake",
    26.0: "prototype_validation_team",
    28.3: "competitive_market_trade_fair",
    30.8: "overseas_clients_technical_meeting",
    33.3: "contracts_careful_review",
    35.6: "expansion_medium_factory_floor",
    37.3: "chairman_backstage_present",
    39.6: "annual_conference_wide",
    42.1: "employees_listening_closeup",
    44.0: "sincerity_not_strategy_address",
    46.8: "sincerity_quality_inspection",
    49.2: "commercial_success_present_company",
    52.4: "community_electronics_workshop",
    55.5: "local_repair_support",
    58.9: "transparent_management_roundtable",
    61.6: "fair_promotion_evidence_review",
    64.3: "promoted_employee_new_responsibility",
    67.2: "original_workbench_present_day",
    70.8: "success_beyond_numbers_open_day",
    75.2: "founder_staff_clients_community",
    79.4: "regional_company_evening_finale",
}


def purpose(image: Path) -> str:
    match = NAME_RE.match(image.name)
    if not match:
        raise RuntimeError(f"unexpected H082 scene filename: {image.name}")
    return match.group(1)


def main() -> None:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    mixed = json.loads(MIXED.read_text(encoding="utf-8"))
    timing = json.loads(TIMING.read_text(encoding="utf-8"))
    duration = float(plan["duration"])
    if abs(duration - 83.720167) > 0.02:
        raise RuntimeError(f"unexpected H082 adopted duration: {duration}")
    if timing.get("exact_word_match") is not True or int(timing["word_count"]) != 143:
        raise RuntimeError("H082 TacoBeat timing is not exact")

    unit = duration / SCENE_COUNT
    images = sorted((LESSON / "scenes/final_style01").glob("[0-9][0-9][0-9]_*.jpg"))
    if len(images) != SCENE_COUNT:
        raise RuntimeError(f"H082 scene count: {len(images)} != {SCENE_COUNT}")
    scenes = [
        {
            "start": round(unit * ordinal, 3),
            "image": str(image.relative_to(LESSON)),
            "purpose": purpose(image),
        }
        for ordinal, image in enumerate(images)
    ]
    gaps = [float(b["start"]) - float(a["start"]) for a, b in zip(scenes, scenes[1:])]
    gaps.append(duration - float(scenes[-1]["start"]))
    if min(gaps) < 1.285 or max(gaps) > 1.291:
        raise RuntimeError((len(scenes), min(gaps), max(gaps)))

    scene_starts = [float(scene["start"]) for scene in scenes]
    for time, expected in EXPECTED_AT.items():
        scene = scenes[bisect_right(scene_starts, time) - 1]
        if scene["purpose"] != expected:
            raise RuntimeError(f"H082 alignment at {time:.2f}s: {scene['purpose']} != {expected}")

    plan["title_en"] = "The Story of a Company"
    plan["scenes"] = scenes
    plan["captions"] = [
        {
            "start": float(timed["start"]),
            "end": float(timed["end"]),
            "en": line["english"],
            "ja": line["mixed"],
        }
        for line, timed in zip(mixed["lines"], timing["lines"])
    ]
    plan["qa_status"] = "READY_TO_RENDER_STYLE01_FICTIONAL_COMPANY_CONTINUITY_REVIEWED"
    plan["output_name"] = "h082_adopted_song_cinematic_v1.mp4"
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"H082 video plan: {len(scenes)} scenes, min {min(gaps):.3f}s "
        f"max {max(gaps):.3f}s; lyric checkpoints PASS"
    )


if __name__ == "__main__":
    main()
