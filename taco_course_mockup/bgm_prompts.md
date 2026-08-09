# Teacher Tacos English フルコース — BGM生成プロンプト集

> WordTacos とは**別の楽曲**を用意するためのプロンプト。Suno / Udio / Stable Audio などに貼って生成する。
> 生成した mp3 を下記のファイル名で `taco_course_mockup/app_assets/bgm/` に置くだけで、アプリが自動で再生する（ファイルが無い場面は無音のまま動く）。
>
> ※ 厨房ラッシュのみ、ユーザー指定により WordTacos と同一の `sounds/kitchen_bgm.mp3` を使用（生成不要）。

## 共通の方針（全曲）
- 世界観: 「タコス食堂のフルコース」× 学習アプリ。**メキシカン風味 × あたたかいアコースティック**
- 歌声・英語の音読・TTSの邪魔をしない: **ボーカルなし（instrumental）・中低域を控えめ・音数少なめ**
- ループ前提: 曲頭と曲尾が自然につながる **seamless loop / 60〜90秒**
- 音量はアプリ側で 40% に絞るが、生成時点でダイナミクスは穏やかに

---

## 1. タイトル画面 — `bgm/title.mp3`
**場面**: アプリを開いた瞬間。ワクワクした「いらっしゃいませ！」感。

```
Warm inviting Mexican-inspired instrumental theme for a friendly learning app title screen.
Acoustic guitar strumming, marimba melody, soft handclaps, light maracas.
Cheerful, welcoming, like the door of a cozy taco diner opening.
Mid-tempo (100 BPM), no vocals, clean ending for seamless loop, 60-90 seconds.
```

（日本語補足: 陽気すぎず「今日も一皿いこう」という優しい高揚感。マリンバ主旋律＋アコギ。）

## 2. ホーム／コース選択・設定 — `bgm/home.mp3`
**場面**: メニュー（コース一覧）を眺めている時間。読みやすさ優先の控えめ曲。

```
Relaxed cafe background instrumental with a subtle Latin flavor.
Nylon-string guitar arpeggios, soft upright bass, gentle shaker, occasional warm electric piano chords.
Calm and unobtrusive, like browsing a menu in a quiet taqueria in the afternoon.
Slow-mid tempo (85 BPM), no vocals, no drums fill, seamless loop, 60-90 seconds.
```

## 3. レッスンジャーニー（7品の道のり） — `bgm/journey.mp3`
**場面**: 次の皿を選ぶ画面。少しだけ前進感・冒険感を足す。

```
Light adventurous instrumental with Mexican folk instruments for a learning quest map screen.
Marimba and acoustic guitar duet, soft cajon rhythm, playful flute accents.
A sense of gentle progress and appetite for the next challenge, optimistic but not busy.
Mid-tempo (95 BPM), no vocals, seamless loop, 60-90 seconds.
```

## 4. シャドウイング — `bgm/shadow.mp3`（任意・無くてもよい）
**場面**: 音読中。音声認識とTTSの邪魔を絶対にしない極小音数のアンビエント。
**注意**: マイク認識に干渉する可能性があるため、**入れない選択も推奨**。入れる場合は超控えめに。

```
Minimal ambient instrumental pad for a speaking practice screen.
Very sparse: warm sustained pads, faint acoustic guitar harmonics every few bars, no percussion, no melody line.
Extremely quiet and calm, must not interfere with speech recognition or text-to-speech audio.
Slow (70 BPM feel), no vocals, seamless loop, 60-90 seconds, low dynamic range.
```

## 5. コース完食ファンファーレ — `sounds/victory.mp3` を差し替える場合（任意）
**場面**: 7品完食のご褒美ジングル（ループなし・3〜6秒）。現在は WordTacos の victory.mp3 を暫定使用。

```
Short celebratory jingle, 4-6 seconds, mariachi-style trumpet fanfare with marimba flourish and a single festive "olé!"-like brass hit at the end.
Bright, triumphant, restaurant "order up!" energy. No vocals, clean tail, not a loop.
```

## 6. （参考）厨房ラッシュ — 生成不要
ユーザー指定により WordTacos と**同一**の `app_assets/sounds/kitchen_bgm.mp3` をそのまま使用。
将来差し替えたくなった場合のプロンプト:

```
Fast upbeat Mexican kitchen rush instrumental, 120-130 BPM.
Energetic acoustic guitar, marimba runs, driving cajon and shaker groove, occasional trumpet stabs.
Feels like a busy taco kitchen at lunch rush - exciting, slightly frantic but fun.
No vocals, seamless loop, 60-90 seconds.
```

---

## 導入手順
1. 各プロンプトで生成 → mp3 でダウンロード
2. ファイル名を上記どおりにリネームして `taco_course_mockup/app_assets/bgm/` に配置
3. `taco_course_mockup/sync_assets.sh` は bgm/ を消さない（mascot/sounds のみ同期）
4. デプロイすると各場面で自動再生（設定画面の「🎵 BGM」でON/OFF可能）

| 場面 | ファイル | ループ | 状態 |
|---|---|---|---|
| タイトル | `app_assets/bgm/title.mp3` | ○ | 未生成（無音で動作） |
| ホーム/設定 | `app_assets/bgm/home.mp3` | ○ | 未生成（無音で動作） |
| ジャーニー | `app_assets/bgm/journey.mp3` | ○ | 未生成（無音で動作） |
| シャドウ | `app_assets/bgm/shadow.mp3` | ○ | 任意（推奨: 無し） |
| 厨房ラッシュ | `app_assets/sounds/kitchen_bgm.mp3` | ○ | **WordTacosと同一・配置済** |
| 完食ジングル | `app_assets/sounds/victory.mp3` | × | WordTacos流用中（差替可） |
