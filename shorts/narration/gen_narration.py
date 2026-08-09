#!/usr/bin/env python3
"""ルー語クイズShort用ナレーションを区間別合成して結合。

ナレ1: 本文（JP→EN→JP）
ナレ2: 問題（EN→JP）

出力:
  narr_body.wav   (本文)
  narr_quiz.wav   (問題)
  尺(秒)を JSON で出力 → 字幕タイミングに使う
"""
from __future__ import annotations
import json
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

VP_BIN = "/Applications/voicepeak.app/Contents/MacOS/voicepeak"
VP_NARRATOR = "Japanese Female 2"  # 落ち着いた女性
EN_VOICE = "Samantha"
SR = 48000
CH = 1

OUT_DIR = Path(
    "/Users/masaki/Documents/ClaudeCode/英語学習教材作成/shorts/narration"
)
OUT_DIR.mkdir(exist_ok=True)


@dataclass(frozen=True)
class Seg:
    lang: str       # "jp" or "en"
    text: str
    speed: float = 1.0
    gap_after: float = 0.0


# 本文: 桜の美しさは、ephemeral だ。咲いてから散るまで、わずか一週間しかないなんて。
SCRIPT_BODY = [
    Seg("jp", "桜の美しさは、", speed=1.0, gap_after=0.05),
    Seg("en", "ephemeral", speed=0.95, gap_after=0.15),
    Seg("jp", "だ。咲いてから散るまで、わずか一週間しかないなんて。", speed=1.0),
]

# 問題: ephemeral の意味は？
SCRIPT_QUIZ = [
    Seg("en", "ephemeral", speed=0.95, gap_after=0.10),
    Seg("jp", "の意味は？", speed=1.0),
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
    time.sleep(1.0)


def en_synth(text: str, speed: float, dst: Path):
    rate = max(80, min(360, round(200 * speed)))
    aiff = dst.with_suffix(".aiff")
    run(["say", "-v", EN_VOICE, "-r", str(rate), "-o", str(aiff), text])
    normalize(aiff, dst)
    aiff.unlink()


def concat(parts: list, dst: Path):
    listfile = dst.parent / f"_concat_{dst.stem}.txt"
    listfile.write_text(
        "".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8"
    )
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
         "-ar", str(SR), "-ac", str(CH), "-c:a", "pcm_s16le", str(dst)])
    listfile.unlink()


def duration_seconds(path: Path) -> float:
    p = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a:0",
         "-show_entries", "stream=duration", "-of", "default=nw=1:nk=1",
         str(path)], capture_output=True, text=True)
    return float(p.stdout.strip())


def build_script(name: str, script: list[Seg]) -> tuple[Path, float]:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        parts: list[Path] = []
        for i, seg in enumerate(script):
            piece = tmp / f"{name}_{i:02d}_{seg.lang}.wav"
            print(f"  ♪ [{name} {i:02d}] {seg.lang.upper()}  {seg.text}")
            if seg.lang == "jp":
                vp_synth(seg.text, seg.speed, piece)
            else:
                en_synth(seg.text, seg.speed, piece)
            parts.append(piece)
            if seg.gap_after > 0:
                sil = tmp / f"{name}_sil{i:02d}.wav"
                silence(seg.gap_after, sil)
                parts.append(sil)
        out_wav = OUT_DIR / f"narr_{name}.wav"
        concat(parts, out_wav)
        dur = duration_seconds(out_wav)
        print(f"  → {out_wav.name}  ({dur:.2f}s, {out_wav.stat().st_size/1024:.1f}KB)")
        return out_wav, dur


def main():
    print("=== 本文ナレ ===")
    body_path, body_dur = build_script("body", SCRIPT_BODY)
    print("=== 問題ナレ ===")
    quiz_path, quiz_dur = build_script("quiz", SCRIPT_QUIZ)

    meta = {
        "body": {"path": str(body_path), "duration_sec": round(body_dur, 3)},
        "quiz": {"path": str(quiz_path), "duration_sec": round(quiz_dur, 3)},
    }
    meta_path = OUT_DIR / "durations.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2),
                         encoding="utf-8")
    print(f"\n✅ meta -> {meta_path}")
    print(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
