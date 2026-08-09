#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REF="$ROOT/H057/scenes/character_refs"
OUT="$ROOT/H057/scenes/final_style01"
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

# 1856年Smiljan。現在のCroatiaと当時の領域を国旗で単純化しない
frame smiljan_birth_master.png 001_smiljan_valley_wide.png
crop smiljan_birth_master.png 760x428+0+150 002_church_after_rain.png
crop smiljan_birth_master.png 720x405+430+120 003_tesla_family_home.png
crop smiljan_birth_master.png 720x405+900+150 004_warm_doorway_family.png
crop smiljan_birth_master.png 620x349+820+310 005_newborn_nikola.png
crop smiljan_birth_master.png 660x371+650+230 006_priest_father_and_mother.png
crop smiljan_birth_master.png 680x383+980+230 007_siblings_gather.png
tone smiljan_birth_master.png 008_dawn_over_smiljan.png 103,103,102 '#334766'

frame smiljan_birth_master.png 009_smiljan_birth_scene_wide.png
crop smiljan_birth_master.png 600x338+850+330 010_newborn_in_mothers_arms.png
crop smiljan_birth_master.png 620x349+650+260 011_father_blesses_child.png
crop smiljan_birth_master.png 920x518+350+130 012_family_and_church.png
tone smiljan_birth_master.png 013_birth_in_modern_croatia_historic_land.png 105,103,101 '#60442f'

# 1884年の移住。現代の港・移民手続を入れない
frame immigrant_arrival_master.png 014_new_york_harbor_1884_wide.png
crop immigrant_arrival_master.png 760x428+0+140 015_steamship_and_docks.png
crop immigrant_arrival_master.png 720x405+440+130 016_immigrant_tesla_arrives.png
crop immigrant_arrival_master.png 650x366+420+360 017_one_small_case.png
crop immigrant_arrival_master.png 620x349+720+330 018_folded_technical_sketch.png
crop immigrant_arrival_master.png 620x349+500+130 019_uncertain_first_step.png
crop immigrant_arrival_master.png 760x428+850+120 020_period_manhattan_waterfront.png
crop immigrant_arrival_master.png 900x506+60+180 021_immigrant_among_many_arrivals.png
tone immigrant_arrival_master.png 022_inventor_looks_toward_city.png 104,103,101 '#5b4939'

# Teslaの実用的AC induction motorとpolyphase system
frame ac_induction_motor_master.png 023_ac_motor_workshop_wide.png
crop ac_induction_motor_master.png 720x405+430+100 024_tesla_explains_rotating_field.png
crop ac_induction_motor_master.png 820x461+0+300 025_engineers_measure_motor.png
crop ac_induction_motor_master.png 760x428+760+180 026_westinghouse_reviews_patent.png

# DCとACの競争を二人だけの決闘にしない
frame current_war_engineering_master.png 027_current_war_meeting_wide.png
crop current_war_engineering_master.png 720x405+0+150 028_edison_and_dc_engineers.png
crop current_war_engineering_master.png 760x428+180+350 029_dc_local_distribution_model.png
crop current_war_engineering_master.png 760x428+760+120 030_tesla_and_westinghouse_team.png
crop current_war_engineering_master.png 680x383+820+300 031_transformer_coils.png
crop current_war_engineering_master.png 820x461+380+300 032_long_distance_route_model.png
crop current_war_engineering_master.png 720x405+430+120 033_city_officials_compare_costs.png
tone current_war_engineering_master.png 034_engineers_discuss_safety.png 101,103,102 '#41465a'
frame chicago_exposition_master.png 035_chicago_exposition_wide.png
crop chicago_exposition_master.png 820x461+350+0 036_thousands_of_lamps.png
crop chicago_exposition_master.png 720x405+900+220 037_protected_ac_switchgear.png
tone chicago_exposition_master.png 038_team_lights_the_fair.png 106,104,101 '#704b2c'

# 1896年Niagaraと現代gridを分ける
frame niagara_power_master.png 039_niagara_powerhouse_wide.png
crop niagara_power_master.png 760x428+0+350 040_water_drives_generators.png
crop niagara_power_master.png 720x405+900+320 041_analog_control_gallery.png
crop niagara_power_master.png 700x394+420+190 042_tesla_and_westinghouse_with_team.png
crop niagara_power_master.png 650x366+1000+20 043_early_wooden_power_poles.png
tone niagara_power_master.png 044_power_toward_buffalo.png 102,104,103 '#344665'
frame modern_ac_dc_grid_master.png 045_modern_grid_wide.png
crop modern_ac_dc_grid_master.png 720x405+900+150 046_student_and_grid_engineer.png
crop modern_ac_dc_grid_master.png 720x405+0+260 047_transformer_and_substation.png
crop modern_ac_dc_grid_master.png 720x405+820+320 048_solar_battery_and_inverter.png
tone modern_ac_dc_grid_master.png 049_ac_grid_and_dc_devices.png 106,104,101 '#765238'

# 高周波、wireless、radio-controlled boat、radarに連なる未完成構想
frame high_frequency_lab_master.png 050_high_frequency_lab_wide.png
crop high_frequency_lab_master.png 700x394+0+220 051_tesla_at_safe_controls.png
crop high_frequency_lab_master.png 760x428+700+100 052_coil_and_fixed_arcs.png
crop high_frequency_lab_master.png 700x394+850+300 053_glowing_discharge_tubes.png
frame radio_controlled_boat_master.png 054_radio_boat_demo_wide.png
crop radio_controlled_boat_master.png 700x394+820+150 055_tesla_operates_control_box.png
crop radio_controlled_boat_master.png 760x428+0+320 056_unmanned_boat_turns.png
crop radio_controlled_boat_master.png 700x394+900+350 057_receiver_and_rudder.png
frame radar_precursor_concept_master.png 058_reflection_concept_wide.png
crop radar_precursor_concept_master.png 760x428+0+100 059_transmitter_target_receiver.png
tone radar_precursor_concept_master.png 060_faint_return_on_galvanometer.png 99,102,103 '#32435d'

# Wardenclyffeのvision、建設、資金停止、技術的未完成
frame wardenclyffe_construction_master.png 061_wardenclyffe_construction_wide.png
crop wardenclyffe_construction_master.png 720x405+0+160 062_brick_lab_and_tower.png
crop wardenclyffe_construction_master.png 760x428+420+200 063_tesla_engineers_and_plans.png
crop wardenclyffe_construction_master.png 720x405+900+200 064_timber_and_cables.png
tone wardenclyffe_construction_master.png 065_world_wireless_unfinished.png 104,103,101 '#654a34'
frame wardenclyffe_funding_collapse_master.png 066_funding_meeting_wide.png
crop wardenclyffe_funding_collapse_master.png 720x405+350+320 067_rising_cost_ledger.png
crop wardenclyffe_funding_collapse_master.png 680x383+760+330 068_competing_wireless_news.png
crop wardenclyffe_funding_collapse_master.png 620x349+0+390 069_empty_payroll_box.png
crop wardenclyffe_funding_collapse_master.png 720x405+0+80 070_workers_cover_machinery.png
crop wardenclyffe_funding_collapse_master.png 650x366+0+0 071_silent_unpowered_tower.png
crop wardenclyffe_funding_collapse_master.png 900x506+330+190 072_multiple_causes_not_betrayal.png
tone wardenclyffe_funding_collapse_master.png 073_project_stops_in_mist.png 94,100,104 '#29384d'

# patents、生前の評価、財政の縮小、1943年の死を尊厳を保って描く
frame final_hotel_years_master.png 074_hotel_room_wide.png
crop final_hotel_years_master.png 720x405+0+300 075_patent_folders.png
crop final_hotel_years_master.png 620x349+120+430 076_old_medal_and_awards.png
crop final_hotel_years_master.png 760x428+350+330 077_bills_and_correspondence.png
crop final_hotel_years_master.png 680x383+450+160 078_elderly_tesla_at_desk.png
crop final_hotel_years_master.png 620x349+530+80 079_same_face_across_years.png
crop final_hotel_years_master.png 620x349+1050+100 080_attendant_respects_privacy.png
crop final_hotel_years_master.png 650x366+0+0 081_snowy_manhattan_outside.png
tone final_hotel_years_master.png 082_life_ends_without_spectacle.png 97,101,103 '#2c3b53'
crop chicago_exposition_master.png 760x428+350+160 083_recognition_before_death.png
crop high_frequency_lab_master.png 820x461+300+150 084_public_science_demonstration.png
crop final_hotel_years_master.png 820x461+100+300 085_patents_and_medal.png
frame modern_legacy_museum_master.png 086_later_museum_recognition.png
tone modern_legacy_museum_master.png 087_legacy_spreads_over_time.png 104,103,101 '#5f4936'

# 現代の名と技術。EVをTesla本人の発明にしない
frame modern_legacy_museum_master.png 088_modern_museum_wide.png
crop modern_legacy_museum_master.png 720x405+0+300 089_student_studies_ac_motor.png
crop modern_legacy_museum_master.png 720x405+620+160 090_curator_explains_many_contributors.png
crop modern_legacy_museum_master.png 700x394+500+330 091_wardenclyffe_model.png
crop modern_legacy_museum_master.png 680x383+980+350 092_radio_boat_model.png
crop modern_legacy_museum_master.png 700x394+950+60 093_coil_and_transformers.png
crop modern_legacy_museum_master.png 760x428+500+0 094_patent_records_and_portrait.png
crop modern_legacy_museum_master.png 720x405+0+80 095_electric_cars_outside.png
crop modern_legacy_museum_master.png 800x450+0+0 096_renewable_grid_beyond_glass.png
crop modern_legacy_museum_master.png 700x394+450+180 097_student_reads_engineering_history.png
crop modern_legacy_museum_master.png 900x506+350+160 098_name_and_ideas_carry_forward.png
tone modern_legacy_museum_master.png 099_future_built_by_many.png 107,104,101 '#735038'
tone modern_legacy_museum_master.png 100_teslas_dream_within_our_world.png 110,105,100 '#805a37'

count=$(find "$OUT" -type f -name '[0-9][0-9][0-9]_*.png' | wc -l | tr -d ' ')
test "$count" -eq 100
for file in "$OUT"/[0-9][0-9][0-9]_*.png; do
  test -s "$file"
done
echo "H057 final_style01 files verified: $count"
