"""Build v5-style motion videos for ALL 26 character verses.

Reads:
- /tmp/phonics_lines.json (5-line boundaries per verse)
- 地学基礎漫画作成/phonics_island_scenes/{folder}/scene_*.png (5 images per char)

Outputs:
- dist/phonics-segments-video/{NN}_{letter}_{folder}.mp4
"""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).parent
SCENES_ROOT = Path(
    '/Users/masaki/Library/CloudStorage/'
    'GoogleDrive-sarosaro36@gmail.com/マイドライブ/個人用/ClaudeCode/'
    '地学基礎漫画作成/phonics_island_scenes'
)
OUT_DIR = ROOT / 'dist' / 'phonics-segments-video'
OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP = ROOT / 'tmp_phonics_clips'
TMP.mkdir(exist_ok=True)

CHAR_FOLDERS = {
    'A':'aunt_ant','B':'baker_bear','C':'cowboy_cat','D':'doctor_dragon',
    'E':'engineer_egg','F':'fisher_frog','G':'guardian_goat','H':'hiker_hippo',
    'I':'inventor_ice','J':'juggler_jellyfish','K':'king_kangaroo',
    'L':'librarian_lion','M':'magician_mouse','N':'ninja_nut',
    'O':'outlaw_octopus','P':'pilot_panda','Q':'queen_quiz','R':'runner_rabbit',
    'S':'singer_snake','T':'teacher_tacos','U':'uncle_unicorn','V':'viking_virus',
    'W':'waiter_wolf','X':'boxer_fox','Y':'yoga_yeti','Z':'zigzag_zebra',
}

# scene labels: A uses different labels (action_asks/_adds/_applauds)
def labels_for(folder: str) -> list[str]:
    if folder == 'aunt_ant':
        return ['intro_call','question','action_asks','action_adds','action_applauds']
    return ['intro_call','question','action_1','action_2','action_3']

# Motion modes per scene (rotated)
MODES_BY_SCENE = [
    'zoom_in_center',
    'pan_diag_tl_br',
    'zoom_out_center',
    'pan_rl_zoom',
    'zoom_in_br',
]
XFADE_TYPES = ['fade','slideleft','smoothleft','slideright','fade']
FPS = 30
XFADE_DUR = 0.30


def ken_burns(img: Path, dur: float, out: Path, mode: str):
    n = int(dur * FPS) + 1
    if mode == 'zoom_in_center':
        z = f"min(1.0+on/{n}*0.30, 1.30)"; x = "iw/2-(iw/zoom/2)"; y = "ih/2-(ih/zoom/2)"
    elif mode == 'zoom_out_center':
        z = f"max(1.30-on/{n}*0.30, 1.0)"; x = "iw/2-(iw/zoom/2)"; y = "ih/2-(ih/zoom/2)"
    elif mode == 'pan_diag_tl_br':
        z = "1.20"; x = f"on/{n}*(iw-iw/zoom)"; y = f"on/{n}*(ih-ih/zoom)"
    elif mode == 'pan_rl_zoom':
        z = f"min(1.15+on/{n}*0.10, 1.25)"; x = f"(iw-iw/zoom)*(1-on/{n})"; y = "ih/2-(ih/zoom/2)"
    elif mode == 'zoom_in_br':
        z = f"min(1.0+on/{n}*0.30, 1.30)"; x = "iw-iw/zoom"; y = "ih-ih/zoom"
    elif mode == 'pan_lr_zoom':
        z = f"min(1.15+on/{n}*0.10, 1.25)"; x = f"on/{n}*(iw-iw/zoom)"; y = "ih/2-(ih/zoom/2)"
    elif mode == 'pan_diag_br_tl':
        z = "1.20"; x = f"(iw-iw/zoom)*(1-on/{n})"; y = f"(ih-ih/zoom)*(1-on/{n})"
    elif mode == 'zoom_in_tl':
        z = f"min(1.0+on/{n}*0.30, 1.30)"; x = "0"; y = "0"
    else:
        z = f"min(1.0+on/{n}*0.20, 1.20)"; x = "iw/2-(iw/zoom/2)"; y = "ih/2-(ih/zoom/2)"
    vf = (
        f"scale=2880:1620:force_original_aspect_ratio=increase,crop=2880:1620,"
        f"zoompan=z='{z}':d={n}:x='{x}':y='{y}':s=1920x1080:fps={FPS}"
    )
    subprocess.run([
        'ffmpeg','-hide_banner','-loglevel','error','-y',
        '-loop','1','-i',str(img),'-t',f'{dur:.3f}','-vf',vf,
        '-c:v','libx264','-pix_fmt','yuv420p','-r',str(FPS),'-an',str(out),
    ], check=True)


def build_verse(letter: str, folder: str, line_times: list[float]) -> Path:
    char_dir = SCENES_ROOT / folder
    labels = labels_for(folder)
    scene_imgs = [char_dir / f"scene_{i+1:02d}_{labels[i]}.png" for i in range(5)]
    if not all(p.exists() for p in scene_imgs):
        missing = [p for p in scene_imgs if not p.exists()]
        raise SystemExit(f'{letter}: missing scenes: {missing}')

    # Per-clip durations: each non-last + XFADE so xfade cancels back
    durations = []
    for i in range(5):
        base = line_times[i+1] - line_times[i]
        durations.append(base + XFADE_DUR if i < 4 else base)

    clips = []
    for i, (img, dur) in enumerate(zip(scene_imgs, durations)):
        mode = MODES_BY_SCENE[i % len(MODES_BY_SCENE)]
        out = TMP / f'{letter.lower()}_{folder}_clip{i}.mp4'
        ken_burns(img, dur, out, mode)
        clips.append((out, dur))

    # xfade chain
    cur = clips[0][0]
    cum = clips[0][1]
    for i in range(1, len(clips)):
        nxt, nxt_d = clips[i]
        out = TMP / f'{letter.lower()}_{folder}_xf{i}.mp4'
        offset = cum - XFADE_DUR
        subprocess.run([
            'ffmpeg','-hide_banner','-loglevel','error','-y',
            '-i', str(cur), '-i', str(nxt),
            '-filter_complex',
            f'[0:v][1:v]xfade=transition={XFADE_TYPES[i]}:duration={XFADE_DUR}:offset={offset:.3f},format=yuv420p[v]',
            '-map','[v]','-c:v','libx264','-pix_fmt','yuv420p','-r',str(FPS),'-an',str(out),
        ], check=True)
        cum = cum + nxt_d - XFADE_DUR
        cur = out

    # ordinal index in track (A=01, B=02, ..., Z=26)
    ord_n = ord(letter) - ord('A') + 1
    final_out = OUT_DIR / f'{ord_n:02d}_{letter.lower()}_{folder}.mp4'
    # encode final to clean container
    subprocess.run([
        'ffmpeg','-hide_banner','-loglevel','error','-y',
        '-i', str(cur),
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-r', str(FPS),
        '-an', str(final_out),
    ], check=True)
    return final_out


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    with open('/tmp/phonics_lines.json') as f:
        lines = json.load(f)

    for letter, folder in CHAR_FOLDERS.items():
        if only and letter != only.upper():
            continue
        info = lines.get(letter)
        if not info:
            print(f'{letter}: no line info, skip')
            continue
        scenes_dir = SCENES_ROOT / folder
        if not scenes_dir.exists() or len(list(scenes_dir.glob('scene_*.png'))) < 5:
            print(f'{letter} {folder}: scenes not ready, skip')
            continue
        print(f'\n=== {letter} {folder} ===')
        try:
            out = build_verse(letter, folder, info['line_times'])
            sz = out.stat().st_size // 1024
            print(f'  built: {out.name} ({sz} KB)')
        except Exception as e:
            print(f'  FAIL: {e}')


if __name__ == '__main__':
    main()
