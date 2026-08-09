#!/usr/bin/env python3
"""Build the dense, fact-checked Style01 scene plan for H054."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H054"
PLAN_PATH = LESSON / "planning" / "video_plan.json"


def scene(number: int, name: str, purpose: str) -> tuple[str, str]:
    return (f"scenes/final_style01/{number:02d}_{name}.png", purpose)


GROUPS: list[tuple[float, float, list[tuple[str, str]]]] = [
    (0.0, 10.0, [
        scene(1, "ancient_truce_road_wide", "古代Olympicsのekecheiriaを安全な通行として導入"),
        scene(2, "olive_road_and_heralds", "ElisからOlympiaへ向かうheraldsと参加者"),
        scene(3, "herald_proclaims_safe_passage", "休戦を告知するherald"),
        scene(4, "weapon_left_at_boundary", "聖域へ武器を持ち込まない境界"),
        scene(5, "ancient_olympia_race_wide", "古代Olympiaの競技と観客"),
        scene(6, "athletes_judges_and_rules", "競技者・審判・共有されたrules"),
    ]),
    (10.0, 12.8, [
        scene(7, "modern_spirit_wide", "現代Olympicsへ受け継がれる理念"),
        scene(8, "athletes_greet_with_respect", "excellence・friendship・respect"),
    ]),
    (12.8, 20.0, [
        scene(9, "years_of_training_wide", "世界のathletesと長年のtraining"),
        scene(10, "sprinter_start_detail", "反復するstart技術"),
        scene(11, "coach_observes_form", "coachによるフォーム確認"),
        scene(12, "recovery_and_teammate", "trainingと回復の両立"),
    ]),
    (20.0, 24.78, [
        scene(13, "discipline_dedication_wide", "disciplineとdedicationの全体"),
        scene(14, "athlete_recovery_work", "けが予防と地道な身体管理"),
        scene(15, "coach_notebook_food_and_rest", "休養・栄養・計画も努力の一部"),
    ]),
    (24.78, 28.68, [
        scene(16, "victory_not_everything_wide", "Victoryだけがすべてではない"),
        scene(17, "runner_accepts_result", "順位を受け止める主人公"),
        scene(18, "many_kinds_of_completion", "勝者以外にもある達成"),
    ]),
    (28.68, 37.42, [
        scene(19, "sportsmanship_wide", "opponentと安全を尊重するSportsmanship"),
        scene(20, "offer_a_hand", "相手へ手を差し伸べる"),
        scene(21, "official_checks_safety", "officialが安全確認を主導"),
        scene(22, "opponents_rise_together", "rulesの下で互いを認める"),
        scene(23, "respect_after_competition", "競技後に残るrespect"),
    ]),
    (37.42, 42.96, [
        scene(24, "doping_control_notification_wide", "competitionを守るroutineの通知"),
        scene(25, "athlete_and_representative", "athleteがrepresentativeと参加"),
        scene(26, "officer_explains_procedure", "権利と手順を質問できる場"),
        scene(27, "sealed_kits_and_secure_room", "未開封kitと管理された場所"),
    ]),
    (42.96, 50.16, [
        scene(28, "results_management_hearing_wide", "禁止物質使用の判断までにあるresults management"),
        scene(29, "scientist_presents_anonymous_evidence", "匿名検体と分析資料"),
        scene(30, "independent_panel_listens", "独立panelによるfair hearing"),
        scene(31, "athlete_and_representative_are_heard", "athlete側にも説明機会がある"),
    ]),
    (50.16, 55.3, [
        scene(32, "strict_testing_chain_wide", "fair playを守るstrict testing"),
        scene(33, "athlete_seals_samples", "athlete本人がsampleを封印"),
        scene(34, "secure_handoff_and_laboratory", "chain of custodyと認定laboratory"),
    ]),
    (55.3, 63.42, [
        scene(35, "winning_and_losing_teams_wide", "winning teamとlosing team"),
        scene(36, "winning_relay_team", "勝者へ集まるenthusiastic fans"),
        scene(37, "losing_team_stays_together", "敗者にも届く静かなapplause"),
        scene(38, "teams_acknowledge_each_other", "両teamが互いを認める"),
        scene(39, "applause_for_every_effort", "勝敗を越えて努力へ拍手"),
    ]),
    (63.42, 71.16, [
        scene(40, "accept_defeat_next_challenge_wide", "defeatを受け入れnext challengeへ"),
        scene(41, "baton_and_quiet_reflection", "batonを戻して結果を振り返る"),
        scene(42, "coach_resets_starting_blocks", "coachと安全に再準備"),
        scene(43, "athlete_turns_toward_start", "次のstart lineへ向き直る"),
        scene(44, "dawn_after_defeat", "即勝利でなく再挑戦を選ぶ夜明け"),
    ]),
    (71.16, 77.5, [
        scene(45, "children_watch_sportsmanship_wide", "televisionの前のchildren"),
        scene(46, "television_helping_opponent", "勝敗よりSportsmanshipを見る"),
        scene(47, "children_practice_respect", "子どもがrespectを行動で真似る"),
        scene(48, "student_and_children_learn", "男子高校生も次世代と学ぶ"),
    ]),
    (77.5, 85.880167, [
        scene(49, "role_model_community_track_wide", "athleteがrole modelとして地域へ戻る"),
        scene(50, "athlete_teaches_safe_start", "努力と安全なstartを教える"),
        scene(51, "children_practice_relay", "多様なchildrenがrelayを練習"),
        scene(52, "inclusive_track_and_student", "誰も排除しないsportとstudentの参加"),
        scene(53, "effort_can_bear_fruit_dawn", "effortのmessageを次世代へ渡す結末"),
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
    if len(scenes) != 53 or min(gaps) < 1.28 or max(gaps) > 1.90:
        raise RuntimeError(
            f"invalid density: count={len(scenes)} min={min(gaps)} max={max(gaps)}"
        )

    plan["scenes"] = scenes
    plan["qa_status"] = "READY_TO_RENDER_STYLE01"
    plan["output_name"] = "h054_adopted_song_cinematic_v1.mp4"
    PLAN_PATH.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"H054 video plan: {len(scenes)} scenes, "
        f"min gap {min(gaps):.3f}s, max gap {max(gaps):.3f}s"
    )


if __name__ == "__main__":
    main()
