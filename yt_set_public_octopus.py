"""Flip the Outlaw Octopus Short O video from unlisted to public.

Fetches the current status, changes only privacyStatus -> public, and preserves
the other writable status fields (selfDeclaredMadeForKids, license, embeddable,
publicStatsViewable) so the kids/compliance settings are not reset.
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).parent
VIDEO_ID = "LKb1DWeb-4k"
SCOPES = ["https://www.googleapis.com/auth/youtube"]


def auth():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    creds = Credentials.from_authorized_user_file(str(ROOT / "token.json"), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        (ROOT / "token.json").write_text(creds.to_json())
    from googleapiclient.discovery import build
    return build("youtube", "v3", credentials=creds)


def main() -> None:
    yt = auth()
    resp = yt.videos().list(part="status", id=VIDEO_ID).execute()
    items = resp.get("items", [])
    if not items:
        print(f"ERROR: video {VIDEO_ID} not found", file=sys.stderr)
        sys.exit(1)
    cur = items[0]["status"]
    print(f"current privacyStatus: {cur.get('privacyStatus')}")

    new_status = {"privacyStatus": "public"}
    for key in ("selfDeclaredMadeForKids", "license", "embeddable", "publicStatsViewable"):
        if key in cur:
            new_status[key] = cur[key]

    updated = yt.videos().update(
        part="status", body={"id": VIDEO_ID, "status": new_status}
    ).execute()
    print(f"new privacyStatus:     {updated['status'].get('privacyStatus')}")
    print(f"madeForKids preserved: {updated['status'].get('selfDeclaredMadeForKids')}")
    print(f"  https://youtu.be/{VIDEO_ID}")


if __name__ == "__main__":
    main()
