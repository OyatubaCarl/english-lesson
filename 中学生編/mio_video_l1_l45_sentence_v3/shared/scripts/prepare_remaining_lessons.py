#!/usr/bin/env python3
"""Prepare sentence-level L17-L45 plans from the middle-school source.

This script does not overwrite any original video.  It extracts the English and
Japanese source text, aligns every English sentence to the Taco Beat word timing,
and writes planning data plus one ImageGen brief per sentence.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

from lxml import html


PROJECT_ROOT = Path("/Users/masaki/Documents/ClaudeCode/英語学習教材作成")
VIDEO_ROOT = PROJECT_ROOT / "中学生編" / "mio_video_l1_l45_sentence_v3"
REF_ROOT = VIDEO_ROOT / "shared" / "face_references"

LESSON_TITLES = {
    17: ("Choosing the Best in Class", "クラスで『一番』を決める"),
    18: ("Tom and Me", "トムとわたし"),
    19: ("At the Museum", "博物館で"),
    20: ("The Town Craft Market", "町の工芸市場"),
    21: ("On Grandmother's Veranda", "祖母の縁側で"),
    22: ("The Old Album", "古いアルバム"),
    23: ("Friday Night", "金曜日の夜"),
    24: ("Getting Ready for a Trip", "旅行の準備"),
    25: ("Reading on a Winter Night", "冬の夜の読書"),
    26: ("The Teacher's Wish", "先生の願い"),
    27: ("What I Want to Know", "知りたいこと"),
    28: ("The Family Album", "家族アルバム"),
    29: ("A Book from the Library", "図書館の一冊"),
    30: ("A Sunday Walk", "日曜日の散歩"),
    31: ("An Afternoon Alone", "ひとりの午後"),
    32: ("A Day in Town", "町の一日"),
    33: ("A Lively Dinner Table", "食卓のにぎわい"),
    34: ("The Day I Caught a Cold", "かぜをひいた日"),
    35: ("The Lake at Sunset", "夕暮れの湖"),
    36: ("At Grandfather's Farm", "祖父の農場で"),
    37: ("A New School Year", "新しい学年"),
    38: ("A Letter from My Uncle", "叔父からの手紙"),
    39: ("The Mystery of Time", "時間のふしぎ"),
    40: ("Art Class", "美術の時間"),
    41: ("A Quiet Morning at Home", "静かな朝の家"),
    42: ("Sports Day", "運動会の一日"),
    43: ("Many Kinds of Jobs", "いろいろな仕事"),
    44: ("The Envelope That Arrived", "届いた封筒"),
    45: ("At the Shopping Street", "商店街にて"),
}

# The setting note is deliberately broad.  It anchors continuity while leaving
# ImageGen free to choose the clearest composition for each English sentence.
LESSON_SETTINGS = {
    17: "school lunch in the small mountain-village middle-school classroom; navy school uniforms",
    18: "school, park, and Mio's home across cold late-autumn days; practical layered clothes outdoors",
    19: "local history museum on a cool day; neat casual outing clothes",
    20: "covered craft market in the old town center after the museum visit; cool-weather outing clothes",
    21: "grandmother Fumi's sunny wooden veranda and garden in mild autumn; comfortable home clothes",
    22: "Mio's warm family living room on a winter Sunday; cozy knit home clothes; memories appear as soft-edged visual vignettes, never memorial portraits",
    23: "Mio's house on Friday evening; each person stays in the room appropriate to the action; casual indoor clothes",
    24: "trip planning at home before departure; every destination or packed item is visibly imagined, sketched, or discussed rather than already happening",
    25: "Mio's bedroom and living room on a snowy winter night; warm pajamas or knit indoor clothes",
    26: "small mountain-village middle school during the day; navy school uniforms; teacher-led classroom scenes",
    27: "school and home research scenes; navy uniform at school and casual home clothes; questions may appear as soft visual thought vignettes without readable text",
    28: "family living room at night with an old album; memories shown as living flashback vignettes, not framed memorial photographs",
    29: "quiet town library and Mio's reading spaces; season-appropriate casual clothes",
    30: "Sunday walk through the mountain village, river path, fields, and town; comfortable walking clothes",
    31: "Mio alone in the same wooden house during a rainy afternoon through evening; no family visible until they return at night",
    32: "one continuous day around the old town center; clothing and weather stay consistent within the lesson",
    33: "family dinner in the south-facing living-dining room; only people required by each sentence, casual indoor clothes",
    34: "Mio's bedroom, village clinic, and recovery at home; Mio wears pajamas or patient-appropriate layers, never a school uniform in bed",
    35: "quiet lakeside at sunset near the village; practical light jacket and walking clothes",
    36: "grandfather's working farm in the countryside; boots, workwear, and clothes suited to animals and soil",
    37: "first days of a new school year at the village middle school; clean navy uniforms and spring light",
    38: "Mio's home while reading an uncle's letter; imagined overseas places use soft vignette edges so they are not mistaken for present reality",
    39: "home and school reflections about time; memories and imagined time visibly separated from present reality",
    40: "art classroom with easels, clay, brushes, and mountain-window light; navy uniform protected by art smocks when needed",
    41: "same wooden family house during one quiet morning; individual actions remain in their correct separate rooms",
    42: "school sports day on the mountain-view field; athletic gym uniforms, hats where appropriate, no formal school jackets during competition",
    43: "career discussion at school and imagined workplaces; navy uniforms in class, job scenes clearly framed as aspirations",
    44: "Mio's house when an envelope arrives; its contents appear as an unfolding thought or memory, without readable writing",
    45: "Sunday shopping in the village's old covered shopping street; comfortable casual clothes, continuous shopping bags and wallet",
}

COMMON_PROMPT = (
    "Create one polished 16:9 cinematic educational story illustration, composed for 1920x1080. "
    "Warm contemporary Japanese anime picture-book style, soft painterly light, expressive natural faces, clean anatomy. "
    "This is one continuous single image, not a split panel or collage. The picture must communicate the English sentence immediately. "
    "Preserve every referenced character's face, hair, age, and body proportions; references lock identity only, not clothing. "
    "Use only the people necessary for this exact sentence. Match clothing to setting, season, weather, and activity. "
    "Leave the lower quarter visually calm because bilingual captions will be added later. "
    "No captions, no speech balloons, no readable text, no letters or numbers, no logos, no watermark."
)

# Paragraph-level translations where the current Japanese paragraph does not
# contain one sentence for every English image.
JA_OVERRIDES: dict[tuple[int, int], list[str]] = {
    (17, 4): [
        "「どの本が一番好き？」とトムが聞きました。",
        "わたしはかばんから一冊取り出しました。",
        "「わたしはこの本が一番面白いと思う」と言いました。",
    ],
    (18, 1): ["トムとわたしは仲良しで、いろいろなところが似ています。"],
    (19, 3): [
        "次の部屋には古い本がありました。",
        "その本は多くの人に愛されています。",
        "毎年、たくさんの生徒に読まれています。",
    ],
    (20, 2): [
        "入り口には大きな絵がありました。",
        "「この絵はお父さんが描いたんですか？」とトムが聞きました。",
        "「いいえ、父が描いたのではありません。",
        "父の友人が描いたんです」とお店の人は答えました。",
    ],
    (20, 3): [
        "店の中には、素朴なテーブルがたくさん並んでいました。",
        "「何でできているんですか？」と妹が聞きました。",
        "「地元の山の木で作られているんですよ」とお店の人は笑って答えました。",
    ],
    (22, 2): [
        "アルバムには、兄が山のてっぺんに立っている写真がありました。",
        "「トム、高い山に登ったことある？」とわたしは聞きました。",
        "「いや、ぼくは一度もないな」とトムは答えました。",
        "妹は雪を一度も見たことがなく、少し寂しそうにそう言いました。",
    ],
    (22, 4): [
        "わたしはこの本を2回読みました。それくらい面白いんです。",
        "兄は、こんなに甘いケーキは今まで食べたことがないと言っていました。",
    ],
    (23, 2): [
        "わたしは妹にも、もう宿題を終えたのかと聞きました。",
        "妹は「うん、夕食の前にもう終わらせたよ」と笑顔で答えました。",
    ],
    (23, 3): [
        "でも、兄はまだ本を読んでいました。",
        "「その英語の本はもう読んだ？」とわたしは聞きました。",
        "「いや、まだ読んでいないよ」と兄は答えました。",
    ],
    (24, 2): [
        "「何を持っていけばいい？」と妹が聞きました。",
        "兄はちょっと考えました。",
        "「そんなに多くなくていいよ。",
        "荷物のまとめ方は知っているから」と兄は答えました。",
    ],
    (24, 3): [
        "「どこに泊まる予定なの？」とわたしは父に聞きました。",
        "「静かな小さなホテルにもう決めてあるよ」と父は言いました。",
        "「いつ出発するか、もう決めた？」とわたしは聞きました。",
        "「うん、土曜日の早朝だよ」と父は笑いました。",
    ],
    (31, 6): [
        "夜、みんなにこの話をしたら、妹はうれしそうにちょっぴり涙ぐみました。",
        "「わたしもその虹、見たかった！」",
    ],
    (34, 3): [
        "母はわたしを近くの病院へ連れていきました。",
        "看護師さんはとても親切でした。",
        "お医者さんは道具を使ってわたしの胸の音を聞きました。",
        "「心配しなくて大丈夫ですよ」とお医者さんは言いました。",
    ],
    (36, 2): [
        "牧場には牛が一頭います。",
        "豚は三頭います。",
        "羊も何頭かいます。",
    ],
    (37, 3): [
        "休み時間には、みんなで校庭へ行きました。",
        "広い空の下で走ったり笑ったりしました。",
    ],
    (39, 4): [
        "父は、わたしが小さかったころの姿を見せてくれました。",
        "「時間はみんなを少しずつ変えていくんだよ」と父は言いました。",
        "時間って不思議だとわたしは思いました。",
    ],
    (42, 3): [
        "兄がボールを投げ、わたしはそれをしっかり受け止めました。",
        "「ナイスキャッチ！」と兄が叫びました。",
        "みんなの歓声が空に広がりました。",
    ],
}

REPORTING_VERBS = (
    "asked|said|answered|replied|suggested|sighed|smiled|cried|called|"
    "told|whispered|shouted|laughed"
)

TRANSITIONS = [
    "dissolve", "smoothleft", "hblur", "smoothright", "circleopen",
    "slideup", "diagtl", "radial", "fade", "diagbr",
]

# Pronouns and "we" are resolved from story context here so the recurring faces
# remain stable without adding the whole family to unrelated images.
CAST_OVERRIDES: dict[tuple[int, int], list[str]] = {
    (17, 1): ["mio", "tom"], (17, 4): ["mio", "tom"], (17, 11): ["mio", "tom"],
    (18, 3): ["mio", "tom"], (18, 4): ["mio", "tom"],
    (18, 5): ["mio", "tom"],
    (19, 1): ["mio", "tom"], (19, 3): ["mio", "tom"], (19, 9): ["mio", "tom"],
    (20, 1): ["mio", "tom", "saki"], (20, 13): ["mio", "tom", "saki"],
    (21, 3): ["fumi"], (21, 4): ["fumi", "mio"],
    (22, 9): ["hiroshi"],
    (23, 4): ["saki"], (23, 6): ["mio", "kenta"],
    (23, 7): ["kenta"], (23, 9): ["yuka"], (23, 11): ["hiroshi"],
    (24, 2): ["mio", "kenta", "saki"], (24, 12): ["tom"],
    (24, 15): ["mio", "kenta", "saki", "hiroshi", "yuka"],
    (25, 4): ["kenta"], (25, 6): ["saki"],
    (28, 14): ["tom"],
    (30, 2): ["mio", "kenta", "saki", "hiroshi", "yuka"],
    (30, 5): ["mio", "kenta", "saki", "hiroshi", "yuka"],
    (30, 7): ["mio", "kenta", "saki", "hiroshi", "yuka"],
    (30, 9): ["mio", "kenta", "saki", "hiroshi", "yuka"],
    (32, 6): ["mio", "kenta", "saki", "hiroshi", "yuka"],
    (32, 8): ["mio", "kenta", "saki", "hiroshi", "yuka"],
    (32, 13): ["mio", "kenta", "saki", "hiroshi", "yuka"],
    (32, 14): ["mio", "kenta", "saki", "hiroshi", "yuka"],
    (33, 12): ["mio", "kenta", "saki", "hiroshi", "yuka"],
    (34, 7): ["mio", "yuka"],
    (36, 6): ["mio", "kenta", "saki", "hiroshi", "yuka"],
    (36, 7): ["mio"], (36, 13): ["mio"], (36, 14): ["mio"],
    (37, 7): ["mio"], (37, 8): ["mio"], (37, 9): ["mio"],
    (40, 8): ["saki"], (40, 10): ["tom"],
    (41, 6): ["mio"], (41, 13): ["mio"],
    (42, 14): ["saki"],
    (43, 1): ["mio", "tom"],
    (45, 3): ["mio", "saki"],
}


def clean_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value)
    value = re.sub(r"\s+([,.!?;:])", r"\1", value)
    return re.sub(r"\s+", " ", value).strip()


def english_sentences(text: str) -> list[str]:
    """Split prose while retaining a quoted sentence's reporting clause."""
    text = clean_text(text).replace('"', "”")
    protected = re.sub(r"\b(Mt|Mr|Mrs|Ms|Dr|St)\.", r"\1<prd>", text)
    pieces = []
    start = 0
    for match in re.finditer(r"[.!?](?:”)?(?=\s|$)", protected):
        pieces.append(protected[start : match.end()].strip())
        start = match.end()
    tail = protected[start:].strip()
    if tail:
        pieces.append(tail)

    merged: list[str] = []
    reporting = re.compile(
        rf"^(?:(?:[A-Z][A-Za-z']*|I|he|she|my\s+\w+|the\s+\w+)\s+"
        rf"(?:{REPORTING_VERBS})\b|(?:{REPORTING_VERBS})\s+\w+\b)",
        re.I,
    )
    index = 0
    while index < len(pieces):
        current = pieces[index]
        if current.endswith("”") and index + 1 < len(pieces) and reporting.match(pieces[index + 1]):
            current += " " + pieces[index + 1]
            index += 1
        merged.append(current.replace("<prd>", "."))
        index += 1
    return merged


def japanese_sentences(text: str) -> list[str]:
    text = clean_text(text)
    parts = [item.strip() for item in re.findall(r".*?。|.+$", text) if item.strip()]
    return parts or [text]


def normalize_word(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).lower()
    return "".join(ch for ch in value if ch.isalnum())


def source_words(sentence: str) -> list[str]:
    return [item for item in sentence.split() if normalize_word(item)]


def load_beat(path: Path) -> list[list[object]]:
    source = path.read_text(encoding="utf-8")
    match = re.search(r"const BEAT=(\[.*\]);", source, re.S)
    if not match:
        raise RuntimeError(f"BEAT array not found: {path}")
    return json.loads(match.group(1))


def probe_duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nk=1:nw=1", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(result.stdout.strip())


def align_sentences(sentences: list[str], beat: list[list[object]]) -> list[list[int]]:
    timed = [(index, str(item[1])) for index, item in enumerate(beat) if normalize_word(str(item[1]))]
    targets = ["".join(normalize_word(word) for word in source_words(sentence)) for sentence in sentences]
    result: list[list[int]] = []
    cursor = 0
    for sentence_index, target in enumerate(targets):
        if sentence_index == len(targets) - 1:
            chosen = len(timed)
        else:
            remaining_min = len(targets) - sentence_index - 1
            source_count = len(source_words(sentences[sentence_index]))
            low = cursor + max(1, source_count - 7)
            high = min(len(timed) - remaining_min, cursor + source_count + 8)
            best_score = -1.0
            chosen = min(high, cursor + max(1, source_count))
            for end in range(low, high + 1):
                candidate = "".join(normalize_word(word) for _, word in timed[cursor:end])
                similarity = SequenceMatcher(None, target, candidate).ratio()
                length_penalty = abs(len(target) - len(candidate)) / max(1, len(target))
                score = similarity - 0.12 * length_penalty
                if score > best_score:
                    best_score = score
                    chosen = end
        indices = [item[0] for item in timed[cursor:chosen]]
        if not indices:
            raise RuntimeError(f"empty alignment for sentence {sentence_index + 1}: {sentences[sentence_index]}")
        result.append(indices)
        cursor = chosen
    if cursor != len(timed):
        raise RuntimeError(f"alignment did not consume chart: {cursor}/{len(timed)}")
    return result


def display_segments(sentence: str, indices: list[int], beat: list[list[object]]) -> tuple[list[str], list[list[int]]]:
    """Map the intended source wording onto imperfect ASR timing tokens.

    The displayed English always comes from the lesson source.  Adjacent source
    words can share one highlight when Suno contracts them; multiple ASR tokens
    can drive one source word when the transcription inserts or mishears words.
    """
    source = sentence.split()
    chart = [str(beat[index][1]) for index in indices]
    n, m = len(source), len(chart)
    inf = 10**9
    dp = [[inf] * (m + 1) for _ in range(n + 1)]
    prev: list[list[tuple[int, int] | None]] = [[None] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = 0.0
    for i in range(n):
        for j in range(m):
            if dp[i][j] >= inf:
                continue
            max_a = n - i if m - j == 1 else min(4, n - i)
            max_b = m - j if n - i == 1 else min(6, m - j)
            for a in range(1, max_a + 1):
                if n - (i + a) > m - (j + 1):
                    continue
                for b in range(1, max_b + 1):
                    if m - (j + b) > 6 * (n - (i + a)) and n - (i + a) > 0:
                        continue
                    left = "".join(normalize_word(item) for item in source[i : i + a])
                    right = "".join(normalize_word(item) for item in chart[j : j + b])
                    similarity = SequenceMatcher(None, left, right).ratio()
                    grouping_penalty = 0.025 * (a + b - 2)
                    cost = dp[i][j] + (1.0 - similarity) + grouping_penalty
                    if cost < dp[i + a][j + b]:
                        dp[i + a][j + b] = cost
                        prev[i + a][j + b] = (i, j)
    if prev[n][m] is None:
        raise RuntimeError(f"could not map display words: {sentence}")
    groups: list[tuple[int, int, int, int]] = []
    i, j = n, m
    while i or j:
        before = prev[i][j]
        if before is None:
            raise RuntimeError(f"broken display-word map: {sentence}")
        pi, pj = before
        groups.append((pi, i, pj, j))
        i, j = pi, pj
    groups.reverse()
    display = [" ".join(source[si:ei]) for si, ei, _, _ in groups]
    timing = [indices[sj:ej] for _, _, sj, ej in groups]
    return display, timing


def alignment_score(sentence: str, words: list[str]) -> float:
    left = "".join(normalize_word(item) for item in source_words(sentence))
    right = "".join(normalize_word(item) for item in words)
    return SequenceMatcher(None, left, right).ratio()


def choose_break(words: list[str]) -> list[int]:
    visible_counts = [max(1, len(item.split())) for item in words]
    total_visible = sum(visible_counts)
    rendered = " ".join(words)
    if total_visible <= 10 and len(rendered) <= 58:
        return []
    if len(words) < 2:
        return []
    line_count = 3 if len(rendered) > 90 else 2
    weights = [len(item) + 1 for item in words]
    total_weight = sum(weights)
    cumulative_weights: list[int] = []
    running = 0
    for weight in weights:
        running += weight
        cumulative_weights.append(running)
    breaks: list[int] = []
    previous = -1
    for part in range(1, line_count):
        target = total_weight * part / line_count
        candidates = [
            index
            for index in range(previous + 1, len(words) - (line_count - part))
            if index >= 0
        ]
        if not candidates:
            break
        chosen = min(
            candidates,
            key=lambda index: abs(cumulative_weights[index] - target)
            - (4 if words[index].endswith((",", ";", "—")) else 0),
        )
        breaks.append(chosen)
        previous = chosen
    return breaks


def scene_slug(sentence: str, fallback: str) -> str:
    terms = [normalize_word(item) for item in source_words(sentence)]
    terms = [item for item in terms if item][:6]
    return "_".join(terms)[:58] or fallback


def infer_cast(sentence: str, lesson: int) -> list[str]:
    lower = sentence.lower()
    cast: list[str] = []
    def add(name: str) -> None:
        if name not in cast:
            cast.append(name)
    if re.search(r"\b(i|me|my|mine)\b", lower):
        add("mio")
    if "tom" in lower:
        add("tom")
    if "my brother" in lower or "kenta" in lower:
        add("kenta")
    if "my sister" in lower or "saki" in lower:
        add("saki")
    if "my mother" in lower:
        add("yuka")
    if "my father" in lower:
        add("hiroshi")
    if "grandmother" in lower:
        add("fumi")
    if "pochi" in lower or "dog" in lower:
        add("pochi")
    if "teacher" in lower:
        add("teacher")
    if "yuuka" in lower:
        add("yuuka")
    if re.search(r"\b(our family|my family|everyone in my family|all of us)\b", lower):
        for name in ("mio", "kenta", "saki", "hiroshi", "yuka"):
            add(name)
    # The market owner's father is not Mio's father.
    if lesson == 20 and "painted by" in lower and "your father" in lower:
        cast = [name for name in cast if name != "hiroshi"]
    return cast


def visual_brief(sentence: str, lesson: int) -> str:
    lower = sentence.lower()
    layer = "Show this as the present action."
    if lesson == 24:
        layer = "This is planning before the trip: show the real characters discussing or packing, with any destination only as a soft-edged imagined vignette."
    elif any(term in lower for term in ("years ago", "when she was small", "when i was small", "a few years ago", "old album", "picture of")):
        layer = "Show the remembered event as a warm, living flashback vignette connected to the present observer; avoid a formal framed portrait."
    elif lesson in (38, 39, 43) and any(term in lower for term in ("will", "want to", "would", "letter", "time")):
        layer = "Make the imagined, remembered, or hoped-for part visibly distinct from present reality with a soft luminous edge."
    return f'English sentence: "{sentence}" {layer} Show the exact subject, action, emotion, and object in one clear composition.'


def references_for(cast: list[str], lesson: int, sentence: str) -> list[str]:
    refs = [
        str(REF_ROOT / ("pochi_ref.png" if name == "pochi" else f"{name}_face.png"))
        for name in cast
    ]
    lower = sentence.lower()
    anchors: list[Path] = []
    v2 = PROJECT_ROOT / "中学生編" / "mio_video_l2_l10_sentence_v2"
    if lesson in (21, 22, 23, 24, 25, 28, 31, 33, 34, 38, 39, 41, 44):
        if any(term in lower for term in ("room", "bed", "book", "home", "house", "desk", "window", "night", "morning", "dinner")):
            anchors.append(v2 / "L3" / "scenes" / "10_quiet_afternoon_same_house.png")
    if lesson in (17, 18, 26, 27, 37, 40, 42, 43):
        # Existing classroom identity is a loose visual anchor, not a layout lock.
        candidate = VIDEO_ROOT / "L14" / "scenes" / "09_tom_asks_about_river.png"
        if candidate.exists():
            anchors.append(candidate)
    return refs[:4] + [str(item) for item in anchors[:1]]


def character_guidance(cast: list[str]) -> str:
    details: list[str] = []
    if "mio" in cast:
        details.append("Mio is the girl protagonist and narrating 'I'.")
    if "tom" in cast:
        details.append("Tom is Mio's same-age freckled middle-school classmate with teal accents.")
        details.append("A single tiny unobtrusive Funnics Island cameo may appear far outside a window or on a background object, never as the focal subject.")
    if "kenta" in cast:
        details.append("Kenta is Mio's taller high-school brother; he has no freckles and must not resemble Tom.")
    if "saki" in cast:
        details.append("Saki is Mio's much younger elementary-school sister with twin tails.")
    if "hiroshi" in cast:
        details.append("Hiroshi is Mio's forty-something father with glasses.")
    if "yuka" in cast:
        details.append("Yuka is Mio's forty-something mother with short dark hair.")
    if "fumi" in cast:
        details.append("Fumi is Mio's living grandmother with tied white hair; never portray her as a memorial image.")
    if not details:
        details.append("Do not add any recurring family member or classmate unless the current sentence clearly requires that person.")
    return " ".join(details)


def build_lesson(lesson: int, dry_run: bool = False) -> dict:
    document = html.parse(str(PROJECT_ROOT / "index.html"))
    sections = document.xpath(f'//div[@id="book-middle"]//section[@data-lesson="{lesson}"]')
    if len(sections) != 1:
        raise RuntimeError(f"L{lesson}: expected one middle section, found {len(sections)}")
    section = sections[0]
    en_paragraphs = [clean_text(p.text_content()) for p in section.xpath('./div[contains(concat(" ",normalize-space(@class)," ")," en-body ")]/p')]
    ja_paragraphs = [clean_text(p.text_content()) for p in section.xpath('./div[contains(concat(" ",normalize-space(@class)," ")," jp-full ")]/p')]
    if len(en_paragraphs) != len(ja_paragraphs):
        raise RuntimeError(f"L{lesson}: paragraph mismatch")

    sentences: list[str] = []
    translations: list[str] = []
    paragraph_ids: list[int] = []
    mismatch: list[dict] = []
    for paragraph, (en_text, ja_text) in enumerate(zip(en_paragraphs, ja_paragraphs), start=1):
        en_lines = english_sentences(en_text)
        ja_lines = JA_OVERRIDES.get((lesson, paragraph), japanese_sentences(ja_text))
        ja_lines = [line.replace("ぼくたち", "わたしたち").replace("ぼく", "わたし") for line in ja_lines]
        # Restore the only two male first-person quotes in the selected corpus.
        if (lesson, paragraph) == (22, 2):
            ja_lines[2] = ja_lines[2].replace("わたしは一度も", "ぼくは一度も")
        if lesson == 43 and paragraph == 3:
            ja_lines = [line.replace("わたしはバスの運転手", "ぼくはバスの運転手") for line in ja_lines]
        if len(en_lines) != len(ja_lines):
            mismatch.append({"paragraph": paragraph, "english": en_lines, "japanese": ja_lines})
        sentences.extend(en_lines)
        translations.extend(ja_lines)
        paragraph_ids.extend([paragraph] * len(en_lines))

    if mismatch:
        return {"lesson": lesson, "mismatch": mismatch}

    chart_path = PROJECT_ROOT / "taco_beat" / "charts" / f"m{lesson}.js"
    audio_path = PROJECT_ROOT / "taco_beat" / "songs" / f"m{lesson}.mp3"
    beat = load_beat(chart_path)
    chart_words = [str(item[1]).lower() for item in beat if normalize_word(str(item[1]))]
    if chart_words[-4:] == ["thank", "you", "for", "watching"]:
        sentences.append("Thank you for watching.")
        translations.append("ご覧いただき、ありがとうございました。")
        paragraph_ids.append(max(paragraph_ids) + 1)
    alignments = align_sentences(sentences, beat)
    duration = probe_duration(audio_path)
    title_en, title_ja = LESSON_TITLES[lesson]
    slug = re.sub(r"[^a-z0-9]+", "_", title_en.lower()).strip("_")

    lines: list[dict] = []
    shots: list[dict] = []
    prompts: list[dict] = []
    scores: list[float] = []
    for index, (sentence, ja, indices, paragraph_id) in enumerate(zip(sentences, translations, alignments, paragraph_ids), start=1):
        timing_words = [str(beat[token][1]) for token in indices]
        display_words, word_indices = display_segments(sentence, indices, beat)
        score = alignment_score(sentence, timing_words)
        scores.append(score)
        filename = f"{index:02d}_{scene_slug(sentence, f'scene_{index:02d}')}.png"
        cast = CAST_OVERRIDES.get((lesson, index), infer_cast(sentence, lesson))
        lines.append({
            "indices": indices,
            "en_words": display_words,
            "word_indices": word_indices,
            "break_after": choose_break(display_words),
            "ja": ja,
            "source_en": sentence,
            "paragraph": paragraph_id,
            "alignment_score": round(score, 4),
        })
        if index == 1:
            start = 0.0
        else:
            start = max(0.0, float(beat[indices[0]][0]) - 0.04)
        if index < len(sentences):
            next_first = alignments[index][0]
            end = max(start + 0.5, float(beat[next_first][0]) - 0.04)
        else:
            end = duration

        camera = (index - 1) % 4
        if camera == 0:  # clear left-to-right pan
            start_center, end_center = [0.43, 0.49], [0.57, 0.49]
            start_zoom, end_zoom = 1.12, 1.12
        elif camera == 1:  # fixed-center pull back
            start_center = end_center = [0.50, 0.48]
            start_zoom, end_zoom = 1.12, 1.02
        elif camera == 2:  # clear right-to-left pan
            start_center, end_center = [0.57, 0.49], [0.43, 0.49]
            start_zoom, end_zoom = 1.12, 1.12
        else:  # fixed-center push in
            start_center = end_center = [0.50, 0.47]
            start_zoom, end_zoom = 1.02, 1.10
        shot = {
            "image": f"scenes/{filename}",
            "start": round(start, 6),
            "end": round(end, 6),
            "start_center": start_center,
            "end_center": end_center,
            "start_zoom": start_zoom,
            "end_zoom": end_zoom,
            "intent": "人物または英文の主題を中心に、一つだけの明確なパンまたはズームを行う",
        }
        if index > 1:
            shot["transition"] = TRANSITIONS[(index - 2) % len(TRANSITIONS)]
            shot["transition_duration"] = 0.24 if shot["transition"] in ("dissolve", "fade") else 0.30
        shots.append(shot)

        previous_context = sentences[index - 2] if index > 1 else "This is the opening sentence of the lesson."
        prompt = " ".join((
            COMMON_PROMPT,
            f"Lesson continuity: {LESSON_SETTINGS[lesson]}.",
            f'Immediately preceding story context: "{previous_context}" Use it only to resolve pronouns and continuity; illustrate the current sentence, not the preceding one.',
            visual_brief(sentence, lesson),
            f"Required named cast: {', '.join(cast) if cast else 'no recurring named character unless the sentence clearly requires one'}.",
            character_guidance(cast),
        ))
        prompts.append({
            "lesson": lesson,
            "scene": index,
            "filename": f"scenes/{filename}",
            "english": sentence,
            "japanese": ja,
            "cast": cast,
            "references": references_for(cast, lesson, sentence),
            "prompt": prompt,
        })

    config = {
        "project_root": str(PROJECT_ROOT),
        "audio": f"taco_beat/songs/m{lesson}.mp3",
        "chart": f"taco_beat/charts/m{lesson}.js",
        "title_en": f"Lesson {lesson}  {title_en}",
        "title_ja": title_ja,
        "title_position": [620, 145],
        "title_ja_position": [620, 225],
        "slug": f"l{lesson}_{slug}_sentence_v3",
        "duration": duration,
        "transition_duration": 0.28,
        "camera_style": "simple_subject",
        "sentence_image_count": len(sentences),
        "line_to_scene": list(range(len(sentences))),
        "lines": lines,
        "shots": shots,
    }

    if not dry_run:
        lesson_dir = VIDEO_ROOT / f"L{lesson}"
        for name in ("planning", "scenes", "output", "work", "captions"):
            (lesson_dir / name).mkdir(parents=True, exist_ok=True)
        (lesson_dir / "planning" / "lesson.json").write_text(
            json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        with (lesson_dir / "planning" / "image_prompts.jsonl").open("w", encoding="utf-8") as handle:
            for item in prompts:
                handle.write(json.dumps(item, ensure_ascii=False) + "\n")
        (lesson_dir / "planning" / "source_sentences.json").write_text(
            json.dumps(
                {
                    "lesson": lesson,
                    "title_en": title_en,
                    "title_ja": title_ja,
                    "setting": LESSON_SETTINGS[lesson],
                    "sentences": [
                        {"index": i, "paragraph": p, "english": e, "japanese": j}
                        for i, (p, e, j) in enumerate(zip(paragraph_ids, sentences, translations), start=1)
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ) + "\n",
            encoding="utf-8",
        )

    return {
        "lesson": lesson,
        "sentences": len(sentences),
        "timed_tokens": sum(len(item) for item in alignments),
        "minimum_alignment": round(min(scores), 4),
        "mean_alignment": round(sum(scores) / len(scores), 4),
        "low_alignment": [
            {"scene": i, "score": round(score, 4), "english": sentences[i - 1]}
            for i, score in enumerate(scores, start=1) if score < 0.93
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=17)
    parser.add_argument("--end", type=int, default=45)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    reports = [build_lesson(lesson, args.dry_run) for lesson in range(args.start, args.end + 1)]
    print(json.dumps(reports, ensure_ascii=False, indent=2))
    if any("mismatch" in report for report in reports):
        raise SystemExit(2)
    if not args.dry_run:
        report_path = VIDEO_ROOT / "shared" / "alignment_report_l17_l45.json"
        report_path.write_text(json.dumps(reports, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(report_path)


if __name__ == "__main__":
    main()
