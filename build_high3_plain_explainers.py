from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import time
from dataclasses import dataclass
from html import unescape
from pathlib import Path
from typing import Callable

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
INDEX_HTML = ROOT / "index.html"
TMP_ROOT = ROOT / "tmp_high_lesson_explainers"
OUT_ROOT = ROOT / "dist" / "high3-plain-explainers"

VOICEPEAK = "/Applications/voicepeak.app/Contents/MacOS/voicepeak"
NARRATOR = "Japanese Male 2"
EN_VOICE = "Daniel"

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
YELLOW = (245, 158, 11)
PURPLE = (124, 58, 237)
PAPER = (250, 247, 239)
PAPER_BLUE = (239, 246, 255)
CARD = (255, 255, 255)
BORDER = (226, 232, 240)
WHITE = (255, 255, 255)
SLATE = (15, 23, 42)
ROLE_COLORS = {"S": BLUE, "V": RED, "O": GREEN, "C": YELLOW, "M": PURPLE}
ROLE_LABELS = {
    "S": "S（主語）",
    "V": "V（動詞）",
    "O": "O（目的語）",
    "C": "C（補語）",
    "M": "M（修飾）",
}
BOOKS = {
    "high1": {
        "label": "高校編1 文法基礎",
        "range": (1, 45),
        "hero": "高校編1 文法基礎",
        "teaser": "文法の骨格をしっかり押さえて、読む前の理解力を作る",
        "output_dir": "high1-plain-explainers",
    },
    "high2": {
        "label": "高校編2 読解前編",
        "range": (46, 107),
        "hero": "高校編2 総合読解前編",
        "teaser": "本文の構文を読み取り、論理の流れを追って理解を広げる",
        "output_dir": "high2-plain-explainers",
    },
    "high3": {
        "label": "高校編3 読解後編",
        "range": (108, 160),
        "hero": "高校編3 読解後編",
        "teaser": "高１→高２→高３まで、本文の骨格を読み解く流れで進める",
        "output_dir": "high3-plain-explainers",
    },
}


def font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REGULAR, size)


F_TITLE = font(62)
F_H1 = font(56)
F_H2 = font(44)
F_H3 = font(34)
F_BODY = font(32, bold=False)
F_SMALL = font(24, bold=False)
F_EN = font(44)
F_EN_SMALL = font(30)
F_LABEL = font(24)


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise RuntimeError("Command failed:\n" + " ".join(cmd) + "\n" + result.stderr[-2500:])
    return result


def _text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def _rounded(draw: ImageDraw.ImageDraw, xy, radius: int, fill, outline=None, width: int = 2):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def _draw_center(draw: ImageDraw.ImageDraw, text: str, box, fnt, fill=INK):
    x1, y1, x2, y2 = box
    tw, th = _text_size(draw, text, fnt)
    draw.text((x1 + (x2 - x1 - tw) / 2, y1 + (y2 - y1 - th) / 2), text, font=fnt, fill=fill)


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        tokens = paragraph.split()
        cur = ""
        for token in tokens:
            if not token:
                continue
            if _text_size(draw, token, fnt)[0] > max_width:
                if cur:
                    lines.append(cur)
                    cur = ""
                fallback = ""
                for ch in token:
                    if _text_size(draw, fallback + ch, fnt)[0] <= max_width:
                        fallback += ch
                    else:
                        if fallback:
                            lines.append(fallback)
                        fallback = ch
                if fallback:
                    lines.append(fallback)
                continue
            candidate = token if not cur else cur + " " + token
            if _text_size(draw, candidate, fnt)[0] <= max_width:
                cur = candidate
            else:
                if cur:
                    lines.append(cur)
                cur = token
        if cur:
            lines.append(cur)
    return lines


def _draw_wrapped(draw: ImageDraw.ImageDraw, text: str, x: int, y: int, max_width: int, fnt, fill=INK, line_gap: int = 8):
    cur_y = y
    for line in _wrap_text(draw, text, fnt, max_width):
        draw.text((x, cur_y), line, font=fnt, fill=fill)
        cur_y += fnt.size + line_gap
    return cur_y


# Compatibility helpers for the original helper naming used by the slide builders.
draw_wrapped = _draw_wrapped
draw_center = _draw_center


def _gradient_bg(top=PAPER_BLUE, bottom=(255, 251, 235), height=H) -> Image.Image:
    img = Image.new("RGB", (W, height), top)
    draw = ImageDraw.Draw(img)
    for y in range(height):
        t = y / max(height - 1, 1)
        color = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        draw.line((0, y, W, y), fill=color)
    return img


def _add_header(img: Image.Image, section: str, title: str, color=NAVY):
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, W, 104), fill=color)
    draw.text((54, 24), section, font=F_LABEL, fill=(219, 234, 254))
    draw.text((236, 16), title, font=F_H2, fill=WHITE)
    draw.rectangle((0, 102, W, 106), fill=ORANGE)


def _remove_tags(value: str) -> str:
    no_script = re.sub(r"<script.*?</script>", "", value, flags=re.S)
    no_tags = re.sub(r"<[^>]+>", "", no_script)
    return unescape(no_tags).replace("\u00a0", " ").strip()


@dataclass
class LessonSyntaxData:
    book_id: str
    lesson_id: int
    title: str
    grammar_target: str
    description: str
    examples: list[tuple[str, str]]
    syntax_patterns: list[tuple[str, str]]
    board_tokens: list[tuple[str, str]]


def _extract_book_block(book_id: str = "high3") -> str:
    html = INDEX_HTML.read_text(encoding="utf-8")
    marker_re = re.compile(rf'<div[^>]*id="book-{book_id}"[^>]*data-book="{book_id}"[^>]*>', re.S)
    m = marker_re.search(html)
    if not m:
        raise RuntimeError(f"Book block not found: {book_id}")
    start = m.start()

    depth = 0
    pos = start
    end = len(html)
    while pos < len(html):
        open_pos = html.find("<div", pos)
        close_pos = html.find("</div>", pos)
        if close_pos == -1:
            break
        if open_pos != -1 and open_pos < close_pos:
            depth += 1
            pos = html.find(">", open_pos)
            if pos == -1:
                break
            pos += 1
        else:
            depth -= 1
            pos = close_pos + len("</div>")
            if depth == 0:
                end = pos
                break

    return html[start:end]


def _parse_examples(block: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for en_raw, ja_raw in re.findall(
        r'<li>\s*<em>(.*?)</em>\s*<span class="ja">(.*?)</span>\s*</li>',
        block,
        flags=re.S,
    ):
        en = _remove_tags(en_raw)
        ja = _remove_tags(ja_raw)
        if en or ja:
            out.append((en, ja))
    return out


def _parse_board_tokens(sentence_html: str) -> list[tuple[str, str]]:
    tokens = []
    role_re = re.compile(
        r'<span class="[^"]*?(?:l([SVCMO])|role-([SVCMO]))[^\"]*">(.*?)</span>',
        re.S,
    )
    seen: set[str] = set()

    for m in role_re.finditer(sentence_html):
        role = m.group(1) or m.group(2)
        if role in seen:
            continue
        seen.add(role)
        raw = m.group(3)
        raw = re.sub(r'<span class="lab">.*?</span>', '', raw, flags=re.S)
        raw = re.sub(r'<span class="role">.*?</span>', '', raw, flags=re.S)
        raw = re.sub(r'<span class="ja">.*?</span>', '', raw, flags=re.S)
        raw = re.sub(r'<span[^>]*>.*?</span>', '', raw, flags=re.S)
        word = _remove_tags(raw)
        word = re.sub(r'\s+', ' ', word)
        word = word.strip()
        if not word:
            continue
        tokens.append((role, word))
        if len(tokens) >= 5:
            break

    if not tokens:
        return []

    return tokens


def _extract_lesson_blocks(book_block: str) -> list[str]:
    lesson_pattern = re.compile(
        r'<section[^>]*class="[^"]*\blesson\b[^"]*"[^>]*data-lesson="(\d+)"[^>]*data-has-syntax="true"[^>]*>',
        flags=re.S,
    )
    matches = list(lesson_pattern.finditer(book_block))
    out: list[str] = []
    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(book_block)
        out.append(book_block[start:end])
    return out


def parse_lessons_from_book(book_id: str) -> list[LessonSyntaxData]:
    block = _extract_book_block(book_id)
    lesson_blocks = _extract_lesson_blocks(block)
    lessons: list[LessonSyntaxData] = []

    for raw in lesson_blocks:
        lesson_m = re.search(r'data-lesson="(\d+)"', raw)
        if not lesson_m:
            continue
        lesson_id = int(lesson_m.group(1))

        title_m = re.search(r'<h2>Lesson H\d+\s*[—-]\s*(.*?)</h2>', raw)
        title = _remove_tags(title_m.group(1)) if title_m else f"H{lesson_id:03d}"

        target_m = re.search(r'<span class="g-title">文法ターゲット：([^<]+)</span>', raw)
        target = _remove_tags(target_m.group(1)) if target_m else "文法ターゲット"

        desc_m = re.search(r'<p class="g-desc">(.*?)</p>', raw, flags=re.S)
        desc = _remove_tags(desc_m.group(1)) if desc_m else "本文の文法ポイントを丁寧に確認します。"

        examples = _parse_examples(raw)

        syntax_pat = re.findall(r'<span class="pattern">(.*?)</span><span>(.*?)</span>', raw, flags=re.S)
        patterns = [(_remove_tags(p), _remove_tags(e)) for p, e in syntax_pat]

        syntax_block_m = re.search(r'<div class="body-syntax hidden">(.*?)</div>\s*<\/section>', raw, flags=re.S)
        board_tokens = []
        if syntax_block_m:
            first_sentence_m = re.search(r'<div class="sentence">(.*?)</div>', syntax_block_m.group(1), flags=re.S)
            if first_sentence_m:
                board_tokens = _parse_board_tokens(first_sentence_m.group(1))
        if not board_tokens and examples:
            first_en = examples[0][0]
            fallback = re.split(r"[ ,.]", first_en)
            if fallback:
                fallback = [w for w in fallback if w]
                if len(fallback) >= 2:
                    board_tokens = [("S", fallback[0]), ("V", fallback[1])]

        lessons.append(
            LessonSyntaxData(
                book_id=book_id,
                lesson_id=lesson_id,
                title=title,
                grammar_target=target,
                description=desc,
                examples=examples,
                syntax_patterns=patterns,
                board_tokens=board_tokens,
            )
        )

    return lessons


def parse_lessons_from_high3() -> list[LessonSyntaxData]:
    return parse_lessons_from_book("high3")


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


def SILENT(name: str, render: Callable[[], Image.Image], seconds: float = 0.6) -> Step:
    return Step(name, render, "silent", "", seconds)


def _draw_slots_generic(draw: ImageDraw.ImageDraw, x: int, y: int, slots: list[tuple[str, str]], visible: int, lift_v: bool = False, stage: int = 0):
    cur_x = x
    box_w = 380
    for idx, (role, word) in enumerate(slots[:4]):
        color = ROLE_COLORS.get(role, BLUE)
        _rounded(draw, (cur_x, y, cur_x + box_w, y + 124), 18, fill=CARD, outline=color, width=4)
        _rounded(draw, (cur_x + 16, y + 18, cur_x + 72, y + 74), 12, fill=color)
        draw.text((cur_x + 82, y + 22), ROLE_LABELS.get(role, role), font=F_SMALL, fill=MUTED)
        if idx < visible:
            draw.text((cur_x + 82, y + 52), _truncate(word, 13), font=F_BODY, fill=INK)
        else:
            _rounded(draw, (cur_x + 84, y + 48, cur_x + box_w - 16, y + 102), 12, fill=(241, 245, 249), outline=BORDER, width=2)
            _draw_center(draw, "?", (cur_x + 84, y + 48, cur_x + box_w - 16, y + 102), F_H3, fill=MUTED)
        cur_x += box_w + 36


def _truncate(text: str, max_len: int) -> str:
    t = text.replace("\n", " ").strip()
    if len(t) <= max_len:
        return t
    return t[: max_len - 1].strip() + "…"


def _book_meta(book_id: str) -> dict[str, str | tuple[int, int]]:
    return BOOKS[book_id]


def _lesson_label(lesson: LessonSyntaxData) -> str:
    return f"{_book_meta(lesson.book_id)['label']} Lesson H{lesson.lesson_id:03d}"


def _lesson_label_speech(lesson: LessonSyntaxData) -> str:
    return f"{lesson.book_id}のレッスン H{lesson.lesson_id:03d}"


def slide_title(lesson: LessonSyntaxData) -> Image.Image:
    img = _gradient_bg((239, 246, 255), (255, 251, 235))
    draw = ImageDraw.Draw(img)
    _rounded(draw, (116, 112, 1804, 850), 34, fill=(255, 255, 255), outline=(191, 219, 254), width=5)
    meta = _book_meta(lesson.book_id)
    draw.text((176, 188), str(meta["hero"]), font=F_H2, fill=NAVY)
    draw.text((176, 242), _lesson_label(lesson), font=F_TITLE, fill=INK)
    draw.text((176, 328), lesson.title, font=F_H1, fill=ORANGE)
    draw_wrapped(draw, f"文法ターゲット：{lesson.grammar_target}", 176, 470, 1500, F_BODY, fill=MUTED)
    _rounded(draw, (176, 650, 1210, 744), 24, fill=SLATE)
    _draw_center(draw, str(meta["teaser"]), (176, 650, 1210, 744), F_H3, fill=WHITE)
    return img


def slide_target(lesson: LessonSyntaxData) -> Image.Image:
    img = _gradient_bg((248, 250, 252), (240, 253, 250))
    draw = ImageDraw.Draw(img)
    _add_header(img, "What to learn", f"{_lesson_label(lesson)} 目標")
    _rounded(draw, (120, 140, W - 120, 220), 26, fill=CARD, outline=GREEN, width=3)
    draw.text((160, 168), "文法ターゲット", font=F_H3, fill=INK)
    draw_wrapped(draw, lesson.grammar_target, 560, 165, 1160, F_EN, fill=BLUE)

    draw_wrapped(
        draw,
        lesson.description,
        160,
        290,
        1600,
        F_BODY,
        fill=INK,
    )

    if lesson.syntax_patterns:
        pat_name, _ = lesson.syntax_patterns[0]
        _rounded(draw, (120, 540, W - 120, 760), 26, fill=CARD, outline=BORDER, width=3)
        draw.text((166, 575), "本文での見るポイント（例）", font=F_H3, fill=ORANGE)
        _draw_wrapped_lines(draw, (166, 630), pat_name, 1650, F_BODY, fill=MUTED)
    return img


def _draw_wrapped_lines(draw: ImageDraw.ImageDraw, pos, text: str, max_width: int, fnt, fill):
    x, y = pos
    for line in _wrap_text(draw, text, fnt, max_width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + 8
    return y


def slide_examples(lesson: LessonSyntaxData, idx: int = 0) -> Image.Image:
    img = _gradient_bg((240, 253, 250), (255, 247, 237))
    draw = ImageDraw.Draw(img)
    _add_header(img, "Example", f"{_lesson_label(lesson)} 例文")

    en = lesson.examples[idx][0] if idx < len(lesson.examples) else ""
    ja = lesson.examples[idx][1] if idx < len(lesson.examples) else ""

    draw.text((132, 186), f"Example {idx + 1}", font=F_H2, fill=ORANGE)
    if en:
        _draw_wrapped_lines(draw, (132, 250), f"EN: {en}", 1660, F_EN, fill=INK)
    if ja:
        _draw_wrapped_lines(draw, (132, 390), f"JP: {ja}", 1660, F_BODY, fill=MUTED)
    return img


def slide_flip_board(lesson: LessonSyntaxData, stage: int) -> Image.Image:
    img = _gradient_bg((239, 246, 255), (240, 253, 244))
    draw = ImageDraw.Draw(img)
    _add_header(img, "Flip Board", "文の役割を順番に見ていく")
    draw.text((128, 156), f"今回の鍵は、{lesson.grammar_target}", font=F_H2, fill=INK)

    if not lesson.board_tokens:
        tokens = [("S", ""), ("V", ""), ("O", ""), ("C", "")]
    else:
        tokens = lesson.board_tokens[:4]

    reveal = min(max(stage, 0), len(tokens))
    _draw_slots_generic(draw, 150, 420, tokens, reveal)

    if stage == 0:
        note = "まず、主語・動詞を順に読みます。"
    elif stage == 1:
        note = "主語(S) から先に決める。"
    elif stage == 2:
        note = "動詞(V) が何を示すか。"
    else:
        note = "残りの役割は文末や文脈で確認しよう。"

    _rounded(draw, (280, 760, 1670, 845), 22, fill=(15, 23, 42))
    _draw_center(draw, note, (280, 760, 1670, 845), F_H3, fill=WHITE)
    return img


def slide_pattern(lesson: LessonSyntaxData, stage: int = 1) -> Image.Image:
    img = _gradient_bg((248, 250, 252), (255, 247, 237))
    draw = ImageDraw.Draw(img)
    _add_header(img, "Syntax", "本文で見る構文ポイント")

    draw.text((140, 160), "本文の主要メモ", font=F_H2, fill=INK)
    for i, (pat, exp) in enumerate(lesson.syntax_patterns[:4]):
        if i >= stage:
            continue
        y = 240 + i * 185
        _rounded(draw, (120, y, W - 120, y + 150), 22, fill=CARD, outline=BORDER, width=3)
        _rounded(draw, (165, y + 28, 246, y + 80), 14, fill=PURPLE)
        draw.text((166, y + 26), f"{i + 1}", font=F_H2, fill=WHITE)
        _draw_wrapped_lines(draw, (275, y + 28), pat, 1520, F_H3, fill=BLUE)
        _draw_wrapped_lines(draw, (195, y + 74), re.sub(r"\s+", " ", exp), 1580, F_SMALL, fill=MUTED)

    if lesson.syntax_patterns and stage >= len(lesson.syntax_patterns):
        _rounded(draw, (280, 870, 1640, 970), 22, fill=GREEN)
        _draw_center(draw, "同じ形でも語順・意味の流れで役割が決まります", (280, 870, 1640, 970), F_H3, fill=WHITE)
    return img


def slide_summary(lesson: LessonSyntaxData) -> Image.Image:
    img = _gradient_bg((255, 247, 237), (239, 246, 255))
    draw = ImageDraw.Draw(img)
    _add_header(img, "Summary", f"{_lesson_label(lesson)} まとめ")

    points = [
        ("1", "ターゲット", lesson.grammar_target),
        ("2", "チェック", "主語・動詞・目的語・補語の位置を確認"),
        ("3", "確認", "本文の構文説明語を1文ずつ分解"),
    ]

    for i, (num, title, body) in enumerate(points):
        y = 200 + i * 210
        _rounded(draw, (130, y, W - 130, y + 150), 24, fill=CARD, outline=BORDER, width=3)
        _rounded(draw, (172, y + 30, 246, y + 120), 16, fill=ORANGE)
        _draw_center(draw, num, (172, y + 30, 246, y + 120), F_H2, fill=WHITE)
        draw.text((246 + 40, y + 26), title, font=F_H2, fill=INK)
        _draw_wrapped_lines(draw, (246 + 40, y + 80), body, 1460, F_BODY, fill=MUTED)

    return img


def build_steps(lesson: LessonSyntaxData) -> list[Step]:
    ex1 = lesson.examples[0][0] if lesson.examples else ""
    ex1_ja = lesson.examples[0][1] if lesson.examples else ""

    steps: list[Step] = [
        JP(
            "title",
            lambda: slide_title(lesson),
            f"{_lesson_label_speech(lesson)} を開始します。タイトルは{lesson.title}です。",
        ),
        JP(
            "target",
            lambda: slide_target(lesson),
            f"今回の文法ターゲットは {lesson.grammar_target} です。",
        ),
    ]

    if lesson.examples:
        steps.extend(
            [
                EN(
                    "example_1",
                    lambda: slide_examples(lesson, 0),
                    ex1,
                ),
                JP(
                    "example_1_ja",
                    lambda: slide_examples(lesson, 0),
                    f"例文1は、{ex1_ja} です。",
                ),
            ]
        )

    steps.extend(
        [
        JP(
            "flip_0",
            lambda: slide_flip_board(lesson, 0),
            "まずは文の枠をつくります。まずは空欄として見ます。",
        ),
        JP(
            "flip_1",
            lambda: slide_flip_board(lesson, 1),
            "主語の部分を確認し、主語の意味を決めます。",
        ),
        JP(
            "flip_2",
            lambda: slide_flip_board(lesson, 2),
            "次に、動詞の位置を確認します。",
        ),
        JP(
            "flip_3",
            lambda: slide_flip_board(lesson, 3),
            "さらに他の役割を見て、文の全体構造を把握します。",
        ),
        JP(
            "pattern_1",
            lambda: slide_pattern(lesson, 1),
            lesson.syntax_patterns[0][1] if lesson.syntax_patterns else "本文の文型を確認して、節ごとの意味を分けて読めるようにします。",
        ),
        JP(
            "pattern_2",
            lambda: slide_pattern(lesson, 2),
            lesson.syntax_patterns[1][1] if len(lesson.syntax_patterns) > 1 else "文の中でどの位置が重要な役割かを比較すると分かりやすいです。",
        ),
        JP(
            "summary",
            lambda: slide_summary(lesson),
            f"まとめです。{_lesson_label_speech(lesson)}では、文の役割をS、V、O から確認しました。"
            f"本文のこの構文を見て、同じ型を別の文でも使えるようにします。",
        ),
        ]
    )
    return steps


def _audio_seconds(path: Path) -> float:
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


def _to_wav(src: Path, dst: Path):
    run(["ffmpeg", "-y", "-i", str(src), "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(dst)])


def _voicepeak(text: str, raw_path: Path):
    env = os.environ.copy()
    env["LC_ALL"] = "ja_JP.UTF-8"
    env["LANG"] = "ja_JP.UTF-8"

    last_result = None
    timeout_msg = ""
    for attempt in range(4):
        raw_path.unlink(missing_ok=True)
        try:
            result = subprocess.run(
                [VOICEPEAK, "-s", text, "-n", NARRATOR, "-o", str(raw_path), "--speed", "94", "--pitch", "0"],
                capture_output=True,
                text=True,
                env=env,
                timeout=60,
            )
        except subprocess.TimeoutExpired:
            timeout_msg = f"VOICEPEAK timeout: {text[:40]}"
            time.sleep(1.2 + attempt)
            continue
        if result.returncode == 0 and raw_path.exists() and raw_path.stat().st_size > 1024:
            return
        last_result = result
        time.sleep(1.2 + attempt)

    raise RuntimeError(
        "VOICEPEAK failed\n"
        + timeout_msg
        + "\n"
        + ((last_result.stderr if last_result else "")[-2200:])
        + ((last_result.stdout if last_result else "")[-1200:])
    )


def _say_english(text: str, out_path: Path):
    tmp = out_path.with_suffix(".aiff")
    tmp.unlink(missing_ok=True)
    out_path.unlink(missing_ok=True)
    run(["say", "-v", EN_VOICE, "-r", "145", "-o", str(tmp), text])
    _to_wav(tmp, out_path)
    tmp.unlink(missing_ok=True)


def _make_silence(path: Path, seconds: float):
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


def _cache_audio_name(step: Step) -> str:
    key = f"{step.kind}:{NARRATOR}:macos-say:{EN_VOICE}:{step.speech}:{step.seconds}".encode("utf-8")
    digest = hashlib.sha1(key).hexdigest()[:12]
    return f"{step.name}_{digest}.wav"


def _build_step_audio(audio_dir: Path, step: Step) -> tuple[Path, float]:
    audio_dir.mkdir(parents=True, exist_ok=True)
    out = audio_dir / _cache_audio_name(step)
    if out.exists() and out.stat().st_size > 1024:
        return out, _audio_seconds(out)

    if step.kind == "jp":
        raw = audio_dir / f"{out.stem}_raw.wav"
        _voicepeak(step.speech, raw)
        _to_wav(raw, out)
        raw.unlink(missing_ok=True)
    elif step.kind == "en":
        _say_english(step.speech, out)
    elif step.kind == "silent":
        _make_silence(out, step.seconds or 0.6)
    else:
        raise ValueError(step.kind)

    return out, _audio_seconds(out)


def _compose_slide(content: Image.Image, step: Step, idx: int, total: int) -> Image.Image:
    canvas = Image.new("RGB", (W, H), (241, 245, 249))
    canvas.paste(content, (0, 0))
    return canvas


def _build_one(lesson: LessonSyntaxData, out_path: Path) -> None:
    tmp_dir = TMP_ROOT / lesson.book_id / f"lesson_{lesson.lesson_id}"
    frame_dir = tmp_dir / "frames"
    audio_dir = tmp_dir / "audio"
    clip_dir = tmp_dir / "clips"
    for d in (frame_dir, audio_dir, clip_dir):
        d.mkdir(parents=True, exist_ok=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    steps = build_steps(lesson)
    clips: list[Path] = []
    durations: list[float] = []

    for idx, step in enumerate(steps):
        img = _compose_slide(step.render(), step, idx, len(steps))
        frame_path = frame_dir / f"frame_{idx:03d}_{step.name}.png"
        img.save(frame_path)

        audio_path, duration = _build_step_audio(audio_dir, step)
        duration += 0.18 if step.kind != "silent" else 0.0
        durations.append(duration)

        clip_path = clip_dir / f"clip_{idx:03d}_{step.name}.mp4"
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

    concat = tmp_dir / "concat.txt"
    concat.write_text("".join(f"file '{clip.resolve()}'\n" for clip in clips), encoding="utf-8")
    temp_out = out_path.with_suffix(".tmp.mp4")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", str(temp_out)])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    run(["mv", str(temp_out), str(out_path)])


def build_selected_lessons(lessons: list[LessonSyntaxData], selected: list[int], force: bool = False):
    selected_set = set(selected)
    target_lessons = [lesson for lesson in lessons if lesson.lesson_id in selected_set]
    target_lessons.sort(key=lambda i: i.lesson_id)

    created: list[Path] = []
    for lesson in target_lessons:
        out_path = OUT_ROOT / f"{lesson.book_id}_H{lesson.lesson_id:03d}_plain_explainer.mp4"
        if out_path.exists() and not force:
            print(f"skip existing: {out_path.name}")
            continue
        print(f"=== {out_path.name} ===")
        start = time.time()
        _build_one(lesson, out_path)
        elapsed = time.time() - start
        print(f"done: {out_path.name} ({elapsed:.1f}s)")
        created.append(out_path)

    return created


def parse_targets(args_lessons: list[str] | None) -> list[int]:
    if not args_lessons:
        return []
    out: list[int] = []
    for token in args_lessons:
        if "-" in token:
            start, end = token.split("-", 1)
            start_i = int(start)
            end_i = int(end)
            if start_i > end_i:
                start_i, end_i = end_i, start_i
            out.extend(list(range(start_i, end_i + 1)))
        else:
            out.append(int(token))
    return sorted(set(out))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build plain flip-board styled explanation videos for grammar lessons")
    p.add_argument("--book", default="high3", choices=sorted(BOOKS), help="Target book: high1, high2, or high3")
    p.add_argument("--lesson", action="append", help="Lesson id or range, e.g. --lesson 108 --lesson 112-120")
    p.add_argument("--only-missing", action="store_true", help="Generate only lessons without existing output")
    p.add_argument("--force", action="store_true", help="Regenerate even if output exists")
    p.add_argument(
        "--output-dir",
        default=None,
        help="Output directory (default: dist/<book>-plain-explainers)",
    )
    p.add_argument("--english-voice", default=EN_VOICE, help="macOS say voice name for English examples (default: Daniel)")
    return p.parse_args()


def main():
    if not Path(VOICEPEAK).exists():
        raise FileNotFoundError(f"VOICEPEAK not found: {VOICEPEAK}")

    args = parse_args()
    global OUT_ROOT
    global EN_VOICE
    book_id = args.book
    if book_id not in BOOKS:
        raise ValueError(f"Unknown book: {book_id}")
    OUT_ROOT = Path(args.output_dir) if args.output_dir else ROOT / "dist" / str(_book_meta(book_id)["output_dir"])
    EN_VOICE = args.english_voice

    lessons = parse_lessons_from_book(book_id)
    if not lessons:
        print("No lessons parsed")
        return

    selected = parse_targets(args.lesson)
    all_ids = {l.lesson_id for l in lessons}
    if not args.lesson:
        selected = sorted(all_ids)
    else:
        selected = [sid for sid in selected if sid in all_ids]
    if not selected:
        print("No matching lesson IDs")
        return

    if args.only_missing:
        selected = [sid for sid in selected if not (OUT_ROOT / f"{book_id}_H{sid:03d}_plain_explainer.mp4").exists()]

    if not selected:
        print("No lessons to build")
        return

    build_selected_lessons(lessons, selected, force=args.force)


if __name__ == "__main__":
    main()
