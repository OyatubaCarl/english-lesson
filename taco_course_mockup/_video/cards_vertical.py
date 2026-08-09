#!/usr/bin/env python3
"""縦型ショート(1080x1920)用の フック/CTA カードを生成。"""
from playwright.sync_api import sync_playwright

W, H = 1080, 1920
LOGO = "http://localhost:8790/taco_course_mockup/app_assets/party/tacos_party_logo.png"
TOM = "http://localhost:8790/taco_course_mockup/app_assets/celebrate/tom_cheer.png"

BASE = """
<!doctype html><meta charset=utf-8>
<style>
  html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden}}
  body{{background:linear-gradient(170deg,#2563eb 0%,#1d4ed8 72%,#1e3a8a 100%);
    font-family:"Hiragino Maru Gothic ProN","Hiragino Sans",system-ui,sans-serif;color:#fff;
    display:flex;flex-direction:column;align-items:center;justify-content:center;gap:44px;text-align:center;position:relative}}
  body::before{{content:"";position:absolute;inset:0;opacity:.16;
    background:radial-gradient(circle 7px at 16% 20%,#fff 98%,transparent),
      radial-gradient(circle 6px at 78% 14%,#ffd76e 98%,transparent),
      radial-gradient(circle 7px at 88% 54%,#fff 98%,transparent),
      radial-gradient(circle 6px at 26% 74%,#ffd76e 98%,transparent),
      radial-gradient(circle 6px at 12% 86%,#fff 98%,transparent);background-size:340px 340px}}
  .logo{{width:80%;max-width:840px;filter:drop-shadow(0 12px 26px rgba(0,0,0,.3));z-index:2}}
  .tom{{width:52%;z-index:2;filter:drop-shadow(0 12px 22px rgba(0,0,0,.32))}}
  .big{{z-index:2;font-size:82px;font-weight:900;letter-spacing:.02em;line-height:1.35;text-shadow:0 3px 0 rgba(0,0,0,.22)}}
  .big b{{color:#ffd76e}}
  .mid{{z-index:2;font-size:52px;font-weight:800;opacity:.95;line-height:1.5}}
  .tag{{z-index:2;font-size:46px;font-weight:900;background:#ffd76e;color:#1e3a8a;border-radius:999px;padding:18px 48px;
    box-shadow:0 8px 0 rgba(0,0,0,.18)}}
</style>
{body}
"""

HOOK = BASE.format(W=W, H=H, body=f"""
  <img class=logo src="{LOGO}">
  <div class=big>英語の1レッスンを<br><b>まるごと「完食」</b>🌮</div>
  <div class=mid>歌 → 5つのミニゲーム → 完成</div>
""")

CTA = BASE.format(W=W, H=H, body=f"""
  <img class=tom src="{TOM}">
  <div class=big>ブラウザだけで<br><b>無料</b>で遊べる</div>
  <div class=tag>taco-course.pages.dev</div>
""")


def shot(html, path):
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        pg.set_content(html, wait_until="networkidle")
        pg.wait_for_timeout(500)
        pg.screenshot(path=path)
        b.close()


if __name__ == "__main__":
    shot(HOOK, "_video/card_hook_v.png")
    shot(CTA, "_video/card_cta_v.png")
    print("vertical cards written")
