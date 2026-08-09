#!/usr/bin/env python3
"""Verify completed mixed-Japanese/full-ruby high-school video outputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path


HERE = Path(__file__).resolve().parent
PIPELINE = HERE.parent
PROJECT = PIPELINE.parent.parent
MANIFEST = PIPELINE / "planning" / "adopted_songs_h001_h160.json"
OUTPUT = PIPELINE / "planning" / "mixed_ruby_video_progress.json"
KANJI_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff々ヶ]")
EN_WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['’][A-Za-z]+)?")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def probe(path: Path) -> dict:
    command = ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)]
    return json.loads(subprocess.run(command, check=True, capture_output=True, text=True).stdout)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(number: int, manifest_row: dict) -> dict:
    lesson = f"H{number:03d}"
    root = PIPELINE / lesson
    plan = read_json(root / "planning" / "video_plan.json")
    mixed = read_json(root / "planning" / "mixed_ruby.json")
    expected = manifest_row["lyrics_lines"]
    v5_tacobeat_candidates = sorted((root / "output").glob("*_mixed_japanese_full_ruby_v5_tacobeat_canonical_vocab_color_only.mp4"))
    v5_candidates = sorted((root / "output").glob("*_mixed_japanese_full_ruby_v5_canonical_vocab_color_only.mp4"))
    v4_tacobeat_candidates = sorted((root / "output").glob("*_mixed_japanese_full_ruby_v4_tacobeat_color_only.mp4"))
    v3_candidates = sorted((root / "output").glob("*_mixed_japanese_full_ruby_v3_tacobeat.mp4"))
    v4_candidates = sorted((root / "output").glob("*_mixed_japanese_full_ruby_v4_color_only.mp4"))
    v2_candidates = sorted((root / "output").glob("*_mixed_japanese_full_ruby_v2.mp4"))
    output_candidates = v5_tacobeat_candidates or v5_candidates or v4_tacobeat_candidates or v3_candidates or v4_candidates or v2_candidates
    exact_tacobeat_candidates = v5_tacobeat_candidates or v4_tacobeat_candidates or v3_candidates
    timing_path = root / "planning" / "word_timing_tacobeat.json"
    timing = read_json(timing_path) if timing_path.exists() else {}
    audio = (root / plan["audio"]).resolve()
    expected_word_count = sum(len(EN_WORD_RE.findall(line)) for line in expected)
    checks = {
        "exact_adopted_lyrics": [line["english"] for line in mixed["lines"]] == expected,
        "plan_matches_adopted_lyrics": [re.sub(r"</?k>", "", row["en"]).replace(r"\N", " ") for row in plan["captions"]] == expected,
        "every_english_segment_has_meaning_ruby": all(
            run.get("ruby") for line in mixed["lines"] for run in line["runs"] if run["type"] == "en"
        ),
        "every_japanese_kanji_segment_has_reading_ruby": all(
            not KANJI_RE.search(part["text"]) or bool(part.get("ruby"))
            for line in mixed["lines"]
            for run in line["runs"] if run["type"] == "ja"
            for part in run["parts"]
        ),
        "canonical_lesson_vocabulary_only": mixed.get("noncanonical_replacements") == 0
        and all(
            replacement.get("source", "").startswith("canonical_new_word")
            for line in mixed["lines"]
            for replacement in line["replacements"]
        ),
        "no_forced_easy_word_fallback": all(
            line.get("preparation") != "safe_fallback" for line in mixed["lines"]
        ),
        "output_exists": len(output_candidates) == 1,
        "tacobeat_exact_word_alignment": bool(exact_tacobeat_candidates)
        and timing.get("exact_word_match") is True
        and timing.get("word_count") == expected_word_count
        and timing.get("source_audio_sha256") == sha256(audio),
    }
    result = {"lesson": lesson, "checks": checks, "status": "NOT_RENDERED"}
    if output_candidates:
        output = output_candidates[0]
        info = probe(output)
        video = next((row for row in info["streams"] if row.get("codec_type") == "video"), {})
        audio = next((row for row in info["streams"] if row.get("codec_type") == "audio"), {})
        duration = float(info["format"]["duration"])
        expected_duration = float(plan["duration"])
        if v5_tacobeat_candidates:
            version = "v5_tacobeat_canonical_vocab_color_only"
        elif v5_candidates:
            version = "v5_canonical_vocab_color_only"
        elif v4_tacobeat_candidates:
            version = "v4_tacobeat_color_only"
        elif v3_candidates:
            version = "v3_tacobeat"
        elif v4_candidates:
            version = "v4_color_only"
        else:
            version = "v2"
        ass_files = sorted((root / "captions").glob(f"*_mixed_japanese_full_ruby_{version}.ass"))
        ass_text = ass_files[0].read_text(encoding="utf-8") if len(ass_files) == 1 else ""
        verification_name = f"VERIFICATION_MIXED_RUBY_{version.upper()}.json"
        verification = read_json(root / "output" / verification_name)
        checks.update(
            {
                "duration_matches": abs(duration - expected_duration) <= 0.08,
                "video_1920x1080_h264": video.get("codec_name") == "h264" and video.get("width") == 1920 and video.get("height") == 1080,
                "audio_aac": audio.get("codec_name") == "aac",
                "word_highlight_present": r"\c&H4D62FF&" in ass_text,
                "highlight_color_only_fixed_size": (
                    r"\c&H4D62FF&\fs66\b1" in ass_text
                    and r"\fs72" not in ass_text
                ),
                "canonical_vocab_edition_rendered": bool(v5_tacobeat_candidates or v5_candidates),
                "no_grammar_specific_verb_highlight_instruction": "S+Vの動詞を色で示しています" not in ass_text and "<k>" not in ass_text,
                "stable_camera_policy_recorded": "no jitter" in verification["camera_policy"],
                "highlight_policy_recorded": "color only" in verification.get("highlight_policy", ""),
                "canonical_vocab_policy_recorded": verification.get("canonical_lesson_vocabulary_only") is True
                and verification.get("noncanonical_replacements") == 0,
            }
        )
        result.update(
            {
                "output": str(output.relative_to(PROJECT)),
                "duration_seconds": duration,
                "expected_seconds": expected_duration,
                "duration_delta_seconds": round(duration - expected_duration, 6),
                "size_bytes": output.stat().st_size,
                "word_timing_method": timing.get("method"),
                "word_timing_word_count": timing.get("word_count"),
            }
        )
        result["status"] = "PASS" if all(checks.values()) else "FAIL"
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("lessons", nargs="*", type=int)
    args = parser.parse_args()
    manifest = read_json(MANIFEST)
    rows = {int(row["lesson"][1:]): row for row in manifest["lessons"]}
    numbers = args.lessons or list(range(1, 161))
    results = [verify(number, rows[number]) for number in numbers if (PIPELINE / f"H{number:03d}" / "planning" / "video_plan.json").exists()]
    progress = {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "counts": {
            "pass": sum(row["status"] == "PASS" for row in results),
            "fail": sum(row["status"] == "FAIL" for row in results),
            "not_rendered": sum(row["status"] == "NOT_RENDERED" for row in results),
        },
        "results": results,
    }
    OUTPUT.write_text(json.dumps(progress, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(progress["counts"], ensure_ascii=False))
    if progress["counts"]["fail"]:
        raise SystemExit("mixed-ruby video verification failed")


if __name__ == "__main__":
    main()
