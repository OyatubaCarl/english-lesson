#!/usr/bin/env python3
"""Generate B1-B20 beginner line audio with OpenAI TTS.

This script only calls OpenAI's audio speech endpoint through
openai_tts_rest.py. It reads existing audio/beginner/L*/manifest.json files and
creates the mp3 files referenced by those manifests.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from openai_tts_rest import DEFAULT_MODEL, DEFAULT_VOICE, synthesize_mp3


ROOT = Path(__file__).resolve().parent
DEFAULT_AUDIO_ROOT = ROOT / "audio" / "beginner"
DEFAULT_PUBLIC_ROOT = ROOT / "dist-public" / "audio" / "beginner"


def lesson_manifest(audio_root: Path, lesson: int) -> Path:
    return audio_root / f"L{lesson}" / "manifest.json"


def load_manifest(audio_root: Path, lesson: int) -> dict:
    path = lesson_manifest(audio_root, lesson)
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def update_manifest(path: Path, manifest: dict, *, model: str, voice: str) -> None:
    manifest = dict(manifest)
    manifest["model"] = model
    manifest["voice"] = voice
    manifest["granularity"] = manifest.get("granularity", "line")
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio-root", default=str(DEFAULT_AUDIO_ROOT))
    parser.add_argument("--public-root", default=str(DEFAULT_PUBLIC_ROOT))
    parser.add_argument("--lesson", type=int, action="append", help="B lesson number; repeatable")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--voice", default=DEFAULT_VOICE)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-public-copy", action="store_true")
    args = parser.parse_args()

    audio_root = Path(args.audio_root)
    public_root = Path(args.public_root)
    lessons = args.lesson or list(range(1, 21))

    total_files = 0
    total_chars = 0
    plan: list[tuple[int, dict]] = []
    for lesson in lessons:
        manifest = load_manifest(audio_root, lesson)
        chunks = manifest.get("chunks", [])
        total_files += len(chunks)
        total_chars += sum(len(str(chunk.get("text", ""))) for chunk in chunks)
        plan.append((lesson, manifest))

    print(f"Plan: {len(plan)} lessons, {total_files} files, {total_chars:,} chars")
    print(f"Model: {args.model}  Voice: {args.voice}")
    if args.dry_run:
        for lesson, manifest in plan[:5]:
            chunks = manifest.get("chunks", [])
            first = chunks[0]["text"] if chunks else ""
            print(f"  B{lesson}: {len(chunks)} files, first={first[:70]}")
        return 0

    generated = 0
    skipped = 0
    for lesson, manifest in plan:
        lesson_dir = audio_root / f"L{lesson}"
        update_manifest(lesson_dir / "manifest.json", manifest, model=args.model, voice=args.voice)
        for chunk in manifest.get("chunks", []):
            idx = int(chunk["idx"])
            text = str(chunk["text"])
            audio_name = str(chunk.get("audio") or f"s{idx}.mp3")
            out_path = lesson_dir / audio_name
            if out_path.exists() and out_path.stat().st_size > 1024 and not args.overwrite:
                skipped += 1
                continue
            print(f"  [B{lesson} {audio_name}] {len(text)} chars: {text[:70]}", flush=True)
            synthesize_mp3(text, out_path, model=args.model, voice=args.voice)
            generated += 1

        if not args.no_public_copy:
            public_dir = public_root / f"L{lesson}"
            public_dir.mkdir(parents=True, exist_ok=True)
            for source in lesson_dir.glob("*"):
                if source.is_file() and source.suffix in {".mp3", ".json"}:
                    shutil.copy2(source, public_dir / source.name)

    print(f"Done. generated={generated}, skipped={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
