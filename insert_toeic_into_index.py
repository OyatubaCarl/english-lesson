#!/usr/bin/env python3
"""toeic_section.html を index.html に挿入する。
既に挿入済みの場合は古い book-toeic セクションを削除して新しい内容で置き換える。
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "index.html"
SECTION = ROOT / "toeic_section.html"
MARKER = '    <div class="book hidden" id="book-phonics" data-book="phonics">'


def main():
    if not INDEX.exists():
        sys.exit(f"index.html not found at {INDEX}")
    if not SECTION.exists():
        sys.exit(f"toeic_section.html not found at {SECTION}")

    html = INDEX.read_text(encoding="utf-8")
    section = SECTION.read_text(encoding="utf-8")

    # 既存 book-toeic セクションが入っていれば置換、なければ挿入
    pattern = re.compile(
        r'\n\n    <div class="book hidden" id="book-toeic" data-book="toeic">.*?\n    </div>\n',
        re.DOTALL,
    )
    if pattern.search(html):
        old_size = len(html)
        html = pattern.sub("\n\n" + section.rstrip() + "\n", html, count=1)
        INDEX.write_text(html, encoding="utf-8")
        print(f"Replaced existing book-toeic section.")
        print(f"index.html: {old_size} -> {len(html)} bytes")
        return

    if MARKER not in html:
        sys.exit(f"Insertion marker not found: {MARKER!r}")

    new_html = html.replace(MARKER, section.rstrip() + "\n\n" + MARKER, 1)
    INDEX.write_text(new_html, encoding="utf-8")
    print(f"Inserted {len(section)} bytes of TOEIC section into index.html")
    print(f"index.html grew from {len(html)} to {len(new_html)} bytes")


if __name__ == "__main__":
    main()
