"""Build the final Phonics Island video.

Pipeline:
1. For each verse, split the audio segment timing equally across the 5 scene
   images (intro + question + 3 actions). Adjust if needed.
2. Use ffmpeg to render each scene as a Ken-Burns clip of the right duration.
3. Concatenate all 28 segments end-to-end.
4. Overlay the original phonics_island.mp3 as the audio track.
"""
from __future__ import annotations
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent
SCENES_ROOT = Path(
    '/Users/masaki/Library/CloudStorage/'
    'GoogleDrive-sarosaro36@gmail.com/マイドライブ/個人用/ClaudeCode/'
    '地学基礎漫画作成/phonics_island_scenes'
)
AUDIO_FULL = ROOT / 'phonics island.mp3'
SEGMENTS_JSON = Path('/tmp/phonics_segments_v2.json')
OUT_DIR = ROOT / 'dist' / 'phonics-video'
OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_CLIPS = ROOT / 'tmp_phonics_clips'
TMP_CLIPS.mkdir(exist_ok=True)

# Map letter → folder
CHAR_FOLDERS = {
    'A':'aunt_ant','B':'baker_bear','C':'cowboy_cat','D':'doctor_dragon',
    'E':'engineer_egg','F':'fisher_frog','G':'guardian_goat','H':'hiker_hippo',
    'I':'inventor_ice','J':'juggler_jellyfish','K':'king_kangaroo',
    'L':'librarian_lion','M':'magician_mouse','N':'ninja_nut',
    'O':'outlaw_octopus','P':'pilot_panda','Q':'queen_quiz','R':'runner_rabbit',
    'S':'singer_snake','T':'teacher_tacos','U':'uncle_unicorn','V':'viking_virus',
    'W':'waiter_wolf','X':'boxer_fox','Y':'yoga_yeti','Z':'zigzag_zebra',
}
SCENE_LABELS = ['intro_call','question','action_1','action_2','action_3']
SCENE_LABELS_AUNT = ['intro_call','question','action_asks','action_adds','action_applauds']


def build_kenburns_clip(image: Path, duration: float, out: Path) -> None:
    """Build a 16:9 1920x1080 video clip from a single image with slow zoom."""
    duration_str = f'{duration:.3f}'
    fps = 30
    total_frames = int(duration * fps) + 1
    # zoompan: slow zoom from 1.0 to 1.05
    zoom_expr = f'zoom+0.0006'  # +0.0006 per frame ≈ +0.018/sec
    vf = (
        f'scale=2560:1440:force_original_aspect_ratio=increase,'
        f'crop=2560:1440,'
        f'zoompan=z=\'min(zoom+0.0006,1.06)\':d={total_frames}:'
        f'x=\'iw/2-(iw/zoom/2)\':y=\'ih/2-(ih/zoom/2)\':s=1920x1080:fps={fps}'
    )
    cmd = [
        'ffmpeg','-hide_banner','-loglevel','error','-y',
        '-loop','1','-i',str(image),
        '-t',duration_str,
        '-vf',vf,
        '-c:v','libx264','-pix_fmt','yuv420p','-r',str(fps),
        '-an',str(out)
    ]
    subprocess.run(cmd, check=True)


def build_verse_segment(letter: str, folder: str, seg_start: float, seg_end: float, out: Path) -> None:
    duration = seg_end - seg_start
    char_dir = SCENES_ROOT / folder
    labels = SCENE_LABELS_AUNT if folder == 'aunt_ant' else SCENE_LABELS
    scene_imgs = []
    for i, label in enumerate(labels, start=1):
        p = char_dir / f'scene_{i:02d}_{label}.png'
        if p.exists():
            scene_imgs.append(p)
    if not scene_imgs:
        raise SystemExit(f'No scene images for {folder}')

    # Equal duration split
    per_scene = duration / len(scene_imgs)
    clip_paths = []
    for i, img in enumerate(scene_imgs, 1):
        clip_out = TMP_CLIPS / f'{letter.lower()}_{folder}_clip{i}.mp4'
        build_kenburns_clip(img, per_scene, clip_out)
        clip_paths.append(clip_out)

    # concat using concat demuxer
    list_file = TMP_CLIPS / f'{letter.lower()}_{folder}_list.txt'
    list_file.write_text('\n'.join(f"file '{p.absolute()}'" for p in clip_paths))
    subprocess.run([
        'ffmpeg','-hide_banner','-loglevel','error','-y',
        '-f','concat','-safe','0','-i',str(list_file),
        '-c','copy',str(out)
    ], check=True)


def build_intro_outro(label: str, seg_start: float, seg_end: float, out: Path) -> None:
    """Intro/outro: simple multi-image montage. Falls back to first character images if no dedicated images yet."""
    duration = seg_end - seg_start
    # Use 4 different characters across the segment as placeholder
    pick = ['aunt_ant','librarian_lion','pilot_panda','zigzag_zebra'] if label=='intro' else ['runner_rabbit','singer_snake','viking_virus','zigzag_zebra']
    imgs = []
    for folder in pick:
        single = SCENES_ROOT / folder / 'scene_01_intro_call.png'
        if not single.exists():
            single = Path('/Users/masaki/Library/CloudStorage/GoogleDrive-sarosaro36@gmail.com/マイドライブ/個人用/ClaudeCode/地学基礎漫画作成/phonics_island') / folder / 'single.png'
        if single.exists():
            imgs.append(single)
    if not imgs:
        raise SystemExit(f'No images for {label}')
    per = duration / len(imgs)
    clips=[]
    for i,img in enumerate(imgs,1):
        c = TMP_CLIPS / f'{label}_clip{i}.mp4'
        build_kenburns_clip(img, per, c)
        clips.append(c)
    list_file = TMP_CLIPS / f'{label}_list.txt'
    list_file.write_text('\n'.join(f"file '{p.absolute()}'" for p in clips))
    subprocess.run([
        'ffmpeg','-hide_banner','-loglevel','error','-y',
        '-f','concat','-safe','0','-i',str(list_file),
        '-c','copy',str(out)
    ], check=True)


def main():
    seg = json.loads(SEGMENTS_JSON.read_text())
    bounds = seg['boundaries']
    labels = seg['labels']

    seg_clips = []
    for i in range(len(bounds)-1):
        start, end = bounds[i], bounds[i+1]
        label = labels[i]
        if label == 'Intro':
            out = TMP_CLIPS / 'seg_00_intro.mp4'
            build_intro_outro('intro', start, end, out)
        elif label == 'Outro':
            out = TMP_CLIPS / 'seg_27_outro.mp4'
            build_intro_outro('outro', start, end, out)
        else:
            letter = label.split(' ',1)[0]
            folder = CHAR_FOLDERS[letter]
            out = TMP_CLIPS / f'seg_{i:02d}_{letter.lower()}_{folder}.mp4'
            build_verse_segment(letter, folder, start, end, out)
        print(f'  built [{i:2d}] {label} ({end-start:.2f}s) → {out.name}')
        seg_clips.append(out)

    # Final concat
    list_file = TMP_CLIPS / 'final_list.txt'
    list_file.write_text('\n'.join(f"file '{p.absolute()}'" for p in seg_clips))
    silent_full = TMP_CLIPS / 'silent_full.mp4'
    subprocess.run([
        'ffmpeg','-hide_banner','-loglevel','error','-y',
        '-f','concat','-safe','0','-i',str(list_file),
        '-c','copy',str(silent_full),
    ], check=True)
    print(f'  silent_full: {silent_full}')

    # Add original audio
    final_out = OUT_DIR / 'phonics_island_final.mp4'
    subprocess.run([
        'ffmpeg','-hide_banner','-loglevel','error','-y',
        '-i',str(silent_full),'-i',str(AUDIO_FULL),
        '-c:v','copy','-c:a','aac','-b:a','192k','-shortest',
        str(final_out),
    ], check=True)
    print(f'\nFINAL: {final_out}')


if __name__ == '__main__':
    main()
