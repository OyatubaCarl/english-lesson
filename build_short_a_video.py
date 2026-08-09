"""Build Aunt Ant Short A music video from 14 scene images + audio."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent
SCENES = Path(
    '/Users/masaki/Library/CloudStorage/'
    'GoogleDrive-sarosaro36@gmail.com/マイドライブ/個人用/ClaudeCode/'
    '地学基礎漫画作成/phonics_island_scenes/aunt_ant_short_a'
)
TMP = ROOT / 'tmp_short_a'
TMP.mkdir(exist_ok=True)
AUDIO = ROOT / 'aunt_ant_short_a.mp3'
OUT = ROOT / 'aunt_ant_short_a_FINAL.mp4'

# Scene timings based on Whisper transcript (124.8s total)
# Format: (image_label, start, end, motion_mode)
TIMELINE = [
    # 1. Intro 前半 (ねえ知ってる…短いアン)
    ('01_intro_aunt_ant',     0.00, 12.40, 'zoom_in_center'),
    # 2. "Cat, Hat, Ant, Bag" 単語列挙パート — シーンを差し込み
    ('02_fat_cat_in_a_hat',   12.40, 13.50, 'zoom_in_center'),  # Cat / Hat
    ('04_sad_ant_at_a_plant', 13.50, 14.20, 'zoom_in_br'),       # Ant
    ('05_black_bag_with_a_flag', 14.20, 14.70, 'zoom_in_center'),# Bag
    # 3. "Fat, Mad, Sad, Black" 形容詞パート — 形容詞 parade
    ('10_parade_adjectives',  14.70, 16.40, 'pan_lr_zoom'),
    # 4. Intro 後半 (全部短いAの音 / じゃあ聞いてみて) — Aunt Ant 戻る
    ('01_intro_aunt_ant',     16.40, 22.20, 'pan_rl_zoom'),
    # 5. Hook 1 — keep Aunt Ant
    ('01_intro_aunt_ant',     22.20, 30.80, 'pan_diag_tl_br'),
    # 3-6. Verse 1 — 4 base scenes (each line repeated 2x in song? actually mostly 1x)
    ('02_fat_cat_in_a_hat',   30.80, 34.18, 'zoom_in_center'),
    ('03_mad_rat_on_a_mat',   34.18, 37.82, 'pan_lr_zoom'),
    ('04_sad_ant_at_a_plant', 37.82, 41.40, 'zoom_in_br'),
    ('05_black_bag_with_a_flag', 41.40, 47.00, 'zoom_out_center'),
    # 7-9. Verse 2 — reverse order (3 scenes)
    ('04_sad_ant_at_a_plant', 47.00, 52.10, 'pan_rl_zoom'),
    ('03_mad_rat_on_a_mat',   52.10, 55.70, 'zoom_in_center'),
    ('02_fat_cat_in_a_hat',   55.70, 60.50, 'pan_diag_tl_br'),
    # 10-13. Verse 3 — adjective shift (4 NEW scenes)
    ('06_mad_cat_in_a_hat',   60.50, 63.32, 'zoom_in_center'),
    ('07_sad_rat_on_a_mat',   63.32, 67.16, 'pan_lr_zoom'),
    ('08_black_ant_at_a_plant', 67.16, 70.56, 'zoom_in_br'),
    ('09_fat_bag_with_a_flag', 70.56, 73.64, 'zoom_out_center'),
    # 14-17. Attribute parade (4 scenes)
    ('10_parade_adjectives',  73.64, 78.50, 'pan_lr_zoom'),
    ('11_parade_subjects',    78.50, 81.86, 'pan_lr_zoom'),
    ('12_parade_prepositions', 81.86, 84.84, 'pan_lr_zoom'),
    ('13_parade_objects',     84.84, 88.44, 'pan_lr_zoom'),
    # 18-21. Bridge (rapid fire — reuse 4 base scenes)
    ('02_fat_cat_in_a_hat',   88.44, 91.14, 'zoom_in_center'),
    ('03_mad_rat_on_a_mat',   91.14, 94.82, 'pan_diag_tl_br'),
    ('04_sad_ant_at_a_plant', 94.82, 99.86, 'zoom_in_br'),
    ('05_black_bag_with_a_flag', 99.86, 102.04, 'zoom_out_center'),
    # 22. Hook 2
    ('14_finale_aunt_ant',    102.04, 109.46, 'zoom_in_center'),
    # 23. Outro (Japanese narration)
    ('14_finale_aunt_ant',    109.46, 116.70, 'pan_diag_tl_br'),
    # 24. Final hook
    ('14_finale_aunt_ant',    116.70, 124.80, 'zoom_out_center'),
]

FPS = 30
XFADE = 0.30


def ken(img: Path, dur: float, out: Path, mode: str):
    n = int(dur * FPS) + 1
    if mode == 'zoom_in_center':
        z = f"min(1.0+on/{n}*0.30, 1.30)"; x = "iw/2-(iw/zoom/2)"; y = "ih/2-(ih/zoom/2)"
    elif mode == 'zoom_out_center':
        z = f"max(1.30-on/{n}*0.30, 1.0)"; x = "iw/2-(iw/zoom/2)"; y = "ih/2-(ih/zoom/2)"
    elif mode == 'pan_diag_tl_br':
        z = "1.20"; x = f"on/{n}*(iw-iw/zoom)"; y = f"on/{n}*(ih-ih/zoom)"
    elif mode == 'pan_rl_zoom':
        z = f"min(1.15+on/{n}*0.10, 1.25)"; x = f"(iw-iw/zoom)*(1-on/{n})"; y = "ih/2-(ih/zoom/2)"
    elif mode == 'pan_lr_zoom':
        z = f"min(1.15+on/{n}*0.10, 1.25)"; x = f"on/{n}*(iw-iw/zoom)"; y = "ih/2-(ih/zoom/2)"
    elif mode == 'zoom_in_br':
        z = f"min(1.0+on/{n}*0.30, 1.30)"; x = "iw-iw/zoom"; y = "ih-ih/zoom"
    else:
        z = "1.0"; x = "0"; y = "0"
    vf = (f"scale=2880:1620:force_original_aspect_ratio=increase,crop=2880:1620,"
          f"zoompan=z='{z}':d={n}:x='{x}':y='{y}':s=1920x1080:fps={FPS}")
    subprocess.run([
        'ffmpeg','-hide_banner','-loglevel','error','-y',
        '-loop','1','-i',str(img),'-t',f'{dur:.3f}','-vf',vf,
        '-c:v','libx264','-pix_fmt','yuv420p','-r',str(FPS),'-an',str(out),
    ], check=True)


XFADE_TYPES = ['fade','slideleft','smoothleft','slideright','smoothright','fade']


def main():
    clips = []
    for i, (label, start, end, mode) in enumerate(TIMELINE):
        img = SCENES / f'{label}.png'
        if not img.exists():
            print(f'MISSING: {img}'); return
        dur = end - start
        # add XFADE buffer to non-last clips
        clip_dur = dur + XFADE if i < len(TIMELINE) - 1 else dur
        out = TMP / f'clip_{i:02d}.mp4'
        ken(img, clip_dur, out, mode)
        clips.append((out, clip_dur))
        print(f'  built clip {i:02d}: {label} ({dur:.2f}s)')

    # xfade chain
    cur = clips[0][0]
    cum = clips[0][1]
    for i in range(1, len(clips)):
        nxt, nd = clips[i]
        out = TMP / f'xf_{i:02d}.mp4'
        offset = cum - XFADE
        subprocess.run([
            'ffmpeg','-hide_banner','-loglevel','error','-y',
            '-i', str(cur), '-i', str(nxt),
            '-filter_complex',
            f'[0:v][1:v]xfade=transition={XFADE_TYPES[i % len(XFADE_TYPES)]}:duration={XFADE}:offset={offset:.3f},format=yuv420p[v]',
            '-map','[v]','-c:v','libx264','-pix_fmt','yuv420p','-r',str(FPS),'-an',str(out),
        ], check=True)
        cum = cum + nd - XFADE
        cur = out
        print(f'  xfade {i:02d}: cum={cum:.2f}s')

    silent_final = TMP / 'silent_final.mp4'
    subprocess.run([
        'ffmpeg','-hide_banner','-loglevel','error','-y',
        '-i', str(cur),
        '-c:v','libx264','-pix_fmt','yuv420p','-r',str(FPS),'-an',str(silent_final),
    ], check=True)

    # overlay audio
    subprocess.run([
        'ffmpeg','-hide_banner','-loglevel','error','-y',
        '-i', str(silent_final), '-i', str(AUDIO),
        '-c:v','copy','-c:a','aac','-b:a','192k','-shortest',
        str(OUT),
    ], check=True)
    print(f'\nFINAL: {OUT.absolute()} ({OUT.stat().st_size//1024//1024} MB)')


if __name__ == '__main__':
    main()
