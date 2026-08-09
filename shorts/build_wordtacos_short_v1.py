#!/usr/bin/env python3
"""ルー語クイズShort v4 — 難単語版用。
冒頭イントロ + 論文バリエーション動的 + v3 と同じパイプライン。

usage:
  python3 build_lou_quiz_short_v4.py --quiz 02_resilient
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

# v4 タイムライン: 0-2.6 イントロ→…→24.8 paper まで既存通り
T_INTRO_IN = 0.0
T_INTRO_OUT = 2.6
T_BODY_START = 2.8
T_BODY_END = 10.4
T_QUIZ_START = 10.6
T_QUIZ_END = 12.4
T_HOOK_LABEL_IN = T_BODY_START
T_HOOK_LABEL_OUT = T_QUIZ_END
T_CHOICE_START = 12.6
T_COUNTDOWN_START = 15.6
T_COUNTDOWN_END = 18.6
T_ANS_START = 18.6
T_ANS_END = 20.2
T_PAPER_START = 20.2
T_PAPER_END = 24.8

# 24.8〜 拡張 CTA: 通常学習モード → 昇級試験 → URL の 3パート
T_STUDY_START = 24.8
T_STUDY_END = 34.0     # study.wav 9.3s
T_PROMO_START = 34.0
T_PROMO_END = 41.5     # promo.wav 7.0s
T_URL_START = 41.5
T_URL_END = 46.5       # url.wav 4.65s
T_CTA_START = T_STUDY_START   # ←旧変数 (TT 大きさ切替用)
T_CTA_END = T_URL_END
DUR = T_URL_END

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
Style: IntroHeader,Hiragino Sans W7,            72, &H003DD9FF, &H003DD9FF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 4, 0, 1, 8, 5, 5, 0, 0, 0, 1
Style: IntroWord,  Helvetica,                  144, &H00FFFFFF, &H00FFFFFF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 4, 0, 1, 10, 6, 5, 0, 0, 0, 1
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
Style: PaperEmph,Hiragino Sans W7,              88, &H0066FF55, &H0066FF55, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 2, 0, 1, 7, 4, 5, 60, 60, 0, 1
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
    intro = quiz.get("intro_overlay", {})
    pvar = quiz.get("paper_variant", {})
    lines = []

    # 上部ハンドル
    lines.append(D(0, 0.0, DUR, "Handle", "@TeacherTacosEnglish",
                   "{\\pos(540,90)\\fad(300,300)}"))

    # 0.0-2.6 イントロ
    if intro:
        header = intro.get("header", "超 難単語 が 一発で 覚えられる 裏技 !")
        word_y = intro.get("word_position_y", 1100)
        lines.append(D(0, T_INTRO_IN, T_INTRO_OUT, "IntroHeader",
                       header,
                       "{\\pos(540,820)\\fad(220,250)\\t(\\fscx108\\fscy108)}"))
        lines.append(D(0, T_INTRO_IN + 0.4, T_INTRO_OUT, "IntroWord",
                       word,
                       f"{{\\pos(540,{word_y})\\fad(280,250)\\t(\\fscx112\\fscy112)}}"))

    # 「これ、読める ?」上部に常時(4択開始で消える)
    lines.append(D(0, T_HOOK_LABEL_IN, T_HOOK_LABEL_OUT, "HookLabel",
                   "これ、読める ?",
                   "{\\pos(540,180)\\fad(220,300)}"))

    # 本文/問題/4択は WordTacos のクイズカード画像で表示 (filter_complex で overlay)
    # ASS では補助テキストのみ

    # 「文脈で 答えよう」 ヒント (4択期間中、カード上に重ねず下に小さく)
    lines.append(D(0, T_CHOICE_START, T_COUNTDOWN_END, "QuizQ",
                   "文脈で 答えよう",
                   "{\\pos(540,1740)\\fad(220,150)\\fs44\\c&H6BE0FF&}"))

    # カウントダウン 3-2-1 (カード下に大型表示)
    for i, num in enumerate(["3", "2", "1"]):
        s = T_COUNTDOWN_START + i * 1.0
        e = s + 1.0
        lines.append(D(0, s, e, "Count", num,
                       "{\\pos(540,1820)\\fad(120,180)\\t(\\fscx115\\fscy115)\\fs140}"))

    # 正解の補足: 「文脈が あれば、自然と 身につく 。」 (カードの下)
    lines.append(D(0, T_ANS_START + 0.4, T_ANS_END, "PaperBody",
                   "文脈が あれば、自然と 身につく 。",
                   "{\\pos(540,1780)\\fad(220,200)\\fs48\\c&H66FF55&}"))

    # 論文セクション (paper_variant から動的生成)
    if pvar:
        ph = pvar.get("header", "▷  研究では")
        lines.append(D(0, T_PAPER_START, T_PAPER_END, "PaperH",
                       ph,
                       "{\\pos(540,720)\\fad(220,180)\\fs54}"))
        for i, ln in enumerate(pvar.get("lines", [])):
            text = ln["text"]
            y = ln["y"]
            start = T_PAPER_START + 0.3 + i * 0.3
            if ln.get("emphasis"):
                fs = ln.get("fs", 90)
                color = ln.get("color", "")
                color_tag = f"\\c{color}" if color else ""
                lines.append(D(0, start, T_PAPER_END, "PaperEmph",
                               text,
                               f"{{\\pos(540,{y})\\fad(220,180)\\fs{fs}{color_tag}\\t(\\fscx110\\fscy110)}}"))
            else:
                lines.append(D(0, start, T_PAPER_END, "PaperBody",
                               text,
                               f"{{\\pos(540,{y})\\fad(220,180)}}"))
        cite = pvar.get("cite", "")
        if cite:
            lines.append(D(0, T_PAPER_START + 2.0, T_PAPER_END, "PaperCite",
                           cite,
                           "{\\pos(540,1450)\\fad(280,180)}"))

    # === 拡張 CTA: 3パート (通常学習モード → 昇級試験 → URL) ===

    # PART 1: 通常学習モード
    lines.append(D(0, T_STUDY_START, T_STUDY_END - 0.3, "PaperH",
                   "▷  通常の 学習モード",
                   "{\\pos(540,200)\\fad(300,250)\\fs64\\c&H3DD9FF&}"))
    lines.append(D(0, T_STUDY_START + 0.5, T_STUDY_END - 0.3, "PaperBody",
                   "日本語の文に 英単語を 埋め込んで 4択で 答える",
                   "{\\pos(540,1700)\\fad(300,250)\\fs44}"))
    lines.append(D(0, T_STUDY_START + 5.5, T_STUDY_END - 0.3, "PaperBody",
                   "中学から 大学受験まで 7000語",
                   "{\\pos(540,1780)\\fad(300,250)\\fs44\\c&H6BE0FF&}"))

    # PART 2: 昇級試験は ミニゲーム
    lines.append(D(0, T_PROMO_START, T_PROMO_END - 0.3, "PaperH",
                   "▷  昇級試験は ミニゲーム",
                   "{\\pos(540,200)\\fad(300,250)\\fs64\\c&H3DD9FF&}"))
    lines.append(D(0, T_PROMO_START + 0.5, T_PROMO_END - 0.3, "PaperBody",
                   "工房ラッシュで タコス を 作ろう",
                   "{\\pos(540,1700)\\fad(300,250)\\fs44}"))
    lines.append(D(0, T_PROMO_START + 4.0, T_PROMO_END - 0.3, "PaperBody",
                   "10連続正解で 次の レッスン 解放 !",
                   "{\\pos(540,1780)\\fad(300,250)\\fs44\\c&H6BE0FF&}"))

    # PART 3: URL CTA
    lines.append(D(0, T_URL_START, T_URL_END, "CtaBig",
                   "今すぐ 無料で。",
                   "{\\pos(540,720)\\fad(280,250)}"))
    lines.append(D(0, T_URL_START + 0.6, T_URL_END, "CtaBig",
                   "ブラウザ だけで OK。",
                   "{\\pos(540,860)\\fad(280,250)}"))
    lines.append(D(0, T_URL_START + 1.6, T_URL_END, "CtaHandle",
                   "→  words.teachertacos.com",
                   "{\\pos(540,1300)\\fad(280,300)\\fs64\\c&H3DD9FF&\\t(\\fscx108\\fscy108)}"))

    return lines


def build_video(quiz: dict, narr_body: Path, narr_quiz: Path, bg_png: Path,
                ass_path: Path, out_mp4: Path,
                card_default: Path, card_answered: Path,
                study_rec: Path, promo_rec: Path,
                narr_study: Path, narr_promo: Path, narr_url: Path) -> None:
    body_delay = int(T_BODY_START * 1000)
    quiz_delay = int(T_QUIZ_START * 1000)
    ass_escaped = str(ass_path).replace(":", r"\:")

    CARD_IN  = T_BODY_START
    CARD_OUT = T_ANS_START
    ANS_OUT  = T_ANS_END
    CARD_Y = 320
    FADE = 0.3

    # クリップ配置 (Kitchen Rush 同様、中央 720x1276)
    CLIP_W, CLIP_H = 720, 1276
    CLIP_X = (W - CLIP_W) // 2  # 180
    CLIP_Y = 320

    # 録画から切り出す区間 (study 9.5s, promo 7.0s)
    STUDY_IN, STUDY_OUT = 3.5, 13.0      # 通常学習 録画 (440x900)
    PROMO_IN, PROMO_OUT = 30.0, 37.0     # 昇級試験 録画 (440x780)

    filter_complex = (
        # 背景
        f"[0:v]loop=loop=-1:size=1:start=0,trim=duration={DUR},setpts=PTS-STARTPTS,"
        f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},"
        f"zoompan=z='min(zoom+0.0006,1.10)':d=1:s={W}x{H}:fps={FPS},"
        f"eq=brightness=-0.1:saturation=1.05[bg];"
        # ティーチャータコス (常時 corner、CTA以降は表示しない=クリップに集中)
        f"[1:v]scale=240:-1,fps={FPS},trim=duration={T_STUDY_START},setpts=PTS-STARTPTS[tt_s];"
        # クイズカード
        f"[2:v]loop=loop=-1:size=1:start=0,trim=duration={DUR},setpts=PTS-STARTPTS,"
        f"scale=1080:1300,format=rgba,"
        f"fade=t=in:st={CARD_IN}:d={FADE}:alpha=1,"
        f"fade=t=out:st={CARD_OUT-FADE}:d={FADE}:alpha=1[card_d];"
        f"[3:v]loop=loop=-1:size=1:start=0,trim=duration={DUR},setpts=PTS-STARTPTS,"
        f"scale=1080:1300,format=rgba,"
        f"fade=t=in:st={CARD_OUT}:d=0.2:alpha=1,"
        f"fade=t=out:st={ANS_OUT-0.2}:d=0.2:alpha=1[card_a];"
        # 通常学習 録画 (440x900 → 720x1276 にクロップしてスケール)
        f"[4:v]trim=start={STUDY_IN}:end={STUDY_OUT},setpts=PTS-STARTPTS,fps={FPS},"
        f"scale={CLIP_W}:-2,crop={CLIP_W}:{CLIP_H}:0:0,"
        f"setpts=PTS+{T_STUDY_START}/TB[study];"
        # 昇級試験 録画 (440x780 → 720x1276 にスケール)
        f"[5:v]trim=start={PROMO_IN}:end={PROMO_OUT},setpts=PTS-STARTPTS,fps={FPS},"
        f"scale={CLIP_W}:{CLIP_H},"
        f"setpts=PTS+{T_PROMO_START}/TB[promo];"
        # 合成
        f"[bg][tt_s]overlay=x=W-w-40:y=H-h-180:enable='between(t,0,{T_STUDY_START})'[v1];"
        f"[v1][card_d]overlay=x=0:y={CARD_Y}:format=auto[v2];"
        f"[v2][card_a]overlay=x=0:y={CARD_Y}:format=auto[v3];"
        f"[v3][study]overlay=x={CLIP_X}:y={CLIP_Y}:enable='between(t,{T_STUDY_START},{T_STUDY_END})'[v4];"
        f"[v4][promo]overlay=x={CLIP_X}:y={CLIP_Y}:enable='between(t,{T_PROMO_START},{T_PROMO_END})'[v5];"
        f"[v5]subtitles=filename={ass_escaped}[vout];"
        # 音声: BGM + 本文/問題 + study/promo/url ナレーション
        f"[6:a]atrim=0:{DUR},asetpts=PTS-STARTPTS,volume={BGM_VOLUME},"
        f"afade=t=in:st=0:d=0.6,afade=t=out:st={DUR-1.5}:d=1.5[bgm];"
        f"[7:a]adelay={body_delay}|{body_delay},apad[body];"
        f"[8:a]adelay={quiz_delay}|{quiz_delay},apad[quiz];"
        f"[9:a]adelay={int(T_STUDY_START*1000)}|{int(T_STUDY_START*1000)}[narr_s];"
        f"[10:a]adelay={int(T_PROMO_START*1000)}|{int(T_PROMO_START*1000)}[narr_p];"
        f"[11:a]adelay={int(T_URL_START*1000)}|{int(T_URL_START*1000)}[narr_u];"
        f"[bgm][body][quiz][narr_s][narr_p][narr_u]amix=inputs=6:duration=first:normalize=0[aout]"
    )
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(bg_png),
        "-loop", "1", "-i", str(TT_PNG),
        "-loop", "1", "-i", str(card_default),
        "-loop", "1", "-i", str(card_answered),
        "-i", str(study_rec),
        "-i", str(promo_rec),
        "-stream_loop", "-1", "-i", str(BGM_SRC),
        "-i", str(narr_body),
        "-i", str(narr_quiz),
        "-i", str(narr_study),
        "-i", str(narr_promo),
        "-i", str(narr_url),
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
        raise SystemExit(f"{quiz_id} has no body_subtitles")

    narr_dir = NARR_ROOT / quiz_id
    narr_body = narr_dir / "narr_body.wav"
    narr_quiz = narr_dir / "narr_quiz.wav"
    bg_png = ASSETS / "bg_quizzes" / quiz["bg_filename"]
    card_default = ASSETS / f"quiz_card_{quiz_id}_default.png"
    card_answered = ASSETS / f"quiz_card_{quiz_id}_answered.png"
    study_rec = Path("/Users/masaki/Workspace/projects/wordtacos-promo/captures/recording_440x900.webm")
    promo_rec = WORK / "recordings" / "promo_test_kitchen_rush.webm"
    narr_study = NARR_ROOT / "cta_v2" / "study.wav"
    narr_promo = NARR_ROOT / "cta_v2" / "promo.wav"
    narr_url = NARR_ROOT / "cta_v2" / "url.wav"

    for path, label in [(narr_body, "narr_body"), (narr_quiz, "narr_quiz"),
                         (bg_png, "bg_png"), (TT_PNG, "tt"), (BGM_SRC, "bgm"),
                         (card_default, "card_default"), (card_answered, "card_answered"),
                         (study_rec, "study_rec"), (promo_rec, "promo_rec"),
                         (narr_study, "narr_study"), (narr_promo, "narr_promo"),
                         (narr_url, "narr_url")]:
        if not path.exists():
            raise SystemExit(f"missing {label}: {path}")

    ass_path = Path(f"/tmp/wordtacos_quiz_v1_{quiz_id}.ass")
    out_mp4 = WORK / f"wordtacos_quiz_short_v1_{quiz_id}.mp4"

    body = ASS_HEADER + "\n".join(build_lines(quiz)) + "\n"
    ass_path.write_text(body, encoding="utf-8")
    print(f"ASS -> {ass_path}")

    build_video(quiz, narr_body, narr_quiz, bg_png, ass_path, out_mp4,
                card_default, card_answered,
                study_rec, promo_rec, narr_study, narr_promo, narr_url)
    return out_mp4


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quiz", required=True)
    args = parser.parse_args()
    run_one(args.quiz)


if __name__ == "__main__":
    main()
