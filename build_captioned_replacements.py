"""Burn lyric captions into the existing ABC and Aunt Ant videos.

Outputs:
  dist/phonics-video/phonics_island_FINAL_480p_captioned.mp4
  dist/phonics-video/aunt_ant_short_a_480p_captioned.mp4
"""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).parent
SEG_DIR = ROOT / "dist" / "phonics-segments-video"
OUT_DIR = ROOT / "dist" / "phonics-video"

ABC_SRC = OUT_DIR / "phonics_island_FINAL_480p.mp4"
ABC_ASS = OUT_DIR / "phonics_island_FINAL_480p_captioned.ass"
ABC_OUT = OUT_DIR / "phonics_island_FINAL_480p_captioned.mp4"

ANT_SRC = OUT_DIR / "aunt_ant_short_a_480p.mp4"
ANT_ASS = OUT_DIR / "aunt_ant_short_a_480p_captioned.ass"
ANT_OUT = OUT_DIR / "aunt_ant_short_a_480p_captioned.mp4"

PLAY_W = 854
PLAY_H = 480
FONT_EN = "Arial Rounded MT Bold"
FONT_JP = "Hiragino Maru Gothic ProN W4"
FONT_SIZE = 42
FONT_SIZE_JP = 35

ABC_LINES = {
    "A": [
        "A! A! A! Aunt Ant!",
        "What can Aunt Ant do?",
        "Aunt Ant asks a question,",
        "Aunt Ant adds two apples,",
        "Aunt Ant applauds - clap clap clap!",
    ],
    "B": [
        "B! B! B! Baker Bear!",
        "What can Baker Bear do?",
        "Baker Bear bakes the bread,",
        "Baker Bear blows a bubble,",
        "Baker Bear builds it big and tall!",
    ],
    "C": [
        "C! C! C! Cowboy Cat!",
        "What can Cowboy Cat do?",
        "Cowboy Cat catches a cow,",
        "Cowboy Cat climbs the cliff,",
        "Cowboy Cat counts to ten!",
    ],
    "D": [
        "D! D! D! Doctor Dragon!",
        "What can Doctor Dragon do?",
        "Doctor Dragon draws a duck,",
        "Doctor Dragon digs a hole,",
        "Doctor Dragon dives - splash!",
    ],
    "E": [
        "E! E! E! Engineer Egg!",
        "What can Engineer Egg do?",
        "Engineer Egg edits a book,",
        "Engineer Egg enters a room,",
        "Engineer Egg exercises - one, two, three!",
    ],
    "F": [
        "F! F! F! Fisher Frog!",
        "What can Fisher Frog do?",
        "Fisher Frog finds a fly,",
        "Fisher Frog flips a fish,",
        "Fisher Frog flies a kite!",
    ],
    "G": [
        "G! G! G! Guardian Goat!",
        "What can Guardian Goat do?",
        "Guardian Goat grows a flower,",
        "Guardian Goat gives a gift,",
        "Guardian Goat grabs a glove!",
    ],
    "H": [
        "H! H! H! Hiker Hippo!",
        "What can Hiker Hippo do?",
        "Hiker Hippo holds a hat,",
        "Hiker Hippo hugs a friend,",
        "Hiker Hippo hides - peek-a-boo!",
    ],
    "I": [
        "I! I! I! Inventor Ice!",
        "What can Inventor Ice do?",
        "Inventor Ice invents a robot,",
        "Inventor Ice imagines a star,",
        "Inventor Ice imitates a cat - meow!",
    ],
    "J": [
        "J! J! J! Juggler Jellyfish!",
        "What can Juggler Jellyfish do?",
        "Juggler Jellyfish juggles three balls,",
        "Juggler Jellyfish jumps a rope,",
        "Juggler Jellyfish joins the team!",
    ],
    "K": [
        "K! K! K! King Kangaroo!",
        "What can King Kangaroo do?",
        "King Kangaroo kicks a ball,",
        "King Kangaroo keeps a key,",
        "King Kangaroo kisses his queen!",
    ],
    "L": [
        "L! L! L! Librarian Lion!",
        "What can Librarian Lion do?",
        "Librarian Lion lifts a book,",
        "Librarian Lion learns a letter,",
        "Librarian Lion likes the library!",
    ],
    "M": [
        "M! M! M! Magician Mouse!",
        "What can Magician Mouse do?",
        "Magician Mouse makes a hat,",
        "Magician Mouse mixes some milk,",
        "Magician Mouse moves the mat!",
    ],
    "N": [
        "N! N! N! Ninja Nut!",
        "What can Ninja Nut do?",
        "Ninja Nut nibbles a nut,",
        "Ninja Nut names his pet,",
        "Ninja Nut needs a nap!",
    ],
    "O": [
        "O! O! O! Outlaw Octopus!",
        "What can Outlaw Octopus do?",
        "Outlaw Octopus opens an orange,",
        "Outlaw Octopus offers a snack,",
        "Outlaw Octopus orders an omelet!",
    ],
    "P": [
        "P! P! P! Pilot Panda!",
        "What can Pilot Panda do?",
        "Pilot Panda paints a plane,",
        "Pilot Panda pulls a rope,",
        "Pilot Panda packs a parachute!",
    ],
    "Q": [
        "Q! Q! Q! Queen Quiz!",
        "What can Queen Quiz do?",
        "Queen Quiz quizzes the class,",
        "Queen Quiz questions a king,",
        "Queen Quiz quacks like a duck!",
    ],
    "R": [
        "R! R! R! Runner Rabbit!",
        "What can Runner Rabbit do?",
        "Runner Rabbit reads a book,",
        "Runner Rabbit rolls a ball,",
        "Runner Rabbit rides a bike!",
    ],
    "S": [
        "S! S! S! Singer Snake!",
        "What can Singer Snake do?",
        "Singer Snake sings a song,",
        "Singer Snake sees a star,",
        "Singer Snake sips some soup!",
    ],
    "T": [
        "T! T! T! Teacher Tacos!",
        "What can Teacher Tacos do?",
        "Teacher Tacos teaches a class,",
        "Teacher Tacos taps a table,",
        "Teacher Tacos throws a ball!",
    ],
    "U": [
        "U! U! U! Uncle Unicorn!",
        "What can Uncle Unicorn do?",
        "Uncle Unicorn unzips a bag,",
        "Uncle Unicorn unties a knot,",
        "Uncle Unicorn unfolds a map!",
    ],
    "V": [
        "V! V! V! Viking Virus!",
        "What can Viking Virus do?",
        "Viking Virus visits a friend,",
        "Viking Virus vacuums the floor,",
        "Viking Virus vanishes - poof!",
    ],
    "W": [
        "W! W! W! Waiter Wolf!",
        "What can Waiter Wolf do?",
        "Waiter Wolf washes a window,",
        "Waiter Wolf waves his hand,",
        "Waiter Wolf walks a dog!",
    ],
    "X": [
        "X! X! X! Boxer Fox!",
        "What can Boxer Fox do?",
        "Boxer Fox fixes a clock,",
        "Boxer Fox mixes the paint,",
        "Boxer Fox waxes a car!",
    ],
    "Y": [
        "Y! Y! Y! Yoga Yeti!",
        "What can Yoga Yeti do?",
        "Yoga Yeti yells a word,",
        "Yoga Yeti yanks a rope,",
        "Yoga Yeti yawns - so sleepy!",
    ],
    "Z": [
        "Z! Z! Z! Zigzag Zebra!",
        "What can Zigzag Zebra do?",
        "Zigzag Zebra zips a jacket,",
        "Zigzag Zebra zooms around,",
        "Zigzag Zebra zonks - to the ground!",
    ],
}

ABC_INTRO = [
    "Welcome, welcome, come along,",
    "26 friends in one big song!",
    "Wiggle, giggle, clap and shake,",
    "Sing along - what fun we'll make!",
]
ABC_OUTRO = [
    "A to Z, all 26,",
    "Funnics Island friends - what a mix!",
    "Hip hip hooray, jump and play,",
    "We love English every day!",
]

ANT_CUES: list[tuple[float, float, str, str]] = [
    (0.00, 3.60, 'ねえ知ってる？ "Ay" の文字 - ABC の A。', "jp"),
    (3.60, 7.00, "でも、別の読み方もあるんだよ。", "jp"),
    (7.00, 10.60, "Aunt Ant の 短い「あ」。", "jp"),
    (10.60, 14.70, "Cat, hat, ant, bag.", "en"),
    (14.70, 18.20, "Fat, mad, sad, black.", "en"),
    (18.20, 22.20, "ぜんぶ 短い A の音。じゃあ、聞いてみて！", "jp"),
    (22.20, 26.40, "A! A! A! Aunt Ant!", "en"),
    (26.40, 30.80, "Short A! Short A! Aunt Ant!", "en"),
    (30.80, 32.48, "Fat cat in a hat,", "en"),
    (32.48, 34.18, "Fat cat in a hat,", "en"),
    (34.18, 36.00, "Mad rat on a mat,", "en"),
    (36.00, 37.82, "Mad rat on a mat,", "en"),
    (37.82, 39.61, "Sad ant at a plant,", "en"),
    (39.61, 41.40, "Sad ant at a plant,", "en"),
    (41.40, 44.20, "Black bag with a flag!", "en"),
    (44.20, 47.00, "Black bag with a flag!", "en"),
    (47.00, 49.55, "Black bag with a flag,", "en"),
    (49.55, 52.10, "Sad ant at a plant,", "en"),
    (52.10, 55.70, "Mad rat on a mat,", "en"),
    (55.70, 60.50, "Fat cat in a hat!", "en"),
    (60.50, 63.32, "Mad cat in a hat,", "en"),
    (63.32, 67.16, "Sad rat on a mat,", "en"),
    (67.16, 70.56, "Black ant at a plant,", "en"),
    (70.56, 73.64, "Fat bag with a flag!", "en"),
    (73.64, 78.50, "Fat! Fat! Mad! Mad! Sad! Sad! Black! Black!", "en"),
    (78.50, 81.86, "Cat! Cat! Rat! Rat! Ant! Ant! Bag! Bag!", "en"),
    (81.86, 84.84, "In! In! On! On! At! At! With! With!", "en"),
    (84.84, 88.44, "Hat! Hat! Mat! Mat! Plant! Plant! Flag! Flag!", "en"),
    (88.44, 91.14, "Fat-cat-hat! Fat-cat-hat!", "en"),
    (91.14, 94.82, "Mad-rat-mat! Mad-rat-mat!", "en"),
    (94.82, 99.86, "Sad-ant-plant! Sad-ant-plant!", "en"),
    (99.86, 102.04, "Black-bag-flag! Black-bag-flag!", "en"),
    (102.04, 106.00, "A! A! A! Aunt Ant!", "en"),
    (106.00, 109.46, "Short A! Short A! Aunt Ant!", "en"),
    (109.46, 112.40, "これが 短い A の音！", "jp"),
    (112.40, 115.00, "Cat, hat, ant, bag.", "en"),
    (115.00, 116.70, "Fat, mad, sad, black.", "en"),
    (116.70, 120.60, "A! A! A! Aunt Ant!", "en"),
    (120.60, 124.80, "Short A! Short A! Aunt Ant!", "en"),
]


def fmt_ts(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t - h * 3600 - m * 60
    return f"{h}:{m:02d}:{s:05.2f}"


def duration(path: Path) -> float:
    out = subprocess.check_output([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=nk=1:nw=1",
        str(path),
    ], text=True)
    return float(out.strip())


def ass_escape(s: str) -> str:
    return s.replace("{", r"\{").replace("}", r"\}")


def header() -> list[str]:
    return [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {PLAY_W}",
        f"PlayResY: {PLAY_H}",
        "ScaledBorderAndShadow: yes",
        "WrapStyle: 0",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
        "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: English,{FONT_EN},{FONT_SIZE},&H00FFFFFF,&H00FFFFFF,"
        "&H001A1A1A,&H90000000,1,0,0,0,100,100,0,0,1,4,2,2,38,38,38,1",
        f"Style: Japanese,{FONT_JP},{FONT_SIZE_JP},&H00FFFFFF,&H00FFFFFF,"
        "&H001A1A1A,&H90000000,1,0,0,0,100,100,0,0,1,4,2,2,34,34,36,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, "
        "MarginV, Effect, Text",
    ]


def add_even(cues: list[tuple[float, float, str, str]],
             start: float, end: float, lines: list[str],
             lang: str = "en") -> None:
    step = (end - start) / len(lines)
    for i, line in enumerate(lines):
        cues.append((start + i * step, start + (i + 1) * step, line, lang))


def write_ass(path: Path, cues: list[tuple[float, float, str, str]]) -> None:
    ass = header()
    for start, end, text, lang in cues:
        style = "Japanese" if lang == "jp" else "English"
        ass.append(
            f"Dialogue: 0,{fmt_ts(start)},{fmt_ts(end)},{style},,"
            f"0,0,0,,{{\\fad(90,90)}}{ass_escape(text)}"
        )
    path.write_text("\n".join(ass), encoding="utf-8")
    print(f"wrote {path}")


def build_abc_ass() -> None:
    cues: list[tuple[float, float, str, str]] = []
    t = 0.0
    segment_files = sorted(SEG_DIR.glob("*.mp4"))
    for seg in segment_files:
        dur = duration(seg)
        stem = seg.stem
        if stem == "00_intro":
            add_even(cues, t, t + dur, ABC_INTRO, "en")
        elif stem == "27_outro":
            add_even(cues, t, t + dur, ABC_OUTRO, "en")
        else:
            letter = stem.split("_", 2)[1].upper()
            add_even(cues, t, t + dur, ABC_LINES[letter], "en")
        t += dur
    write_ass(ABC_ASS, cues)


def burn(src: Path, ass: Path, out: Path) -> None:
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(src),
        "-vf", f"subtitles={ass}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "copy",
        str(out),
    ], check=True)
    print(f"done: {out} ({out.stat().st_size // 1024 // 1024} MB)")


def main() -> None:
    build_abc_ass()
    write_ass(ANT_ASS, ANT_CUES)
    burn(ABC_SRC, ABC_ASS, ABC_OUT)
    burn(ANT_SRC, ANT_ASS, ANT_OUT)


if __name__ == "__main__":
    main()
