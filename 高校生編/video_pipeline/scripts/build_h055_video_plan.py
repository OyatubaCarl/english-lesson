#!/usr/bin/env python3
"""Build the dense, fact-checked Style01 scene plan for H055."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H055"
PLAN_PATH = LESSON / "planning" / "video_plan.json"


def scene(number: int, name: str, purpose: str) -> tuple[str, str]:
    return (f"scenes/final_style01/{number:02d}_{name}.png", purpose)


GROUPS: list[tuple[float, float, list[tuple[str, str]]]] = [
    (0.0, 4.74, [
        scene(1, "modern_japan_morning_wide", "現代日本の多世代が暮らす朝を導入"),
        scene(2, "student_observes_the_city", "H15基準の男子高校生が社会の変化を見る"),
        scene(3, "older_worker_commutes", "高齢期にも仕事と日常が続く"),
    ]),
    (4.74, 10.88, [
        scene(4, "silver_haired_shop_worker", "日本のagingを働く高齢者から描く"),
        scene(5, "varied_older_lives", "高齢期の能力と生活は一様でない"),
        scene(6, "generations_share_the_street", "多世代が同じ町を共有する"),
        scene(7, "aging_society_dawn", "急速なagingを人物のある社会風景で示す"),
    ]),
    (10.88, 21.0, [
        scene(8, "population_ageing_plaza_wide", "65歳以上が大きな比率を占める社会"),
        scene(9, "older_worker_and_kiosk", "年齢を越えて担い手となる"),
        scene(10, "student_among_generations", "男子高校生が多世代の広場を歩く"),
        scene(11, "wheelchair_conversation_at_eye_level", "支援を受ける人も対等な市民"),
        scene(12, "accessible_transit_support", "移動のaccessibilityを日常として描く"),
        scene(13, "many_ways_of_living_later_life", "数値図解でなく多様な高齢期を示す"),
    ]),
    (21.0, 31.22, [
        scene(14, "long_life_celebration_wide", "長寿を家族と友人が祝う"),
        scene(15, "woodworker_and_grandchild", "長い人生で培った技能が続く"),
        scene(16, "hands_pass_the_wooden_bird", "作品を次世代へ渡す手"),
        scene(17, "student_listens_to_life_story", "男子高校生が人生の経験に耳を傾ける"),
        scene(18, "family_and_old_friend", "長寿を病気でなく関係から捉える"),
        scene(19, "longevity_is_worth_celebrating", "祝福と新たなchallengeを分ける"),
    ]),
    (31.22, 39.42, [
        scene(20, "mixed_age_workforce_wide", "複数世代が同じworkforceで働く"),
        scene(21, "silver_haired_worker_at_counter", "高齢者も就業と地域経済の担い手"),
        scene(22, "older_craft_worker", "技能を生かして働き続ける"),
        scene(23, "pension_consultation", "pensionを公的な制度調整として扱う"),
        scene(24, "work_and_system_in_one_community", "workforceとpensionを年齢対立にしない"),
    ]),
    (39.42, 46.44, [
        scene(25, "community_clinic_wide", "medical費の背景にある地域医療"),
        scene(26, "older_man_asks_clinician", "本人が医療の意思決定に参加する"),
        scene(27, "preventive_rehabilitation", "予防と自立支援もmedical care"),
        scene(28, "health_resource_meeting", "限られたbudgetの資源配分を話し合う"),
        scene(29, "care_and_budget_decisions", "高齢者を責めず制度として検討する"),
    ]),
    (46.44, 54.34, [
        scene(30, "welfare_roundtable_wide", "welfareの持続を共通課題として導入"),
        scene(31, "citizen_representatives_listen", "市民の声を含めて制度を考える"),
        scene(32, "care_worker_and_older_voice", "当事者とcare workerが対等に発言する"),
        scene(33, "public_planners_compare_options", "先進地域が複数の選択肢を比較する"),
        scene(34, "shared_welfare_challenge", "welfareを協力と設計で支える"),
    ]),
    (54.34, 59.94, [
        scene(35, "separate_homes_connected_family_wide", "家族の住まい方が変化する"),
        scene(36, "student_sees_family_visit", "男子高校生が別居家族の訪問を見る"),
        scene(37, "grandchild_arrives_for_dinner", "別々の家から食事に集まる"),
        scene(38, "warm_visit_and_video_call", "別居と家族のconnectionは両立する"),
    ]),
    (59.94, 71.06, [
        scene(39, "connection_across_households", "子や孫と離れて暮らしても交流は続く"),
        scene(40, "family_connection_close", "温かな訪問をlonelinessと混同しない"),
        scene(41, "quiet_supper_wide", "望まないlonelinessの静かな一場面"),
        scene(42, "older_man_in_blue_dusk", "一人の夕暮れを尊厳を保って描く"),
        scene(43, "single_meal_and_silent_phone", "食事と電話に孤独の感覚を寄せる"),
        scene(44, "capable_life_and_moment_of_loneliness", "生活力と孤独感が両立する"),
        scene(45, "unwanted_loneliness_not_helplessness", "一人暮らしを無力さと同一視しない"),
    ]),
    (71.06, 84.78, [
        scene(46, "community_support_hub_wide", "elderlyの一人暮らしを支える地域"),
        scene(47, "shared_meal_preparation", "共同食堂を多世代で準備する"),
        scene(48, "older_woman_and_student_serve_together", "高齢者も地域活動の担い手"),
        scene(49, "older_man_brings_his_own_tray", "支援されるだけでなく貢献する"),
        scene(50, "accessible_shuttle_arrives", "移動支援が参加を可能にする"),
        scene(51, "neighbors_check_in", "玄関での自然な見守り"),
        scene(52, "older_adults_organize_and_participate", "地域サロンを相互支援として描く"),
        scene(53, "local_efforts_in_the_rain", "さまざまなlocal effortsが生活をつなぐ"),
    ]),
    (84.78, 97.9, [
        scene(54, "weekly_volunteer_visit_wide", "volunteerが定期的に訪問する"),
        scene(55, "older_man_teaches_woodcarving", "高齢者から高校生へ技能を渡す"),
        scene(56, "student_shares_phone_skill", "高校生からdigitalの助けを返す"),
        scene(57, "two_way_learning_over_tea", "訪問を対等な交流にする"),
        scene(58, "care_technology_wide", "人手不足を補うtechnologyを導入"),
        scene(59, "explanation_and_consent", "本人への説明と同意を先に置く"),
        scene(60, "staff_operate_transfer_lift", "職員が移乗liftを安全に操作する"),
        scene(61, "human_care_and_recording", "technologyは人のcareと記録を補助する"),
    ]),
    (97.9, 108.4, [
        scene(62, "generations_support_workshop_wide", "generations間のmutual support"),
        scene(63, "older_man_teaches_children", "高齢者が知識と技能を渡す"),
        scene(64, "children_learn_the_craft", "子どもが経験から学ぶ"),
        scene(65, "student_helps_with_phone", "男子高校生がdigital操作を手伝う"),
        scene(66, "silver_haired_woman_shares_a_smile", "支援を受ける人の選択と主体性"),
        scene(67, "knowledge_moves_both_directions", "知識が双方向へ動く"),
        scene(68, "mutual_support_between_generations", "相互支援を未来社会のfoundationにする"),
    ]),
    (108.4, 114.9, [
        scene(69, "accessible_park_planning_wide", "若者と高齢者が対等に計画する"),
        scene(70, "older_craft_and_student_hands", "経験と若い力が同じ作業へ向かう"),
        scene(71, "wheelchair_user_voice_is_heard", "必要な人の意見を中心に置く"),
        scene(72, "building_the_community_together", "互いをrespectしsupportする"),
    ]),
    (114.9, 120.26, [
        scene(73, "long_lived_society_morning_wide", "長寿社会の豊かな朝を全景で示す"),
        scene(74, "older_man_teaches_a_child", "経験が次世代へ受け継がれる"),
        scene(75, "student_sets_up_community_books", "男子高校生も地域の担い手となる"),
        scene(76, "care_worker_walks_beside_resident", "必要なcareを対話とともに受ける"),
    ]),
    (120.26, 126.480979, [
        scene(77, "older_women_garden_and_share_tea", "働く・学ぶ・支える高齢期"),
        scene(78, "accessible_paths_connect_everyone", "accessibilityが多世代をつなぐ"),
        scene(79, "relationships_agency_care_and_dignity", "関係・主体性・care・尊厳を豊かさとする"),
        scene(80, "richness_of_a_long_lived_society", "静かな希望を残して曲を閉じる"),
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
    if len(scenes) != 80 or min(gaps) < 1.30 or max(gaps) > 1.90:
        raise RuntimeError(
            f"invalid density: count={len(scenes)} min={min(gaps)} max={max(gaps)}"
        )

    plan["scenes"] = scenes
    plan["qa_status"] = "READY_TO_RENDER_STYLE01"
    plan["output_name"] = "h055_adopted_song_cinematic_v1.mp4"
    PLAN_PATH.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"H055 video plan: {len(scenes)} scenes, "
        f"min gap {min(gaps):.3f}s, max gap {max(gaps):.3f}s"
    )


if __name__ == "__main__":
    main()
