"""Print current title + description for the two existing phonics videos."""
from __future__ import annotations
import os, sys
from pathlib import Path

ROOT = Path(__file__).parent
SCOPES = ["https://www.googleapis.com/auth/youtube"]


def auth():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    creds = Credentials.from_authorized_user_file(str(ROOT / "token.json"),
                                                  SCOPES)
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    from googleapiclient.discovery import build
    return build("youtube", "v3", credentials=creds)


def main() -> None:
    yt = auth()
    ids = ["pAt-35463Kk", "SvainIO0TQw"]
    resp = yt.videos().list(part="snippet", id=",".join(ids)).execute()
    for it in resp["items"]:
        print("=" * 70)
        print("ID         :", it["id"])
        print("Title      :", it["snippet"]["title"])
        print("Tags       :", it["snippet"].get("tags", []))
        print("Category   :", it["snippet"].get("categoryId"))
        print("Description:")
        print("-" * 70)
        print(it["snippet"]["description"])


if __name__ == "__main__":
    main()
