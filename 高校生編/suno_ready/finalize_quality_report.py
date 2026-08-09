#!/usr/bin/env python3
"""Choose one song per lesson and write the final Suno QA/adoption reports."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SHEETS = ROOT / "H046-H160"
GENERATED = ROOT / "generated"
AUDIO = GENERATED / "audio"
PROGRESS_PATH = GENERATED / "bulk_progress.json"
THIRD_PATH = GENERATED / "third_candidate_progress.json"

THIRD_PASS = {68, 97, 104, 120, 128, 130, 148}
THIRD_OMISSION_ONLY = {155}
EQUIVALENT_SECOND = {67, 70, 123, 126, 133, 138}
FORCE_SECOND = {93, 149}
FORCE_FIRST = {91}
UNRESOLVED_BEST = {
    56: 2,
    57: 2,
    81: 3,
    108: 3,
    109: 3,
    117: 2,
    134: 3,
    135: 3,
    157: 2,
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def title_for(lesson: int) -> str:
    text = (SHEETS / f"H{lesson:03d}.md").read_text(encoding="utf-8")
    match = re.search(r"## Suno Title\s+```text\s*\n(.*?)\n```", text, re.S)
    if not match:
        raise ValueError(f"Missing title: H{lesson:03d}")
    return match.group(1).strip()


def qa(lesson: int, candidate: int, mlx: bool = False) -> dict:
    suffix = "_QA_mlx.json" if mlx else "_QA.json"
    return load_json(AUDIO / f"H{lesson:03d}" / f"candidate{candidate}{suffix}")


def choose(lesson: int) -> tuple[int, str, str]:
    if lesson in THIRD_PASS:
        return 3, "PASS", "第3候補で置換疑い解消"
    if lesson in THIRD_OMISSION_ONLY:
        return 3, "PASS_NO_WRONG_LYRIC_OMISSION", "第3候補で誤語解消、脱落のみ残存"
    if lesson in UNRESOLVED_BEST:
        candidate = UNRESOLVED_BEST[lesson]
        report = qa(lesson, candidate, mlx=True)
        replacements = []
        for row in report["replacement_spans"]:
            if row.get("actual_confidence", 0.0) >= 0.72:
                replacements.append(
                    f"{' '.join(row['expected'])}→{' '.join(row['actual'])}"
                )
        note = "3曲で停止・要確認: " + ", ".join(replacements)
        return candidate, "REVIEW_STOPPED_AFTER_3", note
    if lesson in EQUIVALENT_SECOND:
        return 2, "PASS_EQUIVALENT", "表記分割・英米綴り・同音語のみ"
    if lesson in FORCE_SECOND:
        if lesson == 93:
            return 2, "PASS", "第2候補で大きな脱落を解消"
        return 2, "PASS_NO_WRONG_LYRIC_OMISSION", "誤語なし、第1候補より脱落を優先"
    if lesson in FORCE_FIRST:
        return 1, "PASS_EQUIVALENT", "第2候補は大きな脱落、第1候補の英米綴り差のみ"

    first = qa(lesson, 1)
    if first["verdict"] == "PASS":
        return 1, "PASS", "第1候補合格"
    if first["verdict"] == "REVIEW_WRONG_LYRIC":
        second = qa(lesson, 2)
        if second["verdict"] == "PASS":
            return 2, "PASS", "第2候補で置換疑い解消"
        mlx_path = AUDIO / f"H{lesson:03d}" / "candidate2_QA_mlx.json"
        if mlx_path.exists():
            second_mlx = load_json(mlx_path)
            if second_mlx["verdict"] == "PASS":
                return 2, "PASS", "高精度再検査で置換疑い解消"
    raise ValueError(f"No final decision rule for H{lesson:03d}")


def main() -> None:
    progress = load_json(PROGRESS_PATH)
    third = load_json(THIRD_PATH)
    adopted = {}
    markdown = [
        "# 高校生編 H048〜H160 採用曲一覧（歌詞QA後）",
        "",
        "- 判定優先順位：誤った歌詞・語句の置換を最優先、次に脱落・構成。",
        "- 置換疑いが残る曲は最大3曲まで検査し、改善しない場合は再生成を停止。",
        "- Sunoが同時生成した未検査の追加候補は採用判定に使用していない。",
        "",
        "| Lesson | Title | 採用候補 | QA | 採用リンク | 備考 |",
        "|---:|---|---:|---|---|---|",
    ]
    counts = {}
    for lesson in range(48, 161):
        candidate, status, note = choose(lesson)
        row = progress["lessons"][str(lesson)]
        if candidate == 1:
            url = row["first"]
        elif candidate == 2:
            url = row["backup"]
        else:
            url = third["lessons"][str(lesson)]["third"]
        title = title_for(lesson)
        adopted[str(lesson)] = {
            "title": title,
            "adopted_candidate": candidate,
            "adopted_url": url,
            "qa_status": status,
            "note": note,
        }
        row["adopted"] = url
        row["adopted_candidate"] = candidate
        row["status"] = "adopted" if status != "REVIEW_STOPPED_AFTER_3" else "provisional_review"
        row["qa"] = status
        counts[status] = counts.get(status, 0) + 1
        markdown.append(
            f"| H{lesson:03d} | {title.replace('|', '／')} | {candidate} | {status} | "
            f"[Suno]({url}) | {note.replace('|', '／')} |"
        )

    markdown.extend([
        "",
        "## 集計",
        "",
        *[f"- {key}: {value}曲" for key, value in sorted(counts.items())],
        "",
        "## 3曲で打ち切った要確認レッスン",
        "",
        ", ".join(f"H{lesson:03d}" for lesson in sorted(UNRESOLVED_BEST)),
        "",
    ])
    progress["policy"] = (
        "Generate all first, prioritize wrong-word substitutions over omissions, "
        "inspect at most three songs per lesson, and record one adopted/provisional song."
    )
    PROGRESS_PATH.write_text(json.dumps(progress, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (GENERATED / "adopted_songs.json").write_text(
        json.dumps({"counts": counts, "lessons": adopted}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report_path = GENERATED / "H048-H160_adopted_2026-08-02.md"
    report_path.write_text("\n".join(markdown), encoding="utf-8")
    print(json.dumps({
        "report": str(report_path),
        "adopted_json": str(GENERATED / "adopted_songs.json"),
        "counts": counts,
        "total": len(adopted),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
