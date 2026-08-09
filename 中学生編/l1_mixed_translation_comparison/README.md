# L1 英語混じり文・英語ルビ比較（修正版）

既存の新版L1を上書きせず、日本語訳の字幕だけを英語混じり文へ差し替える比較試作。

- 共通：既存のSuno音源、17場面、英語の単語ハイライト、カメラ移動を維持
- 英語ルビなし：英語にはルビを付けないが、日本語の漢字ルビは100%表示
- 英語ルビあり：英語部分の上に日本語の読み・意味を表示し、日本語の漢字ルビも100%表示
- 色分け：英語部分は琥珀、日本語部分は水色、英語ルビは淡いクリーム色
- 2行字幕：ルビ付き版は1行目と2行目の間隔を70pxから110pxへ拡大

## 英語ルビの例

| 英語部分 | 日本語ルビ |
|---|---|
| name | 名前 |
| twelve years old | 12歳 |
| small village | 小さな村 |
| My family | 私の家族 |
| father / mother | 父 / 母 |
| really cute | とてもかわいい |
| Every morning | 毎朝 |
| friend / school | 友達 / 学校 |
| really good day | とても良い日 |

固有名詞の `Mio` と `Pochi` には、それぞれ「ミオ」「ポチ」と読みを付ける。

## 修正版出力

- `output/l1_mixed_translation_no_english_ruby_v2.mp4`
- `output/l1_mixed_translation_japanese_ruby_on_english_v2.mp4`
- `output/comparison_english_ruby_contact_sheet_v2.jpg`

比較の差分は「英語部分への日本語ルビ」の有無だけで、漢字ルビは両方に残す。

再生成：`python3 scripts/build_comparison.py`
