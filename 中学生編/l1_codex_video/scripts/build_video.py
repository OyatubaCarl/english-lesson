#!/usr/bin/env python3
"""Build the Codex-illustrated bilingual L1 video.

English word highlights use Taco Beat's BEAT token start times verbatim.
"""

from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "planning" / "scene_plan.json"
LYRICS_PATH = ROOT / "planning" / "lyrics_timing.json"
SCENES_DIR = ROOT / "scenes"
CAPTIONS_DIR = ROOT / "captions"
WORK_DIR = ROOT / "work"
OUTPUT_DIR = ROOT / "output"
ASS_PATH = CAPTIONS_DIR / "l1_bilingual_word_highlight.ass"
SCENES_VIDEO = WORK_DIR / "l1_scenes.mp4"
FINAL_VIDEO = OUTPUT_DIR / "l1_my_family_and_pochi_codex_bilingual.mp4"
CONTACT_SHEET = OUTPUT_DIR / "l1_scene_contact_sheet.jpg"
FPS = 30
FADE = 0.35


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
    beat = json.loads(match.group(1))
    if not beat:
        raise RuntimeError("BEAT array is empty")
    return beat


def display_line(words: list[str], active: int, break_after: set[int]) -> str:
    normal = r"{\c&HFFFFFF&\fs78\b1}"
    hot = r"{\c&H4D62FF&\fs86\b1\fscx106\fscy106}"
    out: list[str] = []
    for index, word in enumerate(words):
        if index:
            out.append(r"\N" if index - 1 in break_after else " ")
        out.append(hot if index == active else normal)
        out.append(ass_escape(word))
    return "".join(out)


def build_ass(lyrics: dict, beat: list[list[object]]) -> None:
    CAPTIONS_DIR.mkdir(parents=True, exist_ok=True)
    lines = lyrics["lines"]
    header = """[Script Info]
Title: Teacher Tacos English L1 bilingual word highlight
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: English,Arial Rounded MT Bold,78,&H00FFFFFF,&H00FFFFFF,&H00181818,&H78000000,-1,0,0,0,100,100,0,0,1,6,2,5,40,40,0,1
Style: Japanese,Hiragino Maru Gothic ProN W4,62,&H00C8E9FF,&H00C8E9FF,&H00181818,&H78000000,-1,0,0,0,100,100,0,0,1,5,2,5,40,40,0,1
Style: TitleEn,Arial Rounded MT Bold,72,&H00FFFFFF,&H00FFFFFF,&H003B251A,&H00000000,-1,0,0,0,100,100,1,0,1,5,2,5,40,40,0,1
Style: TitleJa,Hiragino Maru Gothic ProN W4,54,&H00C8E9FF,&H00C8E9FF,&H003B251A,&H00000000,-1,0,0,0,100,100,0,0,1,4,2,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = [
        f"Dialogue: 3,{ass_time(0)},{ass_time(1.02)},TitleEn,,0,0,0,,{{\\an5\\pos(960,210)}}{ass_escape(lyrics['title_en'])}",
        f"Dialogue: 3,{ass_time(0)},{ass_time(1.02)},TitleJa,,0,0,0,,{{\\an5\\pos(960,300)}}{ass_escape(lyrics['title_ja'])}",
    ]

    for line_index, line in enumerate(lines):
        start_idx = int(line["start_index"])
        end_idx = int(line["end_index"])
        words = line["en_words"]
        if len(words) != end_idx - start_idx + 1:
            raise RuntimeError(f"line {line_index}: word count does not match BEAT indices")

        line_start = float(beat[start_idx][0])
        hold_end = float(beat[end_idx][3] or 0)
        if hold_end > float(beat[end_idx][0]):
            line_end = hold_end
        elif line_index + 1 < len(lines):
            next_start = float(beat[int(lines[line_index + 1]["start_index"])][0])
            line_end = max(float(beat[end_idx][0]) + 0.18, next_start - 0.04)
        else:
            line_end = max(float(beat[end_idx][0]) + 0.4, 43.328435)

        is_two_line = bool(line.get("break_after"))
        english_y = 800 if is_two_line else 850
        japanese_y = 985 if is_two_line else 958
        breaks = set(line.get("break_after", []))

        events.append(
            f"Dialogue: 1,{ass_time(line_start)},{ass_time(line_end)},Japanese,,0,0,0,,"
            f"{{\\an5\\pos(960,{japanese_y})}}{ass_escape(line['ja'])}"
        )

        for rel_index, abs_index in enumerate(range(start_idx, end_idx + 1)):
            word_start = float(beat[abs_index][0])
            if abs_index < end_idx:
                word_end = float(beat[abs_index + 1][0])
            else:
                word_end = line_end
            if word_end <= word_start:
                word_end = word_start + 0.08
            text = display_line(words, rel_index, breaks)
            events.append(
                f"Dialogue: 2,{ass_time(word_start)},{ass_time(word_end)},English,,0,0,0,,"
                f"{{\\an5\\pos(960,{english_y})}}{text}"
            )

    ASS_PATH.write_text(header + "\n".join(events) + "\n", encoding="utf-8")


def render_scenes(plan: dict) -> None:
    scenes = plan["scenes"]
    inputs: list[str] = []
    filters: list[str] = []
    for index, scene in enumerate(scenes):
        image_path = SCENES_DIR / f"{scene['id']}.png"
        if not image_path.exists():
            raise FileNotFoundError(f"missing scene image: {image_path}")
        inputs.extend(["-i", str(image_path)])

        duration = float(scene["end"]) - float(scene["start"])
        clip_duration = duration + (FADE if index < len(scenes) - 1 else 0)
        frames = math.ceil(clip_duration * FPS)
        if index % 2 == 0:
            x_expr = "iw/2-(iw/zoom/2)+8*sin(on/70)"
        else:
            x_expr = "iw/2-(iw/zoom/2)-8*sin(on/70)"
        filters.append(
            f"[{index}:v]"
            "scale=2304:1296:force_original_aspect_ratio=increase,"
            "crop=2304:1296,"
            f"zoompan=z='min(zoom+0.00016,1.085)':x='{x_expr}':"
            "y='ih/2-(ih/zoom/2)':"
            f"d={frames}:s=1920x1080:fps={FPS},"
            f"trim=duration={clip_duration:.6f},setpts=PTS-STARTPTS,format=yuv420p[v{index}]"
        )

    current = "v0"
    for index in range(1, len(scenes)):
        boundary = float(scenes[index]["start"])
        out = f"x{index}"
        filters.append(
            f"[{current}][v{index}]xfade=transition=fade:duration={FADE:.3f}:"
            f"offset={boundary:.6f}[{out}]"
        )
        current = out

    final_duration = float(scenes[-1]["end"])
    filters.append(
        f"[{current}]trim=duration={final_duration:.6f},setpts=PTS-STARTPTS[video]"
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
            str(SCENES_VIDEO),
        ]
    )


def burn_subtitles(audio_path: Path, duration: float) -> None:
    ass_filter_path = str(ASS_PATH.resolve()).replace("\\", r"\\").replace(":", r"\:")
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
            str(SCENES_VIDEO),
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
            str(FINAL_VIDEO),
        ]
    )


def make_contact_sheet() -> None:
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "warning",
            "-y",
            "-i",
            str(FINAL_VIDEO),
            "-vf",
            "fps=1/5.2,scale=640:360,tile=4x2",
            "-frames:v",
            "1",
            "-update",
            "1",
            str(CONTACT_SHEET),
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
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            raise RuntimeError(f"{tool} is required")
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    lyrics = json.loads(LYRICS_PATH.read_text(encoding="utf-8"))
    chart_path = (ROOT / lyrics["source_chart"]).resolve()
    audio_path = (ROOT / lyrics["source_audio"]).resolve()
    if not audio_path.exists():
        raise FileNotFoundError(audio_path)

    beat = load_beat(chart_path)
    if len(beat) != 100:
        raise RuntimeError(f"expected 100 Taco Beat tokens, found {len(beat)}")
    build_ass(lyrics, beat)
    render_scenes(plan)
    duration = float(plan["scenes"][-1]["end"])
    burn_subtitles(audio_path, duration)
    make_contact_sheet()

    metadata = probe(FINAL_VIDEO)
    stream = next(s for s in metadata["streams"] if s.get("width"))
    actual_duration = float(metadata["format"]["duration"])
    if (stream["width"], stream["height"]) != (1920, 1080):
        raise RuntimeError(f"unexpected dimensions: {stream}")
    if abs(actual_duration - duration) > 0.08:
        raise RuntimeError(f"duration mismatch: expected {duration}, got {actual_duration}")
    print(json.dumps(metadata, ensure_ascii=False, indent=2))
    print(f"Built: {FINAL_VIDEO}")


if __name__ == "__main__":
    main()
