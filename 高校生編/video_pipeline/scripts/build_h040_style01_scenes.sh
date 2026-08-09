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
  magick "$REF/$1" -modulate "$3" -fill "$4" -colorize 12% "$OUT/$2"
}

# 1953年、ワトソンとクリックが二重らせん模型を組み上げる
frame dna_double_helix_publication_master.png 01_double_helix_publication_wide.png
crop dna_double_helix_publication_master.png 910x512+680+40 02_double_helix_model_detail.png
crop dna_double_helix_publication_master.png 1050x591+0+0 03_watson_and_crick_at_model.png
crop dna_double_helix_publication_master.png 1180x664+360+20 04_model_and_research_notes.png
tone dna_double_helix_publication_master.png 05_structure_published_1953.png 92,103,102 '#243244'

# King's College Londonで研究を主導するロザリンド・フランクリン
frame rosalind_lab_identity_master.png 06_rosalind_in_kings_lab_wide.png
crop rosalind_lab_identity_master.png 760x428+0+20 07_rosalind_scientist_portrait.png
crop rosalind_lab_identity_master.png 980x551+520+120 08_experimental_record_and_instrument.png

# フランクリンとゴスリングによるDNAのX線回折実験
frame xray_diffraction_experiment_master.png 09_xray_diffraction_experiment_wide.png
crop xray_diffraction_experiment_master.png 820x461+0+40 10_rosalind_aligns_dna_fibre.png
crop xray_diffraction_experiment_master.png 800x450+760+50 11_gosling_adjusts_camera.png
crop xray_diffraction_experiment_master.png 930x523+390+170 12_hydrated_fibre_and_xray_camera.png

# Photo 51を測定し、らせん構造の証拠を読む
frame photo51_analysis_master.png 13_photo51_analysis_wide.png
crop photo51_analysis_master.png 760x428+760+90 14_photo51_x_pattern.png
crop photo51_analysis_master.png 920x518+0+100 15_rosalind_measures_pattern.png
tone photo51_analysis_master.png 16_evidence_for_helical_structure.png 88,103,104 '#2b2337'

# フランクリンの知らないところで写真がワトソンへ示される
frame photo51_shown_without_knowledge_master.png 17_photo51_shown_wide.png
crop photo51_shown_without_knowledge_master.png 700x394+0+40 18_wilkins_holds_diffraction_image.png
crop photo51_shown_without_knowledge_master.png 760x428+840+30 19_watson_sees_photo51.png
crop photo51_shown_without_knowledge_master.png 760x428+460+160 20_photo51_between_two_scientists.png

# 1962年のノーベル賞は三人へ
frame nobel_1962_master.png 21_nobel_ceremony_1962_wide.png
crop nobel_1962_master.png 1180x664+250+0 22_three_laureates_together.png
crop nobel_1962_master.png 980x551+520+230 23_three_laureates_and_medals.png

# Birkbeckで続いた研究と、残された空白
frame birkbeck_science_master.png 24_birkbeck_virus_science_wide.png
frame empty_birkbeck_lab_master.png 25_empty_birkbeck_lab_wide.png
crop empty_birkbeck_lab_master.png 800x450+800+250 26_folded_lab_coat_and_notebook.png
crop empty_birkbeck_lab_master.png 1050x591+320+270 27_unfinished_virus_research.png
tone empty_birkbeck_lab_master.png 28_quiet_absence_after_1958.png 72,90,103 '#172235'

# 死後授与をしない規則を、架空の拒否場面なしで示す
frame nobel_rule_archive_master.png 29_nobel_archive_three_awards_wide.png
crop nobel_rule_archive_master.png 1120x630+420+250 30_exactly_three_award_sets.png

# 長く過小評価された精密な仕事
crop photo51_analysis_master.png 840x473+0+30 31_dedication_in_darkroom.png
crop rosalind_lab_identity_master.png 980x551+380+180 32_measurements_and_notebook.png
tone photo51_analysis_master.png 33_photo51_and_rosalind_remembered.png 92,104,103 '#3b2934'

# 現代の科学へ続く遺産
frame legacy_modern_science_master.png 34_legacy_in_modern_science_wide.png
crop legacy_modern_science_master.png 1160x653+360+170 35_scientists_compare_photo51_and_dna.png

# 「科学史は大声だけで作られない」を高校生へ返す
frame quiet_voices_history_master.png 36_student_in_science_archive_wide.png
crop quiet_voices_history_master.png 1180x664+360+120 37_student_photo51_and_franklin.png
tone quiet_voices_history_master.png 38_quiet_voices_history_final.png 88,103,102 '#17253a'

expected=(
  01_double_helix_publication_wide.png
  02_double_helix_model_detail.png
  03_watson_and_crick_at_model.png
  04_model_and_research_notes.png
  05_structure_published_1953.png
  06_rosalind_in_kings_lab_wide.png
  07_rosalind_scientist_portrait.png
  08_experimental_record_and_instrument.png
  09_xray_diffraction_experiment_wide.png
  10_rosalind_aligns_dna_fibre.png
  11_gosling_adjusts_camera.png
  12_hydrated_fibre_and_xray_camera.png
  13_photo51_analysis_wide.png
  14_photo51_x_pattern.png
  15_rosalind_measures_pattern.png
  16_evidence_for_helical_structure.png
  17_photo51_shown_wide.png
  18_wilkins_holds_diffraction_image.png
  19_watson_sees_photo51.png
  20_photo51_between_two_scientists.png
  21_nobel_ceremony_1962_wide.png
  22_three_laureates_together.png
  23_three_laureates_and_medals.png
  24_birkbeck_virus_science_wide.png
  25_empty_birkbeck_lab_wide.png
  26_folded_lab_coat_and_notebook.png
  27_unfinished_virus_research.png
  28_quiet_absence_after_1958.png
  29_nobel_archive_three_awards_wide.png
  30_exactly_three_award_sets.png
  31_dedication_in_darkroom.png
  32_measurements_and_notebook.png
  33_photo51_and_rosalind_remembered.png
  34_legacy_in_modern_science_wide.png
  35_scientists_compare_photo51_and_dna.png
  36_student_in_science_archive_wide.png
  37_student_photo51_and_franklin.png
  38_quiet_voices_history_final.png
)
for file in $expected; do
  test -s "$OUT/$file"
done
echo "H040 adopted final_style01 PNG count: ${#expected[@]}"
