"""既存全ステージの body_ruby から「漢字塊 → 読み」の頻度マップを構築。

これは ground truth として、新規ルビ振り時に上書きする用語辞書になる。
複数読みがある場合は最頻読みをデフォルト、他はバリアントとして記録。

出力: ruby_pipeline/dict_kanji_readings.csv
形式: kanji,top_reading,top_count,alt_readings(JSON)
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

from ruby_core import extract_kanji_groups

# 青空文庫の範囲指定ルビ `｜...《...》` を除外するため、ピュア漢字ルビのみ拾う
import re as _re
PURE_RUBY_RE = _re.compile(r"(?<!｜)([一-鿿々]+)《([぀-ゟ]+)》")

VOCAB_DIR = Path(__file__).resolve().parent.parent / "vocab_sources"
OUT_CSV = Path(__file__).resolve().parent / "dict_kanji_readings.csv"

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
    counter: dict[str, Counter[str]] = {}
    total_fields = 0

    for stage in STAGES:
        path = VOCAB_DIR / f"{stage}_quizzes_clean.json"
        if not path.exists():
            continue
        d = json.loads(path.read_text(encoding="utf-8"))
        for q in d.get("quizzes", []):
            for field in ("body_ruby", "headline_ruby", "explanation_ruby", "choices_ruby"):
                val = q.get(field)
                if not val:
                    continue
                if isinstance(val, list):
                    items = val
                else:
                    items = [val]
                for v in items:
                    if not isinstance(v, str):
                        continue
                    total_fields += 1
                    # ｜直前のルビは除外する: ｜の手前にある《》を識別するのは難しいので、
                    # ｜...《...》パターン全体を取り除いてから漢字ルビを抽出する
                    sanitized = re.sub(r"｜[^《》]+《[぀-ゟ]+》", "", v)
                    for kanji, reading in PURE_RUBY_RE.findall(sanitized):
                        counter.setdefault(kanji, Counter())[reading] += 1

    # 結果: top_reading と alt_readings
    rows = []
    for kanji, cnt in counter.items():
        top = cnt.most_common(1)[0]
        alts = [(r, c) for r, c in cnt.most_common() if r != top[0]]
        rows.append((kanji, top[0], top[1], json.dumps(dict(alts), ensure_ascii=False)))

    rows.sort(key=lambda r: -r[2])

    OUT_CSV.write_text("", encoding="utf-8")
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["kanji", "top_reading", "top_count", "alt_readings_json"])
        for row in rows:
            w.writerow(row)

    print(f"処理フィールド数: {total_fields}")
    print(f"ユニーク漢字塊数: {len(counter)}")
    print(f"出力: {OUT_CSV}")

    # トップ30を表示
    print("\n=== 頻出 top 30 ===")
    for k, t, c, _ in rows[:30]:
        print(f"  {k}\t{t}\t({c})")

    # 複数読みが現れているものの top 20
    print("\n=== 複数読みの top 20 ===")
    multi = [r for r in rows if r[3] != "{}"]
    for k, t, c, alts in multi[:20]:
        print(f"  {k}\t主={t} ({c})\t他={alts}")


if __name__ == "__main__":
    main()
