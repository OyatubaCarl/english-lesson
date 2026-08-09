#!/usr/bin/env python3
"""quizzes.json の各クイズ(02-11)について本文・問題ナレを生成。

各 quiz id ごとに narration/{id}/narr_body.wav / narr_quiz.wav / durations.json を出力。
本文 narration を英単語(word)で split し、JP/EN セグメントに分けて
voicepeak(JP) + say Samantha(EN) のハイブリッドで合成→連結。
"""
from __future__ import annotations
import json
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

VP_BIN = "/Applications/voicepeak.app/Contents/MacOS/voicepeak"
VP_NARRATOR = "Japanese Female 2"
EN_VOICE = "Samantha"
SR = 48000
CH = 1

ROOT = Path("/Users/masaki/Documents/ClaudeCode/英語学習教材作成/shorts")
QUIZZES_JSON = ROOT / "quizzes.json"
NARR_ROOT = ROOT / "narration"
NARR_ROOT.mkdir(exist_ok=True)


@dataclass(frozen=True)
class Seg:
    lang: str
    text: str
    gap_after: float = 0.0


def split_by_word(sentence: str, word: str, gap_around_en: float = 0.10) -> list[Seg]:
    """sentence を word(英単語)で分割し、Seg list にする。"""
    parts = sentence.split(word)
    segs: list[Seg] = []
    for i, p in enumerate(parts):
        p = p.strip()
        if p:
            # 末尾に gap を入れる(英単語前後の自然な間)
            gap = gap_around_en if i < len(parts) - 1 else 0.0
            # 末尾の句読点で 0.05s だけ追加してもよいが、まずは均一
            segs.append(Seg("jp", p, gap_after=gap))
        if i < len(parts) - 1:
            segs.append(Seg("en", word, gap_after=gap_around_en))
    return segs


def run(cmd, timeout=60):
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if p.returncode != 0:
        raise SystemExit(f"FAILED: {' '.join(cmd[:3])}\n{p.stderr[-600:]}")


def normalize(src: Path, dst: Path):
    run(["ffmpeg", "-y", "-i", str(src),
         "-ar", str(SR), "-ac", str(CH),
         "-c:a", "pcm_s16le", str(dst)])


def silence(seconds: float, dst: Path):
    run(["ffmpeg", "-y", "-f", "lavfi", "-t", f"{seconds}",
         "-i", f"anullsrc=r={SR}:cl=mono",
         "-c:a", "pcm_s16le", str(dst)])


def vp_synth(text: str, dst: Path):
    raw = dst.with_suffix(".vpraw.wav")
    cmd = [VP_BIN, "-s", text, "-n", VP_NARRATOR, "-o", str(raw), "--speed", "100"]
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


def en_synth(text: str, dst: Path):
    aiff = dst.with_suffix(".aiff")
    run(["say", "-v", EN_VOICE, "-r", "180", "-o", str(aiff), text])
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


def build_one(name: str, segs: list[Seg], out_dir: Path) -> tuple[Path, float]:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        parts: list[Path] = []
        for i, seg in enumerate(segs):
            piece = tmp / f"{name}_{i:02d}_{seg.lang}.wav"
            print(f"  ♪ [{name} {i:02d}] {seg.lang.upper()}  {seg.text[:50]}")
            if seg.lang == "jp":
                vp_synth(seg.text, piece)
            else:
                en_synth(seg.text, piece)
            parts.append(piece)
            if seg.gap_after > 0:
                sil = tmp / f"{name}_sil{i:02d}.wav"
                silence(seg.gap_after, sil)
                parts.append(sil)
        out_wav = out_dir / f"narr_{name}.wav"
        concat(parts, out_wav)
        dur = duration_seconds(out_wav)
        print(f"  → {out_wav.name}  ({dur:.2f}s)")
        return out_wav, dur


def process_quiz(quiz: dict):
    qid = quiz["id"]
    if "body_narration" not in quiz:
        print(f"[skip] {qid} : no body_narration (likely 01_ephemeral reference)")
        return
    word = quiz["word"]
    out_dir = NARR_ROOT / qid
    out_dir.mkdir(exist_ok=True)

    print(f"\n=== {qid} ({word}) ===")
    body_segs = split_by_word(quiz["body_narration"], word)
    body_path, body_dur = build_one("body", body_segs, out_dir)

    quiz_text = f"{word} の意味は？"
    quiz_segs = [Seg("en", word, gap_after=0.10),
                 Seg("jp", "の意味は？")]
    quiz_path, quiz_dur = build_one("quiz", quiz_segs, out_dir)

    meta = {
        "id": qid,
        "word": word,
        "body": {"path": str(body_path), "duration_sec": round(body_dur, 3)},
        "quiz": {"path": str(quiz_path), "duration_sec": round(quiz_dur, 3)},
    }
    (out_dir / "durations.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    import sys
    quizzes = json.loads(QUIZZES_JSON.read_text(encoding="utf-8"))
    targets = sys.argv[1:] if len(sys.argv) > 1 else None
    for q in quizzes:
        if targets and q["id"] not in targets:
            continue
        try:
            process_quiz(q)
        except Exception as e:
            print(f"FAILED {q.get('id')}: {e}")


if __name__ == "__main__":
    main()
