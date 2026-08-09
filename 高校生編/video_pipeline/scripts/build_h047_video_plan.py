#!/usr/bin/env python3
"""Build the dense, concept-aligned Style01 scene plan for H047."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H047"
PLAN_PATH = LESSON / "planning" / "video_plan.json"


def scene(number: int, name: str, purpose: str) -> tuple[str, str]:
    return (f"scenes/final_style01/{number:02d}_{name}.png", purpose)


GROUPS: list[tuple[float, float, list[tuple[str, str]]]] = [
    (
        0.0,
        8.0,
        [
            scene(1, "market_square_wide", "同じ港町のmarket economyを導入"),
            scene(2, "student_observes_market", "市場を観察する17歳の男子高校生"),
            scene(3, "goods_bread_and_produce", "売買されるgoods"),
            scene(4, "bicycle_repair_service", "市場で提供されるservices"),
            scene(5, "delivery_exchange_hands", "goodsとservicesの交換"),
            scene(6, "market_network_transition", "demandとsupplyが出会う市場"),
        ],
    ),
    (
        8.0,
        14.724,
        [
            scene(7, "demand_surge_wide", "特定productへのdemand増加"),
            scene(8, "consumers_wait_for_product", "同じ製品を求める消費者"),
            scene(9, "manager_studies_plain_bottle", "在庫を見て判断する店員"),
            scene(10, "three_bottles_left", "supplyが少なくなった棚"),
            scene(11, "dwindling_supply_and_box", "demand増と在庫減によるprice判断"),
        ],
    ),
    (
        14.724,
        19.665,
        [
            scene(12, "demand_fall_wide", "同じproductへのdemand減少"),
            scene(13, "full_shelves_of_same_product", "多く残った在庫"),
            scene(15, "manager_revises_sales_plan", "pricesと販売条件を見直す"),
        ],
    ),
    (
        19.665,
        25.121,
        [
            scene(1, "market_square_wide", "marketの基本的な仕組み"),
            scene(11, "dwindling_supply_and_box", "需要増と供給減の側面"),
            scene(12, "demand_fall_wide", "需要減と在庫増の側面"),
            scene(15, "manager_revises_sales_plan", "状況に応じて動くmarket"),
        ],
    ),
    (
        25.121,
        31.808,
        [
            scene(16, "company_factory_wide", "企業活動の全体像"),
            scene(17, "capital_meeting", "企業が集めるcapital"),
            scene(18, "production_line", "工場でのproduction"),
            scene(20, "loading_products_for_sale", "productsの販売先への出荷"),
            scene(21, "revenue_to_wages_and_equipment", "profitを賃金と設備へ戻す"),
        ],
    ),
    (
        31.808,
        37.91,
        [
            scene(22, "competition_quality_wide", "industry内のcompetition"),
            scene(23, "two_competing_prototypes", "二社の異なる製品"),
            scene(24, "durability_test_rig", "品質を高める公正な試験"),
            scene(26, "consumers_compare_quality", "消費者がqualityを比較"),
        ],
    ),
    (
        37.91,
        44.911,
        [
            scene(27, "labor_and_compensation_wide", "laborと報酬の全体像"),
            scene(28, "factory_workers_finish_shift", "安全に働く工場作業員"),
            scene(29, "wages_after_time_record", "勤務記録に基づくwages"),
            scene(30, "office_employees_and_salary", "事務・設計職のsalaries"),
            scene(31, "plain_pay_documents", "労働の対価を確認する手元"),
        ],
    ),
    (
        44.911,
        49.863,
        [
            scene(32, "household_income_wide", "stable employmentと家庭"),
            scene(33, "family_reviews_budget", "家計のincomeを確認"),
            scene(35, "school_needs_and_stability", "住居・食事・学用品を支える安定"),
        ],
    ),
    (
        49.863,
        54.805,
        [
            scene(36, "public_services_wide", "taxesと公共サービスの全体像"),
            scene(38, "public_school_students", "taxesが支える教育"),
            scene(39, "community_clinic_care", "税財源が支える福祉と医療"),
        ],
    ),
    (
        54.805,
        59.935,
        [
            scene(41, "bank_investment_wide", "bank loansと企業成長"),
            scene(42, "loan_contract_folder", "返済を伴う融資契約"),
            scene(43, "owner_engineer_and_bank_officer", "銀行員と企業側の慎重な合意"),
            scene(44, "new_machine_and_worker_training", "investmentによる設備と訓練"),
        ],
    ),
    (
        59.935,
        68.897,
        [
            scene(45, "global_trade_port_wide", "globalization下の港とmarkets"),
            scene(46, "two_way_ship_loading", "到着と出発が同時に進む港"),
            scene(47, "freight_train_and_trucks", "一国のeconomyを他国へ結ぶ物流"),
            scene(48, "port_workers_inspect_cargo", "人が支える国際物流"),
            scene(49, "exports_imports_transition", "他国のmarketsとの結びつき"),
        ],
    ),
    (
        68.897,
        71.818,
        [
            scene(46, "two_way_ship_loading", "exportsとimportsの双方向輸送"),
            scene(47, "freight_train_and_trucks", "貿易がgrowthを支える物流"),
        ],
    ),
    (
        71.818,
        80.480167,
        [
            scene(50, "interconnected_city_wide", "国境を越えてつながるEconomies"),
            scene(51, "student_overlooks_network", "相互依存を見つめる男子高校生"),
            scene(52, "rail_factory_clinic_connection", "市場・企業・公共サービス・物流の連鎖"),
            scene(53, "ships_arrive_and_depart", "互いに影響する各国の経済"),
            scene(54, "economies_influence_final", "一つの港町から世界へ続く経済"),
        ],
    ),
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
            scenes.append(
                {
                    "start": round(group_start + interval * index, 3),
                    "image": image,
                    "purpose": purpose,
                }
            )

    gaps = [
        round(float(right["start"]) - float(left["start"]), 3)
        for left, right in zip(scenes, scenes[1:])
    ]
    if len(scenes) != 54 or min(gaps) < 1.28 or max(gaps) > 2.0:
        raise RuntimeError(
            f"invalid density: count={len(scenes)} min={min(gaps)} max={max(gaps)}"
        )

    plan["scenes"] = scenes
    plan["qa_status"] = "READY_TO_RENDER_STYLE01"
    plan["output_name"] = "h047_adopted_song_cinematic_v1.mp4"
    PLAN_PATH.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"H047 video plan: {len(scenes)} scenes, "
        f"min gap {min(gaps):.3f}s, max gap {max(gaps):.3f}s"
    )


if __name__ == "__main__":
    main()
