#!/usr/bin/env python3
"""Prototype picturebook thumbnails for B1-B3 only.

This does not touch index.html. It replaces the local preview/drop-in thumbnail
JPEGs for B1-B3, while backing up the original video-extracted thumbnails.
B1-B2 are read from the currently approved local selected source maps, and B3
uses the built-in imagegen skill output created from the project instructions.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "funnics-beginner-assets"
THUMBS = ASSETS / "picturebook-thumbs"
BACKUP = ASSETS / "picturebook-thumbs-video-backup"
SONGS = Path("/Users/masaki/Documents/ClaudeCode/FunnicsIsland/songs")
REPORT = ASSETS / "b1_b3_picturebook_prototype_sources.json"
CONTACT_SHEET = ASSETS / "b1_b3_picturebook_prototype_contact_sheet.jpg"

SIZE = (480, 270)


SELECTED_DIRS = {
    "B01": SONGS / "05_beginner_tom_b1" / "picturebook_imagegen_20260510_selected",
    "B02": SONGS / "06_beginner_tom_b2" / "picturebook_imagegen_20260510_selected",
}
B3_IMAGEGEN_DIR = SONGS / "07_beginner_tom_b3" / "picturebook_imagegen_20260509_built_in"
DISALLOWED_PATH_PARTS = (
    "/.codex/generated_images/",
    "/api_do_not_use/",
    "/rejected_do_not_use/",
    "/superseded_do_not_use/",
)


def b3_imagegen(filename: str) -> Path:
    return B3_IMAGEGEN_DIR / filename


B3_MAPPING: list[tuple[int, str, Path]] = [
    (1, "Tom is not from this island", b3_imagegen("c001_not_from_island.png")),
    (2, "Teacher Tacos reassures Tom", b3_imagegen("c002_dont_worry.png")),
    (4, "not alone in the island village", b3_imagegen("c004_not_alone.png")),
    (6, "Aunt Ant arrives", b3_imagegen("c006_aunt_ant_arrives.png")),
    (8, "Tom notices Aunt Ant is not a taco", b3_imagegen("c008_not_a_taco.png")),
    (10, "Aunt Ant says she is an ant", b3_imagegen("c010_i_am_an_ant.png")),
    (12, "island is not only for tacos", b3_imagegen("c012_not_only_tacos.png")),
    (14, "Aunt Ant welcomes Tom", b3_imagegen("c014_welcome_here.png")),
    (16, "Tom has new friends", b3_imagegen("c016_new_friends.png")),
]


def selected_rows(lesson: str) -> list[tuple[int, str, Path]]:
    folder = SELECTED_DIRS[lesson]
    payload = json.loads((folder / "source_map.json").read_text(encoding="utf-8"))
    rows = []
    for cue_text, filename in sorted(payload["cue_sources"].items(), key=lambda item: int(item[0])):
        cue = int(cue_text)
        note = Path(filename).stem.replace("_", " ")
        rows.append((cue, note, folder / filename))
    return rows


def build_mapping() -> dict[str, list[tuple[int, str, Path]]]:
    return {
        "B01": selected_rows("B01"),
        "B02": selected_rows("B02"),
        "B03": B3_MAPPING,
    }


MAPPING: dict[str, list[tuple[int, str, Path]]] = build_mapping()


def fit_cover(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    img = img.convert("RGB")
    sw, sh = size
    iw, ih = img.size
    scale = max(sw / iw, sh / ih)
    nw, nh = round(iw * scale), round(ih * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - sw) // 2
    top = (nh - sh) // 2
    return img.crop((left, top, left + sw, top + sh))


def backup_original(target: Path) -> None:
    rel = target.relative_to(THUMBS)
    backup = BACKUP / rel
    if backup.exists():
        return
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(target, backup)


def validate_source(source: Path) -> None:
    text = str(source.resolve())
    if any(part in text for part in DISALLOWED_PATH_PARTS):
        raise ValueError(f"Refusing disallowed image source: {source}")
    if not source.exists():
        raise FileNotFoundError(source)


def write_thumb(source: Path, target: Path) -> None:
    validate_source(source)
    if target.exists():
        backup_original(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    img = fit_cover(Image.open(source), SIZE)
    img.save(target, "JPEG", quality=90, optimize=True)


def make_contact_sheet(report_items: list[dict]) -> None:
    cols = 3
    label_h = 34
    rows = (len(report_items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * SIZE[0], rows * (SIZE[1] + label_h)), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for idx, item in enumerate(report_items):
        row, col = divmod(idx, cols)
        x = col * SIZE[0]
        y = row * (SIZE[1] + label_h)
        thumb = Image.open(ASSETS / item["image"]).convert("RGB")
        sheet.paste(thumb, (x, y))
        label = f'{item["lesson"]} c{item["cue"]:03d}: {item["note"]}'
        draw.text((x + 8, y + SIZE[1] + 8), label[:72], fill=(20, 20, 20), font=font)
    sheet.save(CONTACT_SHEET, "JPEG", quality=88, optimize=True)


def main() -> int:
    report_items: list[dict] = []
    for lesson, rows in MAPPING.items():
        for cue, note, source in rows:
            target = THUMBS / lesson / f"c{cue:03d}.jpg"
            write_thumb(source, target)
            report_items.append(
                {
                    "lesson": lesson,
                    "cue": cue,
                    "note": note,
                    "source": str(source),
                    "image": str(target.relative_to(ASSETS)),
                    "backup": str((BACKUP / lesson / f"c{cue:03d}.jpg").relative_to(ASSETS)),
                }
            )

    REPORT.write_text(json.dumps({"items": report_items}, ensure_ascii=False, indent=2), encoding="utf-8")
    make_contact_sheet(report_items)
    print(f"updated {len(report_items)} B1-B3 picturebook thumbnails")
    print(REPORT)
    print(CONTACT_SHEET)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
