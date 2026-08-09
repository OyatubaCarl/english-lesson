"""quota回復後の48本再アップ用スクリプト。

実行タイミング: 翌日 JST 09:00 以降 (YouTube API quota は UTC 00:00 = JST 09:00 でリセット)

スケジュール:
  12-21 (10本): 翌日(D+1) から 1日3本 (朝7:30/昼12:30/夜22:00) で6/11-6/14 朝
  94 (1本):     既存 62-101 スケジュール (6/28 22:00)
  62-91 (30本): 12-21完了後の枠から1日3本
  (92,93は処理済)
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
JST = timezone(timedelta(hours=9))

SITE = "https://english-lesson.gasflare.workers.dev/"
CH = "https://www.youtube.com/@TeacherTacosEnglish"

# 12-21 (10) を 6/11 7:30 から 1日3本
TARGET_12_21 = ["12_abstruse","13_acrimonious","14_assiduous","15_austere","16_nonchalant",
                "17_capricious","18_clandestine","19_cogent","20_convivial","21_copious"]
# 62-91 (30本) を 12-21 完了の次から (6/14 12:30 〜)
TARGET_62_91 = [f"{n}_{w}" for n, w in [
    (62,"corroborate"),(63,"cryptic"),(64,"deferential"),(65,"demure"),(66,"desultory"),
    (67,"didactic"),(68,"discerning"),(69,"disparate"),(70,"dogmatic"),(71,"ebullient"),
    (72,"effusive"),(73,"esoteric"),(74,"extol"),(75,"facetious"),(76,"fastidious"),
    (77,"furtive"),(78,"gregarious"),(79,"haughty"),(80,"imperturbable"),(81,"incessant"),
    (82,"innocuous"),(83,"precarious"),(84,"intransigent"),(85,"jocular"),(86,"judicious"),
    (87,"laconic"),(88,"languid"),(89,"magnanimous"),(90,"mellifluous"),(91,"mercurial"),
]]
TARGET_94 = "94_obfuscate"  # 単独で 6/28 22:00


def build_recovery_schedule() -> dict:
    """各IDに対する publishAt の JST datetime を返す。"""
    s = {}
    # 12-21: 6/11 7:30 開始、1日3本 (7:30, 12:30, 22:00)
    slots = []
    base = datetime(2026, 6, 11, 0, 0, tzinfo=JST)
    for day in range(4):  # 6/11 -> 6/14
        d = base + timedelta(days=day)
        for h, m in [(7, 30), (12, 30), (22, 0)]:
            slots.append(d.replace(hour=h, minute=m))
    for qid, slot in zip(TARGET_12_21, slots[:10]):
        s[qid] = slot

    # 62-91: 12-21完了の次から (slots[10:] = 6/14 12:30〜)
    slots2 = slots[10:]  # 6/14 12:30, 22:00
    base2 = datetime(2026, 6, 15, 0, 0, tzinfo=JST)
    for day in range(14):
        d = base2 + timedelta(days=day)
        for h, m in [(7, 30), (12, 30), (22, 0)]:
            slots2.append(d.replace(hour=h, minute=m))
    for qid, slot in zip(TARGET_62_91, slots2[:30]):
        s[qid] = slot

    # 94: 6/28 22:00 (62-101 schedule 24番目 = 単独で予約)
    s[TARGET_94] = datetime(2026, 6, 28, 22, 0, tzinfo=JST)
    return s


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
    pvar = quiz.get("paper_variant", {})
    pcite = pvar.get("cite", "Mazur, Rzepka & Araki, 2012")
    title = f"超 難単語が一発で覚えられる裏技! “{word}” 日本語混じり英単語クイズ #Shorts"
    description = f"""【超 難単語が一発で覚えられる裏技】

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

中高〜大学受験で出る英単語が、日本語混じりで全部学べます。

#英語学習 #英単語 #大学受験 #英語クイズ #{word} #Shorts
"""
    return {
        "snippet": {
            "title": title,
            "description": description,
            "tags": ["英語学習", "英単語", "大学受験", "英検準1級", "英検1級",
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
    if "--dry-run" in sys.argv:
        s = build_recovery_schedule()
        print("=== Recovery schedule ===")
        for qid, t in sorted(s.items(), key=lambda x: x[1]):
            print(f"  {qid:<18} {t.strftime('%m/%d %a %H:%M')}")
        return

    yt = auth()
    schedule = build_recovery_schedule()
    uploaded = json.loads(UPLOADED.read_text(encoding="utf-8"))
    now = datetime.now(JST)

    from googleapiclient.http import MediaFileUpload
    for qid, publish_at in schedule.items():
        e = next((x for x in uploaded if x["id"] == qid), None)
        if not e:
            print(f"SKIP {qid}: not in uploaded.json", file=sys.stderr)
            continue
        if e.get("status") != "deleted_pending_reupload":
            print(f"SKIP {qid}: status={e.get('status')}", file=sys.stderr)
            continue
        quiz = next((q for q in QUIZZES if q["id"] == qid), None)
        video = PROJ / "shorts" / f"lou_quiz_short_v4_{qid}.mp4"
        if not video.exists():
            print(f"SKIP {qid}: video file missing", file=sys.stderr)
            continue

        # 過去スロットは押し出し
        pt = publish_at if publish_at >= now + timedelta(minutes=15) else now + timedelta(minutes=20)
        publish_iso_utc = pt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

        body = make_body(quiz, publish_iso_utc)
        media = MediaFileUpload(str(video), mimetype="video/mp4", resumable=True,
                                 chunksize=8 * 1024 * 1024)
        print(f"[{qid}] uploading  publishAt={pt.isoformat()} ...", flush=True)
        try:
            request = yt.videos().insert(part="snippet,status", body=body, media_body=media)
            response = None
            while response is None:
                st, response = request.next_chunk()
            new_vid = response["id"]
        except Exception as ex:
            print(f"  ✗ {ex}", file=sys.stderr)
            UPLOADED.write_text(json.dumps(uploaded, ensure_ascii=False, indent=2),
                                 encoding="utf-8")
            break
        print(f"  ✓ new: {new_vid}")
        e["video_id"] = new_vid
        e["publish_at_jst"] = pt.isoformat()
        e["publish_at_utc"] = publish_iso_utc
        e["shorts_url"] = f"https://www.youtube.com/shorts/{new_vid}"
        e["status"] = "recovered"
        e["version"] = "v4-tagline2-recovered"
        UPLOADED.write_text(json.dumps(uploaded, ensure_ascii=False, indent=2),
                            encoding="utf-8")

    print("\n✅ recovery done")


if __name__ == "__main__":
    main()
