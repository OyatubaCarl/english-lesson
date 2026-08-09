#!/usr/bin/env python3
"""WordTacos v2 一括ビルド（最上級＝TOEICエキスパート200語）。

vocab_sources/stage_toeic_expert_quizzes_clean.json（body=日本語混じり文に<word>埋め込み・4択・correct_index）を
v2形式に変換し、build_wordtacos_v2.py で動画化。アップローダ用に quizzes_expert.json も出力。
既にアップ済み(uploaded_quizzes.json)・既存mp4はスキップ（再開可能）。

usage:
    python3 build_v2_expert.py            # 全部
    python3 build_v2_expert.py 30         # 先頭30語だけ
"""
from __future__ import annotations
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPERT = ROOT.parent / "vocab_sources" / "stage_toeic_expert_quizzes_clean.json"
UPLOADED = ROOT / "uploaded_quizzes.json"
MANIFEST = ROOT / "quizzes_expert.json"   # アップローダ用（word/meaning_jp/body_narration/id）
WORK = ROOT / "_v2_expert"
WORK.mkdir(exist_ok=True)
TAG = "超・難単語クイズ"                    # 最上級なので難単語タグ


def load_expert() -> list[dict]:
    d = json.loads(EXPERT.read_text(encoding="utf-8"))
    return d.get("quizzes", d) if isinstance(d, dict) else d


def to_v2(q: dict) -> dict | None:
    word = q["word"]
    body = q.get("body", "")
    tok = f"<{word}>"
    if tok not in body:
        return None
    i = body.index(tok)
    prefix = body[:i]
    suffix = body[i + len(tok):]
    choices = q["choices"]
    ci = q["correct_index"]
    if len(choices) != 4 or not (0 <= ci < 4):
        return None
    return {
        "word": word, "prefix": prefix, "suffix": suffix,
        "choices": choices, "correct": ci,
        "meaning": q.get("meaning_jp") or choices[ci], "tag": TAG,
    }


def narration(v2: dict) -> str:
    return f"{v2['prefix']}{v2['word']}{v2['suffix']}"


def main() -> None:
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    done = {x.get("word") for x in json.loads(UPLOADED.read_text(encoding="utf-8"))}
    rows = load_expert()
    targets = []
    for idx, q in enumerate(rows, 1):
        w = q.get("word")
        if not w or w in done:
            continue
        v2 = to_v2(q)
        if v2 is None:
            continue
        targets.append((idx, q, v2))
    if limit:
        targets = targets[:limit]

    total = len(targets)
    print(f"=== エキスパート v2 一括ビルド: {total} 本 ===", flush=True)
    manifest = []
    built, skipped, failed = [], [], []
    for i, (idx, q, v2) in enumerate(targets, 1):
        word = v2["word"]
        wid = f"exp{idx:03d}_{word}"
        manifest.append({"id": wid, "word": word,
                         "meaning_jp": v2["meaning"], "body_narration": narration(v2)})
        out_mp4 = ROOT / f"wordtacos_v2_{word}.mp4"
        if out_mp4.exists() and out_mp4.stat().st_size > 100_000:
            print(f"[{i}/{total}] skip {word}", flush=True)
            skipped.append(word)
            continue
        qjson = WORK / f"{wid}.json"
        qjson.write_text(json.dumps(v2, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[{i}/{total}] build {word} …", flush=True)
        r = subprocess.run(["python3", str(ROOT / "build_wordtacos_v2.py"), str(qjson)],
                           capture_output=True, text=True)
        if r.returncode == 0 and out_mp4.exists():
            built.append(word)
            print(f"       ✓ {out_mp4.name}", flush=True)
        else:
            failed.append(word)
            print(f"       ✗ FAILED {word}\n{r.stdout[-300:]}\n{r.stderr[-300:]}", flush=True)
        time.sleep(0.4)

    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n=== 完了: 生成{len(built)} / スキップ{len(skipped)} / 失敗{len(failed)} / manifest {len(manifest)}語 ===", flush=True)
    if failed:
        print("失敗:", ", ".join(failed), flush=True)


if __name__ == "__main__":
    main()
