# H089 ImageGen prompts — 画風01

生成方法: Codex内蔵ImageGen。H15系統の画風と、先に採用したH089場面を人物・架空都市・公共施設の連続性参照として使用。

共通指定: 16:9、1672×941。精密な劇場アニメ風2D線画、現実的な成人の人体比率、群青・青緑と琥珀色の光、微細なフィルム粒子。実在国・実在政党を特定しない現代の架空連邦民主都市。画像内に読める文字・数字・国旗・党章・候補名・ロゴ・透かしなし。

固定人物: 19歳の成人有権者（顎丈の黒髪、青緑ジャケット、白シャツ、濃紺パンツ、生成りショルダーバッグ）、46歳の無党派選挙事務職員（短い黒灰髪、丸眼鏡、生成りシャツ、濃紺ベスト）、同じ高さ・同じ照明・同じ画面比率で扱う三候補（48歳女性・深緑、52歳男性・錆色、39歳女性・紺）、45歳の琥珀色ジャケットの小政党代表。

固定舞台・資料: 石造市庁舎、市民会館の投票所、図書館の政策討論会、ガラス張りの開票所、円形議場、行政庁舎、地域集会室。無地の投票用紙、抽象的な丸印と色カード、無文字の政策模型、封印箱、透明な開票トレーを使い、投票先は見せない。

内容規約: 候補の善悪を色・性別・人種・光で分けない。秘密投票とアクセシビリティを守る。coalitionとcompromiseは公開協議として描く。若者の低参加を怠惰や人格欠陥にせず、仕事・距離・情報アクセス・関心の薄さを含む複合要因として描く。選挙だけを民主主義の全てにせず、集会・請願・報道・監視・地域活動も含める。自由で真正な選挙がない社会は架空・非特定とし、権利擁護は平和的に描く。

## 採用プロンプト集合

1. `democratic_city_morning_master`: 架空民主都市の朝。
2. `neutral_election_preparations_master`: 無党派の選挙準備。
3. `citizens_approach_polling_place_master`: 多様な成人市民が投票所へ向かう。
4. `fundamental_civic_act_ballot_master`: 秘密を守って投票箱へ入れる基本的市民行為。
5. `secret_ballot_booth_master`: 視線を遮る無地の記載台。
6. `accessible_polling_queue_master`: 車椅子利用者を含むアクセシブルな投票所。
7. `ballot_box_and_neutral_workers_master`: 無党派職員と封印投票箱。
8. `three_candidates_equal_platform_master`: 三候補を対等に扱う公開壇上。
9. `candidate_agenda_community_forum_master`: 無文字の政策模型によるagenda説明。
10. `healthcare_policy_issue_master`: 医療の争点模型。
11. `education_policy_issue_master`: 教育の争点模型。
12. `economy_policy_issue_master`: 経済の争点模型。
13. `environment_policy_issue_master`: 環境の争点模型。
14. `candidate_issue_emphasis_comparison_master`: 候補ごとの重点を同じ条件で比較。
15. `voters_compare_blank_platform_cards_master`: 市民が無文字の政策カードを比較。
16. `no_single_party_majority_model_master`: 単独majorityがない議席構成模型。
17. `transparent_vote_count_observers_master`: 透明な開票と複数監視員。
18. `several_parties_begin_coalition_talks_master`: 複数政党が公開協議を開始。
19. `coalition_public_responsibility_agreement_master`: 権力と責任の分担。
20. `coalition_compromise_roundtable_master`: 対等な円卓でのcompromise。
21. `shared_policy_tradeoff_models_master`: 政策調整を模型で可視化。
22. `elected_leader_appoints_cabinet_master`: 選出指導者が多様な閣僚をappoint。
23. `diverse_cabinet_members_master`: 公共の場に立つcabinet。
24. `federal_departments_public_services_master`: 制度例としてのfederal departments。
25. `bill_reviewed_in_legislative_committee_master`: 法案を立法委員会で審議。
26. `legislature_floor_debate_master`: 円形議場での公開討論。
27. `legislative_approval_and_public_record_master`: approvalと公開記録。
28. `declining_interest_empty_civic_forum_master`: 空席が増えた市民フォーラム。
29. `sparse_polling_place_turnout_master`: 低いturnoutを静かに示す投票所。
30. `young_adults_ignore_politics_cafe_master`: 若い成人が政治から距離を置く日常。
31. `young_voter_work_and_access_barriers_master`: 仕事・時間・移動の参加障壁。
32. `missed_opportunity_after_poll_closes_master`: 閉所後に失われた参加機会を見つめる。
33. `many_ballots_shape_council_result_master`: 多数の選択が議席構成を形づくる。
34. `democracy_through_citizen_participation_master`: 投票・会議・報道・地域活動を行う成人市民。
35. `participation_beyond_election_master`: 集会・請願・報道・監視。
36. `fictional_country_without_genuine_election_master`: 自由で真正な選挙がない架空社会。
37. `closed_polling_hall_and_locked_ballot_master`: 閉ざされた投票機会。
38. `peaceful_voting_rights_advocates_master`: 平和的な投票権advocate。
39. `inclusive_universal_adult_suffrage_master`: 多様な成人に開かれた投票。
40. `imperfect_election_observers_review_master`: 選挙の欠点を監視・改善する市民。
41. `accessible_ballots_as_crucial_tool_master`: 車椅子利用者と視覚障害者に対応した投票。
42. `peaceful_transfer_and_open_council_master`: 公開議会での平和的な権力移行。
43. `democratic_civic_life_continues_master`: 選挙後も続く市民参加の夕景。

採用43枚を116カットへ展開。各基準画は最低2回使い、切替間隔を0.648〜1.500秒に収めた。TacoBeat実測17行と43の意味時点を照合し、投票、政策比較、連立、行政・立法、参加低下、投票権、継続的市民参加の順序を固定した。
