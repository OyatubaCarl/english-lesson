"""本日投稿予定だった動画(02-05)を元のpublishAtで再有効化。
過去時刻のものは即public、未来時刻はprivate+publishAtで再予約。

usage: python3 yt_republish_today.py [--dry-run]
"""
from __future__ import annotations
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJ = Path(__file__).resolve().parent
TOKEN = PROJ / "token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]
UPLOADED = PROJ / "shorts" / "uploaded_quizzes.json"
JST = timezone(timedelta(hours=9))

# 本日(JST)投稿予定の4本
TARGET_IDS = ["02_resilient", "03_ubiquitous", "04_scrutinize", "05_profound"]


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
    dry = "--dry-run" in sys.argv
    uploaded = json.loads(UPLOADED.read_text(encoding="utf-8"))
    now = datetime.now(JST)
    plan = []
    for entry in uploaded:
        if entry["id"] not in TARGET_IDS:
            continue
        publish_at = datetime.fromisoformat(entry["publish_at_jst"])
        # 余裕2分: 直前/過ぎている → 即public
        if publish_at <= now + timedelta(minutes=2):
            action = "PUBLIC NOW"
            body = {
                "id": entry["video_id"],
                "status": {
                    "privacyStatus": "public",
                    "selfDeclaredMadeForKids": False,
                },
            }
        else:
            publish_iso_utc = publish_at.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
            action = f"SCHEDULE @{publish_at.strftime('%H:%M JST')}"
            body = {
                "id": entry["video_id"],
                "status": {
                    "privacyStatus": "private",
                    "publishAt": publish_iso_utc,
                    "selfDeclaredMadeForKids": False,
                },
            }
        plan.append((entry, body, action))

    print(f"now = {now.isoformat()}\n")
    print(f"{'id':<14} {'video':<12} action")
    print("-" * 60)
    for entry, body, action in plan:
        print(f"{entry['id']:<14} {entry['video_id']:<12} {action}")
    print()

    if dry:
        print("(dry-run; nothing executed)")
        return

    yt = auth()
    for entry, body, action in plan:
        try:
            res = yt.videos().update(part="status", body=body).execute()
            st = res.get("status", {})
            print(f"  ✓ {entry['id']} ({entry['video_id']}) "
                  f"privacy={st.get('privacyStatus')} publishAt={st.get('publishAt') or '(none)'}")
            # uploaded_quizzes.json 更新は publishAt のままなので変更不要
        except Exception as e:
            print(f"  ✗ {entry['id']} : {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
