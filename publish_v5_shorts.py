#!/usr/bin/env python3
"""WordTacos v5（長難単語・画像スタート=v4形式）Short の予約公開アップ。

- 対象: quizzes.json の version=='v5-long10' で未アップ、かつ shorts/lou_quiz_short_v4_<id>.mp4 が存在
- private + publishAt で予約公開（1日1本・JST 19:00）。既存のどの版の予約とも衝突しない次の日から
- X予約は新方針: **本文は答えへ誘導しない（コメント誘発）**・**リンクはWordTacosを返信に**
- YouTubeクォータ: アップ1本=1600 / 日1万 → 1回の実行は最大6本

usage:
    python3 publish_v5_shorts.py --count 6 [--dry-run]
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
VERSION = "v5-long10"
X_OFFSET_MIN = 15          # 公開の15分後にXへ


def uploaded() -> list[dict]:
    if UPLOADED_PATH.exists():
        return json.loads(UPLOADED_PATH.read_text(encoding="utf-8"))
    return []


def candidates() -> list[dict]:
    done = {x.get("id") for x in uploaded()}
    out = []
    for q in QUIZZES:
        if q.get("version") != VERSION or q.get("id") in done:
            continue
        mp4 = SHORTS / f"lou_quiz_short_v4_{q['id']}.mp4"
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
    # v1で最も再生された勝ちパターン（ベネフィット訴求）を踏襲
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
    """X予約:
    本文 = WordTacosの「日本語混じり文」を出題 + 4択の選択肢 + 答え合わせの動画リンク。
    返信 = WordTacos への誘導リンク（収録ステージも添える）
    """
    question = sentence.strip() or f"「{word}」"
    labels = "ABCD"
    choice_lines = "".join(
        f"    {labels[i]} {''.join(str(c).split())}\n" for i, c in enumerate((choices or [])[:4])
    ) or "    A 〜\n"
    return (
        f"- id: v5_{word}_{vid}\n"
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
        + (f"    この単語は「{stage_of_word(word)}」ステージに収録されています\n" if stage_of_word(word) else
           f"    中1〜TOEIC難単語まで、文脈で身につきます\n")
        + f"    https://wordtacos.pages.dev/\n"
        f"  media: []\n"
        f"  status: pending\n"
        f"  posted_at: null\n"
        f"  tweet_id: null\n"
        f"  error: null\n"
        f"  media_youtube_url: https://www.youtube.com/shorts/{vid}\n"
        f"  source: wordtacos_v5_long\n"
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
        print("対象なし（v5-long10 で未アップかつmp4が存在する語がない）", file=sys.stderr)
        return

    print(f"=== v5 予約公開アップ: {len(cands)}本 / 開始 {start.isoformat()} / 1日1本 ===")
    plan = []
    for i, q in enumerate(cands):
        pub = start + timedelta(days=i)
        plan.append((q, pub))
        print(f"  {q['word']:<18} publishAt(JST) {pub.isoformat()}")
    if args.dry_run:
        print("\n[dry-run] アップロードは行いません。")
        return

    yt = auth()
    from googleapiclient.http import MediaFileUpload
    results = uploaded()
    x_by_month: dict[str, list[str]] = {}
    for q, pub in plan:
        word = q["word"]
        video = SHORTS / f"lou_quiz_short_v4_{q['id']}.mp4"
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

    for month, lines in x_by_month.items():
        yml = X_DIR / f"{month}.yaml"
        prefix = "" if (yml.exists() and yml.read_text(encoding="utf-8").endswith("\n")) else "\n"
        with yml.open("a", encoding="utf-8") as f:
            f.write(prefix + "".join(lines))
        print(f"X予約 {len(lines)}件 → {yml.name}")

    print("\n完了。Vaultの autocommit(23:30) で GitHub に同期され、x-scheduler が拾います。")


if __name__ == "__main__":
    main()
