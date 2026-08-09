#!/usr/bin/env python3
"""Build the dense, historically ordered Style01 scene plan for H045."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H045"
PLAN_PATH = LESSON / "planning" / "video_plan.json"


def scene(number: int, name: str, purpose: str) -> tuple[str, str]:
    return (f"scenes/final_style01/{number:02d}_{name}.png", purpose)


GROUPS: list[tuple[float, float, list[tuple[str, str]]]] = [
    (
        0.0,
        18.094,
        [
            scene(1, "giza_dawn_wide", "夜明けのギザ台地に三基を導入"),
            scene(2, "khufu_largest", "最大のクフ王の大ピラミッド"),
            scene(3, "khafre_higher_ground", "高い地盤で同程度に見えるカフラー王のピラミッド"),
            scene(4, "menkaure_smaller", "明確に小さいメンカウラー王のピラミッド"),
            scene(5, "people_beneath_pyramids", "基部の人々と三基の巨大さ"),
            scene(6, "weathered_limestone_steps", "風化した石灰岩の段"),
            scene(7, "giza_blue_amber_transition", "青と琥珀の光に立つギザ"),
            scene(2, "khufu_largest", "三基の中で最大のクフ王墓"),
            scene(3, "khafre_higher_ground", "地形を含めた規模の比較"),
            scene(4, "menkaure_smaller", "三基が砂漠に立つ全体像"),
        ],
    ),
    (
        18.094,
        29.984,
        [
            scene(8, "khufu_scale_wide", "4500年立ち続ける大ピラミッド"),
            scene(9, "khufu_apex_from_base", "基部から見上げる頂点"),
            scene(10, "massive_corner_courses", "巨大な稜線と石の層"),
            scene(11, "weathered_block_faces", "残る石材一つ一つ"),
            scene(12, "archaeologists_at_base", "現代の研究者との大きさの対比"),
            scene(13, "human_scale_against_stone", "人の大きさと建造物の量感"),
            scene(14, "four_thousand_year_scale", "長い時間を刻む石の表面"),
        ],
    ),
    (
        29.984,
        39.685,
        [
            scene(8, "khufu_scale_wide", "146メートル級の全高"),
            scene(9, "khufu_apex_from_base", "視線の先に遠い頂点"),
            scene(10, "massive_corner_courses", "高さを支える巨大な基部"),
            scene(12, "archaeologists_at_base", "人との比較で高さを示す"),
            scene(13, "human_scale_against_stone", "基部から頂点までの圧倒的な尺度"),
        ],
    ),
    (
        39.685,
        46.106,
        [
            scene(15, "original_casing_wide", "約230万個の石材で建設された外観"),
            scene(17, "core_and_casing_boundary", "地元石灰岩の核と外装石の境界"),
            scene(18, "fitted_casing_seams", "精密に据えられた外装石"),
            scene(23, "local_quarry_wide", "建設を支えたギザの採石場"),
            scene(25, "large_local_block", "切り出された一個のblock"),
        ],
    ),
    (
        46.106,
        53.447,
        [
            scene(8, "khufu_scale_wide", "当時世界に類のない巨大建築"),
            scene(20, "upper_core_construction", "空へ伸びる建設中の核"),
            scene(21, "unfinished_apex_no_gold", "金の頂点を持たない完成直前の姿"),
            scene(22, "pyramid_completion_transition", "巨大建造物の輪郭が整う"),
        ],
    ),
    (
        53.447,
        63.469,
        [
            scene(24, "survey_and_mark_block", "ancient Egyptiansの測量と墨出し"),
            scene(26, "mallet_and_chisel_hands", "石を整形する手と道具"),
            scene(27, "wooden_levers_and_crew", "木製てこと協働作業"),
            scene(28, "quarry_face_work_team", "組織された採石班"),
            scene(31, "tura_harbor_wide", "水運まで含む建設物流"),
            scene(39, "sledge_team_wide", "方法の一部を示すそり運搬"),
        ],
    ),
    (
        63.469,
        78.096,
        [
            scene(32, "limestone_cargo_boat", "limestone blockを運ぶ船"),
            scene(34, "dock_unloading_team", "港で連携する荷下ろし班"),
            scene(35, "transfer_to_sledge", "船から木製そりへの積み替え"),
            scene(40, "flat_wooden_sledge", "車輪のない平らな木製そり"),
            scene(42, "water_on_prepared_path", "路面を湿らせる作業員"),
            scene(47, "ramp_construction_wide", "有力な説明としての傾斜路"),
            scene(48, "low_approach_ramp", "低い接近用傾斜路"),
            scene(50, "masons_and_surveyors", "石工と測量班の分業"),
            scene(54, "exact_method_still_debated", "正確な方法は今も議論中"),
        ],
    ),
    (
        78.096,
        86.148,
        [
            scene(55, "funerary_complex_wide", "王墓を中心とする葬祭複合体"),
            scene(56, "great_pyramid_and_mortuary_temple", "大ピラミッドと葬祭殿"),
            scene(57, "causeway_to_valley", "谷の神殿へ延びる参道"),
            scene(63, "kings_chamber_wide", "墓として設計された王の間"),
            scene(64, "granite_sarcophagus", "花崗岩の石棺"),
        ],
    ),
    (
        86.148,
        99.754,
        [
            scene(58, "queens_pyramids", "王権を囲む王妃のピラミッド"),
            scene(61, "boat_pits_beside_pyramid", "王墓のそばにある船坑"),
            scene(62, "valley_temple_at_water", "水辺の谷の神殿"),
            scene(65, "offerings_in_lamplight", "死後のための静かな供物"),
            scene(67, "funeral_attendants", "葬祭を担う人々"),
            scene(69, "afterlife_offerings_wide", "死後の継続を願う供物"),
            scene(70, "bread_vessels_and_flowers", "パン・器・花に表れた信念"),
            scene(72, "dawn_alignment_in_court", "王権と再生を示す朝の光"),
        ],
    ),
    (
        99.754,
        112.194,
        [
            scene(68, "royal_tomb_silence", "王墓の内部に残る静けさ"),
            scene(75, "centuries_wide", "4500年を越えて残るピラミッド"),
            scene(76, "moonlit_weathered_core", "月光に沈む風化した石の核"),
            scene(77, "dawn_on_enduring_stone", "夜明けにも変わらず残る石"),
            scene(78, "lost_casing_exposed_core", "失われた外装石と露出した核"),
            scene(79, "people_from_passing_eras", "幾つもの時代を通り過ぎる人々"),
            scene(80, "four_thousand_year_silence", "風の中のsilence"),
        ],
    ),
    (
        112.194,
        124.058,
        [
            scene(75, "centuries_wide", "ancient王国が終わった後の景観"),
            scene(76, "moonlit_weathered_core", "王国の終わり後も残る夜の石"),
            scene(77, "dawn_on_enduring_stone", "次の時代を迎える朝"),
            scene(79, "people_from_passing_eras", "異なる時代の人々と不変の石"),
            scene(80, "four_thousand_year_silence", "僕たちへ語りかけるsilence"),
            scene(81, "modern_archaeology_wide", "現代へ受け渡された問い"),
        ],
    ),
    (
        124.058,
        137.819,
        [
            scene(69, "afterlife_offerings_wide", "不老不死を求めた人々の願い"),
            scene(70, "bread_vessels_and_flowers", "石の建築へ託された供物"),
            scene(71, "hands_arrange_offerings", "願いを形にした人の手"),
            scene(73, "solar_symbols_on_objects", "再生への願いを示す太陽の象徴"),
            scene(74, "belief_without_ghosts", "幽霊ではなく儀礼に表れた信念"),
            scene(78, "lost_casing_exposed_core", "削られてもsurviveする石の核"),
            scene(86, "student_and_massive_blocks", "現代の主人公と残る巨石"),
            scene(88, "survives_today_final", "今もsurviveする人々の願い"),
        ],
    ),
    (
        137.819,
        153.000979,
        [
            scene(81, "modern_archaeology_wide", "現代の非破壊調査"),
            scene(82, "nondestructive_survey_team", "石を傷つけずに調べる研究班"),
            scene(83, "tripod_and_careful_notes", "計測器と慎重な記録"),
            scene(84, "student_listens_to_wind", "風を聞く17歳の男子高校生"),
            scene(85, "student_profile_close", "未解明の歴史を考える横顔"),
            scene(86, "student_and_massive_blocks", "主人公と4500年の石"),
            scene(87, "pyramid_beyond_open_questions", "問いの先に立ち続けるピラミッド"),
            scene(88, "survives_today_final", "沈黙を残して静かに終える"),
        ],
    ),
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
            scenes.append(
                {
                    "start": round(group_start + interval * index, 3),
                    "image": image,
                    "purpose": purpose,
                }
            )

    gaps = [
        round(float(right["start"]) - float(left["start"]), 3)
        for left, right in zip(scenes, scenes[1:])
    ]
    if len(scenes) != 88 or min(gaps) < 1.2 or max(gaps) > 2.5:
        raise RuntimeError(
            f"invalid density: count={len(scenes)} min={min(gaps)} max={max(gaps)}"
        )

    plan["scenes"] = scenes
    plan["qa_status"] = "READY_TO_RENDER_STYLE01"
    # The renderer appends the mixed-ruby/TacoBeat suffix itself.
    plan["output_name"] = "h045_adopted_song_cinematic_v1.mp4"
    PLAN_PATH.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"H045 video plan: {len(scenes)} scenes, "
        f"min gap {min(gaps):.3f}s, max gap {max(gaps):.3f}s"
    )


if __name__ == "__main__":
    main()
