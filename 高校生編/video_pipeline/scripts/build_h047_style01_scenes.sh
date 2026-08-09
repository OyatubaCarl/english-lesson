#!/bin/zsh
set -euo pipefail

ROOT="${0:A:h:h}"
REF="$ROOT/H047/scenes/character_refs"
OUT="$ROOT/H047/scenes/final_style01"
mkdir -p "$OUT"

frame() { cp "$REF/$1" "$OUT/$2"; }
crop() {
  magick "$REF/$1" -crop "$2" +repage \
    -resize '1672x941^' -gravity center -extent 1672x941 "$OUT/$3"
}
tone() {
  magick "$REF/$1" -modulate "$3" -fill "$4" -colorize 8% "$OUT/$2"
}

# 市場経済：goods / services / price / demand / supply
frame market_square_overview_master.png 01_market_square_wide.png
crop market_square_overview_master.png 700x394+0+90 02_student_observes_market.png
crop market_square_overview_master.png 780x439+300+230 03_goods_bread_and_produce.png
crop market_square_overview_master.png 700x394+650+250 04_bicycle_repair_service.png
crop market_square_overview_master.png 700x394+900+190 05_delivery_exchange_hands.png
tone market_square_overview_master.png 06_market_network_transition.png 92,102,102 '#1b2a3c'

# demand増加・在庫減少
frame demand_surge_master.png 07_demand_surge_wide.png
crop demand_surge_master.png 760x428+0+100 08_consumers_wait_for_product.png
crop demand_surge_master.png 700x394+620+140 09_manager_studies_plain_bottle.png
crop demand_surge_master.png 680x383+980+180 10_three_bottles_left.png
crop demand_surge_master.png 760x428+700+260 11_dwindling_supply_and_box.png

# demand減少・在庫増加
frame demand_fall_master.png 12_demand_fall_wide.png
crop demand_fall_master.png 820x461+760+80 13_full_shelves_of_same_product.png
crop demand_fall_master.png 650x366+220+160 14_single_customer_browses.png
crop demand_fall_master.png 720x405+700+240 15_manager_revises_sales_plan.png

# capital→production→products→profitの企業循環
frame company_factory_chain_master.png 16_company_factory_wide.png
crop company_factory_chain_master.png 720x405+0+70 17_capital_meeting.png
crop company_factory_chain_master.png 850x478+430+260 18_production_line.png
crop company_factory_chain_master.png 650x366+500+360 19_plain_products_on_conveyor.png
crop company_factory_chain_master.png 700x394+920+300 20_loading_products_for_sale.png
crop company_factory_chain_master.png 650x366+0+370 21_revenue_to_wages_and_equipment.png

# competitionとquality改善
frame competition_quality_master.png 22_competition_quality_wide.png
crop competition_quality_master.png 760x428+220+230 23_two_competing_prototypes.png
crop competition_quality_master.png 720x405+500+100 24_durability_test_rig.png
crop competition_quality_master.png 760x428+0+300 25_engineers_improve_design.png
crop competition_quality_master.png 700x394+930+310 26_consumers_compare_quality.png

# laborとwages / salaries
frame labor_wages_master.png 27_labor_and_compensation_wide.png
crop labor_wages_master.png 760x428+0+80 28_factory_workers_finish_shift.png
crop labor_wages_master.png 680x383+300+170 29_wages_after_time_record.png
crop labor_wages_master.png 760x428+760+100 30_office_employees_and_salary.png
crop labor_wages_master.png 720x405+850+200 31_plain_pay_documents.png

# stable employmentとhousehold income
frame household_income_master.png 32_household_income_wide.png
crop household_income_master.png 850x478+250+160 33_family_reviews_budget.png
crop household_income_master.png 700x394+0+350 34_groceries_and_simple_meal.png
crop household_income_master.png 720x405+850+300 35_school_needs_and_stability.png

# taxesから教育・福祉へ
frame tax_public_services_master.png 36_public_services_wide.png
crop tax_public_services_master.png 700x394+0+230 37_civic_budget_room.png
crop tax_public_services_master.png 760x428+500+100 38_public_school_students.png
crop tax_public_services_master.png 650x366+700+300 39_community_clinic_care.png
crop tax_public_services_master.png 720x405+940+300 40_library_and_accessible_bus.png

# bank loansとinvestment
frame bank_investment_master.png 41_bank_investment_wide.png
crop bank_investment_master.png 760x428+180+250 42_loan_contract_folder.png
crop bank_investment_master.png 760x428+650+200 43_owner_engineer_and_bank_officer.png
crop bank_investment_master.png 820x461+720+40 44_new_machine_and_worker_training.png

# exports / importsとgrowth
frame global_trade_port_master.png 45_global_trade_port_wide.png
crop global_trade_port_master.png 900x506+200+100 46_two_way_ship_loading.png
crop global_trade_port_master.png 760x428+250+300 47_freight_train_and_trucks.png
crop global_trade_port_master.png 700x394+850+320 48_port_workers_inspect_cargo.png
tone global_trade_port_master.png 49_exports_imports_transition.png 88,104,104 '#14243a'

# 国境を越えて影響し合うEconomies
frame interconnected_economies_master.png 50_interconnected_city_wide.png
crop interconnected_economies_master.png 700x394+0+270 51_student_overlooks_network.png
crop interconnected_economies_master.png 850x478+300+350 52_rail_factory_clinic_connection.png
crop interconnected_economies_master.png 900x506+700+80 53_ships_arrive_and_depart.png
tone interconnected_economies_master.png 54_economies_influence_final.png 86,104,104 '#132239'

expected=("$OUT"/[0-9][0-9]_*.png)
test ${#expected[@]} -eq 54
for file in $expected; do
  test -s "$file"
done
echo "H047 final_style01 files verified: ${#expected[@]}"
