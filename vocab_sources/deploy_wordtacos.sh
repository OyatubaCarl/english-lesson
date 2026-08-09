#!/bin/zsh
# WordTacos を Cloudflare Pages へ配信。
# - app.html を index.html として置く(ルートURLで404しないように)
# - 不要ファイル(server.py, *_batch_*.json, mascot_with_bg/ など)は除外
# - app_audio/app_assets/stage*_quizzes_clean.json だけ含める
set -euo pipefail
cd "$(dirname "$0")"

DIST=/tmp/wordtacos-deploy
rm -rf "$DIST"
mkdir -p "$DIST"

cp app.html "$DIST/index.html"
# app.html は manifest.json で start_url=./app.html を指定しているのでそちらにも置く
cp app.html "$DIST/app.html"
cp gasflare.js "$DIST/gasflare.js"
cp kitchen_rush_prototype.html "$DIST/kitchen_rush_prototype.html"
cp manifest.json "$DIST/manifest.json"
cp sw.js "$DIST/sw.js"
cp stage{1,2,3,4,5,6}_quizzes_clean.json "$DIST/"
cp stage_toeic_basic_quizzes_clean.json stage_toeic_mid_quizzes_clean.json stage_toeic_high_quizzes_clean.json stage_toeic_expert_quizzes_clean.json "$DIST/" 2>/dev/null || true
rsync -a --exclude='mascot_with_bg' app_assets/ "$DIST/app_assets/"
cp -r app_audio "$DIST/app_audio"

echo "--- dist staged ---"
du -sh "$DIST"
find "$DIST" -type f | wc -l

echo "--- deploying ---"
npx wrangler@latest pages deploy "$DIST" \
  --project-name=wordtacos \
  --branch=main \
  --commit-dirty=true
