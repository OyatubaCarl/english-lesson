#!/bin/zsh
# 10クイズ動画を順次ビルド (画像とナレが揃っている前提)
set -e
cd "$(dirname "$0")/shorts"
for qid in 02_resilient 03_ubiquitous 04_scrutinize 05_profound 06_mundane 07_fragile 08_vivid 09_inevitable 10_tranquil 11_diligent; do
  echo "==== building $qid ===="
  /usr/bin/python3 build_lou_quiz_short_v3.py --quiz "$qid"
done
echo "All 10 builds done."
ls -la lou_quiz_short_v3_*.mp4
