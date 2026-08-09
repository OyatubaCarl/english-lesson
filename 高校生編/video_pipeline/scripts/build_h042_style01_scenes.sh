#!/bin/zsh
set -euo pipefail

ROOT="${0:A:h:h}"
REF="$ROOT/H042/scenes/character_refs"
OUT="$ROOT/H042/scenes/final_style01"
mkdir -p "$OUT"

frame() { cp "$REF/$1" "$OUT/$2"; }
crop() {
  magick "$REF/$1" -crop "$2" +repage \
    -resize '1672x941^' -gravity center -extent 1672x941 "$OUT/$3"
}
tone() {
  magick "$REF/$1" -modulate "$3" -fill "$4" -colorize 8% "$OUT/$2"
}

# 複数の陸路と海路がつながる「シルクロード群」
frame silk_roads_network_master.png 01_network_table_wide.png
crop silk_roads_network_master.png 1050x591+270+120 02_branching_land_routes.png
crop silk_roads_network_master.png 850x478+50+300 03_western_land_and_sea.png
crop silk_roads_network_master.png 850x478+760+300 04_eastern_land_and_sea.png
crop silk_roads_network_master.png 980x551+360+60 05_hands_build_network.png
crop silk_roads_network_master.png 900x506+650+300 06_maritime_routes_and_ports.png
tone silk_roads_network_master.png 07_network_not_single_road.png 88,99,103 '#142740'
frame silk_roads_network_master.png 08_eurasia_exchange_network.png

# 敦煌近郊の小規模な中継隊商
frame dunhuang_caravan_master.png 09_dunhuang_caravan_dawn.png
crop dunhuang_caravan_master.png 760x428+120+120 10_sogdian_merchant_and_guide.png
crop dunhuang_caravan_master.png 760x428+620+210 11_central_asian_woman_trader.png
crop dunhuang_caravan_master.png 900x506+700+120 12_bactrian_camels_and_oasis.png

# 品物は中継地で人から人へ渡った
frame goods_relay_market_master.png 13_relay_market_wide.png
crop goods_relay_market_master.png 820x461+20+180 14_silk_changes_hands.png
crop goods_relay_market_master.png 820x461+640+180 15_persian_glass_exchange.png
crop goods_relay_market_master.png 930x523+610+340 16_spices_coins_and_ledger.png
crop goods_relay_market_master.png 1050x591+250+80 17_many_merchants_one_network.png
tone goods_relay_market_master.png 18_goods_travel_by_relay.png 90,101,102 '#2b2435'

# 砂漠、オアシス、山岳路を越える
frame desert_mountain_routes_master.png 19_desert_oasis_mountain_wide.png
crop desert_mountain_routes_master.png 760x428+0+140 20_taklamakan_water_skins.png
crop desert_mountain_routes_master.png 820x461+420+170 21_oasis_well_rest.png
crop desert_mountain_routes_master.png 800x450+840+120 22_tianshan_local_guide.png

# 仏教は翻訳・巡礼・美術を通じて伝わった
frame buddhist_transmission_master.png 23_dunhuang_translation_wide.png
crop buddhist_transmission_master.png 850x478+160+300 24_monk_and_translator.png
crop buddhist_transmission_master.png 900x506+700+100 25_mural_artisans_adapt_motifs.png
crop buddhist_transmission_master.png 760x428+0+130 26_pilgrims_enter_cave.png

# イスラムの拡大には交易と政治的変化の双方があった
frame islam_central_asia_master.png 27_central_asian_courtyard_wide.png
crop islam_central_asia_master.png 900x506+80+270 28_scholar_and_local_residents.png
crop islam_central_asia_master.png 760x428+820+30 29_trade_and_city_community.png
tone islam_central_asia_master.png 30_gradual_cultural_transition.png 92,101,102 '#1f3042'

# 言語、音楽、ガラス、織物の技法も交換された
frame language_art_exchange_master.png 31_language_art_workshop_wide.png
crop language_art_exchange_master.png 780x439+0+260 32_merchant_and_scribe.png
crop language_art_exchange_master.png 760x428+440+220 33_glassblower_and_musician.png
crop language_art_exchange_master.png 760x428+850+260 34_textile_motifs_shared.png

# 紙づくりは各地で受け継がれ、改良された
frame samarkand_papermaking_master.png 35_samarkand_paper_workshop.png
crop samarkand_papermaking_master.png 760x428+0+230 36_rag_fibres_beaten_to_pulp.png
crop samarkand_papermaking_master.png 780x439+420+210 37_mould_screen_lifts_sheet.png
crop samarkand_papermaking_master.png 820x461+780+120 38_press_and_drying_sheets.png

# サマルカンド、バグダード、ヨーロッパへ続く長い連鎖
frame paper_learning_chain_master.png 39_paper_learning_chain_wide.png
crop paper_learning_chain_master.png 720x405+0+130 40_paper_delivery_and_scholars.png
crop paper_learning_chain_master.png 720x405+480+160 41_geometry_and_binding.png
crop paper_learning_chain_master.png 720x405+950+130 42_european_codex_shelves.png

# 現代に残るネットワークと、静かな余韻
frame modern_student_silkroads_master.png 43_student_at_silkroads_museum.png
crop modern_student_silkroads_master.png 1050x591+300+160 44_museum_objects_connect.png
crop modern_student_silkroads_master.png 980x551+520+20 45_route_relief_and_student.png
frame desert_wind_legacy_master.png 46_desert_wind_legacy_wide.png
crop desert_wind_legacy_master.png 900x506+120+260 47_centuries_of_tracks.png
crop desert_wind_legacy_master.png 760x428+880+260 48_paper_glass_and_waymarker.png
crop desert_wind_legacy_master.png 900x506+590+60 49_oasis_ruins_and_pass.png
crop desert_wind_legacy_master.png 760x428+0+80 50_distant_caravan_final.png

expected=(
  01_network_table_wide.png 02_branching_land_routes.png
  03_western_land_and_sea.png 04_eastern_land_and_sea.png
  05_hands_build_network.png 06_maritime_routes_and_ports.png
  07_network_not_single_road.png 08_eurasia_exchange_network.png
  09_dunhuang_caravan_dawn.png 10_sogdian_merchant_and_guide.png
  11_central_asian_woman_trader.png 12_bactrian_camels_and_oasis.png
  13_relay_market_wide.png 14_silk_changes_hands.png
  15_persian_glass_exchange.png 16_spices_coins_and_ledger.png
  17_many_merchants_one_network.png 18_goods_travel_by_relay.png
  19_desert_oasis_mountain_wide.png 20_taklamakan_water_skins.png
  21_oasis_well_rest.png 22_tianshan_local_guide.png
  23_dunhuang_translation_wide.png 24_monk_and_translator.png
  25_mural_artisans_adapt_motifs.png 26_pilgrims_enter_cave.png
  27_central_asian_courtyard_wide.png 28_scholar_and_local_residents.png
  29_trade_and_city_community.png 30_gradual_cultural_transition.png
  31_language_art_workshop_wide.png 32_merchant_and_scribe.png
  33_glassblower_and_musician.png 34_textile_motifs_shared.png
  35_samarkand_paper_workshop.png 36_rag_fibres_beaten_to_pulp.png
  37_mould_screen_lifts_sheet.png 38_press_and_drying_sheets.png
  39_paper_learning_chain_wide.png 40_paper_delivery_and_scholars.png
  41_geometry_and_binding.png 42_european_codex_shelves.png
  43_student_at_silkroads_museum.png 44_museum_objects_connect.png
  45_route_relief_and_student.png 46_desert_wind_legacy_wide.png
  47_centuries_of_tracks.png 48_paper_glass_and_waymarker.png
  49_oasis_ruins_and_pass.png 50_distant_caravan_final.png
)
for file in $expected; do
  test -s "$OUT/$file"
done
echo "H042 final_style01 files verified: ${#expected[@]}"
