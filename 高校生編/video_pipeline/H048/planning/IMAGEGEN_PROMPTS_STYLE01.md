# H048 ImageGen 最終プロンプト設計

共通: `modern-media-literacy documentary` / 16:9 / 画風01「光彩・劇場アニメ背景」 / 同じ架空の海辺の都市 / H15基準の同じ17歳男子高校生 / 同じ青緑色ボトル / 下45%字幕余白 / 読める文字・価格・ロゴなし。

1. `advertising_agency_strategy_master` — 現実的な広告会社の夕方。corporation担当者と小規模な制作チームが、文字のない絵コンテと同じ青緑色ボトルを見ながらbrandを知らせるadvertisingを計画する。男子高校生は広告の対象を考える参考人物として窓外の街に小さく見える。
2. `multi_media_ad_exposure_master` — 同じ男子高校生の家庭と通学路を一つの連続空間として描き、テレビ、新聞、雑誌、ノートPC、街頭画面など複数mediaから同じ商品のadvertisementsが届く。画面は抽象的な商品写真だけで文字なし。
3. `attention_persuasion_master` — 清潔な生活用品店。目立つが文字のない商品展示がconsumerである男子高校生のattentionを引き、手を伸ばす前に比較する様子。広告のpersuade作用を姿勢と視線で示し、強制や催眠にしない。
4. `brand_image_vs_quality_master` — 一つの実物商品を中央に置き、左で美しく演出されたbrand image、右で技術者が耐久性・漏れ・素材を確認するproduct quality、手前で男子高校生が双方を比較してchoiceを考える。
5. `social_media_opinions_master` — 放課後の図書館やカフェで、多様なconsumersがスマートフォンから商品のopinionsをsocial mediaへbroadcastする。画面は商品写真、非言語リアクション、共有記号だけで本文やロゴなし。
6. `viral_negative_opinion_master` — 青緑色ボトルのふたから漏れる欠陥を写した一件のnegative opinionが、数時間で複数端末へ共有され、同時にcorporation広報チームが事実を確認する。攻撃的な群衆、個人晒し、読める投稿なし。
7. `consumer_protection_regulation_master` — 落ち着いた消費者行政の会議室。governments側の職員、消費者代表、企業担当者が、誤解を招き得る広告画像と無地の資料を審査しregulationsを確認する。特定国の紋章や法律名なし。
8. `health_claim_evidence_master` — 公的な研究施設。研究者が文字のない健康関連商品のclaimを、測定器、対照サンプル、無地のグラフ、研究資料などsolid evidenceと照合する。薬、患者、治療、万能効能は描かない。
9. `corporation_consumer_state_triangle_master` — 三角形に配置した現実的な円卓で、corporation担当者、consumers代表、stateの規制担当者が同じ商品と資料を互いに確認する。照明と視線で三者関係を示し、発光図形や空中UIを使わない。
10. `critical_media_literacy_master` — 同じ男子高校生が購入前に立ち止まり、実物商品、広告画像、第三者の品質資料、複数の情報源を順に比較する。critical eyeを冷静な確認動作として描き、不信や恐怖の表情にしない。
11. `critical_eye_final_master` — 夕暮れの海辺の街。広告面が静かに灯る中、同じ男子高校生が店を出て商品を急いで買わず、情報を確かめたうえで自分のchoiceをする余韻。群青と琥珀の光、安定した横長構図。

実行方式: 組み込みImageGen。選定画像は `scenes/character_refs/` に保存し、寄り画・クロップ・明度調整で約55カットへ展開する。
