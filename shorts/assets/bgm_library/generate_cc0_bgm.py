#!/usr/bin/env python3
"""Generate a small CC0 procedural BGM library for Shorts.

The tracks are synthesized locally with NumPy and ffmpeg. No third-party
samples, loops, or melodies are used.
"""

from __future__ import annotations

import json
import math
import subprocess
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfilt


SR = 44_100
DURATION = 30.2
N = int(SR * DURATION)
OUT_DIR = Path(__file__).resolve().parent
RNG = np.random.default_rng(20260608)


def midi(note: float) -> float:
    return 440.0 * (2.0 ** ((note - 69.0) / 12.0))


def pan_gains(pan: float) -> tuple[float, float]:
    pan = max(-1.0, min(1.0, pan))
    angle = (pan + 1.0) * math.pi / 4.0
    return math.cos(angle), math.sin(angle)


def add(y: np.ndarray, sig: np.ndarray, start: float, amp: float = 1.0, pan: float = 0.0) -> None:
    if sig.ndim == 2:
        stereo = sig * amp
    else:
        left, right = pan_gains(pan)
        stereo = np.column_stack((sig * left, sig * right)) * amp
    i = int(start * SR)
    if i >= len(y):
        return
    end = min(len(y), i + len(stereo))
    y[i:end] += stereo[: end - i]


def env_ar(n: int, attack: float, release: float) -> np.ndarray:
    e = np.ones(n, dtype=np.float32)
    a = min(n, max(1, int(attack * SR)))
    r = min(n, max(1, int(release * SR)))
    e[:a] *= np.linspace(0, 1, a, dtype=np.float32)
    e[-r:] *= np.linspace(1, 0, r, dtype=np.float32)
    return e


def exp_env(t: np.ndarray, attack: float, decay: float) -> np.ndarray:
    a = np.maximum(1e-5, attack)
    d = np.maximum(1e-5, decay)
    return (1.0 - np.exp(-t / a)) * np.exp(-t / d)


def lowpass(x: np.ndarray, cutoff: float, order: int = 2) -> np.ndarray:
    sos = butter(order, cutoff / (SR / 2), btype="low", output="sos")
    return sosfilt(sos, x, axis=0).astype(np.float32)


def highpass(x: np.ndarray, cutoff: float, order: int = 2) -> np.ndarray:
    sos = butter(order, cutoff / (SR / 2), btype="high", output="sos")
    return sosfilt(sos, x, axis=0).astype(np.float32)


def note_piano(freq: float, dur: float, tone: float = 0.8) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n, dtype=np.float32) / SR
    sig = np.zeros(n, dtype=np.float32)
    for h, a, d in [(1, 1.0, 2.7), (2, 0.42, 1.3), (3, 0.18, 0.9), (4, 0.08, 0.55)]:
        sig += a * np.sin(2 * np.pi * freq * h * t) * np.exp(-t / d)
    sig += 0.015 * RNG.normal(0, 1, n).astype(np.float32) * np.exp(-t / 0.035)
    sig *= exp_env(t, 0.006, max(0.7, dur * tone))
    return lowpass(sig[:, None], 5_200)[:, 0]


def note_rhodes(freq: float, dur: float) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n, dtype=np.float32) / SR
    trem = 0.82 + 0.18 * np.sin(2 * np.pi * 5.2 * t)
    sig = (
        np.sin(2 * np.pi * freq * t)
        + 0.35 * np.sin(2 * np.pi * freq * 2.01 * t + 0.4)
        + 0.16 * np.sin(2 * np.pi * freq * 3.0 * t)
    )
    sig *= trem * exp_env(t, 0.012, max(1.2, dur * 0.9))
    return lowpass(sig[:, None], 3_800)[:, 0]


def note_pad(freqs: list[float], dur: float, bright: float = 0.4, motion: float = 0.04) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n, dtype=np.float32) / SR
    sig = np.zeros((n, 2), dtype=np.float32)
    for idx, f in enumerate(freqs):
        detunes = [-0.006, 0.0, 0.005]
        for j, det in enumerate(detunes):
            phase = idx * 0.8 + j * 1.7
            wave = np.sin(2 * np.pi * f * (1 + det) * t + phase)
            wave += bright * 0.35 * np.sin(2 * np.pi * f * 2 * (1 + det * 0.4) * t + phase / 2)
            lfo = 1.0 + motion * np.sin(2 * np.pi * (0.035 + idx * 0.007) * t + phase)
            pan = -0.55 + (idx + j) % 5 * 0.27
            left, right = pan_gains(pan)
            sig[:, 0] += wave * lfo * left
            sig[:, 1] += wave * lfo * right
    sig *= env_ar(n, 1.8, 2.4)[:, None]
    return lowpass(sig / max(1, len(freqs) * 2.2), 2_300 + bright * 1_700)


def note_strings(freqs: list[float], dur: float) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n, dtype=np.float32) / SR
    sig = np.zeros((n, 2), dtype=np.float32)
    for idx, f in enumerate(freqs):
        wave = np.zeros(n, dtype=np.float32)
        for h in range(1, 7):
            wave += (1 / h) * np.sin(2 * np.pi * f * h * t + idx * 0.3)
        vibrato = 1 + 0.0025 * np.sin(2 * np.pi * 5.0 * t + idx)
        wave += 0.2 * np.sin(2 * np.pi * f * vibrato * t)
        left, right = pan_gains(-0.45 + idx * 0.28)
        sig[:, 0] += wave * left
        sig[:, 1] += wave * right
    sig *= env_ar(n, 0.45, 1.1)[:, None]
    return lowpass(sig / max(1, len(freqs) * 3), 3_100)


def note_pluck(freq: float, dur: float, decay: float = 0.992, color: float = 0.4) -> np.ndarray:
    n = int(dur * SR)
    period = max(2, int(SR / freq))
    buf = RNG.uniform(-1, 1, period).astype(np.float32)
    sig = np.zeros(n, dtype=np.float32)
    idx = 0
    for i in range(n):
        sig[i] = buf[idx]
        nxt = (idx + 1) % period
        buf[idx] = decay * (0.5 * buf[idx] + 0.5 * buf[nxt])
        idx = nxt
    t = np.arange(n, dtype=np.float32) / SR
    sig += color * np.sin(2 * np.pi * freq * 2 * t) * np.exp(-t / 0.5)
    sig *= exp_env(t, 0.002, dur * 0.55)
    return lowpass(sig[:, None], 4_800 + color * 2_000)[:, 0]


def note_koto(freq: float, dur: float, bend: float = 0.012) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n, dtype=np.float32) / SR
    inst_freq = freq * (1.0 + bend * np.exp(-t / 0.12))
    phase = 2 * np.pi * np.cumsum(inst_freq) / SR
    sig = np.sin(phase)
    sig += 0.42 * np.sin(2 * phase + 0.2)
    sig += 0.18 * np.sin(3 * phase + 0.9)
    sig += 0.035 * RNG.normal(0, 1, n).astype(np.float32) * np.exp(-t / 0.02)
    sig *= exp_env(t, 0.003, dur * 0.48)
    return lowpass(sig[:, None], 6_400)[:, 0]


def kick(dur: float = 0.42) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n, dtype=np.float32) / SR
    freq = 45 + 80 * np.exp(-t / 0.055)
    phase = 2 * np.pi * np.cumsum(freq) / SR
    return np.sin(phase) * np.exp(-t / 0.16)


def snare(dur: float = 0.25, brush: bool = False) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n, dtype=np.float32) / SR
    noise = RNG.normal(0, 1, n).astype(np.float32)
    shaped = highpass(noise[:, None], 1_600 if brush else 1_000)[:, 0]
    env = np.exp(-t / (0.12 if brush else 0.06))
    tone = 0.12 * np.sin(2 * np.pi * 180 * t) * np.exp(-t / 0.08)
    return shaped * env * (0.45 if brush else 0.65) + tone


def hat(dur: float = 0.08) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n, dtype=np.float32) / SR
    noise = RNG.normal(0, 1, n).astype(np.float32)
    return highpass(noise[:, None], 5_800)[:, 0] * np.exp(-t / 0.026)


def brush_loop(y: np.ndarray, bpm: float, bars: int, start: float = 0.0, amp: float = 0.05) -> None:
    beat = 60 / bpm
    for b in range(int(bars * 4)):
        t = start + b * beat
        if b % 4 in (1, 3):
            add(y, snare(0.35, brush=True), t, amp * 1.4, pan=0.15)
        if b % 2 == 0:
            add(y, kick(0.34), t, amp * 1.5, pan=-0.05)
        add(y, hat(0.06), t + beat * 0.5, amp * 0.45, pan=-0.35)


def vinyl(n: int, amount: float = 0.015) -> np.ndarray:
    base = RNG.normal(0, amount, (n, 2)).astype(np.float32)
    base = lowpass(base, 2_400)
    impulses = np.zeros((n, 2), dtype=np.float32)
    count = int(DURATION * 18)
    for _ in range(count):
        i = RNG.integers(0, n - 80)
        length = RNG.integers(8, 80)
        click = RNG.uniform(-1, 1) * np.exp(-np.arange(length) / RNG.uniform(8, 25))
        impulses[i : i + length, :] += click[:, None] * amount * RNG.uniform(1.0, 3.2)
    return base + impulses


def wind(n: int, amount: float = 0.025) -> np.ndarray:
    noise = RNG.normal(0, 1, (n, 2)).astype(np.float32)
    slow = lowpass(noise, 650)
    lfo = 0.5 + 0.5 * np.sin(2 * np.pi * np.arange(n) / SR * 0.055)
    return slow * lfo[:, None] * amount


def reverb(y: np.ndarray, wet: float = 0.22) -> np.ndarray:
    out = y.copy()
    for delay_s, gain in [(0.073, 0.20), (0.131, 0.14), (0.211, 0.10), (0.337, 0.07)]:
        d = int(delay_s * SR)
        out[d:] += y[:-d] * gain * wet
    return out


def master(y: np.ndarray, target: float = 0.88, lp_cutoff: float = 13_000) -> np.ndarray:
    y = highpass(y, 28)
    y = lowpass(y, lp_cutoff)
    y = reverb(y, 0.28)
    fade = env_ar(len(y), 0.12, 1.2)
    y *= fade[:, None]
    y = np.tanh(y * 1.15)
    peak = float(np.max(np.abs(y)))
    if peak > 0:
        y *= target / peak
    return y.astype(np.float32)


def write_wav(path: Path, y: np.ndarray) -> None:
    pcm = np.clip(y, -1, 1)
    pcm16 = (pcm * 32767).astype("<i2")
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm16.tobytes())


def encode_mp3(wav_path: Path, mp3_path: Path, title: str, artist: str) -> None:
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(wav_path),
            "-codec:a",
            "libmp3lame",
            "-q:a",
            "3",
            "-metadata",
            f"title={title}",
            "-metadata",
            f"artist={artist}",
            str(mp3_path),
        ],
        check=True,
    )


def duration(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
    )
    return round(float(out.strip()), 3)


def add_chord(y: np.ndarray, notes: list[int], start: float, dur: float, inst, amp: float, pan: float = 0.0) -> None:
    spread = np.linspace(-0.18, 0.18, len(notes)) if len(notes) > 1 else [0.0]
    for note, offset in zip(notes, spread):
        add(y, inst(midi(note), dur), start + max(0, float(offset) * 0.08), amp, pan + float(offset))


def track_01() -> np.ndarray:
    y = np.zeros((N, 2), dtype=np.float32)
    bpm = 76
    beat = 60 / bpm
    chords = [[48, 52, 55, 59], [45, 48, 52, 55], [41, 45, 48, 52], [43, 47, 50, 55]]
    for bar in range(10):
        start = bar * 4 * beat
        chord = chords[bar % len(chords)]
        add_chord(y, chord, start, 2.4, note_piano, 0.105, -0.08)
        add_chord(y, [n + 12 for n in chord[:3]], start + 2 * beat, 1.7, note_piano, 0.055, 0.18)
        for m, rel in enumerate([0.5, 1.5, 2.75]):
            note = [64, 67, 69, 72, 71][(bar + m) % 5]
            add(y, note_piano(midi(note), 1.2), start + rel * beat, 0.035, 0.32)
    brush_loop(y, bpm, 10, amp=0.045)
    y += vinyl(N, 0.004)
    return master(y, 0.84, 10_000)


def track_02() -> np.ndarray:
    y = np.zeros((N, 2), dtype=np.float32)
    chords = [[50, 57, 62, 65], [46, 53, 58, 62], [41, 48, 55, 60], [48, 55, 60, 64]]
    seg = DURATION / 4
    for i, chord in enumerate(chords):
        add(y, note_pad([midi(n) for n in chord], seg + 1.2, bright=0.22, motion=0.08), i * seg, 0.47)
        add(y, note_pad([midi(n + 12) for n in chord[:2]], seg, bright=0.08, motion=0.12), i * seg + 0.7, 0.18)
    for t in np.arange(2.4, DURATION, 3.8):
        add(y, note_piano(midi([74, 76, 79, 81][int(t) % 4]), 2.8, 1.2), float(t), 0.026, 0.42)
    y += wind(N, 0.018)
    return master(y, 0.82, 8_600)


def track_03() -> np.ndarray:
    y = np.zeros((N, 2), dtype=np.float32)
    bpm = 68
    beat = 60 / bpm
    chords = [[52, 55, 59, 64], [48, 52, 55, 60], [43, 47, 50, 55], [45, 48, 52, 57]]
    for bar in range(9):
        start = bar * 4 * beat
        chord = chords[bar % 4]
        add(y, note_strings([midi(n) for n in chord], 4 * beat + 0.8), start, 0.19)
        for i, n in enumerate(chord + [chord[-1] + 5]):
            add(y, note_piano(midi(n + 12), 1.35, 0.95), start + i * beat * 0.72, 0.05, -0.18 + i * 0.08)
        add(y, kick(0.5), start, 0.035, -0.1)
    return master(y, 0.86, 11_500)


def track_04() -> np.ndarray:
    y = np.zeros((N, 2), dtype=np.float32)
    bpm = 82
    beat = 60 / bpm
    chords = [[43, 50, 55, 59], [38, 45, 50, 54], [40, 47, 52, 55], [36, 43, 48, 52]]
    pattern = [0, 2, 1, 3, 2, 1]
    for bar in range(11):
        start = bar * 4 * beat
        chord = chords[bar % 4]
        for step, idx in enumerate(pattern * 2):
            t = start + step * beat / 3
            add(y, note_pluck(midi(chord[idx] + (12 if step % 3 == 2 else 0)), 1.1, 0.989, 0.25), t, 0.065, -0.12)
        add(y, snare(0.18, brush=True), start + 2 * beat, 0.028, 0.25)
        add(y, kick(0.26), start, 0.025, -0.2)
    return master(y, 0.84, 10_800)


def track_05() -> np.ndarray:
    y = np.zeros((N, 2), dtype=np.float32)
    bpm = 72
    beat = 60 / bpm
    scale = [50, 53, 55, 57, 60, 62, 65, 67]
    base_chords = [[38, 50, 55], [43, 50, 57], [45, 53, 57], [41, 53, 60]]
    for bar in range(10):
        start = bar * 4 * beat
        add(y, note_pad([midi(n) for n in base_chords[bar % 4]], 4 * beat + 1, bright=0.18), start, 0.19)
        for step in range(8):
            n = scale[(step * 2 + bar) % len(scale)]
            add(y, note_koto(midi(n + (12 if step in (3, 7) else 0)), 1.0), start + step * beat * 0.5, 0.07, -0.18 + 0.1 * (step % 3))
        add(y, note_pluck(midi(base_chords[bar % 4][0]), 1.1, 0.985, 0.55), start, 0.085, -0.42)
        add(y, snare(0.16, brush=True), start + 2 * beat, 0.018, 0.28)
    return master(y, 0.84, 12_000)


def track_06() -> np.ndarray:
    y = np.zeros((N, 2), dtype=np.float32)
    bpm = 82
    beat = 60 / bpm
    chords = [[41, 45, 52, 55, 60], [40, 43, 47, 52, 55], [38, 41, 45, 50, 53], [36, 40, 43, 47, 52]]
    for bar in range(11):
        start = bar * 4 * beat
        chord = chords[bar % 4]
        add_chord(y, chord, start, 2.7, note_rhodes, 0.065, -0.04)
        add_chord(y, [n + 12 for n in chord[1:4]], start + 2 * beat, 1.8, note_rhodes, 0.044, 0.16)
        add(y, kick(0.35), start, 0.065, -0.08)
        add(y, kick(0.32), start + 2.5 * beat, 0.044, -0.08)
        add(y, snare(0.22, brush=False), start + beat, 0.032, 0.12)
        add(y, snare(0.22, brush=False), start + 3 * beat, 0.034, 0.12)
        for h in range(8):
            add(y, hat(0.055), start + h * beat * 0.5, 0.018, -0.38)
    y += vinyl(N, 0.007)
    return master(y, 0.84, 9_600)


def track_07() -> np.ndarray:
    y = np.zeros((N, 2), dtype=np.float32)
    bpm = 88
    beat = 60 / bpm
    chords = [[48, 55, 60, 64], [43, 50, 55, 59], [45, 52, 57, 60], [41, 48, 53, 57]]
    for bar in range(12):
        start = bar * 4 * beat
        chord = chords[bar % 4]
        add(y, note_strings([midi(n) for n in chord], 4 * beat + 0.3), start, 0.16)
        for step in range(8):
            n = chord[step % len(chord)] + (12 if step > 3 else 0)
            add(y, note_pluck(midi(n), 0.72, 0.992, 0.15), start + step * beat * 0.5, 0.028, -0.22 + 0.08 * step)
        if bar % 2 == 0:
            add(y, note_piano(midi(72), 1.8, 1.0), start + 3 * beat, 0.035, 0.2)
    return master(y, 0.86, 12_000)


def track_08() -> np.ndarray:
    y = np.zeros((N, 2), dtype=np.float32)
    bpm = 90
    beat = 60 / bpm
    chords = [[45, 52, 57, 60], [48, 55, 60, 64], [43, 50, 55, 59], [41, 48, 53, 57]]
    for bar in range(12):
        start = bar * 4 * beat
        chord = chords[bar % 4]
        add(y, note_pad([midi(n) for n in chord], 4 * beat + 0.4, bright=0.48, motion=0.05), start, 0.12)
        arp = [chord[0], chord[1], chord[2], chord[3], chord[2], chord[1], chord[3], chord[1]]
        for step, n in enumerate(arp):
            sig = note_rhodes(midi(n + 12), 0.45)
            add(y, sig, start + step * beat * 0.5, 0.026, -0.25 + 0.08 * (step % 6))
        add(y, kick(0.25), start, 0.032, -0.08)
        add(y, hat(0.04), start + 2 * beat, 0.015, 0.3)
    return master(y, 0.83, 8_500)


def track_09() -> np.ndarray:
    y = np.zeros((N, 2), dtype=np.float32)
    bpm = 70
    beat = 60 / bpm
    chords = [[50, 53, 57, 60, 64], [43, 47, 50, 53, 59], [48, 52, 55, 59, 62], [45, 49, 52, 55, 61]]
    for bar in range(9):
        start = bar * 4 * beat
        chord = chords[bar % 4]
        add_chord(y, chord, start, 2.5, note_piano, 0.075, -0.03)
        add_chord(y, chord[1:] + [chord[-1] + 2], start + 2.2 * beat, 1.7, note_piano, 0.052, 0.13)
        for rel, n in [(0.8, chord[-1] + 5), (1.45, chord[-2] + 7), (3.0, chord[-1] + 2)]:
            add(y, note_piano(midi(n), 0.95, 0.8), start + rel * beat, 0.028, 0.34)
        add(y, kick(0.28), start, 0.028, -0.12)
        add(y, snare(0.36, brush=True), start + 2 * beat, 0.04, 0.22)
        for h in range(8):
            add(y, hat(0.08), start + h * beat * 0.5, 0.009, -0.4)
    return master(y, 0.82, 10_300)


def track_10() -> np.ndarray:
    y = np.zeros((N, 2), dtype=np.float32)
    chords = [[45, 52, 57, 60], [41, 48, 53, 57], [50, 57, 62, 65], [43, 50, 55, 59]]
    seg = DURATION / 4
    scale = [57, 60, 62, 64, 67, 69, 72]
    for i, chord in enumerate(chords):
        start = i * seg
        add(y, note_pad([midi(n) for n in chord], seg + 1.6, bright=0.16, motion=0.1), start, 0.34)
        add(y, note_strings([midi(n) for n in chord[:3]], seg + 0.8), start + 0.5, 0.08)
    for idx, t in enumerate([1.7, 4.9, 8.2, 12.4, 15.8, 19.6, 23.0, 26.5]):
        add(y, note_koto(midi(scale[idx % len(scale)]), 2.2, bend=0.006), t, 0.045, -0.22 + 0.12 * (idx % 4))
    y += wind(N, 0.024)
    return master(y, 0.82, 7_800)


TRACKS = [
    {
        "id": "01_lofi_piano",
        "title": "Lo-fi Piano Study Loop",
        "tags": ["lofi", "piano", "soft drums", "study"],
        "builder": track_01,
    },
    {
        "id": "02_ambient_pad",
        "title": "Floating Ambient Pad",
        "tags": ["ambient", "pad", "ethereal", "study"],
        "builder": track_02,
    },
    {
        "id": "03_cinematic_calm",
        "title": "Cinematic Calm Reflection",
        "tags": ["cinematic", "piano", "strings", "calm"],
        "builder": track_03,
    },
    {
        "id": "04_minimal_acoustic",
        "title": "Minimal Acoustic Morning",
        "tags": ["acoustic", "guitar", "minimal percussion", "study"],
        "builder": track_04,
    },
    {
        "id": "05_japanese_koto",
        "title": "Modern Koto Study",
        "tags": ["koto", "japanese", "shamisen", "modern"],
        "builder": track_05,
    },
    {
        "id": "06_chillhop_warm",
        "title": "Warm Chillhop Notes",
        "tags": ["chillhop", "warm", "vinyl crackle", "study"],
        "builder": track_06,
    },
    {
        "id": "07_orchestral_light",
        "title": "Light Orchestral Learning",
        "tags": ["orchestral", "optimistic", "strings", "learning"],
        "builder": track_07,
    },
    {
        "id": "08_electronic_study",
        "title": "Subtle Electronic Study",
        "tags": ["electronic", "sci-tech", "study", "subtle"],
        "builder": track_08,
    },
    {
        "id": "09_jazz_lounge",
        "title": "Soft Jazz Lounge Study",
        "tags": ["jazz", "piano", "brush drums", "lounge"],
        "builder": track_09,
    },
    {
        "id": "10_sakura_ambient",
        "title": "Yozakura Ambient Stillness",
        "tags": ["sakura", "ambient", "night", "quiet"],
        "builder": track_10,
    },
]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    meta = []
    artist = "Codex Local Generator"
    source = "Original local CC0 composition"
    for item in TRACKS:
        wav_path = OUT_DIR / f"{item['id']}.wav"
        mp3_path = OUT_DIR / f"{item['id']}.mp3"
        audio = item["builder"]()
        write_wav(wav_path, audio)
        encode_mp3(wav_path, mp3_path, item["title"], artist)
        wav_path.unlink()
        dur = duration(mp3_path)
        meta.append(
            {
                "id": item["id"],
                "title": item["title"],
                "artist": artist,
                "license": "CC0",
                "source_url": f"local://shorts/assets/bgm_library/{item['id']}.mp3",
                "duration_sec": dur,
                "tags": item["tags"],
                "credit_line": f"Music by {artist} ({source}, CC0)",
            }
        )
        print(f"[{item['id'][:2]}] OK: {item['title']} / CC0 / {meta[-1]['source_url']}")

    (OUT_DIR / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print("\nmeta.json:")
    print((OUT_DIR / "meta.json").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
