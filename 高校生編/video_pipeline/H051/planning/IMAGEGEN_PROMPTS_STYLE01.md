# H051 ImageGen 最終プロンプト設計

共通: `AI technology and ethics documentary` / 16:9 / 画風01「光彩・劇場アニメ背景」 / 精密な2D線画とセル塗り人物 / 群青の影と自然な暖色光 / 下45%字幕余白 / 読める文字・数字・ロゴなし。現代場面はH15基準の17歳男子と、濃紺ジャケット・低く束ねた黒髪の40歳前後の女性AI研究者で連続させる。人型ロボット、ホログラム、過剰なネオンなし。

1. `ai_progress_data_master` — 10年前の小規模な研究室から現在の現実的なサーバー室・GPUワークステーション・研究チームへ一方向に進み、artificial intelligenceのprogressとvast dataを示す。
2. `ai_support_fields_master` — 同じ研究者と男子高校生が、病院、金融の不正検知、交通管制を用途別の通常画面で見学し、algorithmsが人間をsupportする三分野を結ぶ。
3. `diagnostic_assistance_master` — 医師、放射線技師、研究者が匿名化された医療画像と複数検査を比較し、AI候補を確認する。診断の最終判断は医師と患者の対話に残す。
4. `self_driving_test_master` — 閉鎖された試験コースのセンサー搭載車。安全運転者、遠隔監視、道路標示、歩行者ダミーを置き、限定条件のself-drivingを示す。
5. `natural_language_processing_master` — 学校と公共窓口で、音声文字化、翻訳、要約を人間が確認して使う。正誤を見直す研究者と高校生を描き、魔法の会話機械にしない。
6. `automation_labor_master` — 工場の協働ロボット、停止ボタン、監督・保守、再訓練中の作業者を同じindustry内に描き、automationでlaborの風景が変わる様子を示す。
7. `privacy_jobs_misinformation_master` — consentの確認、匿名化されたdata保管、求人縮小を心配する労働者、同じ偽画像が推薦で広がり検証者が止める流れを一つの倫理監査室で結ぶ。
8. `consequences_society_master` — 市民、技術者、労働者、医師、若者、行政が円卓でbenefitとriskを具体的資料から検討し、societyがconsequencesへ正面から向き合う。
9. `algorithm_responsibility_master` — 開発者、data担当、提供企業、導入組織、現場運用者、監査担当が同じalgorithmの記録と決定経路を追い、responsibilityが分散することを示す。
10. `self_driving_accident_court_master` — 衝突そのものは見せず、損傷した試験車のセンサー記録、道路状況、運転監視、整備履歴を法廷で検討。裁判官、専門家、関係者がaccountabilityを争う。
11. `unanswered_questions_master` — 研究者と高校生が、責任、bias、privacy、安全、説明可能性を示す無文字の資料を前に、complete answersのない問いを考える静かな夜の研究室。
12. `government_regulations_master` — 複数国の行政官、技術者、市民団体、企業、研究者がAIのregulationsを作る公聴会。禁止・高risk・透明性・低riskを異なる無地フォルダーで整理する。
13. `eu_ai_act_master` — 現代の欧州議会風の会議室。EUのrisk-based comprehensive lawを、段階の異なる無地の規制資料、適合確認、権利保護、innovation試験で示す。全施行完了の祝賀にしない。
14. `human_judgment_final_master` — 同じ男子高校生、女性研究者、医師、作業者、市民が、AI出力を鵜呑みにせず根拠を比較して共同判断する教室兼ラボ。AIが人間の代わりではなく、よりよく考えるための道具になる夜明けの結末。

実行方式: 組み込みImageGen。選定画像は `scenes/character_refs/` に保存し、寄り画・クロップ・明度調整で約70カットへ展開する。
