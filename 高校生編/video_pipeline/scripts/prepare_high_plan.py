#!/usr/bin/env python3
"""Create an exact-English caption plan from the adopted-song QA transcript."""

from __future__ import annotations

import argparse
import difflib
import json
import os
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
PIPELINE = HERE.parent
HIGH = PIPELINE.parent
PROJECT = HIGH.parent
MANIFEST = PIPELINE / "planning" / "adopted_songs_h001_h160.json"
HIGH_LESSONS = PROJECT / "taco_course_mockup" / "high_lessons.json"


def words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+(?:'[a-z]+)?", text.lower().replace("’", "'"))


def selected_qa(row: dict) -> Path | None:
    candidate = str(row["local_candidate"])
    if candidate.startswith("rewrite_candidate"):
        rewrite_number = candidate.removeprefix("rewrite_candidate")
        path = (
            HIGH / "suno_ready" / "generated" / "rewrite_audio" / row["lesson"]
            / f"candidate{rewrite_number}_QA_mlx.json"
        )
        return path if path.exists() else None
    if candidate.isdigit():
        directory = HIGH / "suno_ready" / "generated" / "audio" / row["lesson"]
        for suffix in ("_QA_mlx.json", "_QA.json"):
            path = directory / f"candidate{candidate}{suffix}"
            if path.exists():
                return path
        return None
    if row["lesson"] == "H046":
        path = HIGH / "h46_imagen_video" / "work" / "qa_audio" / "qa_summary_candidate1_mlx_selected.json"
        return path if path.exists() else None
    if row["lesson"] == "H047":
        path = PIPELINE / "source_audio" / "H047" / "h047_QA_mlx.json"
        return path if path.exists() else None
    return None


def caption_timings(lines: list[str], qa: dict | None, duration: float) -> list[tuple[float, float]]:
    line_tokens = [words(line) for line in lines]
    expected = [token for line in line_tokens for token in line]
    line_ranges = []
    cursor = 0
    for tokens in line_tokens:
        line_ranges.append((cursor, cursor + len(tokens)))
        cursor += len(tokens)

    token_times: list[tuple[float, float] | None] = [None] * len(expected)
    if qa and qa.get("segments"):
        transcript_tokens = []
        transcript_times = []
        for segment in qa["segments"]:
            segment_words = words(segment["text"])
            if not segment_words:
                continue
            start = float(segment["start"])
            end = float(segment["end"])
            span = max(0.08 * len(segment_words), end - start)
            for index, token in enumerate(segment_words):
                transcript_tokens.append(token)
                transcript_times.append(
                    (start + span * index / len(segment_words), min(end, start + span * (index + 1) / len(segment_words)))
                )
        matcher = difflib.SequenceMatcher(a=expected, b=transcript_tokens, autojunk=False)
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                for offset in range(i2 - i1):
                    token_times[i1 + offset] = transcript_times[j1 + offset]

    known = [index for index, value in enumerate(token_times) if value]
    audio_tail = min(duration - 0.5, (float(qa.get("audio_duration", duration)) if qa else duration) - 0.1)
    if not known:
        start = min(8.0, duration * 0.08)
        span = max(0.2 * len(expected), audio_tail - start)
        token_times = [
            (start + span * index / len(expected), start + span * (index + 1) / len(expected))
            for index in range(len(expected))
        ]
    else:
        for index, value in enumerate(token_times):
            if value:
                continue
            before = max((item for item in known if item < index), default=None)
            after = min((item for item in known if item > index), default=None)
            if before is not None and after is not None:
                left = token_times[before][1]
                right = token_times[after][0]
                ratio = (index - before) / (after - before)
                point = left + (right - left) * ratio
            elif before is not None:
                point = min(audio_tail, token_times[before][1] + 0.28 * (index - before))
            else:
                point = max(0.0, token_times[after][0] - 0.28 * (after - index))
            token_times[index] = (point, min(audio_tail, point + 0.24))

    result = []
    for start_index, end_index in line_ranges:
        start = token_times[start_index][0]
        end = token_times[end_index - 1][1]
        result.append((round(start, 3), round(max(start + 0.35, end), 3)))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("lesson", type=int)
    parser.add_argument("--storyboard", default="scenes/storyboard_01.png")
    args = parser.parse_args()
    if not 1 <= args.lesson <= 160:
        raise ValueError("lesson must be H001-H160")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    row = manifest["lessons"][args.lesson - 1]
    lessons = json.loads(HIGH_LESSONS.read_text(encoding="utf-8"))
    lesson_data = lessons[args.lesson - 1]
    qa_path = selected_qa(row)
    qa = json.loads(qa_path.read_text(encoding="utf-8")) if qa_path else None
    duration = float(row["audio"]["duration_seconds"])
    lines = row["lyrics_lines"]
    timings = caption_timings(lines, qa, duration)
    root = PIPELINE / row["lesson"]
    audio_path = PROJECT / row["audio"]["path"]
    relative_audio = os.path.relpath(audio_path, root)
    title_ja = row["title"].split("—", 1)[-1].strip()
    scene_starts = [0.0]
    for fraction in (0.25, 0.50, 0.75):
        # Storyboard prompts divide the exact lyric list into four chronological
        # quarters. Switch at the corresponding lyric line, not at a raw time
        # quartile, so a short/long sung line cannot move the picture to the
        # wrong semantic section (for example, cherry blossoms over winter).
        line_index = min(len(timings) - 1, int(len(timings) * fraction))
        scene_starts.append(round(timings[line_index][0], 3))
    captions = [
        {"start": start, "end": end, "en": line, "ja": ""}
        for line, (start, end) in zip(lines, timings)
    ]
    plan = {
        "lesson": row["lesson"],
        "title_en": "",
        "title_ja": title_ja,
        "grammar_target": lesson_data["grammar"]["target"],
        "duration": duration,
        "transition": 0.8,
        "audio": relative_audio,
        "source_qa": str(qa_path.relative_to(PROJECT)) if qa_path else None,
        "qa_status": row["qa_status"],
        "output_name": f"{row['lesson'].lower()}_adopted_song_cinematic_v1.mp4",
        "scenes": [
            {"start": start, "image": args.storyboard, "panel": panel, "purpose": f"story quarter {panel}"}
            for panel, start in enumerate(scene_starts, start=1)
        ],
        "captions": captions,
    }
    path = root / "planning" / "video_plan.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(path)
    print(json.dumps({"captions": len(captions), "qa": str(qa_path) if qa_path else None, "scene_starts": scene_starts}, ensure_ascii=False))


if __name__ == "__main__":
    main()
