# 不規則動詞変化の歌 v6（YouTube音源同期版）

- 1動詞につき1枚の新規アクション画像（全55枚）
- 画像を16:9の全画面で表示
- 変化表は画面下部の薄い透過グラデーション上に表示
- 歌唱中の形だけ黄色で強調
- ユーザー作成のYouTube動画から取得した正しい音源を使用
- YouTube音源と元動画の歌唱表示から全55動詞のタイミングを再測定
- 音声で原形が省略された `understand` は括弧なしで表示し、原形を強調しない
- `read` は原形 `/riːd/`、過去形・過去分詞 `/red/` を表示
- 日本語訳・活用見出し・活用形をv3より大きく表示
- `hit` はボールの一部が太い打球部に隠れ、圧縮された接触の瞬間へ修正

## 出力

`output/irregular_verbs_one_action_per_verb_v6_youtube_1080p.mp4`

## 公開（2026-08-02）

- YouTube: https://youtu.be/287bSS2wpRU
- X（ティーチャータコス）: https://x.com/iHzKyC6Sdt2632/status/2083824362470383811
- 投稿メタデータ: `output/youtube_x_metadata.json`
- 公開結果: `output/publish_result.json`

旧v3〜v5動画と修正前の `hit` 画像は比較・復旧用に保存している。

## 再生成

```bash
python3 build_video.py
```
