# 不規則動詞の歌 ABC型中心 Short v2 — QA記録

- 状態: YouTube public 公開済み（processed / HD）
- 公開日時: 2026-08-02 22:14:54 JST
- YouTube: https://www.youtube.com/shorts/KEpKCaYbpyA
- 動画ID: `KEpKCaYbpyA`
- タイトル: `歌なら簡単！不規則動詞変化17語を30秒で覚える #Shorts`
- 動画: `irregular_verbs_short_abc_v2.mp4`
- ビルド: `build_irregular_short_abc_v2.py`
- 長さ: 30.03秒
- 収録: 17語（begin 〜 take）

## 構成

- 冒頭訴求: 「不規則動詞変化　歌なら簡単に覚えられる！」
- 上半分: 動詞の意味を示す動作イラスト
- 下半分: 原形・過去形・過去分詞を常時表示
- 同期: 歌われている形だけ黄色で強調
- 終了訴求: 「保存して、もう1回歌おう！」

## 仕様・検証

- H.264 / 1080×1920 / 30fps
- AAC / 48kHz / stereo
- ffmpeg全編デコード: 合格
- 1秒間隔の30フレーム目視: 文字切れ・黒フレームなし
- `got / gotten`、`shown / showed` は縮小表示で収まることを確認
- YouTube処理: `succeeded`、アップロード: `processed`、定義: `hd`
- ログインなしで `availability=public`、長さ30秒を確認

## 再生成

```bash
python3 shorts/build_irregular_short_abc_v2.py
python3 yt_upload_irregular_short_abc_v2.py public
```
