# タコス・ビート コンテンツ制作手順書（新曲追加）

リズムゲーム「タコス・ビート」(`index.html`) に新しい歌を追加するための完全な手順書。
**他の AI モデルや人間が、この文書だけを読んで単独で実行できる**ことを目的とする。

- ゲーム公開先: https://taco-beat.pages.dev/ （Cloudflare Pages, プロジェクト `taco-beat`）
- パイプラインの経緯・設計判断の正本: Obsidian `_AI-Workspace/01_tasks/in-progress/TASK-20260707-001.md`

---

## 1. 前提（環境）

すべて **ローカル実行・外部 API 不使用・料金ゼロ**。乱数不使用なので同じ入力からは毎回同じ譜面が出る（再実行安全）。

| もの | 場所 / 備考 |
|---|---|
| Python 仮想環境 | `/Users/masaki/Documents/ClaudeCode/英語学習教材作成/venv/bin/python3`（whisper / torch / torchaudio 2.11 / scipy / numpy 入り。**システムの python3 ではなく必ずこれを使う**） |
| ffmpeg / ffprobe | Homebrew 版がパスにある前提（`brew install ffmpeg`） |
| Whisper モデル | `~/.cache/whisper/medium.pt`（キャッシュ済み。消えていた場合は初回実行時に約1.4GB 自動DL） |
| MMS_FA モデル | `~/.cache/torch/hub/checkpoints/model.pt`（約1.18GB。キャッシュ済み。消えていた場合は初回実行時に自動DL） |
| 歌の音源（B系） | `/Users/masaki/Documents/ClaudeCode/FunnicsIsland/songs/<nn>_beginner_tom_b<N>/audio/b<N>_suno.mp3` |
| 歌の音源（L系） | `/Users/masaki/Documents/ClaudeCode/英語学習教材作成/music/L*.mp3` |
| B↔動画ID対応表 | `FunnicsIsland/songs/b_series_1_20/b_series_youtube_urls.json` |

### ⚠️ 既知の落とし穴（重要）

1. **`whisper` コマンド（CLIラッパー）は使わない。** シェバンが旧 Google Drive パスで壊れている。
   `make_chart.py` は内部で `python -m whisper` を使っているので問題ないが、手動で試すときも必ず
   `venv/bin/python3 -m whisper ...` の形で実行すること。
2. **`torchaudio.load` は使えない。** torchcodec が入っていないため失敗する。
   音声の読み込みは「ffmpeg で 16kHz mono wav 化 → `scipy.io.wavfile.read`」で行う（`make_chart.py` 実装済み）。
3. **初回実行はモデル DL/ロードで数分〜十数分かかる。** 2回目以降は Whisper 結果も
   `.cache/<id>/` にキャッシュされるので速い（曲ファイルの md5 が変わると自動で再認識）。

---

## 2. 1曲追加する手順

### 手順A: ラッパースクリプト（推奨・最短）

```bash
cd "/Users/masaki/Documents/ClaudeCode/英語学習教材作成/taco_beat"

# 例: B2 の歌を追加（譜面とmp3の生成まで。index.html は変更しない）
./add_song.sh "/Users/masaki/Documents/ClaudeCode/FunnicsIsland/songs/06_beginner_tom_b2/audio/b2_suno.mp3" b2

# 生成 + そのままゲーム(index.html)を b2 に差し替える場合
./add_song.sh "/Users/masaki/Documents/ClaudeCode/FunnicsIsland/songs/06_beginner_tom_b2/audio/b2_suno.mp3" b2 --inject
```

生成物:
- `songs/b2.mp3` — ゲーム同梱用 96kbps 音源
- `charts/b2.js` — 譜面（`const BEAT=[...]; const SONG_BPM=xx.xx;`）
- `.cache/b2/` — Whisper 結果などの中間キャッシュ（コミット不要・消してよい）

### 手順B: python 直接実行（オプションを細かく制御したいとき）

```bash
VENV_PY="/Users/masaki/Documents/ClaudeCode/英語学習教材作成/venv/bin/python3"
cd "/Users/masaki/Documents/ClaudeCode/英語学習教材作成/taco_beat"

"$VENV_PY" make_chart.py <入力mp3> --id b2 [--outdir .] [--inject index.html] [--force]
```

| オプション | 意味 |
|---|---|
| `--id` | 曲ID（英数字・`-`・`_`）。出力ファイル名になる |
| `--outdir` | 出力先ディレクトリ（既定: カレント）。`songs/` `charts/` `.cache/` を作る |
| `--inject` | 指定した index.html の `const BEAT=...;`/`const SONG_BPM=...;` ブロックと `<audio id="song" src="...">` を置換して1曲差し替える。**デフォルトOFF**（生成のみ） |
| `--force` | Whisper キャッシュを無視して再認識 |

### 手順C: 生成した譜面を手動で組み込む場合

`--inject` を使わないなら、`charts/<id>.js` の中身（2行）を `index.html` 末尾の
`<script>const BEAT=[...];\nconst SONG_BPM=xx.xx;</script>` ブロックに貼り替え、
`<audio id="song" preload="auto" src="songs/<id>.mp3">` の `src` を差し替える。

### デプロイ（ユーザー確認の上で）

```bash
cd "/Users/masaki/Documents/ClaudeCode/英語学習教材作成/taco_beat"
npx wrangler@latest pages deploy . --project-name=taco-beat --branch=main --commit-dirty=true
```

### 動作確認チェックリスト

- [ ] `charts/<id>.js` のノーツ数が歌詞の単語数と概ね一致（全単語が必ず入る仕様）
- [ ] ローカルで開いて再生（`python3 -m http.server` 等）: 最初の単語がタイル到達と同時に歌われるか
- [ ] 短い機能語（i / am / a / the …）のタイミングが歌とズレていないか
- [ ] 間奏に🫓（word="" のプレーンノーツ）が数個だけ入っているか
- [ ] ホールド（伸ばす音）の位置が長い音符と一致しているか
- [ ] 実機で音ズレを感じたらゲーム内の「タイミング微調整」UI（±20ms刻み）で吸収可能

---

## 3. パイプラインの中身（make_chart.py が自動でやること）

```
入力mp3
 → [1] ffmpeg 96kbps mp3化 ......... songs/<id>.mp3（既に mp3 96kbps 以下ならコピー）
 → [2] ffmpeg 16kHz mono wav化 ..... .cache/<id>/<id>_16k.wav（解析用・一時）
 → [3] Whisper medium .............. 「実際に歌われた」単語列 + 概略タイミング
      └ 伴奏を同じ低信頼語として3回以上繰り返す誤認識と、無音区間の
        `Thank(s) you for watching` 型の終端誤認識は自動除外
 → [4] torchaudio MMS_FA ........... wav2vec2 強制アライメントで単語開始時刻を高精度化
 → [5] spectral-flux オンセット検出 → 機能語だけオンセットに吸着（±0.14s）
 → [6] BPM/位相推定 ................ 粗0.5BPM → 細0.02BPM・8ms のグリッドサーチ
 → [7] ホールド焼き込み + 🫓フィラー
 → [8] charts/<id>.js 出力（--inject 時は index.html も書き換え）
```

設計上の要点（TASK-20260707-001 で確立済み）:

- **正確な歌詞テキストには整列させない。** Suno がその通り歌ったとは限らないため、
  Whisper が拾った「実際に歌われた語順」に対して強制アライメントする。
- **全単語が必ずノーツになる**（ハイブリッド譜面）。拍グリッドに揃えるのは間奏の🫓フィラーだけ。
- **短い機能語は強制アライメントがズレやすい**（b1 で i/am が 25〜135ms ズレた実測あり）
  → 機能語だけ音響オンセットに吸着させて解決した。内容語は強制アライメントのまま。

---

## 4. 譜面形式仕様（BEAT 配列）

`charts/<id>.js` の中身:

```js
const BEAT=[[0.583,"",0,0],[1.12,"hello",1,0],[3.001,"Funnics",1,3.661], ...];
const SONG_BPM=70.34;
```

各行 `[t, word, key, holdEnd]`:

| フィールド | 型 | 意味 |
|---|---|---|
| `t` | 秒(小数3桁) | ノーツを叩く時刻 = その単語が歌われる瞬間（`<audio>` の currentTime 基準） |
| `word` | 文字列 | 表示する単語。**`""`（空文字）は間奏の🫓プレーンノーツ**（ghost表示・発声なし） |
| `key` | 0/1 | 1=内容語（大きい・派手なノーツ）、0=機能語（控えめなノーツ） |
| `holdEnd` | 秒 or 0 | 0より大きければホールドノーツで、その値が終端時刻。0なら単発タップ |

- `SONG_BPM` は演出用（背景パルス等）。ノーツ判定には使わない。
- 行は時刻昇順。ホールドは生成時に「焼き込み」済みなので、ゲーム側は `holdEnd>0` を見るだけでよい。

---

## 5. パラメータの意味（make_chart.py 冒頭の定数）

現行 b1 譜面を作った値。**変えると譜面の性格が変わる**ので、変えるなら1つずつ試すこと。

| 定数 | 値 | 意味 |
|---|---|---|
| `SPELL_FIX` | 辞書 | Whisper の綴りブレ補正（例: `phonics→Funnics`）。**新曲で固有名詞が化けたらここに追加** |
| `SNAP_WORDS` | 16語 | オンセット吸着する機能語（i, am, a, the, to, is, are, you, your, my, oh, hi, wow, too, here, what's） |
| `FUNCTION_WORDS` | SNAP+this | `key=0`（機能語ノーツ）にする語。それ以外は `key=1` |
| `SNAP_WINDOW` | 0.14 | 機能語をオンセットに吸着させる探索窓 [s]。広げすぎると誤吸着する |
| `MIN_GAP` | 0.05 | 吸着後もノーツ間隔がこの値を下回らないよう保持 [s] |
| `HOLD_GAP` | 0.95 | 次の単語までこれより空いたらホールド化 [s] |
| `HOLD_PAD` | 0.30 | ホールド終端は次の単語の 0.3s 手前まで [s] |
| `HOLD_MAX` | 1.50 | ホールドの最大長 [s] |
| `FILLER_GAP` | 1.20 | 単語間がこれより空いた区間（＋曲頭/曲末）だけ🫓フィラー候補 [s] |
| `FILLER_EXCLUDE` | 0.38 | 拍の±この範囲に単語があればフィラーを置かない [s] |
| `END_MARGIN` | 0.60 | 曲末尾のこの秒数にはフィラーを置かない [s] |
| `BPM_MIN/MAX` | 55/110 | BPM 探索範囲。**テンポが速い/遅い曲で BPM が明らかに変なら広げる**（倍/半分に化けやすい点に注意） |

---

## 6. トラブルシュート

| 症状 | 原因と対処 |
|---|---|
| `whisper: command not found` / whisper CLI がパスエラーで落ちる | CLI ラッパーのシェバン破損。`make_chart.py` 経由なら発生しない。手動時は `venv/bin/python3 -m whisper` を使う |
| `torchaudio.load` 系のエラー（torchcodec / backend not found） | 仕様。`make_chart.py` は scipy 読みで回避済み。自作コードでも wav 化→`scipy.io.wavfile.read` を使う |
| 初回実行がとても遅い / 大きな DL が始まる | Whisper medium (~1.4GB) と MMS_FA (~1.18GB) の初回モデル DL。`~/.cache/whisper/` と `~/.cache/torch/hub/checkpoints/` にキャッシュされ、2回目以降は不要 |
| 単語の綴りがおかしい（固有名詞が別の語になる） | `make_chart.py` 冒頭の `SPELL_FIX` に `"聞き取られた綴り(小文字)": "正しい表記"` を追加して再実行（Whisper はキャッシュされるので速い） |
| 認識された単語数が明らかに少ない | ボーカルが小さい・エフェクトが強い曲で起こりうる。`--force` で再認識しても同じなら、より歌が明瞭な音源（動画化前の Suno 原音）を使う |
| 間奏に `music` / `thank` など同じ単語が何度も出る | Whisper の伴奏誤認識。現行パイプラインは「高い無音確率・低い単語確率・1語だけ」が同一曲内で3回以上反復した場合に自動除外する。旧譜面は再生成する |
| 曲末に `Thank you for watching` が出る | Whisper が無音・残響を動画の定型句と誤認する既知パターン。無音確率75%以上の独立セグメントに限って自動除外する。本文中の通常の `thank you` や `watching TV` は除外しない |
| BPM が倍/半分になっている | `BPM_MIN/BPM_MAX` を実際のテンポを挟む範囲に調整して再実行。BPM は🫓フィラーの間隔と演出にしか使わないので、多少ズレても致命的ではない |
| 機能語のタイミングが微妙に合わない | `SNAP_WINDOW` を 0.10〜0.20 の範囲で調整。それでもダメなら `charts/<id>.js` の該当時刻を直接手修正してよい（形式は §4） |
| 実機でだけ全体的に遅れて聞こえる | 端末の音声出力遅延（Bluetooth 等）。ゲーム内の「タイミング微調整」UI（localStorage `tb_off`）でプレイヤー側が吸収できるので譜面は直さない |
| `--inject` が「ブロックが見つかりません」で失敗 | index.html の `const BEAT=[...];`＋`const SONG_BPM=...;`（連続2文）または `<audio id="song" src="...">` の形が崩れている。該当箇所を確認 |

---

## 7. 検証記録（2026-07-07）

`b1.mp3`（現行ゲーム同梱の 96k 音源）を入力に `--id b1test` で全パイプラインを実行し、
現行 `index.html` の BEAT（beatmap6 相当）と比較した結果:

| 項目 | 現行 BEAT | 生成 b1test | 判定 |
|---|---|---|---|
| 単語ノーツ数 / 語順 / key | 107 | 107（語順・key 完全一致） | ✅ |
| ホールド数 | 27 | 27 | ✅ |
| 🫓フィラー | 4個 (0.583/81.618/82.471/83.324) | 4個 (0.592/81.627/82.48/83.333) | ✅ (位相グリッド9ms差) |
| SONG_BPM | 70.34 | 70.34 | ✅ 一致 |
| 単語タイミング | — | 59/107 が完全一致・平均差 10ms・最大 192ms（差が出るのはオンセット吸着対象の機能語6語のみ） | ✅ |

再現手順:

```bash
"$VENV_PY" make_chart.py b1.mp3 --id b1test --outdir /tmp/b1test_out
```
