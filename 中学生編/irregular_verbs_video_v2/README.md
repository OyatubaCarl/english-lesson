# 不規則動詞変化の歌 新版動画

## 完成版

- 動画：`output/irregular_verbs_funnics_island_v2_1080p.mp4`
- サムネイル：`output/irregular_verbs_funnics_island_v2_thumbnail.png`
- 全体確認：`output/irregular_verbs_funnics_island_v2_contact_sheet.jpg`
- 元楽曲：[Suno「不規則動詞変化の歌」](https://suno.com/s/Ieo5wFRQpaTowu1R)

## 仕様

- 55動詞、28場面
- 1場面あたり1〜2動詞
- Mio、Tom、Teacher Tacosを共通の案内役として背景に配置
- 左右のファニックスアイランドの仲間を動詞に合わせて切り替え
- 原形・過去形・過去分詞を固定位置に表示し、歌われている形を黄色で強調
- A–A–A、A–B–A / A–B–B、A–B–C の3区分を色分け
- 音声で省かれている原形は `(understand)` と括弧表示し、非強調

## 出力情報

- 映像：H.264、1920×1080、30fps
- 音声：AAC、48kHz、ステレオ
- 長さ：101.166667秒
- SHA-256：`4bcee2ac2c5b7056eeaec7c5691b0b1e2e8b9b9afb3f630944a40d349c4e2412`

## 再生成

```bash
venv/bin/python3 中学生編/irregular_verbs_video_v2/build_video.py
```

タイムラインの正本は `planning/irregular_verbs_timeline.json`、字幕は `captions/irregular_verbs_bilingual_highlight.ass`。

## 検証

- `ffprobe` で映像・音声仕様と長さを確認
- `ffmpeg -f null -` で全編デコード検査済み
- 10秒間隔のコンタクトシートで全体の場面切り替えを確認
- 60.50秒、61.20秒、62.05秒を個別確認し、`(understand)` と2回の `understood` の扱いを確認
