"""Render a still-frame style sample for the new rounded-box captions.

Renders 4 demo phrases on a sample background with one word boxed in
each, using the proposed style (rounded-rect drawing + crisp shadowed
text on top). Output a single PNG so we can iterate on the look without
re-burning the full video.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import ImageFont

ROOT = Path(__file__).parent
OUT = ROOT / "caption_style_sample.png"
ASS_PATH = ROOT / "_caption_sample.ass"
BG_FRAME = ROOT / "_caption_sample_bg.png"
OUT_VIDEO = ROOT / "_caption_sample.mp4"

PLAY_W = 1920
PLAY_H = 1080
FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"
FONT_NAME = "Arial Rounded MT Bold"
FONT_SIZE = 90
LINE_HEIGHT = int(FONT_SIZE * 1.25)

BOX_PAD_X = 18
BOX_PAD_Y = 8
CORNER_R = 22
BOX_COLOR = "6080FF"   # BGR  = RGB FF8060 (warm coral)


# (sentence, active_word_index)
SAMPLES = [
    ("Baker Bear bakes cakes every day", 2),     # bakes
    ("Cap, cap, cap... Add the E!",        3),   # Add
    ("Cap into cape, Cap into cape!",      2),   # cape
    ("Brave mate at the gate.",            0),   # Brave
]


pil = ImageFont.truetype(FONT_PATH, FONT_SIZE)


def w_width(s: str) -> int:
    bb = pil.getbbox(s)
    return bb[2] - bb[0]


SPACE_W = w_width(" ")


def rounded_rect(w: int, h: int, r: int) -> str:
    """ASS \\p1 path string for a rounded rectangle, anchored at (0,0)."""
    k = 0.5523            # cubic-Bezier circle approximation factor
    kr = int(round(r * k))
    parts = [
        f"m {r} 0",
        f"l {w - r} 0",
        f"b {w - r + kr} 0 {w} {r - kr} {w} {r}",
        f"l {w} {h - r}",
        f"b {w} {h - r + kr} {w - r + kr} {h} {w - r} {h}",
        f"l {r} {h}",
        f"b {r - kr} {h} 0 {h - r + kr} 0 {h - r}",
        f"l 0 {r}",
        f"b 0 {r - kr} {r - kr} 0 {r} 0",
    ]
    return " ".join(parts)


def fmt_ts(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t - h * 3600 - m * 60
    return f"{h}:{m:02d}:{s:05.2f}"


def main() -> None:
    # ── 1. Make a soft-cream background still frame ─────────────────
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "lavfi", "-i", f"color=c=0xF6EFE3:size={PLAY_W}x{PLAY_H}:d=2",
        "-frames:v", "1", str(BG_FRAME),
    ], check=True)

    # ── 2. Build ASS with 4 stacked sample phrases ─────────────────
    ass: list[str] = []
    ass.append("[Script Info]")
    ass.append("ScriptType: v4.00+")
    ass.append(f"PlayResX: {PLAY_W}")
    ass.append(f"PlayResY: {PLAY_H}")
    ass.append("ScaledBorderAndShadow: yes")
    ass.append("WrapStyle: 2")
    ass.append("")
    ass.append("[V4+ Styles]")
    ass.append("Format: Name, Fontname, Fontsize, PrimaryColour, "
               "SecondaryColour, OutlineColour, BackColour, Bold, "
               "Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, "
               "Angle, BorderStyle, Outline, Shadow, Alignment, "
               "MarginL, MarginR, MarginV, Encoding")
    # Word: white text + dark outline + soft shadow (kept on top of box)
    ass.append(
        f"Style: Word,{FONT_NAME},{FONT_SIZE},"
        "&H00FFFFFF,&H00FFFFFF,&H00202020,&H80000000,"
        "1,0,0,0,100,100,0,0,1,5,3,5,0,0,0,1"
    )
    # Box: vector-drawing style (BorderStyle=1 + Outline/Shadow=0)
    ass.append(
        f"Style: Box,{FONT_NAME},1,"
        f"&H00{BOX_COLOR},&H00{BOX_COLOR},&H00{BOX_COLOR},&H00000000,"
        "0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1"
    )
    ass.append("")
    ass.append("[Events]")
    ass.append("Format: Layer, Start, End, Style, Name, MarginL, "
               "MarginR, MarginV, Effect, Text")

    # 4 sentences vertically distributed
    n = len(SAMPLES)
    for si, (sentence, active_idx) in enumerate(SAMPLES):
        baseline_y = 200 + si * 200    # rows at y=200,400,600,800
        words = sentence.split(" ")
        widths = [w_width(w) for w in words]
        total = sum(widths) + SPACE_W * (len(words) - 1)
        left = PLAY_W // 2 - total // 2
        cursor = left

        # Pre-compute per-word centers
        centers = []
        for i, w in enumerate(words):
            cx = cursor + widths[i] // 2
            centers.append((cx, widths[i]))
            cursor += widths[i] + SPACE_W

        # Box for active word (Layer 0, drawn first, stays for whole 5s)
        cx, cw = centers[active_idx]
        box_w = cw + 2 * BOX_PAD_X
        box_h = FONT_SIZE + 2 * BOX_PAD_Y
        box_left = cx - box_w // 2
        box_top = baseline_y - box_h // 2
        path = rounded_rect(box_w, box_h, CORNER_R)
        ass.append(
            f"Dialogue: 0,0:00:00.00,0:00:02.00,Box,,0,0,0,,"
            f"{{\\an7\\pos({box_left},{box_top})\\p1\\1c&H{BOX_COLOR}&"
            f"\\bord0\\shad0}}{path}"
        )

        # Words (Layer 1, on top of box)
        for tok, (wcx, _) in zip(words, centers):
            tok_safe = tok.replace("{", "\\{").replace("}", "\\}")
            ass.append(
                f"Dialogue: 1,0:00:00.00,0:00:02.00,Word,,0,0,0,,"
                f"{{\\an5\\pos({wcx},{baseline_y})}}{tok_safe}"
            )

    ASS_PATH.write_text("\n".join(ass), encoding="utf-8")

    # ── 3. Burn into the bg image (1-frame video) ─────────────────
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-loop", "1", "-i", str(BG_FRAME),
        "-vf", f"subtitles={ASS_PATH}",
        "-frames:v", "1", str(OUT),
    ], check=True)
    print(f"wrote {OUT.name}")


if __name__ == "__main__":
    main()
