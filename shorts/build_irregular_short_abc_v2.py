#!/usr/bin/env python3
"""Build a 30-second ABC-pattern irregular-verb memorization Short."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
SHORTS = Path(__file__).resolve().parent
SOURCE_ROOT = PROJECT / "中学生編" / "irregular_verbs_video_v3"
TIMELINE = SOURCE_ROOT / "planning" / "irregular_verbs_v6_youtube_timeline.json"
AUDIO = (
    SOURCE_ROOT
    / "source_audio"
    / "youtube_reference"
    / "teacher_tacos_irregular_verbs_c0bh8bZI6BY.webm"
)
OUT_MP4 = SHORTS / "irregular_verbs_short_abc_v2.mp4"
ASS_PATH = SHORTS / "irregular_verbs_short_abc_v2.ass"

W, H = 1080, 1920
IMAGE_H = 1100
FPS = 30
SOURCE_START = 64.61
SOURCE_END = 94.65
DURATION = SOURCE_END - SOURCE_START

# Subject-aware crops for the 1080x1100 upper image area. The scaled source is
# about 1954px wide, so valid x values are approximately 0..874.
CROP_X = {
    "begin": "620+24*sin(n/16)",
    "break": "435+24*sin(n/15)",
    "do": "430+20*sin(n/14)",
    "drink": "560+28*sin(n/18)",
    "drive": "210+260*n/53",
    "eat": "435+24*sin(n/16)",
    "get": "420+22*sin(n/16)",
    "give": "440+24*sin(n/16)",
    "go": "420+26*sin(n/17)",
    "know": "430+22*sin(n/16)",
    "rise": "430+24*sin(n/16)",
    "see": "435+24*sin(n/16)",
    "show": "430+22*sin(n/16)",
    "sing": "435+24*sin(n/16)",
    "speak": "430+24*sin(n/16)",
    "swim": "430+24*sin(n/16)",
    "take": "435+24*sin(n/16)",
}


def load_verbs() -> list[dict]:
    data = json.loads(TIMELINE.read_text(encoding="utf-8"))
    verbs = [verb for verb in data["verbs"] if 36 <= verb["index"] <= 52]
    if len(verbs) != 17:
        raise RuntimeError(f"Expected 17 verbs, found {len(verbs)}")
    for verb in verbs:
        verb["image_path"] = SOURCE_ROOT / verb["image"]
        verb["crop_x"] = CROP_X[verb["base"]]
    return verbs


VERBS = load_verbs()


def relative(seconds: float) -> float:
    return seconds - SOURCE_START


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


def form_size(form: str) -> int:
    if len(form) >= 12:
        return 66
    if len(form) >= 9:
        return 76
    if len(form) >= 7:
        return 88
    return 104


def build_ass() -> None:
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Series,Hiragino Sans W7,36,&H00FFFFFF,&H00FFFFFF,&H90000000,&H00000000,-1,0,0,0,100,100,2,0,1,2,0,4,0,0,0,1
Style: Hook,Hiragino Sans W7,80,&H00FFFFFF,&H00FFFFFF,&H90000000,&H50000000,-1,0,0,0,100,100,2,0,1,5,2,5,50,50,0,1
Style: HookAccent,Hiragino Sans W7,92,&H0038E6FF,&H0038E6FF,&H90000000,&H50000000,-1,0,0,0,100,100,2,0,1,5,2,5,50,50,0,1
Style: Guide,Hiragino Sans W7,46,&H0038E6FF,&H0038E6FF,&H90000000,&H30000000,-1,0,0,0,100,100,2,0,1,3,1,5,40,40,0,1
Style: Counter,Helvetica,34,&H00FFFFFF,&H00FFFFFF,&H90000000,&H00000000,-1,0,0,0,100,100,2,0,1,2,0,6,0,0,0,1
Style: Meaning,Hiragino Sans W7,58,&H00FFFFFF,&H00FFFFFF,&H90000000,&H00000000,-1,0,0,0,100,100,1,0,1,3,0,4,0,0,0,1
Style: Label,Helvetica,30,&H009FAFC5,&H009FAFC5,&H90000000,&H00000000,-1,0,0,0,100,100,2,0,1,1,0,4,0,0,0,1
Style: Form,Hiragino Sans W7,104,&H00FFFFFF,&H00FFFFFF,&H90000000,&H00000000,-1,0,0,0,100,100,1,0,1,4,1,4,0,0,0,1
Style: CTA,Hiragino Sans W7,56,&H0038E6FF,&H0038E6FF,&H90000000,&H40000000,-1,0,0,0,100,100,2,0,1,4,1,5,40,40,0,1
Style: Handle,Helvetica,30,&HB8FFFFFF,&HB8FFFFFF,&H90000000,&H00000000,0,0,0,0,100,100,1,0,1,2,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    lines = [
        dialogue(
            5,
            0,
            DURATION,
            "Series",
            "♪  30秒で17語  /  ABC型中心",
            r"{\pos(54,72)\fad(80,80)}",
        ),
        dialogue(
            7,
            0,
            2.65,
            "Hook",
            "不規則動詞変化",
            r"{\pos(540,330)\fad(80,140)}",
        ),
        dialogue(
            7,
            0.18,
            2.65,
            "HookAccent",
            "歌なら簡単に覚えられる！",
            r"{\pos(540,475)\fad(100,140)}",
        ),
        dialogue(
            6,
            2.65,
            DURATION - 1.9,
            "Guide",
            "歌に合わせて 3回ずつ♪",
            r"{\pos(540,155)\fad(100,100)}",
        ),
        dialogue(
            7,
            DURATION - 1.9,
            DURATION,
            "CTA",
            "保存して、もう1回歌おう！",
            r"{\pos(540,180)\fad(100,100)}",
        ),
        dialogue(
            4,
            0,
            DURATION,
            "Handle",
            "@TeacherTacosEnglish",
            r"{\pos(540,1860)}",
        ),
    ]

    row_y = (1320, 1510, 1700)
    row_labels = ("BASE  原形", "PAST  過去形", "P.P.  過去分詞")
    white = r"\c&H00FFFFFF&\fscx100\fscy100"
    yellow = r"\c&H0038E6FF&\fscx112\fscy112"

    for index, verb in enumerate(VERBS, start=1):
        start = relative(verb["start"])
        f1, f2, f3 = (relative(t) for t in verb["form_starts"])
        end = relative(verb["end"])
        forms = (verb["base"], verb["past"], verb["past_participle"])

        lines.extend(
            [
                dialogue(
                    5,
                    start,
                    end,
                    "Counter",
                    f"{index:02d} / {len(VERBS):02d}",
                    r"{\pos(1020,72)}",
                ),
                dialogue(
                    5,
                    start,
                    end,
                    "Meaning",
                    verb["jp"],
                    r"{\pos(76,1138)\fad(50,35)}",
                ),
            ]
        )

        for y, label in zip(row_y, row_labels):
            lines.append(
                dialogue(
                    4,
                    start,
                    end,
                    "Label",
                    label,
                    "{" + rf"\pos(80,{y})" + "}",
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
            for form_index, (y, form) in enumerate(zip(row_y, forms)):
                colour = yellow if form_index == active else white
                size = form_size(form)
                lines.append(
                    dialogue(
                        6,
                        phase_start,
                        phase_end,
                        "Form",
                        form,
                        "{" + rf"\pos(400,{y})\fs{size}" + colour + "}",
                    )
                )

    ASS_PATH.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")


def run() -> None:
    required = [TIMELINE, AUDIO, *(verb["image_path"] for verb in VERBS)]
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
                str(verb["image_path"]),
            ]
        )
    cmd.extend(
        [
            "-ss",
            str(SOURCE_START),
            "-t",
            str(DURATION),
            "-i",
            str(AUDIO),
        ]
    )

    filters = []
    for i, verb in enumerate(VERBS):
        duration = verb["end"] - verb["start"]
        filters.append(
            f"[{i}:v]scale=-2:{IMAGE_H}:flags=lanczos,"
            f"crop={W}:{IMAGE_H}:x='{verb['crop_x']}':y=0,"
            f"trim=duration={duration:.3f},setpts=PTS-STARTPTS[v{i}]"
        )
    filters.append(
        "".join(f"[v{i}]" for i in range(len(VERBS)))
        + f"concat=n={len(VERBS)}:v=1:a=0,"
        + f"pad={W}:{H}:0:0:color=0x081427[base]"
    )
    escaped_ass = str(ASS_PATH).replace(":", r"\:").replace("'", r"\'")
    filters.append(
        "[base]"
        "drawbox=x=0:y=0:w=1080:h=230:color=black@0.30:t=fill,"
        "drawbox=x=0:y=1035:w=1080:h=885:color=0x081427@0.98:t=fill,"
        "drawbox=x=0:y=1035:w=1080:h=6:color=0xffd93d@1.0:t=fill,"
        "drawbox=x=70:y=1230:w=5:h=560:color=0xffd93d@0.8:t=fill,"
        "drawbox=x=80:y=1407:w=920:h=1:color=white@0.13:t=fill,"
        "drawbox=x=80:y=1597:w=920:h=1:color=white@0.13:t=fill,"
        f"subtitles=filename='{escaped_ass}'[vout]"
    )

    cmd.extend(
        [
            "-filter_complex",
            ";".join(filters),
            "-map",
            "[vout]",
            "-map",
            f"{len(VERBS)}:a:0",
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
            f"afade=t=out:st={DURATION - 0.12:.2f}:d=0.12",
            "-t",
            str(DURATION),
            "-movflags",
            "+faststart",
            "-shortest",
            str(OUT_MP4),
        ]
    )

    print("Building 30-second ABC memorization Short…", flush=True)
    result = subprocess.run(cmd, text=True, capture_output=True)
    if result.returncode:
        print(result.stderr[-6000:], file=sys.stderr)
        raise SystemExit(result.returncode)

    size_mib = OUT_MP4.stat().st_size / 1024 / 1024
    print(f"Built: {OUT_MP4}")
    print(f"Duration: {DURATION:.2f}s / Verbs: {len(VERBS)} / Size: {size_mib:.1f} MiB")


if __name__ == "__main__":
    run()
