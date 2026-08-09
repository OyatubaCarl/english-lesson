#!/usr/bin/env python3
"""Create H078 dense Style01 crops aligned to the lyric timeline."""
from __future__ import annotations

from bisect import bisect_right
import shutil
import subprocess
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "H078/scenes/character_refs"
OUT = ROOT / "H078/scenes/final_style01"
DURATION = 131.720167
SCENE_COUNT = 101

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

# A master becomes active at the listed time. The times follow the meaning of
# the sung line, rather than distributing the masters evenly across the song.
MASTERS = (
    (0.00, "earth_biodiversity_museum_master.png", "earth_biodiversity_museum"),
    (7.40, "forest_canopy_diversity_master.png", "forest_canopy_diversity"),
    (9.00, "soil_insect_microcosm_master.png", "soil_insect_microcosm"),
    (10.60, "reef_species_diversity_master.png", "reef_species_diversity"),
    (12.10, "taxonomy_estimate_research_master.png", "taxonomy_estimate_research"),
    (14.00, "extinction_risk_archive_master.png", "extinction_risk_archive"),
    (21.00, "habitat_loss_aerial_master.png", "habitat_loss_aerial"),
    (28.50, "deforestation_edge_master.png", "deforestation_edge"),
    (31.04, "farmland_conversion_master.png", "farmland_conversion"),
    (34.00, "urbanization_fragmentation_master.png", "urbanization_fragmentation"),
    (36.50, "displaced_wildlife_corridor_master.png", "displaced_wildlife_corridor"),
    (41.36, "poaching_snare_patrol_master.png", "poaching_snare_patrol"),
    (46.22, "elephant_family_ivory_context_master.png", "elephant_family_ivory_context"),
    (49.50, "rhino_tiger_protection_master.png", "rhino_tiger_protection"),
    (51.90, "customs_illegal_trade_evidence_master.png", "customs_illegal_trade_evidence"),
    (56.64, "climate_heat_monitoring_master.png", "climate_heat_monitoring"),
    (64.48, "healthy_coral_reef_master.png", "healthy_coral_reef"),
    (67.00, "coral_bleaching_survey_master.png", "coral_bleaching_survey"),
    (71.00, "arctic_sea_ice_hunt_master.png", "arctic_sea_ice_hunt"),
    (74.00, "arctic_melt_change_master.png", "arctic_melt_change"),
    (76.18, "rapid_environment_mosaic_master.png", "rapid_environment_mosaic"),
    (80.16, "hope_seedling_dawn_master.png", "hope_seedling_dawn"),
    (83.58, "protected_area_rangers_master.png", "protected_area_rangers"),
    (87.00, "wildlife_corridor_community_master.png", "wildlife_corridor_community"),
    (90.00, "conservation_breeding_program_master.png", "conservation_breeding_program"),
    (95.44, "population_monitoring_assessment_master.png", "population_monitoring_assessment"),
    (108.78, "biodiversity_food_agroecology_master.png", "biodiversity_food_agroecology"),
    # These two thresholds are moved to the preceding 1.304-second cut so the
    # medicine and climate images are already visible when their words begin.
    (110.80, "biodiversity_medicine_research_master.png", "biodiversity_medicine_research"),
    (113.40, "biodiversity_climate_wetland_master.png", "biodiversity_climate_wetland"),
    (116.62, "biodiversity_supports_people_finale_master.png", "biodiversity_supports_people_finale"),
    (121.00, "connected_wetland_wildlife_master.png", "connected_wetland_wildlife"),
    (125.00, "shared_stewardship_sunrise_master.png", "shared_stewardship_sunrise"),
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
        raise RuntimeError(f"H078 output directory must be empty before rebuilding: {OUT}")

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
            f"H078 scene mismatch actual={len(actual)} expected={SCENE_COUNT} missing={missing}"
        )
    print(f"H078 final_style01 files verified: {len(actual)}; masters used: {len(usage)}")


if __name__ == "__main__":
    main()
