#!/bin/zsh
set -euo pipefail

ROOT="${0:A:h:h}"
REF="$ROOT/H035/scenes/character_refs"
OUT="$ROOT/H035/scenes/final_style01"

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

# 1831年の出航と約5年の測量航海
frame beagle_departure_master.png 01_beagle_departure_wide.png
crop beagle_departure_master.png 850x478+750+45 02_young_darwin_departure_portrait.png
crop beagle_departure_master.png 1200x675+472+0 03_beagle_deck_and_sails.png
crop beagle_departure_master.png 1050x591+0+90 04_british_coast_recedes.png
frame beagle_voyage_cabin_master.png 05_beagle_cabin_wide.png
crop beagle_voyage_cabin_master.png 950x534+260+250 06_notebook_chart_and_specimen.png
crop beagle_voyage_cabin_master.png 850x478+750+125 07_microscope_and_coast_window.png
crop beagle_voyage_cabin_master.png 900x506+0+165 08_lantern_boxes_and_hammock.png

# 1835年9〜10月のガラパゴス上陸と観察
frame galapagos_arrival_master.png 09_galapagos_arrival_wide.png
crop galapagos_arrival_master.png 850x478+250+65 10_darwin_on_black_lava.png
crop galapagos_arrival_master.png 850x478+822+230 11_marine_iguanas_and_cactus.png
frame mockingbirds_tortoise_master.png 12_mockingbird_observation_wide.png
crop mockingbirds_tortoise_master.png 720x405+0+0 13_galapagos_mockingbird_close.png

# 鳥類標本の収集と帰国後の同定
frame field_collection_master.png 14_field_collection_wide.png
crop field_collection_master.png 1120x630+160+300 15_bird_specimen_trays.png
frame gould_finches_london_master.png 16_gould_finches_london_wide.png
crop gould_finches_london_master.png 1200x675+0+245 17_related_finch_beaks.png
crop gould_finches_london_master.png 800x450+760+35 18_darwin_hears_gould.png

# 標本と長年の思索
crop field_collection_master.png 850x478+180+175 19_darwin_records_specimen.png
crop field_collection_master.png 1000x563+590+240 20_packed_specimens_and_plants.png
frame down_house_thought_master.png 21_down_house_thought_wide.png
crop down_house_thought_master.png 1000x563+200+240 22_hand_specimen_and_beak_notes.png
crop down_house_thought_master.png 1000x563+450+300 23_island_map_and_branching_notes.png
crop mockingbirds_tortoise_master.png 850x478+822+205 24_island_tortoise_difference.png

# 環境への適応を嘴と食物へ寄って示す
frame finch_adaptation_master.png 25_finch_adaptation_wide.png
crop finch_adaptation_master.png 720x405+0+50 26_thick_beak_cracks_seed.png
crop finch_adaptation_master.png 760x428+455+400 27_fine_beak_finds_insect.png
crop finch_adaptation_master.png 700x394+972+0 28_long_beak_cactus_food.png

# 1859年の出版
frame origin_printing_master.png 29_origin_printing_wide.png
crop origin_printing_master.png 850x478+0+125 30_printing_press_and_sheet.png
crop origin_printing_master.png 850x478+350+55 31_darwin_1859_green_book.png
crop origin_printing_master.png 850x478+822+235 32_first_edition_crate.png

# 批判、検討、時間をかけた受容
frame criticism_lecture_master.png 33_criticism_lecture_wide.png
crop criticism_lecture_master.png 850x478+650+0 34_branching_birds_projection.png
crop criticism_lecture_master.png 1200x675+450+250 35_book_and_beak_evidence.png
crop criticism_lecture_master.png 1000x563+0+160 36_skeptical_and_curious_faces.png
frame later_acceptance_master.png 37_later_acceptance_wide.png
crop later_acceptance_master.png 850x478+430+85 38_next_generation_measures_beak.png
crop later_acceptance_master.png 800x450+800+90 39_student_green_book_and_notes.png

# 世代を重ねる自然
frame nature_generations_master.png 40_nature_generations_wide.png
crop nature_generations_master.png 800x450+0+0 41_mockingbird_parent_and_fledgling.png
crop nature_generations_master.png 850x478+620+285 42_adult_and_young_tortoise.png
crop nature_generations_master.png 700x394+972+0 43_related_finch_generation.png
tone nature_generations_master.png 44_galapagos_final_dawn.png

count=$(find "$OUT" -maxdepth 1 -type f -name '*.png' | wc -l | tr -d ' ')
echo "H035 final_style01 PNG count: $count"
