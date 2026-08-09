"""Dependency-free OpenAI text-to-speech helper.

This module is intentionally limited to the audio speech endpoint. It must not
be extended for chat, embeddings, transcription, or any non-audio OpenAI API
use in this project.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path


TTS_URL = "https://api.openai.com/v1/audio/speech"
DEFAULT_MODEL = "tts-1-hd"
DEFAULT_VOICE = "alloy"


def load_env(path: Path = Path(".env")) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def synthesize_mp3(
    text: str,
    out_path: Path,
    *,
    model: str = DEFAULT_MODEL,
    voice: str = DEFAULT_VOICE,
    api_key: str | None = None,
    retries: int = 3,
) -> None:
    """Create an mp3 file using OpenAI TTS.

    Only the /v1/audio/speech endpoint is called.
    """
    load_env()
    key = api_key or os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    payload = json.dumps(
        {
            "model": model,
            "voice": voice,
            "input": text,
            "response_format": "mp3",
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        TTS_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    last_error = ""
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                out_path.write_bytes(response.read())
            if out_path.stat().st_size < 1024:
                raise RuntimeError(f"TTS output is too small: {out_path}")
            return
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            last_error = f"HTTP {exc.code}: {body[:800]}"
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"

        if attempt < retries - 1:
            time.sleep(2.5 * (attempt + 1))

    raise RuntimeError(f"OpenAI TTS failed for {out_path}: {last_error}")
