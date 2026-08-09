# 中学生編 L1 Codex 動画

現行 Lesson 1「わたしの家族と Pochi」の音源に、Codex の組み込み画像生成で作った水彩シーンをつなぎ、日英字幕と英語の単語ハイライトを重ねる制作フォルダ。

## 正本と参照元

- 音源: `../audio/L1.mp3`（43.328秒）
- 英文・日本語訳: `../../index.html` の中学生編 Lesson 1
- 単語タイミング: `../../taco_beat/charts/m1.js`
- 人物シート: `../characters/family_sheet.png` / `../characters/friends_sheet.png`
- 個別参照: `references/`
- 画像生成指示: `planning/scene_plan.json`
- 日英字幕割り: `planning/lyrics_timing.json`

人物シートは本編生成へ直接渡さず、人物ごとの個別参照へ切り出して使用する。Pochi は同じ水彩タッチで新規に基準画像を作る。

## 出力

- 最終動画: `output/l1_my_family_and_pochi_codex_bilingual.mp4`
- 字幕: `captions/l1_bilingual_word_highlight.ass`
- シーンのみ: `work/l1_scenes.mp4`
- 確認用コンタクトシート: `output/l1_scene_contact_sheet.jpg`

## ビルド

```bash
python3 scripts/build_video.py
```

字幕の英語ハイライトは Taco Beat の `BEAT` 配列にある単語開始時刻をそのまま使う。各単語の開始から次の単語まで、その単語だけをコーラル色にする。日本語は同じ英文行の表示区間に静止表示する。

## 制作上の前提

現行音源の主人公は Ken。一方、2026-07-12 作成の登場人物案はミオ中心で名前・年齢が一致しない。本作は「現行音源を変えない」を優先し、人物シートの外見を映像用デザインとして使う。
