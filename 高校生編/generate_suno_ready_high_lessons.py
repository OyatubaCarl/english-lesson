#!/usr/bin/env python3
"""Generate Suno-ready lyric/style sheets for high-school lessons without songs."""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path

from high_text_corrections import CORRECTIONS, apply_lesson_corrections


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "taco_course_mockup" / "high_lessons.json"
OUTPUT = HERE / "suno_ready" / "H046-H160"
MASTER = HERE / "SUNO投入用_未作成115レッスン_H046-H160.md"
INDEX = HERE / "SUNO未作成レッスン一覧_H046-H160.md"
CORRECTION_REPORT = HERE / "高校生編_H046-H160_本文校正一覧.md"
CORRECTED_SOURCE = OUTPUT / "corrected_english_H046-H160.json"


COMMON_SUFFIX = (
    "Clear young-adult English lead vocal with neutral pronunciation and precise consonants. "
    "Mature high-school educational tone, memorable but not childish. "
    "Verse-led through-composed arrangement; sing every lyric line exactly once, with no repeated chorus. "
    "Restrained melodic range, short instrumental intro, very light outro. "
    "No rap, no spoken narration, no ad-libs, no choir-heavy ending, no excessive melisma, no Japanese lyrics."
)


PROFILES = {
    "civic": {
        "ja": "社会・制度 — 思考的シネマティック・インディーポップ",
        "prompt": "Thoughtful cinematic indie pop, 88 BPM, steady 4/4, warm piano, brushed drums, subtle bass pulse, and restrained low strings. Dignified documentary mood that gradually opens toward hope.",
    },
    "economy": {
        "ja": "経済・仕事 — モダン・リズミック・インディーポップ",
        "prompt": "Clean modern rhythmic indie pop, 96 BPM, muted electric piano, soft plucked synth, precise bass, and light electronic-acoustic drums. Intelligent, energetic, and easy to follow without sounding corporate.",
    },
    "nature": {
        "ja": "自然・環境 — オーガニック・シネマティック・フォークポップ",
        "prompt": "Organic cinematic folk-pop, 86 BPM, acoustic guitar, felt piano, airy strings, gentle woodwinds, and natural percussion. Spacious, observant, and emotionally grounded, with a subtle rise in the final section.",
    },
    "tech": {
        "ja": "技術・未来 — 前向きなシネマティック・シンセポップ",
        "prompt": "Forward-looking cinematic synth-pop, 100 BPM, warm arpeggiated synth, piano, rounded electronic bass, and clean hybrid drums. Curious and human rather than robotic, with controlled futuristic color.",
    },
    "health": {
        "ja": "医療・健康 — 希望を保つアンビエントポップ",
        "prompt": "Hopeful ambient pop, 88 BPM, clear piano motif, warm pads, acoustic-electronic percussion, and soft strings. Respectful and resilient, never sensational or melodramatic.",
    },
    "action": {
        "ja": "行動・スポーツ — アップリフティング・インディーロック",
        "prompt": "Uplifting indie pop-rock, 108 BPM, clean electric guitars, firm live drums, melodic bass, and a cinematic lift. Energetic and motivational while keeping every English word clearly intelligible.",
    },
    "science": {
        "ja": "科学・発見 — アトモスフェリック・シンセポップ",
        "prompt": "Atmospheric cinematic synth-pop, 84 BPM, glassy pads, soft mallets, delicate arpeggiators, piano, and slowly widening strings. A sense of discovery, scale, and quiet wonder.",
    },
    "philosophy": {
        "ja": "哲学・内省 — 空間的なチェンバーポップ",
        "prompt": "Spacious chamber-pop, 78 BPM, felt piano, cello, subtle ambient texture, and minimal percussion. Reflective, intimate, and intellectually calm, leaving breathing room between ideas.",
    },
    "heavy": {
        "ja": "戦争・喪失・重い社会問題 — 荘重なチェンバーバラード",
        "prompt": "Solemn cinematic chamber ballad, 74 BPM, low strings, sparse piano, distant ambient texture, and restrained percussion. Compassionate and anti-sensational, with no triumphant or militaristic feeling.",
    },
    "arts": {
        "ja": "芸術・表現 — 洗練されたアートポップ",
        "prompt": "Sophisticated cinematic art-pop, 92 BPM, expressive piano, elegant strings, clean bass, and lightly asymmetric percussion. Visually evocative, emotionally mature, and rhythmically clear.",
    },
    "history": {
        "ja": "歴史・社会変化 — シネマティック・フォークオーケストラ",
        "prompt": "Cinematic folk-orchestral song, 82 BPM, piano, acoustic guitar, measured frame drums, cello, and gradually expanding strings. Historical scale without bombast, with a reflective present-day perspective.",
    },
    "culture": {
        "ja": "文化・伝統 — 温かいワールドフォーク・アートポップ",
        "prompt": "Warm world-folk art-pop, 92 BPM, acoustic strings, piano, hand percussion, and carefully restrained regional color. Respectful, contemporary, and never novelty music or caricature.",
    },
    "adventure": {
        "ja": "冒険・探検 — 広がりのあるシネマティック・フォークロック",
        "prompt": "Expansive cinematic folk-rock, 106 BPM, driving acoustic guitar, clean electric guitar, live drums, and broad strings. A steady feeling of movement, courage, and discovery.",
    },
    "daily": {
        "ja": "日常・街 — 温かいアコースティック・シティポップ",
        "prompt": "Warm acoustic city-pop, 100 BPM, clean guitar, piano, melodic bass, and light live drums. Natural everyday motion, gentle nostalgia, and an unforced memorable melody.",
    },
    "tension": {
        "ja": "事件・警告 — 抑制したノワール・トリップホップ",
        "prompt": "Restrained noir trip-hop, 82 BPM, upright bass, brushed drums, low piano, subtle electronic pulse, and sparse strings. Suspenseful but not frightening, with exceptionally clear vocal phrasing.",
    },
    "travel": {
        "ja": "旅・異文化 — 陽光のあるアコースティックポップ",
        "prompt": "Sunlit acoustic pop with subtle bossa and world-folk hints, 102 BPM, nylon guitar, soft hand percussion, piano, and warm bass. Open, observant, and gently cinematic.",
    },
    "human": {
        "ja": "家族・人生 — 親密なインディーフォーク／ピアノバラード",
        "prompt": "Intimate indie folk and piano ballad, 80 BPM, acoustic guitar, felt piano, cello, and very light drums. Warm, honest, and emotionally restrained, building to quiet hope rather than a huge climax.",
    },
}


PROFILE_LESSONS = {
    "civic": [46, 50, 53, 55, 56, 58, 76, 77, 85, 86, 89, 92, 96, 109, 117, 118, 133, 136, 142, 148, 156],
    "economy": [47, 48, 82, 95, 104, 149],
    "nature": [49, 62, 63, 72, 78, 84, 97, 121, 129],
    "tech": [51, 65, 79, 98, 113, 128, 139, 150],
    "health": [52, 73, 93, 107, 141],
    "action": [54, 102, 127],
    "science": [57, 61, 67, 69, 90, 137, 159],
    "philosophy": [59, 80, 99, 110, 114, 120, 124],
    "heavy": [60, 108, 115, 132, 147, 151, 155],
    "arts": [64, 71, 83, 100, 123, 130, 138, 160],
    "history": [66, 68, 70],
    "culture": [74, 75, 126, 135, 152, 153, 157],
    "adventure": [81],
    "daily": [87, 94, 103, 145],
    "tension": [88, 101, 125],
    "travel": [91, 154, 158],
    "human": [105, 106, 111, 112, 116, 119, 122, 131, 134, 140, 143, 144, 146],
}


SPECIAL_MODIFIERS = {
    49: " Keep the verses cool and factual, then widen the strings for the call to international cooperation.",
    51: " Add a subtle unresolved harmonic tension; never use a robotic or vocoder lead voice.",
    54: " Use the energy of a stadium warm-up, not a victory anthem; keep the ethical idea of fair play central.",
    56: " Add a quiet newsroom pulse and a serious, watchful atmosphere.",
    57: " Add faint electrical-coil textures and an early-industrial sense of wonder around Tesla's dream.",
    60: " Treat the subject as an antiwar reflection; avoid snare-march rhythms and heroic brass.",
    64: " Use small asymmetric rhythmic accents suggesting Cubism, but keep the vocal meter easy to follow.",
    68: " Build historical tension without turning revolution into a triumphant battle song.",
    69: " Begin almost weightless and expand gradually into a vast cosmic soundscape near the final lines.",
    74: " Add distant festival bells and hand drums, used sparingly and without a cartoon tone.",
    80: " Let the piano phrases feel like questions and answers, with meaningful pauses after rhetorical questions.",
    88: " Add a subtle detective-jazz color with muted trumpet used only between lyric sections.",
    91: " Add understated Mediterranean nylon guitar and accordion colors without becoming tourist music.",
    100: " Use a spacious museum-like reverb and delicate musical colors that appear and disappear like paintings.",
    101: " Keep a measured courtroom pulse and leave a short silence before the verdict line.",
    102: " Add stadium-scale lift and athletic momentum, but keep the arrangement clean enough for study.",
    107: " Use a slightly faster 96 BPM pulse suggesting coordinated emergency work, without thriller exaggeration.",
    108: " Make silence part of the arrangement; no gunshot sound effects and no heroic military color.",
    110: " Use an extremely spacious cosmic texture while keeping the lead vocal close and human.",
    113: " Contrast a bright digital surface with a more anxious harmonic undertone.",
    115: " Add a restrained field-report urgency; never use battle sound effects.",
    119: " Let the melody feel patient and handmade, with a warm late-life sense of discovery.",
    120: " Keep harmful quoted words stark and brief, then move toward warmth when supportive words appear.",
    121: " Use cold glassy textures and slow low strings, with a fragile rather than spectacular mood.",
    123: " Add expressive art-rock guitar swells like brushstrokes, but keep the core intimate and compassionate.",
    126: " Add very subtle koto-like plucked texture and bamboo flute color within the modern arrangement.",
    128: " Use a precise motor-like pulse that softens whenever human responsibility is discussed.",
    130: " Let the instrumentation gradually demonstrate music's emotional power through a controlled orchestral swell.",
    135: " Add subtle Japanese ambient-folk color: soft wooden percussion, plucked strings, and spacious water-like reverb.",
    138: " Add elegant silent-film piano gestures and light pizzicato strings without turning comedic.",
    139: " Use a broad futuristic atmosphere and a hopeful but unresolved final chord.",
    143: " Make acoustic piano the emotional center, with the sound of memory suggested by soft room reverb.",
    151: " Use a memorial tone; no explosion effects, military drums, or triumphant climax.",
    152: " Add a respectful modal clarinet and cello color, avoiding stereotyped or celebratory caricature.",
    153: " Blend restrained Japanese plucked-string color with modern piano, emphasizing craft and patience.",
    157: " Use mature theatrical Japanese folk color with restrained flute and taiko; mysterious and playful, not childish.",
    160: " Add chic Parisian art-pop and subtle chanson color, with crisp runway momentum and no cabaret parody.",
}


CONTENT_NOTES = {
    60: "戦争・核兵器を扱う。反戦的で荘重な演出を維持する。",
    68: "革命・処刑・暴力を扱う可能性があるため、英雄化しない。",
    108: "戦闘、死、PTSD、自殺への言及を含む。効果音で刺激を強めない。",
    115: "戦地報道と死傷を扱う。ニュース的な抑制を保つ。",
    120: "暴言と自殺への言及を含む。引用部分を煽らない。",
    123: "精神的不調と自死への言及を含む。人物への敬意を優先する。",
    125: "詐欺被害を扱う。恐怖演出より注意喚起を優先する。",
    132: "いじめ経験を扱う。被害描写を見世物にしない。",
    136: "政治と金銭を扱う。党派的な勝利演出を避ける。",
    147: "貧困を扱う。当事者を受け身・悲惨さだけで描かない。",
    151: "核兵器と被爆を扱う。追悼と平和を中心にする。",
    152: "宗教史と差別を扱う。特定文化の音楽的ステレオタイプを避ける。",
    155: "戦争、PTSD、帰還兵を扱う。回復を単純化しない。",
    156: "LGBTQ+の権利を扱う。尊厳と当事者性を守る。",
    160: "職場の時間的圧力と身体的負担を扱う。威圧を煽らず、改善へ向かう演出にする。",
}


def profile_map() -> dict[int, str]:
    result: dict[int, str] = {}
    for profile, lessons in PROFILE_LESSONS.items():
        for lesson in lessons:
            if lesson in result:
                raise ValueError(f"duplicate style profile for H{lesson}")
            result[lesson] = profile
    expected = set(range(46, 161))
    if set(result) != expected:
        raise ValueError(f"profile coverage mismatch: missing={sorted(expected-set(result))}, extra={sorted(set(result)-expected)}")
    return result


def normalize_sentences(raw: list[str]) -> list[str]:
    """Fix extraction-only splits while preserving the actual English wording."""
    cleaned = [re.sub(r"\s+", " ", line.replace("“", '"').replace("”", '"')).strip() for line in raw]
    merged: list[str] = []
    i = 0
    while i < len(cleaned):
        current = cleaned[i]
        # JSON extraction split decimals such as 13. + 8 billion and abbreviations such as Mr. + Tanaka.
        if i + 1 < len(cleaned) and re.search(r"\b\d+\.$", current) and re.match(r"^\d", cleaned[i + 1]):
            current = current[:-1] + "." + cleaned[i + 1]
            i += 1
        elif i + 1 < len(cleaned) and current in {"Mr.", "Mrs.", "Ms.", "Dr."}:
            current = current + " " + cleaned[i + 1]
            i += 1
        # Quotes are punctuation, not sung content; removing them also prevents unbalanced extraction fragments.
        current = current.replace('"', "").strip()
        current = re.sub(r"\s+([,.;:!?])", r"\1", current)
        merged.append(current)
        i += 1
    return merged


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)*", text))


def balanced_sections(lines: list[str]) -> list[list[str]]:
    total = sum(word_count(line) for line in lines)
    section_count = max(3, min(6, math.ceil(total / 52)))
    target = total / section_count
    sections: list[list[str]] = []
    current: list[str] = []
    current_words = 0
    for line in lines:
        remaining_lines = len(lines) - sum(len(s) for s in sections) - len(current)
        remaining_sections = section_count - len(sections)
        wc = word_count(line)
        if current and current_words + wc > target and remaining_lines >= remaining_sections:
            sections.append(current)
            current = []
            current_words = 0
        current.append(line)
        current_words += wc
    if current:
        sections.append(current)
    while len(sections) > 6:
        sections[-2].extend(sections[-1])
        sections.pop()
    return sections


def section_labels(count: int) -> list[str]:
    table = {
        3: ["Verse 1", "Verse 2", "Outro"],
        4: ["Verse 1", "Verse 2", "Bridge", "Outro"],
        5: ["Verse 1", "Verse 2", "Verse 3", "Bridge", "Outro"],
        6: ["Verse 1", "Verse 2", "Verse 3", "Bridge", "Verse 4", "Outro"],
    }
    return table[count]


def lyrics_block(lines: list[str]) -> str:
    sections = balanced_sections(lines)
    labels = section_labels(len(sections))
    parts = []
    for label, section in zip(labels, sections):
        parts.append(f"[{label}]\n" + "\n".join(section))
    return "\n\n".join(parts)


def topic_from_title(title: str) -> str:
    match = re.search(r"「(.+?)」", title)
    return match.group(1) if match else title.split("—")[-1].strip()


def style_prompt(lesson: int, profile: str) -> str:
    base = PROFILES[profile]["prompt"]
    modifier = SPECIAL_MODIFIERS.get(lesson, "")
    return f"{base}{modifier} {COMMON_SUFFIX}"


def lesson_markdown(lesson: dict, profile: str) -> tuple[str, dict]:
    number = lesson["src"]["lesson"]
    title = lesson["title"]
    topic = topic_from_title(title)
    lines = normalize_sentences(lesson["enSentences"])
    lines, corrections = apply_lesson_corrections(number, lines)
    lyrics = lyrics_block(lines)
    words = sum(word_count(line) for line in lines)
    duration = words / 82.0
    prompt = style_prompt(number, profile)
    content_note = CONTENT_NOTES.get(number)

    md = [
        f"# H{number:03d} {topic}",
        "",
        f"- レッスン：{title}",
        f"- 文法ターゲット：{lesson['grammar']['target']}",
        "- 動画状態：未作成（`high_lessons.json` の `video` が空）",
        f"- 音楽系統：{PROFILES[profile]['ja']}",
        f"- 本文校正：{len(corrections)}件（校正一覧に修正前・修正後を記録）",
        f"- 歌詞語数：{words}語（目安 {int(duration)}分{int((duration-int(duration))*60):02d}秒〜、生成結果により変動）",
    ]
    if content_note:
        md.append(f"- 内容上の注意：{content_note}")
    md += [
        "",
        "## Suno Title",
        "",
        "```text",
        f"H{number:03d} — {topic}",
        "```",
        "",
        "## Styles",
        "",
        "```text",
        prompt,
        "```",
        "",
        "## Lyrics",
        "",
        "```text",
        lyrics,
        "```",
        "",
        "## 投入時の注意",
        "",
        "- Customモードで使用する。",
        "- 歌詞は本文同期を優先し、各行を1回ずつ歌わせる。",
        "- Sunoが自動でサビを反復した生成は不採用にする。",
        "- 英語の聞き取りやすさを最優先し、発音が潰れた固有名詞・数値は再生成する。",
        "",
    ]
    manifest = {
        "lesson": number,
        "book": lesson["src"]["book"],
        "title": title,
        "topic": topic,
        "grammar_target": lesson["grammar"]["target"],
        "video": lesson.get("video"),
        "status": "song_video_missing",
        "profile": profile,
        "profile_ja": PROFILES[profile]["ja"],
        "style_prompt": prompt,
        "english_lines": lines,
        "lyrics": lyrics,
        "word_count": words,
        "correction_count": len(corrections),
        "corrections": corrections,
        "content_note": content_note,
        "file": f"H{number:03d}.md",
    }
    return "\n".join(md), manifest


def main() -> None:
    source_bytes = SOURCE.read_bytes()
    lessons = json.loads(source_bytes)
    profiles = profile_map()
    missing = [row for row in lessons if 46 <= row["src"]["lesson"] <= 160 and not row.get("video")]
    if len(missing) != 115:
        raise ValueError(f"expected 115 missing song videos, got {len(missing)}")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    manifests = []
    full_sections = []
    for lesson in missing:
        number = lesson["src"]["lesson"]
        md, manifest = lesson_markdown(lesson, profiles[number])
        (OUTPUT / f"H{number:03d}.md").write_text(md, encoding="utf-8")
        manifests.append(manifest)
        full_sections.append(md)

    source_sha = hashlib.sha256(source_bytes).hexdigest()
    manifest_payload = {
        "generated_from": str(SOURCE.relative_to(ROOT)),
        "source_sha256": source_sha,
        "criteria": "lesson 46-160 and video is null/empty",
        "count": len(manifests),
        "correction_count": sum(item["correction_count"] for item in manifests),
        "lessons": manifests,
    }
    (OUTPUT / "manifest.json").write_text(
        json.dumps(manifest_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    CORRECTED_SOURCE.write_text(
        json.dumps(
            [
                {
                    "lesson": item["lesson"],
                    "title": item["title"],
                    "grammar_target": item["grammar_target"],
                    "english_lines": item["english_lines"],
                }
                for item in manifests
            ],
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    correction_count = sum(item["correction_count"] for item in manifests)
    report_lines = [
        "# 高校生編 H046〜H160 本文校正一覧",
        "",
        f"- 対象：動画未作成の115レッスン",
        f"- 校正：全{correction_count}件",
        "- 方針：意味を保ちながら、文法・語法・自然さ・事実関係・教材としての安全性を修正。",
        "- 元の `taco_course_mockup/high_lessons.json` は変更せず、Suno投入用成果物へ校正版を反映。",
        "",
    ]
    for item in manifests:
        if not item["corrections"]:
            continue
        report_lines += [f"## H{item['lesson']:03d} {item['topic']}", ""]
        for change in item["corrections"]:
            report_lines += [
                f"- 修正前：{change['before']}",
                f"  修正後：{change['after']}",
            ]
        report_lines.append("")
    CORRECTION_REPORT.write_text("\n".join(report_lines), encoding="utf-8")

    readme = f"""# H046〜H160 Suno投入用データ

`taco_course_mockup/high_lessons.json` で `video` が空の115レッスンを抽出。

- 個別ファイル：`H046.md`〜`H160.md`
- 機械可読データ：`manifest.json`
- 校正済み英文：`corrected_english_H046-H160.json`
- 本文校正：全{correction_count}件（`../../高校生編_H046-H160_本文校正一覧.md`）
- 元データSHA-256：`{source_sha}`
- 判定基準：H46〜H160かつ `video` が `null` または空

歌詞は英文本文を省略せず、抽出時に分断された小数（例：13. + 8）と敬称（Mr. + 姓）を結合したうえで、監査済みの文法・語法・事実関係・安全表現の校正を適用した。修正前後は校正一覧に記録している。
"""
    (OUTPUT / "README.md").write_text(readme, encoding="utf-8")

    index_lines = [
        "# 高校生編 Suno未作成レッスン一覧（H46〜H160）",
        "",
        "判定基準：`taco_course_mockup/high_lessons.json` の `video` が空。高1 H1〜H45は動画ID登録済みのため対象外。",
        "",
        f"全{len(manifests)}曲。歌詞とStylesは各リンク先にSuno貼り付け用のコードブロックで収録。",
        f"本文校正は全{correction_count}件。修正前後は [本文校正一覧](高校生編_H046-H160_本文校正一覧.md) に収録。",
        "",
        "| Lesson | 主題 | 文法ターゲット | 推奨音楽系統 |",
        "|---|---|---|---|",
    ]
    for item in manifests:
        link = f"suno_ready/H046-H160/{item['file']}"
        index_lines.append(
            f"| [H{item['lesson']:03d}]({link}) | {item['topic']} | {item['grammar_target']} | {item['profile_ja']} |"
        )
    INDEX.write_text("\n".join(index_lines) + "\n", encoding="utf-8")

    master_header = f"""# 高校生編 Suno投入用・未作成115レッスン統合版

## 対象

- H46〜H160
- `taco_course_mockup/high_lessons.json` で `video` が空のレッスン
- 全115曲

## 共通方針

- 本文を省略せず、各英文を1回ずつ歌う通作形式。
- 自動生成された反復サビは採用しない。
- 全曲で「明瞭な若い成人の英語声・正確な子音・過度な節回しなし」を共通化。
- 主題に応じて17の音楽系統を使い分ける。
- 小数・敬称の抽出分断を結合し、文法・語法・事実関係・教材としての安全性を校正済み。
- 修正前後は `高校生編_H046-H160_本文校正一覧.md` に記録。

---

"""
    MASTER.write_text(master_header + "\n---\n\n".join(full_sections), encoding="utf-8")
    print(f"generated {len(manifests)} lesson files")
    print(INDEX)
    print(MASTER)
    print(CORRECTION_REPORT)


if __name__ == "__main__":
    main()
