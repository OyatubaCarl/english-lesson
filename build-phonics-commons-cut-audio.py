#!/usr/bin/env python3
"""Build short phonics clips from Wikimedia Commons IPA recordings.

Jolly Phonics recordings may be used only as local listening references.
This script does not read, transform, or embed Jolly audio. The distributable
clips are cropped from Wikimedia Commons source files and keep attribution
metadata in the generated manifest.
"""
from __future__ import annotations

import argparse
import html
import json
import math
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

import numpy as np
import requests
import soundfile as sf
from scipy import signal


COMMONS_API = "https://commons.wikimedia.org/w/api.php"
DEFAULT_OUT = "audio/phonics-commons-cut"
SAMPLE_RATE = 44_100
USER_AGENT = "CodexPhonicsCommonsCutPrototype/0.1 (local educational prototype)"


CLIPS = {
    # The stop cuts use the short isolated release in the Commons recording.
    # The target length is informed by Jolly-style "pure sound" practice, but
    # no Jolly waveform is used by this script.
    "p": {
        "title": "File:Voiceless bilabial plosive.ogg",
        "ipa": "/p/",
        "label": "voiceless bilabial plosive",
        "cut_start": 0.590,
        "cut_end": 0.755,
        "pad_before": 0.016,
        "pad_after": 0.038,
        "fade_in": 0.003,
        "fade_out": 0.018,
        "peak": 0.82,
        "artist_fallback": "Peter Isotalo",
        "note": "Short release chosen from the middle repetition to avoid an added vowel.",
    },
    "ae": {
        "title": "File:Near-open front unrounded vowel.ogg",
        "ipa": "/æ/",
        "label": "near-open front unrounded vowel",
        "cut_start": 0.020,
        "cut_end": 0.345,
        "pad_before": 0.014,
        "pad_after": 0.040,
        "fade_in": 0.018,
        "fade_out": 0.040,
        "peak": 0.76,
        "artist_fallback": "Denelson83",
        "note": "Short central vowel crop for a phonics card sound.",
    },
    "t": {
        "title": "File:Voiceless alveolar plosive.ogg",
        "ipa": "/t/",
        "label": "voiceless alveolar plosive",
        "cut_start": 0.895,
        "cut_end": 1.085,
        "pad_before": 0.014,
        "pad_after": 0.038,
        "fade_in": 0.003,
        "fade_out": 0.018,
        "peak": 0.82,
        "artist_fallback": "Peter Isotalo",
        "note": "Short release chosen from the middle repetition to avoid an added vowel.",
    },
}


def require_tool(name: str) -> str:
    tool = shutil.which(name)
    if not tool:
        raise SystemExit(f"ERROR: {name} is required but was not found on PATH")
    return tool


def clean_html(value: str | None) -> str:
    if not value:
        return ""
    text = html.unescape(value)
    text = text.replace("&nbsp;", " ")
    import re

    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extension_from_url(url: str) -> str:
    suffix = Path(unquote(urlparse(url).path)).suffix.lower()
    return suffix or ".ogg"


def commons_metadata(session: requests.Session, title: str) -> dict[str, Any]:
    response = session.get(
        COMMONS_API,
        params={
            "action": "query",
            "format": "json",
            "redirects": "1",
            "titles": title,
            "prop": "imageinfo|info",
            "inprop": "url",
            "iiprop": "url|mime|size|user|extmetadata|canonicaltitle",
        },
        timeout=30,
    )
    response.raise_for_status()
    pages = response.json().get("query", {}).get("pages", {})
    for page in pages.values():
        if "missing" not in page and page.get("imageinfo"):
            return page
    raise RuntimeError(f"Commons file not found: {title}")


def metadata_value(page: dict[str, Any], name: str) -> str:
    ext = page["imageinfo"][0].get("extmetadata", {})
    return clean_html(ext.get(name, {}).get("value", ""))


def usable_metadata_value(value: str) -> str:
    if value.lower().startswith("no machine-readable"):
        return ""
    return value


def download_source(session: requests.Session, url: str, out_path: Path, force: bool) -> None:
    if out_path.exists() and not force:
        return
    out_path.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(5):
        response = session.get(url, timeout=60)
        if response.status_code == 429:
            time.sleep(3 + attempt * 3)
            continue
        response.raise_for_status()
        out_path.write_bytes(response.content)
        return
    raise RuntimeError(f"download failed: {url}")


def mono(samples: np.ndarray) -> np.ndarray:
    if samples.ndim == 1:
        return samples.astype(np.float32)
    return samples.mean(axis=1).astype(np.float32)


def resample(samples: np.ndarray, source_rate: int) -> np.ndarray:
    if source_rate == SAMPLE_RATE:
        return samples.astype(np.float32)
    common = math.gcd(source_rate, SAMPLE_RATE)
    return signal.resample_poly(samples, SAMPLE_RATE // common, source_rate // common).astype(np.float32)


def normalize(samples: np.ndarray, peak: float) -> np.ndarray:
    current = float(np.max(np.abs(samples))) if samples.size else 0.0
    if current <= 0.00001:
        return samples.astype(np.float32)
    return (samples / current * peak).astype(np.float32)


def fade(samples: np.ndarray, sample_rate: int, fade_in: float, fade_out: float) -> np.ndarray:
    out = samples.copy().astype(np.float32)
    in_count = min(len(out), max(1, int(fade_in * sample_rate)))
    out_count = min(len(out), max(1, int(fade_out * sample_rate)))
    out[:in_count] *= np.linspace(0, 1, in_count, dtype=np.float32)
    out[-out_count:] *= np.linspace(1, 0, out_count, dtype=np.float32)
    return out


def build_clip(source_path: Path, clip: dict[str, Any]) -> tuple[np.ndarray, float]:
    samples, source_rate = sf.read(source_path, always_2d=False)
    samples = resample(mono(samples), source_rate)
    start = int(clip["cut_start"] * SAMPLE_RATE)
    end = int(clip["cut_end"] * SAMPLE_RATE)
    cropped = samples[start:end]
    cropped = normalize(cropped, clip["peak"])
    cropped = fade(cropped, SAMPLE_RATE, clip["fade_in"], clip["fade_out"])
    padded = np.concatenate(
        [
            np.zeros(int(clip["pad_before"] * SAMPLE_RATE), dtype=np.float32),
            cropped,
            np.zeros(int(clip["pad_after"] * SAMPLE_RATE), dtype=np.float32),
        ]
    )
    return padded.astype(np.float32), len(padded) / SAMPLE_RATE


def write_mp3(ffmpeg: str, samples: np.ndarray, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmpdir:
        wav_path = Path(tmpdir) / "clip.wav"
        sf.write(wav_path, samples, SAMPLE_RATE, subtype="PCM_16")
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(wav_path),
                "-codec:a",
                "libmp3lame",
                "-q:a",
                "2",
                str(out_path),
            ],
            check=True,
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    out_root = Path(args.out)
    source_dir = out_root / "sources"
    phoneme_dir = out_root / "phonemes"
    ffmpeg = require_tool("ffmpeg")
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    manifest: dict[str, Any] = {
        "provider": "Wikimedia Commons IPA recordings, cropped for phonics prototype",
        "license_status": "Derived clips retain the source file license. Attribution and ShareAlike requirements apply where listed.",
        "jolly_reference_note": "Jolly Phonics audio is a local listening reference only and is not copied, transformed, or distributed by this script.",
        "phonemes": [],
    }

    for sound_id, clip in CLIPS.items():
        page = commons_metadata(session, clip["title"])
        imageinfo = page["imageinfo"][0]
        source_url = imageinfo["url"]
        source_path = source_dir / f"{sound_id}{extension_from_url(source_url)}"
        out_path = phoneme_dir / f"{sound_id}.mp3"

        if args.dry_run:
            print(f"would build {sound_id}: {clip['title']} -> {out_path}")
            continue

        download_source(session, source_url, source_path, args.force)
        samples, duration = build_clip(source_path, clip)
        if args.force or not out_path.exists():
            write_mp3(ffmpeg, samples, out_path)

        title = page["title"]
        artist = usable_metadata_value(metadata_value(page, "Artist") or metadata_value(page, "Author"))
        credit = usable_metadata_value(metadata_value(page, "Credit"))
        manifest["phonemes"].append(
            {
                "id": sound_id,
                "ipa": clip["ipa"],
                "label": clip["label"],
                "audio": str(out_path),
                "source_audio": str(source_path),
                "source_title": title,
                "source_page": f"https://commons.wikimedia.org/wiki/{title.replace(' ', '_')}",
                "source_url": source_url,
                "artist": artist or clip.get("artist_fallback", ""),
                "credit": credit,
                "license": metadata_value(page, "LicenseShortName") or metadata_value(page, "UsageTerms"),
                "license_url": metadata_value(page, "LicenseUrl"),
                "modification": f"cropped to {clip['cut_start']:.3f}-{clip['cut_end']:.3f}s, faded, padded, normalized, and converted to MP3",
                "duration": round(duration, 3),
                "note": clip["note"],
            }
        )
        print(f"{sound_id}: {out_path} ({duration:.3f}s)")

    if not args.dry_run:
        out_root.mkdir(parents=True, exist_ok=True)
        (out_root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"manifest: {out_root / 'manifest.json'}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
