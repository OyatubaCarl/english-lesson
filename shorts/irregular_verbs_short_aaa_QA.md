# 不規則動詞の歌 AAA型 Short — 公開・QA記録

- 公開日時: 2026-08-02 19:43:19 JST
- YouTube: https://www.youtube.com/shorts/huqt2lb8nSY
- 動画ID: `huqt2lb8nSY`
- タイトル: `cut-cut-cut、言える？不規則動詞の歌｜AAA型4連発 #Shorts`
- 公開範囲: `public`

## 内容

`cut-cut-cut / hit-hit-hit / put-put-put / set-set-set` の4動詞。
歌唱中の原形・過去形・過去分詞に合わせ、対応する形を黄色で順番にハイライトする。

## 仕様・検証

- 映像: H.264 / 1080×1920 / 30fps / 8.09秒
- 音声: AAC / 48kHz / stereo
- 画面: 動作を中央に残す個別パン付きの縦9:16全画面
- YouTube処理: `succeeded`
- YouTubeアップロード: `processed`
- YouTube定義: `hd`
- ffmpeg全編デコード: 合格
- 0.5秒間隔の16フレームコンタクトシート: 文字切れ・黒フレームなし

## 再生成・公開

```bash
python3 shorts/build_irregular_short_aaa.py
python3 yt_upload_irregular_short_aaa.py public
```

ビルドスクリプトは `shorts/build_irregular_short_aaa.py`、アップロードスクリプトは `yt_upload_irregular_short_aaa.py`。
