#!/usr/bin/env python3
"""YouTube概要欄の旧ドメイン→新ドメインを一括置換。

旧: english-lesson.gasflare.workers.dev
新: english.teachertacos.com

Usage:
  python3 yt_replace_domain.py --dry-run    # 変更対象を表示するだけ
  python3 yt_replace_domain.py              # 実際にPATCH
  python3 yt_replace_domain.py --limit 5    # 最初の5本だけ処理(動作確認用)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

OLD = "english-lesson.gasflare.workers.dev"
NEW = "english.teachertacos.com"

ROOT = Path(__file__).parent
TOKEN = ROOT / "token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]


def auth():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)


def get_uploads_playlist(yt) -> str:
    resp = yt.channels().list(part="contentDetails", mine=True).execute()
    return resp["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]


def list_all_video_ids(yt, uploads_pl: str) -> list[str]:
    ids: list[str] = []
    page = None
    while True:
        resp = yt.playlistItems().list(
            part="contentDetails",
            playlistId=uploads_pl,
            maxResults=50,
            pageToken=page,
        ).execute()
        for it in resp["items"]:
            ids.append(it["contentDetails"]["videoId"])
        page = resp.get("nextPageToken")
        if not page:
            break
    return ids


def fetch_snippets(yt, ids: list[str]) -> list[dict]:
    out: list[dict] = []
    for i in range(0, len(ids), 50):
        chunk = ids[i:i + 50]
        resp = yt.videos().list(part="snippet", id=",".join(chunk)).execute()
        out.extend(resp["items"])
    return out


def update_description(yt, video: dict, new_desc: str) -> None:
    snip = video["snippet"]
    body = {
        "id": video["id"],
        "snippet": {
            "title": snip["title"],
            "description": new_desc,
            "categoryId": snip.get("categoryId", "27"),
            "tags": snip.get("tags", []),
            "defaultLanguage": snip.get("defaultLanguage"),
            "defaultAudioLanguage": snip.get("defaultAudioLanguage"),
        },
    }
    body["snippet"] = {k: v for k, v in body["snippet"].items() if v is not None}
    yt.videos().update(part="snippet", body=body).execute()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    yt = auth()
    uploads_pl = get_uploads_playlist(yt)
    ids = list_all_video_ids(yt, uploads_pl)
    print(f"Total videos in channel: {len(ids)}")
    if args.limit > 0:
        ids = ids[:args.limit]
        print(f"Limited to first {len(ids)}")

    videos = fetch_snippets(yt, ids)
    targets = [v for v in videos if OLD in v["snippet"].get("description", "")]
    print(f"Videos containing '{OLD}': {len(targets)}")
    print("=" * 70)

    changed = 0
    for v in targets:
        desc = v["snippet"]["description"]
        new_desc = desc.replace(OLD, NEW)
        occurrences = desc.count(OLD)
        title = v["snippet"]["title"]
        vid = v["id"]
        print(f"[{vid}] {title}")
        print(f"  replacements: {occurrences}")
        if args.dry_run:
            print("  (dry-run, no API call)")
        else:
            try:
                update_description(yt, v, new_desc)
                print("  ✓ updated")
                changed += 1
            except Exception as e:
                print(f"  ✗ FAILED: {e}", file=sys.stderr)
    print("=" * 70)
    print(f"Done. {'Would update' if args.dry_run else 'Updated'} {len(targets) if args.dry_run else changed} / {len(targets)} videos.")


if __name__ == "__main__":
    main()
