#!/usr/bin/env python3
"""Upload middle-school all-in-one videos and record their YouTube IDs."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "dist" / "middle-marathon" / "manifest.json"
RESULTS = ROOT / "dist" / "middle-marathon" / "youtube_upload_results.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]

SITE_URL = "https://english-lesson.gasflare.workers.dev/"
CHANNEL_URL = "https://www.youtube.com/@songandmixture"


def auth():
    from google.auth.transport.requests import Request
    from google.auth.exceptions import RefreshError
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    token = ROOT / "token.json"
    credentials = ROOT / "credentials.json"
    creds = Credentials.from_authorized_user_file(str(token), SCOPES) if token.exists() else None
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except RefreshError:
            creds = None
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(str(credentials), SCOPES)
        creds = flow.run_local_server(port=0)
        (ROOT / "token.json").write_text(creds.to_json(), encoding="utf-8")
    from googleapiclient.discovery import build

    return build("youtube", "v3", credentials=creds)


def load_json(path: Path, default: dict) -> dict:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_results(data: dict) -> None:
    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    RESULTS.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def video_url(video_id: str) -> str:
    return f"https://youtu.be/{video_id}"


def title_for(part: dict) -> str:
    return f"{part['title']}｜うたとミックス 中学英語"


def description_for(part: dict, uploaded: dict[str, dict]) -> str:
    lessons = f"L{part['start']}〜L{part['end']}"
    lines = [
        f"中学生編 {lessons} のレッスン動画を続けて見られる一気見版です。",
        "",
        f"📖 サイトで英文・日本語訳・発音・単語テストを見る: {SITE_URL}?book=middle&lesson={part['start']}",
        "",
        "▼ この動画に入っているレッスン",
    ]
    for item in part["items"]:
        lesson = item["lesson"]
        label = f"L{lesson}"
        if "_" in item["label"]:
            label += " 追加"
        lines.append(f"{label}: {video_url(item['video_id'])}")

    related = []
    for key in ("part1", "part2", "part3"):
        item = uploaded.get(key)
        if item and key != part["key"]:
            related.append(f"{item['title']}: {item['url']}")
    if related:
        lines += ["", "▼ 関連する一気見動画", *related]

    lines += [
        "",
        "▼ 使い方",
        "1. まず一気見で音とリズムを通して聞く",
        "2. サイトで英文と日本語訳を確認する",
        "3. 個別レッスン動画に戻って苦手なところだけ復習する",
        "",
        "▼ 生成AIについて（注意）",
        "このコンテンツは、英文・訳・解説・楽曲・映像の一部に生成AIを使っています。",
        "AIの特性上、人物の見た目が場面によって変わる、細部が不自然などの点があります。",
        "英語学習の補助としてお使いください。",
        "",
        f"学習サイトトップ: {SITE_URL}",
        f"チャンネル: {CHANNEL_URL}",
        "",
        "#英語学習 #中学英語 #英文法 #英語リスニング #一気見 #Suno #revidai",
    ]
    return "\n".join(lines)


def upload(yt, part: dict, title: str, description: str) -> str:
    from googleapiclient.http import MediaFileUpload

    video = Path(part["video"])
    if not video.exists():
        raise FileNotFoundError(video)

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": [
                "英語学習",
                "中学英語",
                "英文法",
                "英語リスニング",
                "一気見",
                "うたとミックス",
                "Suno",
                "revidai",
            ],
            "categoryId": "27",
            "defaultLanguage": "ja",
            "defaultAudioLanguage": "ja",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }
    media = MediaFileUpload(
        str(video),
        mimetype="video/mp4",
        resumable=True,
        chunksize=8 * 1024 * 1024,
    )
    request = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    print(f"Uploading {video.name} ({video.stat().st_size // 1024 // 1024} MB)...")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  {int(status.progress() * 100)}%")
    return response["id"]


def update_description(yt, video_id: str, title: str, description: str) -> None:
    cur = yt.videos().list(part="snippet", id=video_id).execute()
    if not cur["items"]:
        raise RuntimeError(f"video not found: {video_id}")
    snip = cur["items"][0]["snippet"]
    snip["title"] = title
    snip["description"] = description
    snip["categoryId"] = "27"
    yt.videos().update(part="snippet", body={"id": video_id, "snippet": snip}).execute()


def main() -> int:
    manifest = load_json(MANIFEST, {})
    if not manifest.get("parts"):
        raise RuntimeError(f"No parts found in {MANIFEST}")

    results = load_json(RESULTS, {"created_at": datetime.now(timezone.utc).isoformat(), "items": {}})
    uploaded = results.setdefault("items", {})
    yt = auth()

    for part in manifest["parts"]:
        key = part["key"]
        title = title_for(part)
        existing = uploaded.get(key)
        desc = description_for(part, uploaded)
        if existing and existing.get("video_id"):
            print(f"already uploaded: {key} {existing['url']}")
            update_description(yt, existing["video_id"], title, desc)
            existing["metadata_updated_at"] = datetime.now(timezone.utc).isoformat()
            existing["title"] = title
            save_results(results)
            continue

        video_id = upload(yt, part, title, desc)
        uploaded[key] = {
            "video_id": video_id,
            "url": video_url(video_id),
            "title": title,
            "video": part["video"],
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
        }
        save_results(results)
        print(f"Uploaded: {video_url(video_id)}")

    for part in manifest["parts"]:
        key = part["key"]
        item = uploaded[key]
        update_description(yt, item["video_id"], item["title"], description_for(part, uploaded))
        item["metadata_updated_at"] = datetime.now(timezone.utc).isoformat()
        save_results(results)

    print("")
    for key, item in uploaded.items():
        print(f"{key}: {item['url']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
