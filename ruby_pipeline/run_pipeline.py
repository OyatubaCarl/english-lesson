"""WordTacos 新規例文 (C1 + toeic_high + toeic_mid テンプレ置換分) にルビを振る。

ステージ別に対象を判定し、body_ruby を再生成。
hard ambiguous (両エンジン不一致) を /tmp/wt_ambiguous.json に書き出し、後段の LLM 解決へ。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from apply_ruby import add_ruby_to_text, load_dictionary

VOCAB_DIR = Path(__file__).resolve().parent.parent / "vocab_sources"

# 対象ステージと、ルビを振る単語の選び方:
# - stage_toeic_expert: 全 200 単語 (前回 C1 で作った新規例文すべて)
# - stage_toeic_high:   116 単語 (今回テンプレ置換した分)
# - stage_toeic_mid:    2 単語 (quite, found)

TARGETS = {
    "stage_toeic_expert": None,  # None = 全 quiz
    "stage_toeic_high": "templates",  # 今回テンプレ置換した分
    "stage_toeic_mid": "templates",
}


def is_unrubied(q: dict) -> bool:
    """この quiz の body_ruby にルビ (《》) が一切ついていないかを判定。

    True: body_ruby == body (= ルビ未付与、新規テンプレ置換分など) → ルビを振る対象
    False: 何らかのルビが入っている → 既存品質を維持するため触らない
    """
    body = q.get("body", "")
    body_ruby = q.get("body_ruby", "")
    if not body_ruby:
        return True
    # 漢字でない部分のルビ「《》」が一つでもあれば既存ルビ有り
    return ("《" not in body_ruby) and (body_ruby == body)


def main() -> None:
    dicts = load_dictionary()
    top, polysemous, overrides = dicts
    print(f"辞書: top={len(top)} polysemous={len(polysemous)} overrides={len(overrides)}")

    all_ambiguous: list[dict] = []
    total_processed = 0

    for stage, target_kind in TARGETS.items():
        path = VOCAB_DIR / f"{stage}_quizzes_clean.json"
        d = json.loads(path.read_text(encoding="utf-8"))
        rewritten = 0
        ambiguous_count = 0
        for idx, q in enumerate(d["quizzes"], start=1):
            should_apply = False
            if target_kind is None:
                should_apply = True
            elif target_kind == "templates":
                should_apply = is_unrubied(q)
            if not should_apply:
                continue
            body = q.get("body", "")
            if not body:
                continue
            ruby, amb = add_ruby_to_text(body, top, polysemous, overrides)
            q["body_ruby"] = ruby
            rewritten += 1
            if amb:
                ambiguous_count += len(amb)
                all_ambiguous.append({
                    "stage": stage,
                    "idx": idx,
                    "word": q["word"],
                    "body": body,
                    "ruby_draft": ruby,
                    "ambiguous": [
                        {"kanji": k, "sud": sr, "mec": mr, "draft": best}
                        for k, sr, mr, best in amb
                    ],
                })
        path.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{stage}: ルビ付与 {rewritten} 件 (hard ambiguous {ambiguous_count} 件)")
        total_processed += rewritten

    Path("/tmp/wt_ambiguous.json").write_text(
        json.dumps(all_ambiguous, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n合計 {total_processed} 件処理")
    print(f"hard ambiguous: {len(all_ambiguous)} 文に発生")
    print(f"→ /tmp/wt_ambiguous.json")


if __name__ == "__main__":
    main()
