# H090 ImageGen prompts — 画風01

生成方法: Codex内蔵ImageGen。H15系統の画風と、先に採用したH090場面を人物・理科室・安全な実験装置の連続性参照として使用。

共通指定: 16:9、1672×941。精密な劇場アニメ風2D線画、自然な人体比率、群青の影と朝夕の琥珀色光。画像内に読める文字・数字・数式・学校名・企業名・ロゴ・透かしなし。主要な顔、手、測定器、結果は下部字幕帯を避ける。

固定人物: 黒髪ポニーテール・濃紺ブレザー・苔色リボンの17歳女子、短いくせ毛・茶色カーディガンの17歳男子、褐色肌・細い編み込み髪・濃紺カーディガンの17歳女子、短い波状黒髪・生成りブラウス・炭色パンツの38歳女性理科教員。終盤の研究者は成人チームとし、個人の天才でなく共同作業を描く。

固定実験: 炎を使わない安全な金属熱伝導比較。同じ長さ・太さの金属棒、同じ深さの温水槽、クランプ、接触温度センサー、保護眼鏡、耐熱手袋、こぼれ受けを使う。変える要因は金属の種類だけで、寸法、初期温度、浸す深さ、測定時間をそろえる。炎、沸騰水、赤熱金属、危険薬品、危険な回路操作は描かない。

内容規約: 科学的方法を一度で真理へ至る一本道にせず、問い、仮説、統制、測定、分析、支持・反証、再設計、反復、共有、査読が循環する過程として描く。支持されない結果も有用とし、暫定的結論を「何も確かでない」という相対主義にしない。教員は答えを与える救世主でなく、安全確認と問い返しを支える。

## 採用プロンプト集合

1. `science_school_morning_master`: 架空高校と理科室の朝。
2. `students_notice_everyday_patterns_master`: 日常現象を見る科学部。
3. `question_wall_without_words_master`: 無文字の疑問カード。
4. `scientific_inquiry_begins_question_master`: 探究は問いから始まる。
5. `teacher_returns_question_master`: 教員が問い返す。
6. `blue_sky_rooftop_question_master`: 青い空への疑問。
7. `safe_light_scattering_model_master`: 光散乱の抽象模型。
8. `metal_conducts_heat_question_master`: 金属の熱伝導への疑問。
9. `warm_spoon_everyday_observation_master`: 日常の温かい金属の観察。
10. `everyday_doubt_seed_of_science_master`: 日常の疑問にある科学の種。
11. `students_choose_heat_question_master`: 検証する問いを選ぶ。
12. `students_form_heat_hypothesis_master`: 仮説を立てる。
13. `prediction_model_before_test_master`: 測定前の予測模型。
14. `experiment_design_roundtable_master`: 実験設計の協議。
15. `safe_protocol_sequence_icons_master`: 無文字の安全手順。
16. `conditions_carefully_determined_master`: 条件を慎重に決める。
17. `equipment_prepared_with_ppe_master`: 器具と保護具を準備。
18. `equal_metal_rods_apparatus_master`: 同寸法の金属棒と温水槽。
19. `control_factors_overview_master`: 影響要因を統制。
20. `equal_length_diameter_check_master`: 長さと太さをそろえる。
21. `equal_start_temperature_check_master`: 初期温度と深さをそろえる。
22. `one_factor_material_changed_master`: 金属種類だけを変える。
23. `rest_kept_constant_wide_master`: 他条件を一定に保つ。
24. `temperature_sensors_record_master`: センサーで記録。
25. `distinguish_cause_comparison_master`: 原因を比較で見分ける。
26. `repeat_measurement_uncertainty_master`: 反復測定とばらつき。
27. `obtained_data_analyzed_master`: 得られたデータを分析。
28. `abstract_graph_patterns_master`: 無文字グラフの傾向。
29. `data_compared_with_hypothesis_master`: データと仮説を比較。
30. `supported_hypothesis_further_test_master`: 支持後も追加検証。
31. `second_group_replication_master`: 別班による再現確認。
32. `expanded_material_range_test_master`: 材料範囲を広げる安全な追加試験。
33. `rejected_hypothesis_useful_result_master`: 反証も有用な結果。
34. `seek_new_explanation_master`: 新しい説明を探す。
35. `temporary_conclusion_board_master`: 結論は暫定的。
36. `peer_review_school_seminar_master`: 仲間の質問と査読。
37. `established_theory_layered_model_master`: 確立理論と蓄積証拠。
38. `new_evidence_unexpected_pattern_master`: 新証拠の予想外の傾向。
39. `rewrite_explanatory_model_master`: 証拠で説明模型を改訂。
40. `repeated_scientific_cycle_master`: 反復する科学過程。
41. `progress_through_shared_evidence_master`: 共有証拠による進歩。
42. `students_present_to_public_lab_master`: 結果と限界を公開共有。
43. `adult_biology_research_team_master`: 成人の生物研究チーム。
44. `biology_components_examined_master`: 生物試料の構成を安全に確認。
45. `adult_electronics_engineering_team_master`: 成人の電子工学チーム。
46. `electronic_components_examined_master`: 電子部品を慎重に確認。
47. `safe_compound_properties_lab_master`: 化合物の性質を安全に観察。
48. `elaborate_research_documentation_master`: 詳細な記録と共有。
49. `intelligence_never_ceases_to_doubt_master`: 疑い続ける知性。
50. `open_seminar_questions_master`: 結論から新しい問いへ。
51. `student_returns_to_night_sky_master`: 夜空の問いへ戻る。
52. `science_school_dawn_finale_master`: 次の探究へ向かう夜明け。

採用52枚を129カットへ展開。各基準画は最低2回使い、切替間隔を0.735〜1.500秒に収めた。TacoBeat実測18行・197語と52の意味時点を照合し、問い、仮説、安全な比較実験、統制、分析、反証、再検証、共有、他分野、新しい問いの順序を固定した。
