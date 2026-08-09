"""Transcribe baker_bear_long_a.mp3 with Whisper word-level timestamps."""
from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
CLIENT = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

ROOT = Path(__file__).parent
AUDIO = ROOT / "baker_bear_long_a.mp3"
OUT = ROOT / "baker_bear_long_a_transcript.json"


def main() -> None:
    print(f"Transcribing {AUDIO.name}...")
    with AUDIO.open("rb") as f:
        resp = CLIENT.audio.transcriptions.create(
            file=f,
            model="whisper-1",
            response_format="verbose_json",
            timestamp_granularities=["word", "segment"],
            language="en",  # primary lyrics are English; JP narration is short
        )
    data = resp.model_dump()
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    n_words = len(data.get("words", []))
    n_segs = len(data.get("segments", []))
    print(f"Saved {OUT.name}: {n_words} words, {n_segs} segments, "
          f"duration={data.get('duration', 0):.2f}s")


if __name__ == "__main__":
    main()
