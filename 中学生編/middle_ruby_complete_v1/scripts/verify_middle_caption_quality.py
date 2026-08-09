#!/usr/bin/env python3
"""Verify canonical coverage, ruby completeness and natural-weave guards."""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

from prepare_middle_ruby import (
    KANJI_RE,
    build_dictionary,
    normalize_en,
    read_json,
    sentence_tokens,
    stems,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PROJECT = ROOT.parent.parent
LESSONS = PROJECT / "taco_course_mockup" / "middle_lessons.json"
PLANNING = ROOT / "planning" / "lessons"
TOMATO_REPORT = ROOT / "planning" / "tomatomato_contract_verification.json"
REPORT = ROOT / "planning" / "caption_quality_verification.json"
BROKEN_WEAVE_RE = re.compile(
    r"(?:"
    r"[A-Za-z]+\s+(?:するです|しましたん|するば|していますの|しましたの|する、|するながら)"
    r"|お\s+[A-Za-z]+"
    r"|[A-Za-z]+\s+官"
    r"|[A-Za-z]+\s+(?:Near|Under|Beside|While)\b"
    r")",
    re.I,
)
PAREN_RE = re.compile(r"[（）()]")


def replacement_occurs(replacement: dict, english: str) -> bool:
    wanted = sentence_tokens(replacement["english"])
    tokens = sentence_tokens(english)
    if len(wanted) > 1:
        normalized_wanted = [normalize_en(token) for token in wanted]
        normalized_tokens = [normalize_en(token) for token in tokens]
        return any(
            normalized_tokens[start : start + len(normalized_wanted)]
            == normalized_wanted
            for start in range(len(tokens) - len(wanted) + 1)
        )
    return any(
        stems(replacement["english"]) & stems(token)
        for token in tokens
    )


def main() -> None:
    lesson_data = read_json(LESSONS)
    _, glossary = build_dictionary(lesson_data)
    results = []
    sources = Counter()
    rendered_unique = set()
    total_targets = total_replacements = 0
    for number in range(1, 46):
        item = read_json(PLANNING / f"L{number:02d}.json")
        canonical = {(row["word"].lower(), row["ja"]) for row in glossary[number]}
        lesson_rendered = {
            (replacement["canonical_word"].lower(), replacement["canonical_meaning"])
            for line in item["lines"]
            for replacement in line["replacements"]
        }
        rendered_unique.update((number, *row) for row in lesson_rendered)
        line_checks = []
        for line in item["lines"]:
            targets = line["canonical_targets"]
            replacements = line["replacements"]
            target_words = [row["canonical_word"].lower() for row in targets]
            replacement_words = [row["canonical_word"].lower() for row in replacements]
            total_targets += len(targets)
            total_replacements += len(replacements)
            sources.update(row["source"] for row in replacements)
            line_checks.append(
                {
                    "line": line["line"],
                    "targets_equal_replacements": Counter(target_words)
                    == Counter(replacement_words),
                    "no_duplicate_canonical_word": len(replacement_words)
                    == len(set(replacement_words)),
                    "all_replacements_canonical": all(
                        (row["canonical_word"].lower(), row["canonical_meaning"])
                        in canonical
                        for row in replacements
                    ),
                    "all_replacements_occur_in_sung_line": all(
                        replacement_occurs(row, line["english"])
                        for row in replacements
                    ),
                    "canonical_sources_only": all(
                        row["source"].startswith("canonical_new_word")
                        for row in replacements
                    ),
                    "every_english_segment_has_meaning_ruby": all(
                        run.get("ruby")
                        for run in line["runs"]
                        if run["type"] == "en"
                    ),
                    "every_japanese_kanji_has_reading_ruby": all(
                        not KANJI_RE.search(part["text"]) or bool(part.get("ruby"))
                        for run in line["runs"]
                        if run["type"] == "ja"
                        for part in run["parts"]
                    ),
                    "no_known_broken_direct_weave": not BROKEN_WEAVE_RE.search(
                        line["mixed"]
                    ),
                    "no_parenthetical_word_gloss": not PAREN_RE.search(line["mixed"]),
                    "no_parenthetical_replacement_source": all(
                        "parenthetical" not in row["source"]
                        for row in replacements
                    ),
                    "no_unrubied_ascii_in_japanese_runs": all(
                        not re.search(r"[A-Za-z]", run["text"])
                        for run in line["runs"]
                        if run["type"] == "ja"
                    ),
                    "no_double_japanese_comma": "、、" not in line["mixed"],
                }
            )
        checks = {
            "line_count_matches": item["line_count"] == len(item["lines"]),
            "all_canonical_words_rendered": lesson_rendered == canonical,
            "all_line_checks_pass": all(
                all(value for key, value in row.items() if key != "line")
                for row in line_checks
            ),
        }
        results.append(
            {
                "lesson": number,
                "canonical_words": len(canonical),
                "rendered_words": len(lesson_rendered),
                "checks": checks,
                "status": "PASS" if all(checks.values()) else "FAIL",
                "failed_lines": [
                    row
                    for row in line_checks
                    if not all(value for key, value in row.items() if key != "line")
                ],
            }
        )
    tomato = read_json(TOMATO_REPORT) if TOMATO_REPORT.exists() else {}
    counts = {
        "lessons": len(results),
        "pass": sum(row["status"] == "PASS" for row in results),
        "fail": sum(row["status"] == "FAIL" for row in results),
        "canonical_unique_words": sum(row["canonical_words"] for row in results),
        "rendered_unique_words": len(rendered_unique),
        "canonical_target_segments": total_targets,
        "rendered_segments": total_replacements,
        "replacement_sources": dict(sorted(sources.items())),
    }
    global_checks = {
        "all_45_lessons_pass": counts["pass"] == 45,
        "full_current_canonical_coverage": counts["canonical_unique_words"]
        == counts["rendered_unique_words"]
        == 411,
        "target_and_replacement_segments_match": total_targets == total_replacements,
        "tomatomato_contract_pass": tomato.get("status") == "PASS",
        "no_parenthetical_replacement_sources": not any(
            "parenthetical" in source for source in sources
        ),
    }
    report = {
        "verified_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS" if all(global_checks.values()) else "FAIL",
        "checks": global_checks,
        "counts": counts,
        "results": results,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], **global_checks, **counts}, ensure_ascii=False))
    print(REPORT)
    if report["status"] != "PASS":
        raise SystemExit("middle caption quality verification failed")


if __name__ == "__main__":
    main()
