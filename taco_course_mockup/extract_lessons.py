#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""index.html の B-series レッスン(B1〜B20)を抽出して lessons.json を生成する。

本サイト(../index.html)が正本。標準ライブラリのみ使用(html.parser)。
出力: taco_course_mockup/lessons.json（UTF-8・インデントなし）

各レッスンの形:
{
  "b": 1, "id": 1, "title": "Tom at the Gate", "title_h2": "Lesson B1 — Tom at the Gate",
  "video": "JG6OjXpvUiM",
  "grammar": {"target": "...", "desc": "...", "examples": [{"en": "...", "ja": "..."}, ...]},
  "jp_mixed": [{"text": "…<welcome>…", "words": [{"w": "welcome", "ja": "歓迎されている"}]}, ...],
  "sentences": [{"en": "...", "ja": "..."}, ...],
  "vocab": [{"w": "welcome", "ja": "歓迎されている"}, ...]   # dedupe・機能語除外・最大8語
}

vocab は jp_body の .w を優先し、8語に満たない場合は en-body の .we から補完する
(後半レッスンは .w が少なく、単語テストの問題数を確保するため)。
"""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEX_HTML = ROOT.parent / "index.html"
OUT_JSON = ROOT / "lessons.json"

MAX_VOCAB = 8

# 機能語・間投詞・固有名詞など「新出単語」から除外する base(小文字)
STOP_WORDS = {
    # 冠詞・前置詞・接続詞・代名詞・be/助動詞
    "a", "an", "the", "to", "of", "in", "on", "at", "for", "with", "from", "by", "as",
    "and", "or", "but", "so", "if", "then",
    "is", "am", "are", "was", "were", "be", "been", "being",
    "do", "does", "did", "don't", "doesn't", "didn't",
    "can", "can't", "cannot", "will", "won't", "would", "should", "must", "may",
    "not", "no", "yes",
    "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them",
    "my", "your", "his", "its", "our", "their", "mine", "yours",
    "this", "that", "these", "those", "there", "here",
    "i'm", "you're", "we're", "they're", "it's", "he's", "she's", "isn't", "aren't",
    "let's", "what's", "who's", "how's", "that's",
    "what", "who", "whose", "whom", "how", "when", "where", "why", "which",
    "too", "very", "just", "also",
    # 間投詞・あいづち
    "oh", "wow", "hey", "hi", "hello", "hmm", "huh", "ah", "ok", "okay", "yeah", "yep",
    "bye", "please", "thanks", "thank", "sorry", "ta", "da",
    # 固有名詞(登場キャラクター等)
    "tom", "tacos", "taco", "teacher", "funnics", "mr", "mrs", "ms",
}

VOID_TAGS = {
    "img", "br", "hr", "meta", "link", "input", "source", "area",
    "base", "col", "embed", "param", "track", "wbr",
}

SPEAKER_RE = re.compile(r"^\s*[\(（][^\)）]*[\)）]\s*")
WS_RE = re.compile(r"\s+")
G_TARGET_RE = re.compile(r"^文法ターゲット[：:]\s*")


def clean(text):
    return WS_RE.sub(" ", text or "").strip()


def strip_speaker(text):
    return SPEAKER_RE.sub("", text or "").strip()


class BSeriesParser(HTMLParser):
    """b-series-lesson セクション(B1〜B20)だけを拾うストリーミングパーサ。"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lessons = []
        self.cur = None          # 取り込み中のレッスン
        self.depth = 0           # section 内で開いている子孫要素数
        self.zone = None         # grammar / jp / en / full / skip
        self.zone_depth = -1     # zone の div を開く直前の depth
        # 単純テキスト収集(h2 / g-title / g-desc / li の em・span.ja)
        self.bufkey = None       # 'h2'|'gtitle'|'gdesc'|'li_en'|'li_ja'
        self.buftag = None       # bufkey を閉じるタグ名
        self.buf = ""
        self.li = None           # {'en':..,'ja':..}(li 収集中)
        # p 収集(jp/en/full ゾーン)
        self.p_parts = None
        self.p_words = None
        self.w = None            # span.w 収集中 {'w':..,'ja':..}

    # ---------- helpers ----------
    def _start_buf(self, key, tag):
        self.bufkey, self.buftag, self.buf = key, tag, ""

    def _commit_buf(self):
        key, text = self.bufkey, clean(self.buf)
        self.bufkey = self.buftag = None
        self.buf = ""
        if self.cur is None:
            return
        if key == "h2":
            self.cur["h2"] = text
        elif key == "gtitle":
            self.cur["gtitle"] = text
        elif key == "gdesc":
            self.cur["gdesc"] = text
        elif key == "li_en" and self.li is not None:
            self.li["en"] = text
        elif key == "li_ja" and self.li is not None:
            self.li["ja"] = text

    # ---------- HTMLParser hooks ----------
    def handle_starttag(self, tag, attrs):
        ad = dict(attrs)
        cls = ad.get("class") or ""
        if self.cur is None:
            if tag == "section" and "b-series-lesson" in cls and "data-summary" not in ad:
                try:
                    n = int(ad.get("data-lesson") or 0)
                except ValueError:
                    n = 0
                if 1 <= n <= 20:
                    self.cur = {
                        "b": n,
                        "video": ad.get("data-video-id") or "",
                        "h2": "", "gtitle": "", "gdesc": "", "examples": [],
                        "jp": [], "en": [], "full": [], "we": [],
                    }
                    self.depth = 0
            return

        if self.zone == "skip":
            if tag not in VOID_TAGS:
                self.depth += 1
            return

        if self.zone is None:
            if tag == "h2":
                self._start_buf("h2", "h2")
            elif tag == "div":
                zmap = {
                    "grammar-box": "grammar", "jp-body": "jp",
                    "en-body": "en", "jp-full": "full", "picturebook-body": "skip",
                }
                for key, zone in zmap.items():
                    if key in cls.split():
                        self.zone = zone
                        self.zone_depth = self.depth
                        break
        elif self.zone == "grammar":
            classes = cls.split()
            if tag == "span" and "g-title" in classes:
                self._start_buf("gtitle", "span")
            elif tag == "p" and "g-desc" in classes:
                self._start_buf("gdesc", "p")
            elif tag == "li":
                self.li = {"en": "", "ja": ""}
            elif tag == "em" and self.li is not None:
                self._start_buf("li_en", "em")
            elif tag == "span" and "ja" in classes and self.li is not None:
                self._start_buf("li_ja", "span")
        elif self.zone == "jp":
            if tag == "p":
                self.p_parts, self.p_words = [], []
            elif tag == "span" and "w" in cls.split() and self.p_parts is not None:
                self.w = {"w": ad.get("data-base") or "", "ja": ad.get("data-ja") or ""}
        elif self.zone == "en":
            if tag == "p":
                self.p_parts = []
            elif tag == "span" and "we" in cls.split() and self.p_parts is not None:
                base = ad.get("data-base") or ""
                if base:
                    self.cur["we"].append({"w": base, "ja": ad.get("data-ja") or ""})
        elif self.zone == "full":
            if tag == "p":
                self.p_parts = []

        if tag not in VOID_TAGS:
            self.depth += 1

    def handle_endtag(self, tag):
        if self.cur is None:
            return
        if tag == "section" and self.depth == 0:
            self._close_section()
            return
        if tag in VOID_TAGS:
            return
        self.depth -= 1

        # ゾーン div の終了
        if self.zone is not None and self.depth == self.zone_depth:
            self.zone, self.zone_depth = None, -1
            self.p_parts = self.p_words = self.w = None
            self.li = None
            return

        # 単純テキスト収集の終了
        if self.bufkey is not None and tag == self.buftag:
            self._commit_buf()
            return

        if self.zone == "grammar" and tag == "li" and self.li is not None:
            if self.li["en"] or self.li["ja"]:
                self.cur["examples"].append({"en": self.li["en"], "ja": self.li["ja"]})
            self.li = None
        elif self.zone == "jp":
            if tag == "span" and self.w is not None:
                self.p_parts.append("<" + self.w["w"] + ">")
                self.p_words.append(dict(self.w))
                self.w = None
            elif tag == "p" and self.p_parts is not None:
                self.cur["jp"].append(("".join(self.p_parts), self.p_words))
                self.p_parts = self.p_words = None
        elif self.zone in ("en", "full") and tag == "p" and self.p_parts is not None:
            key = "en" if self.zone == "en" else "full"
            self.cur[key].append("".join(self.p_parts))
            self.p_parts = None

    def handle_data(self, data):
        if self.cur is None:
            return
        if self.bufkey is not None:
            self.buf += data
            return
        if self.zone == "skip":
            return
        if self.zone == "jp" and self.p_parts is not None:
            if self.w is None:  # span.w の中の表示語はマーカーに置換するので捨てる
                self.p_parts.append(data)
        elif self.zone in ("en", "full") and self.p_parts is not None:
            self.p_parts.append(data)

    # ---------- finalize ----------
    def _close_section(self):
        c, self.cur = self.cur, None
        title_h2 = clean(c["h2"])
        m = re.split(r"\s+—\s+", title_h2, maxsplit=1)
        title = m[1].strip() if len(m) == 2 else title_h2

        jp_mixed = []
        for raw, words in c["jp"]:
            jp_mixed.append({
                "text": strip_speaker(clean(raw)),
                "words": [w for w in words if w["w"]],
            })

        en_lines = [strip_speaker(clean(x)) for x in c["en"]]
        ja_lines = [strip_speaker(clean(x)) for x in c["full"]]
        n = min(len(en_lines), len(ja_lines))
        sentences = [{"en": en_lines[k], "ja": ja_lines[k]} for k in range(n)]

        vocab, seen = [], set()

        def add_word(w, ja):
            base = w.lower()
            if len(vocab) >= MAX_VOCAB or base in seen or base in STOP_WORDS or not ja:
                return
            seen.add(base)
            vocab.append({"w": w, "ja": ja})

        for sent in jp_mixed:            # 1st: jp_body の .w（③新出単語の本文タップ学習に使える）
            for w in sent["words"]:
                add_word(w["w"], w["ja"])
        for w in c["we"]:                # 2nd: en-body の .we から補完（④単語テスト用）
            add_word(w["w"], w["ja"])

        self.lessons.append({
            "b": c["b"], "id": c["b"],
            "title": title, "title_h2": title_h2,
            "video": c["video"],
            "grammar": {
                "target": G_TARGET_RE.sub("", c["gtitle"]),
                "desc": c["gdesc"],
                "examples": c["examples"],
            },
            "jp_mixed": jp_mixed,
            "sentences": sentences,
            "vocab": vocab,
            "_en_count": len(en_lines), "_ja_count": len(ja_lines),
        })


def main():
    html = INDEX_HTML.read_text(encoding="utf-8")
    parser = BSeriesParser()
    parser.feed(html)
    parser.close()
    lessons = sorted(parser.lessons, key=lambda x: x["b"])

    # ---- 検証出力 ----
    print(f"抽出元: {INDEX_HTML}")
    print(f"抽出レッスン数: {len(lessons)} (期待値 20)\n")
    hdr = f"{'B':>3} {'title':<32} {'g-ex':>4} {'jp_mixed':>8} {'sent':>5} {'vocab':>5} {'en/ja一致':>8}  video"
    print(hdr)
    print("-" * len(hdr))
    warnings = []
    for ls in lessons:
        match = "OK" if ls["_en_count"] == ls["_ja_count"] else f"NG {ls['_en_count']}/{ls['_ja_count']}"
        if ls["_en_count"] != ls["_ja_count"]:
            warnings.append(f"B{ls['b']}: en-body {ls['_en_count']}文 と jp-full {ls['_ja_count']}文 が不一致")
        print(f"{ls['b']:>3} {ls['title']:<32} {len(ls['grammar']['examples']):>4} "
              f"{len(ls['jp_mixed']):>8} {len(ls['sentences']):>5} {len(ls['vocab']):>5} {match:>8}  {ls['video']}")
        for key, need in (("grammar", None), ("video", None)):
            pass
        if not ls["grammar"]["target"] or not ls["grammar"]["desc"]:
            warnings.append(f"B{ls['b']}: grammar target/desc が空")
        if len(ls["grammar"]["examples"]) != 3:
            warnings.append(f"B{ls['b']}: 例文が {len(ls['grammar']['examples'])} 本 (期待 3)")
        if not ls["video"]:
            warnings.append(f"B{ls['b']}: video-id が空")

    print()
    if len(lessons) != 20:
        warnings.append(f"レッスン数 {len(lessons)} != 20")
    if warnings:
        print("警告:")
        for w in warnings:
            print("  -", w)
    else:
        print("警告: なし")

    for ls in lessons:  # 内部検証用フィールドは出力しない
        ls.pop("_en_count", None)
        ls.pop("_ja_count", None)

    OUT_JSON.write_text(
        json.dumps(lessons, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"\n書き出し: {OUT_JSON} ({OUT_JSON.stat().st_size:,} bytes)")
    return 0 if len(lessons) == 20 else 1


if __name__ == "__main__":
    sys.exit(main())
