#!/bin/bash
# WordTacos の実アセットを taco_course_mockup/app_assets へ同期する。
# 画像はモバイル向けに幅480pxへ縮小コピー(originalは変更しない)。
set -e
SRC="$(cd "$(dirname "$0")/../vocab_sources/app_assets" && pwd)"
DST="$(cd "$(dirname "$0")" && pwd)/app_assets"
CC_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"   # /Users/masaki/Documents/ClaudeCode
mkdir -p "$DST/mascot" "$DST/customers" "$DST/sounds" "$DST/bgm" "$DST/songs"
for m in idle blink proud speaking cheering cheering_warm encouraging surprised worried tumbled; do
  sips -Z 480 "$SRC/mascot/$m.png" --out "$DST/mascot/$m.png" >/dev/null
done
sips -Z 480 "$SRC/customers/tom.png" --out "$DST/customers/tom.png" >/dev/null
for s in kitchen_bgm fail_dizzy fail_negative success_fanfare correct victory checkpoint; do
  cp "$SRC/sounds/$s.mp3" "$DST/sounds/$s.mp3"
done
# レッスンの歌(動画化前のSuno音源)。96kbps へ圧縮してアプリに埋め込む。B{n} = FunnicsIsland/songs の該当フォルダ
# code(app内lesson) -> Funnics songs のパス。増やすときはここに追記。
declare -a SONGS=(
  "b1:FunnicsIsland/songs/05_beginner_tom_b1/audio/b1_suno.mp3"
)
for pair in "${SONGS[@]}"; do
  code="${pair%%:*}"; rel="${pair#*:}"; src="$CC_ROOT/$rel"
  if [ -f "$src" ]; then
    if command -v ffmpeg >/dev/null 2>&1; then ffmpeg -y -i "$src" -c:a libmp3lame -b:a 96k "$DST/songs/$code.mp3" >/dev/null 2>&1 || cp "$src" "$DST/songs/$code.mp3";
    else cp "$src" "$DST/songs/$code.mp3"; fi
    echo "song $code <- $rel"
  else echo "song $code: 見つかりません($rel)"; fi
done
echo "synced -> $DST"; du -sh "$DST"
