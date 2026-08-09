# BGM Library — 学習動画向け使い回し音源

Teacher Tacos English のショート動画用 BGM を 10 ジャンル分ストック。
ファイルは商用利用 OK・著作権クリア（Pixabay License / CC0 / CC BY 4.0 のみ）。

## ジャンル一覧

| ID | スラッグ | トーン | 想定用途 |
|---|---|---|---|
| 01 | lofi_piano | Lo-fi piano + soft drums | 汎用学習・最も無難 |
| 02 | ambient_pad | 浮遊感のあるパッド | 概念紹介・瞑想風 |
| 03 | cinematic_calm | ピアノ＋弦 | 情緒・桜・物語性 |
| 04 | minimal_acoustic | ギター＋最小限の打 | 朝の学習・読書 |
| 05 | japanese_koto | 琴/尺八モダンアレンジ | 和テーマ・日本史/古典 |
| 06 | chillhop_warm | ヴァイナル質感 | カジュアル・通学中 |
| 07 | orchestral_light | 軽オーケストラ | 向上心・達成感 |
| 08 | electronic_study | 控えめエレクトロニカ | IT/サイエンス/プログラミング |
| 09 | jazz_lounge | ジャズピアノ＋ブラッシュ | 大人向け・教養 |
| 10 | sakura_ambient | 桜・夜・しっとり | 桜題材・季節性 |

詳細メタ（artist / license / source_url / duration）は `meta.json` を参照。

## 使い方

### ビルダー側 (build_lou_quiz_short_v1.py / v2.py)

環境変数 `BGM_LIB_NAME` でライブラリから1曲指定:

```bash
# v2 clean を 01_lofi_piano で
BGM_LIB_NAME=01_lofi_piano python3 build_lou_quiz_short_v2.py

# v2 intro を 10_sakura_ambient で
BGM_LIB_NAME=10_sakura_ambient python3 build_lou_quiz_short_v2.py --intro

# v1 論文あり を 03_cinematic_calm で
BGM_LIB_NAME=03_cinematic_calm python3 build_lou_quiz_short_v1.py
```

出力ファイル名には自動で `_<name>` サフィックスが付くので、同じスクリプトで複数 BGM 版を並列保持できます。

### 解決順
1. `BGM_LIB_NAME` (env) — `bgm_library/{name}.mp3` を使用（推奨）
2. `BGM_OVERRIDE` (env, 絶対パス) — 任意ファイル
3. デフォルト — タコス曲 (非推奨：学習動画にはトーン不一致)

### 音量
- デフォルトでライブラリ曲は `BGM_VOLUME=0.20`（タコス曲は0.07）
- 個別に調整したいときは `BGM_VOLUME=0.15` などで上書き

### 短尺ループ
ffmpeg `-stream_loop -1` を入れてあるので、19秒程度の曲でも自動で30秒分ループされます。

## 動画 description でのクレジット表記

CC BY 4.0 の曲は表記必須。`meta.json` の `credit_line` をそのまま動画descriptionに貼ってください。
例:
```
Music by Kevin MacLeod (Incompetech, CC BY 4.0)
```
Pixabay License / CC0 はクレジット任意ですが、礼節として記載推奨。

## 追加・差し替え

新しい曲を追加する場合:
1. `bgm_library/NN_<slug>.mp3` に配置
2. `meta.json` に同じ形式でエントリ追加
3. このREADMEのテーブルに1行追加
