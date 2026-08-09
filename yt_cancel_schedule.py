"""アップロード済み動画の公開予約(publishAt)を取り消して unlisted に戻す。

usage:
  python3 yt_cancel_schedule.py --all          # uploaded_quizzes.json 全件
  python3 yt_cancel_schedule.py <id> [<id>...] # 個別 video_id
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

PROJ = Path(__file__).resolve().parent
TOKEN = PROJ / "token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]
UPLOADED = PROJ / "shorts" / "uploaded_quizzes.json"


def auth():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN.write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: python3 yt_cancel_schedule.py --all | <video_id> [<id>...]")

    if sys.argv[1] == "--all":
        uploaded = json.loads(UPLOADED.read_text(encoding="utf-8"))
        ids = [u["video_id"] for u in uploaded]
    else:
        ids = sys.argv[1:]

    yt = auth()
    for vid in ids:
        # privacyStatus=unlisted にすると publishAt は無効化(クリア)される
        body = {
            "id": vid,
            "status": {
                "privacyStatus": "unlisted",
                "selfDeclaredMadeForKids": False,
            },
        }
        try:
            res = yt.videos().update(part="status", body=body).execute()
            st = res.get("status", {})
            print(f"  ✓ {vid}  privacy={st.get('privacyStatus')}  publishAt={st.get('publishAt') or '(cleared)'}")
        except Exception as e:
            print(f"  ✗ {vid} : {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
