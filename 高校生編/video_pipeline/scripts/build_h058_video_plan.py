#!/usr/bin/env python3
"""Build the dense, legally careful Style01 scene plan for H058."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H058"
PLAN_PATH = LESSON / "planning" / "video_plan.json"


GROUPS = [
    (0.0, 20.88, 1, 13, "court", "裁判所と法による紛争解決を導入"),
    (20.88, 26.88, 14, 4, "investigation", "非暴力事件の現場を記録・保全"),
    (26.88, 31.88, 18, 3, "arrest", "法的根拠を確認したsuspectのarrest"),
    (31.88, 42.88, 21, 7, "prosecution", "prosecutionがevidenceの十分性を検討"),
    (42.88, 51.62, 28, 6, "trial", "prosecutionとdefenseが主張を提示"),
    (51.62, 59.06, 34, 5, "witness", "witnessのoathとtestimony"),
    (59.06, 67.78, 39, 6, "defense", "defendantがattorneyと防御を準備"),
    (67.78, 86.96, 45, 12, "judge_jury", "judgeと一部法域のjuryの役割を分離"),
    (86.96, 104.06, 57, 11, "presumption", "innocent until proven guiltyと立証責任"),
    (104.06, 110.92, 68, 4, "not_guilty", "Case Aはevidence不十分でnot guilty"),
    (110.92, 118.68, 72, 5, "sentencing", "別のCase Bでverdict後のsentence hearing"),
    (118.68, 125.76, 77, 5, "alternatives", "prison・fine・community serviceの条件別選択肢"),
    (125.76, 137.30, 82, 7, "appeal", "上級courtが記録と法的誤りをreview"),
    (137.30, 169.640167, 89, 19, "justice_future", "victims・被告・地域の尊厳と制度改善"),
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
    if len(scenes) != 107 or min(gaps) < 1.30 or max(gaps) > 1.90:
        raise RuntimeError(
            f"invalid density: count={len(scenes)} min={min(gaps)} max={max(gaps)}"
        )

    plan["scenes"] = scenes
    plan["qa_status"] = "READY_TO_RENDER_STYLE01"
    plan["output_name"] = "h058_adopted_song_cinematic_v1.mp4"
    PLAN_PATH.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"H058 video plan: {len(scenes)} scenes, "
        f"min gap {min(gaps):.3f}s, max gap {max(gaps):.3f}s"
    )


if __name__ == "__main__":
    main()
