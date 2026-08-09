"""Upload baker_bear_long_a_FINAL_subs.mp4 to YouTube as 'unlisted'.

Sets title / description / tags / category. Prints the resulting video URL
so we can plug it into index.html and youtube-map.json.
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).parent
VIDEO = ROOT / "baker_bear_long_a_FINAL_subs.mp4"
SCOPES = ["https://www.googleapis.com/auth/youtube"]

TITLE = "ベイカーベアとまほうのe 〜ロングAのおと〜 〜Funnics Island Long A Song〜"

DESCRIPTION = (
    "🐻 ベイカーベアと ふしぎな e で、ながい「A」の おとを おぼえよう！\n"
    "\n"
    "「cap → cape」「mat → mate」「plan → plane」…\n"
    "たんごの うしろに 「e」を つけると、A の おとが 「ア」から 「エイ」に へんしんします！\n"
    "これが フォニックスで ゆうめいな 「Magic E」 の ルール。\n"
    "ベイカーベア と エンジニアエッグ と いっしょに、リズムで おぼえよう。\n"
    "\n"
    "──────────────\n"
    "📖 歌詞・くわしい解説はこちら（公式ページ）\n"
    "──────────────\n"
    "👉 https://english-lesson.gasflare.workers.dev/?book=phonics&lesson=3\n"
    "うたの ぜんぶの 歌詞、変身する たんごの いちらん、クリックで はつおん が きける ページです。\n"
    "\n"
    "──────────────\n"
    "🪄 5 つの 変身ペア（Magic E ルール）\n"
    "──────────────\n"
    "① cap → cape（ぼうし → マント）\n"
    "② can → cane（かん → つえ）\n"
    "③ mat → mate（マット → なかま）\n"
    "④ plan → plane（けいかく → ひこうき）\n"
    "⑤ slat → slate（いた → せきばん）\n"
    "\n"
    "──────────────\n"
    "🔤 きょう おぼえる ながい A の たんご\n"
    "──────────────\n"
    "bake / cake / cape / cane / mate / plane / slate / plate / gate / lane\n"
    "\n"
    "──────────────\n"
    "👶 おすすめの つかいかた\n"
    "──────────────\n"
    "✅ うしろの「e」を 指で さしながら いっしょに よむ\n"
    "✅ 「cap → cape！」と 大きな こえで くりかえす\n"
    "✅ Short A（「ア」の おと）の レッスンと くらべて ちがいに きづく\n"
    "\n"
    "──────────────\n"
    "📚 関連動画（Funnics Island シリーズ） / サイト\n"
    "──────────────\n"
    "🎵 ABC ソング（26 人のなかまたち / Funnics Island ABC Song）:\n"
    "https://youtu.be/pAt-35463Kk\n"
    "\n"
    "🐜 アントおばさんの みじかい「a」の おと（Short A）:\n"
    "https://youtu.be/SvainIO0TQw\n"
    "\n"
    "🌐 中学・高校英語の体系的学習サイト「うたとミックス」:\n"
    "https://english-lesson.gasflare.workers.dev/\n"
    "\n"
    "──────────────\n"
    "\n"
    "#FunnicsIsland #ファニックスアイランド #LongA #MagicE "
    "#フォニックス #英語の歌 #こども英語 #幼児英語 #英語学習"
)

TAGS = [
    "FunnicsIsland", "ファニックスアイランド",
    "LongA", "MagicE",
    "ロングA", "マジックE",
    "フォニックス", "英語の歌", "こども英語",
    "幼児英語", "英語入門", "英語学習",
    "BakerBear", "EngineerEgg",
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
            "categoryId": "27",         # Education
            "defaultLanguage": "ja",
            "defaultAudioLanguage": "ja",
        },
        "status": {
            "privacyStatus": "unlisted",
            "selfDeclaredMadeForKids": True,
        },
    }

    from googleapiclient.http import MediaFileUpload
    media = MediaFileUpload(
        str(VIDEO), mimetype="video/mp4",
        resumable=True, chunksize=8 * 1024 * 1024,
    )
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
    print(f"  (privacy: unlisted — change to public on YouTube Studio when ready)")


if __name__ == "__main__":
    main()
