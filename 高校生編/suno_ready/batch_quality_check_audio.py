#!/usr/bin/env python3
"""Run lyric QA for a lesson range while loading Whisper only once."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from faster_whisper import WhisperModel

from quality_check_audio import alignment_metrics, extract_lyrics, words


def analyze(model: WhisperModel, model_name: str, sheet: Path, audio: Path) -> dict:
    expected_words = words(extract_lyrics(sheet))
    segments, info = model.transcribe(
        str(audio),
        language="en",
        beam_size=5,
        word_timestamps=True,
        vad_filter=False,
        condition_on_previous_text=False,
        temperature=0,
    )
    segment_rows = []
    transcript_parts = []
    actual_confidences = []
    for segment in segments:
        transcript_parts.append(segment.text.strip())
        segment_rows.append({
            "start": round(segment.start, 3),
            "end": round(segment.end, 3),
            "text": segment.text.strip(),
        })
        if segment.words:
            for word in segment.words:
                token_count = len(words(word.word))
                actual_confidences.extend([float(word.probability)] * token_count)

    transcript = " ".join(part for part in transcript_parts if part)
    actual_words = words(transcript)
    if len(actual_confidences) != len(actual_words):
        actual_confidences = [0.0] * len(actual_words)
    metrics = alignment_metrics(expected_words, actual_words, actual_confidences)

    last_index = metrics["last_matched_expected_index"]
    reached_end = last_index is not None and last_index >= max(0, len(expected_words) - 8)
    ratio = len(actual_words) / max(1, len(expected_words))
    structural_passed = (
        metrics["coverage"] >= 0.72
        and metrics["longest_missing_run"] <= 8
        and reached_end
        and 0.60 <= ratio <= 1.55
    )
    wrong_lyric_review = (
        metrics["suspicious_substitution_words"] >= 2
        or metrics["suspicious_content_substitution"]
    )
    if wrong_lyric_review:
        verdict = "REVIEW_WRONG_LYRIC"
    elif not structural_passed:
        verdict = "REVIEW_OMISSION_OR_STRUCTURE"
    else:
        verdict = "PASS"

    return {
        "schema_version": 2,
        "sheet": str(sheet),
        "audio": str(audio),
        "model": model_name,
        "audio_duration": round(info.duration, 3),
        "verdict": verdict,
        "reached_expected_ending": reached_end,
        "transcribed_to_expected_ratio": round(ratio, 4),
        **metrics,
        "transcript": transcript,
        "segments": segment_rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sheets", type=Path, required=True)
    parser.add_argument("--audio-root", type=Path, required=True)
    parser.add_argument("--candidate", choices=("candidate1", "candidate2", "candidate3"), required=True)
    parser.add_argument("--start", type=int, default=48)
    parser.add_argument("--end", type=int, default=160)
    parser.add_argument("--lessons", help="Comma-separated lesson numbers; overrides start/end")
    parser.add_argument("--model", default="small")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    lessons = (
        [int(value) for value in args.lessons.split(",") if value.strip()]
        if args.lessons
        else list(range(args.start, args.end + 1))
    )
    summaries = []
    total = len(lessons)
    for offset, lesson in enumerate(lessons, start=1):
        sheet = args.sheets / f"H{lesson:03d}.md"
        lesson_dir = args.audio_root / f"H{lesson:03d}"
        audio = lesson_dir / f"{args.candidate}-full.mp3"
        output = lesson_dir / f"{args.candidate}_QA.json"
        if not audio.exists():
            raise FileNotFoundError(audio)

        if output.exists() and not args.force:
            report = json.loads(output.read_text(encoding="utf-8"))
            if report.get("schema_version") != 2:
                report = analyze(model, args.model, sheet, audio)
                output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        else:
            report = analyze(model, args.model, sheet, audio)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        summary = {
            "lesson": lesson,
            "candidate": args.candidate,
            "verdict": report["verdict"],
            "coverage": report["coverage"],
            "precision": report["precision"],
            "replacement_count": report["replacement_count"],
            "high_confidence_replacement_count": report["high_confidence_replacement_count"],
            "suspicious_substitution_words": report["suspicious_substitution_words"],
            "longest_missing_run": report["longest_missing_run"],
        }
        summaries.append(summary)
        print(
            f"[{offset:03d}/{total:03d}] H{lesson:03d} {report['verdict']} "
            f"coverage={report['coverage']:.4f} "
            f"high_conf_replacements={report['high_confidence_replacement_count']}",
            flush=True,
        )

    label = (
        "selected"
        if args.lessons
        else f"H{args.start:03d}-H{args.end:03d}"
    )
    summary_path = args.audio_root / f"qa_summary_{args.candidate}_{label}.json"
    summary_path.write_text(json.dumps(summaries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    verdict_counts = {}
    for row in summaries:
        verdict_counts[row["verdict"]] = verdict_counts.get(row["verdict"], 0) + 1
    print(json.dumps({
        "summary": str(summary_path),
        "count": len(summaries),
        "verdict_counts": verdict_counts,
    }, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
