"""Build ASS subtitle file from clean lyrics + line timestamps, then burn
into the 1080p final video using ffmpeg.

- Verse line timings: /tmp/phonics_lines.json (5 lines per verse)
- Intro/outro line timings: derived from Whisper transcript v3
- Lyrics: clean canonical (e.g. 'A! A! A! Aunt Ant!' not 'Eh eh eh ant ant')
"""
from __future__ import annotations
import json, subprocess
from pathlib import Path

VERSE_LYRICS = {
    'A': [
        'A! A! A! Aunt Ant!',
        'What can Aunt Ant do?',
        'Aunt Ant asks a question,',
        'Aunt Ant adds two apples,',
        'Aunt Ant applauds — clap clap clap!',
    ],
    'B': [
        'B! B! B! Baker Bear!',
        'What can Baker Bear do?',
        'Baker Bear bakes the bread,',
        'Baker Bear blows a bubble,',
        'Baker Bear builds it big and tall!',
    ],
    'C': [
        'C! C! C! Cowboy Cat!',
        'What can Cowboy Cat do?',
        'Cowboy Cat catches a cow,',
        'Cowboy Cat climbs the cliff,',
        'Cowboy Cat counts to ten!',
    ],
    'D': [
        'D! D! D! Doctor Dragon!',
        'What can Doctor Dragon do?',
        'Doctor Dragon draws a duck,',
        'Doctor Dragon digs a hole,',
        'Doctor Dragon dives — splash!',
    ],
    'E': [
        'E! E! E! Engineer Egg!',
        'What can Engineer Egg do?',
        'Engineer Egg edits a book,',
        'Engineer Egg enters a room,',
        'Engineer Egg exercises — one, two, three!',
    ],
    'F': [
        'F! F! F! Fisher Frog!',
        'What can Fisher Frog do?',
        'Fisher Frog finds a fly,',
        'Fisher Frog flips a fish,',
        'Fisher Frog flies a kite!',
    ],
    'G': [
        'G! G! G! Guardian Goat!',
        'What can Guardian Goat do?',
        'Guardian Goat grows a flower,',
        'Guardian Goat gives a gift,',
        'Guardian Goat grabs a glove!',
    ],
    'H': [
        'H! H! H! Hiker Hippo!',
        'What can Hiker Hippo do?',
        'Hiker Hippo holds a hat,',
        'Hiker Hippo hugs a friend,',
        'Hiker Hippo hides — peek-a-boo!',
    ],
    'I': [
        'I! I! I! Inventor Ice!',
        'What can Inventor Ice do?',
        'Inventor Ice invents a robot,',
        'Inventor Ice imagines a star,',
        'Inventor Ice imitates a cat — meow!',
    ],
    'J': [
        'J! J! J! Juggler Jellyfish!',
        'What can Juggler Jellyfish do?',
        'Juggler Jellyfish juggles three balls,',
        'Juggler Jellyfish jumps a rope,',
        'Juggler Jellyfish joins the team!',
    ],
    'K': [
        'K! K! K! King Kangaroo!',
        'What can King Kangaroo do?',
        'King Kangaroo kicks a ball,',
        'King Kangaroo keeps a key,',
        'King Kangaroo kisses his queen!',
    ],
    'L': [
        'L! L! L! Librarian Lion!',
        'What can Librarian Lion do?',
        'Librarian Lion lifts a book,',
        'Librarian Lion learns a letter,',
        'Librarian Lion likes the library!',
    ],
    'M': [
        'M! M! M! Magician Mouse!',
        'What can Magician Mouse do?',
        'Magician Mouse makes a hat,',
        'Magician Mouse mixes some milk,',
        'Magician Mouse moves the mat!',
    ],
    'N': [
        'N! N! N! Ninja Nut!',
        'What can Ninja Nut do?',
        'Ninja Nut nibbles a nut,',
        'Ninja Nut names his pet,',
        'Ninja Nut needs a nap!',
    ],
    'O': [
        'O! O! O! Outlaw Octopus!',
        'What can Outlaw Octopus do?',
        'Outlaw Octopus opens an orange,',
        'Outlaw Octopus offers a snack,',
        'Outlaw Octopus orders an omelet!',
    ],
    'P': [
        'P! P! P! Pilot Panda!',
        'What can Pilot Panda do?',
        'Pilot Panda paints a plane,',
        'Pilot Panda pulls a rope,',
        'Pilot Panda packs a parachute!',
    ],
    'Q': [
        'Q! Q! Q! Queen Quiz!',
        'What can Queen Quiz do?',
        'Queen Quiz quizzes the class,',
        'Queen Quiz questions a king,',
        'Queen Quiz quacks like a duck!',
    ],
    'R': [
        'R! R! R! Runner Rabbit!',
        'What can Runner Rabbit do?',
        'Runner Rabbit reads a book,',
        'Runner Rabbit rolls a ball,',
        'Runner Rabbit rides a bike!',
    ],
    'S': [
        'S! S! S! Singer Snake!',
        'What can Singer Snake do?',
        'Singer Snake sings a song,',
        'Singer Snake sees a star,',
        'Singer Snake sips some soup!',
    ],
    'T': [
        'T! T! T! Teacher Tacos!',
        'What can Teacher Tacos do?',
        'Teacher Tacos teaches a class,',
        'Teacher Tacos taps a table,',
        'Teacher Tacos throws a ball!',
    ],
    'U': [
        'U! U! U! Uncle Unicorn!',
        'What can Uncle Unicorn do?',
        'Uncle Unicorn unzips a bag,',
        'Uncle Unicorn unties a knot,',
        'Uncle Unicorn unfolds a map!',
    ],
    'V': [
        'V! V! V! Viking Virus!',
        'What can Viking Virus do?',
        'Viking Virus visits a friend,',
        'Viking Virus vacuums the floor,',
        'Viking Virus vanishes — poof!',
    ],
    'W': [
        'W! W! W! Waiter Wolf!',
        'What can Waiter Wolf do?',
        'Waiter Wolf washes a window,',
        'Waiter Wolf waves his hand,',
        'Waiter Wolf walks a dog!',
    ],
    'X': [
        'X! X! X! Boxer Fox!',
        'What can Boxer Fox do?',
        'Boxer Fox fixes a clock,',
        'Boxer Fox mixes the paint,',
        'Boxer Fox waxes a car!',
    ],
    'Y': [
        'Y! Y! Y! Yoga Yeti!',
        'What can Yoga Yeti do?',
        'Yoga Yeti yells a word,',
        'Yoga Yeti yanks a rope,',
        'Yoga Yeti yawns — so sleepy!',
    ],
    'Z': [
        'Z! Z! Z! Zigzag Zebra!',
        'What can Zigzag Zebra do?',
        'Zigzag Zebra zips a jacket,',
        'Zigzag Zebra zooms around,',
        'Zigzag Zebra zonks — to the ground!',
    ],
}

INTRO_LINES = [
    'Welcome, welcome, come along,',
    '26 friends in one big song!',
    'Wiggle, giggle, clap and shake,',
    "Sing along — what fun we'll make!",
]
OUTRO_LINES = [
    'A to Z, all 26,',
    'Phonics Island friends — what a mix!',
    'Hip hip hooray, jump and play,',
    'We love English every day!',
]


def fmt_ts(t: float) -> str:
    """ASS timestamp: H:MM:SS.cc"""
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t - h*3600 - m*60
    return f"{h}:{m:02d}:{s:05.2f}"


def find_word_idx(words, target_lower: str, start_idx: int) -> int | None:
    for i in range(start_idx, len(words)):
        if words[i]['word'].lower().strip(',.!?-_') == target_lower:
            return i
    return None


def main():
    with open('/tmp/phonics_lines.json') as f:
        lines = json.load(f)
    with open('/tmp/phonics_transcript_v3.json') as f:
        transcript = json.load(f)
    with open('/tmp/phonics_segments_v5.json') as f:
        seg = json.load(f)
    words = transcript['words']

    cues: list[tuple[float, float, str]] = []  # (start, end, text)

    # --- Intro ---
    intro_end = seg['boundaries'][1]
    intro_starts = []
    # 4 lines: "Welcome", "26", "Wiggle", "Sing"
    line_anchors = ['welcome', '26', 'wiggle', 'sing']
    idx_search = 0
    for anchor in line_anchors:
        # find first occurrence of anchor word from idx_search
        found = None
        for i in range(idx_search, len(words)):
            w = words[i]['word'].lower().strip(',.!?-_')
            if w == anchor or w.startswith(anchor):
                found = i; break
        if found:
            intro_starts.append(words[found]['start'])
            idx_search = found + 1
        else:
            intro_starts.append(None)

    # Fallback: if any anchor missing, evenly distribute
    if any(s is None for s in intro_starts):
        N = 4
        for k in range(N):
            if intro_starts[k] is None:
                intro_starts[k] = (intro_end / N) * k
    intro_starts.append(intro_end)
    for i, line in enumerate(INTRO_LINES):
        cues.append((intro_starts[i], intro_starts[i+1], line))

    # --- Verses ---
    for letter, info in lines.items():
        line_times = info['line_times']
        for i in range(5):
            start, end = line_times[i], line_times[i+1]
            cues.append((start, end, VERSE_LYRICS[letter][i]))

    # --- Outro ---
    outro_start = seg['boundaries'][-2]
    outro_end = seg['boundaries'][-1]
    # 4 lines: "A", "Phonics", "Hip", "We"
    line_anchors2 = ['a', 'phonics', 'hip', 'we']
    # Need to start search after the Z verse
    z_end_idx = next(i for i,w in enumerate(words) if w['start'] >= outro_start - 0.5)
    outro_starts = []
    idx_search = z_end_idx
    for anchor in line_anchors2:
        found = None
        for i in range(idx_search, len(words)):
            w = words[i]['word'].lower().strip(',.!?-_')
            if w == anchor:
                found = i; break
        if found:
            outro_starts.append(words[found]['start'])
            idx_search = found + 1
        else:
            outro_starts.append(None)
    if any(s is None for s in outro_starts):
        for k in range(4):
            if outro_starts[k] is None:
                outro_starts[k] = outro_start + (outro_end-outro_start)/4 * k
    outro_starts.append(outro_end)
    for i, line in enumerate(OUTRO_LINES):
        cues.append((outro_starts[i], outro_starts[i+1], line))

    # Sort
    cues.sort()

    # Build ASS file:
    #   Layer 0 (FullLine): whole line in white, no box, displayed full cue duration
    #   Layer 1 (WordBox):  per-word red rounded box at the EXACT screen X of that
    #                       word, displayed only while the word is being sung
    # Word positions computed via PIL with the same font/size that ASS will use.
    from PIL import ImageFont
    FONT_PATH = '/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf'
    FONT_SIZE_PX = 130
    pil_font = ImageFont.truetype(FONT_PATH, FONT_SIZE_PX)

    def text_width_px(s: str) -> int:
        bbox = pil_font.getbbox(s)
        return bbox[2] - bbox[0]

    SPACE_W = text_width_px(' ')
    PLAY_W = 1920
    PLAY_H = 1080
    BASELINE_Y = PLAY_H - 140  # bottom alignment with margin 140

    ass = []
    ass.append('[Script Info]')
    ass.append('ScriptType: v4.00+')
    ass.append('PlayResX: 1920')
    ass.append('PlayResY: 1080')
    ass.append('ScaledBorderAndShadow: yes')
    ass.append('')
    ass.append('[V4+ Styles]')
    ass.append('Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding')
    # FullLine: white text + dark outline, no box (BorderStyle=1)
    ass.append(f'Style: FullLine,Arial Rounded MT Bold,{FONT_SIZE_PX},&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,7,4,2,60,60,140,1')
    # WordBox: white text + red opaque box (BorderStyle=3, OutlineColour = BGR red)
    ass.append(f'Style: WordBox,Arial Rounded MT Bold,{FONT_SIZE_PX},&H00FFFFFF,&H00FFFFFF,&H000027FF,&H80000000,1,0,0,0,100,100,0,0,3,18,2,5,0,0,0,1')
    ass.append('')
    ass.append('[Events]')
    ass.append('Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text')

    def split_words(s: str) -> list[str]:
        import re as _re
        return [t for t in _re.split(r'\s+', s.strip()) if t]

    def whisper_words_in_range(start: float, end: float) -> list[dict]:
        return [w for w in words if w['start'] >= start - 0.05 and w['start'] < end - 0.02]

    def word_x_centers(text_words: list[str]) -> list[tuple[int, int]]:
        """Return list of (center_x, width_px) for each word, given centered alignment."""
        widths = [text_width_px(w) for w in text_words]
        total = sum(widths) + SPACE_W * (len(text_words) - 1)
        left = PLAY_W // 2 - total // 2
        centers = []
        cursor = left
        for i, w in enumerate(text_words):
            cx = cursor + widths[i] // 2
            centers.append((cx, widths[i]))
            cursor += widths[i] + SPACE_W
        return centers

    total_box_cues = 0
    total_line_cues = 0
    OVERHANG = 0.10  # tail visibility after word audio end

    for cstart, cend, text in cues:
        if cend <= cstart: continue
        text_words = split_words(text)
        wsp_words = whisper_words_in_range(cstart, cend)

        # Layer 0: the whole line, full cue duration
        line_safe = text.replace('{','\\{').replace('}','\\}')
        ass.append(f'Dialogue: 0,{fmt_ts(cstart)},{fmt_ts(cend)},FullLine,,0,0,0,,{{\\fad(80,80)}}{line_safe}')
        total_line_cues += 1

        # Layer 1: per-word boxes
        centers = word_x_centers(text_words)
        # Determine word timings: 1:1 if match, else even split across cue
        timings: list[tuple[float, float]] = []
        if len(wsp_words) == len(text_words) and len(text_words) > 0:
            for i, ww in enumerate(wsp_words):
                w_start = ww['start']
                wend_audio = ww.get('end', w_start + 0.30)
                next_start = wsp_words[i+1]['start'] if i+1 < len(wsp_words) else cend
                w_end = min(wend_audio + OVERHANG, next_start)
                timings.append((w_start, w_end))
        else:
            # Fallback even split
            n = max(1, len(text_words))
            per = (cend - cstart) / n
            for i in range(len(text_words)):
                ws = cstart + i * per
                we = ws + per * 0.85  # 85% of slot to give visible gap
                timings.append((ws, we))

        for i, (tok, (w_start, w_end)) in enumerate(zip(text_words, timings)):
            if w_end <= w_start: continue
            cx, _ = centers[i]
            cy = BASELINE_Y - FONT_SIZE_PX // 2 + 10
            safe = tok.replace('{','\\{').replace('}','\\}')
            # \blur3 softens box edges (rounder feel); \fad for transition
            line_text = f'{{\\an5\\pos({cx},{cy})\\blur3\\fad(40,60)}}{safe}'
            ass.append(f'Dialogue: 1,{fmt_ts(w_start)},{fmt_ts(w_end)},WordBox,,0,0,0,,{line_text}')
            total_box_cues += 1

    print(f'  {total_line_cues} line cues + {total_box_cues} word boxes')

    ass_path = Path('/tmp/phonics_subs.ass')
    ass_path.write_text('\n'.join(ass), encoding='utf-8')
    print(f'wrote {len(cues)} cues to {ass_path}')

    # Burn into 1080p
    src = Path('phonics_island_FINAL_1080p.mp4')
    out = Path('phonics_island_FINAL_1080p_subs.mp4')
    if not src.exists():
        print(f'ERR: source video not found: {src}')
        return
    cmd = [
        'ffmpeg','-hide_banner','-loglevel','error','-y',
        '-i', str(src),
        '-vf', f"subtitles={ass_path}",
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
        '-c:a', 'copy',
        str(out),
    ]
    print('burning subtitles via libass...')
    subprocess.run(cmd, check=True)
    print(f'done: {out.absolute()} ({out.stat().st_size//1024//1024} MB)')

if __name__ == '__main__':
    main()
