#!/usr/bin/env python3
"""Build the dense, fact-checked Style01 scene plan for H056."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H056"
PLAN_PATH = LESSON / "planning" / "video_plan.json"


def scene(number: int, name: str, purpose: str) -> tuple[str, str]:
    return (f"scenes/final_style01/{number:02d}_{name}.png", purpose)


GROUPS: list[tuple[float, float, list[tuple[str, str]]]] = [
    (0.0, 13.502, [
        scene(1, "democratic_city_and_newsroom_wide", "民主主義の街と独立したnewsroomを導入"),
        scene(2, "civic_institutions_beyond_the_window", "報道機関を政府組織の外側に置く"),
        scene(3, "student_reads_multiple_reports", "H15基準の男子高校生が複数報道を読む"),
        scene(4, "editor_checks_public_records", "editorが公開記録を確かめる"),
        scene(5, "printed_sources_on_the_desk", "紙のsourceと取材ノートへ寄る"),
        scene(6, "newsroom_serves_the_public", "pressがcitizensへ情報を渡す"),
        scene(7, "independent_press_at_dawn", "独立したpressの静かな朝"),
        scene(8, "citizens_and_public_institutions_wide", "市民と公的機関の全体像"),
    ]),
    (13.502, 19.043, [
        scene(9, "legislative_chamber_observed", "立法の場が報道から観察される"),
        scene(10, "administration_and_public_records", "行政と公開記録を結ぶ"),
        scene(11, "citizen_reads_with_care", "市民が報道を注意深く読む"),
        scene(12, "press_outside_the_three_branches", "fourth estateを比喩として示す"),
    ]),
    (19.043, 31.624, [
        scene(13, "public_institutions_and_newsroom", "立法・行政・司法とnewsroom"),
        scene(14, "legislative_process_in_public", "立法過程を公開の場として描く"),
        scene(15, "administrative_office_and_records", "行政の記録に目を向ける"),
        scene(16, "judicial_hall_and_due_process", "司法とdue processを含める"),
        scene(17, "journalist_between_institutions", "journalistは三権の外から監視する"),
        scene(18, "students_compare_public_information", "次世代の受け手が情報を比較する"),
        scene(19, "citizen_questions_and_participates", "citizenの質問と参加を中心に置く"),
        scene(20, "pillars_support_society_together", "各制度が社会を支える関係"),
    ]),
    (31.624, 40.87, [
        scene(21, "investigative_newsroom_wide", "investigative newsroomの全景"),
        scene(22, "female_reporter_reads_public_record", "記者がgovernment記録を読む"),
        scene(23, "editor_compares_evidence", "editorが複数evidenceを照合する"),
        scene(24, "second_reporter_checks_business_file", "business側の記録も同じ基準で確認"),
        scene(25, "notebook_camera_and_documents", "取材道具とdocumentへ寄る"),
        scene(26, "verified_findings_for_citizens", "wrongdoingを断罪前にverifyする"),
    ]),
    (40.87, 52.76, [
        scene(27, "editorial_review_wide", "investigative reportingのeditorial review"),
        scene(28, "multiple_sources_are_compared", "独立した複数sourceを比較する"),
        scene(29, "editor_questions_the_evidence", "editorが根拠の弱点を問う"),
        scene(30, "subject_response_is_considered", "対象側のresponse機会を確認する"),
        scene(31, "public_hearing_after_reporting", "報道後の公的な応答へつなぐ"),
        scene(32, "citizens_and_officials_respond", "citizensとofficialsが検討する"),
        scene(33, "reporting_can_trigger_change", "報道が社会変化のtriggerとなる"),
    ]),
    (52.76, 74.82, [
        scene(34, "watergate_newsroom_1972_wide", "1972年Watergate取材の時代を示す"),
        scene(35, "dark_haired_reporter_at_typewriter", "若いreporterがtypewriterで整理する"),
        scene(36, "two_reporters_compare_notes", "二人のreportersが取材記録を比較する"),
        scene(37, "rotary_phone_and_editor", "固定電話とeditorで1972年を保つ"),
        scene(38, "public_records_workspace_wide", "公的recordsと複数sourceの全景"),
        scene(39, "first_reporter_checks_document", "一人目がdocumentを精査する"),
        scene(40, "second_reporter_and_editor_crosscheck", "二人目とeditorがcross-checkする"),
        scene(41, "rotary_phone_and_record_boxes", "電話とrecord boxesに裏取りを示す"),
        scene(42, "notes_sources_and_corroboration", "匿名sourceを文書と別sourceで補強する"),
        scene(43, "government_corridor_1974_wide", "1974年の制度的過程へ時間を進める"),
        scene(44, "resignation_letter_enters_process", "resignation文書を静かに手続へ入れる"),
        scene(45, "clerks_reporters_and_records", "clerks・reporters・recordsを同じ廊下に置く"),
        scene(46, "public_hearing_and_due_process", "議会と司法のdue processを含める"),
        scene(47, "many_institutions_reach_accountability", "報道だけでない複合過程を示す"),
    ]),
    (74.82, 92.0, [
        scene(48, "accountability_hearing_wide", "highest authorityへのaccountability"),
        scene(49, "auditor_reviews_verified_records", "independent auditorが記録を確認"),
        scene(50, "reporter_presents_evidence_calmly", "記者は裁判官でなく証拠を示す"),
        scene(51, "authority_answers_in_public", "authorityが公開の場で回答する"),
        scene(52, "verification_desk_at_blue_hour", "現代のinformation reliabilityへ移る"),
        scene(53, "editor_compares_old_photograph", "古い写真の再利用を疑う"),
        scene(54, "fact_checker_traces_date_and_place", "日付と場所を照合する"),
        scene(55, "student_observes_verification", "男子高校生がverificationを学ぶ"),
        scene(56, "map_archive_and_contact_sheets", "map・archive・原写真を比較する"),
        scene(57, "unverified_claim_waits_for_evidence", "未確認情報を公開前に留める"),
    ]),
    (92.0, 101.56, [
        scene(58, "old_image_spreads_without_context", "古い画像が文脈なしで拡散する"),
        scene(59, "students_react_to_their_phones", "受け手の反応は一様でない"),
        scene(60, "student_pauses_before_sharing", "主人公が共有前に立ち止まる"),
        scene(61, "librarian_traces_original_image", "librarianがoriginal imageを探す"),
        scene(62, "archive_map_and_original_context", "date・place・contextを戻す"),
        scene(63, "correction_restores_context", "訂正がjudgmentの材料を整える"),
    ]),
    (101.56, 117.74, [
        scene(64, "censorship_visiting_room_wide", "架空の独裁体制下のcensorship"),
        scene(65, "family_and_lawyer_make_contact", "家族とlawyerが拘束記者に接見する"),
        scene(66, "journalist_speaks_through_glass", "journalistのimprisonmentを抑制的に描く"),
        scene(67, "guard_keeps_formal_distance", "暴力でなく制度的拘束として示す"),
        scene(68, "rain_over_closed_newsroom", "雨の向こうの閉鎖newsroom"),
        scene(69, "shutter_descends_on_printing_room", "printing roomへのcensorship"),
        scene(70, "citizens_notice_newsroom_closure", "citizensが情報経路の消失に気づく"),
        scene(71, "legal_notes_and_family_support", "法的支援と家族のつながりを残す"),
        scene(72, "journalist_remains_composed", "記者を被害の見世物にしない"),
        scene(73, "press_freedom_is_not_guaranteed", "press freedomは当然でないと示す"),
    ]),
    (117.74, 131.56, [
        scene(74, "media_literacy_library_wide", "受け手側のmedia literacyへ移る"),
        scene(75, "classmates_compare_independent_reports", "独立した複数reportsを比べる"),
        scene(76, "student_traces_claim_to_source", "claimを原sourceまでたどる"),
        scene(77, "librarian_guides_without_dictating", "librarianは判断を押しつけず支える"),
        scene(78, "date_place_context_and_evidence", "日付・場所・文脈・evidenceを確認"),
        scene(79, "correction_slip_and_archive", "correction履歴も信頼性の材料"),
        scene(80, "student_makes_his_own_judgment", "男子高校生が自分で判断する"),
        scene(81, "reliable_source_requires_patient_checking", "reliable sourceを慎重に選ぶ"),
    ]),
    (131.56, 148.600167, [
        scene(82, "open_community_discussion_wide", "press freedomと公開討論の全景"),
        scene(83, "parent_and_child_listen", "情報を受け取る家族へ寄る"),
        scene(84, "student_enters_the_circle", "主人公も市民として参加する"),
        scene(85, "elected_official_answers_questions", "officialが市民の質問に答える"),
        scene(86, "wheelchair_user_has_equal_voice", "誰もが等しく発言できる"),
        scene(87, "local_newsroom_remains_open", "local newsroomとlibraryを開いておく"),
        scene(88, "generations_listen_to_each_other", "世代を越えて互いの声を聴く"),
        scene(89, "freedom_belongs_to_every_citizen", "freedomを記者だけの権利にしない"),
        scene(90, "protecting_press_freedom_protects_our_own", "自分たちのfreedomを守る希望で閉じる"),
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
    if len(scenes) != 90 or min(gaps) < 1.30 or max(gaps) > 1.90:
        raise RuntimeError(
            f"invalid density: count={len(scenes)} min={min(gaps)} max={max(gaps)}"
        )

    plan["scenes"] = scenes
    plan["qa_status"] = "READY_TO_RENDER_STYLE01"
    plan["output_name"] = "h056_adopted_song_cinematic_v1.mp4"
    PLAN_PATH.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"H056 video plan: {len(scenes)} scenes, "
        f"min gap {min(gaps):.3f}s, max gap {max(gaps):.3f}s"
    )


if __name__ == "__main__":
    main()
