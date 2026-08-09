# L6 改訂案 — Grandmother's Birthday

> 制作状況: 2026-08-01 完成。Suno改訂曲、確定歌詞83語、8枚の新規画像で `L6_revision_v3` を制作し、L1〜L15差し替え結合版も検証済み。

## 改訂理由

- 旧英文は、祖母宅へ着いて初めて誕生日だと知った直後に全員が贈り物をするため、出来事の因果が不自然。
- 日本語教材の「前から計画していた」と、英語本文の `we learned that today was her birthday` が矛盾している。
- 母の一輪の花、父が見せるだけの写真、妹の学校の話が「特別な贈り物」として弱い。
- L5とL7の訪問者はMio・Saki・Fumiの3人なのに、L6だけ両親を含む家族全員が突然登場する。

## 改訂英文

1. Grandmother's birthday was on Saturday, so my sister and I planned a surprise.
2. Before we left home, we prepared a few special gifts for her.
3. At her house, we gave her a bouquet from our garden.
4. My sister showed her a handmade birthday card.
5. Then she told her a funny story from school, and we all laughed together.
6. I bought her a new gardening book.
7. Grandmother gave us a warm smile and said, “Thank you both.”
8. We gave her a birthday to remember.

## 歌詞一覧（音楽生成サービス貼り付け用）

以下の8文を、順番を変えずに各1回だけ歌う。見出し、番号、繰り返し、コーラス用の追加文は歌詞へ含めない。

```text
Grandmother's birthday was on Saturday, so my sister and I planned a surprise.
Before we left home, we prepared a few special gifts for her.
At her house, we gave her a bouquet from our garden.
My sister showed her a handmade birthday card.
Then she told her a funny story from school, and we all laughed together.
I bought her a new gardening book.
Grandmother gave us a warm smile and said, "Thank you both."
We gave her a birthday to remember.
```

### 発音上の注意

- `Grandmother's` は語頭と所有格の `s` をつぶさず、明瞭に発音する。
- `Saturday` は学習者が聞き取れる自然な3音節で歌う。
- `bouquet` は **boo-KAY / buːˈkeɪ** と発音する。
- `handmade birthday card` は単語同士をつなげすぎず、3語を判別できるようにする。
- `gardening` は **GAR-den-ing**、`Thank you both` は引用部分として自然に区切る。
- `gave her / showed her / told her / bought her / gave us` の「人＋もの」が聞き取れるよう、動詞と間接目的語を急いで圧縮しない。

## 楽曲生成プロンプト

### Style / Song Description

Suno、Udioなどのスタイル欄には以下を貼り付ける。

```text
Create a short, warm English educational song titled "Grandmother's Birthday" for early-teen English learners.

Musical style: cheerful and affectionate acoustic pop with a cozy autumn family-birthday feeling. 4/4 time, around 88 BPM, approximately 48-55 seconds. Light acoustic guitar, gentle piano, soft glockenspiel accents, warm bass, and restrained brushed percussion. Keep the arrangement uncluttered so every English word is easy to hear.

Vocal: one clear, natural female lead with a warm youthful tone, not imitating any real singer. Precise standard English pronunciation, low reverb, little or no vibrato, no melisma, and a short natural breath between sentences.

Structure: through-composed eight-line song. Sing every supplied lyric line exactly once and in the given order. Preserve every word exactly. Do not add a chorus, refrain, spoken introduction, count-in, repeated line, harmony response, ad-lib, vocalization, or closing phrase. Do not add "Happy Birthday" or quote any existing birthday melody. Keep the instrumental intro under two seconds and the ending under two seconds.

Educational priority: make gave her, showed her, told her, bought her, and gave us especially clear so learners can hear the SVOO pattern. Keep the melody simple, memorable, and singable without stretching or swallowing final consonants.
```

### Exclude / Avoid

除外指定欄がある場合は以下を使う。

```text
male lead, duet, choir, children's chorus, rap, spoken word, EDM, trap drums, heavy rock guitars, dramatic orchestral score, dense arrangement, heavy reverb, vocal effects, melisma, scat, ad-libs, lyric repetition, added lyrics, long intro, long outro, tempo changes, key changes, existing Happy Birthday melody
```

### 希望する音源仕様

- 44.1kHz以上、ステレオ。
- 動画用MP3と、保管・再編集用WAVの両方を保存する。
- 先頭の無音は0.5秒以内、歌唱後の余韻は2秒以内を目安にする。
- 可能なら同じ構成のインスト版も保存する。
- 生成後は、歌詞の追加・省略・語順変更・不自然な発音がないかを全文照合してから採用する。

## 日本語字幕

1. 祖母の誕生日は土曜日だったので、妹とわたしはサプライズを計画しました。
2. 家を出る前に、わたしたちは祖母のためにいくつか特別な贈り物を用意しました。
3. 祖母の家で、わたしたちは庭の花で作った花束を贈りました。
4. 妹は祖母に手作りの誕生日カードを見せました。
5. それから妹が学校での面白い話をすると、みんなで笑いました。
6. わたしは祖母に新しい園芸の本を買いました。
7. 祖母はわたしたちに温かな笑顔を見せ、「二人とも、ありがとう」と言いました。
8. わたしたちは祖母に、思い出に残る誕生日を贈りました。

## 文法ターゲットの維持

- `gave her a bouquet` — give + 人 + もの
- `showed her a handmade birthday card` — show + 人 + もの
- `told her a funny story` — tell + 人 + もの
- `bought her a new gardening book` — buy + 人 + もの
- `gave us a warm smile` — give + 人 + もの
- `gave her a birthday to remember` — give + 人 + もの

## 新しい画面構成

1. L5の計画場面からつながる金曜夜。MioとSakiが土曜日の印に気づき、祖母へのサプライズを相談する。
2. MioとSakiが花束、手作りカード、園芸本を旅行かばんへ丁寧に詰める。
3. 祖母宅の縁側で、姉妹が庭の花を束ねた花束をFumiへ渡す。
4. Sakiが自分で作った誕生日カードをFumiへ見せ、そのまま手渡す。
5. Sakiが学校の面白い出来事を身振りを交えて話し、MioとFumiが笑う。
6. MioがFumiの好きな庭仕事に合う新しい園芸本を贈る。
7. Fumiが姉妹二人へ温かな笑顔で礼を言う。
8. 花束、カード、園芸本と小さなケーキを囲み、Mio・Saki・Fumiの3人で夕暮れを過ごす。

## 制作上の注意

- 旧音源は旧英文を歌っているため流用しない。改訂英文で新しい歌音源とTaco Beat時刻を作る。
- 新音源確定後に字幕タイミング、Shot尺、8枚の画像、L6単体動画を作り直す。
- L6完成後、L1〜L15結合版を再生成する。
- L5の秋服と祖母宅、L7の3人構成を連続させる。

## 実制作結果（2026-08-01）

- 採用曲: [Suno共有曲](https://suno.com/s/Gt7jn1dImCjsLlfx)
- Suno clip ID: `7dce29b9-f9b4-4141-a15e-d0852922143c`
- 音源: 49.320979秒、48kHz、ステレオ。歌詞は上記8文・83語と順序どおり一致。
- 新規画像: 8枚。登場人物はMio・Saki・Fumiの3人に限定し、L5の秋服とL7の祖母宅を継承。
- L6単体: `L6_revision_v3/output/l6_grandmothers_birthday_revision_v3_mio_bilingual_camera.mp4`
- L1〜L15差し替え結合版: `mio_video_combined_15_lessons/middle_lessons_L01-L15_mio_bilingual_combined_L6_revision_v3.mp4`
- 旧L6と旧L1〜L15結合版は比較・復旧用として変更せず保存。
