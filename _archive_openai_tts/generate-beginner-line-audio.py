#!/usr/bin/env python3
"""Generate line-based TTS audio for Funnics Island beginner lessons.

The beginner UI plays one mp3 per dialogue line via each element's
``data-audio`` attribute. This script mirrors that structure exactly so the
recorded audio, picture-book lines, passage reading, and shadowing targets stay
in sync.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI


DEFAULT_MODEL = "tts-1-hd"
DEFAULT_VOICE = "alloy"


def clean_text(el) -> str:
    clone = BeautifulSoup(str(el), "html.parser").find(el.name)
    if clone is None:
        return ""
    for rt in clone.find_all("rt"):
        rt.decompose()
    text = clone.get_text(" ", strip=True)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s*-\s*", "-", text)
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)
    text = re.sub(r"^\([^)]+\)\s*", "", text)
    return text.strip()


def extract_lines(html_path: Path, lesson_filter: str | None = None) -> list[dict]:
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    book = soup.select_one('[data-b-series][data-book="beginner"]')
    if not book:
        sys.exit("ERROR: beginner book section was not found")

    lessons: list[dict] = []
    for lesson in book.select(":scope > section.lesson[data-lesson]"):
        lesson_id = lesson.get("data-lesson", "")
        if lesson_filter and lesson_id != lesson_filter:
            continue
        lines = []
        for para_idx, p in enumerate(lesson.select(".en-body p[data-audio]"), start=1):
            audio = p.get("data-audio", "")
            match = re.search(r"/s(\d+)\.mp3$", audio)
            if not match:
                continue
            text = clean_text(p)
            if not text:
                continue
            lines.append({
                "idx": int(match.group(1)),
                "text": text,
                "para": para_idx,
                "audio": Path(audio).name,
            })
        if lines:
            lessons.append({"book": "beginner", "lesson_id": lesson_id, "chunks": lines})
    return lessons


def synth(client: OpenAI, model: str, voice: str, text: str, out_path: Path) -> None:
    with client.audio.speech.with_streaming_response.create(
        model=model,
        voice=voice,
        input=text,
        response_format="mp3",
    ) as response:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        response.stream_to_file(out_path)


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument("--html", default="index.html")
    parser.add_argument("--out", default="audio")
    parser.add_argument("--lesson", help="only generate one beginner lesson number")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--voice", default=DEFAULT_VOICE)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--manifest-only", action="store_true", help="write current line manifests without generating mp3 files")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    lessons = extract_lines(Path(args.html), args.lesson)
    total_lines = sum(len(l["chunks"]) for l in lessons)
    total_chars = sum(len(c["text"]) for l in lessons for c in l["chunks"])
    print(f"Plan: {len(lessons)} beginner lessons, {total_lines} line files, {total_chars:,} chars")
    if args.dry_run:
        for lesson in lessons[:3]:
            first = lesson["chunks"][0]["text"][:70]
            print(f"  beginner/L{lesson['lesson_id']}: {len(lesson['chunks'])} lines, first = {first}...")
        return 0

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key and not args.manifest_only:
        sys.exit("ERROR: set OPENAI_API_KEY in .env or environment")

    client = None if args.manifest_only else OpenAI(api_key=api_key)
    generated = 0
    skipped = 0
    out_root = Path(args.out)
    for lesson in lessons:
        ldir = out_root / "beginner" / f"L{lesson['lesson_id']}"
        ldir.mkdir(parents=True, exist_ok=True)
        manifest = {
            "book": "beginner",
            "lesson_id": lesson["lesson_id"],
            "voice": args.voice,
            "model": args.model,
            "granularity": "line",
            "chunks": lesson["chunks"],
        }
        (ldir / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        if args.manifest_only:
            continue
        for line in lesson["chunks"]:
            out_path = ldir / line["audio"]
            if out_path.exists() and not args.overwrite:
                skipped += 1
                continue
            print(
                f"  [beginner/L{lesson['lesson_id']} {line['audio']}] "
                f"{len(line['text'])} chars: {line['text'][:60]}...",
                flush=True,
            )
            for attempt in range(3):
                try:
                    synth(client, args.model, args.voice, line["text"], out_path)
                    generated += 1
                    break
                except Exception as exc:
                    msg = str(exc)
                    print(f"    attempt {attempt + 1} failed: {msg[:160]}", flush=True)
                    if attempt == 2:
                        raise
                    time.sleep(5 * (attempt + 1))
    print(f"Done. generated={generated}, skipped(existing)={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
