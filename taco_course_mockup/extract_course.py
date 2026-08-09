"""index.html の book-* から、タコスパーティー用のレッスンJSONを抽出する。

中学（book-middle）と同じ構造（jp-body / en-body / grammar-box）なので、
高校（book-high1 / high2 / high3）もそのまま抽出できる。出力形式は middle_lessons.json と同一:

    { b, title, book, grammar:{target,desc,examples:[{en,ja}]},
      vocabSentences:[{text:"…<word>…", words:[{w,ja}]}],
      enSentences:[...], passageJp, video }

使い方:
    python3 extract_course.py middle  > middle_lessons.json
    python3 extract_course.py high    > high_lessons.json     # high1+high2+high3 を通し番号で結合
"""
from __future__ import annotations

import html as htmlmod
import json
import re
import sys
from pathlib import Path

SRC = Path(__file__).parent.parent / "index.html"
YT = Path(__file__).parent.parent / "youtube-map.json"
MIDDLE_OVERRIDES = Path(__file__).parent / "middle_lesson_overrides.json"

BOOKS = {"middle": ["middle"], "high": ["high1", "high2", "high3"], "beginner": ["beginner"]}
BOOK_LABEL = {"high1": "高1", "high2": "高2", "high3": "高3", "middle": "中"}


def strip_tags(s: str) -> str:
    return htmlmod.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def book_segment(html: str, book: str) -> str:
    """book-<name> の div から、次の book-* までを切り出す"""
    m = re.search(rf'<div[^>]*id="book-{book}"', html)
    if not m:
        return ""
    nxt = [x.start() for x in re.finditer(r'<div[^>]*id="book-', html) if x.start() > m.start()]
    return html[m.start(): nxt[0] if nxt else len(html)]


def parse_grammar(sec: str) -> dict:
    box = re.search(r'<div class="grammar-box">([\s\S]*?)</div>', sec)
    if not box:
        return {"target": "", "desc": "", "examples": []}
    b = box.group(1)
    target = strip_tags((re.search(r'<span class="g-title">([\s\S]*?)</span>', b) or [None, ""])[1])
    target = re.sub(r"^文法ターゲット[：:]\s*", "", target)
    desc = strip_tags((re.search(r'<p class="g-desc">([\s\S]*?)</p>', b) or [None, ""])[1])
    examples = []
    for li in re.findall(r"<li>([\s\S]*?)</li>", b):
        t = strip_tags(li)
        # 「英文 — 和訳」「英文（和訳）」など区切りを吸収
        m = (re.match(r"^(.*?)\s*[—–―‐\-−:：]\s*(.+)$", t)
             or re.match(r"^(.*?)\s*[（(](.+)[)）]\s*$", t))
        if m and re.search(r"[A-Za-z]", m.group(1)):
            examples.append({"en": m.group(1).strip(), "ja": m.group(2).strip()})
        elif re.search(r"[A-Za-z]", t):
            examples.append({"en": t, "ja": ""})
    return {"target": target, "desc": desc, "examples": examples}


def parse_jp_body(sec: str) -> tuple[list, str]:
    """jp-body → vocabSentences（段落ごと。英単語は <word> マーカー）と passageJp"""
    m = re.search(r'<div class="jp-body[^"]*">([\s\S]*?)</div>', sec)
    if not m:
        return [], ""
    body = m.group(1)
    sents, plain = [], []
    for p in re.findall(r"<p>([\s\S]*?)</p>", body):
        words = []

        def repl(mm):
            w = strip_tags(mm.group(0))
            ja = htmlmod.unescape(mm.group(1))
            if w and ja:
                words.append({"w": w, "ja": ja})
                return f"\x01{w}\x02"      # strip_tags で消されないよう一時マーカー
            return w

        text = re.sub(r'<span class="w"[^>]*data-ja="([^"]*)"[^>]*>[\s\S]*?</span>', repl, p)
        text = strip_tags(text)
        text = text.replace("\x01", "<").replace("\x02", ">")   # マーカーを復元
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            continue
        plain.append(re.sub(r"<([^>]+)>", r"\1", text))
        if words:
            sents.append({"text": text, "words": words})
    return sents, "\n".join(plain)


def parse_en_body(sec: str) -> list:
    m = re.search(r'<div class="en-body[^"]*">([\s\S]*?)</div>', sec)
    if not m:
        return []
    body = strip_tags(m.group(1))
    body = re.sub(r"\s+", " ", body).strip()
    # 文末（. ! ?）で分割。略記(Mr. など)は今回のデータには出ないので単純分割で足りる
    out = [s.strip() for s in re.findall(r"[^.!?]+[.!?]", body)]
    return [s for s in out if re.search(r"[A-Za-z]", s)]


def main() -> int:
    which = sys.argv[1] if len(sys.argv) > 1 else "high"
    html = SRC.read_text(encoding="utf-8")
    ymap = json.loads(YT.read_text(encoding="utf-8"))
    overrides = (
        json.loads(MIDDLE_OVERRIDES.read_text(encoding="utf-8"))
        if which == "middle" and MIDDLE_OVERRIDES.exists()
        else {}
    )
    out, n = [], 0
    for book in BOOKS[which]:
        seg = book_segment(html, book)
        vids = ymap.get(book, {})
        for sec in re.findall(r'<section class="lesson[^"]*" data-lesson="\d+"[\s\S]*?</section>', seg):
            num = int(re.search(r'data-lesson="(\d+)"', sec).group(1))
            title = strip_tags((re.search(r"<h2[^>]*>([\s\S]*?)</h2>", sec) or [None, ""])[1])
            title = re.sub(r"^Lesson\s+\S+\s*[—–-]\s*", "", title).strip()
            vs, pj = parse_jp_body(sec)
            n += 1
            v = vids.get(str(num))
            if isinstance(v, list):
                v = v[0] if v else None
            item = {
                "b": n,                                   # コース内の通し番号
                "src": {"book": book, "lesson": num},     # 元のブック/課
                "title": (f"{BOOK_LABEL.get(book, '')} L{num} " if len(BOOKS[which]) > 1 else "") + title,
                "grammar": parse_grammar(sec),
                "vocabSentences": vs,
                "enSentences": parse_en_body(sec),
                "passageJp": pj,
                **({"video": v} if v else {}),
            }
            override = overrides.get(str(num), {})
            for field in ("vocabSentences", "passageJp", "enSentences"):
                if field in override:
                    item[field] = override[field]
            out.append(item)
    json.dump(out, sys.stdout, ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
