#!/usr/bin/env python3
"""Build the L01-L15 combined video with the revised Lesson 6."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
VALIDATION = (
    PROJECT_ROOT
    / "中学生編/mio_video_l1_l45_sentence_v3/shared/full_middle_video_validation.json"
)
REVISED_L6 = (
    PROJECT_ROOT
    / "中学生編/mio_video_l2_l10_sentence_v2/L6_revision_v3/output/"
    "l6_grandmothers_birthday_revision_v3_mio_bilingual_camera.mp4"
)
OUTPUT_DIR = Path(__file__).resolve().parent
WORK_DIR = OUTPUT_DIR / "work_l6_revision_v3"
OUTPUT = (
    OUTPUT_DIR
    / "middle_lessons_L01-L15_mio_bilingual_combined_L6_revision_v3.mp4"
)
MANIFEST = OUTPUT_DIR / "L01-L15_L6_revision_v3_validation.json"
TARGET_AUDIO_RATE = 44100


def run(command: list[str], capture: bool = False) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(command))
    return subprocess.run(
        command,
        check=True,
        capture_output=capture,
        text=True,
    )


def probe(path: Path) -> dict:
    result = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            (
                "format=duration,size,bit_rate:"
                "stream=index,codec_type,codec_name,width,height,"
                "r_frame_rate,sample_rate,channels"
            ),
            "-of",
            "json",
            str(path),
        ],
        capture=True,
    )
    return json.loads(result.stdout)


def main() -> None:
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    source_manifest = json.loads(VALIDATION.read_text(encoding="utf-8"))
    selected = [item for item in source_manifest["videos"] if 1 <= item["lesson"] <= 15]
    if len(selected) != 15:
        raise RuntimeError(f"expected 15 lessons, found {len(selected)}")

    inputs: list[dict] = []
    concat_paths: list[Path] = []
    for item in selected:
        lesson = int(item["lesson"])
        source = REVISED_L6 if lesson == 6 else PROJECT_ROOT / item["path"]
        if not source.exists():
            raise FileNotFoundError(source)
        metadata = probe(source)
        video_stream = next(
            stream for stream in metadata["streams"] if stream["codec_type"] == "video"
        )
        audio_stream = next(
            stream for stream in metadata["streams"] if stream["codec_type"] == "audio"
        )
        if (
            video_stream["codec_name"],
            video_stream["width"],
            video_stream["height"],
            video_stream["r_frame_rate"],
        ) != ("h264", 1920, 1080, "30/1"):
            raise RuntimeError(f"unexpected video stream in L{lesson}: {video_stream}")
        if audio_stream["codec_name"] != "aac" or audio_stream["channels"] != 2:
            raise RuntimeError(f"unexpected audio stream in L{lesson}: {audio_stream}")

        concat_path = source
        if int(audio_stream["sample_rate"]) != TARGET_AUDIO_RATE:
            concat_path = WORK_DIR / f"L{lesson:02d}_audio_44100.mp4"
            run(
                [
                    "ffmpeg",
                    "-hide_banner",
                    "-loglevel",
                    "warning",
                    "-y",
                    "-i",
                    str(source),
                    "-map",
                    "0:v:0",
                    "-map",
                    "0:a:0",
                    "-c:v",
                    "copy",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "192k",
                    "-ar",
                    str(TARGET_AUDIO_RATE),
                    "-movflags",
                    "+faststart",
                    str(concat_path),
                ]
            )

        inputs.append(
            {
                "lesson": lesson,
                "source": str(source.relative_to(PROJECT_ROOT)),
                "duration": float(metadata["format"]["duration"]),
                "source_audio_rate": int(audio_stream["sample_rate"]),
                "concat_path": str(concat_path.relative_to(PROJECT_ROOT)),
            }
        )
        concat_paths.append(concat_path)

    concat_file = WORK_DIR / "concat.txt"
    concat_file.write_text(
        "".join(f"file '{path}'\n" for path in concat_paths),
        encoding="utf-8",
    )
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "warning",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_file),
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            str(TARGET_AUDIO_RATE),
            "-movflags",
            "+faststart",
            str(OUTPUT),
        ]
    )

    output_probe = probe(OUTPUT)
    expected_duration = sum(item["duration"] for item in inputs)
    actual_duration = float(output_probe["format"]["duration"])
    if abs(actual_duration - expected_duration) > 0.25:
        raise RuntimeError(
            f"duration mismatch: expected {expected_duration}, got {actual_duration}"
        )
    output_audio = next(
        stream for stream in output_probe["streams"] if stream["codec_type"] == "audio"
    )
    if int(output_audio["sample_rate"]) != TARGET_AUDIO_RATE:
        raise RuntimeError(f"unexpected output audio stream: {output_audio}")

    run(["ffmpeg", "-v", "error", "-xerror", "-i", str(OUTPUT), "-f", "null", "-"])
    digest = hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    report = {
        "title": "Middle school lessons L01-L15 (revised L6)",
        "l6_revision": "revision_v3",
        "inputs": inputs,
        "expected_duration": expected_duration,
        "output": str(OUTPUT.relative_to(PROJECT_ROOT)),
        "output_probe": output_probe,
        "sha256": digest,
        "decode_check": "passed",
    }
    MANIFEST.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
