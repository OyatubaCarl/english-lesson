#!/usr/bin/env python3
"""Build the dense and fact-corrected Style01 scene plan for H062."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H062"
PLAN_PATH = LESSON / "planning" / "video_plan.json"


GROUPS = (
    (0.0, 11.32, 1, 7, "watershed", "雨水・河川・河口・海がつながる流域"),
    (11.32, 18.26, 8, 5, "river_sampling", "歌詞の年間800万トン推計と河口の現地調査"),
    (18.26, 21.908, 13, 2, "truck_scale", "トラック1台分は実投棄ではなく規模の比喩"),
    (21.908, 34.34, 15, 8, "north_pacific", "北太平洋の分散したgarbage高濃度海域を調査"),
    (34.34, 39.76, 23, 4, "currents", "海流がdebrisを広い水柱に集積・分散"),
    (39.76, 53.22, 27, 9, "weathering", "plasticが光・塩・風・波でmicroplasticへ微細化"),
    (53.22, 64.2, 36, 7, "foodweb", "プランクトンから魚への食物網と未解明点"),
    (64.2, 67.805, 43, 2, "seafood_research", "海産物中の粒子と人の健康影響を継続研究"),
    (67.805, 76.2, 45, 5, "seabird_rescue", "海鳥の誤食・絡まりリスクを非扇情的に調査"),
    (76.2, 88.22, 50, 8, "coral_threats", "coral礁の高水温・酸性化・陸由来汚染・ごみの複合threat"),
    (88.22, 98.34, 58, 7, "policy_store", "レジ袋有料化と不要な使い捨てplasticのban"),
    (98.34, 104.34, 65, 4, "reuse_industry", "再使用設計・回収・選別・recycling技術"),
    (104.34, 110.34, 69, 4, "materials_test", "生分解性表示と海水中分解を同一視しない材料試験"),
    (110.34, 117.64, 73, 5, "systems", "個人だけでなく政府・企業・研究・地域が連携"),
    (117.64, 122.512, 78, 3, "daily_choices", "reduce・再使用・recyclingを日常で実行"),
    (122.512, 137.840167, 81, 10, "ocean_future", "小さな選択と制度・設計・回収基盤がつながるoceanの未来"),
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
    if len(scenes) != 90 or min(gaps) < 1.30 or max(gaps) > 1.90:
        raise RuntimeError(
            f"invalid density: count={len(scenes)} min={min(gaps)} max={max(gaps)}"
        )
    plan["scenes"] = scenes
    plan["qa_status"] = "READY_TO_RENDER_STYLE01"
    plan["output_name"] = "h062_adopted_song_cinematic_v1.mp4"
    PLAN_PATH.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"H062 video plan: {len(scenes)} scenes, "
        f"min gap {min(gaps):.3f}s, max gap {max(gaps):.3f}s"
    )


if __name__ == "__main__":
    main()
