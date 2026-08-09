#!/usr/bin/env python3
"""Create H084 dense Style01 JPEG crops while preserving master PNGs."""
from __future__ import annotations

from bisect import bisect_right
import json
import subprocess
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H084"
REF = LESSON / "scenes/character_refs"
OUT = LESSON / "scenes/final_style01"
VISUAL_BIBLE = LESSON / "planning/visual_bible_style01.json"
DURATION = 151.880167
SCENE_COUNT = 118
UNIT = DURATION / SCENE_COUNT

CROP_SEQUENCES = {
    "C": (None, "1460x821+106+28", "1280x720+196+42"),
    "L": (None, "1460x821+0+28", "1280x720+0+42"),
    "R": (None, "1460x821+212+28", "1280x720+392+42"),
}

ANCHORS = {
    "global_food_system_dawn": "R",
    "regional_farm_cooperative_morning": "L",
    "urban_population_food_market": "R",
    "rural_urban_supply_connection": "L",
    "community_food_access_center": "R",
    "disrupted_supply_and_price": "L",
    "southern_mesopotamia_river_plain": "R",
    "mesopotamian_canal_planning": "L",
    "mesopotamian_earthen_water_gate": "L",
    "mesopotamian_irrigated_barley": "R",
    "farmer_seed_selection_history": "L",
    "crop_yield_measurement_history": "R",
    "modern_plant_breeding_team": "L",
    "green_revolution_rice_research_1960s": "R",
    "high_yield_rice_field_asia": "L",
    "south_asia_wheat_harvest": "R",
    "measured_fertilizer_and_irrigation": "L",
    "african_farming_conditions_varied": "R",
    "pesticide_safe_application": "L",
    "fertilizer_runoff_after_rain": "R",
    "contaminated_stream_monitoring": "L",
    "organic_crop_rotation": "R",
    "compost_soil_biodiversity": "L",
    "gene_crop_lab_assessment": "L",
    "gm_crop_field_trial_monitoring": "R",
    "organic_gm_evidence_comparison": "L",
    "smallholder_choice_roundtable": "R",
    "integrated_diversified_farm": "L",
    "food_waste_kitchen_scale": "R",
    "postharvest_storage_loss": "L",
    "retail_unsold_food": "R",
    "restaurant_kitchen_waste": "L",
    "household_leftovers_planning": "R",
    "food_access_logistics_contradiction": "L",
    "farmer_cooperative_storage": "R",
    "cold_chain_transport": "L",
    "local_market_distribution": "R",
    "safe_surplus_redistribution": "L",
    "waste_reduction_consumer_choice": "R",
    "food_scraps_compost_cycle": "L",
    "climate_resilient_sustainable_farm": "R",
    "farmers_researchers_consumers_future": "L",
    "regional_fields_evening_finale": "R",
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
    if len(rows) != 43:
        raise RuntimeError(f"H084 master count: {len(rows)} != 43")
    OUT.mkdir(parents=True, exist_ok=True)
    if any(OUT.iterdir()):
        raise RuntimeError(f"H084 output directory must be empty before rebuilding: {OUT}")

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
            f"H084 scene mismatch actual={len(actual)} expected={SCENE_COUNT} missing={missing}"
        )
    print(f"H084 final_style01 files verified: {len(actual)}; masters used: {len(usage)}")


if __name__ == "__main__":
    main()
