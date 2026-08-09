#!/usr/bin/env python3
"""Build the dense, current-fact-aware Style01 scene plan for H065."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H065"
PLAN_PATH = LESSON / "planning" / "video_plan.json"


GROUPS = (
    (0.0, 12.88, 1, 8, "mid1990s", "1990年代半ば、一部の家庭へ接続が入り始める"),
    (12.88, 25.56, 9, 8, "transformation", "約30年で生活・仕事・つながり方がtransformedされる"),
    (25.56, 35.24, 17, 6, "communication", "手紙・固定電話から現代のcommunicationへ一部が移る"),
    (35.24, 44.74, 23, 6, "video_call", "回線・端末・技能があれば遠方と映像でつながれる"),
    (44.74, 50.58, 29, 4, "pandemic_remote", "流行期、遠隔で可能な職種に在宅勤務が広がる"),
    (50.58, 59.28, 33, 6, "hybrid_work", "自宅・共同作業空間の利点と環境による負担"),
    (59.28, 62.42, 39, 2, "work_divide", "現場仕事と接続格差を含む新しい課題"),
    (62.42, 67.1, 41, 3, "privacy", "収集目的・同意・最小化・管理としてのprivacy"),
    (67.1, 69.92, 44, 2, "security", "詐欺対策・認証・更新・バックアップによるsecurity"),
    (69.92, 73.3, 46, 2, "misinformation", "misinformationと意図的偽情報の拡散"),
    (73.3, 79.034, 48, 4, "verification", "発信元・根拠・日付・別資料の確認"),
    (79.034, 87.42, 52, 5, "algorithm", "複数の目的と信号から推薦を決めるalgorithm"),
    (87.42, 97.02, 57, 6, "attention", "気づかないまま長時間画面を見続ける"),
    (97.02, 103.58, 63, 4, "support", "長時間だけで診断せず、重大な支障が続く場合に支援する"),
    (103.58, 108.9, 67, 3, "physical_system", "物理基盤・設計・事業モデル・規則も結果を形づくる"),
    (108.9, 117.64, 70, 6, "shared_responsibility", "judgmentと企業・政府・学校・家庭の共有責任"),
    (117.64, 135.760167, 76, 11, "balanced_future", "格差を縮め、接続と距離を選ぶdigital時代のchallenge"),
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
    if len(scenes) != 86 or min(gaps) < 1.30 or max(gaps) > 1.90:
        raise RuntimeError(
            f"invalid density: count={len(scenes)} min={min(gaps)} max={max(gaps)}"
        )
    plan["scenes"] = scenes
    plan["qa_status"] = "READY_TO_RENDER_STYLE01"
    plan["output_name"] = "h065_adopted_song_cinematic_v1.mp4"
    PLAN_PATH.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"H065 video plan: {len(scenes)} scenes, "
        f"min gap {min(gaps):.3f}s, max gap {max(gaps):.3f}s"
    )


if __name__ == "__main__":
    main()
