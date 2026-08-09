#!/usr/bin/env python3
"""Build the dense, fact-checked Style01 scene plan for H052."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H052"
PLAN_PATH = LESSON / "planning" / "video_plan.json"


def scene(number: int, name: str, purpose: str) -> tuple[str, str]:
    return (f"scenes/final_style01/{number:02d}_{name}.png", purpose)


GROUPS: list[tuple[float, float, list[tuple[str, str]]]] = [
    (0.0, 6.64, [
        scene(1, "present_day_prepared_wide", "現在のpreparednessから過去を振り返る導入"),
        scene(2, "student_and_physician_plan", "男子高校生と公衆衛生医"),
        scene(3, "public_health_system_wide", "地域のpublic health system"),
        scene(4, "student_enters_history", "2019年末の記録へ入る"),
    ]),
    (6.64, 15.22, [
        scene(5, "wuhan_case_report_wide", "2019年末の武漢で把握された肺炎症例"),
        scene(6, "doctors_review_records", "複数症例を確認する医師"),
        scene(7, "anonymized_chest_images", "匿名化された胸部画像"),
        scene(8, "public_health_report_team", "公衆衛生当局への報告"),
        scene(9, "unknown_cause_winter_night", "原因不明の段階を保つ"),
    ]),
    (15.22, 20.92, [
        scene(10, "cross_border_mobility_wide", "数週間で国境を越える広がり"),
        scene(11, "surveillance_team_left", "地域情報を照合する監視team"),
        scene(12, "reports_and_monitoring", "複数地域から届く報告"),
        scene(13, "air_rail_port_connections", "空路・鉄道・港の人の移動"),
    ]),
    (20.92, 32.32, [
        scene(14, "global_health_briefing_wide", "2020年3月のWHO緊急会見"),
        scene(15, "briefing_central_expert", "pandemic評価を説明する専門家"),
        scene(16, "delegates_listen_left", "加盟国のdelegates"),
        scene(17, "delegates_listen_right", "異なる地域の代表"),
        scene(18, "world_assessment_map", "世界的拡大の評価"),
        scene(19, "pandemic_gravity", "pandemicという語の重さ"),
    ]),
    (32.32, 39.82, [
        scene(20, "lockdowns_city_wide", "地域ごとに異なるlockdowns"),
        scene(21, "closed_school_gate", "閉鎖された学校"),
        scene(22, "remote_learning_and_work", "在宅学習と仕事"),
        scene(23, "closed_shops_essential_workers", "休業する店と続く必要業務"),
    ]),
    (39.82, 45.96, [
        scene(24, "regional_hospital_wide", "各地域のhospitals"),
        scene(25, "ambulance_arrival", "救急搬送"),
        scene(26, "patient_transfer_team", "patientsを受け入れるteam"),
        scene(27, "physician_directs_triage", "院内動線を整理する医師"),
    ]),
    (45.96, 50.92, [
        scene(28, "icu_capacity_wide", "満床に近づくintensive care unit"),
        scene(29, "ventilator_and_nurse", "呼吸管理機器を確認する看護師"),
        scene(30, "icu_beds_and_staff", "病床と医療staffの逼迫"),
    ]),
    (50.92, 56.58, [
        scene(31, "health_workers_risk_wide", "医師と看護師が負ったrisk"),
        scene(32, "shift_coordination", "交代勤務とteam連携"),
        scene(33, "ppe_bedside_care", "PPEを着けたbedside care"),
        scene(34, "hand_hygiene_and_equipment", "手指衛生と機器確認"),
    ]),
    (56.58, 62.92, [
        scene(35, "symptoms_variation_wide", "人によって異なるSymptoms"),
        scene(36, "fever_telehealth", "発熱とremote相談"),
        scene(37, "cough_and_fatigue", "咳と倦怠感"),
        scene(38, "clinic_breath_assessment", "息苦しさの医療評価"),
    ]),
    (62.92, 67.92, [
        scene(39, "common_symptoms_wide", "よく見られた症状"),
        scene(40, "thermometer_and_remote_doctor", "体温確認と遠隔支援"),
        scene(41, "pulse_oximeter_clinic", "診療所での呼吸状態確認"),
    ]),
    (67.92, 77.94, [
        scene(42, "mild_and_high_risk_wide", "軽症と重症化riskの対比"),
        scene(43, "mild_home_recovery", "軽症の在宅療養"),
        scene(44, "community_meal_support", "地域からの生活支援"),
        scene(45, "older_patient_monitored", "基礎疾患のある高齢者の監視"),
        scene(46, "family_and_clinician", "家族とclinicianの連携"),
        scene(47, "risk_is_not_destiny", "年齢だけで運命を決めない"),
    ]),
    (77.94, 83.84, [
        scene(48, "vaccine_research_wide", "前例のない速さのvaccine研究"),
        scene(49, "prior_science_models", "既存研究の積み重ね"),
        scene(50, "cell_and_manufacturing_tests", "細胞試験と製造試験"),
        scene(51, "research_team_review", "研究teamのevidence review"),
    ]),
    (83.84, 95.04, [
        scene(52, "clinical_trial_review_wide", "臨床試験と独立審査"),
        scene(53, "volunteer_health_checks", "成人volunteerの健康確認"),
        scene(54, "anonymized_trial_data", "匿名化されたtrial data"),
        scene(55, "independent_regulatory_review", "規制当局の独立review"),
        scene(56, "cold_chain_delivery", "承認後のcold chain"),
        scene(57, "vaccination_begins_wide", "各地域でvaccination開始"),
    ]),
    (95.04, 98.92, [
        scene(58, "lessons_preparedness_wide", "pandemicが残したlessons"),
        scene(59, "student_physician_lessons", "教訓を学ぶ男子高校生"),
    ]),
    (98.92, 102.08, [
        scene(60, "ventilation_and_ppe", "public health preparednessの実物"),
        scene(61, "staffing_radios_and_supplies", "人材・連絡・物資の備え"),
    ]),
    (102.08, 115.08, [
        scene(62, "international_cooperation_wide", "international cooperation"),
        scene(63, "shared_evidence_team", "国境を越えたevidence共有"),
        scene(64, "safe_samples_and_supplies", "安全な検体情報と物資"),
        scene(65, "global_coordination_people", "研究者・保健当局・物流担当"),
        scene(66, "logistics_bay_overview", "国際的な供給調整"),
        scene(67, "equitable_distribution_work", "公平なaccessと残る格差"),
        scene(68, "cooperation_not_ceremony", "儀礼でなく具体的な協力"),
    ]),
    (115.08, 130.720167, [
        scene(69, "next_crisis_final_wide", "次のcrisisへ備える結末"),
        scene(70, "student_revises_plan", "僕たちがlessonsを記録"),
        scene(71, "health_workers_prepare", "医療者が資材を点検"),
        scene(72, "emergency_radio_and_parent", "地域連絡と家庭の参加"),
        scene(73, "resident_and_delivery_worker", "高齢者と物流担当も参加"),
        scene(74, "systems_and_people_ready", "systemとpeopleのpreparedness"),
        scene(75, "team_checks_resources", "次の危機へ資源を確認"),
        scene(76, "remember_the_lessons", "恐怖でなく記憶と協力"),
        scene(77, "prepared_together_dawn", "lessonsを忘れず夜明けへ"),
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
    if len(scenes) != 77 or min(gaps) < 1.28 or max(gaps) > 2.00:
        raise RuntimeError(
            f"invalid density: count={len(scenes)} min={min(gaps)} max={max(gaps)}"
        )

    plan["scenes"] = scenes
    plan["qa_status"] = "READY_TO_RENDER_STYLE01"
    plan["output_name"] = "h052_adopted_song_cinematic_v1.mp4"
    PLAN_PATH.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"H052 video plan: {len(scenes)} scenes, "
        f"min gap {min(gaps):.3f}s, max gap {max(gaps):.3f}s"
    )


if __name__ == "__main__":
    main()
