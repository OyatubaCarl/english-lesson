#!/usr/bin/env python3
"""Build the dense, fact-checked Style01 scene plan for H051."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H051"
PLAN_PATH = LESSON / "planning" / "video_plan.json"


def scene(number: int, name: str, purpose: str) -> tuple[str, str]:
    return (f"scenes/final_style01/{number:02d}_{name}.png", purpose)


GROUPS: list[tuple[float, float, list[tuple[str, str]]]] = [
    (0.0, 2.62, [
        scene(1, "ai_lab_dawn_wide", "artificial intelligenceへの導入"),
        scene(2, "old_and_new_workstations", "直近10年の機器と研究環境の変化"),
    ]),
    (2.62, 11.36, [
        scene(3, "ai_progress_team_wide", "AIのremarkable progress"),
        scene(4, "old_desktop_and_notebooks", "10年前の小規模な研究環境"),
        scene(5, "modern_gpu_workstations", "現在のAI計算環境"),
        scene(6, "server_and_data_storage", "vast dataを支えるstorage"),
        scene(7, "researcher_student_progress", "progressを学ぶ男子高校生"),
    ]),
    (11.36, 21.073, [
        scene(8, "support_fields_wide", "algorithmsが人間をsupportする三分野"),
        scene(9, "medicine_support_station", "medicineでのAI支援"),
        scene(10, "finance_anomaly_review", "financeでの異常検知支援"),
        scene(11, "transportation_control", "transportationの運行支援"),
        scene(12, "researcher_explains_algorithms", "用途別algorithmを説明する研究者"),
        scene(13, "humans_make_decisions", "最終判断を担うhumans"),
    ]),
    (21.073, 29.491, [
        scene(14, "diagnostic_assistance_wide", "diagnostic assistanceの現場"),
        scene(15, "candidate_region_review", "医師がAI候補領域を確認"),
        scene(16, "doctor_patient_final_decision", "診断を人間の対話へ戻す"),
        scene(17, "self_driving_test_transition", "限定条件で試験するself-driving car"),
        scene(18, "natural_language_support_transition", "natural language processing支援"),
    ]),
    (29.491, 34.204, [
        scene(19, "applications_change_lives_wide", "生活へ入る各application"),
        scene(20, "speech_translation_assistance", "音声・翻訳を助けるapplication"),
        scene(21, "human_summary_correction", "出力を確認し修正する人間"),
    ]),
    (34.204, 40.512, [
        scene(22, "automation_industry_wide", "industryを変えるautomation"),
        scene(23, "collaborative_robot_cells", "協働robotと安全柵"),
        scene(24, "maintenance_new_roles", "監督・保守へ変わるlabor"),
        scene(25, "worker_retraining", "再訓練を受けるworkers"),
    ]),
    (40.512, 45.753, [
        scene(26, "rapid_progress_risk_wide", "rapid technological progressとserious risks"),
        scene(27, "consent_and_data_cabinet", "privacyを守るconsentとdata管理"),
        scene(28, "worker_role_anxiety", "automationに伴うjob risk"),
    ]),
    (45.753, 60.88, [
        scene(29, "privacy_risk_close", "privacy invasionのrisk"),
        scene(30, "sealed_data_access", "data accessを限定する保管"),
        scene(31, "job_change_training", "job loss riskとretraining"),
        scene(32, "misinformation_image_comparison", "生成・改変されたmisinformation"),
        scene(33, "fact_check_team", "原資料と照合するfact-check"),
        scene(34, "recommendation_review", "spreadを広げる推薦経路の確認"),
        scene(35, "student_traces_risks", "複数riskを追う高校生"),
        scene(36, "risks_require_response", "社会対応が必要なrisk"),
    ]),
    (60.88, 64.46, [
        scene(37, "society_roundtable_wide", "societyがconsequencesへ向き合う"),
        scene(38, "evidence_and_consequences", "benefitとriskの具体的証拠"),
    ]),
    (64.46, 69.64, [
        scene(39, "responsibility_review_wide", "algorithmのresponsibility"),
        scene(40, "distributed_actors", "開発・提供・導入・運用・監査の責任"),
        scene(41, "decision_records", "decision経路を記録から追う"),
    ]),
    (69.64, 74.84, [
        scene(42, "accident_court_wide", "self-driving事故後のcourt"),
        scene(43, "damaged_sensor_and_road_model", "sensor・道路・整備記録のevidence"),
        scene(44, "expert_and_parties_accountability", "複数当事者のaccountability"),
    ]),
    (74.84, 79.6, [
        scene(45, "unanswered_questions_wide", "complete answersのない問い"),
        scene(46, "blank_evidence_objects", "bias・privacy・safetyを示す無文字資料"),
        scene(47, "researcher_student_think", "研究者と高校生が問いを考える"),
    ]),
    (79.6, 85.96, [
        scene(48, "regulations_hearing_wide", "governmentsがAI regulationsを検討"),
        scene(49, "public_officials_and_citizens", "行政・市民・技術者の公聴会"),
        scene(50, "four_risk_folders", "risk段階別のregulation"),
        scene(51, "technical_evidence_table", "規制判断を支える技術evidence"),
    ]),
    (85.96, 95.06, [
        scene(52, "eu_ai_act_wide", "European Unionのcomprehensive AI law"),
        scene(53, "european_committee", "複数のstakeholdersによる審議"),
        scene(54, "risk_based_folders", "risk-basedな義務の差"),
        scene(55, "conformity_testing", "高risk用途の適合確認"),
        scene(56, "phased_implementation", "段階的に続くAI Act実施"),
    ]),
    (95.06, 102.56, [
        scene(57, "technology_tool_wide", "Technology in itself is neutralという論点"),
        scene(58, "workstation_without_personality", "意思を持たないhardwareとsoftware"),
        scene(59, "design_data_use_choices", "design・data・useに入る価値判断"),
        scene(60, "neutral_claim_needs_context", "技術の中立性を人間の選択で補う"),
    ]),
    (102.56, 108.44, [
        scene(61, "ethical_judgment_wide", "ethical purposeとhuman judgment"),
        scene(62, "compare_ai_output_evidence", "AI出力をsource evidenceと比較"),
        scene(63, "student_leads_discussion", "男子高校生が判断を言語化"),
    ]),
    (108.44, 119.120167, [
        scene(64, "human_judgment_final_wide", "AIが人間の代わりに考えない結末"),
        scene(65, "physician_checks_sources", "医師が根拠を再確認"),
        scene(66, "technician_checks_sensor", "技術者が現物sensorを確認"),
        scene(67, "public_official_listens", "異なる立場の判断を聞く"),
        scene(68, "student_revises_plan", "AI提案を人間が修正"),
        scene(69, "think_better_together", "AIを使い以前よりbetterに考える"),
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
    if len(scenes) != 69 or min(gaps) < 1.28 or max(gaps) > 2.00:
        raise RuntimeError(
            f"invalid density: count={len(scenes)} min={min(gaps)} max={max(gaps)}"
        )

    plan["scenes"] = scenes
    plan["qa_status"] = "READY_TO_RENDER_STYLE01"
    plan["output_name"] = "h051_adopted_song_cinematic_v1.mp4"
    PLAN_PATH.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"H051 video plan: {len(scenes)} scenes, "
        f"min gap {min(gaps):.3f}s, max gap {max(gaps):.3f}s"
    )


if __name__ == "__main__":
    main()
