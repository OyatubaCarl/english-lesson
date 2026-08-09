"""アップロード済み YouTube 動画を、指定分後に自動公開する。

YouTube Data API の videos.update で:
  privacyStatus = "private"
  publishAt     = ISO 8601 (UTC, Z) の時刻
を設定すると、指定時刻に自動で public になる(scheduled publish)。

usage: python3 yt_schedule_publish.py <video_id> [<video_id> ...] [--in MIN]
       既定: 5 分後
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJ = Path(__file__).resolve().parent
TOKEN = PROJ / "token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]


def auth():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN.write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def parse_args(argv: list[str]) -> tuple[list[str], int]:
    minutes = 5
    ids: list[str] = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--in" and i + 1 < len(argv):
            minutes = int(argv[i + 1])
            i += 2
        else:
            ids.append(a)
            i += 1
    return ids, minutes


def main() -> None:
    ids, minutes = parse_args(sys.argv[1:])
    if not ids:
        print("usage: python3 yt_schedule_publish.py <video_id> [<id> ...] [--in MIN]",
              file=sys.stderr)
        sys.exit(2)

    publish_at = (datetime.now(timezone.utc) + timedelta(minutes=minutes))
    publish_iso = publish_at.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    print(f"Target publishAt (UTC): {publish_iso}  ({minutes} min from now)")

    yt = auth()
    for vid in ids:
        body = {
            "id": vid,
            "status": {
                "privacyStatus": "private",
                "publishAt": publish_iso,
                "selfDeclaredMadeForKids": False,
            },
        }
        try:
            res = yt.videos().update(part="status", body=body).execute()
        except Exception as e:
            print(f"  ✗ {vid} : {e}", file=sys.stderr)
            continue
        st = res.get("status", {})
        print(f"  ✓ {vid}  privacy={st.get('privacyStatus')}  "
              f"publishAt={st.get('publishAt')}")
        print(f"    watch:  https://youtu.be/{vid}")
        print(f"    shorts: https://www.youtube.com/shorts/{vid}")


if __name__ == "__main__":
    main()
