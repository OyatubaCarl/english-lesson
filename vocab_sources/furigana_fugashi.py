"""高精度ふりがな(青空ルビ 漢字《かな》形式)生成 — fugashi + unidic-lite 版。

pykakasi(add_furigana.py)は複合語の読みを誤りやすい(例: 借入→しゃくにゅう)。
本モジュールは形態素解析に fugashi(unidic-lite) を使い、読み精度を上げる。
送り仮名整合・OVERRIDES・数量詞・<word>埋め込み保護は add_furigana の資産を再利用する。

依存: fugashi, unidic-lite  (.venv に導入済み。無ければ
      /Users/masaki/Documents/ClaudeCode/英語学習教材作成/.venv/bin/python -m pip install fugashi unidic-lite)

使い方(モジュール):
    from furigana_fugashi import to_aozora
    to_aozora("借入契約では在庫を<collateral>に含める。")
    # -> 借入《かりいれ》契約《けいやく》では在庫《ざいこ》を<collateral>に含《ふく》める。

使い方(CLI・1文テスト):
    python furigana_fugashi.py "文字列..."
"""
from __future__ import annotations
import re
import sys

import add_furigana as af  # chunk_to_aozora / COUNTERS / OVERRIDES を再利用(単一の正)
from fugashi import Tagger

_tagger = Tagger()


def _kata_to_hira(s: str) -> str:
    return "".join(chr(ord(c) - 0x60) if "ァ" <= c <= "ヴ" else c for c in (s or ""))


def _reading_of(morph) -> str:
    """fugashi形態素の読み(ひらがな)。取れなければ表層をそのまま。"""
    kana = getattr(morph.feature, "kana", None)
    if kana and kana != "*":
        return _kata_to_hira(kana)
    return morph.surface


# 英字(ラテン)の連なり。内部の空白・区切りごと保護する(fugashiが空白を落とすのを防ぐ)。
# マーカーは英字を含めない(このステップ自身が英字を再取得しないように)。
_LATIN = re.compile(r"[A-Za-z][A-Za-z0-9 .,'’/&\-]*[A-Za-z0-9]|[A-Za-z]")


def to_aozora(text: str) -> str:
    """文を青空ルビ(漢字《かな》)化。<word>埋め込み・英字語・数量詞・OVERRIDESは保護。"""
    # 1) <word> 埋め込みを退避(マーカーは数字のみ)
    embeds: list[str] = []

    def _stash_embed(m):
        embeds.append(m.group(0))
        return f"⟦{len(embeds) - 1}⟧"

    text = re.sub(r"<[^>]+>", _stash_embed, text)

    # 2) 英字語(語源のラテン/英語, 内部空白ごと)を退避 — ルビ不要 & 空白消失を防ぐ
    latins: list[str] = []

    def _stash_latin(m):
        latins.append(m.group(0))
        return f"〘{len(latins) - 1}〙"

    text = _LATIN.sub(_stash_latin, text)

    protected: list[str] = []

    # 3) 数字+助数詞を保護(add_furigana と同じ)
    for counter, reading in af.COUNTERS:
        def _repl_counter(m, c=counter, r=reading):
            protected.append(f"{m.group(1)}{c}《{r}》")
            return f"〔{len(protected) - 1}〕"

        text = re.sub(r"(\d+)" + re.escape(counter), _repl_counter, text)

    # 4) OVERRIDES(手動修正の正)を長い順に保護
    for pat, repl in sorted(af.OVERRIDES, key=lambda x: -len(x[0])):
        def _repl_override(m, r=repl):
            protected.append(m.expand(r))
            return f"〔{len(protected) - 1}〕"

        text = re.sub(pat, _repl_override, text)

    # 5) fugashi で分かち書き → 単語ごとに送り仮名整合してルビ化
    out = []
    for m in _tagger(text):
        out.append(af.chunk_to_aozora(m.surface, _reading_of(m)))
    text = "".join(out)

    # 6) 退避を戻す(保護→英字→埋め込みの順)
    for i in range(len(protected) - 1, -1, -1):
        text = text.replace(f"〔{i}〕", protected[i])
    for i in range(len(latins) - 1, -1, -1):
        text = text.replace(f"〘{i}〙", latins[i])
    for i in range(len(embeds) - 1, -1, -1):
        text = text.replace(f"⟦{i}⟧", embeds[i])
    return text


if __name__ == "__main__":
    for s in (sys.argv[1:] or ["借入契約では在庫を<collateral>に含める。"]):
        print(to_aozora(s))
