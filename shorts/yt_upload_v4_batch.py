#!/usr/bin/env python3
"""v4-hard50 を redo_design.json に従って一括アップロード+予約+サムネ設定。

usage:
    python3 shorts/yt_upload_v4_batch.py
    python3 shorts/yt_upload_v4_batch.py --dry-run
    python3 shorts/yt_upload_v4_batch.py --only meticulous,nebulous
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

PROJ = Path(__file__).resolve().parent.parent
TOKEN = PROJ / "token.json"
SHORTS = PROJ / "shorts"
THUMB_DIR = SHORTS / "thumb_tools" / "thumbnails"
DEFAULT_DESIGN = SHORTS / "_analytics" / "redo_design.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]

# 旧予約。新規アップ成功後に削除する
OLD_RESERVED = {
    "meticulous": "nEEnWCFgscQ",
    "nebulous": "QMkxxFOk3FA",
}


@dataclass(frozen=True)
class Item:
    quiz_id: str
    word: str
    level: str
    title: str
    description: str
    tags: list[str]
    publish_jst: str
    video_path: Path
    thumb_path: Path

    @property
    def publish_utc_z(self) -> str:
        return (
            datetime.fromisoformat(self.publish_jst)
            .astimezone(timezone.utc)
            .strftime("%Y-%m-%dT%H:%M:%SZ")
        )


def auth():
    creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if not creds.valid and creds.refresh_token:
        creds.refresh(Request())
        TOKEN.write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def load_items(design_path: Path, filter_words: set[str] | None) -> list[Item]:
    design = json.loads(design_path.read_text(encoding="utf-8"))
    items: list[Item] = []
    for d in design:
        if filter_words and d["word"] not in filter_words:
            continue
        video = SHORTS / f"lou_quiz_short_v4_{d['id']}_thumbed.mp4"
        thumb = THUMB_DIR / f"{d['id']}.jpg"
        items.append(
            Item(
                quiz_id=d["id"],
                word=d["word"],
                level=d["level"],
                title=d["title"],
                description=d["description"],
                tags=d["tags"],
                publish_jst=d["publish_jst"],
                video_path=video,
                thumb_path=thumb,
            )
        )
    return items


def preflight(items: list[Item]) -> list[str]:
    problems: list[str] = []
    for it in items:
        if not it.video_path.is_file():
            problems.append(f"missing video: {it.video_path}")
        if not it.thumb_path.is_file():
            problems.append(f"missing thumb: {it.thumb_path}")
    return problems


def upload_one(yt, item: Item) -> dict:
    body = {
        "snippet": {
            "title": item.title,
            "description": item.description,
            "tags": item.tags,
            "categoryId": "27",
            "defaultLanguage": "ja",
            "defaultAudioLanguage": "ja",
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": item.publish_utc_z,
            "selfDeclaredMadeForKids": False,
        },
    }
    media = MediaFileUpload(
        str(item.video_path),
        mimetype="video/mp4",
        resumable=True,
        chunksize=8 * 1024 * 1024,
    )
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    size_mb = item.video_path.stat().st_size // 1024 // 1024
    print(f"  uploading {item.video_path.name} ({size_mb} MB) → private, publishAt={item.publish_utc_z}")
    response = None
    while response is None:
        status, response = req.next_chunk()
        if status:
            print(f"    {int(status.progress() * 100)}%")
    new_vid = response["id"]
    print(f"  new video_id={new_vid}")

    thumb_media = MediaFileUpload(str(item.thumb_path), mimetype="image/jpeg")
    yt.thumbnails().set(videoId=new_vid, media_body=thumb_media).execute()
    print(f"  thumbnail attached.")
    return {"video_id": new_vid, "shorts_url": f"https://www.youtube.com/shorts/{new_vid}"}


def update_uploaded_quizzes_json(results: list[dict]) -> None:
    path = SHORTS / "uploaded_quizzes.json"
    q = json.loads(path.read_text(encoding="utf-8"))
    by_id = {r["quiz_id"]: r for r in results if r.get("status") == "ok"}
    for entry in q:
        info = by_id.get(entry["id"])
        if not info:
            continue
        if entry.get("video_id"):
            entry["replaced_from_v4_v1"] = entry["video_id"]
        entry["video_id"] = info["new_video_id"]
        entry["privacy"] = "unlisted"  # private + publishAt → 視覚的にはunlistedで運用
        entry["publish_at_jst"] = info["publish_jst"]
        entry["publish_at_utc"] = info["publish_utc"]
        entry["version"] = "v4-redo-20260621"
        entry["deleted_at"] = None
    path.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"updated {path.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--only", help="カンマ区切り word（例: meticulous,nebulous）")
    parser.add_argument(
        "--design",
        type=Path,
        default=DEFAULT_DESIGN,
        help="設計JSON(デフォルト: redo_design.json)",
    )
    parser.add_argument(
        "--skip-old-delete",
        action="store_true",
        help="旧予約 meticulous/nebulous の削除をスキップ",
    )
    args = parser.parse_args()

    filter_words = set(w.strip() for w in args.only.split(",")) if args.only else None
    items = load_items(args.design, filter_words)
    print(f"items to process: {len(items)} (design: {args.design.name})")
    global LOG_OUT
    LOG_OUT = SHORTS / "_analytics" / f"redo_upload_log_{args.design.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    problems = preflight(items)
    if problems:
        print("PREFLIGHT ERRORS:", *problems, sep="\n  ")
        sys.exit(1)

    if args.dry_run:
        for it in items:
            print(f"  [DRY] {it.quiz_id} {it.word} → publishAt={it.publish_utc_z}")
            print(f"        title: {it.title}")
            print(f"        video: {it.video_path}")
            print(f"        thumb: {it.thumb_path}")
        return

    yt = auth()
    results: list[dict] = []
    for it in items:
        print(f"=== {it.quiz_id} ({it.word}) ===")
        try:
            r = upload_one(yt, it)
            results.append(
                {
                    "quiz_id": it.quiz_id,
                    "word": it.word,
                    "status": "ok",
                    "new_video_id": r["video_id"],
                    "shorts_url": r["shorts_url"],
                    "publish_jst": it.publish_jst,
                    "publish_utc": it.publish_utc_z,
                }
            )
        except HttpError as e:
            results.append(
                {"quiz_id": it.quiz_id, "word": it.word, "status": "error", "error": str(e)}
            )
            print(f"  ERROR: {e}", file=sys.stderr)

    # 旧予約削除（新規がOKのものだけ）
    deleted: list[str] = []
    if not args.skip_old_delete:
        ok_words = {r["word"] for r in results if r["status"] == "ok"}
        for w, old_vid in OLD_RESERVED.items():
            if w in ok_words:
                try:
                    yt.videos().delete(id=old_vid).execute()
                    deleted.append(old_vid)
                    print(f"deleted old reservation: {w} {old_vid}")
                except HttpError as e:
                    print(f"delete failed {w} {old_vid}: {e}", file=sys.stderr)

    LOG_OUT.parent.mkdir(parents=True, exist_ok=True)
    LOG_OUT.write_text(
        json.dumps(
            {"results": results, "deleted_old": deleted, "at": datetime.now().isoformat()},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"log saved: {LOG_OUT}")

    update_uploaded_quizzes_json(results)
    print()
    print("=== summary ===")
    ok = sum(1 for r in results if r["status"] == "ok")
    print(f"uploaded: {ok}/{len(results)}")
    print(f"deleted old reservations: {deleted}")


if __name__ == "__main__":
    main()
