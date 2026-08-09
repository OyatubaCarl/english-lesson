#!/bin/zsh
set -euo pipefail

ROOT="${0:A:h:h}"
REF="$ROOT/H050/scenes/character_refs"
OUT="$ROOT/H050/scenes/final_style01"
mkdir -p "$OUT"

frame() { cp "$REF/$1" "$OUT/$2"; }
crop() {
  magick "$REF/$1" -crop "$2" +repage \
    -resize '1672x941^' -gravity center -extent 1672x941 "$OUT/$3"
}
tone() {
  magick "$REF/$1" -modulate "$3" -fill "$4" -colorize 7% "$OUT/$2"
}

# 導入とeducation as a basic right
frame education_basic_right_master.png 01_right_wide.png
crop education_basic_right_master.png 780x439+0+180 02_morning_school_approach.png
crop education_basic_right_master.png 700x394+520+260 03_accessible_entrance.png
crop education_basic_right_master.png 650x366+980+120 04_teacher_student_welcome.png
crop education_basic_right_master.png 760x428+140+250 05_every_person_enters.png
crop education_basic_right_master.png 600x338+520+330 06_wheelchair_ramp.png
tone education_basic_right_master.png 07_shared_open_door.png 94,103,103 '#18283e'

# 1948 UN declaration / universal human right
frame un_declaration_1948_master.png 08_un_hall_wide.png
crop un_declaration_1948_master.png 760x428+0+180 09_diverse_delegates_left.png
crop un_declaration_1948_master.png 760x428+900+180 10_delegates_right.png
crop un_declaration_1948_master.png 850x478+400+160 11_raised_hands.png
crop un_declaration_1948_master.png 620x349+0+390 12_period_microphones.png
crop un_declaration_1948_master.png 540x304+560+420 13_plain_declaration_document.png
crop un_declaration_1948_master.png 760x428+450+250 14_central_adoption_vote.png
tone un_declaration_1948_master.png 15_universal_right_historic.png 91,102,102 '#2a2230'

# birthplace and family income shape opportunity
frame birthplace_income_opportunity_master.png 16_opportunity_region_wide.png
crop birthplace_income_opportunity_master.png 720x405+0+0 17_urban_nearby_school.png
crop birthplace_income_opportunity_master.png 820x461+820+0 18_mountain_long_route.png
crop birthplace_income_opportunity_master.png 620x349+980+180 19_rural_student_walk.png
crop birthplace_income_opportunity_master.png 760x428+0+430 20_family_budget_table.png
crop birthplace_income_opportunity_master.png 620x349+380+520 21_education_costs_hands.png
crop birthplace_income_opportunity_master.png 880x495+300+220 22_same_age_different_paths.png
tone birthplace_income_opportunity_master.png 23_opportunity_not_destiny.png 94,103,103 '#183047'

# children who cannot attend school / multiple barriers
frame out_of_school_children_master.png 24_access_barriers_wide.png
crop out_of_school_children_master.png 760x428+0+120 25_distant_school_bridge.png
crop out_of_school_children_master.png 720x405+500+170 26_temporary_learning_tent.png
crop out_of_school_children_master.png 620x349+740+420 27_older_boy_studies_with_sibling.png
crop out_of_school_children_master.png 620x349+1030+250 28_wheelchair_step_and_ramp.png
tone out_of_school_children_master.png 29_community_support_action.png 95,103,103 '#243044'

# developed countries also have quality and access gaps
frame developed_country_access_quality_master.png 30_school_resource_gap_wide.png
crop developed_country_access_quality_master.png 760x428+0+170 31_worn_classroom_equipment.png
crop developed_country_access_quality_master.png 620x349+180+250 32_shared_computer_access.png
crop developed_country_access_quality_master.png 700x394+0+360 33_students_equally_engaged.png
crop developed_country_access_quality_master.png 580x326+650+240 34_teacher_observes_gap.png
crop developed_country_access_quality_master.png 760x428+900+160 35_equipped_library_lab.png
crop developed_country_access_quality_master.png 620x349+1040+300 36_inclusive_support_staff.png

# family income and future career
frame family_income_career_master.png 37_career_counseling_wide.png
crop family_income_career_master.png 760x428+200+210 38_boy_girl_consider_paths.png
crop family_income_career_master.png 620x349+650+160 39_teacher_explains_options.png
crop family_income_career_master.png 780x439+420+410 40_blank_cost_planning.png
tone family_income_career_master.png 41_future_choices_remain_open.png 94,103,103 '#1a2840'

# education beyond passing on knowledge
frame education_beyond_knowledge_master.png 42_learning_beyond_knowledge_wide.png
crop education_beyond_knowledge_master.png 820x461+0+180 43_science_debate_art.png
crop education_beyond_knowledge_master.png 760x428+880+300 44_practical_teamwork.png

# individual identity and responsible membership
frame identity_responsibility_master.png 45_identity_community_wide.png
crop identity_responsibility_master.png 620x349+730+90 46_boy_presents_idea.png
crop identity_responsibility_master.png 620x349+470+140 47_girl_listens_and_responds.png
crop identity_responsibility_master.png 780x439+100+250 48_elders_students_dialogue.png
crop identity_responsibility_master.png 820x461+420+390 49_blank_safety_map.png
crop identity_responsibility_master.png 650x366+1020+330 50_wheelchair_user_in_planning.png
tone identity_responsibility_master.png 51_responsible_member_growth.png 92,104,103 '#17243b'

# scholarships and reduced tuition
frame scholarship_tuition_master.png 52_scholarship_counseling_wide.png
crop scholarship_tuition_master.png 760x428+230+220 53_girl_family_support.png
crop scholarship_tuition_master.png 620x349+720+210 54_advisor_blank_folders.png
crop scholarship_tuition_master.png 700x394+520+400 55_tuition_reduction_discussion.png
crop scholarship_tuition_master.png 700x394+130+390 56_housing_transport_support.png
crop scholarship_tuition_master.png 760x428+580+0 57_university_workshop_beyond.png
crop scholarship_tuition_master.png 560x315+1080+240 58_boy_waits_supportively.png
tone scholarship_tuition_master.png 59_higher_education_opens.png 96,103,103 '#233047'

# slow but continuing reform
crop slow_reform_master.png 760x428+0+0 60_gradual_ramp_reform.png
crop slow_reform_master.png 900x506+250+210 61_bus_library_progress.png
crop slow_reform_master.png 900x506+650+430 62_teacher_training_progress.png

# same opportunity for every child
frame same_opportunity_every_child_master.png 63_same_opportunity_wide.png
crop same_opportunity_every_child_master.png 650x366+0+190 64_safe_transport_arrival.png
crop same_opportunity_every_child_master.png 700x394+350+160 65_step_free_school_entrance.png
crop same_opportunity_every_child_master.png 600x338+430+330 66_tactile_guidance_and_ramp.png
crop same_opportunity_every_child_master.png 720x405+930+370 67_enough_learning_materials.png
crop same_opportunity_every_child_master.png 650x366+1030+90 68_quiet_support_space.png
crop same_opportunity_every_child_master.png 650x366+980+320 69_teacher_assists_without_isolation.png
tone same_opportunity_every_child_master.png 70_equal_access_continues.png 95,104,103 '#1d3046'

# society gap begins to close
frame education_gap_closing_master.png 71_gap_closing_region_wide.png
crop education_gap_closing_master.png 820x461+0+180 72_bridge_and_school_bus.png
crop education_gap_closing_master.png 720x405+350+0 73_regional_school_under_improvement.png
crop education_gap_closing_master.png 650x366+1020+0 74_connected_classrooms.png
crop education_gap_closing_master.png 650x366+940+280 75_counselor_meets_family.png
crop education_gap_closing_master.png 700x394+950+500 76_vocational_workshop_path.png

# equal education / inclusive society across generations
frame equal_society_final_master.png 77_intergenerational_learning_wide.png
crop equal_society_final_master.png 760x428+500+130 78_boy_girl_teacher_final.png
crop equal_society_final_master.png 780x439+0+360 79_elders_children_build_together.png
tone equal_society_final_master.png 80_inclusive_society_blue_hour.png 88,104,104 '#14243a'

expected=("$OUT"/[0-9][0-9]_*.png)
test ${#expected[@]} -eq 80
for file in $expected; do
  test -s "$file"
done
echo "H050 final_style01 files verified: ${#expected[@]}"
