#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REF="$ROOT/H056/scenes/character_refs"
OUT="$ROOT/H056/scenes/final_style01"
mkdir -p "$OUT"

frame() {
  test -s "$OUT/$2" || cp "$REF/$1" "$OUT/$2"
}
crop() {
  if ! test -s "$OUT/$3"; then
    magick "$REF/$1" -crop "$2" +repage \
      -resize '1672x941^' -gravity center -extent 1672x941 "$OUT/$3"
  fi
}
tone() {
  if ! test -s "$OUT/$2"; then
    magick "$REF/$1" -modulate "$3" -fill "$4" -colorize 7% "$OUT/$2"
  fi
}

# 民主主義の街と独立した報道機関を、政府の一部ではなく社会の外側から描く
frame democratic_fourth_estate_master.png 01_democratic_city_and_newsroom_wide.png
crop democratic_fourth_estate_master.png 760x428+0+170 02_civic_institutions_beyond_the_window.png
crop democratic_fourth_estate_master.png 720x405+400+170 03_student_reads_multiple_reports.png
crop democratic_fourth_estate_master.png 700x394+860+150 04_editor_checks_public_records.png
crop democratic_fourth_estate_master.png 650x366+180+300 05_printed_sources_on_the_desk.png
crop democratic_fourth_estate_master.png 720x405+650+120 06_newsroom_serves_the_public.png
tone democratic_fourth_estate_master.png 07_independent_press_at_dawn.png 103,103,102 '#45506b'
frame pillars_and_citizens_master.png 08_citizens_and_public_institutions_wide.png

# fourth estateは国家の第四部門ではなく、社会を支える比喩
crop pillars_and_citizens_master.png 760x428+0+170 09_legislative_chamber_observed.png
crop pillars_and_citizens_master.png 760x428+450+130 10_administration_and_public_records.png
crop pillars_and_citizens_master.png 720x405+900+170 11_citizen_reads_with_care.png
tone pillars_and_citizens_master.png 12_press_outside_the_three_branches.png 101,103,103 '#3e4e68'

# 立法・行政・司法と市民の間にある監視と情報の流れ
frame pillars_and_citizens_master.png 13_public_institutions_and_newsroom.png
crop pillars_and_citizens_master.png 680x383+40+110 14_legislative_process_in_public.png
crop pillars_and_citizens_master.png 680x383+500+120 15_administrative_office_and_records.png
crop pillars_and_citizens_master.png 680x383+930+120 16_judicial_hall_and_due_process.png
crop pillars_and_citizens_master.png 620x349+40+390 17_journalist_between_institutions.png
crop pillars_and_citizens_master.png 650x366+560+350 18_students_compare_public_information.png
crop pillars_and_citizens_master.png 620x349+1010+370 19_citizen_questions_and_participates.png
tone pillars_and_citizens_master.png 20_pillars_support_society_together.png 104,103,101 '#544a3b'

# governmentとbusinessのwrongdoingを、記録・現場・複数sourceでrevealする
frame investigative_journalists_master.png 21_investigative_newsroom_wide.png
crop investigative_journalists_master.png 720x405+0+170 22_female_reporter_reads_public_record.png
crop investigative_journalists_master.png 680x383+390+170 23_editor_compares_evidence.png
crop investigative_journalists_master.png 720x405+850+150 24_second_reporter_checks_business_file.png
crop investigative_journalists_master.png 680x383+200+330 25_notebook_camera_and_documents.png
tone investigative_journalists_master.png 26_verified_findings_for_citizens.png 102,103,102 '#38465b'

# investigative reportingは編集・反論機会・社会の応答へつなぐ
frame verification_and_editorial_review_master.png 27_editorial_review_wide.png
crop verification_and_editorial_review_master.png 720x405+0+180 28_multiple_sources_are_compared.png
crop verification_and_editorial_review_master.png 700x394+450+160 29_editor_questions_the_evidence.png
crop verification_and_editorial_review_master.png 700x394+900+160 30_subject_response_is_considered.png
frame investigative_report_public_response_master.png 31_public_hearing_after_reporting.png
crop investigative_report_public_response_master.png 820x461+120+180 32_citizens_and_officials_respond.png
tone investigative_report_public_response_master.png 33_reporting_can_trigger_change.png 104,103,101 '#574634'

# 1972年Watergate。記者二人だけの英雄譚にせず裏取りから始める
frame watergate_newsroom_master.png 34_watergate_newsroom_1972_wide.png
crop watergate_newsroom_master.png 760x428+0+160 35_dark_haired_reporter_at_typewriter.png
crop watergate_newsroom_master.png 720x405+450+150 36_two_reporters_compare_notes.png
crop watergate_newsroom_master.png 700x394+900+150 37_rotary_phone_and_editor.png
frame watergate_sources_evidence_master.png 38_public_records_workspace_wide.png
crop watergate_sources_evidence_master.png 760x428+0+160 39_first_reporter_checks_document.png
crop watergate_sources_evidence_master.png 720x405+470+150 40_second_reporter_and_editor_crosscheck.png
crop watergate_sources_evidence_master.png 680x383+900+180 41_rotary_phone_and_record_boxes.png
crop watergate_sources_evidence_master.png 760x428+250+320 42_notes_sources_and_corroboration.png
frame watergate_institutions_resignation_master.png 43_government_corridor_1974_wide.png
crop watergate_institutions_resignation_master.png 720x405+0+180 44_resignation_letter_enters_process.png
crop watergate_institutions_resignation_master.png 720x405+480+120 45_clerks_reporters_and_records.png
crop watergate_institutions_resignation_master.png 720x405+900+120 46_public_hearing_and_due_process.png
tone watergate_institutions_resignation_master.png 47_many_institutions_reach_accountability.png 102,103,102 '#534536'

# 現代の情報のreliabilityを、日付・場所・原資料の照合として描く
frame accountable_authority_master.png 48_accountability_hearing_wide.png
crop accountable_authority_master.png 720x405+0+170 49_auditor_reviews_verified_records.png
crop accountable_authority_master.png 760x428+500+150 50_reporter_presents_evidence_calmly.png
crop accountable_authority_master.png 700x394+920+150 51_authority_answers_in_public.png
frame modern_information_reliability_master.png 52_verification_desk_at_blue_hour.png
crop modern_information_reliability_master.png 720x405+0+170 53_editor_compares_old_photograph.png
crop modern_information_reliability_master.png 720x405+450+170 54_fact_checker_traces_date_and_place.png
crop modern_information_reliability_master.png 700x394+920+150 55_student_observes_verification.png
crop modern_information_reliability_master.png 800x450+300+320 56_map_archive_and_contact_sheets.png
tone modern_information_reliability_master.png 57_unverified_claim_waits_for_evidence.png 98,102,104 '#2e405f'

# deliberate disinformationと、文脈を戻す検証
frame disinformation_spread_master.png 58_old_image_spreads_without_context.png
crop disinformation_spread_master.png 720x405+0+170 59_students_react_to_their_phones.png
crop disinformation_spread_master.png 720x405+430+150 60_student_pauses_before_sharing.png
crop disinformation_spread_master.png 720x405+900+150 61_librarian_traces_original_image.png
crop disinformation_spread_master.png 820x461+360+310 62_archive_map_and_original_context.png
tone disinformation_spread_master.png 63_correction_restores_context.png 104,103,101 '#594633'

# 架空の独裁体制。censorshipと拘束を暴力的に誇張しない
frame censorship_imprisonment_master.png 64_censorship_visiting_room_wide.png
crop censorship_imprisonment_master.png 720x405+0+170 65_family_and_lawyer_make_contact.png
crop censorship_imprisonment_master.png 700x394+460+150 66_journalist_speaks_through_glass.png
crop censorship_imprisonment_master.png 650x366+970+130 67_guard_keeps_formal_distance.png
crop censorship_imprisonment_master.png 760x428+0+40 68_rain_over_closed_newsroom.png
crop censorship_imprisonment_master.png 720x405+350+70 69_shutter_descends_on_printing_room.png
crop censorship_imprisonment_master.png 700x394+80+350 70_citizens_notice_newsroom_closure.png
crop censorship_imprisonment_master.png 720x405+500+300 71_legal_notes_and_family_support.png
crop censorship_imprisonment_master.png 700x394+900+260 72_journalist_remains_composed.png
tone censorship_imprisonment_master.png 73_press_freedom_is_not_guaranteed.png 94,99,104 '#263950'

# 受け手の責任。原source・日付・場所・複数報道・訂正を確認する
frame media_literacy_student_master.png 74_media_literacy_library_wide.png
crop media_literacy_student_master.png 720x405+0+170 75_classmates_compare_independent_reports.png
crop media_literacy_student_master.png 720x405+430+150 76_student_traces_claim_to_source.png
crop media_literacy_student_master.png 720x405+900+150 77_librarian_guides_without_dictating.png
crop media_literacy_student_master.png 760x428+280+320 78_date_place_context_and_evidence.png
crop media_literacy_student_master.png 680x383+760+300 79_correction_slip_and_archive.png
crop media_literacy_student_master.png 650x366+480+180 80_student_makes_his_own_judgment.png
tone media_literacy_student_master.png 81_reliable_source_requires_patient_checking.png 105,103,101 '#62482f'

# press freedomを、市民全員が考え話し参加できる自由として結ぶ
frame press_freedom_final_master.png 82_open_community_discussion_wide.png
crop press_freedom_final_master.png 720x405+0+170 83_parent_and_child_listen.png
crop press_freedom_final_master.png 700x394+340+160 84_student_enters_the_circle.png
crop press_freedom_final_master.png 720x405+650+160 85_elected_official_answers_questions.png
crop press_freedom_final_master.png 700x394+970+170 86_wheelchair_user_has_equal_voice.png
crop press_freedom_final_master.png 720x405+850+30 87_local_newsroom_remains_open.png
crop press_freedom_final_master.png 760x428+180+300 88_generations_listen_to_each_other.png
tone press_freedom_final_master.png 89_freedom_belongs_to_every_citizen.png 107,104,101 '#704e31'
tone press_freedom_final_master.png 90_protecting_press_freedom_protects_our_own.png 110,105,100 '#7a5633'

count=$(find "$OUT" -type f -name '[0-9][0-9]_*.png' | wc -l | tr -d ' ')
test "$count" -eq 90
for file in "$OUT"/[0-9][0-9]_*.png; do
  test -s "$file"
done
echo "H056 final_style01 files verified: $count"
