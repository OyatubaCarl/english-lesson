"""Build Baker Bear & Magic E (Long A) music video.

Pipeline mirrors build_short_a_video.py:
1. Per-scene Ken Burns clip with chosen motion mode.
2. Pairwise xfade chain.
3. Mux original audio.

Whisper-derived TIMELINE (audio total = 213.56s).
"""
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent
SCENES = ROOT / "phonics-songs" / "baker_bear_long_a"
TMP = ROOT / "tmp_long_a"
TMP.mkdir(exist_ok=True)
AUDIO = ROOT / "baker_bear_long_a.mp3"
OUT = ROOT / "baker_bear_long_a_FINAL.mp4"

# Each tuple: (scene_label, start, end, motion_mode)
TIMELINE = [
    # ── Intro (0:00–30:00) ──────────────────────────────────────
    # 0.00 – Baker Bear bakes cakes (chant intro)
    ('01_baking_cakes',           0.00,  12.00, 'zoom_in_center'),
    # JP narration "アント Aは「あ」、bake の A はなぜ？"
    ('02_pondering_question',    12.00,  30.00, 'pan_diag_tl_br'),
    # ── 30:00–36:94 picked up mysterious E ─────────────────────
    ('03_finding_magic_e',       30.00,  36.94, 'zoom_in_center'),
    # ── 36:94–51:12 Hook 1 ─────────────────────────────────────
    ('06_wizard_pose',           36.94,  51.12, 'pan_lr_zoom'),
    # ── 51:12–58:50 Cap → cape (surprised) ─────────────────────
    ('04_first_transform_surprised', 51.12, 58.50, 'zoom_in_center'),
    # ── 58:50–64:90 Can → cane ─────────────────────────────────
    ('04b_can_to_cane',          58.50,  64.90, 'zoom_in_center'),
    # ── 64:90–78:94 Hook 2 ─────────────────────────────────────
    ('06_wizard_pose',           64.90,  78.94, 'pan_rl_zoom'),
    # ── 78:94–85:86 Mat → mate (enjoying) ──────────────────────
    ('05_enjoying_mat_to_mate',  78.94,  85.86, 'zoom_in_center'),
    # ── 85:86–92:52 Plan → plane ───────────────────────────────
    ('06b_plan_to_plane',        85.86,  92.52, 'pan_diag_tl_br'),
    # ── 92:52–99:28 Slat → slate ───────────────────────────────
    ('07b_slat_to_slate',        92.52,  99.28, 'zoom_out_center'),
    # ── 99:38–105:96 Engineer Egg arrives ──────────────────────
    ('08_engineer_egg_arrives',  99.28, 105.96, 'pan_lr_zoom'),
    # ── 106:10–111:14 picks up the E ───────────────────────────
    ('09_engineer_egg_picks_up_e', 105.96, 112.14, 'zoom_in_center'),
    # ── 112:14–127:32 「うしろにeが…ay」narration → dancing ─────
    ('10_dancing_together_01',   112.14, 127.32, 'pan_lr_zoom'),
    # ── 128:14–141:24 Mini hook (continue dancing) ─────────────
    ('11_dancing_together_02',   127.32, 142.00, 'pan_diag_tl_br'),
    # ── 142:00–145:22 Brave mate at the gate ───────────────────
    ('12_brave_mate_at_the_gate', 142.00, 146.04, 'zoom_in_center'),
    # ── 146:04–148:66 Pale cane on a plate ─────────────────────
    ('13_pale_cane_on_a_plate',  146.04, 148.66, 'pan_rl_zoom'),
    # ── 148:66–152:16 Late plane in the rain ───────────────────
    ('14_late_plane_in_the_rain', 148.66, 152.16, 'pan_diag_tl_br'),
    # ── 152:16–155:54 Safe cape on a slate ─────────────────────
    ('15_safe_cape_on_a_slate',  152.16, 155.54, 'zoom_in_center'),
    # ── 155:54–168:22 Hook 3 ───────────────────────────────────
    ('06_wizard_pose',           155.54, 169.22, 'pan_lr_zoom'),
    # ── 169:22–181:46 Word parade (bridge) ─────────────────────
    ('16_word_parade',           169.22, 181.46, 'pan_lr_zoom'),
    # ── 181:46–213:56 Final hook + outro ───────────────────────
    ('17_finale_dancing',        181.46, 213.56, 'zoom_in_center'),
]

FPS = 30
XFADE = 0.30
SIZE_W, SIZE_H = 1920, 1080


def ken(img: Path, dur: float, out: Path, mode: str) -> None:
    n = int(dur * FPS) + 1
    if mode == 'zoom_in_center':
        z = f"min(1.0+on/{n}*0.30, 1.30)"
        x = "iw/2-(iw/zoom/2)"; y = "ih/2-(ih/zoom/2)"
    elif mode == 'zoom_out_center':
        z = f"max(1.30-on/{n}*0.30, 1.0)"
        x = "iw/2-(iw/zoom/2)"; y = "ih/2-(ih/zoom/2)"
    elif mode == 'pan_diag_tl_br':
        z = "1.20"
        x = f"on/{n}*(iw-iw/zoom)"; y = f"on/{n}*(ih-ih/zoom)"
    elif mode == 'pan_rl_zoom':
        z = f"min(1.15+on/{n}*0.10, 1.25)"
        x = f"(iw-iw/zoom)*(1-on/{n})"; y = "ih/2-(ih/zoom/2)"
    elif mode == 'pan_lr_zoom':
        z = f"min(1.15+on/{n}*0.10, 1.25)"
        x = f"on/{n}*(iw-iw/zoom)"; y = "ih/2-(ih/zoom/2)"
    elif mode == 'zoom_in_br':
        z = f"min(1.0+on/{n}*0.30, 1.30)"
        x = "iw-iw/zoom"; y = "ih-ih/zoom"
    else:
        z = "1.0"; x = "0"; y = "0"

    vf = (
        f"scale={SIZE_W*1.5:.0f}:{SIZE_H*1.5:.0f}:force_original_aspect_ratio=increase,"
        f"crop={SIZE_W*1.5:.0f}:{SIZE_H*1.5:.0f},"
        f"zoompan=z='{z}':d={n}:x='{x}':y='{y}':s={SIZE_W}x{SIZE_H}:fps={FPS}"
    )
    subprocess.run([
        'ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
        '-loop', '1', '-i', str(img),
        '-t', f'{dur:.3f}', '-vf', vf,
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-r', str(FPS), '-an', str(out),
    ], check=True)


XFADE_TYPES = ['fade', 'slideleft', 'smoothleft',
               'slideright', 'smoothright', 'fade']


def main() -> None:
    clips = []
    for i, (label, start, end, mode) in enumerate(TIMELINE):
        img = SCENES / f'{label}.png'
        if not img.exists():
            print(f'MISSING: {img}')
            return
        dur = end - start
        clip_dur = dur + XFADE if i < len(TIMELINE) - 1 else dur
        out = TMP / f'clip_{i:02d}.mp4'
        ken(img, clip_dur, out, mode)
        clips.append((out, clip_dur))
        print(f'  built clip {i:02d}: {label} ({dur:.2f}s, mode={mode})')

    # xfade chain
    cur = clips[0][0]
    cum = clips[0][1]
    for i in range(1, len(clips)):
        nxt, nd = clips[i]
        out = TMP / f'xf_{i:02d}.mp4'
        offset = cum - XFADE
        subprocess.run([
            'ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
            '-i', str(cur), '-i', str(nxt),
            '-filter_complex',
            (f'[0:v][1:v]xfade='
             f'transition={XFADE_TYPES[i % len(XFADE_TYPES)]}:'
             f'duration={XFADE}:offset={offset:.3f},format=yuv420p[v]'),
            '-map', '[v]',
            '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
            '-r', str(FPS), '-an', str(out),
        ], check=True)
        cum = cum + nd - XFADE
        cur = out
        print(f'  xfade {i:02d}: cum={cum:.2f}s')

    silent_final = TMP / 'silent_final.mp4'
    subprocess.run([
        'ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
        '-i', str(cur),
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-r', str(FPS), '-an', str(silent_final),
    ], check=True)

    subprocess.run([
        'ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
        '-i', str(silent_final), '-i', str(AUDIO),
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest',
        str(OUT),
    ], check=True)
    size_mb = OUT.stat().st_size // 1024 // 1024
    print(f'\nFINAL: {OUT.name} ({size_mb} MB)')


if __name__ == '__main__':
    main()
