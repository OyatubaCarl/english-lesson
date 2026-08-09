#!/usr/bin/env python3
"""Stage irregular-verbs v6 on YouTube, set its thumbnail, then publish it."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent.parent
OUTPUT = ROOT / "output"
METADATA = OUTPUT / "youtube_x_metadata.json"
RESULT = OUTPUT / "publish_result.json"
TOKEN = PROJECT / "token.json"
EXPECTED_CHANNEL_ID = "UC3Pkv-s22k8Np9aqOzzHaVQ"
SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]


def save_result(data: dict) -> None:
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    RESULT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    spec = json.loads(METADATA.read_text(encoding="utf-8"))
    video = OUTPUT / spec["video_file"]
    thumbnail = OUTPUT / spec["thumbnail_file"]
    yt_spec = spec["youtube"]

    if not video.exists() or not thumbnail.exists():
        raise SystemExit(f"Missing video or thumbnail: {video} / {thumbnail}")

    creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN.write_text(creds.to_json(), encoding="utf-8")
    yt = build("youtube", "v3", credentials=creds)

    channel = yt.channels().list(part="snippet", mine=True).execute()["items"][0]
    if channel["id"] != EXPECTED_CHANNEL_ID:
        raise SystemExit(
            f"Wrong YouTube channel: {channel['snippet']['title']} ({channel['id']})"
        )
    print(f"YouTube channel: {channel['snippet']['title']} ({channel['id']})", flush=True)

    result = json.loads(RESULT.read_text(encoding="utf-8")) if RESULT.exists() else {}
    existing_id = result.get("youtube", {}).get("video_id")
    if existing_id:
        existing = yt.videos().list(part="snippet,status", id=existing_id).execute().get("items", [])
        if not existing:
            raise SystemExit(f"Recorded YouTube video no longer exists: {existing_id}")
        if existing[0]["snippet"]["title"] != yt_spec["title"]:
            raise SystemExit(f"Recorded YouTube video title does not match: {existing_id}")
        video_id = existing_id
        url = f"https://youtu.be/{video_id}"
        result["youtube"]["privacy_status"] = existing[0]["status"]["privacyStatus"]
        print(f"Resuming existing upload: {url}", flush=True)
    else:
        body = {
            "snippet": {
                "title": yt_spec["title"],
                "description": yt_spec["description"],
                "tags": yt_spec["tags"],
                "categoryId": yt_spec["category_id"],
                "defaultLanguage": yt_spec["default_language"],
                "defaultAudioLanguage": yt_spec["default_language"],
            },
            "status": {
                "privacyStatus": "unlisted",
                "selfDeclaredMadeForKids": yt_spec["made_for_kids"],
            },
        }
        media = MediaFileUpload(
            str(video), mimetype="video/mp4", resumable=True, chunksize=8 * 1024 * 1024
        )
        request = yt.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Upload: {int(status.progress() * 100)}%", flush=True)

        video_id = response["id"]
        url = f"https://youtu.be/{video_id}"
        result = {
            "youtube": {
                "video_id": video_id,
                "url": url,
                "channel_id": channel["id"],
                "channel_title": channel["snippet"]["title"],
                "privacy_status": "unlisted",
                "thumbnail_set": False,
                "processing_status": "unknown",
            }
        }
        save_result(result)
        print(f"Uploaded unlisted: {url}", flush=True)

    yt.thumbnails().set(
        videoId=video_id,
        media_body=MediaFileUpload(str(thumbnail), mimetype="image/jpeg"),
    ).execute()
    result["youtube"]["thumbnail_set"] = True
    save_result(result)
    print("Thumbnail: set", flush=True)

    deadline = time.time() + 600
    while True:
        item = yt.videos().list(part="processingDetails,status", id=video_id).execute()[
            "items"
        ][0]
        processing = item.get("processingDetails", {}).get("processingStatus", "unknown")
        result["youtube"]["processing_status"] = processing
        save_result(result)
        print(f"Processing: {processing}", flush=True)
        if processing == "succeeded":
            break
        if processing in {"failed", "terminated"}:
            raise SystemExit(f"YouTube processing failed: {processing}")
        if time.time() >= deadline:
            raise SystemExit("Timed out waiting for YouTube processing")
        time.sleep(10)

    yt.videos().update(
        part="status",
        body={
            "id": video_id,
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": yt_spec["made_for_kids"],
            },
        },
    ).execute()
    result["youtube"]["privacy_status"] = "public"
    result["youtube"]["published_at"] = datetime.now(timezone.utc).isoformat()
    save_result(result)
    print(f"PUBLIC: {url}", flush=True)


if __name__ == "__main__":
    main()
