#!/usr/bin/env python3
"""Build the dense, fact-checked Style01 scene plan for H050."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H050"
PLAN_PATH = LESSON / "planning" / "video_plan.json"


def scene(number: int, name: str, purpose: str) -> tuple[str, str]:
    return (f"scenes/final_style01/{number:02d}_{name}.png", purpose)


GROUPS: list[tuple[float, float, list[tuple[str, str]]]] = [
    (0.0, 7.32, [
        scene(1, "right_wide", "educationを受ける権利への導入"),
        scene(2, "morning_school_approach", "同じ学校へ向かう多様な子ども"),
        scene(3, "accessible_entrance", "障害を取り除いた入口"),
        scene(4, "teacher_student_welcome", "学ぶ人を迎える教員と高校生"),
    ]),
    (7.32, 11.8, [
        scene(5, "every_person_enters", "Educationはevery personのbasic right"),
        scene(6, "wheelchair_ramp", "身体条件に左右されないaccess"),
        scene(7, "shared_open_door", "すべての人へ開かれた教育"),
    ]),
    (11.8, 25.24, [
        scene(8, "un_hall_wide", "1948年の国連総会を参考にした会議"),
        scene(9, "diverse_delegates_left", "異なる地域から集う代表"),
        scene(10, "delegates_right", "universal human rightsを共有する各国"),
        scene(11, "raised_hands", "宣言採択の挙手"),
        scene(12, "period_microphones", "1948年当時の会議設備"),
        scene(13, "plain_declaration_document", "教育を受ける権利を含む無字の文書"),
        scene(14, "central_adoption_vote", "right to educationのdeclared"),
        scene(15, "universal_right_historic", "歴史的に確認されたuniversalな権利"),
    ]),
    (25.24, 39.492, [
        scene(16, "opportunity_region_wide", "生まれた地域とincomeで違うopportunity"),
        scene(17, "urban_nearby_school", "学校が近い都市の通学"),
        scene(18, "mountain_long_route", "山間部の長い通学路"),
        scene(19, "rural_student_walk", "遠距離を歩く同年代の生徒"),
        scene(20, "family_budget_table", "家庭で教育費を慎重に考える"),
        scene(21, "education_costs_hands", "教材・交通・学費に向き合う手"),
        scene(22, "same_age_different_paths", "同年齢でも異なるeducationの道"),
        scene(23, "opportunity_not_destiny", "incomeの影響は強いが未来は未確定"),
    ]),
    (39.492, 49.0, [
        scene(24, "access_barriers_wide", "学校へ通えないchildrenの複数の壁"),
        scene(25, "distant_school_bridge", "距離と交通のbarrier"),
        scene(26, "temporary_learning_tent", "避難先でも続く学び"),
        scene(27, "older_boy_studies_with_sibling", "家族事情と学習を両立する少年"),
        scene(28, "wheelchair_step_and_ramp", "物理的accessの壁と改善"),
        scene(29, "community_support_action", "地域が教育機会を支える行動"),
    ]),
    (49.0, 60.0, [
        scene(30, "school_resource_gap_wide", "developed countriesにも残る教育格差"),
        scene(31, "worn_classroom_equipment", "限られたqualityと設備"),
        scene(32, "shared_computer_access", "不安定なdigital access"),
        scene(33, "students_equally_engaged", "資源差と生徒の能力を混同しない"),
        scene(34, "teacher_observes_gap", "同じ都市圏のgapを確認する教員"),
        scene(35, "equipped_library_lab", "図書・実験設備が充実した学校"),
        scene(36, "inclusive_support_staff", "qualityを支える人員とaccess"),
    ]),
    (60.0, 68.86, [
        scene(37, "career_counseling_wide", "familyのeconomic conditionとcareer"),
        scene(38, "boy_girl_consider_paths", "進路を考える二人の高校生"),
        scene(39, "teacher_explains_options", "選択肢を具体化する相談"),
        scene(40, "blank_cost_planning", "学費・交通・生活費の検討"),
        scene(41, "future_choices_remain_open", "支援でfuture careerを開く余地"),
    ]),
    (68.86, 74.42, [
        scene(42, "learning_beyond_knowledge_wide", "Educationはknowledge伝達だけではない"),
        scene(43, "science_debate_art", "科学・対話・芸術を通じた学び"),
        scene(44, "practical_teamwork", "共同問題解決のprocess"),
    ]),
    (74.42, 86.82, [
        scene(45, "identity_community_wide", "individualのidentityと社会参加"),
        scene(46, "boy_presents_idea", "自分の意見を形成して伝える"),
        scene(47, "girl_listens_and_responds", "異なる意見を聞き応答する"),
        scene(48, "elders_students_dialogue", "世代間の対話"),
        scene(49, "blank_safety_map", "地域課題を共同で考える"),
        scene(50, "wheelchair_user_in_planning", "多様なmemberが意思決定に参加"),
        scene(51, "responsible_member_growth", "responsibilityのある一員へ成長"),
    ]),
    (86.82, 101.4, [
        scene(52, "scholarship_counseling_wide", "scholarshipsとreduced tuitionの相談"),
        scene(53, "girl_family_support", "本人と家族を支える制度"),
        scene(54, "advisor_blank_folders", "申請・審査を伴う支援"),
        scene(55, "tuition_reduction_discussion", "授業料減免を検討する"),
        scene(56, "housing_transport_support", "住居・通学を含むaccess支援"),
        scene(57, "university_workshop_beyond", "higher educationの実習室"),
        scene(58, "boy_waits_supportively", "若者同士が支え合う"),
        scene(59, "higher_education_opens", "より多くのyoung peopleへ機会を開く"),
    ]),
    (101.4, 106.4, [
        scene(60, "gradual_ramp_reform", "少しずつ進むaccessibility reform"),
        scene(61, "bus_library_progress", "交通と図書環境の改善"),
        scene(62, "teacher_training_progress", "教員研修を重ねるslow reform"),
    ]),
    (106.4, 120.4, [
        scene(63, "same_opportunity_wide", "every childへのsame opportunity"),
        scene(64, "safe_transport_arrival", "安全な通学手段"),
        scene(65, "step_free_school_entrance", "段差のないentrance"),
        scene(66, "tactile_guidance_and_ramp", "身体条件に応じたaccess"),
        scene(67, "enough_learning_materials", "十分な教材と学習環境"),
        scene(68, "quiet_support_space", "落ち着いて学べる支援空間"),
        scene(69, "teacher_assists_without_isolation", "孤立させない個別支援"),
        scene(70, "equal_access_continues", "educationのopportunityを保障する"),
    ]),
    (120.4, 138.160167, [
        scene(71, "gap_closing_region_wide", "equal educationでsocietyのgapが縮む"),
        scene(72, "bridge_and_school_bus", "地域を結ぶbridgeとschool bus"),
        scene(73, "regional_school_under_improvement", "改善途中の学校と足場"),
        scene(74, "connected_classrooms", "学校間の教員・教材交流"),
        scene(75, "counselor_meets_family", "家庭へ届く支援"),
        scene(76, "vocational_workshop_path", "職業訓練へ続くpath"),
        scene(77, "intergenerational_learning_wide", "世代を越えるequal education"),
        scene(78, "boy_girl_teacher_final", "高校生と教員が見守る継続"),
        scene(79, "elders_children_build_together", "子どもと高齢者が学び合う"),
        scene(80, "inclusive_society_blue_hour", "格差が縮まり始めるinclusive society"),
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
    if len(scenes) != 80 or min(gaps) < 1.45 or max(gaps) > 1.90:
        raise RuntimeError(
            f"invalid density: count={len(scenes)} min={min(gaps)} max={max(gaps)}"
        )

    plan["scenes"] = scenes
    plan["qa_status"] = "READY_TO_RENDER_STYLE01"
    plan["output_name"] = "h050_adopted_song_cinematic_v1.mp4"
    PLAN_PATH.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"H050 video plan: {len(scenes)} scenes, "
        f"min gap {min(gaps):.3f}s, max gap {max(gaps):.3f}s"
    )


if __name__ == "__main__":
    main()
