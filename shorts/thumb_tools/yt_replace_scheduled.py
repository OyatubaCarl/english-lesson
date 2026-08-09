#!/usr/bin/env python3
"""予約中(private + publishAt)のShortsを _thumbed.mp4 に差し替え、予約時刻を維持する。

手順:
  1. 既存video_idからsnippet/statusを取得し、title/description/tags/publishAtを保持
  2. videos().delete()で既存を削除
  3. _thumbed.mp4 を同じメタで再アップロード(privacy=private, publishAt=元時刻)
  4. uploaded_quizzes.json と manifest_thumbs.json の video_id を新IDに更新

usage:
    python3 yt_replace_scheduled.py --dry-run
    python3 yt_replace_scheduled.py --confirm
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SHORTS_DIR = BASE_DIR.parent
PROJ = SHORTS_DIR.parent
TOKEN = PROJ / "token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]

MANIFEST_PATH = BASE_DIR / "manifest_thumbs.json"
UPLOADED_PATH = SHORTS_DIR / "uploaded_quizzes.json"
THUMBNAILS_DIR = BASE_DIR / "thumbnails"


def auth():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN.write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def thumbnail_filename(item: dict) -> str:
    item_id = item["id"]
    word = item["word"]
    if item_id.lower().endswith(f"_{word.lower()}"):
        return f"{item_id}.jpg"
    return f"{item_id}_{word}.jpg"


def thumbed_video_path(item: dict) -> Path:
    return SHORTS_DIR / f"lou_quiz_short_v4_{item['id']}_thumbed.mp4"


def find_scheduled_targets() -> list[dict]:
    """YouTube側で privacyStatus='private' + publishAt 設定済みの A群動画を選別。
    uploaded_quizzes.json の privacy は古いことがあるため、YouTube APIで実状態を確認する。
    """
    uploaded = json.loads(UPLOADED_PATH.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    by_id = {m["id"]: m for m in manifest}

    candidates = []
    for entry in uploaded:
        if not entry.get("video_id"):
            continue
        if entry["id"] not in by_id:
            continue
        thumbed = thumbed_video_path(entry)
        if not thumbed.is_file():
            continue
        candidates.append((entry, by_id[entry["id"]], thumbed))

    if not candidates:
        return []

    youtube = auth()
    video_ids = [c[0]["video_id"] for c in candidates]
    statuses = {}
    for i in range(0, len(video_ids), 50):
        resp = youtube.videos().list(
            id=",".join(video_ids[i : i + 50]), part="status"
        ).execute()
        for it in resp.get("items", []):
            statuses[it["id"]] = it["status"]

    targets = []
    for entry, manifest_item, thumbed in candidates:
        status = statuses.get(entry["video_id"])
        if not status:
            continue
        if status.get("privacyStatus") != "private":
            continue
        if not status.get("publishAt"):
            continue
        targets.append({
            "id": entry["id"],
            "word": entry["word"],
            "video_id": entry["video_id"],
            "live_publish_at": status["publishAt"],
            "thumbed_video": thumbed,
            "thumbnail_jpg": THUMBNAILS_DIR / thumbnail_filename(manifest_item),
        })
    return targets


def fetch_meta(youtube, video_id: str) -> dict:
    resp = youtube.videos().list(
        id=video_id, part="snippet,status"
    ).execute()
    if not resp["items"]:
        raise SystemExit(f"video not found: {video_id}")
    item = resp["items"][0]
    return {
        "title": item["snippet"]["title"],
        "description": item["snippet"]["description"],
        "tags": item["snippet"].get("tags", []),
        "category_id": item["snippet"].get("categoryId", "27"),
        "default_language": item["snippet"].get("defaultLanguage", "ja"),
        "default_audio_language": item["snippet"].get("defaultAudioLanguage", "ja"),
        "publish_at": item["status"].get("publishAt"),
        "self_declared_made_for_kids": item["status"].get("selfDeclaredMadeForKids", False),
    }


def upload(youtube, video_path: Path, meta: dict) -> str:
    from googleapiclient.http import MediaFileUpload

    body = {
        "snippet": {
            "title": meta["title"],
            "description": meta["description"],
            "tags": meta["tags"],
            "categoryId": meta["category_id"],
            "defaultLanguage": meta["default_language"],
            "defaultAudioLanguage": meta["default_audio_language"],
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": meta["publish_at"],
            "selfDeclaredMadeForKids": meta["self_declared_made_for_kids"],
        },
    }
    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True, chunksize=4 * 1024 * 1024)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  upload {int(status.progress() * 100)}%")
    return response["id"]


def set_thumbnail(youtube, video_id: str, jpg_path: Path) -> None:
    from googleapiclient.http import MediaFileUpload

    youtube.thumbnails().set(
        videoId=video_id,
        media_body=MediaFileUpload(str(jpg_path), mimetype="image/jpeg"),
    ).execute()


def update_jsons(old_to_new: dict[str, str]) -> None:
    uploaded = json.loads(UPLOADED_PATH.read_text(encoding="utf-8"))
    changed = 0
    for entry in uploaded:
        if entry.get("video_id") in old_to_new:
            old = entry["video_id"]
            new = old_to_new[old]
            entry["video_id"] = new
            entry["shorts_url"] = f"https://www.youtube.com/shorts/{new}"
            entry["replaced_from_v4thumbed"] = old
            changed += 1
    UPLOADED_PATH.write_text(json.dumps(uploaded, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"  uploaded_quizzes.json: {changed} entries updated")

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    changed = 0
    for entry in manifest:
        if entry.get("video_id") in old_to_new:
            entry["video_id"] = old_to_new[entry["video_id"]]
            changed += 1
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"  manifest_thumbs.json: {changed} entries updated")


def dry_run(targets: list[dict]) -> None:
    print(f"--- dry-run: {len(targets)}件の差し替え予定 ---")
    for t in targets:
        size_mb = t["thumbed_video"].stat().st_size / 1024 / 1024
        print(
            f"  {t['id']:25s} word={t['word']:15s} video_id={t['video_id']:12s} "
            f"publish={t['live_publish_at']} thumbed={size_mb:.1f}MB"
        )


def confirm(targets: list[dict]) -> None:
    youtube = auth()
    old_to_new: dict[str, str] = {}
    fail = []
    for t in targets:
        print(f"\n=== {t['id']} {t['word']} (旧 {t['video_id']}) ===")
        try:
            meta = fetch_meta(youtube, t["video_id"])
            print(f"  メタ取得: title=「{meta['title'][:30]}…」 publishAt={meta['publish_at']}")
            print(f"  削除: {t['video_id']}")
            youtube.videos().delete(id=t["video_id"]).execute()
            time.sleep(2)
            print(f"  アップロード: {t['thumbed_video'].name}")
            new_id = upload(youtube, t["thumbed_video"], meta)
            print(f"  新video_id: {new_id}")
            time.sleep(2)
            print(f"  サムネAPI設定: {t['thumbnail_jpg'].name}")
            set_thumbnail(youtube, new_id, t["thumbnail_jpg"])
            old_to_new[t["video_id"]] = new_id
            print(f"  OK")
        except Exception as exc:
            print(f"  失敗: {type(exc).__name__}: {exc}", file=sys.stderr)
            fail.append((t["id"], str(exc)))
        time.sleep(3)

    if old_to_new:
        print(f"\n--- JSON更新 ---")
        update_jsons(old_to_new)

    print(f"\n完了: 成功 {len(old_to_new)} / 失敗 {len(fail)}")
    for fid, msg in fail:
        print(f"  失敗 {fid}: {msg}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--confirm", action="store_true")
    args = parser.parse_args()

    if not args.dry_run and not args.confirm:
        parser.print_usage(sys.stderr)
        return 2

    targets = find_scheduled_targets()
    if not targets:
        print("対象なし(privacy=unlisted + publish_at_jst + _thumbed.mp4 を満たすA群が見つかりません)")
        return 0

    if args.dry_run:
        dry_run(targets)
        return 0

    confirm(targets)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
