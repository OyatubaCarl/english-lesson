#!/usr/bin/env python3
"""Build a vertical YouTube Short for the AAA irregular-verb pattern.

The video uses the first four entries from the canonical irregular-verb song:
cut-cut-cut / hit-hit-hit / put-put-put / set-set-set.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
SHORTS = Path(__file__).resolve().parent
SOURCE_ROOT = PROJECT / "中学生編" / "irregular_verbs_video_v3"
AUDIO = (
    SOURCE_ROOT
    / "source_audio"
    / "youtube_reference"
    / "teacher_tacos_irregular_verbs_c0bh8bZI6BY.webm"
)
OUT_MP4 = SHORTS / "irregular_verbs_short_aaa.mp4"
ASS_PATH = SHORTS / "irregular_verbs_short_aaa.ass"

W, H = 1080, 1920
FPS = 30
DURATION = 8.09

VERBS = [
    {
        "image": SOURCE_ROOT / "scenes" / "generated" / "01_cut.png",
        "jp": "切る",
        "forms": ("cut", "cut", "cut"),
        "start": 0.00,
        "form_starts": (1.52, 1.88, 2.22),
        "end": 2.89,
        "crop_x": "1140+24*sin(n/18)",
    },
    {
        "image": SOURCE_ROOT / "scenes" / "generated" / "02_hit.png",
        "jp": "打つ",
        "forms": ("hit", "hit", "hit"),
        "start": 2.89,
        "form_starts": (3.24, 3.64, 3.92),
        "end": 4.91,
        "crop_x": "265+520*n/61",
    },
    {
        "image": SOURCE_ROOT / "scenes" / "generated" / "03_put.png",
        "jp": "置く",
        "forms": ("put", "put", "put"),
        "start": 4.91,
        "form_starts": (5.26, 5.62, 5.96),
        "end": 6.77,
        "crop_x": "1305+30*sin(n/17)",
    },
    {
        "image": SOURCE_ROOT / "scenes" / "generated" / "04_set.png",
        "jp": "置く・設定する",
        "forms": ("set", "set", "set"),
        "start": 6.77,
        "form_starts": (7.12, 7.48, 7.82),
        "end": 8.09,
        "crop_x": "1160+22*sin(n/16)",
    },
]


def ass_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds - hours * 3600 - minutes * 60
    return f"{hours}:{minutes:02d}:{secs:05.2f}"


def dialogue(
    layer: int,
    start: float,
    end: float,
    style: str,
    text: str,
    override: str = "",
) -> str:
    return (
        f"Dialogue: {layer},{ass_time(start)},{ass_time(end)},{style},,0,0,0,,"
        f"{override}{text}"
    )


def build_ass() -> None:
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Brand,Hiragino Sans W7,42,&H00FFFFFF,&H00FFFFFF,&H90000000,&H00000000,-1,0,0,0,100,100,2,0,1,2,0,5,0,0,0,1
Style: Hook,Hiragino Sans W7,88,&H00FFFFFF,&H00FFFFFF,&H90000000,&H50000000,-1,0,0,0,100,100,2,0,1,5,2,5,70,70,0,1
Style: Pattern,Hiragino Sans W7,64,&H0038E6FF,&H0038E6FF,&H90000000,&H30000000,-1,0,0,0,100,100,2,0,1,4,1,5,60,60,0,1
Style: Meaning,Hiragino Sans W7,72,&H00FFFFFF,&H00FFFFFF,&H90000000,&H00000000,-1,0,0,0,100,100,2,0,1,5,1,5,60,60,0,1
Style: Label,Hiragino Sans W6,30,&H00E7E2D8,&H00E7E2D8,&H90000000,&H00000000,-1,0,0,0,100,100,1,0,1,2,0,5,0,0,0,1
Style: Form,Hiragino Sans W7,104,&H00FFFFFF,&H00FFFFFF,&H90000000,&H00000000,-1,0,0,0,100,100,1,0,1,5,2,5,0,0,0,1
Style: Arrow,Hiragino Sans W7,58,&H00E7E2D8,&H00E7E2D8,&H90000000,&H00000000,-1,0,0,0,100,100,0,0,1,3,0,5,0,0,0,1
Style: Progress,Hiragino Sans W7,38,&H00FFFFFF,&H00FFFFFF,&H90000000,&H00000000,-1,0,0,0,100,100,8,0,1,2,0,5,0,0,0,1
Style: Handle,Helvetica,32,&HC8FFFFFF,&HC8FFFFFF,&H90000000,&H00000000,0,0,0,0,100,100,1,0,1,2,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    lines = [
        dialogue(
            4,
            0,
            DURATION,
            "Brand",
            "♪  不規則動詞の歌  ・  AAA型",
            r"{\pos(540,112)\fad(100,80)}",
        ),
        dialogue(
            5,
            0,
            1.46,
            "Hook",
            r"3回とも同じ！\N歌える？",
            r"{\pos(540,300)\fad(80,120)}",
        ),
        dialogue(
            4,
            1.46,
            DURATION,
            "Pattern",
            "変化しない「 A A A 型 」",
            r"{\pos(540,242)\fad(100,80)}",
        ),
        dialogue(
            3,
            0,
            DURATION,
            "Label",
            "原形  BASE",
            r"{\pos(210,1515)}",
        ),
        dialogue(
            3,
            0,
            DURATION,
            "Label",
            "過去形  PAST",
            r"{\pos(540,1515)}",
        ),
        dialogue(
            3,
            0,
            DURATION,
            "Label",
            "過去分詞  P.P.",
            r"{\pos(870,1515)}",
        ),
        dialogue(
            3,
            0,
            DURATION,
            "Arrow",
            "→",
            r"{\pos(375,1625)}",
        ),
        dialogue(
            3,
            0,
            DURATION,
            "Arrow",
            "→",
            r"{\pos(705,1625)}",
        ),
        dialogue(
            3,
            0,
            DURATION,
            "Handle",
            "@TeacherTacosEnglish",
            r"{\pos(540,1840)}",
        ),
    ]

    positions = (210, 540, 870)
    white = r"\c&H00FFFFFF&\fscx100\fscy100"
    yellow = r"\c&H0038E6FF&\fscx116\fscy116"

    for index, verb in enumerate(VERBS):
        start = verb["start"]
        f1, f2, f3 = verb["form_starts"]
        end = verb["end"]
        forms = verb["forms"]

        lines.append(
            dialogue(
                4,
                start,
                end,
                "Meaning",
                verb["jp"],
                r"{\pos(540,1370)\fad(80,60)}",
            )
        )

        dots = ["○"] * len(VERBS)
        dots[index] = "●"
        lines.append(
            dialogue(
                4,
                start,
                end,
                "Progress",
                "  ".join(dots),
                r"{\pos(540,1260)}",
            )
        )

        phases = [
            (start, f1, None),
            (f1, f2, 0),
            (f2, f3, 1),
            (f3, end, 2),
        ]
        for phase_start, phase_end, active in phases:
            if phase_end <= phase_start:
                continue
            for form_index, (x, form) in enumerate(zip(positions, forms)):
                colour = yellow if form_index == active else white
                lines.append(
                    dialogue(
                        5,
                        phase_start,
                        phase_end,
                        "Form",
                        form,
                        "{" + rf"\pos({x},1625)" + colour + "}",
                    )
                )

    ASS_PATH.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")


def run() -> None:
    required = [AUDIO, *(verb["image"] for verb in VERBS)]
    missing = [path for path in required if not path.exists()]
    if missing:
        print("Missing source files:", file=sys.stderr)
        for path in missing:
            print(f"  {path}", file=sys.stderr)
        raise SystemExit(1)

    build_ass()

    cmd = ["ffmpeg", "-y"]
    for verb in VERBS:
        duration = verb["end"] - verb["start"]
        cmd.extend(
            [
                "-loop",
                "1",
                "-framerate",
                str(FPS),
                "-t",
                f"{duration:.3f}",
                "-i",
                str(verb["image"]),
            ]
        )
    cmd.extend(["-ss", "0", "-t", str(DURATION), "-i", str(AUDIO)])

    filters = []
    for i, verb in enumerate(VERBS):
        duration = verb["end"] - verb["start"]
        filters.append(
            f"[{i}:v]scale=-2:{H}:flags=lanczos,"
            f"crop={W}:{H}:x='{verb['crop_x']}':y=0,"
            f"trim=duration={duration:.3f},setpts=PTS-STARTPTS[v{i}]"
        )
    filters.append("".join(f"[v{i}]" for i in range(len(VERBS))) + "concat=n=4:v=1:a=0[base]")
    escaped_ass = str(ASS_PATH).replace(":", r"\:").replace("'", r"\'")
    filters.append(
        "[base]"
        "drawbox=x=0:y=0:w=1080:h=500:color=black@0.25:t=fill,"
        "drawbox=x=0:y=1190:w=1080:h=730:color=black@0.48:t=fill,"
        f"subtitles=filename='{escaped_ass}'[vout]"
    )

    cmd.extend(
        [
            "-filter_complex",
            ";".join(filters),
            "-map",
            "[vout]",
            "-map",
            "4:a:0",
            "-r",
            str(FPS),
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-af",
            "afade=t=out:st=7.94:d=0.15",
            "-t",
            str(DURATION),
            "-movflags",
            "+faststart",
            "-shortest",
            str(OUT_MP4),
        ]
    )

    print("Building AAA-pattern Short…", flush=True)
    result = subprocess.run(cmd, text=True, capture_output=True)
    if result.returncode:
        print(result.stderr[-6000:], file=sys.stderr)
        raise SystemExit(result.returncode)

    size_mib = OUT_MP4.stat().st_size / 1024 / 1024
    print(f"Built: {OUT_MP4}")
    print(f"Size: {size_mib:.1f} MiB")


if __name__ == "__main__":
    run()
