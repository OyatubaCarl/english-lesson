"""WordTacos プロモ動画（約20秒フック）を作る。

実アプリの画面録画 (ending_video/recordings/*.webm, 440x780) を素材に、
3つの訴求ポイントをテロップで見せる縦型 1080x1920 の広告動画:
  ① 日本語に英語を埋め込む / 文脈で覚える
  ② 昇級試験ゲーム「タコス厨房ラッシュ」
  ③ 中1入門〜TOEIC高得点まで誰でも

BGM: vocab_sources/app_assets/theme.mp3 (52s) を先頭から使い、フェードで整える。

段階:
  1. 背景グラデーション PNG を生成
  2. ビートごとに ASS を書き、ffmpeg で個別セグメント mp4 をレンダリング
  3. concat + BGM を合成して最終 mp4
"""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJ = ROOT.parent
REC = PROJ / "ending_video" / "recordings"
ASSETS = PROJ / "vocab_sources" / "app_assets"
MASCOT = ASSETS / "mascot"  # 背景なし透過版
BGM = ROOT / "suno_bgm.mp3"   # Suno曲 (= wordtacos_ending と同一, 3:50)
BGM_START = 155.0             # 最終サビ付近の厚い区間から使う

WORK = ROOT / "_work"
WORK.mkdir(exist_ok=True)
BG = WORK / "bg.png"
OUT = ROOT / "wordtacos_promo_v2.mp4"

W, H = 1080, 1920
FPS = 30
FONTS = "/System/Library/Fonts"

# --- 録画の配置（縦型スマホ画面を中央に）---
REC_W = 720                      # 440->720
REC_H = round(720 * 780 / 440)   # = 1276
REC_X = (W - REC_W) // 2         # = 180
REC_Y = 210                      # 上に余白を残す

# ---------- ASS ヘルパ ----------
# 色は ASS の BGR 表記 (&H00BBGGRR)
C_WHITE = r"&H00FFFFFF"
C_CREAM = r"&H00C8E4F4"   # #F4E4C8
C_ORANGE = r"&H006AA2F4"  # #F4A26A アクセント
C_YELLOW = r"&H00B3E8FF"  # #FFE8B3
C_OUTLINE = r"&H00081020"  # #201008 濃茶

ASS_HEADER = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
ScaledBorderAndShadow: yes
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Lead,   Hiragino Sans W7, 64, {C_WHITE}, {C_OUTLINE}, &H80000000, -1, 0,0,0, 100,100, 1, 0, 1, 5, 3, 8, 70, 70, 120, 1
Style: Sub,    Hiragino Sans W6, 52, {C_CREAM},  {C_OUTLINE}, &H80000000,  0, 0,0,0, 100,100, 1, 0, 1, 4, 3, 2, 70, 70, 210, 1
Style: Big,    Hiragino Sans W8, 128,{C_WHITE}, {C_OUTLINE}, &H80000000, -1, 0,0,0, 100,100, 2, 0, 1, 6, 4, 5, 60, 60, 250, 1
Style: BigSub, Hiragino Sans W6, 50, {C_CREAM},  {C_OUTLINE}, &H80000000,  0, 0,0,0, 100,100, 1, 0, 1, 4, 3, 8, 60, 60, 1120, 1
Style: URL,    Hiragino Sans W7, 58, {C_YELLOW}, {C_OUTLINE}, &H80000000, -1, 0,0,0, 100,100, 1, 0, 1, 4, 3, 2, 60, 60, 360, 1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def t(sec: float) -> str:
    m = int(sec // 60)
    s = sec - m * 60
    return f"0:{m:02d}:{s:05.2f}"


def dlg(start: float, end: float, style: str, text: str) -> str:
    return f"Dialogue: 0,{t(start)},{t(end)},{style},,0,0,0,,{text}"


def orange(s: str) -> str:
    """キーワードをアクセント色に。"""
    return f"{{\\c{C_ORANGE}}}{s}{{\\c{C_WHITE}}}"


# ---------- ビート定義 ----------
# kind: "rec" (録画素材) / "cta"
# rec: src(webm名), ss(トリム開始), dur, lines[(start,end,style,text)]
BEATS = [
    dict(name="s1_title", kind="rec", src="stage_select.webm", ss=0.0, dur=3.0, lines=[
        (0.4, 3.0, "Sub", "{\\fad(400,300)}日本語に、" + orange("英語") + "を埋め込む。"),
    ]),
    dict(name="s2_embed", kind="rec", src="quiz_stage1_easy.webm", ss=4.0, dur=5.2, lines=[
        (0.2, 5.2, "Lead", "{\\fad(350,300)}日本語の文に、" + orange("英単語") + "をそっと。"),
        (1.6, 5.2, "Sub",  "{\\fad(350,300)}文脈ごと、やさしく覚える。"),
    ]),
    dict(name="s3_krtitle", kind="rec", src="kitchen_rush_mistake.webm", ss=1.0, dur=1.9, lines=[
        (0.2, 1.9, "Sub", "{\\fad(300,200)}昇級試験は、" + orange("ゲーム") + "。"),
    ]),
    dict(name="s4_krplay", kind="rec", src="kitchen_rush_unlock.webm", ss=7.0, dur=3.8, lines=[
        (0.2, 3.8, "Lead", "{\\fad(300,300)}タコス" + orange("厨房ラッシュ")),
        (1.2, 3.8, "Sub",  "{\\fad(300,300)}10連続正解で合格！"),
    ]),
    dict(name="s5_range", kind="rec", src="stage_select.webm", ss=2.9, dur=2.6, lines=[
        (0.2, 2.6, "Lead", "{\\fad(300,250)}中1入門 → " + orange("TOEIC") + "高得点まで"),
        (1.0, 2.6, "Sub",  "{\\fad(300,250)}誰でも、7000語を文脈で。"),
    ]),
    dict(name="s6_toeic", kind="rec", src="toeic_basic.webm", ss=8.4, dur=3.1, lines=[
        (0.2, 3.1, "Lead", "{\\fad(300,300)}TOEICも、この一問。"),
        (1.2, 3.1, "Sub",  "{\\fad(300,300)}company = " + orange("会社")),
    ]),
    dict(name="s7_cta", kind="cta", mascot="cheering.png", dur=2.8, lines=[
        (0.2, 2.8, "Big",    "{\\an5\\pos(540,1010)\\fad(350,200)}Word{\\c" + C_ORANGE + "}Tacos"),
        (0.6, 2.8, "BigSub", "{\\an5\\pos(540,1155)\\fad(350,200)}日本語で包む、英単語アプリ"),
        (0.9, 2.8, "URL",    "{\\an5\\pos(540,1610)\\fad(400,200)}words.teachertacos.com"),
    ]),
]


def make_bg() -> None:
    """暖色の濃いグラデーション背景 + 軽いビネット。"""
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-f", "lavfi", "-i",
        f"gradients=s={W}x{H}:c0=0x3A2416:c1=0x160B04:x0=540:y0=0:x1=540:y1={H}",
        "-frames:v", "1",
        "-vf", "vignette=PI/5",
        str(BG),
    ]
    subprocess.run(cmd, check=True)
    print(f"  ✓ bg.png")


def write_ass(beat: dict) -> Path:
    p = WORK / f"{beat['name']}.ass"
    lines = [ASS_HEADER]
    for (s, e, style, text) in beat["lines"]:
        lines.append(dlg(s, e, style, text))
    p.write_text("\n".join(lines), encoding="utf-8")
    return p


def render_beat(beat: dict) -> Path:
    ass = write_ass(beat)
    ass_safe = str(ass).replace(":", "\\:")
    out = WORK / f"{beat['name']}.mp4"
    dur = beat["dur"]

    if beat["kind"] == "rec":
        rec = REC / beat["src"]
        fc = (
            f"[1:v]scale={REC_W}:{REC_H},setpts=PTS-STARTPTS[rec];"
            f"[0:v][rec]overlay={REC_X}:{REC_Y}[bgv];"
            f"[bgv]subtitles='{ass_safe}':fontsdir={FONTS}[v]"
        )
        cmd = [
            "ffmpeg", "-y", "-v", "error",
            "-loop", "1", "-t", str(dur), "-i", str(BG),
            "-ss", str(beat["ss"]), "-t", str(dur), "-i", str(rec),
            "-filter_complex", fc,
            "-map", "[v]", "-t", str(dur),
            "-r", str(FPS), "-pix_fmt", "yuv420p",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            str(out),
        ]
    else:  # cta
        mascot = MASCOT / beat["mascot"]
        fc = (
            f"[1:v]format=rgba,scale=-1:560[mc];"
            f"[0:v][mc]overlay=(W-w)/2:270[bgv];"
            f"[bgv]subtitles='{ass_safe}':fontsdir={FONTS}[v]"
        )
        cmd = [
            "ffmpeg", "-y", "-v", "error",
            "-loop", "1", "-t", str(dur), "-i", str(BG),
            "-i", str(mascot),
            "-filter_complex", fc,
            "-map", "[v]", "-t", str(dur),
            "-r", str(FPS), "-pix_fmt", "yuv420p",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            str(out),
        ]
    subprocess.run(cmd, check=True)
    print(f"  ✓ {beat['name']}.mp4 ({dur}s)")
    return out


def build() -> None:
    print("背景生成…")
    make_bg()
    print("セグメント レンダリング…")
    segs = [render_beat(b) for b in BEATS]
    total = sum(b["dur"] for b in BEATS)
    print(f"合計 {total:.1f}s → concat + BGM…")

    inputs = []
    for s in segs:
        inputs += ["-i", str(s)]
    inputs += ["-i", str(BGM)]

    n = len(segs)
    concat_in = "".join(f"[{i}:v]" for i in range(n))
    a_idx = n
    fc = (
        f"{concat_in}concat=n={n}:v=1:a=0[v];"
        f"[{a_idx}:a]atrim={BGM_START}:{BGM_START + total},asetpts=PTS-STARTPTS,"
        f"afade=t=in:st=0:d=0.5,afade=t=out:st={total-1.2:.2f}:d=1.2[a]"
    )
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        *inputs,
        "-filter_complex", fc,
        "-map", "[v]", "-map", "[a]",
        "-t", f"{total:.2f}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
        "-movflags", "+faststart",
        str(OUT),
    ]
    subprocess.run(cmd, check=True)
    print(f"\n✓ {OUT}  ({total:.1f}s)")


if __name__ == "__main__":
    build()
