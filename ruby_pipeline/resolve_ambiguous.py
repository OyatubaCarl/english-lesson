"""hard ambiguous の文脈解決を Claude Code (Opus) で行ったあと、
その判定を該当 quiz の body_ruby に反映する。

漢字塊+周辺文字パターンでマッチして上書き。
"""
from __future__ import annotations

import json
import re
from pathlib import Path

VOCAB_DIR = Path(__file__).resolve().parent.parent / "vocab_sources"

# (stage, word, search_pattern, replacement) のタプルで指定
# search_pattern と replacement は body_ruby に対する find/replace
RESOLUTIONS: list[tuple[str, str, str, str]] = [
    # [expert#112] leverage: 「ブランド力」の「力」は音読み「りょく」
    (
        "stage_toeic_expert",
        "leverage",
        "ブランド力《ちから》",
        "ブランド力《りょく》",
    ),
    # [expert#137] trough: 「その後」は「そのご」(フォーマル)
    (
        "stage_toeic_expert",
        "trough",
        "その後《あと》はゆるやかに",
        "その後《ご》はゆるやかに",
    ),
    # [expert#183] utilitarian: 「考え方」 — 考 にルビが付かず、方 が「ほう」になっている
    (
        "stage_toeic_expert",
        "utilitarian",
        "考え方《ほう》",
        "考《かんが》え方《かた》",
    ),
    # [high#142] cargo: 「コンテナ船」の「船」は音読み「せん」
    (
        "stage_toeic_high",
        "cargo",
        "コンテナ船《ふね》",
        "コンテナ船《せん》",
    ),
    # [expert] juncture: 「待つ方がよい」 — 方は「ほう」(=「方法、選択肢」)
    (
        "stage_toeic_expert",
        "juncture",
        "待《ま》つ方《かた》",
        "待《ま》つ方《ほう》",
    ),
]


def main() -> None:
    applied = 0
    not_found = []
    for stage, word, src, dst in RESOLUTIONS:
        path = VOCAB_DIR / f"{stage}_quizzes_clean.json"
        d = json.loads(path.read_text(encoding="utf-8"))
        ok = False
        for q in d["quizzes"]:
            if q["word"] != word:
                continue
            ruby = q.get("body_ruby", "")
            if src in ruby:
                q["body_ruby"] = ruby.replace(src, dst)
                ok = True
                applied += 1
                print(f"  {stage}/{word}: {src!r} -> {dst!r}")
                break
        if ok:
            path.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
        else:
            not_found.append((stage, word, src))

    print(f"\n適用: {applied} 件")
    if not_found:
        print(f"未検出: {len(not_found)} 件")
        for s, w, src in not_found:
            print(f"  {s}/{w}: {src!r}")


if __name__ == "__main__":
    main()
