# アーカイブ: OpenAI TTS 単語/レッスン音声生成パイプライン

2026-07-05 アーカイブ。**単語・レッスン音声の生成は Piper に移行したため、OpenAIベースの音声生成スクリプトを退避。**

## 退避したスクリプト
- `generate-audio.py` — index.html シャドーイング用の OpenAI TTS 音声生成
- `generate_openai_beginner_audio.py` — Funnics 初級 B1-B20 の OpenAI TTS 行音声
- `generate-beginner-line-audio.py` — Funnics 初級レッスンの行ベース TTS 音声

## 現行方針（2026-07 以降）
- **英単語の音声は Piper で生成する**（lessac.onnx, 22050Hz mono → mp3 64k）。
  例: `echo "word" | piper -m vocab_sources/piper_test/voices/lessac.onnx -f out.wav`
  → `ffmpeg -i out.wav -af "adelay=100:all=1" -c:a libmp3lame -b:a 64k -ar 22050 -ac 1 word.mp3`
  （先頭に100msリード無音を付与＝頭詰まり/音切れ対策も同時に実施）
- OpenAI は音声生成に**使わない**。

## 残置（注意）
- `openai_tts_rest.py`（依存なしの OpenAI TTS ヘルパー）は、動画解説スクリプト
  `build_h4_svoo_plain_explainer.py` が import しているため**プロジェクト直下に残置**。
  動画ナレーションも Piper へ移す場合は別途対応が必要。
- `phonics_song_pipeline.py` / `transcribe_*.py` / `build_aunt_ant_subtitles.py` は
  OpenAI **Whisper（文字起こし）** を使うもので、TTS ではないため対象外。
