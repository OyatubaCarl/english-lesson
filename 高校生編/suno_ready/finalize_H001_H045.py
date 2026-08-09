#!/usr/bin/env python3
"""Finalize one adopted Suno song per H001-H045 after MLX Whisper lyric QA."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SHEETS = ROOT / "H001-H045"
GENERATED = ROOT / "generated"
AUDIO = GENERATED / "audio"
REWRITE_AUDIO = GENERATED / "rewrite_audio"
INITIAL = GENERATED / "H001-H045_initial_candidates.json"
THIRD = GENERATED / "H001-H045_third_candidate_progress.json"
REWRITE = GENERATED / "H001-H045_rewritten_candidates.json"
OUTPUT_JSON = GENERATED / "H001-H045_song_selection_log.json"
OUTPUT_MD = GENERATED / "H001-H045_adopted_2026-08-02.md"


CHOICES = {
    1: 1, 2: 1, 3: 1, 4: 1, 5: 2, 6: 1, 7: 2, 8: 2, 9: 4,
    10: 1, 11: 1, 12: 2, 13: 2, 14: 2, 15: 1, 16: 2, 17: 1,
    18: 2, 19: 2, 20: 1, 21: 2, 22: 1, 23: 2, 24: 3, 25: 2,
    26: 1, 27: 1, 28: 2, 29: 2, 30: 2, 31: 3, 32: 1, 33: 1,
    34: 2, 35: 4, 36: 1, 37: 2, 38: 2, 39: 1, 40: 1, 41: 1,
    42: 2, 43: 1, 44: 1, 45: 1,
}

PASS_AFTER_REGENERATION = {24, 31}
PASS_AFTER_REWRITE = {9, 35}
EQUIVALENT_ADJUDICATION = {34, 44}


SPECIAL_NOTES = {
    9: (
        "誤認識しやすかった discussed / turned / although を thought / made / but に改稿。"
        "表現改訂版の候補1は内容語置換0件。ten→10 はASR表示上の数字化のみ。"
    ),
    24: "3曲目で checked / wiped / worked の過去形語尾を含め全文一致。",
    31: "3曲目で Marie Curie の異常反復が解消し、全文一致。",
    34: (
        "Gaudí と Sagrada Família のアクセント記号・分かち書きによる機械判定上の差。"
        "候補2は本文語句を保っており、実質的な置換なし。"
    ),
    35: (
        "H.M.S. Beagle を a British survey ship に、Galápagos を the Galapagos Islands に改稿。"
        "表現改訂版の候補1は全文一致。"
    ),
    44: (
        "seventy-eight / three hundred eighty-five / twenty-four はASR表示が数字になったため"
        "照合器が脱落扱い。nonviolent→non-violent と Dandi→Dandy も表記差で、内容語の変更なし。"
    ),
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_block(sheet: Path, heading: str) -> str:
    text = sheet.read_text(encoding="utf-8")
    match = re.search(rf"## {re.escape(heading)}\s+```text\s*\n(.*?)\n```", text, re.S)
    if not match:
        raise ValueError(f"Missing {heading}: {sheet}")
    return match.group(1).strip()


def qa_report(lesson: int, candidate: int) -> dict:
    if candidate >= 4:
        rewrite_candidate = candidate - 3
        return load_json(
            REWRITE_AUDIO
            / f"H{lesson:03d}"
            / f"candidate{rewrite_candidate}_QA_mlx.json"
        )
    return load_json(
        AUDIO / f"H{lesson:03d}" / f"candidate{candidate}_QA_mlx.json"
    )


def candidate_url(
    initial: dict, third: dict, rewrite: dict, lesson: int, candidate: int
) -> str:
    if candidate == 1:
        return initial["lessons"][str(lesson)]["first"]
    if candidate == 2:
        return initial["lessons"][str(lesson)]["backup"]
    if candidate == 3:
        return third["lessons"][str(lesson)]["third"]
    if candidate == 4:
        return rewrite["lessons"][str(lesson)]["first"]
    return rewrite["lessons"][str(lesson)]["backup"]


def status_for(lesson: int) -> str:
    if lesson in PASS_AFTER_REWRITE:
        return "PASS_AFTER_REWRITE"
    if lesson in PASS_AFTER_REGENERATION:
        return "PASS_AFTER_REGENERATION"
    if lesson in EQUIVALENT_ADJUDICATION:
        return "PASS_EQUIVALENT"
    return "PASS"


def selection_reason(lesson: int, candidate: int, first: dict, second: dict) -> str:
    if lesson in PASS_AFTER_REWRITE:
        if lesson == 9:
            return "誤認識しやすい表現を改稿。改訂版候補1は内容語置換0件で、候補2の sight→side を回避。"
        return "誤認識しやすい固有名詞を説明表現へ改稿。改訂版候補1が全文一致100%。"
    if lesson in PASS_AFTER_REGENERATION:
        return "初回2候補の誤語・構造不良を3曲目で解消したため採用。"
    if lesson == 34:
        return "候補2は固有名詞の正規化差だけで、候補1にあった単複・語尾差がない。"
    if lesson == 44:
        return "数字・ハイフン・地名の表記差を除けば候補1が本文通り。候補2の disciplined 脱落を回避。"
    chosen = first if candidate == 1 else second
    other = second if candidate == 1 else first
    if chosen["verdict"] == "PASS" and other["verdict"] != "PASS":
        return f"候補{candidate}のみ誤語置換疑いなし。"
    if chosen["coverage"] != other["coverage"]:
        return (
            f"両候補合格。候補{candidate}の歌詞一致率"
            f"{chosen['coverage']:.2%}が高いため採用。"
        )
    if chosen["precision"] != other["precision"]:
        return (
            f"両候補合格・一致率同等。候補{candidate}の認識精度"
            f"{chosen['precision']:.2%}が高いため採用。"
        )
    return (
        f"両候補とも全文一致。候補{candidate}の約{chosen['audio_duration']:.1f}秒の"
        "ゆとりある発音を採用。"
    )


def main() -> None:
    initial = load_json(INITIAL)
    third = load_json(THIRD)
    rewrite = load_json(REWRITE)
    songs = []
    counts: dict[str, int] = {}
    markdown = [
        "# 高校生編 H001〜H045 採用曲一覧（歌詞QA後）",
        "",
        "- 判定順：誤った語句の置換 → 脱落・構成 → ASR一致率 → 発音のゆとり。",
        "- 初回は各レッスン2候補を比較。両候補に真の誤語がある場合のみ3曲目を検査。",
        "- H009・H035は3曲目まで同じ誤認識が続いたため文章自体を改稿し、改訂版2候補を再比較。",
        "- H034・H044の警告は固有名詞・数字・ハイフンの表記差として人手判定。",
        "",
        "| Lesson | Title | 採用 | QA | Suno | 理由 |",
        "|---:|---|---:|---|---|---|",
    ]

    for lesson in range(1, 46):
        candidate = CHOICES[lesson]
        if lesson in PASS_AFTER_REWRITE:
            first = qa_report(lesson, 4)
            second = qa_report(lesson, 5)
        else:
            first = qa_report(lesson, 1)
            second = qa_report(lesson, 2)
        chosen = qa_report(lesson, candidate)
        status = status_for(lesson)
        counts[status] = counts.get(status, 0) + 1
        sheet = SHEETS / f"H{lesson:03d}.md"
        title = extract_block(sheet, "Suno Title")
        lyrics = extract_block(sheet, "Lyrics")
        expected_word_count = chosen["expected_words"]
        duration = round(float(chosen["audio_duration"]), 3)
        url = candidate_url(initial, third, rewrite, lesson, candidate)
        song_id = url.rstrip("/").split("/")[-1]
        generation_attempt = 3 if candidate >= 4 else (2 if candidate == 3 else 1)
        reason = selection_reason(lesson, candidate, first, second)
        notes = SPECIAL_NOTES.get(
            lesson,
            "高信頼の内容語置換は検出されず、レッスン本文の終端まで到達。",
        )
        omissions = chosen.get("largest_missing_runs", [])
        if lesson in EQUIVALENT_ADJUDICATION:
            omissions = []
        row = {
            "lesson": f"H{lesson:03d}",
            "title": title,
            "adopted_candidate": (
                f"rewrite_candidate{candidate - 3}" if candidate >= 4 else candidate
            ),
            "share_url": url,
            "song_id": song_id,
            "duration_seconds": duration,
            "generation_attempt": generation_attempt,
            "adoption_status": "adopted",
            "lyrics_match": {
                "status": status,
                "raw_asr_verdict": chosen["verdict"],
                "coverage": chosen["coverage"],
                "precision": chosen["precision"],
                "high_confidence_replacement_count": chosen[
                    "high_confidence_replacement_count"
                ],
                "reached_expected_ending": chosen["reached_expected_ending"],
            },
            "omissions": omissions,
            "pronunciation_notes": notes,
            "timing_notes": {
                "duration_seconds": duration,
                "expected_words": expected_word_count,
                "approx_words_per_minute": round(
                    expected_word_count / max(duration, 0.001) * 60, 1
                ),
                "all_lyrics_characters": len(lyrics),
            },
            "selection_reason": reason,
            "comparison": {
                "candidate1": {
                    "verdict": first["verdict"],
                    "coverage": first["coverage"],
                    "duration_seconds": first["audio_duration"],
                },
                "candidate2": {
                    "verdict": second["verdict"],
                    "coverage": second["coverage"],
                    "duration_seconds": second["audio_duration"],
                },
            },
        }
        songs.append(row)
        markdown.append(
            f"| H{lesson:03d} | {title.replace('|', '／')} | "
            f"{'改訂版' + str(candidate - 3) if candidate >= 4 else candidate} | {status} | "
            f"[Suno]({url}) | {reason.replace('|', '／')} |"
        )

    payload = {
        "range": "H001-H045",
        "finalized_at": "2026-08-02T19:25:00+09:00",
        "policy": (
            "Compare both initial candidates, prioritize wrong-word substitutions over "
            "omissions, and normally inspect at most three songs per unchanged lyric version. "
            "When the user explicitly requests a wording rewrite after three failures, compare "
            "the rewritten pair and record exactly one adopted song."
        ),
        "summary": {
            "total": len(songs),
            "counts": counts,
            "stopped_after_three": [],
            "corrected_before_regeneration": {
                "H009": [
                    "We thought about several conditions and made a clear plan.",
                    "Mother was tired, but she said she would prepare sandwiches.",
                    "As Sunday approaches, my sister's face remains calm."
                ],
                "H035": [
                    "In 1831, Charles Darwin began a voyage around the world aboard a British survey ship.",
                    "On the Galapagos Islands, he carefully observed how animals varied from island to island."
                ]
            },
        },
        "required_fields": [
            "lesson", "share_url", "song_id", "duration_seconds",
            "generation_attempt", "lyrics_match", "omissions",
            "pronunciation_notes", "timing_notes", "selection_reason",
        ],
        "songs": songs,
    }
    OUTPUT_JSON.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    markdown.extend([
        "",
        "## 集計",
        "",
        *[f"- {key}: {value}曲" for key, value in sorted(counts.items())],
        "",
        "## 表現改訂で誤認識を解消した曲",
        "",
        "- H009: discussed / turned / although を thought / made / but に改稿し、内容語置換0件。",
        "- H035: H.M.S. Beagle を a British survey ship に改稿し、全文一致100%。",
        "",
    ])
    OUTPUT_MD.write_text("\n".join(markdown), encoding="utf-8")
    print(json.dumps({
        "selection_log": str(OUTPUT_JSON),
        "adopted_report": str(OUTPUT_MD),
        "summary": payload["summary"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
