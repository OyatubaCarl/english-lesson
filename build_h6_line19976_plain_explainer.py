"""Build a plain H6 explainer video from the line-19976 grammar theme.

Japanese narration uses VOICEPEAK Japanese Male 2.
Every spoken English word, phrase, formula, and example uses macOS English
voice so English never falls through to the Japanese narrator.
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "tmp_h6_line19976_plain"
FRAME_DIR = OUT_DIR / "frames"
AUDIO_DIR = OUT_DIR / "audio"
CLIP_DIR = OUT_DIR / "clips"
OUT_VIDEO = ROOT / "h6_perception_causative_line19976_explainer.mp4"

VOICEPEAK = "/Applications/voicepeak.app/Contents/MacOS/voicepeak"
NARRATOR = "Japanese Male 2"
EN_VOICE = "Daniel"
AUDIO_VERSION = "h6-line19976-v1"

W, H = 1920, 1080
FPS = 30

FONT_BOLD = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
FONT_REGULAR = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"

INK = (30, 41, 59)
MUTED = (100, 116, 139)
NAVY = (30, 64, 175)
BLUE = (37, 99, 235)
RED = (220, 38, 38)
GREEN = (5, 150, 105)
ORANGE = (234, 88, 12)
PURPLE = (124, 58, 237)
YELLOW = (245, 158, 11)
PAPER_TOP = (239, 246, 255)
PAPER_BOTTOM = (255, 251, 235)
CARD = (255, 255, 255)
BORDER = (226, 232, 240)
WHITE = (255, 255, 255)
SLATE = (15, 23, 42)

ROLE_COLORS = {
    "S": BLUE,
    "V": RED,
    "O": GREEN,
    "C": ORANGE,
    "M": MUTED,
}


@dataclass(frozen=True)
class AudioEvent:
    kind: str
    text: str = ""
    seconds: float = 0.0


@dataclass(frozen=True)
class RolePart:
    role: str
    en: str
    ja: str


@dataclass(frozen=True)
class Step:
    name: str
    render: Callable[[], Image.Image]
    events: tuple[AudioEvent, ...]


def JP(text: str) -> AudioEvent:
    if re.search(r"[A-Za-z]", text):
        raise ValueError(f"Japanese narration contains ASCII English: {text}")
    return AudioEvent("jp", text)


def EN(text: str) -> AudioEvent:
    return AudioEvent("en", text)


def PAUSE(seconds: float = 0.25) -> AudioEvent:
    return AudioEvent("pause", seconds=seconds)


def font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REGULAR, size)


F_TITLE = font(60)
F_H1 = font(54)
F_H2 = font(42)
F_H3 = font(33)
F_BODY = font(29, bold=False)
F_BODY_BOLD = font(30)
F_SMALL = font(22, bold=False)
F_EN = font(39)
F_EN_SMALL = font(29)
F_LABEL = font(23)
F_TAG = font(22)


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("Command failed:\n" + " ".join(cmd) + "\n" + result.stderr[-3000:])
    return result


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        paragraph = paragraph.strip()
        if not paragraph:
            lines.append("")
            continue
        tokens = paragraph.split(" ") if " " in paragraph else list(paragraph)
        sep = " " if " " in paragraph else ""
        current = ""
        for token in tokens:
            candidate = token if not current else current + sep + token
            if text_size(draw, candidate, fnt)[0] <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = token
        if current:
            lines.append(current)
    return lines


def fit_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    max_height: int,
    start: int,
    minimum: int,
    bold: bool = True,
    line_gap: int = 8,
) -> ImageFont.FreeTypeFont:
    for size in range(start, minimum - 1, -2):
        trial = font(size, bold)
        lines = wrap_text(draw, text, trial, max_width)
        total_h = len(lines) * size + max(0, len(lines) - 1) * line_gap
        if total_h <= max_height and all(text_size(draw, line, trial)[0] <= max_width for line in lines):
            return trial
    return font(minimum, bold)


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    text: str,
    x: int,
    y: int,
    max_width: int,
    fnt: ImageFont.FreeTypeFont,
    fill=INK,
    line_gap: int = 8,
) -> int:
    cur_y = y
    for line in wrap_text(draw, text, fnt, max_width):
        draw.text((x, cur_y), line, font=fnt, fill=fill)
        cur_y += fnt.size + line_gap
    return cur_y


def rounded(draw: ImageDraw.ImageDraw, xy, radius: int, fill, outline=None, width: int = 2):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def draw_center(draw: ImageDraw.ImageDraw, text: str, box, fnt: ImageFont.FreeTypeFont, fill=INK):
    x1, y1, x2, y2 = box
    tw, th = text_size(draw, text, fnt)
    draw.text((x1 + (x2 - x1 - tw) / 2, y1 + (y2 - y1 - th) / 2), text, font=fnt, fill=fill)


def gradient_bg() -> Image.Image:
    img = Image.new("RGB", (W, H), PAPER_TOP)
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / (H - 1)
        color = tuple(int(PAPER_TOP[i] + (PAPER_BOTTOM[i] - PAPER_TOP[i]) * t) for i in range(3))
        draw.line((0, y, W, y), fill=color)
    return img


def base_slide(title: str, eyebrow: str = "知覚動詞・使役動詞 + O + 原形不定詞") -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = gradient_bg()
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, W, 112), fill=NAVY)
    draw.rectangle((0, 106, W, 112), fill=ORANGE)
    draw.text((70, 28), "H6", font=F_H3, fill=(219, 234, 254))
    draw.text((160, 25), eyebrow, font=F_TITLE, fill=WHITE)
    draw.text((120, 152), title, font=F_H1, fill=INK)
    return img, draw


def draw_note(draw: ImageDraw.ImageDraw, text: str, xy, color=BLUE, fill=(239, 246, 255)):
    x1, y1, x2, y2 = xy
    rounded(draw, xy, 20, fill=fill, outline=(191, 219, 254), width=3)
    fnt = fit_font(draw, text, x2 - x1 - 54, y2 - y1 - 34, 30, 21, bold=True)
    draw_wrapped(draw, text, x1 + 28, y1 + 20, x2 - x1 - 56, fnt, fill=color, line_gap=7)


def draw_en_ja_card(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, en: str, ja: str, accent=BLUE):
    rounded(draw, (x, y, x + w, y + h), 18, fill=CARD, outline=BORDER, width=2)
    draw.rectangle((x, y, x + 10, y + h), fill=accent)
    en_font = fit_font(draw, en, w - 70, int(h * 0.42), 38, 23, bold=True, line_gap=4)
    ja_font = fit_font(draw, ja, w - 70, int(h * 0.32), 25, 18, bold=False, line_gap=4)
    draw_wrapped(draw, en, x + 38, y + 18, w - 70, en_font, fill=INK, line_gap=5)
    draw_wrapped(draw, ja, x + 38, y + h - ja_font.size - 25, w - 70, ja_font, fill=MUTED, line_gap=4)


def draw_formula_tokens(draw: ImageDraw.ImageDraw, tokens: list[tuple[str, tuple[int, int, int]]], x: int, y: int, h: int = 92):
    cur_x = x
    for idx, (label, color) in enumerate(tokens):
        if label == "+":
            draw.text((cur_x + 8, y + 22), "+", font=F_H2, fill=MUTED)
            cur_x += 56
            continue
        width = max(130, text_size(draw, label, F_H3)[0] + 62)
        rounded(draw, (cur_x, y, cur_x + width, y + h), 20, fill=WHITE, outline=color, width=4)
        draw_center(draw, label, (cur_x, y + 4, cur_x + width, y + h - 4), F_H3, fill=color)
        cur_x += width + 20


def draw_role_table(draw: ImageDraw.ImageDraw, roles: list[RolePart], x: int, y: int, w: int, row_h: int = 88):
    col_w = [150, int(w * 0.37), int(w * 0.45)]
    headers = [("役割", MUTED), ("本文の語句", INK), ("読み方", INK)]
    cur_x = x
    for i, (header, color) in enumerate(headers):
        rounded(draw, (cur_x, y, cur_x + col_w[i] - 10, y + 56), 12, fill=(241, 245, 249), outline=BORDER, width=2)
        draw_center(draw, header, (cur_x, y, cur_x + col_w[i] - 10, y + 56), F_LABEL, fill=color)
        cur_x += col_w[i]
    y += 70
    for part in roles:
        role_color = ROLE_COLORS.get(part.role, MUTED)
        cur_x = x
        rounded(draw, (cur_x, y, cur_x + col_w[0] - 10, y + row_h), 14, fill=role_color, outline=role_color, width=2)
        draw_center(draw, part.role, (cur_x, y, cur_x + col_w[0] - 10, y + row_h), F_H2, fill=WHITE)
        cur_x += col_w[0]
        rounded(draw, (cur_x, y, cur_x + col_w[1] - 10, y + row_h), 14, fill=WHITE, outline=BORDER, width=2)
        en_font = fit_font(draw, part.en, col_w[1] - 46, row_h - 26, 30, 21, bold=True)
        draw_wrapped(draw, part.en, cur_x + 22, y + 22, col_w[1] - 46, en_font, fill=INK, line_gap=4)
        cur_x += col_w[1]
        rounded(draw, (cur_x, y, cur_x + col_w[2], y + row_h), 14, fill=(248, 250, 252), outline=BORDER, width=2)
        ja_font = fit_font(draw, part.ja, col_w[2] - 46, row_h - 26, 26, 18, bold=False)
        draw_wrapped(draw, part.ja, cur_x + 22, y + 22, col_w[2] - 46, ja_font, fill=INK, line_gap=4)
        y += row_h + 16


def draw_relation(draw: ImageDraw.ImageDraw, left: str, right: str, y: int, caption: str):
    x = 330
    rounded(draw, (x, y, x + 1260, y + 180), 24, fill=SLATE, outline=ORANGE, width=4)
    draw_center(draw, left, (x + 80, y + 36, x + 460, y + 106), F_H2, fill=WHITE)
    draw.line((x + 500, y + 76, x + 760, y + 76), fill=ORANGE, width=8)
    draw.polygon([(x + 760, y + 76), (x + 732, y + 56), (x + 732, y + 96)], fill=ORANGE)
    draw_center(draw, right, (x + 820, y + 36, x + 1180, y + 106), F_H2, fill=WHITE)
    draw_center(draw, caption, (x + 50, y + 112, x + 1210, y + 164), F_BODY, fill=(226, 232, 240))


def slide_intro() -> Image.Image:
    img, draw = base_slide("O が何をするのかまで読む")
    draw_formula_tokens(
        draw,
        [("S", BLUE), ("+", MUTED), ("知覚/使役V", RED), ("+", MUTED), ("O", GREEN), ("+", MUTED), ("原形", ORANGE)],
        260,
        305,
    )
    draw_note(draw, "目的語 O の後ろに、その人・物の動作を原形で置く。", (260, 470, 1660, 580), color=INK)
    draw_relation(draw, "O", "動詞の原形", 660, "O がその動作をする、という関係を文の中に入れる")
    return img


def slide_meanings() -> Image.Image:
    img, draw = base_slide("意味は大きく2つ")
    draw_formula_tokens(
        draw,
        [("S", BLUE), ("+", MUTED), ("知覚/使役V", RED), ("+", MUTED), ("O", GREEN), ("+", MUTED), ("原形", ORANGE)],
        220,
        245,
    )
    cards = [
        ("知覚動詞", "O が〜するのを見る・聞く・感じる・気づく", "see / hear / feel / notice", BLUE),
        ("使役動詞", "O に〜させる・してもらう・させておく", "make / have / let", GREEN),
    ]
    for i, (head, body, examples, color) in enumerate(cards):
        x = 220 + i * 760
        rounded(draw, (x, 430, x + 700, 740), 28, fill=CARD, outline=color, width=4)
        draw.text((x + 42, 462), head, font=F_H2, fill=color)
        draw_wrapped(draw, body, x + 42, 535, 610, F_BODY_BOLD, fill=INK, line_gap=10)
        rounded(draw, (x + 42, 640, x + 658, 700), 16, fill=(248, 250, 252), outline=BORDER, width=2)
        draw_center(draw, examples, (x + 42, 640, x + 658, 700), F_EN_SMALL, fill=INK)
    draw_note(draw, "to を置かずに、動詞の原形を直接置くのが中心です。", (360, 820, 1560, 930), color=RED, fill=(254, 242, 242))
    return img


def slide_example_notice() -> Image.Image:
    img, draw = base_slide("本文の例：知覚動詞 notice")
    draw_en_ja_card(
        draw,
        190,
        260,
        1540,
        160,
        "I could notice petals drift on the wind.",
        "私は花びらが風に乗って漂うのに気づくことができた。",
        BLUE,
    )
    draw_role_table(
        draw,
        [
            RolePart("S", "I", "私は"),
            RolePart("V", "could notice", "気づくことができた"),
            RolePart("O", "petals", "花びらが"),
            RolePart("C", "drift", "漂う"),
            RolePart("M", "on the wind", "風に乗って"),
        ],
        220,
        485,
        1480,
        row_h=70,
    )
    return img


def slide_notice_relation() -> Image.Image:
    img, draw = base_slide("大事なのは、誰が drift するか")
    draw_en_ja_card(
        draw,
        240,
        250,
        1440,
        140,
        "I could notice petals drift on the wind.",
        "花びらが漂うのに気づいた。",
        BLUE,
    )
    draw_relation(draw, "petals", "drift", 455, "漂うのは I ではなく petals")
    draw_note(draw, "petals drift という小さな「主語＋動詞」の関係が、notice の後ろに入っています。", (270, 710, 1650, 840), color=INK)
    return img


def slide_example_hear() -> Image.Image:
    img, draw = base_slide("本文の例：知覚動詞 hear")
    draw_en_ja_card(
        draw,
        170,
        245,
        1580,
        158,
        "I could hear a distant bird sing beyond the hedge.",
        "私は遠くの鳥が垣根の向こうで鳴くのを聞くことができた。",
        BLUE,
    )
    draw_role_table(
        draw,
        [
            RolePart("S", "I", "私は"),
            RolePart("V", "could hear", "聞くことができた"),
            RolePart("O", "a distant bird", "遠くの鳥が"),
            RolePart("C", "sing", "鳴く"),
            RolePart("M", "beyond the hedge", "垣根の向こうで"),
        ],
        220,
        470,
        1480,
        row_h=72,
    )
    return img


def slide_hear_relation() -> Image.Image:
    img, draw = base_slide("hear + O + 原形")
    draw_formula_tokens(draw, [("hear", RED), ("+", MUTED), ("O", GREEN), ("+", MUTED), ("原形", ORANGE)], 470, 245)
    draw_relation(draw, "a distant bird", "sing", 420, "鳥が鳴く、という関係を聞いた")
    draw_note(draw, "hear の後ろでは、O がする動作を to なしの原形で置きます。", (300, 705, 1620, 835), color=INK)
    return img


def slide_causative_intro() -> Image.Image:
    img, draw = base_slide("本文の例：使役動詞")
    draw_formula_tokens(draw, [("使役V", RED), ("+", MUTED), ("O", GREEN), ("+", MUTED), ("原形", ORANGE)], 520, 245)
    cards = [
        ("make", "強くさせる"),
        ("have", "してもらう・立場上させる"),
        ("let", "許す・させておく"),
    ]
    for i, (en, ja) in enumerate(cards):
        x = 230 + i * 500
        rounded(draw, (x, 435, x + 430, 660), 24, fill=CARD, outline=[RED, GREEN, BLUE][i], width=4)
        draw_center(draw, en, (x + 20, 475, x + 410, 545), F_H2, fill=[RED, GREEN, BLUE][i])
        draw_center(draw, ja, (x + 20, 570, x + 410, 625), F_BODY, fill=INK)
    draw_note(draw, "ここでも、O の後ろは基本的に動詞の原形です。", (360, 780, 1560, 900), color=RED, fill=(254, 242, 242))
    return img


def slide_had_example() -> Image.Image:
    img, draw = base_slide("have：O に〜させる・してもらう")
    draw_en_ja_card(
        draw,
        260,
        245,
        1400,
        150,
        "Grandmother had me hold the cup.",
        "祖母は私にカップを持たせた。",
        GREEN,
    )
    draw_role_table(
        draw,
        [
            RolePart("S", "Grandmother", "祖母は"),
            RolePart("V", "had", "させた・してもらった"),
            RolePart("O", "me", "私に"),
            RolePart("C", "hold the cup", "カップを持つ"),
        ],
        250,
        470,
        1420,
        row_h=86,
    )
    return img


def slide_had_relation() -> Image.Image:
    img, draw = base_slide("had me hold の読み方")
    draw_relation(draw, "me", "hold the cup", 290, "私がカップを持つ")
    draw_note(draw, "had me hold は「私に持たせた」または「私に持ってもらった」という意味です。", (280, 540, 1640, 660), color=INK)
    draw_note(draw, "hold に to はつけません。", (520, 740, 1400, 850), color=RED, fill=(254, 242, 242))
    return img


def slide_let_example() -> Image.Image:
    img, draw = base_slide("let：O が〜するのを許す")
    draw_en_ja_card(
        draw,
        210,
        235,
        1500,
        150,
        "Today she let me rest as long as I wanted.",
        "今日、彼女は私が望むだけ休ませてくれた。",
        BLUE,
    )
    draw_role_table(
        draw,
        [
            RolePart("S", "she", "彼女は"),
            RolePart("V", "let", "許した・休ませてくれた"),
            RolePart("O", "me", "私に"),
            RolePart("C", "rest", "休む"),
            RolePart("M", "as long as I wanted", "私が望むだけ"),
        ],
        220,
        455,
        1480,
        row_h=72,
    )
    return img


def slide_let_relation() -> Image.Image:
    img, draw = base_slide("let me rest、to は入れない")
    draw_relation(draw, "me", "rest", 285, "私が休む")
    x = 280
    y = 560
    pairs = [
        ("let me rest", "正しい"),
        ("let me to rest", "この形では使わない"),
    ]
    for i, (en, ja) in enumerate(pairs):
        color = GREEN if i == 0 else RED
        rounded(draw, (x, y + i * 125, x + 1360, y + 95 + i * 125), 20, fill=CARD, outline=color, width=4)
        draw.text((x + 40, y + 25 + i * 125), en, font=F_EN, fill=INK)
        draw_center(draw, ja, (x + 760, y + 18 + i * 125, x + 1320, y + 78 + i * 125), F_BODY_BOLD, fill=color)
    return img


def slide_build_steps() -> Image.Image:
    img, draw = base_slide("作り方：4つの位置で考える")
    steps = [
        ("1", "主語", "I / Grandmother / she"),
        ("2", "知覚動詞・使役動詞", "hear / notice / have / let / make"),
        ("3", "動作する人・物", "a distant bird / petals / me"),
        ("4", "その動作を原形で置く", "sing / drift / hold / rest / stay"),
    ]
    for i, (num, head, examples) in enumerate(steps):
        x = 140 + i * 440
        rounded(draw, (x, 275, x + 390, 760), 24, fill=CARD, outline=[BLUE, RED, GREEN, ORANGE][i], width=4)
        draw.ellipse((x + 26, 303, x + 94, 371), fill=[BLUE, RED, GREEN, ORANGE][i])
        draw_center(draw, num, (x + 28, 308, x + 92, 372), F_H2, fill=WHITE)
        draw_wrapped(draw, head, x + 38, 420, 320, F_H3, fill=INK, line_gap=9)
        rounded(draw, (x + 34, 595, x + 356, 710), 16, fill=(248, 250, 252), outline=BORDER, width=2)
        ex_font = fit_font(draw, examples, 270, 70, 26, 19, bold=True)
        draw_wrapped(draw, examples, x + 60, 623, 270, ex_font, fill=MUTED, line_gap=5)
    draw_note(draw, "文型ではなくても、O とその動作の順番を見ると作れます。", (330, 840, 1590, 940), color=INK)
    return img


def slide_embedded_example() -> Image.Image:
    img, draw = base_slide("本文の応用例：大きな文の中に入る")
    draw_en_ja_card(
        draw,
        180,
        245,
        1560,
        160,
        "I wished she would let me stay on the porch forever.",
        "私は彼女が私をずっと縁側にいさせてくれたらいいのにと思った。",
        PURPLE,
    )
    draw_note(draw, "文全体の中心は「私は願った」ですが、後ろの節の中に H6 の形があります。", (250, 475, 1670, 590), color=INK)
    draw_en_ja_card(
        draw,
        320,
        675,
        1280,
        130,
        "she would let me stay on the porch forever",
        "彼女が私をずっと縁側にいさせてくれる",
        BLUE,
    )
    return img


def slide_embedded_breakdown() -> Image.Image:
    img, draw = base_slide("後ろの節だけを分解する")
    draw_role_table(
        draw,
        [
            RolePart("S", "she", "彼女は"),
            RolePart("V", "would let", "させてくれるだろう"),
            RolePart("O", "me", "私に"),
            RolePart("C", "stay", "いる・とどまる"),
            RolePart("M", "on the porch forever", "ずっと縁側に"),
        ],
        230,
        255,
        1460,
        row_h=76,
    )
    draw_relation(draw, "me", "stay", 760, "私がいる、という関係")
    return img


def slide_ing_intro() -> Image.Image:
    img, draw = base_slide("-ing との違い")
    draw_en_ja_card(
        draw,
        180,
        245,
        1560,
        160,
        "I observed the trees in the garden swaying slowly.",
        "私は庭の木々がゆっくり揺れているのを観察した。",
        YELLOW,
    )
    draw_role_table(
        draw,
        [
            RolePart("O", "the trees in the garden", "庭の木々が"),
            RolePart("C", "swaying slowly", "ゆっくり揺れている"),
        ],
        360,
        500,
        1200,
        row_h=100,
    )
    draw_note(draw, "-ing は、動作の途中・進行中の様子に注目します。", (350, 800, 1570, 910), color=INK)
    return img


def slide_ing_compare() -> Image.Image:
    img, draw = base_slide("原形と -ing の見え方")
    draw_en_ja_card(draw, 210, 275, 1500, 145, "I heard a bird sing.", "鳥が鳴くのを聞いた。", BLUE)
    draw_note(draw, "原形：動作そのものをシンプルにとらえる", (310, 455, 1610, 555), color=BLUE)
    draw_en_ja_card(draw, 210, 640, 1500, 145, "I observed trees swaying.", "木々が揺れている様子を観察した。", YELLOW)
    draw_note(draw, "-ing：進行中の様子に注目する", (310, 820, 1610, 920), color=ORANGE, fill=(255, 247, 237))
    return img


def slide_to_verbs() -> Image.Image:
    img, draw = base_slide("to が必要な動詞との違い")
    draw_en_ja_card(
        draw,
        160,
        235,
        1600,
        135,
        "She always permits me to read any book I like.",
        "彼女はいつも、私が好きな本を読むことを許してくれる。",
        PURPLE,
    )
    draw_en_ja_card(
        draw,
        160,
        415,
        1600,
        125,
        "allow the wind to carry you",
        "風があなたを運ぶのを許しなさい",
        PURPLE,
    )
    draw_en_ja_card(
        draw,
        160,
        585,
        1600,
        125,
        "encourage me to remember him",
        "私に彼のことを思い出すよう促す",
        PURPLE,
    )
    draw_note(draw, "permit / allow / encourage / want などは、ふつう O + to V を取ります。", (250, 800, 1670, 915), color=INK)
    return img


def slide_correct_forms() -> Image.Image:
    img, draw = base_slide("似ていても、型が違う")
    rows = [
        ("let me rest", "正しい：let は原形"),
        ("permit me to read", "正しい：permit は to V"),
        ("allow the wind to carry you", "正しい：allow は to V"),
        ("encourage me to remember him", "正しい：encourage は to V"),
    ]
    y = 260
    for i, (en, ja) in enumerate(rows):
        color = GREEN if i == 0 else PURPLE
        rounded(draw, (220, y, 1700, y + 118), 20, fill=CARD, outline=color, width=3)
        draw.text((260, y + 24), en, font=F_EN_SMALL, fill=INK)
        draw.text((970, y + 34), ja, font=F_BODY, fill=color)
        y += 145
    return img


def slide_summary_patterns() -> Image.Image:
    img, draw = base_slide("まとめ：H6 の中心")
    groups = [
        ("知覚動詞 + O + 原形", [("hear a bird sing", "鳥が鳴くのを聞く"), ("notice petals drift", "花びらが漂うのに気づく")], BLUE),
        ("使役動詞 + O + 原形", [("had me hold the cup", "私にカップを持たせた"), ("let me rest", "私を休ませてくれた"), ("let me stay", "私をいさせてくれた")], GREEN),
    ]
    for i, (head, examples, color) in enumerate(groups):
        x = 180 + i * 790
        rounded(draw, (x, 245, x + 730, 760), 28, fill=CARD, outline=color, width=4)
        draw.text((x + 38, 285), head, font=F_H3, fill=color)
        cur_y = 370
        for en, ja in examples:
            draw_en_ja_card(draw, x + 42, cur_y, 646, 105, en, ja, color)
            cur_y += 125
    draw_note(draw, "意味の中心は、O がその動作をする、という関係です。", (360, 835, 1560, 935), color=INK)
    return img


def slide_final() -> Image.Image:
    img, draw = base_slide("最後に見るところ")
    draw_relation(draw, "O", "C の原形", 260, "O が C する")
    examples = [
        ("me hold", "私が持つ"),
        ("me rest", "私が休む"),
        ("bird sing", "鳥が鳴く"),
        ("petals drift", "花びらが漂う"),
    ]
    for i, (en, ja) in enumerate(examples):
        x = 260 + (i % 2) * 720
        y = 570 + (i // 2) * 150
        draw_en_ja_card(draw, x, y, 620, 110, en, ja, ORANGE)
    draw_note(draw, "この小さな関係を見つけると、長い本文でも読みやすくなります。", (360, 895, 1560, 985), color=INK)
    return img


STEPS: list[Step] = [
    Step(
        "intro",
        slide_intro,
        (
            JP("今回は、知覚動詞と使役動詞のあとに、目的語と動詞の原形が続く形を見ます。"),
            JP("ポイントは、目的語がその動作をする、という関係を文の中に見つけることです。"),
        ),
    ),
    Step(
        "meanings",
        slide_meanings,
        (
            JP("基本形はこの並びです。"),
            EN("S plus perception verb or causative verb plus O plus base verb."),
            JP("知覚動詞なら、目的語が何かをするのを見る、聞く、感じる、気づく、という意味です。"),
            JP("使役動詞なら、目的語に何かをさせる、してもらう、させておく、という意味です。"),
            JP("では、本文の例で見ていきます。"),
        ),
    ),
    Step(
        "notice_example",
        slide_example_notice,
        (
            JP("本文の知覚動詞の例です。まず英文を聞きます。"),
            EN("I could notice petals drift on the wind."),
            JP("意味は、私は花びらが風に乗って漂うのに気づくことができた、です。"),
            JP("分解すると、"),
            EN("I"),
            JP("が主語。"),
            EN("could notice"),
            JP("が動詞。"),
            EN("petals"),
            JP("が目的語。"),
            EN("drift"),
            JP("が補語。"),
            EN("on the wind"),
            JP("が修飾語です。"),
        ),
    ),
    Step(
        "notice_relation",
        slide_notice_relation,
        (
            JP("ここで大事なのは、漂うのが、私ではなく、"),
            EN("petals"),
            JP("だという点です。"),
            EN("petals drift"),
            JP("という関係が、文の中に入っています。"),
            JP("次は、聞く、の例で同じ形を確認します。"),
        ),
    ),
    Step(
        "hear_example",
        slide_example_hear,
        (
            JP("もう一つ、本文の知覚動詞の例です。"),
            EN("I could hear a distant bird sing beyond the hedge."),
            JP("意味は、私は遠くの鳥が垣根の向こうで鳴くのを聞くことができた、です。"),
            EN("I"),
            JP("が主語。"),
            EN("could hear"),
            JP("が動詞。"),
            EN("a distant bird"),
            JP("が目的語。"),
            EN("sing"),
            JP("が補語。"),
            EN("beyond the hedge"),
            JP("が修飾語です。"),
        ),
    ),
    Step(
        "hear_relation",
        slide_hear_relation,
        (
            EN("hear"),
            JP("プラス目的語プラス原形なので、"),
            EN("a distant bird sing"),
            JP("つまり、鳥が鳴く、という関係を聞いた形です。"),
            JP("次は、使役動詞の例に移ります。"),
        ),
    ),
    Step(
        "causative_intro",
        slide_causative_intro,
        (
            JP("使役動詞も、同じように目的語の動作を原形で置きます。"),
            EN("make"),
            JP("は強くさせる。"),
            EN("have"),
            JP("は、してもらう、立場上させる。"),
            EN("let"),
            JP("は、許す、させておく、という感じです。"),
        ),
    ),
    Step(
        "had_example",
        slide_had_example,
        (
            JP("本文の例です。"),
            EN("Grandmother had me hold the cup."),
            JP("意味は、祖母は私にカップを持たせた、です。"),
            EN("Grandmother"),
            JP("が主語。"),
            EN("had"),
            JP("が動詞。"),
            EN("me"),
            JP("が目的語。"),
            EN("hold the cup"),
            JP("が補語です。"),
        ),
    ),
    Step(
        "had_relation",
        slide_had_relation,
        (
            EN("had me hold"),
            JP("は、私に持たせた、または、私に持ってもらった、という意味です。"),
            JP("この形では、"),
            EN("hold"),
            JP("に、"),
            EN("to"),
            JP("はつけません。"),
            JP("次は、許可を表す使役動詞を見ます。"),
        ),
    ),
    Step(
        "let_example",
        slide_let_example,
        (
            JP("次の本文例です。"),
            EN("Today she let me rest as long as I wanted."),
            JP("意味は、今日、彼女は私が望むだけ休ませてくれた、です。"),
            EN("she"),
            JP("が主語。"),
            EN("let"),
            JP("が動詞。"),
            EN("me"),
            JP("が目的語。"),
            EN("rest"),
            JP("が補語です。"),
        ),
    ),
    Step(
        "let_relation",
        slide_let_relation,
        (
            EN("let me rest"),
            JP("は、私に休むことを許した、休ませてくれた、という意味です。"),
            JP("これも、"),
            EN("let me to rest"),
            JP("ではなく、"),
            EN("let me rest"),
            JP("です。"),
            JP("ここまでを、作り方として整理します。"),
        ),
    ),
    Step(
        "build_steps",
        slide_build_steps,
        (
            JP("作るときは、四つの位置で考えます。"),
            JP("一つ目は主語。例は、"),
            EN("I, Grandmother, she."),
            JP("二つ目は、知覚動詞または使役動詞。例は、"),
            EN("hear, notice, have, let, make."),
            JP("三つ目は、動作する人や物。例は、"),
            EN("a distant bird, petals, me."),
            JP("四つ目は、その人や物の動作を、動詞の原形で置きます。例は、"),
            EN("sing, drift, hold, rest, stay."),
        ),
    ),
    Step(
        "embedded_example",
        slide_embedded_example,
        (
            JP("本文には、大きな文の中にこの形が入る例もあります。"),
            EN("I wished she would let me stay on the porch forever."),
            JP("意味は、私は彼女が私をずっと縁側にいさせてくれたらいいのにと思った、です。"),
            JP("文全体の中心は、私は願った、ですが、後ろの節の中に形があります。"),
            EN("she would let me stay on the porch forever"),
        ),
    ),
    Step(
        "embedded_breakdown",
        slide_embedded_breakdown,
        (
            JP("後ろの節だけを分解します。"),
            EN("she"),
            JP("が主語。"),
            EN("would let"),
            JP("が動詞。"),
            EN("me"),
            JP("が目的語。"),
            EN("stay"),
            JP("が補語。"),
            EN("on the porch forever"),
            JP("が修飾語です。"),
            EN("me stay"),
            JP("で、私がいる、という関係です。"),
        ),
    ),
    Step(
        "ing_intro",
        slide_ing_intro,
        (
            JP("ここで、原形ではなく、現在分詞を使う文も確認しておきます。"),
            EN("I observed the trees in the garden swaying slowly."),
            JP("意味は、私は庭の木々がゆっくり揺れているのを観察した、です。"),
            EN("the trees in the garden"),
            JP("が目的語。"),
            EN("swaying slowly"),
            JP("が補語です。"),
            JP("現在分詞を使うと、動作の途中、進行中の様子に注目します。"),
        ),
    ),
    Step(
        "ing_compare",
        slide_ing_compare,
        (
            JP("原形と現在分詞の違いを比べます。"),
            EN("I heard a bird sing."),
            JP("鳥が鳴くのを聞いた。原形は、動作そのものをシンプルにとらえます。"),
            EN("I observed trees swaying."),
            JP("木々が揺れている様子を観察した。現在分詞は、進行中の様子に注目します。"),
            JP("次は、形が似ているけれど、"),
            EN("to"),
            JP("が必要な動詞との違いです。"),
        ),
    ),
    Step(
        "to_verbs",
        slide_to_verbs,
        (
            JP("本文には、似ているけれど、"),
            EN("to"),
            JP("が必要な動詞も出ています。"),
            EN("She always permits me to read any book I like."),
            JP("彼女はいつも、私が好きな本を読むことを許してくれる。"),
            EN("allow the wind to carry you"),
            JP("風があなたを運ぶのを許しなさい。"),
            EN("encourage me to remember him"),
            JP("私に彼のことを思い出すよう促す。"),
        ),
    ),
    Step(
        "correct_forms",
        slide_correct_forms,
        (
            EN("permit, allow, encourage, want"),
            JP("などは、ふつう、目的語のあとに、"),
            EN("to V"),
            JP("を取ります。"),
            EN("let me rest"),
            JP("は正しい。"),
            EN("permit me to read"),
            JP("も正しい。"),
            EN("allow the wind to carry you"),
            JP("も正しい。"),
            EN("encourage me to remember him"),
            JP("も正しい。"),
        ),
    ),
    Step(
        "summary_patterns",
        slide_summary_patterns,
        (
            JP("まとめます。知覚動詞の形は、目的語プラス原形です。"),
            EN("hear a bird sing"),
            JP("鳥が鳴くのを聞く。"),
            EN("notice petals drift"),
            JP("花びらが漂うのに気づく。"),
            JP("使役動詞の形も、目的語プラス原形です。"),
            EN("had me hold the cup"),
            JP("私にカップを持たせた。"),
            EN("let me rest"),
            JP("私を休ませてくれた。"),
            EN("let me stay"),
            JP("私をいさせてくれた。"),
        ),
    ),
    Step(
        "final_relation",
        slide_final,
        (
            JP("最後に、見るところはここです。"),
            EN("me hold"),
            JP("私が持つ。"),
            EN("me rest"),
            JP("私が休む。"),
            EN("bird sing"),
            JP("鳥が鳴く。"),
            EN("petals drift"),
            JP("花びらが漂う。"),
            JP("目的語と補語の間に、主語と動詞のような関係がある、と考えると、長い本文でも読みやすくなります。"),
        ),
    ),
]


def normalize_wav(src: Path, dst: Path):
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(src),
            "-ar",
            "48000",
            "-ac",
            "1",
            "-filter:a",
            "loudnorm=I=-18:TP=-2:LRA=11",
            "-c:a",
            "pcm_s16le",
            str(dst),
        ]
    )


def make_silence(path: Path, seconds: float):
    run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "anullsrc=r=48000:cl=mono",
            "-t",
            f"{seconds:.2f}",
            "-c:a",
            "pcm_s16le",
            str(path),
        ]
    )


def voicepeak(text: str, out_path: Path):
    env = os.environ.copy()
    env["LC_ALL"] = "ja_JP.UTF-8"
    env["LANG"] = "ja_JP.UTF-8"
    raw = out_path.with_name(out_path.stem + "_raw.wav")
    last_result = None
    timeout_message = ""
    for attempt in range(4):
        raw.unlink(missing_ok=True)
        try:
            result = subprocess.run(
                [VOICEPEAK, "-s", text, "-n", NARRATOR, "-o", str(raw), "--speed", "94", "--pitch", "0"],
                capture_output=True,
                text=True,
                env=env,
                timeout=55,
            )
        except subprocess.TimeoutExpired:
            timeout_message = f"VOICEPEAK timed out: {text}"
            time.sleep(1.2 + attempt)
            continue
        if result.returncode == 0 and raw.exists() and raw.stat().st_size > 1024:
            normalize_wav(raw, out_path)
            return
        last_result = result
        time.sleep(1.2 + attempt)
    raise RuntimeError(
        "VOICEPEAK failed\n"
        + timeout_message
        + "\n"
        + ((last_result.stderr if last_result else "")[-2000:])
        + ((last_result.stdout if last_result else "")[-1000:])
    )


def say_english(text: str, out_path: Path):
    raw = out_path.with_suffix(".aiff")
    raw.unlink(missing_ok=True)
    out_path.unlink(missing_ok=True)
    run(["say", "-v", EN_VOICE, "-r", "146", "-o", str(raw), text])
    normalize_wav(raw, out_path)
    raw.unlink(missing_ok=True)


def audio_duration(path: Path) -> float:
    result = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ]
    )
    return float(result.stdout.strip())


def event_cache_path(event: AudioEvent) -> Path:
    key = f"{AUDIO_VERSION}:{event.kind}:{NARRATOR}:{EN_VOICE}:{event.text}:{event.seconds}".encode("utf-8")
    digest = hashlib.sha1(key).hexdigest()[:16]
    return AUDIO_DIR / f"{event.kind}_{digest}.wav"


def build_event_audio(event: AudioEvent) -> Path:
    out = event_cache_path(event)
    if out.exists() and out.stat().st_size > 1024:
        return out
    if event.kind == "jp":
        voicepeak(event.text, out)
    elif event.kind == "en":
        say_english(event.text, out)
    elif event.kind == "pause":
        make_silence(out, event.seconds or 0.25)
    else:
        raise ValueError(event.kind)
    return out


def concat_wavs(parts: list[Path], out_path: Path):
    concat_file = out_path.with_name(out_path.stem + "_concat.txt")
    concat_file.write_text("".join(f"file '{part.resolve()}'\n" for part in parts), encoding="utf-8")
    run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_file),
            "-ar",
            "48000",
            "-ac",
            "1",
            "-c:a",
            "pcm_s16le",
            str(out_path),
        ]
    )


def step_cache_name(step: Step) -> str:
    key = "|".join(f"{ev.kind}:{ev.text}:{ev.seconds}" for ev in step.events)
    digest = hashlib.sha1(f"{AUDIO_VERSION}:{step.name}:{key}".encode("utf-8")).hexdigest()[:16]
    return f"{step.name}_{digest}.wav"


def build_step_audio(step: Step) -> tuple[Path, float]:
    out = AUDIO_DIR / step_cache_name(step)
    if out.exists() and out.stat().st_size > 1024:
        return out, audio_duration(out)
    parts: list[Path] = []
    for index, event in enumerate(step.events):
        parts.append(build_event_audio(event))
        if event.kind != "pause" and index < len(step.events) - 1:
            parts.append(build_event_audio(PAUSE(0.14 if event.kind == "en" else 0.18)))
    concat_wavs(parts, out)
    return out, audio_duration(out)


def build_video():
    if not Path(VOICEPEAK).exists():
        raise FileNotFoundError(VOICEPEAK)
    for d in (FRAME_DIR, AUDIO_DIR, CLIP_DIR):
        d.mkdir(parents=True, exist_ok=True)

    clips: list[Path] = []
    durations: list[float] = []
    print(f"=== Build H6 line-19976 explainer ({len(STEPS)} slides) ===", flush=True)
    for idx, step in enumerate(STEPS):
        print(f"[{idx + 1}/{len(STEPS)}] {step.name}", flush=True)
        frame = step.render()
        frame_path = FRAME_DIR / f"frame_{idx:03d}_{step.name}.png"
        frame.save(frame_path)

        audio_path, duration = build_step_audio(step)
        duration += 0.22
        durations.append(duration)

        clip_path = CLIP_DIR / f"clip_{idx:03d}_{step.name}.mp4"
        run(
            [
                "ffmpeg",
                "-y",
                "-loop",
                "1",
                "-framerate",
                str(FPS),
                "-i",
                str(frame_path),
                "-i",
                str(audio_path),
                "-t",
                f"{duration:.3f}",
                "-vf",
                f"scale={W}:{H},format=yuv420p",
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-crf",
                "20",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-movflags",
                "+faststart",
                "-shortest",
                str(clip_path),
            ]
        )
        clips.append(clip_path)

    concat = OUT_DIR / "concat.txt"
    concat.write_text("".join(f"file '{clip.resolve()}'\n" for clip in clips), encoding="utf-8")
    tmp = OUT_VIDEO.with_suffix(".tmp.mp4")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", str(tmp)])
    shutil.move(str(tmp), str(OUT_VIDEO))
    print(f"Done: {OUT_VIDEO}", flush=True)
    print(f"Duration: {sum(durations):.1f}s", flush=True)
    print(f"Size: {OUT_VIDEO.stat().st_size / 1024 / 1024:.1f} MB", flush=True)


if __name__ == "__main__":
    build_video()
