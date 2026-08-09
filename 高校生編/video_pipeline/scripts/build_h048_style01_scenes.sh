#!/bin/zsh
set -euo pipefail

ROOT="${0:A:h:h}"
REF="$ROOT/H048/scenes/character_refs"
OUT="$ROOT/H048/scenes/final_style01"
mkdir -p "$OUT"

frame() { cp "$REF/$1" "$OUT/$2"; }
crop() {
  magick "$REF/$1" -crop "$2" +repage \
    -resize '1672x941^' -gravity center -extent 1672x941 "$OUT/$3"
}
tone() {
  magick "$REF/$1" -modulate "$3" -fill "$4" -colorize 7% "$OUT/$2"
}

# corporation / brand / advertising
frame advertising_agency_strategy_master.png 01_agency_strategy_wide.png
crop advertising_agency_strategy_master.png 920x518+430+170 02_creative_team_discussion.png
crop advertising_agency_strategy_master.png 660x371+260+260 03_corporation_representative.png
crop advertising_agency_strategy_master.png 540x304+730+270 04_unbranded_teal_bottle.png
crop advertising_agency_strategy_master.png 880x495+300+390 05_blank_storyboards.png
crop advertising_agency_strategy_master.png 600x338+0+90 06_student_outside_agency.png

# television / newspapers / magazines / internet media
frame multi_media_ad_exposure_master.png 07_many_media_wide.png
crop multi_media_ad_exposure_master.png 620x349+0+100 08_television_advertisement.png
crop multi_media_ad_exposure_master.png 700x394+500+20 09_student_leaves_home.png
crop multi_media_ad_exposure_master.png 560x315+1100+160 10_street_display_ad.png
crop multi_media_ad_exposure_master.png 620x349+1040+500 11_laptop_ad.png
crop multi_media_ad_exposure_master.png 760x428+260+470 12_newspaper_magazine_ads.png

# attract attention / persuade consumer
frame attention_persuasion_master.png 13_shop_display_wide.png
crop attention_persuasion_master.png 650x366+280+60 14_consumer_attention.png
crop attention_persuasion_master.png 560x315+760+270 15_spotlit_product.png
crop attention_persuasion_master.png 650x366+430+260 16_student_pauses_before_purchase.png
crop attention_persuasion_master.png 560x315+1080+100 17_clerk_waits_without_pressure.png

# brand image versus product quality
frame brand_image_vs_quality_master.png 18_image_quality_comparison_wide.png
crop brand_image_vs_quality_master.png 620x349+0+120 19_polished_brand_image.png
crop brand_image_vs_quality_master.png 650x366+500+130 20_student_compares_bottles.png
crop brand_image_vs_quality_master.png 620x349+900+230 21_leak_quality_test.png
crop brand_image_vs_quality_master.png 600x338+1070+290 22_lid_material_inspection.png
crop brand_image_vs_quality_master.png 820x461+400+80 23_choice_influenced_by_both.png

# social media / opinions / broadcast
frame social_media_opinions_master.png 24_social_media_wide.png
crop social_media_opinions_master.png 900x506+240+190 25_consumers_share_opinions.png
crop social_media_opinions_master.png 620x349+270+250 26_product_photo_on_phone.png
crop social_media_opinions_master.png 620x349+730+220 27_student_reads_opinion.png
crop social_media_opinions_master.png 620x349+1040+250 28_share_symbol_and_product.png
tone social_media_opinions_master.png 29_opinions_reach_city.png 92,104,103 '#15243a'

# negative opinion spreads / corporation image shifts
frame viral_negative_opinion_master.png 30_negative_opinion_spreads_wide.png
crop viral_negative_opinion_master.png 600x338+0+220 31_leaking_lid_post.png
crop viral_negative_opinion_master.png 620x349+430+200 32_cafe_users_share.png
crop viral_negative_opinion_master.png 540x304+760+80 33_train_users_see_post.png
crop viral_negative_opinion_master.png 700x394+960+230 34_corporation_response_team.png
crop viral_negative_opinion_master.png 560x315+1080+340 35_team_inspects_defect.png

# governments establish regulations
frame consumer_protection_regulation_master.png 36_consumer_protection_review_wide.png
crop consumer_protection_regulation_master.png 650x366+220+230 37_corporation_presents_product.png
crop consumer_protection_regulation_master.png 540x304+530+220 38_advertisement_under_review.png
crop consumer_protection_regulation_master.png 650x366+700+300 39_official_checks_grid.png
crop consumer_protection_regulation_master.png 620x349+1030+250 40_consumer_representatives.png
crop consumer_protection_regulation_master.png 820x461+780+0 41_public_consultation_counter.png

# health claim requires solid evidence
frame health_claim_evidence_master.png 42_evidence_lab_wide.png
crop health_claim_evidence_master.png 620x349+0+220 43_balance_measurement.png
crop health_claim_evidence_master.png 700x394+420+230 44_control_samples_and_record.png
crop health_claim_evidence_master.png 600x338+530+180 45_blank_research_grid.png
crop health_claim_evidence_master.png 620x349+1000+180 46_microscope_comparison.png
crop health_claim_evidence_master.png 740x416+820+420 47_unlabeled_evidence_chart.png

# corporations / consumers / state triangular relationship
frame corporation_consumer_state_triangle_master.png 48_three_party_meeting_wide.png
crop corporation_consumer_state_triangle_master.png 700x394+0+180 49_corporation_quality_team.png
crop corporation_consumer_state_triangle_master.png 600x338+930+180 50_consumer_representative.png
crop corporation_consumer_state_triangle_master.png 560x315+700+120 51_student_consumer_voice.png
crop corporation_consumer_state_triangle_master.png 600x338+1120+220 52_state_regulation_official.png
crop corporation_consumer_state_triangle_master.png 820x461+380+380 53_shared_product_evidence.png
tone corporation_consumer_state_triangle_master.png 54_each_watches_others.png 91,103,103 '#17263b'

# critical eye / deliberate choice / ending
frame critical_media_literacy_master.png 55_critical_media_literacy_wide.png
crop critical_media_literacy_master.png 700x394+470+40 56_student_checks_claims.png
crop critical_media_literacy_master.png 820x461+250+350 57_actual_product_and_sample.png
crop critical_media_literacy_master.png 700x394+900+350 58_leak_photo_as_evidence.png
frame critical_eye_final_master.png 59_critical_eye_final_street.png

expected=("$OUT"/[0-9][0-9]_*.png)
test ${#expected[@]} -eq 59
for file in $expected; do
  test -s "$file"
done
echo "H048 final_style01 files verified: ${#expected[@]}"
