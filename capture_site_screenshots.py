"""
サイトのスクリーンショットを取得するスクリプト
各学習モードをクリックして状態別に撮影する
"""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = "https://english-lesson.gasflare.workers.dev"
OUT = Path("tmp_site_screenshots")
OUT.mkdir(exist_ok=True)

VP = {"width": 1440, "height": 900}


def shot(page, name: str):
    path = str(OUT / f"{name}.png")
    page.screenshot(path=path, full_page=False)
    print(f"  撮影: {name}.png")
    return path


def capture_all():
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--force-device-scale-factor=2"])
        page = browser.new_page(viewport=VP, device_scale_factor=2)
        page.goto(URL, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(1500)

        # ① トップ全体（教材選択前）
        shot(page, "01_top")

        # ② 入門英語を選択
        page.click('button[data-book="beginner"]')
        page.wait_for_timeout(800)
        shot(page, "02_beginner_selected")

        # ③ B1 レッスンを選択（selectドロップダウン）
        page.select_option('select[data-book="beginner"]', "1")
        page.wait_for_timeout(1000)
        shot(page, "03_lesson_b1_default")

        # ④ 英語のみモード
        page.click('button[data-mode="en"]')
        page.wait_for_timeout(400)
        shot(page, "04_mode_en_only")

        # ⑤ 英語＋日本語ルビ（日本語混じり文）
        page.click('button[data-mode="en-ja"]')
        page.wait_for_timeout(400)
        shot(page, "05_mode_en_ja_mix")

        # ⑥ 日本語訳
        page.click('button[data-mode="jp-full"]')
        page.wait_for_timeout(400)
        shot(page, "06_mode_jp_full")

        # ⑦ 絵本モード
        page.click('button[data-mode="picturebook"]')
        page.wait_for_timeout(600)
        shot(page, "07_mode_picturebook")

        # ⑧ ルビなし（デフォルト）に戻してからシャドウイングセクションへスクロール
        page.click('button[data-mode="plain"]')
        page.wait_for_timeout(400)
        sh_btn = page.query_selector(".btn-sh-start")
        if sh_btn:
            sh_btn.scroll_into_view_if_needed()
            page.wait_for_timeout(400)
            shot(page, "08_shadowing_start")

        # ⑨ 高校編を選択
        page.click('button[data-book="high1"]')
        page.wait_for_timeout(800)
        shot(page, "09_high1_selected")

        # ⑩ 高校編 H1 レッスン選択
        page.select_option('select[data-book="high1"]', "1")
        page.wait_for_timeout(800)
        shot(page, "10_high1_lesson1")

        # ⑪ 構文解析モード（H36に構文解析あり）
        page.select_option('select[data-book="high1"]', "36")
        page.wait_for_timeout(1000)
        # JavaScriptで非表示でもクリック可能なようにする
        clicked = page.evaluate("""
            () => {
                const btn = document.querySelector(
                    '#book-high1 .lesson:not(.hidden) button[data-mode="syntax"],' +
                    '.lesson:not(.hidden) button[data-mode="syntax"]'
                );
                if (btn && !btn.disabled) { btn.click(); return true; }
                // disabled でなければ強制クリック
                const allSyntax = document.querySelectorAll('button[data-mode="syntax"]');
                for (const b of allSyntax) {
                    const lesson = b.closest('.lesson');
                    if (lesson && !lesson.classList.contains('hidden') && !b.disabled) {
                        b.click(); return true;
                    }
                }
                return false;
            }
        """)
        page.wait_for_timeout(1000)
        if clicked:
            # 構文解析の色分け部分までスクロール
            page.evaluate("""
                () => {
                    const el = document.querySelector('.body-syntax:not(.hidden) .sentence');
                    if (el) el.scrollIntoView({behavior: 'instant', block: 'start'});
                }
            """)
            page.wait_for_timeout(400)
            shot(page, "11_syntax_mode")

        # ⑫ 単語テスト（クイズ）— JSでスクロール
        page.click('button[data-book="beginner"]')
        page.wait_for_timeout(600)
        page.select_option('select[data-book="beginner"]', "1")
        page.wait_for_timeout(800)
        page.evaluate("""
            () => {
                const el = document.querySelector('.lesson:not(.hidden) .quiz-word');
                if (el) el.scrollIntoView({behavior: 'instant', block: 'center'});
            }
        """)
        page.wait_for_timeout(500)
        shot(page, "12_word_quiz")

        browser.close()
    print(f"\n完了: {len(list(OUT.glob('*.png')))} 枚のスクリーンショットを {OUT} に保存")


if __name__ == "__main__":
    capture_all()
