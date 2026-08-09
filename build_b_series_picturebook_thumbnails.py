#!/usr/bin/env python3
"""Extract one picturebook thumbnail per displayed B-series sentence."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from build_b_series_index_like_dropin import prepare_lessons


ROOT = Path(__file__).resolve().parent
ASSET_DIR = ROOT / "funnics-beginner-assets"
LESSONS_JSON = ASSET_DIR / "b_series_lessons_ja.json"
THUMB_DIR = ASSET_DIR / "picturebook-thumbs"
MANIFEST = ASSET_DIR / "b_series_picturebook_thumbnails.json"


def thumb_rel(b: int, cue: int) -> str:
    return f"picturebook-thumbs/B{b:02d}/c{cue:03d}.jpg"


def extract_frame(video: Path, time_sec: float, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-ss",
        f"{time_sec:.3f}",
        "-i",
        str(video),
        "-frames:v",
        "1",
        "-vf",
        "scale=480:-2",
        "-q:v",
        "4",
        str(target),
    ]
    subprocess.run(cmd, check=True)


def main() -> int:
    lessons = prepare_lessons(json.loads(LESSONS_JSON.read_text(encoding="utf-8"))["lessons"])
    manifest: list[dict] = []
    total = 0
    skipped = 0
    for lesson in lessons:
        b = int(lesson["b"])
        video = Path(lesson["video"])
        if not video.exists():
            raise FileNotFoundError(video)
        for line in lesson["display_lines"]:
            cue = int(line["cue_index"])
            start = float(line["start"])
            end = float(line["end"])
            mid = max(start + 0.08, min((start + end) / 2, max(start + 0.08, end - 0.08)))
            rel = thumb_rel(b, cue)
            target = ASSET_DIR / rel
            if target.exists() and target.stat().st_size > 0:
                skipped += 1
            else:
                extract_frame(video, mid, target)
            manifest.append(
                {
                    "b": b,
                    "cue_index": cue,
                    "time": round(mid, 3),
                    "start": start,
                    "end": end,
                    "image": rel,
                    "audio": line["audio"],
                    "speaker": line["speaker"],
                    "speaker_ja": line["speaker_ja"],
                    "english": line["english"],
                    "japanese": line["japanese"],
                }
            )
            total += 1
    MANIFEST.write_text(json.dumps({"items": manifest}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"picturebook thumbnails ready: {total} total, {skipped} already existed")
    print(MANIFEST)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
