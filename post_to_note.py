"""
note.com に記事を自動投稿するスクリプト
実行: python3 post_to_note.py

手順:
1. ブラウザが開く
2. note.com にログインしてください（すでにログイン済みならスキップ）
3. ログイン後、ターミナルで Enter を押す
4. 自動で記事が入力される
5. 内容を確認して「公開する」ボタンを自分で押す
"""

import time
from playwright.sync_api import sync_playwright

# ========== 記事内容 ==========

TITLE = "歌・日本語混じり文・構文解析・シャドウイング——認知科学に基づく英語学習の多段階アプローチ"

BODY = """英語学習サイト「Funnics Island」は、フォニックスから高校読解まで、同一の教材テキストを複数の方法で学べるように設計されています。この記事では、なぜこのような多段階の学び方が効果的なのかを、認知科学的な背景とともに説明します。

## 1. 歌で学ぶ——音韻が記憶を定着させる

このサイトのレッスンテキストは、そのまま歌になっています。YouTubeの動画でメロディーとともに英文を聴くことができます。

歌には、通常の読み書きと異なる脳の使い方を引き出す力があります。言語理解を担うのが主に左脳の言語野であるのに対し、音楽は両側の大脳半球を広く活性化します。特に**音韻を捉えようとするプロセス**では、文法分析や意味理解より前に、音のパターンをリズムとして取り込む回路が働きます。

さらに実用的な理由として、**歌は頭の中で繰り返しやすい**という特徴があります。いわゆる「耳に残る」状態です。勉強中に意識的に繰り返さなくても、メロディーに乗った英文が自然に頭の中で再生されます。これは、学習効果のある反復が**ほぼ無意識に、ストレスなく**行われているということを意味します。

BGMとして流しっぱなしにできることも大きなメリットです。英語学習の最大の障壁のひとつは「続かないこと」ですが、歌は苦痛なく繰り返し聴けるため、学習量を自然に増やすことができます。

## 2. 日本語混じり文で単語を学ぶ——意味ネットワークへの統合

このサイトには「英語＋日本語ルビ」表示モードがあります。日本語の文章の流れを保ちながら、英単語がルビ付きで登場する形式です。

この学習法の有効性は、**意味ネットワーク**の概念で説明できます。

人間の記憶の中では、言葉が孤立した形で存在するのではなく、意味的・感情的・文脈的な関連のネットワークとして存在しています。日本語で生活している学習者は、すでに豊かな日本語の意味ネットワークを持っています。

英語だけで英語を学ぼうとすると、英語の単語同士の関係を一から構築する必要があります。しかし**日本語の文脈の中に英語単語を埋め込む**ことで、すでに出来上がっている意味ネットワークに英語の単語を接続することができます。"parking" という単語を見たとき、「駐車場に停める」という行為にまつわる身体的・空間的なイメージが一緒に呼び起こされるのです。

認知言語学では、これを「足場かけ（スキャフォールディング）」と呼びます。新しい言語の概念を既知の認知構造に吊り下げることで、学習の負荷を大幅に下げることができます。文脈の中で英単語に触れることは、単語帳で孤立した訳語を暗記するより、はるかに定着率が高いのです。

## 3. 構文解析で文法を視覚化する——パターン認識としての文法

高校編のレッスンには「構文解析」モードがあります。各文のすべての単語やフレーズが、S（主語）・V（動詞）・O（目的語）・C（補語）・M（修飾語）に色分けされ、構造が一目でわかるように表示されます。

文法は「ルール」として暗記するより、**パターン**として視覚的に認識できるほうが使いやすくなります。構文解析の色分けを繰り返し目にすることで、英文の構造を読みながら感じ取れるようになっていきます。

フレーズ単位でのかたまり（チャンク）の表示も重要です。英語を単語ひとつひとつではなく、意味のかたまりとして処理できるようになることが、読解速度と理解度の向上につながります。

## 4. 絵本モードで場面と英語を結びつける

入門英語（Funnics Island）には「絵本」表示モードがあります。主人公トムが島を冒険しながら英語表現を使う、物語形式の教材です。

言語習得において、**場面・文脈・感情との結びつき**は記憶の定着を助けます。絵本形式は、英文を抽象的な文字列としてではなく、登場人物の行動・感情・物語の流れとともに記憶させます。

## 5. シャドウイングで英語を体に入れる

シャドウイング練習モードでは、音声に少し遅れてついて声に出す練習ができます。マイクで発音を認識し、どの単語が正しく言えたかをリアルタイムでフィードバックします。

シャドウイングが有効なのは、英語の習得が**音と意味の自動的なマッピング**を必要とするからです。読んで理解できる英語と、聞いてすぐわかる英語は別物です。音のイントネーション・リズム・連結を体に馴染ませるには、実際に声に出す練習が必要です。

歌でリズムを体に入れ、日本語混じり文で単語の意味を固め、構文解析で文構造を把握した後に行うシャドウイングは、これらの知識を**瞬間的に使える形**に変換する仕上げの工程です。

## 6. 単語テストで定着を確認する

各レッスンには単語テスト（クイズ）機能があります。学習した単語が出題され、その単語を音声で確認することもできます。

テスト（検索練習）は、単に覚えているかを確認するためだけでなく、記憶そのものを強化します。これは**想起練習効果（テスト効果）**として認知心理学でよく知られた現象です。一度頭から引き出そうとする行為が、次回の想起をより確実にします。

## 7. 学習の流れ——「聴く」から「使う」へ

このサイトでの理想的な学習の流れは次のようなものです。

1. **動画（歌）** でメロディーとともに英文を耳に入れる
2. **日本語混じり文** で個々の単語を意味ネットワークに統合する
3. **英語のみ** 表示や **IPA（発音記号）** 表示で英文そのものと向き合う
4. **構文解析** で文の骨格（文型・構造）を視覚的に把握する
5. **日本語訳** で意味の確認をする
6. **単語テスト** で語彙の定着を確認する
7. **シャドウイング** で英語を音として身体化する
8. **長文読解**（高校編）で総合的な読解力を養う

各ステップは独立して使えますが、この順序で使うことで**音・語彙・文法・表現の理解が重なり合い**、英語が複数の経路から定着していきます。

## おわりに

英語学習に「これさえやれば」という万能の方法はありません。しかし、**様々な認知経路から同じ素材に繰り返しアクセスする**ことは、記憶の定着と運用力の両面で効果的であることが知られています。

Funnics Islandは、ひとつのレッスンテキストを歌・絵本・語彙・文法・発音・シャドウイングという異なる角度から学べるよう設計されています。自分のレベルや目的、その日の気分に合わせて使い方を選べるのが、このサイトの特徴です。

https://english-lesson.gasflare.workers.dev"""


def wait_for_login(page):
    """ログインが完了するまで待機"""
    print("\n" + "="*50)
    print("ブラウザが開きました。")
    print("note.com にログインしてください。")
    print("ログイン済みの場合はそのまま待っていてください。")
    print("="*50)

    # ログイン完了を検出（URLが /login でなくなるまで待つ）
    try:
        page.wait_for_function(
            "() => !window.location.pathname.startsWith('/login')",
            timeout=120_000
        )
        print("ログイン確認済み")
    except Exception:
        print("ログインタイムアウト — そのまま続行します")


def post_article(page):
    """記事作成ページへ移動して内容を入力"""
    print("\n記事作成ページへ移動中...")
    page.goto("https://note.com/notes/new", wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(2000)

    # ログインを要求された場合
    if "/login" in page.url:
        print("再ログインが必要です。ブラウザでログインしてください。")
        page.wait_for_function(
            "() => !window.location.pathname.startsWith('/login')",
            timeout=120_000
        )
        page.goto("https://note.com/notes/new", wait_until="networkidle")
        page.wait_for_timeout(2000)

    print(f"現在のURL: {page.url}")

    # タイトル入力
    print("タイトルを入力中...")
    title_sel = 'textarea[placeholder*="タイトル"], input[placeholder*="タイトル"], [data-placeholder*="タイトル"]'
    try:
        page.wait_for_selector(title_sel, timeout=15000)
        page.click(title_sel)
        page.type(title_sel, TITLE, delay=20)
        print("  タイトル入力完了")
    except Exception as e:
        print(f"  タイトル欄が見つかりません: {e}")
        # スクリーンショットで確認
        page.screenshot(path="/tmp/note_debug.png")
        print("  /tmp/note_debug.png にスクリーンショットを保存しました")

    page.wait_for_timeout(500)

    # 本文入力（Tabキーで本文エリアへ移動してから入力）
    print("本文を入力中（しばらくかかります）...")
    try:
        # 本文エリアをクリック
        body_sel = '[contenteditable="true"], .ProseMirror, [data-placeholder*="本文"]'
        page.wait_for_selector(body_sel, timeout=15000)

        # Tabキーで本文エリアへ
        page.keyboard.press("Tab")
        page.wait_for_timeout(300)

        # JavaScriptでクリップボードに入れて貼り付け（高速）
        page.evaluate(f"""
            () => {{
                const el = document.querySelector('[contenteditable="true"]');
                if (el) el.focus();
            }}
        """)
        page.wait_for_timeout(300)

        # クリップボード経由で一括貼り付け
        import subprocess as sp
        proc = sp.run(['pbcopy'], input=BODY.encode('utf-8'), check=True)
        page.keyboard.press("Meta+v")
        page.wait_for_timeout(2000)
        print("  本文入力完了")

    except Exception as e:
        print(f"  本文入力エラー: {e}")

    # 下書き保存
    print("\n下書き保存中...")
    try:
        save_btn = page.query_selector('button:has-text("下書き保存"), button:has-text("保存")')
        if save_btn:
            save_btn.click()
            page.wait_for_timeout(2000)
            print("  下書き保存完了")
        else:
            # Cmd+S を試す
            page.keyboard.press("Meta+s")
            page.wait_for_timeout(1500)
            print("  Cmd+S で保存を試みました")
    except Exception as e:
        print(f"  保存エラー: {e}")

    print("\n" + "="*50)
    print("完了！ブラウザで内容を確認してください。")
    print("問題なければ「公開する」ボタンを押してください。")
    print("="*50)
    print("\nこのウィンドウを閉じるには Ctrl+C を押してください。")

    # ブラウザを開いたまま待機
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        pass


def main():
    with sync_playwright() as p:
        # ヘッドフルで起動（ユーザーが操作できるように）
        browser = p.chromium.launch(
            headless=False,
            args=["--start-maximized"]
        )
        ctx = browser.new_context(
            viewport={"width": 1280, "height": 900},
            # Chromeプロファイルは使えないため、普通に起動
        )
        page = ctx.new_page()

        # note.com を開く
        page.goto("https://note.com/login", wait_until="domcontentloaded")
        page.wait_for_timeout(1500)

        # ログイン待機
        wait_for_login(page)

        # 記事入力
        post_article(page)

        browser.close()


if __name__ == "__main__":
    main()
