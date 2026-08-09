"""Build a narrated H3 grammar explanation video.

Topic: Lesson H3, SVO / transitive verbs.
Japanese narration: VOICEPEAK.
English examples: macOS English voice.
Every spoken event is rendered as on-screen text in the caption strip.
"""
from __future__ import annotations

import shutil
import subprocess
import os
import time
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "tmp_h3_svo_video"
SLIDE_DIR = OUT_DIR / "slides"
AUDIO_DIR = OUT_DIR / "audio"
CLIP_DIR = OUT_DIR / "clips"
OUT_VIDEO = ROOT / "h3_svo_explanation_teacher_tacos.mp4"

VOICEPEAK = "/Applications/voicepeak.app/Contents/MacOS/voicepeak"
NARRATOR = "Japanese Male 1"
EN_VOICE = "Daniel"
EN_AUDIO_DIR = ROOT / "audio" / "high1" / "L3"
TEACHER_IMAGE = ROOT / "dist-public" / "phonics-chars" / "teacher_tacos.png"
TEACHER_SHEET_IMAGE = ROOT / "dist-public" / "phonics-chars" / "sheets" / "teacher_tacos.png"
TEACHER_CUTOUT = OUT_DIR / "teacher_tacos_sheet_style_cutout.png"

W, H = 1920, 1080
FPS = 30
CONTENT_W, CONTENT_H = 1600, 900
CONTENT_X, CONTENT_Y = 160, 0
CAPTION_Y = 900
CAPTION_H = H - CAPTION_Y
FONT_BOLD = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
FONT_REGULAR = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"

INK = (31, 41, 55)
MUTED = (100, 116, 139)
PAPER = (250, 247, 239)
PAPER_2 = (255, 252, 244)
CARD = (255, 255, 255)
BORDER = (226, 232, 240)
NAVY = (30, 64, 175)
ORANGE = (234, 88, 12)
GREEN = (5, 150, 105)
BLUE = (37, 99, 235)
RED = (220, 38, 38)
GRAY = (100, 116, 139)
YELLOW = (245, 158, 11)
PURPLE = (124, 58, 237)
WHITE = (255, 255, 255)

ROLE_COLORS = {
    "S": BLUE,
    "V": RED,
    "O": GREEN,
    "C": YELLOW,
    "M": GRAY,
}


def font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REGULAR, size)


F_TITLE = font(72)
F_H1 = font(60)
F_H2 = font(42)
F_H3 = font(34)
F_BODY = font(31, bold=False)
F_SMALL = font(24, bold=False)
F_EN = font(42)
F_EN_SMALL = font(32)
F_LABEL = font(26)
F_CAPTION = font(30, bold=False)
F_CAPTION_SMALL = font(25, bold=False)


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise RuntimeError(
            "Command failed:\n"
            + " ".join(cmd)
            + "\n"
            + result.stderr[-2000:]
        )
    return result


def rounded(draw: ImageDraw.ImageDraw, xy, radius: int, fill, outline=None, width: int = 2):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


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


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    text: str,
    x: int,
    y: int,
    max_width: int,
    fnt,
    fill=INK,
    line_gap: int = 12,
):
    cur_y = y
    for line in wrap_text(draw, text, fnt, max_width):
        draw.text((x, cur_y), line, font=fnt, fill=fill)
        cur_y += fnt.size + line_gap
    return cur_y


def gradient_bg(top=PAPER, bottom=(232, 240, 254)) -> Image.Image:
    img = Image.new("RGB", (W, H), top)
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / (H - 1)
        col = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        draw.line([(0, y), (W, y)], fill=col)
    return img


def paste_cover(base: Image.Image, src: Image.Image, box):
    x, y, w, h = box
    ratio = max(w / src.width, h / src.height)
    nw, nh = int(src.width * ratio), int(src.height * ratio)
    resized = src.resize((nw, nh), Image.Resampling.LANCZOS)
    crop_x = (nw - w) // 2
    crop_y = (nh - h) // 2
    cropped = resized.crop((crop_x, crop_y, crop_x + w, crop_y + h))
    base.paste(cropped, (x, y))


def paste_contain(base: Image.Image, src: Image.Image, box):
    x, y, w, h = box
    ratio = min(w / src.width, h / src.height)
    nw, nh = int(src.width * ratio), int(src.height * ratio)
    resized = src.resize((nw, nh), Image.Resampling.LANCZOS)
    base.paste(resized, (x + (w - nw) // 2, y + (h - nh) // 2))


def paste_rgba_contain(base: Image.Image, src: Image.Image, box):
    x, y, w, h = box
    src = src.convert("RGBA")
    ratio = min(w / src.width, h / src.height)
    nw, nh = int(src.width * ratio), int(src.height * ratio)
    resized = src.resize((nw, nh), Image.Resampling.LANCZOS)
    px = x + (w - nw) // 2
    py = y + (h - nh) // 2
    base.paste(resized, (px, py), resized.getchannel("A"))


def ensure_teacher_cutout() -> Path:
    if TEACHER_CUTOUT.exists():
        return TEACHER_CUTOUT

    TEACHER_CUTOUT.parent.mkdir(parents=True, exist_ok=True)
    sheet = Image.open(TEACHER_SHEET_IMAGE).convert("RGBA")
    # Use the clean white-background character sheet instead of the classroom
    # illustration. This crop isolates the front-view Teacher Tacos and avoids
    # title text above the character.
    crop = sheet.crop((500, 72, 884, 520))
    arr = np.array(crop)
    rgb = arr[:, :, :3].astype(np.int32)
    distance_from_white = np.sqrt(np.sum((255 - rgb) ** 2, axis=2))
    alpha = np.clip((distance_from_white - 16) * 9, 0, 255).astype(np.uint8)
    kernel = np.ones((3, 3), np.uint8)
    alpha = cv2.morphologyEx(alpha, cv2.MORPH_OPEN, kernel, iterations=1)
    alpha = cv2.GaussianBlur(alpha, (3, 3), 0)
    arr[:, :, 3] = alpha

    ys, xs = np.where(alpha > 8)
    if len(xs) == 0 or len(ys) == 0:
        raise RuntimeError("Teacher cutout mask is empty.")
    pad = 12
    x1, x2 = max(xs.min() - pad, 0), min(xs.max() + pad, crop.width - 1)
    y1, y2 = max(ys.min() - pad, 0), min(ys.max() + pad, crop.height - 1)
    Image.fromarray(arr[y1 : y2 + 1, x1 : x2 + 1]).save(TEACHER_CUTOUT)
    return TEACHER_CUTOUT


def teacher_image() -> Image.Image:
    return Image.open(ensure_teacher_cutout()).convert("RGBA")


def add_header(img: Image.Image, section: str, title: str, color=NAVY):
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, W, 114), fill=color)
    draw.text((70, 28), section, font=F_LABEL, fill=(219, 234, 254))
    draw.text((250, 22), title, font=F_H2, fill=WHITE)
    draw.rectangle((0, 112, W, 118), fill=ORANGE)


def add_teacher_badge(
    img: Image.Image,
    caption="Teacher Tacos",
    *,
    x: int = 1495,
    y: int = 660,
    w: int = 285,
    h: int = 210,
):
    draw = ImageDraw.Draw(img)
    rounded(draw, (x - 16, y - 16, x + w + 16, y + h + 64), 22, fill=CARD, outline=BORDER, width=3)
    paste_rgba_contain(img, teacher_image(), (x, y, w, h))
    draw_center(draw, caption, (x - 10, y + h + 10, x + w + 10, y + h + 52), F_SMALL, fill=NAVY)


def draw_role_box(draw, x, y, label, text, color, w=300, h=130):
    rounded(draw, (x, y, x + w, y + h), 18, fill=(255, 255, 255), outline=color, width=5)
    draw_center(draw, label, (x + 12, y + 14, x + 86, y + 66), F_H3, fill=WHITE)
    rounded(draw, (x + 16, y + 16, x + 82, y + 70), 14, fill=color)
    draw_center(draw, text, (x + 92, y + 14, x + w - 14, y + h - 14), F_EN, fill=INK)


def chunk_width(draw: ImageDraw.ImageDraw, text: str) -> int:
    tw, _ = text_size(draw, text, F_EN_SMALL)
    return min(max(tw + 118, 210), 760)


def draw_chunk_sentence(draw, x, y, chunks, max_width=1500):
    cur_x = x
    cur_y = y
    for role, text, note in chunks:
        color = ROLE_COLORS.get(role, NAVY)
        width = chunk_width(draw, text)
        if cur_x + width > x + max_width:
            cur_x = x
            cur_y += 146
        rounded(draw, (cur_x, cur_y, cur_x + width, cur_y + 112), 16, fill=CARD, outline=color, width=4)
        rounded(draw, (cur_x + 18, cur_y + 20, cur_x + 64, cur_y + 66), 10, fill=color)
        draw_center(draw, role, (cur_x + 18, cur_y + 20, cur_x + 64, cur_y + 66), F_LABEL, fill=WHITE)
        draw.text((cur_x + 84, cur_y + 22), text, font=F_EN_SMALL, fill=INK)
        if note:
            draw.text((cur_x + 84, cur_y + 70), note, font=F_SMALL, fill=MUTED)
        cur_x += width + 24
    return cur_y + 126


def draw_flip_sentence(draw, x, y, left, verb, right, ja):
    rounded(draw, (x, y, x + 1120, y + 138), 18, fill=CARD, outline=BORDER, width=3)
    draw.text((x + 26, y + 34), left, font=F_EN, fill=INK)
    left_w, _ = text_size(draw, left, F_EN)
    card_x = x + 44 + left_w
    verb_w = max(280, text_size(draw, verb, F_EN)[0] + 68)
    rounded(draw, (card_x, y + 18, card_x + verb_w, y + 100), 14, fill=(255, 247, 237), outline=ORANGE, width=4)
    draw_center(draw, verb, (card_x, y + 18, card_x + verb_w, y + 100), F_EN, fill=ORANGE)
    draw.text((card_x + verb_w + 28, y + 34), right, font=F_EN, fill=INK)
    draw.text((x + 26, y + 98), ja, font=F_SMALL, fill=MUTED)


def slide_00_title() -> Image.Image:
    img = gradient_bg((239, 246, 255), (255, 251, 235))
    draw = ImageDraw.Draw(img)
    rounded(draw, (1165, 135, 1765, 840), 36, fill=(255, 255, 255), outline=(191, 219, 254), width=4)
    paste_rgba_contain(img, teacher_image(), (1210, 170, 510, 590))
    draw = ImageDraw.Draw(img)
    rounded(draw, (92, 92, 1055, 520), 34, fill=(255, 255, 255), outline=(191, 219, 254), width=4)
    draw.text((140, 132), "高校編 H3", font=F_H2, fill=NAVY)
    draw.text((140, 202), "第3文型 [SVO]", font=F_TITLE, fill=INK)
    draw.text((140, 312), "本屋での午後", font=F_H1, fill=ORANGE)
    draw_wrapped(
        draw,
        "他動詞のあとに目的語が続く形を、フリップボードと構文色分けで見ます。",
        144,
        410,
        820,
        F_BODY,
        fill=MUTED,
        line_gap=10,
    )
    rounded(draw, (132, 762, 1032, 894), 22, fill=(30, 41, 59))
    draw.text((176, 794), "S  V  O", font=font(70), fill=WHITE)
    draw.text((460, 812), "誰が → どうする → 何を", font=F_H3, fill=(226, 232, 240))
    return img


def slide_01_core() -> Image.Image:
    img = gradient_bg()
    draw = ImageDraw.Draw(img)
    add_header(img, "H3 Grammar", "第3文型 SVO は「動作の対象」を持つ")
    draw_wrapped(
        draw,
        "第3文型は、主語 S の動作が、目的語 O に向かう形です。目的語は「何を」「誰を」にあたる名詞で、S と O は別のものです。",
        90,
        160,
        1320,
        F_BODY,
    )
    y = 330
    draw_role_box(draw, 120, y, "S", "I", BLUE)
    draw_role_box(draw, 500, y, "V", "read", RED)
    draw_role_box(draw, 880, y, "O", "a book", GREEN, w=380)
    draw.line((420, y + 64, 500, y + 64), fill=MUTED, width=5)
    draw.line((800, y + 64, 880, y + 64), fill=MUTED, width=5)
    rounded(draw, (120, 540, 1260, 750), 24, fill=CARD, outline=BORDER, width=3)
    draw.text((160, 580), "チェック", font=F_H3, fill=ORANGE)
    draw_wrapped(draw, "read は「読む」。読む対象として a book が必要です。だから I read a book. は SVO になります。", 160, 642, 1040, F_BODY)
    add_teacher_badge(img)
    return img


def slide_02_flipboard() -> Image.Image:
    img = gradient_bg((255, 247, 237), (240, 253, 244))
    draw = ImageDraw.Draw(img)
    add_header(img, "Flip Board", "動詞をめくると、O が見えてくる")
    draw.text((92, 158), "フリップボードでは、まず動詞を隠して文の形を見ます。", font=F_BODY, fill=INK)
    draw.text((92, 212), "めくった動詞が他動詞なら、その後ろの名詞が O になりやすい。", font=F_BODY, fill=INK)
    draw_flip_sentence(draw, 120, 310, "I", "read", "a book.", "私は本を読む。O = a book")
    draw_flip_sentence(draw, 120, 470, "She", "bought", "a gift.", "彼女は贈り物を買った。O = a gift")
    draw_flip_sentence(draw, 120, 630, "We", "understand", "your feelings.", "私たちはあなたの気持ちを理解する。O = your feelings")
    rounded(draw, (120, 835, 1310, 950), 18, fill=(236, 253, 245), outline=GREEN, width=4)
    draw.text((158, 864), "合言葉：V のあとに「何を？」と聞いて答えが出るなら、SVO の候補。", font=F_H3, fill=GREEN)
    add_teacher_badge(img, "めくって確認")
    return img


def slide_03_h3_sentence_1() -> Image.Image:
    img = gradient_bg((239, 246, 255), (255, 251, 235))
    draw = ImageDraw.Draw(img)
    add_header(img, "H3 Text", "本文の一文を SVO で読む")
    draw_wrapped(draw, "H3「本屋での午後」の冒頭です。hold は「持つ・湛える」という他動詞として使われ、後ろに目的語を取っています。", 90, 150, 1420, F_BODY)
    chunks = [
        ("S", "The afternoon library", "その午後の図書館"),
        ("V", "held", "湛えていた"),
        ("O", "a quiet atmosphere", "静かな雰囲気を"),
    ]
    draw_chunk_sentence(draw, 110, 330, chunks, max_width=1760)
    rounded(draw, (110, 565, 1500, 760), 24, fill=CARD, outline=BORDER, width=3)
    draw.text((150, 604), "日本語では「静かな雰囲気が流れていた」と自然に訳しても、", font=F_BODY, fill=INK)
    draw.text((150, 664), "英語の骨格は library が atmosphere を held する SVO です。", font=F_BODY, fill=INK)
    add_teacher_badge(img, "H3 本文")
    return img


def slide_04_parallel_svo() -> Image.Image:
    img = gradient_bg((240, 253, 250), (239, 246, 255))
    draw = ImageDraw.Draw(img)
    add_header(img, "H3 Text", "ひとつの文に SVO が2つ並ぶこともある")
    draw_wrapped(draw, "次の文では I という主語に対して、picked up と opened という2つの動作が並んでいます。どちらも後ろに目的語があります。", 90, 150, 1420, F_BODY)
    chunks1 = [
        ("S", "I", "わたしは"),
        ("V", "picked up", "手に取った"),
        ("O", "a small essay collection", "小さな随筆集を"),
    ]
    chunks2 = [
        ("V", "opened", "開いた"),
        ("O", "the first chapter", "最初の章を"),
    ]
    y = draw_chunk_sentence(draw, 110, 330, chunks1, max_width=1680)
    draw.text((152, y + 20), "and", font=F_EN, fill=MUTED)
    draw_chunk_sentence(draw, 260, y, chunks2, max_width=1450)
    rounded(draw, (110, 760, 1450, 910), 22, fill=(255, 251, 235), outline=YELLOW, width=4)
    draw.text((150, 800), "and があると、同じ S に対して V + O がもう一組続くことがあります。", font=F_BODY, fill=INK)
    add_teacher_badge(img, "SVO + SVO")
    return img


def slide_05_svo_vs_sv() -> Image.Image:
    img = gradient_bg((248, 250, 252), (255, 247, 237))
    draw = ImageDraw.Draw(img)
    add_header(img, "Compare", "第1文型 SV と第3文型 SVO を分ける")
    draw_wrapped(draw, "すべての動詞の後ろに名詞が来るわけではありません。目的語がない文は SV や SV+M として読みます。", 90, 150, 1370, F_BODY)
    rounded(draw, (110, 285, 900, 520), 24, fill=CARD, outline=BORDER, width=3)
    draw.text((150, 320), "第1文型 SV", font=F_H3, fill=BLUE)
    draw.text((150, 392), "The door opened.", font=F_EN, fill=INK)
    draw.text((150, 455), "ドアが開いた。目的語なし。", font=F_BODY, fill=MUTED)
    rounded(draw, (980, 285, 1770, 520), 24, fill=CARD, outline=GREEN, width=4)
    draw.text((1020, 320), "第3文型 SVO", font=F_H3, fill=GREEN)
    draw.text((1020, 392), "I opened the door.", font=F_EN, fill=INK)
    draw.text((1020, 455), "私はドアを開けた。O = the door", font=F_BODY, fill=MUTED)
    rounded(draw, (110, 610, 1770, 860), 24, fill=(255, 255, 255), outline=BORDER, width=3)
    draw.text((150, 650), "H3 の SV+M 例", font=F_H3, fill=ORANGE)
    draw.text((150, 720), "I glanced out of the window.   /   Outside, a small child ran past.", font=F_EN_SMALL, fill=INK)
    draw.text((150, 782), "glance や run はここでは目的語を取らず、out of the window / past が M として働きます。", font=F_BODY, fill=MUTED)
    return img


def slide_06_transitive_verbs() -> Image.Image:
    img = gradient_bg((255, 251, 235), (240, 253, 244))
    draw = ImageDraw.Draw(img)
    add_header(img, "Verb Map", "H3 に出てくる「O を取りやすい動詞」")
    groups = [
        ("持つ・開く", ["held", "picked up", "opened"], BLUE),
        ("表す・描く", ["described", "expressed", "composed"], ORANGE),
        ("心に働く", ["attracted", "inspired", "preferred"], PURPLE),
        ("見る・続ける", ["watched", "continued", "carry"], GREEN),
    ]
    x_positions = [110, 540, 970, 1400]
    for x, (title, verbs, color) in zip(x_positions, groups):
        rounded(draw, (x, 190, x + 360, 735), 24, fill=CARD, outline=color, width=4)
        draw_center(draw, title, (x + 20, 220, x + 340, 280), F_H3, fill=color)
        y = 320
        for verb in verbs:
            rounded(draw, (x + 46, y, x + 314, y + 66), 14, fill=(248, 250, 252), outline=BORDER, width=2)
            draw_center(draw, verb, (x + 46, y, x + 314, y + 66), F_EN_SMALL, fill=INK)
            y += 88
    rounded(draw, (170, 810, 1750, 940), 22, fill=(236, 253, 245), outline=GREEN, width=4)
    draw.text((214, 848), "暗記のコツ：動詞を見たら、後ろに「何を？」の答えがあるかを見る。", font=F_H3, fill=GREEN)
    return img


def slide_07_site_usage() -> Image.Image:
    img = gradient_bg((239, 246, 255), (255, 247, 237))
    draw = ImageDraw.Draw(img)
    add_header(img, "Learning Site", "サイトでは「構文解析」とフリップボードを行き来する")
    left_x = 105
    rounded(draw, (left_x, 175, 860, 820), 30, fill=CARD, outline=BORDER, width=3)
    draw.text((150, 225), "おすすめの流れ", font=F_H2, fill=NAVY)
    steps = [
        ("1", "英語のみ", "まず文をそのまま読む"),
        ("2", "フリップボード", "動詞やかたまりをめくって確認"),
        ("3", "構文解析", "S/V/O/C/M の色で骨格を見る"),
        ("4", "音読", "最後に文全体を声に出す"),
    ]
    y = 320
    for num, title, desc in steps:
        rounded(draw, (150, y, 230, y + 80), 18, fill=NAVY)
        draw_center(draw, num, (150, y, 230, y + 80), F_H2, fill=WHITE)
        draw.text((260, y + 4), title, font=F_H3, fill=INK)
        draw.text((260, y + 48), desc, font=F_BODY, fill=MUTED)
        y += 116
    rounded(draw, (950, 220, 1770, 760), 28, fill=(30, 41, 59), outline=(147, 197, 253), width=4)
    draw.text((1005, 270), "H3", font=F_H2, fill=(147, 197, 253))
    draw.text((1005, 348), "The afternoon library", font=F_EN_SMALL, fill=BLUE)
    draw.text((1005, 410), "held", font=F_EN_SMALL, fill=RED)
    draw.text((1005, 472), "a quiet atmosphere.", font=F_EN_SMALL, fill=GREEN)
    draw.text((1005, 570), "構文解析で色を見たあと、", font=F_BODY, fill=WHITE)
    draw.text((1005, 626), "フリップで V と O を確認。", font=F_BODY, fill=WHITE)
    add_teacher_badge(img, "サイトで練習", x=1480, y=780, w=245, h=175)
    return img


def slide_08_summary() -> Image.Image:
    img = gradient_bg((255, 247, 237), (239, 246, 255))
    draw = ImageDraw.Draw(img)
    add_header(img, "Summary", "H3 SVO の見方まとめ")
    points = [
        ("1", "V のあとに O", "他動詞の後ろには、動作の対象が続く。"),
        ("2", "S ≠ O", "主語と目的語は別のもの。I love this town. の I と this town は別。"),
        ("3", "M と混同しない", "out of the window / past などは目的語ではなく、場所や方向を足す修飾語。"),
    ]
    y = 190
    for num, title, body in points:
        rounded(draw, (130, y, 1590, y + 180), 24, fill=CARD, outline=BORDER, width=3)
        rounded(draw, (170, y + 42, 260, y + 132), 20, fill=ORANGE)
        draw_center(draw, num, (170, y + 42, 260, y + 132), F_H2, fill=WHITE)
        draw.text((310, y + 35), title, font=F_H2, fill=INK)
        draw_wrapped(draw, body, 310, y + 96, 1190, F_BODY, fill=MUTED)
        y += 220
    rounded(draw, (250, 900, 1670, 1000), 24, fill=(30, 41, 59))
    draw_center(draw, "SVO は「誰が、何を、どうする」の骨格を見るレンズ。", (250, 900, 1670, 1000), F_H3, fill=WHITE)
    return img


@dataclass
class AudioEvent:
    kind: str
    value: str | float


def JP(text: str) -> AudioEvent:
    return AudioEvent("jp", text)


def EN(text: str) -> AudioEvent:
    return AudioEvent("en_say", text)


def EN_FILE(name: str) -> AudioEvent:
    return AudioEvent("en_file", name)


def PAUSE(seconds: float) -> AudioEvent:
    return AudioEvent("pause", seconds)


@dataclass
class Slide:
    name: str
    render: callable
    audio_events: list[AudioEvent] = field(default_factory=list)


SLIDES: list[Slide] = [
    Slide(
        "title",
        slide_00_title,
        [
            JP("今回は高校編 H3、第3文型を説明します。ティーチャータコスと一緒に、誰が、どうする、何を、という英語の骨格を見ていきましょう。フリップボードの考え方を使って、動詞と目的語の関係を一つずつ確認します。"),
        ],
    ),
    Slide(
        "core",
        slide_01_core,
        [
            JP("第3文型は、主語の動作が目的語に向かう形です。目的語は、何を、誰を、にあたる名詞です。まず画面の例文を英語音声で聞きましょう。"),
            EN("I read a book."),
            JP("この文では、読む対象として本が必要です。だから、主語、動詞、目的語の順番で骨格を作っています。"),
        ],
    ),
    Slide(
        "flipboard",
        slide_02_flipboard,
        [
            JP("フリップボードでは、まず動詞をめくるカードとして扱います。動詞をめくったとき、その後ろに、何を、誰を、の答えがあれば、第3文型の候補です。"),
            EN("I read a book."),
            EN("She bought a gift."),
            EN("We understand your feelings."),
            JP("このように、動詞と目的語がセットで見えてきます。"),
        ],
    ),
    Slide(
        "h3_sentence_1",
        slide_03_h3_sentence_1,
        [
            JP("H3 の本文から一文を見ます。まず英語音声で一度聞いてみましょう。"),
            EN("The afternoon library held a quiet atmosphere."),
            JP("日本語では、静かな雰囲気が流れていた、と訳すと自然です。でも英語の骨格は、午後の図書館が主語、湛えていた、が動詞、静かな雰囲気が目的語です。"),
        ],
    ),
    Slide(
        "parallel_svo",
        slide_04_parallel_svo,
        [
            JP("次の文では、一つの主語に対して、二つの動作が並びます。先に英語音声を聞きましょう。"),
            EN("I picked up a small essay collection and opened the first chapter."),
            JP("前半の動作の目的語は、小さな随筆集。後半の動作の目的語は、最初の章です。ひとつの文に、主語、動詞、目的語の組み合わせが二組入ることもあります。"),
        ],
    ),
    Slide(
        "svo_vs_sv",
        slide_05_svo_vs_sv,
        [
            JP("第3文型を見つけるには、第1文型との違いも大切です。次の二つを聞き比べます。"),
            EN("The door opened."),
            EN("I opened the door."),
            JP("一つ目は、ドアが開いた、で目的語がありません。二つ目は、私がドアを開けた、で、ドアが目的語です。H3 の例も聞いてみましょう。"),
            EN("I glanced out of the window, then returned to the page."),
            EN("Outside, a small child ran past."),
            JP("この二つは、目的語ではなく、方向や場所を足す表現を持つ、主語と動詞プラス修飾語として読みます。"),
        ],
    ),
    Slide(
        "transitive_verbs",
        slide_06_transitive_verbs,
        [
            JP("H3 には目的語を取りやすい他動詞がたくさん出てきます。動詞部分は英語音声で確認しましょう。"),
            EN("held. picked up. opened."),
            EN("described. expressed. composed."),
            EN("attracted. inspired. preferred."),
            EN("watched. continued. carry."),
            JP("動詞を見たら、後ろに、何を、の答えがあるかを見る。これが第3文型を見抜く一番の近道です。"),
        ],
    ),
    Slide(
        "site_usage",
        slide_07_site_usage,
        [
            JP("学習サイトでは、英語のみ表示、フリップボード、構文解析を行き来しながら練習できます。まず英文をそのまま読み、次に動詞やかたまりをフリップで確認し、最後に構文解析の色で主語、動詞、目的語、補語、修飾語を確認します。目で構造を見たあとに音読すると、文型が体に残りやすくなります。"),
        ],
    ),
    Slide(
        "summary",
        slide_08_summary,
        [
            JP("まとめです。第3文型では、第一に、動詞の後ろに目的語が来ます。第二に、主語と目的語は別のものです。第三に、目的語と修飾語を混同しないことが大切です。最後にH3本文の短い一文を聞きます。"),
            EN("Words carry us beyond time."),
            JP("第3文型は、誰が、何を、どうする、という英文の骨格を見るためのレンズです。"),
        ],
    ),
]


def split_voicepeak_text(text: str, limit: int = 120) -> list[str]:
    chunks: list[str] = []
    current = ""
    for ch in text:
        current += ch
        if ch in "。！？" and len(current) >= 24:
            chunks.append(current.strip())
            current = ""
        elif ch == "、" and len(current) >= 18:
            chunks.append(current.strip())
            current = ""
        elif len(current) >= limit:
            pos = max(current.rfind("、"), current.rfind("。"))
            if pos > 20:
                chunks.append(current[: pos + 1].strip())
                current = current[pos + 1 :]
            else:
                chunks.append(current.strip())
                current = ""
    if current.strip():
        chunks.append(current.strip())
    return chunks


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


def convert_to_wav(src: Path, dst: Path):
    run(["ffmpeg", "-y", "-i", str(src), "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(dst)])


def say_english_part(text: str, out_path: Path):
    tmp_aiff = out_path.with_suffix(".aiff")
    tmp_aiff.unlink(missing_ok=True)
    out_path.unlink(missing_ok=True)
    run(["say", "-v", EN_VOICE, "-r", "150", "-o", str(tmp_aiff), text])
    convert_to_wav(tmp_aiff, out_path)
    tmp_aiff.unlink(missing_ok=True)


def voicepeak_part(text: str, raw_path: Path):
    env = os.environ.copy()
    env["LC_ALL"] = "ja_JP.UTF-8"
    env["LANG"] = "ja_JP.UTF-8"
    last_result = None
    last_timeout = ""
    for attempt in range(4):
        raw_path.unlink(missing_ok=True)
        try:
            result = subprocess.run(
                [VOICEPEAK, "-s", text, "-n", NARRATOR, "-o", str(raw_path), "--speed", "92", "--pitch", "0"],
                capture_output=True,
                text=True,
                env=env,
                timeout=50,
            )
        except subprocess.TimeoutExpired:
            last_timeout = f"VOICEPEAK timed out after 50s: {text}"
            time.sleep(1.2 + attempt * 0.8)
            continue
        if result.returncode == 0 and raw_path.exists() and raw_path.stat().st_size > 1024:
            return
        last_result = result
        time.sleep(1.2 + attempt * 0.8)
    raise RuntimeError(
        "VOICEPEAK failed:\n"
        + last_timeout
        + "\n"
        + ((last_result.stderr if last_result else "")[-2000:])
        + ((last_result.stdout if last_result else "")[-1000:])
    )


def concat_wavs(parts: list[Path], out_path: Path):
    concat_file = out_path.parent / f"{out_path.stem}_concat.txt"
    with concat_file.open("w", encoding="utf-8") as f:
        for part in parts:
            f.write(f"file '{part.resolve()}'\n")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", str(out_path)])


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


def expand_audio_events(events: list[AudioEvent]) -> list[AudioEvent]:
    expanded: list[AudioEvent] = []
    for event in events:
        if event.kind == "jp":
            for chunk in split_voicepeak_text(str(event.value), limit=82):
                expanded.append(AudioEvent("jp", chunk))
        else:
            expanded.append(event)
    return expanded


def event_caption(event: AudioEvent) -> str:
    if event.kind in {"jp", "en_say"}:
        return str(event.value)
    if event.kind == "en_file":
        return str(event.value)
    if event.kind == "pause":
        return ""
    return str(event.value)


def event_label(event: AudioEvent) -> tuple[str, tuple[int, int, int]]:
    if event.kind == "jp":
        return "日本語説明", NAVY
    if event.kind in {"en_say", "en_file"}:
        return "English voice", GREEN
    return "Pause", GRAY


def caption_font_and_lines(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    max_height: int,
    *,
    english: bool = False,
):
    candidates = [34, 31, 28, 25, 22] if english else [30, 27, 24, 22, 20]
    for size in candidates:
        fnt = font(size, bold=False)
        lines = wrap_text(draw, text, fnt, max_width)
        line_height = size + 10
        if len(lines) * line_height <= max_height:
            return fnt, lines, line_height
    fnt = font(candidates[-1], bold=False)
    return fnt, wrap_text(draw, text, fnt, max_width), candidates[-1] + 8


def compose_event_frame(
    base_slide: Image.Image,
    slide_index: int,
    slide_total: int,
    event_index: int,
    event_total: int,
    event: AudioEvent,
) -> Image.Image:
    img = gradient_bg((241, 245, 249), (255, 251, 235))
    draw = ImageDraw.Draw(img)

    rounded(
        draw,
        (CONTENT_X - 10, CONTENT_Y + 12, CONTENT_X + CONTENT_W + 10, CONTENT_Y + CONTENT_H + 12),
        24,
        fill=(203, 213, 225),
    )
    content = base_slide.resize((CONTENT_W, CONTENT_H), Image.Resampling.LANCZOS)
    img.paste(content, (CONTENT_X, CONTENT_Y))

    draw.rectangle((0, CAPTION_Y, W, H), fill=(15, 23, 42))
    draw.rectangle((0, CAPTION_Y, W, CAPTION_Y + 6), fill=ORANGE)

    label, label_color = event_label(event)
    rounded(draw, (76, CAPTION_Y + 32, 280, CAPTION_Y + 88), 16, fill=label_color)
    draw_center(draw, label, (76, CAPTION_Y + 32, 280, CAPTION_Y + 88), F_LABEL, fill=WHITE)

    caption = event_caption(event)
    english = event.kind in {"en_say", "en_file"}
    caption_font, lines, line_height = caption_font_and_lines(
        draw,
        caption,
        1360,
        CAPTION_H - 48,
        english=english,
    )
    text_x = 320
    text_y = CAPTION_Y + 28
    for line in lines[:5]:
        draw.text((text_x, text_y), line, font=caption_font, fill=(248, 250, 252))
        text_y += line_height

    progress = f"{slide_index + 1}/{slide_total}  {event_index + 1}/{event_total}"
    draw.text((1690, CAPTION_Y + 34), progress, font=F_SMALL, fill=(203, 213, 225))
    dot_x = 1688
    dot_y = CAPTION_Y + 92
    for i in range(min(event_total, 10)):
        fill = ORANGE if i <= event_index else (71, 85, 105)
        draw.ellipse((dot_x + i * 21, dot_y, dot_x + i * 21 + 10, dot_y + 10), fill=fill)
    return img


def build_event_audio(event: AudioEvent, slide: Slide, slide_index: int, event_index: int, gap_seconds: float) -> tuple[Path, float]:
    slide_audio_dir = AUDIO_DIR / f"{slide_index:02d}_{slide.name}"
    slide_audio_dir.mkdir(parents=True, exist_ok=True)

    spoken = slide_audio_dir / f"event_{event_index:02d}_spoken.wav"
    cached_out = slide_audio_dir / f"event_{event_index:02d}.wav" if gap_seconds > 0 else spoken
    if cached_out.exists() and cached_out.stat().st_size > 1024:
        try:
            return cached_out, audio_duration(cached_out)
        except Exception:
            cached_out.unlink(missing_ok=True)

    if event.kind == "jp":
        raw = slide_audio_dir / f"event_{event_index:02d}_jp_raw.wav"
        voicepeak_part(str(event.value), raw)
        convert_to_wav(raw, spoken)
    elif event.kind == "en_say":
        say_english_part(str(event.value), spoken)
    elif event.kind == "en_file":
        src = EN_AUDIO_DIR / str(event.value)
        if not src.exists():
            raise FileNotFoundError(src)
        convert_to_wav(src, spoken)
    elif event.kind == "pause":
        make_silence(spoken, float(event.value))
    else:
        raise ValueError(f"Unknown audio event kind: {event.kind}")

    if gap_seconds > 0:
        gap = slide_audio_dir / f"event_{event_index:02d}_gap.wav"
        out = slide_audio_dir / f"event_{event_index:02d}.wav"
        make_silence(gap, gap_seconds)
        concat_wavs([spoken, gap], out)
        return out, audio_duration(out)

    return spoken, audio_duration(spoken)


def build_slide_audio(slide: Slide, idx: int) -> tuple[Path, float]:
    slide_audio_dir = AUDIO_DIR / f"{idx:02d}_{slide.name}"
    slide_audio_dir.mkdir(parents=True, exist_ok=True)
    parts: list[Path] = []

    for j, event in enumerate(slide.audio_events):
        if event.kind == "jp":
            raw = slide_audio_dir / f"jp_raw_{j:02d}.wav"
            wav = slide_audio_dir / f"jp_{j:02d}.wav"
            voicepeak_part(str(event.value), raw)
            convert_to_wav(raw, wav)
            parts.append(wav)
        elif event.kind == "en_say":
            wav = slide_audio_dir / f"en_say_{j:02d}.wav"
            say_english_part(str(event.value), wav)
            parts.append(wav)
        elif event.kind == "en_file":
            src = EN_AUDIO_DIR / str(event.value)
            if not src.exists():
                raise FileNotFoundError(src)
            wav = slide_audio_dir / f"en_file_{j:02d}.wav"
            convert_to_wav(src, wav)
            parts.append(wav)
        elif event.kind == "pause":
            wav = slide_audio_dir / f"pause_{j:02d}.wav"
            make_silence(wav, float(event.value))
            parts.append(wav)
        else:
            raise ValueError(f"Unknown audio event kind: {event.kind}")

        if j < len(slide.audio_events) - 1:
            mid = slide_audio_dir / f"gap_{j:02d}.wav"
            make_silence(mid, 0.18)
            parts.append(mid)

    end = slide_audio_dir / "pause_end.wav"
    make_silence(end, 0.65)
    parts.append(end)

    out = AUDIO_DIR / f"slide_{idx:02d}.wav"
    concat_wavs(parts, out)
    return out, audio_duration(out)


def build_video():
    if not Path(VOICEPEAK).exists():
        raise FileNotFoundError(f"VOICEPEAK not found: {VOICEPEAK}")
    if not TEACHER_SHEET_IMAGE.exists():
        raise FileNotFoundError(f"Teacher sheet image not found: {TEACHER_SHEET_IMAGE}")
    for d in (SLIDE_DIR, AUDIO_DIR, CLIP_DIR):
        d.mkdir(parents=True, exist_ok=True)

    clip_paths: list[Path] = []
    durations: list[float] = []
    clip_index = 0

    print("=== Render event frames and audio ===")
    for i, slide in enumerate(SLIDES):
        base_slide = slide.render()
        base_path = SLIDE_DIR / f"slide_{i:02d}_{slide.name}_base.png"
        base_slide.save(base_path)
        events = expand_audio_events(slide.audio_events)
        print(f"[{i+1}/{len(SLIDES)}] {slide.name}: {len(events)} events")

        for j, event in enumerate(events):
            frame = compose_event_frame(base_slide, i, len(SLIDES), j, len(events), event)
            frame_path = SLIDE_DIR / f"frame_{i:02d}_{j:02d}_{slide.name}.png"
            frame.save(frame_path)

            gap = 0.58 if j == len(events) - 1 else 0.20
            audio_path, duration = build_event_audio(event, slide, i, j, gap)
            durations.append(duration)

            clip_path = CLIP_DIR / f"clip_{clip_index:03d}_{slide.name}_{j:02d}.mp4"
            cmd = [
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
            run(cmd)
            clip_paths.append(clip_path)
            print(f"  clip {clip_index:03d}: {event.kind} {duration:.1f}s")
            clip_index += 1

    concat_file = OUT_DIR / "concat.txt"
    with concat_file.open("w", encoding="utf-8") as f:
        for clip_path in clip_paths:
            f.write(f"file '{clip_path.resolve()}'\n")

    print("=== Concatenate ===")
    tmp_out = OUT_VIDEO.with_suffix(".tmp.mp4")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", str(tmp_out)])
    shutil.move(str(tmp_out), str(OUT_VIDEO))
    print(f"Done: {OUT_VIDEO}")
    print(f"Duration: {sum(durations):.1f}s")
    print(f"Size: {OUT_VIDEO.stat().st_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    build_video()
