#!/usr/bin/env python3
"""Slice a generated 4x3 phonics sheet into card images and update JSON."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from PIL import Image


DATA_PATH = Path("phonics-audio-items.json")
OUT_ROOT = Path("assets/card-generated")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sheet", required=True, help="Generated sheet image path")
    parser.add_argument("--batch", required=True, help="Batch id, for example batch-001")
    parser.add_argument("--start", type=int, required=True, help="1-based first card index")
    parser.add_argument("--count", type=int, default=12)
    parser.add_argument("--cols", type=int, default=4)
    parser.add_argument("--rows", type=int, default=3)
    args = parser.parse_args()

    sheet_path = Path(args.sheet)
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    words = data["words"]
    start = args.start - 1
    cards = words[start : start + args.count]
    if len(cards) != args.count:
        raise SystemExit(f"Expected {args.count} cards, found {len(cards)}")

    batch_dir = OUT_ROOT / args.batch
    sheet_dir = OUT_ROOT / "sheets"
    batch_dir.mkdir(parents=True, exist_ok=True)
    sheet_dir.mkdir(parents=True, exist_ok=True)

    sheet_copy = sheet_dir / f"{args.batch}.png"
    shutil.copy2(sheet_path, sheet_copy)

    image = Image.open(sheet_path).convert("RGB")
    width, height = image.size
    tile_w = width / args.cols
    tile_h = height / args.rows
    if abs(tile_w - tile_h) > 3:
        print(f"Warning: tile is not square: {tile_w:.1f} x {tile_h:.1f}")

    for offset, card in enumerate(cards):
        col = offset % args.cols
        row = offset // args.cols
        left = round(col * tile_w)
        top = round(row * tile_h)
        right = round((col + 1) * tile_w)
        bottom = round((row + 1) * tile_h)
        tile = image.crop((left, top, right, bottom))
        side = min(tile.size)
        x = (tile.width - side) // 2
        y = (tile.height - side) // 2
        tile = tile.crop((x, y, x + side, y + side)).resize((512, 512), Image.Resampling.LANCZOS)
        out_path = batch_dir / f"{card['id']}.png"
        tile.save(out_path, "PNG", optimize=True)
        card["image"] = str(out_path)
        card["imageSource"] = "generated-sheet"
        card["imageBatch"] = args.batch

    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Sliced {len(cards)} cards from {sheet_path}")
    print(f"Copied sheet to {sheet_copy}")
    print(f"Updated cards {args.start}-{args.start + len(cards) - 1}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
