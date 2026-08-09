"""Upload the Aider Snail AI/AY song to YouTube."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parent
VIDEO = Path(
    "/Users/masaki/Documents/Codex/2026-05-02/"
    "funnics-island-docs-adding-new-song/preview-videos/"
    "aider_snail_final_captioned_with_new_groups.mp4"
)
SCOPES = ["https://www.googleapis.com/auth/youtube"]

SITE_URL = "https://english-lesson.gasflare.workers.dev/?book=phonics&lesson=4"
LINKS_URL = "https://english-lesson.gasflare.workers.dev/funnics-island-links.html"
ABC_ID = "3B5yLO1HJGs"
ANT_ID = "eGTZmwdWmA0"
BAKER_ID = "qvtc6srq1TI"

TITLE = (
    "エイダースネイルの AI・AY のおと "
    "〜Funnics Island AI/AY Song〜【歌詞字幕つき】"
)

DESCRIPTION = (
    f"{SITE_URL}\n"
    "↑ 歌詞・単語カード・解説はこちら（公式ページ）\n"
    "\n"
    "🐌 エイダースネイルといっしょに、AI と AY の「エイ」のおとをおぼえよう！\n"
    "\n"
    "A と I がならぶと ay。\n"
    "A と Y がならんでも ay。\n"
    "snail / trail / rain / train / day / play / way / stay など、\n"
    "同じ「エイ」の音になる単語を、歌とリズムで楽しく練習します。\n"
    "\n"
    "──────────────\n"
    "🔤 きょう おぼえる AI のたんご\n"
    "──────────────\n"
    "snail / trail / rain / train\n"
    "mail / pail / tail / sail\n"
    "paint / brain\n"
    "\n"
    "──────────────\n"
    "🔤 きょう おぼえる AY のたんご\n"
    "──────────────\n"
    "day / play / way / stay\n"
    "say / tray / May / hooray\n"
    "clay / gray\n"
    "\n"
    "──────────────\n"
    "📖 ルール\n"
    "──────────────\n"
    "A and I say “ay.”\n"
    "A and Y say “ay.”\n"
    "\n"
    "バラバラじゃなく、ひとかたまりで見るのがポイントです。\n"
    "\n"
    "──────────────\n"
    "📚 Funnics Island シリーズ\n"
    "──────────────\n"
    f"🎵 ABC ソング: https://youtu.be/{ABC_ID}\n"
    f"🐜 Short A: https://youtu.be/{ANT_ID}\n"
    f"🐻 Long A / Magic E: https://youtu.be/{BAKER_ID}\n"
    f"🔗 シリーズ一覧: {LINKS_URL}\n"
    "\n"
    "#FunnicsIsland #ファニックスアイランド #AI #AY #LongA "
    "#フォニックス #英語の歌 #こども英語 #幼児英語 #英語学習"
)

TAGS = [
    "FunnicsIsland",
    "ファニックスアイランド",
    "AI",
    "AY",
    "LongA",
    "フォニックス",
    "英語の歌",
    "こども英語",
    "幼児英語",
    "英語入門",
    "英語学習",
    "AiderSnail",
    "TeacherTacos",
]


def auth():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials

    creds = Credentials.from_authorized_user_file(str(ROOT / "token.json"), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        (ROOT / "token.json").write_text(creds.to_json())
    from googleapiclient.discovery import build

    return build("youtube", "v3", credentials=creds)


def main() -> None:
    if not VIDEO.exists():
        raise FileNotFoundError(VIDEO)

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
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": True,
        },
    }

    from googleapiclient.http import MediaFileUpload

    media = MediaFileUpload(
        str(VIDEO), mimetype="video/mp4", resumable=True, chunksize=8 * 1024 * 1024
    )
    request = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    print(f"Uploading {VIDEO.name} ({VIDEO.stat().st_size // 1024 // 1024} MB)...")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  {int(status.progress() * 100)}%")
    vid = response["id"]
    print(f"Uploaded video id: {vid}")
    print(f"https://youtu.be/{vid}")


if __name__ == "__main__":
    main()
