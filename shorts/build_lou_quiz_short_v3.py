#!/usr/bin/env python3
"""ルー語クイズShort v3 — quizzes.json 駆動の汎用ビルダー。

usage:
  python3 build_lou_quiz_short_v3.py --quiz 02_resilient
  python3 build_lou_quiz_short_v3.py --quiz 03_ubiquitous

v1論文あり版の構成(タコスBGM、Teacher Tacos登場、論文引用、CTA)を踏襲し、
題材英単語/文章/4択/正解位置を quizzes.json から動的に組み立てる。
"""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

WORK = Path("/Users/masaki/Documents/ClaudeCode/英語学習教材作成/shorts")
ASSETS = WORK / "assets"
NARR_ROOT = WORK / "narration"
QUIZZES_JSON = WORK / "quizzes.json"

TT_PNG = Path(
    "/Users/masaki/Documents/ClaudeCode/FunnicsIsland/characters/T_teacher_tacos/single.png"
)
BGM_DEFAULT = Path(
    "/Users/masaki/Documents/ClaudeCode/FunnicsIsland/songs/21_tacos_fiesta_dance/audio/tacos_fiesta_suno_SX3pVWTGGFxEsIHW.mp3"
)
# BGM 上書き(任意): BGM_LIB_NAME (bgm_library/{name}.mp3) > BGM_OVERRIDE(絶対パス) > default
_BGM_LIB_DIR = ASSETS / "bgm_library"
_BGM_LIB_NAME = os.environ.get("BGM_LIB_NAME", "").strip()
_BGM_OVERRIDE = os.environ.get("BGM_OVERRIDE", "").strip()
if _BGM_LIB_NAME:
    BGM_SRC = _BGM_LIB_DIR / f"{_BGM_LIB_NAME}.mp3"
elif _BGM_OVERRIDE:
    BGM_SRC = Path(_BGM_OVERRIDE)
else:
    BGM_SRC = BGM_DEFAULT
BGM_VOLUME = float(os.environ.get("BGM_VOLUME", "0.07" if BGM_SRC == BGM_DEFAULT else "0.20"))

W, H, FPS = 1080, 1920, 30
DUR = 30.0

# ============== タイムライン(v1論文あり版と同じ) ==============
T_HOOK_LABEL_IN = 0.0
T_HOOK_LABEL_OUT = 12.9
T_BODY_START = 0.0
T_BODY_END = 8.1
T_QUIZ_START = 8.6
T_QUIZ_END = 10.6
T_CHOICE_START = 11.0
T_COUNTDOWN_START = 14.7
T_COUNTDOWN_END = 17.9
T_ANS_START = 17.9
T_ANS_END = 19.6
T_PAPER_START = 19.6
T_PAPER_END = 24.0
T_CTA_START = 24.0
T_CTA_END = DUR

# 本文字幕の表示開始間隔(秒/行)
BODY_LINE_INTERVAL = 1.2


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
Style: HookLabel,Hiragino Sans W7,              64, &H003DD9FF, &H003DD9FF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 2, 0, 1, 6, 4, 5, 0, 0, 0, 1
Style: Handle,   Helvetica,                     32, &HC0FFFFFF, &HC0FFFFFF, &H00000000, &H00000000,  0, 0, 0, 0, 100, 100, 2, 0, 1, 2, 1, 5, 0, 0, 0, 1
Style: BodyJP,   Hiragino Maru Gothic ProN,     58, &H00FFFFFF, &H00FFFFFF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 1, 0, 1, 5, 3, 5, 60, 60, 0, 1
Style: BodyEN,   Helvetica,                     78, &H006B7CFF, &H006B7CFF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 2, 0, 1, 6, 4, 5, 60, 60, 0, 1
Style: QuizQ,    Hiragino Sans W7,              74, &H00FFFFFF, &H00FFFFFF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 2, 0, 1, 6, 4, 5, 60, 60, 0, 1
Style: QuizEN,   Helvetica,                     86, &H006B7CFF, &H006B7CFF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 2, 0, 1, 6, 4, 5, 60, 60, 0, 1
Style: Choice,   Hiragino Sans W7,              60, &H00FFFFFF, &H00FFFFFF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 1, 0, 1, 5, 3, 5, 80, 80, 0, 1
Style: ChoiceOK, Hiragino Sans W7,              66, &H0066FF55, &H0066FF55, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 1, 0, 1, 6, 4, 5, 80, 80, 0, 1
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


def build_lines(quiz: dict) -> list:
    word = quiz["word"]
    body_subs = quiz["body_subtitles"]
    choices = quiz["choices"]
    correct = quiz["correct_index"]
    lines = []

    # 上部ハンドル
    lines.append(D(0, 0.0, DUR, "Handle", "@TeacherTacosEnglish",
                   "{\\pos(540,90)\\fad(300,300)}"))

    # 「これ、読める ?」上部に常時(4択開始で消える)
    lines.append(D(0, T_HOOK_LABEL_IN, T_HOOK_LABEL_OUT, "HookLabel",
                   "これ、読める ?",
                   "{\\pos(540,200)\\fad(220,300)}"))

    # 本文字幕(行ごとに段階的にfade in)
    for i, sub in enumerate(body_subs):
        start = T_BODY_START + i * BODY_LINE_INTERVAL
        style = sub.get("style", "BodyJP")
        y = sub["y"]
        text = sub["text"]
        lines.append(D(0, start, T_BODY_END, style, text,
                       f"{{\\pos(540,{y})\\fad(220,180)}}"))

    # 問題(英単語 + "の意味は ?")
    lines.append(D(0, T_QUIZ_START, T_QUIZ_END, "QuizEN", word,
                   "{\\pos(540,860)\\fad(180,150)}"))
    lines.append(D(0, T_QUIZ_START + 0.2, T_QUIZ_END, "QuizQ",
                   "の 意味は ?",
                   "{\\pos(540,1010)\\fad(220,150)}"))

    # 4択 (A/B/C/D を 2x2)
    cols = [270, 810]
    rows = [920, 1110]
    for i, choice in enumerate(choices):
        letter = "ABCD"[i]
        cx = cols[i % 2]
        cy = rows[i // 2]
        lines.append(D(0, T_CHOICE_START + i * 0.2, T_COUNTDOWN_END, "Choice",
                       f"{letter}  {choice}",
                       f"{{\\pos({cx},{cy})\\fad(200,150)}}"))
    lines.append(D(0, T_CHOICE_START, T_COUNTDOWN_END, "QuizQ",
                   "文脈で 答えよう",
                   "{\\pos(540,820)\\fad(220,150)\\fs48\\c&HC0FFFFFF&}"))

    # カウントダウン 3-2-1
    for i, num in enumerate(["3", "2", "1"]):
        s = T_COUNTDOWN_START + i * 1.0
        e = s + 1.0
        lines.append(D(0, s, e, "Count", num,
                       "{\\pos(540,1500)\\fad(120,180)\\t(\\fscx115\\fscy115)}"))

    # 正解
    correct_letter = "ABCD"[correct]
    correct_answer = choices[correct]
    lines.append(D(0, T_ANS_START, T_ANS_END, "Ans", correct_letter,
                   "{\\pos(380,960)\\fad(120,200)\\t(\\fscx125\\fscy125)}"))
    lines.append(D(0, T_ANS_START + 0.15, T_ANS_END, "ChoiceOK",
                   correct_answer,
                   "{\\pos(720,960)\\fad(150,200)}"))
    lines.append(D(0, T_ANS_START + 0.4, T_ANS_END, "PaperBody",
                   "文脈で とれた人、もう 脳に残ってる。",
                   "{\\pos(540,1180)\\fad(220,200)\\fs44}"))

    # 論文引用
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


def build_video(quiz: dict, narr_body: Path, narr_quiz: Path, bg_png: Path,
                ass_path: Path, out_mp4: Path) -> None:
    body_delay = int(T_BODY_START * 1000)
    quiz_delay = int(T_QUIZ_START * 1000)
    ass_escaped = str(ass_path).replace(":", r"\:")

    filter_complex = (
        f"[0:v]loop=loop=-1:size=1:start=0,trim=duration={DUR},setpts=PTS-STARTPTS,"
        f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},"
        f"zoompan=z='min(zoom+0.0006,1.10)':d=1:s={W}x{H}:fps={FPS}[bg];"
        f"[1:v]scale=260:-1,fps={FPS},trim=duration={T_CTA_START},setpts=PTS-STARTPTS[tt_s];"
        f"[1:v]scale=360:-1,fps={FPS},trim=duration={DUR-T_CTA_START},"
        f"setpts=PTS-STARTPTS+{T_CTA_START}/TB[tt_b];"
        f"[bg][tt_s]overlay=x=W-w-40:y=H-h-180:shortest=0:eof_action=pass[v1];"
        f"[v1][tt_b]overlay=x=(W-w)/2:y=1180:shortest=0:eof_action=pass[v2];"
        f"[v2]subtitles=filename={ass_escaped}[vout];"
        f"[2:a]atrim=0:{DUR},asetpts=PTS-STARTPTS,volume={BGM_VOLUME},"
        f"afade=t=in:st=0:d=0.6,afade=t=out:st={DUR-1.5}:d=1.5[bgm];"
        f"[3:a]adelay={body_delay}|{body_delay},apad[body];"
        f"[4:a]adelay={quiz_delay}|{quiz_delay},apad[quiz];"
        f"[bgm][body][quiz]amix=inputs=3:duration=first:dropout_transition=0:normalize=0[aout]"
    )
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(bg_png),
        "-loop", "1", "-i", str(TT_PNG),
        "-stream_loop", "-1", "-i", str(BGM_SRC),
        "-i", str(narr_body),
        "-i", str(narr_quiz),
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", "[aout]",
        "-r", str(FPS), "-t", str(DUR),
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
        str(out_mp4),
    ]
    print(f"Running ffmpeg → {out_mp4.name}")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(res.stderr[-3000:], file=sys.stderr)
        sys.exit(res.returncode)
    print(f"OK -> {out_mp4}  ({out_mp4.stat().st_size/1024/1024:.1f} MB)")


def run_one(quiz_id: str) -> Path:
    quizzes = json.loads(QUIZZES_JSON.read_text(encoding="utf-8"))
    quiz = next((q for q in quizzes if q["id"] == quiz_id), None)
    if not quiz:
        raise SystemExit(f"quiz not found: {quiz_id}")
    if "body_subtitles" not in quiz:
        raise SystemExit(f"{quiz_id} has no body_subtitles (likely 01_ephemeral reference)")

    narr_dir = NARR_ROOT / quiz_id
    narr_body = narr_dir / "narr_body.wav"
    narr_quiz = narr_dir / "narr_quiz.wav"
    bg_png = ASSETS / "bg_quizzes" / quiz["bg_filename"]

    for path, label in [(narr_body, "narr_body"), (narr_quiz, "narr_quiz"),
                         (bg_png, "bg_png"), (TT_PNG, "tt"), (BGM_SRC, "bgm")]:
        if not path.exists():
            raise SystemExit(f"missing {label}: {path}")

    ass_path = Path(f"/tmp/lou_quiz_v3_{quiz_id}.ass")
    out_mp4 = WORK / f"lou_quiz_short_v3_{quiz_id}.mp4"

    body = ASS_HEADER + "\n".join(build_lines(quiz)) + "\n"
    ass_path.write_text(body, encoding="utf-8")
    print(f"ASS -> {ass_path}")

    build_video(quiz, narr_body, narr_quiz, bg_png, ass_path, out_mp4)
    return out_mp4


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quiz", required=True, help="quiz id (例: 02_resilient)")
    args = parser.parse_args()
    run_one(args.quiz)


if __name__ == "__main__":
    main()
