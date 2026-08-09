"""10クイズ動画を YouTube にまとめてアップロード (private + publishAt 予約)。

スケジュール:
  本日 16:00, 18:00, 20:00, 22:00 (4本)
  翌日 08:00, 10:00, 12:00, 14:00, 16:00, 18:00 (6本)
タイムゾーン: JST → UTC変換 (JST = UTC+9)

出力: shorts/uploaded_quizzes.json に {id, video_id, publish_at_utc, ...}
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

SITE = "https://english-lesson.gasflare.workers.dev/"
CH = "https://www.youtube.com/@TeacherTacosEnglish"

# JST = UTC+9
JST = timezone(timedelta(hours=9))


def jst(year, month, day, hour) -> datetime:
    return datetime(year, month, day, hour, 0, 0, tzinfo=JST)


# 開始日 = 今日 (UTCで判定すべきだがJSTで2026-06-08)
# 今日: 16,18,20,22。翌日(09): 08,10,12,14,16,18
def build_schedule():
    today = datetime.now(JST).date()
    tomorrow = today + timedelta(days=1)
    times = [
        jst(today.year, today.month, today.day, 16),
        jst(today.year, today.month, today.day, 18),
        jst(today.year, today.month, today.day, 20),
        jst(today.year, today.month, today.day, 22),
        jst(tomorrow.year, tomorrow.month, tomorrow.day, 8),
        jst(tomorrow.year, tomorrow.month, tomorrow.day, 10),
        jst(tomorrow.year, tomorrow.month, tomorrow.day, 12),
        jst(tomorrow.year, tomorrow.month, tomorrow.day, 14),
        jst(tomorrow.year, tomorrow.month, tomorrow.day, 16),
        jst(tomorrow.year, tomorrow.month, tomorrow.day, 18),
    ]
    # 既に過ぎている時刻は now+30min に押し出し
    now = datetime.now(JST)
    pushed = []
    for t in times:
        if t < now + timedelta(minutes=15):
            t = now + timedelta(minutes=20)
        pushed.append(t)
    # 最低5分間隔を保証
    for i in range(1, len(pushed)):
        if pushed[i] < pushed[i-1] + timedelta(minutes=5):
            pushed[i] = pushed[i-1] + timedelta(minutes=5)
    return pushed


def auth():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN.write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def make_body(quiz: dict, privacy: str, publish_at_iso: str | None) -> dict:
    word = quiz["word"]
    meaning = quiz["meaning_jp"]
    sentence = quiz.get("body_narration", "")
    title = f"これ読める? “{word}” 日本語混じり英単語クイズ #Shorts"
    description = f"""「{sentence}」

この英単語、意味わかる?
日本語の中に英単語を 1 つ混ぜるだけで、初見の単語でも文脈からほぼ意味が取れる。
これは「Diglot Weave(ダイグロット・ウィーブ)」と呼ばれる第二言語習得の手法です。

北海道大学 Mazur, Rzepka & Araki (2012) の実験では、
事前に単語を知らない子どもでも 約 80% が文脈から正しく当てました。

正解: {meaning}

──────────────
🔗 Teacher Tacos English
──────────────
🌐 {SITE}
▶️ {CH}

中高で習う英単語が、日本語混じりで全部学べます。

#英語学習 #英単語 #高校英語 #中学英語 #英語クイズ #{word} #Shorts
"""
    tags = [
        "英語学習", "英単語", "高校英語", "中学英語", "英語クイズ",
        word, "ルー語", "Diglot Weave", "日本語混じり",
        "Shorts", "Teacher Tacos English",
    ]
    snippet = {
        "title": title,
        "description": description,
        "tags": tags,
        "categoryId": "27",
        "defaultLanguage": "ja",
        "defaultAudioLanguage": "ja",
    }
    status = {
        "privacyStatus": privacy,
        "selfDeclaredMadeForKids": False,
    }
    if publish_at_iso:
        status["publishAt"] = publish_at_iso
    return {"snippet": snippet, "status": status}


def main():
    if "--dry-run" in sys.argv:
        schedule = build_schedule()
        for q, t in zip([q for q in QUIZZES if q["id"] != "01_ephemeral"], schedule):
            print(f"  {q['id']}  publishAt(JST) = {t.isoformat()}  -> UTC = "
                  f"{t.astimezone(timezone.utc).isoformat()}")
        return

    yt = auth()
    schedule = build_schedule()

    targets = [q for q in QUIZZES if q["id"] != "01_ephemeral"]
    if len(targets) != len(schedule):
        sys.exit(f"schedule mismatch: {len(targets)} targets vs {len(schedule)} slots")

    from googleapiclient.http import MediaFileUpload
    results = []
    for q, publish_at in zip(targets, schedule):
        qid = q["id"]
        video = PROJ / "shorts" / f"lou_quiz_short_v3_{qid}.mp4"
        if not video.exists():
            print(f"SKIP {qid}: {video} not found", file=sys.stderr)
            continue

        publish_iso_utc = publish_at.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        body = make_body(q, "private", publish_iso_utc)

        media = MediaFileUpload(
            str(video), mimetype="video/mp4", resumable=True,
            chunksize=8 * 1024 * 1024
        )
        size_mb = video.stat().st_size // 1024 // 1024
        print(f"[{qid}] Uploading ({size_mb} MB)  publishAt={publish_at.isoformat()} ...",
              flush=True)
        request = yt.videos().insert(part="snippet,status",
                                      body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"  {int(status.progress() * 100)}%", flush=True)
        vid = response["id"]
        print(f"  ✓ uploaded: {vid}")
        results.append({
            "id": qid,
            "video_id": vid,
            "publish_at_jst": publish_at.isoformat(),
            "publish_at_utc": publish_iso_utc,
            "shorts_url": f"https://www.youtube.com/shorts/{vid}",
            "word": q["word"],
        })

    out = PROJ / "shorts" / "uploaded_quizzes.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✅ {out}")
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
