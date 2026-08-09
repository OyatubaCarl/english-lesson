#!/usr/bin/env python3
"""Build the dense, fact-corrected Style01 scene plan for H070."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H070"
PLAN_PATH = LESSON / "planning" / "video_plan.json"


GROUPS = (
    (0.00, 5.20, "britain_intro", 3, "18世紀後半の英国で始まる長期的な変化"),
    (5.20, 10.58, "industrial_title", 3, "マンチェスターの工業都市景観と導入"),
    (10.58, 18.10, "britain_change", 5, "技術・労働・市場・帝国が絡む不均一な変化"),
    (18.10, 26.72, "industrial_dawn", 5, "産業革命を一夜の事件にせず都市の変化で示す"),
    (26.72, 31.02, "newcomen_model", 3, "ワットが既存のニューコメン機関を調査する"),
    (31.02, 37.82, "separate_condenser", 4, "別置復水器を中心に蒸気機関の改良を示す"),
    (37.82, 42.80, "water_horse", 3, "水力と馬力が蒸気と長く併用された事実"),
    (42.80, 49.06, "steam_mill", 4, "石炭と蒸気が工場立地・稼働の制約を減らす"),
    (49.06, 53.80, "manchester_mills", 3, "マンチェスターとランカシャーの綿工場"),
    (53.80, 60.52, "liverpool_port", 4, "原綿輸入と綿製品輸出を担うリバプール港"),
    (60.52, 66.50, "rural_migration", 4, "田園から工業都市へ移る複合的な労働者一家"),
    (66.50, 72.12, "housing_arrival", 4, "移住・自然増・国外移民を受け入れる過密都市"),
    (72.12, 76.86, "urbanization", 3, "住宅・上下水道・衛生が追いつかない都市化"),
    (76.86, 81.92, "factory_condition", 3, "スピニングミュールの危険な作業環境"),
    (81.92, 86.40, "long_shift", 3, "灯火の下まで続く長時間労働"),
    (86.40, 90.70, "wage_paydesk", 3, "低い賃金を手渡す支払所と労働者の手元"),
    (90.70, 95.40, "child_mine", 3, "炭鉱で働く子どもを工場労働と区別して示す"),
    (95.40, 99.92, "child_mill", 3, "綿工場で働く子どもと家計の貧困"),
    (99.92, 104.82, "union_origins", 3, "19世紀半ば以前から続く労働者組織化"),
    (104.82, 109.40, "union_organize", 3, "規制と弾圧の中で組合を作る男女の労働者"),
    (109.40, 113.84, "strike_gate", 3, "賃金と労働時間をめぐる工場門前のストライキ"),
    (113.84, 118.40, "factory_inspector", 3, "1833年工場法と少数の工場監督"),
    (118.40, 121.98, "law_still_limited", 2, "法律後も違反と適用の穴が残る工場"),
    (121.98, 125.58, "half_time_school", 2, "段階的な就学と児童労働制限"),
    (125.58, 132.00, "living_standard", 4, "生産性と生活水準の長期的上昇"),
    (132.00, 136.84, "public_health_factors", 3, "寿命を支えた就学・公衆衛生・食料・医療"),
    (136.84, 141.20, "pollution_gap", 3, "石炭煙・汚染水路・深い貧富の差"),
    (141.20, 145.50, "enslaved_cotton", 3, "奴隷労働で生産されたアメリカ原綿との結びつき"),
    (145.50, 150.46, "pollution_return", 3, "工業化が残した環境汚染と化石燃料依存"),
    (150.46, 156.00, "museum_present", 3, "現代の生徒が産業機械と労働史を考える"),
    (156.00, 160.00, "engine_reflection", 3, "機械の進歩を振り返る短い回想"),
    (160.00, 164.00, "rights_reflection", 3, "労働者の権利獲得を振り返る短い回想"),
    (164.00, 169.20, "society_reflection", 3, "生活向上と都市の代価を同時に考える"),
    (169.20, 178.600167, "museum_final", 6, "現代社会を産業革命の延長として捉える終幕"),
)


def main() -> None:
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    scenes: list[dict[str, object]] = []
    for group_start, group_end, prefix, count, purpose in GROUPS:
        images = sorted((LESSON / "scenes" / "final_style01").glob(f"*_{prefix}_*.png"))
        if len(images) != count:
            raise RuntimeError(f"{prefix}: images={len(images)} expected={count}")
        interval = (group_end - group_start) / count
        for offset, image_path in enumerate(images):
            scenes.append({
                "start": round(group_start + interval * offset, 3),
                "image": str(image_path.relative_to(LESSON)),
                "purpose": purpose,
            })
    gaps = [
        round(float(right["start"]) - float(left["start"]), 3)
        for left, right in zip(scenes, scenes[1:])
    ]
    final_gap = float(plan["duration"]) - float(scenes[-1]["start"])
    if len(scenes) != 113 or min(gaps) < 1.30 or max(gaps + [final_gap]) > 1.90:
        raise RuntimeError(
            f"invalid density: count={len(scenes)} min={min(gaps):.3f} "
            f"max={max(gaps + [final_gap]):.3f}"
        )
    plan["scenes"] = scenes
    plan["qa_status"] = "READY_TO_RENDER_STYLE01_FACT_CHECKED"
    plan["output_name"] = "h070_adopted_song_cinematic_v1.mp4"
    PLAN_PATH.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"H070 video plan: {len(scenes)} scenes, "
        f"min gap {min(gaps):.3f}s, max gap {max(gaps + [final_gap]):.3f}s"
    )


if __name__ == "__main__":
    main()
