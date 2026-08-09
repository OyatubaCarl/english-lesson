"""Build missing single-lesson plain explainers for H1-H10 and a marathon video.

Existing single-lesson videos are left untouched. Missing lessons use the same
"build a concrete sentence" flip-board style as h1_sv_plain_explainer.py.
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from PIL import Image, ImageDraw

import build_h3_svo_plain_explainer as base


ROOT = Path(__file__).resolve().parent
MARATHON = ROOT / "h1_h10_plain_explainers_marathon.mp4"


@dataclass(frozen=True)
class RolePart:
    role: str
    en: str
    ja: str


@dataclass(frozen=True)
class LessonConfig:
    lesson_id: int
    slug: str
    pattern: str
    title: str
    target: str
    thesis: str
    examples: list[tuple[str, str]]
    build_sentence: str
    build_translation: str
    build_parts: list[RolePart]
    rule_points: list[tuple[str, str]]
    text_sentence: str
    text_translation: str
    text_parts: list[RolePart]
    text_note: str
    contrast_examples: list[tuple[str, str, str]]

    @property
    def output(self) -> Path:
        return ROOT / f"h{self.lesson_id}_{self.slug}_plain_explainer.mp4"


ROLE_COLORS = {
    "S": base.BLUE,
    "V": base.RED,
    "O": base.GREEN,
    "O1": base.GREEN,
    "O2": base.ORANGE,
    "C": base.YELLOW,
    "M": base.PURPLE,
    "If": base.PURPLE,
    "Main": base.GREEN,
}


LESSONS = [
    LessonConfig(
        2,
        "svc",
        "第2文型 SVC",
        "春、すべてがあたらしい",
        "S = C の関係を読む",
        "主語を、後ろの名詞や形容詞で説明する形です。",
        [
            ("She is a teacher.", "彼女は先生だ。"),
            ("The sky is blue.", "空は青い。"),
            ("He looks tired.", "彼は疲れているように見える。"),
        ],
        "The sky is blue.",
        "空は青い。",
        [RolePart("S", "The sky", "空は"), RolePart("V", "is", "です"), RolePart("C", "blue", "青い")],
        [
            ("S を見る", "説明されるものを見つける"),
            ("V を見る", "be/look/feel などのつなぐ動詞を見る"),
            ("C を見る", "S を説明している語を確認する"),
        ],
        "The earth was awake.",
        "大地は目覚めていた。",
        [RolePart("S", "The earth", "大地は"), RolePart("V", "was", "だった"), RolePart("C", "awake", "目覚めた状態")],
        "awake は大地の状態を説明しています。S と C がつながります。",
        [
            ("SV", "The snow melted.", "雪が溶けた。"),
            ("SVC", "The earth was awake.", "大地は目覚めていた。"),
            ("SVC", "The air felt warm.", "空気は暖かく感じられた。"),
        ],
    ),
    LessonConfig(
        5,
        "svoc",
        "第5文型 SVOC",
        "新しい家族 Sora",
        "O = C の関係を読む",
        "目的語の後ろに、その目的語を説明する語が続きます。",
        [
            ("They call me Ken.", "彼らは私をケンと呼ぶ。"),
            ("We named the dog Pochi.", "私たちはその犬をポチと名づけた。"),
            ("She made him happy.", "彼女は彼をうれしくさせた。"),
        ],
        "They call me Ken.",
        "彼らは私をケンと呼ぶ。",
        [RolePart("S", "They", "彼らは"), RolePart("V", "call", "呼ぶ"), RolePart("O", "me", "私を"), RolePart("C", "Ken", "ケンと")],
        [
            ("O を見る", "動詞の後ろの目的語を見つける"),
            ("C を見る", "目的語を説明する語を見つける"),
            ("O = C", "目的語と補語の関係を確認する"),
        ],
        "We named her Sora.",
        "私たちは彼女をソラと名づけた。",
        [RolePart("S", "We", "私たちは"), RolePart("V", "named", "名づけた"), RolePart("O", "her", "彼女を"), RolePart("C", "Sora", "ソラと")],
        "her と Sora は同じ相手を指しています。だから O = C です。",
        [
            ("SVO", "We met the dog.", "私たちはその犬に会った。"),
            ("SVOC", "We named the dog Pochi.", "私たちはその犬をポチと名づけた。"),
            ("SVOC", "She made him happy.", "彼女は彼をうれしくさせた。"),
        ],
    ),
    LessonConfig(
        6,
        "perception_causative",
        "知覚・使役 + O + 原形",
        "秋の午後の縁側",
        "O が何をするのかまで読む",
        "see/hear/make/have などの後ろで、目的語の動きを原形で表します。",
        [
            ("I saw him run.", "私は彼が走るのを見た。"),
            ("I heard her sing.", "私は彼女が歌うのを聞いた。"),
            ("I felt the house shake.", "私は家が揺れるのを感じた。"),
        ],
        "I saw him run.",
        "私は彼が走るのを見た。",
        [RolePart("S", "I", "私は"), RolePart("V", "saw", "見た"), RolePart("O", "him", "彼が"), RolePart("C", "run", "走るのを")],
        [
            ("知覚動詞を見る", "see/hear/feel などを確認する"),
            ("O を見る", "誰がその動きをするのかを見る"),
            ("原形を見る", "O の動きを原形で読む"),
        ],
        "I observed the trees swaying slowly.",
        "私は木々がゆっくり揺れているのを観察した。",
        [RolePart("S", "I", "私は"), RolePart("V", "observed", "観察した"), RolePart("O", "the trees", "木々が"), RolePart("C", "swaying slowly", "揺れているのを")],
        "本文では現在分詞も出ます。目的語の動きまで一緒に読むのがポイントです。",
        [
            ("知覚", "I saw him run.", "私は彼が走るのを見た。"),
            ("知覚", "I heard her sing.", "私は彼女が歌うのを聞いた。"),
            ("使役", "I had him help me.", "私は彼に手伝ってもらった。"),
        ],
    ),
    LessonConfig(
        7,
        "present_tense",
        "現在形の用法",
        "日々のリズム",
        "習慣・真理・予定を現在形で読む",
        "現在形は、今だけでなく、いつも成り立つことや習慣にも使います。",
        [
            ("The sun rises in the east.", "太陽は東からのぼる。"),
            ("Water boils at 100 degrees.", "水は100度で沸騰する。"),
            ("Time flies.", "時は飛ぶように過ぎる。"),
        ],
        "The sun rises in the east.",
        "太陽は東からのぼる。",
        [RolePart("S", "The sun", "太陽は"), RolePart("V", "rises", "のぼる"), RolePart("M", "in the east", "東から")],
        [
            ("形は現在", "動詞の現在形を確認する"),
            ("意味を見る", "習慣・真理・予定のどれかを見る"),
            ("3単現を見る", "主語が三人称単数なら s に注意する"),
        ],
        "I make coffee and open the newspaper.",
        "私はコーヒーをいれ、新聞を開く。",
        [RolePart("S", "I", "私は"), RolePart("V", "make / open", "いれる / 開く"), RolePart("O", "coffee / the newspaper", "コーヒー / 新聞を")],
        "毎日の習慣なので現在形です。今だけの動作とは限りません。",
        [
            ("真理", "Water boils at 100 degrees.", "水は100度で沸騰する。"),
            ("習慣", "I get up early.", "私は早く起きる。"),
            ("時刻表", "The train leaves at seven.", "電車は7時に出る。"),
        ],
    ),
    LessonConfig(
        8,
        "will_going_to",
        "will / be going to",
        "夕食のテーブル",
        "未来の言い方を使い分ける",
        "前から決めていた予定は be going to、その場で決める意志は will で表しやすいです。",
        [
            ("I am going to leave early tomorrow.", "私は明日早く出発する予定だ。"),
            ("It is going to rain.", "雨が降りそうだ。"),
            ("I will go to bed early tonight.", "私は今夜早く寝よう。"),
        ],
        "I am going to leave early tomorrow.",
        "私は明日早く出発する予定だ。",
        [RolePart("S", "I", "私は"), RolePart("V", "am going to leave", "出発する予定だ"), RolePart("M", "early tomorrow", "明日早く")],
        [
            ("予定を見る", "前から決めていた予定かを見る"),
            ("兆候を見る", "目の前の根拠があるかを見る"),
            ("意志を見る", "その場で決めた will かを見る"),
        ],
        "I am going to have a drink tonight.",
        "私は今夜、飲み物を飲むつもりだ。",
        [RolePart("S", "I", "私は"), RolePart("V", "am going to have", "飲むつもりだ"), RolePart("O", "a drink", "飲み物を"), RolePart("M", "tonight", "今夜")],
        "be going to は、すでに決めていた予定や流れを表しやすい形です。",
        [
            ("予定", "I am going to leave early.", "私は早く出発する予定だ。"),
            ("兆候", "It is going to rain.", "雨が降りそうだ。"),
            ("意志", "I will help you.", "私が手伝います。"),
        ],
    ),
    LessonConfig(
        9,
        "time_condition",
        "時・条件の副詞節",
        "日曜日のピクニック",
        "未来のことでも if / when 節は現在形",
        "条件や時を表す副詞節では、未来の話でも現在形を使います。",
        [
            ("If it rains tomorrow, we will stay home.", "明日雨が降ったら、私たちは家にいます。"),
            ("If he comes, please tell me.", "彼が来たら、教えてください。"),
            ("When she arrives, we will start.", "彼女が着いたら、始めます。"),
        ],
        "If it rains tomorrow, we will stay home.",
        "明日雨が降ったら、私たちは家にいます。",
        [RolePart("If", "If it rains tomorrow", "明日雨が降ったら"), RolePart("Main", "we will stay home", "私たちは家にいる")],
        [
            ("if / when を見る", "副詞節の始まりを見つける"),
            ("現在形を見る", "未来の話でも節内は現在形"),
            ("主節を見る", "主節では will を使える"),
        ],
        "If it rains, we will stay home.",
        "雨が降ったら、私たちは家にいます。",
        [RolePart("If", "If it rains", "雨が降ったら"), RolePart("Main", "we will stay home", "私たちは家にいる")],
        "条件節は rains と現在形。主節では will stay と未来を表せます。",
        [
            ("条件", "If it rains, we will stay home.", "雨が降ったら、家にいます。"),
            ("時", "When she arrives, we will start.", "彼女が着いたら、始めます。"),
            ("注意", "If it will rain tomorrow", "この形は条件節では避ける。"),
        ],
    ),
    LessonConfig(
        10,
        "future_progressive",
        "未来進行形",
        "明日の今ごろ",
        "未来のある時点で進行中の動作を読む",
        "will be + ing は、未来の特定時点に、ちょうどしている最中の動作を表します。",
        [
            ("This time tomorrow, I will be flying over the ocean.", "明日の今ごろ、私は海の上を飛んでいるだろう。"),
            ("I will be having dinner.", "私は夕食を食べているだろう。"),
            ("She will be studying in her room.", "彼女は部屋で勉強しているだろう。"),
        ],
        "I will be flying over the ocean.",
        "私は海の上を飛んでいるだろう。",
        [RolePart("S", "I", "私は"), RolePart("V", "will be flying", "飛んでいるだろう"), RolePart("M", "over the ocean", "海の上を")],
        [
            ("時点を見る", "未来のいつの話かを見る"),
            ("will be を見る", "未来の進行形のサインを確認する"),
            ("ing を見る", "その時に進行中の動作を読む"),
        ],
        "This time tomorrow, I will be flying over the ocean.",
        "明日の今ごろ、私は海の上を飛んでいるだろう。",
        [RolePart("M", "This time tomorrow", "明日の今ごろ"), RolePart("S", "I", "私は"), RolePart("V", "will be flying", "飛んでいるだろう"), RolePart("M", "over the ocean", "海の上を")],
        "未来の一点を思い浮かべ、その時に続いている動作として読みます。",
        [
            ("未来進行", "I will be flying.", "私は飛んでいるだろう。"),
            ("予定中の動作", "I will be having dinner.", "私は夕食中だろう。"),
            ("時点つき", "At ten, she will be studying.", "10時には彼女は勉強しているだろう。"),
        ],
    ),
]


VIDEO_ORDER = [
    ROOT / "h1_sv_plain_explainer.mp4",
    ROOT / "h2_svc_plain_explainer.mp4",
    ROOT / "h3_svo_plain_explainer.mp4",
    ROOT / "h4_svoo_plain_explainer.mp4",
    ROOT / "h5_svoc_plain_explainer.mp4",
    ROOT / "h6_perception_causative_plain_explainer.mp4",
    ROOT / "h7_present_tense_plain_explainer.mp4",
    ROOT / "h8_will_going_to_plain_explainer.mp4",
    ROOT / "h9_time_condition_plain_explainer.mp4",
    ROOT / "h10_future_progressive_plain_explainer.mp4",
]


CARD_HEIGHT = 188


def wrapped_height(draw: ImageDraw.ImageDraw, text: str, fnt, max_width: int, line_gap: int = 5) -> int:
    lines = base.wrap_text(draw, text, fnt, max_width)
    return len(lines) * (fnt.size + line_gap)


def fit_pair_fonts(
    draw: ImageDraw.ImageDraw,
    en: str,
    ja: str,
    max_width: int,
    max_height: int,
    en_font,
    ja_font,
):
    en_start = en_font.size
    ja_start = ja_font.size
    for step in range(0, 22, 2):
        en_size = max(22, en_start - step)
        ja_size = max(19, ja_start - step)
        trial_en = base.font(en_size)
        trial_ja = base.font(ja_size, bold=False)
        total = wrapped_height(draw, en, trial_en, max_width, 5) + 6 + wrapped_height(draw, ja, trial_ja, max_width, 5)
        if total <= max_height:
            return trial_en, trial_ja
    return base.font(22), base.font(19, bold=False)


def fit_role_fonts(draw: ImageDraw.ImageDraw, part: RolePart, max_width: int, height: int):
    for en_size in range(base.F_EN_SMALL.size, 20, -2):
        for ja_size in range(base.F_SMALL.size, 17, -2):
            en_font = base.font(en_size)
            ja_font = base.font(ja_size, bold=False)
            en_bottom = 22 + wrapped_height(draw, part.en, en_font, max_width, 4)
            ja_top = max(en_bottom + 4, 86)
            ja_bottom = ja_top + wrapped_height(draw, part.ja, ja_font, max_width, 4)
            if ja_bottom <= height - 14:
                return en_font, ja_font
    return base.font(21), base.font(18, bold=False)


def draw_pair(
    draw: ImageDraw.ImageDraw,
    en: str,
    ja: str,
    x: int,
    y: int,
    max_width: int,
    *,
    en_font=None,
    ja_font=None,
    max_height: int | None = None,
) -> int:
    en_font = en_font or base.F_EN_SMALL
    ja_font = ja_font or base.F_BODY
    if max_height is not None:
        en_font, ja_font = fit_pair_fonts(draw, en, ja, max_width, max_height, en_font, ja_font)
    y = base.draw_wrapped(draw, en, x, y, max_width, en_font, fill=base.INK, line_gap=5)
    y = base.draw_wrapped(draw, ja, x, y + 6, max_width, ja_font, fill=base.MUTED, line_gap=5)
    return y


def role_card(draw: ImageDraw.ImageDraw, x: int, y: int, part: RolePart, width: int, height: int = CARD_HEIGHT):
    color = ROLE_COLORS.get(part.role, base.MUTED)
    base.rounded(draw, (x, y, x + width, y + height), 20, fill=base.CARD, outline=color, width=4)
    base.rounded(draw, (x + 22, y + 24, x + 86, y + 88), 14, fill=color)
    base.draw_center(draw, part.role, (x + 22, y + 24, x + 86, y + 88), base.F_H3, fill=base.WHITE)
    en_font, ja_font = fit_role_fonts(draw, part, width - 134, height)
    next_y = base.draw_wrapped(draw, part.en, x + 110, y + 22, width - 134, en_font, fill=base.INK, line_gap=4)
    ja_y = max(next_y + 4, y + 84)
    base.draw_wrapped(draw, part.ja, x + 110, ja_y, width - 134, ja_font, fill=base.MUTED, line_gap=4)


def distribute_cards(draw: ImageDraw.ImageDraw, parts: list[RolePart], visible: int, y: int):
    gap = 34
    widths = {1: [760], 2: [680, 680], 3: [500, 500, 500], 4: [380, 380, 380, 430]}
    selected_widths = widths.get(len(parts), [360] * len(parts))
    total = sum(selected_widths) + gap * (len(parts) - 1)
    x = (base.W - total) // 2
    for idx, part in enumerate(parts):
        if idx < visible:
            role_card(draw, x, y, part, selected_widths[idx])
        else:
            base.rounded(draw, (x, y, x + selected_widths[idx], y + CARD_HEIGHT), 20, fill=(241, 245, 249), outline=base.BORDER, width=3)
            base.draw_center(draw, f"{part.role} ?", (x, y, x + selected_widths[idx], y + CARD_HEIGHT), base.F_H2, fill=base.MUTED)
        x += selected_widths[idx] + gap


def slide_title(cfg: LessonConfig) -> Image.Image:
    img = base.gradient_bg((239, 246, 255), (255, 251, 235))
    draw = ImageDraw.Draw(img)
    base.rounded(draw, (96, 108, 1824, 820), 36, fill=base.CARD, outline=(191, 219, 254), width=5)
    draw.text((158, 168), f"高校編 H{cfg.lesson_id}", font=base.F_H2, fill=base.NAVY)
    draw.text((158, 242), cfg.pattern, font=base.F_TITLE, fill=base.INK)
    base.draw_wrapped(draw, cfg.title, 158, 358, 1400, base.F_H1, fill=base.ORANGE)
    base.draw_wrapped(draw, cfg.thesis, 162, 490, 1430, base.F_BODY, fill=base.MUTED)
    base.rounded(draw, (162, 650, 1300, 748), 22, fill=base.SLATE)
    base.draw_center(draw, cfg.target, (162, 650, 1300, 748), base.F_H3, fill=base.WHITE)
    return img


def slide_examples(cfg: LessonConfig, stage: int) -> Image.Image:
    img = base.gradient_bg((255, 251, 235), (239, 246, 255))
    draw = ImageDraw.Draw(img)
    base.add_header(img, "Examples", "英語例文と日本語訳をセットで見る")
    base.rounded(draw, (115, 145, 1805, 300), 28, fill=base.CARD, outline=(191, 219, 254), width=4)
    base.draw_wrapped(draw, cfg.thesis, 165, 190, 1560, base.F_BODY, fill=base.INK)
    for i, (en, ja) in enumerate(cfg.examples[:stage]):
        x = 126 + (i % 2) * 850
        y = 350 + (i // 2) * 250
        color = [base.BLUE, base.GREEN, base.PURPLE, base.ORANGE][i]
        base.rounded(draw, (x, y, x + 760, y + 225), 24, fill=base.CARD, outline=color, width=4)
        draw_pair(draw, en, ja, x + 42, y + 42, 660, max_height=160)
    return img


def slide_contrast(cfg: LessonConfig, stage: int) -> Image.Image:
    img = base.gradient_bg((248, 250, 252), (255, 247, 237))
    draw = ImageDraw.Draw(img)
    base.add_header(img, "Compare", "近い形と比べて、今回のポイントをつかむ")
    examples = cfg.contrast_examples[:3]
    for i, (label, en, ja) in enumerate(examples):
        x = 108 + i * 604
        y = 220
        active = i < stage
        color = [base.BLUE, base.YELLOW, base.GREEN][i]
        base.rounded(draw, (x, y, x + 525, y + 430), 26, fill=base.CARD if active else (248, 250, 252), outline=color if active else base.BORDER, width=5)
        draw.text((x + 40, y + 48), label, font=base.F_H2, fill=color if active else base.MUTED)
        if active:
            draw_pair(draw, en, ja, x + 40, y + 145, 430)
    if stage >= 3:
        base.rounded(draw, (260, 720, 1660, 820), 22, fill=base.SLATE)
        base.draw_center(draw, cfg.target, (260, 720, 1660, 820), base.F_H3, fill=base.WHITE)
    return img


def slide_build(cfg: LessonConfig, stage: int) -> Image.Image:
    img = base.gradient_bg((239, 246, 255), (240, 253, 244))
    draw = ImageDraw.Draw(img)
    base.add_header(img, "Build", "具体的に文を作って、形を確認する")
    pair_end = draw_pair(draw, cfg.build_sentence, cfg.build_translation, 120, 154, 1580, en_font=base.F_H1, max_height=240)
    hint_y = max(pair_end + 14, 305)
    draw.text((120, hint_y), "語順と品詞を確認しながら、文を組み立てます。", font=base.F_BODY, fill=base.MUTED)
    cards_y = min(max(hint_y + 80, 430), 520)
    distribute_cards(draw, cfg.build_parts, min(stage, len(cfg.build_parts)), cards_y)
    if stage >= len(cfg.build_parts):
        note_y = max(cards_y + CARD_HEIGHT + 80, 725)
        base.rounded(draw, (300, note_y, 1620, note_y + 105), 24, fill=(236, 253, 245), outline=base.GREEN, width=4)
        base.draw_center(draw, cfg.target, (300, note_y, 1620, note_y + 105), base.F_H3, fill=base.GREEN)
    return img


def slide_rule(cfg: LessonConfig, stage: int) -> Image.Image:
    img = base.gradient_bg((255, 251, 235), (240, 253, 250))
    draw = ImageDraw.Draw(img)
    base.add_header(img, "Rule", f"{cfg.pattern} の見つけ方")
    for i, (title, body) in enumerate(cfg.rule_points[:stage]):
        x = 170 + i * 550
        y = 250
        color = [base.BLUE, base.RED, base.PURPLE][i]
        base.rounded(draw, (x, y, x + 480, y + 225), 24, fill=base.CARD, outline=color, width=4)
        draw.text((x + 34, y + 34), title, font=base.F_H2, fill=color)
        base.draw_wrapped(draw, body, x + 34, y + 104, 390, base.F_BODY, fill=base.MUTED, line_gap=8)
    if stage >= len(cfg.rule_points):
        base.rounded(draw, (305, 650, 1615, 770), 24, fill=base.SLATE)
        base.draw_center(draw, "英語は、カードの役割を順番に見ると読みやすくなります。", (305, 650, 1615, 770), base.F_H3, fill=base.WHITE)
    return img


def slide_text(cfg: LessonConfig, stage: int) -> Image.Image:
    img = base.gradient_bg((239, 246, 255), (255, 251, 235))
    draw = ImageDraw.Draw(img)
    base.add_header(img, f"H{cfg.lesson_id} Text", "本文の一文を同じ形で読む")
    pair_end = draw_pair(draw, cfg.text_sentence, cfg.text_translation, 110, 150, 1620, en_font=base.F_H1, max_height=245)
    cards_y = min(max(pair_end + 70, 410), 535)
    if stage >= 1:
        distribute_cards(draw, cfg.text_parts, len(cfg.text_parts), cards_y)
    if stage >= 2:
        note_y = max(cards_y + CARD_HEIGHT + 70, 730)
        base.rounded(draw, (260, note_y, 1660, note_y + 120), 24, fill=(236, 253, 245), outline=base.GREEN, width=4)
        base.draw_center(draw, cfg.text_note, (260, note_y, 1660, note_y + 120), base.F_H3, fill=base.GREEN)
    return img


def slide_summary(cfg: LessonConfig, stage: int) -> Image.Image:
    img = base.gradient_bg((255, 247, 237), (239, 246, 255))
    draw = ImageDraw.Draw(img)
    base.add_header(img, "Summary", f"H{cfg.lesson_id} {cfg.pattern} のまとめ")
    points = [
        ("1", "語順", f"{cfg.pattern} で語句が並ぶ位置を確認する"),
        ("2", "品詞", "その位置に名詞・形容詞・副詞句など何が入るかを見る"),
        ("3", "本文で読む", "同じ位置関係を本文の一文に当てはめる"),
    ]
    for i, (num, title, body) in enumerate(points[:stage]):
        y = 185 + i * 190
        base.rounded(draw, (220, y, 1700, y + 145), 24, fill=base.CARD, outline=base.BORDER, width=3)
        base.rounded(draw, (265, y + 34, 340, y + 109), 18, fill=base.ORANGE)
        base.draw_center(draw, num, (265, y + 34, 340, y + 109), base.F_H2, fill=base.WHITE)
        draw.text((390, y + 30), title, font=base.F_H2, fill=base.INK)
        base.draw_wrapped(draw, body, 390, y + 88, 1220, base.F_BODY, fill=base.MUTED)
    if stage >= 3:
        base.rounded(draw, (300, 775, 1620, 860), 22, fill=base.SLATE)
        base.draw_center(draw, "次のレッスンでも、まず文の中心を探しましょう。", (300, 775, 1620, 860), base.F_H3, fill=base.WHITE)
    return img


def make_steps(cfg: LessonConfig) -> list[base.Step]:
    first_en, _ = cfg.examples[0]
    second_en, _ = cfg.examples[1]
    third_en, _ = cfg.examples[2]
    return [
        base.JP("theme", lambda: slide_title(cfg), f"今回のテーマは、H{cfg.lesson_id}、{cfg.pattern}です。{cfg.thesis}"),
        base.JP("examples_1", lambda: slide_examples(cfg, 2), "まず例文を、日本語訳とセットで確認します。あとで組み立てるために、語句の順番にも注目します。"),
        base.EN("example_1", lambda: slide_examples(cfg, 2), first_en),
        base.EN("example_2", lambda: slide_examples(cfg, 2), second_en),
        base.JP("examples_2", lambda: slide_examples(cfg, 3), "もう一つ例を足します。意味の共通点だけでなく、どの位置にどんな語句が来るかを見ます。"),
        base.EN("example_3", lambda: slide_examples(cfg, 3), third_en),
        base.JP("contrast_1", lambda: slide_contrast(cfg, 1), "ここからは近い形との比較です。今回の形がどこで変わるのか、語順を中心に見ます。"),
        base.EN("contrast_en_1", lambda: slide_contrast(cfg, 1), cfg.contrast_examples[0][1]),
        base.JP("contrast_2", lambda: slide_contrast(cfg, 2), "次の例では、同じ位置に何が入っているかを比べます。"),
        base.EN("contrast_en_2", lambda: slide_contrast(cfg, 2), cfg.contrast_examples[1][1]),
        base.JP("contrast_3", lambda: slide_contrast(cfg, 3), "三つ並べて、今回の形で特に見る位置をしぼります。"),
        base.EN("contrast_en_3", lambda: slide_contrast(cfg, 3), cfg.contrast_examples[2][1]),
        base.JP("build_1", lambda: slide_build(cfg, 1), "では、具体的に文を作ってみましょう。文頭から順に、最初の位置に来る語句の役割と品詞を確認します。"),
        base.JP("build_2", lambda: slide_build(cfg, min(2, len(cfg.build_parts))), "続いて、次の位置に来る語句を見ます。動詞なら時制を持つ形、目的語なら名詞や代名詞、修飾語なら副詞句や前置詞句が入ります。"),
        base.JP("build_3", lambda: slide_build(cfg, len(cfg.build_parts)), "最後に、文全体を前からつなげます。それぞれの位置にどんな品詞の語句があるかを見ると、今回の形が読みやすくなります。"),
        base.EN("build_sentence", lambda: slide_build(cfg, len(cfg.build_parts)), cfg.build_sentence),
        base.JP("rule_1", lambda: slide_rule(cfg, 1), "見つけ方は、ただ順番を数えるより、どの位置が意味を決めているかを見るのが大事です。まず文の中心を確認します。"),
        base.JP("rule_2", lambda: slide_rule(cfg, 2), "次に、中心の前後にある語句の品詞を見ます。名詞、形容詞、副詞句、前置詞句で働きが変わります。"),
        base.JP("rule_3", lambda: slide_rule(cfg, 3), "最後に、その語句が何を説明しているかを本文の意味につなげます。形だけで終わらせないのがポイントです。"),
        base.JP("text_1", lambda: slide_text(cfg, 1), "本文の一文にも、同じ考え方を使います。まず英語を聞きましょう。"),
        base.EN("text_sentence", lambda: slide_text(cfg, 1), cfg.text_sentence),
        base.JP("text_2", lambda: slide_text(cfg, 2), "語順と品詞に分けると、本文の中でも今回の文法がどこに出ているか見つけやすくなります。"),
        base.JP("summary_1", lambda: slide_summary(cfg, 1), "まとめです。まず、今回の文では語句がどの順番で並ぶかを確認します。"),
        base.JP("summary_2", lambda: slide_summary(cfg, 2), "次に、それぞれの位置に入る品詞を確認します。名詞、形容詞、副詞句など、入るものが変わると読み方も変わります。"),
        base.JP("summary_3", lambda: slide_summary(cfg, 3), "最後に、同じ見方を本文の一文に当てはめます。文法名を覚えるだけでなく、実際の英文で使える形にします。"),
    ]


def build_lesson(cfg: LessonConfig, *, force: bool = False) -> bool:
    if cfg.output.exists() and not force:
        print(f"skip existing: {cfg.output.name}")
        return False
    base.OUT_DIR = ROOT / f"tmp_h{cfg.lesson_id}_{cfg.slug}_plain"
    base.FRAME_DIR = base.OUT_DIR / "frames"
    base.AUDIO_DIR = base.OUT_DIR / "audio"
    base.CLIP_DIR = base.OUT_DIR / "clips"
    base.OUT_VIDEO = cfg.output
    base.STEPS = make_steps(cfg)
    base.build_video()
    return True


def run(cmd: list[str]):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("Command failed:\n" + " ".join(cmd) + "\n" + result.stderr[-2500:])
    return result


def build_marathon():
    missing = [p for p in VIDEO_ORDER if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing videos for marathon:\n" + "\n".join(str(p) for p in missing))

    tmp_dir = ROOT / "tmp_h1_h10_marathon"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    normalized: list[Path] = []
    for idx, src in enumerate(VIDEO_ORDER, start=1):
        dst = tmp_dir / f"{idx:02d}_{src.stem}.mp4"
        run([
            "ffmpeg",
            "-y",
            "-i",
            str(src),
            "-vf",
            "scale=1920:1080,fps=30,format=yuv420p",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "20",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(dst),
        ])
        normalized.append(dst)

    concat = tmp_dir / "concat.txt"
    concat.write_text("".join(f"file '{p.resolve()}'\n" for p in normalized), encoding="utf-8")
    temp = MARATHON.with_suffix(".tmp.mp4")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", str(temp)])
    temp.replace(MARATHON)
    print(f"Done marathon: {MARATHON}")


def main():
    for cfg in LESSONS:
        build_lesson(cfg)
    build_marathon()


if __name__ == "__main__":
    main()
