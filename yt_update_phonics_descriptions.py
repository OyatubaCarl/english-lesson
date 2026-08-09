"""Update existing 2 phonics videos: rename Phonics Island → Funnics Island.

Rules:
  - Series brand: "Phonics Island" → "Funnics Island"
  - Series brand JP: "フォニックス・アイランド" → "ファニックス・アイランド"
  - Hashtag: "#PhonicsIsland" → "#FunnicsIsland"
  - Educational concept "フォニックス" / "phonics" lowercase → keep
  - Tags list: replace "PhonicsIsland" → "FunnicsIsland"
  - Add "Funnics Island シリーズ" framing to related-video links

Targets:
  - pAt-35463Kk  ABC Song (all 26 characters)
  - SvainIO0TQw  Aunt Ant Short A
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).parent
SCOPES = ["https://www.googleapis.com/auth/youtube"]


# ── Final intended snippets (exact replacements) ──────────────
ABC_TITLE = (
    "ファニックス・アイランド　フォニックスとABCの仲間たち"
    "　〜Funnics Island ABC Song〜"
)

ABC_DESCRIPTION = (
    "🌈 ファニックス・アイランド〜A から Z までの26人のなかまたち〜 🌈\n"
    "\n"
    "「アリおばさん」「ベイカーベア」「ジャグラークラゲ」…\n"
    "A から Z までのアルファベットそれぞれに、ぴったりの動物キャラクターが登場！\n"
    "それぞれの音から始まる単語と動作を、リズムと歌で楽しく覚えられる、こども向けフォニックス・ソングです。\n"
    "\n"
    "🎵 子どもたちが、歌いながら自然に英語の音とリズムを身につけられます。\n"
    "🎵 親子で振り付けしたり、教室の朝の会で流したり、いろんな使い方ができます。\n"
    "\n"
    "──────────────\n"
    "📖 歌詞・キャラクター紹介はこちら（公式ページ）\n"
    "──────────────\n"
    "👉 https://english-lesson.gasflare.workers.dev/?book=phonics\n"
    "動画と一緒に、26 人全員のイラスト・名前・歌詞（英語＋やさしい日本語）を見られます。\n"
    "\n"
    "──────────────\n"
    "🎵 A〜Z の 26 人のなかまたち 🎵\n"
    "──────────────\n"
    "A — アリおばさん（Aunt Ant）  asks / adds / applauds\n"
    "B — ベイカーベア（Baker Bear）  bakes / blows / builds\n"
    "C — カウボーイキャット（Cowboy Cat）  catches / climbs / counts\n"
    "D — ドクタードラゴン（Doctor Dragon）  draws / digs / dives\n"
    "E — エンジニアエッグ(Engineer Egg)  edits / enters / exercises\n"
    "F — フィッシャーフロッグ(Fisher Frog)  finds / flips / flies\n"
    "G — ガーディアンゴート(Guardian Goat)  grows / gives / grabs\n"
    "H — ハイカーヒッポ(Hiker Hippo)  holds / hugs / hides\n"
    "I — 発明家アイス(Inventor Ice)  invents / imagines / imitates\n"
    "J — ジャグラークラゲ(Juggler Jellyfish)  juggles / jumps / joins\n"
    "K — キングカンガルー(King Kangaroo)  kicks / keeps / kisses\n"
    "L — 司書ライオン(Librarian Lion)  lifts / learns / likes\n"
    "M — マジシャンマウス(Magician Mouse)  makes / mixes / moves\n"
    "N — 忍者ナット(Ninja Nut)  nibbles / names / needs\n"
    "O — アウトローオクトパス(Outlaw Octopus)  opens / offers / orders\n"
    "P — パイロットパンダ(Pilot Panda)  paints / pulls / packs\n"
    "Q — クイーンクイズ(Queen Quiz)  quizzes / questions / quacks\n"
    "R — ランナーラビット(Runner Rabbit)  reads / rolls / rides\n"
    "S — シンガースネーク(Singer Snake)  sings / sees / sips\n"
    "T — ティーチャータコス(Teacher Tacos)  teaches / taps / throws\n"
    "U — ユニコーンおじさん(Uncle Unicorn)  unzips / unties / unfolds\n"
    "V — バイキングウイルス(Viking Virus)  visits / vacuums / vanishes\n"
    "W — ウェイターウルフ(Waiter Wolf)  washes / waves / walks\n"
    "X — ボクサーフォックス(Boxer Fox)  fixes / mixes / waxes\n"
    "Y — ヨガイエティ(Yoga Yeti)  yells / yanks / yawns\n"
    "Z — ジグザグゼブラ(Zigzag Zebra)  zips / swims / zonks\n"
    "\n"
    "──────────────\n"
    "👶 おすすめの使い方\n"
    "──────────────\n"
    "✅ 朝の会・帰りの会の BGM に\n"
    "✅ おうちで親子いっしょに踊って覚える\n"
    "✅ 各キャラの動作（asks, adds, applauds…）を真似してみる\n"
    "✅ 子どもが「次は◯◯！」と先取りで歌えるまで繰り返し再生\n"
    "✅ 英語学習のいちばん最初の一歩として\n"
    "\n"
    "──────────────\n"
    "📚 関連動画（Funnics Island シリーズ） / サイト\n"
    "──────────────\n"
    "🐜 アントおばさんの みじかい「a」の おと（Short A）:\n"
    "https://youtu.be/SvainIO0TQw\n"
    "\n"
    "🐻 ベイカーベアと まほうの e（Long A / Magic E）:\n"
    "{BAKER_URL}\n"
    "\n"
    "🌐 中学・高校英語の体系的学習サイト「うたとミックス」:\n"
    "https://english-lesson.gasflare.workers.dev/\n"
    "\n"
    "──────────────\n"
    "\n"
    "#フォニックス #英語の歌 #ABCソング #こども英語 #幼児英語 "
    "#アルファベット #FunnicsIsland #ファニックスアイランド #英語学習"
)

ABC_TAGS = [
    "ABCソング", "FunnicsIsland", "ファニックスアイランド",
    "こども英語", "アルファベット", "フォニックス",
    "幼児英語", "英語の歌", "英語入門", "英語学習",
]

ANT_TITLE = (
    "アントおばさんのみじかい「a」のおと "
    "〜Funnics Island Short A Song〜"
)

ANT_DESCRIPTION = (
    "🐜 アントおばさんと いっしょに、みじかい「a」の おとを おぼえよう！🐜\n"
    "\n"
    "「Cat（キャット）」「Hat（ハット）」「Ant（アント）」「Bag（バッグ）」…\n"
    "ぜんぶ おなじ、みじかい「あ」の おと（/æ/）です。\n"
    "たった 4つの ぶんを、いれかえながら なんども くりかえして、\n"
    "リズムで おぼえる フォニックス ソング。\n"
    "\n"
    "──────────────\n"
    "📖 歌詞・くわしい解説はこちら（公式ページ）\n"
    "──────────────\n"
    "👉 https://english-lesson.gasflare.workers.dev/?book=phonics&lesson=2\n"
    "うたの ぜんぶの 歌詞、たんごのいちらん、クリックで はつおんを きける ページです。\n"
    "\n"
    "──────────────\n"
    "🎵 きょうの 4 つの ぶん 🎵\n"
    "──────────────\n"
    "① Fat cat in a hat（ふとった ねこが、ぼうしの なか）\n"
    "② Mad rat on a mat（おこった ねずみが、マットの うえ）\n"
    "③ Sad ant at a plant（かなしい アリが、はちうえの そばに）\n"
    "④ Black bag with a flag（くろい かばんが、はたを もって）\n"
    "\n"
    "──────────────\n"
    "🔤 きょう おぼえる たんご\n"
    "──────────────\n"
    "形容詞: Fat / Mad / Sad / Black\n"
    "主語:    Cat / Rat / Ant / Bag\n"
    "前置詞:  in / on / at / with\n"
    "もの:    Hat / Mat / Plant / Flag\n"
    "\n"
    "ぜんぶ 17 ご だけ！\n"
    "くみあわせを かえて、なんども きこえてくるよ。\n"
    "\n"
    "──────────────\n"
    "👶 おすすめの つかいかた\n"
    "──────────────\n"
    "✅ 朝の会・帰りの会の BGM に\n"
    "✅ おうちで てを たたきながら\n"
    "✅ 「Cat」「Hat」など 1 つの たんごずつ いっしょに マネ\n"
    "✅ ABC を おぼえた つぎの ステップに\n"
    "\n"
    "──────────────\n"
    "📚 関連動画（Funnics Island シリーズ） / サイト\n"
    "──────────────\n"
    "🎵 ABC ソング（26 人のなかまたち / Funnics Island ABC Song）:\n"
    "https://youtu.be/pAt-35463Kk\n"
    "\n"
    "🐻 ベイカーベアと まほうの e（Long A / Magic E）:\n"
    "{BAKER_URL}\n"
    "\n"
    "🌐 中学・高校英語の体系的学習サイト「うたとミックス」:\n"
    "https://english-lesson.gasflare.workers.dev/\n"
    "\n"
    "#フォニックス #ShortA #英語の歌 #こども英語 #幼児英語 "
    "#アルファベット #FunnicsIsland #ファニックスアイランド #英語学習"
)

ANT_TAGS = [
    "FunnicsIsland", "ファニックスアイランド", "ShortA", "こども英語",
    "アルファベット", "フォニックス", "幼児英語", "短いA",
    "英語の歌", "英語入門", "英語学習",
]


def auth():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    creds = Credentials.from_authorized_user_file(str(ROOT / "token.json"),
                                                  SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        (ROOT / "token.json").write_text(creds.to_json())
    from googleapiclient.discovery import build
    return build("youtube", "v3", credentials=creds)


def update(yt, vid: str, title: str, description: str, tags: list[str]) -> None:
    cur = yt.videos().list(part="snippet,status", id=vid).execute()
    if not cur["items"]:
        print(f"  {vid}: NOT FOUND"); return
    snip = cur["items"][0]["snippet"]
    snip["title"] = title
    snip["description"] = description
    snip["tags"] = tags
    snip["categoryId"] = "27"
    yt.videos().update(part="snippet", body={
        "id": vid, "snippet": snip,
    }).execute()
    print(f"  {vid}: updated  title={title[:40]}…")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python yt_update_phonics_descriptions.py <BAKER_VIDEO_ID>")
        sys.exit(1)
    baker_id = sys.argv[1]
    baker_url = f"https://youtu.be/{baker_id}"
    yt = auth()

    abc_desc = ABC_DESCRIPTION.replace("{BAKER_URL}", baker_url)
    ant_desc = ANT_DESCRIPTION.replace("{BAKER_URL}", baker_url)

    print("Updating ABC Song …")
    update(yt, "pAt-35463Kk", ABC_TITLE, abc_desc, ABC_TAGS)

    print("Updating Aunt Ant Short A …")
    update(yt, "SvainIO0TQw", ANT_TITLE, ant_desc, ANT_TAGS)

    print("Done.")


if __name__ == "__main__":
    main()
