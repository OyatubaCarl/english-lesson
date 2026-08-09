#!/usr/bin/env python3
"""タコスパーティー画面探索ハーネス: 起動→指定クリック列を実行→現在画面の
可視インタラクティブ要素を列挙する。導線発見用。"""
import sys, json
from playwright.sync_api import sync_playwright

URL = "http://localhost:8790/taco_course_mockup/app.html"

# コマンドライン引数 = 順に実行するアクション。形式:
#   "text:ラベル"   … 可視テキストに一致する要素をクリック
#   "sel:CSSセレクタ" … セレクタをクリック
#   "wait:1200"     … 待機(ms)
ACTIONS = sys.argv[1:]

DUMP_JS = r"""
() => {
  const out = [];
  const seen = new Set();
  const cand = document.querySelectorAll('button,[onclick],.btn,.tab,[role=button],a,.opt,.choice,.card,.tile,li');
  for (const el of cand) {
    const r = el.getBoundingClientRect();
    if (r.width < 4 || r.height < 4) continue;
    const st = getComputedStyle(el);
    if (st.display === 'none' || st.visibility === 'hidden' || st.opacity === '0') continue;
    // 画面外(非active screen)を除外: 祖先に .screen があり active でないものは飛ばす
    let scr = el.closest('.screen,.view,section');
    const t = (el.innerText||el.textContent||'').trim().replace(/\s+/g,' ').slice(0,40);
    const id = el.id ? '#'+el.id : '';
    const cls = (el.className && typeof el.className==='string') ? '.'+el.className.trim().split(/\s+/).slice(0,3).join('.') : '';
    const key = id+cls+t;
    if (seen.has(key)) continue; seen.add(key);
    out.push({tag: el.tagName.toLowerCase(), id, cls, text: t,
              x: Math.round(r.x+r.width/2), y: Math.round(r.y+r.height/2)});
  }
  // アクティブなscreen/viewの識別
  const active = [...document.querySelectorAll('.screen.active,.view.active,section.active,[class*=active]')]
     .map(e=>e.id||e.className).filter(Boolean).slice(0,6);
  return {active, els: out};
}
"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 420, "height": 860})
    pg.goto(URL, wait_until="networkidle", timeout=20000)
    pg.wait_for_timeout(800)
    log = []
    for a in ACTIONS:
        try:
            if a.startswith("wait:"):
                pg.wait_for_timeout(int(a[5:]))
            elif a.startswith("sel:"):
                pg.click(a[4:], timeout=4000)
                pg.wait_for_timeout(600)
            elif a.startswith("text:"):
                pg.get_by_text(a[5:], exact=False).first.click(timeout=4000)
                pg.wait_for_timeout(600)
            log.append(f"OK  {a}")
        except Exception as e:
            log.append(f"ERR {a} :: {type(e).__name__} {str(e)[:80]}")
    state = pg.evaluate(DUMP_JS)
    print("=== ACTION LOG ===")
    print("\n".join(log))
    print("=== ACTIVE:", state["active"])
    print("=== VISIBLE INTERACTIVE ELEMENTS ===")
    for e in state["els"]:
        print(f"  ({e['x']:>3},{e['y']:>3}) {e['tag']:6} {e['id']:16} {e['cls'][:28]:28} | {e['text']}")
    pg.screenshot(path="_video/_explore_last.png")
    b.close()
print("screenshot -> _video/_explore_last.png")
