#!/usr/bin/env python3
"""Build the dense, historically corrected Style01 scene plan for H066."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H066"
PLAN_PATH = LESSON / "planning" / "video_plan.json"


GROUPS = (
    (0.0, 9.52, 1, 6, "founding_legend", "紀元前753年をロムルスとレムスの伝承として語る"),
    (9.52, 19.04, 7, 6, "palatine_archaeology", "パラティーノ丘の初期集落跡と確定できない創建日"),
    (19.04, 27.188, 13, 5, "early_republic", "王政から共和政へ、市民集会・政務官・senateと富裕層の影響"),
    (27.188, 33.6, 18, 4, "italian_expansion", "同盟・市民権・征服を組み合わせたイタリア半島での拡大"),
    (33.6, 40.011, 22, 4, "punic_aftermath", "ポエニ戦争後の西地中海優勢と社会的代償"),
    (40.011, 46.673, 26, 4, "institutions", "senate・二人のconsuls・市民集会・属州総督によるterritory統治"),
    (46.673, 54.44, 30, 5, "caesar_rise", "内戦と社会対立の中でカエサルが中心人物となる"),
    (54.44, 59.44, 35, 3, "gaul_cost", "ガリア征服の富とterritory、現地の死・捕虜・奴隷化"),
    (59.44, 70.44, 38, 7, "assassination_aftermath", "終身独裁官と紀元前44年3月15日の暗殺後を非流血で描く"),
    (70.44, 76.9, 45, 4, "octavian_aftermath", "複数の競争者と内戦後のオクタウィアヌス"),
    (76.9, 83.318, 49, 4, "augustus_title", "紀元前27年、senateがAugustusの称号を与え最初のemperorとされる"),
    (83.318, 90.747, 53, 5, "principate", "共和政の外形を残しながら実権を集中する元首政"),
    (90.747, 99.065, 58, 5, "pax_trade", "Pax Romanaの相対的安定、交易、繁栄と検問"),
    (99.065, 108.5, 63, 6, "infrastructure", "道路・水道橋・浴場と西暦80年ローマのコロッセウム"),
    (108.5, 118.04, 69, 6, "province_society", "属州の地域差・地域主体性・繁栄・辺境戦争・奴隷労働"),
    (118.04, 130.04, 75, 7, "third_century", "3世紀の内戦・疫病・経済不安・国境圧力と再編"),
    (130.04, 145.76, 82, 10, "east_west_courts", "395年の東西宮廷への再分担と東の帝国の継続"),
    (145.76, 155.98, 92, 6, "odoacer_transition", "476年の少年皇帝退位と住民・行政・都市生活の継続"),
    (155.98, 168.91, 98, 8, "legacy_transmission", "法・言語・都市・建築・宗教制度が地域で変化しながら継続"),
    (168.91, 181.840167, 106, 8, "critical_legacy", "legacyの創造と征服・奴隷制を現代に批判的に学ぶ"),
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
    if len(scenes) != 113 or min(gaps) < 1.30 or max(gaps) > 1.90:
        raise RuntimeError(
            f"invalid density: count={len(scenes)} min={min(gaps)} max={max(gaps)}"
        )
    plan["scenes"] = scenes
    plan["qa_status"] = "READY_TO_RENDER_STYLE01"
    plan["output_name"] = "h066_adopted_song_cinematic_v1.mp4"
    PLAN_PATH.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"H066 video plan: {len(scenes)} scenes, "
        f"min gap {min(gaps):.3f}s, max gap {max(gaps):.3f}s"
    )


if __name__ == "__main__":
    main()
