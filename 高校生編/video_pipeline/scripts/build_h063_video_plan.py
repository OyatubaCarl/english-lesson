#!/usr/bin/env python3
"""Build the dense, historically corrected Style01 scene plan for H063."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H063"
PLAN_PATH = LESSON / "planning" / "video_plan.json"


GROUPS = (
    (0.0, 18.0, 1, 11, "arrival", "1960年、母ヴァンヌと現地協力者とともにゴンベへ到着"),
    (18.0, 24.76, 12, 4, "camp_team", "湖畔の調査拠点を共同で整える"),
    (24.76, 45.22, 16, 12, "fieldwork", "若い女性が異例の野外調査を率いるが単身探検にはしない"),
    (45.22, 61.0, 28, 10, "leakey", "学位前の観察力・passion・patienceをリーキーが支える"),
    (61.0, 68.4, 38, 5, "distant_observation", "遠い樹冠のchimpanzeeを双眼鏡で観察"),
    (68.4, 73.48, 43, 3, "patient_notes", "何か月もの観察と詳細な無文字ノート"),
    (73.48, 80.5, 46, 4, "habituation", "警戒から馴化へ、接触せず距離を保つ"),
    (80.5, 86.82, 50, 4, "daily_life", "採食・毛づくろい・母子・巣作りの日常"),
    (86.82, 91.5, 54, 3, "termite_selection", "草の茎と小枝を選ぶchimpanzee"),
    (91.5, 96.32, 57, 3, "toolmaking", "葉を除いたtoolでシロアリを取り出すobservation"),
    (96.32, 111.84, 60, 9, "science_boundary", "tool製作・使用を人間だけとする境界を再検討"),
    (111.84, 117.8, 69, 4, "family_emotions", "個性・母子関係・毛づくろいと感情"),
    (117.8, 122.7, 73, 3, "conflict", "協力だけでなく威嚇とconflictも非流血で記録"),
    (122.7, 134.5, 76, 7, "longterm_research", "タンザニア人研究者が世代を越えて長期観察を継続"),
    (134.5, 147.5, 83, 8, "conservation", "地域住民・研究者と進める野生動物conservation"),
    (147.5, 161.68, 91, 9, "roots_shoots", "1991年、12人の高校生との対話からRoots & Shootsが始まる"),
    (161.68, 166.0, 100, 3, "youth_action", "Hope lies in actionを地域のyouthが実行"),
    (166.0, 188.800167, 103, 14, "legacy", "2025年以後も研究・言葉・行動が次世代へ受け継がれる"),
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
    if len(scenes) != 116 or min(gaps) < 1.30 or max(gaps) > 1.90:
        raise RuntimeError(
            f"invalid density: count={len(scenes)} min={min(gaps)} max={max(gaps)}"
        )
    plan["scenes"] = scenes
    plan["qa_status"] = "READY_TO_RENDER_STYLE01"
    plan["output_name"] = "h063_adopted_song_cinematic_v1.mp4"
    PLAN_PATH.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"H063 video plan: {len(scenes)} scenes, "
        f"min gap {min(gaps):.3f}s, max gap {max(gaps):.3f}s"
    )


if __name__ == "__main__":
    main()
