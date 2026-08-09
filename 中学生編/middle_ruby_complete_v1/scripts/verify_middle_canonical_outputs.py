#!/usr/bin/env python3
"""Verify L1-L45 canonical-vocabulary mixed-caption video outputs."""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MIDDLE = ROOT.parent
PROJECT = MIDDLE.parent
PLANNING = ROOT / "planning" / "lessons"
OUTPUT = ROOT / "output"
LESSONS = PROJECT / "taco_course_mockup" / "middle_lessons.json"
REPORT = ROOT / "planning" / "canonical_vocab_video_progress.json"
EDITION = "v4_inline_canonical_vocab"
KANJI_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff々ヶ]")
IRREGULAR_BASE = {
    "bought": "buy",
    "came": "come",
    "cried": "cry",
    "did": "do",
    "done": "do",
    "drank": "drink",
    "eaten": "eat",
    "felt": "feel",
    "gave": "give",
    "gone": "go",
    "had": "have",
    "knew": "know",
    "known": "know",
    "made": "make",
    "paid": "pay",
    "ran": "run",
    "said": "say",
    "saw": "see",
    "seen": "see",
    "spoke": "speak",
    "spoken": "speak",
    "swam": "swim",
    "swum": "swim",
    "taught": "teach",
    "thought": "think",
    "threw": "throw",
    "thrown": "throw",
    "told": "tell",
    "took": "take",
    "taken": "take",
    "understood": "understand",
    "went": "go",
    "written": "write",
    "wrote": "write",
}
DERIVED_BASE = {
    "biggest": "big",
    "cheaper": "cheap",
    "easily": "easy",
    "fastest": "fast",
    "happily": "happy",
    "longer": "long",
    "peacefully": "peaceful",
    "warmer": "warm",
    "younger": "young",
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def stems(text: str) -> set[str]:
    word = normalize(text)
    result = {word, IRREGULAR_BASE.get(word, word), DERIVED_BASE.get(word, word)}
    for suffix, replacement in (("ies", "y"), ("ing", ""), ("ed", ""), ("es", ""), ("s", "")):
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            base = word[: -len(suffix)] + replacement
            result.add(base)
            if suffix in {"ing", "ed"}:
                result.add(word[: -len(suffix)] + "e")
                if len(base) >= 2 and base[-1] == base[-2]:
                    result.add(base[:-1])
    return result


def source_config(lesson: int) -> Path:
    if lesson == 6:
        return MIDDLE / "mio_video_l2_l10_sentence_v2" / "L6_revision_v3" / "planning" / "lesson.json"
    if 2 <= lesson <= 10:
        return MIDDLE / "mio_video_l2_l10_sentence_v2" / f"L{lesson}" / "planning" / "lesson.json"
    return MIDDLE / "mio_video_l1_l45_sentence_v3" / f"L{lesson}" / "planning" / "lesson.json"


def probe(path: Path) -> dict:
    command = ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)]
    return json.loads(subprocess.run(command, check=True, capture_output=True, text=True).stdout)


def verify(number: int, lesson_data: dict) -> dict:
    mixed = read_json(PLANNING / f"L{number:02d}.json")
    source = read_json(source_config(number))
    canonical = {
        (item["w"], item["ja"])
        for paragraph in lesson_data["vocabSentences"]
        for item in paragraph["words"]
    }
    replacements = [replacement for line in mixed["lines"] for replacement in line["replacements"]]
    candidates = sorted((OUTPUT / f"L{number:02d}").glob(f"*_mixed_japanese_full_ruby_{EDITION}.mp4"))
    ass_candidates = sorted((ROOT / "captions" / f"L{number:02d}").glob(f"*_english_highlight_{EDITION}.ass"))
    checks = {
        "source_line_count": mixed["line_count"] == len(source["lines"]),
        "canonical_policy_recorded": "Only canonical new vocabulary" in mixed.get("policy", ""),
        "canonical_word_and_meaning": all(
            (replacement.get("canonical_word"), replacement.get("canonical_meaning")) in canonical
            for replacement in replacements
        ),
        "replacement_occurs_in_sung_line": all(
            normalize(replacement["canonical_word"]) in normalize(line["english"])
            or any(stems(token) & stems(replacement["canonical_word"]) for token in re.findall(r"[A-Za-z]+(?:['’-][A-Za-z]+)?", line["english"]))
            for line in mixed["lines"]
            for replacement in line["replacements"]
        ),
        "canonical_sources_only": all(
            replacement.get("source", "").startswith("canonical_new_word")
            for replacement in replacements
        ),
        "inline_body_has_no_parentheses": all(
            not re.search(r"[（）()]", line["mixed"])
            for line in mixed["lines"]
        ),
        "no_parenthetical_replacement_source": all(
            "parenthetical" not in replacement.get("source", "")
            for replacement in replacements
        ),
        "every_english_segment_has_meaning_ruby": all(
            run.get("ruby") for line in mixed["lines"] for run in line["runs"] if run["type"] == "en"
        ),
        "every_japanese_kanji_segment_has_reading_ruby": all(
            not KANJI_RE.search(part["text"]) or bool(part.get("ruby"))
            for line in mixed["lines"]
            for run in line["runs"] if run["type"] == "ja"
            for part in run["parts"]
        ),
        "output_exists": len(candidates) == 1,
        "ass_exists": len(ass_candidates) == 1,
    }
    result = {"lesson": f"L{number:02d}", "checks": checks, "status": "NOT_RENDERED"}
    if candidates and ass_candidates:
        output = candidates[0]
        ass_text = ass_candidates[0].read_text(encoding="utf-8")
        info = probe(output)
        video = next((row for row in info["streams"] if row.get("codec_type") == "video"), {})
        audio = next((row for row in info["streams"] if row.get("codec_type") == "audio"), {})
        duration = float(info["format"]["duration"])
        verification_path = ROOT / "work" / f"L{number:02d}" / "qa" / f"VERIFICATION_{EDITION.upper()}.json"
        verification = read_json(verification_path) if verification_path.exists() else {}
        checks.update(
            {
                "duration_matches": abs(duration - float(source["duration"])) <= 0.08,
                "video_1920x1080_h264": video.get("codec_name") == "h264" and video.get("width") == 1920 and video.get("height") == 1080,
                "audio_aac": audio.get("codec_name") == "aac",
                "word_highlight_present": r"\c&H4D62FF&\fs72\b1" in ass_text,
                "highlight_color_only_fixed_size": r"\fs81" not in ass_text and r"\fscx" not in ass_text and r"\fscy" not in ass_text,
                "canonical_policy_in_verification": verification.get("canonical_lesson_vocabulary_only") is True
                and verification.get("noncanonical_replacements") == 0,
                "inline_mixed_body_no_parentheses_recorded": verification.get(
                    "inline_mixed_body_no_parentheses"
                )
                is True,
                "full_canonical_coverage_recorded": verification.get(
                    "canonical_vocabulary_coverage"
                )
                == "411/411",
            }
        )
        result.update(
            {
                "output": str(output.relative_to(PROJECT)),
                "duration_seconds": duration,
                "size_bytes": output.stat().st_size,
                "replacement_count": len(replacements),
            }
        )
        result["status"] = "PASS" if all(checks.values()) else "FAIL"
    return result


def main() -> None:
    lessons = read_json(LESSONS)
    results = [verify(number, lessons[number - 1]) for number in range(1, 46)]
    report = {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "edition": EDITION,
        "counts": {
            "pass": sum(row["status"] == "PASS" for row in results),
            "fail": sum(row["status"] == "FAIL" for row in results),
            "not_rendered": sum(row["status"] == "NOT_RENDERED" for row in results),
        },
        "results": results,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["counts"], ensure_ascii=False))
    if report["counts"]["fail"]:
        raise SystemExit("middle canonical-vocabulary video verification failed")


if __name__ == "__main__":
    main()
