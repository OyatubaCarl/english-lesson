"""ルー語クイズShort v1 論文あり版を Suno BGM 差し替えで再アップロード。

usage: python3 yt_upload_lou_quiz_short_sunobgm.py [public|unlisted]
既定: public（指示「流して」に従い即公開）
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJ = Path(__file__).resolve().parent
TOKEN = PROJ / "token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]

VIDEO = PROJ / "shorts" / "lou_quiz_short_v1_sunobgm.mp4"

SITE = "https://english-lesson.gasflare.workers.dev/"
CH = "https://www.youtube.com/@TeacherTacosEnglish"

# 最多再生 v1 論文あり (j2B_HuWjNoM) の内容そのまま、BGM のみ Suno 学習向け曲に差し替え
TITLE = "これ読める? “ephemeral” 日本語混じり英単語クイズ #Shorts"

DESCRIPTION = f"""「桜の美しさは ephemeral だ。」— この英単語、意味わかる?

日本語の中に英単語を 1 つ混ぜるだけで、初見の単語でも文脈からほぼ意味が取れる。
これは「Diglot Weave(ダイグロット・ウィーブ)」と呼ばれる、れっきとした第二言語習得の手法です。

北海道大学の Mazur, Rzepka & Araki (2012) の実験では、
事前に単語を知らない子どもでも 約 80% が文脈から意味を正しく当てました。

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
    "ephemeral", "ルー語", "Diglot Weave", "コードスイッチング",
    "日本語混じり", "Shorts", "Teacher Tacos English",
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
    privacy = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in ("public", "unlisted") else "public"
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
    print(f"  shorts: https://www.youtube.com/shorts/{vid}", flush=True)
    print(f"  (privacy: {privacy})", flush=True)


if __name__ == "__main__":
    main()
