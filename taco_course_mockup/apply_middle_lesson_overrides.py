#!/usr/bin/env python3
"""Apply adopted-song overrides to the generated middle-school course JSON."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path


BASE = Path(__file__).resolve().parent
LESSONS = BASE / "middle_lessons.json"
OVERRIDES = BASE / "middle_lesson_overrides.json"
FIELDS = ("vocabSentences", "passageJp", "enSentences")


def main() -> None:
    lessons = json.loads(LESSONS.read_text(encoding="utf-8"))
    overrides = json.loads(OVERRIDES.read_text(encoding="utf-8"))
    by_number = {str(row["b"]): row for row in lessons}
    changed = []
    for number, override in overrides.items():
        if number not in by_number:
            raise KeyError(f"middle lesson {number} does not exist")
        lesson = by_number[number]
        fields = []
        for field in FIELDS:
            if field in override and lesson.get(field) != override[field]:
                lesson[field] = override[field]
                fields.append(field)
        if fields:
            changed.append({"lesson": int(number), "fields": fields, "reason": override.get("reason", "")})
    rendered = json.dumps(lessons, ensure_ascii=False, indent=1) + "\n"
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=LESSONS.parent, delete=False
    ) as handle:
        handle.write(rendered)
        temporary = Path(handle.name)
    temporary.replace(LESSONS)
    print(json.dumps({"changed": changed}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
