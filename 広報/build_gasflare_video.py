#!/usr/bin/env python3
"""GASflare 解説動画（YouTube用）を作る。

  gasflare_slides.html（1920x1080 のスライド18枚）
     → Playwright で1枚ずつ撮る            → tmp_gasflare/slide_NN.png
     → Voicepeak でナレーションを合成       → tmp_gasflare/narr_NN.wav
     → ffmpeg で 画像 × 音声長 に伸ばして結合 → gasflare_explainer.mp4

スライドの見た目は HTML が正本。文言を直したいときは HTML を直して、これを再実行する。
既にあるものはスキップ（再実行安全）。--force で作り直す。

usage:
    python3 build_gasflare_video.py [--force]
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent          # 広報/
SLIDES_HTML = ROOT / "gasflare_slides.html"
WORK = ROOT / "tmp_gasflare"
OUT = ROOT / "gasflare_explainer.mp4"

VOICEPEAK = "/Applications/voicepeak.app/Contents/MacOS/voicepeak"
NARRATOR = "Japanese Female 1"

W, H, FPS = 1920, 1080, 30
PAD_HEAD = 0.45      # スライドが切り替わってから喋り出すまでの間
PAD_TAIL = 1.10      # 喋り終わってから次のスライドへ行くまでの間

FORCE = "--force" in sys.argv

# ナレーション（スライドの順番と1対1。HTML の <section class="slide"> の並びと合わせる）
NARRATION = [
    # 01 表紙
    "先生ひとりに、データベースひとつ。"
    "スプレッドシートをコピーして、デプロイして、URLを配る。"
    "それだけで、担任ごとの学習記録データベースが立ち上がる。"
    "ガスフレア、と呼んでいる仕組みの話です。",

    # 02 問題1
    "学習アプリを作りました、使ってください。そう言って配って、それで終われるなら苦労はありません。"
    "授業で使うとなると、必ずこう聞かれます。で、誰がどこまでやったんですか。"
    "やった人とやっていない人が同じ扱いになるなら、生徒は次からやりません。"
    "宿題にも、評価にも、声かけにも使えないんです。",

    # 03 問題2
    "かといって、記録を取ろうとすると話が急に重くなります。"
    "サーバを立てて、データベースを設計して、生徒のアカウントを発行して、卒業のたびに整理して、個人情報の管理責任を負う。"
    "これを一教員が背負えるでしょうか。私は無理です。"
    "そもそも先生が欲しいのは、自分の担当している生徒の記録だけなんです。",

    # 04 GASの強み
    "ここで、グーグル・アップス・スクリプト、GASの話をします。"
    "GASには、学校で使う道具として、他に代えがたい強みが三つあります。"
    "ひとつ、教員個人の権限のまま、生徒の情報を集められること。申請も、サーバの調達も、承認待ちもいりません。"
    "ふたつ、データが完全にその先生のものになること。誰かのサーバに預けるのではありません。"
    "みっつ、学校が発行したアカウントで、ちょうど必要なぶんだけ本人が分かること。"
    "厳密に個人を特定しにいく仕組みではないし、私的な情報が混ざり込むわけでもない。この距離感が、ちょうどいい。",

    # 05 GASの壁
    "それでも、GASだけで全部を作ろうとすると、二つの壁に当たります。"
    "壁のひとつめ。配ったコードは、もう直せない。"
    "GASで配るというのは、先生ごとにコードのコピーを配るということです。"
    "バグが出ても、こちらから直す手立てがない。新しいものをまた配って、コピーし直してもらうのを待つしかない。"
    "学習アプリは、使われはじめてからが本番です。直したい場所は毎週出てきます。"
    "壁のふたつめ。リッチにすると、重くなる。"
    "画像はセルにベース64で埋め込めば扱えますが、数が増えると苦しくなりますし、動作も鈍ります。音声となれば、なおさらです。",

    # 06 切り分け
    "並べてみて、はっとしました。"
    "GASの強みは、先生の権限で、先生のものとして、記録が集まる、という一点にある。"
    "GASの弱みは、更新できない、重い、という二点にある。"
    "そして、この二つは混ざっていない。強みは記録の話で、弱みはアプリの話なんです。"
    "ならば、強みの部分だけをGASに残して、残りを全部そこから追い出せばいい。"
    "追い出した先が、クラウドフレアです。"
    "アプリ本体はクラウドフレア。本人確認と記録は、先生のGASとスプレッドシート。"
    "この、GASとクラウドフレアの組み合わせそのものを、ガスフレアと呼んでいます。",

    # 07 生徒から見ると
    "生徒の側から見ると、話はもっと単純になります。"
    "学校のアカウントさえあれば、どの端末からでも、続きから学習できる。"
    "教室のクロームブックでも、家のタブレットでも、同じ場所から再開する。"
    "アカウントが本人を指し、URLが先生を指している。それだけでいいんです。",

    # 08 答え（3ステップ）
    "先生の手順は、三つだけです。"
    "ひとつ、スプレッドシートをコピーする。"
    "ふたつ、デプロイする。"
    "みっつ、デプロイで出てきたURLを、そのまま配る。"
    "サーバも、データベースも、グーグル・クラウド・コンソールも出てきません。費用はゼロです。",

    # 09 全体像
    "全体像です。アプリは一つ。データベースは、先生の数だけ。"
    "生徒が先生のURLを踏むと、その先生のGASが署名トークンを付けて、ゲーム本体へ転送します。"
    "ゲームは、そのトークンに書かれたGASへ記録を送り返す。"
    "だから記録は、必ず自分の先生のシートへ戻ります。"
    "ゲーム本体は全員で共有していますが、記録が混ざることはありません。",

    # 10 ドメイン
    "ここが、個人的にいちばん面白かったところです。"
    "学校のアカウントだけ、という制限は、どこにも書いていません。"
    "アップス・スクリプトのゲット・アクティブ・ユーザーという関数は、"
    "スクリプトの所有者と同じドメインの利用者にしか、メールアドレスを返さないんです。"
    "つまりドメイン制限は、設定ではなく、グーグルの仕様そのもので成立している。"
    "他校の先生がこのシートをコピーすれば、その瞬間から許可ドメインはその学校に切り替わります。誰も何も設定しません。",

    # 11 トークン
    "生徒に渡すのは、改ざんできない名札です。"
    "中身は三つだけ。誰か。ただしメールではなく、不透明なID。"
    "どこへ送り返すか。その先生のGASのURL。そして、有効期限。"
    "これをHMAC-SHA256で署名します。鍵は、そのGASが自分で作った乱数で、アプリにも通信路にも一切出てきません。"
    "IDを書き換えれば署名が合わなくなり、捨てられます。送り先も署名の中にあるので、他人のGASへ差し替えることもできません。",

    # 12 記録
    "ここからが技術的な山場です。"
    "ゲームはページズ・デブ、GASはスクリプト・グーグル・コム。別のオリジンです。"
    "ブラウザは、クロスオリジンの通信にクッキーを付けません。"
    "つまり、記録を送る瞬間、GASは誰が来たのかをグーグルのセッションからは知りようがない。"
    "だから、さっきの署名トークンで名乗るんです。これがこの設計の核心です。"
    "コンテント・タイプをテキスト・プレーンにしているのも理由があります。"
    "ジェイソンにすると、CORSのプリフライトが飛んでしまう。GASはそれに答えられません。"
    "テキスト・プレーンなら単純リクエストとして扱われ、プリフライトが飛ばない。これが唯一の通し方です。",

    # 13 タイミング
    "いつシートに書かれるか。"
    "進捗が動いた2.5秒後に、変わった項目だけをまとめて一回だけ送ります。先生の画面には数秒で出ます。"
    "タブを閉じるときは、送信待ちがあれば即座に送ります。"
    "そして、次にアプリを開いたときに、送れていなかった分を送り直します。"
    "送信済みと覚えるのは、GASがオーケーを返した分だけ。だから、通信が切れても必ず追いつきます。",

    # 14 止まらない
    "壊してはいけない一線があります。"
    "GASが落ちていても、ゲームは絶対に止まらない。"
    "進捗の正本は、あくまで端末の中にあります。クラウドはその写しにすぎません。"
    "通信は全部握りつぶす。生徒から見た違いは、右上に記録中のバッジが出るかどうかだけです。",

    # 15 攻撃
    "URLは生徒全員に配ります。掲示板に貼られることもあるでしょう。だから、正面から並べておきます。"
    "他人になりすまして書き込むことはできません。署名が合わなくなるからです。"
    "トークンなしで書き込むこともできません。読み出しにもトークンが要ります。"
    "ただし、最後の一行は隠しません。"
    "生徒のトークンそのものを盗まれれば、なりすませます。"
    "これはセッションクッキーを盗まれるのと同じ性質の話で、署名で防げる種類のものではありません。"
    "絶対に安全ではない。そこは、きちんと書いておきたいと思いました。",

    # 16 記録の範囲
    "もうひとつ、大事な原則があります。"
    "記録に残るのは、先生のURLから入って学習した分だけです。"
    "端末にもともとあった進捗が、あとからアカウントへ合流することはありません。"
    "進捗には持ち主を刻んであり、違う人がログインしたら、アカウント側の記録を正とします。"
    "友人の端末を借りてログインしても、友人の成果が混ざることはありません。"
    "それでも、防げないものはあります。"
    "本人が開発者ツールで端末の記録を書き換えること。アカウントを貸して、代わりにやってもらうこと。"
    "だから私は、この記録をそのまま成績にはしません。"
    "誰が取り組んでいて、どこがつまずいているかを見るための道具として使う。それで十分だと考えています。",

    # 17 メール
    "生徒のメールアドレスは、先生のスプレッドシートから一歩も出ません。"
    "アプリが持っているのは、不透明なIDだけです。それが誰なのかを知る手立ては、アプリ側には存在しません。"
    "先生が見る進捗シートには、照合済みのメールが並びます。"
    "先生には見える。アプリには見えない。それが正しい形だと考えています。",

    # 18 結び
    "スプレッドシートは、先生がすでに持っています。デプロイのボタンも、グーグルがすでに用意しています。"
    "足りなかったのは、そのURLを踏んだ人だけを、そのシートに繋ぐ、という一本の線だけでした。"
    "先生は、URLを配る。生徒は、それを踏む。"
    "それだけで、担任ごとの独立したデータベースが立ち上がります。"
    "引き継ぎも、卒業も、異動も、シートをコピーするか捨てるかで済みます。"
    "この仕組みで、いま三つのアプリが動いています。",
]


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True)


def shoot_slides() -> int:
    """Playwright でスライドを1枚ずつ撮る。HTML が正本なので、図はSVGのまま綺麗に出る。"""
    pngs = sorted(WORK.glob("slide_*.png"))
    if pngs and not FORCE:
        print(f"スライド: {len(pngs)} 枚（既にある。撮り直すには --force）")
        return len(pngs)

    from playwright.sync_api import sync_playwright

    n = 0
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        page = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        page.goto(SLIDES_HTML.as_uri())
        page.wait_for_timeout(600)                    # フォントの確定を待つ
        slides = page.query_selector_all("section.slide")
        for i, el in enumerate(slides, 1):
            el.scroll_into_view_if_needed()
            page.wait_for_timeout(120)
            el.screenshot(path=str(WORK / f"slide_{i:02d}.png"))
            n += 1
            print(f"  撮影 slide_{i:02d}.png")
        b.close()
    return n


VP_LIMIT = 140      # Voicepeak は1回の実行につき140文字まで


def chunks(text: str) -> list[str]:
    """句点で切って、140文字を超えない塊にまとめる。長すぎる一文は読点でさらに割る。"""
    out: list[str] = []
    buf = ""
    for sent in [s + "。" for s in text.split("。") if s]:
        while len(sent) > VP_LIMIT:                      # 一文が長すぎる → 読点で割る
            cut = sent.rfind("、", 0, VP_LIMIT)
            if cut <= 0:
                cut = VP_LIMIT - 1
            head, sent = sent[:cut + 1], sent[cut + 1:]
            if buf and len(buf) + len(head) > VP_LIMIT:
                out.append(buf); buf = ""
            buf += head
            if len(buf) > VP_LIMIT - 20:
                out.append(buf); buf = ""
        if buf and len(buf) + len(sent) > VP_LIMIT:
            out.append(buf); buf = ""
        buf += sent
    if buf:
        out.append(buf)
    return out


def narrate(i: int, text: str) -> Path:
    """Voicepeak で1枚ぶんのナレーションを作る。140文字ずつに割って合成し、つなぐ。"""
    wav = WORK / f"narr_{i:02d}.wav"
    if wav.exists() and not FORCE:
        return wav

    parts = chunks(text)
    pieces = []
    for j, part in enumerate(parts):
        p = WORK / f"narr_{i:02d}_{j:02d}.wav"
        if not p.exists() or FORCE:
            # Voicepeak は "iconv_open is not supported" で断続的に落ちる。同じ文でも
            # 再試行すれば通るので、少し待って何度かやり直す。
            for attempt in range(4):
                r = run([VOICEPEAK, "-s", part, "-n", NARRATOR, "-o", str(p),
                         "--speed", "100", "--pitch", "0"])
                if p.exists():
                    break
                print(f"    再試行 slide={i} part={j} ({attempt + 1}/4)")
                time.sleep(2.0)
            else:
                raise SystemExit(f"ナレーション生成に失敗 slide={i} part={j}\n{part}\n{r.stderr[-400:]}")
        pieces.append(p)

    if len(pieces) == 1:
        pieces[0].rename(wav)
    else:
        lst = WORK / f"narr_{i:02d}.txt"
        lst.write_text("".join(f"file '{p.name}'\n" for p in pieces), encoding="utf-8")
        r = run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(wav)])
        if not wav.exists():
            raise SystemExit(f"ナレーション結合に失敗: {i}\n{r.stderr[-400:]}")
    print(f"  合成 narr_{i:02d}.wav  ({len(parts)}分割 / {dur(wav):.1f}秒)")
    return wav


def dur(path: Path) -> float:
    r = run(["ffprobe", "-v", "0", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(path)])
    return float((r.stdout or "0").strip())


def build_clip(i: int, png: Path, wav: Path) -> Path:
    """1枚ぶんの動画。前後に間を取り、音声の長さにスライドを合わせる。"""
    mp4 = WORK / f"clip_{i:02d}.mp4"
    if mp4.exists() and not FORCE:
        return mp4
    total = PAD_HEAD + dur(wav) + PAD_TAIL
    r = run([
        "ffmpeg", "-y",
        "-loop", "1", "-framerate", str(FPS), "-i", str(png),
        "-i", str(wav),
        # 頭に無音を足して、喋り出しを少し遅らせる
        "-filter_complex", f"[1:a]adelay={int(PAD_HEAD*1000)}|{int(PAD_HEAD*1000)},apad[a]",
        "-map", "0:v", "-map", "[a]",
        "-t", f"{total:.3f}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-shortest", str(mp4),
    ])
    if not mp4.exists():
        raise SystemExit(f"クリップ生成に失敗: {i}\n{r.stderr[-500:]}")
    print(f"  クリップ clip_{i:02d}.mp4  {total:.1f}秒")
    return mp4


def concat(clips: list[Path]) -> None:
    lst = WORK / "concat.txt"
    lst.write_text("".join(f"file '{c.name}'\n" for c in clips), encoding="utf-8")
    r = run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
             "-c", "copy", "-movflags", "+faststart", str(OUT)])
    if not OUT.exists():
        raise SystemExit(f"結合に失敗\n{r.stderr[-500:]}")


def main() -> int:
    WORK.mkdir(exist_ok=True)

    print("── スライドを撮る")
    n = shoot_slides()
    if n != len(NARRATION):
        raise SystemExit(f"スライド {n} 枚 と ナレーション {len(NARRATION)} 本 が食い違っています。"
                         f"\nHTML を直したら NARRATION も合わせてください。")

    print("── ナレーションを作る")
    clips = []
    for i, text in enumerate(NARRATION, 1):
        wav = narrate(i, text)
        clips.append(build_clip(i, WORK / f"slide_{i:02d}.png", wav))

    print("── 結合")
    concat(clips)

    total = dur(OUT)
    size = OUT.stat().st_size / 1e6
    print(f"\n完成: {OUT}")
    print(f"  {int(total//60)}分{int(total%60)}秒 ／ {size:.0f}MB ／ {W}x{H} {FPS}fps")
    return 0


if __name__ == "__main__":
    sys.exit(main())
