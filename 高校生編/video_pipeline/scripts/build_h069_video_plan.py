#!/usr/bin/env python3
"""Build the dense, fact-corrected Style01 scene plan for H069."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H069"
PLAN_PATH = LESSON / "planning" / "video_plan.json"


GROUPS = (
    (0.0, 8.06, 1, 5, "mount_wilson", "1929年マウント・ウィルソン天文台の導入"),
    (8.06, 20.46, 6, 8, "hubble_humason", "ハッブルとヒューマソンの共同観測"),
    (20.46, 26.54, 14, 4, "spectra_relation", "銀河の距離と後退速度を写真乾板とスペクトルから比較"),
    (26.54, 32.54, 18, 4, "expansion_everywhere", "中心のない空間膨張"),
    (32.54, 38.56, 22, 4, "hot_dense", "高温高密度の初期宇宙、空間内の一点爆発ではない"),
    (38.56, 45.32, 26, 5, "lemaitre", "1927年のルメートルと膨張宇宙theory"),
    (45.32, 54.32, 31, 6, "age_evidence", "約138億年を複数の観測から推定"),
    (54.32, 62.02, 37, 5, "early_cooling", "初期universeの膨張と冷却"),
    (62.02, 66.50, 42, 3, "nucleosynthesis", "最初の数分の軽元素原子核形成"),
    (66.50, 72.84, 45, 4, "first_stars", "数億年後に最初のstarsが輝く"),
    (72.84, 81.94, 49, 6, "holmdel_horn", "1964年ホルムデル・ホーンアンテナ"),
    (81.94, 91.04, 55, 6, "receiver", "ペンジアスとウィルソンが全方向の雑音を検証"),
    (91.04, 105.16, 61, 9, "cmb_all_sky", "約38万年後に自由に進み始めたCMB background"),
    (105.16, 112.16, 70, 5, "evidence", "膨張・軽元素・CMBという相補的な証拠"),
    (112.16, 125.10, 75, 8, "milky_way", "天の川galaxyのstars数は幅のある推計"),
    (125.10, 132.96, 83, 5, "deep_field", "観測可能なuniverseのgalaxies数も幅のある推計"),
    (132.96, 139.188, 88, 4, "composition", "通常物質と暗黒成分の質量・エネルギー収支"),
    (139.188, 146.50, 92, 5, "dark_matter", "dark物質を重力レンズ効果から推定"),
    (146.50, 155.72, 97, 5, "dark_energy", "遠方超新星と加速膨張、暗黒エネルギーは未解明"),
    (155.72, 161.88, 102, 4, "physics_team", "現代physicsの共同研究challenge"),
    (161.88, 176.88, 106, 10, "jwst", "2021年打上げのJWSTで初期galaxiesを観測"),
    (176.88, 187.22, 116, 7, "early_galaxy", "宇宙誕生約3億年後の小さな銀河の光が約135億年旅する"),
    (187.22, 203.720167, 123, 10, "museum_outro", "現代の生徒が観測と推論の更新を学ぶ"),
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
    if len(scenes) != 132 or min(gaps) < 1.30 or max(gaps) > 1.90:
        raise RuntimeError(
            f"invalid density: count={len(scenes)} min={min(gaps)} max={max(gaps)}"
        )
    plan["scenes"] = scenes
    plan["qa_status"] = "READY_TO_RENDER_STYLE01"
    plan["output_name"] = "h069_adopted_song_cinematic_v1.mp4"
    PLAN_PATH.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"H069 video plan: {len(scenes)} scenes, "
        f"min gap {min(gaps):.3f}s, max gap {max(gaps):.3f}s"
    )


if __name__ == "__main__":
    main()
