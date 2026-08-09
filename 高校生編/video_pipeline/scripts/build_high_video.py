#!/usr/bin/env python3
"""Build one high-school lesson video from its adopted audio and scene plan."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


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


def write_ass(plan: dict, ass_path: Path) -> None:
    ass_path.parent.mkdir(parents=True, exist_ok=True)
    duration = float(plan["duration"])
    caption_start = min(float(item["start"]) for item in plan["captions"])
    caption_end = max(float(item["end"]) for item in plan["captions"])
    title_end = min(caption_start - 0.4, float(plan.get("title_end", 9.5)))
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes
WrapStyle: 2

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
        f"Dialogue: 2,{ass_time(0.5)},{ass_time(title_end)},Title,,0,0,0,,{{\\pos(960,465)}}{plan['lesson']}  {plan['title_en']}",
        f"Dialogue: 2,{ass_time(0.5)},{ass_time(title_end)},TitleJa,,0,0,0,,{{\\pos(960,575)}}{plan['title_ja']}",
        f"Dialogue: 2,{ass_time(caption_start)},{ass_time(caption_end + 0.2)},Header,,0,0,0,,{plan['lesson']}  •  {plan['grammar_target']}",
    ]
    for caption in plan["captions"]:
        start = ass_time(float(caption["start"]))
        end = ass_time(float(caption["end"]))
        events.append(f"Dialogue: 2,{start},{end},English,,0,0,0,,{ass_text(caption['en'])}")
        if caption.get("ja"):
            events.append(f"Dialogue: 2,{start},{end},Japanese,,0,0,0,,{ass_text(caption['ja'])}")
    if duration - caption_end >= 5.0:
        events.extend([
            f"Dialogue: 2,{ass_time(caption_end + 1.5)},{ass_time(duration - 0.8)},Title,,0,0,0,,{{\\pos(960,465)}}{plan['lesson']}  {plan['title_en']}",
            f"Dialogue: 2,{ass_time(caption_end + 1.5)},{ass_time(duration - 0.8)},TitleJa,,0,0,0,,{{\\pos(960,575)}}{plan['title_ja']}",
        ])
    ass_path.write_text(header + "\n".join(events) + "\n", encoding="utf-8")


def build(root: Path) -> Path:
    plan_path = root / "planning" / "video_plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    ass_path = root / "captions" / f"{plan['lesson'].lower()}_bilingual.ass"
    write_ass(plan, ass_path)
    output_path = root / "output" / plan["output_name"]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    duration = float(plan["duration"])
    transition = float(plan.get("transition", 0.8))
    scenes = plan["scenes"]
    command = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "warning"]
    filters: list[str] = []
    for index, scene in enumerate(scenes):
        start = float(scene["start"])
        stop = float(scenes[index + 1]["start"]) if index + 1 < len(scenes) else duration
        clip_duration = stop - start + (transition if index + 1 < len(scenes) else 0.0)
        image = root / scene["image"]
        if not image.exists():
            raise FileNotFoundError(image)
        command.extend(["-loop", "1", "-framerate", "30", "-t", f"{clip_duration:.3f}", "-i", str(image)])
        zoom_step = 0.000048 + (index % 4) * 0.000004
        panel = int(scene.get("panel", 0))
        panel_crop = ""
        if panel:
            if panel not in {1, 2, 3, 4}:
                raise ValueError(f"invalid storyboard panel: {panel}")
            x_expr = "2" if panel in {1, 3} else "iw/2+2"
            y_expr = "2" if panel in {1, 2} else "ih/2+2"
            panel_crop = f"crop=w=iw/2-4:h=ih/2-4:x={x_expr}:y={y_expr},"
        filters.append(
            f"[{index}:v]{panel_crop}scale=1920:1080:force_original_aspect_ratio=increase,"
            f"crop=1920:1080,zoompan=z='min(max(zoom,pzoom)+{zoom_step:.6f},1.040)':"
            "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=30,"
            f"setsar=1,format=yuv420p,setpts=PTS-STARTPTS[v{index}]"
        )
    audio_index = len(scenes)
    audio = (root / plan["audio"]).resolve()
    if not audio.exists():
        raise FileNotFoundError(audio)
    command.extend(["-i", str(audio)])
    current = "v0"
    for index in range(1, len(scenes)):
        output = f"x{index}"
        filters.append(
            f"[{current}][v{index}]xfade=transition=fade:duration={transition:.3f}:"
            f"offset={float(scenes[index]['start']):.3f}[{output}]"
        )
        current = output
    caption_start = min(float(item["start"]) for item in plan["captions"])
    caption_end = max(float(item["end"]) for item in plan["captions"])
    ass_filter = str(ass_path.resolve()).replace("\\", "\\\\").replace(":", r"\:").replace("'", r"\'")
    filters.append(
        f"[{current}]fade=t=out:st={max(0.0, duration - 4.0):.3f}:d=4.0,"
        "drawbox=x=0:y=705:w=iw:h=375:color=black@0.56:t=fill:"
        f"enable='between(t,{caption_start - 0.1:.3f},{caption_end + 0.2:.3f})',"
        f"ass=filename='{ass_filter}',format=yuv420p[vout]"
    )
    command.extend([
        "-filter_complex", ";".join(filters),
        "-map", "[vout]", "-map", f"{audio_index}:a:0",
        "-t", f"{duration:.3f}", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-movflags", "+faststart", "-c:a", "aac", "-b:a", "256k", str(output_path),
    ])
    subprocess.run(command, cwd=root, check=True)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("lesson_dir", type=Path)
    args = parser.parse_args()
    print(build(args.lesson_dir.resolve()))


if __name__ == "__main__":
    main()
