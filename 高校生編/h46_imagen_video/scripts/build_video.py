#!/usr/bin/env python3
"""Build the H46 ImageGen trial video from the approved eight-scene plan."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "planning" / "video_plan.json"
ASS_PATH = ROOT / "captions" / "h46_bilingual.ass"
OUTPUT_PATH = ROOT / "output" / "h46_democracy_constitution_imagen_cinematic.mp4"


def ass_time(seconds: float) -> str:
    centiseconds = round(seconds * 100)
    hours, remainder = divmod(centiseconds, 360000)
    minutes, remainder = divmod(remainder, 6000)
    secs, cs = divmod(remainder, 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{cs:02d}"


def ass_text(text: str) -> str:
    escaped = text.replace("{", r"\{").replace("}", r"\}")
    escaped = escaped.replace("<k>", r"{\c&H0066D1FF&}")
    escaped = escaped.replace("</k>", r"{\c&H00FFFFFF&}")
    return escaped


def write_ass(plan: dict) -> None:
    ASS_PATH.parent.mkdir(parents=True, exist_ok=True)
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Title,Helvetica Neue,76,&H00FFFFFF,&H000000FF,&HAA000000,&H70000000,-1,0,0,0,100,100,1,0,1,4,2,5,100,100,20,1
Style: TitleJa,Hiragino Sans,45,&H00FFFFFF,&H000000FF,&HAA000000,&H70000000,-1,0,0,0,100,100,1,0,1,3,1,5,100,100,20,1
Style: Header,Helvetica Neue,30,&H00FFFFFF,&H000000FF,&HAA000000,&H70000000,-1,0,0,0,100,100,0,0,1,2,1,7,48,48,35,1
Style: English,Helvetica Neue,51,&H00FFFFFF,&H000000FF,&HCC000000,&H00000000,-1,0,0,0,100,100,0,0,1,3,1,2,80,80,155,1
Style: Japanese,Hiragino Sans,39,&H00D8F3FF,&H000000FF,&HCC000000,&H00000000,-1,0,0,0,100,100,0,0,1,3,1,2,70,70,50,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    events = [
        f"Dialogue: 2,{ass_time(0.5)},{ass_time(8.8)},Title,,0,0,0,,{{\pos(960,465)}}H46  {plan['title_en']}",
        f"Dialogue: 2,{ass_time(0.5)},{ass_time(8.8)},TitleJa,,0,0,0,,{{\pos(960,575)}}{plan['title_ja']}",
        f"Dialogue: 2,{ass_time(9.0)},{ass_time(118.5)},Header,,0,0,0,,H46  •  {plan['title_en']}",
        f"Dialogue: 2,{ass_time(119.0)},{ass_time(130.8)},Title,,0,0,0,,{{\pos(960,465)}}H46  {plan['title_en']}",
        f"Dialogue: 2,{ass_time(119.0)},{ass_time(130.8)},TitleJa,,0,0,0,,{{\pos(960,575)}}{plan['title_ja']}",
    ]
    for caption in plan["captions"]:
        start = ass_time(float(caption["start"]))
        end = ass_time(float(caption["end"]))
        events.append(
            f"Dialogue: 2,{start},{end},English,,0,0,0,,{ass_text(caption['en'])}"
        )
        events.append(
            f"Dialogue: 2,{start},{end},Japanese,,0,0,0,,{ass_text(caption['ja'])}"
        )
    ASS_PATH.write_text(header + "\n".join(events) + "\n", encoding="utf-8")


def run() -> None:
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    write_ass(plan)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    duration = float(plan["duration"])
    transition = float(plan["transition"])
    scenes = plan["scenes"]
    command = ["ffmpeg", "-y", "-hide_banner"]
    filters: list[str] = []
    for index, scene in enumerate(scenes):
        start = float(scene["start"])
        stop = float(scenes[index + 1]["start"]) if index + 1 < len(scenes) else duration
        clip_duration = stop - start + (transition if index + 1 < len(scenes) else 0.0)
        image = ROOT / scene["image"]
        command.extend(["-loop", "1", "-framerate", "30", "-t", f"{clip_duration:.3f}", "-i", str(image)])
        zoom_step = 0.000055 + index * 0.000004
        filters.append(
            f"[{index}:v]scale=1920:1080:force_original_aspect_ratio=increase,"
            f"crop=1920:1080,zoompan=z='min(max(zoom,pzoom)+{zoom_step:.6f},1.045)':"
            "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=30,"
            f"setsar=1,format=yuv420p,setpts=PTS-STARTPTS[v{index}]"
        )

    audio_index = len(scenes)
    command.extend(["-i", str(ROOT / plan["audio"])])
    current = "v0"
    for index in range(1, len(scenes)):
        output = f"x{index}"
        offset = float(scenes[index]["start"])
        filters.append(
            f"[{current}][v{index}]xfade=transition=fade:duration={transition:.3f}:"
            f"offset={offset:.3f}[{output}]"
        )
        current = output

    ass_filter_path = str(ASS_PATH).replace("\\", "\\\\").replace(":", r"\:").replace("'", r"\'")
    filters.append(
        f"[{current}]fade=t=out:st={duration - 4.5:.3f}:d=4.5,"
        "drawbox=x=0:y=705:w=iw:h=375:color=black@0.58:t=fill:"
        "enable='between(t,9.2,118.7)',"
        f"ass=filename='{ass_filter_path}',format=yuv420p[vout]"
    )
    command.extend([
        "-filter_complex", ";".join(filters),
        "-map", "[vout]",
        "-map", f"{audio_index}:a:0",
        "-t", f"{duration:.3f}",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-movflags", "+faststart",
        "-c:a", "aac",
        "-b:a", "256k",
        str(OUTPUT_PATH),
    ])
    subprocess.run(command, cwd=ROOT, check=True)
    print(OUTPUT_PATH)


if __name__ == "__main__":
    run()
