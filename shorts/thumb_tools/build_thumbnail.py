#!/usr/bin/env python3
"""manifestからTeacher Tacos Shorts用サムネイルを1枚生成する。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Optional

import numpy as np
from PIL import Image, ImageDraw, ImageFont


BASE_DIR = Path(__file__).resolve().parent
MANIFEST_PATH = BASE_DIR / "manifest_thumbs.json"
TAGLINES_PATH = BASE_DIR / "tagline_patterns.json"
DIFFICULTY_PATH = BASE_DIR / "word_difficulty_db.json"
SPEED_TAGLINES_PATH = BASE_DIR / "tagline_speed_patterns.json"
CUTOUT_PATH = BASE_DIR / "tt_welcoming_cutout.png"
THUMBNAILS_DIR = BASE_DIR / "thumbnails"
QUIZZES_PATH = BASE_DIR.parent / "quizzes.json"

FONT_W8 = "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc"
FONT_W6 = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
CANVAS_SIZE = (1080, 1920)
MAX_JPEG_BYTES = 2 * 1024 * 1024


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size, index=0)


def _text_width(text: str, font: ImageFont.FreeTypeFont, stroke_width: int = 0) -> int:
    draw = ImageDraw.Draw(Image.new("L", (1, 1)))
    left, _, right, _ = draw.textbbox(
        (0, 0), text, font=font, stroke_width=stroke_width
    )
    return right - left


def _fit_font(
    text: str,
    font_path: str,
    max_width: int,
    max_size: int,
    min_size: int,
    stroke_width: int = 0,
) -> Optional[ImageFont.FreeTypeFont]:
    for size in range(max_size, min_size - 1, -1):
        font = _font(font_path, size)
        if _text_width(text, font, stroke_width) <= max_width:
            return font
    return None


def thumbnail_filename(item: dict[str, Any]) -> str:
    """IDがすでに単語を含むmanifestでは重複語尾を付けない。"""
    item_id = item["id"]
    word = item["word"]
    if item_id.lower().endswith(f"_{word.lower()}"):
        return f"{item_id}.jpg"
    return f"{item_id}_{word}.jpg"


def _vertical_gradient() -> Image.Image:
    top = np.array([0xB8, 0x00, 0x2E], dtype=np.float32)
    bottom = np.array([0x1F, 0x0A, 0x12], dtype=np.float32)
    t = np.linspace(0.0, 1.0, CANVAS_SIZE[1], dtype=np.float32)[:, None]
    rows = top * (1.0 - t) + bottom * t
    pixels = np.repeat(rows[:, None, :], CANVAS_SIZE[0], axis=1).astype(np.uint8)
    return Image.fromarray(pixels).convert("RGBA")


def _add_radial_glow(canvas: Image.Image) -> None:
    width, height = CANVAS_SIZE
    center_x, center_y, radius = 540, 1590, 600
    yy, xx = np.ogrid[:height, :width]
    distance = np.sqrt((xx - center_x) ** 2 + (yy - center_y) ** 2)
    alpha = np.clip(1.0 - distance / radius, 0.0, 1.0)
    alpha = np.rint(alpha * 30).astype(np.uint8)
    glow = np.empty((height, width, 4), dtype=np.uint8)
    glow[:, :, 0] = 0xFF
    glow[:, :, 1] = 0xE0
    glow[:, :, 2] = 0x66
    glow[:, :, 3] = alpha
    canvas.alpha_composite(Image.fromarray(glow))


def _draw_tagline(canvas: Image.Image, text: str) -> None:
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(
        (40, 100, 1040, 480),
        radius=80,
        fill="#FFD400",
        outline="#000000",
        width=12,
    )
    font = _fit_font(text, FONT_W8, 900, 200, 80)
    if font is None:
        font = _font(FONT_W8, 80)

    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    text_layer = Image.new(
        "RGBA", (right - left, bottom - top + 8), (0, 0, 0, 0)
    )
    text_draw = ImageDraw.Draw(text_layer)
    origin = (-left, -top)
    text_draw.text(
        (origin[0], origin[1] + 8),
        text,
        font=font,
        fill=(0, 0, 0, 128),
    )
    text_draw.text(origin, text, font=font, fill="#111111")

    # 指定の最小80pxでも長い文は、フォント高を保って帯内幅だけに収める。
    if text_layer.width > 900:
        scaled_height = text_layer.height
        text_layer = text_layer.resize((900, scaled_height), Image.Resampling.LANCZOS)
    canvas.alpha_composite(
        text_layer,
        (540 - text_layer.width // 2, 290 - text_layer.height // 2),
    )


def _render_word_line(text: str, font: ImageFont.FreeTypeFont) -> Image.Image:
    scratch = ImageDraw.Draw(Image.new("L", (1, 1)))
    left, top, right, bottom = scratch.textbbox(
        (0, 0), text, font=font, stroke_width=28
    )
    width = right - left
    height = bottom - top
    layer = Image.new("RGBA", (width, height + 14), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    origin = (-left, -top)
    draw.text(
        (origin[0], origin[1] + 14),
        text,
        font=font,
        fill=(0, 0, 0, 153),
        stroke_width=28,
        stroke_fill=(0, 0, 0, 153),
    )
    draw.text(
        origin,
        text,
        font=font,
        fill="#FFFFFF",
        stroke_width=28,
        stroke_fill="#000000",
    )
    return layer


def _draw_word(canvas: Image.Image, word: str) -> None:
    text = word
    font = _fit_font(text, FONT_W8, 1000, 440, 60, stroke_width=28)
    if font is None:
        font = _font(FONT_W8, 60)

    rendered = _render_word_line(text, font)
    group_x = (CANVAS_SIZE[0] - rendered.width) // 2
    group_y = 720 - rendered.height // 2
    canvas.alpha_composite(rendered, (group_x, group_y))


def _add_cutout(canvas: Image.Image) -> None:
    if not CUTOUT_PATH.exists():
        raise FileNotFoundError(
            f"{CUTOUT_PATH} がありません。先に make_tt_cutout.py を実行してください"
        )
    cutout = Image.open(CUTOUT_PATH).convert("RGBA")
    alpha_bbox = cutout.getchannel("A").getbbox()
    if alpha_bbox is None:
        raise ValueError(f"cutoutのアルファが全透明です: {CUTOUT_PATH}")
    cutout = cutout.crop(alpha_bbox)
    cutout.thumbnail((820, 580), Image.Resampling.LANCZOS)
    x = (1080 - cutout.width) // 2
    y = 1300 + (580 - cutout.height) // 2
    canvas.alpha_composite(cutout, (x, y))


def _draw_speed_band(canvas: Image.Image, text: str = "2倍速で覚える裏技!") -> None:
    band_width, band_height = 1100, 240
    band = Image.new("RGBA", (band_width, band_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(band)
    draw.rounded_rectangle(
        (5, 5, band_width - 6, band_height - 6),
        radius=24,
        fill="#B8002E",
        outline="#000000",
        width=10,
    )

    font = _fit_font(text, FONT_W8, 850, 150, 60, stroke_width=4)
    if font is None:
        font = _font(FONT_W8, 60)

    star_font = _font(FONT_W8, 72)
    for x in (70, band_width - 70):
        draw.text(
            (x, band_height // 2),
            "★",
            font=star_font,
            anchor="mm",
            fill="#FFD400",
        )

    draw.text(
        (band_width // 2, band_height // 2 + 8),
        text,
        font=font,
        anchor="mm",
        fill=(0, 0, 0, 128),
        stroke_width=4,
        stroke_fill=(0, 0, 0, 128),
    )
    draw.text(
        (band_width // 2, band_height // 2),
        text,
        font=font,
        anchor="mm",
        fill="#FFFFFF",
        stroke_width=4,
        stroke_fill="#FFD400",
    )

    rotated = band.rotate(
        -3,
        resample=Image.Resampling.BICUBIC,
        expand=True,
    )
    canvas.alpha_composite(
        rotated,
        (
            (CANVAS_SIZE[0] - rotated.width) // 2,
            1620 - rotated.height // 2,
        ),
    )


def _load_quiz_choices(item_id: str) -> Optional[list[str]]:
    """quizzes.json から id 一致の choices を取得。無ければ None。"""
    if not QUIZZES_PATH.exists():
        return None
    try:
        quizzes = _load_json(QUIZZES_PATH)
    except (json.JSONDecodeError, OSError):
        return None
    iterable = quizzes if isinstance(quizzes, list) else quizzes.values()
    for q in iterable:
        if isinstance(q, dict) and q.get("id") == item_id:
            choices = q.get("choices")
            if isinstance(choices, list):
                return [str(c) for c in choices]
    return None


def _draw_choices(canvas: Image.Image, choices: list[str]) -> None:
    """4択を2x2グリッドで小さく描画する。位置: 上帯下〜単語上 (y 510..700)。"""
    if len(choices) < 4:
        return
    items = choices[:4]
    circled = ["①", "②", "③", "④"]
    labels = [f"{circled[i]} {items[i]}" for i in range(4)]

    cell_w, cell_h = 460, 80
    gap_x, gap_y = 40, 20
    grid_w = cell_w * 2 + gap_x
    grid_h = cell_h * 2 + gap_y
    grid_x = (CANVAS_SIZE[0] - grid_w) // 2
    grid_y = 970

    grid = Image.new("RGBA", (grid_w, grid_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(grid)

    for i, label in enumerate(labels):
        col, row = i % 2, i // 2
        x0 = col * (cell_w + gap_x)
        y0 = row * (cell_h + gap_y)
        draw.rounded_rectangle(
            (x0, y0, x0 + cell_w, y0 + cell_h),
            radius=18,
            fill=(0, 0, 0, 140),
            outline=(255, 255, 255, 200),
            width=3,
        )
        font = _fit_font(label, FONT_W6, cell_w - 30, 46, 28)
        if font is None:
            font = _font(FONT_W6, 28)
        draw.text(
            (x0 + cell_w // 2, y0 + cell_h // 2),
            label,
            font=font,
            anchor="mm",
            fill="#FFFFFF",
        )

    canvas.alpha_composite(grid, (grid_x, grid_y))


def _draw_logo(canvas: Image.Image) -> None:
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (1020, 1820),
        "@TeacherTacosEnglish",
        font=_font(FONT_W6, 24),
        anchor="ra",
        fill=(255, 255, 255, 176),
    )


def generate_thumbnail(item: dict[str, Any], output_path: Path) -> Path:
    taglines = _load_json(TAGLINES_PATH)
    difficulty = _load_json(DIFFICULTY_PATH)

    try:
        tagline_pattern = taglines[item["tagline_id"]]
        level_label = difficulty[item["level_key"]]["label"]
    except KeyError as exc:
        raise ValueError(f"manifest参照先が存在しません: {exc}") from exc

    tagline = tagline_pattern["text"]
    if tagline_pattern["needs_level"]:
        tagline = tagline.replace("{level}", level_label)

    speed_id = item.get("speed_tagline_id")
    speed_text = "2倍速で覚える裏技!"
    if speed_id:
        speed_patterns = _load_json(SPEED_TAGLINES_PATH)
        if speed_id not in speed_patterns:
            raise ValueError(f"speed_tagline_idがspeed_patternsにありません: {speed_id}")
        speed_text = speed_patterns[speed_id]["text"]

    canvas = _vertical_gradient()
    _draw_tagline(canvas, tagline)
    _draw_word(canvas, item["word"])
    choices = _load_quiz_choices(item["id"])
    if choices:
        _draw_choices(canvas, choices)
    _add_radial_glow(canvas)
    _add_cutout(canvas)
    _draw_speed_band(canvas, speed_text)
    _draw_logo(canvas)

    output_path = output_path.expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rgb = canvas.convert("RGB")
    rgb.save(output_path, "JPEG", quality=85, optimize=True)
    if output_path.stat().st_size > MAX_JPEG_BYTES:
        print("warning: JPEGが2MBを超えたためquality=75で再保存します")
        rgb.save(output_path, "JPEG", quality=75, optimize=True)
    if output_path.stat().st_size > MAX_JPEG_BYTES:
        print("warning: quality=75でもJPEGが2MBを超えています")

    print(f"生成: {output_path} ({output_path.stat().st_size / 1024:.1f} KB)")
    return output_path


def find_manifest_item(
    *, word: Optional[str] = None, item_id: Optional[str] = None
) -> dict[str, Any]:
    manifest = _load_json(MANIFEST_PATH)
    if word is not None:
        matches = [item for item in manifest if item["word"].casefold() == word.casefold()]
    else:
        matches = [item for item in manifest if item["id"] == item_id]
    if not matches:
        key = f"word={word}" if word is not None else f"id={item_id}"
        raise ValueError(f"manifestに該当項目がありません: {key}")
    if len(matches) > 1:
        raise ValueError(f"manifestの該当項目が重複しています: {matches}")
    return matches[0]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    selector = parser.add_mutually_exclusive_group(required=True)
    selector.add_argument("--word", help="manifestに登録された英単語")
    selector.add_argument("--id", dest="item_id", help="manifestのid")
    parser.add_argument("--out", type=Path, help="出力JPEGパス")
    args = parser.parse_args()

    item = find_manifest_item(word=args.word, item_id=args.item_id)
    output = args.out or THUMBNAILS_DIR / thumbnail_filename(item)
    generate_thumbnail(item, output)


if __name__ == "__main__":
    main()
