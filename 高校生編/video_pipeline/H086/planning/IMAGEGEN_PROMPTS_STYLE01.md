# H086 ImageGen prompts — 画風01

生成方法: Codex内蔵ImageGen。H15 Style01参照画と、直前に採用したH086人物・施設画を連続性参照として使用。

共通指定: 16:9、1672×941。高校生向けの精密な劇場アニメ風2Dイラスト、成熟した人体比率、柔らかな水彩質感、群青・青緑・琥珀を基調にした自然光、架空の地方日本都市。人物・手続・証拠物は上部から中央へ置き、下18%は暗く低情報の字幕余白。写真、3D、油彩、分割画面、コラージュ、読める文字、ロゴ、国旗、透かし、巨大な天秤なし。

固定人物: 42歳女性裁判官（顎丈の黒髪、法廷は無地の黒い法服、庁内は紺のスーツ）、17歳男子生徒（短い黒髪、紺の学生コート、灰色ノート）、38歳男性弁護人（短い黒髪、灰色スーツ、深緑ファイル）、34歳女性記者（肩までの濃茶髪、えんじ色ジャケット、帆布鞄）、51歳社会復帰当事者（短い黒灰髪、簡素な作業着、出所後は茶色ジャケット）、45歳女性相談員（短い黒髪、青緑カーディガン、紺のケース）。同じ人物の年齢・髪・服・小物を場面間で保つ。

内容規約: 法の支配を強い警察や厳罰だけで表さない。ローマを唯一の起源にしない。腐敗は現金を渡す悪役ではなく、調達・利益相反・監査で示す。判決前の有罪視、受刑者の番号・鎖・尊厳を損なう表現を避ける。更生は教育・健康・住居・家族・技能・仕事・継続支援を本人中心で描く。市民参加は傍聴、法教育、公文書、調査報道、安全な通報、平和的集会、公開会議で示す。改革は当事者の声、証拠、審議、周知、実装までを描く。

## 採用プロンプト集合

1. `civic_courthouse_dawn_master`: 夜明けの裁判所と公共交通広場。法と社会の静かな導入。
2. `courthouse_public_entrance_master`: スロープと案内職員のある誰でも入れる公共の司法入口。
3. `equal_service_counter_master`: 障害や年齢に応じた配慮を備えた平等な法的支援窓口。
4. `judge_citizens_same_law_master`: 裁判官・市民・公務員が同じ手続資料を確認する場面。
5. `rule_of_law_all_accountable_master`: 公人・私人・組織の説明責任を対等な円卓で表現。
6. `public_private_state_accountability_detail_master`: 国家自身を含む責任を公文書と監査資料で具体化。
7. `independent_adjudication_courtroom_master`: 女性裁判官が証拠に基づき独立して審理する公開法廷。
8. `legal_equality_access_master`: 弁護・通訳・車椅子アクセスを含む法の下の平等。
9. `ancient_rome_forum_law_custom_master`: 古代ローマの広場で法慣習を相談する市民。
10. `roman_civil_hearing_master`: 土地や取引の民事紛争を証拠物で審理する場面。
11. `legal_traditions_across_centuries_master`: 複数の時代と地域の法伝統を資料で継承する場面。
12. `modern_constitution_archive_master`: 現代の憲法資料を市民と専門職が閲覧する公的保存庫。
13. `constitutional_hierarchy_review_master`: 憲法と他の法令の関係を階層模型で比較。
14. `constitutional_court_review_detail_master`: 法令審査を条文束・事例・公開記録で示す。
15. `rule_of_law_fragile_institutions_master`: 窓口閉鎖と記録欠落で制度の脆弱さを示す。
16. `inaccessible_justice_counter_master`: 高い窓口・階段・不明瞭な手順による司法アクセス障壁。
17. `arbitrary_order_closed_office_master`: 閉じた部屋で理由なく命令が変更される恣意的手続。
18. `civil_society_documents_failure_master`: 記者と市民が制度不備を写真・記録・聞き取りで残す。
19. `corruption_procurement_backroom_master`: 調達の利益相反と不透明な選定を示す。
20. `anti_corruption_audit_trail_master`: 物品・記録・承認の監査証跡を複数人で確認。
21. `judge_receives_pressure_master`: 裁判官への政治的圧力を閉じた執務室で示す。
22. `judicial_colleagues_independence_master`: 同僚・制度・記録が独立判断を守る場面。
23. `open_courtroom_independent_decision_master`: 圧力を離れ、公開法廷で判断を示す。
24. `arrest_rights_and_counsel_master`: 逮捕後に権利カードを説明し弁護人へつなぐ。
25. `evidence_review_fair_trial_master`: 検察・弁護・裁判官が同じ証拠を検討する公正な裁判。
26. `guilty_verdict_due_process_master`: 適正手続を経た落ち着いた有罪判断。
27. `humane_prison_admission_master`: 健康・連絡・相談を確認する尊厳ある入所手続。
28. `punishment_purpose_review_master`: 安全・責任・更生・社会復帰の目的を多職種で検討。
29. `correctional_education_class_master`: 成人学習者が本と幾何模型で学ぶ明るい教育教室。
30. `rehabilitation_counseling_master`: 本人が健康・住居・学習・家族・仕事を選ぶ個別相談。
31. `restorative_reentry_planning_master`: 身分証・鍵・医療・技能・家族・交通・仕事の出所準備。
32. `former_prisoner_identity_housing_master`: 出所後に本人が身分書類と住居を選ぶ公共窓口。
33. `vocational_reentry_workshop_master`: 地域の職業教室で自転車修理と木工を学ぶ。
34. `community_mentor_employment_master`: 地域事業所で有給試行業務と勤務予定を確認。
35. `recidivism_prevention_support_master`: 本人主導で住居・健康・仕事・家族支援を調整。
36. `citizens_court_observation_master`: 生徒と多様な市民が公開法廷を傍聴。
37. `local_legal_literacy_workshop_master`: 弁護人と市民が生活上の法的場面をカードで学ぶ。
38. `public_records_access_master`: 記者・生徒・市民が物理記録と端末を閲覧。
39. `community_rule_of_law_responsibility_master`: 市民と専門職が日常の公正な手続を話し合う。
40. `wrongdoing_reporting_safe_channel_master`: 独立相談員、投書箱、プライバシー端末による安全な通報。
41. `investigative_journalism_verification_master`: 記者が公文書・現物・複数証言を慎重に裏取り。
42. `peaceful_civic_transparency_demand_master`: 市民が裁判所前で平和的に透明性を求める集会。
43. `open_budget_public_meeting_master`: 学校・医療・交通・住居の模型を使う公開予算会議。
44. `law_as_social_promise_master`: 教師・看護師・労働者・裁判官・生徒が権利と責任を共有。
45. `public_services_equal_procedure_master`: 医療・住居・許可・家族支援の共通手続と合理的配慮。
46. `reform_evidence_hearing_master`: 当事者・研究者・現場職が証拠を示す公開聴聞。
47. `impacted_people_law_consultation_master`: 障害者・介護者・労働者・若者・当事者中心の相談。
48. `legislature_revision_deliberation_master`: 架空の地方議会が証拠と修正案を公開審議。
49. `accessible_promulgation_implementation_master`: 点字・音声・絵カードと職員研修による周知・実装。
50. `free_just_society_daily_life_master`: 学校・診療所・交通・市場・仕事で公正さが続く日常。
51. `courthouse_evening_finale_master`: 夕方の裁判所と帰路につく市民で静かに終幕。

採用51枚を140カットへ展開。各マスターは最低2回、長い区間は最大5回使用し、切替間隔を1.0〜1.5秒に収める。
