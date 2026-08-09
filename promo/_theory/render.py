"""Render promo/_theory/index.html to 1920x1080 PNG using Playwright Chromium.

Output: promo/ending_theory.png (overwrites)
"""
from __future__ import annotations
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
HTML = ROOT / "index.html"
OUT = ROOT.parent / "ending_theory.png"


def main() -> None:
    assert HTML.exists(), HTML
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1,
        )
        page = context.new_page()
        page.goto("file://" + str(HTML), wait_until="networkidle")
        # extra wait for webfonts
        page.wait_for_timeout(800)
        page.screenshot(path=str(OUT), clip={"x": 0, "y": 0, "width": 1920, "height": 1080})
        browser.close()
    print(f"saved: {OUT}")


if __name__ == "__main__":
    main()
