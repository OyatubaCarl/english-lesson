"""Build kinetic captions for baker_bear_long_a_FINAL.mp4.

Style:
  - Bottom-aligned full lyric line in white (Arial Rounded MT Bold)
  - Currently-pronounced word gets a soft-edged coral box on top
  - Multi-line: PIL pre-computes line breaks, inserts \\N, places \\pos
    per word so the highlight box stays aligned with the glyph (avoids
    libass auto-wrap drift).
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from PIL import ImageFont

ROOT = Path(__file__).parent
TRANSCRIPT = ROOT / "baker_bear_long_a_transcript.json"
SRC = ROOT / "baker_bear_long_a_FINAL.mp4"
OUT = ROOT / "baker_bear_long_a_FINAL_subs.mp4"
ASS_PATH = ROOT / "baker_bear_long_a.ass"

PLAY_W = 1920
PLAY_H = 1080
FONT_PATH_EN = "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"
FONT_PATH_JP = "/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc"
FONT_NAME_EN = "Arial Rounded MT Bold"
FONT_NAME_JP = "Hiragino Maru Gothic ProN W4"
FONT_SIZE_PX = 90
JP_SIZE_PX = 78
LINE_HEIGHT = int(FONT_SIZE_PX * 1.25)
JP_LINE_HEIGHT = int(JP_SIZE_PX * 1.4)

MARGIN_L = 60
MARGIN_R = 60
MARGIN_V = 130                      # bottom margin
MAX_WIDTH = PLAY_W - MARGIN_L - MARGIN_R
MAX_WIDTH_JP = MAX_WIDTH

# Rounded-box highlight
BOX_PAD_X = 18
BOX_PAD_Y = 8
CORNER_R = 22
BOX_COLOR_BGR = "6080FF"            # = RGB FF8060 (warm coral)


def rounded_rect_path(w: int, h: int, r: int) -> str:
    """ASS \\p1 path for a rounded rect, anchored at (0, 0) top-left."""
    k = 0.5523                       # circle approximation factor
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
# v3 — finer line splits, JP "ア"/"エイ" katakana, English "A" in quotes.
CUES: list[tuple[float, float, str, bool]] = [
    # ── Intro ──────────────────────────────────────────────────────
    ( 1.64,  4.82, "Baker Bear bakes cakes every day,", True),
    ( 5.46,  8.40, "Baker Bear bakes cakes every day.", True),
    ( 8.86, 11.20, "ベイカーベア かんがえた。", False),
    (11.66, 13.82, "アントおばさんの A は", False),
    (13.82, 16.10, "「ア」って よむのに……", False),
    (17.46, 20.30, "Baker Bear bakes cakes every day,", True),
    (20.84, 23.74, "Baker Bear bakes cakes every day.", True),
    (23.92, 26.82, "どうして bake の A は", False),
    (26.82, 29.70, "「ア」って よまないんだろう?", False),
    (29.80, 33.50, "あるひ ベイカーベア、", False),
    (33.50, 36.96, "ふしぎな e を ひろった。", False),
    # ── Hook 1 ────────────────────────────────────────────────────
    (36.96, 40.02, "Magic E! Magic E!", True),
    (40.74, 43.64, "A says “A” with Magic E!", True),
    (43.84, 47.62, "Bake, bake, Baker Bear!", True),
    (47.62, 50.64, "Bake with Magic E!", True),
    # ── Verse 1 ───────────────────────────────────────────────────
    (50.76, 52.86, "Cap, cap, cap...", True),
    (52.86, 54.50, "Add the E!", True),
    (54.50, 56.56, "Cap into cape,", True),
    (56.56, 58.50, "Cap into cape!", True),
    (58.50, 60.42, "Can, can, can...", True),
    (60.42, 61.34, "Add the E!", True),
    (61.34, 63.00, "Can into cane,", True),
    (63.00, 64.72, "Can into cane!", True),
    # ── Hook 2 ────────────────────────────────────────────────────
    (64.72, 67.40, "Magic E! Magic E!", True),
    (68.14, 71.16, "A says “A” with Magic E!", True),
    (71.20, 75.06, "Bake, bake, Baker Bear!", True),
    (75.06, 78.76, "Bake with Magic E!", True),
    # ── Verse 2 ───────────────────────────────────────────────────
    (78.76, 80.30, "Mat, mat, mat...", True),
    (80.30, 81.94, "Add the E!", True),
    (81.94, 82.88, "Mat into mate,", True),
    (82.88, 84.92, "Mat into mate!", True),
    (84.92, 87.30, "Plan, plan, plan...", True),
    (87.58, 88.66, "Add the E!", True),
    (88.66, 90.50, "Plan into plane,", True),
    (90.50, 92.30, "Plan into plane!", True),
    (92.30, 94.38, "Slat, slat, slat...", True),
    (94.38, 95.86, "Add the E!", True),
    (96.88, 98.00, "Slat into slate,", True),
    (98.00, 99.22, "Slat into slate!", True),
    # ── Engineer Egg (JP) ─────────────────────────────────────────
    ( 99.22, 102.78, "エンジニアエッグ あらわれて", False),
    (102.78, 104.50, "おとした おとした", False),
    (104.50, 105.92, "ぼくの “e”!", False),
    (105.98, 107.20, "おとした おとした", False),
    (107.20, 110.20, "まほうの “e”!", False),
    (112.02, 115.02, "うしろに \"e\" が ついたなら、", False),
    (115.04, 118.62, "A は “エイ” と よむんだよ。", False),
    (118.80, 121.40, "うしろに \"e\" が ついたなら、", False),
    (121.40, 127.76, "A は “エイ” と うたうんだよ。", False),
    # ── Mini hook ─────────────────────────────────────────────────
    (127.76, 130.70, "Magic E! Magic E!", True),
    (131.10, 134.00, "A says “A” with Magic E!", True),
    (134.00, 136.88, "Magic E! Magic E!", True),
    (138.50, 141.74, "Put it at the end!", True),
    # ── Verse 3 ───────────────────────────────────────────────────
    (141.74, 143.20, "Brave mate at the gate,", True),
    (143.20, 144.60, "Brave mate at the gate.", True),
    (144.60, 146.50, "Pale cane on a plate,", True),
    (146.50, 148.44, "Pale cane on a plate.", True),
    (148.44, 150.16, "Late plane in the lane,", True),
    (150.16, 151.88, "Late plane in the lane.", True),
    (151.88, 153.60, "Safe cape on a slate,", True),
    (153.60, 155.32, "Safe cape on a slate.", True),
    # ── Hook 3 ────────────────────────────────────────────────────
    (155.32, 158.06, "Magic E! Magic E!", True),
    (158.88, 161.44, "A says “A” with Magic E!", True),
    (162.44, 165.80, "Bake, bake, Baker Bear!", True),
    (165.80, 168.94, "Bake with Magic E!", True),
    # ── Bridge — word parade ─────────────────────────────────────
    (168.94, 170.30, "Bake! Bake!", True),
    (170.30, 171.50, "Cake! Cake!", True),
    (171.50, 172.00, "Cape! Cape!", True),
    (172.00, 172.42, "Cane! Cane!", True),
    (172.42, 173.54, "Mate! Mate!", True),
    (173.54, 174.66, "Plane! Plane!", True),
    (174.66, 175.55, "Slate! Slate!", True),
    (175.55, 176.44, "Plate! Plate!", True),
    (176.44, 177.30, "Gate! Gate!", True),
    (177.30, 178.16, "Lane! Lane!", True),
    (178.16, 178.87, "A says ay!", True),
    (178.87, 179.60, "A says ay!", True),
    (180.98, 182.70, "Long A, long A,", True),
    (182.70, 184.46, "Magic E!", True),
    # ── Final hook ────────────────────────────────────────────────
    (184.46, 187.16, "Magic E! Magic E!", True),
    (188.02, 190.52, "A says “A” with Magic E!", True),
    (191.52, 195.02, "Bake, bake, Baker Bear!", True),
    (195.02, 198.80, "Bake with Magic E!", True),
]


# ── Font measurement helpers ──────────────────────────────────────
_pil_en = ImageFont.truetype(FONT_PATH_EN, FONT_SIZE_PX)
_pil_jp = ImageFont.truetype(FONT_PATH_JP, JP_SIZE_PX)


def measure(font: ImageFont.FreeTypeFont, s: str) -> int:
    bb = font.getbbox(s)
    return bb[2] - bb[0]


SPACE_W = measure(_pil_en, " ")


# ── Layout ───────────────────────────────────────────────────────
def wrap_words(words: list[str], font: ImageFont.FreeTypeFont,
               space_w: int, max_w: int) -> list[list[str]]:
    """Greedy wrap into multiple lines respecting max_w."""
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


def word_positions(
    lines: list[list[str]],
    font: ImageFont.FreeTypeFont,
    space_w: int,
    line_height: int,
    baseline_y: int,
    play_w: int,
) -> list[tuple[int, int]]:
    """Return (cx, cy) per word in flat order, given centered alignment.

    baseline_y = vertical center of the LAST line.
    """
    n = len(lines)
    bottom_cy = baseline_y
    top_cy = bottom_cy - (n - 1) * line_height

    out: list[tuple[int, int]] = []
    for li, line_words in enumerate(lines):
        widths = [measure(font, w) for w in line_words]
        total = sum(widths) + space_w * (len(line_words) - 1)
        left = play_w // 2 - total // 2
        cursor = left
        cy = top_cy + li * line_height
        for i, _w in enumerate(line_words):
            cx = cursor + widths[i] // 2
            out.append((cx, cy))
            cursor += widths[i] + space_w
    return out


# ── ASS helpers ───────────────────────────────────────────────────
def fmt_ts(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t - h * 3600 - m * 60
    return f"{h}:{m:02d}:{s:05.2f}"


def split_words(s: str) -> list[str]:
    return [t for t in re.split(r"\s+", s.strip()) if t]


def whisper_in_range(words: list[dict], start: float,
                     end: float) -> list[dict]:
    return [w for w in words
            if w["start"] >= start - 0.05 and w["start"] < end - 0.02]


def main() -> None:
    transcript = json.loads(TRANSCRIPT.read_text())
    all_words = transcript["words"]

    ass: list[str] = []
    ass.append("[Script Info]")
    ass.append("ScriptType: v4.00+")
    ass.append(f"PlayResX: {PLAY_W}")
    ass.append(f"PlayResY: {PLAY_H}")
    ass.append("ScaledBorderAndShadow: yes")
    ass.append("WrapStyle: 2")          # No automatic wrap; honor only \N
    ass.append("")
    ass.append("[V4+ Styles]")
    ass.append("Format: Name, Fontname, Fontsize, PrimaryColour, "
               "SecondaryColour, OutlineColour, BackColour, Bold, "
               "Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, "
               "Angle, BorderStyle, Outline, Shadow, Alignment, "
               "MarginL, MarginR, MarginV, Encoding")
    # FullLine: white text, dark outline + soft shadow, BorderStyle=1
    # Alignment 5 = middle-center; we'll use \pos to anchor manually
    ass.append(
        f"Style: FullLine,{FONT_NAME_EN},{FONT_SIZE_PX},"
        "&H00FFFFFF,&H00FFFFFF,&H00202020,&H80000000,"
        "1,0,0,0,100,100,0,0,1,5,3,5,0,0,0,1"
    )
    ass.append(
        f"Style: FullLineJP,{FONT_NAME_JP},{JP_SIZE_PX},"
        "&H00FFFFFF,&H00FFFFFF,&H00202020,&H80000000,"
        "1,0,0,0,100,100,0,0,1,5,3,5,0,0,0,1"
    )
    # Box: vector-drawing style for the rounded-rect highlight.
    # BorderStyle=1 + Outline=0 + Shadow=0 → no extra rendering, just the
    # filled drawing. Color is set per-dialogue via \1c override.
    ass.append(
        f"Style: Box,{FONT_NAME_EN},1,"
        f"&H00{BOX_COLOR_BGR},&H00{BOX_COLOR_BGR},"
        f"&H00{BOX_COLOR_BGR},&H00000000,"
        "0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1"
    )
    ass.append("")
    ass.append("[Events]")
    ass.append("Format: Layer, Start, End, Style, Name, MarginL, "
               "MarginR, MarginV, Effect, Text")

    OVERHANG = 0.10
    n_lines = 0
    n_boxes = 0

    last_line_baseline_y_en = PLAY_H - MARGIN_V  # baseline (center of last line)
    last_line_baseline_y_jp = PLAY_H - MARGIN_V

    for cstart, cend, text, is_en in CUES:
        if cend <= cstart:
            continue

        font = _pil_en if is_en else _pil_jp
        line_h = LINE_HEIGHT if is_en else JP_LINE_HEIGHT
        max_w = MAX_WIDTH if is_en else MAX_WIDTH_JP
        baseline_y = last_line_baseline_y_en if is_en else last_line_baseline_y_jp

        words = split_words(text)
        lines = wrap_words(words, font, SPACE_W, max_w)

        if is_en:
            # English: per-word text on Layer 1 (full cue duration).
            # Boxes go on Layer 0 BELOW the text, only during active word.
            positions = word_positions(
                lines, font, SPACE_W, line_h, baseline_y, PLAY_W
            )
            flat_for_full: list[str] = [
                w for line_words in lines for w in line_words
            ]
            for tok, (cx, cy) in zip(flat_for_full, positions):
                tok_safe = tok.replace("{", "\\{").replace("}", "\\}")
                ass.append(
                    f"Dialogue: 1,{fmt_ts(cstart)},{fmt_ts(cend)},FullLine,,"
                    f"0,0,0,,"
                    f"{{\\an5\\pos({cx},{cy})\\fad(80,80)}}{tok_safe}"
                )
                n_lines += 1
        else:
            # Japanese: full-line, libass auto-handles CJK wrap
            line_strs = [" ".join(line_words) for line_words in lines]
            full_text = "\\N".join(line_strs)
            full_safe = full_text.replace("{", "\\{").replace("}", "\\}")
            full_anchor_x = PLAY_W // 2
            full_anchor_y = baseline_y + (line_h // 2)
            ass.append(
                f"Dialogue: 0,{fmt_ts(cstart)},{fmt_ts(cend)},FullLineJP,,"
                f"0,0,0,,{{\\an2\\pos({full_anchor_x},{full_anchor_y})\\fad(80,80)}}"
                f"{full_safe}"
            )
            n_lines += 1
            continue
        # Whisper word match
        wsp = whisper_in_range(all_words, cstart, cend)
        flat_words: list[str] = [w for line_words in lines for w in line_words]
        timings: list[tuple[float, float]] = []
        if len(wsp) == len(flat_words) and flat_words:
            for i, ww in enumerate(wsp):
                w_start = ww["start"]
                w_end_audio = ww.get("end", w_start + 0.30)
                next_start = (
                    wsp[i + 1]["start"] if i + 1 < len(wsp) else cend
                )
                w_end = min(w_end_audio + OVERHANG, next_start)
                timings.append((w_start, w_end))
        else:
            n = max(1, len(flat_words))
            per = (cend - cstart) / n
            for i in range(len(flat_words)):
                ws = cstart + i * per
                we = ws + per * 0.85
                timings.append((ws, we))

        for (tok, (cx, cy), (w_start, w_end)) in zip(
            flat_words, positions, timings
        ):
            if w_end <= w_start:
                continue
            cw = measure(font, tok)
            box_w = cw + 2 * BOX_PAD_X
            box_h = FONT_SIZE_PX + 2 * BOX_PAD_Y
            box_left = cx - box_w // 2
            box_top = cy - box_h // 2
            path = rounded_rect_path(box_w, box_h, CORNER_R)
            ass.append(
                f"Dialogue: 0,{fmt_ts(w_start)},{fmt_ts(w_end)},Box,,"
                f"0,0,0,,"
                f"{{\\an7\\pos({box_left},{box_top})\\p1"
                f"\\1c&H{BOX_COLOR_BGR}&\\bord0\\shad0\\fad(40,60)}}{path}"
            )
            n_boxes += 1

    ASS_PATH.write_text("\n".join(ass), encoding="utf-8")
    print(f"  {n_lines} line cues + {n_boxes} word-box cues")
    print(f"  wrote {ASS_PATH.name}")

    if not SRC.exists():
        print(f"ERR: source not found: {SRC}")
        return
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(SRC),
        "-vf", f"subtitles={ASS_PATH}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "copy",
        str(OUT),
    ]
    print("burning subtitles via libass…")
    subprocess.run(cmd, check=True)
    print(f"done: {OUT.name} ({OUT.stat().st_size // 1024 // 1024} MB)")


if __name__ == "__main__":
    main()
