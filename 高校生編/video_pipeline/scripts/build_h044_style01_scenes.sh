#!/bin/zsh
set -euo pipefail

ROOT="${0:A:h:h}"
REF="$ROOT/H044/scenes/character_refs"
OUT="$ROOT/H044/scenes/final_style01"
mkdir -p "$OUT"

frame() { cp "$REF/$1" "$OUT/$2"; }
crop() {
  magick "$REF/$1" -crop "$2" +repage \
    -resize '1672x941^' -gravity center -extent 1672x941 "$OUT/$3"
}
tone() {
  magick "$REF/$1" -modulate "$3" -fill "$4" -colorize 8% "$OUT/$2"
}

# サバルマティ出発：当初の78人と静かな決意
frame sabarmati_departure_master.png 01_sabarmati_departure_wide.png
crop sabarmati_departure_master.png 900x506+0+80 02_ashram_dawn.png
crop sabarmati_departure_master.png 760x428+680+40 03_leader_at_departure.png
crop sabarmati_departure_master.png 820x461+820+120 04_original_satyagrahis.png
crop sabarmati_departure_master.png 700x394+700+250 05_staff_and_first_steps.png
crop sabarmati_departure_master.png 900x506+0+0 06_first_light_over_ashram.png
tone sabarmati_departure_master.png 07_departure_resolve_transition.png 90,100,103 '#17253a'

# 約385キロ・24日間の道のり
frame long_road_journey_master.png 08_long_road_wide.png
crop long_road_journey_master.png 720x405+250+80 09_leader_walking.png
crop long_road_journey_master.png 780x439+200+250 10_dusty_feet_and_staff.png
crop long_road_journey_master.png 900x506+420+90 11_first_companions_on_road.png
crop long_road_journey_master.png 900x506+770+0 12_road_to_horizon.png
crop long_road_journey_master.png 800x450+0+30 13_village_along_route.png
crop long_road_journey_master.png 760x428+530+180 14_water_vessels_and_bundles.png
tone long_road_journey_master.png 15_many_days_transition.png 92,100,101 '#2d241d'

# 道中で参加者が増える
frame growing_march_master.png 16_growing_march_wide.png
crop growing_march_master.png 780x439+0+100 17_village_families_join.png
crop growing_march_master.png 650x366+0+230 18_spinning_wheel_support.png
crop growing_march_master.png 760x428+450+100 19_leader_and_ordered_rows.png
crop growing_march_master.png 900x506+760+0 20_thousands_recede_at_sunset.png
crop growing_march_master.png 1100x619+280+0 21_village_march_at_sunset.png

# 英国植民地の塩独占
frame salt_monopoly_master.png 22_salt_monopoly_wide.png
crop salt_monopoly_master.png 950x534+0+0 23_coastal_salt_pans.png
crop salt_monopoly_master.png 900x506+430+0 24_guarded_salt_heaps.png
crop salt_monopoly_master.png 720x405+480+110 25_locked_depot_gate.png
crop salt_monopoly_master.png 700x394+750+120 26_colonial_balance_scale.png
crop salt_monopoly_master.png 780x439+850+130 27_ledger_and_official_hands.png
crop salt_monopoly_master.png 760x428+0+190 28_workers_wait_outside.png
crop salt_monopoly_master.png 950x534+650+160 29_sacks_scales_and_control.png

# 貧しい人ほど重い塩税
frame salt_tax_poor_family_master.png 30_salt_tax_family_wide.png
crop salt_tax_poor_family_master.png 820x461+180+90 31_family_faces_at_market.png
crop salt_tax_poor_family_master.png 720x405+470+280 32_hands_count_few_coins.png
crop salt_tax_poor_family_master.png 650x366+850+220 33_small_salt_measure_on_scale.png
crop salt_tax_poor_family_master.png 900x506+260+130 34_children_and_basic_necessity.png

# ダンディで天然塩を拾う
frame dandi_salt_act_master.png 35_dandi_salt_act_wide.png
crop dandi_salt_act_master.png 980x551+0+0 36_wet_dandi_shore.png
crop dandi_salt_act_master.png 760x428+430+80 37_kneeling_at_shore.png
crop dandi_salt_act_master.png 650x366+250+110 38_handful_of_natural_salt.png
crop dandi_salt_act_master.png 820x461+800+50 39_witnesses_watch_quietly.png
crop dandi_salt_act_master.png 900x506+350+250 40_staff_wet_sand_and_salt.png
tone dandi_salt_act_master.png 41_modest_act_sunrise_transition.png 94,102,100 '#47351f'

# 武器のない規律ある抗議
frame disciplined_protest_master.png 42_nonviolent_protest_wide.png
crop disciplined_protest_master.png 900x506+0+180 43_people_make_salt_openly.png
crop disciplined_protest_master.png 700x394+200+190 44_open_empty_hands.png
crop disciplined_protest_master.png 1000x563+0+80 45_orderly_seated_protest.png
crop disciplined_protest_master.png 760x428+880+120 46_police_watch_at_distance.png
crop disciplined_protest_master.png 900x506+600+50 47_calm_marchers_face_authority.png
tone disciplined_protest_master.png 48_discipline_without_weapons.png 90,100,102 '#203040'

# 海岸とは別時点の逮捕
frame gandhi_arrest_master.png 49_arrest_room_wide.png
crop gandhi_arrest_master.png 720x405+530+50 50_calm_leader_at_arrest.png
crop gandhi_arrest_master.png 650x366+580+170 51_open_hands_and_shawl.png
crop gandhi_arrest_master.png 760x428+870+60 52_officers_wait_in_doorway.png
crop gandhi_arrest_master.png 720x405+670+280 53_staff_and_papers_left_behind.png
crop gandhi_arrest_master.png 900x506+0+160 54_companions_witness_predawn.png

# 長い運動と1947年の独立
frame independence_movement_master.png 55_independence_movement_wide.png
crop independence_movement_master.png 1000x563+0+100 56_diverse_citizens_and_organizers.png
crop independence_movement_master.png 820x461+0+230 57_women_workers_and_students.png
crop independence_movement_master.png 900x506+420+0 58_independence_sunrise.png
crop independence_movement_master.png 900x506+700+300 59_staff_sandals_and_salt_memory.png
crop independence_movement_master.png 800x450+850+280 60_documents_of_long_movement.png

# 後年、キング牧師が非暴力の方法を学ぶ
frame king_studies_gandhi_master.png 61_civil_rights_study_wide.png
crop king_studies_gandhi_master.png 760x428+0+80 62_young_organizer_studies.png
crop king_studies_gandhi_master.png 820x461+520+170 63_india_map_and_salt_march_photo.png
crop king_studies_gandhi_master.png 850x478+300+280 64_books_notes_and_fountain_pen.png
crop king_studies_gandhi_master.png 700x394+940+80 65_boycott_planning_in_next_room.png

# 世界の運動が各地の文脈で教訓を受け継ぐ
frame global_justice_legacy_master.png 66_global_justice_legacy_wide.png
crop global_justice_legacy_master.png 700x394+900+120 67_modern_student_reflects.png
crop global_justice_legacy_master.png 850x478+350+300 68_staff_salt_sandals_and_footprints.png
crop global_justice_legacy_master.png 650x366+0+0 69_american_civil_rights_panel.png
crop global_justice_legacy_master.png 800x450+430+0 70_global_sit_in_panels.png
crop global_justice_legacy_master.png 700x394+850+0 71_women_and_students_panel.png
crop global_justice_legacy_master.png 1000x563+500+110 72_illuminated_footsteps_final.png
crop global_justice_legacy_master.png 900x506+0+220 73_walking_staff_and_salt_legacy.png
crop global_justice_legacy_master.png 700x394+780+250 74_student_and_footsteps_close.png
tone global_justice_legacy_master.png 75_legacy_gallery_twilight.png 88,102,102 '#17243a'
crop global_justice_legacy_master.png 1200x675+300+0 76_student_faces_global_history.png

expected=(
  01_sabarmati_departure_wide.png 02_ashram_dawn.png
  03_leader_at_departure.png 04_original_satyagrahis.png
  05_staff_and_first_steps.png 06_first_light_over_ashram.png
  07_departure_resolve_transition.png 08_long_road_wide.png
  09_leader_walking.png 10_dusty_feet_and_staff.png
  11_first_companions_on_road.png 12_road_to_horizon.png
  13_village_along_route.png 14_water_vessels_and_bundles.png
  15_many_days_transition.png 16_growing_march_wide.png
  17_village_families_join.png 18_spinning_wheel_support.png
  19_leader_and_ordered_rows.png 20_thousands_recede_at_sunset.png
  21_village_march_at_sunset.png 22_salt_monopoly_wide.png
  23_coastal_salt_pans.png 24_guarded_salt_heaps.png
  25_locked_depot_gate.png 26_colonial_balance_scale.png
  27_ledger_and_official_hands.png 28_workers_wait_outside.png
  29_sacks_scales_and_control.png 30_salt_tax_family_wide.png
  31_family_faces_at_market.png 32_hands_count_few_coins.png
  33_small_salt_measure_on_scale.png 34_children_and_basic_necessity.png
  35_dandi_salt_act_wide.png 36_wet_dandi_shore.png
  37_kneeling_at_shore.png 38_handful_of_natural_salt.png
  39_witnesses_watch_quietly.png 40_staff_wet_sand_and_salt.png
  41_modest_act_sunrise_transition.png 42_nonviolent_protest_wide.png
  43_people_make_salt_openly.png 44_open_empty_hands.png
  45_orderly_seated_protest.png 46_police_watch_at_distance.png
  47_calm_marchers_face_authority.png 48_discipline_without_weapons.png
  49_arrest_room_wide.png 50_calm_leader_at_arrest.png
  51_open_hands_and_shawl.png 52_officers_wait_in_doorway.png
  53_staff_and_papers_left_behind.png 54_companions_witness_predawn.png
  55_independence_movement_wide.png 56_diverse_citizens_and_organizers.png
  57_women_workers_and_students.png 58_independence_sunrise.png
  59_staff_sandals_and_salt_memory.png 60_documents_of_long_movement.png
  61_civil_rights_study_wide.png 62_young_organizer_studies.png
  63_india_map_and_salt_march_photo.png 64_books_notes_and_fountain_pen.png
  65_boycott_planning_in_next_room.png 66_global_justice_legacy_wide.png
  67_modern_student_reflects.png 68_staff_salt_sandals_and_footprints.png
  69_american_civil_rights_panel.png 70_global_sit_in_panels.png
  71_women_and_students_panel.png 72_illuminated_footsteps_final.png
  73_walking_staff_and_salt_legacy.png 74_student_and_footsteps_close.png
  75_legacy_gallery_twilight.png 76_student_faces_global_history.png
)
for file in $expected; do
  test -s "$OUT/$file"
done
echo "H044 final_style01 files verified: ${#expected[@]}"
