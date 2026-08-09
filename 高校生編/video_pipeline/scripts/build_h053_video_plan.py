#!/usr/bin/env python3
"""Build the dense, fact-checked Style01 scene plan for H053."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H053"
PLAN_PATH = LESSON / "planning" / "video_plan.json"


def scene(number: int, name: str, purpose: str) -> tuple[str, str]:
    return (f"scenes/final_style01/{number:02d}_{name}.png", purpose)


GROUPS: list[tuple[float, float, list[tuple[str, str]]]] = [
    (0.0, 4.06, [
        scene(1, "modern_city_dawn_wide", "現代都市の夜明けから百年を見渡す"),
        scene(2, "city_model_overview", "都市を変えられる空間として示す"),
        scene(3, "student_and_planner_begin", "男子高校生と都市計画家が記録を迎る"),
    ]),
    (4.06, 13.178, [
        scene(4, "early_twentieth_century_wide", "20世紀初頭の田園と成長する都市"),
        scene(5, "rural_fields_and_families", "urban areaの外で暮らす多くの人々"),
        scene(6, "railway_and_migration", "鉄道に沿った人と物の移動"),
        scene(7, "growing_industrial_city", "成長途上の工業都市"),
        scene(8, "one_in_ten_historical_memory", "約10人に1人という歌詞は推計として扱う"),
    ]),
    (13.178, 21.08, [
        scene(9, "today_more_than_half_wide", "現在の広大な都市圏"),
        scene(10, "coastal_housing_districts", "都市人口を支える住宅地"),
        scene(11, "rail_station_and_center", "輸送力の大きな駅と中心部"),
        scene(12, "expanding_urban_edge", "山際まで続く都市の縁"),
        scene(13, "city_population_scale", "人口が集中した規模を静かに示す"),
    ]),
    (21.08, 30.88, [
        scene(14, "urban_opportunities_wide", "Urbanizationが機会を集めた街"),
        scene(15, "jobs_and_small_business", "雇用と小さな事業へのaccess"),
        scene(16, "education_access", "教育へのaccess"),
        scene(17, "medical_care_access", "医療へのaccess"),
        scene(18, "waiting_and_unequal_access", "機会の集中だけで格差は消えない"),
        scene(19, "benefits_and_divides", "利点と深刻な問題の両面"),
    ]),
    (30.88, 37.06, [
        scene(20, "traffic_congestion_wide", "Traffic congestionの街路全体"),
        scene(21, "gridlocked_road_detail", "過密な車列と遅延"),
        scene(22, "housing_price_pressure", "住宅価格と選択肢の狭まり"),
        scene(23, "air_pollution_and_health", "air pollutionと健康の関係"),
    ]),
    (37.06, 41.84, [
        scene(24, "global_cities_model_wide", "Tokyo・New York・London・Shanghaiの比較"),
        scene(25, "student_compares_city_forms", "男子高校生が異なる都市形態を見る"),
        scene(26, "planner_compares_infrastructure", "都市計画家がinfrastructureを比較する"),
    ]),
    (41.84, 48.66, [
        scene(27, "density_and_infrastructure_wide", "population densityとinfrastructure capacity"),
        scene(28, "dense_housing_and_rail", "高密度の住宅と鉄道"),
        scene(29, "station_capacity_and_crowds", "駅の収容力と利用者"),
        scene(30, "network_limits_at_rush_hour", "混雑時に表れる網の限界"),
    ]),
    (48.66, 57.66, [
        scene(31, "sustainable_street_wide", "sustainableなurban planningの実装"),
        scene(32, "residents_review_the_plan", "住民と専門家が計画を確認"),
        scene(33, "protected_cycle_route", "保護された自転車路"),
        scene(34, "accessible_green_corridor", "バリアフリーの緑道"),
        scene(35, "bus_and_shaded_sidewalk", "公共交通と歩行空間"),
    ]),
    (57.66, 68.62, [
        scene(36, "green_park_and_transit_wide", "緑地とpublic transportationを結ぶ地区"),
        scene(37, "rain_garden_restoration", "公園と雨水を受け止める緑地"),
        scene(38, "cyclists_and_accessible_path", "pedestriansとcyclistsの安全な道"),
        scene(39, "tram_bus_and_station", "鉄道・バス・駅へのinvestment"),
        scene(40, "neighbors_plan_green_space", "地域の人々が緑地を検討"),
        scene(41, "public_investment_in_daily_life", "investmentが日常のaccessに変わる"),
    ]),
    (68.62, 76.86, [
        scene(42, "move_to_suburbs_wide", "都市中心部からsuburbsへ"),
        scene(43, "family_and_moving_truck", "移転を選ぶ家族"),
        scene(44, "suburban_station_access", "郊外の鉄道access"),
        scene(45, "housing_consultation", "住宅と生活基盤の相談"),
        scene(46, "city_center_in_distance", "離れた中心部と続く往来"),
    ]),
    (76.86, 83.662, [
        scene(47, "remote_work_regions_wide", "remote workで近づくurbanとrural"),
        scene(48, "city_apartment_remote_work", "都市の住宅で働く人"),
        scene(49, "suburban_home_and_coworking", "郊外の自宅と共有仕事場"),
        scene(50, "rural_broadband_clinic_and_bus", "田園地域に残る通信・医療・交通の差"),
    ]),
    (83.662, 88.18, [
        scene(51, "cities_continue_to_change", "形を変え続ける都市"),
        scene(52, "rail_housing_and_waterfront", "交通・住宅・自然の組み替え"),
        scene(53, "future_shape_is_a_choice", "未来の形は計画と選択で変わる"),
    ]),
    (88.18, 96.240979, [
        scene(54, "inclusive_city_workshop_wide", "誰もが参加する都市設計"),
        scene(55, "bus_driver_older_resident_and_child", "年齢と立場の異なる住民の声"),
        scene(56, "student_planner_and_city_model", "男子高校生と計画家が模型を改善"),
        scene(57, "wheelchair_user_housing_adviser_and_shopkeeper", "移動・住宅・商いのaccessを同時に検討"),
        scene(58, "everyone_can_live_with_peace_of_mind", "みんなが安心して暮らせる都市へ"),
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
    if len(scenes) != 58 or min(gaps) < 1.28 or max(gaps) > 2.00:
        raise RuntimeError(
            f"invalid density: count={len(scenes)} min={min(gaps)} max={max(gaps)}"
        )

    plan["scenes"] = scenes
    plan["qa_status"] = "READY_TO_RENDER_STYLE01"
    plan["output_name"] = "h053_adopted_song_cinematic_v1.mp4"
    PLAN_PATH.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"H053 video plan: {len(scenes)} scenes, "
        f"min gap {min(gaps):.3f}s, max gap {max(gaps):.3f}s"
    )


if __name__ == "__main__":
    main()
