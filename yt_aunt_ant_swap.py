"""Privatize old Aunt Ant video and update related-video links elsewhere.

Steps:
  1. Set old Aunt Ant (p3YFuDCHCxc) to private
  2. Update ABC Song (pAt-35463Kk) description: replace SvainIO0TQw + p3YFuDCHCxc → eGTZmwdWmA0
  3. Update Baker Bear (qvtc6srq1TI) description: same
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).parent
SCOPES = ["https://www.googleapis.com/auth/youtube"]

OLD_IDS = ["SvainIO0TQw", "p3YFuDCHCxc"]
NEW_ID = "eGTZmwdWmA0"
TARGETS_TO_UPDATE_LINKS = ["pAt-35463Kk", "qvtc6srq1TI"]


def auth():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    creds = Credentials.from_authorized_user_file(str(ROOT / "token.json"),
                                                  SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        (ROOT / "token.json").write_text(creds.to_json())
    from googleapiclient.discovery import build
    return build("youtube", "v3", credentials=creds)


def set_private(yt, video_id: str) -> None:
    cur = yt.videos().list(part="status", id=video_id).execute()
    if not cur["items"]:
        print(f"  {video_id}: NOT FOUND")
        return
    status = cur["items"][0]["status"]
    status["privacyStatus"] = "private"
    yt.videos().update(part="status", body={
        "id": video_id, "status": status,
    }).execute()
    print(f"  {video_id}: privacy → private")


def replace_links_in_description(yt, video_id: str) -> None:
    cur = yt.videos().list(part="snippet", id=video_id).execute()
    if not cur["items"]:
        print(f"  {video_id}: NOT FOUND")
        return
    snip = cur["items"][0]["snippet"]
    desc = snip["description"]
    title = snip["title"]
    new_desc = desc
    for old in OLD_IDS:
        new_desc = new_desc.replace(old, NEW_ID)
    if new_desc == desc:
        print(f"  {video_id}: no link update needed")
        return
    snip["description"] = new_desc
    yt.videos().update(part="snippet", body={
        "id": video_id, "snippet": snip,
    }).execute()
    print(f"  {video_id} ({title[:30]}…): description updated")


def main() -> None:
    yt = auth()
    print("Privatizing old Aunt Ant videos…")
    for vid in OLD_IDS:
        set_private(yt, vid)
    print("\nUpdating related-video links in ABC + Baker Bear…")
    for vid in TARGETS_TO_UPDATE_LINKS:
        replace_links_in_description(yt, vid)
    print("\nDone.")


if __name__ == "__main__":
    main()
