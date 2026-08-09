#!/bin/zsh
set -euo pipefail

ROOT="${0:A:h:h}"
REF="$ROOT/H043/scenes/character_refs"
OUT="$ROOT/H043/scenes/final_style01"
mkdir -p "$OUT"

frame() { cp "$REF/$1" "$OUT/$2"; }
crop() {
  magick "$REF/$1" -crop "$2" +repage \
    -resize '1672x941^' -gravity center -extent 1672x941 "$OUT/$3"
}
tone() {
  magick "$REF/$1" -modulate "$3" -fill "$4" -colorize 8% "$OUT/$2"
}

# カーソンの海洋生物学と執筆
frame carson_writer_master.png 01_carson_writer_wide.png
crop carson_writer_master.png 780x439+80+40 02_coastal_marsh_window.png
crop carson_writer_master.png 760x428+520+80 03_carson_scientist_writer.png
crop carson_writer_master.png 980x551+430+250 04_bird_fish_research_notes.png

# 1962年の出版
frame silent_spring_publication_master.png 05_publication_office_wide.png
crop silent_spring_publication_master.png 760x428+480+100 06_carson_first_copy.png
crop silent_spring_publication_master.png 900x506+620+180 07_editors_and_proofs.png
crop silent_spring_publication_master.png 650x366+520+170 08_unlettered_bird_cover.png
crop carson_writer_master.png 720x405+520+250 09_writing_to_publication_link.png
tone silent_spring_publication_master.png 10_publication_team_transition.png 92,101,102 '#19263a'

# 1950年代のDDT大量使用
frame ddt_widespread_use_master.png 11_ddt_use_wide.png
crop ddt_widespread_use_master.png 1100x619+0+20 12_drifting_spray_over_fields.png
crop ddt_widespread_use_master.png 850x478+0+20 13_period_crop_duster.png
crop ddt_widespread_use_master.png 900x506+700+170 14_ground_mixing_crew.png
crop ddt_widespread_use_master.png 820x461+0+290 15_drainage_ditch_beside_field.png
crop ddt_widespread_use_master.png 1200x675+180+120 16_cotton_field_mist.png
tone ddt_widespread_use_master.png 17_insects_and_drift_transition.png 90,100,102 '#243147'

# 持続性と生物濃縮を調べる
frame food_web_biomagnification_master.png 18_food_web_field_station_wide.png
crop food_web_biomagnification_master.png 820x461+820+250 19_eggshell_and_tissue_samples.png
crop food_web_biomagnification_master.png 900x506+0+130 20_marsh_stream_and_osprey.png
crop food_web_biomagnification_master.png 1050x591+450+220 21_water_insect_fish_egg_sequence.png
crop food_web_biomagnification_master.png 760x428+560+260 22_fish_specimen_measurement.png
crop food_web_biomagnification_master.png 700x394+900+250 23_fragile_eggshell_sample.png
crop food_web_biomagnification_master.png 650x366+0+0 24_osprey_nest_above_marsh.png
crop food_web_biomagnification_master.png 1050x591+350+100 25_field_biologists_compare_evidence.png

# 鳥の歌が消える可能性という警告
frame silent_orchard_warning_master.png 26_silent_spring_orchard_wide.png
crop silent_orchard_warning_master.png 1250x703+180+0 27_empty_nests_in_blossom.png
crop silent_orchard_warning_master.png 820x461+430+230 28_still_birdbath_and_empty_sky.png

# 市民の意識が広がる
frame public_awareness_master.png 29_public_awareness_library_wide.png
crop public_awareness_master.png 850x478+0+220 30_readers_share_the_book.png
crop public_awareness_master.png 980x551+650+130 31_letters_scientists_and_reporters.png

# 産業界による批判は言葉と資料の対立で描く
frame industry_criticism_master.png 32_industry_criticism_wide.png
crop industry_criticism_master.png 780x439+0+190 33_carson_and_research_binders.png
crop industry_criticism_master.png 820x461+820+160 34_industry_spokesmen_and_reports.png
crop industry_criticism_master.png 760x428+430+100 35_press_cameras_between_sides.png
tone industry_criticism_master.png 36_public_dispute_transition.png 88,100,103 '#251f2d'

# 1963年の上院証言（まだ禁止決定ではない）
frame senate_testimony_master.png 37_senate_testimony_wide.png
crop senate_testimony_master.png 760x428+160+170 38_carson_calm_testimony.png
crop senate_testimony_master.png 900x506+740+100 39_senators_review_evidence.png

# 1972年の登録取消し（カーソンは登場させない）
frame epa_1972_decision_master.png 40_epa_decision_wide.png
crop epa_1972_decision_master.png 820x461+480+230 41_administrator_signs_order.png

# 現代環境運動の広がり
frame environmental_movement_master.png 42_environmental_movement_wide.png
crop environmental_movement_master.png 860x484+120+210 43_river_science_and_cleanup.png
crop environmental_movement_master.png 780x439+570+220 44_native_tree_planting.png
crop environmental_movement_master.png 820x461+820+190 45_community_policy_table.png
crop environmental_movement_master.png 760x428+700+0 46_recovered_nest_transition.png

# 現代の高校生が生態系の釣り合いを見つめる
frame modern_ecological_balance_master.png 47_modern_wetland_wide.png
crop modern_ecological_balance_master.png 850x478+0+250 48_fish_insects_and_native_plants.png
crop modern_ecological_balance_master.png 720x405+900+120 49_student_field_notebook.png
crop modern_ecological_balance_master.png 650x366+1020+0 50_recovered_bird_nest.png
crop modern_ecological_balance_master.png 980x551+0+0 51_sunrise_birds_final.png

expected=(
  01_carson_writer_wide.png 02_coastal_marsh_window.png
  03_carson_scientist_writer.png 04_bird_fish_research_notes.png
  05_publication_office_wide.png 06_carson_first_copy.png
  07_editors_and_proofs.png 08_unlettered_bird_cover.png
  09_writing_to_publication_link.png 10_publication_team_transition.png
  11_ddt_use_wide.png 12_drifting_spray_over_fields.png
  13_period_crop_duster.png 14_ground_mixing_crew.png
  15_drainage_ditch_beside_field.png 16_cotton_field_mist.png
  17_insects_and_drift_transition.png 18_food_web_field_station_wide.png
  19_eggshell_and_tissue_samples.png 20_marsh_stream_and_osprey.png
  21_water_insect_fish_egg_sequence.png 22_fish_specimen_measurement.png
  23_fragile_eggshell_sample.png 24_osprey_nest_above_marsh.png
  25_field_biologists_compare_evidence.png 26_silent_spring_orchard_wide.png
  27_empty_nests_in_blossom.png 28_still_birdbath_and_empty_sky.png
  29_public_awareness_library_wide.png 30_readers_share_the_book.png
  31_letters_scientists_and_reporters.png 32_industry_criticism_wide.png
  33_carson_and_research_binders.png 34_industry_spokesmen_and_reports.png
  35_press_cameras_between_sides.png 36_public_dispute_transition.png
  37_senate_testimony_wide.png 38_carson_calm_testimony.png
  39_senators_review_evidence.png 40_epa_decision_wide.png
  41_administrator_signs_order.png 42_environmental_movement_wide.png
  43_river_science_and_cleanup.png 44_native_tree_planting.png
  45_community_policy_table.png 46_recovered_nest_transition.png
  47_modern_wetland_wide.png 48_fish_insects_and_native_plants.png
  49_student_field_notebook.png 50_recovered_bird_nest.png
  51_sunrise_birds_final.png
)
for file in $expected; do
  test -s "$OUT/$file"
done
echo "H043 final_style01 files verified: ${#expected[@]}"
