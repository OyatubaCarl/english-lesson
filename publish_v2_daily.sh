#!/bin/bash
# WordTacos v5（長難単語・画像スタート）ショートの日次予約公開アップ（クォータ上限で1日最大6本）。
# 未アップかつ shorts/lou_quiz_short_v4_<id>.mp4 が存在する v5-long10 の語を、1日1本ペースで publishAt 予約。
# launchd (com.masaki.wordtacos-v2-daily) から毎日実行される想定。
# 停止: launchctl unload ~/Library/LaunchAgents/com.masaki.wordtacos-v2-daily.plist
set -euo pipefail
PROJ="/Users/masaki/Documents/ClaudeCode/英語学習教材作成"
LOG="$PROJ/shorts/_v2_daily.log"
cd "$PROJ"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] daily upload start" >> "$LOG"
# v5(画像スタート)を優先して消化し、在庫が尽きたら v2(白カード)へ引き継ぐ。
# 在庫の有無は終了コードでは分からない(対象なしでも正常終了する)ので dry-run の出力で判定する。
if /usr/bin/python3 publish_v5_shorts.py --count 1 --dry-run 2>&1 | grep -q "対象なし"; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] v5 在庫なし → v2白カードへ" >> "$LOG"
  /usr/bin/python3 publish_v2_white.py --count 6 >> "$LOG" 2>&1 || \
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] v2白カード upload error (quota/token/network?)" >> "$LOG"
else
  /usr/bin/python3 publish_v5_shorts.py --count 6 >> "$LOG" 2>&1 || \
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] v5 upload error (quota/token/network?)" >> "$LOG"
fi
echo "[$(date '+%Y-%m-%d %H:%M:%S')] daily upload done" >> "$LOG"
