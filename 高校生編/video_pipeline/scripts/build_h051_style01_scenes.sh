#!/bin/zsh
set -euo pipefail

ROOT="${0:A:h:h}"
REF="$ROOT/H051/scenes/character_refs"
OUT="$ROOT/H051/scenes/final_style01"
mkdir -p "$OUT"

frame() { cp "$REF/$1" "$OUT/$2"; }
crop() {
  magick "$REF/$1" -crop "$2" +repage \
    -resize '1672x941^' -gravity center -extent 1672x941 "$OUT/$3"
}
tone() {
  magick "$REF/$1" -modulate "$3" -fill "$4" -colorize 7% "$OUT/$2"
}

# 導入と過去10年のAI progress
frame ai_progress_data_master.png 01_ai_lab_dawn_wide.png
crop ai_progress_data_master.png 760x428+0+170 02_old_and_new_workstations.png
frame ai_progress_data_master.png 03_ai_progress_team_wide.png
crop ai_progress_data_master.png 620x349+0+210 04_old_desktop_and_notebooks.png
crop ai_progress_data_master.png 760x428+430+220 05_modern_gpu_workstations.png
crop ai_progress_data_master.png 650x366+990+130 06_server_and_data_storage.png
crop ai_progress_data_master.png 620x349+850+180 07_researcher_student_progress.png

# algorithms support medicine, finance, transportation
frame ai_support_fields_master.png 08_support_fields_wide.png
crop ai_support_fields_master.png 700x394+0+240 09_medicine_support_station.png
crop ai_support_fields_master.png 660x371+520+250 10_finance_anomaly_review.png
crop ai_support_fields_master.png 760x428+900+160 11_transportation_control.png
crop ai_support_fields_master.png 600x338+950+300 12_researcher_explains_algorithms.png
tone ai_support_fields_master.png 13_humans_make_decisions.png 94,103,103 '#17263b'

# diagnostic assistance / self-driving / NLP
frame diagnostic_assistance_master.png 14_diagnostic_assistance_wide.png
crop diagnostic_assistance_master.png 760x428+320+230 15_candidate_region_review.png
crop diagnostic_assistance_master.png 620x349+1030+80 16_doctor_patient_final_decision.png
frame self_driving_test_master.png 17_self_driving_test_transition.png
frame natural_language_processing_master.png 18_natural_language_support_transition.png

# each application changes lives
frame natural_language_processing_master.png 19_applications_change_lives_wide.png
crop natural_language_processing_master.png 760x428+0+140 20_speech_translation_assistance.png
crop natural_language_processing_master.png 700x394+900+200 21_human_summary_correction.png

# industry automation and changing labor
frame automation_labor_master.png 22_automation_industry_wide.png
crop automation_labor_master.png 760x428+0+120 23_collaborative_robot_cells.png
crop automation_labor_master.png 620x349+620+300 24_maintenance_new_roles.png
crop automation_labor_master.png 760x428+880+250 25_worker_retraining.png

# rapid progress and serious risks
frame privacy_jobs_misinformation_master.png 26_rapid_progress_risk_wide.png
crop privacy_jobs_misinformation_master.png 620x349+0+220 27_consent_and_data_cabinet.png
crop privacy_jobs_misinformation_master.png 700x394+600+230 28_worker_role_anxiety.png

# privacy, job loss, misinformation
crop privacy_jobs_misinformation_master.png 560x315+0+180 29_privacy_risk_close.png
crop privacy_jobs_misinformation_master.png 620x349+300+180 30_sealed_data_access.png
crop privacy_jobs_misinformation_master.png 650x366+620+240 31_job_change_training.png
crop privacy_jobs_misinformation_master.png 620x349+1030+160 32_misinformation_image_comparison.png
crop privacy_jobs_misinformation_master.png 650x366+930+250 33_fact_check_team.png
crop privacy_jobs_misinformation_master.png 680x383+900+80 34_recommendation_review.png
crop privacy_jobs_misinformation_master.png 560x315+1080+260 35_student_traces_risks.png
tone privacy_jobs_misinformation_master.png 36_risks_require_response.png 88,103,102 '#241d35'

# society faces consequences
frame consequences_society_master.png 37_society_roundtable_wide.png
crop consequences_society_master.png 860x484+430+300 38_evidence_and_consequences.png

# who bears responsibility for an algorithm
frame algorithm_responsibility_master.png 39_responsibility_review_wide.png
crop algorithm_responsibility_master.png 900x506+400+120 40_distributed_actors.png
crop algorithm_responsibility_master.png 900x506+350+360 41_decision_records.png

# self-driving accident accountability in court
frame self_driving_accident_court_master.png 42_accident_court_wide.png
crop self_driving_accident_court_master.png 760x428+520+300 43_damaged_sensor_and_road_model.png
crop self_driving_accident_court_master.png 760x428+850+150 44_expert_and_parties_accountability.png

# unanswered questions
frame unanswered_questions_master.png 45_unanswered_questions_wide.png
crop unanswered_questions_master.png 860x484+350+340 46_blank_evidence_objects.png
crop unanswered_questions_master.png 700x394+450+120 47_researcher_student_think.png

# governments develop regulations
frame government_regulations_master.png 48_regulations_hearing_wide.png
crop government_regulations_master.png 760x428+0+250 49_public_officials_and_citizens.png
crop government_regulations_master.png 760x428+500+350 50_four_risk_folders.png
crop government_regulations_master.png 700x394+600+20 51_technical_evidence_table.png

# EU comprehensive risk-based AI law
frame eu_ai_act_master.png 52_eu_ai_act_wide.png
crop eu_ai_act_master.png 780x439+0+250 53_european_committee.png
crop eu_ai_act_master.png 700x394+480+350 54_risk_based_folders.png
crop eu_ai_act_master.png 760x428+760+80 55_conformity_testing.png
tone eu_ai_act_master.png 56_phased_implementation.png 94,102,102 '#202943'

# technology itself and human values
frame unanswered_questions_master.png 57_technology_tool_wide.png
crop ai_progress_data_master.png 720x405+420+220 58_workstation_without_personality.png
crop unanswered_questions_master.png 760x428+300+330 59_design_data_use_choices.png
tone unanswered_questions_master.png 60_neutral_claim_needs_context.png 88,103,102 '#18233a'

# ethical purpose depends on human judgment
frame human_judgment_final_master.png 61_ethical_judgment_wide.png
crop human_judgment_final_master.png 850x478+350+330 62_compare_ai_output_evidence.png
crop human_judgment_final_master.png 650x366+480+170 63_student_leads_discussion.png

# AI helps humans think better, not think in their place
frame human_judgment_final_master.png 64_human_judgment_final_wide.png
crop human_judgment_final_master.png 620x349+780+160 65_physician_checks_sources.png
crop human_judgment_final_master.png 620x349+1030+310 66_technician_checks_sensor.png
crop human_judgment_final_master.png 620x349+1010+130 67_public_official_listens.png
crop human_judgment_final_master.png 700x394+380+300 68_student_revises_plan.png
tone human_judgment_final_master.png 69_think_better_together.png 94,104,104 '#15243a'

expected=("$OUT"/[0-9][0-9]_*.png)
test ${#expected[@]} -eq 69
for file in $expected; do
  test -s "$file"
done
echo "H051 final_style01 files verified: ${#expected[@]}"
