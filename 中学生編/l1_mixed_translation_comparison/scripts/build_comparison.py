#!/usr/bin/env python3
"""Build L1 mixed-Japanese videos with/without Japanese ruby on English text."""

from __future__ import annotations

import importlib.util
import json
import math
import re
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PROJECT = ROOT.parent
SOURCE_LESSON = PROJECT / "mio_video_l1_l45_sentence_v3" / "L1"
SOURCE_CONFIG = SOURCE_LESSON / "planning" / "lesson.json"
BASE_SCRIPT = PROJECT / "mio_video_l1_l45_sentence_v3" / "shared" / "scripts" / "build_story_video.py"
MIXED_CONFIG = ROOT / "planning" / "mixed_translation.json"
OUTPUT = ROOT / "output"
WORK = ROOT / "work"
CAPTIONS = ROOT / "captions"
OVERLAYS_NO_RUBY = WORK / "overlays_no_english_ruby"
OVERLAYS_RUBY = WORK / "overlays_japanese_ruby_on_english"
SCENES_VIDEO = WORK / "l1_mixed_camera_scenes.mp4"
FONT_PATH = Path("/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc")

BASE_SIZE = 56
RUBY_SIZE = 27
EN_COLOR = (255, 211, 102, 255)
JA_COLOR = (200, 233, 255, 255)
RUBY_COLOR = (255, 245, 214, 255)
OUTLINE = (24, 24, 24, 255)
FPS = 30


def load_base_module():
    spec = importlib.util.spec_from_file_location("l1_story_builder", BASE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {BASE_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def line_timings(config: dict, beat: list[list[object]]) -> list[tuple[float, float]]:
    result: list[tuple[float, float]] = []
    lines = config["lines"]
    for line_index, line in enumerate(lines):
        indices = line.get("indices")
        token_indices = [int(item) for item in indices] if indices else list(
            range(int(line["start_index"]), int(line["end_index"]) + 1)
        )
        start = float(beat[token_indices[0]][0])
        last_index = token_indices[-1]
        hold_end = float(beat[last_index][3] or 0)
        if hold_end > float(beat[last_index][0]):
            end = hold_end
        elif line_index + 1 < len(lines):
            next_line = lines[line_index + 1]
            next_indices = next_line.get("indices")
            next_index = int(next_indices[0]) if next_indices else int(next_line["start_index"])
            end = max(float(beat[last_index][0]) + 0.18, float(beat[next_index][0]) - 0.04)
        else:
            end = float(config["duration"])
        result.append((start, end))
    return result


def is_english_segment(text: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z][A-Za-z .'-]*", text))


def colored_runs(text: str) -> list[tuple[str, tuple[int, int, int, int]]]:
    parts = re.split(r"([A-Za-z][A-Za-z .'-]*)", text)
    return [
        (part, EN_COLOR if is_english_segment(part) else JA_COLOR)
        for part in parts
        if part
    ]


def text_width(font: ImageFont.FreeTypeFont, text: str) -> float:
    return float(font.getlength(text))


def draw_text_with_outline(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
    stroke: int,
) -> None:
    draw.text(xy, text, font=font, fill=fill, stroke_width=stroke, stroke_fill=OUTLINE)


def render_overlay(entry: dict, with_english_ruby: bool, out_path: Path) -> None:
    canvas = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    base_font = ImageFont.truetype(str(FONT_PATH), BASE_SIZE)
    ruby_font = ImageFont.truetype(str(FONT_PATH), RUBY_SIZE)
    lines: list[str] = entry["mixed_lines"]
    if len(lines) == 1:
        # Keep the mixed sentence at the same height in both comparison variants.
        positions = [970]
    else:
        # The ruby above line 2 must not touch line 1. Keep 110 px between baselines.
        positions = [900, 1010] if with_english_ruby else [910, 980]

    for text, base_y in zip(lines, positions):
        width = text_width(base_font, text)
        start_x = (1920 - width) / 2
        x = start_x
        for run_text, color in colored_runs(text):
            draw_text_with_outline(draw, (x, base_y), run_text, base_font, color, 4)
            x += text_width(base_font, run_text)

        ruby_items = list(entry["kanji_ruby"])
        if with_english_ruby:
            ruby_items = list(entry["english_ruby"]) + ruby_items
        for ruby in ruby_items:
                target = ruby["text"]
                if target not in text:
                    continue
                prefix, _, _ = text.partition(target)
                target_x = start_x + text_width(base_font, prefix)
                target_w = text_width(base_font, target)
                reading_w = text_width(ruby_font, ruby["reading"])
                ruby_x = target_x + (target_w - reading_w) / 2
                ruby_y = base_y - 38
                draw_text_with_outline(
                    draw, (ruby_x, ruby_y), ruby["reading"], ruby_font, RUBY_COLOR, 3
                )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path)


def build_english_ass(base, config: dict, beat: list[list[object]], out_path: Path) -> None:
    title_x, title_y = config.get("title_position", [960, 205])
    title_ja_x, title_ja_y = config.get("title_ja_position", [title_x, title_y + 85])
    header = f"""[Script Info]
Title: L1 mixed translation English highlight
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: English,Arial Rounded MT Bold,72,&H00FFFFFF,&H00FFFFFF,&H00181818,&H78000000,-1,0,0,0,100,100,0,0,1,6,2,5,40,40,0,1
Style: TitleEn,Arial Rounded MT Bold,68,&H00FFFFFF,&H00FFFFFF,&H003B251A,&H00000000,-1,0,0,0,100,100,1,0,1,5,2,5,40,40,0,1
Style: TitleJa,Hiragino Maru Gothic ProN W4,50,&H00C8E9FF,&H00C8E9FF,&H003B251A,&H00000000,-1,0,0,0,100,100,0,0,1,4,2,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = [
        f"Dialogue: 3,{base.ass_time(0)},{base.ass_time(1.06)},TitleEn,,0,0,0,,{{\\an5\\pos({title_x},{title_y})}}{base.ass_escape(config['title_en'])}",
        f"Dialogue: 3,{base.ass_time(0)},{base.ass_time(1.06)},TitleJa,,0,0,0,,{{\\an5\\pos({title_ja_x},{title_ja_y})}}{base.ass_escape(config['title_ja'])}",
    ]
    timings = line_timings(config, beat)
    for line_index, line in enumerate(config["lines"]):
        indices = line.get("indices")
        token_indices = [int(item) for item in indices] if indices else list(
            range(int(line["start_index"]), int(line["end_index"]) + 1)
        )
        words = line["en_words"]
        raw_word_indices = line.get("word_indices")
        word_indices = (
            [[int(item) for item in group] for group in raw_word_indices]
            if raw_word_indices
            else [[item] for item in token_indices]
        )
        breaks = set(int(item) for item in line.get("break_after", []))
        english_line_count = len(breaks) + 1
        english_y = 775 if english_line_count >= 3 else (790 if english_line_count == 2 else 830)
        line_end = timings[line_index][1]
        for relative_index, timing_group in enumerate(word_indices):
            word_start = float(beat[timing_group[0]][0])
            if relative_index + 1 < len(word_indices):
                word_end = float(beat[word_indices[relative_index + 1][0]][0])
            else:
                word_end = line_end
            word_end = max(word_end, word_start + 0.08)
            events.append(
                f"Dialogue: 2,{base.ass_time(word_start)},{base.ass_time(word_end)},English,,0,0,0,,"
                f"{{\\an5\\pos(960,{english_y})}}{base.display_line(words, relative_index, breaks)}"
            )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(header + "\n".join(events) + "\n", encoding="utf-8")


def burn_variant(
    scenes_video: Path,
    audio_path: Path,
    ass_path: Path,
    overlays: list[Path],
    timings: list[tuple[float, float]],
    duration: float,
    final_path: Path,
) -> None:
    inputs = ["-i", str(scenes_video), "-i", str(audio_path)]
    for overlay in overlays:
        inputs += ["-loop", "1", "-i", str(overlay)]
    filters = ["[0:v]drawbox=x=0:y=630:w=iw:h=450:color=black@0.20:t=fill[v0]"]
    current = "v0"
    for index, (start, end) in enumerate(timings):
        out = f"v{index + 1}"
        filters.append(
            f"[{current}][{index + 2}:v]overlay=0:0:enable='between(t,{start:.4f},{end:.4f})'[{out}]"
        )
        current = out
    ass_filter_path = str(ass_path.resolve()).replace("\\", r"\\").replace(":", r"\:")
    filters.append(f"[{current}]subtitles=filename='{ass_filter_path}'[vout]")
    run([
        "ffmpeg", "-hide_banner", "-loglevel", "warning", "-y",
        *inputs,
        "-filter_complex", ";".join(filters),
        "-map", "[vout]", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "slow", "-crf", "17",
        "-c:a", "aac", "-b:a", "192k", "-t", f"{duration:.6f}",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(final_path),
    ])


def make_comparison_sheet(no_ruby: Path, ruby: Path, out_path: Path) -> None:
    samples = [2.0, 7.9, 15.2, 22.0, 25.6, 31.0, 34.0, 39.5]
    frames: list[Path] = []
    frame_dir = WORK / "comparison_frames"
    frame_dir.mkdir(parents=True, exist_ok=True)
    for row, video in enumerate((no_ruby, ruby)):
        for col, timestamp in enumerate(samples):
            frame = frame_dir / f"r{row}_c{col}.jpg"
            run([
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-ss", f"{timestamp:.3f}", "-i", str(video),
                "-frames:v", "1", "-q:v", "2", str(frame),
            ])
            frames.append(frame)
    run([
        "ffmpeg", "-hide_banner", "-loglevel", "warning", "-y",
        "-pattern_type", "glob", "-framerate", "1", "-i", str(frame_dir / "*.jpg"),
        "-vf", "scale=480:270,tile=4x4:padding=4:margin=4",
        "-frames:v", "1", "-update", "1", str(out_path),
    ])


def probe(path: Path) -> dict:
    result = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration,size:stream=codec_name,width,height,r_frame_rate",
        "-of", "json", str(path),
    ], check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def main() -> None:
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            raise RuntimeError(f"{tool} is required")
    base = load_base_module()
    config = json.loads(SOURCE_CONFIG.read_text(encoding="utf-8"))
    mixed = json.loads(MIXED_CONFIG.read_text(encoding="utf-8"))
    if len(config["lines"]) != len(mixed["lines"]):
        raise ValueError("mixed translation line count mismatch")
    project_root = Path(config["project_root"])
    chart_path = project_root / config["chart"]
    audio_path = project_root / config["audio"]
    beat = base.load_beat(chart_path)
    timings = line_timings(config, beat)

    for directory in (OUTPUT, WORK, CAPTIONS, OVERLAYS_NO_RUBY, OVERLAYS_RUBY):
        directory.mkdir(parents=True, exist_ok=True)
    build_english_ass(base, config, beat, CAPTIONS / "l1_mixed_english_highlight.ass")
    for index, entry in enumerate(mixed["lines"], start=1):
        render_overlay(entry, False, OVERLAYS_NO_RUBY / f"{index:02d}.png")
        render_overlay(entry, True, OVERLAYS_RUBY / f"{index:02d}.png")

    if not SCENES_VIDEO.exists():
        base.render_shots(config, SOURCE_LESSON, SCENES_VIDEO)
    no_ruby = OUTPUT / "l1_mixed_translation_no_english_ruby_v2.mp4"
    with_ruby = OUTPUT / "l1_mixed_translation_japanese_ruby_on_english_v2.mp4"
    ass_path = CAPTIONS / "l1_mixed_english_highlight.ass"
    burn_variant(
        SCENES_VIDEO, audio_path, ass_path,
        sorted(OVERLAYS_NO_RUBY.glob("*.png")), timings, float(config["duration"]), no_ruby,
    )
    burn_variant(
        SCENES_VIDEO, audio_path, ass_path,
        sorted(OVERLAYS_RUBY.glob("*.png")), timings, float(config["duration"]), with_ruby,
    )
    make_comparison_sheet(no_ruby, with_ruby, OUTPUT / "comparison_english_ruby_contact_sheet_v2.jpg")
    verification = {
        "source_video_assets": str(SOURCE_LESSON),
        "mixed_translation": str(MIXED_CONFIG),
        "no_ruby": probe(no_ruby),
        "with_ruby": probe(with_ruby),
        "line_count": len(mixed["lines"]),
        "english_ruby_line_count": sum(bool(item["english_ruby"]) for item in mixed["lines"]),
        "kanji_ruby_line_count": sum(bool(item["kanji_ruby"]) for item in mixed["lines"]),
        "ruby_policy": "Kanji ruby is retained in both variants; the with-ruby variant additionally places Japanese readings/meanings above English segments.",
        "two_line_ruby_spacing_pixels": 110,
    }
    (ROOT / "VERIFICATION.json").write_text(
        json.dumps(verification, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(verification, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
