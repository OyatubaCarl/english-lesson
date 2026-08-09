#!/usr/bin/env python3
"""Create H082 dense Style01 JPEG crops while preserving master PNGs."""
from __future__ import annotations

from bisect import bisect_right
import json
import subprocess
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H082"
REF = LESSON / "scenes/character_refs"
OUT = LESSON / "scenes/final_style01"
VISUAL_BIBLE = LESSON / "planning/visual_bible_style01.json"
DURATION = 83.720167
SCENE_COUNT = 65
UNIT = DURATION / SCENE_COUNT

CROP_SEQUENCES = {
    "C": (None, "1460x821+106+28", "1280x720+196+42"),
    "L": (None, "1460x821+0+28", "1280x720+0+42"),
    "R": (None, "1460x821+212+28", "1280x720+392+42"),
}

ANCHORS = {
    "regional_city_small_company_dawn": "R",
    "rented_workshop_exterior_1990s": "L",
    "capable_founder_engineer_closeup": "L",
    "accounts_figures_closeup": "L",
    "small_revenue_sparse_orders": "R",
    "investor_pitch_with_prototype": "R",
    "funding_agreement_handshake": "L",
    "prototype_validation_team": "L",
    "competitive_market_trade_fair": "R",
    "overseas_clients_technical_meeting": "R",
    "contracts_careful_review": "L",
    "expansion_medium_factory_floor": "R",
    "chairman_backstage_present": "L",
    "annual_conference_wide": "R",
    "employees_listening_closeup": "L",
    "sincerity_not_strategy_address": "L",
    "sincerity_quality_inspection": "L",
    "commercial_success_present_company": "R",
    "community_electronics_workshop": "R",
    "local_repair_support": "L",
    "transparent_management_roundtable": "L",
    "fair_promotion_evidence_review": "R",
    "promoted_employee_new_responsibility": "L",
    "original_workbench_present_day": "L",
    "success_beyond_numbers_open_day": "R",
    "founder_staff_clients_community": "L",
    "regional_company_evening_finale": "R",
}


def snap_before(time: float) -> float:
    return int(time / UNIT) * UNIT


def masters() -> tuple[tuple[float, str, str, str], ...]:
    bible = json.loads(VISUAL_BIBLE.read_text(encoding="utf-8"))
    rows = []
    for item in bible["masters"]:
        filename = str(item["file"])
        prefix = filename.removesuffix("_master.png")
        rows.append((snap_before(float(item["time"])), filename, prefix, ANCHORS.get(prefix, "C")))
    return tuple(rows)


def render(source: Path, destination: Path, crop: str | None) -> None:
    command = ["magick", str(source)]
    if crop is not None:
        command.extend([
            "-crop", crop, "+repage", "-resize", "1672x941^",
            "-gravity", "center", "-extent", "1672x941",
        ])
    command.extend(["-sampling-factor", "4:2:0", "-quality", "92", str(destination)])
    subprocess.run(command, check=True)


def main() -> None:
    rows = masters()
    if len(rows) != 30:
        raise RuntimeError(f"H082 master count: {len(rows)} != 30")
    OUT.mkdir(parents=True, exist_ok=True)
    if any(OUT.iterdir()):
        raise RuntimeError(f"H082 output directory must be empty before rebuilding: {OUT}")

    for _, filename, _, _ in rows:
        if not (REF / filename).is_file():
            raise FileNotFoundError(REF / filename)

    starts = [item[0] for item in rows]
    usage: Counter[str] = Counter()
    expected: list[Path] = []
    for ordinal in range(SCENE_COUNT):
        time = UNIT * ordinal
        master_index = bisect_right(starts, time + 1e-9) - 1
        _, filename, prefix, anchor = rows[master_index]
        usage[prefix] += 1
        crop_number = usage[prefix]
        sequence = CROP_SEQUENCES[anchor]
        crop = sequence[min(crop_number - 1, len(sequence) - 1)]
        destination = OUT / f"{ordinal + 1:03d}_{prefix}_{crop_number:02d}.jpg"
        render(REF / filename, destination, crop)
        expected.append(destination)

    actual = sorted(OUT.glob("[0-9][0-9][0-9]_*.jpg"))
    missing = [prefix for _, _, prefix, _ in rows if usage[prefix] == 0]
    if actual != expected or len(actual) != SCENE_COUNT or missing:
        raise RuntimeError(
            f"H082 scene mismatch actual={len(actual)} expected={SCENE_COUNT} missing={missing}"
        )
    print(f"H082 final_style01 files verified: {len(actual)}; masters used: {len(usage)}")


if __name__ == "__main__":
    main()
