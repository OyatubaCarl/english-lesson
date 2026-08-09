"""
note.com に画像付き記事を投稿するスクリプト v2
"""

import subprocess
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

PROJ = Path("/Users/masaki/Library/CloudStorage/GoogleDrive-sarosaro36@gmail.com/マイドライブ/個人用/ClaudeCode/英語学習教材作成")
SS = PROJ / "tmp_site_screenshots"

TITLE = "歌・日本語混じり文・構文解析・シャドウイング——認知科学に基づく英語学習の多段階アプローチ"

# (テキスト, 直後に挿入するスクリーンショット名 or None)
ARTICLE = [
    (
        "英語学習サイト「Funnics Island」は、フォニックスから高校読解まで、同一の教材テキストを複数の方法で学べるように設計されています。この記事では、なぜこのような多段階の学び方が効果的なのかを、認知科学的な背景とともに説明します。",
        "01_top",
    ),
    (
        "## 1. 歌で学ぶ——音韻が記憶を定着させる\n\nこのサイトのレッスンテキストは、そのまま歌になっています。YouTubeの動画でメロディーとともに英文を聴くことができます。\n\n歌には、通常の読み書きと異なる脳の使い方を引き出す力があります。言語理解を担うのが主に左脳の言語野であるのに対し、音楽は両側の大脳半球を広く活性化します。特に**音韻を捉えようとするプロセス**では、文法分析や意味理解より前に、音のパターンをリズムとして取り込む回路が働きます。\n\nさらに実用的な理由として、**歌は頭の中で繰り返しやすい**という特徴があります。いわゆる「耳に残る」状態です。勉強中に意識的に繰り返さなくても、メロディーに乗った英文が自然に頭の中で再生されます。これは、学習効果のある反復が**ほぼ無意識に、ストレスなく**行われているということを意味します。\n\nBGMとして流しっぱなしにできることも大きなメリットです。英語学習の最大の障壁のひとつは「続かないこと」ですが、歌は苦痛なく繰り返し聴けるため、学習量を自然に増やすことができます。",
        "03_lesson_b1_default",
    ),
    (
        "## 2. 日本語混じり文で単語を学ぶ——意味ネットワークへの統合\n\nこのサイトには「英語＋日本語ルビ」表示モードがあります。日本語の文章の流れを保ちながら、英単語がルビ付きで登場する形式です。\n\nこの学習法の有効性は、**意味ネットワーク**の概念で説明できます。\n\n人間の記憶の中では、言葉が孤立した形で存在するのではなく、意味的・感情的・文脈的な関連のネットワークとして存在しています。日本語で生活している学習者は、すでに豊かな日本語の意味ネットワークを持っています。\n\n英語だけで英語を学ぼうとすると、英語の単語同士の関係を一から構築する必要があります。しかし**日本語の文脈の中に英語単語を埋め込む**ことで、すでに出来上がっている意味ネットワークに英語の単語を接続することができます。\"parking\" という単語を見たとき、「駐車場に停める」という行為にまつわる身体的・空間的なイメージが一緒に呼び起こされるのです。\n\n認知言語学では、これを「足場かけ（スキャフォールディング）」と呼びます。新しい言語の概念を既知の認知構造に吊り下げることで、学習の負荷を大幅に下げることができます。文脈の中で英単語に触れることは、単語帳で孤立した訳語を暗記するより、はるかに定着率が高いのです。",
        "05_mode_en_ja_mix",
    ),
    (
        "## 3. 構文解析で文法を視覚化する——パターン認識としての文法\n\n高校編のレッスンには「構文解析」モードがあります。各文のすべての単語やフレーズが、S（主語）・V（動詞）・O（目的語）・C（補語）・M（修飾語）に色分けされ、構造が一目でわかるように表示されます。\n\n文法は「ルール」として暗記するより、**パターン**として視覚的に認識できるほうが使いやすくなります。構文解析の色分けを繰り返し目にすることで、英文の構造を読みながら感じ取れるようになっていきます。\n\nフレーズ単位でのかたまり（チャンク）の表示も重要です。英語を単語ひとつひとつではなく、意味のかたまりとして処理できるようになることが、読解速度と理解度の向上につながります。",
        "11_syntax_mode",
    ),
    (
        "## 4. 絵本モードで場面と英語を結びつける\n\n入門英語（Funnics Island）には「絵本」表示モードがあります。主人公トムが島を冒険しながら英語表現を使う、物語形式の教材です。\n\n言語習得において、**場面・文脈・感情との結びつき**は記憶の定着を助けます。絵本形式は、英文を抽象的な文字列としてではなく、登場人物の行動・感情・物語の流れとともに記憶させます。",
        "07_mode_picturebook",
    ),
    (
        "## 5. シャドウイングで英語を体に入れる\n\nシャドウイング練習モードでは、音声に少し遅れてついて声に出す練習ができます。マイクで発音を認識し、どの単語が正しく言えたかをリアルタイムでフィードバックします。\n\nシャドウイングが有効なのは、英語の習得が**音と意味の自動的なマッピング**を必要とするからです。読んで理解できる英語と、聞いてすぐわかる英語は別物です。音のイントネーション・リズム・連結を体に馴染ませるには、実際に声に出す練習が必要です。\n\n歌でリズムを体に入れ、日本語混じり文で単語の意味を固め、構文解析で文構造を把握した後に行うシャドウイングは、これらの知識を**瞬間的に使える形**に変換する仕上げの工程です。",
        "08_shadowing_start",
    ),
    (
        "## 6. 単語テストで定着を確認する\n\n各レッスンには単語テスト（クイズ）機能があります。学習した単語が出題され、その単語を音声で確認することもできます。\n\nテスト（検索練習）は、単に覚えているかを確認するためだけでなく、記憶そのものを強化します。これは**想起練習効果（テスト効果）**として認知心理学でよく知られた現象です。一度頭から引き出そうとする行為が、次回の想起をより確実にします。",
        "12_word_quiz",
    ),
    (
        "## 7. 学習の流れ——「聴く」から「使う」へ\n\nこのサイトでの理想的な学習の流れは次のようなものです。\n\n1. **動画（歌）** でメロディーとともに英文を耳に入れる\n2. **日本語混じり文** で個々の単語を意味ネットワークに統合する\n3. **英語のみ** 表示や **IPA（発音記号）** 表示で英文そのものと向き合う\n4. **構文解析** で文の骨格（文型・構造）を視覚的に把握する\n5. **日本語訳** で意味の確認をする\n6. **単語テスト** で語彙の定着を確認する\n7. **シャドウイング** で英語を音として身体化する\n8. **長文読解**（高校編）で総合的な読解力を養う\n\n各ステップは独立して使えますが、この順序で使うことで**音・語彙・文法・表現の理解が重なり合い**、英語が複数の経路から定着していきます。",
        None,
    ),
    (
        "## おわりに\n\n英語学習に「これさえやれば」という万能の方法はありません。しかし、**様々な認知経路から同じ素材に繰り返しアクセスする**ことは、記憶の定着と運用力の両面で効果的であることが知られています。\n\nFunnics Islandは、ひとつのレッスンテキストを歌・絵本・語彙・文法・発音・シャドウイングという異なる角度から学べるよう設計されています。自分のレベルや目的、その日の気分に合わせて使い方を選べるのが、このサイトの特徴です。\n\nhttps://english-lesson.gasflare.workers.dev",
        None,
    ),
]


def wait_for_login(page):
    print("\n" + "=" * 50)
    print("ブラウザが開きました。note.com にログインしてください。")
    print("=" * 50, flush=True)
    try:
        page.wait_for_function(
            "() => !window.location.pathname.startsWith('/login')",
            timeout=120_000,
        )
        print("ログイン確認済み", flush=True)
    except Exception:
        print("タイムアウト — 続行します", flush=True)


def copy_image_to_clipboard(image_path: str):
    """macOS クリップボードに PNG 画像をコピー"""
    script = f'set the clipboard to (read (POSIX file "{image_path}") as «class PNGf»)'
    subprocess.run(["osascript", "-e", script], check=True)


def insert_image(page, ss_name: str):
    """スクリーンショットをクリップボード経由でエディタに貼り付け"""
    img_path = str(SS / f"{ss_name}.png")
    if not Path(img_path).exists():
        print(f"  スクリーンショットが見つかりません: {img_path}", flush=True)
        return

    print(f"  画像挿入中: {ss_name}.png", flush=True)

    # 画像をクリップボードへ
    copy_image_to_clipboard(img_path)
    page.wait_for_timeout(400)

    # エディタにフォーカスして貼り付け
    page.keyboard.press("Meta+v")
    page.wait_for_timeout(3000)  # アップロード完了を待つ
    print(f"  画像貼り付け完了: {ss_name}", flush=True)


def type_text(page, text: str):
    """テキストをクリップボード経由で高速入力"""
    subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=True)
    page.wait_for_timeout(200)
    page.keyboard.press("Meta+v")
    page.wait_for_timeout(500)


def post_article(page):
    print("\n記事作成ページへ移動中...", flush=True)
    page.goto("https://note.com/notes/new", wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(2000)

    if "/login" in page.url:
        print("再ログインが必要です", flush=True)
        page.wait_for_function(
            "() => !window.location.pathname.startsWith('/login')",
            timeout=120_000,
        )
        page.goto("https://note.com/notes/new", wait_until="networkidle")
        page.wait_for_timeout(2000)

    print(f"URL: {page.url}", flush=True)

    # タイトル入力
    print("タイトルを入力中...", flush=True)
    title_sel = 'textarea[placeholder*="タイトル"], input[placeholder*="タイトル"]'
    try:
        page.wait_for_selector(title_sel, timeout=15000)
        page.click(title_sel)
        page.type(title_sel, TITLE, delay=15)
        print("  タイトル入力完了", flush=True)
    except Exception as e:
        print(f"  タイトル欄エラー: {e}", flush=True)

    page.wait_for_timeout(500)

    # 本文エリアにフォーカス
    page.keyboard.press("Tab")
    page.wait_for_timeout(400)
    page.evaluate("() => { const el = document.querySelector('[contenteditable=\"true\"]'); if (el) el.focus(); }")
    page.wait_for_timeout(300)

    # セクションごとにテキスト + 画像を挿入
    for i, (text, ss_name) in enumerate(ARTICLE):
        print(f"\nセクション {i+1}/{len(ARTICLE)} を入力中...", flush=True)

        type_text(page, text)
        page.wait_for_timeout(300)

        if ss_name:
            # 改行して画像を挿入
            page.keyboard.press("Enter")
            page.keyboard.press("Enter")
            page.wait_for_timeout(300)
            insert_image(page, ss_name)

        # セクション間の改行
        page.keyboard.press("Enter")
        page.keyboard.press("Enter")
        page.wait_for_timeout(200)

    # 下書き保存
    print("\n下書き保存中...", flush=True)
    try:
        save_btn = page.query_selector('button:has-text("下書き保存"), button:has-text("保存")')
        if save_btn:
            save_btn.click()
            page.wait_for_timeout(2000)
            print("  下書き保存完了", flush=True)
        else:
            page.keyboard.press("Meta+s")
            page.wait_for_timeout(1500)
            print("  Cmd+S で保存", flush=True)
    except Exception as e:
        print(f"  保存エラー: {e}", flush=True)

    print("\n" + "=" * 50, flush=True)
    print("完了！内容を確認して「公開する」を押してください。", flush=True)
    print("=" * 50, flush=True)

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        pass


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--start-maximized"])
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()

        page.goto("https://note.com/login", wait_until="domcontentloaded")
        page.wait_for_timeout(1500)

        wait_for_login(page)
        post_article(page)

        browser.close()


if __name__ == "__main__":
    main()
