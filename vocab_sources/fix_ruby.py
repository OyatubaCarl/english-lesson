#!/usr/bin/env python3
"""ステージJSONのふりがな(ruby)フィールドを高精度(fugashi)で再生成する。

pykakasi 由来の読み誤り(借入=しゃくにゅう 等)を一括修正する確立済み手順。
各 *_ruby は対応する素フィールドから再生成する:
    body_ruby         <- body            (文字列)
    alt_bodies_ruby   <- alt_bodies       (配列)
    choices_ruby      <- choices          (配列)
    explanation_ruby  <- explanation      (文字列)

使い方(必ず .venv の python で):
    PY=/Users/masaki/Documents/ClaudeCode/英語学習教材作成/.venv/bin/python
    cd /Users/masaki/Documents/ClaudeCode/英語学習教材作成/vocab_sources
    $PY fix_ruby.py stage_toeic_expert_quizzes_clean.json                 # body_ruby+alt_bodies_ruby を再生成
    $PY fix_ruby.py stage6_quizzes_clean.json --dry-run                   # 変化件数とサンプルだけ表示
    $PY fix_ruby.py stageX.json --fields body_ruby,alt_bodies_ruby,choices_ruby,explanation_ruby

反映(アプリ): 保存後に vocab_sources/deploy_wordtacos.sh を実行し、sw.js の CACHE を1つ上げる。
"""
from __future__ import annotations
import argparse
import json
import random
import shutil
from datetime import datetime
from pathlib import Path

from furigana_fugashi import to_aozora

# ruby フィールド -> 素フィールド, 配列か
FIELD_SRC = {
    "body_ruby": ("body", False),
    "alt_bodies_ruby": ("alt_bodies", True),
    "choices_ruby": ("choices", True),
    "explanation_ruby": ("explanation", False),
}
DEFAULT_FIELDS = ["body_ruby", "alt_bodies_ruby"]


def load_quizzes(path: Path):
    d = json.loads(path.read_text(encoding="utf-8"))
    qs = d if isinstance(d, list) else d["quizzes"]
    return d, qs


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("json", type=Path, help="ステージJSON (例: stage_toeic_expert_quizzes_clean.json)")
    ap.add_argument("--fields", default=",".join(DEFAULT_FIELDS),
                    help="再生成する ruby フィールド(カンマ区切り)。既定: " + ",".join(DEFAULT_FIELDS))
    ap.add_argument("--dry-run", action="store_true", help="保存せず、変化件数とサンプルだけ表示")
    args = ap.parse_args()

    fields = [f.strip() for f in args.fields.split(",") if f.strip()]
    for f in fields:
        if f not in FIELD_SRC:
            raise SystemExit(f"未対応フィールド: {f} (対応: {', '.join(FIELD_SRC)})")

    d, qs = load_quizzes(args.json)
    changes = []  # (field, word, old, new)
    counts = {f: 0 for f in fields}

    for q in qs:
        for rf in fields:
            src, is_list = FIELD_SRC[rf]
            if src not in q or not q[src]:
                continue
            if is_list:
                new = [to_aozora(s) for s in q[src]]
                old = q.get(rf) or []
                for i, nv in enumerate(new):
                    ov = old[i] if i < len(old) else None
                    if ov != nv:
                        changes.append((rf, q.get("word", "?"), ov, nv))
                if not args.dry_run:
                    q[rf] = new
                counts[rf] += len(new)
            else:
                new = to_aozora(q[src])
                if q.get(rf) != new:
                    changes.append((rf, q.get("word", "?"), q.get(rf), new))
                if not args.dry_run:
                    q[rf] = new
                counts[rf] += 1

    print(f"対象: {args.json.name} / クイズ {len(qs)}件")
    print("再生成フィールド:", ", ".join(f"{k}={v}" for k, v in counts.items()))
    print(f"変化した箇所: {len(changes)}")
    for rf, w, old, new in random.Random(3).sample(changes, min(12, len(changes))):
        print(f"  [{rf}] {w}")
        print(f"    旧: {old}")
        print(f"    新: {new}")

    if args.dry_run:
        print("\n(dry-run: 保存していません)")
        return

    bak = args.json.with_name(args.json.name + ".bak-ruby-" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    shutil.copy(args.json, bak)
    args.json.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    # 妥当性確認
    load_quizzes(args.json)
    print(f"\n✓ 保存しました (バックアップ: {bak.name})")
    print("  次: deploy_wordtacos.sh を実行し、sw.js の CACHE を1つ上げる")


if __name__ == "__main__":
    main()
