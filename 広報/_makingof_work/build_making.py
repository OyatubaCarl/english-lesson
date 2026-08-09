#!/usr/bin/env python3
"""メイキング紹介ショート (1080x1920, 30fps, 8カット) ビルダー。

前提: narr1..8.wav / slides.html / 画像素材 が同ディレクトリに生成済み。
出力: ../making_of_short.mp4
"""
from __future__ import annotations
import subprocess
from pathlib import Path

WORK = Path(__file__).resolve().parent
OUT = WORK.parent / "making_of_short.mp4"
RENDER_JS = "/Users/masaki/Documents/ClaudeCode/英語学習教材作成/shorts/render_card_v2.js"
BGM = "/Users/masaki/Documents/ClaudeCode/FunnicsIsland/songs/21_tacos_fiesta_dance/audio/tacos_fiesta_suno_SX3pVWTGGFxEsIHW.mp3"
BGM_VOL = "0.22"
W, H, FPS = 1080, 1920, 30
N_CUTS = 8
LEAD_IN = 0.4          # カット頭のナレ前の間
MIN_CUT = 7.0          # 各カット最低尺 (合計55秒以上を確保)
MIN_LAST = 7.5         # 最終カットは少し長めに余韻


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def dur(path: Path) -> float:
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", str(path)])
    return float(r.stdout.strip())


def silence(seconds: float, out: Path):
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
         "-t", f"{seconds:.3f}", str(out)])


def concat_audio(parts: list[Path], out: Path):
    inputs = []
    for p in parts:
        inputs += ["-i", str(p)]
    n = len(parts)
    filt = "".join(f"[{i}:a]aresample=44100,aformat=channel_layouts=stereo[a{i}];" for i in range(n))
    filt += "".join(f"[a{i}]" for i in range(n)) + f"concat=n={n}:v=0:a=1[out]"
    run(["ffmpeg", "-y", *inputs, "-filter_complex", filt, "-map", "[out]", str(out)])


def img_clip_zoom(img: Path, seconds: float, out: Path):
    """Ken Burns: 1.5倍解像度→中心へゆっくりズーム (静止画感の解消)。"""
    frames = max(1, int(seconds * FPS))
    vf = (f"scale={int(W*1.5)}:-1,"
          f"zoompan=z='1+0.00028*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
          f":d={frames}:s={W}x{H}:fps={FPS},format=yuv420p")
    run(["ffmpeg", "-y", "-i", str(img), "-vf", vf, "-t", f"{seconds:.3f}",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", str(out)])


def concat_video(clips: list[Path], out: Path):
    lst = WORK / "concat.txt"
    lst.write_text("".join(f"file '{c}'\n" for c in clips))
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-c", "copy", str(out)])


def main():
    # 1) スライドPNG描画
    for i in range(1, N_CUTS + 1):
        png = WORK / f"slide{i}.png"
        if not png.exists():
            run(["node", RENDER_JS, f"file://{WORK}/slides.html?cut={i}", str(png)])
            print(f"  ok slide{i}.png")

    # 2) カット尺 = max(ナレ+LEAD_IN+0.8, MIN_CUT)
    cut_secs: list[float] = []
    narr_secs: list[float] = []
    for i in range(1, N_CUTS + 1):
        nd = dur(WORK / f"narr{i}.wav")
        narr_secs.append(nd)
        floor = MIN_LAST if i == N_CUTS else MIN_CUT
        cut_secs.append(max(nd + LEAD_IN + 0.8, floor))
    total = sum(cut_secs)
    for i, (c, n) in enumerate(zip(cut_secs, narr_secs), 1):
        print(f"  cut{i}: {c:.2f}s (narr {n:.2f}s)")
    print(f"  total: {total:.2f}s")

    # 3) 音声トラック: 各カット [LEAD_IN無音 + ナレ + 残り無音]
    voice_parts: list[Path] = []
    for i in range(1, N_CUTS + 1):
        pre = WORK / f"s_pre{i}.wav"
        silence(LEAD_IN, pre)
        tail_len = cut_secs[i - 1] - LEAD_IN - narr_secs[i - 1]
        tail = WORK / f"s_tail{i}.wav"
        silence(max(tail_len, 0.05), tail)
        voice_parts += [pre, WORK / f"narr{i}.wav", tail]
    concat_audio(voice_parts, WORK / "voice.wav")
    vd = dur(WORK / "voice.wav")
    print(f"  voice.wav: {vd:.2f}s")

    # 4) 映像: 各スライド→ズームクリップ→連結
    clips = []
    for i in range(1, N_CUTS + 1):
        clip = WORK / f"clip{i}.mp4"
        img_clip_zoom(WORK / f"slide{i}.png", cut_secs[i - 1], clip)
        clips.append(clip)
        print(f"  ok clip{i}.mp4")
    concat_video(clips, WORK / "base.mp4")

    # 5) 最終mix: 映像(先頭フェードイン/末尾フェードアウト) + ナレ + BGM(0.22,ループ,末尾1.2sフェード)
    fc = (
        f"[0:v]fade=t=in:st=0:d=0.4,fade=t=out:st={total-0.5:.2f}:d=0.5[v];"
        f"[2:a]aloop=loop=-1:size=2e9,atrim=0:{total:.2f},volume={BGM_VOL},"
        f"afade=t=out:st={total-1.2:.2f}:d=1.2[bgm];"
        f"[1:a]volume=1.25[vo];"
        f"[vo][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
        f"alimiter=limit=0.95[a]"
    )
    run(["ffmpeg", "-y", "-i", str(WORK / "base.mp4"), "-i", str(WORK / "voice.wav"),
         "-i", BGM, "-filter_complex", fc,
         "-map", "[v]", "-map", "[a]", "-t", f"{total:.2f}",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
         "-c:a", "aac", "-b:a", "192k", "-shortest", str(OUT)])
    print(f"done: {OUT} ({total:.1f}s)")


if __name__ == "__main__":
    main()
