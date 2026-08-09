"""Build a plain H3 SVO explainer video.

This version intentionally does not use Teacher Tacos. It starts with
questions and use scenes, then simulates a flip-board by switching a series of
short visual steps. Spoken lines are not shown in a bottom caption strip; the
slides themselves carry the visual explanation.
"""
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "tmp_h3_svo_plain"
FRAME_DIR = OUT_DIR / "frames"
AUDIO_DIR = OUT_DIR / "audio"
CLIP_DIR = OUT_DIR / "clips"
OUT_VIDEO = ROOT / "h3_svo_plain_explainer.mp4"

VOICEPEAK = "/Applications/voicepeak.app/Contents/MacOS/voicepeak"
NARRATOR = "Japanese Male 2"
EN_VOICE = "Daniel"

W, H = 1920, 1080
CONTENT_H = H
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
YELLOW = (245, 158, 11)
PURPLE = (124, 58, 237)
PAPER = (250, 247, 239)
PAPER_BLUE = (239, 246, 255)
CARD = (255, 255, 255)
BORDER = (226, 232, 240)
WHITE = (255, 255, 255)
SLATE = (15, 23, 42)

ROLE_COLORS = {"S": BLUE, "V": RED, "O": GREEN, "C": YELLOW, "M": MUTED}


def font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REGULAR, size)


F_TITLE = font(70)
F_H1 = font(58)
F_H2 = font(42)
F_H3 = font(34)
F_BODY = font(30, bold=False)
F_SMALL = font(23, bold=False)
F_EN = font(43)
F_EN_SMALL = font(31)
F_LABEL = font(25)


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise RuntimeError("Command failed:\n" + " ".join(cmd) + "\n" + result.stderr[-2500:])
    return result


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def rounded(draw: ImageDraw.ImageDraw, xy, radius: int, fill, outline=None, width: int = 2):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def draw_center(draw: ImageDraw.ImageDraw, text: str, box, fnt, fill=INK):
    x1, y1, x2, y2 = box
    tw, th = text_size(draw, text, fnt)
    draw.text((x1 + (x2 - x1 - tw) / 2, y1 + (y2 - y1 - th) / 2), text, font=fnt, fill=fill)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        current = ""
        tokens = paragraph.split(" ") if " " in paragraph else list(paragraph)
        sep = " " if " " in paragraph else ""
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


def draw_wrapped(draw, text: str, x: int, y: int, max_width: int, fnt, fill=INK, line_gap: int = 10):
    cur_y = y
    for line in wrap_text(draw, text, fnt, max_width):
        draw.text((x, cur_y), line, font=fnt, fill=fill)
        cur_y += fnt.size + line_gap
    return cur_y


def gradient_bg(top=PAPER_BLUE, bottom=(255, 251, 235), height=CONTENT_H) -> Image.Image:
    img = Image.new("RGB", (W, height), top)
    draw = ImageDraw.Draw(img)
    for y in range(height):
        t = y / max(height - 1, 1)
        color = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        draw.line((0, y, W, y), fill=color)
    return img


def add_header(img: Image.Image, section: str, title: str, color=NAVY):
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, W, 106), fill=color)
    draw.text((70, 29), section, font=F_LABEL, fill=(219, 234, 254))
    draw.text((270, 20), title, font=F_H2, fill=WHITE)
    draw.rectangle((0, 104, W, 110), fill=ORANGE)


def role_badge(draw, x: int, y: int, role: str, label: str, color):
    rounded(draw, (x, y, x + 230, y + 120), 18, fill=CARD, outline=color, width=4)
    rounded(draw, (x + 18, y + 22, x + 76, y + 80), 12, fill=color)
    draw_center(draw, role, (x + 18, y + 22, x + 76, y + 80), F_LABEL, fill=WHITE)
    draw_wrapped(draw, label, x + 92, y + 24, 118, F_SMALL, fill=INK, line_gap=4)


def draw_question_panel(draw, japanese: str, english_hint: str):
    rounded(draw, (115, 145, 1805, 350), 30, fill=CARD, outline=(191, 219, 254), width=4)
    draw.text((165, 185), "考えてみよう", font=F_H2, fill=ORANGE)
    draw.text((455, 180), japanese, font=F_H1, fill=INK)
    draw.text((455, 275), english_hint, font=F_BODY, fill=MUTED)


def draw_slots(draw, x: int, y: int, visible: dict[str, str], *, lift_v: bool = False, highlight_o: bool = False):
    slots = [("S", "だれが", "I"), ("V", "どうする", "read"), ("O", "何を", "a book")]
    cur_x = x
    for role, ja, word in slots:
        color = ROLE_COLORS[role]
        rounded(draw, (cur_x, y, cur_x + 420, y + 138), 22, fill=CARD, outline=color, width=4)
        rounded(draw, (cur_x + 20, y + 22, cur_x + 82, y + 84), 14, fill=color)
        draw_center(draw, role, (cur_x + 20, y + 22, cur_x + 82, y + 84), F_H3, fill=WHITE)
        draw.text((cur_x + 105, y + 20), ja, font=F_SMALL, fill=MUTED)
        if role in visible:
            draw.text((cur_x + 105, y + 58), visible[role], font=F_EN, fill=INK)
        else:
            rounded(draw, (cur_x + 106, y + 60, cur_x + 360, y + 108), 13, fill=(241, 245, 249), outline=BORDER, width=2)
            draw_center(draw, "?", (cur_x + 106, y + 60, cur_x + 360, y + 108), F_H3, fill=MUTED)
        if role == "V" and lift_v:
            rounded(draw, (cur_x + 84, y - 52, cur_x + 375, y + 14), 14, fill=(255, 247, 237), outline=ORANGE, width=4)
            draw_center(draw, "動詞カードを外す", (cur_x + 84, y - 52, cur_x + 375, y + 14), F_SMALL, fill=ORANGE)
        if role == "O" and highlight_o:
            draw.arc((cur_x - 20, y - 28, cur_x + 440, y + 160), 10, 350, fill=GREEN, width=7)
        cur_x += 470


def draw_sentence_chunks(draw, x: int, y: int, chunks: list[tuple[str, str, str]]):
    cur_x = x
    for role, text, note in chunks:
        color = ROLE_COLORS[role]
        width = max(235, min(650, text_size(draw, text, F_EN_SMALL)[0] + 130))
        rounded(draw, (cur_x, y, cur_x + width, y + 118), 16, fill=CARD, outline=color, width=4)
        rounded(draw, (cur_x + 18, y + 20, cur_x + 66, y + 68), 10, fill=color)
        draw_center(draw, role, (cur_x + 18, y + 20, cur_x + 66, y + 68), F_LABEL, fill=WHITE)
        draw.text((cur_x + 86, y + 22), text, font=F_EN_SMALL, fill=INK)
        draw.text((cur_x + 86, y + 70), note, font=F_SMALL, fill=MUTED)
        cur_x += width + 24


def slide_title() -> Image.Image:
    img = gradient_bg((239, 246, 255), (255, 251, 235))
    draw = ImageDraw.Draw(img)
    rounded(draw, (95, 110, 1825, 790), 36, fill=(255, 255, 255), outline=(191, 219, 254), width=5)
    draw.text((155, 170), "高校編 H3", font=F_H2, fill=NAVY)
    draw.text((155, 245), "第3文型 SVO", font=F_TITLE, fill=INK)
    draw.text((155, 360), "「何を？」まで届く動作を読む", font=F_H1, fill=ORANGE)
    draw_wrapped(
        draw,
        "第1文型・第2文型で見た「文の骨格」に、動作の相手・対象が加わると第3文型になります。",
        160,
        475,
        1400,
        F_BODY,
        fill=MUTED,
    )
    rounded(draw, (160, 635, 1185, 735), 22, fill=SLATE)
    draw_center(draw, "S  +  V  +  O     だれが → どうする → 何を", (160, 635, 1185, 735), F_H3, fill=WHITE)
    return img


def slide_outlook(stage: int) -> Image.Image:
    img = gradient_bg()
    draw = ImageDraw.Draw(img)
    add_header(img, "Roadmap", "まず、何を読めるようになるのか")
    items = [
        ("1", "場面を想像する", "「何かに働きかける」場面で使う"),
        ("2", "第1・第2との違い", "動作だけか、説明か、対象を持つか"),
        ("3", "フリップボード", "単語を順番に出して骨格を見る"),
        ("4", "本文へ戻す", "H3 の文を S/V/O で読む"),
    ]
    for i, (num, title, body) in enumerate(items):
        x = 135 + (i % 2) * 845
        y = 185 + (i // 2) * 260
        active = i < stage
        fill = CARD if active else (248, 250, 252)
        outline = NAVY if active else BORDER
        rounded(draw, (x, y, x + 760, y + 190), 24, fill=fill, outline=outline, width=4)
        rounded(draw, (x + 36, y + 50, x + 112, y + 126), 18, fill=NAVY if active else MUTED)
        draw_center(draw, num, (x + 36, y + 50, x + 112, y + 126), F_H2, fill=WHITE)
        draw.text((x + 145, y + 42), title, font=F_H2, fill=INK if active else MUTED)
        draw.text((x + 145, y + 106), body, font=F_BODY, fill=MUTED)
    return img


def slide_use_scene(stage: int) -> Image.Image:
    img = gradient_bg((255, 251, 235), (239, 246, 255))
    draw = ImageDraw.Draw(img)
    add_header(img, "Scene", "第3文型は「動作が対象へ届く」場面で使う")
    draw_question_panel(draw, "日本語で「私は本を読む」と言うとき、", "英語では、読む対象をどこに置くのでしょう。")
    verbs = [("read", "本を読む"), ("open", "ドアを開ける"), ("buy", "プレゼントを買う"), ("like", "町が好き")]
    for i, (verb, ja) in enumerate(verbs[:stage]):
        x = 170 + i * 420
        y = 500
        rounded(draw, (x, y, x + 330, y + 160), 22, fill=CARD, outline=[BLUE, RED, GREEN, PURPLE][i], width=4)
        draw_center(draw, verb, (x + 20, y + 28, x + 310, y + 82), F_EN, fill=INK)
        draw_center(draw, ja, (x + 20, y + 88, x + 310, y + 135), F_BODY, fill=MUTED)
    if stage >= 4:
        rounded(draw, (350, 735, 1570, 820), 22, fill=(236, 253, 245), outline=GREEN, width=4)
        draw_center(draw, "動詞のあとに「何を？」「誰を？」の答えを置く。", (350, 735, 1570, 820), F_H3, fill=GREEN)
    return img


def slide_patterns(stage: int) -> Image.Image:
    img = gradient_bg((248, 250, 252), (255, 247, 237))
    draw = ImageDraw.Draw(img)
    add_header(img, "Compare", "第1文型・第2文型を受けて、第3文型を見る")
    panels = [
        ("第1文型 SV", "The door opened.", "動作だけで文が終わる", BLUE),
        ("第2文型 SVC", "She is kind.", "主語を説明して終わる", YELLOW),
        ("第3文型 SVO", "I opened the door.", "動作が対象へ届く", GREEN),
    ]
    for i, (title, example, body, color) in enumerate(panels):
        x = 110 + i * 600
        y = 220
        active = i < stage
        rounded(draw, (x, y, x + 520, y + 430), 26, fill=CARD if active else (248, 250, 252), outline=color if active else BORDER, width=5)
        draw.text((x + 40, y + 50), title, font=F_H2, fill=color if active else MUTED)
        draw.text((x + 40, y + 150), example if active else ".........", font=F_EN_SMALL, fill=INK if active else MUTED)
        draw_wrapped(draw, body if active else "", x + 40, y + 240, 420, F_BODY, fill=MUTED)
    if stage >= 3:
        rounded(draw, (260, 720, 1660, 820), 22, fill=SLATE)
        draw_center(draw, "第3文型では、V の後ろに O が来るかを見る。", (260, 720, 1660, 820), F_H3, fill=WHITE)
    return img


def slide_flip(stage: int) -> Image.Image:
    img = gradient_bg((239, 246, 255), (240, 253, 244))
    draw = ImageDraw.Draw(img)
    add_header(img, "Flip Board", "単語を順番に出して、SVO を作る")
    draw.text((120, 158), "「私は本を読む」を英語で表現すると？", font=F_H2, fill=INK)
    draw.text((120, 220), "ポイントは「何を読むのか」を動詞の後ろに置くことです。", font=F_BODY, fill=MUTED)
    visible = {"S": "I", "V": "read"}
    lift_v = False
    highlight_o = False
    if stage >= 4:
        visible["O"] = "a book"
        highlight_o = True
    draw_slots(draw, 245, 405, visible, lift_v=lift_v, highlight_o=highlight_o)
    if stage == 2:
        rounded(draw, (1270, 353, 1560, 419), 14, fill=(255, 247, 237), outline=ORANGE, width=4)
        draw_center(draw, "目的語カードを外す", (1270, 353, 1560, 419), F_SMALL, fill=ORANGE)
    if stage == 0:
        rounded(draw, (420, 690, 1500, 785), 20, fill=(255, 247, 237), outline=ORANGE, width=4)
        draw_center(draw, "I read まで見えている。問題は「何を」をどこに置くか。", (420, 690, 1500, 785), F_H3, fill=ORANGE)
    elif stage == 1:
        rounded(draw, (420, 690, 1500, 785), 20, fill=(239, 246, 255), outline=BLUE, width=4)
        draw_center(draw, "S = I  誰が読むのかを先に置く。", (420, 690, 1500, 785), F_H3, fill=BLUE)
    elif stage in {2, 3}:
        rounded(draw, (420, 690, 1500, 785), 20, fill=(254, 242, 242), outline=RED, width=4)
        draw_center(draw, "隠すのはポイントになる O だけ。", (420, 690, 1500, 785), F_H3, fill=RED)
    else:
        rounded(draw, (420, 690, 1500, 785), 20, fill=(236, 253, 245), outline=GREEN, width=4)
        draw_center(draw, "O = a book  「何を？」の答えが目的語。", (420, 690, 1500, 785), F_H3, fill=GREEN)
    return img


def slide_rule(stage: int) -> Image.Image:
    img = gradient_bg((255, 251, 235), (240, 253, 250))
    draw = ImageDraw.Draw(img)
    add_header(img, "Rule", "第3文型の見つけ方")
    rules = [
        ("1", "動詞を見る", "動作を表す V を見つける"),
        ("2", "後ろを見る", "V の後ろに言葉が続くか見る"),
        ("3", "名詞か確認", "目的語は基本的に名詞・代名詞・名詞句"),
    ]
    for i, (num, title, body) in enumerate(rules):
        x = 180 + i * 560
        y = 210
        active = i < stage
        rounded(draw, (x, y, x + 460, y + 270), 24, fill=CARD if active else (248, 250, 252), outline=ORANGE if active else BORDER, width=5)
        rounded(draw, (x + 36, y + 44, x + 112, y + 120), 18, fill=ORANGE if active else MUTED)
        draw_center(draw, num, (x + 36, y + 44, x + 112, y + 120), F_H2, fill=WHITE)
        draw.text((x + 140, y + 48), title, font=F_H2, fill=INK if active else MUTED)
        draw_wrapped(draw, body if active else "", x + 44, y + 160, 370, F_BODY, fill=MUTED)
    if stage >= 3:
        draw_sentence_chunks(
            draw,
            330,
            585,
            [("S", "I", "私は"), ("V", "read", "読む"), ("O", "a book", "本を")],
        )
        rounded(draw, (350, 755, 1570, 835), 22, fill=SLATE)
        draw_center(draw, "a book は名詞句。「何を？」の答えなので O。", (350, 755, 1570, 835), F_H3, fill=WHITE)
    return img


def slide_contrast(stage: int) -> Image.Image:
    img = gradient_bg((248, 250, 252), (255, 247, 237))
    draw = ImageDraw.Draw(img)
    add_header(img, "Contrast", "同じ open でも、O があるかで文型が変わる")
    if stage >= 1:
        rounded(draw, (150, 220, 870, 565), 26, fill=CARD, outline=BLUE, width=5)
        draw.text((200, 270), "第1文型 SV", font=F_H2, fill=BLUE)
        draw.text((200, 370), "The door opened.", font=F_EN, fill=INK)
        draw.text((200, 455), "ドアが開いた。目的語なし。", font=F_BODY, fill=MUTED)
    if stage >= 2:
        rounded(draw, (1050, 220, 1770, 565), 26, fill=CARD, outline=GREEN, width=5)
        draw.text((1100, 270), "第3文型 SVO", font=F_H2, fill=GREEN)
        draw.text((1100, 370), "I opened the door.", font=F_EN, fill=INK)
        draw.text((1100, 455), "私はドアを開けた。O = the door", font=F_BODY, fill=MUTED)
    if stage >= 3:
        rounded(draw, (255, 690, 1665, 805), 24, fill=(236, 253, 245), outline=GREEN, width=4)
        draw_center(draw, "opened の後ろに the door があると、「何を開けた？」の答えになる。", (255, 690, 1665, 805), F_H3, fill=GREEN)
    return img


def slide_h3_text(stage: int) -> Image.Image:
    img = gradient_bg((239, 246, 255), (255, 251, 235))
    draw = ImageDraw.Draw(img)
    add_header(img, "H3 Text", "本文の一文を SVO で読む")
    draw_wrapped(draw, "日本語では「静かな雰囲気が流れていた」と訳すと自然でも、英語では SVO の形を取っています。", 110, 150, 1520, F_BODY, fill=INK)
    if stage >= 1:
        draw_sentence_chunks(
            draw,
            155,
            315,
            [
                ("S", "The afternoon library", "その午後の図書館"),
                ("V", "held", "湛えていた"),
                ("O", "a quiet atmosphere", "静かな雰囲気を"),
            ],
        )
    if stage >= 2:
        rounded(draw, (155, 545, 1760, 735), 24, fill=CARD, outline=BORDER, width=3)
        draw.text((205, 585), "見るポイント", font=F_H2, fill=ORANGE)
        draw_wrapped(draw, "hold / held は「持つ・含む・湛える」。後ろの a quiet atmosphere が「何を？」の答えになります。", 205, 655, 1420, F_BODY, fill=MUTED)
    return img


def slide_parallel(stage: int) -> Image.Image:
    img = gradient_bg((240, 253, 250), (239, 246, 255))
    draw = ImageDraw.Draw(img)
    add_header(img, "H3 Text", "SVO が2つ並ぶ文もある")
    draw_wrapped(draw, "ひとつの主語に、動詞と目的語の組み合わせが2つ続くことがあります。", 110, 150, 1480, F_BODY)
    if stage >= 1:
        draw_sentence_chunks(
            draw,
            115,
            300,
            [
                ("S", "I", "私は"),
                ("V", "picked up", "手に取った"),
                ("O", "a small essay collection", "小さな随筆集を"),
            ],
        )
    if stage >= 2:
        draw.text((165, 500), "and", font=F_EN, fill=MUTED)
        draw_sentence_chunks(draw, 315, 485, [("V", "opened", "開いた"), ("O", "the first chapter", "最初の章を")])
    if stage >= 3:
        rounded(draw, (215, 700, 1705, 810), 24, fill=(255, 251, 235), outline=YELLOW, width=4)
        draw_center(draw, "and の後ろで、同じ主語 I に対して V + O がもう一組続く。", (215, 700, 1705, 810), F_H3, fill=INK)
    return img


def slide_summary(stage: int) -> Image.Image:
    img = gradient_bg((255, 247, 237), (239, 246, 255))
    draw = ImageDraw.Draw(img)
    add_header(img, "Summary", "第3文型 SVO の見方")
    points = [
        ("1", "使う場面", "何かに働きかける、何かを対象にする"),
        ("2", "形", "S + V + O"),
        ("3", "確認", "V の後ろに「何を？」「誰を？」の答えがある"),
    ]
    for i, (num, title, body) in enumerate(points[:stage]):
        y = 185 + i * 190
        rounded(draw, (220, y, 1700, y + 145), 24, fill=CARD, outline=BORDER, width=3)
        rounded(draw, (265, y + 34, 340, y + 109), 18, fill=ORANGE)
        draw_center(draw, num, (265, y + 34, 340, y + 109), F_H2, fill=WHITE)
        draw.text((390, y + 30), title, font=F_H2, fill=INK)
        draw.text((390, y + 88), body, font=F_BODY, fill=MUTED)
    if stage >= 3:
        rounded(draw, (300, 775, 1620, 850), 22, fill=SLATE)
        draw_center(draw, "SVO は「だれが、どうする、何を」を見るための骨格。", (300, 775, 1620, 850), F_H3, fill=WHITE)
    return img


@dataclass
class Step:
    name: str
    render: Callable[[], Image.Image]
    kind: str
    speech: str
    seconds: float | None = None


def JP(name: str, render: Callable[[], Image.Image], speech: str) -> Step:
    return Step(name, render, "jp", speech)


def EN(name: str, render: Callable[[], Image.Image], speech: str) -> Step:
    return Step(name, render, "en", speech)


def SILENT(name: str, render: Callable[[], Image.Image], seconds: float = 0.55) -> Step:
    return Step(name, render, "silent", "", seconds)


STEPS: list[Step] = [
    JP("theme", slide_title, "今回のテーマは第3文型です。動作が何かに届く文を見ていきます。"),
    JP("scene_1", lambda: slide_use_scene(2), "たとえば、日本語で、私は本を読む、と言うとき、英語では読む対象をどこに置くのでしょう。"),
    JP("scene_2", lambda: slide_use_scene(4), "読む、開ける、買う、好きだと言う。このように、動作や気持ちが何かに向かう場面で、第3文型をよく使います。"),
    JP("patterns_1", lambda: slide_patterns(1), "第1文型は、主語と動詞だけで文が終わります。ドアが自然に開いた、という文では目的語がありません。"),
    JP("patterns_2", lambda: slide_patterns(2), "第2文型は、主語を説明する文です。主語がどんな状態かを説明して終わります。"),
    JP("patterns_3", lambda: slide_patterns(3), "第3文型では、動作の後ろに対象が来ます。開ける、読む、買う、のような動作が何かに届きます。"),
    JP("flip_0", lambda: slide_flip(0), "この文で大切なのは、読む対象をどこに置くかです。"),
    SILENT("flip_lift", lambda: slide_flip(2), 0.45),
    JP("flip_3", lambda: slide_flip(4), "最後に、何を読むのかを置きます。この後ろのかたまりが目的語です。"),
    EN("flip_sentence", lambda: slide_flip(4), "I read a book."),
    JP("rule_1", lambda: slide_rule(1), "第3文型を見つけるときは、動詞が自分だけで終わるか、後ろに対象を求めるかを見ます。まず中心の動詞を確認します。"),
    JP("rule_2", lambda: slide_rule(2), "動詞の後ろに名詞や代名詞が続けば、その語句が動作の向かう先になります。前置詞句との違いに注意します。"),
    JP("rule_3", lambda: slide_rule(3), "ここで大切なのは、目的語に入るのは基本的に名詞、代名詞、名詞のかたまりだということです。何を、誰を、の答えになる名詞を探します。"),
    JP("contrast_1", lambda: slide_contrast(1), "同じ意味の動詞でも、目的語があるかどうかで文型が変わります。まず、第1文型です。"),
    EN("door_opened", lambda: slide_contrast(1), "The door opened."),
    JP("contrast_2", lambda: slide_contrast(2), "次に、第3文型です。私がドアを開けた、という文では、ドアが目的語になります。"),
    EN("i_opened", lambda: slide_contrast(2), "I opened the door."),
    JP("contrast_3", lambda: slide_contrast(3), "動詞の後ろに名詞があれば、何をしたのか、という答えになることがあります。だから第3文型と読めます。"),
    JP("h3_1", lambda: slide_h3_text(1), "高校編第三回の本文にも、第3文型が出てきます。まず英語の一文を聞いてみましょう。"),
    EN("h3_sentence", lambda: slide_h3_text(1), "The afternoon library held a quiet atmosphere."),
    JP("h3_2", lambda: slide_h3_text(2), "日本語では、静かな雰囲気が流れていた、と訳すと自然です。でも英語の骨格では、図書館が主語で、後ろの名詞のかたまりが目的語です。"),
    JP("parallel_1", lambda: slide_parallel(1), "ひとつの文に、第3文型が二つ並ぶこともあります。"),
    EN("parallel_sentence", lambda: slide_parallel(2), "I picked up a small essay collection and opened the first chapter."),
    JP("parallel_2", lambda: slide_parallel(3), "前半にも、後半にも、動詞と目的語の組み合わせがあります。同じ主語に対して、二つの第3文型が続いています。"),
    JP("summary_1", lambda: slide_summary(1), "まとめです。第3文型は、何かに働きかける場面でよく使います。"),
    JP("summary_2", lambda: slide_summary(2), "形は、主語、動詞、目的語。だれが、どうする、何を、という順番です。"),
    JP("summary_3", lambda: slide_summary(3), "動詞を見たら、後ろに、何を、誰を、の答えがあるか確認します。これが第3文型を見つける基本です。"),
]


def audio_duration(path: Path) -> float:
    result = run([
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(path),
    ])
    return float(result.stdout.strip())


def make_silence(path: Path, seconds: float):
    run([
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
    ])


def convert_to_wav(src: Path, dst: Path):
    run(["ffmpeg", "-y", "-i", str(src), "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(dst)])


def voicepeak(text: str, raw_path: Path):
    env = os.environ.copy()
    env["LC_ALL"] = "ja_JP.UTF-8"
    env["LANG"] = "ja_JP.UTF-8"
    last_result = None
    timeout_message = ""
    for attempt in range(4):
        raw_path.unlink(missing_ok=True)
        try:
            result = subprocess.run(
                [VOICEPEAK, "-s", text, "-n", NARRATOR, "-o", str(raw_path), "--speed", "94", "--pitch", "0"],
                capture_output=True,
                text=True,
                env=env,
                timeout=50,
            )
        except subprocess.TimeoutExpired:
            timeout_message = f"VOICEPEAK timed out: {text}"
            time.sleep(1.2 + attempt)
            continue
        if result.returncode == 0 and raw_path.exists() and raw_path.stat().st_size > 1024:
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
    tmp = out_path.with_suffix(".aiff")
    tmp.unlink(missing_ok=True)
    out_path.unlink(missing_ok=True)
    run(["say", "-v", EN_VOICE, "-r", "150", "-o", str(tmp), text])
    convert_to_wav(tmp, out_path)
    tmp.unlink(missing_ok=True)


def audio_cache_name(step: Step) -> str:
    key = f"{step.kind}:{NARRATOR}:macos-say:{EN_VOICE}:{step.speech}:{step.seconds}".encode("utf-8")
    digest = hashlib.sha1(key).hexdigest()[:12]
    return f"{step.name}_{digest}.wav"


def build_step_audio(step: Step) -> tuple[Path, float]:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    out = AUDIO_DIR / audio_cache_name(step)
    if out.exists() and out.stat().st_size > 1024:
        return out, audio_duration(out)
    if step.kind == "jp":
        raw = AUDIO_DIR / f"{out.stem}_raw.wav"
        voicepeak(step.speech, raw)
        convert_to_wav(raw, out)
    elif step.kind == "en":
        say_english(step.speech, out)
    elif step.kind == "silent":
        make_silence(out, step.seconds or 0.5)
    else:
        raise ValueError(step.kind)
    return out, audio_duration(out)


def compose_frame(content: Image.Image, step: Step, idx: int, total: int) -> Image.Image:
    img = Image.new("RGB", (W, H), (241, 245, 249))
    img.paste(content, (0, 0))
    return img


def build_video():
    if not Path(VOICEPEAK).exists():
        raise FileNotFoundError(VOICEPEAK)
    for d in (FRAME_DIR, AUDIO_DIR, CLIP_DIR):
        d.mkdir(parents=True, exist_ok=True)

    clips: list[Path] = []
    durations: list[float] = []
    print("=== Build plain H3 SVO explainer ===")
    for idx, step in enumerate(STEPS):
        print(f"[{idx + 1}/{len(STEPS)}] {step.name} {step.kind}")
        content = step.render()
        frame = compose_frame(content, step, idx, len(STEPS))
        frame_path = FRAME_DIR / f"frame_{idx:03d}_{step.name}.png"
        frame.save(frame_path)

        audio_path, duration = build_step_audio(step)
        duration += 0.18 if step.kind != "silent" else 0.0
        durations.append(duration)

        clip_path = CLIP_DIR / f"clip_{idx:03d}_{step.name}.mp4"
        run([
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
        ])
        clips.append(clip_path)

    concat = OUT_DIR / "concat.txt"
    with concat.open("w", encoding="utf-8") as f:
        for clip in clips:
            f.write(f"file '{clip.resolve()}'\n")

    tmp = OUT_VIDEO.with_suffix(".tmp.mp4")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", str(tmp)])
    shutil.move(str(tmp), str(OUT_VIDEO))
    print(f"Done: {OUT_VIDEO}")
    print(f"Duration: {sum(durations):.1f}s")
    print(f"Size: {OUT_VIDEO.stat().st_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    build_video()
