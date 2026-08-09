"""不規則変化動詞の歌 ショート版を YouTube に限定公開(unlisted)でアップロード。
認証は同ディレクトリの token.json（OAuth refresh_token入り）を再利用。
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJ = Path(__file__).resolve().parent
VIDEO = PROJ / "shorts" / "irregular_verbs_short_v3.mp4"
TOKEN = PROJ / "token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]

TITLE = "不規則変化動詞の歌(30秒ショート版・ABC型ハイライト)#Shorts"

DESCRIPTION = (
    "不規則変化動詞の歌 — 30秒ショート版(ABC型ハイライト)\n"
    "\n"
    "中学英語で出てくる「ABC型」の不規則変化動詞 15 個を、歌に乗せて 30 秒で復習できる"
    "ショート版です。\n"
    "(元曲=フル尺の「不規則変化動詞の歌」: https://youtu.be/c0bh8bZI6BY )\n"
    "\n"
    "▼ 収録動詞(ABC型)\n"
    "eat-ate-eaten / get-got-got / give-gave-given / go-went-gone / know-knew-known /\n"
    "rise-rose-risen / see-saw-seen / show-showed-shown / sing-sang-sung / "
    "speak-spoke-spoken /\n"
    "swim-swam-swum / take-took-taken / wake-woke-woken / wear-wore-worn / "
    "write-wrote-written\n"
    "\n"
    "──────────────\n"
    "🔗 Teacher Tacos English\n"
    "──────────────\n"
    "🌐 学習サイト: https://english-lesson.gasflare.workers.dev/\n"
    "▶️ チャンネル: https://www.youtube.com/@TeacherTacosEnglish\n"
    "\n"
    "中高 6 年分の英語を、歌・動画・日本語混じり文で、まるごと学べる学習サイトです。\n"
    "歌が呼び覚ます「子どもの頃の脳」。バイリンガル脳を、もう一度。\n"
    "\n"
    "▼ 連動レッスン\n"
    "中学英語 Lesson 4「新しい友達トム」と特にセットで使うと効果的:\n"
    "https://english-lesson.gasflare.workers.dev/?book=middle&lesson=4\n"
    "\n"
    "#英語学習 #不規則動詞 #中学英語 #英語の歌 #Shorts"
)

TAGS = [
    "英語学習",
    "不規則動詞",
    "不規則変化動詞",
    "中学英語",
    "高校英語",
    "英語の歌",
    "歌で覚える英語",
    "ABC型",
    "Shorts",
    "Teacher Tacos English",
]


def auth():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN.write_text(creds.to_json())
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
            "selfDeclaredMadeForKids": False,
        },
    }
    from googleapiclient.http import MediaFileUpload

    media = MediaFileUpload(
        str(VIDEO), mimetype="video/mp4", resumable=True, chunksize=8 * 1024 * 1024
    )
    request = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    size_mb = VIDEO.stat().st_size // 1024 // 1024
    print(f"Uploading {VIDEO.name} ({size_mb} MB)…", flush=True)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  {int(status.progress() * 100)}%", flush=True)
    vid = response["id"]
    print(f"\nUploaded video id: {vid}", flush=True)
    print(f"  watch:  https://youtu.be/{vid}", flush=True)
    print(f"  shorts: https://www.youtube.com/shorts/{vid}", flush=True)
    print(
        "  (privacy: unlisted/限定公開 — YouTube Studio で公開に変更してください)",
        flush=True,
    )


if __name__ == "__main__":
    main()
