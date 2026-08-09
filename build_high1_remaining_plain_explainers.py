"""Build plain grammar explainer videos for the remaining High1 lessons.

This creates H11-H45 while leaving the existing H1-H10 single videos untouched.
The visual and narration policy follows build_h1_h10_plain_explainers.py:
English example sentences are rendered with Japanese translations and spoken
with the English macOS voice, while Japanese narration uses VoicePeak.
"""
from __future__ import annotations

import re
from html import unescape
from pathlib import Path

from build_high3_plain_explainers import (
    _extract_book_block,
    _extract_lesson_blocks,
    _remove_tags,
    parse_lessons_from_book,
)
from build_h1_h10_plain_explainers import (
    LessonConfig,
    RolePart,
    build_lesson,
)


ROOT = Path(__file__).resolve().parent

PREPOSITIONS = {
    "at",
    "by",
    "in",
    "on",
    "from",
    "to",
    "toward",
    "towards",
    "into",
    "with",
    "without",
    "for",
    "during",
    "after",
    "before",
    "under",
    "over",
    "through",
    "across",
    "around",
    "near",
    "beside",
    "within",
    "because",
    "although",
    "while",
    "when",
    "if",
    "unless",
}

VERB_HINTS = {
    "am",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "will",
    "would",
    "should",
    "ought",
    "can",
    "could",
    "may",
    "might",
    "must",
    "do",
    "does",
    "did",
    "look",
    "looks",
    "feel",
    "feels",
    "seem",
    "seems",
    "become",
    "became",
    "call",
    "called",
    "make",
    "made",
    "let",
    "saw",
    "see",
    "heard",
    "hear",
    "felt",
    "found",
    "find",
    "stood",
    "rose",
    "rises",
    "passed",
    "passes",
    "appeared",
    "emerged",
    "spoke",
    "said",
    "told",
    "asked",
    "gave",
    "showed",
    "kept",
    "continued",
    "begin",
    "began",
    "start",
    "started",
    "stand",
    "stands",
    "publish",
    "published",
    "connect",
    "connected",
    "exchange",
    "exchanged",
    "set",
    "live",
    "lived",
    "remained",
    "became",
    "meant",
    "means",
    "depends",
    "matters",
    "seems",
    "seemed",
}

ADVERB_HINTS = {
    "always",
    "already",
    "never",
    "often",
    "usually",
    "sometimes",
    "quietly",
    "slowly",
    "simply",
    "still",
    "just",
    "deeply",
    "gradually",
    "more",
}


def clean_ja(value: str) -> str:
    value = _remove_tags(value)
    value = re.sub(r"^[―—-]\s*", "", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value or "日本語訳を確認します。"


def clean_title(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def clean_en_example(value: str) -> str:
    value = _remove_tags(unescape(value))
    if "例文" in value:
        value = value.split("例文", 1)[1]
    value = re.sub(r"\s+", " ", value).strip()
    candidates = split_english_sentences(value)
    if candidates:
        return re.sub(r"^[：:\s]+", "", candidates[0]).strip()
    return clean_title(value)


def safe_pattern(target: str, lesson_id: int) -> str:
    target = clean_title(target)
    if not target or target == "文法ターゲット":
        return f"H{lesson_id} 本文文法"
    return target


def split_english_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    protected = text
    for src, dst in {
        "H.M.S.": "H<prd>M<prd>S<prd>",
        "U.S.": "U<prd>S<prd>",
        "U.K.": "U<prd>K<prd>",
        "Mr.": "Mr<prd>",
        "Mrs.": "Mrs<prd>",
        "Dr.": "Dr<prd>",
    }.items():
        protected = protected.replace(src, dst)
    raw = re.findall(r"[^.!?]+[.!?]", protected)
    out = []
    for item in raw:
        item = item.replace("<prd>", ".").strip()
        if 5 <= len(item) <= 180:
            out.append(item)
    return out


def split_japanese_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    raw = re.findall(r"[^。！？]+[。！？]", text)
    return [item.strip() for item in raw if item.strip()]


def lesson_raw_blocks() -> dict[int, str]:
    block = _extract_book_block("high1")
    out = {}
    for raw in _extract_lesson_blocks(block):
        m = re.search(r'data-lesson="(\d+)"', raw)
        if m:
            out[int(m.group(1))] = raw
    return out


def fallback_examples(raw: str) -> list[tuple[str, str]]:
    en_body = re.search(r'<div class="en-body hidden">(.*?)</div>\s*<div class="jp-full hidden">', raw, flags=re.S)
    jp_body = re.search(r'<div class="jp-full hidden">(.*?)</div>\s*<div class="body-syntax hidden">', raw, flags=re.S)
    en_sentences = split_english_sentences(_remove_tags(en_body.group(1))) if en_body else []
    ja_sentences = split_japanese_sentences(_remove_tags(jp_body.group(1))) if jp_body else []
    pairs = []
    for idx, en in enumerate(en_sentences[:3]):
        ja = ja_sentences[idx] if idx < len(ja_sentences) else "本文の日本語訳を確認します。"
        pairs.append((en, ja))
    return pairs


def sentence_from_patterns(raw: str) -> tuple[str, str] | None:
    syntax = re.search(r'<div class="body-syntax hidden">(.*?)</div>\s*</section>', raw, flags=re.S)
    if not syntax:
        return None
    sentence = re.search(r'<div class="sentence">(.*?)<div class="meta-row">', syntax.group(1), flags=re.S)
    if not sentence:
        return None
    text = _remove_tags(sentence.group(1))
    text = re.sub(r"\s+", " ", text).strip()
    en = re.sub(r"[^\x00-\x7F]+", " ", text)
    en = re.sub(r"\s+", " ", en).strip()
    en = re.sub(r"\s+([,.!?;:])", r"\1", en)
    if len(en) < 8:
        return None
    return en, "本文の一文を確認します。"


def strip_sentence(sentence: str) -> str:
    return re.sub(r"[\"“”]", "", sentence).strip()


def token_clean(token: str) -> str:
    return re.sub(r"^[,;:()]+|[,;:().!?]+$", "", token)


def detect_prefix(tokens: list[str]) -> tuple[RolePart | None, list[str]]:
    if not tokens:
        return None, tokens
    lower0 = token_clean(tokens[0]).lower()
    if lower0 in {"if", "when", "unless", "although", "while", "after", "before"}:
        joined = " ".join(tokens)
        if "," in joined:
            left, right = joined.split(",", 1)
            role = "If" if lower0 in {"if", "unless"} else "M"
            ja = "条件・時のまとまり" if role == "If" else "時・状況のまとまり"
            return RolePart(role, left.strip(), ja), right.strip().split()
    if lower0 in PREPOSITIONS or " ".join(t.lower() for t in tokens[:2]) == "this time":
        joined = " ".join(tokens)
        if "," in joined:
            left, right = joined.split(",", 1)
            return RolePart("M", left.strip(), "時・場所の説明"), right.strip().split()
    return None, tokens


def extract_leading_modifier(sentence: str) -> tuple[RolePart | None, str]:
    pieces = [piece.strip() for piece in sentence.split(",")]
    if len(pieces) < 2:
        return None, sentence
    first = token_clean(pieces[0].split()[0]).lower() if pieces[0].split() else ""
    first_text = pieces[0].lower()
    starts_as_modifier = (
        first in PREPOSITIONS
        or first in {"every", "today", "yesterday", "tomorrow"}
        or first_text.endswith("ago")
        or " ago" in first_text
    )
    if not starts_as_modifier:
        return None, sentence

    collected = [pieces[0]]
    idx = 1
    while idx < len(pieces) - 1:
        segment = pieces[idx].strip()
        first_word = token_clean(segment.split()[0]).lower() if segment.split() else ""
        if first_word in PREPOSITIONS or re.fullmatch(r"\d{3,4}", segment):
            collected.append(segment)
            idx += 1
            continue
        break

    rest = ", ".join(pieces[idx:]).strip()
    return RolePart("M", ", ".join(collected), "時・場所の説明"), rest


def extract_interrupting_modifier(sentence: str) -> tuple[str | None, RolePart | None, str]:
    pieces = [piece.strip() for piece in sentence.split(",")]
    if len(pieces) < 3:
        return None, None, sentence
    middle = pieces[1]
    first_word = token_clean(middle.split()[0]).lower() if middle.split() else ""
    if first_word not in PREPOSITIONS:
        return None, None, sentence
    subject = pieces[0]
    rest = ", ".join(pieces[2:]).strip()
    return subject, RolePart("M", middle, "補足説明"), rest


def find_verb_index(tokens: list[str]) -> int:
    if tokens and token_clean(tokens[0]).lower() in VERB_HINTS:
        return 0

    for idx, token in enumerate(tokens[1:], start=1):
        low = token_clean(token).lower()
        if low in ADVERB_HINTS:
            continue
        if low in VERB_HINTS:
            return idx

    for idx, token in enumerate(tokens[1:], start=1):
        low = token_clean(token).lower()
        if low in ADVERB_HINTS:
            continue
        if low.endswith("ed") or low.endswith("ing"):
            return idx

    for idx, token in enumerate(tokens[1:], start=1):
        low = token_clean(token).lower()
        if low in ADVERB_HINTS:
            continue
        if idx > 1 and low.endswith("s") and not low.endswith(("ness", "less", "ous", "ics")):
            return idx
    return 1 if len(tokens) > 1 else 0


def verb_span(tokens: list[str], idx: int) -> int:
    low = token_clean(tokens[idx]).lower()
    end = idx + 1
    if low in {"will", "would", "should", "could", "may", "might", "must", "can"}:
        end = min(len(tokens), idx + 2)
        if idx + 1 < len(tokens) and token_clean(tokens[idx + 1]).lower() in {"be", "have"}:
            end = min(len(tokens), idx + 3)
    elif low in {"am", "is", "are", "was", "were", "have", "has", "had", "be", "been"}:
        end = min(len(tokens), idx + 2)
        if idx + 2 < len(tokens) and token_clean(tokens[idx + 1]).lower() == "going" and token_clean(tokens[idx + 2]).lower() == "to":
            end = min(len(tokens), idx + 4)
        elif idx + 1 < len(tokens) and token_clean(tokens[idx + 1]).lower() in {"be", "been", "being"}:
            end = min(len(tokens), idx + 3)
    elif low == "ought":
        end = min(len(tokens), idx + 3)
    elif low in {"began", "begin", "started", "start"} and idx + 1 < len(tokens) and token_clean(tokens[idx + 1]).lower() == "to":
        end = min(len(tokens), idx + 3)
    elif low == "set" and idx + 1 < len(tokens) and token_clean(tokens[idx + 1]).lower() == "out":
        end = min(len(tokens), idx + 2)
    return end


def rest_role(rest: str, pattern: str) -> str:
    if not rest:
        return "M"
    first = token_clean(rest.split()[0]).lower()
    if first in PREPOSITIONS:
        return "M"
    if first in ADVERB_HINTS:
        return "M"
    if "SVC" in pattern or "第2文型" in pattern:
        return "C"
    if "SVOC" in pattern or "第5文型" in pattern or "知覚" in pattern or "使役" in pattern:
        return "C"
    return "O"


def rough_parts(sentence: str, pattern: str) -> list[RolePart]:
    sentence = strip_sentence(sentence)
    leading, sentence = extract_leading_modifier(sentence)
    fixed_subject, interrupting, sentence_for_tokens = extract_interrupting_modifier(sentence)
    if fixed_subject:
        sentence = sentence_for_tokens
    tokens = [token_clean(t) for t in sentence.split() if token_clean(t)]
    if not tokens:
        return [RolePart("S", "Subject", "主語"), RolePart("V", "Verb", "動詞")]

    prefix, tokens = detect_prefix(tokens)
    if not tokens:
        return [prefix] if prefix else [RolePart("S", sentence, "文全体")]

    verb_idx = find_verb_index(tokens)
    subject_tokens = tokens[:verb_idx]
    pre_verb_modifier = None
    if len(subject_tokens) > 1 and token_clean(subject_tokens[-1]).lower() in ADVERB_HINTS:
        pre_verb_modifier = subject_tokens[-1]
        subject_tokens = subject_tokens[:-1]
    subject = fixed_subject or " ".join(subject_tokens).strip() or tokens[0]
    end = verb_span(tokens, verb_idx)
    verb = " ".join(tokens[verb_idx:end]).strip()
    rest = " ".join(tokens[end:]).strip()

    parts: list[RolePart] = []
    if leading:
        parts.append(leading)
    if prefix:
        parts.append(prefix)
    parts.append(RolePart("S", subject, "主語"))
    if interrupting and len(parts) < 4:
        parts.append(interrupting)
    if pre_verb_modifier and len(parts) < 4:
        parts.append(RolePart("M", pre_verb_modifier, "修飾語"))
    parts.append(RolePart("V", verb, "動詞"))
    if rest and len(parts) < 4:
        parts.append(RolePart(rest_role(rest, pattern), rest, "後ろのまとまり"))
    return parts[:4]


def make_rule_points(pattern: str) -> list[tuple[str, str]]:
    if "仮定法" in pattern:
        return [("条件を見る", "事実と違う想定を見つける"), ("時制を見る", "時制が一段下がる形に注意する"), ("主節を見る", "would/could などの助動詞を見る")]
    if "関係" in pattern:
        return [("先行詞を見る", "説明される名詞を見つける"), ("関係詞を見る", "who/which/that/what などの働きを見る"), ("節を戻す", "名詞を後ろから説明する形で読む")]
    if "完了" in pattern:
        return [("have を見る", "完了形のサインを見つける"), ("過去分詞を見る", "動詞の形を確認する"), ("時間を見る", "いつからいつまでのつながりかを読む")]
    if "受動態" in pattern:
        return [("be を見る", "受け身のサインを見つける"), ("過去分詞を見る", "何をされたのかを確認する"), ("by を見る", "必要なら動作主を確認する")]
    if "比較" in pattern:
        return [("比較語を見る", "more/most/as などを見つける"), ("比べる対象を見る", "何と何を比べるか確認する"), ("程度を読む", "同じ・より・最も、を区別する")]
    return [("形を見る", "今回の文法のサインを探す"), ("役割を見る", "主語・動詞・補足説明を分ける"), ("本文へ戻す", "同じ形を本文の一文で確認する")]


def slug_for(lesson_id: int) -> str:
    return "grammar"


def make_config(lesson, raw: str) -> LessonConfig:
    pattern = safe_pattern(lesson.grammar_target, lesson.lesson_id)
    title = clean_title(lesson.title)
    thesis = clean_title(lesson.description)
    if not thesis or thesis == "本文の文法ポイントを丁寧に確認します。":
        thesis = "本文の一文を使って、文の形と意味の流れを確認します。"

    examples = [(clean_en_example(en), clean_ja(ja)) for en, ja in lesson.examples[:3]]
    if len(examples) < 3:
        examples.extend(fallback_examples(raw))
    examples = examples[:3]
    while len(examples) < 3:
        examples.append(("We read the sentence carefully.", "私たちはその文を注意深く読む。"))

    build_sentence, build_translation = examples[0]
    text_pair = examples[0]
    text_sentence, text_translation = text_pair
    if text_translation == "本文の一文を確認します。":
        text_translation = examples[0][1]

    return LessonConfig(
        lesson.lesson_id,
        slug_for(lesson.lesson_id),
        pattern,
        title,
        f"{pattern} を本文で確認する",
        thesis,
        examples,
        build_sentence,
        build_translation,
        rough_parts(build_sentence, pattern),
        make_rule_points(pattern),
        text_sentence,
        clean_ja(text_translation),
        rough_parts(text_sentence, pattern),
        "画面の文を役割カードに分けると、文法のポイントが見えやすくなります。",
        [("例文", en, ja) for en, ja in examples[:3]],
    )


def main():
    raw_by_id = lesson_raw_blocks()
    lessons = [lesson for lesson in parse_lessons_from_book("high1") if 11 <= lesson.lesson_id <= 45]
    for lesson in lessons:
        cfg = make_config(lesson, raw_by_id[lesson.lesson_id])
        build_lesson(cfg)


if __name__ == "__main__":
    main()
