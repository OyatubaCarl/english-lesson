#!/usr/bin/env python3
"""Import a TacoBeat chart as exact per-word video-caption timing."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['’][A-Za-z]+)?")


def normalise_word(text: str) -> str:
    words = WORD_RE.findall(text.lower().replace("’", "'"))
    if len(words) != 1:
        raise ValueError(f"caption token is not one English word: {text!r}")
    return words[0]


def read_chart(path: Path) -> tuple[list[list], float]:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"const BEAT=(\[.*\]);\s*const SONG_BPM=([0-9.]+);", text, re.S)
    if not match:
        raise ValueError(f"BEAT block not found: {path}")
    return json.loads(match.group(1)), float(match.group(2))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build(mixed_path: Path, chart_path: Path, audio_path: Path) -> dict:
    mixed = json.loads(mixed_path.read_text(encoding="utf-8"))
    beat, bpm = read_chart(chart_path)
    sung = [entry for entry in beat if entry[1]]

    caption_tokens: list[tuple[int, int, str, str]] = []
    for line_index, line in enumerate(mixed["lines"]):
        for display_index, display_word in enumerate(line["english"].split()):
            # A standalone em dash or similar punctuation is displayed but not sung.
            # Keep it in the caption while excluding it from word alignment/highlight.
            normalised_parts = WORD_RE.findall(display_word.lower().replace("’", "'"))
            if not normalised_parts:
                continue
            # Hyphenated display tokens such as ``short-tempered`` are aligned
            # as two acoustic words by MMS_FA.  Map both timings back to the
            # same display index so the complete hyphenated word stays lit and
            # the caption layout never changes.
            caption_tokens.extend(
                (line_index, display_index, display_word, part)
                for part in normalised_parts
            )

    chart_words = [normalise_word(str(entry[1])) for entry in sung]
    expected_words = [item[3] for item in caption_tokens]
    if expected_words != chart_words:
        mismatch = next(
            (index for index, pair in enumerate(zip(expected_words, chart_words)) if pair[0] != pair[1]),
            min(len(expected_words), len(chart_words)),
        )
        raise ValueError(
            "adopted lyrics and TacoBeat transcript differ at word "
            f"{mismatch + 1}: expected={expected_words[mismatch:mismatch + 4]!r}, "
            f"chart={chart_words[mismatch:mismatch + 4]!r}; "
            f"counts={len(expected_words)}/{len(chart_words)}"
        )

    lines: list[dict] = [
        {"line": line["line"], "english": line["english"], "word_timings": []}
        for line in mixed["lines"]
    ]
    for flat_index, ((line_index, display_index, display_word, _), entry) in enumerate(zip(caption_tokens, sung)):
        start = float(entry[0])
        hold_end = float(entry[3]) if len(entry) >= 4 else 0.0
        if flat_index + 1 < len(caption_tokens) and caption_tokens[flat_index + 1][0] == line_index:
            end = float(sung[flat_index + 1][0])
        elif hold_end > start:
            end = hold_end
        else:
            next_start = float(sung[flat_index + 1][0]) if flat_index + 1 < len(sung) else start + 0.8
            end = min(start + 0.8, next_start)
        lines[line_index]["word_timings"].append({
            "word": display_word,
            "display_index": display_index,
            "start": round(start, 3),
            "end": round(max(start + 0.08, end), 3),
        })

    for line in lines:
        line["start"] = line["word_timings"][0]["start"]
        line["end"] = line["word_timings"][-1]["end"]

    return {
        "lesson": mixed["lesson"],
        "method": "TacoBeat: Whisper word timestamps + MMS_FA forced alignment + onset snapping",
        "source_chart": str(chart_path.resolve()),
        "source_audio": str(audio_path.resolve()),
        "source_audio_sha256": sha256(audio_path),
        "bpm": bpm,
        "exact_word_match": True,
        "word_count": len(sung),
        "line_count": len(lines),
        "first_word_start": lines[0]["start"],
        "last_word_end": lines[-1]["end"],
        "lines": lines,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mixed_ruby", type=Path)
    parser.add_argument("chart", type=Path)
    parser.add_argument("audio", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = build(args.mixed_ruby, args.chart, args.audio)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"{args.output}: {result['word_count']} words, "
        f"{result['first_word_start']:.3f}-{result['last_word_end']:.3f}s, exact match"
    )


if __name__ == "__main__":
    main()
