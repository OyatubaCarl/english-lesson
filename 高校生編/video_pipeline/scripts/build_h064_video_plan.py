#!/usr/bin/env python3
"""Build the dense, art-historically corrected Style01 scene plan for H064."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H064"
PLAN_PATH = LESSON / "planning" / "video_plan.json"


GROUPS = (
    (0.0, 12.08, 1, 8, "malaga_birth", "1881年10月25日、地中海の港町マラガに生まれる"),
    (12.08, 27.18, 9, 9, "multimedia", "painterとしてpainting・sculpture・版画・陶芸・舞台へ展開"),
    (27.18, 37.06, 18, 6, "blue_period", "1901〜1904年、パリとバルセロナを往復したBlue Period"),
    (37.06, 40.5, 24, 2, "rose_period", "1904年ごろからRose Periodへ色調が移る"),
    (40.5, 43.46, 26, 2, "media_change", "一つのstyleに留まらず媒体と表現を変える"),
    (43.46, 50.38, 28, 4, "preparatory", "1906〜1907年の多数の準備作と1916年までの非公開"),
    (50.38, 59.9, 32, 6, "geometry", "人体と空間を幾何学的shapeへ再構成"),
    (59.9, 71.84, 38, 7, "braque_collab", "ピカソとブラックの共同実験からCubismが発展"),
    (71.84, 81.36, 45, 6, "single_perspective", "単一perspectiveに基づく自然主義的再現"),
    (81.36, 90.78, 51, 6, "multiple_views", "複数角度・時間のshapeを一枚のcanvasで分解・再構成"),
    (90.78, 99.8, 57, 6, "guernica_aftermath", "1937年4月26日の爆撃後、民間人のsufferingと支援"),
    (99.8, 103.5, 63, 2, "receives_news", "既にあったスペイン館依頼と爆撃報道へ向き合う"),
    (103.5, 111.0, 65, 5, "creation_documented", "5月1日〜6月4日の巨大painting制作をドラ・マールが記録"),
    (111.0, 119.035, 70, 5, "pavilion_viewers", "1937年スペイン館で反戦のsymbolとして受け止められる"),
    (119.035, 123.68, 75, 3, "later_media", "戦後も陶芸・版画・sculptureへstyleを変え続ける"),
    (123.68, 133.6, 78, 6, "older_drawing", "晩年の単純化と出典不確かな子ども発言"),
    (133.6, 149.520979, 84, 10, "critical_legacy", "contemporary artへの大きな影響と現在の批判的検討"),
)


def main() -> None:
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    scenes: list[dict[str, object]] = []
    for group_start, group_end, first, count, prefix, purpose in GROUPS:
        interval = (group_end - group_start) / count
        for offset in range(count):
            number = first + offset
            image = f"scenes/final_style01/{number:03d}_{prefix}_{offset + 1:02d}.png"
            if not (LESSON / image).is_file():
                raise FileNotFoundError(LESSON / image)
            scenes.append({
                "start": round(group_start + interval * offset, 3),
                "image": image,
                "purpose": purpose,
            })
    gaps = [
        round(float(right["start"]) - float(left["start"]), 3)
        for left, right in zip(scenes, scenes[1:])
    ]
    if len(scenes) != 93 or min(gaps) < 1.30 or max(gaps) > 1.90:
        raise RuntimeError(
            f"invalid density: count={len(scenes)} min={min(gaps)} max={max(gaps)}"
        )
    plan["scenes"] = scenes
    plan["qa_status"] = "READY_TO_RENDER_STYLE01"
    plan["output_name"] = "h064_adopted_song_cinematic_v1.mp4"
    PLAN_PATH.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"H064 video plan: {len(scenes)} scenes, "
        f"min gap {min(gaps):.3f}s, max gap {max(gaps):.3f}s"
    )


if __name__ == "__main__":
    main()
