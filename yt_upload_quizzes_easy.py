"""12-21 (easy級) クイズShortを朝7:30/夜22:00 で5日連続予約アップ。

開始: 今日 22:00 JST (今日朝はもう過ぎているため夜から)
順序: gentle(22:00) → nervous(翌7:30) → huge(翌22:00) → ...

出力: shorts/uploaded_quizzes.json に追記 (既存02-11は保持)
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

TARGET_IDS = [
    "12_gentle", "13_nervous", "14_huge", "15_silent", "16_delicious",
    "17_disappear", "18_whisper", "19_brave", "20_lonely", "21_honest",
]


def build_schedule() -> list[datetime]:
    """今夜22:00から、朝7:30+夜22:00 を5日分=10スロット生成。
    既に過ぎているスロットは now+20min に押し出し。"""
    now = datetime.now(JST)
    today = now.date()
    slots: list[datetime] = []
    # Day 1: only 22:00 (今夜) - 12_gentle
    # Day 2-5: 7:30 + 22:00
    # Day 6: only 7:30 - 21_honest
    days = [today + timedelta(days=i) for i in range(6)]
    # Day1
    slots.append(datetime(days[0].year, days[0].month, days[0].day, 22, 0, 0, tzinfo=JST))
    # Days 2-5: 7:30 と 22:00
    for d in days[1:5]:
        slots.append(datetime(d.year, d.month, d.day, 7, 30, 0, tzinfo=JST))
        slots.append(datetime(d.year, d.month, d.day, 22, 0, 0, tzinfo=JST))
    # Day6: 7:30 のみ
    d = days[5]
    slots.append(datetime(d.year, d.month, d.day, 7, 30, 0, tzinfo=JST))

    assert len(slots) == 10
    # past slot は now+20min に押し出し
    pushed = []
    for t in slots:
        if t < now + timedelta(minutes=15):
            t = now + timedelta(minutes=20)
        pushed.append(t)
    # 最低10分間隔保証
    for i in range(1, len(pushed)):
        if pushed[i] < pushed[i-1] + timedelta(minutes=10):
            pushed[i] = pushed[i-1] + timedelta(minutes=10)
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


def make_body(quiz: dict, publish_at_iso: str) -> dict:
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

#英語学習 #英単語 #中学英語 #高校英語 #英語クイズ #{word} #Shorts
"""
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
        "status": {
            "privacyStatus": "private",
            "publishAt": publish_at_iso,
            "selfDeclaredMadeForKids": False,
        },
    }


def main():
    schedule = build_schedule()
    targets = [q for q in QUIZZES if q["id"] in TARGET_IDS]
    targets.sort(key=lambda q: TARGET_IDS.index(q["id"]))  # 順序保証

    if "--dry-run" in sys.argv:
        for q, t in zip(targets, schedule):
            print(f"  {q['id']:<13}  publishAt(JST) = {t.isoformat()}")
        return

    yt = auth()
    existing = json.loads(UPLOADED.read_text(encoding="utf-8")) if UPLOADED.exists() else []
    # 既存の同一idエントリは置換(重複防止)
    keep = [e for e in existing if e["id"] not in TARGET_IDS]
    new_entries = []

    from googleapiclient.http import MediaFileUpload
    for q, publish_at in zip(targets, schedule):
        qid = q["id"]
        video = PROJ / "shorts" / f"lou_quiz_short_v3_{qid}.mp4"
        if not video.exists():
            print(f"SKIP {qid}: {video} not found", file=sys.stderr)
            continue
        publish_iso_utc = publish_at.astimezone(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.000Z")
        body = make_body(q, publish_iso_utc)
        media = MediaFileUpload(str(video), mimetype="video/mp4", resumable=True,
                                 chunksize=8 * 1024 * 1024)
        print(f"[{qid}] Uploading  publishAt={publish_at.isoformat()} ...", flush=True)
        request = yt.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"  {int(status.progress() * 100)}%", flush=True)
        vid = response["id"]
        print(f"  ✓ {vid}")
        new_entries.append({
            "id": qid,
            "video_id": vid,
            "publish_at_jst": publish_at.isoformat(),
            "publish_at_utc": publish_iso_utc,
            "shorts_url": f"https://www.youtube.com/shorts/{vid}",
            "word": q["word"],
        })

    UPLOADED.write_text(
        json.dumps(keep + new_entries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✅ {UPLOADED}")
    print(json.dumps(new_entries, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
