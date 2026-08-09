# H088 ImageGen prompts — 画風01

生成方法: Codex内蔵ImageGen。採用済みH088場面を人物・屋敷・証拠の連続性参照として使用。

共通指定: 16:9、1672×941。精密な劇場アニメ風2D線画、現実的な人体比率、群青・青緑と琥珀色の光、微細なフィルム粒子。現代の架空地方日本都市に残る1920年代洋館。画像内に読める文字・数字・ロゴ・警察章・透かしなし。武器、流血、暴行、遺体、悪役的な外見誇張なし。

固定人物: 44歳男性検査官（短い黒髪、こめかみの白髪、濃紺スーツ、暗緑ネクタイ、炭色トレンチ、茶革の証拠ケース、手袋、懐中電灯）、58歳の屋敷主人（銀灰髪、細い眼鏡、濃緑カーディガン）、55歳の元共同経営者（濃茶髪、濃えんじ雨コート、茶革鞄）、52歳女性管理人（黒灰ボブ、ベージュのカーディガン）。

固定舞台・物証: 暗緑の急勾配屋根、黄褐色の石壁、真鍮照明、木造の長い廊下。ほぼ空の書斎には机、椅子、煉瓦で外側を塞がれた窓、床から天井までの固定棚。棚の後ろに狭い石造通路と地下室。物証は棚脚の擦れ、湿った赤土、えんじ色繊維、架空の事業資料、小さな真鍮の鍵カム部品。

内容規約: 密室の仕掛けや侵入方法を再現できる手順にしない。検査官は手袋と記録を用い、無謀に突入しない。主人は生存・無傷で尊厳を保って救出する。元共同経営者は、動機と複数物証がそろった後にだけ容疑者として示す。解決は格闘や私刑でなく、静かな事情聴取と公的手続で描く。

## 採用プロンプト集合

1. `storm_mansion_establishing_master`: 嵐の丘に立つ洋館の夜景。
2. `rain_on_mansion_roof_master`: 暗緑屋根を打つ雨。
3. `ceiling_beams_strange_vibration_master`: 天井梁と奇妙な振動。
4. `strange_sound_from_study_ceiling_master`: 主人が書斎の天井音を見上げる。
5. `study_pendant_and_plaster_dust_master`: 揺れる真鍮灯と落ちる粉。
6. `master_missing_from_study_master`: 管理人が主人の不在に気づく。
7. `empty_chair_and_warm_tea_master`: 空席とまだ温かい茶。
8. `door_locked_from_inside_master`: 内側から施錠された扉。
9. `window_blocked_by_brick_wall_master`: 外側を煉瓦壁で塞がれた窓。
10. `inspector_receives_report_master`: 検査官が通報を受ける。
11. `inspector_arrives_in_storm_master`: 嵐の洋館へ到着。
12. `long_corridor_walk_master`: 長い木造廊下を進む。
13. `inspector_enters_study_master`: 管理人と書斎へ入る。
14. `nearly_empty_study_wide_master`: ほぼ空の書斎全景。
15. `empty_desk_detail_master`: 机と空席を確認。
16. `fixed_wall_shelf_out_of_place_master`: 場違いな固定棚。
17. `fresh_floor_scrape_beneath_shelf_master`: 棚脚下の新しい擦れ。
18. `inspector_does_not_dismiss_clue_master`: 違和感をdismissしない検査官。
19. `gloved_hand_checks_shelf_edge_master`: 手袋で棚端を確認。
20. `shelf_reveals_hidden_passage_master`: 棚の後ろに入口が現れる。
21. `hidden_passage_entrance_master`: 狭い石造通路の奥行き。
22. `inspector_enters_passage_master`: 安全確認して中へ入る。
23. `dark_corridor_leads_underground_master`: 暗い通路が地下へ続く。
24. `stone_stairs_descent_master`: 石段を慎重に降りる。
25. `master_captured_alive_basement_master`: 主人を生存・無傷で発見。
26. `inspector_frees_master_master`: 軽い拘束を外して救出。
27. `master_indicates_captor_clue_master`: 主人が手掛かりを伝える。
28. `former_business_partner_revealed_master`: 元共同経営者が現れる。
29. `suspect_wet_coat_and_bag_master`: 濡れたえんじコートと革鞄。
30. `financial_dispute_documents_master`: 無文字の事業資料で金銭争いを示す。
31. `shared_business_ledger_models_master`: 共同事業と動機の模型。
32. `inspector_identifies_suspect_master`: 複数証拠から容疑者を特定。
33. `motive_evidence_mechanism_overview_master`: 動機・物証・鍵部品の全体像。
34. `physical_evidence_comparison_master`: 赤土とえんじ繊維を比較。
35. `discarded_brass_key_mechanism_master`: 捨てられた小さな鍵カム部品。
36. `evidence_points_to_partner_master`: 証拠の連鎖が元共同経営者を指す。
37. `case_resolved_procedural_escort_master`: 暴力のない公的な同行。
38. `master_safe_statement_master`: 安全な主人が事情を説明。
39. `truth_hidden_in_plain_sight_shelf_master`: 最初から見えていた棚の真相。
40. `corridor_shelf_truth_reconstruction_master`: 手順化しない安全な事件再構成。
41. `storm_clears_at_dawn_master`: 嵐が去る夜明けの洋館。
42. `inspector_departs_with_evidence_master`: 証拠ケースを持って退出。
43. `mansion_morning_finale_master`: 晴れた朝の静かな洋館。

採用43枚を118カットへ展開。各基準画は最低2回使い、切替間隔を0.706〜1.500秒に収めた。TacoBeat実測18行と43の意味時点を照合し、発端、密室、捜査、通路、救出、動機、物証、手続的解決、夜明けの順序を固定した。
