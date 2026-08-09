"""WordTacos ルビ・日本語監査スクリプト.

stage5_quizzes_clean.json のルビ誤読を検出し、
stage6_batch_01-08.json の body 内容問題を抽出する。

検出パターン:
1. 連用形音便誤読: 漢字《音読み》+活用語尾
2. 熟語の文字分割: 漢字《ルビ》漢字《ルビ》の連続
3. OVERRIDES漏れ: add_furigana.pyの既存OVERRIDES外で頻出する誤読

出力: furigana_audit_report.md
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Iterable

# ---------------------------------------------------------------------------
# パス設定

ROOT = Path("/Users/masaki/Documents/ClaudeCode/英語学習教材作成/vocab_sources")
STAGE5 = ROOT / "stage5_quizzes_clean.json"
STAGE6_DRAFT = ROOT / "stage6_quizzes_draft.json"
STAGE6_FILES = sorted(ROOT.glob("stage6_batch_*.json"))
ADD_FURIGANA = ROOT / "add_furigana.py"
REPORT = ROOT / "furigana_audit_report.md"

# ---------------------------------------------------------------------------
# 訓読み/音読み参考データ
# 「動詞活用形+音読みっぽいルビ」を見つけるため、よく見る誤読パターンを表で持つ

# 「漢字: 動詞語幹として使うときの正しい訓読み(送り仮名直前まで)」
# キーに無い漢字は OVERRIDES に登録されているとみなす(あるいは音読みでも正しい場合がある)
VERB_KUN: dict[str, list[str]] = {
    "乗": ["の"],
    "降": ["お", "ふ"],
    "通": ["とお", "かよ"],
    "走": ["はし"],
    "歩": ["ある"],
    "上": ["あ", "のぼ"],
    "下": ["お", "くだ", "さ"],
    "出": ["で", "だ"],
    "入": ["はい", "い"],
    "見": ["み"],
    "聞": ["き"],
    "話": ["はな"],
    "読": ["よ"],
    "書": ["か"],
    "言": ["い"],
    "行": ["い", "おこな", "ゆ"],
    "来": ["き", "く"],
    "帰": ["かえ"],
    "戻": ["もど"],
    "始": ["はじ"],
    "終": ["お"],
    "止": ["と", "や"],
    "立": ["た"],
    "座": ["すわ"],
    "寝": ["ね"],
    "起": ["お"],
    "食": ["た"],
    "飲": ["の"],
    "買": ["か"],
    "売": ["う"],
    "作": ["つく"],
    "使": ["つか"],
    "持": ["も"],
    "取": ["と"],
    "渡": ["わた"],
    "押": ["お"],
    "引": ["ひ"],
    "切": ["き"],
    "貼": ["は"],
    "貸": ["か"],
    "借": ["か"],
    "開": ["あ", "ひら"],
    "閉": ["し", "と"],
    "知": ["し"],
    "思": ["おも"],
    "考": ["かんが"],
    "覚": ["おぼ", "さ"],
    "忘": ["わす"],
    "感": ["かん"],  # 「感じる」=かんじる(音読み)
    "信": ["しん"],  # 「信じる」=しんじる(音読み)
    "愛": ["あい"],  # 「愛する」=あいする
    "決": ["き"],
    "選": ["えら"],
    "助": ["たす"],
    "守": ["まも"],
    "戦": ["たたか"],
    "勝": ["か"],
    "負": ["ま"],
    "笑": ["わら"],
    "泣": ["な"],
    "怒": ["おこ", "いか"],
    "喜": ["よろこ"],
    "驚": ["おどろ"],
    "悲": ["かな"],
    "楽": ["たの"],
    "嬉": ["うれ"],
    "怖": ["こわ"],
    "急": ["いそ"],
    "遅": ["おく", "おそ"],
    "早": ["はや"],
    "速": ["はや"],
    "強": ["つよ"],
    "弱": ["よわ"],
    "深": ["ふか"],
    "浅": ["あさ"],
    "高": ["たか"],
    "低": ["ひく"],
    "重": ["おも"],
    "軽": ["かる"],
    "新": ["あたら"],
    "古": ["ふる"],
    "若": ["わか"],
    "大": ["おお"],
    "暑": ["あつ"],
    "寒": ["さむ"],
    "暖": ["あたた"],
    "涼": ["すず"],
    "明": ["あか"],
    "暗": ["くら"],
    "白": ["しろ"],
    "黒": ["くろ"],
    "赤": ["あか"],
    "青": ["あお"],
    "汚": ["きたな", "よご"],
    "美": ["うつく"],
    "醜": ["みにく"],
    "甘": ["あま"],
    "辛": ["から", "つら"],
    "苦": ["くる", "にが"],
    "酸": ["す"],
    "塩": ["しお"],
    "丸": ["まる"],
    "細": ["ほそ", "こま"],
    "太": ["ふと"],
    "短": ["みじか"],
    "長": ["なが"],
    "広": ["ひろ"],
    "狭": ["せま", "せば"],
    "近": ["ちか"],
    "遠": ["とお"],
    "易": ["やさ"],
    "難": ["むずか"],
    "優": ["やさ"],
    "厳": ["きび"],
    "怪": ["あや"],
    "甚": ["はなはだ"],
    "珍": ["めずら"],
    "羨": ["うらや"],
    "恋": ["こい"],
    "祈": ["いの"],
    "願": ["ねが"],
    "頼": ["たの"],
    "誘": ["さそ"],
    "招": ["まね"],
    "迎": ["むか"],
    "送": ["おく"],
    "返": ["かえ"],
    "答": ["こた"],
    "尋": ["たず"],
    "問": ["と"],
    "求": ["もと"],
    "探": ["さが"],
    "見つ": ["みつ"],
    "拾": ["ひろ"],
    "落": ["お"],
    "捨": ["す"],
    "残": ["のこ"],
    "増": ["ふ"],
    "減": ["へ"],
    "加": ["くわ"],
    "減らす": ["へらす"],
    "集": ["あつ"],
    "散": ["ち"],
    "離": ["はな"],
    "別": ["わか"],
    "結": ["むす"],
    "縛": ["しば"],
    "解": ["と", "ほど"],
    "包": ["つつ"],
    "巻": ["ま"],
    "折": ["お"],
    "曲": ["ま"],
    "伸": ["の"],
    "縮": ["ちぢ"],
    "壊": ["こわ"],
    "直": ["なお"],
    "治": ["なお"],
    "改": ["あらた"],
    "整": ["ととの"],
    "並": ["なら"],
    "揃": ["そろ"],
    "比": ["くら"],
    "競": ["きそ"],
    "争": ["あらそ"],
    "戦う": ["たたかう"],
    "倒": ["たお"],
    "起こ": ["おこ"],
    "立ち": ["たち"],
    "回": ["まわ", "まわり"],
    "回り": ["まわり"],
    "転": ["ころ"],
    "踏": ["ふ"],
    "蹴": ["け"],
    "投": ["な"],
    "打": ["う"],
    "叩": ["たた"],
    "握": ["にぎ"],
    "抱": ["だ", "いだ", "かか"],
    "撫": ["な"],
    "触": ["さわ", "ふ"],
    "放": ["ほう", "はな"],  # 放っておく=ほうっておく(「ほう+っ」)、放つ=はなつ
    "撒": ["ま"],
    "感じ": ["かんじ"],  # 感じる
    "信じ": ["しんじ"],  # 信じる
    "命じ": ["めいじ"],  # 命じる
    "応じ": ["おうじ"],  # 応じる
    "禁じ": ["きんじ"],  # 禁じる
    "演じ": ["えんじ"],  # 演じる
    "報じ": ["ほうじ"],  # 報じる
    "閉じ": ["とじ"],  # 閉じる
    "似": ["に"],
    "落ち": ["お"],
    "減る": ["へる"],
    "増え": ["ふえ"],
    "増す": ["ます"],
    "建": ["た"],
    "造": ["つく"],
    "築": ["きず"],
    "創": ["つく"],
    "焼": ["や"],
    "茹": ["ゆ"],
    "煮": ["に"],
    "炒": ["いた"],
    "蒸": ["む"],
    "炊": ["た"],
    "混": ["ま"],
    "和": ["やわ", "なご"],
    "乱": ["みだ"],
    "汚れ": ["よご"],
    "洗": ["あら"],
    "拭": ["ふ", "ぬぐ"],
    "磨": ["みが"],
    "削": ["けず"],
    "彫": ["ほ"],
    "刻": ["きざ"],
    "塗": ["ぬ"],
    "描": ["か", "えが"],
    "踊": ["おど"],
    "歌": ["うた"],
    "奏": ["かな"],
    "響": ["ひび"],
    "鳴": ["な"],
    "唸": ["うな"],
    "叫": ["さけ"],
    "呼": ["よ"],
    "怒鳴": ["どな"],
    "呟": ["つぶや"],
    "囁": ["ささや"],
    "黙": ["だま"],
    "騒": ["さわ"],
    "弾": ["はず", "ひ"],
    "弾く": ["ひく"],
    "貯": ["た"],
    "蓄": ["たくわ"],
    "稼": ["かせ"],
    "使い": ["つかい"],
    "雇": ["やと"],
    "働": ["はたら"],
    "務": ["つと"],
    "勤": ["つと"],
    "勉強": ["べんきょう"],  # 音読み熟語
    "学": ["まな"],
    "教": ["おし"],
    "習": ["なら"],
    "練習": ["れんしゅう"],  # 音読み熟語
    "復習": ["ふくしゅう"],  # 音読み熟語
    "予習": ["よしゅう"],  # 音読み熟語
}

# 音読みっぽい1文字ルビ(典型例)
# これらが「動詞活用語尾」の直前に来ていたら誤読の可能性が高い
OBVIOUS_ONYOMI_HIRA = {
    "じょう", "りゅう", "しょう", "ちょう", "りょう", "きょう", "みょう",
    "ぎょう", "じょ", "りょ", "しゃ", "じゃ", "ちゃ",
    "がく", "かく", "けつ", "とく", "こく", "てき", "けき",
    "ふつ", "ぶつ", "せつ", "ばつ", "じつ", "つう",
    "ぜん", "せん", "けん", "げん", "へん", "ほん", "もん",
    "がん", "かん", "さん", "じん", "しん", "ちん", "ふん", "ぶん", "ぐん",
    "りん", "りん", "ぱん", "ばん", "らん",
    "りつ", "ろう", "そう", "ぞう", "とう", "どう", "のう", "ぼう",
    "りき", "りつ", "りん", "じり", "じょう",
    "ねん", "せい", "りん", "へい", "けい", "がい", "かい", "ざい", "せい",
    "び", "じょ", "じ", "ぎ", "き", "じ", "し", "ち", "に", "ひ", "び", "ぴ",
    "み", "り", "い",  # 1音節は混乱するが、後で原則で判定する
    "じ", "に", "き",
}

# 動詞活用語尾(「漢字《○》活用語尾」のパターン)
VERB_ENDINGS_REGEX = r"(っ|った|って|る|り|ら|れ|ろ|い|き|く|け|こ|し|す|せ|そ|た|ち|つ|て|と|な|に|ぬ|ね|の|ば|び|ぶ|べ|ぼ|ま|み|む|め|も|や|ゆ|よ|わ|え|お)"

# 形容詞活用語尾
ADJ_ENDINGS_REGEX = r"(い|く|か|け|さ)"

# 連用形+「った」「って」など濁音化・促音化を含む活用形
GODAN_ENDINGS = {"っ", "った", "って", "い", "いて", "いた", "き", "く", "ぐ", "ぎ", "し", "した", "して"}

# ---------------------------------------------------------------------------
# 検出ロジック

RUBY_TOKEN = re.compile(r"(?:｜([^《》｜]+)|([一-龯々〆ヶ]+))《([^》]+)》")
SINGLE_KANJI_RUBY = re.compile(r"([一-龯々])《([ぁ-ん]+)》")
COMPOUND_KANJI_RUBY = re.compile(r"([一-龯々])《([ぁ-ん]+)》([一-龯々])《([ぁ-ん]+)》")
KANJI_BARE = re.compile(r"[一-龯々]")


def is_likely_onyomi(reading: str) -> bool:
    """1文字漢字に対するルビが音読みっぽいか判定する.

    保守的: 明らかに音読み的なパターン(「ょう」「ゅう」を含む等)のみTrueを返す.
    """
    if len(reading) >= 2:
        # 拗音を含むものはほぼ音読み
        if any(small in reading for small in ("ょ", "ゅ", "ゃ")):
            return True
        # 撥音「ん」で終わるものは多くが音読み(例外あり)
        if reading.endswith("ん"):
            return True
        # 促音「っ」を含むものは多くが音読み熟語の一部
        if "っ" in reading:
            return True
        # 「く」「き」「ち」「つ」で終わる2音節は音読みが多い(かく/きく/かつ/かち)
        if reading in {"がく", "かく", "けつ", "つう", "てき", "ふん", "ぶん"}:
            return True
    return False


def find_consecutive_kanji_ruby(
    body_ruby: str,
) -> list[tuple[str, str, str, str]]:
    """連続漢字《》漢字《》パターンを検出.

    Returns: [(kanji1, ruby1, kanji2, ruby2), ...]
    """
    results = []
    for m in COMPOUND_KANJI_RUBY.finditer(body_ruby):
        k1, r1, k2, r2 = m.group(1), m.group(2), m.group(3), m.group(4)
        results.append((k1, r1, k2, r2))
    return results


def find_verb_misreading(body_ruby: str) -> list[tuple[str, str, str, str]]:
    """連用形・促音便で漢字+音読みっぽいルビ+動詞語尾のパターン.

    Returns: [(kanji, ruby, suffix, context), ...]

    重要な誤検出除外:
    - サ変動詞「○○する/した/して/しろ/しよう」の「し」(これは正しい音読み+「し」)
    - 助詞「と/も/は/が/を/に/で」が後に来るパターン(動詞活用ではない)
    - 助数詞+格助詞のパターン
    """
    results = []
    # 動詞の連用形・促音便を表す活用語尾(助詞は含めない)
    # 「っ」(促音便)、「い」(イ音便)、「り」(連用形)、「る」(終止形)、「れ」(已然形)、
    # 「ろ」(命令形)、「ら」「ば」(未然形/仮定形)など
    pattern = re.compile(
        r"([一-龯々])《([ぁ-ん]+)》(っ[たてぱ]|い[たてつ]|き出|り出|り合|り返|れ|ろ|る|り|ら|わ|え)"
    )
    for m in pattern.finditer(body_ruby):
        kanji = m.group(1)
        ruby = m.group(2)
        suffix = m.group(3)

        # 文脈40字を取得
        start = max(0, m.start() - 15)
        end = min(len(body_ruby), m.end() + 15)
        context = body_ruby[start:end]

        # 助数詞の後ろは除外(年/分/時/個/回/枚/本/匹/人/円/階/月/週/日/問など)
        # 漢字の直前が数字なら助数詞の可能性が高い
        if m.start() > 0:
            prev_char = body_ruby[m.start() - 1]
            if prev_char.isdigit():
                continue
            # 全角数字も
            if prev_char in "０１２３４５６７８９":
                continue

        # サ変動詞の語尾「し」を含めない(別途処理)
        if suffix == "し":
            continue
        # 「と」「も」も助詞の可能性が高い(動詞活用「と」「も」は稀)
        if suffix in {"と", "も", "は", "が", "を", "に", "で"}:
            continue

        # この漢字が VERB_KUN にあるなら、ルビが訓読みか判定
        if kanji in VERB_KUN:
            expected_kuns = VERB_KUN[kanji]
            # ルビが期待される訓読みのいずれにもマッチしない場合は怪しい
            if ruby not in expected_kuns:
                # かつ音読みっぽいルビなら、誤読の可能性が高い
                if is_likely_onyomi(ruby):
                    results.append((kanji, ruby, suffix, context))
                elif kanji in {"乗", "降", "通", "走", "歩"} and len(ruby) >= 2:
                    # 訓読みが期待される漢字だが、長め(2音以上)のルビは音読みの疑い
                    results.append((kanji, ruby, suffix, context))
        else:
            # VERB_KUNに無い漢字でも、明らかに音読み的なルビ+動詞語尾なら候補
            # 「っ」「いて」「いた」「った」「って」のような明確な動詞活用形のみ
            if is_likely_onyomi(ruby) and suffix.startswith(("っ", "い")):
                results.append((kanji, ruby, suffix, context))
    return results


def load_existing_overrides() -> set[str]:
    """add_furigana.py から既存OVERRIDESのパターン部分を抽出."""
    text = ADD_FURIGANA.read_text(encoding="utf-8")
    # (r"...", "...") のパターン部分
    patterns = set()
    for m in re.finditer(r'\(r"([^"]+)",\s*[r]?"([^"]+)"\)', text):
        patterns.add(m.group(1))
    return patterns


# ---------------------------------------------------------------------------
# stage5 監査

def _audit_ruby(src_path, label: str) -> dict:
    """body_ruby 付きJSONファイルの全問を監査(stage5 / stage6_draft 共通)."""
    data = json.loads(src_path.read_text(encoding="utf-8"))
    quizzes = data["quizzes"]
    print(f"{label}: {len(quizzes)} 問を監査中...")

    verb_misreadings: list[dict] = []
    compound_splits: list[dict] = []
    # 集計用
    verb_pattern_counter: Counter[str] = Counter()
    compound_pattern_counter: Counter[str] = Counter()

    for q in quizzes:
        qid = q.get("id", "?")
        word = q.get("word", "?")
        body_ruby = q.get("body_ruby", "")
        body = q.get("body", "")

        if not body_ruby:
            continue

        # 1) 連続漢字ルビ(熟語分割)
        for k1, r1, k2, r2 in find_consecutive_kanji_ruby(body_ruby):
            compound = f"{k1}{k2}"
            # 数字直後パターン(年前、回目、分間など助数詞+〇)は除外
            split_pos = body_ruby.find(f"{k1}《{r1}》{k2}《{r2}》")
            if split_pos > 0:
                prev_char = body_ruby[split_pos - 1]
                if prev_char.isdigit() or prev_char in "０１２３４５６７８９":
                    # 数字 + 助数詞 + 漢字 のパターン → 多くは独立した語
                    continue
            # 文字数が2で、両方音読みっぽい→熟語分割の疑い大
            if is_likely_onyomi(r1) and is_likely_onyomi(r2):
                # 両方とも音読みっぽい = 二字熟語の可能性が高い
                compound_splits.append({
                    "id": qid,
                    "word": word,
                    "compound": compound,
                    "split": f"{k1}《{r1}》{k2}《{r2}》",
                    "combined_ruby": r1 + r2,
                    "context": _extract_context(body_ruby, f"{k1}《{r1}》{k2}《{r2}》"),
                })
                compound_pattern_counter[compound] += 1

        # 2) 連用形音便の音読み誤読
        for kanji, ruby, suffix, context in find_verb_misreading(body_ruby):
            verb_misreadings.append({
                "id": qid,
                "word": word,
                "kanji": kanji,
                "ruby": ruby,
                "suffix": suffix,
                "expected_kun": VERB_KUN.get(kanji, []),
                "fragment": f"{kanji}《{ruby}》{suffix}",
                "context": context,
            })
            verb_pattern_counter[f"{kanji}{suffix[:1]}"] += 1

    return {
        "total": len(quizzes),
        "verb_misreadings": verb_misreadings,
        "compound_splits": compound_splits,
        "verb_pattern_counter": verb_pattern_counter,
        "compound_pattern_counter": compound_pattern_counter,
    }


def audit_stage5() -> dict:
    return _audit_ruby(STAGE5, "stage5")


def audit_stage6_draft() -> dict:
    return _audit_ruby(STAGE6_DRAFT, "stage6_draft")


def _extract_context(body_ruby: str, target: str) -> str:
    """body_ruby の中で target の前後20字を抜き出す."""
    idx = body_ruby.find(target)
    if idx < 0:
        return body_ruby[:60]
    start = max(0, idx - 20)
    end = min(len(body_ruby), idx + len(target) + 20)
    return body_ruby[start:end]


def _guess_original_compound(context: str, split: str, compound: str) -> str:
    """文脈から元の熟語(3字以上含む可能性)を推定する.

    例: split = "間《じかん》前《ぜん》" → original = "時間前"
    分割形の前の漢字+「漢字《》」連続を結合.
    """
    # ルビ除去 → 純文字列に
    stripped_context = RUBY_TOKEN.sub(lambda m: m.group(1) or m.group(2), context)
    # 純文字列内で compound の位置を探し、前の漢字を拾う
    idx = stripped_context.find(compound)
    if idx < 0:
        return compound
    # 前方向に漢字を遡る
    pre_chars = []
    i = idx - 1
    while i >= 0 and KANJI_BARE.match(stripped_context[i]):
        pre_chars.append(stripped_context[i])
        i -= 1
    pre = "".join(reversed(pre_chars))
    # 後方向にも漢字を進む
    post_chars = []
    j = idx + len(compound)
    while j < len(stripped_context) and KANJI_BARE.match(stripped_context[j]):
        post_chars.append(stripped_context[j])
        j += 1
    post = "".join(post_chars)
    return pre + compound + post


# ---------------------------------------------------------------------------
# stage6 監査

# 単純な日本語自然さチェック用パターン
UNNATURAL_PATTERNS = [
    (re.compile(r"<[a-zA-Z]+>な<[a-zA-Z]+>"), "<word>+な+<word>連続"),
    (re.compile(r"(ななな|だだだ|たたた|ががが)"), "ひらがな3回重複(誤入力疑い)"),
    (re.compile(r"<[a-zA-Z]+><[a-zA-Z]+>"), "<word>連続(空白なし)"),
    (re.compile(r"。。"), "句点連続"),
    (re.compile(r"、、"), "読点連続"),
    (re.compile(r"!!"), "感嘆符連続"),
    (re.compile(r"・・・・"), "中黒4つ以上"),
]


def audit_stage6() -> dict:
    """stage6_batch_01-08 の body内容を機械的にチェック."""
    print(f"stage6: {len(STAGE6_FILES)} ファイルを監査中...")
    issues: list[dict] = []
    total = 0
    samples_by_batch: dict[str, list[dict]] = {}

    for path in STAGE6_FILES:
        data = json.loads(path.read_text(encoding="utf-8"))
        quizzes = data["quizzes"]
        batch_name = path.stem
        samples_by_batch[batch_name] = quizzes[:5]  # サンプル
        total += len(quizzes)

        for idx, q in enumerate(quizzes):
            body = q.get("body", "")
            word = q.get("word", "?")
            pos = q.get("pos", "?")

            # 機械的検出可能な問題
            for pat, desc in UNNATURAL_PATTERNS:
                if pat.search(body):
                    issues.append({
                        "batch": batch_name,
                        "idx": idx,
                        "word": word,
                        "pos": pos,
                        "body": body,
                        "issue": desc,
                    })

            # <word>が本文に含まれていない
            if f"<{word}>" not in body:
                issues.append({
                    "batch": batch_name,
                    "idx": idx,
                    "word": word,
                    "pos": pos,
                    "body": body,
                    "issue": "<word>タグが本文に無い",
                })

            # 本文が短すぎる(20字未満)
            stripped = re.sub(r"<[^>]+>", "", body)
            if len(stripped) < 20:
                issues.append({
                    "batch": batch_name,
                    "idx": idx,
                    "word": word,
                    "pos": pos,
                    "body": body,
                    "issue": f"本文が短い({len(stripped)}字)",
                })

            # 同じ <word> が2回以上出る
            if body.count(f"<{word}>") > 1:
                issues.append({
                    "batch": batch_name,
                    "idx": idx,
                    "word": word,
                    "pos": pos,
                    "body": body,
                    "issue": "<word>タグが2回以上出現",
                })

            # 品詞と文脈の整合性
            m = re.search(rf"<{re.escape(word)}>([぀-ゟ]{{0,4}})", body)
            if m:
                tail = m.group(1)
                # 副詞 (副) が「な/の/で/だ」に続く=形容動詞的使用
                if "副" in pos and tail.startswith(("な", "の", "で", "だ")):
                    issues.append({
                        "batch": batch_name,
                        "idx": idx,
                        "word": word,
                        "pos": pos,
                        "body": body,
                        "issue": f"副詞のはずが直後に「{tail[:2]}」(形容動詞的使用)",
                    })
                # 動詞 (動) で「のよう/のため/による/について」のような名詞節
                if pos == "動" and tail.startswith(("のよう", "のため", "による", "について", "の中", "の上", "の前", "の後", "の時")):
                    issues.append({
                        "batch": batch_name,
                        "idx": idx,
                        "word": word,
                        "pos": pos,
                        "body": body,
                        "issue": f"動詞のはずが直後に「{tail[:3]}」(名詞的使用)",
                    })

    return {
        "total": total,
        "issues": issues,
        "samples_by_batch": samples_by_batch,
    }


# ---------------------------------------------------------------------------
# OVERRIDES提案

def propose_overrides(
    stage5_result: dict, existing_overrides: set[str]
) -> dict:
    """検出結果からOVERRIDES追加提案を生成.

    Returns: {
        "verb_proposals": [(pattern_jp, fix, count), ...],
        "compound_proposals": [(pattern_jp, mark, count), ...]
    }

    ルールはOVERRIDESを正規表現で適用するので、提案する pattern_jp の重複は避ける.
    """
    # 連用形誤読: (漢字+語尾頭1字) で集計し、最頻訓読みを採用
    # 例: 「乗っ」「乗って」「乗った」をまとめて(漢字 乗 + 接頭 っ)→「乗《の》っ」
    verb_freq: Counter[tuple[str, str, str]] = Counter()  # (パターン, 訓読み)
    for m in stage5_result["verb_misreadings"]:
        kanji = m["kanji"]
        suffix = m["suffix"]
        # パターンは「漢字 + 語尾の頭1字」(促音便なら「っ」、イ音便なら「い」、等)
        first_suffix = suffix[:1]
        pattern_jp = kanji + first_suffix
        if m["expected_kun"]:
            kun = m["expected_kun"][0]
            verb_freq[(pattern_jp, kun, kanji)] += 1

    # 熟語分割: ルビ案は連結しない(誤読が多発するため)。
    # 文脈から「元の3字以上の熟語(原語)」を推定する
    compound_freq: Counter[tuple[str, str, str, str]] = Counter()
    for m in stage5_result["compound_splits"]:
        compound = m["compound"]
        split = m["split"]
        context = m["context"]
        # 元の3字以上の熟語を文脈から推定する
        # 分割形の前の1〜2漢字を取得して結合する
        original = _guess_original_compound(context, split, compound)
        compound_freq[(compound, split, m["combined_ruby"], original)] += 1

    verb_proposals: list[tuple[str, str, int]] = []
    seen_patterns: set[str] = set()
    for (pattern_jp, kun, kanji), count in verb_freq.most_common(80):
        if pattern_jp in existing_overrides or pattern_jp in seen_patterns:
            continue
        seen_patterns.add(pattern_jp)
        suffix_char = pattern_jp[1] if len(pattern_jp) > 1 else ""
        fix = f"{kanji}《{kun}》{suffix_char}"
        verb_proposals.append((pattern_jp, fix, count))

    # 熟語提案は「元の3字以上の語(original)」をキーに集計し直す
    # (同じ split fragment でも複数 originalが出る場合に備える)
    original_freq: Counter[tuple[str, str]] = Counter()  # (original, split_example)
    original_to_examples: dict[str, list[tuple[str, str]]] = {}  # original → [(split, combined)]
    for (compound, split_example, combined, original), count in compound_freq.items():
        original_freq[(original, split_example)] += count
        original_to_examples.setdefault(original, []).append((split_example, combined))

    compound_proposals: list[tuple[str, str, str, int]] = []
    seen_originals: set[str] = set()
    for (original, split_example), count in original_freq.most_common(50):
        if original in existing_overrides or original in seen_originals:
            continue
        seen_originals.add(original)
        # 元語が3字以上ならその語をパターンに使う(誤マッチを減らす)
        # 元語が2字なら短いまま(他文脈で誤マッチする可能性あり)
        pattern_jp = original if len(original) >= 2 else split_example
        combined_ref = original_to_examples[original][0][1]
        compound_proposals.append((pattern_jp, combined_ref, split_example, count))

    return {
        "verb_proposals": verb_proposals,
        "compound_proposals": compound_proposals,
    }


# ---------------------------------------------------------------------------
# レポート生成

def write_report(
    stage5_result: dict, stage6_result: dict, proposals: dict,
    stage6_draft_result: dict | None = None,
) -> None:
    lines: list[str] = []
    lines.append("# WordTacos ルビ・日本語監査レポート (2026-06-15)")
    lines.append("")
    lines.append("## 全体サマリ")
    lines.append("")
    lines.append(f"- **stage5 監査対象**: {stage5_result['total']} 問")
    lines.append(f"- **stage5 連用形音便誤読候補**: {len(stage5_result['verb_misreadings'])} 件")
    lines.append(f"- **stage5 熟語文字分割誤読候補**: {len(stage5_result['compound_splits'])} 件")
    if stage6_draft_result is not None:
        lines.append(f"- **stage6_draft 監査対象**: {stage6_draft_result['total']} 問")
        lines.append(f"- **stage6_draft 連用形音便誤読候補**: {len(stage6_draft_result['verb_misreadings'])} 件")
        lines.append(f"- **stage6_draft 熟語文字分割誤読候補**: {len(stage6_draft_result['compound_splits'])} 件")
    lines.append(f"- **stage6_batch_全件 監査対象**: {stage6_result['total']} 問")
    lines.append(f"- **stage6 body内容問題候補**: {len(stage6_result['issues'])} 件")
    total_proposals = len(proposals['verb_proposals']) + len(proposals['compound_proposals'])
    lines.append(f"- **OVERRIDES追加提案**: {total_proposals} 件 (動詞:{len(proposals['verb_proposals'])} / 熟語:{len(proposals['compound_proposals'])})")
    lines.append("")

    # === stage6_draft 監査結果(stage5と同じ形式) ===
    if stage6_draft_result is not None:
        lines.append("## stage6_draft 連用形音便誤読 (上位30件)")
        lines.append("")
        lines.append("| id | word | 問題箇所 | 文脈 | 修正案 |")
        lines.append("|---|---|---|---|---|")
        for m in stage6_draft_result["verb_misreadings"][:30]:
            expected = "/".join(m["expected_kun"]) if m["expected_kun"] else "?"
            suggested_fix = f"{m['kanji']}《{m['expected_kun'][0]}》{m['suffix']}" if m["expected_kun"] else "?"
            context_escaped = m["context"].replace("|", "\\|")
            fragment_escaped = m["fragment"].replace("|", "\\|")
            fix_escaped = suggested_fix.replace("|", "\\|")
            lines.append(f"| {m['id']} | {m['word']} | {fragment_escaped} | {context_escaped} | {fix_escaped} (期待訓:{expected}) |")
        lines.append("")
        if len(stage6_draft_result["verb_misreadings"]) > 30:
            lines.append(f"...残り {len(stage6_draft_result['verb_misreadings']) - 30} 件")
            lines.append("")

        lines.append("## stage6_draft 熟語文字分割 (上位30件)")
        lines.append("")
        lines.append("| id | word | 分割形 | 結合後ルビ案 | 文脈 |")
        lines.append("|---|---|---|---|---|")
        for m in stage6_draft_result["compound_splits"][:30]:
            combined_fix = f"{m['compound']}《{m['combined_ruby']}》"
            context_escaped = m["context"].replace("|", "\\|")
            split_escaped = m["split"].replace("|", "\\|")
            fix_escaped = combined_fix.replace("|", "\\|")
            lines.append(f"| {m['id']} | {m['word']} | {split_escaped} | {fix_escaped} | {context_escaped} |")
        lines.append("")
        if len(stage6_draft_result["compound_splits"]) > 30:
            lines.append(f"...残り {len(stage6_draft_result['compound_splits']) - 30} 件")
            lines.append("")

        lines.append("### stage6_draft 熟語分割 頻度 (上位20)")
        lines.append("")
        lines.append("| 熟語 | 件数 |")
        lines.append("|---|---|")
        for compound, count in stage6_draft_result["compound_pattern_counter"].most_common(20):
            lines.append(f"| {compound} | {count} |")
        lines.append("")

    # === stage5 連用形音便誤読 ===
    lines.append("## stage5 連用形音便誤読 (上位30件 詳細)")
    lines.append("")
    lines.append("| id | word | 問題箇所 | 文脈 | 修正案 |")
    lines.append("|---|---|---|---|---|")
    for m in stage5_result["verb_misreadings"][:30]:
        expected = "/".join(m["expected_kun"]) if m["expected_kun"] else "?"
        suggested_fix = f"{m['kanji']}《{m['expected_kun'][0]}》{m['suffix']}" if m["expected_kun"] else "?"
        context_escaped = m["context"].replace("|", "\\|")
        fragment_escaped = m["fragment"].replace("|", "\\|")
        fix_escaped = suggested_fix.replace("|", "\\|")
        lines.append(f"| {m['id']} | {m['word']} | {fragment_escaped} | {context_escaped} | {fix_escaped} (期待訓:{expected}) |")
    lines.append("")
    if len(stage5_result["verb_misreadings"]) > 30:
        remaining = len(stage5_result["verb_misreadings"]) - 30
        lines.append(f"...残り {remaining} 件")
        lines.append("")

    lines.append("### 連用形誤読 漢字+語尾別頻度 (上位20)")
    lines.append("")
    lines.append("| 漢字+語尾 | 件数 |")
    lines.append("|---|---|")
    for pattern, count in stage5_result["verb_pattern_counter"].most_common(20):
        lines.append(f"| {pattern} | {count} |")
    lines.append("")

    # === stage5 熟語文字分割 ===
    lines.append("## stage5 熟語文字分割 (上位30件)")
    lines.append("")
    lines.append("| id | word | 分割形 | 結合後ルビ案 | 文脈 |")
    lines.append("|---|---|---|---|---|")
    for m in stage5_result["compound_splits"][:30]:
        combined_fix = f"{m['compound']}《{m['combined_ruby']}》"
        context_escaped = m["context"].replace("|", "\\|")
        split_escaped = m["split"].replace("|", "\\|")
        lines.append(f"| {m['id']} | {m['word']} | {split_escaped} | {combined_fix} | {context_escaped} |")
    lines.append("")
    if len(stage5_result["compound_splits"]) > 30:
        remaining = len(stage5_result["compound_splits"]) - 30
        lines.append(f"...残り {remaining} 件")
        lines.append("")

    lines.append("### 熟語分割 頻度 (上位20)")
    lines.append("")
    lines.append("| 熟語 | 件数 |")
    lines.append("|---|---|")
    for pattern, count in stage5_result["compound_pattern_counter"].most_common(20):
        lines.append(f"| {pattern} | {count} |")
    lines.append("")

    # === stage6 body内容問題 ===
    lines.append("## stage6_batch_01-08 body内容問題 (検出全件)")
    lines.append("")
    if stage6_result["issues"]:
        lines.append("| batch | idx | word | pos | 問題内容 | body |")
        lines.append("|---|---|---|---|---|---|")
        for m in stage6_result["issues"]:
            body_escaped = m["body"].replace("|", "\\|")
            lines.append(f"| {m['batch']} | {m['idx']} | {m['word']} | {m.get('pos','?')} | {m['issue']} | {body_escaped} |")
    else:
        lines.append("(機械検出可能な明確な問題は見つからず — 目視サンプルチェック結果は下記参照)")
    lines.append("")

    lines.append("### stage6 各batch先頭5問サンプル (目視確認用)")
    lines.append("")
    for batch_name, samples in stage6_result["samples_by_batch"].items():
        lines.append(f"#### {batch_name}")
        lines.append("")
        for i, q in enumerate(samples):
            lines.append(f"- **{i}** `{q.get('word')}` ({q.get('pos','?')}): {q.get('body','')}")
        lines.append("")

    # === OVERRIDES提案 ===
    lines.append("## add_furigana.py OVERRIDES 追加提案")
    lines.append("")
    lines.append("### A. 動詞活用形 (連用形音便) — 機械生成ルビ案 ")
    lines.append("")
    lines.append("頻度順。既存OVERRIDESに含まれていないパターンのみ。")
    lines.append("ルビ案は `VERB_KUN` 辞書から自動生成しているため、")
    lines.append("意味的にあてはまるかは要目視確認。")
    lines.append("")
    lines.append("```python")
    lines.append("ADDITIONAL_OVERRIDES_VERB = [")
    for pattern_jp, fix, count in proposals["verb_proposals"][:80]:
        lines.append(f'    (r"{pattern_jp}", "{fix}"),  # 検出{count}件')
    lines.append("]")
    lines.append("```")
    lines.append("")
    lines.append("### B. 熟語(2字漢語) — ルビ案は機械では出せないので**手動で正しい読みを書く**")
    lines.append("")
    lines.append("`# TODO: 要正しい読み` の部分は母艦Claudeか辞書で確定する。")
    lines.append("「結合参考」は機械的に連結したルビ(誤読の可能性が高い参考値)。")
    lines.append("")
    lines.append("```python")
    lines.append("ADDITIONAL_OVERRIDES_COMPOUND = [")
    for compound, combined, split_example, count in proposals["compound_proposals"][:50]:
        lines.append(f'    (r"{compound}", "{compound}《TODO》"),  # 検出{count}件 結合参考:{combined} 例:{split_example}')
    lines.append("]")
    lines.append("```")
    lines.append("")

    # === 補足 ===
    lines.append("## 補足: 検出ロジックの注意点")
    lines.append("")
    lines.append("**連用形誤読検出 (12件)**:")
    lines.append("- `VERB_KUN`辞書 (動詞語幹漢字→正しい訓読みリスト) と")
    lines.append("  `is_likely_onyomi`(拗音/撥音/促音を含む≒音読み判定)を組み合わせて検出。")
    lines.append("- 誤検出が多発したサ変動詞「○○する/して/した」(語尾「し」)、")
    lines.append("  助数詞+格助詞のパターン(語尾「と」「も」)、数字直前の漢字は明示的に除外。")
    lines.append("- 動詞活用語尾は `っ/った/って/い/いて/いた/り/る/れ/ろ/ら/わ` のみに絞り込み。")
    lines.append("- 残った候補はほぼ全件が真の誤読(母艦目視で確認推奨)。")
    lines.append("")
    lines.append("**熟語分割検出 (19件)**:")
    lines.append("- 連続2文字の `漢字《ルビ》漢字《ルビ》` パターンを全件抽出。")
    lines.append("- **両方音読みっぽい**(拗音/撥音/促音/二字以上)場合のみ採用(二字熟語が割れている可能性大)。")
    lines.append("- 数字直前のパターン(助数詞+漢字)は除外(「3年前」の「年前」等)。")
    lines.append("- OVERRIDES提案では文脈から3字以上の元の語を推定したパターンを優先使用。")
    lines.append("")
    lines.append("**stage6 body内容 (4件)**:")
    lines.append("- 機械的に検出できるのは書式エラー + 品詞と直後の助詞/接続詞の不整合のみ。")
    lines.append("- 「副詞 + な」「動詞 + のような」のような明確な品詞ミスマッチを検出。")
    lines.append("- 文の自然さ・<word>の品詞内での妥当性は別途LLMレビュー推奨。")
    lines.append("- 各batchの先頭5問サンプルを上記に列挙(目視確認用)。")
    lines.append("")
    lines.append("## 母艦への引き継ぎメモ")
    lines.append("")
    lines.append("1. **OVERRIDES-A (動詞活用形)を add_furigana.py に追加** → コピペでOK")
    lines.append("   - 4件のみ。`乗っ`は4箇所修正、他は1件ずつ。")
    lines.append("2. **OVERRIDES-B (熟語) を add_furigana.py に追加** → 各エントリの`TODO`部に")
    lines.append("   正しい読みを書く必要あり。母艦Claudeで辞書確認しながら埋める。")
    lines.append("   - 「日中安全点検」「一日中本」「外出時間」のような誤抽出も含む(元の3字以上推定が過剰)。")
    lines.append("     母艦で実物のbody_rubyを見て、正しい元語(例: 安全点検、外出時間)を確定する。")
    lines.append("3. **add_furigana.py を再実行して stage5_quizzes_clean.json を再生成**")
    lines.append("4. **stage5 個別誤読の手動修正**: airplane の「離陸」「乗った」を含む 12+19 = 31 件は")
    lines.append("   OVERRIDES追加後の add_furigana.py 再実行で大半が解消する想定。")
    lines.append("5. **stage6_batch_01-08 はルビ未生成** — 現状body のみ。stage6 専用に")
    lines.append("   `add_furigana.py` の `SRC` を変えて回す必要あり(構造は同じ `quizzes` キー)。")
    lines.append("6. **stage6 4件の本文修正**: 品詞ミスマッチは LLM 経由でbody再生成 or 手動修正。")
    lines.append("")
    lines.append("## 検出限界(LLMレビュー推奨案件)")
    lines.append("")
    lines.append("以下は機械で検出できないため、母艦Claudeまたは別LLMでバッチレビューが必要:")
    lines.append("- 動詞語尾以外の場所で起きている熟語誤読(例: 「乗《じょう》り場《ば》」)")
    lines.append("- 連体修飾の不自然さ、敬語の混乱")
    lines.append("- 文脈で<word>の意味が推測しにくいbody")
    lines.append("- B2語彙として適切か(高校生〜大人向けレベル感)")
    lines.append("")
    lines.append("## 再実行方法")
    lines.append("")
    lines.append("```bash")
    lines.append("cd /Users/masaki/Documents/ClaudeCode/英語学習教材作成/vocab_sources/")
    lines.append("python3 audit_furigana.py")
    lines.append("```")
    lines.append("出力: `furigana_audit_report.md` (本ファイル) を上書き再生成。")
    lines.append("")

    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"レポート出力: {REPORT}")


# ---------------------------------------------------------------------------
# main

def main() -> None:
    existing_overrides = load_existing_overrides()
    print(f"既存OVERRIDES: {len(existing_overrides)} パターン")

    stage5_result = audit_stage5()
    print(f"  連用形音便誤読候補: {len(stage5_result['verb_misreadings'])} 件")
    print(f"  熟語文字分割誤読候補: {len(stage5_result['compound_splits'])} 件")

    stage6_draft_result = None
    if STAGE6_DRAFT.exists():
        stage6_draft_result = audit_stage6_draft()
        print(f"  stage6_draft 連用形誤読候補: {len(stage6_draft_result['verb_misreadings'])} 件")
        print(f"  stage6_draft 熟語分割候補: {len(stage6_draft_result['compound_splits'])} 件")

    stage6_result = audit_stage6()
    print(f"  stage6 body内容問題候補: {len(stage6_result['issues'])} 件")

    # OVERRIDES提案は stage5 + stage6_draft の両方を合算
    merged_for_proposals = dict(stage5_result)
    if stage6_draft_result is not None:
        from collections import Counter
        merged_for_proposals = {
            "total": stage5_result["total"] + stage6_draft_result["total"],
            "verb_misreadings": stage5_result["verb_misreadings"] + stage6_draft_result["verb_misreadings"],
            "compound_splits": stage5_result["compound_splits"] + stage6_draft_result["compound_splits"],
            "verb_pattern_counter": stage5_result["verb_pattern_counter"] + stage6_draft_result["verb_pattern_counter"],
            "compound_pattern_counter": stage5_result["compound_pattern_counter"] + stage6_draft_result["compound_pattern_counter"],
        }
    proposals = propose_overrides(merged_for_proposals, existing_overrides)
    print(f"  OVERRIDES提案: 動詞{len(proposals['verb_proposals'])}件 / 熟語{len(proposals['compound_proposals'])}件")

    write_report(stage5_result, stage6_result, proposals, stage6_draft_result=stage6_draft_result)


if __name__ == "__main__":
    main()
