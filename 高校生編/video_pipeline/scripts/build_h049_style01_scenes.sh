#!/bin/zsh
set -euo pipefail

ROOT="${0:A:h:h}"
REF="$ROOT/H049/scenes/character_refs"
OUT="$ROOT/H049/scenes/final_style01"
mkdir -p "$OUT"

frame() { cp "$REF/$1" "$OUT/$2"; }
crop() {
  magick "$REF/$1" -crop "$2" +repage \
    -resize '1672x941^' -gravity center -extent 1672x941 "$OUT/$3"
}
tone() {
  magick "$REF/$1" -modulate "$3" -fill "$4" -colorize 7% "$OUT/$2"
}

# 導入：産業革命から現代まで
frame industrial_climate_timeline_master.png 01_industrial_to_modern_wide.png
crop industrial_climate_timeline_master.png 700x394+0+250 02_early_coal_factories.png
crop industrial_climate_timeline_master.png 720x405+260+360 03_steam_rail_and_port.png
crop industrial_climate_timeline_master.png 780x439+600+260 04_expanding_modern_city.png
crop industrial_climate_timeline_master.png 620x349+1030+260 05_scientist_student_weather_station.png

# climate has changed rapidly since industrial revolution
crop industrial_climate_timeline_master.png 760x428+0+100 06_industrial_revolution_city.png
crop industrial_climate_timeline_master.png 760x428+420+180 07_century_of_urban_growth.png
crop industrial_climate_timeline_master.png 760x428+850+170 08_present_coastal_city.png
tone industrial_climate_timeline_master.png 09_one_atmosphere_across_time.png 91,103,103 '#15243a'
frame global_temperature_observation_master.png 10_observatory_transition.png
crop global_temperature_observation_master.png 660x371+450+110 11_student_learns_measurement.png

# global average temperature and 1.1-degree comparison
frame global_temperature_observation_master.png 12_temperature_observation_wide.png
crop global_temperature_observation_master.png 620x349+0+180 13_historic_weather_recorder.png
crop global_temperature_observation_master.png 680x383+380+120 14_scientist_explains_baseline.png
crop global_temperature_observation_master.png 660x371+660+160 15_modern_land_ocean_sensors.png
crop global_temperature_observation_master.png 780x439+0+450 16_ice_core_samples.png
crop global_temperature_observation_master.png 860x484+550+410 17_warming_stripes_without_numbers.png

# fossil fuel burning / carbon dioxide emission
frame fossil_fuel_emissions_master.png 18_fossil_fuel_district_wide.png
crop fossil_fuel_emissions_master.png 760x428+0+360 19_coal_stockpile_and_rail.png
crop fossil_fuel_emissions_master.png 760x428+450+300 20_petroleum_tank_and_truck.png
crop fossil_fuel_emissions_master.png 720x405+650+110 21_power_plant_stacks.png
crop fossil_fuel_emissions_master.png 620x349+1040+260 22_stack_sampling_team.png
crop fossil_fuel_emissions_master.png 580x326+1050+400 23_emission_sample_canisters.png

# deforestation and agricultural practices
frame land_use_agriculture_master.png 24_land_use_watershed_wide.png
crop land_use_agriculture_master.png 720x405+0+150 25_intact_forest_and_stream.png
crop land_use_agriculture_master.png 720x405+400+220 26_cleared_forest_edge.png
crop land_use_agriculture_master.png 720x405+700+320 27_restoration_seedlings_and_scientist.png
crop land_use_agriculture_master.png 760x428+920+300 28_rice_cattle_and_soil_management.png

# sea-level rise / floods / drought / stronger storm risk
frame climate_impacts_master.png 29_climate_impacts_region_wide.png
crop climate_impacts_master.png 720x405+0+210 30_high_tide_wetland.png
crop climate_impacts_master.png 620x349+100+350 31_tide_gauge_technicians.png
crop climate_impacts_master.png 760x428+430+250 32_high_river_and_barriers.png
crop climate_impacts_master.png 650x366+750+230 33_orderly_flood_response.png
crop climate_impacts_master.png 720x405+920+110 34_low_reservoir_and_dry_fields.png
crop climate_impacts_master.png 620x349+1020+350 35_scientist_student_observe_impacts.png
tone climate_impacts_master.png 36_regional_hazards_not_apocalypse.png 88,103,103 '#18243a'

# ecosystems / species / extinction threat
frame ecosystems_species_master.png 37_ecosystems_fieldwork_wide.png
crop ecosystems_species_master.png 720x405+0+180 38_tidal_wetland_birds.png
crop ecosystems_species_master.png 620x349+350+260 39_scientist_photographs_amphibian.png
crop ecosystems_species_master.png 700x394+780+400 40_partly_bleached_coral.png
crop ecosystems_species_master.png 620x349+900+170 41_reduced_forest_habitat.png
crop ecosystems_species_master.png 650x366+1050+160 42_ecologists_mark_habitat.png
tone ecosystems_species_master.png 43_species_extinction_risk.png 91,104,103 '#183047'

# 1997 Kyoto Protocol
frame kyoto_protocol_1997_master.png 44_kyoto_conference_wide.png
crop kyoto_protocol_1997_master.png 760x428+500+100 45_chair_adopts_protocol.png
crop kyoto_protocol_1997_master.png 720x405+0+250 46_many_country_delegates.png
crop kyoto_protocol_1997_master.png 650x366+0+480 47_blue_target_folder.png
crop kyoto_protocol_1997_master.png 650x366+400+460 48_green_yellow_targets.png
crop kyoto_protocol_1997_master.png 650x366+960+420 49_red_target_folder.png
tone kyoto_protocol_1997_master.png 50_differentiated_reduction_targets.png 94,102,102 '#2b2435'

# 2015 Paris Agreement
frame paris_agreement_2015_master.png 51_paris_conference_wide.png
crop paris_agreement_2015_master.png 760x428+500+170 52_scientist_explains_shared_goal.png
crop paris_agreement_2015_master.png 720x405+0+240 53_diverse_delegations_left.png
crop paris_agreement_2015_master.png 720x405+930+240 54_diverse_delegations_right.png
crop paris_agreement_2015_master.png 700x394+630+10 55_two_temperature_goal_bands.png
crop paris_agreement_2015_master.png 780x439+430+360 56_common_agreement_document.png
crop paris_agreement_2015_master.png 800x450+700+300 57_serious_ongoing_commitment.png
tone paris_agreement_2015_master.png 58_paris_framework_not_finished.png 92,103,102 '#24253a'

# renewable investment and emissions regulation
frame renewable_energy_investment_master.png 59_renewable_region_wide.png
crop renewable_energy_investment_master.png 780x439+0+120 60_rooftop_solar_and_workers.png
crop renewable_energy_investment_master.png 820x461+450+50 61_wind_grid_storage.png
crop renewable_energy_investment_master.png 700x394+550+360 62_scientist_student_engineers.png
frame emissions_regulation_master.png 63_regulation_program_wide.png
crop emissions_regulation_master.png 760x428+0+280 64_vehicle_emission_test.png
crop emissions_regulation_master.png 760x428+850+180 65_factory_monitoring_and_upgrade.png

# no single country can solve it alone
frame transboundary_climate_master.png 66_transboundary_climate_wide.png
crop transboundary_climate_master.png 860x484+0+80 67_rain_and_shared_river.png
crop transboundary_climate_master.png 780x439+650+60 68_haze_and_shared_coast.png
crop transboundary_climate_master.png 760x428+470+350 69_sensor_exchange_at_border.png

# international cooperation
frame international_cooperation_master.png 70_international_cooperation_wide.png
crop international_cooperation_master.png 700x394+0+80 71_shared_weather_sensors.png
crop international_cooperation_master.png 660x371+350+140 72_teams_exchange_data_drive.png
crop international_cooperation_master.png 700x394+700+130 73_student_carries_sensor_case.png
crop international_cooperation_master.png 760x428+0+390 74_wetland_adaptation_model.png
crop international_cooperation_master.png 680x383+980+300 75_early_warning_training.png
tone international_cooperation_master.png 76_science_technology_adaptation_shared.png 93,103,103 '#15283d'

# sustainable society / shared goal across generations
frame sustainable_generations_final_master.png 77_sustainable_generations_wide.png
crop sustainable_generations_final_master.png 760x428+0+300 78_wetland_replanting_elders_children.png
crop sustainable_generations_final_master.png 680x383+500+330 79_student_and_child_work_together.png
crop sustainable_generations_final_master.png 760x428+700+120 80_electric_public_transit.png
crop sustainable_generations_final_master.png 700x394+900+30 81_insulated_solar_homes.png
crop sustainable_generations_final_master.png 660x371+1050+300 82_repair_workshop_generations.png
crop sustainable_generations_final_master.png 850x478+250+260 83_shared_goal_in_action.png
tone sustainable_generations_final_master.png 84_sustainable_society_final.png 88,104,104 '#14243a'

expected=("$OUT"/[0-9][0-9]_*.png)
test ${#expected[@]} -eq 84
for file in $expected; do
  test -s "$file"
done
echo "H049 final_style01 files verified: ${#expected[@]}"
