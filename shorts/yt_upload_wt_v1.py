"""WordTacos 46.5秒 quiz短編 (wordtacos_quiz_short_v1_*) を一括YouTubeアップロード+予約。

設計: _analytics/wt_v1_design.json  (wt_v1_design.py で生成)
動画: shorts/wordtacos_quiz_short_v1_{id}.mp4
サムネ: shorts/wt_v1_thumbs/{id}.jpg

usage:
    python3 shorts/yt_upload_wt_v1.py --dry-run
    python3 shorts/yt_upload_wt_v1.py
    python3 shorts/yt_upload_wt_v1.py --only 02_resilient,03_ubiquitous

結果は shorts/_analytics/wt_v1_upload_log_YYYYmmdd_HHMMSS.json と
shorts/_analytics/wt_v1_uploads.json に書き出す。
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

ROOT = Path(__file__).resolve().parent
PROJ = ROOT.parent
TOKEN = PROJ / "token.json"
DESIGN = ROOT / "_analytics" / "wt_v1_design.json"
THUMB_DIR = ROOT / "wt_v1_thumbs"
UPLOADS_JSON = ROOT / "_analytics" / "wt_v1_uploads.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]


def auth():
    creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if not creds.valid and creds.refresh_token:
        creds.refresh(Request())
        TOKEN.write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def publish_utc_z(jst_str: str) -> str:
    return (
        datetime.fromisoformat(jst_str)
        .astimezone(timezone.utc)
        .strftime("%Y-%m-%dT%H:%M:%SZ")
    )


def preflight(items: list[dict]) -> list[str]:
    problems: list[str] = []
    for it in items:
        video = ROOT / f"wordtacos_quiz_short_v1_{it['id']}.mp4"
        thumb = THUMB_DIR / f"{it['id']}.jpg"
        if not video.is_file():
            problems.append(f"missing video: {video.name}")
        if not thumb.is_file():
            problems.append(f"missing thumb: {thumb.name}")
    return problems


def upload_one(yt, item: dict, unlisted: bool = False) -> dict:
    video = ROOT / f"wordtacos_quiz_short_v1_{item['id']}.mp4"
    thumb = THUMB_DIR / f"{item['id']}.jpg"
    if unlisted:
        status = {
            "privacyStatus": "unlisted",
            "selfDeclaredMadeForKids": False,
        }
    else:
        status = {
            "privacyStatus": "private",
            "publishAt": publish_utc_z(item["publish_jst"]),
            "selfDeclaredMadeForKids": False,
        }
    body = {
        "snippet": {
            "title": item["title"],
            "description": item["description"],
            "tags": item["tags"],
            "categoryId": "27",
            "defaultLanguage": "ja",
            "defaultAudioLanguage": "ja",
        },
        "status": status,
    }
    media = MediaFileUpload(
        str(video),
        mimetype="video/mp4",
        resumable=True,
        chunksize=8 * 1024 * 1024,
    )
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    size_mb = video.stat().st_size // 1024 // 1024
    mode = "unlisted" if unlisted else f"private, publishAt={publish_utc_z(item['publish_jst'])}"
    print(f"  uploading {video.name} ({size_mb} MB) → {mode}")
    response = None
    while response is None:
        status, response = req.next_chunk()
        if status:
            print(f"    {int(status.progress() * 100)}%")
    new_vid = response["id"]
    print(f"  new video_id={new_vid}")

    thumb_media = MediaFileUpload(str(thumb), mimetype="image/jpeg")
    yt.thumbnails().set(videoId=new_vid, media_body=thumb_media).execute()
    print(f"  thumbnail attached.")
    return {
        "video_id": new_vid,
        "shorts_url": f"https://www.youtube.com/shorts/{new_vid}",
    }


def load_uploads() -> dict:
    if UPLOADS_JSON.is_file():
        return json.loads(UPLOADS_JSON.read_text(encoding="utf-8"))
    return {}


def save_uploads(d: dict) -> None:
    UPLOADS_JSON.parent.mkdir(parents=True, exist_ok=True)
    UPLOADS_JSON.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--only", help="カンマ区切りid (例: 02_resilient,03_ubiquitous)")
    parser.add_argument("--unlisted", action="store_true",
                        help="予約公開ではなく限定公開(unlisted)でアップロードする")
    args = parser.parse_args()

    design = json.loads(DESIGN.read_text(encoding="utf-8"))
    if args.only:
        ids = set(s.strip() for s in args.only.split(","))
        design = [d for d in design if d["id"] in ids]
    print(f"items to process: {len(design)}")

    problems = preflight(design)
    if problems:
        print("PREFLIGHT ERRORS:", *problems, sep="\n  ")
        sys.exit(1)

    if args.dry_run:
        for it in design:
            print(f"  [DRY] {it['id']} {it['word']} → publishAt={publish_utc_z(it['publish_jst'])}")
            print(f"        title: {it['title']}")
            print(f"        desc head: {it['description'].splitlines()[0]}")
        return

    yt = auth()
    uploads = load_uploads()
    results: list[dict] = []
    for it in design:
        if it["id"] in uploads and uploads[it["id"]].get("video_id"):
            print(f"SKIP (already uploaded): {it['id']} -> {uploads[it['id']]['shorts_url']}")
            continue
        print(f"=== {it['id']} ({it['word']}) ===")
        try:
            r = upload_one(yt, it, unlisted=args.unlisted)
            entry = {
                "id": it["id"],
                "word": it["word"],
                "video_id": r["video_id"],
                "shorts_url": r["shorts_url"],
                "publish_jst": it["publish_jst"],
                "publish_utc": publish_utc_z(it["publish_jst"]),
                "title": it["title"],
                "uploaded_at": datetime.now(timezone.utc).isoformat(),
            }
            uploads[it["id"]] = entry
            save_uploads(uploads)
            results.append(entry)
        except HttpError as e:
            results.append({"id": it["id"], "word": it["word"], "status": "error", "error": str(e)})
            print(f"  ERROR: {e}", file=sys.stderr)

    log = ROOT / "_analytics" / f"wt_v1_upload_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    log.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"log -> {log.name}")
    print(f"total uploaded to wt_v1_uploads.json: {len([v for v in uploads.values() if v.get('video_id')])}")


if __name__ == "__main__":
    main()
