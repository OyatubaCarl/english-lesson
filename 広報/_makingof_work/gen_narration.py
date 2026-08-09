#!/usr/bin/env python3
"""メイキング動画用ナレーション8本を VoicePeak で生成（タイムアウト+リトライ付き）。"""
from __future__ import annotations
import subprocess, time
from pathlib import Path

WORK = Path(__file__).resolve().parent
VP = "/Applications/voicepeak.app/Contents/MacOS/voicepeak"
VP_NARRATOR = "Japanese Female 1"
VP_TIMEOUT = 60

NARRATIONS = [
    "この英語アプリ、じつは、AIといっしょに作りました。",
    "ワードタコスは、日本語まじりの文で英単語を覚えるクイズアプリ。",
    "タコスパーティーは、5つのミニゲームで具材を集める学習ゲームです。",
    "なにを作るか、教材の中身、最後のチェックは、人間の仕事。",
    "プログラムは、AIと相談しながら、対話で組み立てていきます。",
    "キャラクターも背景も、画像生成AIとの共同作業。",
    "音声は合成音声、歌は音楽AI。ぜんぶローカルとブラウザで完結。",
    "無料で、ブラウザだけ。ぜひ遊んでみてください。",
]


def vp(text: str, out: Path) -> None:
    out.unlink(missing_ok=True)
    for _attempt in range(5):
        try:
            subprocess.run(
                [VP, "-s", text, "-n", VP_NARRATOR, "-o", str(out), "--speed", "110"],
                check=True, capture_output=True, text=True, timeout=VP_TIMEOUT)
        except subprocess.TimeoutExpired:
            subprocess.run(["pkill", "-f", "voicepeak -s"], capture_output=True)
            time.sleep(1.5)
        except subprocess.CalledProcessError:
            pass
        if out.exists() and out.stat().st_size > 2000:
            return
        time.sleep(1.5)
    raise RuntimeError(f"VoicePeak failed after retries: {text[:30]}")


def main() -> None:
    for i, text in enumerate(NARRATIONS, 1):
        out = WORK / f"narr{i}.wav"
        if out.exists() and out.stat().st_size > 2000:
            print(f"  skip narr{i}.wav (exists)")
            continue
        vp(text, out)
        print(f"  ok narr{i}.wav ({out.stat().st_size} bytes)")
    print("done")


if __name__ == "__main__":
    main()
