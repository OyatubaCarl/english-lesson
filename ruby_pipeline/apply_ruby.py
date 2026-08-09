"""新規例文にルビを振る。

優先順位:
1. dict_kanji_readings.csv (既存全ステージから抽出した ground truth)
2. SudachiPy mode C + MeCab (UniDic-lite) 並行解析、一致したら採用
3. 不一致 → ambiguous リストに退避 (後で LLM 解決)

入出力:
- input: 対象 JSON のパスと、書き換える例文の (word, body) リスト
- output: 各文の body_ruby と、ambiguous リスト
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

from ruby_core import (
    KANJI_RE,
    extract_kanji_groups,
    has_kanji,
    kata_to_hira,
    mecab_morphs,
    morphs_to_ruby,
    sudachi_morphs,
)

DICT_CSV = Path(__file__).resolve().parent / "dict_kanji_readings.csv"
CUSTOM_CSV = Path(__file__).resolve().parent / "dict_custom_overrides.csv"


def load_dictionary() -> tuple[dict[str, str], set[str], dict[str, str]]:
    """既存ステージから構築した辞書を読む。

    返り値:
    - top: 漢字塊 → top reading
    - polysemous: 多義漢字塊 (alt が無視できない頻度で存在)
    - overrides: カスタム上書き (絶対優先)
    """
    top: dict[str, str] = {}
    polysemous: set[str] = set()
    if DICT_CSV.exists():
        with DICT_CSV.open(encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                k = row["kanji"]
                top_reading = row["top_reading"]
                top_count = int(row["top_count"])
                alts = json.loads(row["alt_readings_json"])
                top[k] = top_reading
                # 多義判定: alt の最大頻度が top の 20% 以上 → 多義
                if alts:
                    max_alt = max(alts.values())
                    if max_alt >= max(3, top_count * 0.2):
                        polysemous.add(k)
    overrides: dict[str, str] = {}
    if CUSTOM_CSV.exists():
        with CUSTOM_CSV.open(encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                overrides[row["kanji"]] = row["reading"]
    return top, polysemous, overrides


def split_text_by_word_tag(text: str) -> list[tuple[str, bool]]:
    """`<word>` タグを境界に分割。(チャンク, is_tag) を返す。
    タグ中身はルビを振らない (英単語なので)。
    """
    pattern = re.compile(r"<[^>]+>")
    out: list[tuple[str, bool]] = []
    pos = 0
    for m in pattern.finditer(text):
        if m.start() > pos:
            out.append((text[pos:m.start()], False))
        out.append((m.group(), True))
        pos = m.end()
    if pos < len(text):
        out.append((text[pos:], False))
    return out


def merge_ruby_with_dict(
    text: str,
    sud_ruby: str,
    mec_ruby: str,
    top: dict[str, str],
    polysemous: set[str],
    overrides: dict[str, str],
) -> tuple[str, list[tuple[str, str, str, str]]]:
    """sud_ruby と mec_ruby を辞書で調停して最終ルビを生成。

    手順:
    1. overrides にあれば絶対上書き
    2. 両エンジンが一致 → エンジン採用 (辞書スルー)。ただし多義漢字なら ambiguous に追加
    3. 不一致 → top の読みを優先、なければ SudachiPy 優先、ambiguous に退避

    返り値: (最終ルビ文字列, [(漢字塊, sud読, mec読, 採用読), ...] の要レビュー記録)
    """
    sud_groups = dict(extract_kanji_groups(sud_ruby))
    mec_groups = dict(extract_kanji_groups(mec_ruby))
    all_kanji = set(sud_groups) | set(mec_groups)
    ambiguous: list[tuple[str, str, str, str]] = []
    chosen: dict[str, str] = {}

    for k in all_kanji:
        sr = sud_groups.get(k)
        mr = mec_groups.get(k)
        if k in overrides:
            best = overrides[k]
        elif sr == mr and sr is not None:
            best = sr
        elif sr is not None and mr is None:
            best = sr
        elif sr is None and mr is not None:
            best = mr
        elif k in top:
            # 両エンジンで異なる → top を優先
            best = top[k]
        else:
            # 本当に違う読み、辞書にもない → SudachiPy 優先で、後で要レビュー
            best = sr or mr or ""
            ambiguous.append((k, sr or "", mr or "", best))
            chosen[k] = best
            continue
        # hard ambiguous: 両エンジンが不一致 (= 本当に怪しい) のみ LLM 解決対象に追加
        engines_disagree = (sr is not None and mr is not None and sr != mr)
        if engines_disagree and k not in overrides:
            ambiguous.append((k, sr or "", mr or "", best))
        chosen[k] = best

    # SudachiPy ルビ文字列に対して、 chosen[k] を当てる
    # 範囲指定ルビ ｜...《...》 はそのまま保護する (内部の漢字が誤マッチしないよう)
    placeholders: dict[str, str] = {}

    def stash(m: re.Match) -> str:
        i = len(placeholders)
        ph = f"\x00R{i}\x00"
        placeholders[ph] = m.group(0)
        return ph

    protected = re.sub(r"｜[^《》]+《[぀-ゟぁ-ゔ゠-ヿ]+》", stash, sud_ruby)

    def repl(m: re.Match) -> str:
        k = m.group(1)
        if k in chosen:
            return f"{k}《{chosen[k]}》"
        return m.group(0)

    out = re.sub(r"([一-鿿々]+)《([぀-ゟ]+)》", repl, protected)
    for ph, orig in placeholders.items():
        out = out.replace(ph, orig)
    return out, ambiguous


def add_ruby_to_text(
    text: str,
    top: dict[str, str],
    polysemous: set[str],
    overrides: dict[str, str],
) -> tuple[str, list[tuple[str, str, str, str]]]:
    """文をルビ化。<word> タグは保護。"""
    chunks = split_text_by_word_tag(text)
    out_parts: list[str] = []
    all_ambiguous: list[tuple[str, str, str, str]] = []
    for chunk, is_tag in chunks:
        if is_tag or not has_kanji(chunk):
            out_parts.append(chunk)
            continue
        sud = morphs_to_ruby(sudachi_morphs(chunk))
        mec = morphs_to_ruby(mecab_morphs(chunk))
        merged, amb = merge_ruby_with_dict(chunk, sud, mec, top, polysemous, overrides)
        out_parts.append(merged)
        all_ambiguous.extend(amb)
    return "".join(out_parts), all_ambiguous


def add_ruby_to_quizzes(
    json_path: Path,
    only_words: set[str] | None = None,
    dicts: tuple[dict[str, str], set[str], dict[str, str]] | None = None,
) -> tuple[int, dict[str, list[tuple[str, str, str, str]]]]:
    """quizzes の body / body_ruby を再生成。
    only_words が指定された場合、そこに含まれる word のみ処理。
    """
    if dicts is None:
        dicts = load_dictionary()
    top, polysemous, overrides = dicts
    d = json.loads(json_path.read_text(encoding="utf-8"))
    updated = 0
    amb_per_word: dict[str, list[tuple[str, str, str, str]]] = {}
    for q in d["quizzes"]:
        w = q["word"]
        if only_words is not None and w not in only_words:
            continue
        body = q.get("body", "")
        if not body:
            continue
        ruby, amb = add_ruby_to_text(body, top, polysemous, overrides)
        q["body_ruby"] = ruby
        if amb:
            amb_per_word[w] = amb
        updated += 1
    json_path.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    return updated, amb_per_word


if __name__ == "__main__":
    # スモークテスト
    top, polysemous, overrides = load_dictionary()
    print(f"辞書サイズ: top={len(top)} polysemous={len(polysemous)} overrides={len(overrides)}")
    samples = [
        "私が初めてピアノを弾いたのは、5年<ago>のことでした。",
        "教授は『記憶は感情に依存する』と<hypothesize>し、3年がかりの実験を組んだ。",
        "新組織は5つの部門を<comprise>する設計だ。",
        "監視カメラの映像が目撃者の話を<corroborate>したので、判決は早かった。",
        "顧客の安全は、コストや効率より<paramount>であるべきだ。",
        "突然の値引きには、私はかなり<dubious>な気持ちになった。",
    ]
    for s in samples:
        ruby, amb = add_ruby_to_text(s, top, polysemous, overrides)
        print(f"\n  IN : {s}")
        print(f"  OUT: {ruby}")
        if amb:
            for k, sr, mr, best in amb:
                print(f"  AMB: {k}  sud={sr}  mec={mr}  → 採用={best}")
