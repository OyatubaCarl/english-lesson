#!/usr/bin/env python3
"""Build the dense and historically careful Style01 scene plan for H059."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H059"
PLAN_PATH = LESSON / "planning" / "video_plan.json"


GROUPS = [
    (0.0, 17.295, 1, 11, "psychology_intro", "behaviorと心を複数の科学的方法で研究"),
    (17.295, 31.98, 12, 9, "wundt_lab", "1879年頃のWundtとライプツィヒ大学実験室"),
    (31.98, 39.92, 21, 5, "measurement", "測定・記録・再確認による学問的出発"),
    (39.92, 51.5, 26, 7, "pavlov_food", "Pavlovが犬の食物への自然反応を観察"),
    (51.5, 71.84, 33, 13, "conditioning", "ベルを食物前に反復するclassical conditioning"),
    (71.84, 85.4, 46, 8, "freud_theory", "Freudがunconscious desiresを歴史的理論として提唱"),
    (85.4, 100.18, 54, 9, "freud_spread", "議論と出版を伴うunconscious概念の普及"),
    (100.18, 108.0, 63, 5, "milgram_setup", "偽の電撃装置と安全なlearner役を含む実験状況"),
    (108.0, 115.82, 68, 5, "milgram_distress", "権威の促しに迷い・問い返す参加者"),
    (115.82, 121.88, 73, 4, "debrief", "learner役の無事と実験後のdebriefing"),
    (121.88, 133.2, 77, 7, "decision_bias", "不確実なdecisionを歪めうるbiasesの研究"),
    (133.2, 143.58, 84, 6, "student_decision", "主人公がemotion・assumption・事実を分けて再考"),
    (143.58, 157.4, 90, 9, "therapy", "anxiety・depressionに対する協働的なtherapy"),
    (157.4, 176.480167, 99, 12, "mind_science", "心の科学を自己理解と支援のtoolとして結ぶ"),
]


def main() -> None:
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    scenes: list[dict[str, object]] = []
    for group_start, group_end, first, count, prefix, purpose in GROUPS:
        interval = (group_end - group_start) / count
        for offset in range(count):
            number = first + offset
            image = f"scenes/final_style01/{number:03d}_{prefix}_{offset + 1:02d}.png"
            path = LESSON / image
            if not path.is_file():
                raise FileNotFoundError(path)
            scenes.append({
                "start": round(group_start + interval * offset, 3),
                "image": image,
                "purpose": purpose,
            })

    gaps = [
        round(float(right["start"]) - float(left["start"]), 3)
        for left, right in zip(scenes, scenes[1:])
    ]
    if len(scenes) != 110 or min(gaps) < 1.30 or max(gaps) > 1.90:
        raise RuntimeError(
            f"invalid density: count={len(scenes)} min={min(gaps)} max={max(gaps)}"
        )

    plan["scenes"] = scenes
    plan["qa_status"] = "READY_TO_RENDER_STYLE01"
    plan["output_name"] = "h059_adopted_song_cinematic_v1.mp4"
    PLAN_PATH.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"H059 video plan: {len(scenes)} scenes, "
        f"min gap {min(gaps):.3f}s, max gap {max(gaps):.3f}s"
    )


if __name__ == "__main__":
    main()
