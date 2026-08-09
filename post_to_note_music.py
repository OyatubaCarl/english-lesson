"""
note.com に「英語は歌で覚えるとなぜ脳に残るのか」記事を下書き投稿するスクリプト。
- 可視ブラウザを開き、ユーザーが手動で note.com にログイン
- タイトル＋本文をクリップボード経由で入力し、サイトスクリーンショットを挿入
- 「下書き保存」して終了（公開はユーザーが内容確認後に手動で行う）

実行: python3 post_to_note_music.py
"""

import subprocess
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

PROJ = Path(__file__).resolve().parent
SS = PROJ / "tmp_site_screenshots"

TITLE = "英語は「歌で覚える」となぜ脳に残るのか——音楽と第二言語習得の神経科学"

# (テキスト, 直後に挿入するスクリーンショット名 or None)
ARTICLE = [
    (
        "英語を歌で覚える学習法には、いつも小さな疑いがつきまといます。楽しいのはわかる。でも、本当に「勉強」になっているのだろうか。メロディーに気を取られて、英文そのものの理解がかえって弱くなるのではないか。音楽は右脳、言語は左脳というイメージがあるから、両者は脳の中で邪魔し合うのではないか——。\n\n"
        "先に結論を言います。覚えたい英文そのものを歌として聴き、声に出して歌うかぎり、音楽は英語学習を邪魔するものではなく、むしろ強力な「足場」になります。これは精神論ではなく、第二言語習得・認知心理学・神経科学の知見が一貫して支持する話です。\n\n"
        "ただし一つだけ例外があります。それは「別の英文を勉強している横で、関係のない歌詞入り音楽をBGMとして流す」場合。このときは言語情報どうしがぶつかって集中を奪います。逆に言えば、覚えたい英文と歌詞が一致してさえいれば、音楽はノイズにならず、リズム・音韻・意味・感情・記憶をひとつに束ねる「第二の通路」として働きます。\n\n"
        "この記事では、なぜ歌での英語学習が脳に残りやすいのかを順番に解きほぐし、最後に、この考え方を教材として形にした英語学習サイト「Teacher Tacos English / Funnics Island」の「歌で覚える」入り口を紹介します。",
        "01_top",
    ),
    (
        "## 1.「音韻は右脳」は、半分だけ正しい\n\n"
        "「音は右脳で処理する」というイメージは、半分正しく、半分足りません。\n\n"
        "個々の音素――たとえば /r/ と /l/、cat のアと cut のアのような細かな音の区別や、単語の音韻判断、文法構造の解析には、左半球の言語ネットワーク（とりわけ左下前頭回後部）が優位に関わります。ただし「音韻＝左脳だけ」は単純化しすぎです。Hartwigsenら（2010）の二重部位TMS実験（健常右利き、各群14名）では、左でも右でも後部下前頭回を止めると、意味判断ではなく音韻判断が同程度に乱れました。つまり音韻処理は左が優位でありつつ右の後部下前頭回も必要なのです。英語の音を「言語として」聞き分けるには、左脳を中心としつつ両半球が関わります。\n\n"
        "一方で、イントネーション、リズム、ピッチの上下、声の表情といった超分節的（プロソディ）な特徴は、右半球が主役です。\n\n"
        "ここに歌の強みがあります。英語を歌で学ぶと、左半球が扱う「音素・単語・文法」と、右半球が扱う「メロディー・リズム・抑揚」が同時に動きます。文字でただ読むのと違い、耳・声・体のリズムを巻き込みながら、英語の音の流れをひとつのまとまりとして受け取れるのです。",
        None,
    ),
    (
        "## 2. 言語と音楽は、脳の「組み立て資源」を共有している\n\n"
        "では、左脳の言語処理と音楽処理は、ぶつかってしまわないのでしょうか。ここが核心です。\n\n"
        "音楽心理学者パテルの共有統語統合資源仮説（SSIRH）によれば、言語の文法知識と音楽の和声知識は脳の別々の場所に保管されている一方で、それらをその場で組み立てていく作業システムは、言語と音楽で同じ神経資源を共有しています。\n\n"
        "わかりやすい証拠があります。文章中で文法ミスや予想外の単語に出会ったときと、音楽で予想を裏切る不協和音に出会ったときに、まったく同じ脳波成分（P600）が現れるのです。意味のつながりに関わるN400という成分でも、音楽と言語は処理を共有しています。\n\n"
        "つまり、英文を歌として聴くとき、脳の中では「音楽を組み立てる作業」と「英文法を組み立てる作業」が同じネットワークの上で同時に走ります。これは資源の奪い合い（干渉）ではなく、予測と統合のしくみを二重に鍛えるシナジーを生みます。音楽は、構造を組み立てる回路を力強く駆動させる「促進剤」なのです。",
        None,
    ),
    (
        "## 3. 歌は、英文を「二重に」記憶させる\n\n"
        "記憶の面でも、歌には明確な利点があります。鍵になるのは、心理学者パイヴィオの二重符号化理論です。\n\n"
        "人の脳は情報を、「言語のチャンネル（言葉・意味）」と「非言語のチャンネル（イメージ・音・感覚）」という、独立しつつも結びついた二つの経路で覚えています。教科書を黙読すると主に言語チャンネルだけが働きますが、英文を歌として聴くと、歌詞の意味と音韻に加えて、メロディー・リズム・強弱・感情までが同時に結びつく。同じ英文が脳内で「二重に」符号化されるわけです。\n\n"
        "ルートケら（2014、査読誌 Memory & Cognition）は、英語母語話者の成人60名を「話す」「リズム」「歌う」の3条件に無作為割当（各20名）し、15分学習させました。3条件で音声の長さと提示速度をそろえ、「歌はゆっくりだから有利」という可能性を排除しています。結果、歌唱群は5テスト中、ハンガリー語を思い出して声に出す2つ（産出・遅延会話）で有意に高成績でした（p<.05）。差は年齢・性別・気分・記憶力・音楽経験では説明されません。ただし単一研究・短期の効果で、有意差は逐語的な産出課題に出ています。\n\n"
        "後で英文を思い出すとき、意味の糸が切れていても、出だしのメロディーやリズムという別の検索ルートをたどれば引き出せる。歌は「楽しいから続く」だけでなく、記憶の構造そのものを助けているのです。",
        "05_mode_en_ja_mix",
    ),
    (
        "## 4. 英語のリズムは、そもそも歌と相性がいい\n\n"
        "日本語は、モーラ（拍）がほぼ一定の長さで進む「音節拍リズム」の言語です。これに対し英語は、典型的な「強勢拍リズム」の言語。意味の中心になる強い音節がほぼ等間隔で現れ、その間の弱い音節（冠詞・前置詞・代名詞・助動詞など）は、数に関係なく時間が圧縮されて、速く・弱く・つながって発音されます。\n\n"
        "教科書で単語ごとの発音だけを覚えた人が、ネイティブの自然な会話を「まったく別物」のように感じてしまうのは、このリンキング（音の連結）とリダクション（弱化・脱落）のためです。\n\n"
        "歌では、強い拍に大事な語が乗り、弱い語は短い音符やつながったメロディーの中に自然に収まります。すると、英語のストレス・リンキング・リダクションを、理屈の説明としてではなく、体のタイミングとして覚えられる。これは発音とリスニングの両方に効きます。",
        None,
    ),
    (
        "## 5. 頭の中で勝手に流れることも、立派な学習になる\n\n"
        "歌のもう一つの大きな特徴は、「頭に残る」こと。一度聴いたメロディーが、歩いているとき、お風呂で、寝る前にふと再生される――これは語学にとって、かなり強い味方です。\n\n"
        "第二言語習得の研究では、学んだ外国語のフレーズが頭の中で勝手に繰り返される現象を「din in the head（頭の中の響き）」や「不随意の心的リハーサル」と呼んできました。サルセド（2010）は大学のスペイン語クラス94名で、dinを報告した学生が歌群66.7%対テキスト群33.3%と有意に多いと報告しました（カイ二乗、p<.05）。ただし無作為割当でない準実験で、dinは自己申告、遅延再生は非有意、調査期間に大型ハリケーンが重なるなど限界も大きく、Ludkeほど強い証拠ではありません。\n\n"
        "机に向かっていない時間にも英文がメロディーと一緒に再生される――これは意識的な努力に頼らない反復であり、語学で一番むずかしい「何度も触れる」を、歌はごく自然に助けてくれます。",
        None,
    ),
    (
        "## 6. ただし――「BGMとしての歌詞入り音楽」は別問題\n\n"
        "誤解を防ぐために、大事な線引きをしておきます。「英語を歌で覚える」ことと、「英語を勉強しながら別の歌を流す」ことは、まったく別物です。\n\n"
        "覚えたい英文そのものが歌になっているなら、言語情報と音楽情報は同じ対象を支え合います。ところが、読解や単語暗記をしている横で、別の歌詞入り音楽を流すと、耳から入る歌詞がワーキングメモリに割り込み、読んでいる英文と競合します。とくに英語学習中に英語の歌詞入りBGMを流すと、読む言葉と聴こえる言葉がぶつかり、読解の精度も語彙の定着も落ちます。\n\n"
        "整理すると、(1)覚えたい英文そのものを歌として聴く・歌うのは「強い促進」、(2)歌詞のないインスト曲を小さく流すのは「中立〜軽い促進」、(3)別の英文を学習中に歌詞入り音楽を流すのは「干渉」。\n\n"
        "この記事が勧めているのは、もちろん(1)です。関係ない曲を流すことではなく、覚えたい英文を、その英文の歌として聴くこと。ここが核心です。",
        None,
    ),
    (
        "## 7. 音楽は、新しい言語回路の「足場」にもなる\n\n"
        "音楽は、聴覚・運動・感情・予測・注意を同時に動かすマルチモーダルな活動であり、脳そのものを作り替える力を持ちます。\n\n"
        "その象徴が、失語症リハビリで使われるメロディック・イントネーション・セラピー（MIT）です。左脳の言語野を損傷して話せなくなった人でも、耳慣れた歌なら驚くほど流暢に歌えることがある。MITはこれを利用し、日常のフレーズをメロディーとリズムに乗せて歌わせることで発話を取り戻していきます。その背景には、メロディーとリズムが損傷を免れた右半球を活性化させ、左脳の言語機能を肩代わりさせるという神経の作り替え（可塑性）があります。\n\n"
        "構造のレベルでも変化が起きます。長期的な音楽トレーニングは、左右の脳をつなぐ脳梁の白質を強化し、聴いた音を声に変える経路である弓状束も鍛えます。英語の歌を聴いて一緒に歌う行為は、まさに「聴く→正確に発音する」ループを回す練習です。\n\n"
        "さらに報酬系も働きます。心地よい音楽は脳の報酬中枢（腹側被蓋野・VTA）を刺激してドーパミンを放出させ、その瞬間に届いた音（＝覚えたい英語）は記憶に定着しやすくなります。音楽の「気持ちよさ」そのものが、記憶を定着させる引き金になっているのです。",
        None,
    ),
    (
        "## 8.「楽しい」は、最強の学習条件でもある\n\n"
        "クラッシェンの情意フィルター仮説によれば、学習者が不安・緊張・退屈を感じていると、見えない「フィルター」が上がり、せっかくの良質なインプットも脳の習得プロセスに届きません。\n\n"
        "音楽は、このフィルターを下げる最も効果的な道具のひとつです。親しみやすい歌は心理的なハードルを下げ、リラックスした学習空間を作ります。さらに歌は、言語的・論理的な知能だけでなく、音楽的知能やリズムに乗る身体運動的知能など、複数の学び方の入り口を同時に開きます。論理的な暗記が苦手な人でも、得意なチャンネルから英語に入れるのです。",
        None,
    ),
    (
        "## Teacher Tacos English / Funnics Island ――「歌で覚える」入り口がある教材\n\n"
        "ここまでの考え方を、実際の教材として形にしたのが、英語学習サイト「Teacher Tacos English / Funnics Island」です。\n\n"
        "サイトURL：https://english-lesson.gasflare.workers.dev/\n\n"
        "ティーチャー・タコスと島の仲間たちが登場する英語学習サイトで、フォニックス → 入門英語 → 中学英語 → 高校文法 → 高校読解までを、同じサイトの中で段階的に学べます。最大の特徴は、どのレッスンにも「歌で英語を覚える」入り口が用意されていることです。",
        "03_lesson_b1_default",
    ),
    (
        "フォニックスでは、AからZまで、26人のキャラクターと歌で音を学びます。Aunt Ant、Baker Bear、Singer Snake、Teacher Tacos……。音・キャラクター・単語・動作がひとつに結びつき、ただのアルファベット暗記ではなく、音・意味・イメージ・リズムをまとめて入れる設計です。各レッスンには本文をそのまま歌にしたYouTube動画が紐づいています。\n\n"
        "入門英語Funnics Islandでは、主人公トムが島を冒険しながら、Teacher Tacosや仲間たちと会話し、中学1年レベルの基本表現を歌と物語で学びます。各レッスンには、英語音声・日本語混じり文・英語のみ・日本語訳・絵本表示・単語チェック・シャドウイングが揃っています。\n\n"
        "この構成は、本記事の理屈どおりです。まず歌で英文の音の輪郭をつかみ、そのあとで意味・語彙・文法・発音へ進む。最初から文法で固めるのではなく、まず歌で英文を耳と体に入れ、それから理解を重ねていく流れになっています。",
        "07_mode_picturebook",
    ),
    (
        "## おすすめの使い方――「聴く」から「声に出す」へ\n\n"
        "脳に沿った自然な順番は、次のとおりです。\n\n"
        "1. まず歌・動画を、理解しようとせず聴く。メロディーと英語のリズムを耳に残すのが目的です。\n"
        "2. 歌詞・本文を見ながらもう一度聴く。知らない単語があっても文全体の流れを優先し、音と文字を対応させます。\n"
        "3. 日本語混じり文・日本語訳で意味を確認する。ここで初めて「何を言っていたか」がはっきりします。\n"
        "4. 英語のみ表示やIPA（発音記号）に切り替え、音の細部を見る。\n"
        "5. 声に出して歌う・シャドウイングする。声を出すことで、聴くだけだった英語が口の動きと結びつきます。\n\n"
        "「音として入る → 意味がつながる → 構造が見える → 声として出る」。この往復を何度も回すうちに、英語は“覚えた知識”から“口に出せる音の流れ”へと近づいていきます。",
        "08_shadowing_start",
    ),
    (
        "## まとめ\n\n"
        "歌で英語を覚えることは、単なる気分転換ではありません。\n\n"
        "音素や文法を扱う左半球、リズムやプロソディを扱う右半球、記憶を支えるメロディー、声に出す運動回路、報酬系のドーパミン、そして「頭に残る」不随意の反復――これらが同じ英文に向かって働くとき、音楽は英語学習の邪魔ではなく、強力な足場になります。\n\n"
        "もちろん、歌だけで文法も読解もすべて身につくわけではありません。けれど、英語を最初に「音のまとまり」として受け取る入口として、歌はとても理にかなっています。英語を覚える第一歩は、いつも机の上の暗記から始めなくてもいい。まずは一曲、耳に残る英文から。それだけで、脳はもう学習を始めています。\n\n"
        "Teacher Tacos English / Funnics Island：https://english-lesson.gasflare.workers.dev/\n\n"
        "（参考：Patel 2003／Ludke, Ferreira & Overy 2014／Salcedo 2010／Merrett, Peretz & Wilson 2014／Herholz & Zatorre 2012／Lehmann & Seufert 2017。本記事は教育目的の一般的な解説です。）",
        None,
    ),
]


def ensure_logged_in(page, max_wait=600):
    """note.com のログインを辛抱強く待つ（最大 max_wait 秒）。クラッシュしない。
    永続プロファイルで既にログイン済みなら即 True を返す。"""
    try:
        page.goto("https://note.com/login", wait_until="domcontentloaded", timeout=30000)
    except Exception:
        pass
    print("\n" + "=" * 50)
    print("ブラウザで note.com にログインしてください。")
    print("（Googleログインは自動ブラウザで弾かれることがあります。"
          "うまくいかない場合はメールアドレス＋パスワードでログインしてください）")
    print("ログインを検知すると自動で続行します。最大10分待ちます。")
    print("=" * 50, flush=True)
    deadline = time.time() + max_wait
    while time.time() < deadline:
        page.wait_for_timeout(2000)
        try:
            url = page.url
            # note.com 上にいて、かつ /login でない＝ログイン成功とみなす。
            # Googleログイン中の accounts.google.com 等では待機を継続（誤検知防止）。
            if "note.com" in url and "/login" not in url:
                print("ログイン確認済み", flush=True)
                return True
        except Exception:
            pass
    print("ログイン待ちがタイムアウトしました。", flush=True)
    return False


def copy_image_to_clipboard(image_path: str):
    script = f'set the clipboard to (read (POSIX file "{image_path}") as «class PNGf»)'
    subprocess.run(["osascript", "-e", script], check=True)


def insert_image(page, ss_name: str):
    img_path = str(SS / f"{ss_name}.png")
    if not Path(img_path).exists():
        print(f"  スクリーンショットが見つかりません: {img_path}", flush=True)
        return
    print(f"  画像挿入中: {ss_name}.png", flush=True)
    copy_image_to_clipboard(img_path)
    page.wait_for_timeout(400)
    page.keyboard.press("Meta+v")
    page.wait_for_timeout(3000)
    print(f"  画像貼り付け完了: {ss_name}", flush=True)


def type_text(page, text: str):
    subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=True)
    page.wait_for_timeout(200)
    page.keyboard.press("Meta+v")
    page.wait_for_timeout(500)


def post_article(page):
    print("\n記事作成ページへ移動中...", flush=True)
    page.goto("https://note.com/notes/new", wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(2000)

    if "/login" in page.url:
        print("セッション未確立。もう一度ログインを待ちます。", flush=True)
        if not ensure_logged_in(page):
            print("ログインされなかったため中止します。", flush=True)
            return
        page.goto("https://note.com/notes/new", wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)
        if "/login" in page.url:
            print("まだログインできていません。中止します。", flush=True)
            return

    print(f"URL: {page.url}", flush=True)

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
    page.keyboard.press("Tab")
    page.wait_for_timeout(400)
    page.evaluate("() => { const el = document.querySelector('[contenteditable=\"true\"]'); if (el) el.focus(); }")
    page.wait_for_timeout(300)

    for i, (text, ss_name) in enumerate(ARTICLE):
        print(f"\nセクション {i+1}/{len(ARTICLE)} を入力中...", flush=True)
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
    # 永続プロファイル（Drive 同期外）。一度ログインすれば次回以降はログイン不要。
    user_data = str(Path.home() / ".note_profile_funnics")
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data,
            headless=False,
            args=["--start-maximized"],
            viewport={"width": 1280, "height": 900},
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        if ensure_logged_in(page):
            post_article(page)
        else:
            print("ログインされなかったため終了します。", flush=True)
        ctx.close()


if __name__ == "__main__":
    main()
