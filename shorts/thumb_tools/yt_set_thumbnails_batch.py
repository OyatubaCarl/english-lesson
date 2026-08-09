#!/usr/bin/env python3
"""A群のYouTube動画に生成済みサムネイルを一括設定する。"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent
TOKEN = PROJECT_ROOT / "token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]
MANIFEST_PATH = BASE_DIR / "manifest_thumbs.json"
THUMBNAILS_DIR = BASE_DIR / "thumbnails"


def auth():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN.write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def thumbnail_filename(item: dict[str, Any]) -> str:
    item_id = item["id"]
    word = item["word"]
    if item_id.lower().endswith(f"_{word.lower()}"):
        return f"{item_id}.jpg"
    return f"{item_id}_{word}.jpg"


def targets() -> list[tuple[dict[str, Any], Path]]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return [
        (item, THUMBNAILS_DIR / thumbnail_filename(item))
        for item in manifest
        if item.get("group") == "A" and item.get("video_id") is not None
    ]


def dry_run(rows: list[tuple[dict[str, Any], Path]]) -> int:
    for item, jpg_path in rows:
        size_kb = round(jpg_path.stat().st_size / 1024, 1) if jpg_path.exists() else None
        print((item["id"], item["word"], item["video_id"], str(jpg_path), size_kb))
    return 0


def confirm(rows: list[tuple[dict[str, Any], Path]]) -> int:
    missing = [path for _, path in rows if not path.is_file()]
    if missing:
        print("以下のJPEGがないため送信を開始しません:", file=sys.stderr)
        for path in missing:
            print(f"  {path}", file=sys.stderr)
        return 1

    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload

    youtube = auth()
    success = 0
    failed = 0
    for index, (item, jpg_path) in enumerate(rows):
        last_exc: Exception | None = None
        for attempt in range(1, 4):
            try:
                youtube.thumbnails().set(
                    videoId=item["video_id"],
                    media_body=MediaFileUpload(str(jpg_path), mimetype="image/jpeg"),
                ).execute()
                success += 1
                print(f"成功: {item['id']} {item['word']} {item['video_id']}")
                last_exc = None
                break
            except (HttpError, ConnectionError, OSError) as exc:
                last_exc = exc
                print(
                    f"  試行{attempt}失敗 {item['id']} ({type(exc).__name__}): {exc}",
                    file=sys.stderr,
                )
                if attempt < 3:
                    time.sleep(5)
        if last_exc is not None:
            failed += 1
            print(f"失敗確定: {item['id']} {item['video_id']}", file=sys.stderr)
        if index + 1 < len(rows):
            time.sleep(1)

    print(f"完了: 成功 {success} / 失敗 {failed}")
    return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="対象とファイル情報だけを表示")
    mode.add_argument("--confirm", action="store_true", help="YouTube APIで実際に設定")
    args = parser.parse_args()

    if not args.dry_run and not args.confirm:
        parser.print_usage(sys.stderr)
        return 2

    rows = targets()
    if args.dry_run:
        return dry_run(rows)
    return confirm(rows)


if __name__ == "__main__":
    raise SystemExit(main())
