"""中学英語 Lesson 2「海での一日」ショート A/B版を YouTube に限定公開でアップロード。
引数で版を選択: python3 yt_upload_l2_short.py a   /   b
A版=日本語訳つき, B版=英文のみ。A/Bテスト用。
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJ = Path(__file__).resolve().parent
TOKEN = PROJ / "token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]

SITE = "https://english-lesson.gasflare.workers.dev/?book=middle&lesson=2"
CH = "https://www.youtube.com/@TeacherTacosEnglish"

COMMON_TAIL = (
    "\n"
    "be 動詞の過去形は主語で使い分け。I/He/She/It は was、You/We/They は were。\n"
    "歌に乗せて、海での一日の思い出と一緒に覚えよう。\n"
    "\n"
    "──────────────\n"
    "🔗 Teacher Tacos English\n"
    "──────────────\n"
    f"🌐 本文・日本語訳・発音記号・単語テスト: {SITE}\n"
    f"▶️ チャンネル: {CH}\n"
    "\n"
    "歌・動画・日本語混じり文で、中高 6 年分の英語をまるごと。\n"
    "\n"
    "#英語学習 #中学英語 #be動詞 #英語の歌 #Shorts"
)

VARIANTS = {
    "a": {
        "video": PROJ / "shorts" / "l2_seaside_short_a_jp_v3.mp4",
        "title": "【日本語訳つき】海での一日|中学英語 Lesson 2 be動詞の過去形 #Shorts",
        "desc_head": (
            "海での一日 — 中学英語 Lesson 2(be動詞の過去形 was / were)\n"
            "【日本語訳つきバージョン】\n"
            "\n"
            "英文に合わせて日本語訳も表示。意味を確かめながら、英語の音とリズムを"
            "つかめます。\n"
        ),
        "tags": [
            "英語学習", "中学英語", "be動詞", "be動詞の過去形", "was were",
            "英語の歌", "歌で覚える英語", "日本語訳つき", "Shorts",
            "Teacher Tacos English",
        ],
    },
    "b": {
        "video": PROJ / "shorts" / "l2_seaside_short_b_raw_v3.mp4",
        "title": "海での一日|中学英語 Lesson 2 be動詞の過去形 was/were #Shorts",
        "desc_head": (
            "海での一日 — 中学英語 Lesson 2(be動詞の過去形 was / were)\n"
            "\n"
            "英語の音とリズムにそのまま浸れるバージョン。まず耳と目で英文を浴びよう。\n"
            "(日本語訳つきバージョンもあります)\n"
        ),
        "tags": [
            "英語学習", "中学英語", "be動詞", "be動詞の過去形", "was were",
            "英語の歌", "歌で覚える英語", "リスニング", "Shorts",
            "Teacher Tacos English",
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
    if len(sys.argv) < 2 or sys.argv[1] not in VARIANTS:
        print("usage: python3 yt_upload_l2_short.py [a|b] [public|unlisted]", file=sys.stderr)
        sys.exit(2)
    global PRIVACY
    PRIVACY = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] in ("public", "unlisted") else "unlisted"
    v = VARIANTS[sys.argv[1]]
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
            "privacyStatus": PRIVACY,
            "selfDeclaredMadeForKids": False,
        },
    }
    from googleapiclient.http import MediaFileUpload

    media = MediaFileUpload(
        str(video), mimetype="video/mp4", resumable=True, chunksize=8 * 1024 * 1024
    )
    request = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    print(f"Uploading {video.name} ({video.stat().st_size // 1024 // 1024} MB)…", flush=True)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  {int(status.progress() * 100)}%", flush=True)
    vid = response["id"]
    print(f"\nUploaded video id: {vid}", flush=True)
    print(f"  watch:  https://youtu.be/{vid}", flush=True)
    print(f"  shorts: https://www.youtube.com/shorts/{vid}", flush=True)
    print("  (privacy: unlisted/限定公開)", flush=True)


if __name__ == "__main__":
    main()
