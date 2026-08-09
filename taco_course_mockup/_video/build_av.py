#!/usr/bin/env python3
"""映像(無音) + VOICEPEAKナレーション + ビート区間の本来BGM(b1.mp3) + 軽いBGM を合成。

timings.json の各区間開始時刻を使って、ナレーションと b1.mp3 を正しい位置に置く。
"""
import json
import subprocess
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent          # _video/
os.chdir(HERE)
MOCK = HERE.parent                              # taco_course_mockup/
ROOT = MOCK.parent                              # 英語学習教材作成/

VOICEPEAK = "/Applications/voicepeak.app/Contents/MacOS/voicepeak"
NARRATOR = "Japanese Female 1"
SPEED = "92"

W, H, FPS = 860, 1760, 30
INTRO_DUR, OUTRO_DUR = 3.0, 3.4
CAL = 0.0                                        # 録画開始とT0のずれ補正（必要なら調整）

REC = sorted((HERE / "rec").glob("*.webm"), key=lambda p: p.stat().st_mtime)[-1]
SONG = MOCK / "app_assets/songs/b1.mp3"          # タコビートの本来BGM
BED = ROOT / "promo_video/suno_bgm.mp3"          # 全体の軽いBGM
INTRO_CARD = HERE / "card_intro.png"
OUTRO_CARD = HERE / "card_outro.png"
OUT = HERE / "taco_party_lesson1.mp4"

# ナレーション台本（落ち着いたトーン。各区間の開始に配置）
NARRATION = {
    "goto":        "タコス・パーティー。歌とミニゲームで英語を学ぶ、無料のアプリです。ひとつのレッスンを、五つのミニゲームで遊びながら、一個のタコスに仕上げます。入門レッスンを、最初から通して見ていきます。",
    "beat_open":   "まずはタコビート。歌に合わせて、飛んでくる単語のノーツをタップします。今日の英文が、そのまま歌になっていて、リズムで単語を体に入れます。",
    "tomato_open": "トマトマト。日本語まじりの文の中の英単語をタップし、意味を選んで収穫します。文脈から意味を推測する、という学び方です。",
    "shadow_open": "チーズ・シャドウイング。お手本の音声に続けて音読すると、読めた単語が緑に光っていきます。",
    "salsa_open":  "サルサ・グラマー。文法の穴うめクイズです。正しい材料のボトルを、すり鉢に入れてサルサを作ります。",
    "lettuce_open": "シャキシャキ・レタス。ばらばらのタイルを正しい順にならべて、文を組み立てます。",
    "complete":    "五つの具材がそろって、タコスの完成です。ブラウザだけで、無料で遊べます。ぜひ、一個食べてみてください。",
}
# 各ナレーションを置くタイミング（区間開始からの遅延・秒）
DELAY_AFTER = {"goto": 0.4, "beat_open": 1.2, "tomato_open": 1.0, "shadow_open": 1.0,
               "salsa_open": 1.0, "lettuce_open": 1.0, "complete": 1.2}


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("ERR:", " ".join(str(c) for c in cmd[:6]), "...")
        print(r.stderr[-600:])
        raise SystemExit(1)
    return r


def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nk=1:nw=1", str(path)], capture_output=True, text=True)
    return float(r.stdout.strip())


def vp(text, out):
    subprocess.run(["pkill", "-9", "-f", "/Applications/voicepeak.app"], capture_output=True)
    r = subprocess.run([VOICEPEAK, "-s", text, "-n", NARRATOR, "-o", str(out), "--speed", SPEED],
                       capture_output=True, text=True)
    if r.returncode != 0 or not Path(out).exists():
        print("VP ERR:", r.stderr[-300:])
        raise SystemExit(1)


def main():
    tim = json.load(open("timings.json"))
    marks = {m["name"]: m for m in tim["marks"]}
    print("marks:", {k: v["t"] for k, v in marks.items()})

    # ---- 1) 無音の映像を組む（クロップ→拡大→前後カード） ----
    print("[1] silent video")
    run(["ffmpeg", "-y", "-i", str(REC),
         "-vf", f"crop=430:880:0:0,fps={FPS},scale={W}:{H}:flags=lanczos,unsharp=5:5:0.5,format=yuv420p",
         "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "body.mp4"])
    for card, t, name in [(INTRO_CARD, INTRO_DUR, "introv.mp4"), (OUTRO_CARD, OUTRO_DUR, "outrov.mp4")]:
        run(["ffmpeg", "-y", "-loop", "1", "-t", str(t), "-i", str(card),
             "-vf", f"fps={FPS},scale={W}:{H},format=yuv420p",
             "-c:v", "libx264", "-preset", "medium", "-crf", "20", name])
    open("concat.txt", "w").write("file 'introv.mp4'\nfile 'body.mp4'\nfile 'outrov.mp4'\n")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "concat.txt",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "silent.mp4"])
    TOTAL = dur("silent.mp4")
    print("  total:", TOTAL)

    # ---- 2) ナレーション生成 ----
    print("[2] narration (VOICEPEAK)")
    clips = []          # (path, video_time_sec)
    for name, text in NARRATION.items():
        if name not in marks:
            continue
        wav = f"n_{name}.wav"
        vp(text, wav)
        vt = INTRO_DUR + marks[name]["t"] + DELAY_AFTER.get(name, 1.0) + CAL
        if name == "goto":
            vt = 0.5     # イントロカードに重ねる
        clips.append((wav, vt, dur(wav)))
        print(f"  {name}: @{vt:.1f}s  len={clips[-1][2]:.1f}s")

    # narration ミックス（各clipを配置 → 合算）
    inp = []
    fc = []
    for i, (wav, vt, _l) in enumerate(clips):
        inp += ["-i", wav]
        fc.append(f"[{i}:a]aresample=48000,adelay={int(vt*1000)}|{int(vt*1000)}[n{i}]")
    mixstr = "".join(f"[n{i}]" for i in range(len(clips)))
    fc.append(f"{mixstr}amix=inputs={len(clips)}:normalize=0:dropout_transition=0,"
              f"apad,atrim=0:{TOTAL},volume=1.35[na]")
    run(["ffmpeg", "-y", *inp, "-filter_complex", ";".join(fc), "-map", "[na]",
         "-ac", "2", "-ar", "48000", "narration.wav"])

    # ---- 3) 音楽トラック: ビート区間=本来のb1.mp3 / それ以外=軽いBED ----
    print("[3] music (beat song + bed)")
    song_len = dur(SONG)
    s0 = marks["beat_song0"]
    beat_song_vt = INTRO_DUR + s0["t"] - float(s0.get("songT", 0.0)) + CAL   # b1のt=0が来るvideo時刻
    beat_a = beat_song_vt
    beat_b = beat_song_vt + song_len
    print(f"  beat song @ {beat_a:.2f}..{beat_b:.2f}s")
    # BED: 全体に薄く。ただしビート区間は0にする（本来BGM優先）
    bed_vol = f"volume='if(between(t,{beat_a-0.4:.2f},{beat_b+0.3:.2f}),0,0.085)':eval=frame"
    run(["ffmpeg", "-y", "-stream_loop", "-1", "-i", str(BED),
         "-af", f"{bed_vol},atrim=0:{TOTAL},aresample=48000", "-ac", "2", "bed.wav"])
    # b1.mp3 をビート開始位置へ
    run(["ffmpeg", "-y", "-i", str(SONG),
         "-af", f"volume=0.5,adelay={int(beat_a*1000)}|{int(beat_a*1000)},apad,atrim=0:{TOTAL},aresample=48000",
         "-ac", "2", "beatsong.wav"])
    run(["ffmpeg", "-y", "-i", "bed.wav", "-i", "beatsong.wav",
         "-filter_complex", "[0][1]amix=inputs=2:normalize=0[m]", "-map", "[m]", "-ac", "2", "music.wav"])

    # ---- 4) ナレーション + 音楽 を合算 → 映像にmux ----
    print("[4] mux")
    run(["ffmpeg", "-y", "-i", "silent.mp4", "-i", "narration.wav", "-i", "music.wav",
         "-filter_complex",
         "[1:a]volume=1.0[v];[2:a]volume=1.0[m];[v][m]amix=inputs=2:normalize=0,alimiter=limit=0.95[a]",
         "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-t", str(TOTAL), str(OUT)])
    print("=== DONE:", OUT, f"({dur(OUT):.1f}s) ===")


if __name__ == "__main__":
    main()
