#!/bin/zsh
set -euo pipefail

ROOT="${0:A:h:h}"
REF="$ROOT/H033/scenes/character_refs"
OUT="$ROOT/H033/scenes/final_style01"

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

# 晩年の自己認識と、未知の広がり
frame elder_newton_master.png 01_elder_newton_study_wide.png
crop elder_newton_master.png 1000x563+672+120 02_candle_books_and_globe.png
crop elder_newton_master.png 1400x788+0+40 03_elder_newton_at_desk.png
crop elder_newton_master.png 800x450+250+25 04_silver_hair_and_eyes.png
crop elder_newton_master.png 1100x619+120+275 05_newton_closes_book.png
crop elder_newton_master.png 760x428+410+475 06_single_pebble_on_desk.png
crop elder_newton_master.png 1000x563+672+35 07_study_window_night_sky.png
crop ocean_wide_master.png 1500x844+172+40 08_vast_unknown_horizon.png

# 『プリンキピア』と人類へ渡る知識
frame principia_printing_master.png 09_principia_in_library.png
crop principia_printing_master.png 1100x619+0+165 10_hands_on_principia_pages.png
frame later_scholars_master.png 11_scholars_receive_knowledge.png
frame trinity_courtyard_master.png 12_trinity_courtyard_dawn.png

# 重力・三法則・微積分
crop unification_master.png 920x518+0+120 13_gravity_falling_sphere.png
crop motion_laws_master.png 920x518+420+235 14_first_law_cart_in_motion.png
crop motion_laws_master.png 1150x647+170+75 15_second_law_force_and_mass.png
crop motion_laws_master.png 850x478+822+105 16_third_law_opposing_forces.png
frame calculus_master.png 17_calculus_curve_and_quill.png

# 地上の落下と天体軌道の統一
crop unification_master.png 920x518+0+130 18_falling_object_before_newton.png
frame falling_tower_master.png 19_stone_falls_from_tower.png
crop unification_master.png 900x506+772+65 20_planetary_orbit_chart.png
frame unification_master.png 21_young_newton_unifies_diagrams.png
crop unification_master.png 1350x759+250+55 22_earth_moon_and_falling_ball.png

# 数学が科学の言語を作り直す
frame calculus_master.png 23_mathematics_manuscript_wide.png
crop calculus_master.png 900x506+330+300 24_geometry_compass_close.png
crop calculus_master.png 1050x591+370+260 25_tangent_and_area_diagram.png
frame principia_printing_master.png 26_principia_printing_and_scholars.png

# 名誉より未知へ向く晩年
frame humble_elder_master.png 27_elder_newton_turns_from_honors.png
crop humble_elder_master.png 840x473+832+310 28_honors_in_shadow.png
crop humble_elder_master.png 760x428+240+80 29_newton_lowers_his_eyes.png
crop humble_elder_master.png 940x529+732+85 30_empty_chair_and_books.png

# 海岸の子どもの比喩（伝記上の幼少期ではない）
frame child_seashore_master.png 31_child_on_seashore_wide.png
crop child_seashore_master.png 850x478+0+310 32_child_feet_at_tidepool.png
crop pebble_shell_master.png 900x506+650+155 33_smooth_pebble_close.png
crop pebble_shell_master.png 900x506+0+275 34_small_shell_close.png
frame pebble_shell_master.png 35_child_holds_few_finds.png

# 未踏の真実の大海
frame ocean_wide_master.png 36_ocean_of_truth_wide.png
crop ocean_wide_master.png 1400x788+272+145 37_waves_and_depth.png
crop ocean_wide_master.png 1500x844+172+0 38_low_endless_horizon.png
frame ocean_wide_master.png 39_small_child_before_ocean.png
frame final_book_beach_master.png 40_pebble_shell_and_vast_sea.png
crop child_seashore_master.png 1500x844+172+20 41_seashore_dusk_hold.png

# 謙虚さと次世代
frame humble_elder_master.png 42_elder_newton_humble_return.png
crop elder_newton_master.png 1000x563+140+320 43_open_hands_over_book.png
crop later_scholars_master.png 980x551+0+170 44_young_scholar_reads_newton.png
frame later_scholars_master.png 45_generations_of_scholars.png
crop humble_elder_master.png 760x428+235+65 46_humility_in_newtons_face.png

# 理論の到達点と、さらに深い知の海
crop calculus_master.png 1200x675+320+195 47_theory_lines_extend_far.png
crop unification_master.png 940x529+732+75 48_planet_model_and_manuscript.png
frame deep_ocean_master.png 49_deep_ocean_below_surface.png
frame final_book_beach_master.png 50_book_pebble_shell_on_sand.png
frame ocean_wide_master.png 51_vast_ocean_final.png

count=$(find "$OUT" -maxdepth 1 -type f -name '*.png' | wc -l | tr -d ' ')
echo "H033 final_style01 PNG count: $count"
