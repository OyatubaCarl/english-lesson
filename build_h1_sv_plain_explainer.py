"""Build a plain H1 SV explainer video.

This follows the single-lesson flip-board style used by
build_h3_svo_plain_explainer.py, but focuses on Lesson H1: the first sentence
pattern, SV.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

import build_h3_svo_plain_explainer as base


ROOT = Path(__file__).resolve().parent

base.OUT_DIR = ROOT / "tmp_h1_sv_plain"
base.FRAME_DIR = base.OUT_DIR / "frames"
base.AUDIO_DIR = base.OUT_DIR / "audio"
base.CLIP_DIR = base.OUT_DIR / "clips"
base.OUT_VIDEO = ROOT / "h1_sv_plain_explainer.mp4"


def _role_card(draw: ImageDraw.ImageDraw, x: int, y: int, role: str, text: str, note: str, color, width: int = 430):
    base.rounded(draw, (x, y, x + width, y + 138), 22, fill=base.CARD, outline=color, width=4)
    base.rounded(draw, (x + 22, y + 24, x + 86, y + 88), 14, fill=color)
    base.draw_center(draw, role, (x + 22, y + 24, x + 86, y + 88), base.F_H3, fill=base.WHITE)
    base.draw_wrapped(draw, text, x + 110, y + 24, width - 138, base.F_EN_SMALL, fill=base.INK, line_gap=4)
    base.draw_wrapped(draw, note, x + 110, y + 78, width - 138, base.F_SMALL, fill=base.MUTED, line_gap=4)


def _mini_rule(draw: ImageDraw.ImageDraw, x: int, y: int, title: str, body: str, color):
    base.rounded(draw, (x, y, x + 480, y + 220), 24, fill=base.CARD, outline=color, width=4)
    draw.text((x + 34, y + 34), title, font=base.F_H2, fill=color)
    base.draw_wrapped(draw, body, x + 34, y + 104, 390, base.F_BODY, fill=base.MUTED, line_gap=8)


def slide_title() -> Image.Image:
    img = base.gradient_bg((239, 246, 255), (255, 251, 235))
    draw = ImageDraw.Draw(img)
    base.rounded(draw, (96, 108, 1824, 800), 36, fill=base.CARD, outline=(191, 219, 254), width=5)
    draw.text((158, 168), "高校編 H1", font=base.F_H2, fill=base.NAVY)
    draw.text((158, 242), "第1文型 SV", font=base.F_TITLE, fill=base.INK)
    draw.text((158, 358), "主語と動詞だけで、文は立ち上がる", font=base.F_H1, fill=base.ORANGE)
    base.draw_wrapped(
        draw,
        "H1では、いちばん小さな文の骨格を見ます。修飾語がついても、中心は S + V です。",
        162,
        482,
        1380,
        base.F_BODY,
        fill=base.MUTED,
    )
    base.rounded(draw, (162, 640, 1105, 738), 22, fill=base.SLATE)
    base.draw_center(draw, "S  +  V     だれが / 何が  →  どうする", (162, 640, 1105, 738), base.F_H3, fill=base.WHITE)
    return img


def slide_scene(stage: int) -> Image.Image:
    img = base.gradient_bg((255, 251, 235), (239, 246, 255))
    draw = ImageDraw.Draw(img)
    base.add_header(img, "Scene", "第1文型は、動作や存在がそこで完結する")
    base.rounded(draw, (115, 145, 1805, 340), 30, fill=base.CARD, outline=(191, 219, 254), width=4)
    draw.text((165, 185), "考えてみよう", font=base.F_H2, fill=base.ORANGE)
    draw.text((455, 184), "太陽がのぼる。鳥が歌う。", font=base.F_H1, fill=base.INK)
    draw.text((455, 275), "「何を？」を足さなくても、文として完結します。", font=base.F_BODY, fill=base.MUTED)
    items = [
        ("The sun rises.", "太陽がのぼる"),
        ("Birds sing.", "鳥が歌う"),
        ("Time passes quickly.", "時が速く過ぎる"),
        ("Fish live in the river.", "魚は川に住む"),
    ]
    for i, (en, ja) in enumerate(items[:stage]):
        x = 126 + (i % 2) * 850
        y = 450 + (i // 2) * 210
        color = [base.BLUE, base.GREEN, base.PURPLE, base.ORANGE][i]
        base.rounded(draw, (x, y, x + 760, y + 158), 24, fill=base.CARD, outline=color, width=4)
        draw.text((x + 42, y + 40), en, font=base.F_EN_SMALL, fill=base.INK)
        draw.text((x + 42, y + 94), ja, font=base.F_BODY, fill=base.MUTED)
    return img


def slide_compare(stage: int) -> Image.Image:
    img = base.gradient_bg((248, 250, 252), (255, 247, 237))
    draw = ImageDraw.Draw(img)
    base.add_header(img, "Compare", "H1では、まず SV と SV ではない形を見分ける")
    panels = [
        ("第1文型 SV", "The sun rises.", "太陽がのぼる。", "V の後ろに O や C がない", base.BLUE),
        ("第2文型 SVC", "The water lay calm.", "水面は穏やかに横たわっていた。", "calm が主語を説明する", base.YELLOW),
        ("第3文型 SVO", "I noticed a deer.", "私は鹿に気づいた。", "a deer が「何に気づいた？」の答え", base.GREEN),
    ]
    for i, (title, example, ja, body, color) in enumerate(panels):
        x = 108 + i * 604
        y = 220
        active = i < stage
        base.rounded(draw, (x, y, x + 525, y + 430), 26, fill=base.CARD if active else (248, 250, 252), outline=color if active else base.BORDER, width=5)
        draw.text((x + 40, y + 48), title, font=base.F_H2, fill=color if active else base.MUTED)
        draw.text((x + 40, y + 150), example if active else ".........", font=base.F_EN_SMALL, fill=base.INK if active else base.MUTED)
        draw.text((x + 40, y + 205), ja if active else "", font=base.F_SMALL, fill=base.MUTED)
        base.draw_wrapped(draw, body if active else "", x + 40, y + 270, 420, base.F_BODY, fill=base.MUTED)
    if stage >= 3:
        base.rounded(draw, (260, 720, 1660, 820), 22, fill=base.SLATE)
        base.draw_center(draw, "H1の中心は、余計なものを削って S + V を見つけること。", (260, 720, 1660, 820), base.F_H3, fill=base.WHITE)
    return img


def slide_flip(stage: int) -> Image.Image:
    img = base.gradient_bg((239, 246, 255), (240, 253, 244))
    draw = ImageDraw.Draw(img)
    base.add_header(img, "Build", "具体的に文を作って、SV だけを残す")
    draw.text((120, 158), "The sun rises.", font=base.F_H1, fill=base.INK)
    draw.text((120, 228), "太陽がのぼる。", font=base.F_BODY, fill=base.MUTED)
    draw.text((120, 280), "まず「何が？」、次に「どうする？」を見ます。", font=base.F_BODY, fill=base.MUTED)
    if stage >= 1:
        _role_card(draw, 310, 420, "S", "The sun", "太陽が", base.BLUE, 500)
    else:
        base.rounded(draw, (310, 420, 810, 558), 22, fill=(241, 245, 249), outline=base.BORDER, width=3)
        base.draw_center(draw, "S ?", (310, 420, 810, 558), base.F_H2, fill=base.MUTED)
    if stage >= 2:
        _role_card(draw, 910, 420, "V", "rises", "のぼる", base.RED, 500)
    else:
        base.rounded(draw, (910, 420, 1410, 558), 22, fill=(241, 245, 249), outline=base.BORDER, width=3)
        base.draw_center(draw, "V ?", (910, 420, 1410, 558), base.F_H2, fill=base.MUTED)
    if stage >= 3:
        base.rounded(draw, (380, 690, 1540, 790), 22, fill=(236, 253, 245), outline=base.GREEN, width=4)
        base.draw_center(draw, "ここで文は完成。O は必要ありません。", (380, 690, 1540, 790), base.F_H3, fill=base.GREEN)
    return img


def slide_modifier(stage: int) -> Image.Image:
    img = base.gradient_bg((240, 253, 250), (255, 247, 237))
    draw = ImageDraw.Draw(img)
    base.add_header(img, "Modifier", "修飾語 M は、骨格の外に置いて読む")
    draw.text((120, 156), "Time passes quickly.", font=base.F_H1, fill=base.INK)
    draw.text((120, 226), "時は速く過ぎる。", font=base.F_BODY, fill=base.MUTED)
    draw.text((120, 278), "quickly は「どのように？」を足す言葉。文型の骨格には入りません。", font=base.F_BODY, fill=base.MUTED)
    if stage >= 1:
        _role_card(draw, 150, 425, "S", "Time", "時は", base.BLUE, 410)
    if stage >= 2:
        _role_card(draw, 625, 425, "V", "passes", "過ぎる", base.RED, 410)
    if stage >= 3:
        _role_card(draw, 1100, 425, "M", "quickly", "速く", base.PURPLE, 410)
        base.rounded(draw, (315, 700, 1605, 805), 24, fill=base.SLATE)
        base.draw_center(draw, "文型は SV。quickly は文を詳しくするだけ。", (315, 700, 1605, 805), base.F_H3, fill=base.WHITE)
    return img


def slide_rule(stage: int) -> Image.Image:
    img = base.gradient_bg((255, 251, 235), (240, 253, 250))
    draw = ImageDraw.Draw(img)
    base.add_header(img, "Rule", "第1文型 SV の見つけ方")
    rules = [
        ("1. S を見る", "何が、誰が、の中心を見つける", base.BLUE),
        ("2. V を見る", "その主語がどうするかを見つける", base.RED),
        ("3. M を外す", "副詞や前置詞句は骨格の外に置く", base.PURPLE),
    ]
    for i, (title, body, color) in enumerate(rules[:stage]):
        _mini_rule(draw, 170 + i * 550, 250, title, body, color)
    if stage >= 3:
        base.rounded(draw, (305, 650, 1615, 770), 24, fill=base.SLATE)
        base.draw_center(draw, "SV は、いちばん短い「文の背骨」。", (305, 650, 1615, 770), base.F_H3, fill=base.WHITE)
    return img


def slide_h1_text(stage: int) -> Image.Image:
    img = base.gradient_bg((239, 246, 255), (255, 251, 235))
    draw = ImageDraw.Draw(img)
    base.add_header(img, "H1 Text", "本文の一文を SV で読む")
    draw.text((110, 152), "At dawn, I stood by the lake.", font=base.F_H1, fill=base.INK)
    draw.text((110, 230), "夜明け、私は湖のそばに立っていた。", font=base.F_BODY, fill=base.MUTED)
    draw.text((110, 282), "文頭と文末に修飾語があっても、中心は I stood です。", font=base.F_BODY, fill=base.MUTED)
    if stage >= 1:
        _role_card(draw, 120, 400, "M", "At dawn", "夜明けに", base.PURPLE, 380)
        _role_card(draw, 540, 400, "S", "I", "私は", base.BLUE, 300)
        _role_card(draw, 880, 400, "V", "stood", "立っていた", base.RED, 360)
        _role_card(draw, 1280, 400, "M", "by the lake", "湖のそばに", base.PURPLE, 480)
    if stage >= 2:
        base.rounded(draw, (300, 690, 1620, 805), 24, fill=(236, 253, 245), outline=base.GREEN, width=4)
        base.draw_center(draw, "At dawn と by the lake を外すと、I stood。だから SV。", (300, 690, 1620, 805), base.F_H3, fill=base.GREEN)
    return img


def slide_h1_second(stage: int) -> Image.Image:
    img = base.gradient_bg((248, 250, 252), (255, 247, 237))
    draw = ImageDraw.Draw(img)
    base.add_header(img, "H1 Text", "前置詞句は O ではなく M として見る")
    draw.text((110, 152), "A gentle mist drifted on the surface.", font=base.F_H1, fill=base.INK)
    draw.text((110, 230), "やわらかな霧が水面の上を漂った。", font=base.F_BODY, fill=base.MUTED)
    draw.text((110, 282), "on the surface は場所の説明。drifted の目的語ではありません。", font=base.F_BODY, fill=base.MUTED)
    if stage >= 1:
        _role_card(draw, 145, 395, "S", "A gentle mist", "やわらかな霧が", base.BLUE, 520)
        _role_card(draw, 710, 395, "V", "drifted", "漂った", base.RED, 380)
        _role_card(draw, 1135, 395, "M", "on the surface", "水面の上に", base.PURPLE, 560)
    if stage >= 2:
        base.rounded(draw, (255, 690, 1665, 805), 24, fill=(255, 251, 235), outline=base.YELLOW, width=4)
        base.draw_center(draw, "前置詞 on から始まるかたまりは、場所を足す M。", (255, 690, 1665, 805), base.F_H3, fill=base.INK)
    return img


def slide_summary(stage: int) -> Image.Image:
    img = base.gradient_bg((255, 247, 237), (239, 246, 255))
    draw = ImageDraw.Draw(img)
    base.add_header(img, "Summary", "第1文型 SV の見方")
    points = [
        ("1", "骨格", "S + V だけで文が成り立つ"),
        ("2", "動詞", "目的語を取らない自動詞が中心"),
        ("3", "修飾語", "副詞・前置詞句は M として外側に置く"),
    ]
    for i, (num, title, body) in enumerate(points[:stage]):
        y = 185 + i * 190
        base.rounded(draw, (220, y, 1700, y + 145), 24, fill=base.CARD, outline=base.BORDER, width=3)
        base.rounded(draw, (265, y + 34, 340, y + 109), 18, fill=base.ORANGE)
        base.draw_center(draw, num, (265, y + 34, 340, y + 109), base.F_H2, fill=base.WHITE)
        draw.text((390, y + 30), title, font=base.F_H2, fill=base.INK)
        base.draw_wrapped(draw, body, 390, y + 88, 1200, base.F_BODY, fill=base.MUTED)
    if stage >= 3:
        base.rounded(draw, (300, 775, 1620, 860), 22, fill=base.SLATE)
        base.draw_center(draw, "H1は、英文を読むための最初の骨格練習です。", (300, 775, 1620, 860), base.F_H3, fill=base.WHITE)
    return img


base.STEPS = [
    base.JP("theme", slide_title, "今回のテーマは第1文型です。主語と動詞だけで成り立つ、いちばん小さな文の骨格を見ます。"),
    base.JP("scene_1", lambda: slide_scene(2), "太陽がのぼる。鳥が歌う。このように、何を、を足さなくても完結する文があります。"),
    base.EN("scene_sun", lambda: slide_scene(2), "The sun rises."),
    base.EN("scene_birds", lambda: slide_scene(2), "Birds sing."),
    base.JP("scene_2", lambda: slide_scene(4), "速く、川に、のような説明がついても、中心は主語と動詞です。"),
    base.EN("scene_time", lambda: slide_scene(4), "Time passes quickly."),
    base.JP("compare_1", lambda: slide_compare(1), "まず、第1文型です。動詞の後ろに目的語や補語を置かなくても文が終わります。"),
    base.EN("compare_sv", lambda: slide_compare(1), "The sun rises."),
    base.JP("compare_2", lambda: slide_compare(2), "第2文型では、後ろの言葉が主語の説明になります。これはH1の中心ではなく、比較として見ます。"),
    base.EN("compare_svc", lambda: slide_compare(2), "The water lay calm."),
    base.JP("compare_3", lambda: slide_compare(3), "第3文型では、動詞の後ろに、何を、誰を、の答えがあります。H1では、そうではない形を見分けます。"),
    base.EN("compare_svo", lambda: slide_compare(3), "I noticed a deer."),
    base.JP("flip_1", lambda: slide_flip(1), "具体的に文章を作ってみましょう。第1文型では、文頭に主語が来ます。主語には名詞や代名詞が入ります。"),
    base.JP("flip_2", lambda: slide_flip(2), "主語の後ろには、時制を持つ動詞が来ます。ここでは rises が動詞で、これだけで文の中心が完成します。"),
    base.JP("flip_3", lambda: slide_flip(3), "第1文型では、動詞の後ろに目的語を足しません。後ろに来るなら、副詞や前置詞句のような説明として読みます。"),
    base.EN("flip_sentence", lambda: slide_flip(3), "The sun rises."),
    base.JP("modifier_1", lambda: slide_modifier(1), "次は、修飾語がついた文です。主語を先に見ます。"),
    base.JP("modifier_2", lambda: slide_modifier(2), "次に動詞を見ます。ここまでが骨格です。"),
    base.JP("modifier_3", lambda: slide_modifier(3), "画面の副詞は、速く、という説明です。文型の中心には入りません。"),
    base.EN("modifier_sentence", lambda: slide_modifier(3), "Time passes quickly."),
    base.JP("rule_1", lambda: slide_rule(1), "見つけるときは、まず文を長くしている説明を脇に置きます。残った中心に主語があるか見ます。"),
    base.JP("rule_2", lambda: slide_rule(2), "次に、主語の後ろに時制を持つ動詞があるかを確認します。目的語を必要としない動詞なら第1文型で読めます。"),
    base.JP("rule_3", lambda: slide_rule(3), "副詞や前置詞句は、場所、時、様子を足す語句です。文型の中心に入れず、外側の説明として扱います。"),
    base.JP("h1_text_1", lambda: slide_h1_text(1), "H1の本文に戻ります。画面の一文では、文頭と文末に説明がついています。まず英語を聞きます。"),
    base.EN("h1_sentence_1", lambda: slide_h1_text(1), "At dawn, I stood by the lake."),
    base.JP("h1_text_2", lambda: slide_h1_text(2), "夜明けに、湖のそばに、を外すと、中心は、私は立っていた、です。だから第1文型です。"),
    base.JP("h1_text_3", lambda: slide_h1_second(1), "もう一文見ます。前置詞句が後ろについても、目的語とは限りません。"),
    base.EN("h1_sentence_2", lambda: slide_h1_second(1), "A gentle mist drifted on the surface."),
    base.JP("h1_text_4", lambda: slide_h1_second(2), "前置詞から始まるかたまりは、場所の説明です。霧が何を漂った、ではなく、どこに漂った、です。"),
    base.JP("summary_1", lambda: slide_summary(1), "まとめです。第1文型は、主語と動詞だけで文が成り立ちます。"),
    base.JP("summary_2", lambda: slide_summary(2), "中心になる動詞は、目的語を取らない自動詞です。"),
    base.JP("summary_3", lambda: slide_summary(3), "副詞や前置詞句は、文を詳しくしますが、骨格には入れません。まずSとVを探しましょう。"),
]


if __name__ == "__main__":
    base.build_video()
