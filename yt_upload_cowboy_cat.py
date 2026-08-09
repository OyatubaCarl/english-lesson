"""Upload the Cowboy Cat counting-song video to YouTube.

Bilingual line-caption version (final_captioned.mp4). Uploads as 'unlisted' by
default (set PRIVACY=public to publish directly). Beginner-book "番外編" (extra).
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent
VIDEO = Path(
    "/Users/masaki/Documents/ClaudeCode/FunnicsIsland/songs/"
    "23_cowboy_cat_counting/final_captioned.mp4"
)
SCOPES = ["https://www.googleapis.com/auth/youtube"]
PRIVACY = os.environ.get("PRIVACY", "unlisted")

TITLE = (
    "カウボーイキャットのかぞえうた "
    "〜1から10まで英語で / Funnics Island Counting Song〜【歌詞字幕つき】"
)

DESCRIPTION = (
    "🤠 カウボーイキャットと いっしょに、1から10まで えいごで かぞえよう！🐱\n"
    "\n"
    "One big sun／Two brown boots／Three tall hats… みじかい えいごの フレーズで、\n"
    "1〜10の かずと みのまわりの ことばを、たのしい カントリー ソングで おぼえます。\n"
    "かぞえあげ（1→10）と かぞえさげ（10→1）の りょうほうが はいっています。\n"
    "\n"
    "👉 英語の行＋日本語訳の字幕つき。Funnics Island の絵本タッチ。\n"
    "\n"
    "──────────────\n"
    "📖 歌詞・くわしい解説はこちら（公式ページ・番外編）\n"
    "──────────────\n"
    "👉 https://english-lesson.gasflare.workers.dev/?book=beginner&lesson=22\n"
    "\n"
    "──────────────\n"
    "🔢 かぞえる もの（1〜10）\n"
    "──────────────\n"
    "1 sun（たいよう）／2 boots（ブーツ）／3 hats（ぼうし）／4 cows（うし）／5 stars（ほし）\n"
    "6 fish（さかな）／7 shells（かい）／8 birds（とり）／9 flags（はた）／10 cats（ねこ）\n"
    "\n"
    "──────────────\n"
    "👶 おすすめの つかいかた\n"
    "──────────────\n"
    "✅ ゆびで さしながら 1〜10を いっしょに かぞえる\n"
    "✅ One, two, three… と こえに だして リピート\n"
    "✅ かぞえさげ（10→1）にも チャレンジ\n"
    "\n"
    "──────────────\n"
    "📚 関連動画（Funnics Island シリーズ） / サイト\n"
    "──────────────\n"
    "🎵 ABC ソング（26 人のなかまたち）:\n"
    "https://youtu.be/pAt-35463Kk\n"
    "\n"
    "📒 入門英語 B1〜B20 一気見（Tom の物語で英文法）:\n"
    "https://youtu.be/y7WXvXCU9u8\n"
    "\n"
    "🌐 公式サイト（うたとミックス / Teacher Tacos English）:\n"
    "https://english-lesson.gasflare.workers.dev/\n"
    "\n"
    "#FunnicsIsland #ファニックスアイランド #カウボーイキャット #CowboyCat "
    "#かぞえうた #数の歌 #英語の歌 #こども英語 #幼児英語 #英語学習 #ティーチャータコス"
)

TAGS = [
    "FunnicsIsland", "ファニックスアイランド", "CowboyCat", "カウボーイキャット",
    "かぞえうた", "数の歌", "数字", "counting", "numbers", "1to10",
    "英語の歌", "こども英語", "幼児英語", "英語入門", "英語学習",
    "ティーチャータコス", "Teacher Tacos", "TeacherTacos",
]


def auth():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    creds = Credentials.from_authorized_user_file(str(ROOT / "token.json"), SCOPES)
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
        "status": {"privacyStatus": PRIVACY, "selfDeclaredMadeForKids": True},
    }
    from googleapiclient.http import MediaFileUpload
    media = MediaFileUpload(str(VIDEO), mimetype="video/mp4",
                            resumable=True, chunksize=8 * 1024 * 1024)
    request = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    print(f"Uploading {VIDEO.name} ({VIDEO.stat().st_size // 1024 // 1024} MB) as {PRIVACY}…")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  {int(status.progress() * 100)}%")
    print(f"\nUploaded video id: {response['id']}")
    print(f"  https://youtu.be/{response['id']}")


if __name__ == "__main__":
    main()
