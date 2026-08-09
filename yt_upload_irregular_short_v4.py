"""不規則変化動詞の歌 ショート v4(問いかけ+豆知識トーン・ABB型ハイライト)を
YouTube に限定公開(unlisted)でアップロード。"""
from __future__ import annotations

import sys
from pathlib import Path

PROJ = Path(__file__).resolve().parent
VIDEO = PROJ / "shorts" / "irregular_verbs_short_v4.mp4"
TOKEN = PROJ / "token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]

TITLE = "歌で覚えると2倍残るらしい?不規則変化動詞・ABB型30秒 #Shorts"

DESCRIPTION = (
    "歌で覚える不規則変化動詞 — 30秒ショート版(ABB型ハイライト)\n"
    "\n"
    "「不規則変化動詞、全部覚えてる?」\n"
    "歌で覚えると、2倍残りやすいらしいよ。\n"
    "(Ludke et al., 2014 / Memory & Cognition)\n"
    "\n"
    "中学英語で頻出する「ABB型」(過去形=過去分詞)の不規則変化動詞を中心に、"
    "歌に乗せて 30 秒で復習できるショート版です。\n"
    "(元曲=フル尺の「不規則変化動詞の歌」: https://youtu.be/c0bh8bZI6BY )\n"
    "\n"
    "▼ この30秒に登場するパターン(中盤ABB型→末尾でABC型に移行)\n"
    "make-made-made / meet-met-met / pay-paid-paid / read-read-read /\n"
    "say-said-said / sell-sold-sold / send-sent-sent / sit-sat-sat /\n"
    "sleep-slept-slept / spend-spent-spent / stand-stood-stood /\n"
    "teach-taught-taught / tell-told-told / think-thought-thought /\n"
    "understand-understood-understood / win-won-won\n"
    "→ begin-began-begun / break-broke-broken (ABC型へ)\n"
    "\n"
    "──────────────\n"
    "🔗 Teacher Tacos English\n"
    "──────────────\n"
    "🌐 学習サイト: https://english-lesson.gasflare.workers.dev/\n"
    "▶️ チャンネル: https://www.youtube.com/@TeacherTacosEnglish\n"
    "\n"
    "歌・動画・日本語混じり文で、中高 6 年分の英語をまるごと学べる学習サイト。\n"
    "\n"
    "▼ 関連\n"
    "・フル尺『不規則変化動詞の歌』: https://youtu.be/c0bh8bZI6BY\n"
    "・ABC型ハイライト・ショート版: https://youtube.com/shorts/LaHcDKNKevM\n"
    "\n"
    "#英語学習 #不規則動詞 #中学英語 #英語の歌 #ABB型 #Shorts"
)

TAGS = [
    "英語学習",
    "不規則動詞",
    "不規則変化動詞",
    "中学英語",
    "高校英語",
    "英語の歌",
    "歌で覚える英語",
    "ABB型",
    "Shorts",
    "Teacher Tacos English",
    "二重符号化",
    "第二言語習得",
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
