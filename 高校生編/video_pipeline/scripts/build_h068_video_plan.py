#!/usr/bin/env python3
"""Build the dense, historically corrected Style01 scene plan for H068."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H068"
PLAN_PATH = LESSON / "planning" / "video_plan.json"


GROUPS = (
    (0.0, 20.98, 1, 13, "bread_finance", "国家財政危機、凶作、パン価格高騰、地域差のあるfamine"),
    (20.98, 40.14, 14, 12, "tax_privilege", "tax負担、peasantsと都市貧困層、身分特権、王室との格差"),
    (40.14, 47.52, 26, 5, "enlightenment", "啓蒙思想、財政、アメリカ独立革命、政治対立という複数要因"),
    (47.52, 54.52, 31, 4, "estates_general", "三部会の代表性と投票方法をめぐる対立"),
    (54.52, 61.70, 35, 5, "tennis_oath", "国民議会と球戯場の誓い、libertyを制度へ結ぶ過程"),
    (61.70, 67.16, 40, 4, "invalides_arms", "アンヴァリッドで武器を得て火薬を求める民衆"),
    (67.16, 75.30, 44, 5, "bastille_storm", "バスティーユを要塞兼監獄・火薬庫として描く"),
    (75.30, 84.42, 49, 6, "bastille_aftermath", "少数の囚人、負傷者、火薬と記録、revolutionの象徴的転換点"),
    (84.42, 90.42, 55, 4, "declaration", "国民Assemblyによる権利宣言の審議と採択"),
    (90.42, 96.42, 59, 4, "rights_exclusions", "declaredされた普遍的権利と女性・植民地奴隷制への未実現"),
    (96.42, 100.22, 63, 2, "republic_1792", "1792年9月に君主制を廃しrepublicを宣言"),
    (100.22, 108.02, 65, 5, "louis_trial", "共和国成立後のルイ16世裁判と1793年1月21日の処刑"),
    (108.02, 117.02, 70, 6, "terror_committee", "外敵戦争、内戦、食糧問題、公安委員会と革命政府"),
    (117.02, 130.62, 76, 8, "terror_civil", "恐怖政治の死刑判決、獄死、裁判外殺害、地方内戦を複合的に扱う"),
    (130.62, 139.00, 84, 5, "brumaire_coup", "30歳のボナパルトと協力者によるブリュメール18日の軍事的クーデター"),
    (139.00, 143.32, 89, 3, "consulate", "統領政府の安定化とrevolutionとの連続性・終結論争"),
    (143.32, 153.50, 92, 6, "civil_code", "法の統一と財産保護を進めるreform、家父長権の強化"),
    (153.50, 158.50, 98, 3, "emperor_1804", "1804年の皇帝化と革命原則・権威主義の同居"),
    (158.50, 167.16, 101, 5, "reform_occupation", "reformの広がりと戦争・占領・地域の受容と抵抗"),
    (167.16, 177.00, 106, 6, "haiti_resistance", "1794年廃止、1802年奴隷制復活、サン＝ドマングの抵抗とハイチ独立"),
    (177.00, 197.200167, 112, 12, "critical_legacy", "Liberty・平等・友愛の後世の定着とrevolutionのideals・排除を批判的に学ぶ"),
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
    if len(scenes) != 123 or min(gaps) < 1.30 or max(gaps) > 1.90:
        raise RuntimeError(
            f"invalid density: count={len(scenes)} min={min(gaps)} max={max(gaps)}"
        )
    plan["scenes"] = scenes
    plan["qa_status"] = "READY_TO_RENDER_STYLE01"
    plan["output_name"] = "h068_adopted_song_cinematic_v1.mp4"
    PLAN_PATH.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"H068 video plan: {len(scenes)} scenes, "
        f"min gap {min(gaps):.3f}s, max gap {max(gaps):.3f}s"
    )


if __name__ == "__main__":
    main()
