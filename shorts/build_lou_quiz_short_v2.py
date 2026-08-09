#!/usr/bin/env python3
"""ルー語クイズ Short v2 — ナレを英単語(ephemeral)のみに、論文なし固定。

usage:
  python3 build_lou_quiz_short_v2.py            # clean: イントロなし
  python3 build_lou_quiz_short_v2.py --intro    # intro: 冒頭に「ルー語風 英単語クイズ」

字幕の日本語パートはそのまま画面に出る（読者が目で追う前提）。
ナレは ephemeral を本文中と問題中の2回だけ流す。
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

# ============== モード ==============
INTRO = "--intro" in sys.argv

# ============== パス ==============
WORK = Path("/Users/masaki/Documents/ClaudeCode/英語学習教材作成/shorts")
ASSETS = WORK / "assets"
NARR_DIR = WORK / "narration"

BG_PNG = ASSETS / "sakura_bg.png"
TT_PNG = Path(
    "/Users/masaki/Documents/ClaudeCode/FunnicsIsland/characters/T_teacher_tacos/single.png"
)

# BGM 解決順: BGM_LIB_NAME (bgm_library/{name}.mp3) > BGM_OVERRIDE (絶対パス) > default(タコス曲)
_BGM_DEFAULT = Path(
    "/Users/masaki/Documents/ClaudeCode/FunnicsIsland/songs/21_tacos_fiesta_dance/audio/tacos_fiesta_suno_SX3pVWTGGFxEsIHW.mp3"
)
_BGM_LIB_DIR = ASSETS / "bgm_library"
_BGM_LIB_NAME = os.environ.get("BGM_LIB_NAME", "").strip()
_BGM_OVERRIDE = os.environ.get("BGM_OVERRIDE", "").strip()
if _BGM_LIB_NAME:
    BGM_SRC = _BGM_LIB_DIR / f"{_BGM_LIB_NAME}.mp3"
elif _BGM_OVERRIDE:
    BGM_SRC = Path(_BGM_OVERRIDE)
else:
    BGM_SRC = _BGM_DEFAULT
_is_default_bgm = (BGM_SRC == _BGM_DEFAULT)
BGM_VOLUME = float(os.environ.get("BGM_VOLUME", "0.07" if _is_default_bgm else "0.20"))
SUFFIX_BGM = os.environ.get(
    "SUFFIX_BGM",
    f"_{_BGM_LIB_NAME}" if _BGM_LIB_NAME else "",
)
SUFFIX = ("_intro" if INTRO else "_clean") + SUFFIX_BGM

EPH_WAV = NARR_DIR / "ephemeral.wav"   # say Samantha "ephemeral" を合成済

OUT_MP4 = WORK / f"lou_quiz_short_v2{SUFFIX}.mp4"
ASS_PATH = Path(f"/tmp/lou_quiz_v2{SUFFIX}.ass")

W, H, FPS = 1080, 1920, 30
DUR = 30.0

# ============== タイムライン定数 ==============
if INTRO:
    T_INTRO_IN = 0.0
    T_INTRO_OUT = 2.6
    T_BODY_START = 2.9
    T_BODY_END = 9.8
    T_QUIZ_START = 10.1
    T_QUIZ_END = 11.9
    T_HOOK_LABEL_IN = T_BODY_START
    T_HOOK_LABEL_OUT = T_QUIZ_END
    T_CHOICE_START = 12.2
    T_COUNTDOWN_START = 15.7
    T_COUNTDOWN_END = 18.7
    T_ANS_START = 18.7
    T_ANS_END = 21.0
    T_CTA_START = 21.0
else:
    T_INTRO_IN = T_INTRO_OUT = -1.0
    T_BODY_START = 0.0
    T_BODY_END = 8.1
    T_QUIZ_START = 8.6
    T_QUIZ_END = 10.6
    T_HOOK_LABEL_IN = 0.0
    T_HOOK_LABEL_OUT = T_QUIZ_END
    T_CHOICE_START = 11.0
    T_COUNTDOWN_START = 14.7
    T_COUNTDOWN_END = 17.9
    T_ANS_START = 17.9
    T_ANS_END = 21.6
    T_CTA_START = 21.6
T_CTA_END = DUR

# ナレ ephemeral 再生タイミング: 本文の ephemeral 字幕表示と同期
EPH_PLAY_BODY_DELAY_MS = int((T_BODY_START + 0.95) * 1000)
EPH_PLAY_QUIZ_DELAY_MS = int(T_QUIZ_START * 1000)


# ============== ASS ヘルパ ==============
def t(s: float) -> str:
    h = int(s // 3600); m = int((s % 3600) // 60); sec = s - h * 3600 - m * 60
    return f"{h}:{m:02d}:{sec:05.2f}"


def D(layer, start, end, style, text, ov=""):
    return f"Dialogue: {layer},{t(start)},{t(end)},{style},,0,0,0,,{ov}{text}"


ASS_HEADER = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
ScaledBorderAndShadow: yes
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: IntroTop, Hiragino Sans W7,              82, &H00FFFFFF, &H00FFFFFF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 4, 0, 1, 8, 5, 5, 0, 0, 0, 1
Style: IntroBig, Hiragino Sans W7,             138, &H003DD9FF, &H003DD9FF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 4, 0, 1, 10, 6, 5, 0, 0, 0, 1
Style: HookLabel,Hiragino Sans W7,              64, &H003DD9FF, &H003DD9FF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 2, 0, 1, 6, 4, 5, 0, 0, 0, 1
Style: Handle,   Helvetica,                     32, &HC0FFFFFF, &HC0FFFFFF, &H00000000, &H00000000,  0, 0, 0, 0, 100, 100, 2, 0, 1, 2, 1, 5, 0, 0, 0, 1
Style: BodyJP,   Hiragino Maru Gothic ProN,     58, &H00FFFFFF, &H00FFFFFF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 1, 0, 1, 5, 3, 5, 60, 60, 0, 1
Style: BodyEN,   Helvetica,                     78, &H006B7CFF, &H006B7CFF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 2, 0, 1, 6, 4, 5, 60, 60, 0, 1
Style: QuizQ,    Hiragino Sans W7,              74, &H00FFFFFF, &H00FFFFFF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 2, 0, 1, 6, 4, 5, 60, 60, 0, 1
Style: QuizEN,   Helvetica,                     86, &H006B7CFF, &H006B7CFF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 2, 0, 1, 6, 4, 5, 60, 60, 0, 1
Style: Choice,   Hiragino Sans W7,              64, &H00FFFFFF, &H00FFFFFF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 1, 0, 1, 5, 3, 5, 80, 80, 0, 1
Style: ChoiceOK, Hiragino Sans W7,              72, &H0066FF55, &H0066FF55, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 1, 0, 1, 6, 4, 5, 80, 80, 0, 1
Style: Count,    Helvetica,                    220, &H003DD9FF, &H003DD9FF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 2, 0, 1, 10, 6, 5, 0, 0, 0, 1
Style: Ans,      Hiragino Sans W7,             132, &H0066FF55, &H0066FF55, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 2, 0, 1, 10, 6, 5, 0, 0, 0, 1
Style: PaperBody,Hiragino Maru Gothic ProN,     46, &H00FFFFFF, &H00FFFFFF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 1, 0, 1, 5, 3, 5, 80, 80, 0, 1
Style: CtaBig,   Hiragino Sans W7,              74, &H00FFFFFF, &H00FFFFFF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 1, 0, 1, 6, 4, 5, 60, 60, 0, 1
Style: CtaHandle,Helvetica,                     60, &H003DD9FF, &H003DD9FF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 2, 0, 1, 6, 4, 5, 0, 0, 0, 1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def build_lines() -> list:
    lines = []

    # 上部ハンドル
    lines.append(D(0, 0.0, DUR, "Handle", "@TeacherTacosEnglish",
                   "{\\pos(540,90)\\fad(300,300)}"))

    # 0.0-2.6 イントロ「ルー語風 英単語クイズ」（INTROモードのみ）
    if INTRO:
        lines.append(D(0, T_INTRO_IN, T_INTRO_OUT, "IntroTop",
                       "ルー語風",
                       "{\\pos(540,820)\\fad(220,200)\\t(\\fscx108\\fscy108)}"))
        lines.append(D(0, T_INTRO_IN + 0.25, T_INTRO_OUT, "IntroBig",
                       "英単語 クイズ",
                       "{\\pos(540,1000)\\fad(280,200)\\t(\\fscx112\\fscy112)}"))

    # 「これ、読める ?」を上部に常時表示（4択開始で消える）
    lines.append(D(0, T_HOOK_LABEL_IN, T_HOOK_LABEL_OUT, "HookLabel",
                   "これ、読める ?",
                   "{\\pos(540,200)\\fad(220,300)}"))

    # 本文（字幕のみ・ナレなし）
    lines.append(D(0, T_BODY_START, T_BODY_END, "BodyJP",
                   "桜の 美しさは、",
                   "{\\pos(540,820)\\fad(220,180)}"))
    lines.append(D(0, T_BODY_START + 0.95, T_BODY_END, "BodyEN",
                   "ephemeral",
                   "{\\pos(540,940)\\fad(200,180)}"))
    lines.append(D(0, T_BODY_START + 1.95, T_BODY_END, "BodyJP",
                   "だ 。",
                   "{\\pos(540,1060)\\fad(180,180)}"))
    lines.append(D(0, T_BODY_START + 3.0, T_BODY_END, "BodyJP",
                   "咲いて から 散る まで 、",
                   "{\\pos(540,1180)\\fad(180,180)}"))
    lines.append(D(0, T_BODY_START + 4.6, T_BODY_END, "BodyJP",
                   "わずか 一週間 しか ない なんて 。",
                   "{\\pos(540,1300)\\fad(180,180)}"))

    # 問題（字幕のみ）
    lines.append(D(0, T_QUIZ_START, T_QUIZ_END, "QuizEN", "ephemeral",
                   "{\\pos(540,860)\\fad(180,150)}"))
    lines.append(D(0, T_QUIZ_START + 0.2, T_QUIZ_END, "QuizQ",
                   "の 意味は ?",
                   "{\\pos(540,1010)\\fad(220,150)}"))

    # 4択
    cx_L, cx_R = 270, 810
    cy_top, cy_bot = 920, 1110
    lines.append(D(0, T_CHOICE_START, T_COUNTDOWN_END, "Choice",
                   "A  永遠の",
                   f"{{\\pos({cx_L},{cy_top})\\fad(200,150)}}"))
    lines.append(D(0, T_CHOICE_START + 0.2, T_COUNTDOWN_END, "Choice",
                   "B  鮮やかな",
                   f"{{\\pos({cx_R},{cy_top})\\fad(200,150)}}"))
    lines.append(D(0, T_CHOICE_START + 0.4, T_COUNTDOWN_END, "Choice",
                   "C  はかない",
                   f"{{\\pos({cx_L},{cy_bot})\\fad(200,150)}}"))
    lines.append(D(0, T_CHOICE_START + 0.6, T_COUNTDOWN_END, "Choice",
                   "D  美しい",
                   f"{{\\pos({cx_R},{cy_bot})\\fad(200,150)}}"))
    lines.append(D(0, T_CHOICE_START, T_COUNTDOWN_END, "QuizQ",
                   "文脈で 答えよう",
                   "{\\pos(540,820)\\fad(220,150)\\fs48\\c&HC0FFFFFF&}"))

    # カウントダウン
    for i, num in enumerate(["3", "2", "1"]):
        s = T_COUNTDOWN_START + i * 1.0
        e = s + 1.0
        lines.append(D(0, s, e, "Count", num,
                       "{\\pos(540,1500)\\fad(120,180)\\t(\\fscx115\\fscy115)}"))

    # 正解
    lines.append(D(0, T_ANS_START, T_ANS_END, "Ans", "C",
                   "{\\pos(380,960)\\fad(120,200)\\t(\\fscx125\\fscy125)}"))
    lines.append(D(0, T_ANS_START + 0.15, T_ANS_END, "ChoiceOK",
                   "は か な い",
                   "{\\pos(720,960)\\fad(150,200)}"))
    lines.append(D(0, T_ANS_START + 0.4, T_ANS_END, "PaperBody",
                   "文脈で とれた人、もう 脳に残ってる。",
                   "{\\pos(540,1180)\\fad(220,200)\\fs44}"))

    # CTA
    lines.append(D(0, T_CTA_START, T_CTA_END, "CtaHandle",
                   "Teacher  Tacos  English  では、",
                   "{\\pos(540,720)\\fad(220,180)\\fs56}"))
    lines.append(D(0, T_CTA_START + 0.4, T_CTA_END, "CtaBig",
                   "中高で 習う 英単語が、",
                   "{\\pos(540,860)\\fad(220,180)}"))
    lines.append(D(0, T_CTA_START + 0.7, T_CTA_END, "CtaBig",
                   "日本語 混じり で 学べます 。",
                   "{\\pos(540,980)\\fad(220,180)\\c&H6BE0FF&}"))
    lines.append(D(0, T_CTA_START + 1.3, T_CTA_END, "CtaHandle",
                   "→  @ TeacherTacosEnglish",
                   "{\\pos(540,1640)\\fad(280,200)\\t(\\fscx108\\fscy108)}"))

    return lines


def write_ass() -> None:
    body = ASS_HEADER + "\n".join(build_lines()) + "\n"
    ASS_PATH.write_text(body, encoding="utf-8")
    print(f"ASS -> {ASS_PATH}  ({'INTRO' if INTRO else 'CLEAN'} mode)")


def build_video() -> None:
    for p, label in [(BG_PNG, "bg"), (TT_PNG, "tt"), (EPH_WAV, "eph"),
                     (BGM_SRC, "bgm")]:
        if not p.exists():
            sys.exit(f"missing {label}: {p}")

    ass_escaped = str(ASS_PATH).replace(":", r"\:")
    filter_complex = (
        # 背景
        f"[0:v]loop=loop=-1:size=1:start=0,trim=duration={DUR},setpts=PTS-STARTPTS,"
        f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},"
        f"zoompan=z='min(zoom+0.0006,1.10)':d=1:s={W}x{H}:fps={FPS}[bg];"
        # TT 小(右下、260px、0-T_CTA_START)
        f"[1:v]scale=260:-1,fps={FPS},trim=duration={T_CTA_START},setpts=PTS-STARTPTS[tt_s];"
        # TT 大(中央寄せ、360px、CTA区間)
        f"[1:v]scale=360:-1,fps={FPS},trim=duration={DUR-T_CTA_START},"
        f"setpts=PTS-STARTPTS+{T_CTA_START}/TB[tt_b];"
        # 合成
        f"[bg][tt_s]overlay=x=W-w-40:y=H-h-180:shortest=0:eof_action=pass[v1];"
        f"[v1][tt_b]overlay=x=(W-w)/2:y=1180:shortest=0:eof_action=pass[v2];"
        f"[v2]subtitles=filename={ass_escaped}[vout];"
        # 音声: BGM(-23dB) + ephemeral×2
        f"[2:a]aresample=48000,aformat=channel_layouts=mono,"
        f"adelay={EPH_PLAY_BODY_DELAY_MS}|{EPH_PLAY_BODY_DELAY_MS},apad[eph1];"
        f"[2:a]aresample=48000,aformat=channel_layouts=mono,"
        f"adelay={EPH_PLAY_QUIZ_DELAY_MS}|{EPH_PLAY_QUIZ_DELAY_MS},apad[eph2];"
        f"[3:a]atrim=0:{DUR},asetpts=PTS-STARTPTS,"
        f"aresample=48000,aformat=channel_layouts=mono,"
        f"volume={BGM_VOLUME},afade=t=in:st=0:d=0.6,afade=t=out:st={DUR-1.5}:d=1.5[bgm];"
        f"[bgm][eph1][eph2]amix=inputs=3:duration=first:dropout_transition=0:normalize=0[aout]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(BG_PNG),    # 0
        "-loop", "1", "-i", str(TT_PNG),    # 1
        "-i", str(EPH_WAV),                 # 2 (re-used for both plays via adelay)
        "-stream_loop", "-1", "-i", str(BGM_SRC),  # 3: BGM (loop if shorter than DUR)
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", "[aout]",
        "-r", str(FPS), "-t", str(DUR),
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(OUT_MP4),
    ]
    print(f"Running ffmpeg → {OUT_MP4.name}")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(res.stderr[-4500:], file=sys.stderr)
        sys.exit(res.returncode)
    size_mb = OUT_MP4.stat().st_size / 1024 / 1024
    print(f"OK -> {OUT_MP4}  ({size_mb:.1f} MB)")


def extract_frames() -> None:
    samples = [1.5, 4.0, 8.5, 13.0, 19.0, 25.0] if INTRO else [1.0, 5.0, 9.0, 13.0, 18.0, 25.0]
    for sec in samples:
        out = WORK / f"lou_v2{SUFFIX}_frame_{sec:.1f}.jpg"
        cmd = ["ffmpeg", "-y", "-ss", str(sec), "-i", str(OUT_MP4),
               "-frames:v", "1", "-q:v", "3", str(out)]
        subprocess.run(cmd, capture_output=True, text=True)
        print(f"  frame -> {out.name}")


if __name__ == "__main__":
    write_ass()
    build_video()
    extract_frames()
