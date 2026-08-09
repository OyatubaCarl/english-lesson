#!/usr/bin/env python3
"""L2「海での一日」ショート v3 — 真の全画面(縦クロップ拡大)＋冒頭フック＋日本語訳。
映像を画面いっぱいに。情報は上下の暗がりグラデ内に寄せ、中央は映像主役。"""
from pathlib import Path
import subprocess
import sys

WORK_DIR = Path(
    "/Users/masaki/Documents/ClaudeCode/英語学習教材作成/shorts"
)
SRC_VIDEO = Path("/tmp/middle_L2.mp4")
GRAD_PNG = Path("/tmp/grad_overlay.png")
VARIANT = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in ("a", "b") else "a"
_SUFFIX = {"a": "a_jp_v3", "b": "b_raw_v3"}[VARIANT]
OUT_MP4 = WORK_DIR / f"l2_seaside_short_{_SUFFIX}.mp4"
ASS_PATH = Path(f"/tmp/l2_short_{VARIANT}_v3.ass")

SLICE_START = 0.0
DURATION = 32.0
W, H = 1080, 1920
FPS = 30

# 日本語訳: 1文1行・最長16字。映像下部の暗がりグラデ内 y1245 に配置。
JP_SEGMENTS = [
    (2.5,  8.0,  "先週の日曜日、家族と海へ行った。"),
    (8.0,  14.0, "海は青くて、きれいだった。"),
    (14.0, 20.2, "太陽は明るく、雲ひとつなかった。"),
    (20.2, 26.0, "兄は泳ぎが得意で、"),
    (26.0, 31.5, "何度も泳いで、楽しそうだった。"),
]


def t_ass(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = t - h*3600 - m*60
    return f"{h}:{m:02d}:{s:05.2f}"


def dialogue(layer, start, end, style, text, ov=""):
    return f"Dialogue: {layer},{t_ass(start)},{t_ass(end)},{style},,0,0,0,,{ov}{text}"


ASS_HEADER = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
ScaledBorderAndShadow: yes
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: HookY,    Hiragino Sans W7,            98, &H003DD9FF, &H003DD9FF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 2, 0, 1, 7, 4, 5, 0, 0, 0, 1
Style: HookW,    Hiragino Sans W7,            86, &H00FFFFFF, &H00FFFFFF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 2, 0, 1, 7, 4, 5, 0, 0, 0, 1
Style: TopLab,   Hiragino Maru Gothic ProN,    46, &H00FFFFFF, &H00FFFFFF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 4, 0, 1, 3, 2, 5, 0, 0, 0, 1
Style: Handle,   Helvetica,                    34, &HC0FFFFFF, &HC0FFFFFF, &H00000000, &H00000000,  0, 0, 0, 0, 100, 100, 2, 0, 1, 2, 1, 5, 0, 0, 0, 1
Style: JpLine,   Hiragino Maru Gothic ProN,    60, &H00FFFFFF, &H00FFFFFF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 1, 0, 1, 5, 3, 5, 60, 60, 0, 1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

lines = []

# 冒頭フック 0.0-2.3（中央・映像の上に大きく）
lines.append(dialogue(0, 0.0, 2.3, "HookY", "“海へ行った”",
                      "{\\pos(540,880)\\fad(150,180)}"))
lines.append(dialogue(0, 0.0, 2.3, "HookW", "英語で 言える ?",
                      "{\\pos(540,1015)\\fad(200,180)}"))

# 上部: ハンドル＋レッスン名（上グラデ内）
lines.append(dialogue(0, 0.0, DURATION, "Handle", "@TeacherTacosEnglish",
                      "{\\pos(540,110)\\fad(250,200)}"))
lines.append(dialogue(0, 2.3, DURATION, "TopLab", "中学英語 Lesson 2 ・ 海 で の 一日",
                      "{\\pos(540,205)\\fad(220,200)}"))
lines.append(dialogue(0, 2.3, DURATION, "TopLab", "be 動詞 の 過去形  was / were",
                      "{\\pos(540,290)\\fad(280,200)}"))

# 日本語訳（A=訳あり のみ。B=訳なし は出さない＝A/Bの差を訳の有無だけにする）
if VARIANT == "a":
    for start, end, text in JP_SEGMENTS:
        lines.append(dialogue(0, start, end, "JpLine", text,
                              "{\\pos(540,1245)\\fad(150,120)}"))

ASS_PATH.write_text(ASS_HEADER + "\n".join(lines) + "\n", encoding="utf-8")
print(f"ASS -> {ASS_PATH} ({len(lines)} lines)")

ass_escaped = str(ASS_PATH).replace(":", r"\:")
filter_complex = (
    f"[0:v]scale=-2:{H},crop={W}:{H},setsar=1[v0];"
    f"[v0][1:v]overlay=0:0[v1];"
    f"[v1]subtitles=filename={ass_escaped}[vout]"
)

cmd = [
    "ffmpeg", "-y",
    "-ss", str(SLICE_START), "-t", str(DURATION), "-i", str(SRC_VIDEO),
    "-i", str(GRAD_PNG),
    "-filter_complex", filter_complex,
    "-map", "[vout]", "-map", "0:a",
    "-af", "afade=t=in:st=0:d=0.3,afade=t=out:st=29:d=3",
    "-r", str(FPS),
    "-c:v", "libx264", "-preset", "fast", "-crf", "21", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "192k",
    "-t", str(DURATION), "-movflags", "+faststart", "-shortest",
    str(OUT_MP4),
]
print("Running ffmpeg…")
res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode != 0:
    print(res.stderr[-3500:], file=sys.stderr)
    sys.exit(res.returncode)
print(f"OK -> {OUT_MP4} ({OUT_MP4.stat().st_size/1024/1024:.1f} MB)")
