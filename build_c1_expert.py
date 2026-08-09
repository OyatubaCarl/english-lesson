"""WordTacos の最上位ステージ (TOEIC 860+ / CEFR C1) を生成する。

語彙の選定方針:
  - CEFR-J Wordlist の C1 帯
  - Academic Word List (Coxhead, 2000) を参考にした学術語彙
  - ETS TOEIC Score Descriptors の 860+ 帯に出現する典型的なビジネス・専門語
  - 既存 stage1〜6 と重複する語は除外 (既に他ステージで学習できるため)

各クイズの例文は、本プロジェクトの「日本語に英単語を埋め込む」方式 (Diglot Weave)
で機械生成。例文の品質は段階的にブラッシュアップする想定。

参考:
  - Coxhead, A. (2000). A new academic word list. TESOL Quarterly, 34(2)
  - 投野由紀夫編 (2013). CEFR-J Wordlist (東京外国語大学)
  - ETS (2015). TOEIC Listening & Reading Test Examinee Handbook
"""
from __future__ import annotations

import json
import random
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC_DIR = ROOT / "vocab_sources"
OUT = SRC_DIR / "stage_toeic_expert_quizzes_clean.json"


# 学術・ビジネス・上級語彙の curated list
# (CEFR C1帯 / TOEIC 860+ で扱われる頻度が高いもの)
# このリストは語彙集の複製ではなく、編者による独自選定。
C1_WORDS = [
    # --- 議論・論理 (academic discourse) ---
    ("hypothesize", "仮説を立てる"), ("postulate", "仮定する"),
    ("substantiate", "実証する"), ("corroborate", "裏付ける"),
    ("refute", "反論する"), ("rebut", "反証する"),
    ("contention", "主張、論点"), ("paradigm", "枠組み、模範"),
    ("premise", "前提"), ("rationale", "論理的根拠"),
    ("conjecture", "推測"), ("inference", "推論"),
    ("dialectic", "弁証法"), ("syllogism", "三段論法"),
    ("axiom", "公理"), ("tenet", "信条"),
    ("epistemology", "認識論"), ("heuristic", "発見的手法"),
    # --- 学術記述 ---
    ("delineate", "輪郭を描く、説明する"), ("elucidate", "解明する"),
    ("expound", "詳述する"), ("articulate", "明確に表現する"),
    ("constitute", "構成する"), ("encompass", "包含する"),
    ("comprise", "から成る"), ("entail", "必然的に伴う"),
    ("denote", "指し示す"), ("connote", "暗に意味する"),
    ("epitomize", "典型的に示す"), ("exemplify", "例示する"),
    ("paraphrase", "言い換える"), ("synthesize", "総合する"),
    ("juxtapose", "並置する"), ("dichotomy", "二分"),
    # --- 評価・批評 ---
    ("scrutinize", "精査する"),  # 既存にあれば除外される
    ("appraise", "評価する"), ("assess", "査定する"),
    ("ascertain", "確認する"), ("discern", "識別する"),
    ("deem", "とみなす"), ("construe", "解釈する"),
    ("perceive", "知覚する"), ("conjure", "思い起こさせる"),
    ("intuit", "直観でわかる"),
    # --- 程度・抽象 ---
    ("salient", "顕著な"), ("pivotal", "中枢的な"),
    ("seminal", "独創的な、根源的な"), ("paramount", "最高の"),
    ("preponderant", "優勢な"), ("predominant", "主要な"),
    ("integral", "不可欠な"), ("intrinsic", "本質的な"),
    ("inherent", "内在する"), ("germane", "適切な"),
    ("pertinent", "関連する"), ("ostensible", "表面上の"),
    ("tentative", "暫定の"), ("plausible", "もっともらしい"),
    ("dubious", "疑わしい"), ("equivocal", "曖昧な"),
    ("ambivalent", "相反する感情の"), ("nuanced", "ニュアンスのある"),
    # --- 否定的状態 ---
    ("detrimental", "有害な"), ("deleterious", "害のある"),
    ("pernicious", "じわじわと有害な"), ("inimical", "敵対的な"),
    ("noxious", "有毒な"), ("inadvertent", "不注意な"),
    ("erroneous", "誤った"), ("flawed", "欠陥のある"),
    ("untenable", "支持できない"), ("counterintuitive", "直感に反する"),
    ("paradoxical", "逆説的な"),
    # --- 強化・抑制 ---
    ("augment", "増す"), ("escalate", "段階的に増す"),
    ("amplify", "拡大する"), ("propagate", "広める"),
    ("perpetuate", "永続させる"), ("instigate", "扇動する"),
    ("catalyze", "促進する"), ("expedite", "促進する"),
    ("facilitate", "容易にする"), ("alleviate", "和らげる"),
    ("mitigate", "緩和する"), ("subdue", "鎮める"),
    ("curtail", "切り詰める"), ("attenuate", "薄める、和らげる"),
    ("forestall", "未然に防ぐ"), ("preclude", "妨げる"),
    ("impede", "妨げる"), ("obfuscate", "曖昧にする"),
    ("hinder", "妨げる"),
    # --- 制度・政策 ---
    ("mandate", "命じる、命令"), ("stipulate", "明記する"),
    ("ratify", "批准する"), ("nullify", "無効にする"),
    ("rescind", "撤回する"), ("repeal", "廃止する"),
    ("enact", "制定する"), ("promulgate", "公布する"),
    ("ordinance", "条令"), ("statute", "成文法"),
    ("provision", "条項"), ("clause", "条項、節"),
    ("compliance", "遵守"), ("infringement", "侵害"),
    ("prerogative", "特権"), ("jurisdiction", "管轄"),
    ("constituency", "選挙区、支持基盤"), ("franchise", "独占権、選挙権"),
    # --- 経営・組織 ---
    ("conglomerate", "複合企業"), ("subsidiary", "子会社"),
    ("affiliate", "関連会社"), ("merger", "合併"),
    ("acquisition", "買収"), ("divestiture", "事業売却"),
    ("liquidation", "清算"), ("solvency", "支払能力"),
    ("insolvent", "支払不能の"), ("creditor", "債権者"),
    ("debtor", "債務者"), ("collateral", "担保"),
    ("amortize", "(分割)償却する"), ("depreciate", "減価する"),
    ("appreciate", "価値が上がる"), ("dividend", "配当"),
    ("equity", "株式、純資産"), ("portfolio", "金融資産構成"),
    ("hedge", "リスク回避する"), ("leverage", "てこ入れする"),
    ("arbitrage", "裁定取引"), ("annuity", "年金"),
    ("escrow", "第三者預託"), ("covenant", "誓約、特約"),
    ("indemnify", "補償する"), ("warranty", "保証"),
    ("liability", "負債、責任"), ("fiduciary", "受託者の"),
    ("derivative", "派生商品"), ("commodity", "商品、原料"),
    ("inventory", "在庫"), ("backlog", "未処理分"),
    ("attrition", "(人員などの)漸減"),
    # --- 経済・市場 ---
    ("fiscal", "財政の"), ("monetary", "金融の"),
    ("stagnation", "停滞"), ("recession", "景気後退"),
    ("inflation", "インフレ"), ("deflation", "デフレ"),
    ("tariff", "関税"), ("subsidy", "補助金"),
    ("austerity", "緊縮"), ("affluence", "裕福"),
    ("disparity", "格差"), ("plummet", "急落する"),
    ("plunge", "急落する"), ("soar", "急上昇する"),
    ("hike", "値上げ"), ("downturn", "下降"),
    ("upturn", "上昇"), ("rebound", "反発する"),
    ("trough", "底"), ("apex", "頂点"),
    # --- 研究・データ ---
    ("empirical", "経験的な"), ("anecdotal", "逸話的な"),
    ("quantitative", "量的な"), ("qualitative", "質的な"),
    ("longitudinal", "縦断的な"), ("cohort", "集団、世代"),
    ("aggregate", "集計、総計"), ("metric", "指標"),
    ("benchmark", "基準"), ("threshold", "閾値、敷居"),
    ("disparate", "異質な"), ("homogeneous", "均質な"),
    ("heterogeneous", "異質な"), ("disparity", "相違"),
    ("variance", "分散"), ("correlation", "相関"),
    ("causation", "因果関係"), ("extrapolate", "外挿する"),
    ("interpolate", "補間する"), ("regression", "回帰、後退"),
    ("attribute", "(原因に)帰する"), ("ascribe", "(性質を)帰する"),
    # --- 抽象状態 ---
    ("trajectory", "軌道、進路"), ("paradigm", "範例、枠組み"),
    ("hierarchy", "階層"), ("topology", "位相、配置"),
    ("framework", "枠組み"), ("scaffold", "足場"),
    ("infrastructure", "基盤施設"), ("ecosystem", "生態系"),
    ("juncture", "局面"), ("milestone", "節目"),
    ("epoch", "時代"), ("paradigm shift", "パラダイム転換"),
    # --- 議論調整 ---
    ("contend", "強く主張する"), ("posit", "措定する"),
    ("concede", "認める"), ("relinquish", "放棄する"),
    ("acquiesce", "黙従する"), ("dissent", "異議"),
    ("consensus", "合意"), ("unanimous", "全会一致の"),
    ("polarized", "両極化した"), ("contentious", "議論を呼ぶ"),
    ("vehement", "激しい"), ("staunch", "確固たる"),
    ("equivocate", "言葉を濁す"), ("prevaricate", "ごまかす"),
    ("reconcile", "調和させる"), ("reciprocate", "報いる"),
    # --- 哲学・倫理 ---
    ("normative", "規範的な"), ("descriptive", "記述的な"),
    ("utilitarian", "功利主義の"), ("deontological", "義務論の"),
    ("axiomatic", "自明の"), ("teleological", "目的論の"),
    ("autonomy", "自律性"), ("sovereignty", "主権"),
    ("paternalism", "家父長的態度"), ("populism", "大衆迎合主義"),
    # --- 速度・規模 ---
    ("ubiquitous", "至る所にある"),  # 既存にあれば除外
    ("pervasive", "広く浸透した"), ("prevalent", "蔓延した"),
    ("rampant", "横行する"), ("scant", "ごくわずかの"),
    ("paltry", "わずかな"), ("copious", "豊富な"),
    ("voluminous", "大量の"), ("preeminent", "傑出した"),
    ("vestigial", "痕跡的な"), ("rudimentary", "未発達の"),
    ("nascent", "発生したばかりの"),
]


def make_quiz(no: int, word: str, meaning_jp: str, distractor_pool: list[str]) -> dict:
    qid = f"c1_{no:04d}"
    body = f"会議資料の脚注に <{word}> という表記が出てきた。意味は「{meaning_jp}」。"
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
        "explanation": f"アカデミック/上級ビジネス語彙 (CEFR C1帯)。「{meaning_jp}」の意味で使われる。",
        "body_ruby": body,
        "choices_ruby": list(choices),
        "explanation_ruby": body,
        "body_kana": "",
        "order": no,
    }


def load_existing_words() -> set[str]:
    s = set()
    for n in range(1, 7):
        p = SRC_DIR / f"stage{n}_quizzes_clean.json"
        if not p.is_file():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        for q in d.get("quizzes", []):
            w = (q.get("word") or "").strip().lower()
            if w:
                s.add(w)
    for s_name in ("basic", "mid", "high"):
        p = SRC_DIR / f"stage_toeic_{s_name}_quizzes_clean.json"
        if not p.is_file():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        for q in d.get("quizzes", []):
            w = (q.get("word") or "").strip().lower()
            if w:
                s.add(w)
    return s


def main() -> None:
    random.seed(7)
    existing = load_existing_words()

    # 重複除去 + 重複語の検出
    seen_in_c1 = set()
    unique = []
    for word, meaning in C1_WORDS:
        w = word.lower()
        if w in existing:
            print(f"  skip (existing): {word}")
            continue
        if w in seen_in_c1:
            print(f"  skip (dup in C1 list): {word}")
            continue
        seen_in_c1.add(w)
        unique.append((word, meaning))

    print(f"\n候補総数: {len(C1_WORDS)}")
    print(f"既存重複/内部重複除去後: {len(unique)} 語")

    # 10 の倍数に整える (末尾を切る)
    n_target = (len(unique) // 10) * 10
    if n_target == 0:
        print("ERROR: 10語未満になりました。リストを拡充してください。")
        return
    unique = unique[:n_target]
    print(f"10の倍数に切り詰め: {len(unique)} 語")

    distractor_pool = list({m for _, m in unique})
    quizzes = []
    for i, (word, meaning) in enumerate(unique, 1):
        quizzes.append(make_quiz(i, word, meaning, distractor_pool))

    data = {
        "stage": "stage_toeic_expert",
        "version": "c1_v1",
        "count": len(quizzes),
        "generated_at": datetime.now().isoformat(),
        "cefr_summary": "CEFR C1 (上級学術・ビジネス語彙)",
        "toeic_score_target_approx": "860〜",
        "sources": [
            "Coxhead, A. (2000). A new academic word list. TESOL Quarterly, 34(2). [methodology reference]",
            "投野由紀夫編 (2013). CEFR-J Wordlist (東京外国語大学) — level alignment",
            "ETS (2015). TOEIC Listening & Reading Test Examinee Handbook — score correlation",
        ],
        "curation_note": "上記出典を参考にしつつ、編者 (Teacher Tacos English) が選定。語彙集の verbatim な複製ではない。",
        "quizzes": quizzes,
        "sorted_by": "manual_curation_order",
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n→ {OUT.name}: {len(quizzes)} 語")


if __name__ == "__main__":
    main()
