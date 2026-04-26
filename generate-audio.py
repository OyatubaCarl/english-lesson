#!/usr/bin/env python3
"""Generate OpenAI TTS audio per shadowing chunk for index.html.

Audio is generated per *chunk* — the same sentence segmentation that the
shadowing UI uses (split by . ! ? and further by , ; if a sentence exceeds
15 words). Both the long-passage player and the shadowing player can reuse
the same files.

Setup:
    pip install openai python-dotenv beautifulsoup4
    # add OPENAI_API_KEY="sk-..." to .env

Usage:
    python generate-audio.py --book high1 --lesson 1   # test 1 lesson
    python generate-audio.py --book high1              # all H1-H45
    python generate-audio.py                           # everything

Output per lesson:
    audio/{book}/L{lesson_id}/s{n}.mp3   # one mp3 per chunk, n=1..N
    audio/{book}/L{lesson_id}/manifest.json  # ordered list with text, para_idx
"""
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

# ---- OpenAI TTS voices (中性・アナウンス調 candidates) ----
VOICES = {
    "alloy":   "neutral, news-anchor style (recommended)",
    "echo":    "deep male, calm narrator",
    "fable":   "warm British male, storyteller",
    "onyx":    "very deep male, authoritative",
    "nova":    "bright female, educational tone",
    "shimmer": "soft female, gentle",
}
DEFAULT_VOICE = "alloy"  # most neutral/announcer-like, good for English learners
DEFAULT_MODEL = "tts-1-hd"  # tts-1 ($0.015/1k) or tts-1-hd ($0.030/1k)

SH_MAX_WORDS = 15  # must match the JS constant


def split_long_sentence(sent: str) -> list[str]:
    """Mirror of the JS splitLongSentence_ function."""
    words = sent.split()
    if len(words) <= SH_MAX_WORDS:
        return [sent]
    parts = [p.strip() for p in re.split(r"[,;]\s+", sent) if p.strip()]
    chunks: list[str] = []
    buf = ""
    for p in parts:
        bw = len(buf.split()) if buf else 0
        pw = len(p.split())
        if bw + pw > SH_MAX_WORDS and buf:
            chunks.append(buf)
            buf = p
        else:
            buf = (buf + ", " + p) if buf else p
    if buf:
        chunks.append(buf)
    return chunks


def chunks_from_paragraph(p_text: str) -> list[str]:
    """Mirror of the JS extractSentences per-paragraph logic."""
    txt = re.sub(r"\s+", " ", p_text).strip()
    txt = re.sub(r"^\([^)]+\)\s*", "", txt)  # drop leading "(Name)" speaker markers
    if not txt:
        return []
    sentences = re.findall(r"[^.!?]+[.!?]+|[^.!?]+$", txt) or [txt]
    out: list[str] = []
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        for c in split_long_sentence(s):
            c = c.strip()
            if c:
                out.append(c)
    return out


def text_of_paragraph(p_el) -> str:
    """Extract clean text from a <p> in en-body, dropping <rt> furigana annotations."""
    clone = BeautifulSoup(str(p_el), "html.parser").find("p")
    for rt in clone.find_all("rt"):
        rt.decompose()
    text = clone.get_text(separator=" ", strip=True)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)
    return text.strip()


def extract_lessons(html_path: Path, books: list[str] | None) -> list[dict]:
    """Return [{book, lesson_id, chunks:[{idx, text, para_idx}, ...]}, ...]."""
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    out = []
    for book_div in soup.select("div.book[data-book]"):
        book = book_div["data-book"]
        if books and book not in books:
            continue
        for sec in book_div.select(":scope > section.lesson"):
            lesson_id = sec.get("data-lesson", "?")
            en_body = sec.find("div", class_="en-body")
            if not en_body:
                continue
            chunks = []
            idx = 1
            for para_idx, p in enumerate(en_body.find_all("p"), start=1):
                p_text = text_of_paragraph(p)
                for c in chunks_from_paragraph(p_text):
                    chunks.append({"idx": idx, "text": c, "para": para_idx})
                    idx += 1
            if chunks:
                out.append({"book": book, "lesson_id": lesson_id, "chunks": chunks})
    return out


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
    # Force UTF-8 stdout/stderr on Windows so Japanese characters in chunk
    # text don't crash the print statements (cp932 cannot encode em dashes).
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    load_dotenv()  # pick up OPENAI_API_KEY from .env

    ap = argparse.ArgumentParser()
    ap.add_argument("--book", action="append", help="filter by book (beginner/middle/high1/high2/high3); repeatable")
    ap.add_argument("--lesson", help="filter by data-lesson value (e.g. 60). only with --book")
    ap.add_argument("--limit", type=int, help="stop after N lessons (for test runs)")
    ap.add_argument("--voice", choices=list(VOICES.keys()), default=DEFAULT_VOICE)
    ap.add_argument("--model", choices=["tts-1", "tts-1-hd"], default=DEFAULT_MODEL,
                    help="tts-1 = $0.015/1k chars, tts-1-hd = $0.030/1k chars")
    ap.add_argument("--out", default="audio")
    ap.add_argument("--html", default="index.html")
    ap.add_argument("--dry-run", action="store_true", help="list what would be generated, no API call")
    args = ap.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key and not args.dry_run:
        sys.exit("ERROR: set OPENAI_API_KEY in .env or environment")

    print(f"Voice: {args.voice} ({VOICES[args.voice]})  Model: {args.model}")

    lessons = extract_lessons(Path(args.html), args.book)
    if args.lesson:
        lessons = [l for l in lessons if l["lesson_id"] == args.lesson]
    if args.limit:
        lessons = lessons[: args.limit]

    total_chars = sum(len(c["text"]) for l in lessons for c in l["chunks"])
    total_files = sum(len(l["chunks"]) for l in lessons)
    rate = 0.030 if args.model == "tts-1-hd" else 0.015
    cost = total_chars / 1000 * rate
    print(f"Plan: {len(lessons)} lessons, {total_files} chunks, {total_chars:,} chars total")
    print(f"Estimated cost: ${cost:.2f} ({args.model} @ ${rate:.3f}/1k chars)")
    if args.dry_run:
        for l in lessons[:3]:
            sample = l["chunks"][0]["text"][:60]
            print(f"  {l['book']}/L{l['lesson_id']}: {len(l['chunks'])} chunks, "
                  f"first = {sample}...")
        return 0

    client = OpenAI(api_key=api_key)
    out_root = Path(args.out)
    generated, skipped = 0, 0
    for l in lessons:
        ldir = out_root / l["book"] / f"L{l['lesson_id']}"
        ldir.mkdir(parents=True, exist_ok=True)
        # write/refresh manifest first (cheap, idempotent, useful for debugging)
        manifest = {
            "book": l["book"],
            "lesson_id": l["lesson_id"],
            "voice": args.voice,
            "model": args.model,
            "chunks": l["chunks"],
        }
        (ldir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        for c in l["chunks"]:
            out_path = ldir / f"s{c['idx']}.mp3"
            if out_path.exists():
                skipped += 1
                continue
            print(f"  [{l['book']}/L{l['lesson_id']} s{c['idx']}] {len(c['text'])} chars: {c['text'][:50]}...", flush=True)
            for attempt in range(3):
                try:
                    synth(client, args.model, args.voice, c["text"], out_path)
                    generated += 1
                    break
                except Exception as e:
                    msg = str(e)
                    print(f"    attempt {attempt+1} failed: {msg[:120]}", flush=True)
                    if "rate" in msg.lower() or "429" in msg:
                        time.sleep(5 * (attempt + 1))
                    elif attempt == 2:
                        raise
                    else:
                        time.sleep(2)
    print(f"Done. generated={generated}, skipped(existing)={skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
