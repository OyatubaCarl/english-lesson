"""12-21 (easy) を v4 (intro+paper_variant) で差し替え。
旧12-21削除→新規アップ→元の publish_at_jst で再予約。
"""
from __future__ import annotations
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJ = Path(__file__).resolve().parent
TOKEN = PROJ / "token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]
QUIZZES = json.loads((PROJ / "shorts" / "quizzes.json").read_text(encoding="utf-8"))
UPLOADED = PROJ / "shorts" / "uploaded_quizzes.json"

SITE = "https://english-lesson.gasflare.workers.dev/"
CH = "https://www.youtube.com/@TeacherTacosEnglish"
JST = timezone(timedelta(hours=9))

TARGET_IDS = ["12_gentle", "13_nervous", "14_huge", "15_silent", "16_delicious",
              "17_disappear", "18_whisper", "19_brave", "20_lonely", "21_honest"]


def auth():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN.write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def make_body(quiz: dict, publish_at_iso: str | None) -> dict:
    word = quiz["word"]
    meaning = quiz["meaning_jp"]
    sentence = quiz.get("body_narration", "")
    title = f"知らない単語でも一発で覚える裏技! “{word}” 日本語混じり英単語クイズ #Shorts"
    pvar = quiz.get("paper_variant", {})
    pcite = pvar.get("cite", "偶発的 語彙 学習 研究")
    description = f"""【知らない単語でも一発で覚える裏技】

「{sentence}」

この英単語、意味わかる?
日本語の中に英単語を 1 つ混ぜるだけで、初見の単語でも文脈からスッと意味が取れる。
これは「Diglot Weave(ダイグロット・ウィーブ)」と呼ばれる第二言語習得の手法です。

研究の根拠: {pcite}

正解: {meaning}

──────────────
🔗 Teacher Tacos English
──────────────
🌐 {SITE}
▶️ {CH}

中高で習う英単語が、日本語混じりで全部学べます。

#英語学習 #英単語 #中学英語 #高校英語 #英語クイズ #{word} #Shorts
"""
    status = {
        "privacyStatus": "private",
        "selfDeclaredMadeForKids": False,
    }
    if publish_at_iso:
        status["publishAt"] = publish_at_iso
    return {
        "snippet": {
            "title": title,
            "description": description,
            "tags": ["英語学習", "英単語", "中学英語", "高校英語", "英語クイズ",
                     word, "ルー語", "Diglot Weave", "日本語混じり",
                     "Shorts", "Teacher Tacos English"],
            "categoryId": "27",
            "defaultLanguage": "ja",
            "defaultAudioLanguage": "ja",
        },
        "status": status,
    }


def main():
    yt = auth()
    uploaded = json.loads(UPLOADED.read_text(encoding="utf-8"))
    keep = [e for e in uploaded if e["id"] not in TARGET_IDS]
    new_entries = []
    now = datetime.now(JST)

    from googleapiclient.http import MediaFileUpload

    for q in QUIZZES:
        qid = q["id"]
        if qid not in TARGET_IDS:
            continue
        video = PROJ / "shorts" / f"lou_quiz_short_v4_{qid}.mp4"
        if not video.exists():
            print(f"SKIP {qid}: {video} not found", file=sys.stderr)
            continue

        old = next((e for e in uploaded if e["id"] == qid), None)
        publish_at_jst = old.get("publish_at_jst") if old else None
        publish_iso_utc = None
        if publish_at_jst:
            pt = datetime.fromisoformat(publish_at_jst)
            if pt < now + timedelta(minutes=15):
                pt = now + timedelta(minutes=20)
            publish_iso_utc = pt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
            publish_at_jst = pt.isoformat()

        if old:
            print(f"[{qid}] deleting old {old['video_id']}...", flush=True)
            try:
                yt.videos().delete(id=old["video_id"]).execute()
                print(f"  ✓ deleted")
            except Exception as e:
                print(f"  ✗ delete failed: {e}", file=sys.stderr)

        body = make_body(q, publish_iso_utc)
        media = MediaFileUpload(str(video), mimetype="video/mp4", resumable=True,
                                 chunksize=8 * 1024 * 1024)
        size_mb = video.stat().st_size // 1024 // 1024
        print(f"[{qid}] uploading v4 ({size_mb} MB)  publishAt={publish_at_jst}...", flush=True)
        request = yt.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"  {int(status.progress() * 100)}%", flush=True)
        new_vid = response["id"]
        print(f"  ✓ new: {new_vid}")

        new_entries.append({
            "id": qid,
            "video_id": new_vid,
            "publish_at_jst": publish_at_jst,
            "publish_at_utc": publish_iso_utc,
            "shorts_url": f"https://www.youtube.com/shorts/{new_vid}",
            "word": q["word"],
            "replaced_from_v3": old["video_id"] if old else None,
            "version": "v4",
        })

    out = keep + new_entries
    UPLOADED.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✅ {UPLOADED}")
    for n in new_entries:
        print(f"  {n['id']:<14} {n['video_id']:<13} publishAt={n['publish_at_jst']}")


if __name__ == "__main__":
    main()
