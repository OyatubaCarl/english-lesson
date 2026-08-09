#!/usr/bin/env python3
"""Create H089 dense Style01 JPEG crops while preserving master PNGs."""
from __future__ import annotations

from collections import Counter
import json
import math
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H089"
REF = LESSON / "scenes/character_refs"
OUT = LESSON / "scenes/final_style01"
VISUAL_BIBLE = LESSON / "planning/visual_bible_style01.json"
DURATION = 139.000167
SCENE_COUNT = 116

CROP_SEQUENCES = {
    "C": (None, "1460x821+106+28", "1280x720+196+42"),
    "L": (None, "1460x821+0+28", "1280x720+0+42"),
    "R": (None, "1460x821+212+28", "1280x720+392+42"),
}
ANCHOR_CYCLE = ("C", "L", "R", "C", "R", "L")


def allocate_counts(spans: list[float]) -> list[int]:
    """Give every master two cuts and keep every cut at 1.5s or less."""
    counts = [max(2, math.ceil(span / 1.5)) for span in spans]
    if sum(counts) > SCENE_COUNT:
        raise RuntimeError(f"SCENE_COUNT is too small for dense allocation: {sum(counts)}")
    while sum(counts) < SCENE_COUNT:
        index = max(range(len(spans)), key=lambda i: spans[i] / counts[i])
        counts[index] += 1
    if sum(counts) != SCENE_COUNT or min(counts) < 2:
        raise RuntimeError(f"invalid cut allocation: {sum(counts)=} {min(counts)=}")
    return counts


def schedule() -> list[tuple[float, str, str, str, int]]:
    bible = json.loads(VISUAL_BIBLE.read_text(encoding="utf-8"))
    masters = bible["masters"]
    starts = [float(item["time"]) for item in masters]
    ends = starts[1:] + [DURATION]
    spans = [end - start for start, end in zip(starts, ends)]
    counts = allocate_counts(spans)
    rows: list[tuple[float, str, str, str, int]] = []
    for master_index, (item, start, span, count) in enumerate(
        zip(masters, starts, spans, counts)
    ):
        filename = str(item["file"])
        prefix = filename.removesuffix("_master.png")
        anchor = ANCHOR_CYCLE[master_index % len(ANCHOR_CYCLE)]
        for crop_number in range(1, count + 1):
            scene_start = start + span * (crop_number - 1) / count
            rows.append((scene_start, filename, prefix, anchor, crop_number))
    if len(rows) != SCENE_COUNT:
        raise RuntimeError(f"H089 schedule count: {len(rows)} != {SCENE_COUNT}")
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
    if len(bible["masters"]) != 43:
        raise RuntimeError(f"H089 master count: {len(bible['masters'])} != 43")
    OUT.mkdir(parents=True, exist_ok=True)
    if any(OUT.iterdir()):
        raise RuntimeError(f"H089 output directory must be empty before rebuilding: {OUT}")

    for _, filename, _, _, _ in rows:
        if not (REF / filename).is_file():
            raise FileNotFoundError(REF / filename)

    usage: Counter[str] = Counter()
    expected: list[Path] = []
    for ordinal, (_, filename, prefix, anchor, crop_number) in enumerate(rows, start=1):
        usage[prefix] += 1
        sequence = CROP_SEQUENCES[anchor]
        crop = sequence[min(crop_number - 1, len(sequence) - 1)]
        destination = OUT / f"{ordinal:03d}_{prefix}_{crop_number:02d}.jpg"
        render(REF / filename, destination, crop)
        expected.append(destination)

    actual = sorted(OUT.glob("[0-9][0-9][0-9]_*.jpg"))
    underused = {prefix: count for prefix, count in usage.items() if count < 2}
    if actual != expected or len(actual) != SCENE_COUNT or len(usage) != 43 or underused:
        raise RuntimeError(
            f"H089 scene mismatch actual={len(actual)} expected={SCENE_COUNT} "
            f"masters={len(usage)} underused={underused}"
        )
    print(
        f"H089 final_style01 files verified: {len(actual)}; masters used: {len(usage)}; "
        f"minimum uses: {min(usage.values())}; maximum uses: {max(usage.values())}"
    )


if __name__ == "__main__":
    main()
