"""ルー語クイズShort 論文なし版 (lou_quiz_short_v1_nopaper.mp4) を YouTube に限定公開でアップロード。

論文引用ブロックを抜き、CTA をじっくり出した A/B 用バリアント。

usage: python3 yt_upload_lou_quiz_short_nopaper.py [unlisted|public]
既定: unlisted
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJ = Path(__file__).resolve().parent
TOKEN = PROJ / "token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]

VIDEO = PROJ / "shorts" / "lou_quiz_short_v1_nopaper.mp4"

SITE = "https://english-lesson.gasflare.workers.dev/"
CH = "https://www.youtube.com/@TeacherTacosEnglish"

TITLE = "これ読める? 桜と “ephemeral” 日本語混じり英単語 #Shorts"

DESCRIPTION = f"""「桜の美しさは ephemeral だ。」— この英単語、意味わかる?

日本語の中に英単語を 1 つ混ぜるだけで、初見でも文脈からスッと意味が取れる。
これが「日本語混じりで覚える英単語」の入口です。

──────────────
🔗 Teacher Tacos English
──────────────
🌐 {SITE}
▶️ {CH}

中高で習う英単語が、日本語混じりで全部学べます。
歌・動画・日本語混じり文で、中高 6 年分の英語をまるごと。

#英語学習 #英単語 #高校英語 #中学英語 #英語クイズ #ephemeral #Shorts
"""

TAGS = [
    "英語学習", "英単語", "高校英語", "中学英語", "英語クイズ",
    "ephemeral", "ルー語", "日本語混じり", "歌で覚える英語",
    "Shorts", "Teacher Tacos English",
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
    privacy = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in ("public", "unlisted") else "unlisted"
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
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }
    from googleapiclient.http import MediaFileUpload

    media = MediaFileUpload(
        str(VIDEO), mimetype="video/mp4", resumable=True, chunksize=8 * 1024 * 1024
    )
    request = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    size_mb = VIDEO.stat().st_size // 1024 // 1024
    print(f"Uploading {VIDEO.name} ({size_mb} MB) as {privacy}…", flush=True)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  {int(status.progress() * 100)}%", flush=True)
    vid = response["id"]
    print(f"\nUploaded: {vid}", flush=True)
    print(f"  watch:  https://youtu.be/{vid}", flush=True)
    print(f"  shorts: https://www.youtube.com/shorts/{vid}", flush=True)
    print(f"  (privacy: {privacy})", flush=True)


if __name__ == "__main__":
    main()
