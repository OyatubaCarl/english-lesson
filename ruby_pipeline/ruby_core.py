"""ルビ振りコア: SudachiPy + MeCab (UniDic) で並行解析、青空文庫形式に変換。

青空文庫ルビ形式:
- `漢字《よみ》`              ... 漢字シーケンスにルビ
- `｜任意文字列《よみ》`       ... 範囲指定 (今回は使わない)
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache

# 漢字判定 (CJK統合漢字 + 漢字「々」)
KANJI_RE = re.compile(r"[一-鿿々]")
# 漢字のみのシーケンス
KANJI_SEQ_RE = re.compile(r"[一-鿿々]+")


def kata_to_hira(s: str) -> str:
    """カタカナ→ひらがな変換。長音記号「ー」はそのまま。"""
    out = []
    for ch in s:
        code = ord(ch)
        if 0x30A1 <= code <= 0x30F6:  # ァ〜ヶ
            out.append(chr(code - 0x60))
        else:
            out.append(ch)
    return "".join(out)


def has_kanji(s: str) -> bool:
    return bool(KANJI_RE.search(s))


# ===== SudachiPy backend =====
_sudachi = None


def get_sudachi():
    global _sudachi
    if _sudachi is None:
        from sudachipy import dictionary
        _sudachi = dictionary.Dictionary(dict="full").create()
    return _sudachi


def sudachi_morphs(text: str) -> list[tuple[str, str]]:
    """SudachiPy mode C で形態素分解。各 (surface, reading_kata) を返す。"""
    from sudachipy import tokenizer as _tok
    tok = get_sudachi()
    return [(m.surface(), m.reading_form()) for m in tok.tokenize(text, mode=_tok.Tokenizer.SplitMode.C)]


# ===== MeCab (fugashi + UniDic-lite) backend =====
_mecab = None


def get_mecab():
    global _mecab
    if _mecab is None:
        import fugashi
        _mecab = fugashi.Tagger()
    return _mecab


def mecab_morphs(text: str) -> list[tuple[str, str]]:
    """fugashi (UniDic-lite) で形態素分解。各 (surface, reading_kata) を返す。"""
    tagger = get_mecab()
    out: list[tuple[str, str]] = []
    for w in tagger(text):
        kana = getattr(w.feature, "kana", None)
        # UniDic-lite では feature.kana が読み (カタカナ)。pronounce より kana の方が正確。
        if kana is None or kana == "*":
            kana = w.surface
        out.append((w.surface, kana))
    return out


# ===== 漢字シーケンス分解とルビ生成 =====


def split_morph_to_kanji_and_kana(surface: str, reading_kata: str) -> list[tuple[str, str | None, str]]:
    """1 形態素の (surface, reading) を、漢字シーケンスと非漢字に分割。

    各セグメントは (text, ruby, kind) を返す。
    - ruby: 読み (ひらがな) or None
    - kind: 'normal' (`漢字《ruby》`) / 'range' (`｜text《ruby》`) / 'plain' (ルビなし)

    複雑な複合語 (漢字+ひらがな+漢字) は 'range' で形態素全体に1つのルビをかける。

    例:
        ('裏付け', 'ウラヅケ')   -> [('裏付', 'うらづ', 'normal'), ('け', None, 'plain')]
        ('監視カメラ', 'カンシカメラ') -> [('監視', 'かんし', 'normal'), ('カメラ', None, 'plain')]
        ('書き換わっ', 'カキカワッ') -> [('書き換わっ', 'かきかわっ', 'range')]
        ('引っ越し', 'ヒッコシ')  -> [('引っ越し', 'ひっこし', 'range')]
    """
    reading_hira = kata_to_hira(reading_kata)

    # surface 中の文字を漢字 / 非漢字 で分類してチャンクに分ける
    chunks: list[tuple[str, bool]] = []  # (text, is_kanji)
    cur_text = ""
    cur_is_kanji: bool | None = None
    for ch in surface:
        is_k = bool(KANJI_RE.match(ch))
        if cur_is_kanji is None:
            cur_text = ch
            cur_is_kanji = is_k
        elif is_k == cur_is_kanji:
            cur_text += ch
        else:
            chunks.append((cur_text, cur_is_kanji))
            cur_text = ch
            cur_is_kanji = is_k
    if cur_text:
        chunks.append((cur_text, cur_is_kanji or False))

    # 漢字を含まない形態素はそのまま
    if not any(is_k for _, is_k in chunks):
        return [(surface, None, "plain")]

    # 読みがない (空) または surface とまるごと一致 → ルビ不要 (例: 全部カタカナ)
    if not reading_hira:
        return [(surface, None, "plain")]
    if reading_hira == surface:
        return [(surface, None, "plain")]

    # 漢字チャンクが 2個以上 → 範囲指定ルビ (形態素全体に1つの読み)
    kanji_chunks = [c for c, k in chunks if k]
    if len(kanji_chunks) >= 2:
        return [(surface, reading_hira, "range")]

    # 漢字チャンクが 1個のみ: 既存ロジックで分解
    # 漢字チャンク前後の非漢字を読みから引いて、漢字部分の読みを抽出
    kanji_idx = next(i for i, (_, k) in enumerate(chunks) if k)
    leading = "".join(c for c, k in chunks[:kanji_idx] if not k)
    trailing = "".join(c for c, k in chunks[kanji_idx + 1:] if not k)
    kanji_text = chunks[kanji_idx][0]

    rem = reading_hira
    # 先頭の非漢字を引く
    if leading:
        lead_hira = kata_to_hira(leading)
        if rem.startswith(lead_hira):
            rem = rem[len(lead_hira):]
        elif rem.startswith(leading):
            rem = rem[len(leading):]
        else:
            # マッチしない → 範囲指定にフォールバック
            return [(surface, reading_hira, "range")]
    # 末尾の非漢字を引く
    if trailing:
        trail_hira = kata_to_hira(trailing)
        if rem.endswith(trail_hira):
            rem = rem[: -len(trail_hira)]
        elif rem.endswith(trailing):
            rem = rem[: -len(trailing)]
        else:
            return [(surface, reading_hira, "range")]

    out: list[tuple[str, str | None, str]] = []
    if leading:
        out.append((leading, None, "plain"))
    if rem:
        out.append((kanji_text, rem, "normal"))
    else:
        # 読みが空になった → ルビなし扱い (普通は発生しない)
        out.append((kanji_text, None, "plain"))
    if trailing:
        out.append((trailing, None, "plain"))
    return out


def morphs_to_ruby(morphs: list[tuple[str, str]]) -> str:
    """形態素のリスト → 青空文庫ルビ文字列。

    `range` セグメントは `｜text《ruby》` 形式 (青空文庫範囲指定)。
    """
    parts: list[str] = []
    for surface, reading in morphs:
        if not has_kanji(surface):
            parts.append(surface)
            continue
        segs = split_morph_to_kanji_and_kana(surface, reading)
        for text, ruby, kind in segs:
            if ruby is None:
                parts.append(text)
            elif kind == "range":
                parts.append(f"｜{text}《{ruby}》")
            else:  # normal
                parts.append(f"{text}《{ruby}》")
    return "".join(parts)


def sudachi_ruby(text: str) -> str:
    return morphs_to_ruby(sudachi_morphs(text))


def mecab_ruby(text: str) -> str:
    return morphs_to_ruby(mecab_morphs(text))


# ===== 比較・不一致抽出 =====


def extract_ruby_pairs(ruby_text: str) -> list[tuple[str, str]]:
    """ルビ文字列から (漢字, 読み) のペアを抽出。"""
    pattern = re.compile(r"([一-鿿々]+)《([぀-ゟ]+)》")
    return pattern.findall(ruby_text)


def extract_kanji_groups(ruby_text: str) -> list[tuple[str, str]]:
    """連続する `漢字《読み》` を結合して 1 グループにする。
    粒度違いを吸収するため、隣接ルビ・送り仮名なしでつながる漢字塊をまとめる。

    青空文庫の範囲指定 `｜...《...》` は除外する (漢字単位ではないため)。

    例: "目撃《もくげき》者《しゃ》の話《はなし》"
        -> [("目撃者", "もくげきしゃ"), ("話", "はなし")]
    """
    # ｜...《...》 範囲指定をまず除去
    sanitized = re.sub(r"｜[^《》]+《[぀-ゟ]+》", "", ruby_text)

    groups: list[tuple[str, str]] = []
    chain_re = re.compile(r"([一-鿿々]+)《([぀-ゟ]+)》")

    pos = 0
    while pos < len(sanitized):
        m = chain_re.match(sanitized, pos)
        if not m:
            pos += 1
            continue
        kanji = m.group(1)
        reading = m.group(2)
        end = m.end()
        while end < len(sanitized):
            m2 = chain_re.match(sanitized, end)
            if not m2:
                break
            kanji += m2.group(1)
            reading += m2.group(2)
            end = m2.end()
        groups.append((kanji, reading))
        pos = end
    return groups


def compare_rubies(a: str, b: str) -> tuple[bool, list[tuple[str, str | None, str | None]]]:
    """2つのルビ文字列を比較。粒度違いは漢字グループ結合で吸収して比較する。

    返り値: (a == b ?, 不一致 [(漢字塊, A読み, B読み)])
    """
    pa = dict(extract_kanji_groups(a))
    pb = dict(extract_kanji_groups(b))
    all_kanji = set(pa.keys()) | set(pb.keys())
    diffs = []
    for k in all_kanji:
        ra = pa.get(k)
        rb = pb.get(k)
        if ra != rb:
            diffs.append((k, ra, rb))
    return (a == b, diffs)


if __name__ == "__main__":
    # スモークテスト
    samples = [
        "監視カメラの映像が目撃者の話を裏付けた。",
        "私が初めてピアノを弾いたのは、5年前のことでした。",
        "今日の議題の最大の争点は、リモートワークを継続するかどうかだ。",
        "教授は『記憶は感情に依存する』と仮説を立て、3年がかりの実験を組んだ。",
        "新組織は5つの部門を構成する設計だ。",
    ]
    for s in samples:
        sa = sudachi_ruby(s)
        ma = mecab_ruby(s)
        same, diffs = compare_rubies(sa, ma)
        print(f"\n[{'OK' if same else 'DIFF'}] {s}")
        print(f"  sud: {sa}")
        print(f"  mec: {ma}")
        if diffs:
            for k, ra, rb in diffs:
                print(f"  !!  {k}: sud={ra}  mec={rb}")
