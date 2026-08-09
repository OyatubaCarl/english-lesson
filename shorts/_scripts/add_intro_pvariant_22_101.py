#!/usr/bin/env python3
"""quizzes.json の 22-101 (80件) に intro_overlay と paper_variant を追加。
既存02-21の paper_variant 20種類をローテーションで割り当てる。
- 22-61 (難単語): intro = "超 難単語 が 一発で 覚えられる 裏技 !"
- 62-101 (易単語): intro = "知らない 単語 でも 一発で 覚える 裏技 !"
"""
import json
from pathlib import Path

QPATH = Path("/Users/masaki/Documents/ClaudeCode/英語学習教材作成/shorts/quizzes.json")
data = json.loads(QPATH.read_text(encoding="utf-8"))

# 既存 02-21 (20件) の paper_variant を取得してプール化
pool = []
for q in data:
    if q["id"].startswith(("0", "1")) and q["id"] != "01_ephemeral":
        if "paper_variant" in q:
            pool.append(q["paper_variant"])
print(f"paper_variant pool: {len(pool)} variants")

HEADER_HARD = "超 難単語 が 一発で 覚えられる 裏技 !"
HEADER_EASY = "知らない 単語 でも 一発で 覚える 裏技 !"

# 22-61 → 難単語 (40件), 62-101 → 易単語 (40件)
hard_count = 0
easy_count = 0
for q in data:
    qid = q["id"]
    try:
        num = int(qid.split("_")[0])
    except ValueError:
        continue
    if num < 22:
        continue
    if num <= 61:
        header = HEADER_HARD
        idx = hard_count % len(pool)
        hard_count += 1
    else:
        header = HEADER_EASY
        idx = easy_count % len(pool)
        easy_count += 1
    q["intro_overlay"] = {
        "header": header,
        "word_position_y": 1100,
    }
    q["paper_variant"] = pool[idx]

QPATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                 encoding="utf-8")
print(f"hard added: {hard_count}, easy added: {easy_count}")
