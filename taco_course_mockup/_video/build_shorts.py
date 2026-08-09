#!/usr/bin/env python3
"""短尺ハイライト(860x1760) と 縦型ショート(1080x1920) を、生キャプチャ webm から組む。
ビートのクリップは本来のゲーム曲(b1.mp3)を同じ曲位置で使う。他は軽いBGM＋短いナレーション。"""
import json
import subprocess
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
os.chdir(HERE)
MOCK = HERE.parent
ROOT = MOCK.parent

VP = "/Applications/voicepeak.app/Contents/MacOS/voicepeak"
NAR = "Japanese Female 1"
FPS = 30
REC = sorted((HERE / "rec").glob("*.webm"), key=lambda p: p.stat().st_mtime)[-1]
SONG = MOCK / "app_assets/songs/b1.mp3"
BED = ROOT / "promo_video/suno_bgm.mp3"

TIM = json.load(open("timings.json"))
M = {m["name"]: m for m in TIM["marks"]}
SONG0_T = M["beat_song0"]["t"]                 # webm時刻
SONG0_POS = float(M["beat_song0"].get("songT", 0.26))


def song_pos(webm_t):
    return (webm_t - SONG0_T) + SONG0_POS       # そのwebm時刻での曲位置(秒)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("ERR", " ".join(str(c) for c in cmd[:5]), "\n", r.stderr[-500:])
        raise SystemExit(1)
    return r


def durof(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nk=1:nw=1", str(p)], capture_output=True, text=True)
    return float(r.stdout.strip())


def vp(text, out):
    subprocess.run(["pkill", "-9", "-f", "/Applications/voicepeak.app"], capture_output=True)
    run([VP, "-s", text, "-n", NAR, "-o", str(out), "--speed", "94"])
    return durof(out)


def clip(ss, dur, W, H, out, accurate=False):
    vf = (f"crop=430:880:0:0,scale={W}:{H}:force_original_aspect_ratio=decrease,"
          f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=0x1e3a8a,fps={FPS},format=yuv420p")
    if accurate:
        run(["ffmpeg", "-y", "-i", str(REC), "-ss", str(ss), "-t", str(dur),
             "-vf", vf, "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "20", out])
    else:
        run(["ffmpeg", "-y", "-ss", str(ss), "-i", str(REC), "-t", str(dur),
             "-vf", vf, "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "20", out])


def card(png, dur, W, H, out):
    run(["ffmpeg", "-y", "-loop", "1", "-t", str(dur), "-i", png,
         "-vf", f"scale={W}:{H},fps={FPS},format=yuv420p",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", out])


def concat_video(parts, out):
    txt = "concat_list.txt"
    open(txt, "w").write("".join(f"file '{p}'\n" for p in parts))
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", txt,
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", out])


def build_audio(total, narr, beat_win, beat_song_pos, out, bed_vol=0.09, song_vol=0.5):
    """narr=[(wav,start)], beat_win=(a,b) 本来曲を敷く区間, beat_song_pos=区間開始時の曲位置"""
    a, b = beat_win
    # narration
    inp, fc = [], []
    for i, (wav, st) in enumerate(narr):
        inp += ["-i", wav]
        fc.append(f"[{i}:a]aresample=48000,adelay={int(st*1000)}|{int(st*1000)}[n{i}]")
    fc.append("".join(f"[n{i}]" for i in range(len(narr))) +
              f"amix=inputs={len(narr)}:normalize=0:dropout_transition=0,apad,atrim=0:{total},volume=1.4[na]")
    run(["ffmpeg", "-y", *inp, "-filter_complex", ";".join(fc), "-map", "[na]", "-ac", "2", "s_narr.wav"])
    # bed（ビート区間は0）
    run(["ffmpeg", "-y", "-stream_loop", "-1", "-i", str(BED),
         "-af", f"volume='if(between(t,{a-0.3:.2f},{b+0.2:.2f}),0,{bed_vol})':eval=frame,atrim=0:{total},aresample=48000",
         "-ac", "2", "s_bed.wav"])
    # 本来曲（区間位置から）
    run(["ffmpeg", "-y", "-ss", f"{beat_song_pos:.3f}", "-i", str(SONG),
         "-af", f"volume={song_vol},adelay={int(a*1000)}|{int(a*1000)},apad,atrim=0:{total},aresample=48000",
         "-ac", "2", "s_song.wav"])
    run(["ffmpeg", "-y", "-i", "s_narr.wav", "-i", "s_bed.wav", "-i", "s_song.wav",
         "-filter_complex", "[0][1][2]amix=inputs=3:normalize=0,alimiter=limit=0.95[a]",
         "-map", "[a]", "-ac", "2", "-ar", "48000", out])


def mux(vsilent, awav, out):
    run(["ffmpeg", "-y", "-i", vsilent, "-i", awav, "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out])


# ================= 短尺ハイライト (860x1760) =================
def build_highlight():
    W, H = 860, 1760
    print("== highlight ==")
    segs = [
        ("card", "card_intro.png", 2.0),
        ("clip", 27, 13, True),      # beat（本来曲）
        ("clip", 105, 10, False),    # tomato
        ("clip", 136, 9, False),     # shadow
        ("clip", 229, 11, False),    # salsa
        ("clip", 268, 11, False),    # lettuce
        ("clip", 297.6, 6, False),   # complete
        ("card", "card_outro.png", 3.0),
    ]
    parts, t, starts = [], 0.0, {}
    for i, s in enumerate(segs):
        out = f"h_{i}.mp4"
        if s[0] == "card":
            card(s[1], s[2], W, H, out); d = s[2]
        else:
            _, ss, d, real = s
            clip(ss, d, W, H, out, accurate=real)
        starts[i] = t; t += d; parts.append(out)
    concat_video(parts, "h_silent.mp4")
    total = durof("h_silent.mp4")
    beat_a = starts[1]; beat_b = beat_a + segs[1][2]
    # narration
    lines = {
        0: ("タコス・パーティー。1レッスンを、5つのゲームで完食します。", 0.3),
        1: ("タコビート。リズムで単語を覚えます。", starts[1] + 0.4),
        2: ("トマトマト。文の中の英単語を収穫。", starts[2] + 0.3),
        3: ("チーズ・シャドウイング。続けて音読。", starts[3] + 0.3),
        4: ("サルサ・グラマー。文法を調合します。", starts[4] + 0.3),
        5: ("シャキシャキ・レタス。並べ替え。", starts[5] + 0.3),
        6: ("5つそろって、タコス完成！", starts[6] + 0.3),
    }
    narr = []
    for i, (txt, st) in lines.items():
        w = f"hn_{i}.wav"; vp(txt, w); narr.append((w, st))
    build_audio(total, narr, (beat_a, beat_b), song_pos(27), "h_audio.wav", bed_vol=0.09, song_vol=0.5)
    mux("h_silent.mp4", "h_audio.wav", "taco_party_highlight.mp4")
    print("  -> taco_party_highlight.mp4", round(durof("taco_party_highlight.mp4"), 1), "s")


# ================= 縦型ショート (1080x1920) =================
def build_short():
    W, H = 1080, 1920
    print("== vertical short ==")
    segs = [
        ("card", "card_hook_v.png", 2.6),
        ("clip", 29, 6, True),       # beat（本来曲）
        ("clip", 106, 5, False),     # tomato
        ("clip", 137, 4, False),     # shadow
        ("clip", 230, 5, False),     # salsa
        ("clip", 297.6, 5.2, False), # complete
        ("card", "card_cta_v.png", 3.0),
    ]
    parts, t, starts = [], 0.0, {}
    for i, s in enumerate(segs):
        out = f"v_{i}.mp4"
        if s[0] == "card":
            card(s[1], s[2], W, H, out); d = s[2]
        else:
            _, ss, d, real = s
            clip(ss, d, W, H, out, accurate=real)
        starts[i] = t; t += d; parts.append(out)
    concat_video(parts, "v_silent.mp4")
    total = durof("v_silent.mp4")
    beat_a = starts[1]; beat_b = beat_a + segs[1][2]
    lines = {
        0: ("英語の1レッスンを、まるごと完食。", 0.3),
        5: ("5つの具材で、タコス完成。無料で遊べます。", starts[5] + 0.2),
    }
    narr = []
    for i, (txt, st) in lines.items():
        w = f"vn_{i}.wav"; vp(txt, w); narr.append((w, st))
    build_audio(total, narr, (beat_a, beat_b), song_pos(29), "v_audio.wav", bed_vol=0.14, song_vol=0.55)
    mux("v_silent.mp4", "v_audio.wav", "taco_party_short_vertical.mp4")
    print("  -> taco_party_short_vertical.mp4", round(durof("taco_party_short_vertical.mp4"), 1), "s")


if __name__ == "__main__":
    import sys
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    if which in ("both", "highlight"):
        build_highlight()
    if which in ("both", "short"):
        build_short()
    print("done")
