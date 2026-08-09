#!/usr/bin/env python3
"""Build the dense and historically careful Style01 scene plan for H061."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H061"
PLAN_PATH = LESSON / "planning" / "video_plan.json"


GROUPS = (
    (0.0, 18.0, 1, 11, "brno_1856", "1856年ブルノ修道院でmonkが交配実験を開始"),
    (18.0, 27.46, 12, 6, "mendel_identity", "Gregor Mendel本人と植物・数学・記録"),
    (27.46, 41.54, 18, 9, "pea_traits", "茎・種子色・種子形など明確なtraitの比較"),
    (41.54, 46.5, 27, 3, "cross_pollination", "花粉管理・保護袋・木札による交配"),
    (46.5, 52.78, 30, 4, "nine_years", "約9年・2万7000株超の継続と記録"),
    (52.78, 60.8, 34, 5, "true_breeding", "純系の背高・背低の親株を等しく維持"),
    (60.8, 64.36, 39, 2, "first_generation", "交配後の第1世代はすべて背高"),
    (64.36, 74.82, 41, 7, "second_generation", "自家受粉後の第2世代で背低が再出現"),
    (74.82, 83.08, 48, 5, "ratio_counting", "多数個体の集計からおよそ3対1"),
    (83.08, 98.2, 53, 9, "paired_elements", "親から一つずつ受け継ぐ二要素の推論"),
    (98.2, 108.06, 62, 6, "dominance_relation", "dominantとrecessiveを価値でなく発現関係として表現"),
    (108.06, 115.74, 68, 5, "presentation_1865", "1865年ブルノ自然科学協会の二会合で発表"),
    (115.74, 123.64, 73, 5, "publication_1866", "1866年刊行と限定的な初期流通"),
    (123.64, 130.2, 78, 4, "decades_unnoticed", "利用可能な論文が数十年間ほぼ注目されない"),
    (130.2, 142.44, 82, 8, "researchers_1900", "1900年前後の三研究者による別々の研究と再評価"),
    (142.44, 155.62, 90, 8, "modern_genetics", "現代geneticsの重要な基礎と複雑形質の研究"),
    (155.62, 182.200167, 98, 17, "quiet_finale", "静かな修道院で観察と数が遺伝の規則性を照らす"),
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
    if len(scenes) != 114 or min(gaps) < 1.30 or max(gaps) > 1.90:
        raise RuntimeError(
            f"invalid density: count={len(scenes)} min={min(gaps)} max={max(gaps)}"
        )
    plan["scenes"] = scenes
    plan["qa_status"] = "READY_TO_RENDER_STYLE01"
    plan["output_name"] = "h061_adopted_song_cinematic_v1.mp4"
    PLAN_PATH.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"H061 video plan: {len(scenes)} scenes, "
        f"min gap {min(gaps):.3f}s, max gap {max(gaps):.3f}s"
    )


if __name__ == "__main__":
    main()
