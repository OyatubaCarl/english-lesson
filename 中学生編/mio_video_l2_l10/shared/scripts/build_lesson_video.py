#!/usr/bin/env python3
"""Build a bilingual lesson video with composition-aware camera moves."""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
from pathlib import Path


FPS = 30
FADE = 0.28


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def ass_time(seconds: float) -> str:
    total_cs = max(0, round(seconds * 100))
    hours, rem = divmod(total_cs, 360000)
    minutes, rem = divmod(rem, 6000)
    secs, cs = divmod(rem, 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{cs:02d}"


def ass_escape(text: str) -> str:
    return text.replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}")


def load_beat(chart_path: Path) -> list[list[object]]:
    source = chart_path.read_text(encoding="utf-8")
    match = re.search(r"const BEAT=(\[.*\]);", source, re.S)
    if not match:
        raise RuntimeError(f"BEAT array not found: {chart_path}")
    return json.loads(match.group(1))


def display_line(words: list[str], active: int, break_after: set[int]) -> str:
    normal = r"{\c&HFFFFFF&\fs72\b1}"
    hot = r"{\c&H4D62FF&\fs81\b1\fscx106\fscy106}"
    out: list[str] = []
    for index, word in enumerate(words):
        if index:
            out.append(r"\N" if index - 1 in break_after else " ")
        out.append(hot if index == active else normal)
        out.append(ass_escape(word))
    return "".join(out)


def build_ass(config: dict, beat: list[list[object]], ass_path: Path) -> None:
    header = f"""[Script Info]
Title: {config['title_en']} bilingual word highlight
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: English,Arial Rounded MT Bold,72,&H00FFFFFF,&H00FFFFFF,&H00181818,&H78000000,-1,0,0,0,100,100,0,0,1,6,2,5,40,40,0,1
Style: Japanese,Hiragino Maru Gothic ProN W4,56,&H00C8E9FF,&H00C8E9FF,&H00181818,&H78000000,-1,0,0,0,100,100,0,0,1,5,2,5,40,40,0,1
Style: TitleEn,Arial Rounded MT Bold,68,&H00FFFFFF,&H00FFFFFF,&H003B251A,&H00000000,-1,0,0,0,100,100,1,0,1,5,2,5,40,40,0,1
Style: TitleJa,Hiragino Maru Gothic ProN W4,50,&H00C8E9FF,&H00C8E9FF,&H003B251A,&H00000000,-1,0,0,0,100,100,0,0,1,4,2,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = [
        (
            f"Dialogue: 3,{ass_time(0)},{ass_time(1.06)},TitleEn,,0,0,0,,"
            f"{{\\an5\\pos(960,205)}}{ass_escape(config['title_en'])}"
        ),
        (
            f"Dialogue: 3,{ass_time(0)},{ass_time(1.06)},TitleJa,,0,0,0,,"
            f"{{\\an5\\pos(960,290)}}{ass_escape(config['title_ja'])}"
        ),
    ]

    lines = config["lines"]
    for line_index, line in enumerate(lines):
        indices = line.get("indices")
        if indices:
            token_indices = [int(item) for item in indices]
        else:
            token_indices = list(
                range(int(line["start_index"]), int(line["end_index"]) + 1)
            )
        words = line["en_words"]
        if len(words) != len(token_indices):
            raise RuntimeError(
                f"line {line_index}: {len(words)} words for "
                f"{len(token_indices)} timing tokens"
            )

        line_start = float(beat[token_indices[0]][0])
        last_index = token_indices[-1]
        hold_end = float(beat[last_index][3] or 0)
        if hold_end > float(beat[last_index][0]):
            line_end = hold_end
        elif line_index + 1 < len(lines):
            next_line = lines[line_index + 1]
            next_indices = next_line.get("indices")
            next_index = (
                int(next_indices[0])
                if next_indices
                else int(next_line["start_index"])
            )
            line_end = max(
                float(beat[last_index][0]) + 0.18,
                float(beat[next_index][0]) - 0.04,
            )
        else:
            line_end = float(config["duration"])

        breaks = set(int(item) for item in line.get("break_after", []))
        is_two_line = bool(breaks)
        english_y = 802 if is_two_line else 850
        japanese_y = 982 if is_two_line else 958
        events.append(
            f"Dialogue: 1,{ass_time(line_start)},{ass_time(line_end)},Japanese,,0,0,0,,"
            f"{{\\an5\\pos(960,{japanese_y})}}{ass_escape(line['ja'])}"
        )
        for relative_index, token_index in enumerate(token_indices):
            word_start = float(beat[token_index][0])
            if relative_index + 1 < len(token_indices):
                word_end = float(beat[token_indices[relative_index + 1]][0])
            else:
                word_end = line_end
            word_end = max(word_end, word_start + 0.08)
            events.append(
                f"Dialogue: 2,{ass_time(word_start)},{ass_time(word_end)},English,,0,0,0,,"
                f"{{\\an5\\pos(960,{english_y})}}"
                f"{display_line(words, relative_index, breaks)}"
            )

    ass_path.parent.mkdir(parents=True, exist_ok=True)
    ass_path.write_text(header + "\n".join(events) + "\n", encoding="utf-8")


def number_expr(start: float, end: float, frames: int) -> str:
    if frames <= 1 or abs(end - start) < 0.000001:
        return f"{start:.6f}"
    progress = f"(on/{frames - 1})"
    eased = f"(({progress})*({progress})*(3-2*({progress})))"
    return f"{start:.6f}+({end - start:.6f})*{eased}"


def render_shots(config: dict, lesson_dir: Path, scenes_video: Path) -> None:
    shots = config["shots"]
    inputs: list[str] = []
    filters: list[str] = []
    for index, shot in enumerate(shots):
        image_path = lesson_dir / shot["image"]
        if not image_path.exists():
            raise FileNotFoundError(image_path)
        inputs.extend(["-i", str(image_path)])
        duration = float(shot["end"]) - float(shot["start"])
        clip_duration = duration + (FADE if index < len(shots) - 1 else 0)
        frames = math.ceil(clip_duration * FPS)
        zoom = number_expr(
            float(shot["start_zoom"]), float(shot["end_zoom"]), frames
        )
        center_x = number_expr(
            float(shot["start_center"][0]),
            float(shot["end_center"][0]),
            frames,
        )
        center_y = number_expr(
            float(shot["start_center"][1]),
            float(shot["end_center"][1]),
            frames,
        )
        x_expr = (
            f"max(0,min(iw-iw/zoom,iw*({center_x})-iw/zoom/2))"
        )
        y_expr = (
            f"max(0,min(ih-ih/zoom,ih*({center_y})-ih/zoom/2))"
        )
        filters.append(
            f"[{index}:v]"
            "scale=2400:1350:force_original_aspect_ratio=increase,"
            "crop=2400:1350,"
            f"zoompan=z='{zoom}':x='{x_expr}':y='{y_expr}':"
            f"d={frames}:s=1920x1080:fps={FPS},"
            f"trim=duration={clip_duration:.6f},"
            "setpts=PTS-STARTPTS,format=yuv420p"
            f"[v{index}]"
        )

    current = "v0"
    for index in range(1, len(shots)):
        boundary = float(shots[index]["start"])
        out = f"x{index}"
        filters.append(
            f"[{current}][v{index}]"
            f"xfade=transition=fade:duration={FADE:.3f}:"
            f"offset={boundary:.6f}[{out}]"
        )
        current = out
    filters.append(
        f"[{current}]trim=duration={float(config['duration']):.6f},"
        "setpts=PTS-STARTPTS[video]"
    )
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "warning",
            "-y",
            *inputs,
            "-filter_complex",
            ";".join(filters),
            "-map",
            "[video]",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "17",
            "-r",
            str(FPS),
            "-pix_fmt",
            "yuv420p",
            str(scenes_video),
        ]
    )


def burn_subtitles(
    scenes_video: Path,
    audio_path: Path,
    ass_path: Path,
    duration: float,
    final_video: Path,
) -> None:
    ass_filter_path = str(ass_path.resolve()).replace("\\", r"\\").replace(":", r"\:")
    vf = (
        "drawbox=x=0:y=700:w=iw:h=380:color=black@0.20:t=fill,"
        f"subtitles=filename='{ass_filter_path}'"
    )
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "warning",
            "-y",
            "-i",
            str(scenes_video),
            "-i",
            str(audio_path),
            "-vf",
            vf,
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "17",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-t",
            f"{duration:.6f}",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(final_video),
        ]
    )


def make_qa(config: dict, final_video: Path, qa_dir: Path) -> None:
    qa_dir.mkdir(parents=True, exist_ok=True)
    for index, shot in enumerate(config["shots"], start=1):
        start = float(shot["start"])
        end = float(shot["end"])
        for suffix, timestamp in (
            ("a", start + min(0.35, (end - start) * 0.12)),
            ("b", end - min(0.35, (end - start) * 0.12)),
        ):
            run(
                [
                    "ffmpeg",
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-y",
                    "-ss",
                    f"{timestamp:.3f}",
                    "-i",
                    str(final_video),
                    "-frames:v",
                    "1",
                    "-q:v",
                    "2",
                    str(qa_dir / f"{index:02d}{suffix}.jpg"),
                ]
            )
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "warning",
            "-y",
            "-i",
            str(final_video),
            "-vf",
            f"fps=1/{max(3.0, float(config['duration']) / 11):.3f},"
            "scale=480:270,tile=4x3",
            "-frames:v",
            "1",
            "-update",
            "1",
            str(qa_dir / "contact.jpg"),
        ]
    )


def probe(path: Path) -> dict:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration,size:stream=codec_name,width,height,r_frame_rate",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=Path)
    args = parser.parse_args()
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            raise RuntimeError(f"{tool} is required")

    config_path = args.config.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    lesson_dir = config_path.parent.parent
    project_root = Path(config["project_root"]).resolve()
    chart_path = project_root / config["chart"]
    audio_path = project_root / config["audio"]
    output_dir = lesson_dir / "output"
    work_dir = lesson_dir / "work"
    captions_dir = lesson_dir / "captions"
    output_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)
    captions_dir.mkdir(parents=True, exist_ok=True)

    ass_path = captions_dir / f"{config['slug']}_bilingual_highlight.ass"
    scenes_video = work_dir / f"{config['slug']}_camera_scenes.mp4"
    final_video = output_dir / f"{config['slug']}_mio_bilingual_camera.mp4"
    beat = load_beat(chart_path)
    build_ass(config, beat, ass_path)
    render_shots(config, lesson_dir, scenes_video)
    burn_subtitles(
        scenes_video,
        audio_path,
        ass_path,
        float(config["duration"]),
        final_video,
    )
    make_qa(config, final_video, work_dir / "camera_qa")

    metadata = probe(final_video)
    stream = next(item for item in metadata["streams"] if item.get("width"))
    actual_duration = float(metadata["format"]["duration"])
    if (stream["width"], stream["height"]) != (1920, 1080):
        raise RuntimeError(f"unexpected dimensions: {stream}")
    if abs(actual_duration - float(config["duration"])) > 0.10:
        raise RuntimeError(
            f"duration mismatch: expected {config['duration']}, got {actual_duration}"
        )
    print(json.dumps(metadata, ensure_ascii=False, indent=2))
    print(f"Built: {final_video}")


if __name__ == "__main__":
    main()
