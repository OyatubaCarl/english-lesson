# L1 Mio版 動画制作

## 方針

- 主人公と語り手を、登場人物シートの正式設定どおり「ミオ」に統一する。
- 既存の女性ボーカルに合うよう、Ken版の音源は流用せず、Mio版として歌い直す。
- Tomを基にしたKenの画像は使わない。`references/mio_ref.png` を全場面の基準画像にする。
- 旧Ken版は比較用に残し、上書きしない。

## 完成状態

- [x] Mioの公式キャラクター原画を切り出し
- [x] 英語歌詞と日本語訳をMio設定へ改訂
- [x] 再作曲・再歌唱用の制作指示を作成
- [x] Mio版のSuno音源を取得
- [x] 新音源から100語の単語タイミングを取得
- [x] Mio版の8場面を用意
- [x] 日英字幕とTaco Beat式ハイライトを作成
- [x] 1920×1080動画を書き出して全編検証

## 重要ファイル

- `output/l1_my_family_and_pochi_mio_bilingual_pan_zoom.mp4` — 推奨完成動画（パン＋ズーム版）
- `output/l1_my_family_and_pochi_mio_bilingual.mp4` — 初版動画（比較用として保持）
- `output/l1_mio_scene_contact_sheet.jpg` — 完成動画の場面一覧
- `output/l1_mio_pan_zoom_motion_proof.jpg` — 各場面の開始・終了フレーム比較
- `source_audio/l1_mio_suno_be1f5114.mp3` — Mio版の音源複製
- `references/mio_ref.png` — Mioの公式基準画像
- `planning/mio_lyrics_rewrite.md` — 確定用の英語歌詞と日本語訳
- `planning/music_generation_brief.md` — 新音源の制作指示
- `planning/lyrics_timing.json` — 日英字幕の構成
- `planning/chart_correction.json` — Taco Beat解析の補正記録
- `planning/motion_plan.json` — 場面ごとのパン・ズーム設計
- `taco_timing/charts/l1_mio_video_words.js` — 動画用100語タイミング
- `captions/l1_mio_bilingual_word_highlight.ass` — ハイライト字幕

## 音源の由来

- Suno曲: `https://suno.com/song/be1f5114-3aca-40b5-984c-f4f978cf5393`
- Suno上の曲は変更・削除していない。
- ダウンロードしたMP3をMio版フォルダへ複製して使用した。

## 原本の保護

- 旧Ken版 `../l1_codex_video/` は変更していない。
- 元音源 `../audio/L1.mp3` は変更していない。
- Taco Beat本体、既存譜面、既存動画へ新曲を注入していない。
- Mio版の全生成物は、この `l1_mio_video/` 以下だけに保存している。

## パン・ズーム版

- 8場面すべてに緩やかなカメラ移動を設定した。
- 最大ズームは1.16倍に抑え、人物やポチがフレーム外へ切れないことを確認した。
- ズームイン、ズームアウト、左右パンを場面内容に合わせて交互に使用した。
- 初版動画は上書きせず、別名の比較用ファイルとして残している。
