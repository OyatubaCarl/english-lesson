"""
ナレーション付き説明動画生成スクリプト
- Voicepeak でスライドごとのナレーション音声を生成
- PIL でスライド画像 + サイトスクリーンショット合成
- ffmpeg で音声・画像を動画に結合
"""
import os
import subprocess
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

# ---- パス ----
OUT_DIR   = Path("tmp_narrated_slides")
AUDIO_DIR = Path("tmp_narrated_audio")
SS_DIR    = Path("tmp_site_screenshots")
OUT_VIDEO = Path("funnics_island_narrated.mp4")
VOICEPEAK = "/Applications/voicepeak.app/Contents/MacOS/voicepeak"
NARRATOR  = "Japanese Female 1"

# ---- 動画設定 ----
W, H = 1920, 1080
FPS  = 30
FONT_BOLD    = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
FONT_REGULAR = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"

# ---- カラーパレット ----
BG_DARK  = (15, 23, 42)
BG_CARD  = (30, 41, 59)
ACCENT   = (37, 99, 235)
ACCENT_L = (96, 165, 250)
WHITE    = (255, 255, 255)
GRAY_300 = (203, 213, 225)
GRAY_500 = (100, 116, 139)
YELLOW   = (251, 191, 36)
GREEN    = (52, 211, 153)
ORANGE   = (251, 146, 60)
PINK     = (244, 114, 182)
PURPLE   = (167, 139, 250)

def font(size, bold=True):
    path = FONT_BOLD if bold else FONT_REGULAR
    return ImageFont.truetype(path, size)

def draw_rounded_rect(draw, xy, radius, fill, outline=None, outline_width=2):
    draw.rounded_rectangle(xy, radius=radius, fill=fill,
                           outline=outline, width=outline_width)

def gradient_bg(c1, c2):
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        r = int(c1[0] + (c2[0]-c1[0])*t)
        g = int(c1[1] + (c2[1]-c1[1])*t)
        b = int(c1[2] + (c2[2]-c1[2])*t)
        draw.line([(0,y),(W,y)], fill=(r,g,b))
    return img

def load_screenshot(name: str, w: int, h: int) -> Image.Image:
    path = SS_DIR / f"{name}.png"
    if not path.exists():
        img = Image.new("RGB", (w, h), (40, 50, 70))
        draw = ImageDraw.Draw(img)
        draw.text((20, h//2-20), f"[{name}]", font=font(28, bold=False), fill=GRAY_500)
        return img
    img = Image.open(path).convert("RGB")
    img = img.resize((w, h), Image.LANCZOS)
    return img

def add_screenshot_panel(base: Image.Image, ss_name: str,
                          x: int, y: int, w: int, h: int,
                          label: str = "", label_color=WHITE) -> Image.Image:
    """スクリーンショットをパネルとして貼り付け（影 + ラベル付き）"""
    img = base.copy()
    draw = ImageDraw.Draw(img)

    # 影
    shadow = Image.new("RGB", (w+8, h+8), (5, 10, 25))
    img.paste(shadow, (x+4, y+4))

    # スクリーンショット
    ss = load_screenshot(ss_name, w, h)
    img.paste(ss, (x, y))

    # 枠線
    draw.rectangle([x-2, y-2, x+w+1, y+h+1], outline=ACCENT_L, width=2)

    # ラベル（下）
    if label:
        f = font(26, bold=False)
        bbox = draw.textbbox((0, 0), label, font=f)
        lw = bbox[2] - bbox[0]
        lx = x + (w - lw) // 2
        draw.text((lx, y + h + 8), label, font=f, fill=label_color)

    return img

# ========== スライド + ナレーション定義 ==========
# (slide_fn, narration_text, screenshot_name_or_None, ss_position)
# ss_position: (x, y, w, h)

SLIDES = []

# --- 0: タイトル ---
def slide_title():
    img = gradient_bg((10,20,60), (25,50,120))
    draw = ImageDraw.Draw(img)

    f_t = font(100)
    title = "Funnics Island"
    bbox = draw.textbbox((0,0), title, font=f_t)
    draw.text(((W-bbox[2])//2, 60), title, font=f_t, fill=WHITE)

    draw_rounded_rect(draw, (180, 210, W-180, 290), 12, fill=(20,45,110))
    f_sub = font(42, bold=False)
    sub = "認知科学に基づく英語学習の多段階アプローチ"
    bbox2 = draw.textbbox((0,0), sub, font=f_sub)
    draw.text(((W-bbox2[2])//2, 226), sub, font=f_sub, fill=ACCENT_L)

    draw.line([(W//2-200,318),(W//2+200,318)], fill=ACCENT_L, width=2)

    items = [
        ("♪ 歌・動画",        YELLOW),
        ("混 日本語混じり文",  GREEN),
        ("S/V 構文解析",       ORANGE),
        ("mic シャドウイング", PINK),
        ("Q 単語テスト",       PURPLE),
        ("絵 絵本",            ACCENT_L),
    ]
    f_l = font(30, bold=False)
    col_w = (W-160)//len(items)
    for i, (label, color) in enumerate(items):
        cx = 80 + col_w*i
        draw_rounded_rect(draw, (cx+6, 340, cx+col_w-6, 440), 12, fill=BG_CARD,
                          outline=color, outline_width=2)
        bbox = draw.textbbox((0,0), label, font=f_l)
        lw = bbox[2]-bbox[0]
        draw.text((cx+(col_w-lw)//2, 378), label, font=f_l, fill=color)

    # サイトSS（右下）
    img = add_screenshot_panel(img, "01_top", 200, 470, W-400, 530,
                               label="Funnics Island — https://english-lesson.gasflare.workers.dev",
                               label_color=GRAY_300)
    return img

SLIDES.append((slide_title,
    "このサイトは「Funnics Island（ファニックス・アイランド）」といいます。"
    "フォニックスから高校読解まで、同じレッスンテキストを7つの方法で学べる英語学習サイトです。"
    "認知科学の知見に基づいて設計されています。"))


# --- 1: 学習フロー ---
def slide_flow():
    img = gradient_bg((12,25,55),(20,40,90))
    draw = ImageDraw.Draw(img)

    f_h = font(52)
    head = "学習フロー：「聴く」から「使う」へ"
    bbox = draw.textbbox((0,0), head, font=f_h)
    draw.text(((W-bbox[2])//2, 30), head, font=f_h, fill=WHITE)

    steps = [
        ("①","動画（歌）",      "メロディーで英文を耳に入れる",     YELLOW),
        ("②","日本語混じり文",  "単語を意味ネットワークに接続する", GREEN),
        ("③","英語のみ / IPA",  "英文そのものと向き合う",           ACCENT_L),
        ("④","構文解析",        "文の骨格をS/V/O/C/Mで可視化する",  ORANGE),
        ("⑤","単語テスト",      "想起練習で記憶を強化する",         PINK),
        ("⑥","シャドウイング",  "英語を音として身体化する",         PURPLE),
        ("⑦","長文読解",        "総合的な読解力を養う",             (100,220,180)),
    ]
    f_n, f_ti, f_de = font(34), font(32), font(26, bold=False)
    row_h = 72
    start_y = 110
    for i, (num, ti, desc, color) in enumerate(steps):
        y = start_y + i*row_h
        draw_rounded_rect(draw, (80, y, W//2-20, y+row_h-6), 10, fill=BG_CARD)
        draw_rounded_rect(draw, (80, y, 100, y+row_h-6), 0, fill=color)
        draw.text((110, y+16), num, font=f_n, fill=color)
        draw.text((185, y+18), ti, font=f_ti, fill=WHITE)
        draw.text((430, y+22), desc, font=f_de, fill=GRAY_300)
        if i < len(steps)-1:
            draw.text((116, y+row_h-6), "↓", font=font(20, bold=False), fill=GRAY_500)

    # 右側にサイトの教材選択SS
    img = add_screenshot_panel(img, "02_beginner_selected", W//2+20, 110, W//2-100, 590,
                               label="教材選択画面")
    return img

SLIDES.append((slide_flow,
    "学習は7つのステップで構成されています。"
    "まず歌の動画で英文のメロディーを耳に入れ、"
    "日本語混じり文で単語の意味を覚え、"
    "英語のみ表示で英文そのものと向き合います。"
    "そして構文解析で文法を視覚化し、単語テストで記憶を強化し、"
    "シャドウイングで英語を体に入れ、最後に長文読解へと進みます。"))


# --- 2: 歌・動画 ---
def slide_song():
    img = gradient_bg((30,20,5),(60,40,10))
    draw = ImageDraw.Draw(img)
    draw_rounded_rect(draw, (0,0,W,100), 0, fill=(80,50,0))
    f_h = font(48)
    head = "♪  歌で学ぶ——音韻が記憶を定着させる"
    bbox = draw.textbbox((0,0), head, font=f_h)
    draw.text(((W-bbox[2])//2, 26), head, font=f_h, fill=YELLOW)

    points = [
        ("音楽は両脳を活性化",
         "言語野（主に左脳）だけでなく、\n音楽は両側の大脳半球を広く活性化。\n音韻処理回路がリズムとして英文を捉える。"),
        ("頭の中で自動反復",
         "メロディーに乗った英文は\n意識しなくても頭の中で繰り返される。\nストレスなく反復学習が行われる。"),
        ("流しっぱなしでOK",
         "BGMとして流しておくだけでよい。\n「勉強している感覚」なしに\n学習量を自然に増やせる。"),
    ]
    f_pt, f_pb = font(34), font(28, bold=False)
    card_w = (W//2 - 100) // 3
    py = 120
    for i, (tit, body) in enumerate(points):
        cx = 40 + i*(card_w+16)
        draw_rounded_rect(draw, (cx, py, cx+card_w, py+340), 14, fill=(50,35,5),
                          outline=YELLOW, outline_width=2)
        bbox = draw.textbbox((0,0), tit, font=f_pt)
        draw.text((cx+(card_w-bbox[2])//2, py+14), tit, font=f_pt, fill=YELLOW)
        draw.line([(cx+12, py+60),(cx+card_w-12, py+60)], fill=YELLOW, width=1)
        y = py+76
        for line in body.split("\n"):
            draw.text((cx+16, y), line, font=f_pb, fill=GRAY_300)
            y += 44

    f_foot = font(34)
    foot = "「勉強」ではなく「浸透」——歌は最初のステップ"
    bbox = draw.textbbox((0,0), foot, font=f_foot)
    draw.text(((W//2-bbox[2])//2, 490), foot, font=f_foot, fill=YELLOW)

    img = add_screenshot_panel(img, "03_lesson_b1_default", W//2+10, 108, W//2-30, 450,
                               label="B1レッスン — YouTubeの歌動画リンク付き")
    return img

SLIDES.append((slide_song,
    "このサイトの各レッスンには、本文をそのまま歌にしたYouTube動画が埋め込まれています。"
    "歌で学ぶことには、認知科学的な根拠があります。"
    "音楽は両側の大脳半球を活性化し、音韻処理回路が先に働くため、"
    "文法分析より前に英文がリズムとして入ってきます。"
    "また、メロディーに乗った英文は頭の中で自然に繰り返されるため、"
    "ストレスなく反復学習ができます。"))


# --- 3: 日本語混じり文 ---
def slide_mix():
    img = gradient_bg((5,30,15),(10,55,25))
    draw = ImageDraw.Draw(img)
    draw_rounded_rect(draw, (0,0,W,100), 0, fill=(10,60,25))
    f_h = font(46)
    head = "混  日本語混じり文——意味ネットワークへの統合"
    bbox = draw.textbbox((0,0), head, font=f_h)
    draw.text(((W-bbox[2])//2, 24), head, font=f_h, fill=GREEN)

    # 左カラム（説明）
    left_items = [
        "日本語話者はすでに豊かな",
        "「意味ネットワーク」を持っている。",
        "",
        "英語の文脈の中に日本語訳を埋め込むことで、",
        "既存ネットワークに英単語が接続される。",
        "",
        "単語帳で孤立した訳語を暗記するより、",
        "文脈の中で出会った単語の方が",
        "はるかに定着率が高い。",
        "",
        "認知言語学では「足場かけ」と呼ぶ——",
        "新しい概念を既知の認知構造に",
        "吊り下げる学習法。",
    ]
    f_b = font(30, bold=False)
    draw_rounded_rect(draw, (40,118, W//2-20, 760), 14, fill=(15,50,25))
    y = 140
    for line in left_items:
        draw.text((60, y), line, font=f_b, fill=GRAY_300)
        y += 44

    # 右：スクリーンショット
    img = add_screenshot_panel(img, "05_mode_en_ja_mix", W//2+10, 108, W//2-30, 650,
                               label="英語＋日本語ルビ表示モード")

    f_foot = font(34)
    foot = "単語帳を捨てて、文脈の中で覚える。"
    bbox = draw.textbbox((0,0), foot, font=f_foot)
    draw.text(((W-bbox[2])//2, H-80), foot, font=f_foot, fill=GREEN)
    return img

SLIDES.append((slide_mix,
    "このサイトには「英語プラス日本語ルビ」という表示モードがあります。"
    "日本語の文章の流れを保ちながら、英単語がルビ付きで登場する形式です。"
    "日本語話者はすでに豊かな意味ネットワークを持っています。"
    "日本語の文脈の中に英語を埋め込むことで、"
    "既存のネットワークに英単語を接続することができます。"
    "これを認知言語学では「足場かけ」と呼びます。"
    "単語帳で孤立した訳語を暗記するより、定着率が大幅に高くなります。"))


# --- 4: 構文解析 ---
def slide_syntax():
    img = gradient_bg((20,15,5),(50,35,10))
    draw = ImageDraw.Draw(img)
    draw_rounded_rect(draw, (0,0,W,100), 0, fill=(55,35,5))
    f_h = font(46)
    head = "S/V  構文解析——S/V/O/C/M を色で可視化"
    bbox = draw.textbbox((0,0), head, font=f_h)
    draw.text(((W-bbox[2])//2, 24), head, font=f_h, fill=ORANGE)

    # 凡例（左）
    legend = [
        ((96,165,250), "S  主語"),
        ((251,146,60), "V  動詞"),
        ((52,211,153), "O  目的語"),
        ((251,191,36), "C  補語"),
        ((148,163,184), "M  修飾語"),
    ]
    f_leg = font(38)
    draw_rounded_rect(draw, (40, 118, 340, 500), 14, fill=(40,28,5))
    y = 138
    for color, label in legend:
        draw_rounded_rect(draw, (60, y+4, 90, y+38), 6, fill=color)
        draw.text((104, y), label, font=f_leg, fill=WHITE)
        y += 62

    # 説明（左下）
    desc_items = [
        "文法を「ルール」として暗記するより、",
        "「パターン」として視覚的に",
        "認識できるほうが使いやすくなる。",
        "",
        "色分けを繰り返し見ることで、",
        "英文を読みながら構造を",
        "感じ取れるようになる。",
    ]
    f_d = font(28, bold=False)
    draw_rounded_rect(draw, (40, 520, 340, 820), 14, fill=(40,28,5))
    y = 540
    for line in desc_items:
        draw.text((56, y), line, font=f_d, fill=GRAY_300)
        y += 40

    # 右：スクリーンショット（大きめ）
    img = add_screenshot_panel(img, "11_syntax_mode", 360, 108, W-400, 730,
                               label="H1レッスン 構文解析モード — S/V/O/C/Mが色分け表示される")

    f_foot = font(34)
    foot = "文法は「見る」と「わかる」——ルール暗記から直感へ。"
    bbox = draw.textbbox((0,0), foot, font=f_foot)
    draw.text(((W-bbox[2])//2, H-80), foot, font=f_foot, fill=ORANGE)
    return img

SLIDES.append((slide_syntax,
    "高校編のレッスンには「構文解析」モードがあります。"
    "各文の単語やフレーズが、主語・動詞・目的語・補語・修飾語に色分けされ、"
    "文の構造が一目でわかるように表示されます。"
    "文法はルールとして暗記するより、パターンとして視覚的に認識できるほうが実用的です。"
    "色分けを繰り返し目にすることで、英文を読みながら構造を感じ取れるようになっていきます。"))


# --- 5: シャドウイング ---
def slide_shadow():
    img = gradient_bg((20,5,30),(45,15,65))
    draw = ImageDraw.Draw(img)
    draw_rounded_rect(draw, (0,0,W,100), 0, fill=(45,15,65))
    f_h = font(46)
    head = "mic  シャドウイング——英語を音として身体化する"
    bbox = draw.textbbox((0,0), head, font=f_h)
    draw.text(((W-bbox[2])//2, 24), head, font=f_h, fill=PINK)

    # 積み上げフロー（左）
    steps_pre = [
        ("♪ 歌",        "リズム・音韻", YELLOW),
        ("混 日本語混じり", "語彙・意味",  GREEN),
        ("S/V 構文解析", "文法・構造",  ORANGE),
    ]
    draw_rounded_rect(draw, (40,118,380,700), 14, fill=(35,10,55))
    f_s, f_sl = font(30), font(24, bold=False)
    y = 148
    for tit, sub, color in steps_pre:
        draw_rounded_rect(draw, (60, y, 360, y+90), 10, fill=BG_CARD, outline=color, outline_width=2)
        bbox = draw.textbbox((0,0), tit, font=f_s)
        draw.text((60+(300-bbox[2])//2, y+14), tit, font=f_s, fill=color)
        bbox2 = draw.textbbox((0,0), sub, font=f_sl)
        draw.text((60+(300-bbox2[2])//2, y+54), sub, font=f_sl, fill=GRAY_300)
        draw.text((190, y+94), "↓", font=font(24, bold=False), fill=GRAY_500)
        y += 118

    draw_rounded_rect(draw, (60, y, 360, y+100), 12, fill=(60,15,90), outline=PINK, outline_width=3)
    f_sh = font(32)
    bbox = draw.textbbox((0,0), "mic シャドウイング", font=f_sh)
    draw.text((60+(300-bbox[2])//2, y+14), "mic シャドウイング", font=f_sh, fill=PINK)
    f_shs = font(26, bold=False)
    sub2 = "知識を「即時使用」に変換"
    bbox2 = draw.textbbox((0,0), sub2, font=f_shs)
    draw.text((60+(300-bbox2[2])//2, y+58), sub2, font=f_shs, fill=GRAY_300)

    # 右：スクリーンショット
    img = add_screenshot_panel(img, "08_shadowing_start", 400, 108, W-440, 650,
                               label="シャドウイング練習 — マイクで発音を認識してリアルタイムフィードバック")

    f_foot = font(34)
    foot = "スピーキングは最後ではなく、積み上げの先にある。"
    bbox = draw.textbbox((0,0), foot, font=f_foot)
    draw.text(((W-bbox[2])//2, H-80), foot, font=f_foot, fill=PINK)
    return img

SLIDES.append((slide_shadow,
    "シャドウイングモードでは、音声に少し遅れてついて声に出す練習ができます。"
    "マイクで発音を認識し、どの単語が正しく言えたかをリアルタイムでフィードバックします。"
    "読んで理解できる英語と、聴いてすぐわかる英語は別物です。"
    "歌でリズムを入れ、日本語混じり文で語彙を固め、構文解析で文法を把握した後に行うシャドウイングは、"
    "これらの知識を瞬間的に使える形に変換する仕上げの工程です。"))


# --- 6: 単語テスト ---
def slide_quiz():
    img = gradient_bg((5,10,40),(15,25,80))
    draw = ImageDraw.Draw(img)
    draw_rounded_rect(draw, (0,0,W,100), 0, fill=(15,25,80))
    f_h = font(46)
    head = "Q  単語テスト——想起練習が記憶を強化する"
    bbox = draw.textbbox((0,0), head, font=f_h)
    draw.text(((W-bbox[2])//2, 24), head, font=f_h, fill=PURPLE)

    # 左：説明
    draw_rounded_rect(draw, (40,118, W//2-20, 700), 14, fill=(25,20,60))
    f_key = font(42)
    key = "テスト効果"
    bbox = draw.textbbox((0,0), key, font=f_key)
    draw.text((40+(W//2-60-bbox[2])//2, 148), key, font=f_key, fill=PURPLE)
    draw.line([(60, 202),(W//2-40, 202)], fill=PURPLE, width=1)
    body = [
        "「テスト」は単に理解度を測るためだけでなく、",
        "記憶そのものを強化するプロセスである。",
        "",
        "一度頭から引き出そうとする行為（想起練習）が、",
        "次回の想起をより確実にする。",
        "",
        "認知心理学でよく知られた現象——",
        "「見て覚える」より「思い出して覚える」方が",
        "長期記憶への定着率が高い。",
        "",
        "このサイトの単語テストでは、",
        "単語をタップすると音声も確認できる。",
    ]
    f_b = font(28, bold=False)
    y = 224
    for line in body:
        draw.text((64, y), line, font=f_b, fill=GRAY_300)
        y += 42

    img = add_screenshot_panel(img, "12_word_quiz", W//2+10, 108, W//2-30, 590,
                               label="単語テスト — 音声確認付き")

    f_foot = font(34)
    foot = "テストは「確認」ではなく「学習」そのもの。"
    bbox = draw.textbbox((0,0), foot, font=f_foot)
    draw.text(((W-bbox[2])//2, H-80), foot, font=f_foot, fill=PURPLE)
    return img

SLIDES.append((slide_quiz,
    "各レッスンには単語テスト機能があります。"
    "テストは単に覚えているかを確認するためだけでなく、記憶そのものを強化します。"
    "これは「テスト効果」として認知心理学でよく知られた現象です。"
    "一度頭から引き出そうとする行為が、次回の想起をより確実にします。"
    "また、単語をタップすると音声も確認できるため、視覚と聴覚で定着を強化できます。"))


# --- 7: 絵本モード ---
def slide_picturebook():
    img = gradient_bg((5,30,30),(10,60,55))
    draw = ImageDraw.Draw(img)
    draw_rounded_rect(draw, (0,0,W,100), 0, fill=(10,60,55))
    color = (100,220,180)
    f_h = font(46)
    head = "絵  絵本モード——場面・感情と英語を結びつける"
    bbox = draw.textbbox((0,0), head, font=f_h)
    draw.text(((W-bbox[2])//2, 24), head, font=f_h, fill=color)

    draw_rounded_rect(draw, (40,118, W//2-20, 700), 14, fill=(15,50,45))
    body = [
        "入門英語（Funnics Island）には",
        "「絵本」表示モードがある。",
        "",
        "主人公トムが島を冒険しながら",
        "英語表現を使う物語形式。",
        "",
        "英文が「文字列」ではなく、",
        "「場面・行動・感情」と",
        "結びついて記憶される。",
        "",
        "物語の続きが気になる構成が",
        "学習への動機付けを生む。",
    ]
    f_b = font(30, bold=False)
    y = 148
    for line in body:
        draw.text((64, y), line, font=f_b, fill=GRAY_300)
        y += 46

    img = add_screenshot_panel(img, "07_mode_picturebook", W//2+10, 108, W//2-30, 590,
                               label="絵本モード — 物語の流れで英文を学ぶ")

    f_foot = font(34)
    foot = "物語の中で出会った英語は、文脈ごと記憶される。"
    bbox = draw.textbbox((0,0), foot, font=f_foot)
    draw.text(((W-bbox[2])//2, H-80), foot, font=f_foot, fill=color)
    return img

SLIDES.append((slide_picturebook,
    "入門英語Funnics Islandには「絵本」表示モードがあります。"
    "主人公のトムが島を冒険しながら英語表現を使う、物語形式の教材です。"
    "英文が抽象的な文字列としてではなく、"
    "登場人物の行動や感情、物語の流れとともに記憶されます。"
    "場面記憶と感情の結びつきは、長期記憶への定着を大きく助けます。"))


# --- 8: まとめ ---
def slide_summary():
    img = gradient_bg((10,20,60),(25,50,120))
    draw = ImageDraw.Draw(img)
    f_h = font(56)
    head = "まとめ——多経路学習の設計思想"
    bbox = draw.textbbox((0,0), head, font=f_h)
    draw.text(((W-bbox[2])//2, 30), head, font=f_h, fill=WHITE)
    draw.line([(W//2-300,106),(W//2+300,106)], fill=ACCENT_L, width=2)

    draw_rounded_rect(draw, (180,120, W-180, 220), 16, fill=(20,40,100))
    f_p = font(34, bold=False)
    prin = "同じテキストに、異なる認知経路から繰り返しアクセスする。"
    bbox = draw.textbbox((0,0), prin, font=f_p)
    draw.text(((W-bbox[2])//2, 148), prin, font=f_p, fill=ACCENT_L)
    prin2 = "これが記憶の定着と運用力向上を同時に実現する。"
    bbox2 = draw.textbbox((0,0), prin2, font=f_p)
    draw.text(((W-bbox2[2])//2, 196), prin2, font=f_p, fill=GRAY_300)

    rows = [
        ("学習方法",         "主な認知ターゲット",    WHITE,   GRAY_300, True),
        ("♪ 歌・動画",       "音韻・リズム・無意識的反復", YELLOW, GRAY_300, False),
        ("混 日本語混じり文", "語彙・意味ネットワーク",    GREEN,  GRAY_300, False),
        ("絵 絵本",          "場面・感情・物語記憶",      color2 := (100,220,180), GRAY_300, False),
        ("S/V 構文解析",     "文法・文型の視覚的把握",    ORANGE, GRAY_300, False),
        ("Q 単語テスト",     "想起練習・記憶強化",        PURPLE, GRAY_300, False),
        ("mic シャドウイング","音声産出・即時使用",        PINK,   GRAY_300, False),
    ]
    f_th = font(28)
    f_tr = font(26, bold=False)
    c1x, c2x = 180, 820
    cw1, cw2 = 580, 800
    rh = 56
    ty = 240
    for method, target, cc1, cc2, is_h in rows:
        fill = (25,45,110) if is_h else BG_CARD
        draw_rounded_rect(draw, (c1x,ty,c1x+cw1,ty+rh-4), 5, fill=fill)
        draw_rounded_rect(draw, (c2x,ty,c2x+cw2,ty+rh-4), 5, fill=fill)
        f = f_th if is_h else f_tr
        draw.text((c1x+14, ty+12), method, font=f, fill=cc1)
        draw.text((c2x+14, ty+12), target, font=f, fill=cc2)
        ty += rh

    f_foot = font(36)
    foot = "自分のレベル・目的・気分に合わせて、7つの入口から英語へ。"
    bbox = draw.textbbox((0,0), foot, font=f_foot)
    draw.text(((W-bbox[2])//2, H-80), foot, font=f_foot, fill=WHITE)
    return img

SLIDES.append((slide_summary,
    "まとめです。"
    "このサイトは、同じレッスンテキストに対して、"
    "歌・日本語混じり文・絵本・構文解析・単語テスト・シャドウイング、"
    "という異なる認知経路から繰り返しアクセスできるよう設計されています。"
    "英語学習に万能の方法はありませんが、"
    "複数の経路から同じ素材に触れることで、"
    "記憶の定着と運用力の向上を同時に実現できます。"
    "ぜひ自分のレベルや目的に合わせて、7つの入口から英語を学んでみてください。"))


# ========== 音声生成 ==========

def split_text(text: str, limit: int = 135) -> list[str]:
    """テキストを 135 文字以下に句点・読点で分割する"""
    chunks = []
    current = ""
    for ch in text:
        current += ch
        if ch in ("。", "．", "！", "？") and len(current) >= 20:
            chunks.append(current.strip())
            current = ""
        elif len(current) >= limit:
            # 読点で切る
            pos = max(current.rfind("、"), current.rfind("，"))
            if pos > 10:
                chunks.append(current[:pos+1].strip())
                current = current[pos+1:]
            else:
                chunks.append(current.strip())
                current = ""
    if current.strip():
        chunks.append(current.strip())
    return [c for c in chunks if c]


def voicepeak_one(text: str, out_path: Path) -> bool:
    """Voicepeak で 1 チャンク音声生成"""
    cmd = [VOICEPEAK, "-s", text, "-n", NARRATOR,
           "-o", str(out_path), "--speed", "90"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def get_duration(path: Path) -> float:
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True
    )
    try:
        return float(probe.stdout.strip())
    except Exception:
        return 3.0


def generate_audio(text: str, out_path: Path) -> float:
    """Voicepeak でナレーション音声を生成（140文字制限対応）。再生時間（秒）を返す。"""
    chunks = split_text(text)
    tmp_dir = out_path.parent / f"_tmp_{out_path.stem}"
    tmp_dir.mkdir(exist_ok=True)

    part_paths = []
    for j, chunk in enumerate(chunks):
        part = tmp_dir / f"part_{j:02d}.wav"
        ok = voicepeak_one(chunk, part)
        if not ok or not part.exists():
            print(f"    チャンク{j}失敗: {chunk[:30]}...")
            continue
        part_paths.append(part)

    if not part_paths:
        print("  全チャンク失敗")
        return 4.0

    if len(part_paths) == 1:
        import shutil
        shutil.copy(part_paths[0], out_path)
    else:
        # concat
        concat_file = tmp_dir / "concat.txt"
        with open(concat_file, "w") as f:
            for p in part_paths:
                f.write(f"file '{p.resolve()}'\n")
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
             "-i", str(concat_file), "-c", "copy", str(out_path)],
            capture_output=True
        )

    if not out_path.exists():
        return 4.0

    return get_duration(out_path) + 0.6  # 末尾余白


# ========== メイン ==========

def build_video():
    OUT_DIR.mkdir(exist_ok=True)
    AUDIO_DIR.mkdir(exist_ok=True)

    slide_paths = []
    durations   = []

    print("=== スライド生成 & 音声生成 ===")
    for i, (fn, narration) in enumerate(SLIDES):
        print(f"\n[{i+1}/{len(SLIDES)}] {fn.__name__}")

        # スライド画像
        img = fn()
        img_path = OUT_DIR / f"slide_{i:02d}.png"
        img.save(img_path)
        slide_paths.append(img_path)
        print(f"  画像保存: {img_path.name}")

        # ナレーション音声
        audio_path = AUDIO_DIR / f"narration_{i:02d}.wav"
        print(f"  Voicepeak 音声生成中...")
        dur = generate_audio(narration, audio_path)
        durations.append(dur)
        print(f"  音声生成完了: {audio_path.name} ({dur:.1f}秒)")

    print("\n=== ffmpeg で動画結合 ===")

    # 各スライドを静止画+音声のクリップに変換
    clip_paths = []
    for i, (img_path, audio_path, dur) in enumerate(
        zip(slide_paths, [AUDIO_DIR/f"narration_{j:02d}.wav" for j in range(len(SLIDES))], durations)
    ):
        clip_path = OUT_DIR / f"clip_{i:02d}.mp4"
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", str(img_path),
            "-i", str(audio_path),
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-t", str(dur),
            "-vf", f"scale={W}:{H}",
            "-shortest",
            str(clip_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  clip {i} エラー: {result.stderr[-500:]}")
        else:
            print(f"  クリップ {i+1}: {dur:.1f}秒")
        clip_paths.append(clip_path)

    # concat
    concat_file = OUT_DIR / "concat.txt"
    with open(concat_file, "w") as f:
        for cp in clip_paths:
            f.write(f"file '{cp.resolve()}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(OUT_VIDEO)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("最終結合エラー:", result.stderr[-1000:])
        return

    total = sum(durations)
    print(f"\n完成: {OUT_VIDEO.resolve()}")
    print(f"  総再生時間: {total:.0f}秒 ({total/60:.1f}分)")
    print(f"  ファイルサイズ: {OUT_VIDEO.stat().st_size/1024/1024:.1f} MB")


if __name__ == "__main__":
    build_video()
