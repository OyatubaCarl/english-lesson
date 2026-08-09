#!/usr/bin/env python3
"""ハイブリッドTTS試作: voicepeak(JP) + say(EN) を区間別に合成して連結。

文を [JP] [EN] [JP] ... の区間タグでパースし、各区間を別エンジンで合成。
連結時は同じ wav フォーマット(48kHz mono pcm_s16le)に揃える。
"""
from __future__ import annotations
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

VP_BIN = "/Applications/voicepeak.app/Contents/MacOS/voicepeak"
VP_NARRATOR = "Japanese Female 2"  # 教材ナレ寄りの落ち着いた女性
EN_VOICE = "Samantha"              # macOS 内蔵 en_US 自然voice
SR = 48000
CH = 1

OUT_DIR = Path(
    "/Users/masaki/Documents/ClaudeCode/英語学習教材作成/shorts/tts_samples"
)
OUT_DIR.mkdir(exist_ok=True)


@dataclass(frozen=True)
class Seg:
    lang: str   # "jp" or "en"
    text: str
    speed: float = 1.0   # 1.0 等速
    gap_after: float = 0.0  # 後ろに入れる無音秒


# 試聴用の本文（コンマで自然な間が取れるよう調整）
SCRIPT = [
    Seg("jp", "桜の美しさは、", speed=1.0, gap_after=0.05),
    Seg("en", "ephemeral",      speed=1.0, gap_after=0.10),
    Seg("jp", "だ。咲いてから散るまで、わずか一週間しかないなんて。", speed=1.0),
]


def run(cmd, timeout=60):
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if p.returncode != 0:
        raise SystemExit(f"FAILED: {' '.join(cmd[:3])}...\n{p.stderr[-600:]}")


def normalize(src: Path, dst: Path):
    run(["ffmpeg", "-y", "-i", str(src),
         "-ar", str(SR), "-ac", str(CH),
         "-c:a", "pcm_s16le", str(dst)])


def silence(seconds: float, dst: Path):
    run(["ffmpeg", "-y", "-f", "lavfi", "-t", f"{seconds}",
         "-i", f"anullsrc=r={SR}:cl=mono",
         "-c:a", "pcm_s16le", str(dst)])


def vp_synth(text: str, speed: float, dst: Path):
    speed_pct = max(50, min(200, round(speed * 100)))
    raw = dst.with_suffix(".vpraw.wav")
    cmd = [VP_BIN, "-s", text, "-n", VP_NARRATOR,
           "-o", str(raw), "--speed", str(speed_pct)]
    # VP は連続実行で詰まることがある → 失敗時は kill+retry
    last = ""
    for attempt in range(4):
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
        except subprocess.TimeoutExpired:
            last = "timeout"
            subprocess.run(["pkill", "-9", "-f", "/Applications/voicepeak.app"],
                           capture_output=True)
            time.sleep(2)
            continue
        if p.returncode == 0 and raw.exists() and raw.stat().st_size > 0:
            break
        last = (p.stderr or "")[-400:]
        if raw.exists():
            raw.unlink()
        subprocess.run(["pkill", "-9", "-f", "/Applications/voicepeak.app"],
                       capture_output=True)
        time.sleep(1 + attempt)
    else:
        raise SystemExit(f"voicepeak failed: {last}")
    normalize(raw, dst)
    raw.unlink()
    # voicepeak の連続呼び出し詰まり対策
    time.sleep(1.0)


def en_synth(text: str, speed: float, dst: Path):
    # say は rate=200 が等速の体感に近い (default ≈ 175)。speed=1.0 で 200。
    rate = max(80, min(360, round(200 * speed)))
    aiff = dst.with_suffix(".aiff")
    # 既定の AIFF 出力 → ffmpeg で 48kHz mono pcm_s16le に正規化
    run(["say", "-v", EN_VOICE, "-r", str(rate), "-o", str(aiff), text])
    normalize(aiff, dst)
    aiff.unlink()


def concat(parts: list, dst: Path):
    listfile = dst.parent / "_concat_list.txt"
    listfile.write_text(
        "".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8"
    )
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
         "-ar", str(SR), "-ac", str(CH), "-c:a", "pcm_s16le", str(dst)])
    listfile.unlink()


def main():
    if shutil.which("ffmpeg") is None:
        raise SystemExit("ffmpeg が必要。 brew install ffmpeg")
    if not Path(VP_BIN).exists():
        raise SystemExit(f"voicepeak が見つからない: {VP_BIN}")

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        parts: list[Path] = []
        for i, seg in enumerate(SCRIPT):
            piece = tmp / f"seg{i:02d}_{seg.lang}.wav"
            print(f"  ♪ [{i:02d}] {seg.lang.upper()}  {seg.text[:30]}")
            if seg.lang == "jp":
                vp_synth(seg.text, seg.speed, piece)
            else:
                en_synth(seg.text, seg.speed, piece)
            parts.append(piece)
            if seg.gap_after > 0:
                sil = tmp / f"sil{i:02d}.wav"
                silence(seg.gap_after, sil)
                parts.append(sil)
        out_wav = OUT_DIR / "hybrid_sample.wav"
        out_mp3 = OUT_DIR / "hybrid_sample.mp3"
        concat(parts, out_wav)
        # mp3 化も同時に（再生互換性のため）
        run(["ffmpeg", "-y", "-i", str(out_wav),
             "-c:a", "libmp3lame", "-b:a", "192k", str(out_mp3)])
        print(f"\n✅ {out_wav}  ({out_wav.stat().st_size/1024:.1f} KB)")
        print(f"✅ {out_mp3}  ({out_mp3.stat().st_size/1024:.1f} KB)")


if __name__ == "__main__":
    main()
