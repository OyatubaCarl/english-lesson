#!/bin/bash
# add_song.sh — タコス・ビートに新しい歌を1曲追加する薄いラッパー
#
# 使い方:
#   ./add_song.sh <mp3パス> <曲ID>
#   例: ./add_song.sh "/Users/masaki/Documents/ClaudeCode/FunnicsIsland/songs/06_beginner_tom_b2/audio/b2_suno.mp3" b2
#
# ゲームに載せる（index.html を書き換える）場合は第3引数に --inject:
#   ./add_song.sh <mp3パス> <曲ID> --inject
#
# 詳細な手順・パラメータの意味は CONTENT.md を参照。
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PY="/Users/masaki/Documents/ClaudeCode/英語学習教材作成/venv/bin/python3"

if [ $# -lt 2 ]; then
  echo "使い方: $0 <mp3パス> <曲ID> [--inject]" >&2
  echo "  例:   $0 /path/to/b2_suno.mp3 b2" >&2
  exit 1
fi

MP3="$1"
SONG_ID="$2"
INJECT_ARGS=()
if [ "${3:-}" = "--inject" ]; then
  INJECT_ARGS=(--inject "$SCRIPT_DIR/index.html")
fi

if [ ! -x "$VENV_PY" ]; then
  echo "ERROR: venv の python が見つかりません: $VENV_PY" >&2
  echo "       (whisper/torch/torchaudio/scipy 入りの venv が必要。CONTENT.md 参照)" >&2
  exit 1
fi

# ${arr[@]+...} は空配列でも set -u で落ちない書き方（macOS の bash 3.2 対策）
"$VENV_PY" "$SCRIPT_DIR/make_chart.py" "$MP3" --id "$SONG_ID" \
  --outdir "$SCRIPT_DIR" ${INJECT_ARGS[@]+"${INJECT_ARGS[@]}"}

echo ""
echo "--------------------------------------------------------------"
echo "デプロイするには:"
echo "  cd \"$SCRIPT_DIR\" && npx wrangler@latest pages deploy . --project-name=taco-beat --branch=main --commit-dirty=true"
echo "--------------------------------------------------------------"
