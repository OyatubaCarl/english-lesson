#!/bin/zsh
set -euo pipefail

ROOT="${0:A:h:h}"
REF="$ROOT/H036/scenes/character_refs"
OUT="$ROOT/H036/scenes/final_style01"

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
  magick "$REF/$1" -modulate 82,96,105 -fill '#14243f' -colorize 14% "$OUT/$2"
}

# 古代アテネとアゴラの導入
frame agora_dawn_master.png 01_agora_dawn_wide.png
crop agora_dawn_master.png 1120x630+100+40 02_agora_market_and_acropolis.png

# 書物ではなく、対話に生きた哲学
frame socrates_agora_dialogue_master.png 03_socrates_dialogue_wide.png
crop socrates_agora_dialogue_master.png 720x405+540+80 04_socrates_questioning_portrait.png
crop socrates_agora_dialogue_master.png 850x478+800+120 05_listeners_consider_question.png
frame no_book_walking_dialogue_master.png 06_no_book_walking_wide.png
crop no_book_walking_dialogue_master.png 900x506+360+85 07_walking_dialogue_socrates.png
crop no_book_walking_dialogue_master.png 850x478+780+80 08_walking_listeners_think.png

# プラトンの記録と「吟味されない生」
frame plato_account_unexamined_master.png 09_plato_account_wide.png
crop plato_account_unexamined_master.png 760x428+820+60 10_plato_blank_papyrus_portrait.png
crop plato_account_unexamined_master.png 900x506+40+70 11_socrates_spoken_philosophy.png
tone plato_account_unexamined_master.png 12_unexamined_life_reflection.png

# virtue / justice への問い
frame virtue_question_master.png 13_virtue_question_wide.png
crop virtue_question_master.png 780x439+100+70 14_socrates_asks_virtue.png
frame justice_question_master.png 15_justice_question_wide.png
crop justice_question_master.png 1050x591+320+160 16_civic_tokens_and_debate.png

# 知っていると主張する人と、揺らぐ権威
frame claimed_knowledge_master.png 17_claimed_knowledge_wide.png
crop claimed_knowledge_master.png 760x428+150+40 18_confident_authority.png
crop claimed_knowledge_master.png 760x428+720+80 19_socrates_open_questions.png
frame authority_shaken_master.png 20_authority_shaken_wide.png
crop authority_shaken_master.png 760x428+80+40 21_authority_reconsiders.png

# 399 BC の告発、裁判、有罪判決
frame trial_accusation_master.png 22_trial_accusation_wide.png
crop trial_accusation_master.png 720x405+40+70 23_accuser_addresses_jury.png
crop trial_accusation_master.png 800x450+850+50 24_socrates_faces_trial.png
frame jury_condemnation_master.png 25_jury_condemnation_wide.png

# 逃亡の勧めと法への応答
frame prison_escape_master.png 26_friends_urge_escape_wide.png
crop prison_escape_master.png 780x439+80+50 27_open_door_and_friends.png
crop prison_escape_master.png 920x518+520+60 28_offered_cloak_and_socrates.png
frame laws_refusal_master.png 29_socrates_refuses_escape_wide.png
crop laws_refusal_master.png 900x506+650+50 30_athens_beyond_doorway.png

# 毒杯と静かな死
frame hemlock_cup_master.png 31_hemlock_cup_wide.png
crop hemlock_cup_master.png 850x478+360+75 32_socrates_accepts_cup.png
frame quiet_death_master.png 33_quiet_death_wide.png

# 二千年後の現代に続く問い
frame modern_self_examination_master.png 34_modern_agora_student_wide.png
crop modern_self_examination_master.png 1120x630+0+80 35_ruins_and_acropolis_today.png
crop modern_self_examination_master.png 780x439+850+70 36_student_and_reflection.png
crop modern_self_examination_master.png 1000x563+610+40 37_student_examines_his_life.png
tone socrates_agora_dialogue_master.png 38_socrates_question_enduring.png
tone modern_self_examination_master.png 39_modern_agora_final_dusk.png

count=$(find "$OUT" -maxdepth 1 -type f -name '*.png' | wc -l | tr -d ' ')
echo "H036 final_style01 PNG count: $count"
test "$count" = "39"
