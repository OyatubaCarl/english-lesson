#!/bin/zsh
set -euo pipefail

ROOT="${0:A:h:h}"
REF="$ROOT/H045/scenes/character_refs"
OUT="$ROOT/H045/scenes/final_style01"
mkdir -p "$OUT"

frame() { cp "$REF/$1" "$OUT/$2"; }
crop() {
  magick "$REF/$1" -crop "$2" +repage \
    -resize '1672x941^' -gravity center -extent 1672x941 "$OUT/$3"
}
tone() {
  magick "$REF/$1" -modulate "$3" -fill "$4" -colorize 8% "$OUT/$2"
}

# ギザの三大ピラミッド：舞台と規模差
frame giza_three_pyramids_master.png 01_giza_dawn_wide.png
crop giza_three_pyramids_master.png 900x506+0+80 02_khufu_largest.png
crop giza_three_pyramids_master.png 820x461+500+110 03_khafre_higher_ground.png
crop giza_three_pyramids_master.png 700x394+950+170 04_menkaure_smaller.png
crop giza_three_pyramids_master.png 920x518+180+300 05_people_beneath_pyramids.png
crop giza_three_pyramids_master.png 760x428+40+250 06_weathered_limestone_steps.png
tone giza_three_pyramids_master.png 07_giza_blue_amber_transition.png 91,103,102 '#17243a'

# クフ王の大ピラミッド：高さと量感
frame khufu_scale_master.png 08_khufu_scale_wide.png
crop khufu_scale_master.png 780x439+430+0 09_khufu_apex_from_base.png
crop khufu_scale_master.png 820x461+650+170 10_massive_corner_courses.png
crop khufu_scale_master.png 700x394+760+300 11_weathered_block_faces.png
crop khufu_scale_master.png 720x405+0+300 12_archaeologists_at_base.png
crop khufu_scale_master.png 840x473+350+300 13_human_scale_against_stone.png
tone khufu_scale_master.png 14_four_thousand_year_scale.png 90,102,102 '#3d2c20'

# 完成当時：地元石灰岩の核とトゥーラ産外装石
frame original_casing_master.png 15_original_casing_wide.png
crop original_casing_master.png 820x461+760+260 16_white_tura_casing.png
crop original_casing_master.png 820x461+500+120 17_core_and_casing_boundary.png
crop original_casing_master.png 720x405+900+350 18_fitted_casing_seams.png
crop original_casing_master.png 760x428+0+330 19_masons_beside_casing_blocks.png
crop original_casing_master.png 900x506+500+0 20_upper_core_construction.png
crop original_casing_master.png 700x394+710+0 21_unfinished_apex_no_gold.png
tone original_casing_master.png 22_pyramid_completion_transition.png 94,101,100 '#5a462e'

# 採石：測量・切り出し・粗整形
frame local_quarry_master.png 23_local_quarry_wide.png
crop local_quarry_master.png 860x484+430+120 24_survey_and_mark_block.png
crop local_quarry_master.png 760x428+330+250 25_large_local_block.png
crop local_quarry_master.png 620x349+360+300 26_mallet_and_chisel_hands.png
crop local_quarry_master.png 720x405+850+270 27_wooden_levers_and_crew.png
crop local_quarry_master.png 760x428+900+60 28_quarry_face_work_team.png
crop local_quarry_master.png 700x394+0+250 29_rough_shaping_station.png
tone local_quarry_master.png 30_millions_of_blocks_transition.png 95,100,99 '#5b4934'

# トゥーラ産石灰岩の水運と荷下ろし
frame tura_transport_master.png 31_tura_harbor_wide.png
crop tura_transport_master.png 900x506+0+230 32_limestone_cargo_boat.png
crop tura_transport_master.png 760x428+190+250 33_blocks_secured_on_boat.png
crop tura_transport_master.png 760x428+760+250 34_dock_unloading_team.png
crop tura_transport_master.png 650x366+980+320 35_transfer_to_sledge.png
crop tura_transport_master.png 900x506+350+0 36_canal_and_distant_pyramids.png
crop tura_transport_master.png 700x394+930+80 37_harbor_logistics_and_support.png
tone tura_transport_master.png 38_nile_logistics_transition.png 90,102,104 '#183249'

# そり・湿らせた路面・組織作業
frame sledges_and_crews_master.png 39_sledge_team_wide.png
crop sledges_and_crews_master.png 820x461+350+260 40_flat_wooden_sledge.png
crop sledges_and_crews_master.png 740x416+500+230 41_taut_rope_team.png
crop sledges_and_crews_master.png 650x366+0+300 42_water_on_prepared_path.png
crop sledges_and_crews_master.png 700x394+920+240 43_foreman_sets_cadence.png
crop sledges_and_crews_master.png 850x478+650+330 44_feet_ropes_and_wet_sand.png
crop sledges_and_crews_master.png 900x506+250+80 45_block_weight_and_teamwork.png
tone sledges_and_crews_master.png 46_skilled_crews_transition.png 94,101,100 '#4b3926'

# 建設法：傾斜路は有力、正確な形は未確定
frame ramp_construction_master.png 47_ramp_construction_wide.png
crop ramp_construction_master.png 900x506+240+250 48_low_approach_ramp.png
crop ramp_construction_master.png 720x405+380+280 49_sledge_on_earthen_ramp.png
crop ramp_construction_master.png 760x428+820+250 50_masons_and_surveyors.png
crop ramp_construction_master.png 700x394+1010+280 51_food_and_water_support.png
crop ramp_construction_master.png 900x506+520+0 52_partial_courses_and_access.png
crop ramp_construction_master.png 760x428+0+300 53_multiple_work_stages.png
tone ramp_construction_master.png 54_exact_method_still_debated.png 90,102,102 '#233548'

# 王墓を中心とする葬祭複合体
frame funerary_complex_master.png 55_funerary_complex_wide.png
crop funerary_complex_master.png 900x506+350+0 56_great_pyramid_and_mortuary_temple.png
crop funerary_complex_master.png 780x439+490+240 57_causeway_to_valley.png
crop funerary_complex_master.png 700x394+0+180 58_queens_pyramids.png
crop funerary_complex_master.png 760x428+0+340 59_mastaba_cemetery.png
crop funerary_complex_master.png 760x428+850+320 60_eastern_cemetery.png
crop funerary_complex_master.png 720x405+820+0 61_boat_pits_beside_pyramid.png
crop funerary_complex_master.png 650x366+900+520 62_valley_temple_at_water.png

# 王の間：花崗岩の石棺と墓としての建築
frame burial_chamber_master.png 63_kings_chamber_wide.png
crop burial_chamber_master.png 800x450+430+230 64_granite_sarcophagus.png
crop burial_chamber_master.png 680x383+850+150 65_offerings_in_lamplight.png
crop burial_chamber_master.png 680x383+210+120 66_plain_granite_wall_and_passage.png
crop burial_chamber_master.png 760x428+760+60 67_funeral_attendants.png
tone burial_chamber_master.png 68_royal_tomb_silence.png 86,100,103 '#241b24'

# 死後の継続と王権への信念
frame afterlife_beliefs_master.png 69_afterlife_offerings_wide.png
crop afterlife_beliefs_master.png 820x461+250+300 70_bread_vessels_and_flowers.png
crop afterlife_beliefs_master.png 720x405+250+220 71_hands_arrange_offerings.png
crop afterlife_beliefs_master.png 820x461+650+170 72_dawn_alignment_in_court.png
crop afterlife_beliefs_master.png 700x394+1000+180 73_solar_symbols_on_objects.png
tone afterlife_beliefs_master.png 74_belief_without_ghosts.png 90,103,103 '#1c293a'

# 王国の終わり後も残る石と沈黙
frame centuries_of_weathering_master.png 75_centuries_wide.png
crop centuries_of_weathering_master.png 820x461+0+120 76_moonlit_weathered_core.png
crop centuries_of_weathering_master.png 820x461+720+100 77_dawn_on_enduring_stone.png
crop centuries_of_weathering_master.png 760x428+350+260 78_lost_casing_exposed_core.png
crop centuries_of_weathering_master.png 900x506+180+300 79_people_from_passing_eras.png
tone centuries_of_weathering_master.png 80_four_thousand_year_silence.png 85,104,104 '#142239'

# 現代の非破壊調査と高校生の問い
frame modern_archaeology_silence_master.png 81_modern_archaeology_wide.png
crop modern_archaeology_silence_master.png 760x428+0+280 82_nondestructive_survey_team.png
crop modern_archaeology_silence_master.png 650x366+0+330 83_tripod_and_careful_notes.png
crop modern_archaeology_silence_master.png 760x428+850+100 84_student_listens_to_wind.png
crop modern_archaeology_silence_master.png 650x366+980+120 85_student_profile_close.png
crop modern_archaeology_silence_master.png 820x461+710+250 86_student_and_massive_blocks.png
crop modern_archaeology_silence_master.png 880x495+250+0 87_pyramid_beyond_open_questions.png
tone modern_archaeology_silence_master.png 88_survives_today_final.png 87,103,104 '#17253a'

expected=("$OUT"/[0-9][0-9]_*.png)
test ${#expected[@]} -eq 88
for file in $expected; do
  test -s "$file"
done
echo "H045 final_style01 files verified: ${#expected[@]}"
