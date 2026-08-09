"""チャンネル全体の動画統計を取得して、視聴数異常を検知する。

- token.json の youtube scope でアクセス
- チャンネルの直近動画リストと累計再生数を取得
- アップロード日時 vs 累計視聴数で1日あたりの「平均速度」を計算
- 最近の動画(48h内)、wt_v1新規20本、警告ステータスを確認
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import json

PROJ = Path(__file__).resolve().parent.parent
TOKEN = PROJ / "token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]


def auth():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN.write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def main() -> None:
    yt = auth()
    # First get channel info
    ch = yt.channels().list(part="snippet,statistics,status,contentDetails", mine=True).execute()
    info = ch["items"][0]
    print(f"=== Channel ===")
    print(f"  title: {info['snippet']['title']}")
    print(f"  customUrl: {info['snippet'].get('customUrl', '?')}")
    print(f"  stats: subs={info['statistics']['subscriberCount']} views={info['statistics']['viewCount']} videos={info['statistics']['videoCount']}")
    print(f"  status: {info.get('status', {})}")
    print()

    # Get uploads playlist
    uploads_pid = info["contentDetails"]["relatedPlaylists"]["uploads"] if "contentDetails" in info else None
    if not uploads_pid:
        # Need contentDetails part
        ch2 = yt.channels().list(part="contentDetails", mine=True).execute()
        uploads_pid = ch2["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    print(f"uploads playlist: {uploads_pid}")

    # Walk through uploads (max 50 at a time)
    video_ids = []
    next_token = None
    while True:
        req = yt.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=uploads_pid,
            maxResults=50,
            pageToken=next_token,
        )
        res = req.execute()
        for item in res.get("items", []):
            video_ids.append({
                "id": item["contentDetails"]["videoId"],
                "title": item["snippet"]["title"],
                "publishedAt": item["contentDetails"].get("videoPublishedAt", item["snippet"]["publishedAt"]),
            })
        next_token = res.get("nextPageToken")
        if not next_token or len(video_ids) >= 200:
            break

    print(f"total videos collected: {len(video_ids)}")
    print()

    # Get stats in batches of 50
    enriched = []
    now = datetime.now(timezone.utc)
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        ids = ",".join(v["id"] for v in batch)
        res = yt.videos().list(part="statistics,snippet,status", id=ids).execute()
        items = {it["id"]: it for it in res.get("items", [])}
        for v in batch:
            it = items.get(v["id"], {})
            st = it.get("statistics", {})
            sn = it.get("snippet", {})
            stat = it.get("status", {})
            try:
                pub = datetime.fromisoformat(v["publishedAt"].replace("Z", "+00:00"))
                age_days = max((now - pub).total_seconds() / 86400, 0.001)
            except Exception:
                age_days = 0
            views = int(st.get("viewCount", 0))
            enriched.append({
                "id": v["id"],
                "title": sn.get("title", v["title"])[:50],
                "publishedAt": v["publishedAt"],
                "ageDays": round(age_days, 1),
                "views": views,
                "viewsPerDay": round(views / age_days, 1) if age_days > 0 else 0,
                "likes": int(st.get("likeCount", 0)),
                "comments": int(st.get("commentCount", 0)),
                "privacy": stat.get("privacyStatus", "?"),
                "uploadStatus": stat.get("uploadStatus", "?"),
            })

    # Sort by recent
    enriched.sort(key=lambda r: r["publishedAt"], reverse=True)

    print("=== Recent 30 videos (newest first) ===")
    print(f"{'rank':>3} {'days':>6} {'views':>7} {'v/day':>7} {'likes':>5} {'comm':>4} {'priv':>9}  {'id':<12}  title")
    print("-" * 130)
    for i, r in enumerate(enriched[:30], 1):
        print(f"{i:>3} {r['ageDays']:>6} {r['views']:>7} {r['viewsPerDay']:>7} {r['likes']:>5} {r['comments']:>4} {r['privacy']:>9}  {r['id']:<12}  {r['title']}")

    # Summary
    print()
    print("=== Privacy breakdown ===")
    pc = {}
    for r in enriched:
        pc[r["privacy"]] = pc.get(r["privacy"], 0) + 1
    for k, v in pc.items():
        print(f"  {k}: {v}")

    # Today's views proxy: very young videos (<2 day) views
    very_young = [r for r in enriched if r["ageDays"] < 2 and r["privacy"] == "public"]
    print()
    print(f"=== Very young public videos (<2 days) ===")
    print(f"  count: {len(very_young)}")
    if very_young:
        total = sum(r["views"] for r in very_young)
        avg = total / len(very_young)
        print(f"  total views: {total}, avg per video: {avg:.1f}")

    # Output JSON
    out = PROJ / "shorts" / "_analytics" / f"channel_health_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out.write_text(json.dumps(enriched, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nfull data -> {out.name}")


if __name__ == "__main__":
    main()
