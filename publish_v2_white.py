#!/usr/bin/env python3
"""WordTacos v2（白地クイズカード版）Short の予約公開アップ。

v5（画像スタート）と併走させる白カード版。動画は shorts/wordtacos_v2_<word>.mp4（ビルド済み）。
X予約は v5 と同方針: 本文＝WordTacos本体と同じ日本語混じり文で出題、答えへは誘導せずコメントを誘発。
リンクは返信で WordTacos へ（収録ステージ名は実在するときだけ書く＝嘘をつかない）。

usage:
    python3 publish_v2_white.py --count 6 [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJ = Path(__file__).resolve().parent
SHORTS = PROJ / "shorts"
QUIZZES = json.loads((SHORTS / "quizzes.json").read_text(encoding="utf-8"))
UPLOADED_PATH = SHORTS / "uploaded_quizzes.json"
X_DIR = Path.home() / "workspace-local/Obsidian/MainVault/_AI-Workspace/_x-posts"
TOKEN = PROJ / "token.json"

JST = timezone(timedelta(hours=9), "JST")
SITE = "https://www.teachertacos.com"
CH = "https://www.youtube.com/@TeacherTacosEnglish"
VERSION = "v2-white10"
X_OFFSET_MIN = 15          # 公開の15分後にXへ


def uploaded() -> list[dict]:
    if UPLOADED_PATH.exists():
        return json.loads(UPLOADED_PATH.read_text(encoding="utf-8"))
    return []


def video_of(quiz: dict) -> Path:
    return SHORTS / f"wordtacos_v2_{quiz['word']}.mp4"


def candidates() -> list[dict]:
    done = {x.get("id") for x in uploaded()}
    done_words = {x.get("word") for x in uploaded()}
    out = []
    for q in QUIZZES:
        if q.get("version") != VERSION or q.get("id") in done or q.get("word") in done_words:
            continue
        mp4 = video_of(q)
        if mp4.exists() and mp4.stat().st_size > 100_000:
            out.append(q)
    return out


def default_start() -> datetime:
    """既存の（どの版の）予約とも衝突しない次の空き日。無ければ明日。"""
    today = datetime.now(JST).date()
    floor = datetime(today.year, today.month, today.day, 0, 0, tzinfo=JST) + timedelta(days=1)
    latest = None
    for u in uploaded():
        j = u.get("publish_at_jst")
        if not j:
            continue
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
📚 英単語クイズアプリ WordTacos → https://wordtacos.pages.dev/

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


_STAGE_CACHE: dict = {}
def stage_of_word(word: str) -> str:
    """WordTacos本体の収録ステージ名。見つからなければ空（ツイートに書かない＝嘘をつかない）。"""
    if not _STAGE_CACHE:
        import json as _json
        defs = [("stage1", None, None, "中1"), ("stage2", None, None, "中2"),
                ("stage3", None, None, "中3"), ("stage4", None, None, "中学発展"),
                ("stage5", 0, 1360, "高校入門"), ("stage5", 1360, 2720, "高校標準"),
                ("stage6", 0, 1197, "高校上級"), ("stage6", 1197, 2394, "高校発展"),
                ("stage_toeic_basic", None, None, "TOEIC 〜600"),
                ("stage_toeic_mid", None, None, "TOEIC 600〜790"),
                ("stage_toeic_high", None, None, "TOEIC 790〜860"),
                ("stage_toeic_expert", None, None, "TOEIC 860〜")]
        for st, a, b, name in defs:
            try:
                d = _json.loads((PROJ / "vocab_sources" / f"{st}_quizzes_clean.json").read_text(encoding="utf-8"))
                qs = d.get("quizzes") if isinstance(d, dict) else d
                if a is not None:
                    qs = qs[a:b]
                for q in qs:
                    w = str(q.get("word", "")).lower().strip()
                    if w and w not in _STAGE_CACHE:
                        _STAGE_CACHE[w] = name
            except Exception:
                pass
    return _STAGE_CACHE.get(word.lower(), "")


def x_entry(word: str, vid: str, x_dt: datetime, sentence: str = "", choices: list | None = None) -> str:
    """X予約: 本文は出題（日本語混じり文）+ 4択の選択肢 + 答え合わせの動画リンク。
    リンク（WordTacos本体）は返信に置く。"""
    question = sentence.strip() or f"「{word}」"
    stage = stage_of_word(word)
    labels = "ABCD"
    choice_lines = "".join(
        f"    {labels[i]} {''.join(str(c).split())}\n" for i, c in enumerate((choices or [])[:4])
    ) or "    A 〜\n"
    return (
        f"- id: v2w_{word}_{vid}\n"
        f"  scheduled: '{x_dt.isoformat()}'\n"
        f"  text: |-\n"
        f"    {question}\n"
        f"\n"
        f"    {word} の意味、どれ?\n"
        + choice_lines
        + f"\n"
        f"    答え合わせは動画で🎥\n"
        f"    https://www.youtube.com/shorts/{vid}\n"
        f"\n"
        f"    #英単語 #英語学習\n"
        f"  reply_text: |-\n"
        f"    日本語混じり文で覚える無料アプリ「WordTacos」で復習🌮\n"
        + (f"    この単語は「{stage}」ステージに収録されています\n" if stage else
           f"    中1〜TOEIC難単語まで、文脈で身につきます\n")
        + f"    https://wordtacos.pages.dev/\n"
        f"  media: []\n"
        f"  status: pending\n"
        f"  posted_at: null\n"
        f"  tweet_id: null\n"
        f"  error: null\n"
        f"  media_youtube_url: https://www.youtube.com/shorts/{vid}\n"
        f"  source: wordtacos_v2_white\n"
    )


def auth():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    creds = Credentials.from_authorized_user_file(str(TOKEN))
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
        start = default_start().replace(hour=hh, minute=mm)

    cands = candidates()[: args.count]
    if not cands:
        print(f"対象なし（{VERSION} で未アップかつmp4が存在する語がない）", file=sys.stderr)
        return

    print(f"=== v2白カード 予約公開アップ: {len(cands)}本 / 開始 {start.isoformat()} / 1日1本 ===")
    plan = []
    for i, q in enumerate(cands):
        pub = start + timedelta(days=i)
        plan.append((q, pub))
        print(f"  {q['word']:<18} publishAt(JST) {pub.isoformat()}")
    if args.dry_run:
        print("\n[dry-run] アップロードは行いません。")
        print("\n--- X予約プレビュー(1本目) ---")
        q0, pub0 = plan[0]
        print(x_entry(q0["word"], "DRYRUNVIDEO", pub0 + timedelta(minutes=X_OFFSET_MIN),
                      q0.get("body_narration", ""), q0.get("choices", [])))
        return

    yt = auth()
    from googleapiclient.http import MediaFileUpload
    results = uploaded()
    x_by_month: dict[str, list[str]] = {}
    for q, pub in plan:
        word = q["word"]
        video = video_of(q)
        pub_utc = pub.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        body = make_body(q, "private", pub_utc)
        media = MediaFileUpload(str(video), mimetype="video/mp4", resumable=True,
                                chunksize=8 * 1024 * 1024)
        print(f"[{word}] Uploading ({video.stat().st_size // 1024 // 1024}MB) "
              f"publishAt={pub.isoformat()} ...", flush=True)
        req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
        resp = None
        while resp is None:
            st, resp = req.next_chunk()
            if st:
                print(f"  {int(st.progress() * 100)}%", flush=True)
        vid = resp["id"]
        print(f"  ✓ {vid}")
        results.append({
            "id": q["id"], "video_id": vid,
            "publish_at_jst": pub.isoformat(), "publish_at_utc": pub_utc,
            "shorts_url": f"https://www.youtube.com/shorts/{vid}",
            "word": word, "privacy": "private->public(scheduled)", "version": VERSION,
        })
        UPLOADED_PATH.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        x_dt = pub + timedelta(minutes=X_OFFSET_MIN)
        x_by_month.setdefault(x_dt.strftime("%Y-%m"), []).append(
            x_entry(word, vid, x_dt, q.get("body_narration", ""), q.get("choices", [])))

    # X予約を月別yamlへ追記（x-scheduler の GitHub Actions が拾う）
    for ym, entries in x_by_month.items():
        path = X_DIR / f"{ym}.yaml"
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        prefix = "" if not existing or existing.endswith("\n") else "\n"
        with path.open("a", encoding="utf-8") as f:
            f.write(prefix + "".join(entries))
        print(f"X予約 追記: {path} ({len(entries)}件)")
    print("\n完了。X予約はVaultをcommit→pull --rebase→pushで反映してください。")


if __name__ == "__main__":
    main()
