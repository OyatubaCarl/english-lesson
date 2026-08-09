#!/usr/bin/env python3
"""Build the H083 107-cut video plan and verify lyric-to-image alignment."""
from __future__ import annotations

from bisect import bisect_right
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H083"
PLAN = LESSON / "planning/video_plan.json"
MIXED = LESSON / "planning/mixed_ruby.json"
TIMING = LESSON / "planning/word_timing_tacobeat.json"
VISUAL_BIBLE = LESSON / "planning/visual_bible_style01.json"
SCENE_COUNT = 107
NAME_RE = re.compile(r"^\d{3}_(.+)_\d{2}\.jpg$")


def purpose(image: Path) -> str:
    match = NAME_RE.match(image.name)
    if not match:
        raise RuntimeError(f"unexpected H083 scene filename: {image.name}")
    return match.group(1)


def main() -> None:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    mixed = json.loads(MIXED.read_text(encoding="utf-8"))
    timing = json.loads(TIMING.read_text(encoding="utf-8"))
    bible = json.loads(VISUAL_BIBLE.read_text(encoding="utf-8"))
    duration = float(plan["duration"])
    if abs(duration - 138.480979) > 0.02:
        raise RuntimeError(f"unexpected H083 adopted duration: {duration}")
    if timing.get("exact_word_match") is not True or int(timing["word_count"]) != 200:
        raise RuntimeError("H083 TacoBeat timing is not exact")

    unit = duration / SCENE_COUNT
    images = sorted((LESSON / "scenes/final_style01").glob("[0-9][0-9][0-9]_*.jpg"))
    if len(images) != SCENE_COUNT:
        raise RuntimeError(f"H083 scene count: {len(images)} != {SCENE_COUNT}")
    scenes = [
        {
            "start": round(unit * ordinal, 3),
            "image": str(image.relative_to(LESSON)),
            "purpose": purpose(image),
        }
        for ordinal, image in enumerate(images)
    ]
    gaps = [float(b["start"]) - float(a["start"]) for a, b in zip(scenes, scenes[1:])]
    gaps.append(duration - float(scenes[-1]["start"]))
    if min(gaps) < 1.291 or max(gaps) > 1.297:
        raise RuntimeError((len(scenes), min(gaps), max(gaps)))

    scene_starts = [float(scene["start"]) for scene in scenes]
    for item in bible["masters"]:
        expected = str(item["file"]).removesuffix("_master.png")
        check_time = min(float(item["time"]) + 0.2, duration - 0.01)
        scene = scenes[bisect_right(scene_starts, check_time) - 1]
        if scene["purpose"] != expected:
            raise RuntimeError(
                f"H083 alignment at {check_time:.2f}s: {scene['purpose']} != {expected}"
            )

    if len(mixed["lines"]) != len(timing["lines"]) or len(mixed["lines"]) != 14:
        raise RuntimeError("H083 caption/timing line count mismatch")
    plan["title_en"] = "Cinema and the Power of Story"
    plan["scenes"] = scenes
    plan["captions"] = [
        {
            "start": float(timed["start"]),
            "end": float(timed["end"]),
            "en": line["english"],
            "ja": line["mixed"],
        }
        for line, timed in zip(mixed["lines"], timing["lines"])
    ]
    plan["qa_status"] = "READY_TO_RENDER_STYLE01_CINEMA_HISTORY_AND_FICTION_GUARDRAILS_REVIEWED"
    plan["output_name"] = "h083_adopted_song_cinematic_v1.mp4"
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"H083 video plan: {len(scenes)} scenes, min {min(gaps):.3f}s "
        f"max {max(gaps):.3f}s; lyric checkpoints PASS"
    )


if __name__ == "__main__":
    main()
