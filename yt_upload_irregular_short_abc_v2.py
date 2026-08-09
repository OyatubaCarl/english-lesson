#!/usr/bin/env python3
"""Upload the 30-second ABC-pattern irregular-verb Short."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT = Path(__file__).resolve().parent
VIDEO = PROJECT / "shorts" / "irregular_verbs_short_abc_v2.mp4"
TOKEN = PROJECT / "token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]

TITLE = "歌なら簡単！不規則動詞変化17語を30秒で覚える #Shorts"
DESCRIPTION = """不規則動詞変化は、歌なら簡単に覚えられる！

ABC型を中心に、原形・過去形・過去分詞の17語を30秒で練習できる歌です。
歌われている形が黄色になるので、画面を見ながら一緒に歌ってみてください。

▼ 収録17語
begin-began-begun / break-broke-broken / do-did-done /
drink-drank-drunk / drive-drove-driven / eat-ate-eaten /
get-got-got/gotten / give-gave-given / go-went-gone /
know-knew-known / rise-rose-risen / see-saw-seen /
show-showed-shown/showed / sing-sang-sung / speak-spoke-spoken /
swim-swam-swum / take-took-taken

▶ フル尺『不規則変化動詞の歌』
https://youtu.be/c0bh8bZI6BY

▶ Teacher Tacos English
https://www.youtube.com/@TeacherTacosEnglish

#不規則動詞 #中学英語 #歌で覚える英語 #Shorts"""

TAGS = [
    "不規則動詞",
    "不規則変化動詞",
    "ABC型",
    "中学英語",
    "英語学習",
    "英語の歌",
    "歌で覚える英語",
    "過去分詞",
    "Shorts",
    "Teacher Tacos English",
]


def youtube_client():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    credentials = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        TOKEN.write_text(credentials.to_json(), encoding="utf-8")
    return build("youtube", "v3", credentials=credentials)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "privacy",
        nargs="?",
        choices=("private", "unlisted", "public"),
        default="unlisted",
    )
    args = parser.parse_args()

    if not VIDEO.exists():
        print(f"ERROR: video not found: {VIDEO}", file=sys.stderr)
        raise SystemExit(1)
    if not TOKEN.exists():
        print(f"ERROR: OAuth token not found: {TOKEN}", file=sys.stderr)
        raise SystemExit(1)

    youtube = youtube_client()
    channels = youtube.channels().list(part="snippet", mine=True).execute().get("items", [])
    if not channels:
        print("ERROR: authenticated YouTube channel was not found", file=sys.stderr)
        raise SystemExit(1)
    channel = channels[0]
    print(f"Channel: {channel['snippet']['title']} ({channel['id']})", flush=True)

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
            "privacyStatus": args.privacy,
            "selfDeclaredMadeForKids": False,
        },
    }

    from googleapiclient.http import MediaFileUpload

    media = MediaFileUpload(
        str(VIDEO),
        mimetype="video/mp4",
        resumable=True,
        chunksize=8 * 1024 * 1024,
    )
    request = youtube.videos().insert(
        part="snippet,status", body=body, media_body=media
    )
    print(
        f"Uploading {VIDEO.name} ({VIDEO.stat().st_size / 1024 / 1024:.1f} MiB) "
        f"as {args.privacy}…",
        flush=True,
    )
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  {int(status.progress() * 100)}%", flush=True)

    video_id = response["id"]
    print(f"VIDEO_ID={video_id}")
    print(f"WATCH_URL=https://youtu.be/{video_id}")
    print(f"SHORTS_URL=https://www.youtube.com/shorts/{video_id}")


if __name__ == "__main__":
    main()
