#!/usr/bin/env python3
"""不規則変化動詞ショート v4 — CMっぽさを消し、問いかけ＋豆知識トーン。
再生位置: 元動画 35-65秒（中盤ABB型ハイライト→ABC型導入）"""

from pathlib import Path
import subprocess
import sys

WORK_DIR = Path(
    "/Users/masaki/Documents/ClaudeCode/英語学習教材作成/shorts"
)
WORK_DIR.mkdir(parents=True, exist_ok=True)

SRC_VIDEO = Path("/tmp/original_irregular.mp4")
OUT_MP4 = WORK_DIR / "irregular_verbs_short_v4.mp4"
ASS_PATH = Path("/tmp/irregular_short_v4.ass")

SLICE_START = 35.0
DURATION = 30.0
W, H = 1080, 1920
FPS = 30

VID_W, VID_H = 1080, 608
VID_Y = (H - VID_H) // 2

def t_ass(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t - h * 3600 - m * 60
    return f"{h}:{m:02d}:{s:05.2f}"

def dialogue(layer, start, end, style, text, override=""):
    return f"Dialogue: {layer},{t_ass(start)},{t_ass(end)},{style},,0,0,0,,{override}{text}"

ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: HeadMain,  Hiragino Sans W7,            108, &H00FFFFFF, &H00FFFFFF, &H00081020, &H00000000, -1, 0, 0, 0, 100, 100, 4, 0, 1, 4, 0, 5, 0, 0, 0, 1
Style: HeadAcc,   Hiragino Sans W7,            108, &H003DD9FF, &H003DD9FF, &H00081020, &H00000000, -1, 0, 0, 0, 100, 100, 4, 0, 1, 4, 0, 5, 0, 0, 0, 1
Style: HeadQ,     Hiragino Maru Gothic ProN,    66, &H00C4CD4E, &H00C4CD4E, &H00081020, &H00000000,  0, 0, 0, 0, 100, 100, 6, 0, 1, 3, 0, 5, 0, 0, 0, 1
Style: HandleSm,  Helvetica,                    32, &H90FFFFFF, &H90FFFFFF, &H90000000, &H00000000,  0, 0, 0, 0, 100, 100, 2, 0, 1, 0, 0, 5, 0, 0, 0, 1
Style: FactLead,  Hiragino Maru Gothic ProN,    76, &H00FFFFFF, &H00FFFFFF, &H00081020, &H00000000, -1, 0, 0, 0, 100, 100, 2, 0, 1, 3, 0, 5, 0, 0, 0, 1
Style: FactBig,   Hiragino Sans W7,            210, &H009D6BFF, &H009D6BFF, &H00081020, &H00000000, -1, 0, 0, 0, 100, 100, 4, 0, 1, 6, 0, 5, 0, 0, 0, 1
Style: FactTail,  Hiragino Maru Gothic ProN,    68, &H00FFFFFF, &H00FFFFFF, &H00081020, &H00000000,  0, 0, 0, 0, 100, 100, 2, 0, 1, 3, 0, 5, 0, 0, 0, 1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

lines = []

# ── 上帯（全編固定・問いかけトーン） ──
lines.append(dialogue(
    0, 0.0, DURATION, "HeadMain", "歌 で 覚える",
    "{\\pos(540,180)\\fad(220,200)}"
))
lines.append(dialogue(
    0, 0.0, DURATION, "HeadAcc", "不規則変化動詞",
    "{\\pos(540,330)\\fad(260,200)}"
))
lines.append(dialogue(
    0, 0.0, DURATION, "HeadQ", "全部、覚えてる ?",
    "{\\pos(540,500)\\fad(340,200)}"
))
lines.append(dialogue(
    0, 0.0, DURATION, "HandleSm", "@TeacherTacosEnglish",
    "{\\pos(540,610)\\fad(420,200)}"
))

# ── 下帯（全編固定・豆知識トーン） ──
lines.append(dialogue(
    0, 0.0, DURATION, "FactLead", "歌 で 覚えると",
    "{\\pos(540,1390)\\fad(280,200)}"
))
lines.append(dialogue(
    0, 0.0, DURATION, "FactBig", "2 倍",
    "{\\pos(540,1605)\\fad(340,200)}"
))
lines.append(dialogue(
    0, 0.0, DURATION, "FactTail", "残りやすい らしいよ",
    "{\\pos(540,1810)\\fad(420,200)}"
))

ass_text = ass_header + "\n".join(lines) + "\n"
ASS_PATH.write_text(ass_text, encoding="utf-8")
print(f"ASS written: {ASS_PATH} ({len(lines)} dialogue lines)")

ass_path_escaped = str(ASS_PATH).replace(":", r"\:")
filter_complex = (
    f"color=c=0x0a1530:s={W}x{H}:r={FPS}:d={DURATION}[bg0];"
    f"[bg0]format=rgba,geq=r='10+34*Y/{H}':g='21+50*Y/{H}':b='48+82*Y/{H}':a=255,format=yuv420p[bg];"
    f"[0:v]scale={VID_W}:{VID_H}:flags=lanczos[vid];"
    f"[bg][vid]overlay=0:{VID_Y}[v0];"
    f"[v0]subtitles=filename={ass_path_escaped}[vout]"
)

cmd = [
    "ffmpeg", "-y",
    "-ss", str(SLICE_START), "-t", str(DURATION), "-i", str(SRC_VIDEO),
    "-filter_complex", filter_complex,
    "-map", "[vout]", "-map", "0:a",
    "-af", "afade=t=in:st=0:d=0.3,afade=t=out:st=27:d=3",
    "-r", str(FPS),
    "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "192k",
    "-t", str(DURATION),
    "-movflags", "+faststart",
    "-shortest",
    str(OUT_MP4),
]

print("Running ffmpeg...")
res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode != 0:
    print("FFMPEG STDERR (tail):", file=sys.stderr)
    print(res.stderr[-4000:], file=sys.stderr)
    sys.exit(res.returncode)

print(f"OK -> {OUT_MP4}")
print(f"size: {OUT_MP4.stat().st_size / 1024 / 1024:.1f} MB")
