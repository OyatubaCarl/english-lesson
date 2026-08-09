# Teacher Tacos English — YouTube Shorts 制作

本編の歌動画を、縦9:16ショートに再構成して @TeacherTacosEnglish に公開する仕組み。

## 公開中のショート（2026-08-02 時点）
| 種別 | 動画ID | 構成 |
|---|---|---|
| 不規則動詞 ABC型中心・新版 | KEpKCaYbpyA | 17語30秒＋常時3形表示＋歌唱同期ハイライト |
| 不規則動詞 AAA型 | huqt2lb8nSY | 動作画全画面＋冒頭クイズ＋歌唱同期ハイライト |
| 不規則動詞 ABC型 | LaHcDKNKevM | 元動画を中央＋上下CM帯 |
| 不規則動詞 ABB型 | oNyxVRL6tQU | 同上・問いかけ＋豆知識トーン |
| 中学 L2 海での一日（訳つき）| FyO0qL4QyOI | 全画面＋冒頭フック＋日本語訳 |
| 中学 L2 海での一日 B版（訳なし）| VfLGftlUyXs | 旧・帯サンドイッチ（A/B比較用） |

## 重要な制作知見（A/Bで判明）
**ショートは「全画面＋冒頭フック」が基本。** レターボックス/帯サンドイッチ
（中央だけ映像・上下が文字帯やぼかし）は没入感が落ちてスワイプされやすい。
- 映像は縦クロップ拡大で画面いっぱい（`scale=-2:1920,crop=1080:1920`）
- 冒頭1〜2秒に問いかけフック（例:「"海へ行った" 英語で言える?」）
- 情報（タイトル・訳）は上下の暗がりグラデPNG内に寄せ、中央は映像主役
- 日本語訳は1文1行・最長16字（フォント56〜60px・左右マージン60px）。
  英語は元動画のタイミングで速く切替、訳は1行読み終えてから切替。

## ビルド手順
### 1. 元動画を取得
```
yt-dlp -f "bv*[height<=1080]+ba/b[height<=1080]" --merge-output-format mp4 \
  -o /tmp/middle_L2.mp4 "https://youtu.be/2I2CtX5CNDw"
```
（不規則動詞フル尺は c0bh8bZI6BY → /tmp/original_irregular.mp4）

### 2. グラデPNG生成（全画面版で使用）
```
python3 make_grad.py        # → /tmp/grad_overlay.png
```

### 3. ショート生成
- `build_l2_short_v3.py` … 全画面＋フック＋日本語訳（L2／**雛形**）
- `build_irregular_short_aaa.py` … 不規則動詞 AAA型（全画面＋冒頭クイズ＋歌唱同期）
- `build_irregular_short_abc_v2.py` … 不規則動詞 ABC型中心17語（30秒＋常時3形表示＋歌唱同期）
- `build_irregular_short_v3.py` … 不規則動詞 ABC型（元動画中央＋上下帯）
- `build_irregular_short_v4.py` … 不規則動詞 ABB型（問いかけ＋豆知識）

各スクリプト冒頭の `SRC_VIDEO` / `SLICE_START` / `JP_SEGMENTS` を題材に合わせて変更。

### 4. アップロード（限定公開→確認→公開）
```
# L2: a=訳つき b=訳なし、第2引数 unlisted|public
python3 ../yt_upload_l2_short.py a unlisted
python3 ../yt_upload_l2_short.py a public

# 不規則動詞
python3 ../yt_upload_irregular_short_abc_v2.py public # ABC型中心・新版
python3 ../yt_upload_irregular_short_aaa.py public # AAA型（公開範囲を引数指定）
python3 ../yt_upload_irregular_short.py       # ABC型(v3) → 後でStudioでpublic
python3 ../yt_upload_irregular_short_v4.py     # ABB型(v4)
```
認証は `../token.json`（OAuth refresh_token）を再利用。

## A/B改善の経緯（L2「海での一日」）
- v1 帯サンドイッチ（中央608px映像＋上下文字帯）→ 再生伸びず
- v2 ぼかし背景フィル（中央のみ鮮明）→「全画面でない」と却下
- v3 真の全画面（縦クロップ）＋冒頭フック → **採用・公開**

## 注意
- プロジェクトの場所は 2026-06 頃 `ClaudeCode/` →
  `ClaudeCode/` にリネームされた。新パス基準。
- 日本語パスは Google Drive 同期で NFC/NFD 揺れがあり、bash の cd/cp/ls が
  文字化けすることがある。ファイル操作は Python（shutil/pathlib）経由が安全。
- 元動画の英語ラベル（赤）は映像内に既にあるので、英語字幕を別途重ねない。

## カスタムサムネ運用（thumb_tools/）

単語学習Shortsで「煽り文+単語+クイズ4択+TT+第2煽り」のカスタムサムネを自動生成し、
**動画冒頭1秒にオーバーレイ**してShortsフィードでも反映されるようにする。

### 重要な知見
- YouTube API `thumbnails().set()` で設定したサムネは
  検索結果・YouTube Studio・チャンネル一覧では効くが、
  **Shortsフィード（縦スワイプUI）では動画の最初のフレームが使われる**
- Shortsフィードでサムネを効かせるには **動画冒頭1秒にサムネ画像をオーバーレイ**
  （動画長・音声はそのまま、最初のフレームだけ差し変わる）

### 新規Shortsを作る運用フロー
```bash
# 1. 動画ビルド（既存）
python3 shorts/build_lou_quiz_short_v4.py  # など

# 2. 単語をマニフェストに追加
#    shorts/thumb_tools/word_difficulty_db.json  に {word, level, meaning_jp}
#    shorts/thumb_tools/manifest_thumbs.json     に1行追加
#    （level_key, tagline_id, speed_tagline_id を割当）

# 3. サムネ画像生成
python3 shorts/thumb_tools/build_thumbnail.py --word <word>

# 4. 動画冒頭1秒にサムネをオーバーレイ
python3 shorts/thumb_tools/apply_intro_thumbnail.py --word <word>
# → lou_quiz_short_v4_<id>_thumbed.mp4 ができる。これをアップロードする

# 5. アップロード後、video_id をmanifestに書き戻し、APIサムネも同時設定
python3 shorts/thumb_tools/yt_set_thumbnails_batch.py --dry-run
python3 shorts/thumb_tools/yt_set_thumbnails_batch.py --confirm
```

### ツール構成（shorts/thumb_tools/）
- `tagline_patterns.json`        上帯の煽り文13個（プレースホルダ{level}付）
- `tagline_speed_patterns.json`  下帯の煽り文（30秒で記憶/一発で覚える）
- `word_difficulty_db.json`      難易度12枠の単語マスタ
- `manifest_thumbs.json`         単語ごとの割当（level/tagline/video_id）
- `make_tt_cutout.py`            welcoming.png をクロマキー処理（1度だけ）
- `build_thumbnail.py`           単発生成 `--word X` または `--id X`
- `build_all_thumbnails.py`      manifest全件レンダリング
- `apply_intro_thumbnail.py`     動画冒頭1秒オーバーレイ（Shortsフィード対応）
- `yt_set_thumbnails_batch.py`   A群（video_id有）一括サムネ設定（リトライ3回）

### 既存A群8本のサムネ更新（2026-06-21）
mundane/fragile/vivid/inevitable/tranquil/diligent/meticulous/nebulous の
カスタムサムネを設定済み（検索・Studioでは反映、Shortsフィードは旧フレーム）。
動画ファイルの置き換えは「削除→新規」になりURL・視聴数がリセットされるため、
**公開済み6本は現状サムネのみ**、**今後の新規予約から冒頭オーバーレイを運用**。
