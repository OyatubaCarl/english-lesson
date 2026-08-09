#!/usr/bin/env python3
"""Build the YouTube-audio edition: one full-screen action image per verb."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps


HERE = Path(__file__).resolve().parent
AUDIO = (
    HERE
    / "source_audio"
    / "youtube_reference"
    / "teacher_tacos_irregular_verbs_c0bh8bZI6BY.webm"
)
GENERATED = HERE / "scenes" / "generated"
DISPLAY = HERE / "work" / "display_frames"
TRANSITIONS = HERE / "work" / "transition_frames"
CAPTIONS = HERE / "captions"
PLANNING = HERE / "planning"
OUTPUT = HERE / "output"
WORK = HERE / "work"

WIDTH = 1920
HEIGHT = 1080
FPS = 30
AUDIO_END = 101.901
VERSION = "v6_youtube"
TRANSITION_DURATION = 0.12
TRANSITION_FRAMES = 4


# Japanese meaning, display base, display past, display participle,
# entry start, and the start time of each sung form.
VERBS = [
    ("切る", "cut", "cut", "cut", 0.000, (1.380, 1.740, 2.080)),
    ("打つ", "hit", "hit", "hit", 2.560, (3.221, 3.581, 3.941)),
    ("置く", "put", "put", "put", 4.640, (5.121, 5.481, 5.821)),
    ("置く・据える／設定する", "set", "set", "set", 6.340, (6.981, 7.341, 7.682)),
    ("〜になる", "become", "became", "become", 7.960, (8.300, 8.760, 9.180)),
    ("来る", "come", "came", "come", 9.600, (9.760, 10.060, 10.340)),
    ("走る", "run", "ran", "run", 10.480, (10.782, 11.122, 11.462)),
    ("持ってくる", "bring", "brought", "brought", 11.940, (12.602, 12.983, 13.323)),
    ("建てる・組み立てる", "build", "built", "built", 13.680, (14.060, 14.400, 14.940)),
    ("買う", "buy", "bought", "bought", 15.440, (15.783, 16.360, 16.720)),
    ("つかまえる", "catch", "caught", "caught", 17.220, (17.780, 18.140, 18.740)),
    ("感じる", "feel", "felt", "felt", 19.120, (19.680, 20.060, 20.500)),
    ("見つける", "find", "found", "found", 20.940, (21.500, 21.860, 22.400)),
    ("持っている", "have", "had", "had", 22.820, (23.440, 23.840, 24.340)),
    ("聞く・聞こえる", "hear", "heard", "heard", 24.760, (25.360, 25.680, 26.280)),
    ("保つ・持ち続ける", "keep", "kept", "kept", 26.680, (27.500, 27.980, 28.300)),
    ("学ぶ", "learn", "learned / learnt", "learned / learnt", 28.660, (29.020, 29.400, 29.900)),
    ("去る・出発する", "leave", "left", "left", 30.420, (31.220, 31.760, 32.040)),
    ("失う", "lose", "lost", "lost", 32.280, (32.860, 33.520, 33.820)),
    ("作る", "make", "made", "made", 34.120, (34.920, 35.340, 35.760)),
    ("会う", "meet", "met", "met", 36.000, (36.800, 37.300, 37.620)),
    ("支払う", "pay", "paid", "paid", 37.780, (38.760, 39.080, 39.640)),
    ("読む", "read /riːd/", "read /red/", "read /red/", 39.720, (40.580, 40.920, 41.320)),
    ("言う", "say", "said", "said", 41.640, (42.128, 42.608, 43.129)),
    ("売る", "sell", "sold", "sold", 43.440, (43.800, 44.269, 44.729)),
    ("送る", "send", "sent", "sent", 45.229, (45.669, 46.109, 46.609)),
    ("座る", "sit", "sat", "sat", 47.069, (47.569, 48.009, 48.470)),
    ("眠る", "sleep", "slept", "slept", 48.950, (49.370, 50.030, 50.470)),
    ("過ごす／費やす", "spend", "spent", "spent", 50.850, (51.210, 51.850, 52.350)),
    ("立つ", "stand", "stood", "stood", 53.010, (53.791, 54.171, 54.511)),
    ("教える", "teach", "taught", "taught", 54.871, (55.291, 55.751, 56.111)),
    ("伝える・話す", "tell", "told", "told", 56.451, (56.931, 57.631, 57.991)),
    ("考える", "think", "thought", "thought", 58.332, (59.032, 59.492, 59.852)),
    # The recording omits the base form, so it stays visible but is never highlighted.
    ("理解する", "understand", "understood", "understood", 60.192, (60.992, 60.992, 61.912)),
    ("勝つ", "win", "won", "won", 62.812, (63.152, 63.753, 64.193)),
    ("始める", "begin", "began", "begun", 64.633, (65.133, 65.493, 65.853)),
    ("こわす・壊れる", "break", "broke", "broken", 66.193, (66.513, 66.793, 66.993)),
    ("する", "do", "did", "done", 67.473, (67.833, 68.193, 68.414)),
    ("飲む", "drink", "drank", "drunk", 68.674, (68.874, 69.354, 69.814)),
    ("運転する", "drive", "drove", "driven", 70.254, (70.954, 71.234, 71.554)),
    ("食べる", "eat", "ate", "eaten", 72.174, (72.714, 73.174, 73.595)),
    ("得る・手に入れる", "get", "got", "got / gotten", 74.095, (74.395, 74.755, 75.115)),
    ("与える", "give", "gave", "given", 75.835, (76.375, 76.855, 77.215)),
    ("行く", "go", "went", "gone", 77.835, (78.155, 78.696, 79.196)),
    ("知っている", "know", "knew", "known", 79.516, (80.096, 80.616, 80.756)),
    ("昇る・上がる", "rise", "rose", "risen", 81.356, (81.796, 82.496, 82.956)),
    ("見る・見える", "see", "saw", "seen", 83.376, (83.877, 84.337, 84.797)),
    ("見せる", "show", "showed", "shown / showed", 85.197, (85.717, 86.197, 86.637)),
    ("歌う", "sing", "sang", "sung", 87.197, (87.617, 88.057, 88.518)),
    ("話す", "speak", "spoke", "spoken", 88.918, (89.398, 89.878, 90.318)),
    ("泳ぐ", "swim", "swam", "swum", 90.818, (91.198, 91.718, 92.198)),
    ("取る・持っていく", "take", "took", "taken", 92.798, (93.138, 93.719, 94.079)),
    ("目を覚ます", "wake", "woke", "woken", 94.639, (95.599, 96.079, 96.459)),
    ("身につける・着ている", "wear", "wore", "worn", 97.019, (97.519, 97.979, 98.419)),
    ("書く", "write", "wrote", "written", 98.880, (99.340, 99.800, 100.240)),
]

# Timings re-measured against the exact audio downloaded from the user's
# YouTube video. YouTube's auto-caption word timings were cross-checked against
# the burnt-in red karaoke labels in the source video. The recording skips the
# base form ``understand``; the first 60.600 entry is therefore the start of the
# first ``understood`` and is intentionally shared by base/past timing slots.
YOUTUBE_FORM_STARTS = [
    (1.520, 1.880, 2.220),  # 01 cut
    (3.240, 3.640, 3.920),  # 02 hit
    (5.260, 5.620, 5.960),  # 03 put
    (7.120, 7.480, 7.820),  # 04 set
    (8.440, 8.900, 9.320),  # 05 become
    (9.900, 10.200, 10.480),  # 06 come
    (10.920, 11.260, 11.600),  # 07 run
    (12.840, 13.120, 13.440),  # 08 bring
    (14.080, 14.560, 15.040),  # 09 build
    (15.880, 16.480, 16.880),  # 10 buy
    (17.960, 18.320, 18.800),  # 11 catch
    (19.780, 20.160, 20.680),  # 12 feel
    (21.680, 22.040, 22.520),  # 13 find
    (23.560, 23.960, 24.360),  # 14 have
    (25.440, 25.760, 26.280),  # 15 hear
    (27.680, 28.040, 28.400),  # 16 keep
    (29.180, 29.560, 29.960),  # 17 learn
    (30.720, 31.360, 31.920),  # 18 leave
    (32.599, 33.280, 33.800),  # 19 lose
    (34.400, 35.040, 35.600),  # 20 make
    (36.160, 36.960, 37.440),  # 21 meet
    (38.400, 38.880, 39.320),  # 22 pay
    (40.460, 40.800, 41.280),  # 23 read
    (41.840, 42.480, 43.000),  # 24 say
    (43.520, 44.200, 44.720),  # 25 sell
    (45.280, 46.040, 46.520),  # 26 send
    (47.480, 47.920, 48.400),  # 27 sit
    (49.340, 50.000, 50.480),  # 28 sleep
    (51.120, 51.880, 52.360),  # 29 spend
    (53.700, 54.080, 54.440),  # 30 stand
    (54.880, 55.640, 56.000),  # 31 teach
    (56.440, 57.480, 57.880),  # 32 tell
    (58.860, 59.320, 59.720),  # 33 think
    (60.600, 60.600, 61.800),  # 34 understand -> understood -> understood
    (62.760, 63.640, 64.040),  # 35 win
    (64.960, 65.320, 65.680),  # 36 begin
    (66.200, 66.640, 66.880),  # 37 break
    (67.400, 67.960, 68.120),  # 38 do
    (68.480, 69.160, 69.600),  # 39 drink
    (70.720, 71.000, 71.320),  # 40 drive
    (72.460, 72.920, 73.280),  # 41 eat
    (73.920, 74.520, 74.840),  # 42 get
    (76.200, 76.800, 77.100),  # 43 give
    (77.640, 78.520, 78.920),  # 44 go
    (79.760, 80.280, 80.760),  # 45 know
    (82.200, 82.440, 82.640),  # 46 rise
    (83.200, 83.920, 84.400),  # 47 see
    (85.000, 85.760, 86.240),  # 48 show
    (87.240, 87.680, 88.120),  # 49 sing
    (89.040, 89.520, 90.000),  # 50 speak
    (90.520, 91.240, 91.720),  # 51 swim
    (92.750, 93.500, 93.750),  # 52 take
    (95.000, 95.750, 96.500),  # 53 wake
    (97.250, 98.000, 98.500),  # 54 wear
    (99.250, 99.600, 100.000),  # 55 write
]

if len(YOUTUBE_FORM_STARTS) != len(VERBS):
    raise ValueError("YouTube timing count must match the 55 verb rows")

# Switch the full-screen action image shortly before the first sung form. This
# retains a brief visual lead-in without showing the next action over the prior
# verb. ``understand`` needs a little more lead time for its Japanese meaning.
_youtube_verbs = []
for _index, (_row, _starts) in enumerate(zip(VERBS, YOUTUBE_FORM_STARTS)):
    if _index == 0:
        _entry = 0.0
    else:
        _lead = 0.60 if _index == 33 else 0.35
        _entry = max(YOUTUBE_FORM_STARTS[_index - 1][2] + 0.05, _starts[0] - _lead)
        _entry = min(_entry, _starts[0] - 0.05)
    _youtube_verbs.append((*_row[:4], round(_entry, 3), _starts))
VERBS = _youtube_verbs


def run(cmd: list[str]) -> None:
    if cmd and cmd[0] == "ffmpeg":
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "warning", *cmd[1:]]
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def action_files() -> list[Path]:
    files = sorted(GENERATED.glob("*.png"))
    numbers = [int(path.name.split("_", 1)[0]) for path in files]
    if numbers != list(range(1, 56)):
        raise ValueError(f"expected action images 01..55, got {numbers}")
    return files


def make_display_frames(source_files: list[Path]) -> list[Path]:
    DISPLAY.mkdir(parents=True, exist_ok=True)
    paths = []
    for index, source in enumerate(source_files, start=1):
        output = DISPLAY / f"{index:02d}.jpg"
        image = ImageOps.fit(
            Image.open(source).convert("RGB"),
            (WIDTH, HEIGHT),
            Image.Resampling.LANCZOS,
            centering=(0.5, 0.5),
        ).convert("RGBA")

        # A transparent gradient preserves the full action image while giving
        # the timed verb table just enough contrast to remain readable.
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        top = 744
        for y in range(top, HEIGHT):
            progress = (y - top) / (HEIGHT - top)
            alpha = int(20 + 68 * progress)  # about 8% -> 35% black
            draw.line((0, y, WIDTH, y), fill=(4, 14, 24, alpha), width=1)
        draw.line((54, 770, WIDTH - 54, 770), fill=(145, 211, 231, 72), width=2)
        Image.alpha_composite(image, overlay).convert("RGB").save(output, quality=95, subsampling=0)
        paths.append(output)
    return paths


def make_timeline() -> None:
    PLANNING.mkdir(parents=True, exist_ok=True)
    source_files = action_files()
    payload = {
        "source_song": "https://www.youtube.com/watch?v=c0bh8bZI6BY",
        "audio_duration": AUDIO_END,
        "verb_count": len(VERBS),
        "visual_rule": "One newly generated full-screen action image per verb.",
        "overlay": "Bottom transparent gradient, about 8-35% black.",
        "notes": [
            "The base form understand is omitted in the recording; it is displayed without parentheses and never highlighted.",
            "Past and past-participle read are displayed with /red/; the base form is /riːd/.",
        ],
        "verbs": [],
    }
    for i, row in enumerate(VERBS):
        jp, base, past, pp, start, form_starts = row
        payload["verbs"].append({
            "index": i + 1,
            "image": str(source_files[i].relative_to(HERE)),
            "jp": jp,
            "base": base,
            "past": past,
            "past_participle": pp,
            "start": start,
            "form_starts": list(form_starts),
            "end": VERBS[i + 1][4] if i + 1 < len(VERBS) else AUDIO_END,
        })
    (PLANNING / f"irregular_verbs_{VERSION}_timeline.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def make_concat_sequence(display_files: list[Path]) -> Path:
    TRANSITIONS.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    frame_duration = TRANSITION_DURATION / TRANSITION_FRAMES
    lines: list[str] = []
    for i, frame in enumerate(display_files):
        start = VERBS[i][4]
        end = VERBS[i + 1][4] if i + 1 < len(VERBS) else AUDIO_END
        hold = end - start - (TRANSITION_DURATION if i + 1 < len(VERBS) else 0)
        lines += [f"file '{frame.resolve()}'", f"duration {max(0.1, hold):.6f}"]
        if i + 1 < len(display_files):
            current = Image.open(frame).convert("RGB")
            upcoming = Image.open(display_files[i + 1]).convert("RGB")
            for transition_index in range(1, TRANSITION_FRAMES + 1):
                x = transition_index / (TRANSITION_FRAMES + 1)
                alpha = x * x * (3.0 - 2.0 * x)
                blended = Image.blend(current, upcoming, alpha)
                transition = TRANSITIONS / f"{i + 1:02d}_{transition_index:02d}.jpg"
                blended.save(transition, quality=93, subsampling=0)
                lines += [f"file '{transition.resolve()}'", f"duration {frame_duration:.6f}"]
    lines.append(f"file '{display_files[-1].resolve()}'")
    concat = WORK / "scene_sequence.ffconcat"
    concat.write_text("ffconcat version 1.0\n" + "\n".join(lines) + "\n", encoding="utf-8")
    return concat


def ass_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours}:{minutes:02d}:{secs:05.2f}"


def ass_escape(text: str) -> str:
    return text.replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}")


def make_ass() -> Path:
    CAPTIONS.mkdir(parents=True, exist_ok=True)
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Japanese,Hiragino Sans,56,&H00F8F5ED,&H000000FF,&H70100804,&H30000000,-1,0,0,0,100,100,1,0,1,4,1,5,40,40,0,1
Style: Column,Hiragino Sans,34,&H00D4E7ED,&H000000FF,&H70100804,&H20000000,-1,0,0,0,100,100,1,0,1,3,0,5,40,40,0,1
Style: Form,Hiragino Sans,78,&H00FBFAF5,&H000000FF,&H70100804,&H30000000,-1,0,0,0,100,100,0,0,1,5,1,5,20,20,0,1
Style: Counter,Hiragino Sans,30,&H00C4DFE7,&H000000FF,&H70100804,&H20000000,-1,0,0,0,100,100,1,0,1,3,0,5,20,20,0,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    events: list[str] = []
    end_all = ass_time(AUDIO_END)
    columns = [(430, "原形  BASE"), (960, "過去形  PAST"), (1490, "過去分詞  PAST PARTICIPLE")]
    for x, label in columns:
        events.append(f"Dialogue: 1,0:00:00.00,{end_all},Column,,0,0,0,,{{\\an5\\pos({x},860)}}{label}")
    events.append(f"Dialogue: 1,0:00:00.00,{end_all},Column,,0,0,0,,{{\\an5\\pos(695,960)\\fs52}}→")
    events.append(f"Dialogue: 1,0:00:00.00,{end_all},Column,,0,0,0,,{{\\an5\\pos(1225,960)\\fs52}}→")

    positions = (430, 960, 1490)
    for i, row in enumerate(VERBS):
        jp, base, past, pp, entry_start, form_starts = row
        entry_end = VERBS[i + 1][4] if i + 1 < len(VERBS) else AUDIO_END
        start_s, end_s = ass_time(entry_start), ass_time(entry_end)
        events.append(
            f"Dialogue: 3,{start_s},{end_s},Japanese,,0,0,0,,"
            f"{{\\an4\\pos(78,805)}}{ass_escape(jp)}"
        )
        events.append(
            f"Dialogue: 3,{start_s},{end_s},Counter,,0,0,0,,"
            f"{{\\an6\\pos(1840,808)}}{i + 1:02d} / 55"
        )

        forms = (base, past, pp)
        phase_starts = (entry_start, form_starts[0], form_starts[1], form_starts[2])
        phase_ends = (form_starts[0], form_starts[1], form_starts[2], entry_end)
        active_forms = (-1, 0, 1, 2)
        for phase_start, phase_end, active in zip(phase_starts, phase_ends, active_forms):
            if phase_end <= phase_start:
                continue
            for form_index, (x, value) in enumerate(zip(positions, forms)):
                fs = 54 if len(value) >= 14 else 62 if len(value) >= 11 else 78
                # understand is visible for reference but never highlighted,
                # because the recording starts with understood.
                highlighted = form_index == active and not (i == 33 and form_index == 0)
                if highlighted:
                    tags = f"\\an5\\pos({x},965)\\fs{fs}\\c&H0038E6FF&\\bord6\\fscx108\\fscy108"
                else:
                    tags = f"\\an5\\pos({x},965)\\fs{fs}\\c&H00FBFAF5&\\bord3\\fscx100\\fscy100"
                events.append(
                    f"Dialogue: 2,{ass_time(phase_start)},{ass_time(phase_end)},Form,,0,0,0,,"
                    f"{{{tags}}}{ass_escape(value)}"
                )

    path = CAPTIONS / f"irregular_verbs_{VERSION}.ass"
    path.write_text(header + "\n".join(events) + "\n", encoding="utf-8")
    return path


def build_video(concat: Path, ass: Path) -> Path:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    background = WORK / f"irregular_verbs_{VERSION}_background.mp4"
    final = OUTPUT / f"irregular_verbs_one_action_per_verb_{VERSION}_1080p.mp4"
    run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
        "-vf", f"fps={FPS},format=yuv420p", "-t", f"{AUDIO_END:.6f}",
        "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-movflags", "+faststart", str(background),
    ])
    escaped_ass = str(ass.resolve()).replace("\\", r"\\").replace(":", r"\:").replace("'", r"\'")
    run([
        "ffmpeg", "-y", "-i", str(background), "-i", str(AUDIO),
        "-vf", f"subtitles=filename='{escaped_ass}'", "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2",
        "-t", f"{AUDIO_END:.6f}", "-movflags", "+faststart", str(final),
    ])
    return final


def verify(final: Path) -> None:
    probe = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(final)],
        text=True,
    )
    (OUTPUT / f"irregular_verbs_{VERSION}_ffprobe.json").write_text(probe, encoding="utf-8")
    run(["ffmpeg", "-v", "error", "-i", str(final), "-f", "null", "-"])
    run(["ffmpeg", "-y", "-ss", "3.50", "-i", str(final), "-frames:v", "1", str(OUTPUT / f"irregular_verbs_{VERSION}_thumbnail.png")])
    run([
        "ffmpeg", "-y", "-i", str(final),
        "-vf", "fps=1/10,scale=480:-1,tile=5x2:padding=8:margin=8:color=#18242a",
        "-frames:v", "1", str(OUTPUT / f"irregular_verbs_{VERSION}_contact_sheet.jpg"),
    ])


def main() -> None:
    if not AUDIO.exists():
        raise FileNotFoundError(AUDIO)
    source_files = action_files()
    make_timeline()
    display_files = make_display_frames(source_files)
    concat = make_concat_sequence(display_files)
    ass = make_ass()
    final = build_video(concat, ass)
    verify(final)
    print(f"DONE: {final}")


if __name__ == "__main__":
    main()
