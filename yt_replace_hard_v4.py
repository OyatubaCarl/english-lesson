"""02-11 を v4 (intro+paper_variant) で差し替え。
旧02-11削除→新規アップ。
02-05はpublic即公開、06-11はunlisted。
"""
from __future__ import annotations
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJ = Path(__file__).resolve().parent
TOKEN = PROJ / "token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]
QUIZZES = json.loads((PROJ / "shorts" / "quizzes.json").read_text(encoding="utf-8"))
UPLOADED = PROJ / "shorts" / "uploaded_quizzes.json"

SITE = "https://english-lesson.gasflare.workers.dev/"
CH = "https://www.youtube.com/@TeacherTacosEnglish"

# 02-05: public 即公開, 06-11: unlisted
PUBLIC_IDS = {"02_resilient", "03_ubiquitous", "04_scrutinize", "05_profound"}
UNLISTED_IDS = {"06_mundane", "07_fragile", "08_vivid",
                "09_inevitable", "10_tranquil", "11_diligent"}
TARGET_IDS = PUBLIC_IDS | UNLISTED_IDS


def auth():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN.write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def make_body(quiz: dict, privacy: str) -> dict:
    word = quiz["word"]
    meaning = quiz["meaning_jp"]
    sentence = quiz.get("body_narration", "")
    title = f"超 難単語が一発で覚えられる裏技! “{word}” 日本語混じり英単語クイズ #Shorts"
    pvar = quiz.get("paper_variant", {})
    pcite = pvar.get("cite", "Mazur, Rzepka & Araki, 2012")
    description = f"""【超 難単語が一発で覚えられる裏技】

「{sentence}」

この英単語、意味わかる?
日本語の中に英単語を 1 つ混ぜるだけで、初見の単語でも文脈からほぼ意味が取れる。
これは「Diglot Weave(ダイグロット・ウィーブ)」と呼ばれる第二言語習得の手法です。

研究の根拠: {pcite}

正解: {meaning}

──────────────
🔗 Teacher Tacos English
──────────────
🌐 {SITE}
▶️ {CH}

中高で習う英単語が、日本語混じりで全部学べます。

#英語学習 #英単語 #高校英語 #英語クイズ #{word} #Shorts
"""
    return {
        "snippet": {
            "title": title,
            "description": description,
            "tags": ["英語学習", "英単語", "高校英語", "英語クイズ",
                     word, "ルー語", "Diglot Weave", "日本語混じり",
                     "Shorts", "Teacher Tacos English"],
            "categoryId": "27",
            "defaultLanguage": "ja",
            "defaultAudioLanguage": "ja",
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }


def main():
    yt = auth()
    uploaded = json.loads(UPLOADED.read_text(encoding="utf-8"))
    keep = [e for e in uploaded if e["id"] not in TARGET_IDS]
    new_entries = []

    from googleapiclient.http import MediaFileUpload

    for q in QUIZZES:
        qid = q["id"]
        if qid not in TARGET_IDS:
            continue
        video = PROJ / "shorts" / f"lou_quiz_short_v4_{qid}.mp4"
        if not video.exists():
            print(f"SKIP {qid}: {video} not found", file=sys.stderr)
            continue

        # 旧動画ID を取得して削除
        old = next((e for e in uploaded if e["id"] == qid), None)
        if old:
            old_vid = old["video_id"]
            print(f"[{qid}] deleting old {old_vid}...", flush=True)
            try:
                yt.videos().delete(id=old_vid).execute()
                print(f"  ✓ deleted {old_vid}")
            except Exception as e:
                print(f"  ✗ delete failed: {e}", file=sys.stderr)

        privacy = "public" if qid in PUBLIC_IDS else "unlisted"
        body = make_body(q, privacy)
        media = MediaFileUpload(str(video), mimetype="video/mp4", resumable=True,
                                 chunksize=8 * 1024 * 1024)
        size_mb = video.stat().st_size // 1024 // 1024
        print(f"[{qid}] uploading v4 ({size_mb} MB) as {privacy}...", flush=True)
        request = yt.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"  {int(status.progress() * 100)}%", flush=True)
        new_vid = response["id"]
        print(f"  ✓ new: {new_vid}  ({privacy})")

        # uploaded_quizzes.json用 (publishAt は v4 ではクリア → 即公開 or unlisted)
        new_entries.append({
            "id": qid,
            "video_id": new_vid,
            "publish_at_jst": None,
            "publish_at_utc": None,
            "shorts_url": f"https://www.youtube.com/shorts/{new_vid}",
            "word": q["word"],
            "privacy": privacy,
            "replaced_from_v3": old["video_id"] if old else None,
            "version": "v4",
        })

    out = keep + new_entries
    UPLOADED.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✅ {UPLOADED}")
    for n in new_entries:
        print(f"  {n['id']:<14} {n['video_id']:<13} {n['privacy']}  {n['shorts_url']}")


if __name__ == "__main__":
    main()
