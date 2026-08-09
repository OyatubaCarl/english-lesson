#!/usr/bin/env python3
"""Generate phonics card audio with espeak-ng.

This is a preview generator for phonics cards. It uses espeak-ng phoneme
mnemonics for isolated phonemes and plain words for word-level audio.
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional


DEFAULT_DATA = "phonics-audio-items.json"
DEFAULT_OUT = "audio/phonics-card-demo"


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def require_tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise SystemExit(f"ERROR: {name} is required but was not found on PATH")
    return path


def synth_wav(espeak: str, text: str, wav_path: Path, voice: str, speed: int, amplitude: int) -> None:
    run([
        espeak,
        "-v",
        voice,
        "-s",
        str(speed),
        "-a",
        str(amplitude),
        "-z",
        "-w",
        str(wav_path),
        text,
    ])


BOOST_FILTERS = {
    "stop": "volume=13dB,alimiter=limit=0.95",
    "affricate": "volume=9dB,alimiter=limit=0.95",
    "cluster": "volume=8dB,alimiter=limit=0.95",
    "fricative": "volume=7dB,alimiter=limit=0.95",
    "nasal": "volume=4dB,alimiter=limit=0.95",
    "approximant": "volume=4dB,alimiter=limit=0.95",
    "vowel": "alimiter=limit=0.95",
}


def wav_to_mp3(ffmpeg: str, wav_path: Path, mp3_path: Path, audio_filter: Optional[str] = None) -> None:
    mp3_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(wav_path),
    ]
    if audio_filter:
        cmd.extend(["-af", audio_filter])
    cmd.extend([
        "-codec:a",
        "libmp3lame",
        "-q:a",
        "3",
        str(mp3_path),
    ])
    run(cmd)


def make_audio(
    espeak: str,
    ffmpeg: str,
    text: str,
    out_path: Path,
    args: argparse.Namespace,
    audio_filter: Optional[str] = None,
) -> None:
    if out_path.exists() and not args.force:
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        wav_path = Path(tmpdir) / "audio.wav"
        synth_wav(espeak, text, wav_path, args.voice, args.speed, args.amplitude)
        wav_to_mp3(ffmpeg, wav_path, out_path, audio_filter)


def segment_ids(segments):
    out = []
    for segment in segments:
        if isinstance(segment, dict):
            out.append(segment.get("sound", segment.get("id", "")))
        else:
            out.append(segment)
    return [item for item in out if item]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=DEFAULT_DATA)
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--voice", default="en-us")
    parser.add_argument("--speed", type=int, default=120)
    parser.add_argument("--amplitude", type=int, default=160)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    data_path = Path(args.data)
    out_root = Path(args.out)
    data = json.loads(data_path.read_text(encoding="utf-8"))

    phoneme_dir = out_root / "phonemes"
    word_dir = out_root / "words"
    manifest = {
        "provider": "espeak-ng",
        "voice": args.voice,
        "speed": args.speed,
        "amplitude": args.amplitude,
        "phonemes": [],
        "words": [],
    }

    if args.dry_run:
        print(f"Would generate {len(data['phonemes'])} phonemes and {len(data['words'])} words into {out_root}")
        return 0

    espeak = require_tool("espeak-ng")
    ffmpeg = require_tool("ffmpeg")

    for item in data["phonemes"]:
        out_path = phoneme_dir / f"{item['id']}.mp3"
        # espeak-ng phoneme input is wrapped in [[...]].
        make_audio(espeak, ffmpeg, f"[[{item['espeak']}]]", out_path, args, BOOST_FILTERS.get(item["type"]))
        manifest["phonemes"].append({
            "id": item["id"],
            "label": item["label"],
            "ipa": item["ipa"],
            "type": item["type"],
            "audio": str(out_path),
        })
        print(f"phoneme {item['id']}: {out_path}")

    for item in data["words"]:
        out_path = word_dir / f"{item['id']}.mp3"
        make_audio(espeak, ffmpeg, item["word"], out_path, args)
        manifest["words"].append({
            "id": item["id"],
            "word": item["word"],
            "ipa": item["ipa"],
            "segments": segment_ids(item["segments"]),
            "display_segments": item["segments"],
            "audio": str(out_path),
        })
        print(f"word {item['id']}: {out_path}")

    out_root.mkdir(parents=True, exist_ok=True)
    (out_root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"manifest: {out_root / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
