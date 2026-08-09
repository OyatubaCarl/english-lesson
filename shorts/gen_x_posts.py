"""各quiz動画用の X (Twitter) 投稿テンプレートを生成。

X の文字制限は無料280文字、有料 (Premium) は 25,000文字。
ここでは無料垢でも収まる280文字以下版と、Premium向けロングを両方出力。
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
QUIZZES = ROOT / "quizzes.json"
OUT_DIR = ROOT / "x_posts"
OUT_DIR.mkdir(exist_ok=True)


def body_text(body_subs: list[dict]) -> str:
    parts = []
    for sub in body_subs:
        text = sub["text"].replace(" ", "")
        if sub.get("style") == "BodyEN":
            parts.append(text)
        else:
            parts.append(text)
    return "".join(parts)


def make_post_short(quiz: dict) -> str:
    word = quiz["word"]
    meaning = quiz["meaning_jp"]
    body = body_text(quiz["body_subtitles"])
    # 例文を全文使うと長いので80字程度に省略
    body_short = body if len(body) <= 60 else body[:58] + "…"
    return f"""🌮 大学受験の難単語

{word} = {meaning}

例:「{body_short}」

日本語の文に英単語を埋め込んで覚えるWordTacos
👇 無料・ブラウザだけでOK
https://words.teachertacos.com

#英単語 #大学受験 #英語学習 #WordTacos"""


def make_post_long(quiz: dict) -> str:
    word = quiz["word"]
    meaning = quiz["meaning_jp"]
    body = body_text(quiz["body_subtitles"])
    pvar = quiz.get("paper_variant", {})
    research = " ".join(ln["text"].replace(" ", "") for ln in pvar.get("lines", []))
    cite = pvar.get("cite", "").replace(" ", "")
    return f"""🌮 今日の難単語 — {word} ({meaning})

例文:
「{body}」

────
日本語の文に英単語をすっと埋め込んで覚えるアプリ「WordTacos」
中1〜大学受験までの7,000語+
昇級試験はミニゲーム(タコス工房ラッシュ)で楽しく実力チェック

👇 無料・ブラウザだけでOK・登録不要
https://words.teachertacos.com

公式サイト: https://teachertacos.com
YouTube: https://www.youtube.com/@teachertacosenglish

────
{research}{(' / ' + cite) if cite else ''}

#英単語 #大学受験 #英語学習 #高校英語 #難単語 #WordTacos #{word}"""


def make_post_thread(quizzes: list[dict]) -> list[str]:
    """複数quizを 1ツイート1問の連投スレッドにする (要 280字対応)"""
    posts: list[str] = [
        f"""🌮 大学受験の難単語クイズ・全{len(quizzes)}問

例文の中に隠した英単語、意味を当てられますか?
答えは続きのツイートで👇

ノーヒント正解できたらかなりの英語ガチ勢🔥

▼ アプリで覚えるなら無料・ブラウザだけ
https://words.teachertacos.com

#英単語 #大学受験 #英語学習 #WordTacos"""
    ]
    for i, q in enumerate(quizzes, 1):
        body = body_text(q["body_subtitles"])
        body_s = body if len(body) <= 80 else body[:78] + "…"
        post = f"""Q{i}. {q['word']}

「{body_s}」

答え: {q['meaning_jp']}

#WordTacos"""
        posts.append(post)
    # 最後にもう一度CTA
    posts.append(f"""👆 ぜんぶ知ってましたか?

WordTacos なら、日本語の文に英単語を埋め込んで自然に覚えられる。
中1〜大学受験まで7,000語、無料・ブラウザだけでOK。

▼ いますぐ
https://words.teachertacos.com

▼ YouTube/Shorts
@teachertacosenglish""")
    return posts


def main(ids: list[str]) -> None:
    qs = {q["id"]: q for q in json.loads(QUIZZES.read_text(encoding="utf-8"))}
    selected = []
    for qid in ids:
        q = qs.get(qid)
        if not q:
            print(f"skip {qid}: not found")
            continue
        selected.append(q)
        # 280字版
        sp = make_post_short(q)
        (OUT_DIR / f"{qid}_short.txt").write_text(sp, encoding="utf-8")
        # ロング版
        lp = make_post_long(q)
        (OUT_DIR / f"{qid}_long.txt").write_text(lp, encoding="utf-8")
        print(f"  ✓ {qid} ({len(sp)}字 short / {len(lp)}字 long)")

    # 連投スレッド
    if selected:
        thread = make_post_thread(selected)
        for i, p in enumerate(thread):
            (OUT_DIR / f"_thread_{i:02d}.txt").write_text(p, encoding="utf-8")
        print(f"\n  ✓ thread: {len(thread)}ツイート → _thread_*.txt")

    print(f"\n→ {OUT_DIR}/")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        ids = sys.argv[1:]
    else:
        ids = [
            "02_resilient", "03_ubiquitous", "04_scrutinize", "05_profound",
            "06_mundane", "07_fragile", "08_vivid", "09_inevitable",
            "10_tranquil", "11_diligent",
            "12_abstruse", "13_acrimonious", "14_assiduous", "15_austere",
            "16_nonchalant", "17_capricious", "18_clandestine", "19_cogent",
            "20_convivial", "21_copious",
        ]
    main(ids)
