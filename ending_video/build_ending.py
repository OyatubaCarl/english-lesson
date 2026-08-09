"""WordTacos 卒業エンディング動画を作る。

Suno 曲 (~3:50) を BGM に、
- タイトル
- アプリ画面の思い出
- Kitchen Rush ハイライト
- クレジット (開発・音楽・画像・音声・語彙)
- 感謝のアウトロ
を縦型 1080x1920 で組み立てる。
"""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJ = ROOT.parent
ASSETS = PROJ / "vocab_sources" / "app_assets"
MASCOT = ASSETS / "mascot_with_bg"
RECORDINGS = PROJ / "shorts" / "recordings"
SHORTS = PROJ / "shorts"

BGM = ROOT / "wordtacos_ending.mp3"
OUT = ROOT / "wordtacos_ending_v3.mp4"
ASS_PATH = ROOT / "credits.ass"
W, H = 1080, 1920
FPS = 30
TOTAL = 230  # 曲の長さに合わせる

# ========== ASS (字幕) ==========
ASS_HEADER = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Title,    Hiragino Sans W7, 110, &H00FFFFFF, &H00351D0A, &H00000000, 1, 1, 4, 2, 5, 60, 60, 0,     1
Style: SubTitle, Hiragino Sans W6, 56,  &H00F4E4C8, &H00351D0A, &H00000000, 0, 1, 3, 2, 5, 80, 80, 0,     1
Style: Section,  Hiragino Sans W7, 78,  &H00FFFFFF, &H00351D0A, &H00000000, 1, 1, 4, 2, 8, 60, 60, 1700,  1
Style: Item,     Hiragino Sans W5, 50,  &H00F4E4C8, &H00351D0A, &H00000000, 0, 1, 3, 2, 8, 60, 60, 1100,  1
Style: ItemSub,  Hiragino Sans W4, 42,  &H00BDA585, &H00351D0A, &H00000000, 0, 1, 2, 2, 8, 60, 60, 980,   1
Style: Outro,    Hiragino Sans W7, 96,  &H00FFFFFF, &H00351D0A, &H00000000, 1, 1, 4, 2, 5, 60, 60, 0,     1
Style: URL,      Hiragino Sans W6, 50,  &H00FFE8B3, &H00351D0A, &H00000000, 0, 1, 3, 2, 5, 60, 60, 0,     1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def t(sec: float) -> str:
    """秒 -> ASS time format"""
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec - h * 3600 - m * 60
    return f"{h:d}:{m:02d}:{s:05.2f}"


def dialogue(start: float, end: float, style: str, text: str, layer: int = 0, marginv: int | None = None) -> str:
    mv = "" if marginv is None else str(marginv)
    return f"Dialogue: {layer},{t(start)},{t(end)},{style},,0,0,{mv},,{text}"


# クレジット内容
SEGMENTS = [
    # (start, end, style, text)
    # --- intro 0-12s
    (0.0,  4.0, "Title",    "🌮"),
    (1.0,  6.0, "SubTitle", "{\\fad(400,400)}— WordTacos —"),
    (4.5, 11.0, "Title",    "{\\fad(400,400)}卒業おめでとう"),
    (8.0, 11.0, "SubTitle", "{\\fad(400,400)}最後のレッスンまで\\Nよく辿りついたね"),

    # --- memories 12-65s : 字幕は控えめにして画面録画/モンタージュを主役に
    (13.0, 18.0, "SubTitle", "{\\fad(400,400)}日本語の中に\\N英単語を埋め込んで"),
    (18.5, 23.5, "SubTitle", "{\\fad(400,400)}文脈ごと覚える"),
    (24.0, 30.0, "SubTitle", "{\\fad(400,400)}中1から大学受験まで\\N7000語ぜんぶ"),

    # --- kitchen rush highlight 65-100s
    (66.0, 72.0, "SubTitle", "{\\fad(400,400)}🌮 タコス工房ラッシュ"),
    (73.0, 79.0, "SubTitle", "{\\fad(400,400)}10連続正解で\\N昇級試験突破"),

    # --- credits roll 100-220s (120s)
    # service header
    (101.0, 106.0, "Section", "{\\fad(500,500)}— このアプリは こうやって作った —"),

    # 開発
    (108.0, 116.0, "Section",  "{\\fad(400,400)}開発"),
    (109.0, 116.0, "Item",     "{\\fad(400,400)}Claude Code"),
    (110.0, 116.0, "ItemSub",  "{\\fad(400,400)}Anthropic"),

    # ホスティング
    (118.0, 126.0, "Section",  "{\\fad(400,400)}ホスティング"),
    (119.0, 126.0, "Item",     "{\\fad(400,400)}Cloudflare Pages"),
    (120.0, 126.0, "ItemSub",  "{\\fad(400,400)}wordtacos.pages.dev"),

    # 音楽
    (128.0, 136.0, "Section",  "{\\fad(400,400)}音楽"),
    (129.0, 136.0, "Item",     "{\\fad(400,400)}Suno"),
    (130.0, 136.0, "ItemSub",  "{\\fad(400,400)}このエンディング曲"),

    # 画像生成
    (138.0, 148.0, "Section",  "{\\fad(400,400)}画像生成"),
    (139.0, 148.0, "Item",     "{\\fad(400,400)}OpenAI image_gen / GPT Image"),
    (141.0, 148.0, "Item",     "{\\fad(400,400)}Google Gemini (Nano Banana)"),
    (143.0, 148.0, "ItemSub",  "{\\fad(400,400)}マスコット・背景・タイル素材"),

    # 画像加工
    (150.0, 158.0, "Section",  "{\\fad(400,400)}画像加工"),
    (151.0, 158.0, "Item",     "{\\fad(400,400)}rembg (isnet-general-use)"),
    (153.0, 158.0, "Item",     "{\\fad(400,400)}Python Pillow / ffmpeg"),

    # 音声合成
    (160.0, 170.0, "Section",  "{\\fad(400,400)}音声合成"),
    (161.0, 170.0, "Item",     "{\\fad(400,400)}OpenAI TTS"),
    (163.0, 170.0, "ItemSub",  "{\\fad(400,400)}英単語と例文の発音 (4000語)"),
    (165.0, 170.0, "Item",     "{\\fad(400,400)}VOICEPEAK / Piper TTS"),

    # 語彙レベル
    (172.0, 186.0, "Section",  "{\\fad(400,400)}英単語の出典・レベル分類"),
    (173.0, 186.0, "Item",     "{\\fad(400,400)}CEFR-J Wordlist"),
    (175.0, 186.0, "ItemSub",  "{\\fad(400,400)}投野研究室 (東京外国語大学)"),
    (178.0, 186.0, "Item",     "{\\fad(400,400)}中学校・高等学校 学習指導要領"),
    (181.0, 186.0, "ItemSub",  "{\\fad(400,400)}TOEIC 点数表記は CEFR との対応からの目安"),

    # 制作者
    (186.0, 196.0, "Section",  "{\\fad(400,400)}企画・制作"),
    (187.0, 196.0, "Item",     "{\\fad(400,400)}Teacher Tacos English"),
    (189.0, 196.0, "ItemSub",  "{\\fad(400,400)}神奈川県 現役教員"),

    # 謝辞
    (198.0, 210.0, "Section",  "{\\fad(400,400)}スペシャルサンクス"),
    (199.0, 210.0, "Item",     "{\\fad(400,400)}遊んでくれた すべての学習者へ"),
    (203.0, 210.0, "ItemSub",  "{\\fad(400,400)}— Thank you for studying! —"),

    # --- outro 220-230s
    (212.0, 222.0, "Outro", "{\\fad(700,500)}またね 🌮"),
    (215.0, 228.0, "URL",   "{\\fad(700,500)}words.teachertacos.com"),
]


def build_ass() -> None:
    lines = [ASS_HEADER]
    for s, e, style, text in SEGMENTS:
        lines.append(dialogue(s, e, style, text))
    ASS_PATH.write_text("\n".join(lines), encoding="utf-8")


def build_video() -> None:
    """ffmpeg filter_complex でレイヤを重ねる:
       - 背景: 暗い茶 (#351D0A) のソリッド
       - 0-12s: WordTacos アイコン中央
       - 12-65s: wordtacos 02_resilient のループ + 04_scrutinize
       - 65-100s: Kitchen Rush playthrough
       - 100-218s: 暗背景 + マスコット (隅) + クレジット
       - 218-230s: マスコット中央 + outro
       - 全体に Suno BGM
    """
    # 利用する素材
    icon = ASSETS / "icon-512.png"
    mascot_cheering = MASCOT / "cheering.png"
    mascot_proud = MASCOT / "proud.png"

    # Playwright で録画したプレイ素材 (440x780)
    REC = ROOT / "recordings"
    r_stage   = REC / "stage_select.webm"
    r_lesson1 = REC / "lesson_select_stage1.webm"
    r_lesson4 = REC / "lesson_select_stage4.webm"
    r_quiz1   = REC / "quiz_stage1_easy.webm"
    r_quiz4   = REC / "quiz_stage4_intermediate.webm"
    r_wrong   = REC / "quiz_wrong_retry.webm"
    r_kr_unlk = REC / "kitchen_rush_unlock.webm"
    r_kr_mist = REC / "kitchen_rush_mistake.webm"
    r_toeic   = REC / "toeic_basic.webm"

    # 入力リスト
    inputs = [
        ("-f", "lavfi", "-t", str(TOTAL), "-i", f"color=c=0x351D0A:size={W}x{H}:rate={FPS}"),
        ("-i", str(icon)),
        ("-i", str(mascot_cheering)),
        ("-i", str(mascot_proud)),
        ("-stream_loop", "-1", "-i", str(r_stage)),    # 4
        ("-stream_loop", "-1", "-i", str(r_lesson1)),  # 5
        ("-stream_loop", "-1", "-i", str(r_lesson4)),  # 6
        ("-stream_loop", "-1", "-i", str(r_quiz1)),    # 7
        ("-stream_loop", "-1", "-i", str(r_quiz4)),    # 8
        ("-stream_loop", "-1", "-i", str(r_wrong)),    # 9
        ("-stream_loop", "-1", "-i", str(r_kr_unlk)),  # 10
        ("-stream_loop", "-1", "-i", str(r_kr_mist)),  # 11
        ("-stream_loop", "-1", "-i", str(r_toeic)),    # 12
        ("-i", str(BGM)),                              # 13
    ]
    args = []
    for grp in inputs:
        args.extend(grp)

    ass_safe = str(ASS_PATH).replace(":", "\\:").replace("'", r"\'")

    # 録画素材を 440x780 -> サイドバイサイド用 480x850 / 単独表示用 760x1346 にスケール
    # サイドバイサイドは frame の角を丸めず、シンプルに2つ並べる
    fc = (
        # 静止画素材
        f"[1:v]format=rgba,scale=512:512[icon];"
        f"[2:v]format=rgba,scale=-1:700[mc];"
        f"[3:v]format=rgba,scale=-1:700[mp];"
        # 録画素材 (sidebyside = 480x850, single = 760x1346)
        f"[4:v]scale=480:850,setpts=PTS-STARTPTS[r_stage_s];"
        f"[5:v]scale=480:850,setpts=PTS-STARTPTS[r_l1_s];"
        f"[6:v]scale=480:850,setpts=PTS-STARTPTS[r_l4_s];"
        f"[7:v]scale=480:850,setpts=PTS-STARTPTS[r_q1_s];"
        f"[8:v]scale=480:850,setpts=PTS-STARTPTS[r_q4_s];"
        f"[9:v]scale=480:850,setpts=PTS-STARTPTS[r_w_s];"
        f"[10:v]scale=760:1346,setpts=PTS-STARTPTS[r_kru_l];"
        f"[11:v]scale=760:1346,setpts=PTS-STARTPTS[r_krm_l];"
        f"[12:v]scale=480:850,setpts=PTS-STARTPTS[r_toe_s];"
        # === 合成 ===
        # 段1: icon (1-6s)
        f"[0:v][icon]overlay=(W-w)/2:600:enable='between(t,1,6.0)'[v1];"
        # 段2 メモリ前半 (12-26s): stage_select + lesson_select_stage1
        f"[v1][r_stage_s]overlay=40:560:enable='between(t,12,26)'[v2];"
        f"[v2][r_l1_s]overlay=W-w-40:560:enable='between(t,12,26)'[v3];"
        # 段3 メモリ中 (26-40s): quiz_stage1 + quiz_stage4
        f"[v3][r_q1_s]overlay=40:560:enable='between(t,26,40)'[v4];"
        f"[v4][r_q4_s]overlay=W-w-40:560:enable='between(t,26,40)'[v5];"
        # 段4 メモリ後 (40-54s): quiz_wrong_retry + lesson_select_stage4
        f"[v5][r_w_s]overlay=40:560:enable='between(t,40,54)'[v6];"
        f"[v6][r_l4_s]overlay=W-w-40:560:enable='between(t,40,54)'[v7];"
        # 段5 TOEIC (54-66s): toeic_basic (中央寄り)
        f"[v7][r_toe_s]overlay=(W-w)/2:560:enable='between(t,54,66)'[v8];"
        # 段6 Kitchen Rush ハイライト (66-100s)
        f"[v8][r_kru_l]overlay=(W-w)/2:380:enable='between(t,66,84)'[v9];"
        f"[v9][r_krm_l]overlay=(W-w)/2:380:enable='between(t,84,100)'[v10];"
        # 段7 クレジット (100-218s): マスコットを下部隅
        f"[v10][mp]overlay=W-w-30:H-h-160:enable='between(t,100,218)'[v11];"
        # 段8 outro (218-230): マスコット中央
        f"[v11][mc]overlay=(W-w)/2:520:enable='between(t,218,230)'[v12];"
        # ASS subtitles をオーバーレイ
        f"[v12]subtitles='{ass_safe}':fontsdir=/System/Library/Fonts[vfinal]"
    )

    cmd = [
        "ffmpeg", "-y",
        *args,
        "-filter_complex", fc,
        "-map", "[vfinal]",
        "-map", "13:a",
        "-t", str(TOTAL),
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-r", str(FPS),
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "44100",
        "-movflags", "+faststart",
        str(OUT),
    ]
    print(f"running ffmpeg → {OUT.name}")
    subprocess.run(cmd, check=True)
    print(f"\n✓ {OUT}")


def main() -> None:
    build_ass()
    print(f"wrote {ASS_PATH.name}")
    build_video()


if __name__ == "__main__":
    main()
