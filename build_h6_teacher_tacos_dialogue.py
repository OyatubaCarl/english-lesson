"""Build H6 Teacher Tacos x Tom dialogue explainer video.

Teacher Tacos uses VOICEPEAK Japanese Male 2.
Tom uses VOICEVOX 猫使アル.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import time
import urllib.parse
import urllib.request
import wave
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "tmp_h6_teacher_tacos_dialogue"
FRAME_DIR = OUT_DIR / "frames"
AUDIO_DIR = OUT_DIR / "audio"
CLIP_DIR = OUT_DIR / "clips"
OUT_VIDEO = ROOT / "h6_teacher_tacos_tom_dialogue.mp4"

VOICEPEAK = "/Applications/voicepeak.app/Contents/MacOS/voicepeak"
NARRATOR = "Japanese Male 2"
EN_VOICE = "Daniel"
VOICEVOX_URL = "http://127.0.0.1:50021"
TOM_SPEAKER_ID = 55  # 猫使アル ノーマル

TEACHER_IMAGE = ROOT / "tmp_h3_svo_video" / "teacher_tacos_sheet_style_cutout.png"
TOM_IMAGE = ROOT / "funnics-beginner-assets" / "generated-picturebook-sources" / "B01" / "c005_tom_intro_market.png"

W, H = 1920, 1080
FPS = 30

FONT_BOLD = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
FONT_REGULAR = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"

INK = (30, 41, 59)
MUTED = (100, 116, 139)
WHITE = (255, 255, 255)
BLUE = (37, 99, 235)
GREEN = (5, 150, 105)
ORANGE = (234, 88, 12)
RED = (220, 38, 38)
SLATE = (15, 23, 42)
PAPER = (248, 250, 252)
CARD = (255, 255, 255)
BORDER = (226, 232, 240)


SCRIPT = """
Teacher Tacos:
Tom、今日は「知覚動詞」と「使役動詞」やるよ。名前はゴツいけど、中身はわりとシンプル。

Tom:
名前だけでちょっと嫌なんだけど。

Teacher Tacos:
まあまあ。まず「知覚動詞」から。
「見る」「聞く」「感じる」みたいに、五感で気づく動詞のことね。たとえば see、hear、feel、watch、notice。

Tom:
あー、「知覚」ってそういうことか。

Teacher Tacos:
そうそう。じゃあ問題。
「僕はTomが走るのを見た」って英語で？

Tom:
I saw Tom run. かな？

Teacher Tacos:
正解。ここ大事。
saw Tom run みたいに、

知覚動詞 + 人 + 動詞の原形

になる。

Tom:
え、to run じゃないんだ？

Teacher Tacos:
そこがポイント。
I saw Tom to run. とは言わない。
知覚動詞の後ろでは、基本的に to を使わずに原形を置く。

Tom:
なるほど。see 人 原形 ね。

Teacher Tacos:
じゃあ次。これはどう違う？

I saw Tom cross the street.
I saw Tom crossing the street.

Tom:
うーん。
cross は「道路を渡るのを見た」。
crossing は「道路を渡ってるところを見た」って感じ？

Teacher Tacos:
いいね。かなり合ってる。
原形は「動作全体を見た」感じ。
-ing は「その途中を見た」感じ。

Tom:
じゃあ、
I heard her sing. は「彼女が歌うのを聞いた」。
I heard her singing. は「彼女が歌ってるのが聞こえた」？

Teacher Tacos:
完璧。Tom、今日冴えてるじゃん。

Tom:
たまたまだよ。

Teacher Tacos:
じゃあもう一段階。
「僕は自分の名前が呼ばれるのを聞いた」は？

Tom:
名前は「呼ばれる」側だから……
I heard my name called.

Teacher Tacos:
そう。これは、

知覚動詞 + もの + 過去分詞

の形。
my name は呼ばれる側だから called。

Tom:
つまり、
自分から「する」なら原形か -ing、
「される」なら過去分詞ってことか。

Teacher Tacos:
そのまとめでOK。

Teacher Tacos:
じゃあ次、使役動詞いこう。
「使役」って、ざっくり言うと「誰かに何かをさせる」ってこと。

Tom:
make とか？

Teacher Tacos:
そう。代表はこの3つ。

make / have / let

基本は、

使役動詞 + 人 + 動詞の原形

Tom:
また原形か。

Teacher Tacos:
そう、ここも to はいらない。
まず make。これは「強制してさせる」感じ。

My teacher made me study English.

Tom:
「先生が僕に英語を勉強させた」か。ちょっと強めだね。

Teacher Tacos:
そう。じゃあ have。

I had Tom carry the boxes.

Tom:
「Tomに箱を運んでもらった」？

Teacher Tacos:
そう。have は「頼んでやってもらう」とか「立場上させる」感じ。
make ほど強制っぽくない。

Tom:
じゃあ let は？

Teacher Tacos:
let は「許す」。
たとえば、

My mother let me use her computer.

Tom:
「母さんがパソコン使わせてくれた」って感じか。

Teacher Tacos:
そうそう。じゃあクイズ。
「僕は弟に部屋を掃除させた」。強制っぽく言うなら？

Tom:
I made my brother clean the room.

Teacher Tacos:
正解。
「僕はTomに窓を開けてもらった」は？

Tom:
I had Tom open the window.

Teacher Tacos:
いいね。
「父さんが僕に夜更かしを許してくれた」は？

Tom:
My father let me stay up late.

Teacher Tacos:
ばっちり。
ここで注意。make / have / let は原形だけど、get は違う。

Tom:
え、違うの？

Teacher Tacos:
get + 人 + to V になる。

I got Tom to help me.
「Tomに手伝ってもらった」

Tom:
なるほど。
make, have, let は原形。
get は to V。

Teacher Tacos:
そう。テストでめちゃくちゃ狙われるやつ。

Tom:
そう言われると覚えるしかないな。

Teacher Tacos:
最後に、「髪を切ってもらった」は？

Tom:
I cut my hair. じゃダメ？

Teacher Tacos:
それだと「自分で髪を切った」っぽくなる。
誰かに切ってもらったなら、

I had my hair cut.

Tom:
my hair は切られる側だから cut は過去分詞か。

Teacher Tacos:
そう。これは、

have + もの + 過去分詞

「ものを〜してもらう」って形。

I had my bike repaired.
自転車を修理してもらった。

I got my phone fixed.
スマホを直してもらった。

Tom:
だいぶ見えてきた。
「人がする」のか、「ものがされる」のかを見ればいいんだね。

Teacher Tacos:
その通り。今日のまとめいくよ。

see / hear / watch + 人 + 原形
人が〜するのを見る・聞く。

see / hear / watch + 人 + -ing
人が〜しているところを見る・聞く。

see / hear + もの + 過去分詞
ものが〜されるのを見る・聞く。

make / have / let + 人 + 原形
人に〜させる・してもらう・許す。

get + 人 + to V
人に〜してもらう。

have / get + もの + 過去分詞
ものを〜してもらう。

Tom:
うん、形だけじゃなくて意味で考えるとわかりやすい。

Teacher Tacos:
そうそう。文法って、結局「誰がする？」「何がされる？」を見るゲームみたいなもんだからね。今日はここまで。
""".strip()


@dataclass
class Turn:
    speaker: str
    text: str


@dataclass
class AudioPiece:
    kind: str
    speaker: str
    text: str


def font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REGULAR, size)


F_TITLE = font(52)
F_H2 = font(38)
F_H3 = font(30)
F_BODY = font(27, bold=False)
F_SMALL = font(22, bold=False)
F_EN = font(34)
F_EN_SMALL = font(27)
F_CAPTION = font(33)


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("Command failed:\n" + " ".join(cmd) + "\n" + result.stderr[-2500:])
    return result


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        paragraph = paragraph.strip()
        if not paragraph:
            lines.append("")
            continue
        tokens = paragraph.split(" ") if " " in paragraph else list(paragraph)
        sep = " " if " " in paragraph else ""
        current = ""
        for token in tokens:
            candidate = token if not current else current + sep + token
            if text_size(draw, candidate, fnt)[0] <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = token
        if current:
            lines.append(current)
    return lines


def draw_wrapped(draw: ImageDraw.ImageDraw, text: str, x: int, y: int, max_width: int, fnt, fill=INK, line_gap: int = 8) -> int:
    cur_y = y
    for line in wrap_text(draw, text, fnt, max_width):
        draw.text((x, cur_y), line, font=fnt, fill=fill)
        cur_y += fnt.size + line_gap
    return cur_y


def fit_font(draw: ImageDraw.ImageDraw, text: str, max_width: int, max_height: int, start: int, minimum: int, bold: bool = True):
    for size in range(start, minimum - 1, -2):
        trial = font(size, bold)
        lines = wrap_text(draw, text, trial, max_width)
        total = len(lines) * (size + 8)
        if total <= max_height:
            return trial
    return font(minimum, bold)


def rounded(draw: ImageDraw.ImageDraw, xy, radius: int, fill, outline=None, width: int = 2):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def draw_center(draw: ImageDraw.ImageDraw, text: str, box, fnt, fill=INK):
    x1, y1, x2, y2 = box
    tw, th = text_size(draw, text, fnt)
    draw.text((x1 + (x2 - x1 - tw) / 2, y1 + (y2 - y1 - th) / 2), text, font=fnt, fill=fill)


def gradient_bg() -> Image.Image:
    top = (239, 246, 255)
    bottom = (255, 251, 235)
    img = Image.new("RGB", (W, H), top)
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / (H - 1)
        color = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        draw.line((0, y, W, y), fill=color)
    return img


def parse_dialogue(raw: str) -> list[Turn]:
    turns: list[Turn] = []
    current_speaker: str | None = None
    buf: list[str] = []

    def append_turns(speaker: str, text: str):
        for chunk in chunk_turn_text(text):
            turns.append(Turn(speaker, chunk))

    for line in raw.splitlines():
        if line in {"Teacher Tacos:", "Tom:"}:
            if current_speaker:
                append_turns(current_speaker, "\n".join(buf).strip())
            current_speaker = line[:-1]
            buf = []
        else:
            buf.append(line)
    if current_speaker:
        append_turns(current_speaker, "\n".join(buf).strip())
    return turns


def chunk_turn_text(text: str) -> list[str]:
    chunks: list[str] = []
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text.strip()) if part.strip()]
    for paragraph in paragraphs:
        current: list[str] = []
        for line in paragraph.splitlines():
            line = line.strip()
            candidate = "\n".join(current + [line]).strip()
            if current and len(candidate) > 105:
                chunks.append("\n".join(current).strip())
                current = [line]
            else:
                current.append(line)
        if current:
            chunks.append("\n".join(current).strip())
    return chunks or [text.strip()]


def board_for_turn(idx: int, turn: Turn) -> tuple[str, list[tuple[str, str] | str]]:
    text = turn.text
    if (
        "今日のまとめ" in text
        or "see / hear / watch" in text
        or "make / have / let + 人" in text
        or "have / get + もの" in text
    ):
        return "今日のまとめ", [
            ("see / hear / watch + 人 + 原形", "人が〜するのを見る・聞く"),
            ("see / hear / watch + 人 + -ing", "人が〜しているところを見る・聞く"),
            ("make / have / let + 人 + 原形", "人に〜させる・してもらう・許す"),
            ("get + 人 + to V", "人に〜してもらう"),
            ("have / get + もの + 過去分詞", "ものを〜してもらう"),
        ]
    if "髪" in text or "hair" in text or "bike" in text or "phone" in text:
        return "ものがされる形", [
            ("I had my hair cut.", "髪を切ってもらった。"),
            ("I had my bike repaired.", "自転車を修理してもらった。"),
            ("I got my phone fixed.", "スマホを直してもらった。"),
            "have / get + もの + 過去分詞",
        ]
    if "get" in text or "to V" in text:
        return "get は to V", [
            ("I got Tom to help me.", "Tomに手伝ってもらった。"),
            "make / have / let は原形",
            "get + 人 + to V",
        ]
    if "let" in text or "stay up" in text:
        return "let: 許す", [
            ("My mother let me use her computer.", "母が私にパソコンを使わせてくれた。"),
            ("My father let me stay up late.", "父が夜更かしを許してくれた。"),
            "let + 人 + 動詞の原形",
        ]
    if "have" in text or "carry" in text or "open the window" in text:
        return "have: してもらう", [
            ("I had Tom carry the boxes.", "Tomに箱を運んでもらった。"),
            ("I had Tom open the window.", "Tomに窓を開けてもらった。"),
            "have + 人 + 動詞の原形",
        ]
    if "make" in text or "made" in text or "強制" in text or "brother" in text:
        return "make: 強くさせる", [
            ("My teacher made me study English.", "先生が私に英語を勉強させた。"),
            ("I made my brother clean the room.", "弟に部屋を掃除させた。"),
            "make + 人 + 動詞の原形",
        ]
    if "使役" in text:
        return "使役動詞", [
            "誰かに何かをさせる・してもらう",
            "make / have / let",
            "使役動詞 + 人 + 動詞の原形",
        ]
    if "called" in text or "過去分詞" in text or "呼ばれる" in text:
        return "される側なら過去分詞", [
            ("I heard my name called.", "自分の名前が呼ばれるのを聞いた。"),
            "知覚動詞 + もの + 過去分詞",
            "ものが〜される、という関係を見る",
        ]
    if "cross" in text or "singing" in text or "-ing" in text:
        return "原形と -ing の違い", [
            ("I saw Tom cross the street.", "Tomが道路を渡るのを見た。"),
            ("I saw Tom crossing the street.", "Tomが道路を渡っているところを見た。"),
            "原形: 動作全体",
            "-ing: 動作の途中",
        ]
    if "to run" in text or "原形" in text or "saw Tom run" in text:
        return "知覚動詞 + 人 + 原形", [
            ("I saw Tom run.", "Tomが走るのを見た。"),
            "知覚動詞 + 人 + 動詞の原形",
            "to run ではなく run",
        ]
    return "知覚動詞", [
        "見る・聞く・感じる",
        "see / hear / feel / watch / notice",
        "五感で気づく動詞",
    ]


def audio_cache_name(speaker: str, text: str) -> str:
    digest = hashlib.sha1(f"{speaker}\n{text}".encode("utf-8")).hexdigest()[:16]
    return f"{speaker.lower().replace(' ', '_')}_{digest}.wav"


def audio_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wf:
        return wf.getnframes() / wf.getframerate()


def normalize_wav(src: Path, dst: Path):
    run([
        "ffmpeg",
        "-y",
        "-i",
        str(src),
        "-ar",
        "48000",
        "-ac",
        "1",
        "-filter:a",
        "loudnorm=I=-18:TP=-2:LRA=11",
        str(dst),
    ])


def concat_wavs(parts: list[Path], out: Path):
    concat_file = out.with_name(out.stem + "_concat.txt")
    concat_file.write_text("".join(f"file '{part.resolve()}'\n" for part in parts), encoding="utf-8")
    run([
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_file),
        "-ar",
        "48000",
        "-ac",
        "1",
        "-c:a",
        "pcm_s16le",
        str(out),
    ])


def synth_voicepeak(text: str, out: Path):
    raw = out.with_name(out.stem + "_raw.wav")
    text = spoken_character_text(text)
    cmd = [VOICEPEAK, "-s", text, "-n", NARRATOR, "-o", str(raw), "--speed", "93", "--pitch", "0"]
    last_error = ""
    for _ in range(2):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=70)
        except subprocess.TimeoutExpired:
            last_error = f"VOICEPEAK timed out: {text[:80]}"
            time.sleep(1)
            continue
        if result.returncode == 0 and raw.exists():
            normalize_wav(raw, out)
            return
        last_error = result.stderr[-1200:]
        time.sleep(1)
    raise RuntimeError(last_error)


def synth_english(text: str, out: Path):
    raw = out.with_name(out.stem + "_raw.aiff")
    raw.unlink(missing_ok=True)
    run(["say", "-v", EN_VOICE, "-r", "148", "-o", str(raw), text])
    normalize_wav(raw, out)
    raw.unlink(missing_ok=True)


def synth_voicevox(text: str, out: Path):
    text = spoken_character_text(text)
    query_url = f"{VOICEVOX_URL}/audio_query?{urllib.parse.urlencode({'text': text, 'speaker': TOM_SPEAKER_ID})}"
    req = urllib.request.Request(query_url, method="POST")
    with urllib.request.urlopen(req, timeout=30) as res:
        query = json.loads(res.read().decode("utf-8"))
    query["speedScale"] = 1.05
    query["intonationScale"] = 1.05
    body = json.dumps(query).encode("utf-8")
    synth_url = f"{VOICEVOX_URL}/synthesis?{urllib.parse.urlencode({'speaker': TOM_SPEAKER_ID})}"
    req = urllib.request.Request(synth_url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    raw = out.with_name(out.stem + "_raw.wav")
    with urllib.request.urlopen(req, timeout=60) as res:
        raw.write_bytes(res.read())
    normalize_wav(raw, out)


ENGLISH_EXAMPLE = re.compile(r"^([A-Z][A-Za-z0-9'.,?! ]+[.!?])(\s*)(.*)$")


def spoken_character_text(text: str) -> str:
    replacements = {
        "see / hear / watch": "see、hear、watch",
        "make / have / let": "make、have、let",
        "have / get": "have、get",
        "see / hear": "see、hear",
        "+": " プラス ",
        "/": "、",
        "-ing": "アイエヌジー",
        "to V": "to V",
    }
    spoken = text
    for old, new in replacements.items():
        spoken = spoken.replace(old, new)
    spoken = re.sub(r"\s+", " ", spoken).strip()
    return spoken


def split_audio_pieces(turn: Turn) -> list[AudioPiece]:
    pieces: list[AudioPiece] = []
    for raw_line in turn.text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = ENGLISH_EXAMPLE.match(line)
        if match and "/" not in match.group(1) and "+" not in match.group(1):
            en_text = match.group(1).strip()
            rest = match.group(3).strip()
            pieces.append(AudioPiece("en", "English", en_text))
            if rest:
                pieces.append(AudioPiece("character", turn.speaker, rest))
        else:
            pieces.append(AudioPiece("character", turn.speaker, line))
    return pieces or [AudioPiece("character", turn.speaker, turn.text)]


def piece_cache_name(piece: AudioPiece) -> str:
    cache_text = spoken_character_text(piece.text) if piece.kind == "character" else piece.text
    digest = hashlib.sha1(f"piece_v2\n{piece.kind}\n{piece.speaker}\n{cache_text}".encode("utf-8")).hexdigest()[:16]
    safe_speaker = piece.speaker.lower().replace(" ", "_")
    return f"{piece.kind}_{safe_speaker}_{digest}.wav"


def build_audio(turn: Turn) -> tuple[Path, float]:
    speaker_key = "teacher" if turn.speaker == "Teacher Tacos" else "tom"
    out = AUDIO_DIR / audio_cache_name(f"{speaker_key}_split_v3", turn.text)
    if not out.exists():
        part_paths: list[Path] = []
        for piece in split_audio_pieces(turn):
            part = AUDIO_DIR / piece_cache_name(piece)
            if not part.exists():
                if piece.kind == "en":
                    synth_english(piece.text, part)
                elif piece.speaker == "Teacher Tacos":
                    synth_voicepeak(piece.text, part)
                else:
                    synth_voicevox(piece.text, part)
            part_paths.append(part)
        if len(part_paths) == 1:
            shutil.copyfile(part_paths[0], out)
        else:
            concat_wavs(part_paths, out)
    return out, audio_duration(out)


def crop_avatar(path: Path, kind: str) -> Image.Image:
    img = Image.open(path).convert("RGB")
    if kind == "tom":
        w, h = img.size
        img = img.crop((int(w * 0.17), int(h * 0.04), int(w * 0.51), int(h * 0.96)))
    else:
        img = ImageOps.expand(img, border=26, fill=(255, 255, 255))
    img.thumbnail((360, 360), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (360, 360), (255, 255, 255))
    canvas.paste(img, ((360 - img.width) // 2, (360 - img.height) // 2))
    return canvas


def draw_avatar(canvas: Image.Image, draw: ImageDraw.ImageDraw, img: Image.Image, x: int, y: int, name: str, active: bool, color):
    outline = color if active else BORDER
    rounded(draw, (x, y, x + 360, y + 430), 28, fill=CARD, outline=outline, width=6 if active else 3)
    draw.rounded_rectangle((x + 24, y + 24, x + 336, y + 336), radius=28, fill=(248, 250, 252))
    canvas.paste(img, (x + 24, y + 24))
    draw_center(draw, name, (x + 20, y + 358, x + 340, y + 414), F_H3, fill=color if active else MUTED)


def draw_board(draw: ImageDraw.ImageDraw, title: str, items: list[tuple[str, str] | str]):
    x, y, w, h = 500, 150, 920, 540
    rounded(draw, (x, y, x + w, y + h), 24, fill=CARD, outline=(191, 219, 254), width=4)
    draw.text((x + 42, y + 34), title, font=F_H2, fill=BLUE)
    cur_y = y + 105
    gap = 12 if len(items) <= 4 else 8
    row_h = min(96, max(58, (h - 132 - gap * max(0, len(items) - 1)) // max(1, len(items))))
    for item in items:
        if isinstance(item, tuple):
            en, ja = item
            en_font = F_EN_SMALL if row_h >= 86 else font(22)
            ja_font = F_SMALL if row_h >= 86 else font(18, bold=False)
            rounded(draw, (x + 40, cur_y, x + w - 40, cur_y + row_h), 18, fill=(248, 250, 252), outline=BORDER, width=2)
            draw_wrapped(draw, en, x + 66, cur_y + 12, w - 132, en_font, fill=INK, line_gap=3)
            draw_wrapped(draw, ja, x + 66, cur_y + row_h - ja_font.size - 14, w - 132, ja_font, fill=MUTED, line_gap=2)
            cur_y += row_h + gap
        else:
            item_font = F_BODY if row_h >= 68 else font(22, bold=False)
            rounded(draw, (x + 40, cur_y, x + w - 40, cur_y + row_h), 16, fill=(239, 246, 255), outline=(191, 219, 254), width=2)
            draw_wrapped(draw, item, x + 66, cur_y + max(10, (row_h - item_font.size) // 2 - 3), w - 132, item_font, fill=INK, line_gap=4)
            cur_y += row_h + gap


def draw_caption(draw: ImageDraw.ImageDraw, turn: Turn):
    color = ORANGE if turn.speaker == "Teacher Tacos" else GREEN
    y = 760
    rounded(draw, (120, y, 1800, 1015), 28, fill=SLATE, outline=color, width=5)
    draw.text((165, y + 32), turn.speaker, font=F_H3, fill=color)
    body_font = fit_font(draw, turn.text, 1500, 160, 33, 23, bold=True)
    draw_wrapped(draw, turn.text, 165, y + 88, 1500, body_font, fill=WHITE, line_gap=7)


def render_frame(idx: int, turn: Turn, teacher_img: Image.Image, tom_img: Image.Image) -> Image.Image:
    img = gradient_bg()
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, W, 112), fill=(30, 64, 175))
    draw.rectangle((0, 106, W, 112), fill=ORANGE)
    draw.text((70, 28), "H6", font=F_H3, fill=(219, 234, 254))
    draw.text((170, 20), "知覚動詞・使役動詞 + O + 原形", font=F_TITLE, fill=WHITE)

    active_teacher = turn.speaker == "Teacher Tacos"
    draw_avatar(img, draw, teacher_img, 90, 190, "Teacher Tacos", active_teacher, ORANGE)
    draw_avatar(img, draw, tom_img, 1470, 190, "Tom", not active_teacher, GREEN)

    board_title, board_items = board_for_turn(idx, turn)
    draw_board(draw, board_title, board_items)
    draw_caption(draw, turn)
    return img


def build_video():
    if not Path(VOICEPEAK).exists():
        raise FileNotFoundError(VOICEPEAK)
    try:
        urllib.request.urlopen(f"{VOICEVOX_URL}/version", timeout=2).read()
    except Exception as exc:
        raise RuntimeError("VOICEVOX engine is not running at http://127.0.0.1:50021") from exc

    for d in (FRAME_DIR, AUDIO_DIR, CLIP_DIR):
        d.mkdir(parents=True, exist_ok=True)

    turns = parse_dialogue(SCRIPT)
    teacher_img = crop_avatar(TEACHER_IMAGE, "teacher")
    tom_img = crop_avatar(TOM_IMAGE, "tom")

    clips: list[Path] = []
    total_duration = 0.0
    print(f"=== Build H6 Teacher Tacos dialogue ({len(turns)} turns) ===")
    for idx, turn in enumerate(turns):
        print(f"[{idx + 1}/{len(turns)}] {turn.speaker}: {turn.text[:36].replace(chr(10), ' ')}")
        frame = render_frame(idx, turn, teacher_img, tom_img)
        frame_path = FRAME_DIR / f"frame_{idx:03d}_{turn.speaker.lower().replace(' ', '_')}.png"
        frame.save(frame_path)

        audio_path, duration = build_audio(turn)
        duration += 0.28
        total_duration += duration

        clip_path = CLIP_DIR / f"clip_{idx:03d}.mp4"
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
            str(clip_path),
        ])
        clips.append(clip_path)

    concat = OUT_DIR / "concat.txt"
    concat.write_text("".join(f"file '{clip.resolve()}'\n" for clip in clips), encoding="utf-8")
    temp = OUT_VIDEO.with_suffix(".tmp.mp4")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", str(temp)])
    shutil.move(str(temp), str(OUT_VIDEO))
    print(f"Done: {OUT_VIDEO}")
    print(f"Duration: {total_duration:.1f}s")
    print(f"Size: {OUT_VIDEO.stat().st_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    build_video()
