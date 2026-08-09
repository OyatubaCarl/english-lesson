"""Upload the new captioned Aunt Ant Short A video to YouTube as 'unlisted'.

This is v3: rebuilt with whisper.cpp word-level timing + black ant scene.
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).parent
VIDEO = Path(
    "/Users/masaki/Library/CloudStorage/GoogleDrive-sarosaro36@gmail.com/"
    "マイドライブ/個人用/ClaudeCode/Funnics Island/songs/"
    "02_aunt_ant_short_a/final_captioned.mp4"
)
SCOPES = ["https://www.googleapis.com/auth/youtube"]

TITLE = (
    "アントおばさんのみじかい「a」のおと "
    "〜Funnics Island Short A Song〜【歌詞字幕つき】"
)

DESCRIPTION = (
    "🐜 アントおばさんと いっしょに、みじかい「a」の おとを おぼえよう！🐜\n"
    "\n"
    "「Cat（キャット）」「Hat（ハット）」「Ant（アント）」「Bag（バッグ）」…\n"
    "ぜんぶ おなじ、みじかい「あ」の おと（/æ/）です。\n"
    "たった 4つの ぶんを、いれかえながら なんども くりかえして、\n"
    "リズムで おぼえる フォニックス ソング。\n"
    "\n"
    "👉 単語ごとに リズムに 合わせた キネティック字幕つき！\n"
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
    "https://youtu.be/qvtc6srq1TI\n"
    "\n"
    "🌐 中学・高校英語の体系的学習サイト「うたとミックス」:\n"
    "https://english-lesson.gasflare.workers.dev/\n"
    "\n"
    "#フォニックス #ShortA #英語の歌 #こども英語 #幼児英語 "
    "#アルファベット #FunnicsIsland #ファニックスアイランド #英語学習"
)

TAGS = [
    "FunnicsIsland", "ファニックスアイランド", "ShortA", "こども英語",
    "アルファベット", "フォニックス", "幼児英語", "短いA",
    "英語の歌", "英語入門", "英語学習", "AuntAnt",
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


def main() -> None:
    if not VIDEO.exists():
        print(f"ERROR: {VIDEO} not found", file=sys.stderr)
        sys.exit(1)
    yt = auth()

    body = {
        "snippet": {
            "title": TITLE,
            "description": DESCRIPTION,
            "tags": TAGS,
            "categoryId": "27",
            "defaultLanguage": "ja",
            "defaultAudioLanguage": "ja",
        },
        "status": {
            "privacyStatus": "unlisted",
            "selfDeclaredMadeForKids": True,
        },
    }

    from googleapiclient.http import MediaFileUpload
    media = MediaFileUpload(str(VIDEO), mimetype="video/mp4",
                            resumable=True, chunksize=8 * 1024 * 1024)
    request = yt.videos().insert(part="snippet,status", body=body,
                                 media_body=media)
    print(f"Uploading {VIDEO.name} ({VIDEO.stat().st_size // 1024 // 1024} MB)…")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            print(f"  {pct}%")
    print(f"\nUploaded video id: {response['id']}")
    print(f"  https://youtu.be/{response['id']}")


if __name__ == "__main__":
    main()
