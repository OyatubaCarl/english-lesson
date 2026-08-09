#!/usr/bin/env python3
"""Create a sentence-per-image video config without altering the original config."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


TRANSITIONS = [
    "smoothleft",
    "circleopen",
    "hblur",
    "diagtl",
    "slideup",
    "dissolve",
    "radial",
    "pixelize",
    "smoothright",
    "diagbr",
]

LINE_TO_SCENE = {
    3: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9],
    6: [0, 1, 2, 3, 4, 4, 5, 6, 7],
    8: [0, 1, 2, 3, 3, 4, 5, 6],
    10: [0, 1, 2, 3, 4, 4, 5, 6, 7, 8, 9],
}


def load_beat(path: Path) -> list[list[object]]:
    source = path.read_text(encoding="utf-8")
    match = re.search(r"const BEAT=(\[.*\]);", source, re.S)
    if not match:
        raise RuntimeError(f"BEAT array not found: {path}")
    return json.loads(match.group(1))


def first_token(line: dict) -> int:
    indices = line.get("indices")
    return int(indices[0]) if indices else int(line["start_index"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("lesson", type=int)
    args = parser.parse_args()

    middle_root = Path(__file__).resolve().parents[3]
    original_root = middle_root / "mio_video_l2_l10"
    v2_root = middle_root / "mio_video_l2_l10_sentence_v2"
    lesson = args.lesson
    original_path = original_root / f"L{lesson}" / "planning" / "lesson.json"
    config = json.loads(original_path.read_text(encoding="utf-8"))
    beat = load_beat(Path(config["project_root"]) / config["chart"])

    lesson_dir = v2_root / f"L{lesson}"
    scene_paths = sorted((lesson_dir / "scenes").glob("*.png"))
    line_to_scene = LINE_TO_SCENE.get(
        lesson, list(range(len(config["lines"])))
    )
    expected = max(line_to_scene) + 1
    if len(scene_paths) != expected:
        raise RuntimeError(
            f"L{lesson}: expected {expected} sentence images, found "
            f"{len(scene_paths)}"
        )

    groups: list[tuple[int, list[int]]] = []
    for line_index, scene_index in enumerate(line_to_scene):
        if not groups or groups[-1][0] != scene_index:
            groups.append((scene_index, [line_index]))
        else:
            groups[-1][1].append(line_index)

    shots = []
    for shot_index, (scene_index, line_indices) in enumerate(groups):
        if shot_index == 0:
            start = 0.0
        else:
            line = config["lines"][line_indices[0]]
            start = max(0.0, float(beat[first_token(line)][0]) - 0.05)
        if shot_index + 1 < len(groups):
            next_line_index = groups[shot_index + 1][1][0]
            next_line = config["lines"][next_line_index]
            end = max(start + 0.5, float(beat[first_token(next_line)][0]) - 0.05)
        else:
            end = float(config["duration"])

        if shot_index % 4 == 0:
            start_center, end_center = [0.46, 0.48], [0.54, 0.48]
            start_zoom, end_zoom = 1.03, 1.16
        elif shot_index % 4 == 1:
            start_center, end_center = [0.56, 0.48], [0.44, 0.48]
            start_zoom, end_zoom = 1.13, 1.04
        elif shot_index % 4 == 2:
            start_center, end_center = [0.50, 0.43], [0.50, 0.54]
            start_zoom, end_zoom = 1.04, 1.17
        else:
            start_center, end_center = [0.50, 0.54], [0.50, 0.45]
            start_zoom, end_zoom = 1.15, 1.05

        shot = {
            "image": f"scenes/{scene_paths[scene_index].name}",
            "start": round(start, 6),
            "end": round(end, 6),
            "start_center": start_center,
            "end_center": end_center,
            "start_zoom": start_zoom,
            "end_zoom": end_zoom,
            "intent": (
                "英文ごとに独立生成した画像を、主題を保つ範囲で緩やかに"
                "パン・ズームする"
            ),
        }
        if shot_index:
            shot["transition"] = TRANSITIONS[(shot_index - 1) % len(TRANSITIONS)]
        shots.append(shot)

    config["slug"] = f"{config['slug']}_sentence_v2"
    config["transition_duration"] = 0.42
    config["shots"] = shots
    config["sentence_image_count"] = len(scene_paths)
    config["line_to_scene"] = line_to_scene

    planning_dir = lesson_dir / "planning"
    planning_dir.mkdir(parents=True, exist_ok=True)
    output_path = planning_dir / "lesson.json"
    output_path.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(output_path)


if __name__ == "__main__":
    main()
