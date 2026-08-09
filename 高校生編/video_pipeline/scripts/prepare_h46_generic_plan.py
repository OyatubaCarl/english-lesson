#!/usr/bin/env python3
"""Adapt the established H46 ImageGen assets to the unified video pipeline."""

from __future__ import annotations

import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
PIPELINE = HERE.parent
HIGH = PIPELINE.parent
PROJECT = HIGH.parent
SOURCE_ROOT = HIGH / "h46_imagen_video"
TARGET_ROOT = PIPELINE / "H046"


def main() -> None:
    source = json.loads((SOURCE_ROOT / "planning" / "video_plan.json").read_text(encoding="utf-8"))
    manifest = json.loads((PIPELINE / "planning" / "adopted_songs_h001_h160.json").read_text(encoding="utf-8"))
    row = manifest["lessons"][45]
    lessons = json.loads((PROJECT / "taco_course_mockup" / "high_lessons.json").read_text(encoding="utf-8"))
    captions = []
    for caption in source["captions"]:
        english = re.sub(r"</?k>", "", caption["en"]).replace(r"\N", " ")
        captions.append({"start": caption["start"], "end": caption["end"], "en": english, "ja": ""})
    if [item["en"] for item in captions] != row["lyrics_lines"]:
        raise RuntimeError("H046 established timing captions do not match the adopted lyrics")
    plan = {
        "lesson": "H046",
        "title_en": source["title_en"],
        "title_ja": source["title_ja"],
        "grammar_target": lessons[45]["grammar"]["target"],
        "duration": row["audio"]["duration_seconds"],
        "transition": 1.0,
        "audio": "../../h46_imagen_video/source_audio/h46_democracy_constitution.mp3",
        "source_qa": "高校生編/h46_imagen_video/work/qa_audio/qa_summary_candidate1_mlx_selected.json",
        "qa_status": row["qa_status"],
        "output_name": "h046_democracy_constitution_adopted_song_cinematic_v1.mp4",
        "scenes": [
            {
                **scene,
                "image": "../../h46_imagen_video/" + scene["image"],
            }
            for scene in source["scenes"]
        ],
        "captions": captions,
    }
    path = TARGET_ROOT / "planning" / "video_plan.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
