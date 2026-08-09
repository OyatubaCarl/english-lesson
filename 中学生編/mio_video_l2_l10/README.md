# 中学生編 Mio版 L2〜L10 動画

既存の音源、既存動画、L1動画を変更せず、Mio主人公の画像と動画を課ごとの
独立フォルダに保存する。

- 画像: Codex built-in ImageGen
- 英語ハイライト: 既存の Taco Beat `m*.js` の語タイミング
- 日本語字幕: 自然な文単位訳
- カメラ: 画像生成後に構図を確認し、注目点の開始・終了座標とズーム量を指定
- 出力: 1920x1080 / H.264 / AAC

兄ケンタは高校1年生として、長身、落ち着いた顔、紺白のジャケットで統一し、
中学1年生のトム（そばかす、青緑のパーカー）と区別する。

## 完成動画

| 課 | 動画 |
|---|---|
| L2 | `L2/output/l2_a_day_at_the_sea_mio_bilingual_camera.mp4` |
| L3 | `L3/output/l3_a_rainy_afternoon_mio_bilingual_camera.mp4` |
| L4 | `L4/output/l4_my_new_friend_tom_mio_bilingual_camera.mp4` |
| L5 | `L5/output/l5_planning_to_visit_grandmother_mio_bilingual_camera.mp4` |
| L6 | `L6/output/l6_grandmothers_birthday_mio_bilingual_camera.mp4` |
| L7 | `L7/output/l7_my_future_dream_mio_bilingual_camera.mp4` |
| L8 | `L8/output/l8_tomorrows_class_trip_mio_bilingual_camera.mp4` |
| L9 | `L9/output/l9_a_school_day_mio_bilingual_camera.mp4` |
| L10 | `L10/output/l10_the_mountain_promise_mio_bilingual_camera.mp4` |

各課の `planning/lesson.json` に、字幕、語タイミングの対応、ショット境界、
パン・ズームの始点と終点、演出意図を保存した。`work/camera_qa/contact.jpg`
では動画全体のカメラ移動を一覧確認できる。

全9本の代表フレーム一覧は `qa_l2_l10_overview.jpg`。

## 原本と旧版

- 既存の音源、既存動画、L1動画は変更していない。
- L2でTomに似すぎたKentaの旧画像は `02_swimming.png` として残し、
  動画には年長らしく修正した `02_swimming_kenta_v2.png` を使用した。
- L6で人物の動作が誤っていた旧画像は `02_story_book_v1.png` として残し、
  動画には修正版 `02_story_book_v2.png` を使用した。
- ImageGenの生成元画像もCodexの生成画像保存先に残している。
