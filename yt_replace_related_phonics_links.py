"""Replace old ABC/Aunt YouTube links in existing phonics descriptions."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parent
SCOPES = ["https://www.googleapis.com/auth/youtube"]

OLD_ABC = "pAt-35463Kk"
OLD_ANT = "SvainIO0TQw"
NEW_ABC = "3B5yLO1HJGs"
NEW_ANT = "p3YFuDCHCxc"

TARGETS = [
    "qvtc6srq1TI",  # Baker Bear Long A
]


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
    for vid in TARGETS:
        cur = yt.videos().list(part="snippet", id=vid).execute()
        if not cur["items"]:
            print(f"{vid}: not found")
            continue
        snip = cur["items"][0]["snippet"]
        desc = snip.get("description", "")
        new_desc = desc.replace(OLD_ABC, NEW_ABC).replace(OLD_ANT, NEW_ANT)
        if new_desc == desc:
            print(f"{vid}: no old links found")
            continue
        snip["description"] = new_desc
        yt.videos().update(part="snippet", body={"id": vid, "snippet": snip}).execute()
        print(f"{vid}: updated related links")


if __name__ == "__main__":
    main()
