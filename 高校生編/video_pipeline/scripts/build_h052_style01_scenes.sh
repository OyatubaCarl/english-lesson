#!/bin/zsh
set -euo pipefail

ROOT="${0:A:h:h}"
REF="$ROOT/H052/scenes/character_refs"
OUT="$ROOT/H052/scenes/final_style01"
mkdir -p "$OUT"

frame() { cp "$REF/$1" "$OUT/$2"; }
crop() {
  magick "$REF/$1" -crop "$2" +repage \
    -resize '1672x941^' -gravity center -extent 1672x941 "$OUT/$3"
}
tone() {
  magick "$REF/$1" -modulate "$3" -fill "$4" -colorize 7% "$OUT/$2"
}

# 現在から2019年末の記録へ
frame next_crisis_prepared_final_master.png 01_present_day_prepared_wide.png
crop next_crisis_prepared_final_master.png 700x394+390+120 02_student_and_physician_plan.png
frame preparedness_lessons_master.png 03_public_health_system_wide.png
crop preparedness_lessons_master.png 720x405+180+170 04_student_enters_history.png

# 2019年末、武漢で症例報告
frame wuhan_case_report_master.png 05_wuhan_case_report_wide.png
crop wuhan_case_report_master.png 700x394+0+190 06_doctors_review_records.png
crop wuhan_case_report_master.png 760x428+350+180 07_anonymized_chest_images.png
crop wuhan_case_report_master.png 720x405+820+130 08_public_health_report_team.png
tone wuhan_case_report_master.png 09_unknown_cause_winter_night.png 91,102,101 '#17243a'

# 国境を越える拡大
frame cross_border_spread_master.png 10_cross_border_mobility_wide.png
crop cross_border_spread_master.png 800x450+0+120 11_surveillance_team_left.png
crop cross_border_spread_master.png 800x450+720+100 12_reports_and_monitoring.png
crop cross_border_spread_master.png 980x551+340+0 13_air_rail_port_connections.png

# WHOによるpandemic評価
frame who_pandemic_assessment_master.png 14_global_health_briefing_wide.png
crop who_pandemic_assessment_master.png 760x428+430+150 15_briefing_central_expert.png
crop who_pandemic_assessment_master.png 650x366+0+190 16_delegates_listen_left.png
crop who_pandemic_assessment_master.png 650x366+1000+190 17_delegates_listen_right.png
crop who_pandemic_assessment_master.png 1000x563+330+0 18_world_assessment_map.png
tone who_pandemic_assessment_master.png 19_pandemic_gravity.png 90,101,101 '#1d263b'

# 地域ごとに異なるlockdowns
frame lockdowns_school_business_master.png 20_lockdowns_city_wide.png
crop lockdowns_school_business_master.png 650x366+0+150 21_closed_school_gate.png
crop lockdowns_school_business_master.png 760x428+470+0 22_remote_learning_and_work.png
crop lockdowns_school_business_master.png 700x394+930+180 23_closed_shops_essential_workers.png

# 各地域のhospitalsとpatients
frame regional_hospital_patients_master.png 24_regional_hospital_wide.png
crop regional_hospital_patients_master.png 650x366+0+170 25_ambulance_arrival.png
crop regional_hospital_patients_master.png 760x428+260+180 26_patient_transfer_team.png
crop regional_hospital_patients_master.png 650x366+1000+120 27_physician_directs_triage.png

# ICUの逼迫
frame icu_health_workers_master.png 28_icu_capacity_wide.png
crop icu_health_workers_master.png 700x394+0+160 29_ventilator_and_nurse.png
crop icu_health_workers_master.png 760x428+850+130 30_icu_beds_and_staff.png

# 医療従事者のriskと連携
tone icu_health_workers_master.png 31_health_workers_risk_wide.png 94,101,101 '#16243b'
crop icu_health_workers_master.png 720x405+450+120 32_shift_coordination.png
crop icu_health_workers_master.png 620x349+1030+180 33_ppe_bedside_care.png
crop icu_health_workers_master.png 620x349+40+180 34_hand_hygiene_and_equipment.png

# Symptomsの個人差
frame symptoms_variation_master.png 35_symptoms_variation_wide.png
crop symptoms_variation_master.png 650x366+0+150 36_fever_telehealth.png
crop symptoms_variation_master.png 620x349+430+150 37_cough_and_fatigue.png
crop symptoms_variation_master.png 700x394+900+120 38_clinic_breath_assessment.png

# 発熱、咳、息苦しさ
tone symptoms_variation_master.png 39_common_symptoms_wide.png 96,101,101 '#20263a'
crop symptoms_variation_master.png 720x405+0+200 40_thermometer_and_remote_doctor.png
crop symptoms_variation_master.png 700x394+920+150 41_pulse_oximeter_clinic.png

# 軽症と高riskの人
frame mild_and_high_risk_master.png 42_mild_and_high_risk_wide.png
crop mild_and_high_risk_master.png 620x349+0+170 43_mild_home_recovery.png
crop mild_and_high_risk_master.png 620x349+300+160 44_community_meal_support.png
crop mild_and_high_risk_master.png 700x394+880+150 45_older_patient_monitored.png
crop mild_and_high_risk_master.png 620x349+1040+170 46_family_and_clinician.png
tone mild_and_high_risk_master.png 47_risk_is_not_destiny.png 94,103,102 '#19273b'

# vaccine研究
frame vaccine_research_master.png 48_vaccine_research_wide.png
crop vaccine_research_master.png 650x366+0+120 49_prior_science_models.png
crop vaccine_research_master.png 720x405+420+150 50_cell_and_manufacturing_tests.png
crop vaccine_research_master.png 700x394+880+100 51_research_team_review.png

# 試験、審査、承認、接種開始
frame clinical_trial_review_master.png 52_clinical_trial_review_wide.png
crop clinical_trial_review_master.png 620x349+0+140 53_volunteer_health_checks.png
crop clinical_trial_review_master.png 700x394+400+130 54_anonymized_trial_data.png
crop clinical_trial_review_master.png 650x366+1000+150 55_independent_regulatory_review.png
crop vaccination_rollout_master.png 760x428+0+130 56_cold_chain_delivery.png
frame vaccination_rollout_master.png 57_vaccination_begins_wide.png

# pandemicが残したlessons
frame preparedness_lessons_master.png 58_lessons_preparedness_wide.png
crop preparedness_lessons_master.png 760x428+250+130 59_student_physician_lessons.png

# public health preparedness
crop preparedness_lessons_master.png 650x366+0+170 60_ventilation_and_ppe.png
crop preparedness_lessons_master.png 760x428+800+140 61_staffing_radios_and_supplies.png

# international cooperation
frame international_cooperation_master.png 62_international_cooperation_wide.png
crop international_cooperation_master.png 720x405+0+180 63_shared_evidence_team.png
crop international_cooperation_master.png 650x366+300+250 64_safe_samples_and_supplies.png
crop international_cooperation_master.png 700x394+750+160 65_global_coordination_people.png
crop international_cooperation_master.png 760x428+900+0 66_logistics_bay_overview.png
crop international_cooperation_master.png 650x366+1020+180 67_equitable_distribution_work.png
tone international_cooperation_master.png 68_cooperation_not_ceremony.png 94,103,103 '#18243a'

# 次のcrisisへ備える結末
frame next_crisis_prepared_final_master.png 69_next_crisis_final_wide.png
crop next_crisis_prepared_final_master.png 720x405+400+160 70_student_revises_plan.png
crop next_crisis_prepared_final_master.png 650x366+0+150 71_health_workers_prepare.png
crop next_crisis_prepared_final_master.png 650x366+980+200 72_emergency_radio_and_parent.png
crop next_crisis_prepared_final_master.png 650x366+850+120 73_resident_and_delivery_worker.png
frame preparedness_lessons_master.png 74_systems_and_people_ready.png
crop preparedness_lessons_master.png 700x394+650+140 75_team_checks_resources.png
tone next_crisis_prepared_final_master.png 76_remember_the_lessons.png 105,104,102 '#50341d'
frame next_crisis_prepared_final_master.png 77_prepared_together_dawn.png

expected=("$OUT"/[0-9][0-9]_*.png)
test ${#expected[@]} -eq 77
for file in $expected; do
  test -s "$file"
done
echo "H052 final_style01 files verified: ${#expected[@]}"
