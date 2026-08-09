#!/usr/bin/env python3
"""Concatenate the completed middle-school full-ruby videos in blocks of 15."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "output"
COMBINED = ROOT / "combined"
WORK = ROOT / "work" / "concat"
EDITION = "v4_inline_canonical_vocab"


def probe(path: Path) -> dict:
    result = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration,size:stream=codec_type,codec_name,width,height,"
        "r_frame_rate,sample_rate,channels,start_time,duration",
        "-of", "json", str(path),
    ], check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def stream(probe_result: dict, codec_type: str) -> dict:
    matches = [item for item in probe_result["streams"] if item.get("codec_type") == codec_type]
    if len(matches) != 1:
        raise RuntimeError(f"expected one {codec_type} stream, found {len(matches)}")
    return matches[0]


def parse_starts(value: str) -> list[int]:
    starts = sorted({int(item.strip()) for item in value.split(",") if item.strip()})
    if not starts or any(item not in (1, 16, 31) for item in starts):
        raise argparse.ArgumentTypeError("--starts must contain 1, 16, or 31")
    return starts


def combine_block(start: int, videos: list[Path], concat_list: Path, destination: Path) -> dict:
    end = start + 14
    input_probes = [probe(path) for path in videos]
    expected_duration = sum(float(item["format"]["duration"]) for item in input_probes)
    source_audio_duration = sum(float(stream(item, "audio")["duration"]) for item in input_probes)
    expected_audio_duration = expected_duration

    # The individual lessons are not all encoded at the same audio sample rate
    # (L1/L6 are 48 kHz while most middle lessons are 44.1 kHz). The concat
    # demuxer requires matching stream parameters; feeding the mixed AAC packets
    # directly made L2-L5 play about 8.8% fast in the L01-L15 block. Concatenate
    # video and audio separately: video remains a lossless stream copy, while
    # every lesson's audio is decoded, reset to a zero-based clock, normalised to
    # 48 kHz stereo, and then joined with the concat filter.
    temp_video = WORK / f"L{start:02d}-L{end:02d}.video.tmp.mp4"
    temp_audio = WORK / f"L{start:02d}-L{end:02d}.audio.tmp.m4a"
    temp_final = destination.with_name(destination.stem + ".tmp.mp4")
    temporary = (temp_video, temp_audio, temp_final)
    try:
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "warning", "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_list),
            "-map", "0:v:0", "-an", "-c:v", "copy",
            "-movflags", "+faststart", str(temp_video),
        ], check=True)

        audio_inputs: list[str] = []
        audio_filters: list[str] = []
        audio_labels: list[str] = []
        for index, path in enumerate(videos):
            audio_inputs.extend(["-i", str(path)])
            label = f"a{index}"
            audio_labels.append(f"[{label}]")
            lesson_duration = float(input_probes[index]["format"]["duration"])
            audio_filters.append(
                f"[{index}:a:0]aresample=48000:async=0,"
                f"aformat=sample_rates=48000:channel_layouts=stereo,"
                # Preserve the exact video boundary for every lesson. AAC
                # encoder delay makes each source audio stream about 0.02 s
                # shorter than its video; without padding, that error would
                # accumulate to roughly 0.24 s by L15.
                f"apad=pad_dur=1,atrim=duration={lesson_duration:.6f},"
                f"asetpts=PTS-STARTPTS[{label}]"
            )
        audio_filters.append(
            "".join(audio_labels) + f"concat=n={len(videos)}:v=0:a=1[aout]"
        )
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "warning", "-y",
            *audio_inputs,
            "-filter_complex", ";".join(audio_filters),
            "-map", "[aout]", "-vn", "-c:a", "aac", "-b:a", "192k",
            "-ar", "48000", "-movflags", "+faststart", str(temp_audio),
        ], check=True)

        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "warning", "-y",
            "-i", str(temp_video), "-i", str(temp_audio),
            "-map", "0:v:0", "-map", "1:a:0", "-c", "copy",
            "-movflags", "+faststart", str(temp_final),
        ], check=True)

        destination_probe = probe(temp_final)
        video_stream = stream(destination_probe, "video")
        audio_stream = stream(destination_probe, "audio")
        actual_duration = float(destination_probe["format"]["duration"])
        video_duration = float(video_stream["duration"])
        audio_duration = float(audio_stream["duration"])
        if abs(actual_duration - expected_duration) > 1.0:
            raise RuntimeError(
                f"L{start:02d}-L{end:02d}: duration mismatch "
                f"expected={expected_duration:.3f}, actual={actual_duration:.3f}"
            )
        if abs(audio_duration - expected_audio_duration) > 0.5:
            raise RuntimeError(
                f"L{start:02d}-L{end:02d}: audio duration mismatch "
                f"expected={expected_audio_duration:.3f}, actual={audio_duration:.3f}"
            )
        if abs(video_duration - audio_duration) > 0.5:
            raise RuntimeError(
                f"L{start:02d}-L{end:02d}: A/V duration mismatch "
                f"video={video_duration:.3f}, audio={audio_duration:.3f}"
            )
        if audio_stream.get("sample_rate") != "48000":
            raise RuntimeError(
                f"L{start:02d}-L{end:02d}: expected 48 kHz audio, "
                f"found {audio_stream.get('sample_rate')}"
            )

        temp_final.replace(destination)
        return {
            "range": f"L{start:02d}-L{end:02d}",
            "lessons": 15,
            "output": str(destination),
            "expected_duration": expected_duration,
            "expected_audio_duration": expected_audio_duration,
            "source_audio_duration_before_boundary_padding": source_audio_duration,
            "audio_normalisation": "each lesson reset to PTS 0, resampled to 48 kHz stereo, and padded/trimmed to its video duration before concat",
            "av_duration_delta": abs(video_duration - audio_duration),
            "probe": destination_probe,
        }
    finally:
        for path in temporary:
            if path.exists():
                path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--starts", type=parse_starts, default=parse_starts("1,16,31"),
        help="comma-separated block starts: 1,16,31 (default: all)",
    )
    args = parser.parse_args()
    COMBINED.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    report_path = COMBINED / f"VERIFICATION_{EDITION.upper()}.json"
    report = {
        "edition": "current-lesson canonical vocabulary only + mixed Japanese + full kanji ruby + English meaning ruby",
        "version": EDITION,
        "blocks": [],
    }
    if report_path.exists():
        previous = json.loads(report_path.read_text(encoding="utf-8"))
        if previous.get("version") == EDITION:
            report = previous
    blocks = {item["range"]: item for item in report.get("blocks", [])}
    for start in args.starts:
        end = start + 14
        videos = []
        for lesson in range(start, end + 1):
            matches = list((OUTPUT / f"L{lesson:02d}").glob(f"*_mixed_japanese_full_ruby_{EDITION}.mp4"))
            if len(matches) != 1:
                raise RuntimeError(f"L{lesson:02d}: expected one video, found {len(matches)}")
            videos.append(matches[0].resolve())
        concat_list = WORK / f"L{start:02d}-L{end:02d}.txt"
        concat_list.write_text(
            "".join(f"file '{str(path).replace(chr(39), chr(39) + chr(92) + chr(39) + chr(39))}'\n" for path in videos),
            encoding="utf-8",
        )
        destination = COMBINED / f"middle_L{start:02d}-L{end:02d}_mixed_japanese_full_ruby_{EDITION}.mp4"
        item = combine_block(start, videos, concat_list, destination)
        blocks[item["range"]] = item
    report["blocks"] = [blocks[key] for key in sorted(blocks)]
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
