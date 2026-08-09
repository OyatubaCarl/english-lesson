"""WordTacos プロモ (wordtacos_promo_v2.mp4) を YouTube ショートとして
非公開アップロード → 指定時刻に自動公開 (publishAt)。

token.json (scope: youtube) を使用。yt_upload_wt_v1.py と同じ作法。
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

ROOT = Path(__file__).resolve().parent
PROJ = ROOT.parent
TOKEN = PROJ / "token.json"
VIDEO = ROOT / "wordtacos_promo_v2.mp4"
SCOPES = ["https://www.googleapis.com/auth/youtube"]

PUBLISH_JST = "2026-07-02T07:00:00+09:00"   # 木曜 朝7時に自動公開

TITLE = '日本語に英語を"埋め込む"英単語アプリ WordTacos🌮 #Shorts'

DESCRIPTION = """▶ WordTacos https://words.teachertacos.com ｜ 公式 https://teachertacos.com ｜ YouTube https://www.youtube.com/@TeacherTacosEnglish

日本語の文に英単語をそっと埋め込み、文脈ごとやさしく覚える単語アプリ「WordTacos」。
中学入門からTOEIC高得点まで、7000語をぜんぶ無料で。
昇級試験はゲーム「タコス厨房ラッシュ」──10連続正解で合格！🌮

🔗 いますぐ無料ではじめる → https://words.teachertacos.com

#英語学習 #英単語 #TOEIC #中学英語 #高校英語 #大学受験 #WordTacos #英語アプリ #Shorts"""

TAGS = ["英語学習", "英単語", "TOEIC", "中学英語", "高校英語",
        "大学受験", "WordTacos", "英語アプリ", "文脈", "Shorts"]


def publish_utc_z(jst_iso: str) -> str:
    return datetime.fromisoformat(jst_iso).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def auth():
    creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if not creds.valid and creds.refresh_token:
        creds.refresh(Request())
        TOKEN.write_text(creds.to_json())
        print("token refreshed")
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def main() -> None:
    assert VIDEO.is_file(), f"missing video: {VIDEO}"
    publish_at = publish_utc_z(PUBLISH_JST)
    body = {
        "snippet": {
            "title": TITLE,
            "description": DESCRIPTION,
            "tags": TAGS,
            "categoryId": "27",           # Education
            "defaultLanguage": "ja",
            "defaultAudioLanguage": "ja",
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": publish_at,       # この時刻に自動で public 化
            "selfDeclaredMadeForKids": False,
        },
    }
    yt = auth()
    media = MediaFileUpload(str(VIDEO), mimetype="video/mp4", resumable=True,
                            chunksize=8 * 1024 * 1024)
    size_mb = VIDEO.stat().st_size / 1024 / 1024
    print(f"uploading {VIDEO.name} ({size_mb:.1f} MB) → private, publishAt={publish_at} (07:00 JST 7/2)")
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = req.next_chunk()
        if status:
            print(f"  {int(status.progress() * 100)}%")
    vid = response["id"]
    url = f"https://www.youtube.com/shorts/{vid}"
    print(f"\n✓ uploaded  video_id={vid}")
    print(f"  Shorts URL (公開後): {url}")
    print(f"  Studio: https://studio.youtube.com/video/{vid}/edit")

    log = ROOT / "upload_result.json"
    log.write_text(json.dumps({
        "video_id": vid, "shorts_url": url,
        "publish_jst": PUBLISH_JST, "publish_utc": publish_at,
        "title": TITLE, "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  log -> {log.name}")


if __name__ == "__main__":
    main()
