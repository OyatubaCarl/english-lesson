# Phonics Song Video Pipeline

このフォルダにある **phonics-songs/** 配下のキャラクター画像を入力に、
Suno で作った曲を「自分の絵 + Revid の字幕」で動画化する。

## 全体フロー

```
Suno share URL  →  ① mp3 ダウンロード
                ↓
                ② Whisper 文字起こし（単語タイムスタンプ付き）
                ↓
                ③ TIMELINE 設計
                   = (scene_label, start, end, motion_mode) のリスト
                ↓
                ④ ffmpeg で Ken Burns + xfade 動画ビルド (1080p)
                ↓
                ⑤ 480p に圧縮（17 MB 前後）
                ↓
                ⑥ 公開ホストにアップ（tmpfiles.org / 直接 DL URL）
                ↓
                ⑦ Revid `caption-video` ワークフローに投げる
                   ※字幕だけ付けてくれる。music-to-video より大幅に低クレジット
```

## 重要な設計判断

### `caption-video` ワークフローを使う
Revid には複数のワークフローがあるが、自分の絵をそのまま使いつつ字幕だけ
付けたいなら `caption-video` 一択。

| workflow | source | 自前画像 | クレジット |
|---|---|---|---|
| music-to-video | Suno URL | ❌ Revid が再生成 | 高 |
| caption-video | 公開 mp4 URL | ✅ そのまま | 低 |

### 公開ホストの選び方
Revid は `source.url` に **直接 DL 可能な mp4 URL** を要求する。

| host | 結果 |
|---|---|
| catbox.moe | ❌ 0 バイトで配信されることがある（不安定） |
| 0x0.st | ❌ 2026 春現在、AI bot 対策で uploads disabled |
| gofile.io | ❌ 直接 URL ではなく download page しか返さない |
| **tmpfiles.org** | ✅ `https://tmpfiles.org/dl/<id>/<file>` が直接 DL OK（60分 expiry） |
| Cloudflare Pages | ✅ 永続的（要 wrangler 認証） |

→ 60 分以内に Revid 投稿まで完了する前提なら **tmpfiles.org** が最もラク

## 使い方（最小例）

```python
from phonics_song_pipeline import run_pipeline, BAKER_BEAR_TIMELINE

result = run_pipeline(
    slug="baker_bear_long_a",                       # ファイル名 prefix
    suno_sid="pbgdUBUJURWbujp1",                   # Suno share ID
    project_name="Baker Bear and Magic E — Long A (captioned)",
    timeline=BAKER_BEAR_TIMELINE,
)
print(result["revid_url"])  # → https://www.revid.ai/projects/<pid>
```

または `python3 phonics_song_pipeline.py baker` で直接実行。

## TIMELINE の作り方

1. `_transcript.json`（Whisper 出力）を眺めて、歌詞のセクション境界を拾う
2. 各セクションに対応する画像 (`phonics-songs/<slug>/NN_xxx.png`) を割り当て
3. motion_mode を選ぶ（下記参照）
4. 最後の end を mp3 の総尺にちょうど合わせる（余白カット OK）

### motion_mode
| 名前 | 動き |
|---|---|
| zoom_in_center | 真ん中に向かってゆっくりズームイン（標準） |
| zoom_out_center | 真ん中からズームアウト |
| pan_lr_zoom | 左→右パン + 軽くズーム |
| pan_rl_zoom | 右→左パン + 軽くズーム |
| pan_diag_tl_br | 左上→右下に斜めパン |
| zoom_in_br | 右下にズームイン |

## 必要な準備

### `.env`
```
OPENAI_API_KEY="sk-..."
REVID_API_KEY="..."
```

### Python 依存
```bash
python3 -m venv venv
source venv/bin/activate
pip install openai python-dotenv requests
```

### ディレクトリ
```
英語学習教材作成/
├── phonics_song_pipeline.py     ← 本体
├── phonics-songs/
│   └── <slug>/
│       ├── 01_xxx.png           ← scene 画像（1920x1080 推奨）
│       ├── 02_xxx.png
│       └── ...
├── <slug>.mp3                   ← Suno mp3（自動 DL）
├── <slug>_transcript.json       ← Whisper 結果
├── <slug>_FINAL.mp4             ← 1080p 動画
└── <slug>_480p.mp4              ← 480p 圧縮版（Revid に投げるやつ）
```

## トラブルシュート

| 症状 | 原因 / 対処 |
|---|---|
| `Invalid media file` | `source.url` が直接 DL できない（gofile, catbox 0byte 等） |
| `[Errno 8] nodename nor servname` | DNS 一時的失敗。リトライで OK |
| Whisper が日本語を取れない | `language="en"` を外して `language=None` に |
| ffmpeg "Could not find input" | scene 画像のパスズレ。`phonics-songs/<slug>/<label>.png` を確認 |
| Revid status=error すぐ | tmpfiles の URL が expire（60分）した可能性。再アップ |

## 実績

| 曲 | slug | duration | Revid pid |
|---|---|---|---|
| ベイカーベアとまほうのe | `baker_bear_long_a` | 213.56s | `0dej0uyPNUuR6TI1lpKH` |
