"""50単語差し替え (12-21 と 62-101 を新難単語に)。
- 12-21: 旧 (gentle等) 削除 → 新 (abstruse等) 元のpublishAt継承で再アップ
- 62-101: 旧 (exciting等) 削除 → 新 (corroborate等) unlistedで再アップ
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

# 旧ID → 新ID マップ (連番一致)
ID_MAP = {
    "12_gentle": "12_abstruse",
    "13_nervous": "13_acrimonious",
    "14_huge": "14_assiduous",
    "15_silent": "15_austere",
    "16_delicious": "16_nonchalant",
    "17_disappear": "17_capricious",
    "18_whisper": "18_clandestine",
    "19_brave": "19_cogent",
    "20_lonely": "20_convivial",
    "21_honest": "21_copious",
    "62_exciting": "62_corroborate",
    "63_amazing": "63_cryptic",
    "64_terrible": "64_deferential",
    "65_weird": "65_demure",
    "66_lovely": "66_desultory",
    "67_ordinary": "67_didactic",
    "68_mysterious": "68_discerning",
    "69_complex": "69_disparate",
    "70_ancient": "70_dogmatic",
    "71_modern": "71_ebullient",
    "72_powerful": "72_effusive",
    "73_sudden": "73_esoteric",
    "74_perfect": "74_extol",
    "75_busy": "75_facetious",
    "76_tired": "76_fastidious",
    "77_comfortable": "77_furtive",
    "78_dangerous": "78_gregarious",
    "79_precious": "79_haughty",
    "80_different": "80_imperturbable",
    "81_clever": "81_incessant",
    "82_shy": "82_innocuous",
    "83_polite": "83_precarious",
    "84_patient": "84_intransigent",
    "85_excited": "85_jocular",
    "86_confused": "86_judicious",
    "87_surprised": "87_laconic",
    "88_friendly": "88_languid",
    "89_talkative": "89_magnanimous",
    "90_lazy": "90_mellifluous",
    "91_determined": "91_mercurial",
    "92_ambitious": "92_meticulous",
    "93_creative": "93_nebulous",
    "94_cheerful": "94_obfuscate",
    "95_peaceful": "95_obstinate",
    "96_fortunate": "96_opulent",
    "97_independent": "97_ostentatious",
    "98_responsible": "98_palpable",
    "99_cautious": "99_pedantic",
    "100_enormous": "100_perfunctory",
    "101_tiny": "101_prudent",
}


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
日本語の中に英単語を 1 つ混ぜるだけで、初見の単語でも文脈からほぼ意味が取れる。
これは「Diglot Weave(ダイグロット・ウィーブ)」と呼ばれる第二言語習得の手法です。

研究の根拠: {pcite}

正解: {meaning}

──────────────
🔗 Teacher Tacos English
──────────────
🌐 {SITE}
▶️ {CH}

中高〜大学受験で出る英単語が、日本語混じりで全部学べます。

#英語学習 #英単語 #高校英語 #英語クイズ #{word} #Shorts
"""
    status = {
        "privacyStatus": privacy,
        "selfDeclaredMadeForKids": False,
    }
    if publish_at_iso:
        status["publishAt"] = publish_at_iso
    return {
        "snippet": {
            "title": title,
            "description": description,
            "tags": ["英語学習", "英単語", "高校英語", "大学受験",
                     "英検準1級", word, "ルー語", "Diglot Weave",
                     "日本語混じり", "Shorts", "Teacher Tacos English"],
            "categoryId": "27",
            "defaultLanguage": "ja",
            "defaultAudioLanguage": "ja",
        },
        "status": status,
    }


def main():
    yt = auth()
    uploaded = json.loads(UPLOADED.read_text(encoding="utf-8"))
    keep = [e for e in uploaded if e["id"] not in ID_MAP.keys()]
    new_entries = []
    now = datetime.now(JST)

    from googleapiclient.http import MediaFileUpload

    for old_id, new_id in ID_MAP.items():
        old = next((e for e in uploaded if e["id"] == old_id), None)
        quiz = next((q for q in QUIZZES if q["id"] == new_id), None)
        if not quiz:
            print(f"SKIP {new_id}: not in quizzes.json", file=sys.stderr)
            continue
        video = PROJ / "shorts" / f"lou_quiz_short_v4_{new_id}.mp4"
        if not video.exists():
            print(f"SKIP {new_id}: {video} not found", file=sys.stderr)
            continue

        # 12-21 は publish_at 継承 (privateで予約)、62-101 は unlisted
        is_scheduled_range = new_id.startswith(("12_","13_","14_","15_","16_",
                                                  "17_","18_","19_","20_","21_"))
        publish_iso_utc = None
        publish_at_jst_str = None
        if is_scheduled_range and old and old.get("publish_at_jst"):
            pt = datetime.fromisoformat(old["publish_at_jst"])
            if pt < now + timedelta(minutes=15):
                pt = now + timedelta(minutes=20)
            publish_iso_utc = pt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
            publish_at_jst_str = pt.isoformat()
            privacy = "private"
        else:
            privacy = "unlisted"

        if old:
            print(f"[{new_id}] deleting old {old['video_id']} ({old_id})...", flush=True)
            try:
                yt.videos().delete(id=old["video_id"]).execute()
                print(f"  ✓ deleted")
            except Exception as e:
                print(f"  ✗ delete failed: {e}", file=sys.stderr)

        body = make_body(quiz, privacy, publish_iso_utc)
        media = MediaFileUpload(str(video), mimetype="video/mp4", resumable=True,
                                 chunksize=8 * 1024 * 1024)
        size_mb = video.stat().st_size // 1024 // 1024
        print(f"[{new_id}] uploading v4 ({size_mb} MB) {privacy}  publishAt={publish_at_jst_str}...", flush=True)
        request = yt.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"  {int(status.progress() * 100)}%", flush=True)
        new_vid = response["id"]
        print(f"  ✓ new: {new_vid}")

        new_entries.append({
            "id": new_id,
            "video_id": new_vid,
            "publish_at_jst": publish_at_jst_str,
            "publish_at_utc": publish_iso_utc,
            "shorts_url": f"https://www.youtube.com/shorts/{new_vid}",
            "word": quiz["word"],
            "privacy": privacy,
            "replaced_from": old["video_id"] if old else None,
            "replaced_from_id": old_id,
            "version": "v4-hard50",
        })

    out = keep + new_entries
    UPLOADED.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✅ {UPLOADED}")
    print(f"  scheduled (12-21): {sum(1 for n in new_entries if n['privacy']=='private')}")
    print(f"  unlisted (62-101): {sum(1 for n in new_entries if n['privacy']=='unlisted')}")


if __name__ == "__main__":
    main()
