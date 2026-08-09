# 中学生編 L1〜L45 英語混じり・ルビ完全版

L1で確定した表示仕様を、既存の中学生編45レッスンへ展開する別版。

## 表示仕様

- 日本語訳を、内容語の一部を英語に置き換えた英語混じり文にする。
- 英語化する語は、そのレッスンの `middle_lessons.json > vocabSentences.words` にある正本の新出語だけに限定する。
- 全体単語帳・他レッスン・簡単な既習語による穴埋めをしない。当該課の正本新出語を日本語本文の中へ直接埋め込む。
- 単語の意味は英単語の直上の日本語ルビだけで示す。括弧内の補足、本文外の単語解説、意味の併記は禁止する。
- 英語部分には日本語の意味ルビを付ける。
- 残る日本語部分の漢字には、ひらがなルビを100%付ける。
- 既存の英語語単位ハイライト、採用楽曲、画像、カメラ移動は維持する。
- 歌唱語の強調は色だけを変更する。通常語・強調語とも72pxで、太さ・字間・位置・改行・拡大率を変えない。
- 既存完成動画は上書きしない。
- 括弧なしで正本新出語を本文へ直接埋め込む現行版名は `v4_inline_canonical_vocab`。旧 `v1`・`v2_canonical_vocab`・`v3_natural_canonical_vocab` は比較用に保持する。

## 整合性修正

新版字幕では、英語本文と日本語字幕が一致していなかった次の箇所を修正する。

- L34: 医師の発言を `Please don't push yourself for a while.` に一致させる。
- L36: 牛・豚・羊の動作と特徴を各英文に一致させる。
- L39: 古い写真、100年前の時計、過去の時間についての3文を各英文に一致させる。

採用楽曲との正本不一致は次の3語だけ修正した。

- L1: `ten` → `twelve`
- L6: `pretty` → `bouquet`、`picture` → `card`

この変更は動画字幕だけでなく、TacosPartyのTomatoMatoが直接読む
`taco_course_mockup/middle_lessons.json > vocabSentences` にも反映した。
あわせて、L1の採用曲が `with my friend` なのにTomatoMato文だけ「妹」としていた箇所を「友だち」に修正した。L6は `bought` の意味を「買った」に統一し、`passageJp` を採用曲8文の完全な日本語本文へ揃えた。いずれもL1/L6内の整合性修正で、TomatoMatoの出題数・対象語・音声キー数は変わらない。
将来 `extract_course.py` を再実行しても戻らないよう、
`taco_course_mockup/middle_lesson_overrides.json` を正本の上書き定義とする。

## 字幕マニフェスト生成

```bash
python3 scripts/prepare_middle_ruby.py
```

- `planning/manifest.json`: 全45課の集計
- `planning/lessons/Lxx.json`: 動画生成用の字幕データ
- `planning/mixed_translation_review.md`: 全文レビュー一覧

## 検証と出力

```bash
python3 scripts/verify_tomatomato_caption_contract.py
python3 scripts/verify_middle_caption_quality.py
python3 scripts/verify_middle_canonical_outputs.py
python3 scripts/verify_full_decode.py --scope all
```

- 個別45本: `output/Lxx/*_mixed_japanese_full_ruby_v4_inline_canonical_vocab.mp4`
- 字幕品質検証: 45/45 PASS、TomatoMato正本語411/411、字幕内ターゲト502/502、非正本語0件、括弧0件、ルビのない英字0件
- TomatoMato契約検証: PASS。問題カード205、対象語411、音声キー411を維持し、変更は上記L1/L6の3語置換だけ
- 個別動画の構造検証: 45/45 PASS
- 15課結合版は `scripts/combine_15_lessons.py` で生成する。2026-08-03時点でL01〜L15・L16〜L30・L31〜L45の現行3本が完成。
- 結合版の尺・コーデック検証は `combined/VERIFICATION_V4_INLINE_CANONICAL_VOCAB.json`、個別45本＋結合3本の全編デコード結果は `combined/FULL_DECODE_ALL_V4_INLINE_CANONICAL_VOCAB_20260803.json`。
- 旧 `v1`・`v2_canonical_vocab`・`v3_natural_canonical_vocab` 個別版は比較用に保持。旧 `v1` 結合版3本だけは、ディスク容量確保のためユーザー許可を得て削除した。旧個別版から再生成可能。

## 15課結合版の音声仕様

- 個別動画は課によって44.1kHzと48kHzのAACが混在する。異なるサンプルレートのAACをconcat demuxerへ直接渡してはならない。
- 映像はH.264をストリームコピーする。音声は各課ごとにPTSを0へ戻し、48kHz stereoへ変換し、各課の映像尺までpad/trimしてからconcat filterで連結する。
- 2026-08-03、旧L01〜L15結合版では先頭L1の48kHzを基準にL2以降の44.1kHz音声が解釈され、L2以降が約8.8%高速化していた。旧版は映像693.300秒に対して音声636.982秒だった。
- `combine_15_lessons.py` を上記方式へ修正し、L01〜L15を同名で上書きした。修正版は映像・音声とも693.300秒、15課の開始位置波形照合誤差は最大0.000084秒、全編デコードPASS。
- 現行v4のL01〜L15音声ストリームは、上記15境界波形照合済みv2/v3とSHA-256が完全一致する。`combined/L02_SYNC_VERIFICATION_V4_20260803.json` に記録。
