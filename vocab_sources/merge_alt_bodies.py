#!/usr/bin/env python3
"""サブエージェントが起草した alt_bodies(多重日本語埋め込み例文)を品質検証してステージJSONへ注入する。

各ステージ横展開で再利用する確立手順:
  1. ステージ語を N 語ずつ入力バッチにし、Claudeサブエージェントに2文ずつ起草させ th_out_*.json 等へ書かせる
  2. 本スクリプトで検証(埋め込み1回/長さ/報告調禁止/body重複/日本語有無)→合格分のみ採用
  3. --apply で alt_bodies を注入 → fix_ruby.py --fields alt_bodies_ruby でルビ生成 → 動作確認 → deploy

使い方:
  PY=.../.venv/bin/python
  $PY merge_alt_bodies.py <stage.json> "<out_glob>" [--apply] [--max 2]
    例: $PY merge_alt_bodies.py stage_toeic_high_quizzes_clean.json "$SC/th_out_*.json"
        $PY merge_alt_bodies.py stage_toeic_high_quizzes_clean.json "$SC/th_out_*.json" --apply
"""
from __future__ import annotations
import argparse, glob, json, re, shutil, sys
from datetime import datetime
from pathlib import Path

# 受け身・伝聞の報告調(単調)を弾く。文末限定。
BANNED_END = re.compile(r"(?:と(?:報告|指摘|説明|評価|確認|記録|判断|認識)|"
                        r"報告|指摘|評価|確認|記録)さ?れ(?:た|ている)。?$")
JP = re.compile(r"[぀-ゟ゠-ヿ一-鿿]")
TAG = re.compile(r"<[^>]+>")

def has_jp(s): return bool(JP.search(s))

def validate(sent, word, body):
    if not isinstance(sent, str) or not sent.strip():
        return "空"
    s = sent.strip()
    emb = f"<{word}>"
    tags = TAG.findall(s)
    if tags.count(emb) != 1:
        return f"埋め込み<{word}>が{tags.count(emb)}回"
    if len(tags) != 1:
        return f"余分なタグ {tags}"
    if not has_jp(s):
        return "日本語なし"
    L = len(s)
    if L < 12 or L > 70:
        return f"長さ{L}字(範囲外)"
    if BANNED_END.search(s):
        return "報告調の文末"
    if s == (body or "").strip():
        return "既存bodyと同一"
    return None  # OK

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("json", type=Path)
    ap.add_argument("out_glob")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--max", type=int, default=2, help="1語あたり採用する最大文数(既定2)")
    args = ap.parse_args()

    d = json.loads(args.json.read_text(encoding="utf-8"))
    qs = d if isinstance(d, list) else d["quizzes"]
    by_word = {q["word"]: q for q in qs}

    drafts = {}  # word -> [sent,...]
    files = sorted(glob.glob(args.out_glob))
    if not files:
        raise SystemExit(f"出力ファイルが見つからない: {args.out_glob}")
    for f in files:
        try:
            obj = json.loads(Path(f).read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  ! 読込失敗 {Path(f).name}: {e}"); continue
        if isinstance(obj, dict):
            for w, arr in obj.items():
                drafts.setdefault(w, [])
                if isinstance(arr, list):
                    drafts[w].extend(x for x in arr if isinstance(x, str))

    ok2 = ok1 = ok0 = missing = 0
    redo = []          # (word, reasons)
    fails = []         # (word, sent, reason)
    accepted = {}      # word -> [valid sents]
    for q in qs:
        w = q["word"]
        cands = drafts.get(w)
        if not cands:
            missing += 1; redo.append((w, ["起草なし"])); continue
        valid = []
        reasons = []
        for s in cands:
            r = validate(s, w, q.get("body", ""))
            if r is None:
                if s.strip() not in valid:
                    valid.append(s.strip())
            else:
                fails.append((w, s, r)); reasons.append(r)
        valid = valid[:args.max]
        accepted[w] = valid
        if len(valid) >= 2: ok2 += 1
        elif len(valid) == 1: ok1 += 1; redo.append((w, reasons or ["1文のみ"]))
        else: ok0 += 1; redo.append((w, reasons or ["有効文0"]))

    print(f"対象: {args.json.name} / {len(qs)}語 / 起草ファイル {len(files)}個")
    print(f"合格: 2文={ok2}  1文={ok1}  0文={ok0}  起草なし={missing}")
    print(f"不合格文: {len(fails)}")
    from collections import Counter
    rc = Counter(r for _, _, r in fails)
    for r, c in rc.most_common():
        print(f"   - {r}: {c}")
    if redo:
        print(f"\n要再起草({len(redo)}語):")
        print("  " + " ".join(w for w, _ in redo[:60]))
    # サンプル
    print("\n=== 合格サンプル ===")
    shown = 0
    for w, vs in accepted.items():
        if len(vs) >= 2 and shown < 6:
            print(f"  {w}: {vs[0]}  /  {vs[1]}"); shown += 1
    if fails:
        print("\n=== 不合格サンプル ===")
        for w, s, r in fails[:8]:
            print(f"  [{r}] {w}: {s}")

    if args.apply:
        n = 0
        for q in qs:
            vs = accepted.get(q["word"], [])
            if vs:
                q["alt_bodies"] = vs; n += 1
        bak = args.json.with_name(args.json.name + ".bak-alt-" + datetime.now().strftime("%Y%m%d_%H%M%S"))
        shutil.copy(args.json, bak)
        args.json.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n✓ {n}語に alt_bodies を注入・保存 (バックアップ {bak.name})")
        print("  次: fix_ruby.py --fields alt_bodies_ruby でルビ生成 → 動作確認 → deploy")
    else:
        print("\n(dry-run: --apply で注入)")

if __name__ == "__main__":
    main()
