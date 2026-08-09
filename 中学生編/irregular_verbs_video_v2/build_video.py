#!/usr/bin/env python3
"""Build the Funnics Island irregular-verbs song video.

The script keeps each visual scene to one or two verb entries, composites the
existing Funnics character cards over newly generated key art, and creates an
ASS caption track that follows base / past / past-participle timing.
"""

from __future__ import annotations

import json
import math
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DIST_CHARS = ROOT / "dist" / "phonics-chars"
KEY_ART = HERE / "scenes" / "funnics_irregular_verbs_key_art.png"
AUDIO = HERE / "source_audio" / "irregular_verbs_song_v2.mp3"
SCENES_DIR = HERE / "scenes" / "verb_pairs"
TRANSITIONS_DIR = HERE / "work" / "transition_frames"
CAPTIONS_DIR = HERE / "captions"
OUTPUT_DIR = HERE / "output"
PLANNING_DIR = HERE / "planning"
WORK_DIR = HERE / "work"

WIDTH = 1920
HEIGHT = 1080
FPS = 30
AUDIO_END = 101.159979
TRANSITION_DURATION = 0.18
TRANSITION_FRAMES = 6

FONT_REGULAR = Path("/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc")
FONT_BOLD = Path("/System/Library/Fonts/ヒラギノ角ゴシック W7.ttc")


VERBS = [
    # jp, base, past, past participle, entry start, three sung-form starts
    ("切る", "cut", "cut", "cut", 0.000, (1.380, 1.740, 2.080)),
    ("打つ", "hit", "hit", "hit", 2.560, (3.221, 3.581, 3.941)),
    ("置く", "put", "put", "put", 4.640, (5.121, 5.481, 5.821)),
    ("置く・据える", "set", "set", "set", 6.340, (6.981, 7.341, 7.682)),
    ("〜になる", "become", "became", "become", 7.960, (8.300, 8.760, 9.180)),
    ("来る", "come", "came", "come", 9.600, (9.760, 10.060, 10.340)),
    ("走る", "run", "ran", "run", 10.480, (10.782, 11.122, 11.462)),
    ("持ってくる", "bring", "brought", "brought", 11.940, (12.602, 12.983, 13.323)),
    ("建てる", "build", "built", "built", 13.680, (14.060, 14.400, 14.940)),
    ("買う", "buy", "bought", "bought", 15.440, (15.783, 16.360, 16.720)),
    ("つかまえる", "catch", "caught", "caught", 17.220, (17.780, 18.140, 18.740)),
    ("感じる", "feel", "felt", "felt", 19.120, (19.680, 20.060, 20.500)),
    ("見つける", "find", "found", "found", 20.940, (21.500, 21.860, 22.400)),
    ("持っている", "have", "had", "had", 22.820, (23.440, 23.840, 24.340)),
    ("聞こえる", "hear", "heard", "heard", 24.760, (25.360, 25.680, 26.280)),
    ("持ち続ける", "keep", "kept", "kept", 26.680, (27.500, 27.980, 28.300)),
    ("学ぶ", "learn", "learned / learnt", "learned / learnt", 28.660, (29.020, 29.400, 29.900)),
    ("去る", "leave", "left", "left", 30.420, (31.220, 31.760, 32.040)),
    ("失う", "lose", "lost", "lost", 32.280, (32.860, 33.520, 33.820)),
    ("作る", "make", "made", "made", 34.120, (34.920, 35.340, 35.760)),
    ("会う", "meet", "met", "met", 36.000, (36.800, 37.300, 37.620)),
    ("支払う", "pay", "paid", "paid", 37.780, (38.760, 39.080, 39.640)),
    ("読む", "read", "read", "read", 39.720, (40.580, 40.920, 41.320)),
    ("言う", "say", "said", "said", 41.640, (42.128, 42.608, 43.129)),
    ("売る", "sell", "sold", "sold", 43.440, (43.800, 44.269, 44.729)),
    ("送る", "send", "sent", "sent", 45.229, (45.669, 46.109, 46.609)),
    ("座る", "sit", "sat", "sat", 47.069, (47.569, 48.009, 48.470)),
    ("眠る", "sleep", "slept", "slept", 48.950, (49.370, 50.030, 50.470)),
    ("過ごす", "spend", "spent", "spent", 50.850, (51.210, 51.850, 52.350)),
    ("立っている", "stand", "stood", "stood", 53.010, (53.791, 54.171, 54.511)),
    ("教える", "teach", "taught", "taught", 54.871, (55.291, 55.751, 56.111)),
    ("話す・伝える", "tell", "told", "told", 56.451, (56.931, 57.631, 57.991)),
    ("考える", "think", "thought", "thought", 58.332, (59.032, 59.492, 59.852)),
    # The base form is printed in parentheses because it is omitted in the recording.
    ("理解する", "(understand)", "understood", "understood", 60.192, (60.992, 60.992, 61.912)),
    ("勝つ", "win", "won", "won", 62.812, (63.152, 63.753, 64.193)),
    ("始める", "begin", "began", "begun", 64.633, (65.133, 65.493, 65.853)),
    ("こわす", "break", "broke", "broken", 66.193, (66.513, 66.793, 66.993)),
    ("する", "do", "did", "done", 67.473, (67.833, 68.193, 68.414)),
    ("飲む", "drink", "drank", "drunk", 68.674, (68.874, 69.354, 69.814)),
    ("運転する", "drive", "drove", "driven", 70.254, (70.954, 71.234, 71.554)),
    ("食べる", "eat", "ate", "eaten", 72.174, (72.714, 73.174, 73.595)),
    ("得る", "get", "got", "got / gotten", 74.095, (74.395, 74.755, 75.115)),
    ("与える", "give", "gave", "given", 75.835, (76.375, 76.855, 77.215)),
    ("行く", "go", "went", "gone", 77.835, (78.155, 78.696, 79.196)),
    ("知っている", "know", "knew", "known", 79.516, (80.096, 80.616, 80.756)),
    ("昇る", "rise", "rose", "risen", 81.356, (81.796, 82.496, 82.956)),
    ("見える", "see", "saw", "seen", 83.376, (83.877, 84.337, 84.797)),
    ("見せる", "show", "showed", "shown / showed", 85.197, (85.717, 86.197, 86.637)),
    ("歌う", "sing", "sang", "sung", 87.197, (87.617, 88.057, 88.518)),
    ("話す", "speak", "spoke", "spoken", 88.918, (89.398, 89.878, 90.318)),
    ("泳ぐ", "swim", "swam", "swum", 90.818, (91.198, 91.718, 92.198)),
    ("取る", "take", "took", "taken", 92.798, (93.138, 93.719, 94.079)),
    ("目を覚ます", "wake", "woke", "woken", 94.639, (95.599, 96.079, 96.459)),
    ("着ている", "wear", "wore", "worn", 97.019, (97.519, 97.979, 98.419)),
    ("書く", "write", "wrote", "written", 98.880, (99.340, 99.800, 100.240)),
]


# Entry indexes are zero based. Every scene deliberately contains at most two.
SCENE_GROUPS = [
    ((0, 1), ("ninja_nut", "boxer_fox")),
    ((2, 3), ("waiter_wolf", "teacher_tacos")),
    ((4, 5), ("magician_mouse", "uncle_unicorn")),
    ((6, 7), ("runner_rabbit", "waiter_wolf")),
    ((8, 9), ("engineer_egg", "baker_bear")),
    ((10, 11), ("fisher_frog", "doctor_dragon")),
    ((12, 13), ("hiker_hippo", "guardian_goat")),
    ((14, 15), ("singer_snake", "king_kangaroo")),
    ((16, 17), ("librarian_lion", "pilot_panda")),
    ((18, 19), ("outlaw_octopus", "inventor_ice")),
    ((20, 21), ("aunt_ant", "cowboy_cat")),
    ((22, 23), ("librarian_lion", "teacher_tacos")),
    ((24, 25), ("baker_bear", "pilot_panda")),
    ((26, 27), ("yoga_yeti", "doctor_dragon")),
    ((28, 29), ("queen_quiz", "guardian_goat")),
    ((30, 31), ("teacher_tacos", "librarian_lion")),
    ((32, 33), ("inventor_ice", "queen_quiz")),
    ((34,), ("boxer_fox", "queen_quiz")),
    ((35, 36), ("zigzag_zebra", "viking_virus")),
    ((37, 38), ("engineer_egg", "waiter_wolf")),
    ((39, 40), ("pilot_panda", "baker_bear")),
    ((41, 42), ("aunt_ant", "guardian_goat")),
    ((43, 44), ("hiker_hippo", "queen_quiz")),
    ((45, 46), ("runner_rabbit", "pilot_panda")),
    ((47, 48), ("magician_mouse", "singer_snake")),
    ((49, 50), ("teacher_tacos", "fisher_frog")),
    ((51, 52), ("juggler_jellyfish", "doctor_dragon")),
    ((53, 54), ("cowboy_cat", "librarian_lion")),
]


def run(cmd: list[str]) -> None:
    if cmd and cmd[0] == "ffmpeg":
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "warning", *cmd[1:]]
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size, index=0)


def fit_cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    return ImageOps.fit(image.convert("RGB"), size, Image.Resampling.LANCZOS, centering=(0.5, 0.5))


def rounded_card(image: Image.Image, size: tuple[int, int], radius: int = 30) -> Image.Image:
    content = fit_cover(image, size)
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out.paste(content, (0, 0), mask)
    border = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(border).rounded_rectangle(
        (3, 3, size[0] - 4, size[1] - 4), radius=radius, outline=(255, 231, 157, 235), width=7
    )
    return Image.alpha_composite(out, border)


def paste_with_shadow(canvas: Image.Image, card: Image.Image, xy: tuple[int, int]) -> None:
    x, y = xy
    shadow = Image.new("RGBA", card.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        (8, 8, card.width - 1, card.height - 1), radius=32, fill=(2, 13, 24, 185)
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(15))
    canvas.alpha_composite(shadow, (x + 12, y + 16))
    canvas.alpha_composite(card, (x, y))


def centered(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fnt: ImageFont.FreeTypeFont, fill) -> None:
    box = draw.textbbox((0, 0), text, font=fnt)
    draw.text((xy[0] - (box[2] - box[0]) / 2, xy[1] - (box[3] - box[1]) / 2), text, font=fnt, fill=fill)


def category_for(index: int) -> tuple[str, tuple[int, int, int, int]]:
    if index <= 3:
        return "A–A–A　同じ形", (40, 188, 154, 235)
    if index <= 34:
        return "A–B–A / A–B–B　変化を比べよう", (40, 123, 188, 235)
    return "A–B–C　3つの形が変化", (137, 92, 201, 235)


def resolve_character(name: str) -> Path:
    path = DIST_CHARS / f"{name}.png"
    if path.exists():
        return path
    aliases = {"pilot_panda": "pilot_pig"}
    alt = DIST_CHARS / f"{aliases.get(name, 'teacher_tacos')}.png"
    if alt.exists():
        return alt
    return DIST_CHARS / "teacher_tacos.png"


def make_scene_images() -> list[Path]:
    SCENES_DIR.mkdir(parents=True, exist_ok=True)
    base = fit_cover(Image.open(KEY_ART), (WIDTH, HEIGHT)).filter(ImageFilter.GaussianBlur(0.7))
    base = ImageEnhance.Color(base).enhance(0.90).convert("RGBA")
    scene_paths: list[Path] = []
    header_font = font(FONT_BOLD, 42)
    small_font = font(FONT_BOLD, 30)
    pair_font = font(FONT_BOLD, 38)

    for scene_no, (entry_indexes, characters) in enumerate(SCENE_GROUPS, start=1):
        out = SCENES_DIR / f"scene_{scene_no:02d}.jpg"
        if out.exists():
            scene_paths.append(out)
            continue
        canvas = base.copy()
        wash = Image.new("RGBA", canvas.size, (5, 20, 39, 0))
        wdraw = ImageDraw.Draw(wash)
        wdraw.rectangle((0, 0, WIDTH, 115), fill=(4, 22, 41, 205))
        wdraw.rectangle((0, 650, WIDTH, HEIGHT), fill=(3, 19, 36, 226))
        # Light focus through the hosts in the middle; darker corners hold the cards.
        wdraw.rectangle((0, 115, 610, 650), fill=(3, 19, 36, 70))
        wdraw.rectangle((1310, 115, WIDTH, 650), fill=(3, 19, 36, 70))
        canvas = Image.alpha_composite(canvas, wash)
        draw = ImageDraw.Draw(canvas)

        draw.text((64, 33), "IRREGULAR VERB ADVENTURE", font=header_font, fill=(255, 246, 214, 255))
        badge = f"SCENE {scene_no:02d} / {len(SCENE_GROUPS):02d}"
        badge_box = draw.textbbox((0, 0), badge, font=small_font)
        draw.text((WIDTH - 66 - (badge_box[2] - badge_box[0]), 43), badge, font=small_font, fill=(201, 225, 239, 255))

        category, color = category_for(entry_indexes[0])
        draw.rounded_rectangle((650, 132, 1270, 193), radius=28, fill=color, outline=(255, 255, 255, 90), width=2)
        centered(draw, (960, 161), category, small_font, (255, 255, 255, 255))

        pair_text = "  ×  ".join(VERBS[i][1] for i in entry_indexes)
        draw.rounded_rectangle((690, 536, 1230, 603), radius=30, fill=(3, 21, 40, 205), outline=(255, 225, 137, 145), width=3)
        centered(draw, (960, 568), pair_text, pair_font, (255, 231, 143, 255))

        card_size = (500, 281)
        positions = [(62, 208), (1358, 208)]
        for char_name, position in zip(characters, positions):
            image = Image.open(resolve_character(char_name))
            paste_with_shadow(canvas, rounded_card(image, card_size), position)

        # The bottom panel is intentionally blank; the ASS track adds crisp, timed text.
        draw.rounded_rectangle((80, 679, WIDTH - 80, HEIGHT - 35), radius=42, outline=(89, 174, 204, 85), width=3)
        canvas.convert("RGB").save(out, quality=96, subsampling=0)
        scene_paths.append(out)

    return scene_paths


def write_planning_files() -> list[float]:
    PLANNING_DIR.mkdir(parents=True, exist_ok=True)
    starts = [VERBS[group[0][0]][4] for group in SCENE_GROUPS]
    payload = {
        "source": "https://suno.com/s/Ieo5wFRQpaTowu1R",
        "audio_duration": AUDIO_END,
        "verb_count": len(VERBS),
        "scene_count": len(SCENE_GROUPS),
        "rule": "Each visual scene contains one or two verb entries.",
        "verbs": [
            {
                "index": i + 1,
                "jp": row[0],
                "base": row[1],
                "past": row[2],
                "past_participle": row[3],
                "start": row[4],
                "form_starts": list(row[5]),
                "end": VERBS[i + 1][4] if i + 1 < len(VERBS) else AUDIO_END,
            }
            for i, row in enumerate(VERBS)
        ],
        "scenes": [
            {
                "scene": scene_no,
                "entries": [i + 1 for i in indexes],
                "verbs": [VERBS[i][1] for i in indexes],
                "characters": list(characters),
                "start": starts[scene_no - 1],
                "end": starts[scene_no] if scene_no < len(starts) else AUDIO_END,
            }
            for scene_no, (indexes, characters) in enumerate(SCENE_GROUPS, start=1)
        ],
    }
    (PLANNING_DIR / "irregular_verbs_timeline.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return starts


def make_concat_sequence(scene_paths: list[Path], starts: list[float]) -> Path:
    TRANSITIONS_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    frame_duration = TRANSITION_DURATION / TRANSITION_FRAMES
    lines: list[str] = []

    for i, scene_path in enumerate(scene_paths):
        start = starts[i]
        end = starts[i + 1] if i + 1 < len(starts) else AUDIO_END
        if i + 1 < len(scene_paths):
            hold = max(0.1, end - start - TRANSITION_DURATION)
        else:
            hold = end - start
        lines.append(f"file '{scene_path.resolve()}'")
        lines.append(f"duration {hold:.6f}")

        if i + 1 < len(scene_paths):
            current = Image.open(scene_path).convert("RGB")
            upcoming = Image.open(scene_paths[i + 1]).convert("RGB")
            for frame_index in range(1, TRANSITION_FRAMES + 1):
                # Smoothstep gives the fast song a clean but non-mechanical cut.
                x = frame_index / (TRANSITION_FRAMES + 1)
                alpha = x * x * (3.0 - 2.0 * x)
                blended = Image.blend(current, upcoming, alpha)
                frame_path = TRANSITIONS_DIR / f"transition_{i + 1:02d}_{frame_index:02d}.jpg"
                blended.save(frame_path, quality=94, subsampling=0)
                lines.append(f"file '{frame_path.resolve()}'")
                lines.append(f"duration {frame_duration:.6f}")

    # The concat demuxer requires the final file to appear twice for its duration.
    lines.append(f"file '{scene_paths[-1].resolve()}'")
    concat = WORK_DIR / "scene_sequence.ffconcat"
    concat.write_text("ffconcat version 1.0\n" + "\n".join(lines) + "\n", encoding="utf-8")
    return concat


def ass_time(seconds: float) -> str:
    seconds = max(0.0, seconds)
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours}:{minutes:02d}:{secs:05.2f}"


def ass_escape(text: str) -> str:
    return text.replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}")


def build_ass() -> Path:
    CAPTIONS_DIR.mkdir(parents=True, exist_ok=True)
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Japanese,Hiragino Sans,58,&H00F8F5E9,&H000000FF,&H00241608,&H88000000,-1,0,0,0,100,100,1,0,1,4,2,5,40,40,0,1
Style: Column,Hiragino Sans,28,&H00C6E3ED,&H000000FF,&H00241608,&H88000000,-1,0,0,0,100,100,1,0,1,2,0,5,40,40,0,1
Style: Form,Hiragino Sans,72,&H00F9F7EF,&H000000FF,&H00241608,&H88000000,-1,0,0,0,100,100,0,0,1,4,2,5,20,20,0,1
Style: Counter,Hiragino Sans,28,&H00A9D8E7,&H000000FF,&H00241608,&H88000000,-1,0,0,0,100,100,1,0,1,2,0,5,20,20,0,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    events: list[str] = []
    end = ass_time(AUDIO_END)
    columns = [(455, "原形  BASE"), (960, "過去形  PAST"), (1465, "過去分詞  PAST PARTICIPLE")]
    for x, label in columns:
        events.append(f"Dialogue: 1,0:00:00.00,{end},Column,,0,0,0,,{{\\an5\\pos({x},815)}}{label}")
    events.append(f"Dialogue: 1,0:00:00.00,{end},Column,,0,0,0,,{{\\an5\\pos(708,910)\\fs54}}→")
    events.append(f"Dialogue: 1,0:00:00.00,{end},Column,,0,0,0,,{{\\an5\\pos(1212,910)\\fs54}}→")

    x_positions = (455, 960, 1465)
    for i, row in enumerate(VERBS):
        jp, base, past, pp, entry_start, form_starts = row
        entry_end = VERBS[i + 1][4] if i + 1 < len(VERBS) else AUDIO_END
        start_s = ass_time(entry_start)
        end_s = ass_time(entry_end)
        events.append(
            f"Dialogue: 3,{start_s},{end_s},Japanese,,0,0,0,,"
            f"{{\\an5\\pos(960,737)}}{ass_escape(jp)}"
        )
        events.append(
            f"Dialogue: 3,{start_s},{end_s},Counter,,0,0,0,,"
            f"{{\\an6\\pos(1805,744)}}{i + 1:02d} / {len(VERBS):02d}"
        )

        forms = (base, past, pp)
        phase_starts = [entry_start, form_starts[0], form_starts[1], form_starts[2]]
        phase_ends = [form_starts[0], form_starts[1], form_starts[2], entry_end]
        active_indexes = [-1, 0, 1, 2]
        for phase_start, phase_end, active in zip(phase_starts, phase_ends, active_indexes):
            if phase_end <= phase_start:
                continue
            for form_index, (x, value) in enumerate(zip(x_positions, forms)):
                long = len(value) >= 15
                fs = 49 if long else (58 if len(value) >= 11 else 72)
                if form_index == active:
                    tags = f"\\an5\\pos({x},914)\\fs{fs}\\c&H0049E8FF&\\bord7\\fscx112\\fscy112"
                else:
                    tags = f"\\an5\\pos({x},914)\\fs{fs}\\c&H00F9F7EF&\\bord4\\fscx100\\fscy100"
                events.append(
                    f"Dialogue: 2,{ass_time(phase_start)},{ass_time(phase_end)},Form,,0,0,0,,"
                    f"{{{tags}}}{ass_escape(value)}"
                )

    path = CAPTIONS_DIR / "irregular_verbs_bilingual_highlight.ass"
    path.write_text(header + "\n".join(events) + "\n", encoding="utf-8")
    return path


def build_video(concat: Path, ass: Path) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    background = WORK_DIR / "irregular_verbs_background.mp4"
    final = OUTPUT_DIR / "irregular_verbs_funnics_island_v2_1080p.mp4"
    run(
        [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
            "-vf", f"fps={FPS},format=yuv420p", "-t", f"{AUDIO_END:.6f}",
            "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-movflags", "+faststart", str(background),
        ]
    )
    ass_path = str(ass.resolve()).replace("\\", r"\\").replace(":", r"\:").replace("'", r"\'")
    run(
        [
            "ffmpeg", "-y", "-i", str(background), "-i", str(AUDIO),
            "-vf", f"subtitles=filename='{ass_path}'",
            "-map", "0:v:0", "-map", "1:a:0", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2",
            "-t", f"{AUDIO_END:.6f}", "-movflags", "+faststart", str(final),
        ]
    )
    return final


def verify(final: Path) -> None:
    probe = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(final)],
        text=True,
    )
    (OUTPUT_DIR / "irregular_verbs_funnics_island_v2_ffprobe.json").write_text(probe, encoding="utf-8")
    run(["ffmpeg", "-v", "error", "-i", str(final), "-f", "null", "-"])
    run(
        [
            "ffmpeg", "-y", "-ss", "0.35", "-i", str(final), "-frames:v", "1",
            str(OUTPUT_DIR / "irregular_verbs_funnics_island_v2_thumbnail.png"),
        ]
    )
    run(
        [
            "ffmpeg", "-y", "-i", str(final),
            "-vf", "fps=1/10,scale=480:-1,tile=5x2:padding=8:margin=8:color=#071827",
            "-frames:v", "1", str(OUTPUT_DIR / "irregular_verbs_funnics_island_v2_contact_sheet.jpg"),
        ]
    )


def main() -> None:
    for required in (KEY_ART, AUDIO, DIST_CHARS):
        if not required.exists():
            raise FileNotFoundError(required)
    for folder in (SCENES_DIR, TRANSITIONS_DIR, CAPTIONS_DIR, OUTPUT_DIR, PLANNING_DIR, WORK_DIR):
        folder.mkdir(parents=True, exist_ok=True)
    starts = write_planning_files()
    scene_paths = make_scene_images()
    concat = make_concat_sequence(scene_paths, starts)
    ass = build_ass()
    final = build_video(concat, ass)
    verify(final)
    print(f"DONE: {final}")


if __name__ == "__main__":
    main()
