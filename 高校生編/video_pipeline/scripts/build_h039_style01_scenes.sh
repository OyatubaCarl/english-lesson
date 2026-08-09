#!/bin/zsh
set -euo pipefail

ROOT="${0:A:h:h}"
REF="$ROOT/H039/scenes/character_refs"
OUT="$ROOT/H039/scenes/final_style01"
mkdir -p "$OUT"

frame() { cp "$REF/$1" "$OUT/$2"; }
crop() {
  magick "$REF/$1" -crop "$2" +repage \
    -resize '1672x941^' -gravity center -extent 1672x941 "$OUT/$3"
}
tone() {
  magick "$REF/$1" -modulate "$3" -fill "$4" -colorize 12% "$OUT/$2"
}

# 現代の高校生が星空を見上げる
frame modern_night_sky_master.png 01_modern_night_sky_wide.png
crop modern_night_sky_master.png 1080x608+560+0 02_student_looks_up.png
crop modern_night_sky_master.png 1120x630+0+0 03_milky_way_over_observatory.png
tone modern_night_sky_master.png 04_light_travels_thousands_years.png 90,102,103 '#142641'

# 1609年、ガリレオが望遠鏡を作る
frame galileo_telescope_workshop_master.png 05_galileo_builds_telescope_wide.png
crop galileo_telescope_workshop_master.png 850x478+20+30 06_galileo_lens_and_hands.png
crop galileo_telescope_workshop_master.png 1000x563+470+20 07_early_telescope_tube.png
frame galileo_observes_sky_master.png 08_galileo_rooftop_observation_wide.png
crop galileo_observes_sky_master.png 880x495+0+20 09_galileo_at_eyepiece.png
crop galileo_observes_sky_master.png 1100x619+500+0 10_moon_and_jupiter_over_padua.png

# 月面と木星の衛星の発見
frame moon_jupiter_discovery_master.png 11_moon_jupiter_discovery_wide.png
crop moon_jupiter_discovery_master.png 900x506+0+30 12_galileo_draws_moon.png
crop moon_jupiter_discovery_master.png 820x461+680+100 13_four_dots_beside_jupiter.png
crop moon_jupiter_discovery_master.png 1000x563+250+20 14_observations_change_cosmos.png
tone moon_jupiter_discovery_master.png 15_geocentric_belief_shaken.png 86,94,104 '#2d2232'

# 1633年の異端審問、それでも消えない観測事実
frame galileo_inquisition_master.png 16_galileo_inquisition_wide.png
crop galileo_inquisition_master.png 760x428+0+25 17_aged_galileo_stands_alone.png
crop galileo_inquisition_master.png 980x551+650+25 18_cardinals_deliver_judgment.png
tone galileo_inquisition_master.png 19_truth_not_erased.png 74,90,103 '#18253b'

# 1977年、二機のボイジャーが出発
frame voyager_launch_master.png 20_voyager_launch_wide.png
crop voyager_launch_master.png 1020x574+330+0 21_titan_iiie_rises.png
crop voyager_launch_master.png 1120x630+260+100 22_fire_and_smoke_to_space.png
tone voyager_launch_master.png 23_voyager_one_and_two.png 88,100,103 '#23334a'

# 木星、土星、そして海王星まで
frame voyager_jupiter_master.png 24_voyager_at_jupiter_wide.png
crop voyager_jupiter_master.png 1000x563+500+0 25_jupiter_bands_and_probe.png
frame voyager_saturn_master.png 26_voyager_at_saturn_wide.png
crop voyager_saturn_master.png 1120x630+0+60 27_probe_crosses_saturn_rings.png
frame voyager_neptune_master.png 28_voyager_at_neptune_wide.png
crop voyager_neptune_master.png 1060x596+420+0 29_neptune_and_triton.png

# 太陽系を越えて続く静かな旅
frame voyager_interstellar_master.png 30_voyager_interstellar_wide.png
crop voyager_interstellar_master.png 1050x591+450+80 31_probe_recedes_into_dark.png
tone voyager_interstellar_master.png 32_quiet_journey_beyond_sun.png 74,94,105 '#101c32'

# ゴールデンレコードを機体に取り付ける
frame golden_record_master.png 33_golden_record_installation_wide.png
crop golden_record_master.png 940x529+500+20 34_engineers_mount_record.png
crop golden_record_master.png 760x428+760+60 35_human_hands_and_gold_disc.png
crop golden_record_master.png 1050x591+350+0 36_record_under_protective_cover.png

# 地球の声・言葉・音楽を運ぶ小さなメッセージ
frame earth_message_master.png 37_message_from_earth_wide.png
crop earth_message_master.png 1100x619+0+70 38_record_mounted_on_voyager.png
crop earth_message_master.png 760x428+880+120 39_small_earth_and_moon.png
tone earth_message_master.png 40_human_message_in_vast_space.png 82,102,104 '#10182a'

# 好奇心が世紀を越えて続く
frame curiosity_centuries_master.png 41_curiosity_centuries_wide.png
crop curiosity_centuries_master.png 980x551+620+0 42_student_and_telescope_at_dawn.png
crop curiosity_centuries_master.png 1120x630+0+0 43_last_stars_over_horizon.png
tone galileo_observes_sky_master.png 44_galileo_question_endures.png 76,96,104 '#13223a'
tone curiosity_centuries_master.png 45_curiosity_toward_universe_final.png 88,104,104 '#15233a'

count=$(find "$OUT" -maxdepth 1 -type f -name '*.png' | wc -l | tr -d ' ')
echo "H039 final_style01 PNG count: $count"
test "$count" = "45"
