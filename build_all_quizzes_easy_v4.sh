#!/bin/zsh
# 12-21 (easy) を v4 でビルド
set -e
cd "$(dirname "$0")/shorts"
for qid in 12_gentle 13_nervous 14_huge 15_silent 16_delicious 17_disappear 18_whisper 19_brave 20_lonely 21_honest; do
  echo "==== building v4 $qid ===="
  /usr/bin/python3 build_lou_quiz_short_v4.py --quiz "$qid"
done
echo "All 10 v4 easy builds done."
ls -la lou_quiz_short_v4_1*.mp4 lou_quiz_short_v4_2*.mp4 2>/dev/null
