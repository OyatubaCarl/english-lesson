"""Build Baker-style kinetic captions for Aunt Ant Short A.

This uses the same ASS structure as Baker Bear:
  - each English word is positioned as its own text layer
  - the currently active word gets a coral rounded rectangle underneath
  - Japanese cues are shown as full lines without per-word boxes
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from PIL import ImageFont

ROOT = Path(__file__).parent
SRC = ROOT / "dist" / "phonics-video" / "aunt_ant_short_a_480p.mp4"
OUT_DIR = ROOT / "uploaded-videos"
OUT_DIR.mkdir(exist_ok=True)
OUT = OUT_DIR / "aunt_ant_short_a_480p_kinetic.mp4"
ASS_PATH = OUT_DIR / "aunt_ant_short_a_480p_kinetic.ass"

FUNNICS_DIR = Path(
    "/Users/masaki/Library/CloudStorage/"
    "GoogleDrive-sarosaro36@gmail.com/マイドライブ/個人用/ClaudeCode/"
    "Funnics Island/songs/02_aunt_ant_short_a"
)

PLAY_W = 854
PLAY_H = 480
FONT_PATH_EN = "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"
FONT_PATH_JP = "/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc"
FONT_NAME_EN = "Arial Rounded MT Bold"
FONT_NAME_JP = "Hiragino Maru Gothic ProN W4"
FONT_SIZE_PX = 42
JP_SIZE_PX = 34
LINE_HEIGHT = int(FONT_SIZE_PX * 1.25)
JP_LINE_HEIGHT = int(JP_SIZE_PX * 1.4)

MARGIN_L = 24
MARGIN_R = 24
MARGIN_V = 58
MAX_WIDTH = PLAY_W - MARGIN_L - MARGIN_R
MAX_WIDTH_JP = MAX_WIDTH

BOX_PAD_X = 8
BOX_PAD_Y = 4
CORNER_R = 10
BOX_COLOR_BGR = "6080FF"
BOX_TIME_SHIFT = 0.25


def rounded_rect_path(w: int, h: int, r: int) -> str:
    k = 0.5523
    kr = int(round(r * k))
    return (
        f"m {r} 0 "
        f"l {w - r} 0 "
        f"b {w - r + kr} 0 {w} {r - kr} {w} {r} "
        f"l {w} {h - r} "
        f"b {w} {h - r + kr} {w - r + kr} {h} {w - r} {h} "
        f"l {r} {h} "
        f"b {r - kr} {h} 0 {h - r + kr} 0 {h - r} "
        f"l 0 {r} "
        f"b 0 {r - kr} {r - kr} 0 {r} 0"
    )


# (start, end, text, is_english)
# Timings are anchored to aunt_ant_short_a_transcript.json segments.
# The Suno performance does not include every Hook/repetition from the draft
# lyrics, so these cues follow the actual audio to keep the highlight synced.
CUES: list[tuple[float, float, str, bool]] = [
    # Intro
    (0.00, 2.20, 'ねえ しってる？ "A" の もじ。', False),
    (2.20, 4.20, "ABC の A。", False),
    (4.20, 7.00, "でも、べつの よみかたも あるんだよ。", False),
    (7.00, 10.60, "アントおばさんの みじかい「あ」。", False),
    (12.42, 15.00, "Cat, hat, ant, bag.", True),
    (15.00, 16.50, "Fat, mad, sad, black.", True),
    (16.50, 19.16, "ぜんぶ みじかい A の おと。", False),
    (19.34, 22.16, "じゃあ、きいてみて！", False),
    # Hook 1
    (23.12, 26.80, "A! A! A! Aunt Ant!", True),
    (26.80, 30.80, "Short A! Short A! Aunt Ant!", True),
    # Verse 1
    (30.80, 34.18, "Fat cat in a hat, Fat cat in a hat,", True),
    (34.18, 37.82, "Mad rat on a mat, Mad rat on a mat,", True),
    (37.82, 41.40, "Sad ant at a plant, Sad ant at a plant,", True),
    (41.40, 46.82, "Black bag with a flag! Black bag with a flag!", True),
    # Verse 2, as actually sung after Verse 1.
    (48.24, 52.08, "Sad ant at a plant, Sad ant at a plant,", True),
    (52.08, 55.70, "Mad rat on a mat, Mad rat on a mat,", True),
    (55.70, 59.34, "Fat cat in a hat! Fat cat in a hat!", True),
    # Verse 3
    (59.34, 62.90, "Mad cat in a hat, Mad cat in a hat,", True),
    (62.90, 66.48, "Sad rat on a mat, Sad rat on a mat,", True),
    (66.48, 70.08, "Black ant at a plant, Black ant at a plant,", True),
    (70.08, 73.64, "Fat bag with a flag! Fat bag with a flag!", True),
    # Verse 4
    (73.64, 77.30, "Fat! Fat! Mad! Mad! Sad! Sad! Black! Black!", True),
    (77.30, 80.76, "Cat! Cat! Rat! Rat! Ant! Ant! Bag! Bag!", True),
    (80.76, 84.34, "In! In! On! On! At! At! With! With!", True),
    (84.34, 88.00, "Hat! Hat! Mat! Mat! Plant! Plant! Flag! Flag!", True),
    # Bridge
    (88.00, 91.54, "Fat-cat-hat! Fat-cat-hat!", True),
    (91.54, 94.94, "Mad-rat-mat! Mad-rat-mat!", True),
    (94.94, 98.46, "Sad-ant-plant! Sad-ant-plant!", True),
    (98.46, 102.08, "Black-bag-flag! Black-bag-flag!", True),
    (102.08, 105.95, "A! A! A! Aunt Ant!", True),
    (105.95, 109.44, "Short A! Short A! Aunt Ant!", True),
    # Outro
    (109.44, 112.54, "これが みじかい A の おと！", False),
    (112.72, 114.90, "Cat, hat, ant, bag.", True),
    (114.90, 116.70, "Fat, mad, sad, black.", True),
    (116.70, 120.35, "A! A! A! Aunt Ant!", True),
    (120.35, 123.50, "Short A! Short A! Aunt Ant!", True),
]


_pil_en = ImageFont.truetype(FONT_PATH_EN, FONT_SIZE_PX)
_pil_jp = ImageFont.truetype(FONT_PATH_JP, JP_SIZE_PX)


def measure(font: ImageFont.FreeTypeFont, s: str) -> int:
    bb = font.getbbox(s)
    return bb[2] - bb[0]


SPACE_W_EN = measure(_pil_en, " ")
SPACE_W_JP = measure(_pil_jp, " ")


def split_words(s: str) -> list[str]:
    return [t for t in re.split(r"\s+", s.strip()) if t]


def wrap_words(words: list[str], font: ImageFont.FreeTypeFont,
               space_w: int, max_w: int) -> list[list[str]]:
    lines: list[list[str]] = [[]]
    cur_w = 0
    for w in words:
        ww = measure(font, w)
        delta = ww + (space_w if lines[-1] else 0)
        if lines[-1] and cur_w + delta > max_w:
            lines.append([w])
            cur_w = ww
        else:
            lines[-1].append(w)
            cur_w += delta
    return lines


def word_positions(lines: list[list[str]], font: ImageFont.FreeTypeFont,
                   space_w: int, line_height: int, baseline_y: int) -> list[tuple[int, int]]:
    top_cy = baseline_y - (len(lines) - 1) * line_height
    out: list[tuple[int, int]] = []
    for li, line_words in enumerate(lines):
        widths = [measure(font, w) for w in line_words]
        total = sum(widths) + space_w * (len(line_words) - 1)
        left = PLAY_W // 2 - total // 2
        cursor = left
        cy = top_cy + li * line_height
        for i, _w in enumerate(line_words):
            cx = cursor + widths[i] // 2
            out.append((cx, cy))
            cursor += widths[i] + space_w
    return out


def word_layouts(lines: list[list[str]], font: ImageFont.FreeTypeFont,
                 space_w: int, line_height: int,
                 baseline_y: int) -> list[tuple[str, int, int, int]]:
    """Return (token, left_x, center_y, width) for rendered display tokens."""
    top_cy = baseline_y - (len(lines) - 1) * line_height
    out: list[tuple[str, int, int, int]] = []
    for li, line_words in enumerate(lines):
        widths = [measure(font, w) for w in line_words]
        total = sum(widths) + space_w * (len(line_words) - 1)
        left = PLAY_W // 2 - total // 2
        cursor = left
        cy = top_cy + li * line_height
        for tok, width in zip(line_words, widths):
            out.append((tok, cursor, cy, width))
            cursor += width + space_w
    return out


def highlight_spans(tok: str, font: ImageFont.FreeTypeFont) -> list[tuple[str, int, int]]:
    """Split a display token into highlightable text spans.

    The display layer can keep punctuation and hyphens, while the box layer
    highlights pronounceable chunks. Examples:
      "Cat," -> [("Cat", x, w)]
      "Fat-cat-hat!" -> Fat / cat / hat at their measured positions.
    """
    spans: list[tuple[str, int, int]] = []
    for match in re.finditer(r"[A-Za-z]+", tok):
        label = match.group(0)
        prefix = tok[:match.start()]
        sub = tok[match.start():match.end()]
        left = measure(font, prefix)
        width = measure(font, sub)
        spans.append((label, left, width))
    return spans


def fmt_ts(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t - h * 3600 - m * 60
    return f"{h}:{m:02d}:{s:05.2f}"


def safe(s: str) -> str:
    return s.replace("{", r"\{").replace("}", r"\}")


def build_ass() -> None:
    ass: list[str] = [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {PLAY_W}",
        f"PlayResY: {PLAY_H}",
        "ScaledBorderAndShadow: yes",
        "WrapStyle: 2",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
        "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: FullLine,{FONT_NAME_EN},{FONT_SIZE_PX},"
        "&H00FFFFFF,&H00FFFFFF,&H00202020,&H80000000,"
        "1,0,0,0,100,100,0,0,1,4,2,5,0,0,0,1",
        f"Style: FullLineJP,{FONT_NAME_JP},{JP_SIZE_PX},"
        "&H00FFFFFF,&H00FFFFFF,&H00202020,&H80000000,"
        "1,0,0,0,100,100,0,0,1,4,2,5,0,0,0,1",
        f"Style: Box,{FONT_NAME_EN},1,"
        f"&H00{BOX_COLOR_BGR},&H00{BOX_COLOR_BGR},"
        f"&H00{BOX_COLOR_BGR},&H00000000,"
        "0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, "
        "MarginV, Effect, Text",
    ]

    n_text = 0
    n_boxes = 0
    baseline_en = PLAY_H - MARGIN_V
    baseline_jp = PLAY_H - MARGIN_V

    for start, end, text, is_en in CUES:
        if end <= start:
            continue
        font = _pil_en if is_en else _pil_jp
        space_w = SPACE_W_EN if is_en else SPACE_W_JP
        line_h = LINE_HEIGHT if is_en else JP_LINE_HEIGHT
        max_w = MAX_WIDTH if is_en else MAX_WIDTH_JP
        words = split_words(text)
        lines = wrap_words(words, font, space_w, max_w)

        if not is_en:
            full = r"\N".join(" ".join(line) for line in lines)
            ass.append(
                f"Dialogue: 1,{fmt_ts(start)},{fmt_ts(end)},FullLineJP,,"
                f"0,0,0,,{{\\an2\\pos({PLAY_W // 2},{baseline_jp})\\fad(80,80)}}"
                f"{safe(full)}"
            )
            n_text += 1
            continue

        positions = word_positions(lines, font, space_w, line_h, baseline_en)
        flat_words = [w for line in lines for w in line]
        layouts = word_layouts(lines, font, space_w, line_h, baseline_en)

        for tok, (cx, cy) in zip(flat_words, positions):
            ass.append(
                f"Dialogue: 1,{fmt_ts(start)},{fmt_ts(end)},FullLine,,"
                f"0,0,0,,{{\\an5\\pos({cx},{cy})\\fad(80,80)}}{safe(tok)}"
            )
            n_text += 1

        highlight_units: list[tuple[str, int, int, int]] = []
        for tok, left, cy, _width in layouts:
            for _label, sub_left, sub_width in highlight_spans(tok, font):
                highlight_units.append((tok, left + sub_left, cy, sub_width))

        per = (end - start) / max(1, len(highlight_units))
        for i, (_tok, left, cy, width) in enumerate(highlight_units):
            w_start = min(end, start + i * per + BOX_TIME_SHIFT)
            w_end = min(end, start + (i + 1) * per + BOX_TIME_SHIFT)
            w_end = min(w_end, w_start + per * 0.88)
            if w_end <= w_start:
                continue
            box_w = width + 2 * BOX_PAD_X
            box_h = FONT_SIZE_PX + 2 * BOX_PAD_Y
            box_left = left - BOX_PAD_X
            box_top = cy - box_h // 2
            path = rounded_rect_path(box_w, box_h, CORNER_R)
            ass.append(
                f"Dialogue: 0,{fmt_ts(w_start)},{fmt_ts(w_end)},Box,,"
                f"0,0,0,,{{\\an7\\pos({box_left},{box_top})\\p1"
                f"\\1c&H{BOX_COLOR_BGR}&\\bord0\\shad0\\fad(35,50)}}{path}"
            )
            n_boxes += 1

    ASS_PATH.write_text("\n".join(ass), encoding="utf-8")
    print(f"wrote {ASS_PATH}")
    print(f"{n_text} text cues + {n_boxes} word boxes")


def burn() -> None:
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(SRC),
        "-vf", f"subtitles={ASS_PATH}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "copy",
        str(OUT),
    ], check=True)
    print(f"done: {OUT} ({OUT.stat().st_size // 1024 // 1024} MB)")


def update_funnics_assets() -> None:
    (FUNNICS_DIR / "captions.ass").write_text(ASS_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    subprocess.run(["cp", str(OUT), str(FUNNICS_DIR / "final_captioned.mp4")], check=True)
    print(f"updated {FUNNICS_DIR / 'captions.ass'}")
    print(f"updated {FUNNICS_DIR / 'final_captioned.mp4'}")


def main() -> None:
    build_ass()
    burn()
    update_funnics_assets()


if __name__ == "__main__":
    main()
