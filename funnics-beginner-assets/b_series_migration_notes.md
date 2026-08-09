# Bシリーズ移植メモ

`index.html` はまだ変更していません。このフォルダ内のファイルを使うと、現在の入門編Bシリーズ部分を、既存の教材構造に合わせて置き換えられます。

## 使うファイル

- `b_series_book_replacement.html`: `div#book-beginner` の置き換え用HTML
- `b_series_book_replacement.css`: Bシリーズ専用の最小追加スタイル
- `b_series_book_replacement.js`: Bシリーズ用の動画表示、読み上げ、シャドウイング、単語チェック補助
- `b_series_book_preview.html`: 単体プレビュー
- `b_series_lessons_ja.json`: 元データ
- `b_series_youtube_urls.json`: YouTube URL一覧

## index.html に移植するとき

1. `<head>` 内に次を追加します。

```html
<link rel="stylesheet" href="funnics-beginner-assets/b_series_book_replacement.css">
```

2. 既存の `<div class="book hidden" id="book-beginner" data-book="beginner"> ... </div>` を、`b_series_book_replacement.html` の中身で置き換えます。

3. 既存のメイン `<script>` の後ろ、`</body>` の前に次を追加します。

```html
<script src="funnics-beginner-assets/b_series_book_replacement.js"></script>
```

## 含めた要素

- 各Bレッスンの文法説明と例文
- 日本語混じり文（`jp-body`）: 新出語だけ英語で残し、それ以外は日本語訳
- 英語だけの文（`en-body`）
- 日本語訳（`jp-full`）
- 本文では歌詞の繰り返し行を省略
- YouTube個別動画とB1〜B20一気見リンク
- 21ページ目のまとめページ（文法事項とB1〜B20個別YouTubeリンクを一体化した一覧、一気見動画リンク）
- シャドウイング練習
- このレッスンの新出単語チェック

## 補足

- 既存の `id="book-beginner"` と `data-book="beginner"` はそのまま残しています。
- `data-audio` の録音音声を優先して再生し、音源が見つからない場合だけ Web Speech にフォールバックします。
- `index.html` 本体はこの生成処理では変更しません。
