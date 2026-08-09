"""WordTacos 46.5秒 quiz短編 (wordtacos_quiz_short_v1_*) のYouTubeアップロード設計を生成。

usage:
    python3 shorts/wt_v1_design.py
        → _analytics/wt_v1_design.json を出力
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
QUIZZES = json.loads((ROOT / "quizzes.json").read_text(encoding="utf-8"))
QUIZZES_BY_ID = {q["id"]: q for q in QUIZZES}

# 公開順 + JST時刻 (1日2本: 07:00 / 19:00)
SCHEDULE: list[tuple[str, str]] = []
QUIZ_IDS = [
    "02_resilient", "03_ubiquitous", "04_scrutinize", "05_profound",
    "06_mundane", "07_fragile", "08_vivid", "09_inevitable",
    "10_tranquil", "11_diligent",
    "12_abstruse", "13_acrimonious", "14_assiduous", "15_austere",
    "16_nonchalant", "17_capricious", "18_clandestine", "19_cogent",
    "20_convivial", "21_copious",
]

# 開始: 2026-06-29 07:00 JST
JST = timezone(timedelta(hours=9))
START = datetime(2026, 6, 29, 7, 0, tzinfo=JST)
slots: list[datetime] = []
day = 0
while len(slots) < 20:
    base = START + timedelta(days=day)
    slots.append(base.replace(hour=7))
    slots.append(base.replace(hour=19))
    day += 1
slots = slots[:20]


def body_text(quiz: dict) -> str:
    """body_subtitlesから純粋な日本語+英語の例文を組み立てる"""
    parts: list[str] = []
    for sub in quiz["body_subtitles"]:
        parts.append(sub["text"].replace(" ", ""))
    return "".join(parts)


def choices_compact(quiz: dict) -> str:
    cs = [c.replace(" ", "") for c in quiz["choices"]]
    return f"A {cs[0]}  B {cs[1]}  C {cs[2]}  D {cs[3]}"


def correct_letter(quiz: dict) -> str:
    return "ABCD"[quiz["correct_index"]]


def make_title(quiz: dict) -> str:
    w = quiz["word"]
    return f"「{w}」5秒で意味当てられる? #Shorts"


def make_description(quiz: dict) -> str:
    w = quiz["word"]
    body = body_text(quiz)
    choices = choices_compact(quiz)
    answer = f"{correct_letter(quiz)} {quiz['choices'][quiz['correct_index']].replace(' ', '')}"
    return f"""【超難単語が一発で覚えられる裏技】

{body}

"{w}" の意味は?
{choices}

──────────────
🔗 WordTacos アプリ (日本語に包んでやさしく覚える英単語)
🌐 https://words.teachertacos.com

🌐 公式 https://teachertacos.com
▶️ https://www.youtube.com/@TeacherTacosEnglish

#英語学習 #英単語 #大学受験 #高校英語 #英語クイズ #{w} #Shorts
"""


def make_tags(quiz: dict) -> list[str]:
    return [
        "英語学習", "英単語", "大学受験", "高校英語", "英語クイズ",
        "ルー語", "Diglot Weave", "WordTacos",
        quiz["word"],
        "Shorts",
    ]


def main() -> None:
    out: list[dict] = []
    for i, qid in enumerate(QUIZ_IDS):
        quiz = QUIZZES_BY_ID[qid]
        pub_jst = slots[i].isoformat()
        out.append({
            "id": qid,
            "word": quiz["word"],
            "meaning_jp": quiz["meaning_jp"],
            "correct_letter": correct_letter(quiz),
            "title": make_title(quiz),
            "description": make_description(quiz),
            "tags": make_tags(quiz),
            "publish_jst": pub_jst,
        })
    path = ROOT / "_analytics" / "wt_v1_design.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {path} ({len(out)} items)")
    print(f"first slot: {out[0]['publish_jst']}  ({out[0]['id']})")
    print(f"last slot:  {out[-1]['publish_jst']}  ({out[-1]['id']})")


if __name__ == "__main__":
    main()
