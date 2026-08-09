#!/bin/bash
# 生キャプチャ(webm) → イントロ/アウトロカード + BGM を合成した mp4 を書き出す。
set -e
cd "$(dirname "$0")"                       # _video/
REC=$(ls -t rec/*.webm | head -1)
BGM="../../promo_video/suno_bgm.mp3"
INTRO="card_intro.png"
OUTRO="card_outro.png"
OUT="taco_party_lesson1.mp4"
W=860; H=1760; FPS=30

echo "source webm: $REC"
DUR=$(ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 "$REC")
echo "gameplay duration: ${DUR}s"

# 1) 本編: 左上430x880(=アプリ全面)をクロップ → lanczosで860x1760へ → CFR/h264(無音)
ffmpeg -y -i "$REC" -vf "crop=430:880:0:0,fps=$FPS,scale=$W:$H:flags=lanczos,unsharp=5:5:0.5,format=yuv420p" \
  -an -c:v libx264 -preset medium -crf 20 body.mp4

# 2) イントロ(2.6s) / アウトロ(3.2s) を静止画から生成
ffmpeg -y -loop 1 -t 2.6 -i "$INTRO" -vf "fps=$FPS,scale=$W:$H,format=yuv420p" -c:v libx264 -preset medium -crf 20 intro.mp4
ffmpeg -y -loop 1 -t 3.2 -i "$OUTRO" -vf "fps=$FPS,scale=$W:$H,format=yuv420p" -c:v libx264 -preset medium -crf 20 outro.mp4

# 3) 連結（intro + body + outro）
printf "file 'intro.mp4'\nfile 'body.mp4'\nfile 'outro.mp4'\n" > concat.txt
ffmpeg -y -f concat -safe 0 -i concat.txt -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p novo_silent.mp4

TOTAL=$(ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 novo_silent.mp4)
echo "total (with cards): ${TOTAL}s"

# 4) BGM を尺に合わせて敷く（イン/アウトのフェード、音量控えめ）
FOUT=$(python3 -c "print(max(0, ${TOTAL}-1.4))")
ffmpeg -y -i novo_silent.mp4 -stream_loop -1 -i "$BGM" \
  -filter_complex "[1:a]volume=0.55,afade=t=in:st=0:d=1.2,afade=t=out:st=${FOUT}:d=1.3[a]" \
  -map 0:v -map "[a]" -t "$TOTAL" -c:v copy -c:a aac -b:a 192k -shortest "$OUT"

echo "=== DONE: $(pwd)/$OUT ==="
ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 "$OUT" | xargs -I{} echo "final duration: {}s"
ls -la "$OUT"
