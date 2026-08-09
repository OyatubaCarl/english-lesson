#!/bin/zsh
set -euo pipefail

ROOT="${0:A:h:h}"
REF="$ROOT/H038/scenes/character_refs"
OUT="$ROOT/H038/scenes/final_style01"
mkdir -p "$OUT"

frame() { cp "$REF/$1" "$OUT/$2"; }
crop() {
  magick "$REF/$1" -crop "$2" +repage \
    -resize '1672x941^' -gravity center -extent 1672x941 "$OUT/$3"
}
tone() {
  magick "$REF/$1" -modulate "$3" -fill "$4" -colorize 12% "$OUT/$2"
}

# 十二秒の飛行を先に提示
frame first_flight_master.png 01_first_flight_opening_wide.png
crop first_flight_master.png 1120x630+300+10 02_orville_lifts_from_rail.png
crop first_flight_master.png 760x428+880+80 03_wilbur_runs_beside_flyer.png
frame twelve_second_flight_master.png 04_twelve_seconds_in_air.png
crop twelve_second_flight_master.png 980x551+400+25 05_fragile_controlled_flight.png
crop twelve_second_flight_master.png 1050x591+0+40 06_wilbur_watches_from_ground.png

# 自転車店から始まった夢
frame bicycle_shop_dream_master.png 07_bicycle_shop_dream_wide.png
crop bicycle_shop_dream_master.png 840x473+20+20 08_wilbur_repairs_bicycle.png
crop bicycle_shop_dream_master.png 850x478+760+20 09_orville_studies_wing.png
crop bicycle_shop_dream_master.png 1080x608+300+25 10_brothers_share_flight_dream.png

# 風洞と翼型の反復実験
frame wind_tunnel_master.png 11_wind_tunnel_workshop_wide.png
crop wind_tunnel_master.png 920x518+20+40 12_wilbur_tests_wing_section.png
crop wind_tunnel_master.png 850x478+720+35 13_orville_reads_balance.png
crop wind_tunnel_master.png 1120x630+200+150 14_many_wing_shapes.png
crop wind_tunnel_master.png 900x506+370+15 15_own_hands_repeated_tests.png

# 無動力グライダーで不可能を削る
frame glider_experiment_master.png 16_glider_experiment_wide.png
crop glider_experiment_master.png 1120x630+0+30 17_wilbur_prone_in_glider.png
crop glider_experiment_master.png 820x461+780+60 18_orville_holds_guide_rope.png
tone glider_experiment_master.png 19_impossible_in_strong_wind.png 78,92,103 '#203046'
crop glider_experiment_master.png 1040x585+260+10 20_brothers_do_not_abandon.png
tone glider_experiment_master.png 21_birds_can_fly_resolve.png 96,104,102 '#34352e'

# 1903年12月17日の準備
frame flyer_preparation_master.png 22_flyer_preparation_wide.png
crop flyer_preparation_master.png 1050x591+0+20 23_brothers_check_fabric.png
crop flyer_preparation_master.png 1120x630+480+30 24_engine_props_and_launch_rail.png
tone flyer_preparation_master.png 25_strong_wind_that_morning.png 84,92,104 '#1b3047'

# 車輪なし、腹ばい操縦の初飛行
frame first_flight_master.png 26_first_flight_historic_wide.png
crop first_flight_master.png 960x540+300+25 27_orville_prone_controls.png
crop first_flight_master.png 820x461+820+35 28_wilbur_releases_wing.png
frame twelve_second_flight_master.png 29_flight_twelve_seconds_wide.png
crop twelve_second_flight_master.png 950x534+550+30 30_flyer_over_open_sand.png
crop twelve_second_flight_master.png 1060x596+0+80 31_thirty_seven_meter_path.png
tone twelve_second_flight_master.png 32_controlled_powered_effort.png 94,100,103 '#273347'

# 着地と静かな実感
frame landing_realization_master.png 33_landing_realization_wide.png
crop landing_realization_master.png 900x506+300+30 34_orville_after_touchdown.png
crop landing_realization_master.png 780x439+850+25 35_wilbur_approaches.png
crop landing_realization_master.png 1050x591+300+20 36_years_of_work_take_flight.png
tone landing_realization_master.png 37_inventor_title_means_nothing.png 84,94,102 '#25313e'

# 人類が空へ踏み出した最初の一歩
frame humanity_sky_step_master.png 38_humanity_sky_step_wide.png
crop humanity_sky_step_master.png 1100x619+0+60 39_brothers_and_fragile_flyer.png
tone humanity_sky_step_master.png 40_open_sky_final.png 94,102,104 '#28364a'

count=$(find "$OUT" -maxdepth 1 -type f -name '*.png' | wc -l | tr -d ' ')
echo "H038 final_style01 PNG count: $count"
test "$count" = "40"
