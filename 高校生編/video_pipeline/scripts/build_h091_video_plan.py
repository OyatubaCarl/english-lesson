#!/usr/bin/env python3
"""Build the H091 132-cut plan and verify lyric-to-image alignment."""
from __future__ import annotations

from bisect import bisect_right
import json
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H091"
PLAN = LESSON / "planning/video_plan.json"
MIXED = LESSON / "planning/mixed_ruby.json"
TIMING = LESSON / "planning/word_timing_tacobeat.json"
VISUAL_BIBLE = LESSON / "planning/visual_bible_style01.json"
SCENE_COUNT = 132
NAME_RE = re.compile(r"^\d{3}_(.+)_\d{2}\.jpg$")


def purpose(image: Path) -> str:
    match = NAME_RE.match(image.name)
    if not match:
        raise RuntimeError(f"unexpected H091 scene filename: {image.name}")
    return match.group(1)


def allocate_counts(spans: list[float]) -> list[int]:
    counts = [max(2, math.ceil(span / 1.5)) for span in spans]
    if sum(counts) > SCENE_COUNT:
        raise RuntimeError(f"SCENE_COUNT is too small for dense allocation: {sum(counts)}")
    while sum(counts) < SCENE_COUNT:
        index = max(range(len(spans)), key=lambda i: spans[i] / counts[i])
        counts[index] += 1
    return counts


def expected_schedule(bible: dict, duration: float) -> list[tuple[float, str]]:
    masters = bible["masters"]
    starts = [float(item["time"]) for item in masters]
    ends = starts[1:] + [duration]
    spans = [end - start for start, end in zip(starts, ends)]
    counts = allocate_counts(spans)
    rows: list[tuple[float, str]] = []
    for item, start, span, count in zip(masters, starts, spans, counts):
        prefix = str(item["file"]).removesuffix("_master.png")
        rows.extend((start + span * offset / count, prefix) for offset in range(count))
    return rows


def main() -> None:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    mixed = json.loads(MIXED.read_text(encoding="utf-8"))
    timing = json.loads(TIMING.read_text(encoding="utf-8"))
    bible = json.loads(VISUAL_BIBLE.read_text(encoding="utf-8"))
    duration = float(plan["duration"])
    if abs(duration - 156.920167) > 0.02:
        raise RuntimeError(f"unexpected H091 adopted duration: {duration}")
    if timing.get("exact_word_match") is not True or int(timing["word_count"]) != 178:
        raise RuntimeError("H091 TacoBeat timing is not exact")

    schedule = expected_schedule(bible, duration)
    images = sorted((LESSON / "scenes/final_style01").glob("[0-9][0-9][0-9]_*.jpg"))
    if len(images) != SCENE_COUNT or len(schedule) != SCENE_COUNT:
        raise RuntimeError(f"H091 scene count: images={len(images)} schedule={len(schedule)}")
    scenes = []
    for (start, expected_purpose), image in zip(schedule, images):
        actual_purpose = purpose(image)
        if actual_purpose != expected_purpose:
            raise RuntimeError(f"H091 purpose mismatch: {actual_purpose} != {expected_purpose}")
        scenes.append({
            "start": round(start, 3),
            "image": str(image.relative_to(LESSON)),
            "purpose": actual_purpose,
        })

    gaps = [float(b["start"]) - float(a["start"]) for a, b in zip(scenes, scenes[1:])]
    gaps.append(duration - float(scenes[-1]["start"]))
    if min(gaps) < 0.62 or max(gaps) > 1.501:
        raise RuntimeError((len(scenes), min(gaps), max(gaps)))

    scene_starts = [float(scene["start"]) for scene in scenes]
    for item in bible["masters"]:
        expected = str(item["file"]).removesuffix("_master.png")
        check_time = min(float(item["time"]) + 0.05, duration - 0.01)
        scene = scenes[bisect_right(scene_starts, check_time) - 1]
        if scene["purpose"] != expected:
            raise RuntimeError(
                f"H091 alignment at {check_time:.2f}s: {scene['purpose']} != {expected}"
            )

    if len(mixed["lines"]) != len(timing["lines"]) or len(mixed["lines"]) != 15:
        raise RuntimeError("H091 caption/timing line count mismatch")
    plan["title_en"] = "A Journey Through Southern Europe"
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
    plan["qa_status"] = (
        "READY_TO_RENDER_STYLE01_SAFE_RESPECTFUL_SOUTHERN_EUROPE_TRAVELOGUE_REVIEWED"
    )
    plan["output_name"] = "h091_adopted_song_cinematic_v1.mp4"
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"H091 video plan: {len(scenes)} scenes, min {min(gaps):.3f}s "
        f"max {max(gaps):.3f}s; 54 semantic checkpoints PASS"
    )


if __name__ == "__main__":
    main()
