#!/usr/bin/env python3
"""toeic_section.html に含まれる target word (data-base) と
toeic_vocab.csv の全732語を突き合わせ、未カバー語を出力する。
"""
from __future__ import annotations
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CSV = ROOT / "toeic_vocab.csv"
HTML = ROOT / "toeic_section.html"
OUT = ROOT / "toeic_uncovered.txt"


def normalize(word: str) -> str:
    """Drop punctuation, lower-case, strip extra whitespace.
    Multi-word entries (e.g. 'vice president') keep their inner space."""
    s = word.lower().strip()
    s = re.sub(r"\s+", " ", s)
    return re.sub(r"[^a-z' ]", "", s)


def variants(word: str) -> set[str]:
    """Produce simple inflection variants to broaden matching."""
    w = normalize(word)
    out = {w}
    # Common suffix variants both ways
    if w.endswith("y") and len(w) > 2:
        out.add(w[:-1] + "ies")
        out.add(w[:-1] + "ied")
    if w.endswith("e"):
        out.add(w + "d")
        out.add(w[:-1] + "ing")
    out.update({w + s for s in ("s", "es", "ed", "ing", "er", "est", "ly", "tion", "ment")})
    for suf in ("ies", "es", "s", "ed", "ing", "er", "est", "ly", "tion", "ment"):
        if w.endswith(suf) and len(w) > len(suf) + 2:
            out.add(w[: -len(suf)])
            if suf == "ies":
                out.add(w[: -len(suf)] + "y")
    return out


def load_csv_words() -> list[str]:
    words = []
    with CSV.open(encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            words.append(row["word"].strip())
    return words


def extract_covered_words() -> set[str]:
    """HTML中の data-base / .we span / .w span / 英文中の単語を抽出。"""
    html = HTML.read_text(encoding="utf-8")
    covered: set[str] = set()
    # data-base="word" 属性（複合語はそのまま、+各単語も登録）
    for m in re.finditer(r'data-base="([^"]+)"', html):
        full = normalize(m.group(1))
        covered.add(full)
        for w in m.group(1).split():
            covered.add(normalize(w))
    # 英文本文中の単語（we span のtext）
    for m in re.finditer(r'class="we[^"]*"[^>]*>([^<]+)<', html):
        for w in m.group(1).split():
            covered.add(normalize(w))
    # 各形式の解説（en例文）の単語
    for m in re.finditer(r'<em>([^<]+)</em>', html):
        for w in m.group(1).split():
            covered.add(normalize(w))
    covered.discard("")
    return covered


def main():
    csv_words = load_csv_words()
    covered = extract_covered_words()

    matched = []
    unmatched = []
    for w in csv_words:
        norm = normalize(w)
        if not norm:
            continue
        vars_ = variants(w)
        if vars_ & covered:
            matched.append(w)
        else:
            unmatched.append(w)

    print(f"Total CSV words : {len(csv_words)}")
    print(f"Covered         : {len(matched)} ({len(matched)/len(csv_words)*100:.1f}%)")
    print(f"Uncovered       : {len(unmatched)}")

    OUT.write_text("\n".join(unmatched), encoding="utf-8")
    print(f"Wrote uncovered list to {OUT}")


if __name__ == "__main__":
    main()
