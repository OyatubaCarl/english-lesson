#!/usr/bin/env python3
"""Screen a Suno lesson song for wrong words, omissions, repeats, and order errors."""

from __future__ import annotations

import argparse
import json
import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Optional

from faster_whisper import WhisperModel


def extract_lyrics(sheet: Path) -> str:
    text = sheet.read_text(encoding="utf-8")
    match = re.search(r"## Lyrics\s+```text\s*\n(.*?)\n```", text, re.S)
    if not match:
        raise ValueError(f"Lyrics block not found: {sheet}")
    return match.group(1).strip()


ORDINALS = {
    "1st": "first", "2nd": "second", "3rd": "third", "4th": "fourth",
    "5th": "fifth", "6th": "sixth", "7th": "seventh", "8th": "eighth",
    "9th": "ninth", "10th": "tenth", "11th": "eleventh", "12th": "twelfth",
    "13th": "thirteenth", "14th": "fourteenth", "15th": "fifteenth",
    "16th": "sixteenth", "17th": "seventeenth", "18th": "eighteenth",
    "19th": "nineteenth", "20th": "twentieth", "21st": "twenty first",
    "22nd": "twenty second", "23rd": "twenty third", "24th": "twenty fourth",
    "25th": "twenty fifth", "26th": "twenty sixth", "27th": "twenty seventh",
    "28th": "twenty eighth", "29th": "twenty ninth", "30th": "thirtieth",
    "31st": "thirty first",
}

PHRASE_EQUIVALENTS = {
    "net like": "netlike",
    "work days": "workdays",
    "cyber attacks": "cyberattacks",
    "hot spots": "hotspots",
    "brush stroke": "brushstroke",
    "post war": "postwar",
    "mountain side": "mountainside",
    "car maker": "carmaker",
    "co exist": "coexist",
    "re evaluated": "reevaluated",
    "all so": "also",
    "a new": "anew",
    "u s": "us",
}

WORD_EQUIVALENTS = {
    "centres": "centers",
    "harbour": "harbor",
    "labour": "labor",
    "manoeuvre": "maneuver",
    "urbanisation": "urbanization",
    "to": "to",
    "too": "to",
    "two": "to",
}


def words(text: str) -> list[str]:
    text = re.sub(r"\[[^]]+\]", " ", text)
    text = text.replace("’", "'").lower()
    for numeric, spelled in ORDINALS.items():
        text = re.sub(rf"(?<![a-z0-9]){re.escape(numeric)}(?![a-z0-9])", spelled, text)
    for phrase, replacement in PHRASE_EQUIVALENTS.items():
        text = re.sub(rf"\b{re.escape(phrase)}\b", replacement, text)
    tokens = re.findall(r"[a-z]+(?:'[a-z]+)?", text)
    normalized = []
    for token in tokens:
        if token.endswith("'s") and len(token) > 2:
            token = token[:-2]
        normalized.append(WORD_EQUIVALENTS.get(token, token))
    return normalized


FUNCTION_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "being", "but",
    "by", "for", "from", "had", "has", "have", "he", "her", "hers", "him",
    "his", "i", "if", "in", "into", "is", "it", "its", "me", "my", "nor",
    "not", "of", "on", "or", "our", "ours", "she", "so", "than", "that",
    "the", "their", "theirs", "them", "they", "this", "those", "to", "us",
    "was", "we", "were", "what", "when", "where", "which", "who", "why",
    "will", "with", "would", "you", "your", "yours",
}


def alignment_metrics(
    expected: list[str],
    actual: list[str],
    actual_confidences: Optional[list[float]] = None,
) -> dict:
    matcher = SequenceMatcher(a=expected, b=actual, autojunk=False)
    opcodes = matcher.get_opcodes()
    blocks = [block for block in matcher.get_matching_blocks() if block.size]
    matched_expected = {i for block in blocks for i in range(block.a, block.a + block.size)}
    matched = len(matched_expected)

    missing_runs: list[dict] = []
    run_start = None
    for i in range(len(expected) + 1):
        missing = i < len(expected) and i not in matched_expected
        if missing and run_start is None:
            run_start = i
        elif not missing and run_start is not None:
            missing_runs.append({
                "start": run_start,
                "length": i - run_start,
                "words": expected[run_start:i],
            })
            run_start = None

    first_match = min(matched_expected) if matched_expected else None
    last_match = max(matched_expected) if matched_expected else None
    longest = max((run["length"] for run in missing_runs), default=0)

    replacements: list[dict] = []
    insertions: list[dict] = []
    deletions: list[dict] = []
    for tag, i1, i2, j1, j2 in opcodes:
        if tag == "equal":
            continue
        row = {
            "expected_start": i1,
            "actual_start": j1,
            "expected": expected[i1:i2],
            "actual": actual[j1:j2],
        }
        if actual_confidences is not None and j2 > j1:
            confidence_slice = actual_confidences[j1:j2]
            row["actual_confidence"] = round(
                sum(confidence_slice) / len(confidence_slice), 4
            )
        if tag == "replace":
            row["substitution_words"] = min(i2 - i1, j2 - j1)
            row["has_content_word"] = any(
                word not in FUNCTION_WORDS for word in expected[i1:i2] + actual[j1:j2]
            )
            replacements.append(row)
        elif tag == "insert":
            insertions.append(row)
        elif tag == "delete":
            deletions.append(row)

    high_confidence_replacements = [
        row for row in replacements
        if row.get("actual_confidence", 0.0) >= 0.72
    ]
    suspicious_substitution_words = sum(
        row["substitution_words"] for row in high_confidence_replacements
    )
    suspicious_content_substitution = any(
        row["has_content_word"] for row in high_confidence_replacements
    )
    return {
        "expected_words": len(expected),
        "transcribed_words": len(actual),
        "matched_words": matched,
        "coverage": round(matched / max(1, len(expected)), 4),
        "precision": round(matched / max(1, len(actual)), 4),
        "first_matched_expected_index": first_match,
        "last_matched_expected_index": last_match,
        "longest_missing_run": longest,
        "largest_missing_runs": sorted(missing_runs, key=lambda row: row["length"], reverse=True)[:8],
        "replacement_count": len(replacements),
        "replacement_spans": replacements[:16],
        "insertion_spans": insertions[:12],
        "deletion_spans": deletions[:12],
        "high_confidence_replacement_count": len(high_confidence_replacements),
        "suspicious_substitution_words": suspicious_substitution_words,
        "suspicious_content_substitution": suspicious_content_substitution,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("sheet", type=Path)
    parser.add_argument("audio", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", default="small")
    args = parser.parse_args()

    expected_text = extract_lyrics(args.sheet)
    expected_words = words(expected_text)
    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        str(args.audio),
        language="en",
        beam_size=5,
        word_timestamps=True,
        vad_filter=False,
        condition_on_previous_text=False,
        temperature=0,
    )
    segment_rows = []
    transcript_parts = []
    actual_confidences: list[float] = []
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
    report = {
        "sheet": str(args.sheet),
        "audio": str(args.audio),
        "model": args.model,
        "audio_duration": round(info.duration, 3),
        "verdict": verdict,
        "reached_expected_ending": reached_end,
        "transcribed_to_expected_ratio": round(ratio, 4),
        **metrics,
        "transcript": transcript,
        "segments": segment_rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in (
        "verdict", "audio_duration", "expected_words", "transcribed_words",
        "matched_words", "coverage", "precision", "longest_missing_run",
        "reached_expected_ending", "transcribed_to_expected_ratio",
        "replacement_count", "high_confidence_replacement_count",
        "suspicious_substitution_words", "suspicious_content_substitution",
    )}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
