"""ルー語クイズShort 4本の再生数を取得して降順表示。"""
from __future__ import annotations
from pathlib import Path

PROJ = Path(__file__).resolve().parent
TOKEN = PROJ / "token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]

# (id, ラベル, builder, variant)
VIDEOS = [
    ("j2B_HuWjNoM", "v1 論文あり",   "v1", "default"),
    ("gAudVLTCX-g", "v1 論文なし",   "v1", "no-paper"),
    ("2S-hoFMdM2A", "v2 clean",     "v2", "clean"),
    ("OcVnRh7wQMI", "v2 intro",     "v2", "intro"),
]


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
    ids = ",".join(v[0] for v in VIDEOS)
    res = yt.videos().list(part="statistics,snippet", id=ids).execute()
    stats = {item["id"]: item for item in res.get("items", [])}

    rows = []
    for vid, label, builder, variant in VIDEOS:
        item = stats.get(vid, {})
        st = item.get("statistics", {})
        views = int(st.get("viewCount", 0))
        likes = int(st.get("likeCount", 0))
        comments = int(st.get("commentCount", 0))
        published = item.get("snippet", {}).get("publishedAt", "?")
        rows.append((views, likes, comments, vid, label, builder, variant, published))

    rows.sort(key=lambda r: -r[0])
    print(f"{'rank':>4}  {'views':>6}  {'likes':>5}  {'comm':>4}  {'id':<12}  {'label':<14}  builder/variant")
    print("-" * 90)
    for i, (v, lk, cm, vid, lb, br, va, pub) in enumerate(rows, 1):
        print(f"{i:>4}  {v:>6}  {lk:>5}  {cm:>4}  {vid:<12}  {lb:<14}  {br}/{va}")
    print()
    top = rows[0]
    print(f"TOP -> {top[3]} ({top[4]})  builder={top[5]}  variant={top[6]}  views={top[0]}")


if __name__ == "__main__":
    main()
