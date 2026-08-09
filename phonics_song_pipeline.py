#!/usr/bin/env python3
"""End-to-end phonics song video pipeline.

Steps performed:
  1. Download mp3 from a Suno share URL
  2. Whisper word-level transcription (OpenAI API)
  3. Build motion video from a TIMELINE of (scene_label, start, end, mode)
     using Ken Burns + xfade — images live in `phonics-songs/<slug>/`
  4. Compress to 480p
  5. Upload compressed mp4 to a public host (tmpfiles.org)
  6. Submit URL to Revid `caption-video` workflow (captions only, cheap)

USAGE
-----
This is the canonical recipe. Each new song should:
  - drop a TIMELINE list at the top
  - point SLUG / SUNO_SID / NAME at the right places
  - run with `python3 phonics_song_pipeline.py`

REQUIREMENTS
------------
  - .env: OPENAI_API_KEY, REVID_API_KEY
  - venv with: openai, python-dotenv, requests
  - ffmpeg / ffprobe on PATH
  - PNG scenes named like `01_scene.png`, `02_scene.png` ...
    in phonics-songs/<SLUG>/

REUSABLE FUNCTIONS
------------------
download_suno_audio(suno_sid, out_mp3)
whisper_transcribe(mp3_path, out_json)
build_motion_video(timeline, scenes_dir, audio_path, out_mp4, tmp_dir)
compress_to_480p(in_mp4, out_mp4)
upload_to_tmpfiles(mp4_path) -> str
revid_caption_only(public_url, project_name) -> str (pid)
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).parent
ENV_PATH = ROOT / ".env"


# ── Config helpers ────────────────────────────────────────────────
def _env(key: str) -> str:
    text = ENV_PATH.read_text()
    m = re.search(rf'{key}="?([^"\n]+)"?', text)
    if not m:
        raise RuntimeError(f"{key} missing from .env")
    return m.group(1)


# ── Step 1: Suno download ─────────────────────────────────────────
def download_suno_audio(suno_sid: str, out_mp3: Path) -> None:
    """Download mp3 from Suno share URL via og:image UUID pattern."""
    UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    req = urllib.request.Request(
        f"https://suno.com/s/{suno_sid}", headers={"User-Agent": UA}
    )
    html = urllib.request.urlopen(req, timeout=20).read().decode(errors="ignore")
    m = re.search(
        r'og:image"\s+content="https://[^"]*image_large_'
        r'([0-9a-f-]{36})\.jpe?g"',
        html,
    )
    if not m:
        raise RuntimeError(f"Could not extract Suno UUID from {suno_sid}")
    uuid = m.group(1)
    url = f"https://cdn1.suno.ai/{uuid}.mp3"
    print(f"  Suno UUID: {uuid}")
    with urllib.request.urlopen(url, timeout=120) as r:
        data = r.read()
    out_mp3.write_bytes(data)
    print(f"  saved {out_mp3.name} ({len(data) // 1024} KB)")


# ── Step 2: Whisper transcription ─────────────────────────────────
def whisper_transcribe(mp3_path: Path, out_json: Path) -> dict:
    """OpenAI Whisper word-level timestamps."""
    from dotenv import load_dotenv  # noqa: PLC0415
    from openai import OpenAI       # noqa: PLC0415

    load_dotenv()
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    with mp3_path.open("rb") as f:
        resp = client.audio.transcriptions.create(
            file=f,
            model="whisper-1",
            response_format="verbose_json",
            timestamp_granularities=["word", "segment"],
            language="en",
        )
    data = resp.model_dump()
    out_json.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    print(f"  {out_json.name}: {len(data.get('words', []))} words, "
          f"{len(data.get('segments', []))} segments")
    return data


# ── Step 3: Motion video build ────────────────────────────────────
FPS = 30
XFADE = 0.30
SIZE_W, SIZE_H = 1920, 1080
XFADE_TYPES = ['fade', 'slideleft', 'smoothleft',
               'slideright', 'smoothright', 'fade']


def _ken_burns(img: Path, dur: float, out: Path, mode: str) -> None:
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
    vf = (
        f"scale={int(SIZE_W*1.5)}:{int(SIZE_H*1.5)}:force_original_aspect_ratio=increase,"
        f"crop={int(SIZE_W*1.5)}:{int(SIZE_H*1.5)},"
        f"zoompan=z='{z}':d={n}:x='{x}':y='{y}':s={SIZE_W}x{SIZE_H}:fps={FPS}"
    )
    subprocess.run([
        'ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
        '-loop', '1', '-i', str(img),
        '-t', f'{dur:.3f}', '-vf', vf,
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-r', str(FPS), '-an', str(out),
    ], check=True)


def build_motion_video(
    timeline: Iterable[tuple[str, float, float, str]],
    scenes_dir: Path,
    audio_path: Path,
    out_mp4: Path,
    tmp_dir: Path,
) -> None:
    tmp_dir.mkdir(parents=True, exist_ok=True)
    timeline = list(timeline)
    clips: list[tuple[Path, float]] = []
    for i, (label, start, end, mode) in enumerate(timeline):
        img = scenes_dir / f"{label}.png"
        if not img.exists():
            raise FileNotFoundError(img)
        dur = end - start
        clip_dur = dur + XFADE if i < len(timeline) - 1 else dur
        out = tmp_dir / f"clip_{i:02d}.mp4"
        _ken_burns(img, clip_dur, out, mode)
        clips.append((out, clip_dur))
        print(f"  clip {i:02d}: {label} ({dur:.2f}s {mode})")

    cur, cum = clips[0]
    for i in range(1, len(clips)):
        nxt, nd = clips[i]
        out = tmp_dir / f"xf_{i:02d}.mp4"
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
        print(f"  xfade {i:02d}: cum={cum:.2f}s")

    silent_final = tmp_dir / "silent_final.mp4"
    subprocess.run([
        'ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
        '-i', str(cur),
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-r', str(FPS), '-an', str(silent_final),
    ], check=True)
    subprocess.run([
        'ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
        '-i', str(silent_final), '-i', str(audio_path),
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest',
        str(out_mp4),
    ], check=True)
    print(f"  final: {out_mp4.name} "
          f"({out_mp4.stat().st_size // 1024 // 1024} MB)")


# ── Step 4: Compress to 480p ──────────────────────────────────────
def compress_to_480p(in_mp4: Path, out_mp4: Path, crf: int = 26) -> None:
    subprocess.run([
        'ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
        '-i', str(in_mp4), '-vf', 'scale=854:480',
        '-c:v', 'libx264', '-preset', 'slow', '-crf', str(crf),
        '-c:a', 'aac', '-b:a', '96k',
        '-movflags', '+faststart', str(out_mp4),
    ], check=True)
    print(f"  480p: {out_mp4.name} "
          f"({out_mp4.stat().st_size // 1024 // 1024} MB)")


# ── Step 5: Public-host upload ────────────────────────────────────
def upload_to_tmpfiles(mp4_path: Path) -> str:
    """Returns direct-download URL (https://tmpfiles.org/dl/<id>/<file>).

    NOTE: tmpfiles.org URLs expire in ~60 minutes — chain into Revid
    submission immediately after this returns.
    """
    out = subprocess.run(
        ['curl', '-s', '-F', f'file=@{mp4_path}',
         'https://tmpfiles.org/api/v1/upload'],
        check=True, capture_output=True, text=True,
    ).stdout
    j = json.loads(out)
    raw = j["data"]["url"]                       # http://tmpfiles.org/<id>/<f>
    # convert to direct-download form
    direct = raw.replace("http://", "https://").replace(
        "tmpfiles.org/", "tmpfiles.org/dl/"
    )
    print(f"  uploaded → {direct}")
    return direct


# ── Step 6: Revid caption-video ───────────────────────────────────
def revid_caption_only(public_url: str, project_name: str) -> str:
    api_key = _env("REVID_API_KEY")
    hdr = {
        "Content-Type": "application/json",
        "key": api_key,
        "User-Agent": (
            "Mozilla/5.0 (Macintosh) AppleWebKit/605.1.15 "
            "(KHTML, like Gecko) Version/17.0 Safari/605.1.15"
        ),
        "Accept": "application/json",
    }
    payload = {
        "workflow": "caption-video",
        "source": {"url": public_url},
        "captions": {
            "enabled": True,
            "preset": "Wrap 1",
            "position": "bottom",
            "autoCrop": False,
        },
        "options": {"hasToGenerateCover": False},
        "metadata": {"title": project_name, "name": project_name,
                     "projectName": project_name},
        "aspectRatio": "16 / 9",
    }

    def _req(url: str, body: dict | None = None) -> dict | str:
        data = json.dumps(body).encode("utf-8") if body else None
        req = urllib.request.Request(
            url, data=data, headers=hdr,
            method="POST" if body else "GET",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            return {"error": e.read().decode(), "code": e.code}

    print(f"Submitting Revid caption-video: {project_name}")
    body = _req("https://www.revid.ai/api/public/v3/render", payload)
    pid = body.get("pid") if isinstance(body, dict) else None
    if not pid:
        raise RuntimeError(f"Revid render failed: {body}")
    print(f"  pid={pid}")
    start = time.time()
    while True:
        time.sleep(15)
        st_body = _req(
            f"https://www.revid.ai/api/public/v3/status?pid={pid}"
        )
        st = st_body.get("status") if isinstance(st_body, dict) else None
        print(f"  [{int(time.time() - start):4d}s] status={st}")
        if st == "ready":
            break
        if st in ("failed", "error"):
            raise RuntimeError(f"Revid build failed: {st_body}")

    rename = {"pid": pid, "name": project_name,
              "projectName": project_name, "title": project_name}
    _req("https://www.revid.ai/api/public/v2/rename-project", rename)
    time.sleep(3)
    _req("https://www.revid.ai/api/public/v2/rename-project", rename)
    print(f"  https://www.revid.ai/projects/{pid}")
    return pid


# ── Convenience: end-to-end driver ────────────────────────────────
def run_pipeline(
    *,
    slug: str,                  # e.g. "baker_bear_long_a"
    suno_sid: str,              # e.g. "pbgdUBUJURWbujp1"
    project_name: str,          # Revid project name
    timeline: Iterable[tuple[str, float, float, str]],
    skip_existing: bool = True,
) -> dict[str, str]:
    """Run the full pipeline. Returns paths/URLs/pids."""
    mp3 = ROOT / f"{slug}.mp3"
    transcript = ROOT / f"{slug}_transcript.json"
    final_mp4 = ROOT / f"{slug}_FINAL.mp4"
    out_480 = ROOT / f"{slug}_480p.mp4"
    tmp_dir = ROOT / f"tmp_{slug}"
    scenes_dir = ROOT / "phonics-songs" / slug

    print(f"\n=== {slug} ===")
    print("[1/6] Download Suno audio…")
    if mp3.exists() and skip_existing:
        print(f"  {mp3.name} exists, skip")
    else:
        download_suno_audio(suno_sid, mp3)

    print("[2/6] Whisper transcription…")
    if transcript.exists() and skip_existing:
        print(f"  {transcript.name} exists, skip")
    else:
        whisper_transcribe(mp3, transcript)

    print("[3/6] Build motion video…")
    if final_mp4.exists() and skip_existing:
        print(f"  {final_mp4.name} exists, skip")
    else:
        build_motion_video(timeline, scenes_dir, mp3, final_mp4, tmp_dir)

    print("[4/6] Compress to 480p…")
    if out_480.exists() and skip_existing:
        print(f"  {out_480.name} exists, skip")
    else:
        compress_to_480p(final_mp4, out_480)

    print("[5/6] Upload to tmpfiles…")
    public_url = upload_to_tmpfiles(out_480)

    print("[6/6] Revid caption-video…")
    pid = revid_caption_only(public_url, project_name)

    return {
        "mp3": str(mp3),
        "transcript": str(transcript),
        "final_mp4": str(final_mp4),
        "mp4_480p": str(out_480),
        "public_url": public_url,
        "revid_pid": pid,
        "revid_url": f"https://www.revid.ai/projects/{pid}",
    }


# ── Example: Baker Bear (already done; here as a template) ────────
BAKER_BEAR_TIMELINE = [
    # v2 (Suno SID S9Omy1HpfhN8ELWT, duration 212.76s, 'lane' lyric version)
    ('01_baking_cakes',                   0.00,  12.00, 'zoom_in_center'),
    ('02_pondering_question',            12.00,  29.80, 'pan_diag_tl_br'),
    ('03_finding_magic_e',               29.80,  36.96, 'zoom_in_center'),
    ('06_wizard_pose',                   36.96,  50.76, 'pan_lr_zoom'),
    ('04_first_transform_surprised',     50.76,  58.50, 'zoom_in_center'),
    ('04b_can_to_cane',                  58.50,  64.72, 'zoom_in_center'),
    ('06_wizard_pose',                   64.72,  78.76, 'pan_rl_zoom'),
    ('05_enjoying_mat_to_mate',          78.76,  84.92, 'zoom_in_center'),
    ('06b_plan_to_plane',                84.92,  92.30, 'pan_diag_tl_br'),
    ('07b_slat_to_slate',                92.30,  99.22, 'zoom_out_center'),
    ('08_engineer_egg_arrives',          99.22, 105.92, 'pan_lr_zoom'),
    ('09_engineer_egg_picks_up_e',      105.92, 112.02, 'zoom_in_center'),
    ('10_dancing_together_01',          112.02, 127.76, 'pan_lr_zoom'),
    ('11_dancing_together_02',          127.76, 141.74, 'pan_diag_tl_br'),
    ('12_brave_mate_at_the_gate',       141.74, 144.60, 'zoom_in_center'),
    ('13_pale_cane_on_a_plate',         144.60, 148.44, 'pan_rl_zoom'),
    ('14_late_plane_in_the_lane',       148.44, 151.88, 'pan_diag_tl_br'),
    ('15_safe_cape_on_a_slate',         151.88, 155.32, 'zoom_in_center'),
    ('06_wizard_pose',                  155.32, 168.94, 'pan_lr_zoom'),
    ('16_word_parade',                  168.94, 180.98, 'pan_lr_zoom'),
    ('17_finale_dancing',               180.98, 212.76, 'zoom_in_center'),
]

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "baker":
        result = run_pipeline(
            slug="baker_bear_long_a",
            suno_sid="S9Omy1HpfhN8ELWT",   # v2: lane version (212.76s)
            project_name="Baker Bear and Magic E — Long A (captioned, v2)",
            timeline=BAKER_BEAR_TIMELINE,
        )
        print("\n" + json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(__doc__)
