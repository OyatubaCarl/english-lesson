#!/bin/zsh
# 02-11 (難単語) を v4 (intro+paper_variant) でビルド
set -e
cd "$(dirname "$0")/shorts"
for qid in 02_resilient 03_ubiquitous 04_scrutinize 05_profound 06_mundane 07_fragile 08_vivid 09_inevitable 10_tranquil 11_diligent; do
  echo "==== building v4 $qid ===="
  /usr/bin/python3 build_lou_quiz_short_v4.py --quiz "$qid"
done
echo "All 10 v4 hard builds done."
ls -la lou_quiz_short_v4_*.mp4
