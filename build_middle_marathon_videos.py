#!/usr/bin/env python3
"""Build three middle-school all-in-one videos from existing YouTube lessons."""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
YT_MAP = ROOT / "youtube-map.json"
OUT_DIR = ROOT / "dist" / "middle-marathon"
DOWNLOAD_DIR = OUT_DIR / "downloads"
NORMALIZED_DIR = OUT_DIR / "normalized"
PARTS_DIR = OUT_DIR / "parts"
MANIFEST = OUT_DIR / "manifest.json"

PARTS = [
    {
        "key": "part1",
        "part": 1,
        "start": 1,
        "end": 15,
        "title": "中学生編 L1-L15 一気見",
        "filename": "middle_L01_L15_marathon.mp4",
    },
    {
        "key": "part2",
        "part": 2,
        "start": 16,
        "end": 30,
        "title": "中学生編 L16-L30 一気見",
        "filename": "middle_L16_L30_marathon.mp4",
    },
    {
        "key": "part3",
        "part": 3,
        "start": 31,
        "end": 45,
        "title": "中学生編 L31-L45 一気見",
        "filename": "middle_L31_L45_marathon.mp4",
    },
]


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def capture(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True).strip()


def load_middle_map() -> dict[str, str | list[str]]:
    data = json.loads(YT_MAP.read_text(encoding="utf-8"))
    return data["middle"]


def safe_existing_mp4(pattern: str) -> Path | None:
    matches = sorted(DOWNLOAD_DIR.glob(pattern))
    return matches[0] if matches else None


def download_video(video_id: str, label: str) -> Path:
    existing = safe_existing_mp4(f"{label}_{video_id}.*")
    if existing:
        print(f"download exists: {existing.name}")
        return existing

    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    out_tmpl = str(DOWNLOAD_DIR / f"{label}_{video_id}.%(ext)s")
    run(
        [
            "yt-dlp",
            "--no-playlist",
            "-f",
            "bv*[height<=1080][vcodec^=avc1]+ba[ext=m4a]/b[height<=1080][vcodec^=avc1]/bv*[height<=1080]+ba/b[height<=1080]",
            "--merge-output-format",
            "mp4",
            "-o",
            out_tmpl,
            f"https://youtu.be/{video_id}",
        ]
    )

    existing = safe_existing_mp4(f"{label}_{video_id}.*")
    if not existing:
        raise FileNotFoundError(f"downloaded file not found for {label}_{video_id}")
    return existing


def normalize_video(source: Path, target: Path) -> None:
    if target.exists() and target.stat().st_size > 0:
        print(f"normalized exists: {target.name}")
        return

    target.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(source),
            "-vf",
            "scale=1920:1080:force_original_aspect_ratio=decrease,"
            "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,format=yuv420p",
            "-af",
            "aresample=48000,aformat=channel_layouts=stereo",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "22",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-movflags",
            "+faststart",
            str(target),
        ]
    )


def duration_seconds(video: Path) -> float:
    out = capture(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(video),
        ]
    )
    return float(out)


def concat_part(part: dict, clips: list[Path]) -> Path:
    output = PARTS_DIR / part["filename"]
    list_file = PARTS_DIR / f"{part['key']}_concat.txt"
    PARTS_DIR.mkdir(parents=True, exist_ok=True)
    list_file.write_text(
        "".join(f"file '{clip.as_posix()}'\n" for clip in clips),
        encoding="utf-8",
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_file),
            "-c",
            "copy",
            "-movflags",
            "+faststart",
            str(output),
        ]
    )
    return output


def part_items(middle_map: dict[str, str | list[str]], start: int, end: int) -> list[dict]:
    items = []
    for lesson in range(start, end + 1):
        raw = middle_map[str(lesson)]
        ids = raw if isinstance(raw, list) else [raw]
        for idx, video_id in enumerate(ids, start=1):
            suffix = f"_{idx}" if len(ids) > 1 else ""
            label = f"L{lesson:02d}{suffix}"
            items.append({"lesson": lesson, "label": label, "video_id": video_id})
    return items


def main() -> int:
    middle_map = load_middle_map()
    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": str(YT_MAP),
        "parts": [],
    }

    for part in PARTS:
        print("")
        print(f"=== {part['title']} ===")
        items = part_items(middle_map, part["start"], part["end"])
        normalized_clips = []
        manifest_items = []
        for item in items:
            source = download_video(item["video_id"], item["label"])
            normalized = NORMALIZED_DIR / f"{item['label']}_{item['video_id']}_1080p.mp4"
            normalize_video(source, normalized)
            normalized_clips.append(normalized)
            manifest_items.append(
                {
                    **item,
                    "source": str(source),
                    "normalized": str(normalized),
                    "duration": round(duration_seconds(normalized), 3),
                }
            )

        output = concat_part(part, normalized_clips)
        manifest["parts"].append(
            {
                **part,
                "video": str(output),
                "duration": round(duration_seconds(output), 3),
                "items": manifest_items,
            }
        )
        print(f"wrote: {output}")

    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print("")
    print(f"manifest: {MANIFEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
