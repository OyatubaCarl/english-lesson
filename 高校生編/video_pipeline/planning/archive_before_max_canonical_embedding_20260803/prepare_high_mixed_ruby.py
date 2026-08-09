#!/usr/bin/env python3
"""Prepare exact-lyric, mixed-Japanese captions with complete ruby for H1-H160."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


HERE = Path(__file__).resolve().parent
PIPELINE = HERE.parent
HIGH = PIPELINE.parent
PROJECT = HIGH.parent
MANIFEST = PIPELINE / "planning" / "adopted_songs_h001_h160.json"
LESSONS = PROJECT / "taco_course_mockup" / "high_lessons.json"
CACHE = PIPELINE / "planning" / "exact_lyrics_ja_translation_cache.json"
SUMMARY = PIPELINE / "planning" / "mixed_ruby_manifest.json"
REVIEW = PIPELINE / "planning" / "mixed_ruby_review.md"
MIDDLE_PREP = (
    PROJECT / "中学生編" / "middle_ruby_complete_v1" / "scripts" / "prepare_middle_ruby.py"
)


def load_middle_helpers():
    spec = importlib.util.spec_from_file_location("middle_ruby_helpers", MIDDLE_PREP)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {MIDDLE_PREP}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


HELPERS = load_middle_helpers()


EXTRA_GLOSSARY = {
    "ai": "人工知能",
    "sns": "SNS",
    "nasa": "アメリカ航空宇宙局",
    "dna": "DNA",
    "ddt": "DDT",
    "npt": "核拡散防止条約",
    "mri": "磁気共鳴画像法",
    "ptsd": "心的外傷後ストレス障害",
    "lgbtq": "性的少数者",
    "sora": "ソラ",
    "deepl": "ディープエル",
    "eu": "欧州連合",
    "ngo": "非政府組織",
    "serendipity": "思いがけない幸運",
    "nostalgia": "郷愁",
    "privacy": "プライバシー",
    "intelligence": "知能",
    "innocent": "無罪の",
    "proven": "証明された",
    "guilty": "有罪の",
    "traffic jam": "交通渋滞",
    "black lives matter": "黒人の命も大切だ",
    "rite of passage": "通過儀礼",
    "spoke": "話した",
    "stood": "立っていた",
    "noticed": "気づいた",
    "vanished": "消えた",
    "lived": "生きていた",
    "continued": "続けた",
    "trusted": "信頼した",
    "proposed": "提案した",
    "wished": "願った",
    "wonder": "思う",
    "hope": "願う",
    "mind": "決心",
}

FALLBACK_STOPWORDS = HELPERS.STOPWORDS | {
    "no", "one", "nothing", "everything", "something", "someone", "anyone",
    "everyone", "every", "sometimes", "first", "then", "there", "here",
    "really", "just", "even", "yet", "still",
}


# Reviewed canonical-word phrasing for places where the exact Japanese
# translation uses a synonym.  These forms preserve the adopted lyric meaning
# while making the lesson's actual new words visible; no easy/global terms are
# introduced.
CANONICAL_MANUAL_MIXED: dict[tuple[int, int], dict] = {
    (1, 4): {"mixed": "世界は静かに breathed。", "ruby": {"breathed": "息づいていた"}},
    (1, 6): {"mixed": "太陽が emerged。", "ruby": {"emerged": "立ち現れた"}},
    (1, 7): {"mixed": "その光は pure な空気に広がりました。", "ruby": {"pure": "澄んだ"}},
    (1, 14): {"mixed": "森の depths から、かすかな presence が動きました。", "ruby": {"depths": "奥深く", "presence": "気配"}},
    (1, 15): {"mixed": "私は一頭の鹿を noticed。", "ruby": {"noticed": "見つけて気づいた"}},
    (1, 18): {"mixed": "私は風景を、ただ静かに observed。", "ruby": {"observed": "観察した"}},
    (1, 21): {"mixed": "新しい一日が arose。", "ruby": {"arose": "始まった"}},
    (5, 2): {"mixed": "母はその子を adopt することに決め、僕たちはソラと名付けました。", "ruby": {"adopt": "家族に迎える"}},
    (5, 4): {"mixed": "父はソラを僕たちの家族の一員だと declare し、僕たちは皆で歓迎しました。", "ruby": {"declare": "宣言"}},
    (5, 5): {"mixed": "母はソラが gentle な子だと気づきました。", "ruby": {"gentle": "優しい"}},
    (5, 8): {"mixed": "僕はソラを protect すると誓いました。", "ruby": {"protect": "守る"}},
    (5, 10): {"mixed": "父は『この犬を家族として迎えよう』と言い、僕たちは一緒にソラを embrace しました。", "ruby": {"embrace": "抱きしめる"}},
    (5, 11): {"mixed": "数週間後、僕たちの世話のおかげで、ソラは calm で満ち足りた犬になりました。", "ruby": {"calm": "穏やか"}},
    (6, 12): {"mixed": "彼女は、私に彼を思い出すよう encourage しようとしているのだと感じました。", "ruby": {"encourage": "励ます"}},
    (6, 13): {"mixed": "やがて夕日が、屋根を gentle な色調に染めました。", "ruby": {"gentle": "やわらかな"}},
    (6, 14): {"mixed": "庭は calm で、黄金色になりました。", "ruby": {"calm": "穏やか"}},
    (13, 2): {"mixed": "息を整えてベンチに座り、exhausted な状態でした。", "ruby": {"exhausted": "疲れ切った"}},
    (13, 5): {"mixed": "Meanwhile、友人は定刻に駅へ着いていました。", "ruby": {"Meanwhile": "一方で"}},
    (13, 12): {"mixed": "彼がいつも示してくれた gentle な優しさを、今になって realize しました。", "ruby": {"gentle": "優しい", "realize": "気づく"}},
    (13, 14): {"mixed": "気持ちは eventually settled。", "ruby": {"eventually": "ついに", "settled": "落ち着いた"}},
    (14, 1): {"mixed": "あと5年で、私は何を accomplish しているでしょうか。", "ruby": {"accomplish": "達成する"}},
    (14, 3): {"mixed": "私の ambition は大きくありませんが、他の人の人生に静かに contribute したいです。", "ruby": {"ambition": "大望", "contribute": "貢献する"}},
    (14, 5): {"mixed": "日々の progress が、静かに一本の道になっているでしょう。", "ruby": {"progress": "進歩"}},
    (14, 6): {"mixed": "それまでに、小さな achievements を積み重ね、多くのものを seeking。", "ruby": {"achievements": "達成", "seeking": "求め続けている"}},
    (14, 8): {"mixed": "私はもう少し mature になっているでしょう。", "ruby": {"mature": "成熟した"}},
    (14, 9): {"mixed": "大きな prospect が、いつも必要なわけではありません。", "ruby": {"prospect": "見通し"}},
    (14, 10): {"mixed": "小さな goals を fulfill できる人になりたいです。", "ruby": {"goals": "目標", "fulfill": "実現する"}},
    (14, 11): {"mixed": "私の未来は likely、目の前に静かに開いていくでしょう。今はそう信じています。", "ruby": {"likely": "おそらく"}},
    (15, 3): {"mixed": "これは、自分を見つめ直す reflection の時間です。", "ruby": {"reflection": "内省"}},
    (15, 8): {"mixed": "それを recall するたびに、恥ずかしくなります。", "ruby": {"recall": "思い出す"}},
    (15, 10): {"mixed": "新しい年は、もっと modest に過ごしたいです。", "ruby": {"modest": "控えめに"}},
    (15, 11): {"mixed": "家族への感謝を、もっと express したいです。", "ruby": {"express": "表現する"}},
    (15, 12): {"mixed": "少し早起きして深呼吸するという、小さな habit を adopt したいです。", "ruby": {"habit": "習慣", "adopt": "取り入れる"}},
    (15, 14): {"mixed": "僕は手を合わせ、亡くなった祖父を静かに recall しました。", "ruby": {"recall": "思い出す"}},
    (16, 8): {"mixed": "僕はその regret を、妹に confess できませんでした。", "ruby": {"regret": "後悔", "confess": "打ち明ける"}},
    (16, 13): {"mixed": "人は regret しても、誰かの affection に救われることがあります。", "ruby": {"regret": "後悔する", "affection": "愛情"}},
    (17, 2): {"mixed": "長い間忘れられていましたが、ある年、町の人たちは建物を restore することに決めました。", "ruby": {"restore": "修復"}},
    (17, 6): {"mixed": "町の人たちは、この建物を地域の heritage として preserve すべきだと声を上げました。", "ruby": {"heritage": "遺産", "preserve": "保存する"}},
    (18, 9): {"mixed": "このように明確な purpose を持つ姿は、まぶしく、尊敬できます。", "ruby": {"purpose": "目的"}},
    (18, 11): {"mixed": "その日、姉は単なるランナーではなく、地道な effort を本当の自信に変えた人になるでしょう。", "ruby": {"effort": "努力"}},
}

# A sung line can contain canonical vocabulary without admitting a natural
# Japanese mixed sentence.  Keep these reviewed lines Japanese-only instead of
# forcing fragments such as “ought だった” or a bare “used” into the caption.
CANONICAL_JAPANESE_ONLY: set[tuple[int, int]] = {
    (15, 4),
    (15, 5),
    (15, 6),
    (15, 7),
    (15, 15),
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def translate_block(lines: list[str]) -> list[str]:
    query = "\n".join(lines)
    params = urllib.parse.urlencode(
        {"client": "gtx", "sl": "en", "tl": "ja", "dt": "t", "q": query}
    )
    request = urllib.request.Request(
        f"https://translate.googleapis.com/translate_a/single?{params}",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    last_error = None
    for attempt in range(1, 5):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = json.loads(response.read().decode("utf-8"))
            translated = "".join(part[0] for part in payload[0]).strip().splitlines()
            if len(translated) == len(lines):
                return [line.strip() for line in translated]
            break
        except Exception as error:  # pragma: no cover - network retry
            last_error = error
            if attempt < 4:
                time.sleep(attempt * 1.5)
    # Preserve one-to-one line integrity if the service reflows a block.
    if len(lines) > 1:
        return [translate_block([line])[0] for line in lines]
    raise RuntimeError(f"translation failed for {lines[0]!r}: {last_error}")


def ensure_translations(manifest: dict, requested: list[int], workers: int) -> dict:
    cache = read_json(CACHE) if CACHE.exists() else {"source": "exact adopted lyrics", "lessons": {}}
    tasks = []
    for number in requested:
        row = manifest["lessons"][number - 1]
        key = row["lesson"]
        cached = cache["lessons"].get(key, [])
        if [item.get("en") for item in cached] != row["lyrics_lines"]:
            tasks.append((number, row["lyrics_lines"]))
    if tasks:
        with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
            futures = {
                executor.submit(translate_block, lines): (number, lines)
                for number, lines in tasks
            }
            for future in as_completed(futures):
                number, lines = futures[future]
                translated = future.result()
                cache["lessons"][f"H{number:03d}"] = [
                    {"en": en, "ja": ja} for en, ja in zip(lines, translated)
                ]
                print(f"translated H{number:03d}: {len(lines)} lines", flush=True)
        CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return cache


def build_dictionaries(lesson_data: list[dict]):
    """Build current-lesson canonical glossaries only.

    Whole-course and WordTacos dictionaries are intentionally excluded: they
    caused easy known words to displace each lesson's actual new vocabulary.
    """
    local_rows: dict[int, list[dict]] = {}
    for lesson in lesson_data:
        number = int(lesson["b"])
        rows = []
        for paragraph in lesson["vocabSentences"]:
            for item in paragraph["words"]:
                row = {
                    "word": item["w"],
                    "ja": item["ja"],
                    "priority": 10,
                    "source": "canonical_new_word",
                }
                rows.append(row)
        local_rows[number] = rows
    return {}, local_rows


def find_high_candidates(english: str, japanese: str, local_rows: list[dict]) -> list[dict]:
    """Preserve the established high-school weaving policy.

    The shared middle-school helper now requires author-assigned POS metadata,
    but ``high_lessons.json`` intentionally contains only ``w`` and ``ja``.
    Calling the newer helper directly therefore silently changed the full high
    manifest from 1,038 mixed lines to only the hand-written exceptions.  Keep
    the previously established high-school behavior here while retaining its
    morphology-boundary and overlap safety checks.
    """
    candidates = []
    morph_boundaries = {0, len(japanese)}
    for morph in HELPERS.japanese_morphs(japanese):
        morph_boundaries.add(morph["start"])
        morph_boundaries.add(morph["end"])
    for target in HELPERS.english_targets(english, local_rows):
        row = target["row"]
        if HELPERS.normalize_en(row["word"]) in {"years"}:
            continue
        exact_matches = []
        for surface in HELPERS.japanese_candidates(row["ja"]):
            for match in re.finditer(re.escape(surface), japanese):
                if match.start() not in morph_boundaries or match.end() not in morph_boundaries:
                    continue
                if len(surface) == 1 and HELPERS.KANJI_RE.fullmatch(surface):
                    before = japanese[match.start() - 1] if match.start() else ""
                    after = japanese[match.end()] if match.end() < len(japanese) else ""
                    if HELPERS.KANJI_RE.fullmatch(before) or HELPERS.KANJI_RE.fullmatch(after):
                        continue
                surface_morphs = [
                    item for item in HELPERS.japanese_morphs(surface) if item["content"]
                ]
                last_pos = surface_morphs[-1]["pos"] if surface_morphs else ""
                if HELPERS.normalize_en(row["word"]) in {"like", "likes"} and surface == "好き":
                    continue
                if (
                    last_pos in {"動詞", "形容詞", "形状詞"}
                    and japanese[match.end() :].startswith(("が", "けれど", "けれども", "のに"))
                ):
                    continue
                if last_pos == "動詞" and japanese[match.end() :].startswith(("んだ", "のだ")):
                    continue
                exact_matches.append((match.start(), match.end(), ""))
        if exact_matches:
            spans = [(*match, "canonical_new_word_exact") for match in exact_matches]
        else:
            spans = []
            for surface in HELPERS.japanese_candidates(row["ja"]):
                match = HELPERS.japanese_morph_span(japanese, surface)
                if match:
                    spans.append((*match, "canonical_new_word_morph"))
                    break
        for start, end, suffix, source in spans:
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
        if len(selected) == 4:
            break
    return sorted(selected, key=lambda item: item["start"])


def lookup_word(token: str, global_index: dict, local_rows: list[dict]) -> dict | None:
    candidates = []
    for row in local_rows:
        if HELPERS.stems(row["word"]) & HELPERS.stems(token):
            candidates.append(row)
    for stem in HELPERS.stems(token):
        candidates.extend(global_index.get(stem, []))
    if not candidates:
        return None
    return max(candidates, key=lambda row: (row["priority"], len(row["ja"])))


def fallback_runs(english: str, japanese: str, global_index: dict, local_rows: list[dict]):
    tokens = [token for token in HELPERS.sentence_tokens(english) if token.lower() not in FALLBACK_STOPWORDS]
    for token in tokens:
        row = lookup_word(token, global_index, local_rows)
        if row:
            raw = [
                {"type": "en", "text": token, "ruby": HELPERS.japanese_candidates(row["ja"])[0]},
                {"type": "ja", "text": " — " + japanese},
            ]
            return HELPERS.finalize_runs(raw), token, row["ja"], row["source"]
    # Last-resort exact-line ruby keeps the meaning correct and visible even
    # when the lesson glossary has no safe one-word replacement.
    raw = [
        {"type": "ja", "text": "内容："},
        {"type": "en", "text": english, "ruby": japanese},
    ]
    return HELPERS.finalize_runs(raw), english, japanese, "exact_line_fallback"


def prepare_lesson(number: int, manifest_row: dict, plan: dict, translations: list[dict], global_index, local_rows):
    if len(plan["captions"]) != len(translations):
        raise RuntimeError(f"H{number:03d}: caption/translation count mismatch")
    lines = []
    canonical_target_lines = mixed_lines = japanese_only_lines = 0
    for index, (caption, translation) in enumerate(zip(plan["captions"], translations), start=1):
        english = re.sub(r"</?k>", "", caption["en"]).replace(r"\N", " ")
        if english != translation["en"]:
            raise RuntimeError(f"H{number:03d} line {index}: exact lyric mismatch")
        japanese = translation["ja"]
        targets = HELPERS.english_targets(english, local_rows)
        manual = CANONICAL_MANUAL_MIXED.get((number, index))
        force_japanese_only = (number, index) in CANONICAL_JAPANESE_ONLY
        if manual:
            target_by_stem = {
                stem: target
                for target in targets
                for stem in HELPERS.stems(target["english"])
            }
            replacements = []
            for actual, reading in manual["ruby"].items():
                target = next(
                    (target_by_stem[stem] for stem in HELPERS.stems(actual) if stem in target_by_stem),
                    None,
                )
                if target is None:
                    raise RuntimeError(
                        f"H{number:03d} line {index}: manual canonical word {actual!r} is not in the sung line"
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
            runs = HELPERS.runs_from_manual(manual["mixed"], manual["ruby"])
            source = "canonical_new_words_manual"
            mixed_lines += 1
        elif force_japanese_only:
            runs = HELPERS.finalize_runs([{"type": "ja", "text": japanese}])
            replacements = []
            source = "japanese_only_reviewed_for_naturalness"
            japanese_only_lines += 1
        else:
            spans = find_high_candidates(english, japanese, local_rows)
            if spans:
                runs = HELPERS.runs_from_spans(japanese, spans)
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
                source = "canonical_new_words"
                mixed_lines += 1
            else:
                runs = HELPERS.finalize_runs([{"type": "ja", "text": japanese}])
                replacements = []
                source = (
                    "japanese_only_no_safe_canonical_span"
                    if targets
                    else "japanese_only_no_canonical_target"
                )
                japanese_only_lines += 1
        canonical_target_lines += int(bool(targets))
        lines.append(
            {
                "line": index,
                "start": caption["start"],
                "end": caption["end"],
                "english": english,
                "japanese": japanese,
                "mixed": "".join(run["text"] for run in runs),
                "runs": runs,
                "canonical_targets": [
                    {
                        "english": target["english"],
                        "canonical_word": target["row"]["word"],
                        "meaning": target["row"]["ja"],
                    }
                    for target in targets
                ],
                "replacements": replacements,
                "preparation": source,
            }
        )
    return {
        "lesson": f"H{number:03d}",
        "title_ja": manifest_row["title"].split("—", 1)[-1].strip(),
        "policy": "Exact adopted lyric; word-synchronous fixed-size color-only lyric highlight. Only canonical new vocabulary from the current lesson may appear in English below. No whole-course or easy-word fallback. Lines without a safe canonical replacement remain natural Japanese. Japanese-meaning ruby appears on every English segment and hiragana ruby on every Japanese kanji.",
        "translation_source": "Exact adopted lyric Japanese translation; current-lesson canonical Teacher Tacos English vocabulary replacement and ruby validation",
        "line_count": len(lines),
        "canonical_target_lines": canonical_target_lines,
        "mixed_lines": mixed_lines,
        "japanese_only_lines": japanese_only_lines,
        "noncanonical_replacements": 0,
        "lines": lines,
    }


def parse_range(value: str) -> list[int]:
    numbers = set()
    for part in value.split(","):
        if "-" in part:
            start, end = (int(item) for item in part.split("-", 1))
            numbers.update(range(start, end + 1))
        else:
            numbers.add(int(part))
    if not numbers or min(numbers) < 1 or max(numbers) > 160:
        raise argparse.ArgumentTypeError("lessons must be within H1-H160")
    return sorted(numbers)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lessons", default="1-160")
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    requested = parse_range(args.lessons)
    manifest = read_json(MANIFEST)
    lesson_data = read_json(LESSONS)
    cache = ensure_translations(manifest, requested, args.workers)
    global_index, local = build_dictionaries(lesson_data)
    summary_rows = []
    review = [
        "# 高校生編 H001〜H160 採用歌詞・英語混じり全ルビ字幕",
        "",
        "- 上段は採用歌詞を一字句も変えず、歌唱中の語を順に強調。",
        "- 下段は同じ行の意味を表す英語混じり日本語。英語には日本語の意味ルビ、日本語の漢字には読みルビ。",
        "",
    ]
    total_lines = total_targets = total_mixed = total_japanese_only = 0
    for number in requested:
        row = manifest["lessons"][number - 1]
        plan_path = PIPELINE / f"H{number:03d}" / "planning" / "video_plan.json"
        if not plan_path.exists():
            raise FileNotFoundError(plan_path)
        plan = read_json(plan_path)
        prepared = prepare_lesson(
            number, row, plan, cache["lessons"][f"H{number:03d}"], global_index, local[number]
        )
        output = PIPELINE / f"H{number:03d}" / "planning" / "mixed_ruby.json"
        output.write_text(json.dumps(prepared, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        summary_rows.append(
            {
                "lesson": prepared["lesson"],
                "path": str(output.relative_to(PROJECT)),
                "lines": prepared["line_count"],
                "canonical_target_lines": prepared["canonical_target_lines"],
                "mixed_lines": prepared["mixed_lines"],
                "japanese_only_lines": prepared["japanese_only_lines"],
                "noncanonical_replacements": 0,
            }
        )
        total_lines += prepared["line_count"]
        total_targets += prepared["canonical_target_lines"]
        total_mixed += prepared["mixed_lines"]
        total_japanese_only += prepared["japanese_only_lines"]
        review.extend([f"## {prepared['lesson']} {prepared['title_ja']}", ""])
        for line in prepared["lines"]:
            review.append(f"{line['line']:02d}. `{line['mixed']}`")
            review.append(f"    - EN: {line['english']}")
            review.append("    - ルビ: " + " / ".join(f"{item['english']}→{item['reading']}" for item in line["replacements"]))
        review.append("")
    summary = {
        "range": args.lessons,
        "counts": {
            "lessons": len(summary_rows),
            "lines": total_lines,
            "canonical_target_lines": total_targets,
            "mixed_lines": total_mixed,
            "japanese_only_lines": total_japanese_only,
            "noncanonical_replacements": 0,
        },
        "lessons": summary_rows,
    }
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REVIEW.write_text("\n".join(review) + "\n", encoding="utf-8")
    print(json.dumps(summary["counts"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
