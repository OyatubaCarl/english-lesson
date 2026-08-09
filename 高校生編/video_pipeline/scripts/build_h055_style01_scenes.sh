#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REF="$ROOT/H055/scenes/character_refs"
OUT="$ROOT/H055/scenes/final_style01"
mkdir -p "$OUT"

frame() { cp "$REF/$1" "$OUT/$2"; }
crop() {
  magick "$REF/$1" -crop "$2" +repage \
    -resize '1672x941^' -gravity center -extent 1672x941 "$OUT/$3"
}
tone() {
  magick "$REF/$1" -modulate "$3" -fill "$4" -colorize 7% "$OUT/$2"
}

# 現代日本のagingを、暮らし方の異なる市民として導入
frame modern_japan_intergenerational_master.png 01_modern_japan_morning_wide.png
crop modern_japan_intergenerational_master.png 850x478+0+120 02_student_observes_the_city.png
crop modern_japan_intergenerational_master.png 700x394+430+180 03_older_worker_commutes.png
crop modern_japan_intergenerational_master.png 690x388+950+120 04_silver_haired_shop_worker.png
crop modern_japan_intergenerational_master.png 720x405+650+180 05_varied_older_lives.png
crop modern_japan_intergenerational_master.png 950x534+320+130 06_generations_share_the_street.png
tone modern_japan_intergenerational_master.png 07_aging_society_dawn.png 103,103,102 '#4c3a32'

# 65歳以上が大きな比率を占める社会。数値図解ではなく多様性
frame population_ageing_master.png 08_population_ageing_plaza_wide.png
crop population_ageing_master.png 720x405+0+140 09_older_worker_and_kiosk.png
crop population_ageing_master.png 720x405+420+120 10_student_among_generations.png
crop population_ageing_master.png 700x394+650+320 11_wheelchair_conversation_at_eye_level.png
crop population_ageing_master.png 700x394+960+140 12_accessible_transit_support.png
crop population_ageing_master.png 1000x562+300+100 13_many_ways_of_living_later_life.png

# 長寿は祝福であり、生活は続いていく
frame longevity_celebration_master.png 14_long_life_celebration_wide.png
crop longevity_celebration_master.png 760x428+430+130 15_woodworker_and_grandchild.png
crop longevity_celebration_master.png 650x366+600+200 16_hands_pass_the_wooden_bird.png
crop longevity_celebration_master.png 720x405+850+130 17_student_listens_to_life_story.png
crop longevity_celebration_master.png 680x383+0+180 18_family_and_old_friend.png
tone longevity_celebration_master.png 19_longevity_is_worth_celebrating.png 105,104,102 '#5f4030'

# workforceとpensionを年齢対立でなく制度調整として描く
frame workforce_pension_master.png 20_mixed_age_workforce_wide.png
crop workforce_pension_master.png 760x428+0+170 21_silver_haired_worker_at_counter.png
crop workforce_pension_master.png 650x366+500+140 22_older_craft_worker.png
crop workforce_pension_master.png 760x428+900+150 23_pension_consultation.png
tone workforce_pension_master.png 24_work_and_system_in_one_community.png 102,103,102 '#4e3d32'

# medical費とbudgetは予防・ケア・資源配分として示す
frame medical_budget_master.png 25_community_clinic_wide.png
crop medical_budget_master.png 720x405+0+170 26_older_man_asks_clinician.png
crop medical_budget_master.png 700x394+440+160 27_preventive_rehabilitation.png
crop medical_budget_master.png 760x428+890+140 28_health_resource_meeting.png
tone medical_budget_master.png 29_care_and_budget_decisions.png 102,104,102 '#554033'

# welfareを支える共通の政策課題
frame welfare_policy_master.png 30_welfare_roundtable_wide.png
crop welfare_policy_master.png 760x428+0+170 31_citizen_representatives_listen.png
crop welfare_policy_master.png 720x405+430+150 32_care_worker_and_older_voice.png
crop welfare_policy_master.png 760x428+880+160 33_public_planners_compare_options.png
tone welfare_policy_master.png 34_shared_welfare_challenge.png 101,103,102 '#3e4660'

# 家族の形の変化。別居とつながりは両立する
frame changing_family_master.png 35_separate_homes_connected_family_wide.png
crop changing_family_master.png 650x366+0+170 36_student_sees_family_visit.png
crop changing_family_master.png 800x450+650+120 37_grandchild_arrives_for_dinner.png
crop changing_family_master.png 650x366+1010+150 38_warm_visit_and_video_call.png

# 別居そのものとlonelinessを同一視しない
tone changing_family_master.png 39_connection_across_households.png 104,103,102 '#60432f'
crop changing_family_master.png 760x428+600+140 40_family_connection_close.png
frame living_apart_loneliness_master.png 41_quiet_supper_wide.png
crop living_apart_loneliness_master.png 760x428+650+160 42_older_man_in_blue_dusk.png
crop living_apart_loneliness_master.png 680x383+360+300 43_single_meal_and_silent_phone.png
crop living_apart_loneliness_master.png 720x405+900+130 44_capable_life_and_moment_of_loneliness.png
tone living_apart_loneliness_master.png 45_unwanted_loneliness_not_helplessness.png 96,102,104 '#263c60'

# 一人暮らしを支える地域の複層的な仕組み
frame community_support_master.png 46_community_support_hub_wide.png
crop community_support_master.png 720x405+0+160 47_shared_meal_preparation.png
crop community_support_master.png 720x405+330+170 48_older_woman_and_student_serve_together.png
crop community_support_master.png 680x383+720+210 49_older_man_brings_his_own_tray.png
crop community_support_master.png 720x405+930+160 50_accessible_shuttle_arrives.png
crop community_support_master.png 850x478+700+120 51_neighbors_check_in.png
crop community_support_master.png 900x506+260+130 52_older_adults_organize_and_participate.png
tone community_support_master.png 53_local_efforts_in_the_rain.png 102,103,103 '#38465d'

# volunteer訪問は対等な交流
frame volunteer_visit_master.png 54_weekly_volunteer_visit_wide.png
crop volunteer_visit_master.png 760x428+180+160 55_older_man_teaches_woodcarving.png
crop volunteer_visit_master.png 700x394+700+160 56_student_shares_phone_skill.png
tone volunteer_visit_master.png 57_two_way_learning_over_tea.png 105,104,102 '#5a3f2f'

# technologyは人の介護と自立を補助
frame care_technology_master.png 58_care_technology_wide.png
crop care_technology_master.png 800x450+580+120 59_explanation_and_consent.png
crop care_technology_master.png 720x405+870+160 60_staff_operate_transfer_lift.png
crop care_technology_master.png 720x405+0+150 61_human_care_and_recording.png

# generations間の双方向の支え合い
frame generations_support_master.png 62_generations_support_workshop_wide.png
crop generations_support_master.png 720x405+0+160 63_older_man_teaches_children.png
crop generations_support_master.png 760x428+300+150 64_children_learn_the_craft.png
crop generations_support_master.png 700x394+720+160 65_student_helps_with_phone.png
crop generations_support_master.png 650x366+1010+150 66_silver_haired_woman_shares_a_smile.png
crop generations_support_master.png 950x534+350+110 67_knowledge_moves_both_directions.png
tone generations_support_master.png 68_mutual_support_between_generations.png 104,103,102 '#584030'

# 若者と高齢者が対等に尊重し支え合う
frame mutual_respect_master.png 69_accessible_park_planning_wide.png
crop mutual_respect_master.png 760x428+250+180 70_older_craft_and_student_hands.png
crop mutual_respect_master.png 760x428+650+170 71_wheelchair_user_voice_is_heard.png
tone mutual_respect_master.png 72_building_the_community_together.png 104,104,102 '#514735'

# 長寿社会の真の豊かさ
frame long_lived_society_final_master.png 73_long_lived_society_morning_wide.png
crop long_lived_society_final_master.png 720x405+0+180 74_older_man_teaches_a_child.png
crop long_lived_society_final_master.png 700x394+430+170 75_student_sets_up_community_books.png
crop long_lived_society_final_master.png 720x405+760+170 76_care_worker_walks_beside_resident.png
crop long_lived_society_final_master.png 720x405+950+170 77_older_women_garden_and_share_tea.png
crop long_lived_society_final_master.png 1000x562+320+100 78_accessible_paths_connect_everyone.png
tone long_lived_society_final_master.png 79_relationships_agency_care_and_dignity.png 106,104,102 '#66482f'
tone long_lived_society_final_master.png 80_richness_of_a_long_lived_society.png 109,105,101 '#745239'

count=$(find "$OUT" -type f -name '[0-9][0-9]_*.png' | wc -l | tr -d ' ')
test "$count" -eq 80
for file in "$OUT"/[0-9][0-9]_*.png; do
  test -s "$file"
done
echo "H055 final_style01 files verified: $count"
