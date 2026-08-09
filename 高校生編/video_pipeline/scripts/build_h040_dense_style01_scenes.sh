#!/bin/zsh
set -euo pipefail

ROOT="${0:A:h:h}"
REF="$ROOT/H040/scenes/character_refs"
OUT="$ROOT/H040/scenes/final_style01"
mkdir -p "$OUT"

frame() { cp "$REF/$1" "$OUT/$2"; }
crop() {
  magick "$REF/$1" -crop "$2" +repage \
    -resize '1672x941^' -gravity center -extent 1672x941 "$OUT/$3"
}
tone() {
  magick "$REF/$1" -modulate "$3" -fill "$4" -colorize 10% "$OUT/$2"
}

# 1953年、ワトソンとクリックによる二重らせん構造の発表
frame dna_double_helix_publication_master.png 01_double_helix_publication_wide.png
crop dna_double_helix_publication_master.png 1000x563+350+0 02_model_and_two_scientists.png
crop dna_double_helix_publication_master.png 760x428+720+80 03_crick_adjusts_metal_plate.png
crop dna_double_helix_publication_master.png 820x461+150+80 04_watson_studies_structure.png
crop dna_double_helix_publication_master.png 780x439+550+50 05_double_helix_model_detail.png
crop dna_double_helix_publication_master.png 1180x664+230+0 06_discovery_ready_for_publication.png

# もう一人の科学者、ロザリンド・フランクリン
frame rosalind_lab_identity_master.png 07_rosalind_in_kings_lab_wide.png
crop rosalind_lab_identity_master.png 820x461+70+40 08_rosalind_identity_portrait.png
crop rosalind_lab_identity_master.png 930x523+0+160 09_scientist_and_lab_notebook.png
crop rosalind_lab_identity_master.png 820x461+670+40 10_diffraction_apparatus_beside_her.png

# King's College LondonでのX線回折実験
frame xray_diffraction_experiment_master.png 11_xray_experiment_wide.png
crop xray_diffraction_experiment_master.png 850x478+0+60 12_franklin_directs_experiment.png
crop xray_diffraction_experiment_master.png 860x484+580+60 13_gosling_and_xray_camera.png
crop xray_diffraction_experiment_master.png 720x405+720+210 14_hydrated_dna_fiber_setup.png
crop xray_diffraction_experiment_master.png 920x518+380+40 15_precise_alignment_hands.png
tone xray_diffraction_experiment_master.png 16_long_exposure_in_lab.png 82,96,102 '#15283a'

# Photo 51のX字型回折像と分析
frame photo51_analysis_master.png 17_photo51_analysis_wide.png
crop photo51_analysis_master.png 760x428+40+30 18_rosalind_measures_pattern.png
crop photo51_analysis_master.png 760x428+690+40 19_photo51_x_pattern_close.png
crop photo51_analysis_master.png 930x523+520+0 20_diffraction_evidence_detail.png
crop photo51_analysis_master.png 980x551+0+30 21_notebook_and_measurement.png
tone photo51_analysis_master.png 22_helical_evidence_under_safelight.png 78,92,104 '#2a1620'

# 本人の知らないうちにワトソンへ示された写真
frame photo51_shown_without_knowledge_master.png 23_wilkins_shows_watson_wide.png
crop photo51_shown_without_knowledge_master.png 900x506+0+80 24_watson_sees_diffraction_image.png
crop photo51_shown_without_knowledge_master.png 780x439+690+70 25_wilkins_holds_photo51.png
crop photo51_shown_without_knowledge_master.png 960x540+390+40 26_photo_between_two_scientists.png

# 1962年のノーベル賞は三人に授与
frame nobel_1962_master.png 27_three_laureates_wide.png
crop nobel_1962_master.png 1040x585+300+0 28_watson_crick_wilkins_only.png
crop nobel_1962_master.png 760x428+650+120 29_three_medals_and_documents.png
tone nobel_1962_master.png 30_stockholm_ceremony_distance.png 88,98,104 '#26253a'

# 1958年の死と1962年の不在を、空の研究室で静かに示す
frame empty_birkbeck_lab_master.png 31_empty_birkbeck_lab_wide.png
crop empty_birkbeck_lab_master.png 940x529+560+0 32_empty_chair_and_lab_coat.png
crop empty_birkbeck_lab_master.png 850x478+250+210 33_research_plates_left_on_desk.png
tone empty_birkbeck_lab_master.png 34_no_posthumous_award.png 72,90,102 '#182237'

# 死後授与をしない規則は、架空の拒否場面ではなく三人分の資料で示す
frame nobel_rule_archive_master.png 29_nobel_archive_three_awards_wide.png
crop nobel_rule_archive_master.png 1120x630+420+250 30_exactly_three_award_sets.png

# Birkbeckで続けたウイルス構造研究と献身
frame birkbeck_science_master.png 35_birkbeck_virus_research_wide.png
crop birkbeck_science_master.png 900x506+220+0 36_franklin_leads_small_team.png
crop birkbeck_science_master.png 780x439+520+120 37_rod_shaped_virus_model.png
crop birkbeck_science_master.png 860x484+760+40 38_colleague_listens_to_franklin.png
crop birkbeck_science_master.png 1030x579+250+0 39_dedication_in_science.png

# 現代の研究者がPhoto 51とDNA・ウイルス研究を学ぶ
frame legacy_modern_science_master.png 40_modern_scientists_remember_wide.png
crop legacy_modern_science_master.png 980x551+0+30 41_young_researchers_discuss_evidence.png
crop legacy_modern_science_master.png 760x428+430+170 42_photo51_and_models_close.png
crop legacy_modern_science_master.png 780x439+800+70 43_franklin_portrait_in_modern_lab.png
crop legacy_modern_science_master.png 1120x630+260+0 44_quiet_contribution_continues.png

# 科学史は大きな声だけで作られない
frame quiet_voices_history_master.png 45_student_in_archive_wide.png
crop quiet_voices_history_master.png 800x450+0+40 46_student_listens_to_history.png
crop quiet_voices_history_master.png 920x518+650+70 47_portrait_photo51_and_virus.png
crop quiet_voices_history_master.png 1080x608+400+20 48_preserved_evidence_in_blue_hour.png
tone quiet_voices_history_master.png 49_quiet_voice_remembered.png 82,96,103 '#10223b'
tone empty_birkbeck_lab_master.png 50_empty_lab_final_afterglow.png 76,94,104 '#16263b'

expected=(
  01_double_helix_publication_wide.png 02_model_and_two_scientists.png
  03_crick_adjusts_metal_plate.png 04_watson_studies_structure.png
  05_double_helix_model_detail.png 06_discovery_ready_for_publication.png
  07_rosalind_in_kings_lab_wide.png 08_rosalind_identity_portrait.png
  09_scientist_and_lab_notebook.png 10_diffraction_apparatus_beside_her.png
  11_xray_experiment_wide.png 12_franklin_directs_experiment.png
  13_gosling_and_xray_camera.png 14_hydrated_dna_fiber_setup.png
  15_precise_alignment_hands.png 16_long_exposure_in_lab.png
  17_photo51_analysis_wide.png 18_rosalind_measures_pattern.png
  19_photo51_x_pattern_close.png 20_diffraction_evidence_detail.png
  21_notebook_and_measurement.png 22_helical_evidence_under_safelight.png
  23_wilkins_shows_watson_wide.png 24_watson_sees_diffraction_image.png
  25_wilkins_holds_photo51.png 26_photo_between_two_scientists.png
  27_three_laureates_wide.png 28_watson_crick_wilkins_only.png
  29_three_medals_and_documents.png 30_stockholm_ceremony_distance.png
  31_empty_birkbeck_lab_wide.png 32_empty_chair_and_lab_coat.png
  33_research_plates_left_on_desk.png 34_no_posthumous_award.png
  29_nobel_archive_three_awards_wide.png 30_exactly_three_award_sets.png
  35_birkbeck_virus_research_wide.png 36_franklin_leads_small_team.png
  37_rod_shaped_virus_model.png 38_colleague_listens_to_franklin.png
  39_dedication_in_science.png 40_modern_scientists_remember_wide.png
  41_young_researchers_discuss_evidence.png 42_photo51_and_models_close.png
  43_franklin_portrait_in_modern_lab.png 44_quiet_contribution_continues.png
  45_student_in_archive_wide.png 46_student_listens_to_history.png
  47_portrait_photo51_and_virus.png 48_preserved_evidence_in_blue_hour.png
  49_quiet_voice_remembered.png 50_empty_lab_final_afterglow.png
)
for file in $expected; do
  test -s "$OUT/$file"
done
echo "H040 dense final_style01 files verified: ${#expected[@]}"
