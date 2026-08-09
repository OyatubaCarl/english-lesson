#!/usr/bin/env python3
"""タコス・パーティー記事(広報/note_tacoparty.md)を、ログイン済みChrome(CDP:9222)へ
接続して note の下書きを作成する。見出しは note の Markdown ショートカット("## ")、
YouTube URL は単独行で貼って自動埋め込み。最終公開・見出し画像は手動。
起動: open -a "Google Chrome" --args --remote-debugging-port=9222
"""
import re
import subprocess
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

CDP_URL = "http://localhost:9222"
MD = Path("/Users/masaki/Documents/ClaudeCode/英語学習教材作成/広報/note_tacoparty.md")
TITLE = "歌・単語・文法・音読・並べ替え。5つのミニゲームでタコスを作る英語学習アプリ"


def clean(t: str) -> str:
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", t)       # **bold** → bold
    t = re.sub(r"`([^`]+)`", r"\1", t)            # `code` → code
    return t.strip()


def parse_blocks():
    lines = MD.read_text(encoding="utf-8").splitlines()
    # 本文マーカー内 → 最初の "## " から本文終わりまで
    try:
        s = lines.index("---本文ここから---") + 1
        e = lines.index("---本文ここまで---")
    except ValueError:
        s, e = 0, len(lines)
    body = lines[s:e]
    # 最初の見出しから開始（プリアンブルのメタを飛ばす）
    for i, ln in enumerate(body):
        if ln.startswith("## "):
            body = body[i:]
            break
    blocks, para = [], []

    def flush():
        if para:
            blocks.append(("p", clean("".join(para))))
            para.clear()

    for ln in body:
        s_ln = ln.rstrip()
        if not s_ln.strip():
            flush(); continue
        if s_ln.startswith("## "):
            flush(); blocks.append(("h", clean(s_ln[3:]))); continue
        m = re.match(r"^(https?://\S+)$", s_ln.strip())
        if m:
            flush(); blocks.append(("embed", m.group(1))); continue
        if s_ln.lstrip().startswith("- "):
            flush(); blocks.append(("li", clean(s_ln.lstrip()[2:]))); continue
        para.append(s_ln)
    flush()
    return blocks


def paste(page, text):
    subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=True)
    page.wait_for_timeout(150)
    page.keyboard.press("Meta+v")
    page.wait_for_timeout(350)


def main():
    blocks = parse_blocks()
    print(f"blocks: {len(blocks)} (title='{TITLE[:24]}...')", flush=True)
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(CDP_URL)
        except Exception:
            print("Chrome(CDP:9222)に接続できません。次で起動してください:\n"
                  '  open -a "Google Chrome" --args --remote-debugging-port=9222', flush=True)
            return
        ctx = browser.contexts[0]
        page = ctx.new_page()
        page.goto("https://note.com/notes/new", wait_until="networkidle", timeout=40000)
        page.wait_for_timeout(2500)
        if "/login" in page.url or "accounts.google.com" in page.url:
            print("このChromeは note.com にログインしていません。ログインしてから再実行してください。", flush=True)
            return

        # タイトル
        tsel = 'textarea[placeholder*="タイトル"], input[placeholder*="タイトル"]'
        page.wait_for_selector(tsel, timeout=15000)
        page.click(tsel)
        paste(page, TITLE)
        print("タイトル入力", flush=True)
        page.wait_for_timeout(400)
        page.keyboard.press("Tab")
        page.wait_for_timeout(400)
        page.evaluate("() => { const el=document.querySelector('[contenteditable=\"true\"]'); if(el) el.focus(); }")
        page.wait_for_timeout(300)

        for i, (kind, text) in enumerate(blocks):
            print(f"  [{i+1}/{len(blocks)}] {kind}: {text[:26]}", flush=True)
            if kind == "h":
                page.keyboard.type("## ")      # note Markdownショートカット→見出し
                page.wait_for_timeout(150)
                paste(page, text)
                page.keyboard.press("Enter")
            elif kind == "li":
                page.keyboard.type("- ")
                page.wait_for_timeout(120)
                paste(page, text)
                page.keyboard.press("Enter")
            elif kind == "embed":
                paste(page, text)
                page.wait_for_timeout(500)
                page.keyboard.press("Enter")
                page.wait_for_timeout(2500)    # URL→埋め込みカード化を待つ
            else:  # paragraph
                paste(page, text)
                page.keyboard.press("Enter")
                page.keyboard.press("Enter")
            page.wait_for_timeout(200)

        page.wait_for_timeout(800)
        try:
            btn = page.query_selector('button:has-text("下書き保存"), button:has-text("保存")')
            if btn:
                btn.click(); page.wait_for_timeout(2500); print("下書き保存 完了", flush=True)
            else:
                page.keyboard.press("Meta+s"); page.wait_for_timeout(2000); print("Cmd+S 保存", flush=True)
        except Exception as ex:
            print("保存エラー:", ex, flush=True)
        print("DONE: note下書きを作成。ブラウザで内容を確認→見出し画像(card_intro.png)設定→公開ボタン。", flush=True)


if __name__ == "__main__":
    main()
