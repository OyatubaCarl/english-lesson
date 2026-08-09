#!/usr/bin/env python3
"""Second-opinion lyric QA using MLX Whisper large-v3-turbo."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import mlx_whisper

from quality_check_audio import alignment_metrics, extract_lyrics, words


def analyze(model_name: str, sheet: Path, audio: Path) -> dict:
    expected_words = words(extract_lyrics(sheet))
    result = mlx_whisper.transcribe(
        str(audio),
        path_or_hf_repo=model_name,
        language="en",
        word_timestamps=True,
        temperature=0,
        condition_on_previous_text=False,
        verbose=False,
    )
    transcript = result["text"].strip()
    actual_words = words(transcript)
    actual_confidences = []
    segment_rows = []
    for segment in result["segments"]:
        segment_rows.append({
            "start": round(float(segment["start"]), 3),
            "end": round(float(segment["end"]), 3),
            "text": segment["text"].strip(),
        })
        for word in segment.get("words", []):
            token_count = len(words(word["word"]))
            actual_confidences.extend([float(word.get("probability", 0.0))] * token_count)
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
    duration = max((row["end"] for row in segment_rows), default=0.0)
    return {
        "schema_version": 3,
        "sheet": str(sheet),
        "audio": str(audio),
        "model": model_name,
        "audio_duration": duration,
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
    parser.add_argument("--lessons", required=True)
    parser.add_argument("--model", default="mlx-community/whisper-large-v3-turbo")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    lessons = [int(value) for value in args.lessons.split(",") if value.strip()]
    summaries = []
    for offset, lesson in enumerate(lessons, start=1):
        sheet = args.sheets / f"H{lesson:03d}.md"
        lesson_dir = args.audio_root / f"H{lesson:03d}"
        audio = lesson_dir / f"{args.candidate}-full.mp3"
        output = lesson_dir / f"{args.candidate}_QA_mlx.json"
        if output.exists() and not args.force:
            report = json.loads(output.read_text(encoding="utf-8"))
        else:
            report = analyze(args.model, sheet, audio)
            output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        summaries.append({
            "lesson": lesson,
            "candidate": args.candidate,
            "verdict": report["verdict"],
            "coverage": report["coverage"],
            "high_confidence_replacement_count": report["high_confidence_replacement_count"],
            "suspicious_substitution_words": report["suspicious_substitution_words"],
        })
        print(
            f"[{offset:03d}/{len(lessons):03d}] H{lesson:03d} {report['verdict']} "
            f"coverage={report['coverage']:.4f} "
            f"high_conf_replacements={report['high_confidence_replacement_count']}",
            flush=True,
        )

    summary_path = args.audio_root / f"qa_summary_{args.candidate}_mlx_selected.json"
    summary_path.write_text(json.dumps(summaries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    counts = {}
    for row in summaries:
        counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1
    print(json.dumps({"summary": str(summary_path), "verdict_counts": counts}), flush=True)


if __name__ == "__main__":
    main()
