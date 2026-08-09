#!/usr/bin/env python3
"""Build the dense, fact-checked Style01 scene plan for H057."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H057"
PLAN_PATH = LESSON / "planning" / "video_plan.json"


def scene(number: int, name: str, purpose: str) -> tuple[str, str]:
    return (f"scenes/final_style01/{number:03d}_{name}.png", purpose)


GROUPS: list[tuple[float, float, list[tuple[str, str]]]] = [
    (0.0, 12.18, [
        scene(1, "smiljan_valley_wide", "1856年Smiljanの土地を導入"),
        scene(2, "church_after_rain", "父が仕えた教会と雨上がりの村"),
        scene(3, "tesla_family_home", "Tesla家の質素な住まい"),
        scene(4, "warm_doorway_family", "家族のいる暖かな戸口"),
        scene(5, "newborn_nikola", "新生児Nikolaへ寄る"),
        scene(6, "priest_father_and_mother", "父母を時代に即して描く"),
        scene(7, "siblings_gather", "兄姉と家族の全体"),
        scene(8, "dawn_over_smiljan", "電気的運命の誇張なしに夜明けへ"),
    ]),
    (12.18, 19.16, [
        scene(9, "smiljan_birth_scene_wide", "1856年の出生場面"),
        scene(10, "newborn_in_mothers_arms", "母に抱かれるNikola"),
        scene(11, "father_blesses_child", "父と母の静かな祝福"),
        scene(12, "family_and_church", "家族・家・教会を一つの土地に置く"),
        scene(13, "birth_in_modern_croatia_historic_land", "現在のCroatiaと当時の領域を混同しない"),
    ]),
    (19.16, 33.2, [
        scene(14, "new_york_harbor_1884_wide", "1884年New York港の全景"),
        scene(15, "steamship_and_docks", "蒸気船と時代相応の港"),
        scene(16, "immigrant_tesla_arrives", "28歳のimmigrant Tesla"),
        scene(17, "one_small_case", "少ない荷物での移住"),
        scene(18, "folded_technical_sketch", "発明家のtechnical sketch"),
        scene(19, "uncertain_first_step", "不確かさと意志を表情で示す"),
        scene(20, "period_manhattan_waterfront", "現代高層街でないManhattan"),
        scene(21, "immigrant_among_many_arrivals", "一人の英雄でなく多くのimmigrantsの中へ"),
        scene(22, "inventor_looks_toward_city", "electricityの世界へ歩き出す"),
    ]),
    (33.2, 39.68, [
        scene(23, "ac_motor_workshop_wide", "1888年AC motor workshop"),
        scene(24, "tesla_explains_rotating_field", "Teslaがrotating fieldを説明"),
        scene(25, "engineers_measure_motor", "engineersが実用性を測定"),
        scene(26, "westinghouse_reviews_patent", "Westinghouseと共同実装へつなぐ"),
    ]),
    (39.68, 58.78, [
        scene(27, "current_war_meeting_wide", "war of currentsを会議として導入"),
        scene(28, "edison_and_dc_engineers", "EdisonとDC engineers"),
        scene(29, "dc_local_distribution_model", "DCのlocal distribution model"),
        scene(30, "tesla_and_westinghouse_team", "Tesla・Westinghouse・AC team"),
        scene(31, "transformer_coils", "voltage conversionを可能にするtransformer"),
        scene(32, "long_distance_route_model", "long-distance transmissionの比較"),
        scene(33, "city_officials_compare_costs", "city officialsがcostとreachを比較"),
        scene(34, "engineers_discuss_safety", "安全性も技術課題として検討"),
        scene(35, "chicago_exposition_wide", "1893年Chicago Expositionへ進む"),
        scene(36, "thousands_of_lamps", "多数の実用lampが点灯"),
        scene(37, "protected_ac_switchgear", "柵内のswitchgearとoperators"),
        scene(38, "team_lights_the_fair", "個人でなくteamとsystemの成果"),
    ]),
    (58.78, 78.38, [
        scene(39, "niagara_powerhouse_wide", "1896年Niagaraの別時代"),
        scene(40, "water_drives_generators", "水力がgeneratorを駆動"),
        scene(41, "analog_control_gallery", "analog gaugesとoperators"),
        scene(42, "tesla_and_westinghouse_with_team", "TeslaとWestinghouseをteam内に置く"),
        scene(43, "early_wooden_power_poles", "1896年相応のwooden poles"),
        scene(44, "power_toward_buffalo", "Buffalo方向へのtransmission"),
        scene(45, "modern_grid_wide", "現代の家庭へ届くelectricity"),
        scene(46, "student_and_grid_engineer", "H15基準の学生がgridを学ぶ"),
        scene(47, "transformer_and_substation", "現代のAC transformerとsubstation"),
        scene(48, "solar_battery_and_inverter", "solar・battery・inverterのDC利用"),
        scene(49, "ac_grid_and_dc_devices", "AC中心とDC併用を両立させる"),
    ]),
    (78.38, 95.22, [
        scene(50, "high_frequency_lab_wide", "Teslaのimaginationを高周波実験へ"),
        scene(51, "tesla_at_safe_controls", "Teslaは安全なcontrol deskに立つ"),
        scene(52, "coil_and_fixed_arcs", "fixed terminals間の限定arc"),
        scene(53, "glowing_discharge_tubes", "wirelessに光るdischarge tubes"),
        scene(54, "radio_boat_demo_wide", "1898年radio-controlled boat"),
        scene(55, "tesla_operates_control_box", "period control boxを操作"),
        scene(56, "unmanned_boat_turns", "無人boatが水槽で旋回"),
        scene(57, "receiver_and_rudder", "receiverとrudderの応答"),
        scene(58, "reflection_concept_wide", "radarに連なる未完成の着想"),
        scene(59, "transmitter_target_receiver", "transmitter・metal target・receiver"),
        scene(60, "faint_return_on_galvanometer", "faint returnをmeterで比較"),
    ]),
    (95.22, 116.04, [
        scene(61, "wardenclyffe_construction_wide", "1902年Wardenclyffe construction"),
        scene(62, "brick_lab_and_tower", "brick laboratoryとwooden tower"),
        scene(63, "tesla_engineers_and_plans", "Teslaとengineersがplansを検討"),
        scene(64, "timber_and_cables", "timber・cables・buried conductors"),
        scene(65, "world_wireless_unfinished", "world wireless visionは未完成"),
        scene(66, "funding_meeting_wide", "business partnershipとfunding停止"),
        scene(67, "rising_cost_ledger", "cost増大をledgerで示す"),
        scene(68, "competing_wireless_news", "competing wireless communication"),
        scene(69, "empty_payroll_box", "資金不足とpayroll"),
        scene(70, "workers_cover_machinery", "workersがmachineryを保全して撤収"),
        scene(71, "silent_unpowered_tower", "towerは無電力のまま残る"),
        scene(72, "multiple_causes_not_betrayal", "単一のbetrayalでなく複合要因"),
        scene(73, "project_stops_in_mist", "projectが海霧の中で止まる"),
    ]),
    (116.04, 140.96, [
        scene(74, "hotel_room_wide", "1943年New Yorker Hotelの晩年"),
        scene(75, "patent_folders", "多くのpatentsとtechnical records"),
        scene(76, "old_medal_and_awards", "生前のrecognitionを示すmedal"),
        scene(77, "bills_and_correspondence", "reward不足と財政難を示す"),
        scene(78, "elderly_tesla_at_desk", "86歳のTeslaを尊厳ある姿で描く"),
        scene(79, "same_face_across_years", "若い頃から同じ人物性を保つ"),
        scene(80, "attendant_respects_privacy", "hotel attendantが距離を保つ"),
        scene(81, "snowy_manhattan_outside", "1943年冬のNew York"),
        scene(82, "life_ends_without_spectacle", "死の瞬間を見世物にしない"),
        scene(83, "recognition_before_death", "1893年のpublic recognitionを戻す"),
        scene(84, "public_science_demonstration", "生前のlectureとdemonstration"),
        scene(85, "patents_and_medal", "patentsとawardを併置"),
        scene(86, "later_museum_recognition", "死後に評価の範囲が広がる"),
        scene(87, "legacy_spreads_over_time", "生前の名声を消さずlegacyへ"),
    ]),
    (140.96, 164.680167, [
        scene(88, "modern_museum_wide", "現代museumと技術史教育"),
        scene(89, "student_studies_ac_motor", "学生がAC induction motorを見る"),
        scene(90, "curator_explains_many_contributors", "curatorが多くのcontributorsを示す"),
        scene(91, "wardenclyffe_model", "Wardenclyffe modelと未完のvision"),
        scene(92, "radio_boat_model", "radio-controlled boatのlegacy"),
        scene(93, "coil_and_transformers", "coil・transformers・motorの連続"),
        scene(94, "patent_records_and_portrait", "patent recordsとTeslaのportrait"),
        scene(95, "electric_cars_outside", "Teslaの名を持つmodern carsを無印で示す"),
        scene(96, "renewable_grid_beyond_glass", "modern gridとrenewable generation"),
        scene(97, "student_reads_engineering_history", "主人公がengineering historyを読む"),
        scene(98, "name_and_ideas_carry_forward", "nameとideasが後代へ受け継がれる"),
        scene(99, "future_built_by_many", "未来は多くのengineersが築く"),
        scene(100, "teslas_dream_within_our_world", "Teslaのvisionを含む現在で閉じる"),
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
    if len(scenes) != 100 or min(gaps) < 1.30 or max(gaps) > 1.90:
        raise RuntimeError(
            f"invalid density: count={len(scenes)} min={min(gaps)} max={max(gaps)}"
        )

    plan["scenes"] = scenes
    plan["qa_status"] = "READY_TO_RENDER_STYLE01"
    plan["output_name"] = "h057_adopted_song_cinematic_v1.mp4"
    PLAN_PATH.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"H057 video plan: {len(scenes)} scenes, "
        f"min gap {min(gaps):.3f}s, max gap {max(gaps):.3f}s"
    )


if __name__ == "__main__":
    main()
