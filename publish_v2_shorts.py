"""WordTacos v2 ショートの予約公開アップ + X予約ステージング。

- shorts/quizzes.json の未アップ語のうち wordtacos_v2_<word>.mp4 が存在するものを対象
- private + publishAt で予約公開（1日1本・JST固定時刻）
- shorts/uploaded_quizzes.json に【追記】（既存60本を上書きしない）
- X予約は shorts/x_posts_v2_staged.yaml に【追記】（同期修復後にmonth.yamlへマージ）

YouTube Data API はアップ1本=1600ユニット / 日次上限10000 → 実質最大6本/日。

usage:
  python3 publish_v2_shorts.py --dry-run                 # スケジュール確認のみ
  python3 publish_v2_shorts.py --count 6                 # 6本アップ（本番）
  python3 publish_v2_shorts.py --count 6 --start 2026-07-10 --time 19:00
"""
from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJ = Path(__file__).resolve().parent
SHORTS = PROJ / "shorts"
TOKEN = PROJ / "token.json"
# 出題元: エキスパート(最上級)が用意されていればそれを優先。無ければ従来の quizzes.json
_EXPERT = SHORTS / "quizzes_expert.json"
QUIZZES = json.loads((_EXPERT if _EXPERT.exists() else SHORTS / "quizzes.json").read_text(encoding="utf-8"))
UPLOADED_PATH = SHORTS / "uploaded_quizzes.json"
# X予約は MainVault の月次yamlへ直接追記（vault-autocommit が pull --rebase → push で同期）
X_DIR = Path.home() / "workspace-local/Obsidian/MainVault/_AI-Workspace/_x-posts"
SCOPES = ["https://www.googleapis.com/auth/youtube"]
SITE = "https://english-lesson.gasflare.workers.dev/"
CH = "https://www.youtube.com/@TeacherTacosEnglish"
JST = timezone(timedelta(hours=9))
X_OFFSET_MIN = 15  # YouTube公開後にX投稿


def quizzes_list() -> list[dict]:
    return QUIZZES if isinstance(QUIZZES, list) else QUIZZES.get("quizzes", QUIZZES)


def uploaded() -> list[dict]:
    if UPLOADED_PATH.exists():
        return json.loads(UPLOADED_PATH.read_text(encoding="utf-8"))
    return []


def candidates() -> list[dict]:
    done = {x.get("word") for x in uploaded()}
    out = []
    for q in quizzes_list():
        w = q.get("word")
        # 出題データが揃っているか（旧quizzes.json=body_subtitles / エキスパート=body_narration のどちらか）
        if w in done or not (q.get("body_subtitles") or q.get("body_narration")):
            continue
        mp4 = SHORTS / f"wordtacos_v2_{w}.mp4"
        if mp4.exists() and mp4.stat().st_size > 100_000:
            out.append(q)
    return out


def default_start() -> datetime:
    """既存のv2予約と衝突しない次の空き日。無ければ今日+1(JST)。"""
    today = datetime.now(JST).date()
    floor = datetime(today.year, today.month, today.day, 0, 0, tzinfo=JST) + timedelta(days=1)
    latest = None
    for u in uploaded():
        j = u.get("publish_at_jst")
        if u.get("version") == "v2" and j:
            dt = datetime.fromisoformat(j)
            if latest is None or dt > latest:
                latest = dt
    if latest is not None:
        nxt = latest.replace(hour=0, minute=0) + timedelta(days=1)
        return max(floor, nxt)
    return floor


def make_body(quiz: dict, privacy: str, publish_at_iso: str | None) -> dict:
    word = quiz["word"]
    meaning = quiz["meaning_jp"]
    sentence = quiz.get("body_narration", "")
    # v1で最も再生された勝ちパターン(ベネフィット訴求)に統一 — 「これ読める?」型は初速が出なかった
    title = f"超・難単語が一発で覚えられる裏技! “{word}” 日本語混じり英単語クイズ #Shorts"
    description = f"""【超・難単語が一発で覚えられる裏技】

「{sentence}」

この英単語、意味わかる?
日本語の中に英単語を 1 つ混ぜるだけで、初見の単語でも文脈からほぼ意味が取れる。
これは「Diglot Weave(ダイグロット・ウィーブ)」と呼ばれる第二言語習得の手法です。

正解: {meaning}

──────────────
🔗 Teacher Tacos English
──────────────
🌐 {SITE}
▶️ {CH}
📚 英単語クイズアプリ WordTacos → https://words.teachertacos.com

中高で習う英単語が、日本語混じりで全部学べます。

#英語学習 #英単語 #高校英語 #中学英語 #英語クイズ #{word} #Shorts
"""
    snippet = {
        "title": title,
        "description": description,
        "tags": ["英語学習", "英単語", "難単語", "TOEIC", "英語クイズ", "Diglot Weave", "ルー語",
                 word, "日本語混じり", "WordTacos", "Shorts", "Teacher Tacos English"],
        "categoryId": "27",
        "defaultLanguage": "ja",
        "defaultAudioLanguage": "ja",
    }
    status = {"privacyStatus": privacy, "selfDeclaredMadeForKids": False}
    if publish_at_iso:
        status["publishAt"] = publish_at_iso
    return {"snippet": snippet, "status": status}


def x_entry(word: str, vid: str, x_dt: datetime) -> str:
    url = f"https://www.youtube.com/shorts/{vid}"
    return (
        f"- id: v2_{word}_{vid}\n"
        f"  scheduled: '{x_dt.isoformat()}'\n"
        f"  text: |-\n"
        f"    「{word}」\n"
        f"    見た瞬間に意味言える?\n"
        f"\n"
        f"    意味とコツは動画で30秒\n"
        f"    → {url}\n"
        f"\n"
        f"    #英単語 #英語学習\n"
        f"  reply_text: null\n"
        f"  media: []\n"
        f"  status: pending\n"
        f"  posted_at: null\n"
        f"  tweet_id: null\n"
        f"  error: null\n"
        f"  media_youtube_url: {url}\n"
        f"  source: wordtacos_v2_batch\n"
    )


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
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=6, help="今回アップする本数(既定6=クォータ上限)")
    ap.add_argument("--start", type=str, default=None, help="公開開始日 YYYY-MM-DD (JST)")
    ap.add_argument("--time", type=str, default="19:00", help="公開時刻 HH:MM (JST)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    hh, mm = (int(x) for x in args.time.split(":"))
    if args.start:
        y, mo, d = (int(x) for x in args.start.split("-"))
        start = datetime(y, mo, d, hh, mm, tzinfo=JST)
    else:
        s = default_start()
        start = s.replace(hour=hh, minute=mm)

    cands = candidates()[: args.count]
    if not cands:
        print("対象なし（未アップかつmp4が存在する語がない）", file=sys.stderr)
        return

    print(f"=== 予約公開アップ: {len(cands)}本 / 開始 {start.isoformat()} / 1日1本 ===")
    plan = []
    for i, q in enumerate(cands):
        pub = start + timedelta(days=i)
        plan.append((q, pub))
        print(f"  {q['word']:<14} publishAt(JST) {pub.isoformat()}")
    if args.dry_run:
        print("\n[dry-run] アップロードは行いません。")
        return

    yt = auth()
    from googleapiclient.http import MediaFileUpload
    results = uploaded()  # 既存に追記
    x_by_month: dict[str, list[str]] = {}
    for q, pub in plan:
        word = q["word"]
        video = SHORTS / f"wordtacos_v2_{word}.mp4"
        pub_utc = pub.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        body = make_body(q, "private", pub_utc)
        media = MediaFileUpload(str(video), mimetype="video/mp4", resumable=True,
                                chunksize=8 * 1024 * 1024)
        print(f"[{word}] Uploading ({video.stat().st_size//1024//1024}MB) publishAt={pub.isoformat()} ...",
              flush=True)
        req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
        resp = None
        while resp is None:
            st, resp = req.next_chunk()
            if st:
                print(f"  {int(st.progress()*100)}%", flush=True)
        vid = resp["id"]
        print(f"  ✓ {vid}")
        results.append({
            "id": q["id"], "video_id": vid,
            "publish_at_jst": pub.isoformat(), "publish_at_utc": pub_utc,
            "shorts_url": f"https://www.youtube.com/shorts/{vid}",
            "word": word, "privacy": "private->public(scheduled)", "version": "v2",
        })
        UPLOADED_PATH.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        x_dt = pub + timedelta(minutes=X_OFFSET_MIN)
        x_by_month.setdefault(x_dt.strftime("%Y-%m"), []).append(x_entry(word, vid, x_dt))

    for month, lines in x_by_month.items():
        yml = X_DIR / f"{month}.yaml"
        prefix = "" if (yml.exists() and yml.read_text(encoding="utf-8").endswith("\n")) else "\n"
        with yml.open("a", encoding="utf-8") as f:
            f.write(prefix + "".join(lines))
        print(f"✅ X予約追記: {yml}（{len(lines)}件）")
    print(f"✅ uploaded_quizzes.json 追記完了（総 {len(results)} 本）")


if __name__ == "__main__":
    main()
