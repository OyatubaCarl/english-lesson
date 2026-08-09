"""ふりがなチェック用の読み上げ音声を生成する.

- body_kana(= ふりがな読みそのもの)を macOS say (Kyoko) で読み上げ
- 「N番。」の番号アナウンス付き → 耳で聞いて違和感の番号をメモ → 修正
- 45問ずつのチャンクで m4a 出力(audio_check/)
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path("/Users/masaki/Documents/ClaudeCode/英語学習教材作成/vocab_sources")
SRC = ROOT / "stage1_quizzes_clean.json"
OUT = ROOT / "audio_check"
CHUNK = 45
VOICE = "Kyoko"
RATE = "190"

OUT.mkdir(exist_ok=True)

data = json.loads(SRC.read_text(encoding="utf-8"))
quizzes = data["quizzes"]

chunks = [quizzes[i:i+CHUNK] for i in range(0, len(quizzes), CHUNK)]
print(f"全{len(quizzes)}問 → {len(chunks)}チャンク")

for ci, chunk in enumerate(chunks, 1):
    lines = []
    for qi, q in enumerate(chunk):
        n = ci_offset = (ci - 1) * CHUNK + qi + 1
        kana = q["body_kana"]
        # <word> → 前後スペース付き英語(Kyokoがそれなりに読む)
        kana = re.sub(r"<([^>]+)>", r" \1 ", kana)
        lines.append(f"{n}番。{kana}")
    text = "\n".join(lines)

    txt = OUT / f"chunk_{ci:02d}.txt"
    txt.write_text(text, encoding="utf-8")

    aiff = OUT / f"chunk_{ci:02d}.aiff"
    m4a = OUT / f"wordtacos_check_{ci:02d}.m4a"

    subprocess.run(
        ["say", "-v", VOICE, "-r", RATE, "-f", str(txt), "-o", str(aiff)],
        check=True,
    )
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(aiff),
         "-ac", "1", "-b:a", "64k", str(m4a)],
        check=True,
    )
    aiff.unlink()
    size_kb = m4a.stat().st_size / 1024
    print(f"  [{ci}/{len(chunks)}] {m4a.name}  ({size_kb:.0f} KB)")

print("\n✅ 完了: audio_check/wordtacos_check_01〜{:02d}.m4a".format(len(chunks)))
