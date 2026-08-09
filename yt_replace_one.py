"""指定の動画を削除して、新規動画を同じpublishAtでアップロード。
uploaded_quizzes.json も更新。

usage: python3 yt_replace_one.py <quiz_id>
  例: python3 yt_replace_one.py 02_resilient
"""
from __future__ import annotations
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJ = Path(__file__).resolve().parent
TOKEN = PROJ / "token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]
JST = timezone(timedelta(hours=9))

UPLOADED = PROJ / "shorts" / "uploaded_quizzes.json"
QUIZZES = json.loads((PROJ / "shorts" / "quizzes.json").read_text(encoding="utf-8"))

SITE = "https://english-lesson.gasflare.workers.dev/"
CH = "https://www.youtube.com/@TeacherTacosEnglish"


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

#英語学習 #英単語 #高校英語 #中学英語 #英語クイズ #{word} #Shorts
"""
    return {
        "snippet": {
            "title": title,
            "description": description,
            "tags": ["英語学習", "英単語", "高校英語", "中学英語", "英語クイズ",
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
    if len(sys.argv) < 2:
        sys.exit("usage: python3 yt_replace_one.py <quiz_id>")
    target_qid = sys.argv[1]

    uploaded = json.loads(UPLOADED.read_text(encoding="utf-8"))
    target = next((u for u in uploaded if u["id"] == target_qid), None)
    if not target:
        sys.exit(f"{target_qid} not found in uploaded_quizzes.json")
    old_vid = target["video_id"]
    old_publish_jst = datetime.fromisoformat(target["publish_at_jst"])
    quiz = next(q for q in QUIZZES if q["id"] == target_qid)

    # 新publishAt: 元時刻を保持。ただし今より15分以内ならnow+15minに延長。
    now = datetime.now(JST)
    new_publish_jst = old_publish_jst
    if new_publish_jst < now + timedelta(minutes=15):
        new_publish_jst = now + timedelta(minutes=15)
    publish_iso_utc = new_publish_jst.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

    yt = auth()

    # 既存削除
    print(f"Deleting old video: {old_vid}", flush=True)
    yt.videos().delete(id=old_vid).execute()
    print(f"  ✓ deleted", flush=True)

    # 新規アップ
    video = PROJ / "shorts" / f"lou_quiz_short_v3_{target_qid}.mp4"
    if not video.exists():
        sys.exit(f"missing {video}")

    from googleapiclient.http import MediaFileUpload
    body = make_body(quiz, publish_iso_utc)
    media = MediaFileUpload(str(video), mimetype="video/mp4", resumable=True,
                            chunksize=8 * 1024 * 1024)
    print(f"Uploading {video.name}  publishAt={new_publish_jst.isoformat()} ...", flush=True)
    request = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  {int(status.progress() * 100)}%", flush=True)
    new_vid = response["id"]
    print(f"  ✓ new: {new_vid}")

    # uploaded_quizzes.json 更新
    target["video_id"] = new_vid
    target["publish_at_jst"] = new_publish_jst.isoformat()
    target["publish_at_utc"] = publish_iso_utc
    target["shorts_url"] = f"https://www.youtube.com/shorts/{new_vid}"
    target["replaced_from"] = old_vid
    UPLOADED.write_text(json.dumps(uploaded, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✅ updated {UPLOADED}")
    print(f"  old: https://youtu.be/{old_vid} (DELETED)")
    print(f"  new: https://www.youtube.com/shorts/{new_vid}  publishAt={new_publish_jst.isoformat()}")


if __name__ == "__main__":
    main()
