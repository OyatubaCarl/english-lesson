"""ルビ品質サニティチェック。

検査項目:
1. 全漢字カバー: body 中の漢字すべてに body_ruby でルビがついているか
2. ルビ形式: 《...》 中身がひらがなのみか (カタカナ混入はバグ)
3. 文脈別読みの矛盾: 同じ漢字塊が同一ステージ内で異なる読みを持つ場合に警告
4. 空 body_ruby: もし発生していたら検出
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

VOCAB_DIR = Path(__file__).resolve().parent.parent / "vocab_sources"

KANJI_RE = re.compile(r"[一-鿿々]")
RUBY_RE = re.compile(r"([一-鿿々]+)《([぀-ゟ]+)》")
RUBY_BAD_RE = re.compile(r"《([ぁ-ゔ぀-ゟ゠-ヿ]+)》")

STAGES = [
    "stage_toeic_expert",
    "stage_toeic_high",
    "stage_toeic_mid",
]


def strip_ruby(text: str) -> str:
    """ルビを取り除いて原文を復元。"""
    s = re.sub(r"《[぀-ゟぁ-ゔ゠-ヿ]+》", "", text)
    s = s.replace("｜", "")
    return s


def uncovered_kanji(body: str, body_ruby: str) -> list[str]:
    """body_ruby でルビが振られていない漢字を返す。

    手順:
    1. ｜...《...》 範囲指定ルビをまず除去 (範囲内の漢字は全部カバー扱い)
    2. 漢字《読み》 を除去
    3. <word> タグを除去
    4. 残った文字列に漢字があれば未カバー
    """
    no_ruby = re.sub(r"｜[^《》]+《[぀-ゟぁ-ゔ゠-ヿ]+》", "", body_ruby)
    no_ruby = re.sub(r"([一-鿿々]+)《[぀-ゟぁ-ゔ゠-ヿ]+》", "", no_ruby)
    no_ruby = re.sub(r"<[^>]+>", "", no_ruby)
    uncovered: list[str] = []
    for ch in no_ruby:
        if KANJI_RE.match(ch):
            uncovered.append(ch)
    return uncovered


def main() -> None:
    total_quizzes = 0
    total_uncovered = 0
    uncovered_examples: list[tuple[str, str, str, list[str]]] = []
    bad_ruby: list[tuple[str, str, str]] = []
    empty_ruby: list[tuple[str, str]] = []
    # 同じ漢字塊の読みバリエーション
    reading_variants: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))

    for stage in STAGES:
        path = VOCAB_DIR / f"{stage}_quizzes_clean.json"
        d = json.loads(path.read_text(encoding="utf-8"))
        for q in d["quizzes"]:
            total_quizzes += 1
            body = q.get("body", "")
            body_ruby = q.get("body_ruby", "")
            if not body_ruby:
                empty_ruby.append((stage, q["word"]))
                continue
            # 空でないが body == body_ruby (ルビ未付与の残骸)
            if body_ruby == body and KANJI_RE.search(body):
                empty_ruby.append((stage, q["word"]))
                continue
            # ルビ中身がひらがな以外を含む
            for m in RUBY_BAD_RE.finditer(body_ruby):
                inner = m.group(1)
                # カタカナが含まれていたら NG
                if re.search(r"[゠-ヿ]", inner):
                    bad_ruby.append((stage, q["word"], inner))
            # 未カバー漢字
            uncov = uncovered_kanji(body, body_ruby)
            if uncov:
                total_uncovered += len(uncov)
                if len(uncovered_examples) < 50:
                    uncovered_examples.append((stage, q["word"], body_ruby, uncov))
            # 同じ漢字塊の読みを集計
            for m in RUBY_RE.finditer(body_ruby):
                k = m.group(1)
                r = m.group(2)
                reading_variants[stage][k].add(r)

    print(f"検査クイズ数: {total_quizzes}")
    print(f"空ルビ / 未付与: {len(empty_ruby)} 件")
    if empty_ruby[:5]:
        for s, w in empty_ruby[:5]:
            print(f"  - {s}/{w}")
    print(f"カタカナルビ (NG): {len(bad_ruby)} 件")
    print(f"未カバー漢字: {total_uncovered} 件 (発生例文 {len(uncovered_examples)} 件)")
    if uncovered_examples[:10]:
        print("\n=== 未カバー漢字の例 ===")
        for s, w, ruby, chars in uncovered_examples[:10]:
            print(f"  [{s}/{w}] 未カバー={chars}")
            print(f"    {ruby}")

    # 同一ステージ内で複数読みを持つ漢字塊
    print("\n=== 多義読みの注意 (同一ステージ内で2読み以上) ===")
    n_multi = 0
    for stage, kmap in reading_variants.items():
        for k, rs in kmap.items():
            if len(rs) > 1:
                n_multi += 1
                if n_multi <= 30:
                    print(f"  [{stage}] {k}: {sorted(rs)}")
    print(f"  合計: {n_multi} 件")


if __name__ == "__main__":
    main()
