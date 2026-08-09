#!/usr/bin/env python3
"""Build the dense, scientifically corrected Style01 scene plan for H067."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H067"
PLAN_PATH = LESSON / "planning" / "video_plan.json"


GROUPS = (
    (0.0, 10.72, 1, 7, "gallery_intro", "数字を暗記せず推計として学ぶ科学博物館の導入"),
    (10.72, 16.27, 8, 3, "brain_weight", "brainの平均重量と個人差"),
    (16.27, 22.62, 11, 4, "neuron_count", "約860億neuronsを標本抽出と統計から得た推計として扱う"),
    (22.62, 30.62, 15, 5, "synapse_micro", "neuronの軸索・樹状突起とsynapses"),
    (30.62, 36.38, 20, 4, "network_scale", "多数のsynapsesとnetworkの規模・推定幅"),
    (36.38, 40.96, 24, 3, "cognition_domains", "記憶・知覚・感情・判断に関わる広い回路"),
    (40.96, 47.2, 27, 4, "self_network", "自己と身体・記憶・感情・neural networkの関係"),
    (47.2, 56.58, 31, 6, "consciousness_ethics", "consciousness研究の競合理論・臨床・倫理・不確実性"),
    (56.58, 64.15, 37, 5, "imaging_history", "20世紀末の初期機能画像研究と当時の装置"),
    (64.15, 71.815, 42, 5, "fmri_bold", "機能的磁気共鳴画像法が血流・血中酸素を介した間接指標であること"),
    (71.815, 84.44, 47, 8, "signal_inference", "見る課題と想起課題の時系列信号を統計的に推定する"),
    (84.44, 96.26, 55, 7, "plasticity_evidence", "plasticityを学習前後の縦断研究で示す"),
    (96.26, 102.32, 62, 4, "old_belief", "成人brainが変わらないという旧来の見方を改める"),
    (102.32, 114.48, 66, 8, "lifelong_learning", "経験と学習に伴うneurons間の結合変化と個人差"),
    (114.48, 122.72, 74, 5, "disease_care", "アルツハイマー病・パーキンソン病・脳卒中を異なる支援として描く"),
    (122.72, 133.0, 79, 6, "treatment_research", "brain diseasesとbrain injuriesの基礎研究・臨床試験・支援"),
    (133.0, 143.64, 85, 7, "personalized_recovery", "recoveryの程度と目標の個人差・補償手段"),
    (143.64, 156.86, 92, 8, "rehabilitation", "反復練習と多職種チームによる神経リハビリ"),
    (156.86, 168.000979, 100, 7, "human_question", "神経科学・医学・心理学・哲学・当事者が人間とは何かを考える"),
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
    if len(scenes) != 106 or min(gaps) < 1.30 or max(gaps) > 1.90:
        raise RuntimeError(
            f"invalid density: count={len(scenes)} min={min(gaps)} max={max(gaps)}"
        )
    plan["scenes"] = scenes
    plan["qa_status"] = "READY_TO_RENDER_STYLE01"
    plan["output_name"] = "h067_adopted_song_cinematic_v1.mp4"
    PLAN_PATH.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"H067 video plan: {len(scenes)} scenes, "
        f"min gap {min(gaps):.3f}s, max gap {max(gaps):.3f}s"
    )


if __name__ == "__main__":
    main()
