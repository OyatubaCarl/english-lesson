"""Build a plain H4 SVOO explainer video.

This version follows the same structure used for the H3 plain explainer:
- no character mascot
- question-first entry
- staged reveal (cards/scenes)
- no bottom speech strip
"""
from __future__ import annotations

import os
import shutil
import subprocess
import re
import hashlib
import time
from pathlib import Path
from typing import Callable

from PIL import Image, ImageDraw

from build_h3_svo_plain_explainer import (
    EN,
    JP,
    SILENT,
    Step,
    audio_cache_name,
    draw_center,
    draw_sentence_chunks,
    draw_wrapped,
    font,
    gradient_bg,
    rounded,
    run,
    role_badge,
    make_silence,
    convert_to_wav,
)
from openai_tts_rest import DEFAULT_MODEL as OPENAI_TTS_MODEL
from openai_tts_rest import DEFAULT_VOICE as OPENAI_TTS_VOICE
from openai_tts_rest import synthesize_mp3

import build_h3_svo_plain_explainer as base

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "tmp_h4_svoo_plain"
FRAME_DIR = OUT_DIR / "frames"
AUDIO_DIR = OUT_DIR / "audio"
CLIP_DIR = OUT_DIR / "clips"
OUT_VIDEO = ROOT / "h4_svoo_plain_explainer.mp4"

VOICEPEAK = "/Applications/voicepeak.app/Contents/MacOS/voicepeak"
NARRATOR = "Japanese Male 2"
EN_VOICE = OPENAI_TTS_VOICE

W, H = base.W, base.H
FPS = base.FPS
CONTENT_H = H

F_TITLE = base.F_TITLE
F_H1 = base.F_H1
F_H2 = base.F_H2
F_H3 = base.F_H3
F_BODY = base.F_BODY
F_SMALL = base.F_SMALL
F_EN = base.F_EN
F_EN_SMALL = base.F_EN_SMALL
F_LABEL = base.F_LABEL

INK = base.INK
MUTED = base.MUTED
NAVY = base.NAVY
BLUE = base.BLUE
RED = base.RED
GREEN = base.GREEN
ORANGE = base.ORANGE
YELLOW = base.YELLOW
PURPLE = base.PURPLE
SLATE = base.SLATE
BORDER = base.BORDER
WHITE = base.WHITE
CARD = base.CARD

ROLE_COLORS = {
    "S": BLUE,
    "V": RED,
    "O1": GREEN,
    "O2": ORANGE,
    "O": GREEN,
    "C": YELLOW,
    "M": PURPLE,
}
base.ROLE_COLORS = ROLE_COLORS


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt) -> tuple[int, int]:
    return base.text_size(draw, text, fnt)


def draw_slots_h4(draw: ImageDraw.ImageDraw, x: int, y: int, visible: dict[str, str], *, reveal_o2: bool = False):
    slots = [("S", "だれが", "I"), ("V", "どうする", "give"), ("O1", "だれに", "me"), ("O2", "何を", "a book")]
    cur_x = x
    for role, ja, word in slots:
        color = ROLE_COLORS[role]
        rounded(draw, (cur_x, y, cur_x + 420, y + 130), 22, fill=CARD, outline=color, width=4)
        rounded(draw, (cur_x + 20, y + 18, cur_x + 76, y + 78), 14, fill=color)
        draw_center(draw, role, (cur_x + 20, y + 18, cur_x + 76, y + 78), F_H3, fill=WHITE)
        draw_wrapped(draw, ja, cur_x + 98, y + 17, 280, F_SMALL, fill=MUTED)
        if role in visible:
            draw_wrapped(draw, visible[role], cur_x + 98, y + 58, 280, F_EN, fill=INK)
        else:
            rounded(draw, (cur_x + 100, y + 58, cur_x + 360, y + 98), 13, fill=(241, 245, 249), outline=BORDER, width=2)
            draw_center(draw, "?", (cur_x + 100, y + 58, cur_x + 360, y + 98), F_H3, fill=MUTED)
        cur_x += 450
        if role == "O2" and reveal_o2:
            rounded(draw, (cur_x - 470, y - 60, cur_x + 80, y + 8), 12, fill=(255, 247, 237), outline=GREEN, width=4)
            draw_center(draw, "受け取り先 + 受け取るもの", (cur_x - 470, y - 60, cur_x + 80, y + 8), F_SMALL, fill=GREEN)


def slide_title() -> Image.Image:
    img = gradient_bg((239, 246, 255), (255, 251, 235))
    draw = ImageDraw.Draw(img)
    rounded(draw, (95, 110, 1825, 790), 36, fill=(255, 255, 255), outline=(191, 219, 254), width=5)
    draw.text((155, 170), "高校編 H4", font=F_H2, fill=NAVY)
    draw.text((155, 245), "第4文型 SVOO", font=F_TITLE, fill=INK)
    draw.text((155, 355), "だれかに、何かを渡す・伝える文型", font=F_H1, fill=ORANGE)
    draw_wrapped(
        draw,
        "H3で「だれが・どうする・何を」を見たら、次は「だれに・何を」の順番で並ぶ形を覚えます。",
        160,
        480,
        1400,
        F_BODY,
        fill=MUTED,
    )
    rounded(draw, (160, 635, 1185, 735), 22, fill=SLATE)
    draw_center(
        draw,
        "S  +  V  +  O₁  +  O₂     だれが → どうする → 誰に → 何を",
        (160, 635, 1185, 735),
        F_H3,
        fill=WHITE,
    )
    return img


def slide_use_scene(stage: int) -> Image.Image:
    img = gradient_bg((255, 251, 235), (239, 246, 255))
    draw = ImageDraw.Draw(img)
    base.add_header(img, "Scene", "第4文型は「与える・教える・見せる」で使う")
    base.draw_question_panel(draw, "日本語で「私は彼女に花を買った」と言いたい。", "英語では『何を』『誰に』の順番をどう置くと読みやすい？")
    verbs = [("gave", "渡す"), ("told", "話す"), ("showed", "見せる"), ("sent", "送る")]
    for i, (verb, ja) in enumerate(verbs[:stage]):
        x = 170 + i * 420
        y = 500
        rounded(draw, (x, y, x + 330, y + 160), 22, fill=CARD, outline=[BLUE, RED, GREEN, PURPLE][i], width=4)
        draw_center(draw, verb, (x + 20, y + 28, x + 310, y + 82), F_EN, fill=INK)
        draw_center(draw, ja, (x + 20, y + 88, x + 310, y + 135), F_BODY, fill=MUTED)
    if stage >= 4:
        rounded(draw, (350, 735, 1570, 820), 22, fill=(236, 253, 245), outline=GREEN, width=4)
        draw_center(
            draw,
            "第4文型では、V のあとに O₁（受け取り手）と O₂（授与物）が並ぶ。",
            (350, 735, 1570, 820),
            F_H3,
            fill=GREEN,
        )
    return img


def slide_patterns(stage: int) -> Image.Image:
    img = gradient_bg((248, 250, 252), (255, 247, 237))
    draw = ImageDraw.Draw(img)
    base.add_header(img, "Compare", "第3文型と第4文型を見分ける")
    panels = [
        ("第3文型 SVO", "She opened the door.", "動作だけで終わる。"),
        ("第4文型 SVOO", "My father gave me a small box.", "だれかに 何かを与える。"),
        ("第4文型 SVO O", "My father gave a small box to me.", "to で受け取り手を示す書き換え。"),
    ]
    for i, (title, example, body) in enumerate(panels):
        x = 80 + i * 610
        y = 210
        active = i < stage
        rounded(draw, (x, y, x + 520, y + 430), 26, fill=CARD if active else (248, 250, 252), outline=(GREEN if i else BLUE), width=5)
        draw.text((x + 38, y + 50), title, font=F_H2, fill=GREEN if active else MUTED)
        draw.text((x + 38, y + 140), example if active else ".........", font=F_EN_SMALL, fill=INK if active else MUTED)
        draw_wrapped(draw, body if active else "", x + 38, y + 235, 420, F_BODY, fill=MUTED)
    if stage >= 3:
        rounded(draw, (260, 720, 1660, 810), 22, fill=SLATE)
        draw_center(draw, "第4文型では O₁（誰に）と O₂（何を）が鍵。", (260, 720, 1660, 810), F_H3, fill=WHITE)
    return img


def slide_flip(stage: int) -> Image.Image:
    img = gradient_bg((239, 246, 255), (240, 253, 244))
    draw = ImageDraw.ImageDraw(img)
    base.add_header(img, "Flip Board", "単語を並べて SVOO を作る")
    draw.text((120, 158), "「父は私に小さな箱を渡した」を英語にすると？", font=F_H2, fill=INK)
    draw.text((120, 220), "順番は『誰に（O₁）』の後に『何を（O₂）』です。", font=F_BODY, fill=MUTED)
    visible = {"S": "My father", "V": "gave"}
    if stage >= 2:
        visible["O1"] = "me"
    if stage >= 4:
        visible["O2"] = "a small box"
    draw_slots_h4(draw, 200, 390, visible, reveal_o2=stage >= 3)
    if stage == 0:
        rounded(draw, (420, 690, 1500, 785), 20, fill=(255, 247, 237), outline=ORANGE, width=4)
        draw_center(draw, "My father gave ... ここから O₁ と O₂ を順に入れていく。", (420, 690, 1500, 785), F_H3, fill=ORANGE)
    elif stage in {1, 2}:
        rounded(draw, (420, 690, 1500, 785), 20, fill=(239, 246, 255), outline=GREEN, width=4)
        draw_center(draw, "V のあとに『me』は O₁（受け手）として入る。", (420, 690, 1500, 785), F_H3, fill=GREEN)
    elif stage == 3:
        rounded(draw, (420, 690, 1500, 785), 20, fill=(255, 251, 235), outline=YELLOW, width=4)
        draw_center(draw, "次に O₂ = a small box（授与されるもの）を置く。", (420, 690, 1500, 785), F_H3, fill=YELLOW)
    else:
        rounded(draw, (420, 690, 1500, 785), 20, fill=(236, 253, 245), outline=GREEN, width=4)
        draw_center(draw, "完成：My father gave me a small box。", (420, 690, 1500, 785), F_H3, fill=GREEN)
    return img


def slide_rule(stage: int) -> Image.Image:
    img = gradient_bg((255, 251, 235), (240, 253, 250))
    draw = ImageDraw.Draw(img)
    base.add_header(img, "Rule", "第4文型の確認チェック")
    rules = [
        ("1", "動詞を確認", "give, send, tell, show, teach など"),
        ("2", "O₁ を探す", "だれに？ who / whom で読める"),
        ("3", "O₂ を探す", "何を？を表す名詞句を後ろに置く"),
    ]
    for i, (num, title, body) in enumerate(rules):
        x = 170 + i * 560
        y = 210
        active = i < stage
        rounded(draw, (x, y, x + 460, y + 270), 24, fill=CARD if active else (248, 250, 252), outline=ORANGE if active else BORDER, width=5)
        rounded(draw, (x + 36, y + 44, x + 112, y + 120), 18, fill=ORANGE if active else MUTED)
        draw_center(draw, num, (x + 36, y + 44, x + 112, y + 120), F_H2, fill=WHITE)
        draw.text((x + 140, y + 48), title, font=F_H2, fill=INK if active else MUTED)
        draw_wrapped(draw, body if active else "", x + 44, y + 160, 370, F_BODY, fill=MUTED)
    if stage >= 3:
        draw_sentence_chunks(
            draw,
            330,
            580,
            [
                ("S", "My father", "主語"),
                ("V", "gave", "渡した"),
                ("O1", "me", "受け手"),
                ("O2", "a small box", "授与物"),
            ],
        )
        rounded(draw, (350, 755, 1570, 835), 22, fill=SLATE)
        draw_center(draw, "O₁ と O₂ は並んで出てくる。順番を逆にすると不自然になることが多い。", (350, 755, 1570, 835), F_H3, fill=WHITE)
    return img


def slide_contrast(stage: int) -> Image.Image:
    img = gradient_bg((248, 250, 252), (255, 247, 237))
    draw = ImageDraw.Draw(img)
    base.add_header(img, "Contrast", "同じ動詞でも、受け手配置で文型が変わる")
    if stage >= 1:
        rounded(draw, (150, 220, 930, 565), 26, fill=CARD, outline=BLUE, width=5)
        draw.text((200, 270), "第3文型", font=F_H2, fill=BLUE)
        draw.text((200, 360), "She opened a box.", font=F_EN, fill=INK)
        draw_wrapped(draw, "ドアを開けるのと同様に、目的語は1つ。", 200, 455, 680, F_BODY, fill=MUTED)
    if stage >= 2:
        rounded(draw, (980, 220, 1760, 565), 26, fill=CARD, outline=GREEN, width=5)
        draw.text((1030, 270), "第4文型", font=F_H2, fill=GREEN)
        draw.text((1030, 360), "She gave him a map.", font=F_EN, fill=INK)
        draw_wrapped(draw, "動詞のあとに O₁ と O₂ がいる。", 1030, 455, 680, F_BODY, fill=MUTED)
    if stage >= 3:
        rounded(draw, (255, 690, 1665, 805), 24, fill=(236, 253, 245), outline=GREEN, width=4)
        draw_center(draw, "give は to 句へ書き換え可能: She gave a map to him。", (255, 690, 1665, 805), F_H3, fill=GREEN)
    return img


def slide_h4_text(stage: int) -> Image.Image:
    img = gradient_bg((239, 246, 255), (255, 251, 235))
    draw = ImageDraw.Draw(img)
    base.add_header(img, "H4 Text", "本文から第4文型を読む")
    draw_wrapped(
        draw,
        "本文の冒頭文「My father presented me a small box.」も第4文型です。O₁ は me、O₂ は a small box。",
        110,
        150,
        1520,
        F_BODY,
        fill=INK,
    )
    if stage >= 1:
        draw_sentence_chunks(
            draw,
            155,
            315,
            [
                ("S", "My father", "主語"),
                ("V", "presented", "渡した"),
                ("O1", "me", "相手"),
                ("O2", "a small box", "贈るもの"),
            ],
        )
    if stage >= 2:
        rounded(draw, (155, 545, 1760, 735), 24, fill=CARD, outline=BORDER, width=3)
        draw.text((205, 585), "見分け方", font=F_H2, fill=ORANGE)
        draw_wrapped(
            draw,
            "SVOO は「誰に？」と「何を？」が続く時に強く出ます。英語が不自然に聞こえたら順序（O₁→O₂）を戻して確認します。",
            205,
            655,
            1420,
            F_BODY,
            fill=MUTED,
        )
    return img


def slide_parallel(stage: int) -> Image.Image:
    img = gradient_bg((240, 253, 250), (239, 246, 255))
    draw = ImageDraw.Draw(img)
    base.add_header(img, "H4 Text", "同一主語で SVOO が続く")
    draw_wrapped(
        draw,
        "第4文型も2つ続いてくることがあります。主語と O₁ が同じ文で一塊になる場面です。",
        110,
        150,
        1480,
        F_BODY,
    )
    if stage >= 1:
        draw_sentence_chunks(
            draw,
            115,
            300,
            [
                ("S", "He", "彼"),
                ("V", "showed", "見せた"),
                ("O1", "me", "私に"),
                ("O2", "a map", "地図を"),
            ],
        )
    if stage >= 2:
        draw.text((165, 500), "and", font=F_EN, fill=MUTED)
        draw_sentence_chunks(
            draw,
            315,
            485,
            [("V", "sent", "送った"), ("O1", "her", "彼女に"), ("O2", "a gift", "贈り物を")],
        )
    if stage >= 3:
        rounded(draw, (215, 700, 1705, 810), 24, fill=(255, 251, 235), outline=YELLOW, width=4)
        draw_center(
            draw,
            "He は共通で、show / sent が同じ主語に対して O₁ と O₂ を2回作っている。",
            (215, 700, 1705, 810),
            F_H3,
            fill=INK,
        )
    return img


def slide_summary(stage: int) -> Image.Image:
    img = gradient_bg((255, 247, 237), (239, 246, 255))
    draw = ImageDraw.Draw(img)
    base.add_header(img, "Summary", "第4文型 SVOO の見方")
    points = [
        ("1", "使う場面", "与える・伝える・見せる場面でよく出る"),
        ("2", "形", "S + V + O₁ + O₂"),
        ("3", "確認", "O₁ が『だれに』で O₂ が『何を』を受けるものか"),
    ]
    for i, (num, title, body) in enumerate(points[:stage]):
        y = 185 + i * 190
        rounded(draw, (220, y, 1700, y + 145), 24, fill=CARD, outline=BORDER, width=3)
        rounded(draw, (265, y + 34, 340, y + 109), 18, fill=ORANGE)
        draw_center(draw, num, (265, y + 34, 340, y + 109), F_H2, fill=WHITE)
        draw.text((390, y + 30), title, font=F_H2, fill=INK)
        draw.text((390, y + 88), body, font=F_BODY, fill=MUTED)
    if stage >= 3:
        rounded(draw, (300, 775, 1620, 850), 22, fill=SLATE)
        draw_center(draw, "第4文型は「だれに、何を」を追う文型として捉える。", (300, 775, 1620, 850), F_H3, fill=WHITE)
    return img


STEPS: list[Step] = [
    JP("theme", slide_title, "今回のテーマは第4文型です。動詞のあとに、だれにかつ何をで並ぶ文を見ていきます。"),
    JP("scene_1", lambda: slide_use_scene(2), "たとえば、私は彼女に花を買いました。英語にすると、花を買ったあとに『彼女』を受け手として置くのがポイントです。"),
    JP("scene_2", lambda: slide_use_scene(4), "「渡す」「話す」「見せる」「送る」といった、誰かに何かを与える場面でよく使われます。"),
    JP("patterns_1", lambda: slide_patterns(1), "第3文型は、動詞のあとに目的語が一つだけ続きます。"),
    JP("patterns_2", lambda: slide_patterns(2), "第4文型は、動詞の後ろに受け手と授与物が続く形です。"),
    JP("patterns_3", lambda: slide_patterns(3), "別の書き換え形として前置詞句へ置き換えることもありますが、基本順序は受け手、授与物です。"),
    JP("flip_0", lambda: slide_flip(0), "ここでは『誰に、何を』を決める流れを見てみます。"),
    SILENT("flip_lift", lambda: slide_flip(1), 0.45),
    JP("flip_3", lambda: slide_flip(3), "まず受け手、次に授与物を置いて、文を完成させます。"),
    EN("flip_sentence", lambda: slide_flip(4), "My father gave me a small box."),
    JP("rule_1", lambda: slide_rule(1), "第4文型では、動詞が、渡す、見せる、送る、のように、受け手と内容を必要とするかを見ます。"),
    JP("rule_2", lambda: slide_rule(2), "動詞のすぐ後ろには、受け手になる名詞や代名詞が来ます。him や me のような人を表す語が多いです。"),
    JP("rule_3", lambda: slide_rule(3), "その後ろには、渡される物や内容を表す名詞句が続きます。人、物の順番を意識して読みます。"),
    JP("contrast_1", lambda: slide_contrast(1), "同じ動詞でも、目的語が一つだけなら第3文型になります。"),
    EN("contrast_1_en", lambda: slide_contrast(1), "She opened a box."),
    JP("contrast_2", lambda: slide_contrast(2), "目的語が2つあれば第4文型として扱いやすいです。"),
    EN("contrast_2_en", lambda: slide_contrast(2), "She gave him a map."),
    JP("contrast_3", lambda: slide_contrast(3), "また、前置詞句へ書き換える形でも意味は保たれやすいです。"),
    JP("h4_1", lambda: slide_h4_text(1), "本文をひとつだけ取り上げると、受け手と授与物が順番通り出てくる典型例です。"),
    EN("h4_sentence", lambda: slide_h4_text(1), "My father presented me a small box."),
    JP("h4_2", lambda: slide_h4_text(2), "ここでは、受け手と授与物が明確に読み取れます。"),
    JP("parallel_1", lambda: slide_parallel(1), "同じ主語で、第4文型が2回並ぶ例もあります。"),
    EN("parallel_sentence", lambda: slide_parallel(2), "He showed me a map and sent her a gift."),
    JP("parallel_2", lambda: slide_parallel(3), "このように、主語と受け手が同じなら、与える動詞句が2回続くことがあります。"),
    JP("summary_1", lambda: slide_summary(1), "まとめです。第4文型は受け手と授与物を読む文型です。"),
    JP("summary_2", lambda: slide_summary(2), "形は、主語＋動詞＋受け手＋授与物。人称代名詞が受け手に来やすいのが特徴です。"),
    JP("summary_3", lambda: slide_summary(3), "動詞の後ろを見ると、だれに何をが順番どおりかで第4文型を判定できます。"),
]


_JP_REPLACE = {
    r"\bS\b": "主語",
    r"\bV\b": "動詞",
    r"\bO₁\b": "受け手",
    r"\bO₂\b": "授与物",
    r"\bO\b": "目的語",
    r"\bgive\b": "与える",
    r"\btell\b": "話す",
    r"\bshow\b": "見せる",
    r"\bsend\b": "送る",
    r"\bto\b": "〜へ",
    r"\bfor\b": "〜のために",
    r"\bme\b": "私",
    r"\bher\b": "彼女",
    r"\bhim\b": "彼",
    r"\bmy\b": "私の",
    r"\bhis\b": "彼の",
}


def normalize_japanese_speech(raw: str) -> str:
    text = raw.strip()
    for pattern, replacement in _JP_REPLACE.items():
        text = re.sub(pattern, replacement, text)
    text = re.sub(r"\b[a-zA-Z][a-zA-Z0-9_\-'+/₁₂₀]+\b", "英語表現", text)
    text = re.sub(r"\([^)]+\)", "", text)
    text = re.sub(r"\s{2,}", " ", text).strip()
    return text


def jp_audio_path(step: Step) -> Path:
    audio_key = (
        f"{step.kind}:{NARRATOR}:{OPENAI_TTS_MODEL}:{EN_VOICE}:{normalize_japanese_speech(step.speech)}:{step.seconds}"
    ).encode("utf-8")
    digest = hashlib.sha1(audio_key).hexdigest()[:12]
    return AUDIO_DIR / f"{step.name}_{digest}.wav"


def voicepeak(text: str, raw_path: Path):
    env = os.environ.copy()
    env["LC_ALL"] = "ja_JP.UTF-8"
    env["LANG"] = "ja_JP.UTF-8"
    last_result = None
    timeout_message = ""
    for attempt in range(4):
        raw_path.unlink(missing_ok=True)
        try:
            result = subprocess.run(
                [VOICEPEAK, "-s", text, "-n", NARRATOR, "-o", str(raw_path), "--speed", "94", "--pitch", "0"],
                capture_output=True,
                text=True,
                env=env,
                timeout=50,
            )
        except subprocess.TimeoutExpired:
            timeout_message = f"VOICEPEAK timed out: {text}"
            time.sleep(1.2 + attempt)
            continue
        if result.returncode == 0 and raw_path.exists() and raw_path.stat().st_size > 1024:
            return
        last_result = result
        time.sleep(1.2 + attempt)
    raise RuntimeError(
        "VOICEPEAK failed\n"
        + timeout_message
        + "\n"
        + ((last_result.stderr if last_result else "")[-2000:])
        + ((last_result.stdout if last_result else "")[-1000:])
    )


def say_english(text: str, out_path: Path):
    tmp = out_path.with_suffix(".openai.mp3")
    tmp.unlink(missing_ok=True)
    synthesize_mp3(text, tmp, model=OPENAI_TTS_MODEL, voice=EN_VOICE)
    convert_to_wav(tmp, out_path)
    tmp.unlink(missing_ok=True)


def build_step_audio(step: Step) -> tuple[Path, float]:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    if step.kind == "jp":
        out = jp_audio_path(step)
    else:
        digest = audio_cache_name(step)
        out = AUDIO_DIR / f"{step.name}_{digest}.wav"
    if out.exists() and out.stat().st_size > 1024:
        return out, base.audio_duration(out)
    if step.kind == "jp":
        raw = AUDIO_DIR / f"{out.stem}_raw.wav"
        normalized = normalize_japanese_speech(step.speech)
        voicepeak(normalized, raw)
        convert_to_wav(raw, out)
    elif step.kind == "en":
        say_english(step.speech, out)
    elif step.kind == "silent":
        make_silence(out, step.seconds or 0.5)
    else:
        raise ValueError(step.kind)
    return out, base.audio_duration(out)


def compose_frame(content: Image.Image, step: Step, idx: int, total: int) -> Image.Image:
    return base.compose_frame(content, step, idx, total)


def build_video():
    if not Path(VOICEPEAK).exists():
        raise FileNotFoundError(VOICEPEAK)
    for d in (FRAME_DIR, AUDIO_DIR, CLIP_DIR):
        d.mkdir(parents=True, exist_ok=True)

    clips: list[Path] = []
    durations: list[float] = []
    print("=== Build H4 SVOO explainer ===")
    for idx, step in enumerate(STEPS):
        print(f"[{idx + 1}/{len(STEPS)}] {step.name} {step.kind}")
        content = step.render()
        frame_path = FRAME_DIR / f"frame_{idx:03d}_{step.name}.png"
        content.save(frame_path)

        audio_path, duration = build_step_audio(step)
        duration += 0.18 if step.kind != "silent" else 0.0
        durations.append(duration)

        clip_path = CLIP_DIR / f"clip_{idx:03d}_{step.name}.mp4"
        run([
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-framerate",
            str(FPS),
            "-i",
            str(frame_path),
            "-i",
            str(audio_path),
            "-t",
            f"{duration:.3f}",
            "-vf",
            f"scale={W}:{H},format=yuv420p",
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
            "-movflags",
            "+faststart",
            "-shortest",
            str(clip_path),
        ])
        clips.append(clip_path)

    concat = OUT_DIR / "concat.txt"
    with concat.open("w", encoding="utf-8") as f:
        for clip in clips:
            f.write(f"file '{clip.resolve()}'\n")

    tmp = OUT_VIDEO.with_suffix(".tmp.mp4")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", str(tmp)])
    shutil.move(str(tmp), str(OUT_VIDEO))
    print(f"Done: {OUT_VIDEO}")
    print(f"Duration: {sum(durations):.1f}s")
    print(f"Size: {OUT_VIDEO.stat().st_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    build_video()
