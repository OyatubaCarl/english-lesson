#!/usr/bin/env python3
"""Build a TacoBeat timing chart from a lesson's exact adopted lyrics.

Unlike the generic TacoBeat importer, this script does not allow an ASR spelling
error to become the alignment transcript.  The adopted lyrics are the transcript;
MMS_FA, onset snapping, BPM detection, holds, and fillers remain the TacoBeat
pipeline used for the game charts.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
PIPELINE = HERE.parent
PROJECT = PIPELINE.parent.parent
TACOBEAT_SCRIPT = PROJECT / "taco_beat" / "make_chart.py"
IMPORT_SCRIPT = HERE / "import_tacobeat_word_timing.py"
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['’][A-Za-z]+)?")


ONES = [
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
    "seventeen", "eighteen", "nineteen",
]
TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


TACO = load_module("tacobeat_make_chart", TACOBEAT_SCRIPT)
IMPORTER = load_module("tacobeat_timing_importer", IMPORT_SCRIPT)


def exact_words(mixed: dict) -> list[tuple[str, float]]:
    words = [
        token.lower().replace("’", "'")
        for line in mixed["lines"]
        for token in WORD_RE.findall(line["english"])
    ]
    if not words:
        raise ValueError("adopted lyrics contain no English words")
    return [(word, 0.0) for word in words]


def number_words(value: int) -> str:
    """Return a compact acoustic token for a displayed integer.

    MMS_FA only accepts alphabetic transcript tokens. Four-digit dates in the
    1100s-1900s are read in the usual year style (1928 -> nineteen twenty-eight)
    while the chart continues to display the original numeric token.
    """
    if value < 20:
        return ONES[value]
    if value < 100:
        return TENS[value // 10] + (ONES[value % 10] if value % 10 else "")
    if value < 1000:
        return ONES[value // 100] + "hundred" + (number_words(value % 100) if value % 100 else "")
    if 1100 <= value <= 1999:
        first, last = divmod(value, 100)
        return number_words(first) + (number_words(last) if last else "hundred")
    if value < 10000:
        return ONES[value // 1000] + "thousand" + (number_words(value % 1000) if value % 1000 else "")
    return "".join(ONES[int(digit)] for digit in str(value))


def alignment_word(word: str) -> str:
    return number_words(int(word)) if word.isdigit() else word


def chart_word(word: str) -> str:
    """Normalise display words like TacoBeat while retaining numeric tokens."""
    stripped = word.strip().strip('.,!?;:"()…').lower()
    cleaned = re.sub(r"[^a-z0-9']", "", stripped)
    return TACO.SPELL_FIX.get(cleaned, cleaned)


def build(lesson_root: Path, output_root: Path) -> Path:
    plan_path = lesson_root / "planning" / "video_plan.json"
    mixed_path = lesson_root / "planning" / "mixed_ruby.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    mixed = json.loads(mixed_path.read_text(encoding="utf-8"))
    lesson_id = str(plan["lesson"]).lower()
    chart_id = f"{lesson_id}_adopted"
    audio = (lesson_root / plan["audio"]).resolve()
    if not audio.exists():
        raise FileNotFoundError(audio)

    songs_dir = output_root / "songs"
    charts_dir = output_root / "charts"
    cache_dir = output_root / ".cache" / chart_id
    for directory in (songs_dir, charts_dir, cache_dir):
        directory.mkdir(parents=True, exist_ok=True)

    mp3 = songs_dir / f"{chart_id}.mp3"
    wav = cache_dir / f"{chart_id}_16k.wav"
    TACO.encode_song(audio, mp3)
    TACO.make_wav16k(mp3, wav)

    expected = exact_words(mixed)
    print(f"[3/8] 採用歌詞を正解transcriptとして使用: {len(expected)}語", flush=True)
    alignment_transcript = [(alignment_word(word), start) for word, start in expected]
    acoustic_alignment = TACO.force_align(wav, alignment_transcript)
    aligned = [
        (chart_word(expected[index][0]), timing)
        for index, (_, timing) in enumerate(acoustic_alignment)
    ]
    expected_normalised = [chart_word(word) for word, _ in expected]
    aligned_words = [word for word, _ in aligned]
    if aligned_words != expected_normalised:
        raise RuntimeError("MMS_FA output no longer matches the adopted lyric transcript")

    flux, frame_t, onsets = TACO.onset_envelope(wav)
    snapped = TACO.snap_function_words(aligned, onsets)
    bpm, phase = TACO.estimate_bpm(flux, frame_t)
    duration = float(frame_t[-1]) + TACO.N_FFT / 2 / TACO.SR
    beat = TACO.build_beat(snapped, bpm, phase, duration)
    chart_path = charts_dir / f"{chart_id}.js"
    chart_path.write_text(TACO.render_js(beat, bpm), encoding="utf-8")
    print(f"[8/8] 採用歌詞TacoBeat譜面: {chart_path}", flush=True)

    timing = IMPORTER.build(mixed_path, chart_path, audio)
    timing["method"] = (
        "TacoBeat: exact adopted lyrics + MMS_FA forced alignment + onset snapping"
    )
    timing["transcript_source"] = "exact adopted lyrics (ASR substitutions prohibited)"
    timing_path = lesson_root / "planning" / "word_timing_tacobeat.json"
    timing_path.write_text(
        json.dumps(timing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"PASS {plan['lesson']}: {timing['word_count']} words, "
        f"{timing['first_word_start']:.3f}-{timing['last_word_end']:.3f}s",
        flush=True,
    )
    return timing_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("lesson_dirs", nargs="+", type=Path)
    parser.add_argument("--output-root", type=Path, default=PIPELINE / "tacobeat_adopted")
    args = parser.parse_args()
    for lesson_dir in args.lesson_dirs:
        build(lesson_dir.resolve(), args.output_root.resolve())


if __name__ == "__main__":
    main()
