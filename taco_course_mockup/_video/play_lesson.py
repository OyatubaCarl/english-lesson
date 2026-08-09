#!/usr/bin/env python3
"""Teacher Tacos English タコスパーティー — Lesson1 実機プレイ自動走行 & 録画。

各ゲートを「本物の入力」で完食する:
  beat    : __tbDebug.getNotes() の実ノーツ時刻に D/F/J/K を送出（本物の判定・スコア）
  tomato  : 文中の語をタップ→正しい意味の choice をタップ（8語）
  cheese  : シャドウイング開始→ハンズフリー→擬似モードで全文自動通過
  salsa   : __ttfSalsa.words の正解列で正しいボトルをタップ（10問）
  lettuce : __ttfReorderCur.answer の順にタイルをタップ→答え合わせ

使い方:
  play_lesson.py test <gate>   # hub まで進んで1ゲートだけ実行→進捗を検証（録画なし）
  play_lesson.py full          # 全ゲート通し→タコス完成まで録画（webm出力）
"""
import sys, time
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8790/taco_course_mockup"
URL = BASE + "/app_rec.html"
VW, VH = 430, 880           # 端末フレーム（mobileレイアウトが全面になる幅）
SCALE = 2                    # 録画の高精細化

# Lesson1(L12) の新出語→意味（トマトマトの正解選択用）
TOMATO_MEAN = {
    "island": "島", "gate": "門", "welcome": "歓迎されている", "name": "名前",
    "guide": "案内役、案内する", "excited": "わくわくしている",
    "amazing": "すごい、驚くほど素晴らしい", "strange": "不思議な、奇妙な",
}


def ms(page, n):
    page.wait_for_timeout(n)


def dismiss_intro(page):
    """説明モーダル(.intro-box)が出ていたら「はじめる！」を押す。"""
    try:
        btn = page.locator(".intro-box button")
        if btn.count() and btn.first.is_visible():
            btn.first.click()
            ms(page, 350)
            return True
    except Exception:
        pass
    return False


def prog_bits(page):
    return page.evaluate(
        "()=>{try{return (JSON.parse(localStorage.getItem('ttf')||'{}').prog||{})['1']||null;}catch(e){return 'ERR:'+e;}}"
    )


def nav_to_hub(page):
    page.locator(".tapstart").click()
    ms(page, 700)
    page.get_by_text("パーティーをはじめる").first.click()
    ms(page, 700)
    page.get_by_text("ステージ 1", exact=False).first.click()
    ms(page, 700)
    page.get_by_text("タコスを作る", exact=False).first.click()
    ms(page, 900)


def show_song_intro(page):
    """hub でソングカードと歌詞を少し見せる（オープニング用の間）。"""
    ms(page, 900)
    try:
        page.get_by_text("歌詞（本文）を見る", exact=False).first.click()
        ms(page, 1800)
        # 折りたたみを閉じる
        page.get_by_text("歌詞（本文）を見る", exact=False).first.click()
        ms(page, 500)
    except Exception:
        pass


def open_gate(page, label):
    page.get_by_text(label, exact=False).first.click()
    ms(page, 900)
    dismiss_intro(page)


# ---------------- 各ゲート ----------------

def do_tomato(page):
    open_gate(page, "トマトマト")
    for _ in range(8):
        # 前の収穫シートが完全に閉じ、次の語が出るまで待つ
        page.wait_for_selector(".vsheet-bg", state="detached", timeout=8000)
        page.wait_for_selector(".vword:not(.done)", state="visible", timeout=8000)
        ms(page, 550)
        page.locator(".vword:not(.done)").first.click()
        page.wait_for_selector(".vsheet .choice", state="visible", timeout=8000)
        ms(page, 500)
        word = page.locator(".vsheet .w").inner_text().replace("🍅", "").strip()
        mean = TOMATO_MEAN.get(word)
        choices = page.locator(".vsheet .choice")
        n = choices.count()
        clicked = False
        for k in range(n):
            t2 = choices.nth(k).inner_text().lstrip("ABCD").strip()
            if mean and (t2 == mean or mean in choices.nth(k).inner_text()):
                choices.nth(k).click()
                clicked = True
                break
        if not clicked and n:  # 保険
            choices.first.click()
        ms(page, 800)
    page.wait_for_selector("text=具材ゲット", timeout=8000)
    page.get_by_text("具材ゲット", exact=False).first.click()
    ms(page, 700)


def _wait_salsa_n(page, prefix, timeout=12000):
    """`.salsa-n` が「<prefix> /」で始まるまで待つ（問題番号の同期）。"""
    end = time.time() + timeout / 1000
    while time.time() < end:
        try:
            t = page.locator(".salsa-n").first.inner_text()
            if t.strip().startswith(prefix + " /"):
                return True
        except Exception:
            pass
        page.wait_for_timeout(150)
    return False


def do_salsa(page):
    open_gate(page, "サルサグラマー")
    ms(page, 600)
    page.get_by_text("サルサを仕込む", exact=False).first.click()
    ms(page, 900)
    words = page.evaluate("()=>window.__ttfSalsa?window.__ttfSalsa.words:null")
    total = len(words)
    for qi in range(total):
        # この問題の番号が出るまで待つ＝正しい問題に同期
        _wait_salsa_n(page, str(qi + 1))
        page.wait_for_selector(".bottle-row .bottle", timeout=8000)
        ms(page, 500)
        target = str(words[qi])
        bottles = page.locator(".bottle-row .bottle")
        nb = bottles.count()
        done = False
        for k in range(nb):
            if bottles.nth(k).locator(".b-word").inner_text().strip() == target:
                bottles.nth(k).click()
                done = True
                break
        if not done and nb:
            bottles.first.click()
        if qi < total - 1:
            _wait_salsa_n(page, str(qi + 2))   # 次問へ遷移するのを待つ
        else:
            page.wait_for_selector("text=具材ゲット", timeout=12000)
    page.get_by_text("具材ゲット", exact=False).first.click()
    ms(page, 700)


def do_shadow(page):
    open_gate(page, "シャドウイング")
    ms(page, 500)
    # ハンズフリーON（通過ごとに自動で次の文へ）。input は非表示なのでスイッチ(label)をクリック
    try:
        hf = page.locator(".hf-chip input[type=checkbox]").first
        if hf.count() and not hf.is_checked():
            page.locator(".hf-chip .switch").first.click()
            ms(page, 200)
    except Exception:
        pass
    # 開始
    page.get_by_text("シャドウイング開始", exact=False).first.click()
    # 擬似モードで10文自動通過するのを待つ（最大90秒）。完了=「具材ゲット」出現
    end = time.time() + 90
    while time.time() < end:
        try:
            if page.get_by_text("具材ゲット", exact=False).count():
                break
        except Exception:
            pass
        ms(page, 800)
    if page.get_by_text("具材ゲット", exact=False).count():
        page.get_by_text("具材ゲット", exact=False).first.click()
        ms(page, 700)


def do_lettuce(page):
    open_gate(page, "シャキシャキ・レタス")
    ms(page, 700)
    # 問題数は最大10。答えが尽きるまで解く
    for _ in range(12):
        # 完了バナー？
        if page.get_by_text("具材ゲット", exact=False).count():
            break
        page.wait_for_selector(".ro-bank .ro-tile", timeout=8000)
        cur = page.evaluate("()=>{const c=window.__ttfReorderCur; if(!c)return null;"
                            "const norm=window.__ttfReorder.tiles(c);"
                            "return {ans:c.answer, norm:norm.slice(0,(c.answer||[]).length)};}")
        if not cur:
            break
        for tok in cur["norm"]:
            # bank内で該当テキストのタイルを1枚タップ（末尾に追加）
            tile = page.locator(".ro-bank .ro-tile").filter(has_text=None)
            # 完全一致で探す
            loc = page.get_by_role("button", name=tok, exact=True)
            # bank配下に限定
            bank_tile = page.locator(".ro-bank .ro-tile", has_text=tok)
            target = None
            cnt = bank_tile.count()
            for k in range(cnt):
                if bank_tile.nth(k).inner_text().strip() == tok:
                    target = bank_tile.nth(k)
                    break
            if target is None and cnt:
                target = bank_tile.first
            if target:
                target.click()
                ms(page, 260)
        ms(page, 250)
        page.get_by_text("答え合わせ", exact=False).first.click()
        # 正解演出（レタス）→次の問題 or fin
        ms(page, 2200)
    if page.get_by_text("具材ゲット", exact=False).count():
        page.get_by_text("具材ゲット", exact=False).first.click()
        ms(page, 700)


def do_beat(page, mark=None):
    open_gate(page, "タコビート")
    ms(page, 1500)
    # iframe を取得
    frame = None
    for _ in range(20):
        for f in page.frames:
            if "taco_beat" in (f.url or ""):
                frame = f
                break
        if frame:
            break
        ms(page, 300)
    if not frame:
        print("  [beat] iframe not found")
        return
    # START を押す（曲Blobロード完了まで待ってから）
    try:
        frame.wait_for_selector("#startBtn:not([disabled])", timeout=15000)
    except Exception:
        pass
    ms(page, 400)
    frame.locator("#startBtn").click()
    # 自動プレイヤーを iframe 内に注入（実ノーツ時刻に D/F/J/K を送出）
    ms(page, 300)
    # 曲(b1.mp3)が動き出した瞬間を記録（BGM同期の基準）
    if mark is not None:
        songt = 0.0
        for _ in range(120):
            try:
                songt = frame.evaluate("()=>{try{return window.__tbDebug.endState().songT||0;}catch(e){return 0;}}")
            except Exception:
                songt = 0
            if songt and songt > 0.08:
                break
            ms(page, 60)
        mark("beat_song0", extra={"songT": songt})
    frame.evaluate(r"""
      () => {
        const dbg = window.__tbDebug; if(!dbg) return;
        const LANE2CODE = ['KeyD','KeyF','KeyJ','KeyK'];
        let notes = [];
        const fired = new Set(); const held = {};
        window.__autoDone = false;
        function key(type, code){ window.dispatchEvent(new KeyboardEvent(type,{code,key:code,bubbles:true})); }
        function loop(){
          try{
            if(!notes.length){ notes = dbg.getNotes()||[]; }
            const st = dbg.endState(); const now = st.now;
            for(let i=0;i<notes.length;i++){
              const n = notes[i]; if(fired.has(i)) continue;
              if(now >= n.t - 0.02){
                fired.add(i);
                const code = LANE2CODE[n.lane]||'KeyD';
                key('keydown', code);
                if(n.hold && n.tEnd>n.t){ held[i]={code, rel:n.tEnd}; }
                else { setTimeout(()=>key('keyup', code), 40); }
              }
            }
            for(const k in held){ if(now>=held[k].rel){ key('keyup',held[k].code); delete held[k]; } }
            if(st.ended){ window.__autoDone=true; return; }
          }catch(e){}
          requestAnimationFrame(loop);
        }
        requestAnimationFrame(loop);
      }
    """)
    # 合格して「具材ゲット」ボタンが親に出るまで待つ（曲尺ぶん、最大120秒）
    end = time.time() + 120
    while time.time() < end:
        if page.get_by_text("具材ゲット", exact=False).count():
            break
        ms(page, 700)
    if page.get_by_text("具材ゲット", exact=False).count():
        page.get_by_text("具材ゲット", exact=False).first.click()
        ms(page, 800)
    else:
        print("  [beat] pass button not found (timeout)")


GATES = {"beat": do_beat, "tomato": do_tomato, "cheese": do_shadow,
         "shadow": do_shadow, "salsa": do_salsa, "lettuce": do_lettuce}


def make_context(p, record_dir=None):
    browser = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required",
                                       "--use-fake-ui-for-media-stream",
                                       "--use-fake-device-for-media-stream"])
    kw = dict(viewport={"width": VW, "height": VH}, device_scale_factor=SCALE,
              permissions=["microphone"])
    if record_dir:
        kw["record_video_dir"] = record_dir
        kw["record_video_size"] = {"width": VW * SCALE, "height": VH * SCALE}
    ctx = browser.new_context(**kw)
    ctx.add_init_script(
        "try{localStorage.setItem('ttf',JSON.stringify({level:1,prog:{},beatMode:0,beatDiff:0,beatSpeed:1}));}catch(e){}"
    )
    # シャドウイング用フェイク認識: 画面に出ている文を「聞き取った」ことにして返す。
    # → 実ゲームのマッチング処理を本物の入力で駆動（単語が緑に光る＝実機の読み上げ成功と同じ挙動）。
    ctx.add_init_script(r"""
      (function(){
        function FakeSR(){ this.lang=''; this.continuous=false; this.interimResults=false; }
        FakeSR.prototype.start=function(){
          var self=this; if(self.onstart)try{self.onstart();}catch(e){}
          setTimeout(function(){
            var ws=[].slice.call(document.querySelectorAll('.shline .sh-word')).map(function(e){return e.textContent;});
            var txt=ws.join(' ');
            var res=[[{transcript:txt}]]; res[0].isFinal=true; res.length=1;
            var ev={resultIndex:0, results:res};
            if(self.onresult)try{self.onresult(ev);}catch(e){}
            setTimeout(function(){ if(self.onend)try{self.onend();}catch(e){} },120);
          }, 850);
        };
        FakeSR.prototype.stop=function(){ if(this.onend)try{this.onend();}catch(e){} };
        FakeSR.prototype.abort=function(){ if(this.onend)try{this.onend();}catch(e){} };
        window.webkitSpeechRecognition=FakeSR; window.SpeechRecognition=FakeSR;
      })();
    """)
    return browser, ctx


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "test"
    with sync_playwright() as p:
        if mode == "test":
            gate = sys.argv[2]
            browser, ctx = make_context(p)
            page = ctx.new_page()
            page.goto(URL, wait_until="networkidle", timeout=30000)
            nav_to_hub(page)
            GATES[gate](page)
            ms(page, 800)
            bits = prog_bits(page)
            page.screenshot(path=f"_video/_test_{gate}.png")
            print(f"[{gate}] prog bits = {bits}")
            browser.close()
        elif mode == "full":
            import json
            browser, ctx = make_context(p, record_dir="_video/rec")
            page = ctx.new_page()
            T0 = time.monotonic()          # ≒録画開始（page生成直後）
            marks = []

            def mark(name, extra=None):
                m = {"name": name, "t": round(time.monotonic() - T0, 3)}
                if extra:
                    m.update(extra)
                marks.append(m)
                return m

            page.goto(URL, wait_until="networkidle", timeout=30000)
            mark("goto")
            nav_to_hub(page)
            mark("hub")
            show_song_intro(page)
            mark("beat_open")
            do_beat(page, mark=mark)
            mark("tomato_open")
            do_tomato(page)
            mark("shadow_open")
            do_shadow(page)
            mark("salsa_open")
            do_salsa(page)
            mark("lettuce_open")
            do_lettuce(page)
            mark("complete")
            # タコス完成演出
            ms(page, 5500)
            mark("end")
            bits = prog_bits(page)
            print("final prog bits =", bits)
            vid = page.video.path()
            ctx.close()          # 録画を確定
            browser.close()
            with open("_video/timings.json", "w") as f:
                json.dump({"marks": marks, "video": vid}, f, ensure_ascii=False, indent=2)
            print("VIDEO:", vid)
            print("MARKS:", marks)


if __name__ == "__main__":
    main()
