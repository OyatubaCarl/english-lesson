#!/usr/bin/env python3
"""Build a motion-enhanced Mio edition while preserving every earlier output."""

from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_BUILDER_PATH = ROOT / "scripts" / "build_video.py"
MOTION_PATH = ROOT / "planning" / "motion_plan.json"

spec = importlib.util.spec_from_file_location("l1_mio_base_builder", BASE_BUILDER_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load the Mio builder: {BASE_BUILDER_PATH}")

mio_base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mio_base)
builder = mio_base.builder

builder.SCENES_VIDEO = builder.WORK_DIR / "l1_mio_scenes_pan_zoom.mp4"
builder.FINAL_VIDEO = (
    builder.OUTPUT_DIR / "l1_my_family_and_pochi_mio_bilingual_pan_zoom.mp4"
)
builder.CONTACT_SHEET = (
    builder.OUTPUT_DIR / "l1_mio_pan_zoom_scene_contact_sheet.jpg"
)


def zoom_expression(start: float, end: float, frames: int) -> str:
    if frames <= 1 or abs(end - start) < 0.000001:
        return f"{start:.6f}"
    delta = end - start
    return f"{start:.6f}+({delta:.6f})*on/{frames - 1}"


def motion_expressions(
    motion: str,
    start_zoom: float,
    end_zoom: float,
    frames: int,
) -> tuple[str, str, str]:
    zoom = zoom_expression(start_zoom, end_zoom, frames)
    center_x = "iw/2-(iw/zoom/2)"
    center_y = "ih/2-(ih/zoom/2)"
    progress = f"on/{max(1, frames - 1)}"

    if motion.startswith("pan_left_to_right"):
        x = f"(iw-iw/zoom)*({progress})"
        y = center_y
    elif motion.startswith("pan_right_to_left"):
        x = f"(iw-iw/zoom)*(1-({progress}))"
        y = center_y
    elif motion == "pan_top_to_bottom":
        x = center_x
        y = f"(ih-ih/zoom)*({progress})"
    elif motion == "pan_bottom_to_top":
        x = center_x
        y = f"(ih-ih/zoom)*(1-({progress}))"
    else:
        x = center_x
        y = center_y
    return zoom, x, y


def render_scenes_with_motion(plan: dict) -> None:
    motion_plan = json.loads(MOTION_PATH.read_text(encoding="utf-8"))
    motion_by_id = {item["id"]: item for item in motion_plan["scenes"]}

    scenes = plan["scenes"]
    inputs: list[str] = []
    filters: list[str] = []

    for index, scene in enumerate(scenes):
        image_path = builder.SCENES_DIR / f"{scene['id']}.png"
        if not image_path.exists():
            raise FileNotFoundError(f"missing scene image: {image_path}")
        inputs.extend(["-i", str(image_path)])

        duration = float(scene["end"]) - float(scene["start"])
        clip_duration = (
            duration + (builder.FADE if index < len(scenes) - 1 else 0)
        )
        frames = math.ceil(clip_duration * builder.FPS)
        motion = motion_by_id[scene["id"]]
        zoom, x_expr, y_expr = motion_expressions(
            motion["motion"],
            float(motion["start_zoom"]),
            float(motion["end_zoom"]),
            frames,
        )

        filters.append(
            f"[{index}:v]"
            "scale=2304:1296:force_original_aspect_ratio=increase,"
            "crop=2304:1296,"
            f"zoompan=z='{zoom}':x='{x_expr}':y='{y_expr}':"
            f"d={frames}:s=1920x1080:fps={builder.FPS},"
            f"trim=duration={clip_duration:.6f},"
            "setpts=PTS-STARTPTS,format=yuv420p"
            f"[v{index}]"
        )

    current = "v0"
    for index in range(1, len(scenes)):
        boundary = float(scenes[index]["start"])
        out = f"x{index}"
        filters.append(
            f"[{current}][v{index}]"
            f"xfade=transition=fade:duration={builder.FADE:.3f}:"
            f"offset={boundary:.6f}[{out}]"
        )
        current = out

    final_duration = float(scenes[-1]["end"])
    filters.append(
        f"[{current}]trim=duration={final_duration:.6f},"
        "setpts=PTS-STARTPTS[video]"
    )

    builder.run(
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
            str(builder.FPS),
            "-pix_fmt",
            "yuv420p",
            str(builder.SCENES_VIDEO),
        ]
    )


builder.render_scenes = render_scenes_with_motion


if __name__ == "__main__":
    builder.main()

