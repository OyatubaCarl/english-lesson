# Revid 動画化ワークフロー

Suno で作曲した曲を Revid Public API に投げ、レッスン動画として書き出すまでの流れ。
このドキュメントは 2026-04-22 に H21–H31（計11本）を動画化したときの手順をもとにまとめている。

## 前提

- `.env` に `REVID_API_KEY` が入っていること
- User-Agent ヘッダが必須（デフォルト UA は Cloudflare に 1010 で弾かれる）
- 1本あたり 7–16 クレジット（平均 ~10）、ビルド時間 96–230秒（中央値 ~120秒）
- 今回の実測: 11本で ~170秒、全件成功

## 全体の流れ

```
Suno URL（複数）
   ↓ ① og:title で検証
レッスン番号に確定
   ↓ ② index.html から h2 を引く
プロジェクト名（正式タイトル）
   ↓ ③ /v3/render に送信
pid 取得
   ↓ ④ /v3/status で polling
status == ready
   ↓ ⑤ /v2/rename-project をダブルタップ
完了
```

## ① Suno URL → レッスン番号の検証

Suno 共有 URL の ID にはレッスン番号が埋まっていないので、必ず og:title で確認する。
ここをミスると 1本あたり 9–12 クレジットを溝に捨てることになる。

```python
import urllib.request, re
HDR = {'User-Agent': 'Mozilla/5.0 (Macintosh) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'}
req = urllib.request.Request(f'https://suno.com/s/{sid}', headers=HDR)
html = urllib.request.urlopen(req, timeout=15).read().decode(errors='ignore')
og = re.search(r'<meta property="og:title" content="([^"]+)"', html)
print(og.group(1))  # 例: "H31" や "L5　祖母を訪ねる計画"
```

## ② 正式タイトルを index.html から取得

Revid 上のプロジェクト名は `index.html` の `<h2>` と完全一致させる（YouTube 側の説明生成と一致させるため）。

```python
# 例: book-high1 の H21–H31
m = re.search(r'id="book-high1"[^>]*>(.*?)(?=id="book-high2")', t, re.DOTALL)
region = m.group(1)
for num in range(21, 32):
    sec = re.search(rf'<section[^>]*data-lesson="{num}"[^>]*>(.*?)</section>', region, re.DOTALL)
    h2 = re.search(r'<h2[^>]*>(.*?)</h2>', sec.group(1), re.DOTALL)
    clean = re.sub(r'<[^>]+>', '', h2.group(1)).strip()
    # -> "Lesson H21 — 分詞構文の発展「友を見送る朝」"
```

## ③ `/v3/render` にペイロード送信

この payload は十数本の試行で収束した確定レシピ。勝手に弄らない。

```python
HDR = {
    'Content-Type': 'application/json',
    'key': API_KEY,
    'User-Agent': 'Mozilla/5.0 (Macintosh) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Accept': 'application/json',
}

STYLE = 'Consistent 2D anime illustration style throughout. Clean line art, soft pastel colors, warm natural lighting, cheerful school-life atmosphere. No photorealistic images, no 3D renders, no mixed styles.'

payload = {
    'workflow': 'music-to-video',
    'source': {
        'url': f'https://suno.com/s/{sid}',   # Suno 共有ページ URL をそのまま渡す
        'recordingType': 'video',
        'stylePrompt': STYLE,
    },
    'media': {
        'type': 'moving-image',
        'imageModel': 'cheap',      # 'good' は約4倍のコスト
        'videoModel': 'base',
        'animation': 'dynamic',     # ken-burns より動きが多彩
        'mediaPreset': 'DEFAULT',
    },
    'captions': {'enabled': True, 'preset': 'Wrap 1', 'position': 'bottom'},
    'music': {'enabled': False, 'soundWave': True, 'syncWith': 'lyrics'},
    'options': {'disableAudio': True, 'hasToGenerateCover': False},  # cover=false で節約
    'metadata': {'title': name, 'name': name, 'projectName': name},
    'aspectRatio': '16 / 9',
}

r = POST('https://www.revid.ai/api/public/v3/render', payload)
pid = r['pid']
```

複数送るときは 2秒間隔で投げる（レートリミット対策）。今回 11本を順次送って全件 200 OK。

## ④ status を polling

```python
while True:
    r = GET(f'https://www.revid.ai/api/public/v3/status?pid={pid}')
    if r['status'] == 'ready': break
    if r['status'] in ('failed', 'error'): raise RuntimeError(r)
    time.sleep(20)
```

今回は 11本並列で polling し、最速 116秒、最長 170秒で全 ready。

## ⑤ ready になったらリネーム（ダブルタップ）

**最重要ルール**: rename は `status == ready` になってから呼ぶ。ビルド中に呼ぶと、Revid 側が完了時に自分のタイトルで上書きしてしまう。
さらに保険として 3秒空けて2回叩く。

```python
body = {'pid': pid, 'name': name, 'projectName': name, 'title': name}
POST('https://www.revid.ai/api/public/v2/rename-project', body)
time.sleep(3)
POST('https://www.revid.ai/api/public/v2/rename-project', body)
```

注意: `/v3/rename-project` は 307 リダイレクトを返す → **必ず `/v2/rename-project` を直接叩く**。

## エンドポイント一覧

| メソッド | パス | 用途 |
|---|---|---|
| POST | `/api/public/v3/calculate-credits` | クレジット見積もり（任意） |
| POST | `/api/public/v3/render` | 描画ジョブ投入、`pid` 取得 |
| GET  | `/api/public/v3/status?pid={pid}` | 進捗 polling（`building` → `ready`） |
| POST | `/api/public/v2/rename-project` | タイトル確定（ready 後） |

## 失敗モード

- `Invalid media file` → 生 mp3 URL を渡している。Suno 共有ページ URL に切り替え
- `Cannot read properties of undefined (reading 'replace')` → `source.url` 漏れ or フィールド名違い
- `workflow is required` → `workflow` フィールド欠落
- Cloudflare HTTP 1010 → User-Agent ヘッダ漏れ

## スタイルについての注意

- `stylePrompt` は仕様書上は prompt/ad ワークフロー用となっているが、music-to-video でも効く
- キャラ説明（「Yuki と両親と Pochi」など）を入れると全フレームに詰め込もうとして崩れる → **スタイル記述だけに留める**（画材／色／光／雰囲気／除外項目）
- キャラ同一性を厳密に担保したいなら `/v2/consistent-characters` に参照画像 URL（公開 HTTPS の PNG/JPG、≥1024²、単体正面ポートレート）を登録する必要あり。未実装

## 今回の成果物（2026-04-22）

| 元URL (Suno sid) | pid | Revid 上の名前 |
|---|---|---|
| 3Me844PUvAc6HwCo | IUPGVSPxjRuK0LDhEDbs | Lesson H21 — 分詞構文の発展「友を見送る朝」 |
| wzVCXORBVNT4mG3s | iRjalqQxd49woclKlXRE | Lesson H22 — 関係代名詞の発展「先生のお家」 |
| dVh9GLFsEPYAZXF3 | W3tzrLeoRDNSKbcaMmqJ | Lesson H23 — 関係代名詞 what「何が大切か」 |
| O2xoLxAqB0LxNBnl | XbIr3rMVUayd1J3Zpv6y | Lesson H24 — 関係副詞 where / when / why / how「祖父と灯台」 |
| lnVkA4WqAbuijGSR | zz269yLQn7WCYAypVxCg | Lesson H25 — 複合関係詞「町の小さな音楽会」 |
| VbBz3w0gtAEyHNlb | d3QbbKpzEbKFqgI2KX6C | Lesson H26 — 仮定法過去「もしも鳥だったら」 |
| v7y2BRhHgq9hPDwh | TCluT2RsO6dC1NMXmL1u | Lesson H27 — 仮定法過去完了「あの日の手紙」 |
| IL92b3mk0zsPtcZs | N3B8LjOjJkPmrFiqTg7T | Lesson H28 — I wish / as if / But for / if only「ペニシリンの発見」 |
| WRYwFslvOhF3GpfY | qVatr7cmB6RYCCD4pO4K | Lesson H29 — 比較の発展「世界で最も古い樹木」 |
| Qh5VVlD2qAlDVooS | 1Jffl9EwInb38zRn9Ok4 | Lesson H30 — 倒置・強調構文「人類、月に立つ」 |
| YC7DU94vQ57kLgTF | Au0qahXKWchnohbNp0Cj | Lesson H31 — 同格「キュリー夫人の情熱」 |

## 次のステップ（本ドキュメントの範囲外）

1. Revid 画面からダウンロード、`music/` 配下に配置
2. YouTube に手動アップロード
3. `youtube-map.json` に videoId を追記
4. `build-youtube-descriptions.py` → `bulk-update-descriptions.py` で概要欄を一括更新
5. `index.html` からのリンクも `youtube-map.json` 経由で自動反映
