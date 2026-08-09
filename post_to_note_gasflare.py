"""GASflare の note 記事を、ログイン済みの普段のChromeへCDP接続して下書き投稿する。

前提: Chrome を一度終了し、デバッグモードで起動しておく:
    open -a "Google Chrome" --args --remote-debugging-port=9222

実行: python3 post_to_note_gasflare.py
できるのは**下書きまで**。見出し画像（ロゴ）の設定と公開ボタンは自分で押す。
"""
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

CDP_URL = "http://localhost:9222"
PROJ = Path(__file__).resolve().parent
SS = PROJ / "広報" / "note_gasflare_images"

TITLE = "先生ひとりに、データベースひとつ。——シートをコピーするだけの学習記録システム「GASflare」"

# (本文テキスト, 直後に挿入する画像名 or None)
ARTICLE = [
    (
        "英単語アプリを作りました。使ってください。——そう言って配って、それで終われるなら苦労はありません。\n\n"
        "授業で使うとなると、必ずこう聞かれます。**「で、誰がどこまでやったんですか」**\n\n"
        "やった人とやっていない人が同じ扱いになるなら、生徒は次からやりません。宿題にも、評価にも、声かけにも使えない。"
        "学習アプリが「配って終わり」になってしまう一番の理由が、ここだと思っています。\n\n"
        "だから、学習記録が要ります。問題は、**それをどこに置くか**です。",
        None,
    ),
    (
        "## GAS（Google Apps Script）は、学校にとって奇跡的に都合がいい\n\n"
        "先に言うと、私は Google Apps Script が好きです。学校で使う道具として、他に代えがたい強みが3つあります。\n\n"
        "**ひとつ、教員個人の権限のまま、生徒の情報を集められる。**\n\n"
        "情報システム部門に申請して、サーバを借りて、承認を待つ——そういう手続きが一切いりません。"
        "先生が自分のドライブでボタンを押すだけで成立します。「やりたい」と思ってから「動いている」までの距離が、圧倒的に短い。\n\n"
        "**ふたつ、データが完全にその先生のものになる。**\n\n"
        "スプレッドシートは先生のドライブの中にあります。誰かのサーバに預けるのではありません。消すのも、渡すのも、持ち出すのも自由です。\n\n"
        "**みっつ、Googleアカウントと成績が紐づくが、それは学校が発行したアカウントである。**\n\n"
        "厳密に個人を特定しにいく仕組みではありませんし、私的な情報が混ざり込むわけでもありません。"
        "学校という文脈のなかで、ちょうど必要なぶんだけ本人が分かる。この距離感がちょうどいい。",
        None,
    ),
    (
        "## それでも、GASだけで全部を作ると壁に当たる\n\n"
        "**壁1：配ったコードは、もう直せない。**\n\n"
        "GASでアプリを作って配るということは、先生ごとにコードのコピーを配るということです。"
        "バグが見つかっても、こちらから直す手立てがない。新しいものをまた公開して、コピーし直してもらうのを待つしかない。\n\n"
        "学習アプリは、使われはじめてからが本番です。直したい場所は毎週出てきます。"
        "「直せない」を前提にすると、作れるのは、ほぼ完成していて、もう変わらない、単純なものだけになります。\n\n"
        "**壁2：リッチにすると、重くなる。**\n\n"
        "GASでも画像は扱えます。セルに Base64 で埋め込んでしまえばいい。実際にやってみました。"
        "でも数が増えると途端に苦しくなりますし、動作も鈍ります。音声となればなおさらです。\n\n"
        "私が作りたかったのは、イラストが出て、音声が鳴って、リズムに合わせて英単語が飛んでくるアプリでした。"
        "画像と音声の置き場所として、スプレッドシートは向いていません。",
        None,
    ),
    (
        "## 気づいたこと：強みと弱みが、きれいに分かれている\n\n"
        "並べてみて、はっとしました。\n\n"
        "GASの**強み**は、「先生の権限で、先生のものとして、記録が集まる」という一点にある。\n"
        "GASの**弱み**は、「更新できない」「重い」という二点にある。\n\n"
        "そして、この二つは混ざっていない。強みは記録の話で、弱みはアプリの話です。\n\n"
        "**ならば、強みの部分だけをGASに残して、残りを全部そこから追い出せばいい。**",
        "fig_kirikae",
    ),
    (
        "## 答え：アプリはCloudflare、データベースはスプレッドシート\n\n"
        "・**アプリ本体**（UI・出題・画像・音声）→ Cloudflare Pages に置く。よく変わるもの\n"
        "・**本人確認と記録** → 先生のGAS＋スプレッドシート。ほとんど変わらないもの\n\n"
        "すると、こうなります。\n\n"
        "・直したいときは、Cloudflare側を1回直すだけ。全員に届く。先生は何もしなくていい\n"
        "・画像も音声も好きなだけ載せられる\n"
        "・データは今までどおり、先生のスプレッドシートのもの\n\n"
        "生徒の側から見ると、話はもっと単純になります。**学校のアカウントさえあれば、どの端末からでも、続きから学習できる。**"
        "教室のChromebookでも、家のタブレットでも、同じ場所から再開する。アカウントが本人を指し、URLが先生を指している。それだけでいい。\n\n"
        "この組み合わせを、私は **GASflare** と呼んでいます。**GAS ＋ Cloudflare** です。"
        "どちらか一方の話ではなく、組み合わせること自体に名前を付けました。片方だけでは、どうしても足りないからです。",
        None,
    ),
    (
        "## 先生の手順は3ステップ\n\n"
        "1. **スプレッドシートをコピーする** — ファイル → コピーを作成\n"
        "2. **デプロイする** — 拡張機能 → Apps Script → デプロイ\n"
        "3. **URLを配る** — Classroom でも、QRコードでも、黒板に書いてもいい\n\n"
        "生徒がそのURLを学校のGoogleアカウントで開くと、そのままアプリが始まります。"
        "**そのURLを踏んだ生徒の記録だけが、その先生のシートに溜まっていきます。**\n\n"
        "サーバは要りません。データベースも要りません（スプレッドシートがデータベースです）。"
        "Google Cloud Console も出てきません。費用はゼロです。\n\n"
        "シートを開くと「進捗」ができていて、メニューから「クラスの進捗を見る」を選ぶとダッシュボードが開きます。"
        "生徒ごとの到達率、達成した人が少ない順に並ぶ「クラスのつまずき」、生徒×項目の一覧表。",
        "fig_zentai",
    ),
    (
        "## 「学校のアカウントだけ」は、どこにも書いていない\n\n"
        "技術的にいちばん面白かったところです。\n\n"
        "生徒が先生のURLを開くと、Apps Script は Session.getActiveUser().getEmail() で本人を確認します。"
        "この API には、こういう性質があります。\n\n"
        "**スクリプトの所有者と同じドメインの利用者にしか、メールを返さない。**\n\n"
        "他ドメインの人が開けば、空文字が返るだけ。つまり「学校のアカウントのみ」という制限は、"
        "設定ではなく Google の仕様そのもので成立しているわけです。\n\n"
        "許可ドメインを書く設定ファイルは、どこにもありません。他校の先生がこのシートをコピーすれば、"
        "その瞬間から許可ドメインはその学校に切り替わります。誰も何も設定しない。",
        None,
    ),
    (
        "## なりすましは、署名で止める\n\n"
        "生徒がURLを踏むと、Apps Script は署名付きのトークンを発行してアプリへ渡します。中身は3つだけです。\n\n"
        "・**誰か** — メールではなく、stu_9f2c1ab77e40 のような不透明なID\n"
        "・**どこへ送り返すか** — その先生の Apps Script のURL\n"
        "・**期限**\n\n"
        "これを HMAC-SHA256 で署名します。鍵は、その Apps Script が初回に自分で作った乱数で、"
        "アプリにも通信路にも一切出てきません。\n\n"
        "だから、IDを書き換えて他人になりすまそうとしても署名が合わずに捨てられますし、"
        "「送り先だけ別の先生のGASに差し替える」こともできません（送り先も署名の中にあるので）。",
        "fig_token",
    ),
    (
        "## メールは、シートの外へ出ない\n\n"
        "生徒のメールアドレスは、先生のスプレッドシートから一歩も出ません。\n\n"
        "アプリ側（Cloudflareで配信している静的ファイル）が持っているのは不透明IDだけで、"
        "それが誰なのかを知る手立てはアプリ側に存在しません。メールとIDの対応表は、先生のシートの中にしかない。\n\n"
        "先生が見る「進捗」シートには、照合済みのメールが並びます。**先生には見える。アプリには見えない。**"
        "これが正しい形だと思っています。",
        None,
    ),
    (
        "## 記録に残るのは、先生のURLから入った分だけ\n\n"
        "もうひとつ、大事な原則があります。**端末に元からあった進捗が、あとからアカウントへ合流することはありません。**\n\n"
        "localStorage は Googleアカウントに紐づかないので、「端末に記録がある」ことは「その人がやった」ことを意味しません。"
        "友人の端末かもしれない。だから進捗には持ち主を刻んでおき、違う人がログインしたらアカウント側の記録を正とします。"
        "**友人の端末を借りてログインしても、友人の成果が自分のものになることはない。**",
        None,
    ),
    (
        "## 「絶対に安全」ではない、とは書いておきます\n\n"
        "URLは生徒全員に配ります。だから正直に書いておきます。\n\n"
        "**トークンそのものを盗まれれば、なりすませます。** セッションクッキーを盗まれるのと同じ性質の話で、"
        "署名で防げる種類のものではありません。だからURLバーからは即座に消し、有効期限を切っています。\n\n"
        "そして、**本人が開発者ツールで端末の記録を書き換えることは、構造的に防げません。**"
        "進捗の正本が端末にある以上、どんなクライアント主導の設計でも同じです。\n\n"
        "守れるのは「他人になりすませないこと」と「他人の記録が勝手に混ざらないこと」まで。"
        "だから私は、この記録をそのまま成績にはしません。誰が取り組んでいて、クラスのどこがつまずいているかを見るための道具として使う。"
        "そこを偽装する動機は薄いし、声かけの精度はそれだけで十分に変わります。",
        None,
    ),
    (
        "## 引き継ぎも、卒業も、シート1枚\n\n"
        "この形にして良かったと思うのは、運用が全部スプレッドシートの操作に落ちることです。\n\n"
        "・学年が変わる → 新しくコピーして、新しいURLを配る\n"
        "・引き継ぐ → シートを共有する\n"
        "・捨てる → シートを削除する\n"
        "・他の先生に配る → シートを配る（コピーされた瞬間、前のデータは自動で消えます）\n\n"
        "サーバの管理も、アカウントの発行も、データの移行も出てきません。"
        "**先生がすでに知っている道具の上で、全部が完結する。**",
        None,
    ),
    (
        "## 動いているもの\n\n"
        "いま、この仕組みで3つの学習アプリが動いています。GAS側のコードは3つとも完全に同一で、"
        "アプリが初回接続時に「自分が何者で、何を記録するか」を名乗る造りになっています。\n\n"
        "🌮 タコスパーティー（英語フルコース）\n"
        "https://taco-course.pages.dev/app.html\n\n"
        "📚 WordTacos（英単語クイズ）\n"
        "https://wordtacos.pages.dev/\n\n"
        "🔢 CalTacos（計算）\n"
        "https://tacomath.pages.dev/\n\n"
        "仕組みの骨格だけを取り出した最小デモ（ボタンを押した回数を記録するだけ）はこちら。\n"
        "https://gasflare-minimal.pages.dev/",
        None,
    ),
]


def copy_image_to_clipboard(image_path: str):
    script = f'set the clipboard to (read (POSIX file "{image_path}") as «class PNGf»)'
    subprocess.run(["osascript", "-e", script], check=True)


def insert_image(page, ss_name: str):
    img_path = str(SS / f"{ss_name}.png")
    if not Path(img_path).exists():
        print(f"  画像が見つかりません: {img_path}", flush=True)
        return
    print(f"  画像挿入中: {ss_name}.png", flush=True)
    copy_image_to_clipboard(img_path)
    page.wait_for_timeout(400)
    page.keyboard.press("Meta+v")
    page.wait_for_timeout(3000)


def type_text(page, text: str):
    subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=True)
    page.wait_for_timeout(200)
    page.keyboard.press("Meta+v")
    page.wait_for_timeout(500)


def wait_until_logged_in(page, max_wait=600) -> bool:
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
        print("このChromeは note.com にログインしていません。", flush=True)
        return False

    title_sel = 'textarea[placeholder*="タイトル"], input[placeholder*="タイトル"]'
    try:
        page.wait_for_selector(title_sel, timeout=15000)
        page.click(title_sel)
        page.type(title_sel, TITLE, delay=15)
        print("タイトル入力完了", flush=True)
    except Exception as e:
        print(f"タイトル欄エラー: {e}", flush=True)

    page.wait_for_timeout(500)
    page.keyboard.press("Tab")
    page.wait_for_timeout(400)
    page.evaluate("() => { const el = document.querySelector('[contenteditable=\"true\"]'); if (el) el.focus(); }")
    page.wait_for_timeout(300)

    for i, (text, ss_name) in enumerate(ARTICLE):
        print(f"セクション {i + 1}/{len(ARTICLE)}", flush=True)
        type_text(page, text)
        page.wait_for_timeout(300)
        if ss_name:
            page.keyboard.press("Enter")
            page.keyboard.press("Enter")
            page.wait_for_timeout(300)
            insert_image(page, ss_name)
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
            print("Chromeに接続できません。デバッグモードで起動してください:\n"
                  '  open -a "Google Chrome" --args --remote-debugging-port=9222', flush=True)
            print(f"詳細: {e}", flush=True)
            sys.exit(1)

        ctx = browser.contexts[0] if browser.contexts else browser.new_context()
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

        print("note.com のログインを確認しています（未ログインならログインしてください。最大10分待ちます）", flush=True)
        if not wait_until_logged_in(page):
            print("ログインされなかったため終了します。", flush=True)
            return

        ok = fill_draft(page)
        print("=" * 50, flush=True)
        if ok:
            print("完了！下書きを確認して、見出し画像に 広報/note_gasflare_images/logo.png を設定し、", flush=True)
            print("「公開する」を押してください。", flush=True)
        else:
            print("未完了。ログイン状態を確認してください。", flush=True)


if __name__ == "__main__":
    main()
