#!/usr/bin/env python3
"""Create H079 dense Style01 crops aligned to the lyric timeline."""
from __future__ import annotations

from bisect import bisect_right
import shutil
import subprocess
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "H079/scenes/character_refs"
OUT = ROOT / "H079/scenes/final_style01"
DURATION = 126.320167
SCENE_COUNT = 97

F = None
WL = "1420x799+0+20"
WR = "1420x799+252+20"
MR = "1320x743+352+55"
L = "1180x664+0+90"
R = "1180x664+492+90"
C = "1180x664+246+90"
TL = "1000x562+0+100"
TR = "1000x562+672+100"
TC = "1000x562+336+100"
CROPS = (F, WL, WR, MR, L, R, C, TL, TR, TC)

# A master becomes active at the listed time. Thresholds follow the meaning of
# the sung line. A few are pulled back to the preceding 1.302-second cut so the
# intended subject is already visible when its lyric begins.
MASTERS = (
    (0.00, "moon_history_museum_master.png", "moon_history_museum"),
    (5.26, "apollo_lunar_surface_archive_master.png", "apollo_lunar_surface_archive"),
    (9.16, "fifty_years_deep_space_lab_master.png", "fifty_years_deep_space_lab"),
    (14.66, "mars_goal_orbital_model_master.png", "mars_goal_orbital_model"),
    (16.74, "nasa_moon_to_mars_planning_master.png", "nasa_moon_to_mars_planning"),
    (20.20, "mars_crew_simulation_master.png", "mars_crew_simulation"),
    (23.26, "commercial_space_hangar_master.png", "commercial_space_hangar"),
    (30.814, "reusable_booster_landing_master.png", "reusable_booster_landing"),
    (33.80, "recovered_booster_inspection_master.png", "recovered_booster_inspection"),
    (36.999, "mars_obstacles_review_master.png", "mars_obstacles_review"),
    (42.10, "earth_mars_orbital_geometry_master.png", "earth_mars_orbital_geometry"),
    (50.10, "deep_space_transit_spacecraft_master.png", "deep_space_transit_spacecraft"),
    (52.80, "radiation_shielding_dosimeter_master.png", "radiation_shielding_dosimeter"),
    (55.30, "microgravity_exercise_master.png", "microgravity_exercise"),
    (58.00, "isolation_crew_support_master.png", "isolation_crew_support"),
    (61.72, "closed_loop_life_support_master.png", "closed_loop_life_support"),
    (67.06, "mars_water_ice_isru_concept_master.png", "mars_water_ice_isru_concept"),
    (70.30, "mars_greenhouse_concept_master.png", "mars_greenhouse_concept"),
    (72.90, "mars_habitat_concept_master.png", "mars_habitat_concept"),
    (76.72, "launch_infrastructure_cost_master.png", "launch_infrastructure_cost"),
    (81.76, "public_budget_dialogue_master.png", "public_budget_dialogue"),
    (85.00, "earth_needs_health_climate_master.png", "earth_needs_health_climate"),
    (88.50, "water_purification_spinoff_master.png", "water_purification_spinoff"),
    (92.00, "disaster_environment_sensor_master.png", "disaster_environment_sensor"),
    (96.00, "technology_transfer_workshop_master.png", "technology_transfer_workshop"),
    (100.72, "frontier_unknown_boundary_master.png", "frontier_unknown_boundary"),
    (106.70, "planetary_protection_cleanroom_master.png", "planetary_protection_cleanroom"),
    (110.40, "international_governance_roundtable_master.png", "international_governance_roundtable"),
    (113.72, "philosophical_observatory_master.png", "philosophical_observatory"),
    (118.00, "shared_future_earth_mars_finale_master.png", "shared_future_earth_mars_finale"),
)


def render(src: Path, dst: Path, crop: str | None) -> None:
    if crop is None:
        shutil.copyfile(src, dst)
        return
    subprocess.run(
        [
            "magick", str(src), "-crop", crop, "+repage", "-resize", "1672x941^",
            "-gravity", "center", "-extent", "1672x941", str(dst),
        ],
        check=True,
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    if any(OUT.iterdir()):
        raise RuntimeError(f"H079 output directory must be empty before rebuilding: {OUT}")

    for _, master, _ in MASTERS:
        src = REF / master
        if not src.is_file():
            raise FileNotFoundError(src)

    starts = [item[0] for item in MASTERS]
    unit = DURATION / SCENE_COUNT
    usage: Counter[str] = Counter()
    expected: list[Path] = []
    for ordinal in range(SCENE_COUNT):
        time = unit * ordinal
        master_index = bisect_right(starts, time) - 1
        _, master, prefix = MASTERS[master_index]
        usage[prefix] += 1
        crop_number = usage[prefix]
        crop = CROPS[(crop_number - 1) % len(CROPS)]
        dst = OUT / f"{ordinal + 1:03d}_{prefix}_{crop_number:02d}.png"
        render(REF / master, dst, crop)
        expected.append(dst)

    actual = sorted(OUT.glob("[0-9][0-9][0-9]_*.png"))
    missing = [prefix for _, _, prefix in MASTERS if usage[prefix] == 0]
    if actual != expected or len(actual) != SCENE_COUNT or missing:
        raise RuntimeError(
            f"H079 scene mismatch actual={len(actual)} expected={SCENE_COUNT} missing={missing}"
        )
    print(f"H079 final_style01 files verified: {len(actual)}; masters used: {len(usage)}")


if __name__ == "__main__":
    main()
