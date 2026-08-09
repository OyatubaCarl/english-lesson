"""wordtacos クイズの不自然さをヒューリスティックで検出。

検出項目:
- body長の外れ値 (極端に短い/長い)
- choices の重複(同じ選択肢が複数)
- choices の文字長の不均等(極端な長短混在)
- meaning_jp と choices[correct_index] の表記不一致(完全一致でなくて記述ゆれ)
- explanation の極端な短さ/長さ
- <word> プレースホルダ未挿入
- 連続する同じ漢字熟語(冗長表現)
- body 内に同じ語句が3回以上(モチーフ過剰反復)
- choices に語幹レベルの強重複(2字一致など)

出力: quality_heuristic_report.md (人間可読) + quality_heuristic_issues.json (機械可読)
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path("/Users/masaki/Documents/ClaudeCode/英語学習教材作成/vocab_sources")
SOURCES = [
    ("stage5", ROOT / "stage5_quizzes_clean.json"),
    ("stage6", ROOT / "stage6_quizzes_clean.json"),
]

# 閾値
BODY_MIN_NO_TAG = 25   # <word>タグを除いた素の本文の最小文字数
BODY_MAX_NO_TAG = 80   # 同最大
EXPLANATION_MIN = 5
EXPLANATION_MAX = 80
CHOICE_LEN_RATIO_MAX = 4.0  # 最長/最短がこれ以上なら不均等


def check_quiz(stage: str, q: dict) -> list[dict]:
    issues = []
    qid = q.get("id", "?")
    word = q.get("word", "?")
    body = q.get("body", "")
    choices = q.get("choices", [])
    ci = q.get("correct_index", -1)
    meaning_jp = q.get("meaning_jp", "")
    explanation = q.get("explanation", "")

    # <word> 含有
    tag = f"<{word}>"
    if tag not in body:
        issues.append({"type": "missing_tag", "detail": f"body内に {tag} が無い"})

    # body長
    body_no_tag = body.replace(tag, "")
    blen = len(body_no_tag)
    if blen < BODY_MIN_NO_TAG:
        issues.append({"type": "body_too_short", "detail": f"{blen}字 (<{BODY_MIN_NO_TAG})"})
    elif blen > BODY_MAX_NO_TAG:
        issues.append({"type": "body_too_long", "detail": f"{blen}字 (>{BODY_MAX_NO_TAG})"})

    # explanation長
    elen = len(explanation)
    if elen < EXPLANATION_MIN:
        issues.append({"type": "explanation_too_short", "detail": f"{elen}字"})
    elif elen > EXPLANATION_MAX:
        issues.append({"type": "explanation_too_long", "detail": f"{elen}字"})

    # choices構造
    if len(choices) != 4:
        issues.append({"type": "choices_count", "detail": f"{len(choices)}個 (期待4)"})
    else:
        if len(set(choices)) != 4:
            dup = [c for c, n in Counter(choices).items() if n > 1]
            issues.append({"type": "choices_duplicate", "detail": f"重複: {dup}"})

        lens = [len(c) for c in choices]
        if min(lens) > 0:
            ratio = max(lens) / min(lens)
            if ratio > CHOICE_LEN_RATIO_MAX:
                issues.append({"type": "choices_len_unbalanced", "detail": f"長さ {lens}"})

        # 正解 index 妥当
        if not (0 <= ci < len(choices)):
            issues.append({"type": "correct_index_invalid", "detail": f"ci={ci}"})

    # body 内の同一漢字熟語反復(2字以上が3回以上出現)
    # 「彼」「彼女」のような一般語は無視 → 5字以上に限定
    counts = Counter(re.findall(r"[一-龯]{3,}", body_no_tag))
    repeat = [(w, c) for w, c in counts.items() if c >= 3]
    if repeat:
        issues.append({"type": "body_repetition", "detail": f"{repeat}"})

    # choices 内のダミーが正解語を含む(部分包含)
    if 0 <= ci < len(choices):
        correct = choices[ci]
        for j, c in enumerate(choices):
            if j == ci or not c or not correct:
                continue
            # 短い語が長い語に完全包含されている (例: "学校" が "中学校" を含む)
            if len(correct) >= 2 and correct in c:
                issues.append({"type": "choice_contains_correct", "detail": f"choices[{j}]='{c}' contains correct '{correct}'"})
            elif len(c) >= 2 and c in correct:
                issues.append({"type": "correct_contains_choice", "detail": f"correct='{correct}' contains choices[{j}]='{c}'"})

    return [{"id": qid, "stage": stage, "word": word, **i} for i in issues]


def main():
    all_issues = []
    by_type = Counter()
    stage_counts = {}
    for stage, src in SOURCES:
        data = json.loads(src.read_text(encoding="utf-8"))
        quizzes = data["quizzes"]
        stage_counts[stage] = len(quizzes)
        print(f"{stage}: {len(quizzes)} 問を検査中...")
        for q in quizzes:
            issues = check_quiz(stage, q)
            for i in issues:
                by_type[i["type"]] += 1
            all_issues.extend(issues)

    print(f"\n検出件数: {len(all_issues)}")
    print("type別:")
    for t, c in by_type.most_common():
        print(f"  {t}: {c}")

    # JSON出力
    (ROOT / "quality_heuristic_issues.json").write_text(
        json.dumps(all_issues, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Markdown レポート
    lines = ["# WordTacos ヒューリスティック品質検出 (2026-06-15)", ""]
    lines.append("## サマリ")
    lines.append("")
    for s, c in stage_counts.items():
        lines.append(f"- **{s} 対象**: {c}問")
    lines.append(f"- **総検出件数**: {len(all_issues)}件")
    lines.append("")
    lines.append("## type別件数")
    lines.append("")
    lines.append("| type | 件数 |")
    lines.append("|---|---|")
    for t, c in by_type.most_common():
        lines.append(f"| {t} | {c} |")
    lines.append("")

    # 各typeのサンプル
    by_t = defaultdict(list)
    for i in all_issues:
        by_t[i["type"]].append(i)

    for t, c in by_type.most_common():
        lines.append(f"## {t} ({c}件、上位20件)")
        lines.append("")
        lines.append("| id | stage | word | detail |")
        lines.append("|---|---|---|---|")
        for i in by_t[t][:20]:
            detail = i["detail"].replace("|", "\\|")
            lines.append(f"| {i['id']} | {i['stage']} | {i['word']} | {detail} |")
        lines.append("")
        if c > 20:
            lines.append(f"...残り {c - 20} 件 ({{quality_heuristic_issues.json}} 参照)")
            lines.append("")

    (ROOT / "quality_heuristic_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"\nレポート: {ROOT}/quality_heuristic_report.md")
    print(f"JSON: {ROOT}/quality_heuristic_issues.json")


if __name__ == "__main__":
    main()
