#!/usr/bin/env python3
"""イントロ/アウトロのタイトルカードPNGを生成（アプリと同じ配色・フォント）。"""
from playwright.sync_api import sync_playwright

W, H = 860, 1760
LOGO = "http://localhost:8790/taco_course_mockup/app_assets/party/tacos_party_logo.png"
TOM = "http://localhost:8790/taco_course_mockup/app_assets/celebrate/tom_cheer.png"

CARD = """
<!doctype html><meta charset=utf-8>
<style>
  html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden}}
  body{{background:linear-gradient(175deg,#2563eb 0%,#1d4ed8 74%,#1e3a8a 100%);
    font-family:"Hiragino Maru Gothic ProN","Hiragino Sans",system-ui,sans-serif;
    color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:34px;
    text-align:center;position:relative}}
  body::before{{content:"";position:absolute;inset:0;opacity:.16;
    background:radial-gradient(circle 6px at 18% 22%,#fff 98%,transparent),
      radial-gradient(circle 5px at 74% 16%,#ffd76e 98%,transparent),
      radial-gradient(circle 6px at 86% 52%,#fff 98%,transparent),
      radial-gradient(circle 5px at 30% 70%,#ffd76e 98%,transparent),
      radial-gradient(circle 5px at 12% 84%,#fff 98%,transparent);
    background-size:300px 300px}}
  .logo{{width:74%;max-width:640px;filter:drop-shadow(0 10px 22px rgba(0,0,0,.28));z-index:2}}
  .tom{{width:44%;max-width:380px;z-index:2;filter:drop-shadow(0 10px 18px rgba(0,0,0,.3))}}
  .sub{{z-index:2;font-size:52px;font-weight:900;letter-spacing:.04em;text-shadow:0 2px 0 rgba(0,0,0,.22);line-height:1.5}}
  .small{{z-index:2;font-size:34px;font-weight:700;opacity:.9;margin-top:-10px}}
  .tag{{z-index:2;font-size:30px;font-weight:800;background:rgba(255,255,255,.16);
    border:2px solid rgba(255,255,255,.45);border-radius:999px;padding:12px 34px}}
</style>
{body}
"""

INTRO = CARD.format(W=W, H=H, body=f"""
  <img class=logo src="{LOGO}">
  <div class=sub>Lesson 1「Tom at the Gate」<br>を、まるごと完食</div>
  <div class=tag>🎵 うた → 🥩🍅🧀🥫🥬 5つの具材 → 🌮 完成</div>
""")

OUTRO = CARD.format(W=W, H=H, body=f"""
  <img class=tom src="{TOM}">
  <div class=sub>🌮 タコス、完成！</div>
  <div class=small>ブラウザだけで、無料で遊べます</div>
  <div class=tag>taco-course.pages.dev</div>
""")


def shot(html, path):
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        pg.set_content(html, wait_until="networkidle")
        pg.wait_for_timeout(600)
        pg.screenshot(path=path)
        b.close()


if __name__ == "__main__":
    shot(INTRO, "_video/card_intro.png")
    shot(OUTRO, "_video/card_outro.png")
    print("cards written")
