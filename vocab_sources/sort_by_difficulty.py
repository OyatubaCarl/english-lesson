"""WordTacosクイズを難易度順にソート(同ステージ内で easy→hard)。

スコア = 単語長 × 1.0 + 漢字密度(0-1) × 30 + body文字数 × 0.2 + 選択肢平均文字数 × 0.5

漢字密度: bodyの漢字数 ÷ body総字数(<word>タグ除く)
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
KANJI_RE = re.compile(r"[一-龯々〆ヶ]")


def difficulty_score(q: dict) -> float:
    word = q["word"]
    body = q["body"]
    body_no_tag = body.replace(f"<{word}>", "").replace("<", "").replace(">", "")
    kanji_count = len(KANJI_RE.findall(body_no_tag))
    total_chars = max(1, len(body_no_tag))
    kanji_density = kanji_count / total_chars
    choice_avg = sum(len(c) for c in q.get("choices", [])) / max(1, len(q.get("choices", [])))
    score = (
        len(word) * 1.0
        + kanji_density * 30
        + len(body) * 0.2
        + choice_avg * 0.5
    )
    return score


def main() -> None:
    for fp in [
        "stage1_quizzes_clean.json",
        "stage2_quizzes_clean.json",
        "stage3_quizzes_clean.json",
        "stage4_quizzes_clean.json",
        "stage5_quizzes_clean.json",
        "stage6_quizzes_clean.json",
    ]:
        p = ROOT / fp
        d = json.loads(p.read_text(encoding="utf-8"))
        quizzes = d["quizzes"]
        # スコア付与 + ソート
        sorted_qs = sorted(quizzes, key=difficulty_score)
        # 元のidを保持して `order` フィールド付与
        for i, q in enumerate(sorted_qs):
            q["order"] = i + 1
        d["quizzes"] = sorted_qs
        d["sorted_by"] = "difficulty_ascending"
        p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
        # サンプル表示
        print(f"{fp}: {len(quizzes)} quizzes sorted")
        print(f"  easiest 3: {[(q['word'], round(difficulty_score(q), 1)) for q in sorted_qs[:3]]}")
        print(f"  hardest 3: {[(q['word'], round(difficulty_score(q), 1)) for q in sorted_qs[-3:]]}")
        print()


if __name__ == "__main__":
    main()
