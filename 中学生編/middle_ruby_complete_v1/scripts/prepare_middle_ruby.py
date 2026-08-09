#!/usr/bin/env python3
"""Prepare mixed-Japanese captions with complete kanji and English ruby.

The existing lesson text, audio timing, and story images remain untouched.
This script creates a separate caption manifest for L1-L45.
"""

from __future__ import annotations

import html as htmlmod
import json
import re
import sys
from pathlib import Path

from fugashi import Tagger


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MIDDLE = ROOT.parent
PROJECT = MIDDLE.parent
LESSON_DATA = PROJECT / "taco_course_mockup" / "middle_lessons.json"
SOURCE_HTML = PROJECT / "index.html"
L1_FIXED = MIDDLE / "l1_mixed_translation_comparison" / "planning" / "mixed_translation.json"
OUT_DIR = ROOT / "planning" / "lessons"
REVIEW_PATH = ROOT / "planning" / "mixed_translation_review.md"
INLINE_MIXED_PATH = ROOT / "planning" / "inline_mixed_overrides.json"

sys.path.insert(0, str(PROJECT / "vocab_sources"))
from furigana_fugashi import to_aozora  # noqa: E402


KANJI_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff々ヶ]")
AOZORA_RE = re.compile(
    r"(?:｜([^《》]+)|([\u3400-\u4dbf\u4e00-\u9fff々ヶ]+))《([^》]+)》"
)
EN_TOKEN_RE = re.compile(r"[A-Za-z]+(?:['’-][A-Za-z]+)?")
TAGGER = Tagger()
CONTENT_POS = {"名詞", "動詞", "形容詞", "形状詞", "副詞", "連体詞", "代名詞", "感動詞"}
GENERIC_MORPH_KEYS = {"する", "為る", "いる", "居る", "ある", "有る", "なる", "成る"}
DIRECT_WEAVE_POS = {
    "noun", "num", "adj", "verb", "adv", "prep", "conj", "det", "phrase"
}
POS_OVERRIDES = {
    "twelve": "num",
    "bouquet": "noun",
    "card": "noun",
    "bought": "verb",
}

STOPWORDS = {
    "a", "an", "the", "of", "to", "in", "on", "at", "for", "with", "by", "from",
    "is", "am", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "will", "would", "can", "could", "should", "may", "might",
    "must", "and", "but", "or", "so", "that", "this", "these", "those", "it", "i",
    "my", "me", "we", "our", "you", "your", "he", "his", "him", "she", "her", "they",
    "their", "them", "as", "if", "while", "than", "who", "which", "what", "where",
}

PROPER_NAMES = {
    "Mio": "ミオ",
    "Tom": "トム",
    "Pochi": "ポチ",
    "Saki": "サキ",
    "Kenta": "ケンタ",
}

PHRASE_ROWS = [
    ("Thank you", "ありがとう"),
    ("Every morning", "毎朝"),
    ("a little", "少しずつ"),
    ("all day", "一日中"),
    ("new boy", "新しい男の子"),
    ("very happy", "とてもうれしい"),
    ("same house", "同じ家"),
    ("quiet afternoon", "静かな午後"),
    ("special gifts", "特別な贈り物"),
    ("birthday card", "誕生日カード"),
    ("funny story", "面白い話"),
    ("good teacher", "良い先生"),
    ("important language", "大切な言葉"),
    ("important promise", "大切な約束"),
    ("quiet place", "静かな場所"),
    ("small voice", "小さな声"),
    ("sweet smell", "甘い香り"),
    ("old stamps", "古い切手"),
    ("favorite book", "お気に入りの本"),
    ("beautiful park", "美しい公園"),
    ("small pond", "小さな池"),
    ("old rock", "古い岩"),
    ("sunny summer day", "晴れた夏の日"),
    ("Cherry flowers", "桜の花"),
    ("new recipe", "新しいレシピ"),
    ("whole body", "体全体"),
]

# Corrections are applied only to this new caption edition.  L6 is deliberately
# absent because the user asked to retain its current lesson text.
JA_CORRECTIONS: dict[tuple[int, int], str] = {
    (34, 10): "「しばらく無理をしないでください」と、お医者さんは言いました。",
    (36, 3): "大きな目をした一頭の牛が、わたしたちを見ていました。",
    (36, 4): "一頭の豚が柵の後ろで鼻を動かしていました。",
    (36, 5): "柔らかな白い毛の羊が草を食べていました。",
    (39, 6): "父は古い写真を指さしました。",
    (39, 7): "「100年前、人々はこのような正確な時計を持っていませんでした。」",
    (39, 8): "過去の時間について考えると、わたしは少し不思議な気持ちになります。",
}

# Lines for which an exact, natural replacement cannot be derived safely from
# the project dictionaries.  Each English segment is copied from the sung line.
MANUAL_MIXED: dict[tuple[int, int], dict] = {
    (2, 8): {"mixed": "わたしたちは all day いっしょでした。", "ruby": {"all day": "一日中"}},
    (2, 10): {"mixed": "とても delicious でした。", "ruby": {"delicious": "おいしい"}},
    (4, 4): {"mixed": "At first、彼は shy で、あまり話しませんでした。", "ruby": {"At first": "初めは", "shy": "恥ずかしそう"}},
    (4, 9): {"mixed": "でも、わたしは very happy でした。", "ruby": {"very happy": "とてもうれしい"}},
    (5, 7): {"mixed": "きっと祖母は very happy でしょう。", "ruby": {"very happy": "とてもうれしい"}},
    (6, 7): {"mixed": "Grandmother はわたしたちに warm smile を見せ、「Thank you both.」と言いました。", "ruby": {"Grandmother": "祖母", "warm smile": "温かな笑顔", "Thank you both": "二人ともありがとう"}},
    (10, 9): {"mixed": "とても dangerous だからです。", "ruby": {"dangerous": "危険"}},
    (11, 5): {"mixed": "「Yes, you may.」と彼は smile で答えました。", "ruby": {"Yes, you may": "いいですよ", "smile": "笑顔"}},
    (12, 7): {"mixed": "「Shall we eat now?」と father が言いました。", "ruby": {"Shall we eat now": "さあ食べようか", "father": "父"}},
    (13, 7): {"mixed": "「これは Grandfather からだ」と彼は一枚ずつ care を込めて見せました。", "ruby": {"Grandfather": "祖父", "care": "大切に"}},
    (21, 5): {"mixed": "わたしも myself について a little 話しました。", "ruby": {"myself": "自分自身", "a little": "少し"}},
    (24, 2): {"mixed": "でも、what to take も where to stay も、まだわかりません。", "ruby": {"what to take": "何を持つか", "where to stay": "どこに泊まるか"}},
    (24, 5): {"mixed": "「Not much.」", "ruby": {"Not much": "そんなに多くない"}},
    (25, 4): {"mixed": "でも、he keeps trying ので、だんだん strong になっています。", "ruby": {"he keeps trying": "彼は努力を続ける", "strong": "強い"}},
    (26, 7): {"mixed": "わたしは grandmother にも long time、happily 暮らしてほしいです。", "ruby": {"grandmother": "祖母", "long time": "長い間", "happily": "幸せに"}},
    (27, 7): {"mixed": "でも、him には easily 聞けませんでした。", "ruby": {"him": "彼", "easily": "簡単に"}},
    (31, 12): {"mixed": "「How beautiful!」", "ruby": {"How beautiful": "なんてきれい"}},
    (32, 4): {"mixed": "Grandfather は last month から a little sick です。", "ruby": {"Grandfather": "祖父", "last month": "先月", "a little sick": "少し体調が悪い"}},
    (34, 10): {"mixed": "「Please don't push yourself for a while.」と doctor は言いました。", "ruby": {"Please don't push yourself for a while": "しばらく無理をしないでください", "doctor": "医師"}},
    (36, 4): {"mixed": "一頭の pig が fence の後ろで nose を動かしていました。", "ruby": {"pig": "豚", "fence": "柵", "nose": "鼻"}},
    (39, 7): {"mixed": "「A century ago、人々はこのような accurate な clocks を持っていませんでした。」", "ruby": {"A century ago": "100年前", "accurate": "正確な", "clocks": "時計"}},
    (42, 7): {"mixed": "「Nice catch!」と brother が叫びました。", "ruby": {"Nice catch": "うまく捕った", "brother": "兄"}},
    (42, 11): {"mixed": "「It is okay to lose.」", "ruby": {"It is okay to lose": "負けても大丈夫"}},
    (44, 4): {"mixed": "それを receive して、わたしは surprised and happy になりました。", "ruby": {"receive": "受け取る", "surprised and happy": "驚いてうれしい"}},
}

# Carefully reviewed exceptions for canonical words whose Japanese source uses
# a synonym, making automatic span replacement unsafe.  Every English form
# below occurs in the sung line and maps to the current lesson's canonical
# vocabulary; these are not whole-course fallbacks.
CANONICAL_MANUAL_MIXED: dict[tuple[int, int], dict] = {
    (18, 9): {"mixed": "わたしには、数学は英語ほど easy ではありません。", "ruby": {"easy": "簡単"}},
    (21, 2): {"mixed": "「わたしは60年間、この家に lived。」と祖母は静かに言いました。", "ruby": {"lived": "住んできた"}},
    (21, 6): {"mixed": "「生まれてからずっと、この町に lived。", "ruby": {"lived": "住んできた"}},
    (27, 1): {"mixed": "雨の日曜日、窓辺に座って、いろいろなことについて wondered。", "ruby": {"wondered": "思いをめぐらせた"}},
    (27, 3): {"mixed": "妹がなぜ泣いていたのかを understand したかったです。", "ruby": {"understand": "理解する"}},
    (27, 4): {"mixed": "母が夕食に何を作っていたのか、guess してみました。", "ruby": {"guess": "推測する"}},
    (27, 6): {"mixed": "父が若い頃どこで学んだのかを、長い間 wondered。", "ruby": {"wondered": "気になっていた"}},
    (27, 8): {"mixed": "今日は try します。", "ruby": {"try": "試みる"}},
    (27, 10): {"mixed": "try するたび、周りの世界が少し広がるように見えます。", "ruby": {"try": "試みる"}},
    (29, 8): {"mixed": "本を選ぶときは、表紙と title をよく見ます。", "ruby": {"title": "題名"}},
    (44, 1): {"mixed": "雨の土曜日、分厚い封筒が郵便受けに arrived。", "ruby": {"arrived": "届いた"}},
    (44, 4): {"mixed": "それを receive して、驚き、うれしくなりました。", "ruby": {"receive": "受け取る"}},
    (44, 6): {"mixed": "最後に「あなたの reply を待っています」と書かれていました。", "ruby": {"reply": "返事"}},
    (44, 7): {"mixed": "机に向かい、すぐに reply を書き始めました。", "ruby": {"reply": "返事"}},
    (44, 8): {"mixed": "手紙は、メールや電話とは違う、ゆっくり communicate する方法です。", "ruby": {"communicate": "伝える"}},
}


def source_config(lesson: int) -> Path:
    if lesson == 6:
        return MIDDLE / "mio_video_l2_l10_sentence_v2" / "L6_revision_v3" / "planning" / "lesson.json"
    if 2 <= lesson <= 10:
        return MIDDLE / "mio_video_l2_l10_sentence_v2" / f"L{lesson}" / "planning" / "lesson.json"
    return MIDDLE / "mio_video_l1_l45_sentence_v3" / f"L{lesson}" / "planning" / "lesson.json"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_en(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


IRREGULAR_BASE = {
    "bought": "buy",
    "came": "come",
    "cried": "cry",
    "did": "do",
    "done": "do",
    "drank": "drink",
    "eaten": "eat",
    "felt": "feel",
    "gave": "give",
    "gone": "go",
    "had": "have",
    "knew": "know",
    "known": "know",
    "made": "make",
    "paid": "pay",
    "ran": "run",
    "said": "say",
    "saw": "see",
    "seen": "see",
    "spoke": "speak",
    "spoken": "speak",
    "swam": "swim",
    "swum": "swim",
    "taught": "teach",
    "thought": "think",
    "threw": "throw",
    "thrown": "throw",
    "told": "tell",
    "took": "take",
    "taken": "take",
    "understood": "understand",
    "went": "go",
    "written": "write",
    "wrote": "write",
}
DERIVED_BASE = {
    "biggest": "big",
    "cheaper": "cheap",
    "easily": "easy",
    "fastest": "fast",
    "happily": "happy",
    "longer": "long",
    "peacefully": "peaceful",
    "warmer": "warm",
    "younger": "young",
}


def stems(text: str) -> set[str]:
    word = normalize_en(text)
    result = {word, IRREGULAR_BASE.get(word, word), DERIVED_BASE.get(word, word)}
    for suffix, replacement in (
        ("ies", "y"),
        ("ing", ""),
        ("ed", ""),
        ("es", ""),
        ("s", ""),
    ):
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            base = word[: -len(suffix)] + replacement
            result.add(base)
            if suffix in {"ing", "ed"}:
                result.add(word[: -len(suffix)] + "e")
                # planning / swimming / running: undo the doubled consonant.
                if len(base) >= 2 and base[-1] == base[-2]:
                    result.add(base[:-1])
    return result


def japanese_candidates(value: str) -> list[str]:
    value = re.sub(r"\([^)]*\)|（[^）]*）", "", value).strip()
    value = value.replace("〜", "")
    pieces = [value]
    for separator in ("・", "／", "/", "、", ";", "；"):
        pieces = [piece for item in pieces for piece in item.split(separator)]
    output = set()
    for piece in pieces:
        piece = piece.strip()
        piece = re.sub(r"^(とても|非常に|すごく)", "", piece)
        if not piece:
            continue
        if len(piece) == 1 and re.fullmatch(r"[ぁ-ん]", piece):
            continue
        output.add(piece)
    return sorted(output, key=len, reverse=True)


def canonical_pos_index() -> dict[tuple[str, str], str]:
    """Read the author-assigned part of speech without changing shared JSON."""
    source = SOURCE_HTML.read_text(encoding="utf-8")
    start = source.index('id="book-middle"')
    stop = source.find('id="book-high1"', start)
    segment = source[start : stop if stop >= 0 else len(source)]
    output = {}
    for attrs, body in re.findall(r'<span class="w"([^>]*)>([\s\S]*?)</span>', segment):
        def attribute(name: str) -> str:
            match = re.search(rf'{name}="([^"]*)"', attrs)
            return htmlmod.unescape(match.group(1)) if match else ""

        word = htmlmod.unescape(re.sub(r"<[^>]+>", "", body)).strip()
        meaning = attribute("data-ja")
        if word and meaning:
            output[(word.lower(), meaning)] = attribute("data-pos")
    return output


def is_tomatomato_proper_noun(word: str, meaning: str) -> bool:
    """Use the same proper-name rule as TacosParty's buildMiddleLesson."""
    word = str(word or "").strip()
    if not word or not word[0].isupper() or word.lower() == "tv":
        return False
    if re.search(r"[.\s]", word):
        return True
    return bool(re.fullmatch(r"[ァ-ヶー・\s]+", str(meaning or "").strip()))


def build_dictionary(lesson_data: list[dict]) -> tuple[dict[str, list[dict]], dict[int, list[dict]]]:
    """Build a lesson-local canonical glossary.

    Mixed captions are a teaching layer for each lesson's new vocabulary.  A
    whole-course or WordTacos fallback makes familiar words displace the new
    words, so the returned global index is deliberately empty.
    """
    pos_index = canonical_pos_index()
    lesson_rows: dict[int, list[dict]] = {}
    for lesson in lesson_data:
        number = int(lesson["b"])
        rows = []
        seen = set()
        for paragraph in lesson["vocabSentences"]:
            for item in paragraph["words"]:
                key = item["w"].strip().lower().replace("’", "'")
                if key in seen or is_tomatomato_proper_noun(item["w"], item["ja"]):
                    continue
                seen.add(key)
                row = {
                    "word": item["w"],
                    "ja": item["ja"],
                    "pos": POS_OVERRIDES.get(
                        item["w"].lower(),
                        pos_index.get((item["w"].lower(), item["ja"]), ""),
                    ),
                    "priority": 10,
                    "source": "canonical_new_word",
                }
                rows.append(row)
        lesson_rows[number] = rows
    return {}, lesson_rows


def sentence_tokens(english: str) -> list[str]:
    return EN_TOKEN_RE.findall(english)


def english_targets(english: str, local_rows: list[dict]) -> list[dict]:
    """Return only canonical new words that actually occur in the sung line."""
    tokens = sentence_tokens(english)
    normalized_tokens = [normalize_en(token) for token in tokens]
    candidates = []
    for row in local_rows:
        row_tokens = sentence_tokens(row["word"])
        if not row_tokens:
            continue
        if len(row_tokens) == 1:
            for order, token in enumerate(tokens):
                if stems(token) & stems(row["word"]):
                    candidates.append(
                        {
                            "english": token,
                            "row": row,
                            "token_orders": (order,),
                            "match_score": (
                                200
                                if normalize_en(token) == normalize_en(row["word"])
                                else 100
                            ),
                        }
                    )
            continue
        wanted = [normalize_en(token) for token in row_tokens]
        for start in range(len(tokens) - len(wanted) + 1):
            if normalized_tokens[start : start + len(wanted)] == wanted:
                candidates.append(
                    {
                        "english": " ".join(tokens[start : start + len(wanted)]),
                        "row": row,
                        "token_orders": tuple(range(start, start + len(wanted))),
                        "match_score": 300 + len(wanted),
                    }
                )
    # One sung token belongs to one canonical target.  Prefer exact and phrase
    # matches so friendly is not also misread as friend, or teacher as teach.
    selected = []
    used_orders: set[int] = set()
    used_words: set[str] = set()
    for candidate in sorted(
        candidates,
        key=lambda item: (item["match_score"], len(item["row"]["word"])),
        reverse=True,
    ):
        if used_orders.intersection(candidate["token_orders"]):
            continue
        word_key = normalize_en(candidate["row"]["word"])
        if word_key in used_words:
            continue
        used_orders.update(candidate["token_orders"])
        used_words.add(word_key)
        candidate.pop("match_score", None)
        selected.append(candidate)
    return sorted(selected, key=lambda item: item["token_orders"][0])


def _morph_key(morph) -> str:
    value = (
        getattr(morph.feature, "orthBase", None)
        or getattr(morph.feature, "lemma", None)
        or morph.surface
    )
    return value.replace("気付", "気づ").replace("心地良", "心地よ")


def japanese_morphs(text: str) -> list[dict]:
    output = []
    cursor = 0
    for morph in TAGGER(text):
        start = cursor
        cursor += len(morph.surface)
        pos = getattr(morph.feature, "pos1", "")
        output.append(
            {
                "surface": morph.surface,
                "start": start,
                "end": cursor,
                "pos": pos,
                "key": _morph_key(morph),
                "content": pos in CONTENT_POS,
            }
        )
    return output


def japanese_morph_span(japanese: str, glossary_surface: str) -> tuple[int, int, str] | None:
    """Match inflectional variants such as 溶けた／溶けました safely."""
    sentence = japanese_morphs(japanese)
    glossary = [item for item in japanese_morphs(glossary_surface) if item["content"]]
    if not glossary:
        return None
    wanted = [item["key"] for item in glossary]
    if set(wanted) <= GENERIC_MORPH_KEYS:
        return None
    content = [(index, item) for index, item in enumerate(sentence) if item["content"]]
    for content_start in range(len(content) - len(wanted) + 1):
        window = content[content_start : content_start + len(wanted)]
        if [item["key"] for _, item in window] != wanted:
            continue
        first_index = window[0][0]
        last_index = window[-1][0]
        start = sentence[first_index]["start"]
        end = sentence[last_index]["end"]
        last_pos = glossary[-1]["pos"]
        verbal = last_pos in {"動詞", "形容詞", "形状詞"} or any(
            item["key"] == "する" for item in glossary
        )
        suffix = ""
        if verbal:
            cursor = last_index + 1
            # na-adjective + に + なる already contains the correct linker;
            # leave it outside the replaced span: 穏やかになった -> calm になった.
            if (
                last_pos == "形状詞"
                and cursor + 1 < len(sentence)
                and sentence[cursor]["surface"] == "に"
                and sentence[cursor + 1]["pos"] == "動詞"
                and sentence[cursor + 1]["key"] in {"なる", "成る"}
            ):
                return start, end, suffix
            # i-adjective + なる needs the Japanese linking に after the
            # English adjective: 優しくなった -> gentle になった.
            if (
                last_pos == "形容詞"
                and cursor < len(sentence)
                and sentence[cursor]["pos"] == "動詞"
                and sentence[cursor]["key"] in {"なる", "成る"}
            ):
                suffix = "に"
                return start, end, suffix
            while cursor < len(sentence):
                item = sentence[cursor]
                auxiliary_verb = item["pos"] == "動詞" and item["key"] in {
                    "いる", "居る", "ある", "有る", "しまう", "来る", "くる",
                    "いく", "行く",
                }
                connective = item["pos"] == "助詞" and item["surface"] in {"て", "で"}
                if last_pos == "形状詞" and item["surface"] == "で":
                    later_content = next(
                        (later for later in sentence[cursor + 1 :] if later["content"]),
                        None,
                    )
                    if later_content:
                        end = item["end"]
                        suffix = "で" if japanese[end:].startswith("、") else "で、"
                        return start, end, suffix
                if connective:
                    later_content = next(
                        (
                            later
                            for later in sentence[cursor + 1 :]
                            if later["content"]
                        ),
                        None,
                    )
                    if later_content and not (
                        later_content["pos"] == "動詞"
                        and later_content["key"] in {
                            "いる", "居る", "ある", "有る", "しまう", "来る", "くる",
                            "いく", "行く",
                        }
                    ):
                        if last_pos in {"形容詞", "形状詞"}:
                            end = item["end"]
                            suffix = "で、"
                            return start, end, suffix
                        return None
                if item["pos"] == "助動詞" or auxiliary_verb or connective:
                    end = item["end"]
                    cursor += 1
                    continue
                break
            # A bare English predicate followed by a Japanese conjunction is
            # generally ungrammatical (e.g. tired が).  Keep such lines in
            # Japanese unless a safe copular form can be built.
            if japanese[end:].startswith(("が", "けれど", "けれども", "のに")):
                return None
            removed = japanese[start:end]
            if (
                last_pos == "動詞"
                and removed.endswith(("よう", "そう"))
                and japanese[end:].startswith("として")
            ):
                suffix = "しよう"
            if last_pos in {"形容詞", "形状詞"} and not suffix:
                if re.search(r"(?:かった|でした|だった)(?:です)?$", removed):
                    suffix = "でした"
                elif re.search(r"(?:です|だ)$", removed):
                    suffix = "です"
                elif last_pos == "形容詞" and removed.endswith("く") and japanese[end:].startswith("、"):
                    suffix = "で"
        return start, end, suffix
    return None


def direct_weave_suffix(pos: str, removed: str, following: str) -> str:
    """Keep TeacherTacos-style Japanese grammar after an inline English word."""
    if pos != "verb":
        return ""
    if removed.endswith(("ませんでした", "なかった")):
        return " しませんでした"
    if removed.endswith(("ません", "ない")):
        return " しません"
    if removed.endswith("なけれ") and following.startswith("ば"):
        return " しなけれ"
    if removed.endswith(("ていました", "でいました")):
        return " していました"
    if removed.endswith(("ています", "でいます")):
        return " しています"
    if removed.endswith(("ていた", "でいた")):
        return " していました"
    if removed.endswith(("ている", "でいる")):
        return " しています"
    if removed.endswith("ました"):
        return " しました"
    if removed.endswith("ます"):
        return " します"
    if removed.endswith(("て", "で")):
        return " して"
    if following.startswith(("こと", "とき", "時", "ため", "よう")):
        return " する"
    if removed.endswith(("た", "だ")):
        return " しました"
    return " する"


def find_candidates(english: str, japanese: str, global_index: dict, local_rows: list[dict]) -> list[dict]:
    """Find safe Japanese spans for current-lesson canonical words only."""
    candidates = []
    sentence_morphs = japanese_morphs(japanese)
    morph_boundaries = {0, len(japanese)}
    for morph in sentence_morphs:
        morph_boundaries.add(morph["start"])
        morph_boundaries.add(morph["end"])
    for target in english_targets(english, local_rows):
        row = target["row"]
        if row.get("pos") not in DIRECT_WEAVE_POS:
            continue
        exact_matches = []
        for surface in japanese_candidates(row["ja"]):
            for match in re.finditer(re.escape(surface), japanese):
                if match.start() not in morph_boundaries or match.end() not in morph_boundaries:
                    continue
                if len(surface) == 1 and KANJI_RE.fullmatch(surface):
                    before = japanese[match.start() - 1] if match.start() else ""
                    after = japanese[match.end()] if match.end() < len(japanese) else ""
                    if KANJI_RE.fullmatch(before) or KANJI_RE.fullmatch(after):
                        continue
                surface_morphs = [
                    item
                    for item in sentence_morphs
                    if item["start"] >= match.start()
                    and item["end"] <= match.end()
                    and item["content"]
                ]
                last_pos = surface_morphs[-1]["pos"] if surface_morphs else ""
                if (
                    last_pos in {"動詞", "形容詞", "形状詞"}
                    and japanese[match.end() :].startswith(("が", "けれど", "けれども", "のに"))
                ):
                    continue
                if last_pos == "動詞" and japanese[match.end() :].startswith(("んだ", "のだ")):
                    continue
                suffix = direct_weave_suffix(
                    "verb" if last_pos == "動詞" else row.get("pos", "") if not last_pos else "",
                    japanese[match.start() : match.end()],
                    japanese[match.end() :],
                )
                exact_matches.append((match.start(), match.end(), suffix))
        if exact_matches:
            spans = [(*match, "canonical_new_word_exact") for match in exact_matches]
        else:
            spans = []
            for surface in japanese_candidates(row["ja"]):
                match = japanese_morph_span(japanese, surface)
                if match:
                    start, end, suffix = match
                    suffix = suffix or direct_weave_suffix(
                        row.get("pos", ""), japanese[start:end], japanese[end:]
                    )
                    spans.append((start, end, suffix, "canonical_new_word_morph"))
                    break
        for start, end, suffix, source in spans:
            content_morphs = [
                item
                for item in sentence_morphs
                if item["start"] >= start and item["end"] <= end and item["content"]
            ]
            surface_pos = content_morphs[-1]["pos"] if content_morphs else ""
            compatible = {
                "noun": {"名詞", "代名詞"},
                "num": {"名詞", "数詞"},
                "adj": {"形容詞", "形状詞", "連体詞"},
                "verb": {"動詞", "名詞", "形容詞", "形状詞"},
                "adv": {"副詞", "名詞", "形容詞", "形状詞"},
                "prep": {"名詞", "副詞", "助詞"},
                "conj": {"接続詞", "助詞", "名詞"},
                "det": {"連体詞", "名詞", "形容詞"},
                "phrase": {"名詞", "副詞", "接続詞"},
            }
            if surface_pos not in compatible.get(row.get("pos"), set()):
                continue
            candidates.append(
                {
                    "start": start,
                    "end": end,
                    "surface": japanese[start:end],
                    "english": target["english"],
                    "reading": japanese[start:end],
                    "priority": row["priority"] + int(source.endswith("exact")),
                    "source": source,
                    "canonical_word": row["word"],
                    "canonical_meaning": row["ja"],
                    "suffix": suffix,
                    "token_orders": target["token_orders"],
                }
            )
    candidates.sort(
        key=lambda item: (
            item["priority"],
            len(item["surface"]),
            len(item["english"]),
            -item["token_orders"][0],
        ),
        reverse=True,
    )
    selected = []
    occupied: list[tuple[int, int]] = []
    used_tokens: set[int] = set()
    for item in candidates:
        if used_tokens.intersection(item["token_orders"]):
            continue
        if any(item["start"] < stop and start < item["end"] for start, stop in occupied):
            continue
        selected.append(item)
        occupied.append((item["start"], item["end"]))
        used_tokens.update(item["token_orders"])
    return sorted(selected, key=lambda item: item["start"])


def japanese_parts(text: str) -> list[dict]:
    if not text:
        return []
    aozora = to_aozora(text)
    parts = []
    cursor = 0
    for match in AOZORA_RE.finditer(aozora):
        if match.start() > cursor:
            parts.append({"text": aozora[cursor : match.start()], "ruby": ""})
        parts.append({"text": match.group(1) or match.group(2), "ruby": match.group(3)})
        cursor = match.end()
    if cursor < len(aozora):
        parts.append({"text": aozora[cursor:], "ruby": ""})

    uncovered = []
    for part in parts:
        if not part["ruby"]:
            uncovered.extend(KANJI_RE.findall(part["text"]))
    if uncovered:
        raise RuntimeError(f"Uncovered kanji in {text!r}: {uncovered}; aozora={aozora!r}")
    return parts


def add_spacing(runs: list[dict]) -> list[dict]:
    runs = [{**run} for run in runs if run["text"]]
    for index, run in enumerate(runs):
        if run["type"] != "en":
            continue
        if index > 0 and runs[index - 1]["type"] == "en":
            if not runs[index - 1]["text"].endswith(" "):
                runs[index - 1]["text"] += " "
        if index > 0 and runs[index - 1]["type"] == "ja":
            previous = runs[index - 1]["text"]
            if previous and not previous[-1].isspace() and previous[-1] not in "「『（【":
                runs[index - 1]["text"] += " "
        if index + 1 < len(runs) and runs[index + 1]["type"] == "ja":
            following = runs[index + 1]["text"]
            if following and not following[0].isspace() and following[0] not in "、。！？）」』】,.!?":
                runs[index + 1]["text"] = " " + following
    return runs


def finalize_runs(raw_runs: list[dict]) -> list[dict]:
    runs = add_spacing(raw_runs)
    result = []
    for run in runs:
        if run["type"] == "ja":
            result.append({"type": "ja", "text": run["text"], "parts": japanese_parts(run["text"])})
        else:
            result.append({"type": "en", "text": run["text"], "ruby": run["ruby"]})
    return result


def reject_pending_targets(lesson: int, line_number: int, targets: list[dict]) -> None:
    """Require an inline body-text solution instead of a parenthetical gloss."""
    if targets:
        words = [target["english"] for target in targets]
        raise RuntimeError(
            f"L{lesson} line {line_number}: canonical words need an inline mixed-text "
            f"override; parenthetical fallback is forbidden: {words}"
        )


def runs_from_spans(japanese: str, spans: list[dict]) -> list[dict]:
    output = []
    cursor = 0
    for span in spans:
        if span["start"] > cursor:
            output.append({"type": "ja", "text": japanese[cursor : span["start"]]})
        output.append({"type": "en", "text": span["english"], "ruby": span["reading"]})
        if span.get("suffix"):
            output.append({"type": "ja", "text": span["suffix"]})
        cursor = span["end"]
    if cursor < len(japanese):
        output.append({"type": "ja", "text": japanese[cursor:]})
    return finalize_runs(output)


def runs_from_manual(mixed: str, ruby_map: dict[str, str]) -> list[dict]:
    matches = []
    occupied = []
    for target, reading in sorted(ruby_map.items(), key=lambda item: len(item[0]), reverse=True):
        found = None
        for match in re.finditer(re.escape(target), mixed, flags=re.I):
            if not any(match.start() < stop and start < match.end() for start, stop in occupied):
                found = match
                break
        if found is None:
            raise RuntimeError(f"Manual ruby target {target!r} not found in {mixed!r}")
        matches.append((found.start(), found.end(), found.group(0), reading))
        occupied.append((found.start(), found.end()))
    matches.sort()
    output = []
    cursor = 0
    for start, end, text, reading in matches:
        if start > cursor:
            output.append({"type": "ja", "text": mixed[cursor:start]})
        output.append({"type": "en", "text": text, "ruby": reading})
        cursor = end
    if cursor < len(mixed):
        output.append({"type": "ja", "text": mixed[cursor:]})
    # Manual strings already contain intentional spaces.
    result = []
    for run in output:
        if run["type"] == "ja":
            result.append({"type": "ja", "text": run["text"], "parts": japanese_parts(run["text"])})
        else:
            result.append(run)
    return result


def l1_fixed_lines() -> list[dict]:
    fixed = read_json(L1_FIXED)["lines"]
    output = []
    for item in fixed:
        mixed = "\n".join(item["mixed_lines"])
        ruby_map = {entry["text"]: entry["reading"] for entry in item["english_ruby"]}
        output.append(
            {
                "mixed": mixed,
                "runs": runs_from_manual(mixed, ruby_map),
                "replacement_source": "approved_L1_trial",
                "replacements": [
                    {"english": target, "reading": reading, "source": "approved_L1_trial"}
                    for target, reading in ruby_map.items()
                ],
            }
        )
    return output


def build_lesson(
    lesson: int,
    source: dict,
    global_index: dict,
    local_rows: list[dict],
    inline_overrides: dict[str, str],
) -> dict:
    prepared = []
    for line_number, line in enumerate(source["lines"], start=1):
        japanese = JA_CORRECTIONS.get((lesson, line_number), line["ja"])
        english = line.get("source_en") or " ".join(line["en_words"])
        targets = english_targets(english, local_rows)
        inline_mixed = inline_overrides.get(f"{lesson:02d}.{line_number:02d}")
        if inline_mixed is not None:
            ruby_map = {target["english"]: target["row"]["ja"] for target in targets}
            missing = [
                actual
                for actual in ruby_map
                if re.search(re.escape(actual), inline_mixed, flags=re.I) is None
            ]
            if missing:
                raise RuntimeError(
                    f"L{lesson} line {line_number}: inline mixed override is missing {missing}: "
                    f"{inline_mixed!r}"
                )
            runs = runs_from_manual(inline_mixed, ruby_map)
            prepared.append(
                {
                    "mixed": inline_mixed,
                    "runs": runs,
                    "replacement_source": "canonical_new_words_inline_manual",
                    "canonical_targets": [
                        {
                            "english": target["english"],
                            "canonical_word": target["row"]["word"],
                            "meaning": target["row"]["ja"],
                        }
                        for target in targets
                    ],
                    "replacements": [
                        {
                            "english": target["english"],
                            "reading": target["row"]["ja"],
                            "source": "canonical_new_word_inline_manual",
                            "canonical_word": target["row"]["word"],
                            "canonical_meaning": target["row"]["ja"],
                        }
                        for target in targets
                    ],
                }
            )
            continue
        manual = CANONICAL_MANUAL_MIXED.get((lesson, line_number))
        if manual:
            manual_targets = []
            for actual in manual["ruby"]:
                target = next(
                    (
                        candidate
                        for candidate in targets
                        if stems(actual) & stems(candidate["english"])
                    ),
                    None,
                )
                manual_targets.append(target)
            # Older hand-written exceptions sometimes left an English verb as
            # a bare Japanese predicate. Inline overrides above replace those
            # wherever a more readable TeacherTacos-style sentence is needed.
            if any(
                target is None or target["row"].get("pos") not in DIRECT_WEAVE_POS
                for target in manual_targets
            ):
                manual = None
        if manual:
            target_by_stem = {
                stem: target
                for target in targets
                for stem in stems(target["english"])
            }
            replacements = []
            represented_orders: set[int] = set()
            for actual, reading in manual["ruby"].items():
                target = next(
                    (target_by_stem[stem] for stem in stems(actual) if stem in target_by_stem),
                    None,
                )
                if target is None:
                    raise RuntimeError(
                        f"L{lesson} line {line_number}: manual canonical word {actual!r} is not in the sung line"
                    )
                replacements.append(
                    {
                        "english": actual,
                        "reading": reading,
                        "source": "canonical_new_word_manual",
                        "canonical_word": target["row"]["word"],
                        "canonical_meaning": target["row"]["ja"],
                    }
                )
                represented_orders.update(target["token_orders"])
            runs = runs_from_manual(manual["mixed"], manual["ruby"])
            pending = [
                target
                for target in targets
                if not represented_orders.intersection(target["token_orders"])
            ]
            reject_pending_targets(lesson, line_number, pending)
            prepared.append(
                {
                    "mixed": "".join(run["text"] for run in runs),
                    "runs": runs,
                    "replacement_source": "canonical_new_words_manual",
                    "canonical_targets": [
                        {
                            "english": target["english"],
                            "canonical_word": target["row"]["word"],
                            "meaning": target["row"]["ja"],
                        }
                        for target in targets
                    ],
                    "replacements": replacements,
                }
            )
            continue
        spans = find_candidates(english, japanese, global_index, local_rows)
        used_orders = {order for span in spans for order in span["token_orders"]}
        pending = [
            target for target in targets if not used_orders.intersection(target["token_orders"])
        ]
        runs = (
            runs_from_spans(japanese, spans)
            if spans
            else finalize_runs([{"type": "ja", "text": japanese}])
        )
        reject_pending_targets(lesson, line_number, pending)
        if spans:
            replacement_source = "canonical_new_words"
        else:
            replacement_source = "japanese_only_no_canonical_target"
        replacements = [
            {
                "english": span["english"],
                "reading": span["reading"],
                "source": span["source"],
                "canonical_word": span["canonical_word"],
                "canonical_meaning": span["canonical_meaning"],
            }
            for span in spans
        ]
        prepared.append(
            {
                "mixed": "".join(run["text"] for run in runs),
                "runs": runs,
                "replacement_source": replacement_source,
                "canonical_targets": [
                    {
                        "english": target["english"],
                        "canonical_word": target["row"]["word"],
                        "meaning": target["row"]["ja"],
                    }
                    for target in targets
                ],
                "replacements": replacements,
            }
        )

    lines = []
    for index, (source_line, prepared_line) in enumerate(zip(source["lines"], prepared), start=1):
        original_ja = source_line["ja"]
        displayed_ja = JA_CORRECTIONS.get((lesson, index), original_ja)
        lines.append(
            {
                "line": index,
                "english": source_line.get("source_en") or " ".join(source_line["en_words"]),
                "source_ja": original_ja,
                "display_ja": displayed_ja,
                "corrected_translation": displayed_ja != original_ja,
                **prepared_line,
            }
        )

    return {
        "lesson": lesson,
        "source_config": str(source_config(lesson).relative_to(PROJECT)),
        "title_en": source["title_en"],
        "title_ja": source["title_ja"],
        "policy": "Only canonical new vocabulary from the current lesson may appear in English. No whole-course or easy-word fallback. Every selected English word is embedded directly in the mixed Japanese body text; parenthetical glosses are prohibited. All Japanese kanji have hiragana ruby; every English segment has a Japanese meaning ruby.",
        "line_count": len(lines),
        "lines": lines,
    }


def main() -> None:
    lesson_data = read_json(LESSON_DATA)
    inline_overrides = read_json(INLINE_MIXED_PATH)
    global_index, lesson_rows = build_dictionary(lesson_data)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    all_lessons = []
    review = [
        "# 中学生編 L1〜L45 英語混じり字幕レビュー",
        "",
        "- 英語ルビ: 英語部分の上に日本語の意味を表示",
        "- 漢字ルビ: 日本語部分の漢字を100%表示",
        "- 正本新出語は本文内へ直接埋め込み、括弧による単語補足は使用しない",
        "- `【訳修正】` は英語本文との不一致をこの新版で修正した行",
        "",
    ]
    total_lines = total_english = total_kanji = 0
    canonical_target_lines = mixed_lines = japanese_only_lines = 0
    correction_count = 0
    for lesson in range(1, 46):
        source = read_json(source_config(lesson))
        item = build_lesson(
            lesson, source, global_index, lesson_rows[lesson], inline_overrides
        )
        path = OUT_DIR / f"L{lesson:02d}.json"
        path.write_text(json.dumps(item, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        all_lessons.append({"lesson": lesson, "path": str(path.relative_to(ROOT)), "line_count": item["line_count"]})
        review.extend([f"## L{lesson:02d} {item['title_en']}", ""])
        for line in item["lines"]:
            flag = " 【訳修正】" if line["corrected_translation"] else ""
            review.append(f"{line['line']:02d}. `{line['mixed']}`{flag}")
            review.append(f"    - EN: {line['english']}")
            review.append(
                "    - ルビ: "
                + " / ".join(f"{entry['english']}→{entry['reading']}" for entry in line["replacements"])
            )
            total_lines += 1
            total_english += len(line["replacements"])
            canonical_target_lines += int(bool(line["canonical_targets"]))
            mixed_lines += int(bool(line["replacements"]))
            japanese_only_lines += int(not line["replacements"])
            total_kanji += sum(
                1
                for run in line["runs"] if run["type"] == "ja"
                for part in run["parts"] if part["ruby"]
            )
            correction_count += int(line["corrected_translation"])
        review.append("")

    summary = {
        "range": "L1-L45",
        "edition": "v4_inline_canonical_vocab",
        "policy": "Only current-lesson canonical new vocabulary is embedded directly in the mixed Japanese body. Japanese meanings appear only as ruby above English words; parenthetical word glosses and unrubied ASCII are prohibited. Japanese kanji retain full reading ruby.",
        "lessons": all_lessons,
        "counts": {
            "lessons": len(all_lessons),
            "lines": total_lines,
            "english_ruby_segments": total_english,
            "kanji_ruby_segments": total_kanji,
            "translation_corrections": correction_count,
            "canonical_target_lines": canonical_target_lines,
            "mixed_lines": mixed_lines,
            "japanese_only_lines": japanese_only_lines,
            "noncanonical_replacements": 0,
        },
    }
    (ROOT / "planning" / "manifest.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    REVIEW_PATH.write_text("\n".join(review) + "\n", encoding="utf-8")
    print(json.dumps(summary["counts"], ensure_ascii=False, indent=2))
    print(REVIEW_PATH)


if __name__ == "__main__":
    main()
