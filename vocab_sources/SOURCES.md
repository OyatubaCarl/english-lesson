# WordTacos 出典・参考資料

このドキュメントは、WordTacos アプリで使われている語彙データ・レベル分類・スコア表記の根拠を一覧にしたものです。エンディング動画やクレジット、お問い合わせ対応時の出典提示に使います。

最終更新: 2026-06-30

---

## 1. 語彙レベル分類 (CEFR-J)

すべてのステージで使われる CEFR レベル分類の根拠。

- 投野 由紀夫 編 (2013). *CEFR-J Wordlist*. 東京外国語大学 投野研究室
  - URL (公開): https://cefr-j.org/cefrj.html
  - ライセンス: 研究・教育目的の利用を許諾

---

## 2. 学習指導要領 (中学・高校)

中学・高校範囲ステージ (stage1〜stage6) の語彙選定の根拠。

- 文部科学省 (2017). 中学校学習指導要領 (平成 29 年告示). 外国語編
- 文部科学省 (2018). 高等学校学習指導要領 (平成 30 年告示). 外国語編

---

## 3. ステージ別の出典まとめ

### 3.1 stage1 (中1) / stage2 (中2) / stage3 (中3)

- CEFR-J Wordlist (投野研究室)
- 中学校学習指導要領 (文部科学省 平成 29 年告示)
- 編者 (Teacher Tacos English) によるカリキュラム独自編集

### 3.2 stage4 (中学発展)

- 同上 + 高校接続レベルとして編者選定

### 3.3 stage5a / stage5b (高校入門〜標準)

- CEFR-J Wordlist (CEFR B1.1 / B1.2)
- 高等学校学習指導要領 (文部科学省 平成 30 年告示)
- 編者独自編集

### 3.4 stage6a / stage6b (高校上級・発展)

- CEFR-J Wordlist (CEFR B2.1 / B2.2)
- 高等学校学習指導要領 + 大学入試頻出語
- 編者独自編集

### 3.5 TOEIC ステージ (basic / mid / high)

- 編者独自選定の TOEIC 頻出語 732 語コーパス
- CEFR-J Wordlist によるレベル分類
- ETS (2015). *TOEIC Listening & Reading Test Examinee Handbook* — CEFR ↔ TOEIC 対応
- ETS (2019). *TOEIC Can-Do Guide* — スコア帯と能力対応

**重要 (score_note)**: TOEIC スコア表記は CEFR-J レベルから ETS 公表の対応表に基づく**目安**です。実点保証ではありません。

### 3.6 stage_toeic_expert (CEFR C1 上級学術・ビジネス)

- Coxhead, A. (2000). *A new academic word list*. TESOL Quarterly, 34(2). — methodology reference (語彙集の複製ではなく方法論の参照)
- 投野研究室 CEFR-J Wordlist (C1 帯) — レベル整合
- ETS (2015). *TOEIC Listening & Reading Test Examinee Handbook* — スコア対応
- 編者 (Teacher Tacos English) が選定し、独自に例文を執筆

---

## 4. 音声合成 (発音)

- 英語発音: Piper TTS (lessac voice). https://github.com/rhasspy/piper
  - ライセンス: MIT
- 日本語ナレーション (動画用): VOICEPEAK (商用版、AHS 製)
  - 動画ナレーション用途。アプリ内では未使用

---

## 5. CEFR ↔ TOEIC 対応 (loose correlation の根拠)

| CEFR | TOEIC L&R 目安 (ETS) |
|---|---|
| A1 | 〜380 |
| A2 | 380〜595 |
| B1.1 | 595〜700 |
| B1.2 | 700〜790 |
| B2.1 | 790〜855 |
| B2.2 | 855〜945 |
| C1 | 945〜985 |
| C2 | 990 |

- ETS が公表している TOEIC スコアと CEFR レベルの対応表
- 投野 (CEFR-J 研究) が示す日本語学習者向けの目安

---

## 6. 画像・素材

- マスコット・カスタマー画像: Codex CLI (OpenAI image_gen) 経由で生成、編者編集
- 一部の補助画像: Google Gemini (Nano Banana) 経由で生成
- 透過処理: rembg (isnet-general-use)
- 画像合成: Python Pillow + ffmpeg

---

## 7. ホスティング・配信

- Cloudflare Pages
  - URL: https://wordtacos.pages.dev / https://words.teachertacos.com
- 配信: Wrangler CLI

---

## 8. 開発・実装

- 主要開発支援: Claude Code (Anthropic)
- バージョン管理: git
- フロントエンド: 単一 HTML + バニラ JS (PWA, Service Worker)
- データ形式: 各ステージごとの JSON

---

## 9. 動画制作 (将来エンディング動画含む)

- BGM: Suno (編者本人が AI 生成、利用権あり)
- 字幕: ASS (Advanced SubStation Alpha)
- 編集: ffmpeg
- 録画: Playwright (アプリ画面のプレイ録画)

---

## 10. 編者・連絡先

Teacher Tacos English (神奈川県 現役教員) 編集・運営
