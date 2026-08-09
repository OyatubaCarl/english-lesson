#!/bin/zsh
set -euo pipefail

ROOT="${0:A:h:h}"
REF="$ROOT/H053/scenes/character_refs"
OUT="$ROOT/H053/scenes/final_style01"
mkdir -p "$OUT"

frame() { cp "$REF/$1" "$OUT/$2"; }
crop() {
  magick "$REF/$1" -crop "$2" +repage \
    -resize '1672x941^' -gravity center -extent 1672x941 "$OUT/$3"
}
tone() {
  magick "$REF/$1" -modulate "$3" -fill "$4" -colorize 7% "$OUT/$2"
}

# 夜明けの現代都市から、百年の変化を見渡す導入
frame modern_urban_population_master.png 01_modern_city_dawn_wide.png
crop inclusive_city_final_master.png 980x551+330+150 02_city_model_overview.png
crop inclusive_city_final_master.png 720x405+420+120 03_student_and_planner_begin.png

# 20世紀初頭、urban areaに住む人がまだ少なかった時代
frame early_twentieth_century_master.png 04_early_twentieth_century_wide.png
crop early_twentieth_century_master.png 650x366+0+180 05_rural_fields_and_families.png
crop early_twentieth_century_master.png 720x405+380+130 06_railway_and_migration.png
crop early_twentieth_century_master.png 650x366+970+160 07_growing_industrial_city.png
tone early_twentieth_century_master.png 08_one_in_ten_historical_memory.png 91,102,101 '#17243a'

# 現在の巨大な都市圏と交通網
frame modern_urban_population_master.png 09_today_more_than_half_wide.png
crop modern_urban_population_master.png 700x394+0+160 10_coastal_housing_districts.png
crop modern_urban_population_master.png 760x428+420+160 11_rail_station_and_center.png
crop modern_urban_population_master.png 700x394+920+130 12_expanding_urban_edge.png
tone modern_urban_population_master.png 13_city_population_scale.png 96,103,102 '#243b57'

# Urbanizationが集めた雇用・教育・医療と、残る格差
frame urban_opportunities_master.png 14_urban_opportunities_wide.png
crop urban_opportunities_master.png 620x349+0+170 15_jobs_and_small_business.png
crop urban_opportunities_master.png 650x366+360+150 16_education_access.png
crop urban_opportunities_master.png 700x394+780+130 17_medical_care_access.png
crop urban_opportunities_master.png 620x349+1020+170 18_waiting_and_unequal_access.png
tone urban_opportunities_master.png 19_benefits_and_divides.png 94,103,102 '#1a2b45'

# Traffic、housing、air pollutionをそれぞれの対象に寄る
frame traffic_congestion_master.png 20_traffic_congestion_wide.png
crop traffic_congestion_master.png 760x428+400+120 21_gridlocked_road_detail.png
frame housing_cost_master.png 22_housing_price_pressure.png
frame air_pollution_master.png 23_air_pollution_and_health.png

# Tokyo・New York・London・Shanghaiを同じ課題で比較
frame global_cities_infrastructure_master.png 24_global_cities_model_wide.png
crop global_cities_infrastructure_master.png 760x428+0+180 25_student_compares_city_forms.png
crop global_cities_infrastructure_master.png 820x461+760+150 26_planner_compares_infrastructure.png

# population densityとinfrastructure capacityの関係
frame density_infrastructure_master.png 27_density_and_infrastructure_wide.png
crop density_infrastructure_master.png 700x394+0+160 28_dense_housing_and_rail.png
crop density_infrastructure_master.png 760x428+430+140 29_station_capacity_and_crowds.png
crop density_infrastructure_master.png 700x394+930+150 30_network_limits_at_rush_hour.png

# sustainable urban planningの検討と実装
frame sustainable_street_master.png 31_sustainable_street_wide.png
crop sustainable_street_master.png 650x366+0+170 32_residents_review_the_plan.png
crop sustainable_street_master.png 700x394+360+150 33_protected_cycle_route.png
crop sustainable_street_master.png 700x394+760+130 34_accessible_green_corridor.png
crop sustainable_street_master.png 650x366+1010+150 35_bus_and_shaded_sidewalk.png

# pedestrians・cyclists・parks・public transportationへのinvestment
frame green_park_transit_master.png 36_green_park_and_transit_wide.png
crop green_park_transit_master.png 650x366+0+160 37_rain_garden_restoration.png
crop green_park_transit_master.png 720x405+310+150 38_cyclists_and_accessible_path.png
crop green_park_transit_master.png 760x428+650+130 39_tram_bus_and_station.png
crop green_park_transit_master.png 650x366+1000+160 40_neighbors_plan_green_space.png
tone green_park_transit_master.png 41_public_investment_in_daily_life.png 101,104,102 '#284635'

# 都市中心部からsuburbsへ移る家族と生活基盤
frame suburbs_move_master.png 42_move_to_suburbs_wide.png
crop suburbs_move_master.png 650x366+0+170 43_family_and_moving_truck.png
crop suburbs_move_master.png 700x394+350+150 44_suburban_station_access.png
crop suburbs_move_master.png 700x394+760+130 45_housing_consultation.png
crop suburbs_move_master.png 650x366+1010+150 46_city_center_in_distance.png

# remote workで近づくurbanとrural、消えないインフラ差
frame remote_work_urban_rural_master.png 47_remote_work_regions_wide.png
crop remote_work_urban_rural_master.png 650x366+0+160 48_city_apartment_remote_work.png
crop remote_work_urban_rural_master.png 720x405+470+140 49_suburban_home_and_coworking.png
crop remote_work_urban_rural_master.png 700x394+920+150 50_rural_broadband_clinic_and_bus.png

# 形を変え続ける都市
frame modern_urban_population_master.png 51_cities_continue_to_change.png
crop modern_urban_population_master.png 900x506+360+130 52_rail_housing_and_waterfront.png
tone modern_urban_population_master.png 53_future_shape_is_a_choice.png 103,104,102 '#604428'

# 誰もが安心して暮らせる空間を共にdesignする結末
frame inclusive_city_final_master.png 54_inclusive_city_workshop_wide.png
crop inclusive_city_final_master.png 720x405+0+170 55_bus_driver_older_resident_and_child.png
crop inclusive_city_final_master.png 760x428+390+140 56_student_planner_and_city_model.png
crop inclusive_city_final_master.png 720x405+850+160 57_wheelchair_user_housing_adviser_and_shopkeeper.png
tone inclusive_city_final_master.png 58_everyone_can_live_with_peace_of_mind.png 106,104,102 '#6b4828'

expected=("$OUT"/[0-9][0-9]_*.png)
test ${#expected[@]} -eq 58
for file in $expected; do
  test -s "$file"
done
echo "H053 final_style01 files verified: ${#expected[@]}"
