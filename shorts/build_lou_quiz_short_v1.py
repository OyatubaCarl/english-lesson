#!/usr/bin/env python3
"""ルー語クイズ Short v1 — 30秒・1080×1920・Teacher Tacos 登場版。

構成:
  0.0-2.5  フック「これ、読める？」(TT小=右下常駐)
  2.5-10.6 本文ナレ＋字幕（桜の美しさは ephemeral だ。…）
 10.6-12.9 問題ナレ「ephemeral の意味は？」
 12.9-19.9 4択＋カウントダウン 3→2→1
 19.9-21.4 正解 C「はかない」
 21.4-26.0 論文引用 (Mazur, Rzepka & Araki 2012 — Diglot Weave で初見 80%)
 26.0-30.0 サイト誘導「中高生の英単語、日本語混じりで全部覚えよう → @TeacherTacosEnglish」
           Teacher Tacos 中央寄り大で登場
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

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
_BGM_LIB_DIR = Path(
    "/Users/masaki/Documents/ClaudeCode/英語学習教材作成/shorts/assets/bgm_library"
)
_BGM_LIB_NAME = os.environ.get("BGM_LIB_NAME", "").strip()
_BGM_OVERRIDE = os.environ.get("BGM_OVERRIDE", "").strip()
if _BGM_LIB_NAME:
    BGM_SRC = _BGM_LIB_DIR / f"{_BGM_LIB_NAME}.mp3"
elif _BGM_OVERRIDE:
    BGM_SRC = Path(_BGM_OVERRIDE)
else:
    BGM_SRC = _BGM_DEFAULT
# default タコス曲は派手なので 0.07、ライブラリ/Suno曲は 0.20。env で上書き可。
_is_default_bgm = (BGM_SRC == _BGM_DEFAULT)
BGM_VOLUME = float(os.environ.get("BGM_VOLUME", "0.07" if _is_default_bgm else "0.20"))
SUFFIX_BGM = os.environ.get(
    "SUFFIX_BGM",
    f"_{_BGM_LIB_NAME}" if _BGM_LIB_NAME else "",
)
NARR_BODY = NARR_DIR / "narr_body.wav"
NARR_QUIZ = NARR_DIR / "narr_quiz.wav"
DURS_JSON = NARR_DIR / "durations.json"

# --no-paper フラグ: 論文引用ブロックをスキップしてCTAをじっくり見せる版
NOPAPER = "--no-paper" in sys.argv
SUFFIX = ("_nopaper" if NOPAPER else "") + SUFFIX_BGM
OUT_MP4 = WORK / f"lou_quiz_short_v1{SUFFIX}.mp4"
ASS_PATH = Path(f"/tmp/lou_quiz_v1{SUFFIX}.ass")

W, H, FPS = 1080, 1920, 30
DUR = 30.0  # 全体尺(秒)

# ============== タイムライン定数 ==============
# 「これ、読める？」は上部に常時表示。本文ナレは 0 秒から開始。
T_HOOK_LABEL_IN = 0.0
T_HOOK_LABEL_OUT = 12.9     # 問題終わりまで上部に残す（4択開始で消える）

T_BODY_START = 0.0          # ナレ本文＝最初から再生
T_BODY_END = 8.1            # 7.57s + 余白

T_QUIZ_START = 8.6
T_QUIZ_END = 10.6           # 1.86s + 余白

T_CHOICE_START = 11.0
T_COUNTDOWN_START = 14.7    # カウントダウン3秒分
T_COUNTDOWN_END = 17.9

T_ANS_START = 17.9
if NOPAPER:
    # 論文区間(4.4秒)をCTAに回す。正解余韻を少し伸ばす。
    T_ANS_END = 21.6
    T_PAPER_START = T_PAPER_END = -1.0   # 使用しないセンチネル
    T_CTA_START = 21.6
else:
    T_ANS_END = 19.6
    T_PAPER_START = 19.6
    T_PAPER_END = 24.0
    T_CTA_START = 24.0
T_CTA_END = 30.0

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
Style: HookW,    Hiragino Sans W7,             104, &H00FFFFFF, &H00FFFFFF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 2, 0, 1, 8, 5, 5, 0, 0, 0, 1
Style: HookY,    Hiragino Sans W7,              74, &H003DD9FF, &H003DD9FF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 2, 0, 1, 6, 4, 5, 0, 0, 0, 1
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
Style: PaperH,   Hiragino Sans W7,              54, &H003DD9FF, &H003DD9FF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 2, 0, 1, 5, 3, 5, 60, 60, 0, 1
Style: PaperBody,Hiragino Maru Gothic ProN,     46, &H00FFFFFF, &H00FFFFFF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 1, 0, 1, 5, 3, 5, 80, 80, 0, 1
Style: PaperCite,Helvetica,                     34, &HB0FFFFFF, &HB0FFFFFF, &H00000000, &H00000000,  0, 1, 0, 0, 100, 100, 1, 0, 1, 3, 2, 5, 80, 80, 0, 1
Style: CtaBig,   Hiragino Sans W7,              74, &H00FFFFFF, &H00FFFFFF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 1, 0, 1, 6, 4, 5, 60, 60, 0, 1
Style: CtaHandle,Helvetica,                     60, &H003DD9FF, &H003DD9FF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 2, 0, 1, 6, 4, 5, 0, 0, 0, 1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

# ============== ASS Dialogue 構築 ==============
def build_lines() -> list:
    lines = []

    # 全編 上部ハンドル（薄く）
    lines.append(D(0, 0.0, DUR, "Handle", "@TeacherTacosEnglish",
                   "{\\pos(540,90)\\fad(300,300)}"))

    # 「これ、読める ?」を上部に常時表示（4択開始で消える）
    lines.append(D(0, T_HOOK_LABEL_IN, T_HOOK_LABEL_OUT, "HookLabel",
                   "これ、読める ?",
                   "{\\pos(540,200)\\fad(220,300)}"))

    # 2.7-10.6 本文（赤強調なし→英単語は別色で）
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

    # 11.0-12.9 問題
    lines.append(D(0, T_QUIZ_START, T_QUIZ_END, "QuizEN", "ephemeral",
                   "{\\pos(540,860)\\fad(180,150)}"))
    lines.append(D(0, T_QUIZ_START + 0.2, T_QUIZ_END, "QuizQ",
                   "の 意味は ?",
                   "{\\pos(540,1010)\\fad(220,150)}"))

    # 13.0-16.7 4択（横並び 2×2）- カウントダウンと被らないよう上に
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

    # 上部ラベル「文脈で答えよう」
    lines.append(D(0, T_CHOICE_START, T_COUNTDOWN_END, "QuizQ",
                   "文脈で 答えよう",
                   "{\\pos(540,820)\\fad(220,150)\\fs48\\c&HC0FFFFFF&}"))

    # 16.7-19.9 カウントダウン 3-2-1
    for i, num in enumerate(["3", "2", "1"]):
        s = T_COUNTDOWN_START + i * 1.0
        e = s + 1.0
        lines.append(D(0, s, e, "Count", num,
                       "{\\pos(540,1450)\\fad(120,180)\\t(\\fscx115\\fscy115)}"))

    # 19.9-21.6 正解
    lines.append(D(0, T_ANS_START, T_ANS_END, "Ans", "C",
                   "{\\pos(380,960)\\fad(120,200)\\t(\\fscx125\\fscy125)}"))
    lines.append(D(0, T_ANS_START + 0.15, T_ANS_END, "ChoiceOK",
                   "は か な い",
                   "{\\pos(720,960)\\fad(150,200)}"))
    lines.append(D(0, T_ANS_START + 0.4, T_ANS_END, "PaperBody",
                   "文脈で とれた人、もう 脳に残ってる。",
                   "{\\pos(540,1180)\\fad(220,200)\\fs44}"))

    # 19.6-24.0 論文引用（NOPAPER モードでは丸ごとスキップ）
    if not NOPAPER:
        lines.append(D(0, T_PAPER_START, T_PAPER_END, "PaperH",
                       "▷   研究では",
                       "{\\pos(540,720)\\fad(220,180)\\fs54}"))
        lines.append(D(0, T_PAPER_START + 0.3, T_PAPER_END, "PaperBody",
                       "日本語の 中に 英単語を 混ぜる",
                       "{\\pos(540,860)\\fad(220,180)}"))
        lines.append(D(0, T_PAPER_START + 0.6, T_PAPER_END, "PaperBody",
                       "“ Diglot Weave ”法 では、",
                       "{\\pos(540,940)\\fad(220,180)}"))
        lines.append(D(0, T_PAPER_START + 1.0, T_PAPER_END, "PaperBody",
                       "初見の 単語でも",
                       "{\\pos(540,1040)\\fad(220,180)}"))
        lines.append(D(0, T_PAPER_START + 1.3, T_PAPER_END, "PaperH",
                       "約  80 %",
                       "{\\pos(540,1190)\\fad(220,180)\\fs120\\c&H00FF66&\\t(\\fscx115\\fscy115)}"))
        lines.append(D(0, T_PAPER_START + 1.6, T_PAPER_END, "PaperBody",
                       "が 文脈から 意味を 当てた。",
                       "{\\pos(540,1340)\\fad(220,180)}"))
        lines.append(D(0, T_PAPER_START + 2.0, T_PAPER_END, "PaperCite",
                       "Mazur, Rzepka & Araki, 2012 ( 北海道大学 )",
                       "{\\pos(540,1450)\\fad(280,180)}"))

    # 26.0-30.0 サイト誘導（「では」を強調＝中高で習う英単語を日本語混じりで学べる）
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
    print(f"ASS -> {ASS_PATH}")


# ============== ffmpeg 合成 ==============
def build_video() -> None:
    if not BG_PNG.exists():
        sys.exit(f"背景画像なし: {BG_PNG}（Codex生成待ち）")
    if not TT_PNG.exists():
        sys.exit(f"Teacher Tacos なし: {TT_PNG}")
    if not (NARR_BODY.exists() and NARR_QUIZ.exists()):
        sys.exit("ナレ wav が未生成")
    if not BGM_SRC.exists():
        sys.exit(f"BGM なし: {BGM_SRC}")
    if not DURS_JSON.exists():
        sys.exit(f"durations.json なし: {DURS_JSON}")

    body_dur = json.loads(DURS_JSON.read_text())["body"]["duration_sec"]
    quiz_dur = json.loads(DURS_JSON.read_text())["quiz"]["duration_sec"]

    # 各 wav の遅延(ms): body=T_BODY_START, quiz=T_QUIZ_START
    body_delay = int(T_BODY_START * 1000)
    quiz_delay = int(T_QUIZ_START * 1000)

    ass_escaped = str(ASS_PATH).replace(":", r"\:")

    # フィルタチェーン:
    #   [bg]: 桜背景を loop して 30秒・zoompan で微ズーム
    #   [tt_s]: TT 小(右下、0-26s)
    #   [tt_b]: TT 大(中央寄り、26-30s)
    #   音声:
    #     [bgm]: タコス曲 0-30s -28dB ＋ fadeIn/Out
    #     [body]: 本文ナレ -> T_BODY_START 遅延
    #     [quiz]: 問題ナレ -> T_QUIZ_START 遅延
    #     amix で合成
    filter_complex = (
        # 背景: loop=∞ で 30秒、フレーム整え、軽いズーム
        f"[0:v]loop=loop=-1:size=1:start=0,trim=duration={DUR},setpts=PTS-STARTPTS,"
        f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},"
        f"zoompan=z='min(zoom+0.0006,1.10)':d=1:s={W}x{H}:fps={FPS}[bg];"
        # TT 小(右下、260px幅): 0-26秒のみ。trimで完全に時間軸を切る
        f"[1:v]scale=260:-1,fps={FPS},trim=duration={T_CTA_START},setpts=PTS-STARTPTS[tt_s];"
        # TT 大(360px幅): CTA区間のみ。文字(y=720-980)とハンドル(y=1640)の間に配置
        f"[1:v]scale=360:-1,fps={FPS},trim=duration={DUR-T_CTA_START},"
        f"setpts=PTS-STARTPTS+{T_CTA_START}/TB[tt_b];"
        # 合成: bg + tt_s(右下小,0-24s) + tt_b(中央,24-30s 文字下) + ASS字幕
        f"[bg][tt_s]overlay=x=W-w-40:y=H-h-180:shortest=0:eof_action=pass[v1];"
        f"[v1][tt_b]overlay=x=(W-w)/2:y=1180:shortest=0:eof_action=pass[v2];"
        f"[v2]subtitles=filename={ass_escaped}[vout];"
        # 音声
        f"[2:a]atrim=0:{DUR},asetpts=PTS-STARTPTS,volume={BGM_VOLUME},"
        f"afade=t=in:st=0:d=0.6,afade=t=out:st={DUR-1.5}:d=1.5[bgm];"
        f"[3:a]adelay={body_delay}|{body_delay},apad[body];"
        f"[4:a]adelay={quiz_delay}|{quiz_delay},apad[quiz];"
        f"[bgm][body][quiz]amix=inputs=3:duration=first:dropout_transition=0:"
        f"normalize=0[aout]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(BG_PNG),     # 0: background
        "-loop", "1", "-i", str(TT_PNG),     # 1: teacher tacos
        "-stream_loop", "-1", "-i", str(BGM_SRC),  # 2: bgm (loop if shorter than DUR)
        "-i", str(NARR_BODY),                # 3: body narration
        "-i", str(NARR_QUIZ),                # 4: quiz narration
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", "[aout]",
        "-r", str(FPS), "-t", str(DUR),
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(OUT_MP4),
    ]
    print("Running ffmpeg…")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(res.stderr[-4500:], file=sys.stderr)
        sys.exit(res.returncode)
    size_mb = OUT_MP4.stat().st_size / 1024 / 1024
    print(f"OK -> {OUT_MP4}  ({size_mb:.1f} MB)")


def extract_frames() -> None:
    """確認用フレームを5枚抽出"""
    for sec in [1.5, 6.0, 13.0, 18.0, 22.5, 28.0]:
        out = WORK / f"lou_v1_frame_{sec:.1f}.jpg"
        cmd = ["ffmpeg", "-y", "-ss", str(sec), "-i", str(OUT_MP4),
               "-frames:v", "1", "-q:v", "3", str(out)]
        subprocess.run(cmd, capture_output=True, text=True)
        print(f"  frame -> {out.name}")


if __name__ == "__main__":
    write_ass()
    build_video()
    extract_frames()
