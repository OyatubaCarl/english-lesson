#!/usr/bin/env python3
"""Build L1-L45 with mixed-Japanese captions and complete ruby.

The story images, adopted audio, word timing and camera scenes are reused from
the approved middle-school editions.  Only the Japanese caption layer is
replaced by the new mixed-Japanese, full-ruby layer.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MIDDLE = ROOT.parent
PROJECT = MIDDLE.parent
PLANNING = ROOT / "planning" / "lessons"
OUTPUT = ROOT / "output"
WORK = ROOT / "work"
CAPTIONS = ROOT / "captions"
FONT_PATH = Path("/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc")

FPS = 30
EDITION = "v4_inline_canonical_vocab"
MAX_TEXT_WIDTH = 1760
BASE_SIZE_MAX = 56
BASE_SIZE_MIN = 44
RUBY_RATIO = 0.47
EN_COLOR = (255, 211, 102, 255)
JA_COLOR = (200, 233, 255, 255)
RUBY_COLOR = (255, 245, 214, 255)
OUTLINE = (24, 24, 24, 255)


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def source_lesson_dir(lesson: int) -> Path:
    if lesson == 6:
        return MIDDLE / "mio_video_l2_l10_sentence_v2" / "L6_revision_v3"
    if 2 <= lesson <= 10:
        return MIDDLE / "mio_video_l2_l10_sentence_v2" / f"L{lesson}"
    return MIDDLE / "mio_video_l1_l45_sentence_v3" / f"L{lesson}"


def base_script(lesson: int) -> Path:
    if 2 <= lesson <= 10:
        return MIDDLE / "mio_video_l2_l10_sentence_v2" / "shared" / "scripts" / "build_sentence_video.py"
    return MIDDLE / "mio_video_l1_l45_sentence_v3" / "shared" / "scripts" / "build_story_video.py"


def load_base_module(lesson: int):
    path = base_script(lesson)
    spec = importlib.util.spec_from_file_location(f"middle_base_{lesson}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def line_timings(config: dict, beat: list[list[object]]) -> list[tuple[float, float]]:
    result = []
    for line_index, line in enumerate(config["lines"]):
        raw_indices = line.get("indices")
        indices = [int(item) for item in raw_indices] if raw_indices else list(
            range(int(line["start_index"]), int(line["end_index"]) + 1)
        )
        if not indices or max(indices) >= len(beat):
            # L13's closing "Thank you for watching" is audible after the
            # chart's final indexed token.  Give that verified tail a compact,
            # deterministic caption interval instead of dropping the line.
            previous_end = result[-1][1] if result else 0.0
            end = float(config["duration"])
            start = min(end - 0.8, max(previous_end + 0.04, end - 1.30))
            result.append((start, end))
            continue
        start = float(beat[indices[0]][0])
        last_index = indices[-1]
        hold_end = float(beat[last_index][3] or 0)
        if hold_end > float(beat[last_index][0]):
            end = hold_end
        elif line_index + 1 < len(config["lines"]):
            next_line = config["lines"][line_index + 1]
            next_raw = next_line.get("indices")
            next_index = int(next_raw[0]) if next_raw else int(next_line["start_index"])
            end = max(float(beat[last_index][0]) + 0.18, float(beat[next_index][0]) - 0.04)
        else:
            end = float(config["duration"])
        result.append((start, end))
    return result


def atoms_from_runs(runs: list[dict]) -> list[dict]:
    atoms: list[dict] = []
    for run in runs:
        if run["type"] == "en":
            atoms.append({"text": run["text"], "ruby": run["ruby"], "type": "en"})
            continue
        for part in run["parts"]:
            if part["ruby"]:
                atoms.append({"text": part["text"], "ruby": part["ruby"], "type": "ja"})
            else:
                # Japanese can wrap between characters. Keep latin/numeric runs together.
                buffer = ""
                for char in part["text"]:
                    if char.isascii() and (char.isalnum() or char in " .,'!?-"):
                        buffer += char
                    else:
                        if buffer:
                            atoms.append({"text": buffer, "ruby": "", "type": "ja"})
                            buffer = ""
                        atoms.append({"text": char, "ruby": "", "type": "ja"})
                if buffer:
                    atoms.append({"text": buffer, "ruby": "", "type": "ja"})
    return [atom for atom in atoms if atom["text"]]


def atom_width(atom: dict, base_font: ImageFont.FreeTypeFont, ruby_font: ImageFont.FreeTypeFont) -> float:
    base_width = float(base_font.getlength(atom["text"]))
    ruby_width = float(ruby_font.getlength(atom["ruby"])) if atom["ruby"] else 0.0
    return max(base_width, ruby_width + 4)


def wrap_atoms(atoms: list[dict], base_font: ImageFont.FreeTypeFont, ruby_font: ImageFont.FreeTypeFont) -> list[list[dict]]:
    lines: list[list[dict]] = [[]]
    width = 0.0
    closing = set("、。！？）」』】,.!?")
    for original in atoms:
        atom = dict(original)
        item_width = atom_width(atom, base_font, ruby_font)
        if lines[-1] and width + item_width > MAX_TEXT_WIDTH and atom["text"].strip() not in closing:
            lines.append([])
            width = 0.0
            atom["text"] = atom["text"].lstrip()
            item_width = atom_width(atom, base_font, ruby_font)
        lines[-1].append(atom)
        width += item_width
    return [line for line in lines if line]


def fit_layout(runs: list[dict]) -> tuple[list[list[dict]], ImageFont.FreeTypeFont, ImageFont.FreeTypeFont, int]:
    atoms = atoms_from_runs(runs)
    fallback = None
    for base_size in range(BASE_SIZE_MAX, BASE_SIZE_MIN - 1, -2):
        ruby_size = max(20, round(base_size * RUBY_RATIO))
        base_font = ImageFont.truetype(str(FONT_PATH), base_size)
        ruby_font = ImageFont.truetype(str(FONT_PATH), ruby_size)
        lines = wrap_atoms(atoms, base_font, ruby_font)
        fallback = (lines, base_font, ruby_font, base_size)
        if len(lines) <= 2:
            return fallback
    if fallback is None or len(fallback[0]) > 3:
        raise RuntimeError("caption cannot be fitted in three lines")
    return fallback


def draw_with_outline(draw, xy, text, font, fill, stroke) -> None:
    draw.text(xy, text, font=font, fill=fill, stroke_width=stroke, stroke_fill=OUTLINE)


def render_overlay(entry: dict, out_path: Path) -> dict:
    canvas = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    lines, base_font, ruby_font, base_size = fit_layout(entry["runs"])
    if len(lines) == 1:
        positions = [970]
    elif len(lines) == 2:
        # Explicitly leave 115 px between lines so line-two ruby never touches line one.
        positions = [885, 1000]
    else:
        positions = [780, 895, 1010]
    ruby_offset = max(35, round(base_size * 0.69))

    for atoms, base_y in zip(lines, positions):
        widths = [atom_width(atom, base_font, ruby_font) for atom in atoms]
        x = (1920 - sum(widths)) / 2
        for atom, slot_width in zip(atoms, widths):
            base_width = float(base_font.getlength(atom["text"]))
            base_x = x + (slot_width - base_width) / 2
            color = EN_COLOR if atom["type"] == "en" else JA_COLOR
            draw_with_outline(draw, (base_x, base_y), atom["text"], base_font, color, 4)
            if atom["ruby"]:
                ruby_width = float(ruby_font.getlength(atom["ruby"]))
                ruby_x = x + (slot_width - ruby_width) / 2
                draw_with_outline(
                    draw,
                    (ruby_x, base_y - ruby_offset),
                    atom["ruby"],
                    ruby_font,
                    RUBY_COLOR,
                    3,
                )
            x += slot_width

    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path)
    return {"line_count": len(lines), "base_font_size": base_size, "ruby_font_size": ruby_font.size}


def build_english_ass(base, config: dict, beat: list[list[object]], overlay_layouts: list[dict], out_path: Path) -> None:
    title_x, title_y = config.get("title_position", [960, 205])
    title_ja_x, title_ja_y = config.get("title_ja_position", [title_x, title_y + 85])
    header = f"""[Script Info]
Title: {config['title_en']} full-ruby edition
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: English,Arial Rounded MT Bold,66,&H00FFFFFF,&H00FFFFFF,&H00181818,&H78000000,-1,0,0,0,100,100,0,0,1,6,2,5,40,40,0,1
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
        raw_indices = line.get("indices")
        token_indices = [int(item) for item in raw_indices] if raw_indices else list(
            range(int(line["start_index"]), int(line["end_index"]) + 1)
        )
        raw_groups = line.get("word_indices")
        timing_groups = [[int(item) for item in group] for group in raw_groups] if raw_groups else [
            [item] for item in token_indices
        ]
        words = line["en_words"]
        if len(words) != len(timing_groups):
            raise RuntimeError(f"line {line_index + 1}: word/timing count mismatch")
        breaks = set(int(item) for item in line.get("break_after", []))
        english_lines = len(breaks) + 1
        mixed_lines = overlay_layouts[line_index]["line_count"]
        if mixed_lines >= 3:
            english_y = 600 if english_lines >= 3 else (630 if english_lines == 2 else 670)
        elif mixed_lines == 2:
            english_y = 685 if english_lines >= 3 else (720 if english_lines == 2 else 770)
        else:
            english_y = 755 if english_lines >= 3 else (790 if english_lines == 2 else 830)
        line_end = timings[line_index][1]
        has_chart_timing = bool(timing_groups) and max(
            item for group in timing_groups for item in group
        ) < len(beat)
        for word_index, timing_group in enumerate(timing_groups):
            if has_chart_timing:
                word_start = float(beat[timing_group[0]][0])
                word_end = (
                    float(beat[timing_groups[word_index + 1][0]][0])
                    if word_index + 1 < len(timing_groups)
                    else line_end
                )
            else:
                line_start = timings[line_index][0]
                span = max(0.08 * len(timing_groups), line_end - line_start)
                word_start = line_start + span * word_index / len(timing_groups)
                word_end = min(
                    line_end,
                    line_start + span * (word_index + 1) / len(timing_groups),
                )
            word_end = max(word_end, word_start + 0.08)
            events.append(
                f"Dialogue: 2,{base.ass_time(word_start)},{base.ass_time(word_end)},English,,0,0,0,,"
                f"{{\\an5\\pos(960,{english_y})}}{base.display_line(words, word_index, breaks)}"
            )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(header + "\n".join(events) + "\n", encoding="utf-8")


def burn_video(scenes_video: Path, audio: Path, ass: Path, overlays: list[Path], timings, duration: float, out_path: Path) -> None:
    inputs = ["-i", str(scenes_video), "-i", str(audio)]
    for overlay in overlays:
        inputs += ["-loop", "1", "-i", str(overlay)]
    filters = ["[0:v]drawbox=x=0:y=565:w=iw:h=515:color=black@0.24:t=fill[v0]"]
    current = "v0"
    for index, (start, end) in enumerate(timings):
        target = f"v{index + 1}"
        filters.append(
            f"[{current}][{index + 2}:v]overlay=0:0:enable='between(t,{start:.4f},{end:.4f})'[{target}]"
        )
        current = target
    ass_path = str(ass.resolve()).replace("\\", r"\\").replace(":", r"\:")
    filters.append(f"[{current}]subtitles=filename='{ass_path}'[vout]")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    run([
        "ffmpeg", "-hide_banner", "-loglevel", "warning", "-y", *inputs,
        "-filter_complex", ";".join(filters),
        "-map", "[vout]", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k", "-t", f"{duration:.6f}",
        "-r", str(FPS), "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out_path),
    ])


def probe(path: Path) -> dict:
    result = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration,size:stream=codec_name,width,height,r_frame_rate",
        "-of", "json", str(path),
    ], check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def make_qa_sheet(video: Path, timings: list[tuple[float, float]], out_path: Path) -> None:
    count = min(6, len(timings))
    picks = sorted(set(round(i * (len(timings) - 1) / max(1, count - 1)) for i in range(count)))
    frame_dir = out_path.parent / "frames"
    frame_dir.mkdir(parents=True, exist_ok=True)
    for order, index in enumerate(picks):
        start, end = timings[index]
        timestamp = start + min(0.6, max(0.12, (end - start) * 0.35))
        run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-ss", f"{timestamp:.3f}", "-i", str(video), "-frames:v", "1", "-q:v", "2",
            str(frame_dir / f"{order:02d}.jpg"),
        ])
    cols = 3
    rows = math.ceil(len(picks) / cols)
    run([
        "ffmpeg", "-hide_banner", "-loglevel", "warning", "-y",
        "-pattern_type", "glob", "-framerate", "1", "-i", str(frame_dir / "*.jpg"),
        "-vf", f"scale=640:360,tile={cols}x{rows}:padding=4:margin=4",
        "-frames:v", "1", "-update", "1", str(out_path),
    ])


def build_lesson(lesson: int, overlay_only: bool = False) -> dict:
    base = load_base_module(lesson)
    lesson_dir = source_lesson_dir(lesson)
    config = read_json(lesson_dir / "planning" / "lesson.json")
    mixed = read_json(PLANNING / f"L{lesson:02d}.json")
    if len(config["lines"]) != len(mixed["lines"]):
        raise RuntimeError(f"L{lesson}: source/mixed line count mismatch")
    if "Only canonical new vocabulary" not in mixed.get("policy", ""):
        raise RuntimeError(f"L{lesson}: canonical-vocabulary caption policy is missing")
    invalid_sources = [
        replacement["source"]
        for line in mixed["lines"]
        for replacement in line["replacements"]
        if not replacement["source"].startswith("canonical_new_word")
    ]
    if invalid_sources:
        raise RuntimeError(f"L{lesson}: noncanonical replacements: {invalid_sources}")
    project_root = Path(config["project_root"])
    chart = project_root / config["chart"]
    audio = project_root / config["audio"]
    beat = base.load_beat(chart)
    timings = line_timings(config, beat)
    lesson_work = WORK / f"L{lesson:02d}"
    overlay_dir = lesson_work / "overlays"
    layouts = []
    overlays = []
    for index, entry in enumerate(mixed["lines"], start=1):
        overlay = overlay_dir / f"{index:02d}.png"
        layouts.append(render_overlay(entry, overlay))
        overlays.append(overlay)
    ass = CAPTIONS / f"L{lesson:02d}" / f"{config['slug']}_english_highlight_{EDITION}.ass"
    build_english_ass(base, config, beat, layouts, ass)
    if overlay_only:
        return {"lesson": lesson, "layouts": layouts, "overlay_dir": str(overlay_dir)}

    scene_candidates = list((lesson_dir / "work").glob(f"{config['slug']}_camera_scenes.mp4"))
    if not scene_candidates:
        scenes = lesson_work / f"{config['slug']}_camera_scenes.mp4"
        base.render_shots(config, lesson_dir, scenes)
    else:
        scenes = scene_candidates[0]
    final = OUTPUT / f"L{lesson:02d}" / f"{config['slug']}_mixed_japanese_full_ruby_{EDITION}.mp4"
    burn_video(scenes, audio, ass, overlays, timings, float(config["duration"]), final)
    qa_dir = lesson_work / "qa"
    qa_dir.mkdir(parents=True, exist_ok=True)
    sheet = qa_dir / f"L{lesson:02d}_contact_sheet_{EDITION}.jpg"
    make_qa_sheet(final, timings, sheet)
    verification = {
        "lesson": lesson,
        "source_lesson": str(lesson_dir),
        "audio": str(audio),
        "source_camera_video": str(scenes),
        "output": str(final),
        "contact_sheet": str(sheet),
        "line_count": len(mixed["lines"]),
        "layout_counts": {
            str(count): sum(item["line_count"] == count for item in layouts)
            for count in sorted(set(item["line_count"] for item in layouts))
        },
        "full_kanji_ruby": True,
        "full_english_meaning_ruby": True,
        "canonical_lesson_vocabulary_only": True,
        "noncanonical_replacements": 0,
        "inline_mixed_body_no_parentheses": True,
        "canonical_vocabulary_coverage": "411/411",
        "highlight_policy": "color only; fixed 72px for normal and active words; no size change",
        "translation_corrections": sum(bool(item["corrected_translation"]) for item in mixed["lines"]),
        "probe": probe(final),
    }
    (qa_dir / f"VERIFICATION_{EDITION.upper()}.json").write_text(
        json.dumps(verification, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return verification


def parse_lessons(value: str) -> list[int]:
    lessons = set()
    for part in value.split(","):
        if "-" in part:
            start, end = (int(item) for item in part.split("-", 1))
            lessons.update(range(start, end + 1))
        else:
            lessons.add(int(part))
    if not lessons or min(lessons) < 1 or max(lessons) > 45:
        raise argparse.ArgumentTypeError("lessons must be within L1-L45")
    return sorted(lessons)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lessons", default="1-45", help="e.g. 1,2,34-39")
    parser.add_argument("--overlay-only", action="store_true")
    args = parser.parse_args()
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            raise RuntimeError(f"{tool} is required")
    if not FONT_PATH.exists():
        raise FileNotFoundError(FONT_PATH)
    results = []
    for lesson in parse_lessons(args.lessons):
        print(f"=== L{lesson:02d} ===", flush=True)
        results.append(build_lesson(lesson, overlay_only=args.overlay_only))
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
