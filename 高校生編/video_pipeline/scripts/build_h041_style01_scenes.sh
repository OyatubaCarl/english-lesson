#!/bin/zsh
set -euo pipefail

ROOT="${0:A:h:h}"
REF="$ROOT/H041/scenes/character_refs"
OUT="$ROOT/H041/scenes/final_style01"
mkdir -p "$OUT"

frame() { cp "$REF/$1" "$OUT/$2"; }
crop() {
  magick "$REF/$1" -crop "$2" +repage \
    -resize '1672x941^' -gravity center -extent 1672x941 "$OUT/$3"
}
tone() {
  magick "$REF/$1" -modulate "$3" -fill "$4" -colorize 10% "$OUT/$2"
}

# ブレッチリー・パークのチューリングと共同作業
frame turing_bletchley_identity_master.png 01_bletchley_team_wide.png
crop turing_bletchley_identity_master.png 760x428+760+30 02_turing_identity_portrait.png
crop turing_bletchley_identity_master.png 980x551+230+120 03_three_cryptanalysts_work.png
crop turing_bletchley_identity_master.png 740x416+860+300 04_enigma_rotors_and_keyboard.png
crop turing_bletchley_identity_master.png 900x506+380+300 05_rotor_diagrams_and_hands.png
tone turing_bletchley_identity_master.png 06_hut_eight_staff_at_night.png 84,96,103 '#17283d'

# ドイツ潜水艦隊の暗号通信
frame enigma_atlantic_master.png 07_uboat_wireless_room_wide.png
crop enigma_atlantic_master.png 850x478+730+200 08_enigma_machine_close.png
crop enigma_atlantic_master.png 820x461+0+150 09_radio_operator_and_message.png

# 解読できなければ危険にさらされる護送船団
frame atlantic_convoy_risk_master.png 10_atlantic_convoy_wide.png
crop atlantic_convoy_risk_master.png 1030x579+520+80 11_merchant_ships_in_columns.png
crop atlantic_convoy_risk_master.png 760x428+850+180 12_royal_navy_escort.png
crop atlantic_convoy_risk_master.png 820x461+0+320 13_periscope_wake_and_convoy.png

# ボンベを共同で運用するチーム
frame bombe_team_master.png 14_bombe_team_wide.png
crop bombe_team_master.png 930x523+0+40 15_wrens_operate_drums.png
crop bombe_team_master.png 920x518+650+170 16_turing_welchman_and_menu.png
crop bombe_team_master.png 780x439+250+250 17_operator_records_result.png
crop bombe_team_master.png 980x551+450+0 18_rotating_drum_banks.png
tone bombe_team_master.png 19_team_checks_possible_setting.png 90,101,103 '#253047'

# 人間が結果を確認し護送船団の航路へ反映
frame convoy_intelligence_master.png 20_naval_intelligence_room_wide.png
crop convoy_intelligence_master.png 920x518+0+150 21_wren_moves_ship_marker.png
crop convoy_intelligence_master.png 1080x608+360+80 22_team_interprets_verified_result.png
crop convoy_intelligence_master.png 800x450+680+230 23_dividers_and_convoy_chart.png

# 戦後、「機械は考えられるか」を探究
frame machine_think_master.png 24_machine_think_lab_wide.png
crop machine_think_master.png 820x461+720+40 25_turing_with_punched_tape.png
crop machine_think_master.png 900x506+420+220 26_chess_and_teleprinter_output.png
crop machine_think_master.png 1080x608+250+0 27_early_computer_colleagues.png

# コンピューター科学とAIの議論へ続く基礎
frame computer_science_legacy_master.png 28_computer_science_legacy_wide.png
crop computer_science_legacy_master.png 920x518+100+170 29_punched_tape_and_valve_module.png
crop computer_science_legacy_master.png 1100x619+360+70 30_modern_researchers_discuss_ai.png
crop computer_science_legacy_master.png 880x495+700+0 31_turing_portrait_and_networks.png

# 1952年、差別的な法による起訴
frame prosecution_master.png 32_courthouse_exit_wide.png
crop prosecution_master.png 820x461+480+70 33_turing_after_prosecution.png
crop prosecution_master.png 980x551+280+80 34_solicitor_walks_beside_turing.png
crop prosecution_master.png 1120x630+420+0 35_official_and_courthouse_door.png

# 41歳の死と、守った国から受けた処罰を不在で示す
frame empty_study_master.png 36_empty_study_wide.png
crop empty_study_master.png 850x478+700+260 37_empty_chair_and_running_shoes.png
crop empty_study_master.png 900x506+0+330 38_closed_notebook_chess_and_tape.png
tone empty_study_master.png 39_country_punished_him.png 70,88,102 '#131f34'

# 2013年の死後恩赦と、遅すぎた認識
frame pardon_archive_master.png 40_pardon_archive_wide.png
crop pardon_archive_master.png 900x506+0+200 41_gloved_hands_and_pardon.png
crop pardon_archive_master.png 850x478+700+130 42_portrait_red_box_and_seal.png
tone pardon_archive_master.png 43_pardon_came_too_late.png 82,96,102 '#2a2534'

# 現代の高校生へ残る問い
frame modern_student_legacy_master.png 44_student_remembers_turing_final.png

expected=(
  01_bletchley_team_wide.png 02_turing_identity_portrait.png
  03_three_cryptanalysts_work.png 04_enigma_rotors_and_keyboard.png
  05_rotor_diagrams_and_hands.png 06_hut_eight_staff_at_night.png
  07_uboat_wireless_room_wide.png 08_enigma_machine_close.png
  09_radio_operator_and_message.png 10_atlantic_convoy_wide.png
  11_merchant_ships_in_columns.png 12_royal_navy_escort.png
  13_periscope_wake_and_convoy.png 14_bombe_team_wide.png
  15_wrens_operate_drums.png 16_turing_welchman_and_menu.png
  17_operator_records_result.png 18_rotating_drum_banks.png
  19_team_checks_possible_setting.png 20_naval_intelligence_room_wide.png
  21_wren_moves_ship_marker.png 22_team_interprets_verified_result.png
  23_dividers_and_convoy_chart.png 24_machine_think_lab_wide.png
  25_turing_with_punched_tape.png 26_chess_and_teleprinter_output.png
  27_early_computer_colleagues.png 28_computer_science_legacy_wide.png
  29_punched_tape_and_valve_module.png 30_modern_researchers_discuss_ai.png
  31_turing_portrait_and_networks.png 32_courthouse_exit_wide.png
  33_turing_after_prosecution.png 34_solicitor_walks_beside_turing.png
  35_official_and_courthouse_door.png 36_empty_study_wide.png
  37_empty_chair_and_running_shoes.png 38_closed_notebook_chess_and_tape.png
  39_country_punished_him.png 40_pardon_archive_wide.png
  41_gloved_hands_and_pardon.png 42_portrait_red_box_and_seal.png
  43_pardon_came_too_late.png 44_student_remembers_turing_final.png
)
for file in $expected; do
  test -s "$OUT/$file"
done
echo "H041 final_style01 files verified: ${#expected[@]}"
