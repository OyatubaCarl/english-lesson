#!/usr/bin/env python3
"""WordTacos v2 一括ビルド — quizzes.json の未制作語を v2 動画に。

quizzes.json(body_narration/choices/correct_index) → v2形式(prefix/suffix/choices/correct/meaning/tag)
に変換し、build_wordtacos_v2.py で1本ずつ生成する。既に mp4 がある語はスキップ(再開可能)。

usage:
    python3 build_v2_batch.py            # 未制作を全部
    python3 build_v2_batch.py 7          # 先頭7語だけ
"""
from __future__ import annotations
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
QUIZZES = ROOT / "quizzes.json"
UPLOADED = ROOT / "uploaded_quizzes.json"
WORK = ROOT / "_v2_batch"
WORK.mkdir(exist_ok=True)
TAG = "英単語クイズ"  # 易〜中級混在のため中立見出し(超・難単語は既アップ60本の専用)


def to_v2(q: dict) -> dict:
    """quizzes.json エントリ → build_wordtacos_v2.py 入力形式。"""
    word = q["word"]
    narration = q["body_narration"]
    idx = narration.find(word)
    if idx < 0:
        raise ValueError(f"word '{word}' が body_narration に見つからない")
    prefix = narration[:idx].strip()
    suffix = narration[idx + len(word):].strip()
    correct = q["correct_index"]
    choices = [c.replace(" ", "") for c in q["choices"]]
    return {
        "word": word,
        "prefix": prefix,
        "suffix": suffix,
        "choices": choices,
        "correct": correct,
        "meaning": choices[correct],
        "tag": TAG,
    }


def remaining_quizzes() -> list[dict]:
    data = json.loads(QUIZZES.read_text(encoding="utf-8"))
    quizzes = data if isinstance(data, list) else data.get("quizzes", data)
    done = {x.get("word") for x in json.loads(UPLOADED.read_text(encoding="utf-8"))}
    return [q for q in quizzes if q.get("word") not in done and "body_subtitles" in q]


def main() -> None:
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    rem = remaining_quizzes()
    if limit:
        rem = rem[:limit]
    total = len(rem)
    print(f"=== v2 一括ビルド: {total} 本 ===", flush=True)
    built, skipped, failed = [], [], []
    for i, q in enumerate(rem, 1):
        word = q["word"]
        out_mp4 = ROOT / f"wordtacos_v2_{word}.mp4"
        if out_mp4.exists() and out_mp4.stat().st_size > 100_000:
            print(f"[{i}/{total}] skip {word} (既存)", flush=True)
            skipped.append(word)
            continue
        v2 = to_v2(q)
        qjson = WORK / f"{q['id']}.json"
        qjson.write_text(json.dumps(v2, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[{i}/{total}] build {word} …", flush=True)
        r = subprocess.run(
            ["python3", str(ROOT / "build_wordtacos_v2.py"), str(qjson)],
            capture_output=True, text=True,
        )
        if r.returncode == 0 and out_mp4.exists():
            built.append(word)
            print(f"       ✓ {out_mp4.name}", flush=True)
        else:
            failed.append(word)
            print(f"       ✗ FAILED {word}\n{r.stdout[-400:]}\n{r.stderr[-400:]}", flush=True)
        time.sleep(0.5)  # VoicePeak連続実行の安定化
    print(f"\n=== 完了: 生成{len(built)} / スキップ{len(skipped)} / 失敗{len(failed)} ===", flush=True)
    if failed:
        print("失敗:", ", ".join(failed), flush=True)


if __name__ == "__main__":
    main()
