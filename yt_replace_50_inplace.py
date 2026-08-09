"""煽り文句修正済の50本を差し替え (IDは変わらず、動画のみ更新)。
- 12-21: 既存publishAt継承 (private)
- 62-101: 1日3本 (朝7:30/昼13:00/夜22:00) を 6/17 22:00開始で予約
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

TARGET_IDS_12_21 = [
    "12_abstruse","13_acrimonious","14_assiduous","15_austere","16_nonchalant",
    "17_capricious","18_clandestine","19_cogent","20_convivial","21_copious",
]
TARGET_IDS_62_101 = [
    "62_corroborate","63_cryptic","64_deferential","65_demure","66_desultory",
    "67_didactic","68_discerning","69_disparate","70_dogmatic","71_ebullient",
    "72_effusive","73_esoteric","74_extol","75_facetious","76_fastidious",
    "77_furtive","78_gregarious","79_haughty","80_imperturbable","81_incessant",
    "82_innocuous","83_precarious","84_intransigent","85_jocular","86_judicious",
    "87_laconic","88_languid","89_magnanimous","90_mellifluous","91_mercurial",
    "92_meticulous","93_nebulous","94_obfuscate","95_obstinate","96_opulent",
    "97_ostentatious","98_palpable","99_pedantic","100_perfunctory","101_prudent",
]
ALL_TARGETS = TARGET_IDS_12_21 + TARGET_IDS_62_101


def build_62_101_schedule() -> list[datetime]:
    """6/17 22:00 から1本目、6/18 以降は朝7:30/昼13:00/夜22:00の3本/日。"""
    slots: list[datetime] = []
    day1 = datetime(2026, 6, 17, 22, 0, tzinfo=JST)
    slots.append(day1)
    # Day2 (6/18) 以降、朝7:30/昼13:00/夜22:00
    base = datetime(2026, 6, 17, 0, 0, tzinfo=JST)
    for i in range(1, 20):  # 余裕を持って20日分
        d = base + timedelta(days=i)
        for h, m in [(7, 30), (12, 30), (22, 0)]:
            slots.append(d.replace(hour=h, minute=m))
    return slots[:40]


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
    title = f"超 難単語が一発で覚えられる裏技! “{word}” 日本語混じり英単語クイズ #Shorts"
    pvar = quiz.get("paper_variant", {})
    pcite = pvar.get("cite", "Mazur, Rzepka & Araki, 2012")
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
    status = {"privacyStatus": privacy, "selfDeclaredMadeForKids": False}
    if publish_at_iso:
        status["publishAt"] = publish_at_iso
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
        "status": status,
    }


def main():
    yt = auth()
    uploaded = json.loads(UPLOADED.read_text(encoding="utf-8"))
    keep = [e for e in uploaded if e["id"] not in ALL_TARGETS]
    new_entries = []
    now = datetime.now(JST)
    schedule_62_101 = build_62_101_schedule()

    from googleapiclient.http import MediaFileUpload
    for qid in ALL_TARGETS:
        quiz = next((q for q in QUIZZES if q["id"] == qid), None)
        if not quiz:
            print(f"SKIP {qid}: not in quizzes.json", file=sys.stderr)
            continue
        video = PROJ / "shorts" / f"lou_quiz_short_v4_{qid}.mp4"
        if not video.exists():
            print(f"SKIP {qid}: {video} not found", file=sys.stderr)
            continue

        old = next((e for e in uploaded if e["id"] == qid), None)

        # publishAt 決定
        publish_iso_utc = None
        publish_at_jst_str = None
        if qid in TARGET_IDS_12_21:
            # 12-21 は元の publishAt 継承
            if old and old.get("publish_at_jst"):
                pt = datetime.fromisoformat(old["publish_at_jst"])
                if pt < now + timedelta(minutes=15):
                    pt = now + timedelta(minutes=20)
                publish_iso_utc = pt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
                publish_at_jst_str = pt.isoformat()
            privacy = "private"
        else:
            # 62-101 は新スケジュール
            idx = TARGET_IDS_62_101.index(qid)
            pt = schedule_62_101[idx]
            if pt < now + timedelta(minutes=15):
                pt = now + timedelta(minutes=20)
            publish_iso_utc = pt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
            publish_at_jst_str = pt.isoformat()
            privacy = "private"

        # 既存削除
        if old:
            print(f"[{qid}] deleting old {old['video_id']}...", flush=True)
            try:
                yt.videos().delete(id=old["video_id"]).execute()
                print(f"  ✓ deleted")
            except Exception as e:
                print(f"  ✗ delete failed: {e}", file=sys.stderr)

        body = make_body(quiz, privacy, publish_iso_utc)
        media = MediaFileUpload(str(video), mimetype="video/mp4", resumable=True,
                                 chunksize=8 * 1024 * 1024)
        size_mb = video.stat().st_size // 1024 // 1024
        print(f"[{qid}] uploading ({size_mb} MB) {privacy} publishAt={publish_at_jst_str}...", flush=True)
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
            "publish_at_jst": publish_at_jst_str,
            "publish_at_utc": publish_iso_utc,
            "shorts_url": f"https://www.youtube.com/shorts/{new_vid}",
            "word": quiz["word"],
            "privacy": privacy,
            "replaced_from": old["video_id"] if old else None,
            "version": "v4-tagline2",
        })

    out = keep + new_entries
    UPLOADED.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✅ {UPLOADED}")
    print(f"  12-21 (scheduled): {sum(1 for n in new_entries if n['id'] in TARGET_IDS_12_21)}")
    print(f"  62-101 (3/day scheduled): {sum(1 for n in new_entries if n['id'] in TARGET_IDS_62_101)}")


if __name__ == "__main__":
    main()
