"""ルー語クイズShort v2 (英単語ナレのみ・論文なし) を YouTube に限定公開でアップロード。

variant:
  clean : 冒頭タイトルなし
  intro : 冒頭に「ルー語風 英単語クイズ」表示

usage: python3 yt_upload_lou_quiz_short_v2.py [clean|intro] [unlisted|public]
既定: clean unlisted
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJ = Path(__file__).resolve().parent
TOKEN = PROJ / "token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]

SITE = "https://english-lesson.gasflare.workers.dev/"
CH = "https://www.youtube.com/@TeacherTacosEnglish"

COMMON_TAIL = f"""

──────────────
🔗 Teacher Tacos English
──────────────
🌐 {SITE}
▶️ {CH}

中高で習う英単語が、日本語混じりで全部学べます。
歌・動画・日本語混じり文で、中高 6 年分の英語をまるごと。

#英語学習 #英単語 #高校英語 #中学英語 #英語クイズ #ephemeral #Shorts
"""

VARIANTS = {
    "clean": {
        "video": PROJ / "shorts" / "lou_quiz_short_v2_clean.mp4",
        "title": "これ読める? 桜と “ephemeral” 日本語混じり英単語 #Shorts",
        "desc_head": (
            "「桜の美しさは ephemeral だ。」— この英単語、意味わかる?\n"
            "\n"
            "日本語の中に英単語を 1 つ混ぜるだけで、初見でも文脈から意味が取れる。\n"
            "これが「日本語混じりで覚える英単語」のいちばん優しい入口です。\n"
        ),
        "tags": [
            "英語学習", "英単語", "高校英語", "中学英語", "英語クイズ",
            "ephemeral", "ルー語", "日本語混じり",
            "Shorts", "Teacher Tacos English",
        ],
    },
    "intro": {
        "video": PROJ / "shorts" / "lou_quiz_short_v2_intro.mp4",
        "title": "【ルー語風 英単語クイズ】桜と “ephemeral” #Shorts",
        "desc_head": (
            "ルー語風 英単語クイズ。「桜の美しさは ephemeral だ。」— 意味わかる?\n"
            "\n"
            "日本語の中に英単語を 1 つ混ぜるだけで、初見でも文脈から意味が取れる。\n"
            "難しい英単語でも、日本語の文脈に乗せれば一発で頭に入ります。\n"
        ),
        "tags": [
            "英語学習", "英単語", "高校英語", "中学英語", "英語クイズ",
            "ephemeral", "ルー語", "ルー語風", "日本語混じり",
            "Shorts", "Teacher Tacos English",
        ],
    },
}


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
    variant = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in VARIANTS else "clean"
    privacy = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] in ("public", "unlisted") else "unlisted"
    v = VARIANTS[variant]
    video = v["video"]
    if not video.exists():
        print(f"ERROR: {video} not found", file=sys.stderr)
        sys.exit(1)

    yt = auth()
    body = {
        "snippet": {
            "title": v["title"],
            "description": v["desc_head"] + COMMON_TAIL,
            "tags": v["tags"],
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
        str(video), mimetype="video/mp4", resumable=True, chunksize=8 * 1024 * 1024
    )
    request = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    size_mb = video.stat().st_size // 1024 // 1024
    print(f"Uploading [{variant}] {video.name} ({size_mb} MB) as {privacy}…", flush=True)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  {int(status.progress() * 100)}%", flush=True)
    vid = response["id"]
    print(f"\nUploaded [{variant}]: {vid}", flush=True)
    print(f"  shorts: https://www.youtube.com/shorts/{vid}", flush=True)


if __name__ == "__main__":
    main()
