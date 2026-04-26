# 英語学習教材作成プロジェクト ― 引き継ぎノート

## 中断時点（2026-04-26）
**次の再開ポイント：H40 から構文解析＋ルビコンテンツを作成**

## プロジェクトの全体像
中学・高校英語学習者向けサイト `index.html`（30000行超、Cloudflare Pages で公開予定）。
高校編（high1/high2/high3）の各レッスンに、ボタン⑦「構文解析＋ルビ」コンテンツを段階的に追加する作業中。

## 完了済み
| 項目 | 状態 |
|------|------|
| H1〜H39 構文解析（high1） | 完了 |
| H60 構文解析（high2、テンプレ元） | 完了 |
| OpenAI TTS 音声 3959 個生成（audio/ 配下） | 完了 |
| 音声統合（speakOrPlay、Web Speech API フォールバック） | 完了 |
| ルビ位置・トークン inline-flex 列レイアウト | 完了 |
| Notification 音フック（~/.claude/settings.json） | 完了（PC ローカル） |

## 残タスク
1. **H40〜H45**（high1 残り） ← まずここ
2. **H46〜H59、H61〜H160**（high2/high3、H60 はスキップ）
3. Cloudflare Pages デプロイ（ユーザ操作）

## 1 レッスン分の作業手順
1. 該当 `<section class="lesson hidden" data-lesson="N">` を `data-has-syntax="true"` 付きに変更
2. `jp-full hidden` の `</div>` と `</section>` の間に `<div class="body-syntax hidden">…</div>` を挿入
3. テンプレは H36（line 23272）または H37〜H39（line 23625〜24409）参照
4. 段落 → `<div class="para" data-pnum="N">`、文 → `<div class="sentence">`
5. 単独トークン：`<span class="tok lS|lV|lO|lC|lM"><span class="lab">S/V/O/C/M</span>英語<span class="ja">和訳</span></span>`
6. かたまり：`<span class="chunk role-S|role-V|role-O|role-C|role-M"><span class="role">役割</span>...</span>`
7. 各文末に `<div class="meta-row"><span class="pattern">文型</span><span>解説</span></div>`
8. paragraph 群末に `<div class="syntax-legend">…</div>` 凡例

## 運用ルール
- 1 ターンあたり **3 レッスン** まとめて処理する（ユーザ希望「なるべく多く」）
- レッスンの文法ターゲットに即した解説を `meta-row` と `syntax-legend` に書く
- 各レッスンの英文・和訳・文法ターゲットは `<div class="grammar-box">` と `<div class="en-body">` を読んで把握する

## 関連ファイル
- `index.html` — 本体
- `generate-audio.py` — OpenAI TTS 生成（新レッスン追加後に再実行で差分のみ）
- `.env` — `OPENAI_API_KEY` 入り（git 管理外）
- `audio/{book}/L{N}/s{idx}.mp3` + `manifest.json` — 音声ファイル
- `syntax-mockup.html` — 初期モックアップ（H60 の元）

## 別 PC で再開する手順
1. Google Drive 同期完了を確認（`G:\マイドライブ\個人用\ClaudeCode\英語学習教材作成\` 以下が揃っているか）
2. Claude Code をこのディレクトリで起動 → このファイル（CLAUDE.md）を自動読み込み
3. ユーザが「H40 から続けて」または「次へ」と指示
4. Claude は H40 のセクションを読み、上の手順で 3 レッスンずつ進める

## 注意
- index.html は git 上で 11000 行超の未コミット差分あり（commit していない）
- 音声 audio/ ディレクトリは git 管理外（必要なら別 PC で `python generate-audio.py` 再実行）
- `.env` の OPENAI_API_KEY は別 PC でも別途用意が必要
