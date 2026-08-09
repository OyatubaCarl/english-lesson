# 中学生編 L2〜L10 sentence_v2

元データを残したまま、英文1文につき1枚の新規画像を用意して再構成した動画版。

## 方針

- 原本・旧版は変更しない。
  - Revid原動画: `taco_beat/videos/m2.mp4` 〜 `m10.mp4`
  - 直前のCodex版: `中学生編/mio_video_l2_l10/`
- 本版は `中学生編/mio_video_l2_l10_sentence_v2/` のみに保存する。
- 文法上の1文を単位に画像を切り替える。
  - 字幕上で引用文と `asked ...` が分かれている箇所は同じ画像を使う。
  - L3、L6、L8、L10にこの結合がある。
- 登場人物の人数を固定しない。英文を最もよく表す人物・物だけを置き、背景人物は意味を補う場合だけ使う。
- 場所、時間、計画／現実、前後の出来事と矛盾する描写は、人物の集合や既存構図より物語整合性を優先して直す。
- 写真、額縁、手紙などの小道具を定型的に使わない。英文理解に不要、または場面に不自然な連想を生む物は入れない。
- 顔・髪・年齢・体格を人物参照で固定し、服装は場面と季節に合わせて毎回指定する。
- カメラは1場面につき1種類の明確な動きにする。横パンは人物から人物へ分かる量で動かし、ズーム時は中心を固定する。小さな漂い・微小パン・パンとズームの同時使用は避ける。
- 英語の強調は赤への色変更だけとし、文字サイズ・横倍率・縦倍率を変えない。
- 元Revidの傾向を参考に、クロスフェードだけでなく方向ワイプ、円形、ぼかし、斜め、放射、ピクセル化などを混ぜる。
- Tomが登場する話では、Teacher TacosやFunnics Islandのキャラクターを窓外、掲示物、遠景などに小さく配置する。

## 画像数と動画

| Lesson | 真の英文数 | 新規画像数 | 出力動画 |
|---|---:|---:|---|
| L2 | 11 | 11 | `L2/output/l2_a_day_at_the_sea_sentence_v2_mio_bilingual_camera.mp4` |
| L3 | 10 | 10 | `L3/output/l3_a_rainy_afternoon_sentence_v2_mio_bilingual_camera.mp4` |
| L4 | 9 | 9 | `L4/output/l4_my_new_friend_tom_sentence_v2_mio_bilingual_camera.mp4` |
| L5 | 7 | 7 | `L5/output/l5_planning_to_visit_grandmother_sentence_v2_mio_bilingual_camera.mp4` |
| L6 | 8 | 8 | `L6/output/l6_grandmothers_birthday_sentence_v2_mio_bilingual_camera.mp4` |
| L7 | 9 | 9 | `L7/output/l7_my_future_dream_sentence_v2_mio_bilingual_camera.mp4` |
| L8 | 7 | 7 | `L8/output/l8_tomorrows_class_trip_sentence_v2_mio_bilingual_camera.mp4` |
| L9 | 8 | 8 | `L9/output/l9_a_school_day_sentence_v2_mio_bilingual_camera.mp4` |
| L10 | 10 | 10 | `L10/output/l10_the_mountain_promise_sentence_v2_mio_bilingual_camera.mp4` |
| 合計 | 79 | 79 | 9本 |

場面間の切り替えは合計70か所。各レッスンの先頭を除くすべてのShot間に設定している。

## 2026-07-31 整合性修正

- L3: 個別行動の背景に集合していた家族を除去。Mio、Saki、Kenta、Pochiをそれぞれ単独の部屋・一角にした。
- L3: 全員が主語になる導入と総括だけ、窓または壁で別室だと分かる家の外観・断面図を使用。
- L5: 全7場面を「下側＝金曜夜に姉妹が計画する現実」「上側＝光る雲形の吹き出しに浮かぶ明日の想像」の共通構成へ統一。
- L5: Scene 4を吹き出しの基準画像として維持し、Scene 1〜3・5〜7を同じ演出で再生成。
- L5: Scene 7の額入り祖母写真を完全に除去し、Mioが開いた手で未来の吹き出しを示す演出へ変更。祖母の喜びは吹き出し内だけで表現。
- 修正前のL3・L5一式は `_archive/` に保存。

## 服装の連続性

| 範囲 | 服装 |
|---|---|
| L2 海 | Mio: 薄黄色半袖＋紺の膝丈短パン。Saki: 珊瑚色の夏ワンピース。Kenta: 紺の半袖ラッシュガード＋水着。 |
| L3 雨の日の家 | Mio: 青灰色の長袖＋チャコールのパンツ。Kenta: 紺Tシャツ＋灰色パンツ、無そばかす。 |
| L4・L9 学校 | Mio: 紺ブレザー＋白シャツ＋紺リボン＋濃色チェックのスカート。Tom: 紺ブレザー＋青緑ベスト＋青緑ネクタイ＋ベージュパンツ。 |
| L5〜L7 秋の祖母訪問 | Mio: 薄ベージュのカーディガン＋淡青ブラウス＋紺スカート＋タイツ。Saki: 珊瑚色カーディガン＋クリーム色ワンピース＋レギンス。 |
| L7 将来像 | 成人Mio: セージ色ブラウス＋紺カーディガン＋チャコールの膝丈スカート。 |
| L8・L10 山 | Mio: 薄ベージュの登山シャツ＋オリーブ色パンツ＋青リュック＋日よけ帽。Tom: 青緑の速乾シャツ＋ベージュ登山パンツ＋灰色リュック。 |
| L9 帰宅後 | 宿題: 紫灰色の長袖＋チャコールパンツ。日曜の皿洗い: アイボリーの腕まくりシャツ＋青エプロン＋紺パンツ。 |

## 関連記録

- `IMAGEGEN_PROMPTS.md`: 組み込みImageGenで使った最終プロンプトセット
- `REVID_ANALYSIS.md`: 元Revid動画の画面切り替え分析
- `VERIFICATION.md`: 動画・音声・枚数・字幕の検証結果
- `overview_contact.jpg`: L2〜L10の全体俯瞰用コンタクトシート
- `shared/scripts/prepare_sentence_config.py`: 文と画像の対応、カメラ、切り替えの設定作成
- `shared/scripts/build_sentence_video.py`: 字幕、ハイライト、カメラ、切り替えを含む動画構築
- `Lxx/work/camera_qa/movement_contact.jpg`: 各場面の開始・終了を並べたカメラ移動確認用一覧

2026-08-01の固定サイズ強調・カメラ改訂前の動画、字幕、設定、生成処理は、`../_video_archives/2026-08-01_before_fixed_highlight_simple_camera/` に保存している。
