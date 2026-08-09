#!/usr/bin/env python3
"""Guard the TacosParty TomatoMato contract while video captions change.

The video caption generator may improve its own line-level Japanese/English
mixture, but it must not silently change the shared ``vocabSentences`` data
that drives TomatoMato.  This script snapshots and verifies both the raw
lesson vocabulary and the projection used by ``taco_course_mockup/app.html``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PROJECT = ROOT.parent.parent
LESSONS = PROJECT / "taco_course_mockup" / "middle_lessons.json"
BASELINE = ROOT / "planning" / "tomatomato_contract_baseline.json"
REPORT = ROOT / "planning" / "tomatomato_contract_verification.json"
MID_TOMATO_MAX = 8
EXPECTED_CHANGED_LESSONS = {1, 6}
EXPECTED_AUDIO_KEY_REPLACEMENTS = {
    1: {"remove": {"ten"}, "add": {"twelve"}},
    6: {"remove": {"pretty", "picture"}, "add": {"bouquet", "card"}},
}
KATAKANA_RE = re.compile(r"^[ァ-ヶー・ー\s]+$")
NOT_PROPER = {"tv"}


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def is_proper_noun(word: str, meaning: str) -> bool:
    word = str(word or "").strip()
    if not word or not word[0].isupper():
        return False
    if word.lower() in NOT_PROPER:
        return False
    if re.search(r"[.\s]", word):
        return True
    return bool(KATAKANA_RE.fullmatch(str(meaning or "").strip()))


def tomato_projection(lessons: list[dict]) -> list[dict]:
    """Mirror buildMiddleLesson's filtering, de-duplication and 8-card cap."""
    output = []
    marker_re = re.compile(r"<([^>]+)>")
    for lesson in lessons:
        seen: set[str] = set()
        sentences = []
        for source in lesson.get("vocabSentences", []):
            words = [row for row in source.get("words", []) if row.get("w") and row.get("ja")]
            index = 0
            kept = []

            def replace(match: re.Match[str]) -> str:
                nonlocal index
                surface = match.group(1)
                if index >= len(words):
                    return surface
                row = words[index]
                index += 1
                if is_proper_noun(row["w"], row["ja"]):
                    return row["w"]
                key = str(row["w"]).strip().lower().replace("’", "'")
                if key in seen:
                    return row["w"]
                seen.add(key)
                kept.append({"w": row["w"], "ja": row["ja"]})
                return match.group(0)

            text = marker_re.sub(replace, str(source.get("text", "")))
            if kept:
                sentences.append({"text": text, "words": kept})
        visible = sentences[:MID_TOMATO_MAX]
        output.append(
            {
                "lesson": lesson.get("b"),
                "sentences": visible,
                "word_count": sum(len(row["words"]) for row in visible),
                "audio_keys": sorted({
                    row["w"].strip().lower()
                    for sentence in visible
                    for row in sentence["words"]
                }),
            }
        )
    return output


def snapshot() -> dict:
    lessons = json.loads(LESSONS.read_text(encoding="utf-8"))
    raw_vocab = [
        {"lesson": lesson.get("b"), "vocabSentences": lesson.get("vocabSentences", [])}
        for lesson in lessons
    ]
    projection = tomato_projection(lessons)
    return {
        "source": str(LESSONS.relative_to(PROJECT)),
        "lesson_count": len(lessons),
        "raw_vocab_sha256": digest(raw_vocab),
        "tomatomato_projection_sha256": digest(projection),
        "tomatomato_sentence_count": sum(len(row["sentences"]) for row in projection),
        "tomatomato_word_count": sum(row["word_count"] for row in projection),
        "tomatomato_audio_key_count": len({
            key for lesson in projection for key in lesson["audio_keys"]
        }),
        "lessons": [
            {
                "lesson": row["lesson"],
                "sentences": len(row["sentences"]),
                "words": row["word_count"],
                "sha256": digest(row),
            }
            for row in projection
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-baseline", action="store_true")
    args = parser.parse_args()
    current = snapshot()
    if args.write_baseline:
        BASELINE.parent.mkdir(parents=True, exist_ok=True)
        BASELINE.write_text(
            json.dumps(current, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(BASELINE)
        return
    if not BASELINE.exists():
        raise FileNotFoundError(f"Run with --write-baseline first: {BASELINE}")
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    baseline_lessons = {row["lesson"]: row for row in baseline["lessons"]}
    current_lessons = {row["lesson"]: row for row in current["lessons"]}
    changed_lessons = {
        number
        for number in current_lessons
        if current_lessons[number]["sha256"] != baseline_lessons[number]["sha256"]
    }
    lessons = json.loads(LESSONS.read_text(encoding="utf-8"))
    projection = {row["lesson"]: row for row in tomato_projection(lessons)}
    expected_keys = all(
        replacement["add"] <= set(projection[number]["audio_keys"])
        and not (replacement["remove"] & set(projection[number]["audio_keys"]))
        for number, replacement in EXPECTED_AUDIO_KEY_REPLACEMENTS.items()
    )
    checks = {
        "projection_changes_limited_to_declared_lessons": changed_lessons
        == EXPECTED_CHANGED_LESSONS,
        "declared_audio_key_replacements_applied": expected_keys,
        "tomatomato_sentence_count_unchanged": current["tomatomato_sentence_count"]
        == baseline["tomatomato_sentence_count"],
        "tomatomato_word_count_unchanged": current["tomatomato_word_count"]
        == baseline["tomatomato_word_count"],
        "tomatomato_audio_keys_unchanged": current["tomatomato_audio_key_count"]
        == baseline["tomatomato_audio_key_count"],
    }
    report = {
        "verified_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "declared_changes": {
            "lessons": sorted(EXPECTED_CHANGED_LESSONS),
            "audio_key_replacements": {
                str(number): {
                    key: sorted(values) for key, values in replacement.items()
                }
                for number, replacement in EXPECTED_AUDIO_KEY_REPLACEMENTS.items()
            },
        },
        "changed_lessons": sorted(changed_lessons),
        "baseline": baseline,
        "current": current,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], **checks}, ensure_ascii=False))
    print(REPORT)
    if report["status"] != "PASS":
        raise SystemExit("TomatoMato contract changed")


if __name__ == "__main__":
    main()
