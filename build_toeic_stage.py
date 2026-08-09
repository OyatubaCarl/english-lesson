"""TOEIC ステージ用の quizzes_clean.json を生成する。

CEFR-J レベルに基づくスコアバンド (ETS Can-Do Guide / CEFR-J 研究の loose correlation):

  - TOEIC 600  (CEFR A1〜A2-B1 transitional)  150 語
  - TOEIC 730  (CEFR B1.1〜B1.2)                340 語
  - TOEIC 860+ (CEFR B2.1〜)                    240 語

語彙の CEFR レベルは、既存の stage1〜6 (本プロジェクトの中1〜高校発展) に
どこに含まれるかから判定する:
  stage1/2 → A1, stage3 → A2, stage4 → A2-B1
  stage5 前半 (order≤1360) → B1.1, 後半 → B1.2
  stage6 前半 (order≤1197) → B2.1, 後半 → B2.2
  既存になし → unknown (上級バンドに集約)
"""
from __future__ import annotations

import csv
import json
import random
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VOCAB_CSV = ROOT / "toeic_vocab.csv"
SRC_DIR = ROOT / "vocab_sources"
OUT_BASIC = SRC_DIR / "stage_toeic_basic_quizzes_clean.json"
OUT_MID = SRC_DIR / "stage_toeic_mid_quizzes_clean.json"
OUT_HIGH = SRC_DIR / "stage_toeic_high_quizzes_clean.json"

# CEFR レベル -> 採用バンド ("basic" / "mid" / "high")
LEVEL_TO_BAND = {
    "A1":      "basic",
    "A2":      "basic",
    "A2-B1":   "basic",
    "B1.1":    "mid",
    "B1.2":    "mid",
    "B2.1":    "high",
    "B2.2":    "high",
    "C1":      "high",
    "unknown": "high",
}

# 各バンドの目標サイズ (10 の倍数、合計 730)
BAND_SIZE = {"basic": 150, "mid": 340, "high": 240}


def cefr_for(stage_num: int, order: int) -> str:
    if stage_num in (1, 2):
        return "A1"
    if stage_num == 3:
        return "A2"
    if stage_num == 4:
        return "A2-B1"
    if stage_num == 5:
        return "B1.1" if order <= 1360 else "B1.2"
    if stage_num == 6:
        return "B2.1" if order <= 1197 else "B2.2"
    return "unknown"


def load_toeic() -> list[dict]:
    rows = []
    with open(VOCAB_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({
                "no": int(r["no"]),
                "word": r["word"].strip(),
                "meaning_jp": r["meaning"].strip(),
            })
    rows.sort(key=lambda x: x["no"])
    return rows


def load_existing() -> dict[str, tuple[int, dict]]:
    """word(小文字) -> (stage_num, quiz_dict)"""
    table: dict[str, tuple[int, dict]] = {}
    for n in range(1, 7):
        p = SRC_DIR / f"stage{n}_quizzes_clean.json"
        if not p.is_file():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        for q in d.get("quizzes", []):
            w = (q.get("word") or "").strip().lower()
            if w and w not in table:
                table[w] = (n, q)
    return table


def make_stub_quiz(no: int, word: str, meaning_jp: str, distractor_pool: list[str]) -> dict:
    qid = f"toeic_{no:04d}"
    body = f"会議の資料に <{word}> という単語が出てきたら、「{meaning_jp}」を思い出そう。"
    distractors = random.sample([d for d in distractor_pool if d != meaning_jp], k=3)
    choices = [meaning_jp] + distractors
    random.shuffle(choices)
    correct_idx = choices.index(meaning_jp)
    return {
        "id": qid,
        "word": word,
        "meaning_jp": meaning_jp,
        "pos": "",
        "body": body,
        "choices": choices,
        "correct_index": correct_idx,
        "explanation": f"TOEIC 頻出語。「{meaning_jp}」の意味で覚えよう。",
        "body_ruby": body,
        "choices_ruby": list(choices),
        "explanation_ruby": f"TOEIC 頻出語《ひんしゅつご》。「{meaning_jp}」の意味《いみ》で覚《おぼ》えよう。",
        "body_kana": "",
        "order": 1,
        "source": "toeic_stub",
        "cefr": "unknown",
    }


def reuse_existing(no: int, existing_q: dict, cefr: str) -> dict:
    q = dict(existing_q)
    q["id"] = f"toeic_{no:04d}"
    q["source"] = "reused"
    q["cefr"] = cefr
    return q


def write_stage(path: Path, stage_id: str, items: list[dict], cefr_summary: str, score_range: str) -> None:
    for i, q in enumerate(items, 1):
        q["order"] = i
    data = {
        "stage": stage_id,
        "version": "toeic_v2_cefr",
        "count": len(items),
        "generated_at": datetime.now().isoformat(),
        "cefr_summary": cefr_summary,
        "toeic_score_target_approx": score_range,
        "quizzes": items,
        "sorted_by": "toeic_frequency_rank_within_band",
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  {path.name}: {len(items)} 語  ({cefr_summary}, TOEIC {score_range} 目安)")


def main() -> None:
    random.seed(42)
    toeic = load_toeic()
    existing = load_existing()
    distractor_pool = list({t["meaning_jp"] for t in toeic})

    # 各 TOEIC 語に CEFR レベルを付与
    by_band: dict[str, list[dict]] = {"basic": [], "mid": [], "high": []}
    for t in toeic:
        w = t["word"].lower()
        if w in existing:
            stage_n, exq = existing[w]
            cefr = cefr_for(stage_n, exq.get("order", 0))
            q = reuse_existing(t["no"], exq, cefr)
        else:
            cefr = "unknown"
            q = make_stub_quiz(t["no"], t["word"], t["meaning_jp"], distractor_pool)
        band = LEVEL_TO_BAND[cefr]
        # 元の単語の no を保持して後でソートに使う
        q["__no"] = t["no"]
        q["__cefr"] = cefr
        by_band[band].append(q)

    # 帯ごとに no 順 (頻出順) でソート
    for k in by_band:
        by_band[k].sort(key=lambda x: x["__no"])

    print(f"CEFR 分類後の語数:")
    print(f"  basic (A1-A2-B1初): {len(by_band['basic'])} 語  → 目標 {BAND_SIZE['basic']}")
    print(f"  mid (B1.1-B1.2):    {len(by_band['mid'])} 語  → 目標 {BAND_SIZE['mid']}")
    print(f"  high (B2.1+):       {len(by_band['high'])} 語  → 目標 {BAND_SIZE['high']}")

    # 目標サイズに調整 (多ければ末尾を切る、少なければ next band の頭を引いてくる)
    final: dict[str, list[dict]] = {}
    for band in ["basic", "mid", "high"]:
        target = BAND_SIZE[band]
        cur = by_band[band]
        if len(cur) >= target:
            final[band] = cur[:target]
        else:
            need = target - len(cur)
            # 次の帯から借りる (高→中→基)
            donors = {"basic": "mid", "mid": "high", "high": "basic"}
            donor = donors[band]
            donated = by_band[donor][:need]
            by_band[donor] = by_band[donor][need:]
            final[band] = cur + donated
            print(f"  ({band} に {donor} から {need} 語借りた)")

    # 各バンドを no 順でソート (借りた語を含めて頻出順に)
    for k in final:
        final[k].sort(key=lambda x: x["__no"])
        # __no, __cefr は出力 JSON にはいらない (cefr フィールドは別途 stage メタに残す)
        for q in final[k]:
            q.pop("__no", None)
            q.pop("__cefr", None)

    write_stage(OUT_BASIC, "stage_toeic_basic", final["basic"],
                "CEFR A1〜A2-B1 (中1〜中学発展)", "〜600")
    write_stage(OUT_MID, "stage_toeic_mid", final["mid"],
                "CEFR B1.1〜B1.2 (高校入門〜標準)", "600〜790")
    write_stage(OUT_HIGH, "stage_toeic_high", final["high"],
                "CEFR B2.1〜 (高校上級・発展)", "790〜")


if __name__ == "__main__":
    main()
