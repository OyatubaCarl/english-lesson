"""WordTacos 純粋紹介動画 (縦 1080x1920)

構成:
  0-3s   : タイトルカード「WordTacos / 日本語に包んでやさしく学ぶ英単語」
  3-13s  : 通常の学習モード録画 (study.wav ナレーション 9.3s に合わせる)
  13-21s : 昇級試験ミニゲーム録画 (promo.wav ナレーション 7.0s に合わせる)
  21-25.7s: CTA URL カード (url.wav ナレーション 4.65s)
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NARR = ROOT / "narration" / "cta_v2"
STUDY_REC = Path("/Users/masaki/Workspace/projects/wordtacos-promo/captures/recording_440x900.webm")
PROMO_REC = ROOT / "recordings" / "promo_test_kitchen_rush.webm"
BGM = Path(
    "/Users/masaki/Documents/ClaudeCode/FunnicsIsland/songs/21_tacos_fiesta_dance/audio/tacos_fiesta_suno_SX3pVWTGGFxEsIHW.mp3"
)
TT_PNG = Path(
    "/Users/masaki/Documents/ClaudeCode/FunnicsIsland/characters/T_teacher_tacos/single.png"
)
SCENIC_BG = ROOT / "assets" / "bg_quizzes" / "bg_02_resilient.png"
ASSETS = ROOT / "assets"
OUT_MP4 = ROOT / "wordtacos_intro_v1.mp4"
ASS_PATH = Path("/tmp/wordtacos_intro_v1.ass")

W, H, FPS = 1080, 1920, 30

# タイムライン
T_TITLE_END = 3.0
T_STUDY_START = 3.0
T_STUDY_END = 13.0      # study.wav 9.3s + 0.7s 余韻
T_PROMO_START = 13.0
T_PROMO_END = 20.5      # promo.wav 7.0s + 0.5s
T_CTA_START = 20.5
T_CTA_END = 25.5        # url.wav 4.65s + 0.35s
DUR = T_CTA_END

BGM_VOLUME = 0.25

def t(s: float) -> str:
    h = int(s // 3600); m = int((s % 3600) // 60); sec = s - h*3600 - m*60
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
Style: Handle,   Helvetica,                     32, &HC0FFFFFF, &HC0FFFFFF, &H00000000, &H00000000,  0, 0, 0, 0, 100, 100, 2, 0, 1, 2, 1, 5, 0, 0, 0, 1
Style: TitleBig, Hiragino Sans W7,             140, &H00FFFFFF, &H00FFFFFF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 4, 0, 1, 10, 6, 5, 0, 0, 0, 1
Style: TitleAcc, Helvetica,                    150, &H003DD9FF, &H003DD9FF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 4, 0, 1, 10, 6, 5, 0, 0, 0, 1
Style: TitleSub, Hiragino Sans W7,              62, &H00FFFFFF, &H00FFFFFF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 4, 0, 1, 7, 4, 5, 0, 0, 0, 1
Style: SectHead, Hiragino Sans W7,              74, &H003DD9FF, &H003DD9FF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 2, 0, 1, 6, 4, 5, 0, 0, 0, 1
Style: SectSub,  Hiragino Sans W7,              52, &H00FFFFFF, &H00FFFFFF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 2, 0, 1, 5, 3, 5, 0, 0, 0, 1
Style: CtaBig,   Hiragino Sans W7,              80, &H00FFFFFF, &H00FFFFFF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 1, 0, 1, 6, 4, 5, 60, 60, 0, 1
Style: CtaURL,   Helvetica,                     64, &H003DD9FF, &H003DD9FF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 2, 0, 1, 6, 4, 5, 0, 0, 0, 1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def build_ass() -> str:
    lines = []
    # 上部ハンドル (常時)
    lines.append(D(0, 0.0, DUR, "Handle", "@TeacherTacosEnglish",
                   "{\\pos(540,90)\\fad(300,300)}"))

    # === タイトルカード ===
    lines.append(D(0, 0.2, T_TITLE_END, "TitleBig", "Word",
                   "{\\pos(360,650)\\fad(280,250)}"))
    lines.append(D(0, 0.2, T_TITLE_END, "TitleAcc", "Tacos",
                   "{\\pos(750,650)\\fad(280,250)}"))
    lines.append(D(0, 0.7, T_TITLE_END, "TitleSub",
                   "日本語に 包んで やさしく 学ぶ 英単語",
                   "{\\pos(540,830)\\fad(280,250)}"))

    # === セクション 1: 通常の学習モード ===
    lines.append(D(0, T_STUDY_START, T_STUDY_END - 0.3, "SectHead",
                   "▷  通常の 学習モード",
                   "{\\pos(540,200)\\fad(300,250)}"))
    lines.append(D(0, T_STUDY_START + 0.5, T_STUDY_END - 0.3, "SectSub",
                   "日本語の文に 英単語を 埋め込んで 4択で 答える",
                   "{\\pos(540,1700)\\fad(300,250)}"))
    lines.append(D(0, T_STUDY_START + 5.5, T_STUDY_END - 0.3, "SectSub",
                   "中学から 大学受験まで 7000語 カバー",
                   "{\\pos(540,1790)\\fad(300,250)\\c&H6BE0FF&}"))

    # === セクション 2: 昇級試験 ミニゲーム ===
    lines.append(D(0, T_PROMO_START, T_PROMO_END - 0.3, "SectHead",
                   "▷  昇級試験は ミニゲーム",
                   "{\\pos(540,200)\\fad(300,250)}"))
    lines.append(D(0, T_PROMO_START + 0.5, T_PROMO_END - 0.3, "SectSub",
                   "工房ラッシュで タコス を 作りながら 答える",
                   "{\\pos(540,1700)\\fad(300,250)}"))
    lines.append(D(0, T_PROMO_START + 4.0, T_PROMO_END - 0.3, "SectSub",
                   "10連続正解で 次の レッスン 解放 !",
                   "{\\pos(540,1790)\\fad(300,250)\\c&H6BE0FF&}"))

    # === CTA ===
    lines.append(D(0, T_CTA_START, T_CTA_END, "CtaBig",
                   "今すぐ 無料で。",
                   "{\\pos(540,720)\\fad(280,250)}"))
    lines.append(D(0, T_CTA_START + 0.6, T_CTA_END, "CtaBig",
                   "ブラウザ だけで OK。",
                   "{\\pos(540,860)\\fad(280,250)}"))
    lines.append(D(0, T_CTA_START + 1.6, T_CTA_END, "CtaURL",
                   "→  words.teachertacos.com",
                   "{\\pos(540,1300)\\fad(280,300)\\t(\\fscx108\\fscy108)}"))
    return ASS_HEADER + "\n".join(lines) + "\n"


def main() -> None:
    for p in [STUDY_REC, PROMO_REC, BGM, TT_PNG, SCENIC_BG,
              NARR / "study.wav", NARR / "promo.wav", NARR / "url.wav"]:
        if not p.exists():
            sys.exit(f"missing: {p}")

    ASS_PATH.write_text(build_ass(), encoding="utf-8")
    print(f"ASS -> {ASS_PATH}")

    ass_escaped = str(ASS_PATH).replace(":", r"\:")

    # 録画の有効区間を切り出して使う
    STUDY_IN, STUDY_OUT = 3.5, 13.5      # 通常学習モード 10秒
    PROMO_IN, PROMO_OUT = 30.0, 37.5      # 昇級試験 7.5秒

    # キッチンラッシュ録画は 440x780 → 720x1276 にスケール、中央配置
    KR_W, KR_H = 720, 1276
    KR_X = (W - KR_W) // 2  # 180
    KR_Y = 320

    # 通常学習録画は 440x900 → 720x1473 にスケール (高さオーバー、上から1276だけ表示)
    ST_W = 720
    ST_X = (W - ST_W) // 2

    filter_complex = (
        # 背景 (シーン画像、暗め)
        f"[0:v]loop=loop=-1:size=1:start=0,trim=duration={DUR},setpts=PTS-STARTPTS,"
        f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},"
        f"eq=brightness=-0.2:saturation=1.05[bg];"
        # TeacherTacos 常駐 (right-bottom corner)
        f"[1:v]scale=240:-1,fps={FPS},trim=duration={DUR},setpts=PTS-STARTPTS[tt];"
        # 通常学習 録画 (STUDY_IN〜STUDY_OUT を切出、T_STUDY_START 以降に貼付)
        f"[2:v]trim=start={STUDY_IN}:end={STUDY_OUT},setpts=PTS-STARTPTS,fps={FPS},"
        f"scale={ST_W}:-2,crop={ST_W}:1276:0:0,"
        f"setpts=PTS+{T_STUDY_START}/TB[study];"
        # 昇級試験 録画 (PROMO_IN〜PROMO_OUT を切出、T_PROMO_START 以降に貼付)
        f"[3:v]trim=start={PROMO_IN}:end={PROMO_OUT},setpts=PTS-STARTPTS,fps={FPS},"
        f"scale={KR_W}:{KR_H},"
        f"setpts=PTS+{T_PROMO_START}/TB[promo];"
        # 合成
        f"[bg][tt]overlay=x=W-w-40:y=H-h-40[v1];"
        f"[v1][study]overlay=x={ST_X}:y={KR_Y}:enable='between(t,{T_STUDY_START},{T_STUDY_END})'[v2];"
        f"[v2][promo]overlay=x={KR_X}:y={KR_Y}:enable='between(t,{T_PROMO_START},{T_PROMO_END})'[v3];"
        f"[v3]subtitles=filename={ass_escaped}[vout];"
        # 音声: BGM + 3つのナレーション
        f"[4:a]atrim=0:{DUR},asetpts=PTS-STARTPTS,volume={BGM_VOLUME},"
        f"afade=t=in:st=0:d=0.6,afade=t=out:st={DUR-1.5}:d=1.5[bgm];"
        f"[5:a]adelay={int(T_STUDY_START*1000)}|{int(T_STUDY_START*1000)}[narr_s];"
        f"[6:a]adelay={int(T_PROMO_START*1000)}|{int(T_PROMO_START*1000)}[narr_p];"
        f"[7:a]adelay={int(T_CTA_START*1000)}|{int(T_CTA_START*1000)}[narr_u];"
        f"[bgm][narr_s][narr_p][narr_u]amix=inputs=4:duration=first:normalize=0[aout]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(SCENIC_BG),
        "-loop", "1", "-i", str(TT_PNG),
        "-i", str(STUDY_REC),
        "-i", str(PROMO_REC),
        "-stream_loop", "-1", "-i", str(BGM),
        "-i", str(NARR / "study.wav"),
        "-i", str(NARR / "promo.wav"),
        "-i", str(NARR / "url.wav"),
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", "[aout]",
        "-r", str(FPS), "-t", str(DUR),
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
        str(OUT_MP4),
    ]
    print("Running ffmpeg ...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(res.stderr[-3000:], file=sys.stderr)
        sys.exit(res.returncode)
    print(f"✓ {OUT_MP4}  ({OUT_MP4.stat().st_size / 1024 / 1024:.1f} MB)")


if __name__ == "__main__":
    main()
