#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "app_assets" / "mascot_with_bg" / "tumbled.png"
DEFAULT_OUTPUT = ROOT / "app_assets" / "mascot" / "tumbled.png"
DEFAULT_CLEANED = Path("/tmp/tumbled_floor_cleaned.png")
DEFAULT_REMBG_RAW = Path("/tmp/tumbled_floor_rembg_raw.png")
REMBG = Path("/tmp/rembg-venv/bin/rembg")

FLOOR_Y = 1050
BG_SAMPLE = (50, 50, 200, 200)


def median_bg(rgb: Image.Image) -> tuple[int, int, int]:
    x0, y0, x1, y1 = BG_SAMPLE
    sample = np.asarray(rgb.crop((x0, y0, x1, y1)), dtype=np.uint8)
    return tuple(int(v) for v in np.median(sample, axis=(0, 1)).astype(np.uint8))


def draw_floor_scatter_mask(size: tuple[int, int]) -> Image.Image:
    """Mask only the known lower-floor debris, clipped below FLOOR_Y."""
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)

    # Broad debris regions tuned for this fixed 1024x1536 artwork. They avoid the
    # mascot legs, shoes, torso, and hand while covering tomato/lettuce/meat edges.
    ellipses = [
        (150, 1150, 345, 1288),  # left lettuce
        (150, 1265, 322, 1410),  # left tomato
        (45, 1252, 153, 1335),  # lower-left meat
        (118, 1240, 180, 1300),  # small left meat
        (295, 1078, 376, 1158),  # meat between legs
        (320, 1332, 475, 1468),  # lower-center meat
        (485, 1268, 695, 1415),  # lower-center lettuce
        (658, 1108, 775, 1208),  # mid-right lettuce
        (594, 1188, 640, 1228),  # small green dot
        (618, 1196, 710, 1275),  # center-right meat
        (688, 1242, 742, 1295),  # small crumb group
        (698, 1306, 742, 1350),  # lower crumb
        (772, 1178, 928, 1304),  # right tomato
        (836, 1128, 952, 1212),  # right meat cluster
        (752, 1238, 832, 1308),  # right small lettuce
        (772, 1098, 830, 1140),  # upper tiny crumb
        (894, 1048, 942, 1088),  # tiny floor crumb at cutoff
    ]
    for box in ellipses:
        draw.ellipse(box, fill=255)

    dots = [
        (608, 1264, 7),
        (726, 1207, 8),
        (730, 1339, 8),
        (786, 1328, 9),
        (816, 1110, 7),
        (804, 1165, 6),
        (914, 1188, 8),
        (718, 1270, 7),
        (748, 1256, 7),
        (602, 1372, 5),
    ]
    for x, y, radius in dots:
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=255)

    arr = np.asarray(mask, dtype=np.uint8).copy()
    arr[:FLOOR_Y, :] = 0
    return Image.fromarray(arr)


def clean_floor(input_path: Path, cleaned_path: Path) -> dict[str, int | str | tuple[int, int, int]]:
    rgb = Image.open(input_path).convert("RGB")
    bg = median_bg(rgb)
    core_mask = draw_floor_scatter_mask(rgb.size)
    feather = core_mask.filter(ImageFilter.GaussianBlur(1.0))
    feather_arr = np.asarray(feather, dtype=np.uint8).copy()
    feather_arr[:FLOOR_Y, :] = 0
    feather = Image.fromarray(feather_arr)

    bg_image = Image.new("RGB", rgb.size, bg)
    cleaned = Image.composite(bg_image, rgb, feather)
    cleaned.save(cleaned_path)

    original_arr = np.asarray(rgb)
    cleaned_arr = np.asarray(cleaned)
    core_pixels = int((np.asarray(core_mask) > 0).sum())
    feathered_pixels = int(np.any(original_arr != cleaned_arr, axis=2).sum())

    return {
        "input": str(input_path),
        "cleaned": str(cleaned_path),
        "background_rgb": bg,
        "core_rewrite_pixels": core_pixels,
        "feathered_modified_pixels": feathered_pixels,
    }


def run_rembg(cleaned_path: Path, raw_output_path: Path) -> None:
    if not REMBG.exists():
        raise FileNotFoundError(f"rembg binary not found: {REMBG}")
    subprocess.run(
        [
            str(REMBG),
            "i",
            "-m",
            "isnet-general-use",
            str(cleaned_path),
            str(raw_output_path),
        ],
        check=True,
    )


def remove_floor_alpha_residue(raw_output_path: Path, final_output_path: Path) -> dict[str, int | str]:
    rgba = Image.open(raw_output_path).convert("RGBA")
    arr = np.asarray(rgba, dtype=np.uint8).copy()
    alpha = arr[:, :, 3]
    height, width = alpha.shape
    y_coords = np.indices((height, width))[0]

    core_mask = draw_floor_scatter_mask(rgba.size)
    cleanup_mask = core_mask.filter(ImageFilter.MaxFilter(5))
    cleanup = np.asarray(cleanup_mask, dtype=np.uint8) > 0
    cleanup[:FLOOR_Y, :] = False

    high_alpha = Image.fromarray(((alpha >= 128) * 255).astype(np.uint8))
    near_body_edge = np.asarray(high_alpha.filter(ImageFilter.MaxFilter(9)), dtype=np.uint8) > 0
    low_floor_residue = (y_coords >= FLOOR_Y) & (alpha < 90) & (~near_body_edge)

    zero_mask = cleanup | low_floor_residue
    alpha_before = alpha.copy()
    arr[zero_mask, 3] = 0
    Image.fromarray(arr).save(final_output_path)

    return {
        "raw_rembg": str(raw_output_path),
        "output": str(final_output_path),
        "alpha_zeroed_pixels": int(((alpha_before > 0) & zero_mask).sum()),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--cleaned", type=Path, default=DEFAULT_CLEANED)
    parser.add_argument("--raw-rembg", type=Path, default=DEFAULT_REMBG_RAW)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    stats = clean_floor(args.input, args.cleaned)
    run_rembg(args.cleaned, args.raw_rembg)
    stats.update(remove_floor_alpha_residue(args.raw_rembg, args.output))
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
