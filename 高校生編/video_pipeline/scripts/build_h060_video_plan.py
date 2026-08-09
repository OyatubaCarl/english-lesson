#!/usr/bin/env python3
"""Build the dense and historically careful Style01 scene plan for H060."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H060"
PLAN_PATH = LESSON / "planning" / "video_plan.json"


GROUPS = (
    (0.0, 8.4, 1, 5, "hiroshima_morning", "1945年8月6日朝の広島と架空の家族の日常"),
    (8.4, 14.84, 6, 4, "hiroshima_rescue", "同日午後の広島で生存者が水と互助で救援"),
    (14.84, 20.2, 10, 4, "nagasaki_aid", "山に囲まれた長崎の被害と仮救護所"),
    (20.2, 31.76, 14, 7, "months_care", "即時だけでなく数か月続いた診療・記録・追悼"),
    (31.76, 37.0, 21, 4, "nuclear_age", "核weapon時代を測定・試験施設・政策判断で表現"),
    (37.0, 46.024, 25, 6, "cold_war", "二陣営の核軍拡と閉じた外交卓によるCold War"),
    (46.024, 53.3, 31, 5, "world_threat", "世界各地の恐怖・避難訓練・市民の平和運動"),
    (53.3, 61.705, 36, 5, "npt_signature", "1968年に署名のため開放された核不拡散treaty"),
    (61.705, 69.267, 41, 5, "npt_three_pillars", "非拡散・軍縮・平和利用という未完の継続作業"),
    (69.267, 86.18, 46, 10, "post_cold_war", "冷戦後も続く複数地域のconflictと人道対応"),
    (86.18, 97.38, 56, 7, "refugees", "refugeesとvictimsの移動・薬・学校・住居支援"),
    (97.38, 112.38, 63, 9, "un_mediation", "円卓のnegotiation・mediationと現地支援"),
    (112.38, 122.68, 72, 7, "council_limits", "安保理の一票で決議が止まり対応力が制限"),
    (122.68, 145.84, 79, 14, "reconciliation", "戦争不在を超えた傾聴・尊重・共同修復"),
    (145.84, 167.880979, 93, 14, "memory_future", "広島・長崎の記憶を僕たちが未来へ継承"),
)


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
    if len(scenes) != 106 or min(gaps) < 1.30 or max(gaps) > 1.90:
        raise RuntimeError(
            f"invalid density: count={len(scenes)} min={min(gaps)} max={max(gaps)}"
        )

    plan["scenes"] = scenes
    plan["qa_status"] = "READY_TO_RENDER_STYLE01"
    plan["output_name"] = "h060_adopted_song_cinematic_v1.mp4"
    PLAN_PATH.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"H060 video plan: {len(scenes)} scenes, "
        f"min gap {min(gaps):.3f}s, max gap {max(gaps):.3f}s"
    )


if __name__ == "__main__":
    main()
