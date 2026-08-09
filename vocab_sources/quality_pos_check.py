"""<word>直後の品詞ミスマッチを全件機械検出。

LLMレビュー(chunk4)で「副詞+に」「副詞+な」「形容詞+な不一致」等が多発と判明。
パターン:
- 副詞の直後に「な」(形容動詞的使用) - bad
- 副詞の直後に「に」(冗長連用化) - warn (副詞単独でいい)
- 副詞の直後に「と」(冗長) - warn
- 副詞の直後に「の」(連体化、誤) - warn
- 動詞の直後に「のような」「な」(名詞的使用) - bad
- 形容詞の直後に「に」「と」(誤) - warn
- 名詞の直後に「する」(動詞化、語によってOK) - warn

複合品詞(副/形, 名/動 等)は文脈的に許容する場合があるが、フラグはする。
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path("/Users/masaki/Documents/ClaudeCode/英語学習教材作成/vocab_sources")
SOURCES = [
    ("stage5", ROOT / "stage5_quizzes_clean.json"),
    ("stage6", ROOT / "stage6_quizzes_clean.json"),
]

# 品詞別「直後に来てはいけない助詞・語尾」 (パターン -> severity)
# severity: "bad" = 明確な品詞ミスマッチ、"warn" = 冗長・不自然
PATTERNS = {
    "副": [
        ("な", "bad"),       # <副>な → 形容動詞化
        ("のような", "bad"), # <副>のような → 名詞化
    ],
    "形": [
        ("する", "bad"),     # <形>する → 動詞化
        ("された", "bad"),
        ("された", "bad"),
        ("のような", "warn"),
    ],
    "動": [
        ("な", "bad"),       # <動>な → 形容動詞化
        ("のような", "bad"), # <動>のような → 名詞化
    ],
    "名": [
        # 名詞+な は形容動詞的、許容範囲が広い(美しいなジャズ等)
        # 名詞+と が一律ダメではない
    ],
}


def check_quiz(stage: str, q: dict) -> list[dict]:
    issues = []
    word = q.get("word", "")
    body = q.get("body", "")
    pos = q.get("pos", "")
    tag = f"<{word}>"

    if tag not in body:
        return issues
    after_idx = body.find(tag) + len(tag)
    after = body[after_idx:after_idx + 8]  # 直後8文字

    # pos が「副」のみ or 「副/...」の場合のみ「副」パターン適用
    # 「形/副」「動/副」など複合の場合は副副パターン適用しない(文脈次第)
    if pos == "副":
        for pat, sev in PATTERNS["副"]:
            if after.startswith(pat):
                issues.append({
                    "id": q["id"], "stage": stage, "word": word, "pos": pos,
                    "severity": sev, "type": "pos_mismatch_adverb_" + pat,
                    "detail": f"副詞 + 「{pat}」: ...<{word}>{after[:6]}...",
                })
    elif pos == "形":
        for pat, sev in PATTERNS["形"]:
            if after.startswith(pat):
                issues.append({
                    "id": q["id"], "stage": stage, "word": word, "pos": pos,
                    "severity": sev, "type": "pos_mismatch_adjective_" + pat,
                    "detail": f"形容詞 + 「{pat}」: ...<{word}>{after[:6]}...",
                })
    elif pos == "動":
        for pat, sev in PATTERNS["動"]:
            if after.startswith(pat):
                issues.append({
                    "id": q["id"], "stage": stage, "word": word, "pos": pos,
                    "severity": sev, "type": "pos_mismatch_verb_" + pat,
                    "detail": f"動詞 + 「{pat}」: ...<{word}>{after[:6]}...",
                })

    # 副詞の冗長連用化(副 + 「に」「と」) ← 単独で使うべき
    # ただし「ふと」「すでに」など固有副詞+に/と は文中で別単語の可能性あり
    # ここでは <副> の直後を狭く捕捉
    if pos == "副":
        if after.startswith("に") and not after.startswith("にも") and not after.startswith("には"):
            issues.append({
                "id": q["id"], "stage": stage, "word": word, "pos": pos,
                "severity": "warn", "type": "adverb_redundant_ni",
                "detail": f"副詞+「に」(冗長): ...<{word}>{after[:6]}...",
            })
        elif after.startswith("と") and not after.startswith("とき") and not after.startswith("と思"):
            issues.append({
                "id": q["id"], "stage": stage, "word": word, "pos": pos,
                "severity": "warn", "type": "adverb_redundant_to",
                "detail": f"副詞+「と」(冗長): ...<{word}>{after[:6]}...",
            })

    return issues


def main():
    all_issues = []
    by_type = Counter()
    by_sev = Counter()
    by_word = Counter()
    for stage, src in SOURCES:
        data = json.loads(src.read_text(encoding="utf-8"))
        for q in data["quizzes"]:
            for i in check_quiz(stage, q):
                all_issues.append(i)
                by_type[i["type"]] += 1
                by_sev[i["severity"]] += 1
                by_word[(i["word"], i["pos"])] += 1

    print(f"\n品詞ミスマッチ検出: {len(all_issues)} 件")
    print("severity:")
    for s, c in by_sev.most_common():
        print(f"  {s}: {c}")
    print("type別 (top10):")
    for t, c in by_type.most_common(10):
        print(f"  {t}: {c}")

    # JSON出力
    (ROOT / "quality_pos_issues.json").write_text(
        json.dumps(all_issues, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Markdown
    lines = ["# WordTacos <word>直後品詞ミスマッチ検出 (2026-06-16)", ""]
    lines.append("## サマリ")
    lines.append("")
    lines.append(f"- **総検出件数**: {len(all_issues)}件")
    for s, c in by_sev.most_common():
        lines.append(f"- **{s}**: {c}件")
    lines.append("")
    lines.append("## type別件数")
    lines.append("| type | 件数 |")
    lines.append("|---|---|")
    for t, c in by_type.most_common():
        lines.append(f"| {t} | {c} |")
    lines.append("")

    # bad全件
    bads = [i for i in all_issues if i["severity"] == "bad"]
    lines.append(f"## bad 全{len(bads)}件 (明確な品詞ミスマッチ)")
    lines.append("")
    lines.append("| id | stage | word | pos | 内容 |")
    lines.append("|---|---|---|---|---|")
    for i in bads:
        d = i["detail"].replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {i['id']} | {i['stage']} | {i['word']} | {i['pos']} | {d} |")
    lines.append("")

    # warn上位50
    warns = [i for i in all_issues if i["severity"] == "warn"]
    lines.append(f"## warn 上位50件 (全{len(warns)}件中)")
    lines.append("")
    lines.append("| id | stage | word | pos | 内容 |")
    lines.append("|---|---|---|---|---|")
    for i in warns[:50]:
        d = i["detail"].replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {i['id']} | {i['stage']} | {i['word']} | {i['pos']} | {d} |")
    lines.append("")
    if len(warns) > 50:
        lines.append(f"...残り {len(warns) - 50} 件は quality_pos_issues.json 参照")

    (ROOT / "quality_pos_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"\nレポート: {ROOT}/quality_pos_report.md")
    print(f"JSON: {ROOT}/quality_pos_issues.json")


if __name__ == "__main__":
    main()
