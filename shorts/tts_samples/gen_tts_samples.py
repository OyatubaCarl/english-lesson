#!/usr/bin/env python3
"""fal-ai/elevenlabs/tts/multilingual-v2 で日本語混じり文の音声サンプルを2voiceで生成。

ElevenLabsのmultilingual v2は日本語の中の英単語を英語発音に切替て読む。
複数voiceから視聴比較するために2本生成。
"""
import os
import sys
import urllib.request
from pathlib import Path

import fal_client  # tacos-shorts/.venv で 1.0.0 を確認済み

os.environ["FAL_KEY"] = Path("~/.fal_key").expanduser().read_text().strip()

OUT_DIR = Path(
    "/Users/masaki/Documents/ClaudeCode/英語学習教材作成/shorts/tts_samples"
)
OUT_DIR.mkdir(exist_ok=True)

TEXT = "桜の美しさは ephemeral だ。咲いてから散るまで、わずか一週間しかないなんて。"

# ElevenLabs 既定 voice の固有ID（multilingual v2 で日本語対応が良いもの）
# - Rachel: 21m00Tcm4TlvDq8ikWAM (女性・落ち着き、教育系定番)
# - Sarah:  EXAVITQu4vr4xnSDxMaL (女性・柔らかい、ナラ向き)
# - Charlotte: XB0fDUnXU5powFXDhCwa (女性・自信、CMっぽい)
VOICES = [
    ("Rachel", "21m00Tcm4TlvDq8ikWAM"),
    ("Sarah", "EXAVITQu4vr4xnSDxMaL"),
]


def gen(voice_name: str, voice_id: str) -> Path:
    print(f"--- {voice_name} ({voice_id}) ---", flush=True)
    result = fal_client.subscribe(
        "fal-ai/elevenlabs/tts/multilingual-v2",
        arguments={
            "text": TEXT,
            "voice": voice_id,
            "stability": 0.45,
            "similarity_boost": 0.75,
            "style": 0.10,
            "speed": 1.0,
        },
        with_logs=False,
    )
    # result schema: {"audio": {"url": "...", "content_type": "audio/mpeg", ...}}
    audio = result.get("audio") or {}
    url = audio.get("url")
    if not url:
        print("ERROR: no audio url in result:", result, file=sys.stderr)
        sys.exit(1)
    out = OUT_DIR / f"sample_{voice_name.lower()}.mp3"
    urllib.request.urlretrieve(url, out)
    print(f"OK -> {out}  ({out.stat().st_size/1024:.1f} KB)")
    return out


def main():
    paths = []
    for name, vid in VOICES:
        try:
            paths.append(gen(name, vid))
        except Exception as e:
            print(f"FAILED {name}: {e}", file=sys.stderr)
    print("\nGenerated:")
    for p in paths:
        print(" -", p)


if __name__ == "__main__":
    main()
