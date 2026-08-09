"""
説明動画生成スクリプト
Funnics Island の学習方法を説明するスライド動画を生成する。
PIL でスライド画像を生成し、ffmpeg で mp4 に結合する。
"""
import os
import subprocess
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ---- 設定 ----
OUT_DIR = Path("tmp_explanation_slides")
OUT_VIDEO = Path("funnics_island_explanation.mp4")
W, H = 1920, 1080
FPS = 30
FONT_PATH_BOLD   = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
FONT_PATH_REGULAR = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"

# ---- カラーパレット ----
BG_DARK   = (15, 23, 42)      # slate-900
BG_CARD   = (30, 41, 59)      # slate-800
ACCENT    = (37, 99, 235)     # blue-600
ACCENT_L  = (96, 165, 250)    # blue-400
WHITE     = (255, 255, 255)
GRAY_300  = (203, 213, 225)
GRAY_500  = (100, 116, 139)
YELLOW    = (251, 191, 36)
GREEN     = (52, 211, 153)
ORANGE    = (251, 146, 60)
PINK      = (244, 114, 182)
PURPLE    = (167, 139, 250)

def font(size, bold=True):
    path = FONT_PATH_BOLD if bold else FONT_PATH_REGULAR
    return ImageFont.truetype(path, size)

def draw_rounded_rect(draw, xy, radius, fill, outline=None, outline_width=2):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill,
                            outline=outline, width=outline_width)

def draw_multiline_centered(draw, text, y, font_obj, fill, line_spacing=1.4, max_width=None):
    if max_width:
        # 折り返しが必要な場合（PILのテキスト折り返しは文字単位）
        lines = []
        for raw_line in text.split("\n"):
            if not raw_line:
                lines.append("")
                continue
            current = ""
            for ch in raw_line:
                test = current + ch
                bbox = draw.textbbox((0, 0), test, font=font_obj)
                if bbox[2] - bbox[0] > max_width and current:
                    lines.append(current)
                    current = ch
                else:
                    current = test
            if current:
                lines.append(current)
    else:
        lines = text.split("\n")

    lh = font_obj.size
    total_h = lh * len(lines) * line_spacing
    cur_y = y - total_h / 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_obj)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) / 2, cur_y), line, font=font_obj, fill=fill)
        cur_y += lh * line_spacing
    return cur_y

def save_slide(img, idx):
    OUT_DIR.mkdir(exist_ok=True)
    path = OUT_DIR / f"slide_{idx:03d}.png"
    img.save(path)
    return path

def gradient_bg(colors_stops):
    """簡易縦グラデーション背景"""
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        # 2色グラデーション
        c1, c2 = colors_stops
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    return img

# ========== スライド定義 ==========

SLIDES = []  # (generator_fn, duration_sec)

def make_title_slide():
    img = gradient_bg([(10, 20, 60), (25, 50, 120)])
    draw = ImageDraw.Draw(img)

    # メインタイトル
    f_title = font(100)
    title = "Funnics Island"
    bbox = draw.textbbox((0, 0), title, font=f_title)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 80), title, font=f_title, fill=WHITE)

    # サブタイトル帯
    draw_rounded_rect(draw, (200, 230, W - 200, 310), 12, fill=(20, 45, 110))
    f_sub = font(44, bold=False)
    sub = "認知科学に基づく英語学習の多段階アプローチ"
    bbox2 = draw.textbbox((0, 0), sub, font=f_sub)
    draw.text(((W - bbox2[2]) // 2, 246), sub, font=f_sub, fill=ACCENT_L)

    # 区切り線
    draw.line([(W // 2 - 200, 340), (W // 2 + 200, 340)], fill=ACCENT_L, width=2)

    # 学習方法カード列（絵文字なし）
    items = [
        ("♪ 歌・動画",        YELLOW),
        ("混 日本語混じり文",  GREEN),
        ("S/V 構文解析",       ORANGE),
        ("mic シャドウイング", PINK),
        ("Q 単語テスト",       PURPLE),
        ("絵 絵本",            ACCENT_L),
    ]
    f_label = font(32, bold=False)
    col_w = (W - 160) // len(items)
    for i, (label, color) in enumerate(items):
        cx = 80 + col_w * i
        draw_rounded_rect(draw, (cx + 6, 370, cx + col_w - 6, 480), 12, fill=BG_CARD,
                          outline=color, outline_width=2)
        bbox = draw.textbbox((0, 0), label, font=f_label)
        lw = bbox[2] - bbox[0]
        draw.text((cx + (col_w - lw) // 2, 406), label, font=f_label, fill=color)

    # 7 modes 説明エリア
    draw_rounded_rect(draw, (100, 510, W - 100, 760), 18, fill=BG_CARD)
    f_sec = font(38)
    sec = "同じレッスンテキストを、7つの方法で学べる"
    bbox = draw.textbbox((0, 0), sec, font=f_sec)
    draw.text(((W - bbox[2]) // 2, 530), sec, font=f_sec, fill=WHITE)

    modes = [
        ("発音 (IPA)", GRAY_300),    ("語義 (日本語)", GRAY_300),
        ("ルビなし",   GRAY_300),    ("英語のみ",      GRAY_300),
        ("英語+日本語ルビ", ACCENT_L), ("日本語訳",   GRAY_300),
        ("構文解析 / 絵本", ORANGE),
    ]
    f_m = font(30, bold=False)
    mx = 140
    my = 600
    for j, (m, mc) in enumerate(modes):
        draw_rounded_rect(draw, (mx, my, mx + 210, my + 50), 8, fill=(40, 55, 100))
        bbox = draw.textbbox((0, 0), m, font=f_m)
        draw.text((mx + (210 - bbox[2]) // 2, my + 12), m, font=f_m, fill=mc)
        mx += 226
        if mx > W - 300:
            mx = 140
            my += 68

    f_foot = font(34, bold=False)
    foot = "フォニックスから高校読解まで、認知科学に基づく設計"
    bbox = draw.textbbox((0, 0), foot, font=f_foot)
    draw.text(((W - bbox[2]) // 2, H - 90), foot, font=f_foot, fill=GRAY_300)

    return img

SLIDES.append((make_title_slide, 5))


def make_flow_slide():
    """学習フロー全体像"""
    img = gradient_bg([(12, 25, 55), (20, 40, 90)])
    draw = ImageDraw.Draw(img)

    f_head = font(56)
    head = "学習フロー：「聴く」から「使う」へ"
    bbox = draw.textbbox((0, 0), head, font=f_head)
    draw.text(((W - bbox[2]) // 2, 40), head, font=f_head, fill=WHITE)

    steps = [
        ("①", "動画（歌）",       "メロディーで英文を耳に入れる",     YELLOW),
        ("②", "日本語混じり文",   "単語を意味ネットワークに接続する", GREEN),
        ("③", "英語のみ / IPA",   "英文そのものと向き合う",           ACCENT_L),
        ("④", "構文解析",         "文の骨格をS/V/O/C/Mで可視化する",  ORANGE),
        ("⑤", "単語テスト",       "想起練習で記憶を強化する",         PINK),
        ("⑥", "シャドウイング",   "英語を音として身体化する",         PURPLE),
        ("⑦", "長文読解",         "総合的な読解力を養う",             (100, 220, 180)),
    ]

    f_num   = font(36)
    f_title = font(34)
    f_desc  = font(26, bold=False)
    row_h   = 82
    start_y = 140
    col1_x, col2_x, col3_x = 100, 200, 460
    arr_x = col2_x + 205  # 矢印 x
    card_w = W - 160

    for i, (num, title, desc, color) in enumerate(steps):
        y = start_y + i * row_h
        # カード
        draw_rounded_rect(draw, (80, y, W - 80, y + row_h - 8), 12, fill=BG_CARD)
        # 左色帯
        draw_rounded_rect(draw, (80, y, 100, y + row_h - 8), 0, fill=color)
        # 番号
        draw.text((col1_x, y + 16), num, font=f_num, fill=color)
        # タイトル
        draw.text((col2_x, y + 18), title, font=f_title, fill=WHITE)
        # 説明
        draw.text((col3_x, y + 22), desc, font=f_desc, fill=GRAY_300)
        # 矢印（最後以外）
        if i < len(steps) - 1:
            ax = 120
            ay = y + row_h - 4
            draw.text((ax - 5, ay - 6), "↓", font=font(22, bold=False), fill=GRAY_500)

    return img

SLIDES.append((make_flow_slide, 6))


def make_song_slide():
    img = gradient_bg([(30, 20, 5), (60, 40, 10)])
    draw = ImageDraw.Draw(img)

    # ヘッダー
    draw_rounded_rect(draw, (0, 0, W, 120), 0, fill=(80, 50, 0))
    f_h = font(52)
    head = "♪  歌で学ぶ——音韻が記憶を定着させる"
    bbox = draw.textbbox((0, 0), head, font=f_h)
    draw.text(((W - bbox[2]) // 2, 30), head, font=f_h, fill=YELLOW)

    # 3つのポイント
    points = [
        ("音楽は両脳を活性化",
         "言語野（主に左脳）だけでなく、音楽は両側の大脳半球を\n広く活性化します。音韻処理回路が先に働き、\n文法分析より前に英文がリズムとして入ってきます。"),
        ("頭の中で自動反復",
         "歌は「耳に残る」性質があります。意識的に繰り返さなくても、\nメロディーに乗った英文が自然に再生される。\nつまり、ストレスなく反復学習が行われています。"),
        ("流しっぱなしでOK",
         "BGMとして流しっぱなしにできるのも大きなメリット。\n「勉強している感覚」なしに学習量を増やせるため、\n継続のハードルが大幅に下がります。"),
    ]

    f_pt = font(38)
    f_body = font(30, bold=False)
    card_w = (W - 160 - 40) // 3
    card_h = 420
    start_y = 160

    for i, (pt_title, pt_body) in enumerate(points):
        cx = 80 + i * (card_w + 20)
        draw_rounded_rect(draw, (cx, start_y, cx + card_w, start_y + card_h),
                          16, fill=(50, 35, 5), outline=YELLOW, outline_width=2)
        # タイトル
        bbox = draw.textbbox((0, 0), pt_title, font=f_pt)
        tw = bbox[2] - bbox[0]
        draw.text((cx + (card_w - tw) // 2, start_y + 24), pt_title, font=f_pt, fill=YELLOW)
        # 横線
        draw.line([(cx + 20, start_y + 82), (cx + card_w - 20, start_y + 82)],
                  fill=YELLOW, width=1)
        # 本文
        body_x = cx + 24
        body_y = start_y + 100
        for line in pt_body.split("\n"):
            draw.text((body_x, body_y), line, font=f_body, fill=GRAY_300)
            body_y += 46

    # フッター強調
    f_foot = font(36)
    foot = "「勉強」ではなく「浸透」。歌は最初のステップに最適です。"
    bbox = draw.textbbox((0, 0), foot, font=f_foot)
    draw.text(((W - bbox[2]) // 2, H - 90), foot, font=f_foot, fill=YELLOW)

    return img

SLIDES.append((make_song_slide, 6))


def make_mix_slide():
    img = gradient_bg([(5, 30, 15), (10, 55, 25)])
    draw = ImageDraw.Draw(img)

    draw_rounded_rect(draw, (0, 0, W, 120), 0, fill=(10, 60, 25))
    f_h = font(52)
    head = "混  日本語混じり文——意味ネットワークへの統合"
    bbox = draw.textbbox((0, 0), head, font=f_h)
    draw.text(((W - bbox[2]) // 2, 30), head, font=f_h, fill=GREEN)

    # 例文カード
    draw_rounded_rect(draw, (100, 140, W - 100, 280), 16, fill=(20, 70, 35))
    f_ex = font(38, bold=False)
    ex = "現代の若者は、親世代と異なる生活を送る。ファストフード、parking して車で移動…"
    draw.text((130, 168), ex, font=f_ex, fill=WHITE)
    f_exl = font(28, bold=False)
    draw.text((130, 230), "← 日本語の文章の中に英単語が自然に混じっている", font=f_exl, fill=GREEN)

    # 左右2カラム
    f_head2 = font(38)
    f_body2 = font(30, bold=False)

    # 左：なぜ有効か
    draw_rounded_rect(draw, (100, 300, 940, 780), 16, fill=(15, 50, 25))
    draw.text((130, 320), "なぜ有効なのか", font=f_head2, fill=GREEN)
    draw.line([(130, 372), (910, 372)], fill=GREEN, width=1)
    left_text = [
        "日本語話者はすでに豊かな",
        "「意味ネットワーク」を持っている。",
        "",
        "英語だけで学ぶ場合、単語の",
        "意味関係を一から構築する必要がある。",
        "",
        "日本語の文脈に英語を埋め込むと、",
        "既存ネットワークに英単語が接続され、",
        "具体的な場面・感覚とともに記憶される。",
    ]
    y = 388
    for line in left_text:
        draw.text((140, y), line, font=f_body2, fill=GRAY_300)
        y += 44

    # 右：スキャフォールディング
    draw_rounded_rect(draw, (980, 300, W - 100, 780), 16, fill=(15, 50, 25))
    draw.text((1010, 320), "足場かけ（スキャフォールディング）", font=f_head2, fill=GREEN)
    draw.line([(1010, 372), (W - 120, 372)], fill=GREEN, width=1)
    right_text = [
        "新しい概念を既知の認知構造に",
        "「吊り下げる」学習法。",
        "",
        "単語帳で訳語を暗記するより、",
        "文脈の中で出会った英単語のほうが",
        "はるかに定着率が高い。",
        "",
        "外国語習得において最も重要な",
        "「認知的足場」のひとつ。",
    ]
    y = 388
    for line in right_text:
        draw.text((1010, y), line, font=f_body2, fill=GRAY_300)
        y += 44

    f_foot = font(36)
    foot = "単語帳を捨てて、文脈の中で覚える。"
    bbox = draw.textbbox((0, 0), foot, font=f_foot)
    draw.text(((W - bbox[2]) // 2, H - 90), foot, font=f_foot, fill=GREEN)

    return img

SLIDES.append((make_mix_slide, 6))


def make_syntax_slide():
    img = gradient_bg([(20, 15, 5), (50, 35, 10)])
    draw = ImageDraw.Draw(img)

    draw_rounded_rect(draw, (0, 0, W, 120), 0, fill=(55, 35, 5))
    f_h = font(52)
    head = "S/V  構文解析——S/V/O/C/M を色で可視化"
    bbox = draw.textbbox((0, 0), head, font=f_h)
    draw.text(((W - bbox[2]) // 2, 30), head, font=f_h, fill=ORANGE)

    # 構文解析の例示（色分けされたトークン）
    tokens = [
        ("She", "S", (96, 165, 250)),
        ("gave", "V", (251, 146, 60)),
        ("him", "O", (52, 211, 153)),
        ("a beautiful book", "O", (52, 211, 153)),
        ("yesterday", "M", (148, 163, 184)),
    ]
    f_tok = font(42)
    f_lab = font(24, bold=False)
    tok_y = 160
    tok_x = 130
    for tok, lab, color in tokens:
        draw_rounded_rect(draw, (tok_x, tok_y, tok_x + len(tok) * 22 + 40, tok_y + 90),
                          10, fill=BG_CARD, outline=color, outline_width=2)
        draw.text((tok_x + 12, tok_y + 8), tok, font=f_tok, fill=color)
        draw.text((tok_x + 12, tok_y + 60), lab, font=f_lab, fill=color)
        tok_x += len(tok) * 22 + 60

    # 文型ラベル
    f_pat = font(34)
    draw_rounded_rect(draw, (130, 270, 460, 320), 8, fill=(55, 35, 5), outline=ORANGE)
    draw.text((150, 278), "文型：S + V + O + O（第4文型）", font=font(28, bold=False), fill=ORANGE)

    # 2カラム説明
    f_head2 = font(38)
    f_body2 = font(30, bold=False)

    draw_rounded_rect(draw, (100, 340, 940, 780), 16, fill=(40, 28, 5))
    draw.text((130, 358), "色分けで何が変わるか", font=f_head2, fill=ORANGE)
    draw.line([(130, 408), (910, 408)], fill=ORANGE, width=1)
    left_items = [
        "文法をルールとして暗記するより、",
        "パターンとして視覚的に認識できる。",
        "",
        "色分けを繰り返し目にすることで、",
        "英文を読みながら構造を感じ取れる",
        "ようになる（直感的文法）。",
        "",
        "チャンク（意味のかたまり）として",
        "処理できるようになると、読解速度が上がる。",
    ]
    y = 424
    for line in left_items:
        draw.text((140, y), line, font=f_body2, fill=GRAY_300)
        y += 44

    draw_rounded_rect(draw, (980, 340, W - 100, 780), 16, fill=(40, 28, 5))
    draw.text((1010, 358), "色の意味", font=f_head2, fill=ORANGE)
    draw.line([(1010, 408), (W - 120, 408)], fill=ORANGE, width=1)
    legend = [
        ((96, 165, 250), "S  主語"),
        ((251, 146, 60), "V  動詞"),
        ((52, 211, 153), "O  目的語"),
        ((251, 191, 36), "C  補語"),
        ((148, 163, 184), "M  修飾語"),
    ]
    y = 428
    f_leg = font(34)
    for color, label in legend:
        draw_rounded_rect(draw, (1020, y + 4, 1046, y + 36), 4, fill=color)
        draw.text((1060, y), label, font=f_leg, fill=WHITE)
        y += 56

    f_foot = font(36)
    foot = "文法は「見る」と「わかる」——ルール暗記から直感へ。"
    bbox = draw.textbbox((0, 0), foot, font=f_foot)
    draw.text(((W - bbox[2]) // 2, H - 90), foot, font=f_foot, fill=ORANGE)

    return img

SLIDES.append((make_syntax_slide, 6))


def make_shadowing_slide():
    img = gradient_bg([(20, 5, 30), (45, 15, 65)])
    draw = ImageDraw.Draw(img)

    draw_rounded_rect(draw, (0, 0, W, 120), 0, fill=(45, 15, 65))
    f_h = font(52)
    head = "mic  シャドウイング——英語を音として身体化する"
    bbox = draw.textbbox((0, 0), head, font=f_h)
    draw.text(((W - bbox[2]) // 2, 30), head, font=f_h, fill=PINK)

    # フロー図：4ステップが積み重なってシャドウイングへ
    steps_before = [
        ("♪ 歌", "リズム・音韻", YELLOW),
        ("混 日本語混じり文", "語彙・意味", GREEN),
        ("S/V 構文解析", "文法・構造", ORANGE),
    ]
    f_s = font(32)
    f_sl = font(26, bold=False)
    x = 100
    arrow_w = 60
    item_w = 260
    item_h = 110
    iy = 150

    for title, sub, color in steps_before:
        draw_rounded_rect(draw, (x, iy, x + item_w, iy + item_h), 12, fill=BG_CARD,
                          outline=color, outline_width=2)
        bbox = draw.textbbox((0, 0), title, font=f_s)
        draw.text((x + (item_w - bbox[2]) // 2, iy + 16), title, font=f_s, fill=color)
        bbox2 = draw.textbbox((0, 0), sub, font=f_sl)
        draw.text((x + (item_w - bbox2[2]) // 2, iy + 64), sub, font=f_sl, fill=GRAY_300)
        # 矢印
        ax = x + item_w + 10
        draw.text((ax, iy + 36), "→", font=font(48), fill=GRAY_500)
        x += item_w + arrow_w

    # シャドウイングの大きなカード
    sh_x = x
    sh_w = W - sh_x - 100
    draw_rounded_rect(draw, (sh_x, iy - 16, sh_x + sh_w, iy + item_h + 16),
                      16, fill=(60, 15, 90), outline=PINK, outline_width=3)
    f_sh = font(40)
    bbox = draw.textbbox((0, 0), "mic  シャドウイング", font=f_sh)
    draw.text((sh_x + (sh_w - bbox[2]) // 2, iy + 6), "mic  シャドウイング", font=f_sh, fill=PINK)
    f_shs = font(28, bold=False)
    sub2 = "知識を「即時使用」に変換"
    bbox2 = draw.textbbox((0, 0), sub2, font=f_shs)
    draw.text((sh_x + (sh_w - bbox2[2]) // 2, iy + 60), sub2, font=f_shs, fill=GRAY_300)

    # 3つのポイント
    points_sh = [
        ("音と意味の自動マッピング",
         "読んでわかる英語と、聴いてすぐわかる英語は別物。\n"
         "シャドウイングは「聴いてすぐ使える」を鍛える。"),
        ("マイクでリアルタイムフィードバック",
         "発音した単語が認識されるとハイライトされる。\n"
         "どこで詰まったかが一目でわかる。"),
        ("学習の仕上げとして機能",
         "歌・語彙・文法の知識を\n"
         "瞬間的に使える形に変換する最終ステップ。"),
    ]
    f_pt = font(34)
    f_pb = font(28, bold=False)
    card_w = (W - 160 - 40) // 3
    py = 310
    for i, (title, body) in enumerate(points_sh):
        cx = 80 + i * (card_w + 20)
        draw_rounded_rect(draw, (cx, py, cx + card_w, py + 380), 14, fill=(35, 10, 55),
                          outline=PINK, outline_width=2)
        bbox = draw.textbbox((0, 0), title, font=f_pt)
        draw.text((cx + (card_w - bbox[2]) // 2, py + 18), title, font=f_pt, fill=PINK)
        draw.line([(cx + 20, py + 64), (cx + card_w - 20, py + 64)], fill=PINK, width=1)
        y = py + 82
        for line in body.split("\n"):
            draw.text((cx + 18, y), line, font=f_pb, fill=GRAY_300)
            y += 44

    f_foot = font(36)
    foot = "スピーキングは最後ではなく、積み上げの先にある。"
    bbox = draw.textbbox((0, 0), foot, font=f_foot)
    draw.text(((W - bbox[2]) // 2, H - 90), foot, font=f_foot, fill=PINK)

    return img

SLIDES.append((make_shadowing_slide, 6))


def make_quiz_slide():
    img = gradient_bg([(5, 10, 40), (15, 25, 80)])
    draw = ImageDraw.Draw(img)

    draw_rounded_rect(draw, (0, 0, W, 120), 0, fill=(15, 25, 80))
    f_h = font(52)
    head = "Q  単語テスト——想起練習が記憶を強化する"
    bbox = draw.textbbox((0, 0), head, font=f_h)
    draw.text(((W - bbox[2]) // 2, 30), head, font=f_h, fill=PURPLE)

    # 中央の大きな説明
    draw_rounded_rect(draw, (100, 150, W - 100, 540), 20, fill=BG_CARD)

    f_key = font(52)
    key = "テスト効果（Testing Effect）"
    bbox = draw.textbbox((0, 0), key, font=f_key)
    draw.text(((W - bbox[2]) // 2, 180), key, font=f_key, fill=PURPLE)

    f_body = font(34, bold=False)
    body_lines = [
        "「テスト」は単に理解度を測るためだけでなく、",
        "記憶そのものを強化するプロセスである。",
        "",
        "一度頭から引き出そうとする行為（想起練習）が、",
        "次回の想起をより確実にする——",
        "認知心理学でよく知られた現象。",
    ]
    y = 280
    for line in body_lines:
        bbox = draw.textbbox((0, 0), line, font=f_body)
        draw.text(((W - bbox[2]) // 2, y), line, font=f_body, fill=GRAY_300)
        y += 50

    # 2つの機能
    features = [
        ("単語を音声で確認",   "テストの選択肢をタップすると\n発音が再生される。\n視覚＋聴覚で定着を強化。",  PURPLE),
        ("進捗がわかる",       "問題番号と正誤が\nリアルタイム表示される。\n達成感が継続を促す。",         ACCENT_L),
    ]
    f_ft = font(36)
    f_fb = font(28, bold=False)
    feat_w = (W - 220) // 2
    for i, (title, body, color) in enumerate(features):
        fx = 100 + i * (feat_w + 20)
        draw_rounded_rect(draw, (fx, 560, fx + feat_w, 860), 14,
                          fill=(25, 20, 60), outline=color, outline_width=2)
        bbox = draw.textbbox((0, 0), title, font=f_ft)
        draw.text((fx + (feat_w - bbox[2]) // 2, 580), title, font=f_ft, fill=color)
        draw.line([(fx + 20, 632), (fx + feat_w - 20, 632)], fill=color, width=1)
        y2 = 654
        for line in body.split("\n"):
            draw.text((fx + 24, y2), line, font=f_fb, fill=GRAY_300)
            y2 += 46

    f_foot = font(36)
    foot = "「見て覚える」より「思い出して覚える」。"
    bbox = draw.textbbox((0, 0), foot, font=f_foot)
    draw.text(((W - bbox[2]) // 2, H - 90), foot, font=f_foot, fill=PURPLE)

    return img

SLIDES.append((make_quiz_slide, 5))


def make_picturebook_slide():
    img = gradient_bg([(5, 30, 30), (10, 60, 55)])
    draw = ImageDraw.Draw(img)

    draw_rounded_rect(draw, (0, 0, W, 120), 0, fill=(10, 60, 55))
    f_h = font(52)
    head = "絵  絵本モード——場面・感情と英語を結びつける"
    bbox = draw.textbbox((0, 0), head, font=f_h)
    draw.text(((W - bbox[2]) // 2, 30), head, font=f_h, fill=(100, 220, 180))

    f_body = font(34, bold=False)
    body_lines = [
        "Funnics Island の各レッスンには「絵本」表示モードがあります。",
        "主人公トムが島を冒険しながら英語表現を使う物語形式で、",
        "英文が「文字列」ではなく「場面・行動・感情」と結びついて記憶されます。",
    ]
    y = 155
    for line in body_lines:
        bbox = draw.textbbox((0, 0), line, font=f_body)
        draw.text(((W - bbox[2]) // 2, y), line, font=f_body, fill=GRAY_300)
        y += 52

    # 3点カード
    points = [
        ("場面記憶",
         "英文と具体的なシーン（物語の状況）が\n結びつくと、記憶に多角的な引き出しが\n生まれる。"),
        ("感情との結合",
         "登場人物の喜び・驚き・友情などの\n感情が英語表現と紐づくと、\n長期記憶として定着しやすい。"),
        ("物語の流れ",
         "レッスンごとに続きが気になるような\n構成になっており、学習への動機付けが\n自然に生まれる。"),
    ]
    f_pt = font(36)
    f_pb = font(28, bold=False)
    color = (100, 220, 180)
    card_w = (W - 160 - 40) // 3
    py = 320
    for i, (title, body) in enumerate(points):
        cx = 80 + i * (card_w + 20)
        draw_rounded_rect(draw, (cx, py, cx + card_w, py + 400), 14,
                          fill=(15, 50, 45), outline=color, outline_width=2)
        bbox = draw.textbbox((0, 0), title, font=f_pt)
        draw.text((cx + (card_w - bbox[2]) // 2, py + 18), title, font=f_pt, fill=color)
        draw.line([(cx + 20, py + 68), (cx + card_w - 20, py + 68)], fill=color, width=1)
        y2 = py + 88
        for line in body.split("\n"):
            draw.text((cx + 20, y2), line, font=f_pb, fill=GRAY_300)
            y2 += 46

    f_foot = font(36)
    foot = "物語の中で出会った英語は、文脈ごと記憶される。"
    bbox = draw.textbbox((0, 0), foot, font=f_foot)
    draw.text(((W - bbox[2]) // 2, H - 90), foot, font=f_foot, fill=color)

    return img

SLIDES.append((make_picturebook_slide, 5))


def make_summary_slide():
    img = gradient_bg([(10, 20, 60), (25, 50, 120)])
    draw = ImageDraw.Draw(img)

    f_h = font(60)
    head = "まとめ——多経路学習の設計思想"
    bbox = draw.textbbox((0, 0), head, font=f_h)
    draw.text(((W - bbox[2]) // 2, 40), head, font=f_h, fill=WHITE)

    draw.line([(W // 2 - 300, 120), (W // 2 + 300, 120)], fill=ACCENT_L, width=2)

    # 中央の原則カード
    draw_rounded_rect(draw, (200, 140, W - 200, 280), 16, fill=(20, 40, 100))
    f_prin = font(36, bold=False)
    prin = "同じテキストに、異なる認知経路から繰り返しアクセスする。"
    bbox = draw.textbbox((0, 0), prin, font=f_prin)
    draw.text(((W - bbox[2]) // 2, 168), prin, font=f_prin, fill=ACCENT_L)
    prin2 = "これが記憶の定着と運用力向上を同時に実現する。"
    bbox2 = draw.textbbox((0, 0), prin2, font=f_prin)
    draw.text(((W - bbox2[2]) // 2, 220), prin2, font=f_prin, fill=GRAY_300)

    # 方法×認知ターゲットの表
    rows = [
        ("学習方法",       "主な認知ターゲット",    WHITE,   GRAY_300, True),
        ("♪ 歌・動画",       "音韻・リズム・無意識的反復", YELLOW, GRAY_300, False),
        ("混 日本語混じり文", "語彙・意味ネットワーク",    GREEN,  GRAY_300, False),
        ("絵 絵本",          "場面・感情・物語記憶",      (100,220,180), GRAY_300, False),
        ("S/V 構文解析",     "文法・文型の視覚的把握",    ORANGE, GRAY_300, False),
        ("Q 単語テスト",     "想起練習・記憶強化",        PURPLE, GRAY_300, False),
        ("mic シャドウイング", "音声産出・即時使用",       PINK,  GRAY_300, False),
    ]
    f_th = font(30)
    f_tr = font(28, bold=False)
    col1_x, col2_x = 200, 840
    col_w1, col_w2 = 580, 800
    row_h = 62
    ty = 300
    for method, target, c1, c2, is_header in rows:
        fill = (25, 45, 110) if is_header else BG_CARD
        draw_rounded_rect(draw, (col1_x, ty, col1_x + col_w1, ty + row_h - 4), 6, fill=fill)
        draw_rounded_rect(draw, (col2_x, ty, col2_x + col_w2, ty + row_h - 4), 6, fill=fill)
        f = f_th if is_header else f_tr
        draw.text((col1_x + 16, ty + 14), method, font=f, fill=c1)
        draw.text((col2_x + 16, ty + 14), target, font=f, fill=c2)
        ty += row_h

    f_foot = font(38)
    foot = "自分のレベル・目的・気分に合わせて、7つの入口から英語へ。"
    bbox = draw.textbbox((0, 0), foot, font=f_foot)
    draw.text(((W - bbox[2]) // 2, H - 90), foot, font=f_foot, fill=WHITE)

    return img

SLIDES.append((make_summary_slide, 7))


# ========== 動画生成 ==========

def build_video():
    OUT_DIR.mkdir(exist_ok=True)

    print("スライド画像を生成中...")
    slide_paths = []
    for i, (gen_fn, duration) in enumerate(SLIDES):
        print(f"  スライド {i+1}/{len(SLIDES)}: {gen_fn.__name__}")
        img = gen_fn()
        path = save_slide(img, i)
        slide_paths.append((path, duration))

    print("ffmpeg で動画を結合中...")
    # concat リストを作成
    concat_file = OUT_DIR / "concat.txt"
    with open(concat_file, "w") as f:
        for path, dur in slide_paths:
            f.write(f"file '{path.resolve()}'\n")
            f.write(f"duration {dur}\n")
        # 最後のフレームを1フレーム分追加（ffmpegの末尾バグ回避）
        last_path = slide_paths[-1][0]
        f.write(f"file '{last_path.resolve()}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
        "-vf", f"fps={FPS},scale={W}:{H}",
        "-c:v", "libx264", "-preset", "slow",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        str(OUT_VIDEO)
    ]
    print("コマンド:", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("ffmpeg エラー:", result.stderr[-2000:])
        return False

    print(f"\n完成: {OUT_VIDEO.resolve()}")
    print(f"  サイズ: {OUT_VIDEO.stat().st_size / 1024 / 1024:.1f} MB")
    return True


if __name__ == "__main__":
    build_video()
