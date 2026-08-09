"""X (Twitter) 用 v2 投稿テンプレート (選択肢入り + YouTube Shorts URL)。

各 quiz について:
  【超難単語が一発で覚えられる裏技】

  {body sentence with English word}

  "{word}" の意味は?
  A {c0}  B {c1}  C {c2}  D {c3}

  📺 答え→ {youtube_shorts_url}
  🌐 https://teachertacos.com

  #英語学習

usage:
    python3 shorts/gen_x_posts_v2.py
        → shorts/x_posts_v2/{id}.txt と shorts/x_posts_v2/_schedule.json
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
QUIZZES = json.loads((ROOT / "quizzes.json").read_text(encoding="utf-8"))
QUIZZES_BY_ID = {q["id"]: q for q in QUIZZES}
DESIGN = json.loads((ROOT / "_analytics" / "wt_v1_design.json").read_text(encoding="utf-8"))
UPLOADS_PATH = ROOT / "_analytics" / "wt_v1_uploads.json"
OUT_DIR = ROOT / "x_posts_v2"
OUT_DIR.mkdir(exist_ok=True)


def body_text(quiz: dict) -> str:
    parts = []
    for sub in quiz["body_subtitles"]:
        parts.append(sub["text"].replace(" ", ""))
    return "".join(parts)


def make_post(quiz: dict, yt_url: str) -> str:
    w = quiz["word"]
    body = body_text(quiz)
    cs = [c.replace(" ", "") for c in quiz["choices"]]
    return f"""【超難単語が一発で覚えられる裏技】

{body}

"{w}" の意味は?
A {cs[0]}  B {cs[1]}  C {cs[2]}  D {cs[3]}

📺 答え→ {yt_url}
🌐 公式サイト https://teachertacos.com

#英語学習"""


def main() -> None:
    uploads = {}
    if UPLOADS_PATH.is_file():
        uploads = json.loads(UPLOADS_PATH.read_text(encoding="utf-8"))

    schedule = []
    for item in DESIGN:
        qid = item["id"]
        quiz = QUIZZES_BY_ID[qid]
        url = uploads.get(qid, {}).get("shorts_url", "https://youtube.com/shorts/PENDING")
        post = make_post(quiz, url)
        path = OUT_DIR / f"{qid}.txt"
        path.write_text(post, encoding="utf-8")
        schedule.append({
            "id": qid,
            "word": quiz["word"],
            "publish_jst": item["publish_jst"],
            "char_count": len(post),
            "yt_url": url,
            "text_path": str(path),
        })
        print(f"  {qid}: {len(post)}字  {item['publish_jst']}  → {url}")

    sched_path = OUT_DIR / "_schedule.json"
    sched_path.write_text(json.dumps(schedule, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nwrote schedule -> {sched_path}")


if __name__ == "__main__":
    main()
