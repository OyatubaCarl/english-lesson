#!/usr/bin/env python3
"""Integrate the generated Funnics Island B-series book into index.html."""
from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "index.html"
REPLACEMENT = ROOT / "funnics-beginner-assets" / "b_series_book_replacement.html"

CSS_TAG = '<link rel="stylesheet" href="funnics-beginner-assets/b_series_book_replacement.css">'
JS_TAG = '<script src="funnics-beginner-assets/b_series_book_replacement.js"></script>'
STALE_COMMENT = """        <!-- Funnics Island B1-B20 index-like drop-in replacement.
     Replace the current beginner book block with this block.
     Add b_series_book_replacement.css in <head> and b_series_book_replacement.js after the existing main script.
     index.html has not been modified by the build script. -->
"""
CURRENT_COMMENT = "    <!-- Funnics Island B1-B20 beginner book block for index.html. -->\n"


def find_book_block(html: str) -> tuple[int, int]:
    id_pos = html.find('id="book-beginner"')
    if id_pos < 0:
        raise RuntimeError('Could not find id="book-beginner" in index.html')

    start = html.rfind("<div", 0, id_pos)
    if start < 0:
        raise RuntimeError("Could not find the opening <div> for book-beginner")

    depth = 0
    for match in re.finditer(r"</?div\b[^>]*>", html[start:], flags=re.IGNORECASE):
        token = match.group(0).lower()
        if token.startswith("</div"):
            depth -= 1
            if depth == 0:
                return start, start + match.end()
        else:
            depth += 1

    raise RuntimeError("Could not find the closing </div> for book-beginner")


def replace_once(html: str, before: str, after: str) -> str:
    return html.replace(before, after, 1) if before in html else html


def update_shell_text(html: str) -> str:
    replacements = [
        (
            "<title>歌と日本語混じりで覚える英語学習サイト</title>",
            "<title>Funnics Island 英語学習サイト</title>",
        ),
        (
            "<h1>歌と日本語混じりで覚える英語学習サイト</h1>",
            "<h1>Funnics Island 英語学習サイト</h1>",
        ),
        (
            "<p class=\"page-subtitle\">中学生レベル〜高校まで、歌と日本語でつながる英文学習</p>",
            "<p class=\"page-subtitle\">歌・日本語混じり文・文法・シャドウイングで学ぶ英語教材</p>",
        ),
        (
            '<button class="btn-book" data-book="beginner" type="button" aria-pressed="false">📒 入門編</button>',
            '<button class="btn-book" data-book="beginner" type="button" aria-pressed="false">📒 入門英語（Funnics Island）</button>',
        ),
        (
            "<li>📒 <strong>入門編</strong> — 中1文法の基礎。短い例文で文法を1項目ずつ確認（20 レッスン）</li>",
            "<li>📒 <strong>入門英語（Funnics Island）</strong> — トムが島を進みながら、B1〜B20の中1基本表現を歌と会話で学習します</li>",
        ),
        (
            "<p>上のボタンから教材を 1 つ選んでください。選択するまで本文は表示されません。</p>",
            "<p>上のボタンから教材を 1 つ選んでください。入門英語（Funnics Island）では、動画・日本語混じり文・英語文・日本語訳・文法・シャドウイングをまとめて確認できます。</p>",
        ),
        (
            "<p>上のボタンから教材を 1 つ選んでください。Funnics Island 入門では、動画・日本語混じり文・英語文・日本語訳・文法・シャドウイングをまとめて確認できます。</p>",
            "<p>上のボタンから教材を 1 つ選んでください。入門英語（Funnics Island）では、動画・日本語混じり文・英語文・日本語訳・文法・シャドウイングをまとめて確認できます。</p>",
        ),
    ]
    for before, after in replacements:
        html = replace_once(html, before, after)
    return html


def main() -> int:
    html = INDEX.read_text(encoding="utf-8")
    replacement = REPLACEMENT.read_text(encoding="utf-8").rstrip()

    start, end = find_book_block(html)
    html = html[:start] + replacement + html[end:]

    if CSS_TAG not in html:
        html = html.replace("</head>", f"{CSS_TAG}\n</head>", 1)

    if JS_TAG not in html:
        html = html.replace("</body>", f"{JS_TAG}\n</body>", 1)

    html = update_shell_text(html)
    html = html.replace(STALE_COMMENT, "")
    html = html.replace(CURRENT_COMMENT, "")

    INDEX.write_text(html, encoding="utf-8")
    print(f"Integrated B-series replacement into {INDEX}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
