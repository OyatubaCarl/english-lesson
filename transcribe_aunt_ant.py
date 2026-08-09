"""Transcribe Aunt Ant Short A audio with Whisper word-level timestamps."""
from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
CLIENT = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

ROOT = Path(__file__).parent
AUDIO = ROOT / "uploaded-videos" / "aunt_ant_short_a_full.wav"
OUT = ROOT / "aunt_ant_short_a_transcript.json"


def main() -> None:
    print(f"Transcribing {AUDIO}...")
    with AUDIO.open("rb") as f:
        resp = CLIENT.audio.transcriptions.create(
            file=f,
            model="whisper-1",
            response_format="verbose_json",
            timestamp_granularities=["word", "segment"],
        )
    data = resp.model_dump()
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"Saved {OUT}: {len(data.get('words', []))} words, "
        f"{len(data.get('segments', []))} segments, "
        f"duration={data.get('duration', 0):.2f}s"
    )


if __name__ == "__main__":
    main()
