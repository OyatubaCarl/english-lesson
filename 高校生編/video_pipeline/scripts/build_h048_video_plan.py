#!/usr/bin/env python3
"""Build the dense, concept-aligned Style01 scene plan for H048."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H048"
PLAN_PATH = LESSON / "planning" / "video_plan.json"


def scene(number: int, name: str, purpose: str) -> tuple[str, str]:
    return (f"scenes/final_style01/{number:02d}_{name}.png", purpose)


GROUPS: list[tuple[float, float, list[tuple[str, str]]]] = [
    (0.0, 9.72, [
        scene(1, "agency_strategy_wide", "corporationがadvertisingを計画する現場"),
        scene(2, "creative_team_discussion", "brandを知らせる広告制作チーム"),
        scene(3, "corporation_representative", "広告費を判断するcorporation担当者"),
        scene(4, "unbranded_teal_bottle", "一貫して登場する広告対象product"),
        scene(5, "blank_storyboards", "できるだけ多くの人へ届けるadvertising設計"),
        scene(6, "student_outside_agency", "広告を受け取るconsumerである男子高校生"),
    ]),
    (9.72, 19.6, [
        scene(7, "many_media_wide", "多様なmediaから届くadvertisements"),
        scene(8, "television_advertisement", "television上の商品広告"),
        scene(9, "student_leaves_home", "日常の中で広告に触れる男子高校生"),
        scene(10, "street_display_ad", "通学路のadvertisement"),
        scene(11, "laptop_ad", "internetを通じて届く広告"),
        scene(12, "newspaper_magazine_ads", "newspapersとmagazinesの広告"),
    ]),
    (19.6, 28.38, [
        scene(13, "shop_display_wide", "advertisementがconsumerへ働きかける売場"),
        scene(14, "consumer_attention", "広告が引くattention"),
        scene(15, "spotlit_product", "購入を促す商品展示"),
        scene(16, "student_pauses_before_purchase", "persuadeされても立ち止まって考えるconsumer"),
        scene(17, "clerk_waits_without_pressure", "強制でない購買判断"),
    ]),
    (28.38, 38.22, [
        scene(18, "image_quality_comparison_wide", "brand imageとproduct qualityの比較"),
        scene(19, "polished_brand_image", "美しく演出されたbrand image"),
        scene(20, "student_compares_bottles", "両面を比べる男子高校生"),
        scene(21, "leak_quality_test", "product qualityを確かめる漏れ試験"),
        scene(22, "lid_material_inspection", "素材とふたの品質確認"),
        scene(23, "choice_influenced_by_both", "imageとqualityがchoiceへ与えるinfluence"),
    ]),
    (38.22, 48.32, [
        scene(24, "social_media_wide", "social mediaでopinionsを伝えるconsumers"),
        scene(25, "consumers_share_opinions", "複数の消費者自身が情報発信"),
        scene(26, "product_photo_on_phone", "実物productについてのopinion"),
        scene(27, "student_reads_opinion", "他のconsumerの意見を読む"),
        scene(28, "share_symbol_and_product", "opinionsをbroadcastする操作"),
        scene(29, "opinions_reach_city", "世界へ広がり得る消費者の声"),
    ]),
    (48.32, 59.02, [
        scene(30, "negative_opinion_spreads_wide", "negative opinionが広がる一連の場面"),
        scene(31, "leaking_lid_post", "欠陥を写した一件のopinion"),
        scene(32, "cafe_users_share", "internet上で共有が続く"),
        scene(33, "train_users_see_post", "数時間で多くの人へ届く"),
        scene(34, "corporation_response_team", "corporationのimage変化に向き合うチーム"),
        scene(35, "team_inspects_defect", "反応だけでなく事実を確認する企業"),
    ]),
    (59.02, 68.84, [
        scene(36, "consumer_protection_review_wide", "governmentsによるconsumer保護"),
        scene(37, "corporation_presents_product", "企業側の商品説明"),
        scene(38, "advertisement_under_review", "misleadingになり得るadvertisingの審査"),
        scene(39, "official_checks_grid", "regulationsに照らす行政職員"),
        scene(40, "consumer_representatives", "保護される消費者の視点"),
        scene(41, "public_consultation_counter", "制度として設けられた相談と規制"),
    ]),
    (68.84, 78.86, [
        scene(42, "evidence_lab_wide", "health-related productのclaim審査"),
        scene(43, "balance_measurement", "客観的な測定"),
        scene(44, "control_samples_and_record", "比較対象を用いたevidence"),
        scene(45, "blank_research_grid", "検証結果の記録"),
        scene(46, "microscope_comparison", "研究者による詳細確認"),
        scene(47, "unlabeled_evidence_chart", "claimに必要なsolid evidence"),
    ]),
    (78.86, 90.9, [
        scene(48, "three_party_meeting_wide", "consumptionをめぐる三者関係"),
        scene(49, "corporation_quality_team", "corporationsの説明責任"),
        scene(50, "consumer_representative", "consumersの監視と発言"),
        scene(51, "student_consumer_voice", "若いconsumerも含む社会"),
        scene(52, "state_regulation_official", "stateによるルールと確認"),
        scene(53, "shared_product_evidence", "同じproductとevidenceを三者で確認"),
        scene(54, "each_watches_others", "each watches the othersという相互関係"),
    ]),
    (90.9, 99.400167, [
        scene(55, "critical_media_literacy_wide", "示された情報を比較するcritical eye"),
        scene(56, "student_checks_claims", "主張と情報源を見る男子高校生"),
        scene(57, "actual_product_and_sample", "実物と品質sampleの比較"),
        scene(58, "leak_photo_as_evidence", "他者のopinionとevidenceを確認"),
        scene(59, "critical_eye_final_street", "自分で判断するconsumerとしての結末"),
    ]),
]


def main() -> None:
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    scenes: list[dict[str, object]] = []
    for group_start, group_end, items in GROUPS:
        interval = (group_end - group_start) / len(items)
        for index, (image, purpose) in enumerate(items):
            path = LESSON / image
            if not path.is_file():
                raise FileNotFoundError(path)
            scenes.append({
                "start": round(group_start + interval * index, 3),
                "image": image,
                "purpose": purpose,
            })

    gaps = [
        round(float(right["start"]) - float(left["start"]), 3)
        for left, right in zip(scenes, scenes[1:])
    ]
    if len(scenes) != 59 or min(gaps) < 1.55 or max(gaps) > 1.85:
        raise RuntimeError(
            f"invalid density: count={len(scenes)} min={min(gaps)} max={max(gaps)}"
        )

    plan["scenes"] = scenes
    plan["qa_status"] = "READY_TO_RENDER_STYLE01"
    plan["output_name"] = "h048_adopted_song_cinematic_v1.mp4"
    PLAN_PATH.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"H048 video plan: {len(scenes)} scenes, "
        f"min gap {min(gaps):.3f}s, max gap {max(gaps):.3f}s"
    )


if __name__ == "__main__":
    main()
