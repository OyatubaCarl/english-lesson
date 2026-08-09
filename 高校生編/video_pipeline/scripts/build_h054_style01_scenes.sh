#!/bin/zsh
set -euo pipefail

ROOT="${0:A:h:h}"
REF="$ROOT/H054/scenes/character_refs"
OUT="$ROOT/H054/scenes/final_style01"
mkdir -p "$OUT"

frame() { cp "$REF/$1" "$OUT/$2"; }
crop() {
  magick "$REF/$1" -crop "$2" +repage \
    -resize '1672x941^' -gravity center -extent 1672x941 "$OUT/$3"
}
tone() {
  magick "$REF/$1" -modulate "$3" -fill "$4" -colorize 7% "$OUT/$2"
}

# 古代Olympicsとekecheiria：全面的な戦争停止ではなく、安全な通行と聖域
frame ancient_truce_safe_passage_master.png 01_ancient_truce_road_wide.png
crop ancient_truce_safe_passage_master.png 700x394+0+140 02_olive_road_and_heralds.png
crop ancient_truce_safe_passage_master.png 760x428+410+140 03_herald_proclaims_safe_passage.png
crop ancient_truce_safe_passage_master.png 650x366+980+180 04_weapon_left_at_boundary.png
frame ancient_olympia_games_master.png 05_ancient_olympia_race_wide.png
crop ancient_olympia_games_master.png 850x478+470+130 06_athletes_judges_and_rules.png

# 現代へ受け継がれるexcellence・friendship・respect
frame modern_olympic_spirit_master.png 07_modern_spirit_wide.png
crop modern_olympic_spirit_master.png 900x506+380+120 08_athletes_greet_with_respect.png

# 世界のathletesと長年のtraining
frame years_of_training_master.png 09_years_of_training_wide.png
crop years_of_training_master.png 680x383+390+160 10_sprinter_start_detail.png
crop years_of_training_master.png 620x349+1000+150 11_coach_observes_form.png
crop years_of_training_master.png 650x366+0+170 12_recovery_and_teammate.png

# disciplineとdedication
frame discipline_dedication_master.png 13_discipline_dedication_wide.png
crop discipline_dedication_master.png 760x428+360+150 14_athlete_recovery_work.png
crop discipline_dedication_master.png 700x394+0+150 15_coach_notebook_food_and_rest.png

# Victoryだけがすべてではない
frame victory_not_everything_master.png 16_victory_not_everything_wide.png
crop victory_not_everything_master.png 720x405+570+120 17_runner_accepts_result.png
crop victory_not_everything_master.png 700x394+930+170 18_many_kinds_of_completion.png

# opponent、rules、official、safetyを尊重するSportsmanship
frame sportsmanship_master.png 19_sportsmanship_wide.png
crop sportsmanship_master.png 720x405+300+180 20_offer_a_hand.png
crop sportsmanship_master.png 760x428+500+130 21_official_checks_safety.png
crop sportsmanship_master.png 700x394+760+180 22_opponents_rise_together.png
tone sportsmanship_master.png 23_respect_after_competition.png 103,103,102 '#52372b'

# doping問題とroutineのcontrol system
frame doping_system_master.png 24_doping_control_notification_wide.png
crop doping_system_master.png 700x394+0+160 25_athlete_and_representative.png
crop doping_system_master.png 760x428+650+130 26_officer_explains_procedure.png
crop doping_system_master.png 650x366+980+150 27_sealed_kits_and_secure_room.png

# 結果管理、公正な聴聞、確認後の措置
frame results_management_hearing_master.png 28_results_management_hearing_wide.png
crop results_management_hearing_master.png 760x428+430+120 29_scientist_presents_anonymous_evidence.png
crop results_management_hearing_master.png 680x383+0+160 30_independent_panel_listens.png
crop results_management_hearing_master.png 680x383+930+160 31_athlete_and_representative_are_heard.png

# fair playを守るtestingとchain of custody
frame strict_testing_chain_master.png 32_strict_testing_chain_wide.png
crop strict_testing_chain_master.png 760x428+280+160 33_athlete_seals_samples.png
crop strict_testing_chain_master.png 760x428+830+120 34_secure_handoff_and_laboratory.png

# winning teamのfansとlosing teamへの静かなapplause
frame winning_losing_teams_master.png 35_winning_and_losing_teams_wide.png
crop winning_losing_teams_master.png 700x394+0+160 36_winning_relay_team.png
crop winning_losing_teams_master.png 720x405+850+160 37_losing_team_stays_together.png
crop winning_losing_teams_master.png 900x506+380+110 38_teams_acknowledge_each_other.png
tone winning_losing_teams_master.png 39_applause_for_every_effort.png 101,103,102 '#493527'

# defeatを受け入れ、翌朝のnext challengeへ
frame accept_defeat_next_challenge_master.png 40_accept_defeat_next_challenge_wide.png
crop accept_defeat_next_challenge_master.png 650x366+0+140 41_baton_and_quiet_reflection.png
crop accept_defeat_next_challenge_master.png 700x394+750+160 42_coach_resets_starting_blocks.png
crop accept_defeat_next_challenge_master.png 760x428+350+120 43_athlete_turns_toward_start.png
tone accept_defeat_next_challenge_master.png 44_dawn_after_defeat.png 106,104,102 '#67452d'

# televisionの前のchildren
frame children_watch_athletes_master.png 45_children_watch_sportsmanship_wide.png
crop children_watch_athletes_master.png 650x366+0+120 46_television_helping_opponent.png
crop children_watch_athletes_master.png 760x428+280+180 47_children_practice_respect.png
crop children_watch_athletes_master.png 700x394+850+150 48_student_and_children_learn.png

# role modelとして努力とrespectのmessageを渡す
frame role_model_final_master.png 49_role_model_community_track_wide.png
crop role_model_final_master.png 720x405+0+170 50_athlete_teaches_safe_start.png
crop role_model_final_master.png 760x428+520+120 51_children_practice_relay.png
crop role_model_final_master.png 700x394+900+150 52_inclusive_track_and_student.png
tone role_model_final_master.png 53_effort_can_bear_fruit_dawn.png 107,105,102 '#6a482e'

expected=("$OUT"/[0-9][0-9]_*.png)
test ${#expected[@]} -eq 53
for file in $expected; do
  test -s "$file"
done
echo "H054 final_style01 files verified: ${#expected[@]}"
