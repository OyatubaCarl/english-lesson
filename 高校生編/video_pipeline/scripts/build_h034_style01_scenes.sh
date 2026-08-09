#!/bin/zsh
set -euo pipefail

ROOT="${0:A:h:h}"
REF="$ROOT/H034/scenes/character_refs"
OUT="$ROOT/H034/scenes/final_style01"

mkdir -p "$OUT"

frame() {
  cp "$REF/$1" "$OUT/$2"
}

crop() {
  magick "$REF/$1" \
    -crop "$2" +repage \
    -resize '1672x941^' -gravity center -extent 1672x941 \
    "$OUT/$3"
}

tone() {
  magick "$REF/$1" -modulate 82,96,105 -fill '#162643' -colorize 12% "$OUT/$2"
}

crop_tone() {
  magick "$REF/$1" \
    -crop "$2" +repage \
    -resize '1672x941^' -gravity center -extent 1672x941 \
    -modulate 78,96,106 -fill '#13233f' -colorize 14% \
    "$OUT/$3"
}

# 19世紀末バルセロナとガウディの建築言語
frame barcelona_1880s_master.png 01_barcelona_1880s_dawn.png
crop barcelona_1880s_master.png 1500x844+172+45 02_old_barcelona_roofs.png
frame gaudi_workshop_master.png 03_gaudi_workshop_wide.png
crop gaudi_workshop_master.png 1050x591+520+190 04_hands_on_plaster_model.png
crop gaudi_workshop_master.png 800x450+120+55 05_gaudi_1915_portrait.png
crop gaudi_workshop_master.png 1400x788+0+40 06_gaudi_and_barcelona.png
crop gaudi_workshop_master.png 900x506+610+210 07_plaster_spire_model.png
crop gaudi_workshop_master.png 850x478+650+0 08_catenary_chain_model.png
crop gaudi_workshop_master.png 1100x619+450+260 09_curves_compass_and_stone.png
crop gaudi_workshop_master.png 800x450+872+35 10_workshop_window_basilica.png

# 1925年にガウディが見た建設段階
frame sagrada_1925_master.png 11_sagrada_1925_wide.png
crop sagrada_1925_master.png 1200x675+350+150 12_nativity_facade_wide.png
crop sagrada_1925_master.png 720x405+120+0 13_barnabas_tower_detail.png
crop sagrada_1925_master.png 900x506+600+250 14_nativity_stone_detail.png

# 百年以上の建設・中断・再開
crop barcelona_1880s_master.png 1450x816+222+70 15_early_foundations_and_workers.png
crop sagrada_1925_master.png 1050x591+622+80 16_wood_scaffolding_stonemasons.png
frame broken_models_master.png 17_1936_broken_models.png
frame postwar_resumes_master.png 18_postwar_construction_resumes.png
frame sagrada_2026_master.png 19_unfinished_masterpiece_wide.png
crop sagrada_2026_master.png 1000x563+672+260 20_finished_stone_and_scaffold.png

# 樹木・山・貝殻・骨・波から得た着想
frame nature_forms_master.png 21_gaudi_observes_oak.png
crop nature_forms_master.png 1200x675+430+245 22_leaf_shell_and_sketch.png
crop nature_forms_master.png 1150x647+0+180 23_tree_mountain_forms.png
crop nature_forms_master.png 1000x563+450+340 24_shell_bone_wave_forms.png
crop nature_forms_master.png 1250x703+150+115 25_tree_column_comparison.png
crop stone_forest_master.png 850x478+0+80 26_double_twist_column_close.png
frame stone_forest_master.png 27_branching_vaults.png

# 自然を教師、建築そのものとして見る
frame nature_forms_master.png 28_gaudi_beneath_tree.png
crop nature_forms_master.png 850x478+120+55 29_oak_branch_and_gaudi_eyes.png
frame stone_forest_master.png 30_stone_forest_interior_wide.png
crop nature_forms_master.png 1000x563+672+230 31_mountain_curve_model.png
crop stone_forest_master.png 1050x591+622+0 32_light_through_forest_vaults.png

# 1926年6月7日〜12日
frame gaudi_tram_approach_master.png 33_gaudi_walks_barcelona_1926.png
crop gaudi_tram_approach_master.png 1200x675+472+70 34_tram_approaches_crossing.png
frame tram_aftermath_master.png 35_stopped_tram_hat_and_cane.png
frame hospital_master.png 36_hospital_room_quiet.png
frame funeral_master.png 37_funeral_to_sagrada.png

# 2026年7月の建設・訪問者・寄付
frame sagrada_2026_master.png 38_sagrada_2026_current_wide.png
crop sagrada_2026_master.png 1000x563+672+240 39_glory_facade_work_continues.png
crop modern_support_master.png 1050x591+622+180 40_modern_stonemason_hands.png
crop modern_support_master.png 1050x591+0+130 41_visitors_from_world.png
crop modern_support_master.png 900x506+0+260 42_discreet_donation_support.png

# 未完の状態を含む建物の歴史
frame postwar_resumes_master.png 43_generations_of_workers.png
crop postwar_resumes_master.png 1100x619+250+250 44_old_model_new_stone.png
crop sagrada_2026_master.png 1050x591+622+225 45_unfinished_glory_facade.png
frame sagrada_2026_master.png 46_finished_tower_unfinished_base.png
tone sagrada_2026_master.png 47_sagrada_dusk_history.png
crop_tone sagrada_2026_master.png 1450x816+110+0 48_sagrada_final_sky.png

count=$(find "$OUT" -maxdepth 1 -type f -name '*.png' | wc -l | tr -d ' ')
echo "H034 final_style01 PNG count: $count"
