"""wt_v1 で投入した20本を削除する。

shorts/_analytics/wt_v1_uploads.json から video_id を読んで削除。
"""
from __future__ import annotations
from pathlib import Path
import json
import sys

PROJ = Path(__file__).resolve().parent.parent
TOKEN = PROJ / "token.json"
UPLOADS = PROJ / "shorts" / "_analytics" / "wt_v1_uploads.json"
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
    dry = "--dry-run" in sys.argv
    uploads = json.loads(UPLOADS.read_text(encoding="utf-8"))
    print(f"target deletions: {len(uploads)}")
    for k in sorted(uploads):
        u = uploads[k]
        print(f"  {k}: video_id={u['video_id']} url={u['shorts_url']}")

    if dry:
        print("DRY RUN")
        return

    yt = auth()
    results = []
    for k in sorted(uploads):
        u = uploads[k]
        vid = u["video_id"]
        try:
            yt.videos().delete(id=vid).execute()
            results.append({"id": k, "video_id": vid, "status": "deleted"})
            print(f"  ✓ deleted {k} ({vid})")
        except Exception as e:
            results.append({"id": k, "video_id": vid, "status": "error", "error": str(e)})
            print(f"  ✗ FAILED {k}: {e}", file=sys.stderr)

    # Record results
    log = PROJ / "shorts" / "_analytics" / "wt_v1_delete_log.json"
    log.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nlog -> {log.name}")
    ok = sum(1 for r in results if r["status"] == "deleted")
    print(f"deleted: {ok}/{len(results)}")


if __name__ == "__main__":
    main()
