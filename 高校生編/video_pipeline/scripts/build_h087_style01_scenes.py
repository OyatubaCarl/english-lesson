#!/usr/bin/env python3
"""Create H087 dense Style01 JPEG crops while preserving master PNGs."""
from __future__ import annotations

from collections import Counter
import json
import math
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H087"
REF = LESSON / "scenes/character_refs"
OUT = LESSON / "scenes/final_style01"
VISUAL_BIBLE = LESSON / "planning/visual_bible_style01.json"
DURATION = 111.320167
SCENE_COUNT = 94

CROP_SEQUENCES = {
    "C": (None, "1460x821+106+28", "1280x720+196+42"),
    "L": (None, "1460x821+0+28", "1280x720+0+42"),
    "R": (None, "1460x821+212+28", "1280x720+392+42"),
}
ANCHOR_CYCLE = ("C", "L", "R", "C", "R", "L")


def allocate_counts(spans: list[float]) -> list[int]:
    counts = [max(1, math.ceil(span / 1.5)) for span in spans]
    if sum(counts) > SCENE_COUNT:
        raise RuntimeError(f"SCENE_COUNT is too small for dense allocation: {sum(counts)}")
    while sum(counts) < SCENE_COUNT:
        index = max(range(len(spans)), key=lambda i: spans[i] / counts[i])
        counts[index] += 1
    return counts


def schedule() -> list[tuple[float, str, str, str, int]]:
    bible = json.loads(VISUAL_BIBLE.read_text(encoding="utf-8"))
    masters = bible["timeline"]
    starts = [float(item["time"]) for item in masters]
    ends = starts[1:] + [DURATION]
    spans = [end - start for start, end in zip(starts, ends)]
    counts = allocate_counts(spans)
    rows: list[tuple[float, str, str, str, int]] = []
    for master_index, (item, start, span, count) in enumerate(zip(masters, starts, spans, counts)):
        filename = str(item["file"])
        prefix = filename.removesuffix("_master.png")
        anchor = ANCHOR_CYCLE[master_index % len(ANCHOR_CYCLE)]
        for crop_number in range(1, count + 1):
            rows.append((start + span * (crop_number - 1) / count, filename, prefix, anchor, crop_number))
    return rows


def render(source: Path, destination: Path, crop: str | None) -> None:
    command = ["magick", str(source)]
    if crop is not None:
        command.extend([
            "-crop", crop, "+repage", "-resize", "1672x941^",
            "-gravity", "center", "-extent", "1672x941",
        ])
    command.extend(["-sampling-factor", "4:2:0", "-quality", "92", str(destination)])
    subprocess.run(command, check=True)


def main() -> None:
    rows = schedule()
    bible = json.loads(VISUAL_BIBLE.read_text(encoding="utf-8"))
    if len(bible["masters"]) != 36 or len(bible["timeline"]) != 45 or len(rows) != SCENE_COUNT:
        raise RuntimeError(
            f"H087 counts: masters={len(bible['masters'])} "
            f"timeline={len(bible['timeline'])} scenes={len(rows)}"
        )
    OUT.mkdir(parents=True, exist_ok=True)
    if any(OUT.iterdir()):
        raise RuntimeError(f"H087 output directory must be empty before rebuilding: {OUT}")
    for _, filename, _, _, _ in rows:
        if not (REF / filename).is_file():
            raise FileNotFoundError(REF / filename)

    usage: Counter[str] = Counter()
    expected: list[Path] = []
    for ordinal, (_, filename, prefix, anchor, _) in enumerate(rows, start=1):
        usage[prefix] += 1
        crop_number = usage[prefix]
        sequence = CROP_SEQUENCES[anchor]
        crop = sequence[min(crop_number - 1, len(sequence) - 1)]
        destination = OUT / f"{ordinal:03d}_{prefix}_{crop_number:02d}.jpg"
        render(REF / filename, destination, crop)
        expected.append(destination)

    actual = sorted(OUT.glob("[0-9][0-9][0-9]_*.jpg"))
    if actual != expected or len(actual) != SCENE_COUNT or len(usage) != 36:
        raise RuntimeError(
            f"H087 scene mismatch actual={len(actual)} masters={len(usage)}"
        )
    print(
        f"H087 final_style01 files verified: {len(actual)}; masters used: {len(usage)}; "
        f"minimum uses: {min(usage.values())}; maximum uses: {max(usage.values())}"
    )


if __name__ == "__main__":
    main()
