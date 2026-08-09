# H087 完成動画・目視QA

- 確認日: 2026-08-07
- 題名: H087「日常の小さな一日 / An Ordinary Little Day」
- 完成版: `../output/h087_adopted_song_cinematic_v1_mixed_japanese_full_ruby_v5_tacobeat_canonical_vocab_color_only.mp4`
- 仕様: 111.333333秒、119,706,821 bytes、1920×1080、H.264 30fps、AAC 48kHz stereo
- SHA-256: `4bf1663d38547a425cebdb5e7289dd5219dc3edf9b9668ab576cedc67088e012`

## 判定

- 36/36基準画、全画像1672×941、予定名欠落0、余剰0。
- 実測歌詞20行に合わせた45映像ビート・94カット。切替0.641〜1.500秒。
- bored/annoyedを深刻な苦痛や怒りにせず、豆切れ、顔見知りの店員、正常なカード決済、虫刺されと指輪紛失、隣人への手助け、来週のキャンプ、借りるテントを歌詞どおり維持。
- 初回レンダリングの代表画面でキャンプ字幕に指輪捜索画が残るずれを発見。TacoBeat行時刻へ全場面を再配置し、94カット版として再レンダリングした。
- 修正版は歌詞境界21時点で、朝、カフェ、指輪説明、虫刺され、捜索、発見、電話、誘い、テント、振り返り、日常、夕方の順序を確認。
- 英語上段とルビ付き日本語下段の位置・改行・大きさは安定。歌唱語は66px固定で色だけが変わる。
- 映像・音声の全編デコードPASS。構造検証H001〜H087は87/87 PASS。
- 公開・アップロードは未実施。

## 確認画像

- `../scenes/qa_contact_sheets/h087_master_36_contact.jpg`
- `../scenes/qa_contact_sheets/h087_dense_32_contact.jpg`
- `h087_representative_20_contact_sheet.jpg`
- `h087_lyric_checkpoint_21_contact_sheet.jpg`
