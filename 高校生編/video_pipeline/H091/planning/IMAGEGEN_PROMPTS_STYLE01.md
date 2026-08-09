# H091 ImageGen prompts — 画風01

生成方法: Codex内蔵ImageGen。先に採用したH091場面を、主人公・衣装・鞄・宿主夫婦・村・宿の連続性参照として使用。

共通指定: 16:9、1672×941。精密な劇場アニメ風2D線画、自然な人体比率、南ヨーロッパの自然光と群青の影。画像内に読める文字・数字・店名・価格・ロゴ・旗・透かしなし。主要な顔、手、食物、小道具は下部字幕帯を避ける。

固定主人公: 22歳の成人日本人女性。あごまでの黒いボブ、短いオリーブ色旅行ジャケット、アイボリーのブラウス、細い錆色のスカーフ、濃紺のパンツ、茶色の歩きやすい靴。補修布が一つある使い込んだテラコッタ色のキャンバス製バックパックと、無地の紺色ノートを持つ。

固定宿主夫婦: 70歳の女性は銀髪の低いまとめ髪、青緑のカーディガン、アイボリーのエプロン。73歳の男性は短い銀灰色の髪と整えた口ひげ、水色のシャツ、栗色のベスト。主人公と対等な日常の交流として描く。

内容規約: 一人旅を危険行動として描かず、駅・港・列車・道・バルコニーで安全な距離と設備を示す。地域住民、店、漁業、食文化を観光クリシェや「異国情緒」の誇張にしない。貧困・救済物語へ置き換えず、外部の旅行者を救世主化しない。バルコニーでは胸高の丈夫な手すりを描き、身を乗り出させない。

## 採用プロンプト集合

1. `graduation_week_morning_master`: 大学卒業翌週、旅立ち前の静かな朝。
2. `university_graduation_memory_master`: 卒業の記憶。
3. `packing_room_master`: 実用的な旅支度。
4. `worn_backpack_ready_master`: 補修布のあるバックパック。
5. `leaving_home_door_master`: 自宅を出る瞬間。
6. `set_off_alone_master`: 成人女性が自分で旅立つ。
7. `safe_airport_terminal_master`: 安全で落ち着いた空港。
8. `airplane_window_southern_light_master`: 南へ向かう機窓の光。
9. `southern_europe_arrival_master`: 南ヨーロッパ到着。
10. `cheap_ticket_and_backpack_master`: 安い航空券と使い込んだ鞄。
11. `worn_backpack_strap_close_master`: 補修された肩紐への寄り。
12. `barcelona_old_quarter_entrance_master`: バルセロナ旧市街への入口。
13. `bare_stone_walls_master`: 装飾の少ない石壁。
14. `narrow_lanes_master`: 狭い路地。
15. `maze_intersection_master`: 迷路のような分岐。
16. `footsteps_on_stone_master`: 石畳を歩く足元。
17. `echo_against_walls_master`: 壁に響く足音。
18. `traveler_listens_to_echo_master`: 響きへ耳を澄ます主人公。
19. `small_craft_shop_master`: 小さな工芸店。
20. `local_artisan_hands_master`: 地元職人の手仕事。
21. `folk_music_bar_master`: 穏やかな民俗音楽の店。
22. `mediterranean_harbor_wide_master`: 地中海沿岸の港。
23. `dozen_fishing_boats_master`: 並んだ十数隻の漁船。
24. `fishing_nets_and_ropes_master`: 安全な位置から見る網とロープ。
25. `harbor_to_market_walk_master`: 港から市場へ歩く。
26. `barcelona_market_wide_master`: バルセロナの公共市場。
27. `fresh_bread_stall_master`: 焼きたてのパン売り場。
28. `rich_spice_stall_master`: 豊かな色の香辛料売り場。
29. `scent_in_market_air_master`: パンと香辛料の香りを感じる。
30. `appetite_awakened_master`: 市場の軽食で食欲を表す。
31. `train_south_departure_master`: 安全に南行き列車へ乗る。
32. `train_window_coast_master`: 地中海沿岸の車窓。
33. `whitewashed_village_arrival_master`: 架空の白壁の村へ到着。
34. `small_inn_entrance_master`: 家族経営の小さな宿。
35. `elderly_couple_greeting_master`: 宿主夫婦の自然な出迎え。
36. `generous_dinner_served_master`: 家庭料理を囲む準備。
37. `shared_dinner_table_master`: 三人が対等に食卓を囲む。
38. `warm_kitchen_after_dinner_master`: 食後の協力。
39. `old_inn_furniture_master`: 古い木製家具のある客室。
40. `furniture_well_kept_master`: 丁寧に手入れされた机と椅子。
41. `quiet_inn_night_master`: 主人公ひとりの静かな夜。
42. `last_morning_balcony_master`: 最後の朝、ひとりで海を見る。
43. `sea_from_balcony_master`: 手すり越しの広い海景。
44. `traveler_reflects_by_sea_master`: 海を見ながら旅を振り返る。
45. `gentle_wind_balcony_master`: スカーフを揺らす優しい風。
46. `leisure_tea_master`: テラスでの穏やかな余暇。
47. `quiet_village_walk_master`: 暮らしのある村を静かに歩く。
48. `seeking_on_journey_master`: 安全な分かれ道で考える。
49. `trip_taught_something_master`: 旅から得た気づき。
50. `farewell_to_innkeepers_master`: 宿主夫婦への感謝と別れ。
51. `friendly_world_encounters_master`: 旅先の人々との自然な挨拶。
52. `broader_landscape_master`: 地図より広い世界を示す海岸景観。
53. `return_journey_train_master`: 帰りの列車で旅を振り返る。
54. `open_horizon_finale_master`: 車窓の海と開けた水平線。

採用54枚を132カットへ展開。各基準画は最低2回使用し、切替間隔を0.632〜1.500秒に収めた。TacoBeat実測15行・178語と54の意味時点を照合し、卒業後の旅立ち、旧市街、港、市場、列車、白壁の村、宿、海辺の朝、別れ、帰路の順序を固定した。
