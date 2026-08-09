"""
slides_英語は歌で覚える.html を1枚ずつ16:9で撮影する（playwright）。
各 .slide を active 化し、ナビ/プログレス/フッターを隠して .deck を撮る。
出力: tmp_music_slides/frames/slide-01.png ...
"""
from __future__ import annotations
from pathlib import Path
from playwright.sync_api import sync_playwright

PROJ = Path(__file__).resolve().parent
HTML = PROJ / "slides_英語は歌で覚える.html"
OUT = PROJ / "tmp_music_slides" / "frames"

ACTIVATE_JS = """(idx) => {
  const ss = [...document.querySelectorAll('.slide')];
  ss.forEach((s, k) => {
    s.classList.toggle('active', k === idx);
    s.setAttribute('aria-hidden', k === idx ? 'false' : 'true');
  });
}"""

HIDE_CSS = ".nav,.progress,.foot{display:none !important;}"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=2)
        page.goto("file://" + str(HTML), wait_until="networkidle")
        page.add_style_tag(content=HIDE_CSS)
        page.wait_for_timeout(500)
        n = page.evaluate("() => document.querySelectorAll('.slide').length")
        print(f"slides: {n} -> {OUT}")
        for i in range(n):
            page.evaluate(ACTIVATE_JS, i)
            page.wait_for_timeout(520)
            num = f"{i + 1:02d}"
            page.locator(".deck").screenshot(path=str(OUT / f"slide-{num}.png"))
            print(f"shot slide {num}")
        browser.close()
    print("done ->", OUT)


if __name__ == "__main__":
    main()
