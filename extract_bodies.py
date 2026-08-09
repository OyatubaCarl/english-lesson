"""各ステージJSONからbodyだけを抽出して、自然さチェック用のテキストファイルにする。

出力: /tmp/wt_bodies/{stage_id}_bodies.txt
形式: 「[index] word: body」 を1行ずつ
"""
from __future__ import annotations

import json
from pathlib import Path

VOCAB_DIR = Path(__file__).resolve().parent / "vocab_sources"
OUT_DIR = Path("/tmp/wt_bodies")
OUT_DIR.mkdir(exist_ok=True)

STAGES = [
    "stage1",
    "stage2",
    "stage3",
    "stage4",
    "stage5",
    "stage6",
    "stage_toeic_basic",
    "stage_toeic_mid",
    "stage_toeic_high",
    "stage_toeic_expert",
]


def main() -> None:
    for stage in STAGES:
        src = VOCAB_DIR / f"{stage}_quizzes_clean.json"
        if not src.exists():
            print(f"skip: {src} not found")
            continue
        d = json.loads(src.read_text(encoding="utf-8"))
        out = OUT_DIR / f"{stage}_bodies.txt"
        lines: list[str] = []
        for i, q in enumerate(d.get("quizzes", []), start=1):
            word = q.get("word", "?")
            body = q.get("body", "")
            lines.append(f"[{i:04d}] {word}: {body}")
        out.write_text("\n".join(lines), encoding="utf-8")
        print(f"{stage}: {len(lines)} lines -> {out}")


if __name__ == "__main__":
    main()
