"""
すでに note.com にログイン済みの「あなたの普段のChrome」へ CDP 接続して下書き投稿する。
Googleログインを自動化する必要がない（既存セッションをそのまま使う）ので確実。

前提: Chrome を一度終了し、デバッグモードで起動しておくこと:
    open -a "Google Chrome" --args --remote-debugging-port=9222
（ログインCookieは既定プロファイルに残るのでログイン状態は維持される）

実行: python3 post_to_note_cdp.py
本文・タイトル・画像の定義は post_to_note_music.py を再利用する。
"""
import sys
import time
from playwright.sync_api import sync_playwright
import post_to_note_music as m

CDP_URL = "http://localhost:9222"


def wait_until_logged_in(page, max_wait=600) -> bool:
    """タブのURLを監視（再ナビゲーションせず）し、note.com 上で /login でも
    Google認証中でもない状態＝ログイン完了になるまで待つ。ユーザーのログイン操作を邪魔しない。"""
    deadline = time.time() + max_wait
    while time.time() < deadline:
        try:
            url = page.url
            if "note.com" in url and "/login" not in url and "accounts.google.com" not in url:
                return True
        except Exception:
            pass
        time.sleep(3)
    return False


def fill_draft(page) -> bool:
    page.bring_to_front()
    print("記事作成ページへ移動中...", flush=True)
    page.goto("https://note.com/notes/new", wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(2000)

    if "/login" in page.url or "accounts.google.com" in page.url:
        print("このChromeは note.com にログインしていません。"
              "普段ログインしているプロファイルのChromeで起動してください。", flush=True)
        return False

    print(f"URL: {page.url}", flush=True)

    title_sel = 'textarea[placeholder*="タイトル"], input[placeholder*="タイトル"]'
    try:
        page.wait_for_selector(title_sel, timeout=15000)
        page.click(title_sel)
        page.type(title_sel, m.TITLE, delay=15)
        print("タイトル入力完了", flush=True)
    except Exception as e:
        print(f"タイトル欄エラー: {e}", flush=True)

    page.wait_for_timeout(500)
    page.keyboard.press("Tab")
    page.wait_for_timeout(400)
    page.evaluate("() => { const el = document.querySelector('[contenteditable=\"true\"]'); if (el) el.focus(); }")
    page.wait_for_timeout(300)

    for i, (text, ss_name) in enumerate(m.ARTICLE):
        print(f"セクション {i+1}/{len(m.ARTICLE)}", flush=True)
        m.type_text(page, text)
        page.wait_for_timeout(300)
        if ss_name:
            page.keyboard.press("Enter")
            page.keyboard.press("Enter")
            page.wait_for_timeout(300)
            m.insert_image(page, ss_name)
        page.keyboard.press("Enter")
        page.keyboard.press("Enter")
        page.wait_for_timeout(200)

    print("下書き保存中...", flush=True)
    try:
        save_btn = page.query_selector('button:has-text("下書き保存"), button:has-text("保存")')
        if save_btn:
            save_btn.click()
            page.wait_for_timeout(2000)
            print("下書き保存完了", flush=True)
        else:
            page.keyboard.press("Meta+s")
            page.wait_for_timeout(1500)
            print("Cmd+S で保存", flush=True)
    except Exception as e:
        print(f"保存エラー: {e}", flush=True)
    return True


def main():
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(CDP_URL)
        except Exception as e:
            print(f"Chromeに接続できません（{CDP_URL}）。"
                  "Chromeをデバッグモードで起動してください:\n"
                  '  open -a "Google Chrome" --args --remote-debugging-port=9222', flush=True)
            print(f"詳細: {e}", flush=True)
            sys.exit(1)

        ctx = browser.contexts[0] if browser.contexts else browser.new_context()
        # 既存の note タブを探す。なければ作る。
        page = None
        for pg in ctx.pages:
            try:
                if "note.com" in pg.url:
                    page = pg
                    break
            except Exception:
                pass
        if page is None:
            page = ctx.new_page()
            try:
                page.goto("https://note.com/notes/new", wait_until="domcontentloaded", timeout=30000)
            except Exception:
                pass

        print("\n" + "=" * 50, flush=True)
        print("開いている Chrome で note.com にログインしてください。", flush=True)
        print("（このChromeは自動操作フラグが付いていないので Googleログインも通ります）", flush=True)
        print("ログインを検知すると自動で下書きを作成します。最大10分待ちます。", flush=True)
        print("=" * 50, flush=True)

        if not wait_until_logged_in(page):
            print("ログインされなかったため終了します。", flush=True)
            return

        print("ログイン確認。下書きを作成します。", flush=True)
        ok = fill_draft(page)
        # あなたの普段のChromeなので絶対に閉じない（disconnectのみ）
        print("\n" + "=" * 50, flush=True)
        if ok:
            print("完了！開いた下書きタブの内容を確認して「公開する」を押してください。", flush=True)
        else:
            print("未完了。ログイン状態を確認してください。", flush=True)
        print("=" * 50, flush=True)


if __name__ == "__main__":
    main()
