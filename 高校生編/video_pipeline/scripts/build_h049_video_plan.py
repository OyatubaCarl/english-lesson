#!/usr/bin/env python3
"""Build the dense, fact-checked Style01 scene plan for H049."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H049"
PLAN_PATH = LESSON / "planning" / "video_plan.json"


def scene(number: int, name: str, purpose: str) -> tuple[str, str]:
    return (f"scenes/final_style01/{number:02d}_{name}.png", purpose)


GROUPS: list[tuple[float, float, list[tuple[str, str]]]] = [
    (0.0, 9.96, [
        scene(1, "industrial_to_modern_wide", "産業革命から現代への導入"),
        scene(2, "early_coal_factories", "石炭を使う初期工業都市"),
        scene(3, "steam_rail_and_port", "蒸気機関・鉄道・港の拡大"),
        scene(4, "expanding_modern_city", "現代まで続く都市化"),
        scene(5, "scientist_student_weather_station", "climateを観測する現代の科学者と高校生"),
    ]),
    (9.96, 21.22, [
        scene(6, "industrial_revolution_city", "industrial revolution以降の変化"),
        scene(7, "century_of_urban_growth", "長期に続いたエネルギー利用と都市成長"),
        scene(8, "present_coastal_city", "現代のplanetと都市"),
        scene(9, "one_atmosphere_across_time", "時代を越えてつながる一つの大気"),
        scene(10, "observatory_transition", "climate変化を観測する施設"),
        scene(11, "student_learns_measurement", "急速な変化を学ぶ男子高校生"),
    ]),
    (21.22, 32.86, [
        scene(12, "temperature_observation_wide", "global average temperatureの観測"),
        scene(13, "historic_weather_recorder", "過去の基準となる気象記録"),
        scene(14, "scientist_explains_baseline", "歴史基準との比較"),
        scene(15, "modern_land_ocean_sensors", "陸と海の多数の観測"),
        scene(16, "ice_core_samples", "長期変化を調べる氷床core"),
        scene(17, "warming_stripes_without_numbers", "約1.1度の上昇を示す無文字の傾向"),
    ]),
    (32.86, 42.966, [
        scene(18, "fossil_fuel_district_wide", "fossil fuel利用の全体像"),
        scene(19, "coal_stockpile_and_rail", "燃焼へ運ばれる石炭fuel"),
        scene(20, "petroleum_tank_and_truck", "石油系fuelの流れ"),
        scene(21, "power_plant_stacks", "燃焼で生じるcarbon dioxide"),
        scene(22, "stack_sampling_team", "煙道のemission測定"),
        scene(23, "emission_sample_canisters", "科学的に採取する排出sample"),
    ]),
    (42.966, 50.511, [
        scene(24, "land_use_watershed_wide", "deforestationとagricultural practices"),
        scene(25, "intact_forest_and_stream", "残された森林と流域"),
        scene(26, "cleared_forest_edge", "森林減少の境界"),
        scene(27, "restoration_seedlings_and_scientist", "土地利用を調べる科学者と再生作業"),
        scene(28, "rice_cattle_and_soil_management", "農業の水・土・家畜管理"),
    ]),
    (50.511, 64.22, [
        scene(29, "climate_impacts_region_wide", "海岸・河川・内陸に現れる影響"),
        scene(30, "high_tide_wetland", "sea level riseと沿岸湿地"),
        scene(31, "tide_gauge_technicians", "海面を測る技術者"),
        scene(32, "high_river_and_barriers", "頻度を増す洪水risk"),
        scene(33, "orderly_flood_response", "地域の洪水対応"),
        scene(34, "low_reservoir_and_dry_fields", "droughtと貯水池低下"),
        scene(35, "scientist_student_observe_impacts", "複数のhazardsを観察"),
        scene(36, "regional_hazards_not_apocalypse", "強いstormを含む地域差のあるrisk"),
    ]),
    (64.22, 77.04, [
        scene(37, "ecosystems_fieldwork_wide", "破壊されるecosystemsの調査"),
        scene(38, "tidal_wetland_birds", "生息場所が減る渡り鳥species"),
        scene(39, "scientist_photographs_amphibian", "絶滅riskにある小型species"),
        scene(40, "partly_bleached_coral", "影響を受けたサンゴecosystem"),
        scene(41, "reduced_forest_habitat", "縮小した森林habitat"),
        scene(42, "ecologists_mark_habitat", "speciesの生息域を記録"),
        scene(43, "species_extinction_risk", "複数speciesが直面するextinction threat"),
    ]),
    (77.04, 88.32, [
        scene(44, "kyoto_conference_wide", "1997年Kyoto Protocolの会議"),
        scene(45, "chair_adopts_protocol", "Protocolの採択"),
        scene(46, "many_country_delegates", "国際交渉に参加する各国代表"),
        scene(47, "blue_target_folder", "先進国等へ渡る削減target"),
        scene(48, "green_yellow_targets", "国ごとに異なるreduction目標"),
        scene(49, "red_target_folder", "差のある拘束的target"),
        scene(50, "differentiated_reduction_targets", "全世界同一ではないKyotoの目標"),
    ]),
    (88.32, 102.32, [
        scene(51, "paris_conference_wide", "2015年Paris Agreementの会議"),
        scene(52, "scientist_explains_shared_goal", "科学者が共有する温度goal"),
        scene(53, "diverse_delegations_left", "多くの国が参加する枠組み"),
        scene(54, "diverse_delegations_right", "世界規模のAgreement"),
        scene(55, "two_temperature_goal_bands", "well below 2度と1.5度努力の方向"),
        scene(56, "common_agreement_document", "共通のAgreement文書"),
        scene(57, "serious_ongoing_commitment", "実施を続ける各国の責任"),
        scene(58, "paris_framework_not_finished", "達成済みでなく継続中のgoal"),
    ]),
    (102.32, 113.48, [
        scene(59, "renewable_region_wide", "renewable energyへのinvestment"),
        scene(60, "rooftop_solar_and_workers", "太陽光設備と保守人材"),
        scene(61, "wind_grid_storage", "風力・送電網・蓄電"),
        scene(62, "scientist_student_engineers", "地域全体の投資判断"),
        scene(63, "regulation_program_wide", "carsとfactoriesのemissions regulation"),
        scene(64, "vehicle_emission_test", "自動車排出の測定と移行"),
        scene(65, "factory_monitoring_and_upgrade", "工場emissionsの測定と設備改善"),
    ]),
    (113.48, 120.0, [
        scene(66, "transboundary_climate_wide", "一国だけで解けないclimate change"),
        scene(67, "rain_and_shared_river", "国境を越える雨と河川"),
        scene(68, "haze_and_shared_coast", "大気と海岸のつながり"),
        scene(69, "sensor_exchange_at_border", "単独対応を越える観測協力"),
    ]),
    (120.0, 132.84, [
        scene(70, "international_cooperation_wide", "international cooperationの全体像"),
        scene(71, "shared_weather_sensors", "国際的に共有する観測技術"),
        scene(72, "teams_exchange_data_drive", "気候dataと機材の共有"),
        scene(73, "student_carries_sensor_case", "次世代も参加するcooperation"),
        scene(74, "wetland_adaptation_model", "適応と湿地再生の共同計画"),
        scene(75, "early_warning_training", "早期警戒と防災training"),
        scene(76, "science_technology_adaptation_shared", "地球のfutureを守る共同作業"),
    ]),
    (132.84, 147.320167, [
        scene(77, "sustainable_generations_wide", "世代を超えたsustainable society"),
        scene(78, "wetland_replanting_elders_children", "子どもと高齢者が共同する湿地再生"),
        scene(79, "student_and_child_work_together", "次の世代へつなぐ作業"),
        scene(80, "electric_public_transit", "日常を支える低排出の公共交通"),
        scene(81, "insulated_solar_homes", "断熱住宅と分散型energy"),
        scene(82, "repair_workshop_generations", "修理と長期利用を支える地域"),
        scene(83, "shared_goal_in_action", "shared goalを具体化する複数世代"),
        scene(84, "sustainable_society_final", "sustainableな社会へ続く結末"),
    ]),
]


def main() -> None:
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    scenes: list[dict[str, object]] = []
    for group_start, group_end, items in GROUPS:
        interval = (group_end - group_start) / len(items)
        for index, (image, purpose) in enumerate(items):
            path = LESSON / image
            if not path.is_file():
                raise FileNotFoundError(path)
            scenes.append({
                "start": round(group_start + interval * index, 3),
                "image": image,
                "purpose": purpose,
            })

    gaps = [
        round(float(right["start"]) - float(left["start"]), 3)
        for left, right in zip(scenes, scenes[1:])
    ]
    if len(scenes) != 84 or min(gaps) < 1.50 or max(gaps) > 2.0:
        raise RuntimeError(
            f"invalid density: count={len(scenes)} min={min(gaps)} max={max(gaps)}"
        )

    plan["scenes"] = scenes
    plan["qa_status"] = "READY_TO_RENDER_STYLE01"
    plan["output_name"] = "h049_adopted_song_cinematic_v1.mp4"
    PLAN_PATH.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"H049 video plan: {len(scenes)} scenes, "
        f"min gap {min(gaps):.3f}s, max gap {max(gaps):.3f}s"
    )


if __name__ == "__main__":
    main()
