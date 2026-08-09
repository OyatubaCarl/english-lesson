"""WordTacos 短編動画一括ビルダー

各 quiz について:
  1. quiz_card_<id>_default.png / _answered.png を Playwright で生成
  2. build_wordtacos_short_v1.py --quiz <id> を実行
  3. 概要欄テンプレート (descriptions/<id>.txt) を出力
"""
from __future__ import annotations
import json
import subprocess
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
DESC_DIR = ROOT / "descriptions"
DESC_DIR.mkdir(exist_ok=True)
HTML = ROOT / "quiz_card_render.html"


def body_text_with_embed(body_subs: list[dict]) -> str:
    """body_subtitles を <word> 埋め込み形式の1文に再構成"""
    parts: list[str] = []
    for sub in body_subs:
        text = sub["text"].replace(" ", "")  # 表示用スペースを除去
        if sub.get("style") == "BodyEN":
            parts.append(f"<{text}>")
        else:
            parts.append(text)
    return "".join(parts)


def render_card(quiz: dict, reveal: bool) -> Path:
    qid = quiz["id"]
    suffix = "answered" if reveal else "default"
    out = ASSETS / f"quiz_card_{qid}_{suffix}.png"
    if out.exists():
        return out
    body = body_text_with_embed(quiz["body_subtitles"])
    choices = "|".join(quiz["choices"])
    params = {
        "body": body,
        "choices": choices,
        "correct": str(quiz["correct_index"]),
    }
    if reveal:
        params["reveal"] = "1"
    qs = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    url = f"file://{HTML}?{qs}"
    subprocess.run(
        ["node", "render_quiz_card.js", url, str(out)],
        check=True, cwd=ROOT, capture_output=True,
    )
    return out


def build_description(quiz: dict) -> None:
    qid = quiz["id"]
    word = quiz["word"]
    meaning = quiz["meaning_jp"]
    body_text = body_text_with_embed(quiz["body_subtitles"]).replace("<", "【").replace(">", "】")
    template = f"""🌮 今日の難単語: {word} = {meaning}

例文:
「{body_text}」

▶ WordTacos アプリで覚えよう (無料・ブラウザだけでOK)
  https://words.teachertacos.com

▶ Teacher Tacos 公式サイト
  https://teachertacos.com

▶ Teacher Tacos English (YouTube)
  https://www.youtube.com/@teachertacosenglish

▶ X (旧Twitter)
  https://x.com/iHzKyC6Sdt2632

#英単語 #大学受験 #英語学習 #高校英語 #難単語 #WordTacos
#{word} #{meaning} #英検 #TOEIC
"""
    (DESC_DIR / f"{qid}.txt").write_text(template, encoding="utf-8")


def main(quiz_ids: list[str]) -> None:
    quizzes_all = json.loads((ROOT / "quizzes.json").read_text(encoding="utf-8"))
    quiz_map = {q["id"]: q for q in quizzes_all}

    for qid in quiz_ids:
        quiz = quiz_map.get(qid)
        if not quiz:
            print(f"skip {qid}: not found")
            continue
        if "body_subtitles" not in quiz:
            print(f"skip {qid}: no body_subtitles")
            continue
        print(f"=== {qid} ({quiz['word']}) ===")

        # 1. カード画像
        render_card(quiz, reveal=False)
        render_card(quiz, reveal=True)
        print("  ✓ cards")

        # 2. 動画ビルド
        env = {"BGM_VOLUME": "0.20"}
        import os
        e = os.environ.copy(); e.update(env)
        res = subprocess.run(
            ["/usr/bin/python3", "build_wordtacos_short_v1.py", "--quiz", qid],
            cwd=ROOT, env=e, capture_output=True, text=True,
        )
        if res.returncode != 0:
            print(res.stderr[-1500:], file=sys.stderr)
            continue
        print("  ✓ video")

        # 3. 概要欄
        build_description(quiz)
        print("  ✓ description")

    print(f"\n完了 → {ROOT}/wordtacos_quiz_short_v1_*.mp4")
    print(f"概要欄 → {DESC_DIR}/")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        ids = sys.argv[1:]
    else:
        # デフォルト: 02〜11 の10本
        ids = ["02_resilient", "03_ubiquitous", "04_scrutinize", "05_profound",
               "06_mundane", "07_fragile", "08_vivid", "09_inevitable",
               "10_tranquil", "11_diligent"]
    main(ids)
