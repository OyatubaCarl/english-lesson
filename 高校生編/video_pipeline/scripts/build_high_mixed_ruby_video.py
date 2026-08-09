#!/usr/bin/env python3
"""Build one high-school video in the approved middle-school caption style."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import math
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import ImageFont


HERE = Path(__file__).resolve().parent
PIPELINE = HERE.parent
PROJECT = PIPELINE.parent.parent
MIDDLE_BUILD = (
    PROJECT / "中学生編" / "middle_ruby_complete_v1" / "scripts" / "build_middle_ruby.py"
)
EN_FONT = Path("/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf")
FPS = 30
TRANSITION_DEFAULT = 0.8
LYRIC_FONT_SIZE = 66


def load_middle_renderer():
    spec = importlib.util.spec_from_file_location("middle_ruby_renderer", MIDDLE_BUILD)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {MIDDLE_BUILD}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MIDDLE = load_middle_renderer()


def run(command: list[str]) -> None:
    print(f"+ {command[0]} … {command[-1]}", flush=True)
    subprocess.run(command, check=True)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def ass_time(seconds: float) -> str:
    centiseconds = round(seconds * 100)
    hours, remainder = divmod(centiseconds, 360000)
    minutes, remainder = divmod(remainder, 6000)
    secs, cs = divmod(remainder, 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{cs:02d}"


def ass_escape(text: str) -> str:
    return text.replace("{", r"\{").replace("}", r"\}")


def wrap_words(words: list[str], font_size: int = LYRIC_FONT_SIZE, max_width: int = 1740) -> set[int]:
    font = ImageFont.truetype(str(EN_FONT), font_size)
    breaks = set()
    current = ""
    for index, word in enumerate(words):
        candidate = word if not current else current + " " + word
        if current and font.getlength(candidate) > max_width:
            breaks.add(index - 1)
            current = word
        else:
            current = candidate
    return breaks


def display_line(words: list[str], active: int, breaks: set[int]) -> str:
    # Keep every word at exactly the same size.  The active word changes color
    # only; changing font size here reflows the ASS line on every beat.
    normal = rf"{{\c&HFFFFFF&\fs{LYRIC_FONT_SIZE}\b1}}"
    hot = rf"{{\c&H4D62FF&\fs{LYRIC_FONT_SIZE}\b1}}"
    output = []
    for index, word in enumerate(words):
        if index:
            output.append(r"\N" if index - 1 in breaks else " ")
        output.append(hot if index == active else normal)
        output.append(ass_escape(word))
    return "".join(output)


def word_intervals(start: float, end: float, words: list[str]) -> list[tuple[float, float]]:
    weights = []
    for word in words:
        letters = len(re.sub(r"[^A-Za-z0-9]", "", word))
        weights.append(max(1.0, float(letters) ** 0.72))
    total = sum(weights)
    result = []
    cursor = start
    for index, weight in enumerate(weights):
        stop = end if index + 1 == len(weights) else cursor + (end - start) * weight / total
        result.append((cursor, max(cursor + 0.08, stop)))
        cursor = stop
        total -= weight
        start = cursor
    return result


def apply_tacobeat_timing(mixed: dict, timing_path: Path) -> tuple[dict, str]:
    """Replace approximate line timing with TacoBeat's exact per-word timing."""
    if not timing_path.exists():
        return mixed, "proportional estimate within ASR line boundaries"
    timing = read_json(timing_path)
    if timing.get("exact_word_match") is not True:
        raise RuntimeError(f"unverified TacoBeat word match: {timing_path}")
    if len(timing["lines"]) != len(mixed["lines"]):
        raise RuntimeError(f"TacoBeat line count mismatch: {timing_path}")
    result = copy.deepcopy(mixed)
    for line, timed in zip(result["lines"], timing["lines"]):
        if line["english"] != timed["english"]:
            raise RuntimeError(f"TacoBeat lyric mismatch at line {line['line']}: {timing_path}")
        display_words = line["english"].split()
        for fallback_index, word in enumerate(timed["word_timings"]):
            display_index = int(word.get("display_index", fallback_index))
            if display_index >= len(display_words) or display_words[display_index] != word["word"]:
                raise RuntimeError(f"TacoBeat display-token mismatch at line {line['line']}: {timing_path}")
        line["start"] = float(timed["start"])
        line["end"] = float(timed["end"])
        line["word_timings"] = timed["word_timings"]
    return result, str(timing["method"])


def write_ass(plan: dict, mixed: dict, layouts: list[dict], path: Path) -> None:
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: English,Arial Rounded MT Bold,66,&H00FFFFFF,&H00FFFFFF,&H00181818,&H78000000,-1,0,0,0,100,100,0,0,1,6,2,5,40,40,0,1
Style: TitleEn,Arial Rounded MT Bold,68,&H00FFFFFF,&H00FFFFFF,&H003B251A,&H00000000,-1,0,0,0,100,100,1,0,1,5,40,40,0,1
Style: TitleJa,Hiragino Maru Gothic ProN W4,50,&H00C8E9FF,&H00C8E9FF,&H003B251A,&H00000000,-1,0,0,0,100,100,0,0,1,4,2,5,40,40,0,1
Style: Header,Hiragino Sans,28,&H00FFFFFF,&H00FFFFFF,&H00181818,&H78000000,-1,0,0,0,100,100,0,0,1,3,1,7,42,42,30,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    first_start = min(float(line["start"]) for line in mixed["lines"])
    last_end = max(float(line["end"]) for line in mixed["lines"])
    title_end = max(1.0, min(first_start - 0.25, 7.0))
    lesson_label = plan["lesson"]
    title_en = plan.get("title_en") or lesson_label
    if title_en == lesson_label:
        title_line = lesson_label
    else:
        title_line = f"{lesson_label}  {title_en}"
    events = [
        f"Dialogue: 3,{ass_time(0.25)},{ass_time(title_end)},TitleEn,,0,0,0,,{{\\an5\\pos(960,220)}}{ass_escape(title_line)}",
        f"Dialogue: 3,{ass_time(0.25)},{ass_time(title_end)},TitleJa,,0,0,0,,{{\\an5\\pos(960,305)}}{ass_escape(plan['title_ja'])}",
        f"Dialogue: 3,{ass_time(first_start)},{ass_time(last_end + 0.2)},Header,,0,0,0,,{lesson_label}  •  {ass_escape(plan['grammar_target'])}",
    ]
    for line, layout in zip(mixed["lines"], layouts):
        words = line["english"].split()
        breaks = wrap_words(words)
        english_lines = len(breaks) + 1
        mixed_lines = layout["line_count"]
        if mixed_lines >= 3:
            english_y = 600 if english_lines >= 3 else (630 if english_lines == 2 else 670)
        elif mixed_lines == 2:
            english_y = 685 if english_lines >= 3 else (720 if english_lines == 2 else 770)
        else:
            english_y = 755 if english_lines >= 3 else (790 if english_lines == 2 else 830)
        if "word_timings" in line:
            intervals = [
                (float(item["start"]), float(item["end"]), int(item.get("display_index", index)))
                for index, item in enumerate(line["word_timings"])
            ]
        else:
            intervals = [
                (start, end, index)
                for index, (start, end) in enumerate(
                    word_intervals(float(line["start"]), float(line["end"]), words)
                )
            ]
        for start, end, active in intervals:
            events.append(
                f"Dialogue: 2,{ass_time(start)},{ass_time(end)},English,,0,0,0,,"
                f"{{\\an5\\pos(960,{english_y})}}{display_line(words, active, breaks)}"
            )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(header + "\n".join(events) + "\n", encoding="utf-8")


def number_expr(start: float, end: float, frames: int) -> str:
    if frames <= 1 or abs(end - start) < 0.000001:
        return f"{start:.6f}"
    progress = f"(on/{frames - 1})"
    eased = f"(({progress})*({progress})*(3-2*({progress})))"
    return f"{start:.6f}+({end - start:.6f})*{eased}"


def camera_motion(index: int, frames: int) -> tuple[str, str, str]:
    # One deliberate movement at most, matching the middle-school edition.
    # No sin/noise/random terms and no simultaneous pan+zoom: this explicitly
    # prevents the small hand-held-looking shake reported in the old H46 cut.
    mode = index % 4
    if mode == 0:
        zoom = number_expr(1.020, 1.085, frames)
        center_x, center_y = "0.500000", "0.480000"
    elif mode == 1:
        zoom = "1.040000"
        center_x, center_y = "0.500000", "0.500000"
    elif mode == 2:
        zoom = number_expr(1.085, 1.020, frames)
        center_x, center_y = "0.500000", "0.480000"
    else:
        zoom = number_expr(1.025, 1.070, frames)
        center_x, center_y = "0.500000", "0.520000"
    return zoom, center_x, center_y


def render_camera(plan: dict, root: Path, output: Path) -> None:
    duration = float(plan["duration"])
    transition = float(plan.get("transition", TRANSITION_DEFAULT))
    command = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "warning"]
    filters = []
    scenes = plan["scenes"]
    for index, scene in enumerate(scenes):
        start = float(scene["start"])
        stop = float(scenes[index + 1]["start"]) if index + 1 < len(scenes) else duration
        clip_duration = stop - start + (transition if index + 1 < len(scenes) else 0.0)
        frames = math.ceil(clip_duration * FPS)
        image = root / scene["image"]
        if not image.exists():
            raise FileNotFoundError(image)
        command.extend(["-i", str(image)])
        panel = int(scene.get("panel", 0))
        panel_crop = ""
        if panel:
            if panel not in {1, 2, 3, 4}:
                raise ValueError(f"invalid storyboard panel: {panel}")
            x_expr = "2" if panel in {1, 3} else "iw/2+2"
            y_expr = "2" if panel in {1, 2} else "ih/2+2"
            panel_crop = f"crop=w=iw/2-4:h=ih/2-4:x={x_expr}:y={y_expr},"
        zoom, center_x, center_y = camera_motion(index, frames)
        x = f"max(0,min(iw-iw/zoom,iw*({center_x})-iw/zoom/2))"
        y = f"max(0,min(ih-ih/zoom,ih*({center_y})-ih/zoom/2))"
        filters.append(
            f"[{index}:v]{panel_crop}scale=2400:1350:force_original_aspect_ratio=increase,crop=2400:1350,"
            f"zoompan=z='{zoom}':x='{x}':y='{y}':d={frames}:s=1920x1080:fps={FPS},"
            f"trim=duration={clip_duration:.6f},setpts=PTS-STARTPTS,format=yuv420p[v{index}]"
        )
    current = "v0"
    for index in range(1, len(scenes)):
        out = f"x{index}"
        filters.append(
            f"[{current}][v{index}]xfade=transition=fade:duration={transition:.3f}:"
            f"offset={float(scenes[index]['start']):.6f}[{out}]"
        )
        current = out
    filters.append(f"[{current}]trim=duration={duration:.6f},setpts=PTS-STARTPTS[vout]")
    output.parent.mkdir(parents=True, exist_ok=True)
    command.extend([
        "-filter_complex", ";".join(filters), "-map", "[vout]", "-an",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-r", str(FPS),
        "-pix_fmt", "yuv420p", str(output),
    ])
    run(command)


def burn(plan: dict, root: Path, camera: Path, audio: Path, ass: Path, overlays: list[Path], mixed: dict, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    pending = output.with_name(f".{output.stem}.{os.getpid()}.pending{output.suffix}")
    try:
        # Render outside the synchronized project folder.  A direct faststart
        # rewrite inside the folder once produced a duplicated moov atom, so
        # only a fully decoded file is copied back to the canonical location.
        with tempfile.TemporaryDirectory(prefix=f"{plan['lesson'].lower()}_render_") as temp_dir:
            rendered = Path(temp_dir) / output.name
            command = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "warning", "-i", str(camera), "-i", str(audio)]
            for overlay in overlays:
                command.extend(["-loop", "1", "-i", str(overlay)])
            filters = ["[0:v]drawbox=x=0:y=555:w=iw:h=525:color=black@0.42:t=fill[v0]"]
            current = "v0"
            for index, line in enumerate(mixed["lines"]):
                out = f"o{index}"
                filters.append(
                    f"[{current}][{index + 2}:v]overlay=0:0:enable='between(t,{float(line['start']):.4f},{float(line['end']):.4f})'[{out}]"
                )
                current = out
            ass_filter = str(ass.resolve()).replace("\\", r"\\").replace(":", r"\:").replace("'", r"\'")
            filters.append(f"[{current}]subtitles=filename='{ass_filter}'[vout]")
            command.extend([
                "-filter_complex", ";".join(filters), "-map", "[vout]", "-map", "1:a:0",
                "-t", f"{float(plan['duration']):.6f}", "-c:v", "libx264", "-preset", "fast", "-crf", "18",
                "-c:a", "aac", "-b:a", "256k", "-r", str(FPS), "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(rendered),
            ])
            run(command)
            run(["ffmpeg", "-v", "error", "-i", str(rendered), "-f", "null", "-"])
            shutil.copy2(rendered, pending)
            run(["ffmpeg", "-v", "error", "-i", str(pending), "-f", "null", "-"])
            os.replace(pending, output)
    finally:
        pending.unlink(missing_ok=True)


def probe(path: Path) -> dict:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
        check=True, capture_output=True, text=True,
    )
    return json.loads(result.stdout)


def build(root: Path, force_camera: bool = False) -> Path:
    plan = read_json(root / "planning" / "video_plan.json")
    if plan.get("visual_style_status") == "PENDING_USER_SELECTION":
        raise RuntimeError(
            f"{plan['lesson']} visual style is awaiting user selection; "
            "do not render unapproved draft images"
        )
    mixed = read_json(root / "planning" / "mixed_ruby.json")
    if [line["english"] for line in mixed["lines"]] != [re.sub(r"</?k>", "", row["en"]).replace(r"\N", " ") for row in plan["captions"]]:
        raise RuntimeError("mixed captions no longer match exact plan lyrics")
    policy = mixed.get("policy", "")
    if not any(
        marker in policy
        for marker in (
            "Only canonical new vocabulary",
            "Canonical new vocabulary from the current lesson",
        )
    ):
        raise RuntimeError("canonical-vocabulary caption policy is missing")
    invalid_sources = [
        replacement["source"]
        for line in mixed["lines"]
        for replacement in line["replacements"]
        if not replacement["source"].startswith("canonical_new_word")
    ]
    if invalid_sources:
        raise RuntimeError(f"noncanonical replacements: {invalid_sources}")
    timing_path = root / "planning" / "word_timing_tacobeat.json"
    mixed, timing_method = apply_tacobeat_timing(mixed, timing_path)
    exact_timing = timing_path.exists()
    version = "v5_tacobeat_canonical_vocab_color_only" if exact_timing else "v5_canonical_vocab_color_only"
    # Reuse the already verified stable-camera master; only the caption and
    # ruby overlays change in this edition.
    work = root / "work" / "mixed_ruby_v2"
    overlay_dir = work / "overlays"
    layouts = []
    overlays = []
    for index, line in enumerate(mixed["lines"], start=1):
        overlay = overlay_dir / f"{index:02d}.png"
        layouts.append(MIDDLE.render_overlay(line, overlay))
        overlays.append(overlay)
    ass = root / "captions" / f"{plan['lesson'].lower()}_exact_lyric_mixed_japanese_full_ruby_{version}.ass"
    write_ass(plan, mixed, layouts, ass)
    camera = work / f"{plan['lesson'].lower()}_stable_camera.mp4"
    if force_camera or not camera.exists():
        render_camera(plan, root, camera)
    audio = (root / plan["audio"]).resolve()
    source_name = Path(plan["output_name"]).stem
    output = root / "output" / f"{source_name}_mixed_japanese_full_ruby_{version}.mp4"
    burn(plan, root, camera, audio, ass, overlays, mixed, output)
    verification = {
        "lesson": plan["lesson"],
        "status": "PASS",
        "output": str(output),
        "adopted_audio": str(audio),
        "exact_lyric_lines": len(mixed["lines"]),
        "word_synchronous_highlight": exact_timing,
        "highlight_policy": f"color only; fixed {LYRIC_FONT_SIZE}px for normal and active words; no size/weight/position change",
        "word_timing_method": timing_method,
        "word_timing_file": str(timing_path) if exact_timing else None,
        "mixed_japanese": True,
        "canonical_lesson_vocabulary_only": True,
        "noncanonical_replacements": 0,
        "japanese_only_when_no_safe_canonical_span": True,
        "full_english_meaning_ruby": True,
        "full_kanji_reading_ruby": True,
        "camera_policy": "one smooth push/hold/pull per shot; smoothstep interpolation; no jitter/no random/no sinusoidal shake",
        "full_decode_passed": True,
        "layout_counts": {str(count): sum(item["line_count"] == count for item in layouts) for count in sorted(set(item["line_count"] for item in layouts))},
        "probe": probe(output),
    }
    (root / "output" / f"VERIFICATION_MIXED_RUBY_{version.upper()}.json").write_text(
        json.dumps(verification, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("lesson_dir", type=Path)
    parser.add_argument("--force-camera", action="store_true")
    args = parser.parse_args()
    print(build(args.lesson_dir.resolve(), args.force_camera))


if __name__ == "__main__":
    main()
