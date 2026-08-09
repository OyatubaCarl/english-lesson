#!/usr/bin/env python3
"""Sync phonics card data from JSON into the standalone mockup HTML."""
import argparse
import json
import re
import sys
from pathlib import Path


DEFAULT_DATA = "phonics-audio-items.json"
DEFAULT_HTML = "phonics-first-page-mockup.html"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=DEFAULT_DATA)
    parser.add_argument("--html", default=DEFAULT_HTML)
    args = parser.parse_args()

    data_path = Path(args.data)
    html_path = Path(args.html)
    data = json.loads(data_path.read_text(encoding="utf-8"))
    cards = data["words"]

    html = html_path.read_text(encoding="utf-8")
    cards_js = json.dumps(cards, ensure_ascii=False, indent=8)
    replacement = f"      const cards = {cards_js};\n\n"

    pattern = re.compile(r"      const cards = \[[\s\S]*?      const state = \{")
    if not pattern.search(html):
        raise SystemExit("Could not find cards block in HTML")

    html = pattern.sub(replacement + "      const state = {", html, count=1)
    html_path.write_text(html, encoding="utf-8")
    print(f"Synced {len(cards)} cards into {html_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
