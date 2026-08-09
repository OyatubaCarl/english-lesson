#!/bin/zsh
set -euo pipefail

ROOT="${0:A:h:h}"
REF="$ROOT/H037/scenes/character_refs"
OUT="$ROOT/H037/scenes/final_style01"
mkdir -p "$OUT"

frame() { cp "$REF/$1" "$OUT/$2"; }
crop() {
  magick "$REF/$1" -crop "$2" +repage \
    -resize '1672x941^' -gravity center -extent 1672x941 "$OUT/$3"
}
tone() {
  magick "$REF/$1" -modulate "$3" -fill "$4" -colorize 12% "$OUT/$2"
}

# 聴力を失い始めた若いベートーヴェン
frame young_hearing_loss_master.png 01_young_beethoven_silence_wide.png
crop young_hearing_loss_master.png 980x551+30+20 02_young_beethoven_listens_inward.png
crop young_hearing_loss_master.png 820x461+520+55 03_musician_fears_silence.png
tone young_hearing_loss_master.png 04_room_falls_quiet.png 78,92,103 '#16243b'

# 絶望と、それでも続く作曲
frame despair_composition_master.png 05_despair_composition_wide.png
crop despair_composition_master.png 900x506+40+40 06_beethoven_in_despair.png
crop despair_composition_master.png 880x495+720+70 07_manuscript_and_resolve.png
crop despair_composition_master.png 760x428+350+80 08_hand_returns_to_music.png
frame inner_music_master.png 09_inner_music_wide.png
crop inner_music_master.png 920x518+80+50 10_music_inside_him.png
crop inner_music_master.png 840x473+700+35 11_sound_beyond_hearing.png
tone inner_music_master.png 12_inner_music_endures.png 92,102,102 '#3a2b20'

# 第九初演の舞台と合唱
frame ninth_premiere_stage_master.png 13_ninth_premiere_stage_wide.png
crop ninth_premiere_stage_master.png 1050x591+0+40 14_orchestra_at_premiere.png
crop ninth_premiere_stage_master.png 830x467+520+30 15_umlauf_leads_orchestra.png
crop ninth_premiere_stage_master.png 760x428+880+80 16_beethoven_beside_conductor.png
frame ode_to_joy_choir_master.png 17_ode_to_joy_choir_wide.png
crop ode_to_joy_choir_master.png 1000x563+30+30 18_choir_sings_schiller.png
crop ode_to_joy_choir_master.png 820x461+760+55 19_voices_rise_together.png
crop ode_to_joy_choir_master.png 900x506+380+20 20_ode_to_joy_center.png
frame ninth_premiere_stage_master.png 21_beethoven_on_stage_wide.png
crop ninth_premiere_stage_master.png 780x439+820+55 22_beethoven_keeps_time.png
crop ninth_premiere_stage_master.png 650x366+970+70 23_silent_profile_at_podium.png

# 終演しても拍手に気づかない
frame silent_back_to_audience_master.png 24_back_to_audience_wide.png
crop silent_back_to_audience_master.png 1050x591+0+30 25_final_note_orchestra.png
crop silent_back_to_audience_master.png 820x461+560+50 26_beethoven_hears_nothing.png
crop silent_back_to_audience_master.png 850x478+800+20 27_applause_behind_him.png
crop silent_back_to_audience_master.png 920x518+80+35 28_audience_rises.png
tone silent_back_to_audience_master.png 29_silence_amid_applause.png 82,94,104 '#17243a'

# カロリーネが腕に触れ、客席へ向ける
frame caroline_turns_beethoven_master.png 30_caroline_reaches_wide.png
crop caroline_turns_beethoven_master.png 950x534+180+30 31_gentle_touch_on_arm.png
crop caroline_turns_beethoven_master.png 780x439+500+40 32_beethoven_begins_to_turn.png
crop caroline_turns_beethoven_master.png 900x506+650+30 33_soloist_guides_him.png
crop caroline_turns_beethoven_master.png 850x478+20+20 34_audience_on_its_feet.png
crop caroline_turns_beethoven_master.png 780x439+720+35 35_beethoven_sees_applause.png

# 沈黙を越えて人類へ届く音楽
frame humanity_legacy_master.png 36_humanity_legacy_wide.png
crop humanity_legacy_master.png 1000x563+30+25 37_beethoven_reaches_humanity.png
crop humanity_legacy_master.png 900x506+700+25 38_ninth_across_generations.png
tone humanity_legacy_master.png 39_creativity_through_suffering.png 92,104,104 '#342539'
tone inner_music_master.png 40_music_survives_silence.png 72,88,102 '#111d33'

count=$(find "$OUT" -maxdepth 1 -type f -name '*.png' | wc -l | tr -d ' ')
echo "H037 final_style01 PNG count: $count"
test "$count" = "40"
