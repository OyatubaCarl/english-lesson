#!/usr/bin/env python3
"""アプリ紹介ショート用ナレーション7本を VoicePeak で生成（タイムアウト+リトライ付き）。"""
from __future__ import annotations

import subprocess
import time
from pathlib import Path

WORK = Path(__file__).resolve().parent
VP = "/Applications/voicepeak.app/Contents/MacOS/voicepeak"
VP_NARRATOR = "Japanese Female 1"
VP_TIMEOUT = 60

NARRATIONS = [
    "歌と、日本語と、ミニゲームで。楽しく学ぶ英語アプリです。",
    "歌にあわせて、単語をキャッチ。リズムゲームの、タコビート。",
    "日本語まじりの文だから、はじめての単語も、意味がわかる。",
    "文法クイズでサルサを調合。ならべかえで、レタスもりもり。",
    "声に出して読めば、チーズがとろける。",
    "具材を集めて、タコスを、完成させよう。",
    "無料で、ブラウザだけ。きょうから、あそべます。",
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
        out = WORK / f"intro_narr{i}.wav"
        if out.exists() and out.stat().st_size > 2000:
            print(f"  skip intro_narr{i}.wav (exists)")
            continue
        vp(text, out)
        print(f"  ok intro_narr{i}.wav ({out.stat().st_size} bytes)")
    print("done")


if __name__ == "__main__":
    main()
