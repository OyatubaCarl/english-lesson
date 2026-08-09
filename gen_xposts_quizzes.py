"""アップロード済みクイズ動画から X(Twitter) 投稿テキストを10件生成。

入力: shorts/uploaded_quizzes.json (yt_upload_quizzes.py が出力)
出力:
  shorts/x_posts/quizzes_2026-06.yaml  (x-scheduler 用、Obsidian にも同期コピー)
  shorts/x_posts/quizzes_manual.md     (手動コピペ用)
"""
from __future__ import annotations
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJ = Path(__file__).resolve().parent
UPLOADED = PROJ / "shorts" / "uploaded_quizzes.json"
QUIZZES = json.loads((PROJ / "shorts" / "quizzes.json").read_text(encoding="utf-8"))

OUT_DIR = PROJ / "shorts" / "x_posts"
OUT_DIR.mkdir(exist_ok=True)

# Obsidian の x-scheduler 監視先
OBSIDIAN_YAML = Path(
    "/Users/masaki/workspace-local/Obsidian/MainVault/_AI-Workspace/_x-posts/2026-06.yaml"
)

SITE = "https://english-lesson.gasflare.workers.dev/"


def build_tweet(quiz: dict, video_id: str) -> str:
    word = quiz["word"]
    sentence = quiz.get("body_narration", "")
    choices = quiz.get("choices", [])
    # intro_overlay.header から動的にタイトル(裏技フレーズ)を取得
    intro_header = quiz.get("intro_overlay", {}).get("header", "")
    # 空白を詰めて末尾の "!" を外す
    title_text = intro_header.replace(" ", "").rstrip("!").rstrip("！")
    bracket_title = f"【{title_text}】" if title_text else "【日本語混じり英単語クイズ】"
    choices_line = "  ".join(
        f"{letter} {c.replace(' ', '')}" for letter, c in zip("ABCD", choices)
    )
    return f"""{bracket_title}

{sentence}

“{word}” の意味は?
{choices_line}

📺 答え→ https://youtube.com/shorts/{video_id}
🌐 {SITE}

#英語学習"""


def main():
    if not UPLOADED.exists():
        sys.exit(f"missing {UPLOADED}. Run yt_upload_quizzes.py first.")
    uploaded = json.loads(UPLOADED.read_text(encoding="utf-8"))
    qmap = {q["id"]: q for q in QUIZZES}

    yaml_entries = []
    md_lines = ["# クイズShort X投稿草稿 (手動コピペ用)\n"]

    skipped_no_schedule: list[str] = []
    for entry in uploaded:
        qid = entry["id"]
        vid = entry["video_id"]
        publish_jst = entry["publish_at_jst"]
        # YouTube 側でまだ公開予約が振られていないものは YAML に出さない
        # （poster.py の ISO 検証で落ちるため）
        if publish_jst in (None, "None"):
            skipped_no_schedule.append(qid)
            continue
        quiz = qmap[qid]
        tweet = build_tweet(quiz, vid)

        # YAML: x-scheduler想定フォーマット
        yaml_entries.append({
            "id": f"quiz_{qid}_{vid}",
            "scheduled": publish_jst,
            "status": "pending",
            "text": tweet,
            "media_youtube_url": entry["shorts_url"],
            "source": "lou_quiz_shorts_v3",
        })

        md_lines.append(f"## {qid} — {quiz['word']}  (公開 {publish_jst})")
        md_lines.append("```")
        md_lines.append(tweet)
        md_lines.append("```\n")
        chars = len(tweet)
        md_lines.append(f"  → 文字数: {chars}（X上限280、日本語は1文字=1カウント扱い）\n")

    # YAML出力
    yaml_path = OUT_DIR / "quizzes_2026-06.yaml"
    yaml_dump_simple(yaml_entries, yaml_path)
    print(f"✅ YAML -> {yaml_path}")

    # Obsidian 同期コピー
    if OBSIDIAN_YAML.parent.exists():
        OBSIDIAN_YAML.parent.mkdir(exist_ok=True)
        # 既存があれば追記、なければ新規
        if OBSIDIAN_YAML.exists():
            existing = OBSIDIAN_YAML.read_text(encoding="utf-8")
            with OBSIDIAN_YAML.open("a", encoding="utf-8") as f:
                f.write("\n\n# === ルー語クイズ Shorts 10本 (自動追記) ===\n")
                yaml_append_simple(yaml_entries, f)
            print(f"✅ Obsidian (append) -> {OBSIDIAN_YAML}")
        else:
            yaml_dump_simple(yaml_entries, OBSIDIAN_YAML)
            print(f"✅ Obsidian (new) -> {OBSIDIAN_YAML}")

    # MD出力
    md_path = OUT_DIR / "quizzes_manual.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"✅ MD   -> {md_path}")

    if skipped_no_schedule:
        print(
            f"⚠️  publish_at_jst 未設定でスキップ: {len(skipped_no_schedule)}件 "
            f"-> {', '.join(skipped_no_schedule[:5])}{'...' if len(skipped_no_schedule) > 5 else ''}"
        )


def yaml_dump_simple(entries: list[dict], path: Path):
    """PyYAML依存を避けて、x-schedulerの想定するシンプルなYAMLを書く。"""
    lines = []
    for e in entries:
        lines.append(f"- id: {e['id']}")
        lines.append(f"  scheduled: \"{e['scheduled']}\"")
        lines.append(f"  status: {e['status']}")
        text = e["text"].replace("\\", "\\\\").replace("\"", "\\\"")
        # block scalar (literal)
        lines.append("  text: |")
        for line in e["text"].splitlines():
            lines.append(f"    {line}")
        lines.append(f"  media_youtube_url: \"{e['media_youtube_url']}\"")
        lines.append(f"  source: {e['source']}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def yaml_append_simple(entries: list[dict], f):
    for e in entries:
        f.write(f"- id: {e['id']}\n")
        f.write(f"  scheduled: \"{e['scheduled']}\"\n")
        f.write(f"  status: {e['status']}\n")
        f.write("  text: |\n")
        for line in e["text"].splitlines():
            f.write(f"    {line}\n")
        f.write(f"  media_youtube_url: \"{e['media_youtube_url']}\"\n")
        f.write(f"  source: {e['source']}\n\n")


if __name__ == "__main__":
    main()
