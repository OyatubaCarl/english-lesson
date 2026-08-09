#!/usr/bin/env python3
"""Generate original clipped phonics phoneme audio.

This is not a voice clone and does not transform any third-party recording.
It synthesizes short "pure sound" style phoneme clips from basic acoustic
models: bursts for stops, filtered noise for fricatives, and formant synthesis
for vowels and voiced sonorants.
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable

import numpy as np
import soundfile as sf
from scipy import signal


DEFAULT_DATA = "phonics-audio-items.json"
DEFAULT_OUT = "audio/phonics-generated"
SAMPLE_RATE = 44_100


VOWELS = {
    "ae": {"formants": [(660, 1.0, 7), (1720, 0.66, 9), (2410, 0.27, 12)], "pitch": 205, "duration": 0.42},
    "eh": {"formants": [(530, 1.0, 7), (1840, 0.7, 9), (2480, 0.25, 12)], "pitch": 205, "duration": 0.38},
    "ih": {"formants": [(390, 1.0, 8), (1990, 0.64, 10), (2550, 0.22, 12)], "pitch": 210, "duration": 0.36},
    "ah": {"formants": [(730, 1.0, 7), (1090, 0.55, 8), (2440, 0.2, 11)], "pitch": 198, "duration": 0.42},
    "uh": {"formants": [(640, 1.0, 7), (1190, 0.52, 8), (2390, 0.2, 11)], "pitch": 200, "duration": 0.36},
}

SONORANTS = {
    "m": {"formants": [(250, 1.0, 5), (700, 0.25, 7), (1150, 0.16, 7)], "pitch": 145, "duration": 0.32},
    "n": {"formants": [(300, 1.0, 5), (1220, 0.25, 7), (2100, 0.16, 8)], "pitch": 150, "duration": 0.3},
    "ng": {"formants": [(260, 1.0, 5), (980, 0.24, 7), (2500, 0.16, 8)], "pitch": 145, "duration": 0.34},
    "l": {"formants": [(330, 0.75, 5), (1050, 0.45, 7), (2550, 0.22, 9)], "pitch": 155, "duration": 0.28},
    "r": {"formants": [(340, 0.65, 5), (900, 0.32, 8), (1600, 0.22, 10)], "pitch": 150, "duration": 0.3},
    "w": {"formants": [(300, 0.75, 5), (760, 0.42, 7), (2400, 0.2, 9)], "pitch": 155, "duration": 0.24},
    "y": {"formants": [(280, 0.55, 5), (2150, 0.65, 9), (3000, 0.22, 10)], "pitch": 160, "duration": 0.24},
}

FRICATIVES = {
    "f": {"kind": "band", "freq": 1800, "q": 0.65, "duration": 0.26, "level": 0.52, "voiced": False},
    "v": {"kind": "band", "freq": 1600, "q": 0.65, "duration": 0.28, "level": 0.38, "voiced": True},
    "s": {"kind": "high", "freq": 4300, "q": 0.7, "duration": 0.28, "level": 0.5, "voiced": False},
    "z": {"kind": "high", "freq": 3800, "q": 0.7, "duration": 0.3, "level": 0.36, "voiced": True},
    "h": {"kind": "band", "freq": 1500, "q": 0.5, "duration": 0.22, "level": 0.28, "voiced": False},
    "sh": {"kind": "band", "freq": 2500, "q": 0.9, "duration": 0.3, "level": 0.52, "voiced": False},
    "th_voiceless": {"kind": "band", "freq": 3600, "q": 0.55, "duration": 0.25, "level": 0.28, "voiced": False},
    "th_voiced": {"kind": "band", "freq": 3200, "q": 0.55, "duration": 0.26, "level": 0.25, "voiced": True},
}

STOPS = {
    "p": {"freq": 2200, "q": 0.75, "voiced": False, "duration": 0.075, "burst": 0.018, "level": 0.58, "highpass": 900},
    "b": {"freq": 900, "q": 1.35, "voiced": True, "duration": 0.15, "burst": 0.032, "level": 0.72},
    "t": {"freq": 4300, "q": 1.1, "voiced": False, "duration": 0.12, "burst": 0.032, "level": 0.82},
    "d": {"freq": 3600, "q": 1.1, "voiced": True, "duration": 0.14, "burst": 0.03, "level": 0.66},
    "k": {"freq": 2300, "q": 1.2, "voiced": False, "duration": 0.13, "burst": 0.038, "level": 0.86},
    "g": {"freq": 1850, "q": 1.2, "voiced": True, "duration": 0.15, "burst": 0.034, "level": 0.7},
}


def require_tool(name: str) -> str:
    tool = shutil.which(name)
    if not tool:
        raise SystemExit(f"ERROR: {name} is required but was not found on PATH")
    return tool


def envelope(length: int, attack: float, release: float, level: float = 1.0) -> np.ndarray:
    env = np.ones(length, dtype=np.float32) * level
    attack_n = max(1, min(length, int(attack * SAMPLE_RATE)))
    release_n = max(1, min(length, int(release * SAMPLE_RATE)))
    env[:attack_n] *= np.linspace(0.0, 1.0, attack_n, dtype=np.float32)
    env[-release_n:] *= np.linspace(1.0, 0.0, release_n, dtype=np.float32)
    return env


def silence(duration: float) -> np.ndarray:
    return np.zeros(int(duration * SAMPLE_RATE), dtype=np.float32)


def bandpass(samples: np.ndarray, frequency: float, q: float) -> np.ndarray:
    b, a = signal.iirpeak(frequency / (SAMPLE_RATE / 2), q)
    return signal.lfilter(b, a, samples).astype(np.float32)


def highpass(samples: np.ndarray, frequency: float) -> np.ndarray:
    b, a = signal.butter(2, frequency / (SAMPLE_RATE / 2), "highpass")
    return signal.lfilter(b, a, samples).astype(np.float32)


def normalize(samples: np.ndarray, peak: float = 0.88) -> np.ndarray:
    if samples.size == 0:
        return samples.astype(np.float32)
    current = float(np.max(np.abs(samples)))
    if current <= 0.00001:
        return samples.astype(np.float32)
    return (samples / current * peak).astype(np.float32)


def glottal(duration: float, pitch: float, rng: np.random.Generator) -> np.ndarray:
    t = np.arange(int(duration * SAMPLE_RATE), dtype=np.float32) / SAMPLE_RATE
    source = signal.sawtooth(2 * math.pi * pitch * t, width=0.62).astype(np.float32)
    source += 0.12 * np.sin(2 * math.pi * pitch * 2 * t).astype(np.float32)
    source += 0.025 * rng.normal(size=source.shape).astype(np.float32)
    return source


def formant_sound(
    duration: float,
    pitch: float,
    formants: Iterable[tuple[float, float, float]],
    rng: np.random.Generator,
    attack: float = 0.018,
    release: float = 0.04,
) -> np.ndarray:
    source = glottal(duration, pitch, rng)
    out = np.zeros_like(source)
    for frequency, gain, q in formants:
        out += bandpass(source, frequency, q) * gain
    out *= envelope(len(out), attack, release, 1.0)
    return normalize(out)


def synth_vowel(sound_id: str, rng: np.random.Generator) -> np.ndarray:
    profile = VOWELS[sound_id]
    return formant_sound(profile["duration"], profile["pitch"], profile["formants"], rng)


def synth_sonorant(sound_id: str, rng: np.random.Generator) -> np.ndarray:
    profile = SONORANTS[sound_id]
    return normalize(formant_sound(profile["duration"], profile["pitch"], profile["formants"], rng, 0.02, 0.05) * 0.82)


def synth_fricative(sound_id: str, rng: np.random.Generator) -> np.ndarray:
    profile = FRICATIVES[sound_id]
    length = int(profile["duration"] * SAMPLE_RATE)
    noise = rng.normal(size=length).astype(np.float32)
    if profile["kind"] == "high":
        hiss = highpass(noise, profile["freq"])
    else:
        hiss = bandpass(noise, profile["freq"], profile["q"])
    hiss *= envelope(length, 0.016, 0.04, profile["level"])
    if profile["voiced"]:
        voice = formant_sound(profile["duration"], 135, [(260, 0.8, 5), (900, 0.2, 8)], rng, 0.018, 0.05)
        hiss += voice * 0.34
    return normalize(hiss)


def synth_stop(sound_id: str, rng: np.random.Generator) -> np.ndarray:
    profile = STOPS[sound_id]
    body = silence(profile["duration"])
    start = int((0.05 if profile["voiced"] else 0.055) * SAMPLE_RATE)
    burst_n = int(profile["burst"] * SAMPLE_RATE)
    noise = rng.normal(size=burst_n).astype(np.float32)
    burst = bandpass(noise, profile["freq"], profile["q"]) * envelope(burst_n, 0.001, 0.018, profile["level"])
    if profile.get("highpass"):
        burst = highpass(burst, profile["highpass"])
    body[start : start + burst_n] += burst[: max(0, min(burst_n, len(body) - start))]
    if profile["voiced"]:
        pre = formant_sound(0.07, 125, [(230, 0.75, 5), (760, 0.18, 8)], rng, 0.012, 0.025) * 0.35
        body[: len(pre)] += pre
    return normalize(body)


def synth_affricate(sound_id: str, rng: np.random.Generator) -> np.ndarray:
    if sound_id == "ch":
        return normalize(np.concatenate([synth_stop("t", rng)[: int(0.08 * SAMPLE_RATE)], synth_fricative("sh", rng)[: int(0.18 * SAMPLE_RATE)]]))
    stop = synth_stop("d", rng)[: int(0.08 * SAMPLE_RATE)]
    fric = synth_fricative("sh", rng)[: int(0.18 * SAMPLE_RATE)] * 0.75
    voice = formant_sound(0.24, 135, [(260, 0.8, 5), (900, 0.2, 8)], rng, 0.012, 0.05) * 0.25
    combined = np.concatenate([stop, fric])
    combined[: len(voice)] += voice[: len(combined)]
    return normalize(combined)


def synth_cluster(sound_id: str, rng: np.random.Generator) -> np.ndarray:
    if sound_id == "kw":
        return normalize(np.concatenate([synth_stop("k", rng), silence(0.025), synth_sonorant("w", rng)[: int(0.17 * SAMPLE_RATE)]]))
    return normalize(np.concatenate([synth_stop("k", rng), silence(0.025), synth_fricative("s", rng)[: int(0.19 * SAMPLE_RATE)]]))


def synth_phoneme(item: dict, rng: np.random.Generator) -> np.ndarray:
    sound_id = item["id"]
    if sound_id in VOWELS:
        audio = synth_vowel(sound_id, rng)
    elif sound_id in SONORANTS:
        audio = synth_sonorant(sound_id, rng)
    elif sound_id in FRICATIVES:
        audio = synth_fricative(sound_id, rng)
    elif sound_id in STOPS:
        audio = synth_stop(sound_id, rng)
    elif sound_id in ("ch", "j"):
        audio = synth_affricate(sound_id, rng)
    elif sound_id in ("kw", "ks"):
        audio = synth_cluster(sound_id, rng)
    else:
        audio = synth_vowel("uh", rng)

    # A tiny boundary pad avoids browser clipping without adding an audible vowel.
    return np.concatenate([silence(0.015), audio, silence(0.035)]).astype(np.float32)


def write_mp3(ffmpeg: str, samples: np.ndarray, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmpdir:
        wav_path = Path(tmpdir) / "sound.wav"
        sf.write(wav_path, samples, SAMPLE_RATE, subtype="PCM_16")
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(wav_path),
                "-af",
                "loudnorm=I=-19:TP=-1.5:LRA=7",
                "-codec:a",
                "libmp3lame",
                "-q:a",
                "2",
                str(out_path),
            ],
            check=True,
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=DEFAULT_DATA)
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    data = json.loads(Path(args.data).read_text(encoding="utf-8"))
    out_root = Path(args.out)
    phoneme_dir = out_root / "phonemes"
    ffmpeg = require_tool("ffmpeg")
    rng = np.random.default_rng(20260513)
    manifest = {
        "provider": "original-acoustic-synthesis",
        "license_status": "project-original generated audio; no third-party recording embedded",
        "phonemes": [],
    }

    if args.dry_run:
        print(f"Would generate {len(data['phonemes'])} phoneme files into {phoneme_dir}")
        return 0

    for item in data["phonemes"]:
        out_path = phoneme_dir / f"{item['id']}.mp3"
        if out_path.exists() and not args.force:
            continue
        samples = synth_phoneme(item, rng)
        write_mp3(ffmpeg, samples, out_path)
        duration = len(samples) / SAMPLE_RATE
        manifest["phonemes"].append(
            {
                "id": item["id"],
                "label": item["label"],
                "ipa": item["ipa"],
                "type": item["type"],
                "duration": round(duration, 3),
                "audio": str(out_path),
            }
        )
        print(f"phoneme {item['id']}: {out_path} ({duration:.2f}s)")

    out_root.mkdir(parents=True, exist_ok=True)
    (out_root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"manifest: {out_root / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
