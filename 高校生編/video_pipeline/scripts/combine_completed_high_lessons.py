#!/usr/bin/env python3
"""Concatenate completed high-school song videos in roughly ten-lesson blocks."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PIPELINE = HERE.parent
COMBINED = PIPELINE / "combined"
WORK = PIPELINE / "work" / "concat"
EDITION = "v5_tacobeat_canonical_vocab_color_only"


def probe(path: Path) -> dict:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration,size:stream=codec_type,codec_name,width,height,"
            "r_frame_rate,sample_rate,channels,start_time,duration",
            "-of", "json", str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def stream(probe_result: dict, codec_type: str) -> dict:
    matches = [item for item in probe_result["streams"] if item.get("codec_type") == codec_type]
    if len(matches) != 1:
        raise RuntimeError(f"expected one {codec_type} stream, found {len(matches)}")
    return matches[0]


def parse_ranges(value: str) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    for raw in value.split(","):
        parts = raw.strip().split("-")
        if len(parts) != 2:
            raise argparse.ArgumentTypeError("ranges must look like 1-10,11-20")
        start, end = (int(item) for item in parts)
        if not (1 <= start <= end <= 160):
            raise argparse.ArgumentTypeError("range endpoints must satisfy 1 <= start <= end <= 160")
        ranges.append((start, end))
    if not ranges:
        raise argparse.ArgumentTypeError("at least one range is required")
    return ranges


def lesson_video(number: int) -> Path:
    root = PIPELINE / f"H{number:03d}" / "output"
    matches = sorted(root.glob(f"*_mixed_japanese_full_ruby_{EDITION}.mp4"))
    if len(matches) != 1:
        raise RuntimeError(f"H{number:03d}: expected one {EDITION} video, found {len(matches)}")
    return matches[0].resolve()


def full_decode(path: Path) -> None:
    subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:v:0", "-f", "null", "-"],
        check=True,
    )
    subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:a:0", "-f", "null", "-"],
        check=True,
    )


def combine_block(start: int, end: int, videos: list[Path]) -> dict:
    label = f"H{start:03d}-H{end:03d}"
    input_probes = [probe(path) for path in videos]
    durations = [float(item["format"]["duration"]) for item in input_probes]
    expected_duration = sum(durations)

    concat_list = WORK / f"{label}.txt"
    concat_list.write_text(
        "".join(
            f"file '{str(path).replace(chr(39), chr(39) + chr(92) + chr(39) + chr(39))}'\n"
            for path in videos
        ),
        encoding="utf-8",
    )
    chapter_file = WORK / f"{label}.ffmeta"
    chapter_lines = [";FFMETADATA1"]
    cursor_ms = 0
    for number, duration in zip(range(start, end + 1), durations):
        stop_ms = cursor_ms + round(duration * 1000)
        chapter_lines.extend(
            [
                "[CHAPTER]",
                "TIMEBASE=1/1000",
                f"START={cursor_ms}",
                f"END={stop_ms}",
                f"title=H{number:03d}",
            ]
        )
        cursor_ms = stop_ms
    chapter_file.write_text("\n".join(chapter_lines) + "\n", encoding="utf-8")

    destination = COMBINED / f"high_{label}_mixed_japanese_full_ruby_{EDITION}.mp4"
    temp_audio = WORK / f"{label}.audio.tmp.m4a"
    temp_final = WORK / f"{label}.final.tmp.mp4"
    temporary = (temp_audio, temp_final)
    try:
        # Decode every lesson separately, reset timestamps, normalise to 48 kHz
        # stereo, and pad/trim to the corresponding video boundary. This avoids
        # the sample-rate/encoder-delay drift previously found in middle L01-L15.
        audio_inputs: list[str] = []
        audio_filters: list[str] = []
        audio_labels: list[str] = []
        for index, (path, duration) in enumerate(zip(videos, durations)):
            audio_inputs.extend(["-i", str(path)])
            label_out = f"a{index}"
            audio_labels.append(f"[{label_out}]")
            audio_filters.append(
                f"[{index}:a:0]aresample=48000:async=0,"
                "aformat=sample_rates=48000:channel_layouts=stereo,"
                f"apad=pad_dur=1,atrim=duration={duration:.6f},"
                f"asetpts=PTS-STARTPTS[{label_out}]"
            )
        audio_filters.append(
            "".join(audio_labels) + f"concat=n={len(videos)}:v=0:a=1[aout]"
        )
        subprocess.run(
            [
                "ffmpeg", "-hide_banner", "-loglevel", "warning", "-y",
                *audio_inputs,
                "-filter_complex", ";".join(audio_filters),
                "-map", "[aout]", "-vn", "-c:a", "aac", "-b:a", "192k",
                "-ar", "48000", str(temp_audio),
            ],
            check=True,
        )

        subprocess.run(
            [
                "ffmpeg", "-hide_banner", "-loglevel", "warning", "-y",
                # Read the verified lesson videos directly through the concat
                # demuxer and stream-copy their H.264 track into the final file.
                # Avoiding a full-size temporary video keeps ten-lesson joins
                # possible on low-space workstations without another lossy encode.
                "-f", "concat", "-safe", "0", "-i", str(concat_list),
                "-i", str(temp_audio), "-i", str(chapter_file),
                "-map", "0:v:0", "-map", "1:a:0", "-map_metadata", "2",
                "-c", "copy", "-movflags", "+faststart", str(temp_final),
            ],
            check=True,
        )

        result_probe = probe(temp_final)
        video_stream = stream(result_probe, "video")
        audio_stream = stream(result_probe, "audio")
        actual_duration = float(result_probe["format"]["duration"])
        video_duration = float(video_stream["duration"])
        audio_duration = float(audio_stream["duration"])
        checks = {
            "expected_lesson_count": len(videos) == end - start + 1,
            "duration_matches": abs(actual_duration - expected_duration) <= 0.20,
            "av_duration_matches": abs(video_duration - audio_duration) <= 0.20,
            "video_1920x1080_h264": video_stream.get("codec_name") == "h264"
            and video_stream.get("width") == 1920
            and video_stream.get("height") == 1080,
            "audio_aac_48khz": audio_stream.get("codec_name") == "aac"
            and audio_stream.get("sample_rate") == "48000",
        }
        if not all(checks.values()):
            raise RuntimeError(f"{label}: structural verification failed: {checks}")
        full_decode(temp_final)
        temp_final.replace(destination)
        return {
            "range": label,
            "lessons": end - start + 1,
            "output": str(destination),
            "inputs": [str(path) for path in videos],
            "expected_duration": expected_duration,
            "actual_duration": actual_duration,
            "video_duration": video_duration,
            "audio_duration": audio_duration,
            "audio_normalisation": "each lesson reset to PTS 0, resampled to 48 kHz stereo, and padded/trimmed to its video duration before concat",
            "chapters": [f"H{number:03d}" for number in range(start, end + 1)],
            "checks": {**checks, "full_video_decode": True, "full_audio_decode": True},
            "status": "PASS",
            "probe": result_probe,
        }
    finally:
        for path in temporary:
            if path.exists():
                path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ranges",
        type=parse_ranges,
        default=parse_ranges("1-10"),
        help="comma-separated completed ranges, for example 1-10,11-20",
    )
    args = parser.parse_args()
    COMBINED.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    report_path = COMBINED / f"VERIFICATION_{EDITION.upper()}.json"
    report = {"version": EDITION, "blocks": []}
    if report_path.exists():
        previous = json.loads(report_path.read_text(encoding="utf-8"))
        if previous.get("version") == EDITION:
            report = previous
    blocks = {item["range"]: item for item in report.get("blocks", [])}
    for start, end in args.ranges:
        videos = [lesson_video(number) for number in range(start, end + 1)]
        result = combine_block(start, end, videos)
        blocks[result["range"]] = result
    report["blocks"] = [blocks[key] for key in sorted(blocks)]
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({row["range"]: row["status"] for row in report["blocks"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
