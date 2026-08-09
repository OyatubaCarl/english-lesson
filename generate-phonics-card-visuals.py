#!/usr/bin/env python3
"""Generate simple SVG card illustrations and Japanese meaning furigana."""
from __future__ import annotations

import hashlib
import json
import re
from html import escape
from pathlib import Path

import pykakasi


DATA_PATH = Path("phonics-audio-items.json")
ICON_DIR = Path("assets/card-icons")


RULE_COLORS = {
    "short-a": ("#dcfce7", "#34d399", "#0f766e"),
    "short-e": ("#ffe4e6", "#fb7185", "#be123c"),
    "short-i": ("#dbeafe", "#60a5fa", "#1d4ed8"),
    "short-o": ("#fef3c7", "#f59e0b", "#92400e"),
    "short-u": ("#ede9fe", "#8b5cf6", "#5b21b6"),
    "magic-e-a": ("#e0f2fe", "#38bdf8", "#075985"),
    "magic-e-i": ("#f0f9ff", "#0ea5e9", "#0369a1"),
    "magic-e-o": ("#ecfeff", "#06b6d4", "#155e75"),
    "magic-e-u": ("#eef2ff", "#6366f1", "#3730a3"),
    "vowel-team-ai-ay": ("#fef9c3", "#eab308", "#854d0e"),
    "vowel-team-ee-ea": ("#dcfce7", "#22c55e", "#166534"),
    "vowel-team-oa-ow": ("#ffedd5", "#fb923c", "#9a3412"),
    "vowel-team-oo-long": ("#e0e7ff", "#818cf8", "#4338ca"),
    "vowel-team-oo-short": ("#f3e8ff", "#a855f7", "#6b21a8"),
    "diphthong-oi-oy": ("#fae8ff", "#d946ef", "#86198f"),
    "diphthong-ou-ow": ("#cffafe", "#22d3ee", "#0e7490"),
    "r-controlled-ar": ("#fee2e2", "#ef4444", "#991b1b"),
    "r-controlled-or": ("#fed7aa", "#f97316", "#9a3412"),
    "r-controlled-er": ("#e5e7eb", "#64748b", "#334155"),
}


ANIMALS = {
    "cat",
    "bat",
    "rat",
    "ram",
    "yak",
    "ant",
    "hen",
    "pig",
    "fish",
    "chick",
    "dog",
    "fox",
    "frog",
    "bug",
    "pup",
    "duck",
    "cub",
    "slug",
    "snake",
    "mule",
    "sheep",
    "bee",
    "goat",
    "cow",
    "bird",
    "ox",
    "buck",
    "crab",
}

PEOPLE = {"man", "men", "dad", "lad", "pal", "gal", "kid", "mom", "cop", "boy", "girl", "nurse", "vet"}
VEHICLES = {"cab", "van", "jet", "bus", "truck", "bike", "plane", "train", "boat", "car"}
FOOD = {"jam", "ham", "gum", "nut", "bun", "yam", "lunch", "corn", "food", "peach", "cake"}
NATURE = {
    "sun",
    "mud",
    "land",
    "sand",
    "ash",
    "plant",
    "hill",
    "fog",
    "pond",
    "rain",
    "day",
    "clay",
    "tree",
    "green",
    "leaf",
    "beach",
    "snow",
    "moon",
    "cloud",
    "star",
    "park",
    "farm",
    "storm",
    "lake",
    "cave",
    "wave",
    "smoke",
}
BODY = {"lap", "hand", "neck", "leg", "lip", "fin", "feet", "foot", "brain", "bone"}
HOUSE = {"mat", "bag", "cap", "hat", "pan", "can", "bed", "net", "desk", "tent", "tub", "mug", "rug", "home"}
TOOLS = {"ax", "tack", "peg", "rack", "jack", "mask", "stamp", "plug", "drum", "pump", "brush", "fork"}
SHAPES = {"box", "block", "blob", "spot", "dot", "line", "stripe", "cube", "cone", "globe", "coin", "dime", "card"}
MEDIA = {"web", "chess", "quiz", "print", "book", "note", "code", "game", "tune", "show"}
COLORS = {"red", "gray", "brown", "green"}
NUMBERS = {"ten", "nine"}
ACTION_HINTS = {
    "tap",
    "wag",
    "back",
    "pack",
    "snap",
    "clap",
    "trap",
    "dab",
    "gab",
    "jab",
    "yap",
    "ran",
    "dash",
    "bash",
    "get",
    "met",
    "set",
    "let",
    "bet",
    "sell",
    "fell",
    "tell",
    "yell",
    "peck",
    "check",
    "rest",
    "test",
    "went",
    "sent",
    "step",
    "press",
    "sit",
    "win",
    "dig",
    "rip",
    "hit",
    "fix",
    "ring",
    "sing",
    "swim",
    "spin",
    "slip",
    "grin",
    "mop",
    "top",
    "hop",
    "shop",
    "chop",
    "pop",
    "stop",
    "run",
    "hum",
    "cut",
    "shut",
    "chug",
    "tug",
    "dug",
    "hug",
    "lug",
    "rub",
    "scrub",
    "bump",
    "dump",
    "jump",
    "suck",
    "tuck",
    "punch",
    "crush",
    "cluck",
    "make",
    "bake",
    "save",
    "like",
    "hike",
    "ride",
    "shine",
    "slide",
    "smile",
    "hope",
    "joke",
    "broke",
    "use",
    "play",
    "stay",
    "say",
    "see",
    "grow",
    "blow",
    "look",
    "cook",
    "boil",
    "found",
    "turn",
}


KANA_DIRECT = {
    "th": {"æ": "サ", "ɛ": "セ", "ɪ": "シ", "ɑ": "ソ", "ʌ": "サ"},
    "dh": {"æ": "ザ", "ɛ": "ゼ", "ɪ": "ジ", "ɑ": "ゾ", "ʌ": "ザ"},
    "sh": {"æ": "シャ", "ɛ": "シェ", "ɪ": "シ", "ɑ": "ショ", "ʌ": "シャ"},
    "ch": {"æ": "チャ", "ɛ": "チェ", "ɪ": "チ", "ɑ": "チョ", "ʌ": "チャ"},
    "j": {"æ": "ジャ", "ɛ": "ジェ", "ɪ": "ジ", "ɑ": "ジョ", "ʌ": "ジャ"},
    "kw": {"æ": "クァ", "ɛ": "クェ", "ɪ": "クィ", "ɑ": "クォ", "ʌ": "クァ"},
    "p": {"æ": "パ", "ɛ": "ペ", "ɪ": "ピ", "ɑ": "ポ", "ʌ": "パ"},
    "b": {"æ": "バ", "ɛ": "ベ", "ɪ": "ビ", "ɑ": "ボ", "ʌ": "バ"},
    "t": {"æ": "タ", "ɛ": "テ", "ɪ": "ティ", "ɑ": "ト", "ʌ": "タ"},
    "d": {"æ": "ダ", "ɛ": "デ", "ɪ": "ディ", "ɑ": "ド", "ʌ": "ダ"},
    "k": {"æ": "キャ", "ɛ": "ケ", "ɪ": "キ", "ɑ": "コ", "ʌ": "カ"},
    "g": {"æ": "ギャ", "ɛ": "ゲ", "ɪ": "ギ", "ɑ": "ゴ", "ʌ": "ガ"},
    "m": {"æ": "マ", "ɛ": "メ", "ɪ": "ミ", "ɑ": "モ", "ʌ": "マ"},
    "n": {"æ": "ナ", "ɛ": "ネ", "ɪ": "ニ", "ɑ": "ノ", "ʌ": "ナ"},
    "f": {"æ": "ファ", "ɛ": "フェ", "ɪ": "フィ", "ɑ": "フォ", "ʌ": "ファ"},
    "v": {"æ": "ヴァ", "ɛ": "ヴェ", "ɪ": "ヴィ", "ɑ": "ヴォ", "ʌ": "ヴァ"},
    "s": {"æ": "サ", "ɛ": "セ", "ɪ": "シ", "ɑ": "ソ", "ʌ": "サ"},
    "z": {"æ": "ザ", "ɛ": "ゼ", "ɪ": "ジ", "ɑ": "ゾ", "ʌ": "ザ"},
    "h": {"æ": "ハ", "ɛ": "ヘ", "ɪ": "ヒ", "ɑ": "ホ", "ʌ": "ハ"},
    "l": {"æ": "ラ", "ɛ": "レ", "ɪ": "リ", "ɑ": "ロ", "ʌ": "ラ"},
    "r": {"æ": "ラ", "ɛ": "レ", "ɪ": "リ", "ɑ": "ロ", "ʌ": "ラ"},
    "w": {"æ": "ワ", "ɛ": "ウェ", "ɪ": "ウィ", "ɑ": "ウォ", "ʌ": "ワ"},
    "y": {"æ": "ヤ", "ɛ": "イェ", "ɪ": "イ", "ɑ": "ヨ", "ʌ": "ヤ"},
}

LONG_VOWELS = {
    "eɪ": {"": "エイ", "p": "ペイ", "b": "ベイ", "t": "テイ", "d": "デイ", "k": "ケイ", "g": "ゲイ", "m": "メイ", "n": "ネイ", "f": "フェイ", "v": "ヴェイ", "s": "セイ", "z": "ゼイ", "h": "ヘイ", "l": "レイ", "r": "レイ", "w": "ウェイ", "y": "イェイ", "sh": "シェイ", "ch": "チェイ", "j": "ジェイ", "kw": "クウェイ"},
    "aɪ": {"": "アイ", "p": "パイ", "b": "バイ", "t": "タイ", "d": "ダイ", "k": "カイ", "g": "ガイ", "m": "マイ", "n": "ナイ", "f": "ファイ", "v": "ヴァイ", "s": "サイ", "z": "ザイ", "h": "ハイ", "l": "ライ", "r": "ライ", "w": "ワイ", "sh": "シャイ", "ch": "チャイ", "j": "ジャイ"},
    "oʊ": {"": "オー", "p": "ポー", "b": "ボー", "t": "トー", "d": "ドー", "k": "コー", "g": "ゴー", "m": "モー", "n": "ノー", "f": "フォー", "s": "ソー", "z": "ゾー", "h": "ホー", "l": "ロー", "r": "ロー", "w": "ウォー", "sh": "ショー", "ch": "チョー", "j": "ジョー"},
    "iː": {"": "イー", "p": "ピー", "b": "ビー", "t": "ティー", "d": "ディー", "k": "キー", "g": "ギー", "m": "ミー", "n": "ニー", "f": "フィー", "v": "ヴィー", "s": "シー", "z": "ズィー", "h": "ヒー", "l": "リー", "r": "リー", "w": "ウィー", "sh": "シー", "ch": "チー", "j": "ジー"},
    "uː": {"": "ウー", "p": "プー", "b": "ブー", "t": "トゥー", "d": "ドゥー", "k": "クー", "g": "グー", "m": "ムー", "n": "ヌー", "f": "フー", "s": "スー", "h": "フー", "l": "ルー", "r": "ルー", "sh": "シュー", "ch": "チュー", "j": "ジュー"},
    "juː": {"": "ユー", "p": "ピュー", "b": "ビュー", "t": "チュー", "d": "デュー", "k": "キュー", "g": "ギュー", "m": "ミュー", "n": "ニュー", "f": "フュー", "s": "シュー", "h": "ヒュー", "l": "リュー", "r": "リュー"},
    "ʊ": {"": "ウ", "p": "プ", "b": "ブ", "t": "トゥ", "d": "ドゥ", "k": "ク", "g": "グ", "m": "ム", "n": "ヌ", "f": "フ", "s": "ス", "h": "フ", "l": "ル", "r": "ル", "sh": "シュ", "ch": "チュ", "j": "ジュ"},
    "ɔɪ": {"": "オイ", "p": "ポイ", "b": "ボイ", "t": "トイ", "d": "ドイ", "k": "コイ", "g": "ゴイ", "m": "モイ", "n": "ノイ", "s": "ソイ", "l": "ロイ", "r": "ロイ", "j": "ジョイ"},
    "aʊ": {"": "アウ", "p": "パウ", "b": "バウ", "t": "タウ", "d": "ダウ", "k": "カウ", "g": "ガウ", "m": "マウ", "n": "ナウ", "f": "ファウ", "s": "サウ", "l": "ラウ", "r": "ラウ", "w": "ワウ"},
    "ɑr": {"": "アー", "p": "パー", "b": "バー", "t": "ター", "d": "ダー", "k": "カー", "g": "ガー", "m": "マー", "n": "ナー", "f": "ファー", "s": "サー", "l": "ラー", "r": "ラー"},
    "ɔr": {"": "オー", "p": "ポー", "b": "ボー", "t": "トー", "d": "ドー", "k": "コー", "g": "ゴー", "m": "モー", "n": "ノー", "f": "フォー", "s": "ソー", "l": "ロー", "r": "ロー"},
    "ɜr": {"": "アー", "p": "パー", "b": "バー", "t": "ター", "d": "ダー", "k": "カー", "g": "ガー", "m": "マー", "n": "ナー", "f": "ファー", "s": "サー", "l": "ラー", "r": "ラー"},
}

CODA = {
    "p": "プ",
    "b": "ブ",
    "t": "ト",
    "d": "ド",
    "k": "ク",
    "g": "グ",
    "m": "ム",
    "n": "ン",
    "ng": "ング",
    "f": "フ",
    "v": "ヴ",
    "s": "ス",
    "z": "ズ",
    "sh": "シュ",
    "ch": "チ",
    "th": "ス",
    "dh": "ズ",
    "l": "ル",
    "r": "ル",
    "w": "ウ",
    "y": "イ",
}

CLUSTER_PREFIX = {
    "p": "プ",
    "b": "ブ",
    "t": "ト",
    "d": "ド",
    "k": "ク",
    "g": "グ",
    "f": "フ",
    "s": "ス",
    "sh": "シュ",
    "ch": "チ",
    "m": "ム",
    "n": "ン",
}


def norm_sound(sound: str) -> str:
    if sound == "θ":
        return "th"
    if sound == "ð":
        return "dh"
    if sound == "ʃ":
        return "sh"
    if sound == "tʃ":
        return "ch"
    if sound == "dʒ":
        return "j"
    if sound == "ŋ":
        return "ng"
    return sound


def is_vowel(sound: str) -> bool:
    return sound in {"æ", "ɛ", "ɪ", "ɑ", "ʌ", "eɪ", "aɪ", "oʊ", "juː", "iː", "uː", "ʊ", "ɔɪ", "aʊ", "ɑr", "ɔr", "ɜr"}


def single_onset(con: str, vowel: str) -> str:
    if vowel in LONG_VOWELS:
        return LONG_VOWELS[vowel].get(con, LONG_VOWELS[vowel].get("", ""))
    if con:
        return KANA_DIRECT.get(con, {}).get(vowel, "")
    return {"æ": "ア", "ɛ": "エ", "ɪ": "イ", "ɑ": "オ", "ʌ": "ア"}.get(vowel, "")


def onset_kana(onset: list[str], vowel: str) -> str:
    if not onset:
        return single_onset("", vowel)
    if len(onset) == 1:
        return single_onset(onset[0], vowel)
    if onset[0] == "s" and len(onset) > 1:
        return "ス" + onset_kana(onset[1:], vowel)
    if onset[-1] in {"r", "l"} and len(onset) >= 2:
        return "".join(CLUSTER_PREFIX.get(c, CODA.get(c, "")) for c in onset[:-1]) + single_onset("r", vowel)
    if onset[0] == "kw":
        return single_onset("kw", vowel)
    return "".join(CLUSTER_PREFIX.get(c, CODA.get(c, "")) for c in onset[:-1]) + single_onset(onset[-1], vowel)


def coda_kana(coda: list[str], short_vowel: bool) -> str:
    if not coda:
        return ""
    cleaned: list[str] = []
    for sound in coda:
        if cleaned and cleaned[-1] == sound:
            continue
        cleaned.append(sound)
    joined = tuple(cleaned)
    clusters = {
        ("n", "t"): "ント",
        ("n", "d"): "ンド",
        ("n", "ch"): "ンチ",
        ("m", "p"): "ンプ",
        ("s", "t"): "スト",
        ("s", "k"): "スク",
        ("f", "t"): "フト",
        ("l", "k"): "ルク",
        ("l", "d"): "ルド",
        ("l", "f"): "ルフ",
        ("r", "d"): "ード",
        ("r", "m"): "ーム",
        ("r", "n"): "ーン",
    }
    if joined in clusters:
        return clusters[joined]
    if len(cleaned) == 1:
        sound = cleaned[0]
        if short_vowel and sound in {"p", "t", "k", "g", "ch"}:
            return "ッ" + CODA[sound]
        return CODA.get(sound, "")
    return "".join(CODA.get(sound, "") for sound in cleaned)


def kana_for_card(card: dict) -> str:
    sounds = [norm_sound(seg.get("sound", "")) for seg in card.get("segments", [])]
    vowel_indexes = [i for i, sound in enumerate(sounds) if is_vowel(sound)]
    if not vowel_indexes:
        return "".join(CODA.get(sound, "") for sound in sounds) or card["word"]
    first = vowel_indexes[0]
    vowel = sounds[first]
    onset = sounds[:first]
    coda = sounds[first + 1 :]
    short_vowel = vowel in {"æ", "ɛ", "ɪ", "ɑ", "ʌ", "ʊ"}
    kana = onset_kana(onset, vowel) + coda_kana(coda, short_vowel)
    overrides = {
        "am": "アム",
        "an": "アン",
        "and": "アンド",
        "at": "アット",
        "as": "アズ",
        "it": "イット",
        "in": "イン",
        "if": "イフ",
        "ill": "イル",
        "on": "オン",
        "up": "アップ",
        "us": "アス",
        "use": "ユーズ",
        "one": "ワン",
        "June": "ジューン",
        "bug": "バグ",
        "rug": "ラグ",
        "mug": "マグ",
        "dug": "ダグ",
        "jug": "ジャグ",
        "hug": "ハグ",
        "lug": "ラグ",
        "chug": "チャグ",
        "plug": "プラグ",
        "slug": "スラグ",
        "snug": "スナグ",
    }
    return overrides.get(card.get("word", ""), kana)


def seed_for(word: str) -> int:
    return int(hashlib.sha1(word.encode("utf-8")).hexdigest()[:8], 16)


def svg_header(word: str, bg: str) -> list[str]:
    return [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 220" role="img">',
        f"<title>{escape(word)}</title>",
        f'<rect width="320" height="220" rx="28" fill="{bg}"/>',
        '<circle cx="274" cy="42" r="24" fill="#ffffff" opacity=".6"/>',
        '<circle cx="46" cy="177" r="18" fill="#ffffff" opacity=".5"/>',
    ]


def svg_footer() -> str:
    return "</svg>\n"


def animal_svg(word: str, bg: str, main: str, dark: str) -> str:
    e = svg_header(word, bg)
    if word == "bat":
        e += [
            f'<path d="M58 118 C82 58 116 68 132 112 C150 70 188 58 214 118 C186 104 170 118 160 146 C150 118 134 118 122 146 C112 118 88 104 58 118Z" fill="{main}" stroke="{dark}" stroke-width="6" stroke-linejoin="round"/>',
            f'<circle cx="160" cy="106" r="32" fill="{dark}"/>',
            '<circle cx="148" cy="101" r="5" fill="#fff"/><circle cx="172" cy="101" r="5" fill="#fff"/>',
        ]
    elif word in {"fish"}:
        e += [
            f'<path d="M70 118 C112 70 190 72 230 118 C190 164 112 166 70 118Z" fill="{main}" stroke="{dark}" stroke-width="6"/>',
            f'<path d="M230 118 L282 82 L282 154 Z" fill="{main}" stroke="{dark}" stroke-width="6" stroke-linejoin="round"/>',
            '<circle cx="126" cy="105" r="7" fill="#111827"/>',
            '<path d="M52 158 C94 142 122 142 166 158" fill="none" stroke="#38bdf8" stroke-width="7" stroke-linecap="round"/>',
        ]
    elif word in {"snake"}:
        e += [
            f'<path d="M62 134 C106 82 154 180 198 126 C222 98 246 103 264 128" fill="none" stroke="{main}" stroke-width="30" stroke-linecap="round"/>',
            f'<path d="M62 134 C106 82 154 180 198 126 C222 98 246 103 264 128" fill="none" stroke="{dark}" stroke-width="6" stroke-linecap="round"/>',
            '<circle cx="252" cy="119" r="4" fill="#111827"/><path d="M270 130 L292 124" stroke="#ef4444" stroke-width="4" stroke-linecap="round"/>',
        ]
    elif word in {"bee"}:
        e += [
            '<ellipse cx="126" cy="98" rx="42" ry="28" fill="#ffffff" opacity=".8"/><ellipse cx="188" cy="98" rx="42" ry="28" fill="#ffffff" opacity=".8"/>',
            f'<ellipse cx="160" cy="124" rx="72" ry="42" fill="#facc15" stroke="{dark}" stroke-width="6"/>',
            f'<path d="M126 88 V160 M158 82 V166 M190 90 V158" stroke="{dark}" stroke-width="9"/>',
            '<circle cx="104" cy="116" r="6" fill="#111827"/>',
        ]
    elif word in {"frog"}:
        e += [
            f'<ellipse cx="160" cy="132" rx="86" ry="52" fill="{main}" stroke="{dark}" stroke-width="6"/>',
            f'<circle cx="118" cy="82" r="27" fill="{main}" stroke="{dark}" stroke-width="6"/><circle cx="202" cy="82" r="27" fill="{main}" stroke="{dark}" stroke-width="6"/>',
            '<circle cx="118" cy="78" r="8" fill="#111827"/><circle cx="202" cy="78" r="8" fill="#111827"/>',
            '<path d="M126 138 Q160 158 194 138" fill="none" stroke="#111827" stroke-width="5" stroke-linecap="round"/>',
        ]
    elif word in {"crab"}:
        e += [
            f'<ellipse cx="160" cy="130" rx="70" ry="44" fill="{main}" stroke="{dark}" stroke-width="6"/>',
            f'<path d="M92 118 L48 82 M228 118 L272 82" stroke="{dark}" stroke-width="10" stroke-linecap="round"/>',
            f'<circle cx="44" cy="78" r="18" fill="{main}" stroke="{dark}" stroke-width="6"/><circle cx="276" cy="78" r="18" fill="{main}" stroke="{dark}" stroke-width="6"/>',
            '<circle cx="138" cy="116" r="6" fill="#111827"/><circle cx="182" cy="116" r="6" fill="#111827"/>',
        ]
    elif word in {"bird", "hen", "chick", "duck"}:
        beak = "#f59e0b"
        e += [
            f'<ellipse cx="162" cy="128" rx="74" ry="48" fill="{main}" stroke="{dark}" stroke-width="6"/>',
            f'<circle cx="112" cy="92" r="34" fill="{main}" stroke="{dark}" stroke-width="6"/>',
            f'<path d="M78 94 L44 78 L74 113 Z" fill="{beak}" stroke="{dark}" stroke-width="5" stroke-linejoin="round"/>',
            '<circle cx="105" cy="85" r="6" fill="#111827"/>',
            f'<path d="M176 132 Q198 104 222 132 Q198 146 176 132Z" fill="{bg}" stroke="{dark}" stroke-width="5"/>',
            f'<path d="M134 174 V194 M186 174 V194" stroke="{dark}" stroke-width="7" stroke-linecap="round"/>',
        ]
    else:
        tail = "M230 130 Q270 96 284 132" if word in {"cat", "rat", "dog", "fox", "pup", "cub"} else "M230 134 Q260 118 280 134"
        e += [
            f'<ellipse cx="158" cy="132" rx="86" ry="48" fill="{main}" stroke="{dark}" stroke-width="6"/>',
            f'<circle cx="92" cy="102" r="38" fill="{main}" stroke="{dark}" stroke-width="6"/>',
            f'<path d="M72 74 L84 42 L98 76 M110 76 L128 44 L128 84" fill="{main}" stroke="{dark}" stroke-width="6" stroke-linejoin="round"/>',
            f'<path d="{tail}" fill="none" stroke="{dark}" stroke-width="9" stroke-linecap="round"/>',
            '<circle cx="82" cy="96" r="6" fill="#111827"/><circle cx="104" cy="96" r="6" fill="#111827"/>',
            f'<path d="M102 113 Q92 124 78 113" fill="none" stroke="{dark}" stroke-width="4" stroke-linecap="round"/>',
            f'<path d="M118 174 V196 M190 174 V196" stroke="{dark}" stroke-width="8" stroke-linecap="round"/>',
        ]
    return "\n".join(e) + svg_footer()


def person_svg(word: str, bg: str, main: str, dark: str) -> str:
    e = svg_header(word, bg)
    e += [
        f'<circle cx="160" cy="76" r="36" fill="#fed7aa" stroke="{dark}" stroke-width="6"/>',
        f'<path d="M98 188 C110 134 130 116 160 116 C190 116 212 134 224 188Z" fill="{main}" stroke="{dark}" stroke-width="6" stroke-linejoin="round"/>',
        '<circle cx="148" cy="70" r="5" fill="#111827"/><circle cx="172" cy="70" r="5" fill="#111827"/>',
        '<path d="M144 88 Q160 100 176 88" fill="none" stroke="#111827" stroke-width="5" stroke-linecap="round"/>',
    ]
    if word in {"nurse", "vet", "cop"}:
        e.append(f'<rect x="126" y="22" width="68" height="28" rx="8" fill="#ffffff" stroke="{dark}" stroke-width="5"/>')
        e.append(f'<path d="M160 28 V44 M150 36 H170" stroke="{main}" stroke-width="5" stroke-linecap="round"/>')
    return "\n".join(e) + svg_footer()


def vehicle_svg(word: str, bg: str, main: str, dark: str) -> str:
    e = svg_header(word, bg)
    if word == "boat":
        e += [
            f'<path d="M72 134 H260 L230 176 H100Z" fill="{main}" stroke="{dark}" stroke-width="6" stroke-linejoin="round"/>',
            f'<path d="M144 132 V54 L226 132Z" fill="#ffffff" stroke="{dark}" stroke-width="6" stroke-linejoin="round"/>',
            '<path d="M44 184 C86 166 116 166 158 184 C202 202 232 202 276 184" fill="none" stroke="#38bdf8" stroke-width="8" stroke-linecap="round"/>',
        ]
    elif word == "bike":
        e += [
            f'<circle cx="96" cy="156" r="36" fill="none" stroke="{dark}" stroke-width="8"/>',
            f'<circle cx="222" cy="156" r="36" fill="none" stroke="{dark}" stroke-width="8"/>',
            f'<path d="M96 156 L142 102 L178 156 L126 156 L156 122 L222 156" fill="none" stroke="{main}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>',
            f'<path d="M142 102 H174 M174 98 L194 84" stroke="{dark}" stroke-width="7" stroke-linecap="round"/>',
        ]
    elif word == "plane":
        e += [
            f'<path d="M42 130 L274 70 L228 132 L278 164 L42 130Z" fill="{main}" stroke="{dark}" stroke-width="6" stroke-linejoin="round"/>',
            f'<path d="M122 124 L92 176 L174 138" fill="#ffffff" stroke="{dark}" stroke-width="5" stroke-linejoin="round"/>',
        ]
    elif word == "train":
        e += [
            f'<rect x="58" y="80" width="204" height="84" rx="18" fill="{main}" stroke="{dark}" stroke-width="6"/>',
            '<rect x="82" y="98" width="46" height="30" rx="6" fill="#ffffff"/><rect x="144" y="98" width="46" height="30" rx="6" fill="#ffffff"/>',
            f'<circle cx="106" cy="172" r="15" fill="{dark}"/><circle cx="210" cy="172" r="15" fill="{dark}"/>',
            f'<path d="M50 192 H272" stroke="{dark}" stroke-width="7" stroke-linecap="round"/>',
        ]
    else:
        e += [
            f'<path d="M54 132 L88 88 H222 L262 132 V168 H54Z" fill="{main}" stroke="{dark}" stroke-width="6" stroke-linejoin="round"/>',
            '<rect x="104" y="98" width="46" height="30" rx="6" fill="#ffffff"/><rect x="166" y="98" width="46" height="30" rx="6" fill="#ffffff"/>',
            f'<circle cx="102" cy="170" r="18" fill="{dark}"/><circle cx="218" cy="170" r="18" fill="{dark}"/>',
        ]
    return "\n".join(e) + svg_footer()


def object_svg(word: str, bg: str, main: str, dark: str) -> str:
    e = svg_header(word, bg)
    if word in {"hat", "cap"}:
        e += [
            f'<path d="M92 132 C106 70 208 70 226 132Z" fill="{main}" stroke="{dark}" stroke-width="6"/>',
            f'<path d="M58 142 C96 128 220 128 264 142 C226 168 96 168 58 142Z" fill="#ffffff" stroke="{dark}" stroke-width="6"/>',
        ]
    elif word in {"bag", "sack"}:
        e += [
            f'<rect x="84" y="82" width="152" height="104" rx="22" fill="{main}" stroke="{dark}" stroke-width="6"/>',
            f'<path d="M124 82 C124 44 196 44 196 82" fill="none" stroke="{dark}" stroke-width="8" stroke-linecap="round"/>',
        ]
    elif word in {"pan", "pot"}:
        e += [
            f'<ellipse cx="142" cy="138" rx="80" ry="42" fill="{main}" stroke="{dark}" stroke-width="6"/>',
            f'<path d="M214 136 H286" stroke="{dark}" stroke-width="12" stroke-linecap="round"/>',
            '<path d="M112 92 C126 72 146 72 160 92 M170 92 C184 72 204 72 218 92" stroke="#94a3b8" stroke-width="6" stroke-linecap="round" fill="none"/>',
        ]
    elif word in {"net", "web"}:
        e += [
            f'<circle cx="160" cy="116" r="76" fill="#ffffff" stroke="{dark}" stroke-width="6"/>',
            f'<path d="M160 40 V192 M84 116 H236 M106 62 L214 170 M214 62 L106 170" stroke="{main}" stroke-width="5"/>',
            f'<circle cx="160" cy="116" r="34" fill="none" stroke="{main}" stroke-width="5"/>',
        ]
    elif word in {"desk", "table"}:
        e += [
            f'<rect x="58" y="90" width="204" height="40" rx="8" fill="{main}" stroke="{dark}" stroke-width="6"/>',
            f'<path d="M86 130 V190 M234 130 V190" stroke="{dark}" stroke-width="10" stroke-linecap="round"/>',
            '<rect x="112" y="54" width="96" height="28" rx="6" fill="#ffffff" opacity=".85"/>',
        ]
    elif word in {"book"}:
        e += [
            f'<path d="M70 68 H156 C172 68 184 80 184 96 V178 C172 166 156 160 136 160H70Z" fill="#ffffff" stroke="{dark}" stroke-width="6"/>',
            f'<path d="M184 96 C184 80 196 68 212 68H250V160H214C198 160 186 166 184 178Z" fill="{main}" stroke="{dark}" stroke-width="6"/>',
        ]
    elif word in {"ring", "coin", "dime"}:
        e += [
            f'<circle cx="160" cy="116" r="70" fill="{main}" stroke="{dark}" stroke-width="7"/>',
            '<circle cx="160" cy="116" r="34" fill="#ffffff" opacity=".85"/>',
        ]
    elif word in {"fork"}:
        e += [
            f'<path d="M142 48 V104 M160 48 V104 M178 48 V104 M142 104 C142 126 178 126 178 104" stroke="{dark}" stroke-width="9" stroke-linecap="round"/>',
            f'<path d="M160 124 V190" stroke="{main}" stroke-width="18" stroke-linecap="round"/>',
        ]
    elif word in {"drum"}:
        e += [
            f'<ellipse cx="160" cy="78" rx="76" ry="28" fill="#ffffff" stroke="{dark}" stroke-width="6"/>',
            f'<path d="M84 78 V158 C84 176 236 176 236 158 V78" fill="{main}" stroke="{dark}" stroke-width="6"/>',
            f'<ellipse cx="160" cy="158" rx="76" ry="28" fill="{main}" stroke="{dark}" stroke-width="6"/>',
            f'<path d="M78 48 L142 94 M242 48 L178 94" stroke="{dark}" stroke-width="7" stroke-linecap="round"/>',
        ]
    else:
        e += [
            f'<rect x="84" y="70" width="152" height="112" rx="22" fill="{main}" stroke="{dark}" stroke-width="6"/>',
            '<rect x="112" y="94" width="96" height="64" rx="12" fill="#ffffff" opacity=".72"/>',
            f'<path d="M112 176 L208 80" stroke="{dark}" stroke-width="5" stroke-linecap="round" opacity=".28"/>',
        ]
    return "\n".join(e) + svg_footer()


def nature_svg(word: str, bg: str, main: str, dark: str) -> str:
    e = svg_header(word, bg)
    if word in {"sun", "day"}:
        e += [
            f'<circle cx="160" cy="104" r="54" fill="#facc15" stroke="{dark}" stroke-width="6"/>',
            f'<path d="M160 24 V50 M160 158 V192 M80 104 H48 M272 104 H240 M102 46 L122 66 M218 46 L198 66 M102 162 L122 142 M218 162 L198 142" stroke="#f59e0b" stroke-width="8" stroke-linecap="round"/>',
        ]
    elif word in {"rain", "cloud", "snow", "storm"}:
        e += [
            '<ellipse cx="136" cy="94" rx="54" ry="34" fill="#ffffff" stroke="#64748b" stroke-width="6"/>',
            '<ellipse cx="184" cy="94" rx="62" ry="38" fill="#ffffff" stroke="#64748b" stroke-width="6"/>',
            '<rect x="96" y="94" width="138" height="38" rx="19" fill="#ffffff"/>',
            f'<path d="M112 154 L96 184 M154 154 L138 184 M196 154 L180 184" stroke="{main}" stroke-width="8" stroke-linecap="round"/>',
        ]
    elif word in {"tree", "leaf"}:
        e += [
            f'<rect x="146" y="110" width="28" height="78" rx="10" fill="#92400e"/>',
            f'<circle cx="126" cy="94" r="44" fill="{main}" stroke="{dark}" stroke-width="6"/>',
            f'<circle cx="184" cy="86" r="50" fill="{main}" stroke="{dark}" stroke-width="6"/>',
            f'<circle cx="174" cy="128" r="42" fill="{main}" stroke="{dark}" stroke-width="6"/>',
        ]
    elif word in {"lake", "wave", "pond"}:
        e += [
            '<path d="M54 158 C96 134 130 134 168 158 C204 180 236 180 272 158 V198 H54Z" fill="#7dd3fc"/>',
            f'<path d="M54 158 C96 134 130 134 168 158 C204 180 236 180 272 158" fill="none" stroke="{dark}" stroke-width="7" stroke-linecap="round"/>',
            f'<circle cx="232" cy="66" r="28" fill="{main}" opacity=".8"/>',
        ]
    elif word in {"star"}:
        e += [
            f'<path d="M160 42 L181 92 L236 96 L194 132 L208 186 L160 156 L112 186 L126 132 L84 96 L139 92Z" fill="#facc15" stroke="{dark}" stroke-width="6" stroke-linejoin="round"/>',
        ]
    elif word in {"farm", "park", "land", "sand"}:
        e += [
            f'<path d="M48 158 C96 112 132 118 166 154 C202 116 242 110 282 156 V202 H48Z" fill="{main}" stroke="{dark}" stroke-width="6"/>',
            '<path d="M72 176 H256" stroke="#ffffff" stroke-width="8" stroke-linecap="round" opacity=".6"/>',
        ]
    else:
        e += [
            f'<path d="M42 172 L118 80 L178 150 L218 112 L286 172Z" fill="{main}" stroke="{dark}" stroke-width="6" stroke-linejoin="round"/>',
            '<path d="M42 174 H286 V202 H42Z" fill="#ffffff" opacity=".65"/>',
        ]
    return "\n".join(e) + svg_footer()


def food_svg(word: str, bg: str, main: str, dark: str) -> str:
    e = svg_header(word, bg)
    e += [
        '<ellipse cx="160" cy="164" rx="92" ry="28" fill="#ffffff" stroke="#cbd5e1" stroke-width="6"/>',
        f'<path d="M90 150 C100 94 220 94 230 150Z" fill="{main}" stroke="{dark}" stroke-width="6"/>',
        '<circle cx="128" cy="126" r="10" fill="#ffffff" opacity=".75"/><circle cx="174" cy="112" r="9" fill="#ffffff" opacity=".75"/><circle cx="198" cy="138" r="8" fill="#ffffff" opacity=".75"/>',
    ]
    return "\n".join(e) + svg_footer()


def body_svg(word: str, bg: str, main: str, dark: str) -> str:
    e = svg_header(word, bg)
    if word in {"hand"}:
        e += [
            f'<path d="M116 154 V88 C116 74 136 74 136 88 V128 V72 C136 58 156 58 156 72 V126 V78 C156 64 176 64 176 78 V130 V94 C176 80 196 82 196 96 V150 C196 186 168 198 142 190 C120 184 98 166 82 144 C74 132 90 120 100 132Z" fill="{main}" stroke="{dark}" stroke-width="6" stroke-linejoin="round"/>',
        ]
    elif word in {"foot", "feet"}:
        e += [
            f'<path d="M90 148 C92 92 132 68 164 104 C180 122 202 126 232 132 C266 138 266 176 230 182 H122 C102 182 88 168 90 148Z" fill="{main}" stroke="{dark}" stroke-width="6"/>',
            '<circle cx="212" cy="124" r="7" fill="#ffffff"/><circle cx="232" cy="132" r="6" fill="#ffffff"/>',
        ]
    else:
        e += [
            f'<ellipse cx="160" cy="122" rx="70" ry="54" fill="{main}" stroke="{dark}" stroke-width="6"/>',
            f'<path d="M98 118 H222 M160 68 V176" stroke="{dark}" stroke-width="7" stroke-linecap="round"/>',
        ]
    return "\n".join(e) + svg_footer()


def action_svg(word: str, bg: str, main: str, dark: str) -> str:
    e = svg_header(word, bg)
    e += [
        f'<circle cx="122" cy="78" r="26" fill="#fed7aa" stroke="{dark}" stroke-width="6"/>',
        f'<path d="M122 104 L104 158 L76 186 M122 108 L156 148 L198 144 M112 138 L164 184" fill="none" stroke="{dark}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>',
        f'<path d="M202 84 H266 M240 60 L268 84 L240 108" fill="none" stroke="{main}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>',
        '<circle cx="88" cy="58" r="8" fill="#ffffff"/><circle cx="66" cy="76" r="5" fill="#ffffff"/><circle cx="232" cy="142" r="6" fill="#ffffff"/>',
    ]
    return "\n".join(e) + svg_footer()


def shape_svg(word: str, bg: str, main: str, dark: str) -> str:
    e = svg_header(word, bg)
    e += [
        f'<rect x="66" y="82" width="86" height="86" rx="18" fill="{main}" stroke="{dark}" stroke-width="6"/>',
        f'<circle cx="206" cy="124" r="48" fill="#ffffff" stroke="{dark}" stroke-width="6"/>',
        f'<path d="M192 70 L268 174 H116Z" fill="{main}" opacity=".72" stroke="{dark}" stroke-width="6" stroke-linejoin="round"/>',
    ]
    return "\n".join(e) + svg_footer()


def abstract_svg(word: str, bg: str, main: str, dark: str) -> str:
    e = svg_header(word, bg)
    e += [
        f'<circle cx="94" cy="112" r="32" fill="{main}" stroke="{dark}" stroke-width="6"/>',
        f'<circle cx="226" cy="84" r="28" fill="#ffffff" stroke="{dark}" stroke-width="6"/>',
        f'<circle cx="210" cy="158" r="38" fill="{main}" opacity=".75" stroke="{dark}" stroke-width="6"/>',
        f'<path d="M126 108 C160 84 178 78 198 82 M126 122 C156 146 174 156 172 158" fill="none" stroke="{dark}" stroke-width="7" stroke-linecap="round"/>',
    ]
    if word in NUMBERS:
        count = 10 if word == "ten" else 9
        dots = []
        for i in range(count):
            x = 88 + (i % 5) * 36
            y = 78 + (i // 5) * 42
            dots.append(f'<circle cx="{x}" cy="{y}" r="10" fill="#ffffff" stroke="{dark}" stroke-width="4"/>')
        e += dots
    return "\n".join(e) + svg_footer()


def theme_for(word: str, meaning: str) -> str:
    if word in ANIMALS:
        return "animal"
    if word in PEOPLE:
        return "person"
    if word in VEHICLES:
        return "vehicle"
    if word in FOOD:
        return "food"
    if word in NATURE:
        return "nature"
    if word in BODY:
        return "body"
    if word in HOUSE or word in TOOLS or word in MEDIA:
        return "object"
    if word in SHAPES or word in COLORS or word in NUMBERS:
        return "shape"
    if word in ACTION_HINTS:
        return "action"
    if any(key in meaning for key in ("走", "打", "押", "切", "回", "泳", "遊", "見", "吹", "曲が")):
        return "action"
    if any(key in meaning for key in ("色", "線", "点", "形", "立方体", "円すい")):
        return "shape"
    return "abstract"


def icon_svg(card: dict) -> str:
    word = card["word"]
    rule = card.get("rule", "")
    bg, main, dark = RULE_COLORS.get(rule, ("#f8fafc", "#94a3b8", "#334155"))
    seed = seed_for(word)
    accent_options = ["#f97316", "#14b8a6", "#8b5cf6", "#ef4444", "#22c55e", "#0ea5e9"]
    if seed % 5 == 0:
        main = accent_options[seed % len(accent_options)]
    theme = theme_for(word, card.get("meaning", ""))
    if theme == "animal":
        return animal_svg(word, bg, main, dark)
    if theme == "person":
        return person_svg(word, bg, main, dark)
    if theme == "vehicle":
        return vehicle_svg(word, bg, main, dark)
    if theme == "food":
        return food_svg(word, bg, main, dark)
    if theme == "nature":
        return nature_svg(word, bg, main, dark)
    if theme == "body":
        return body_svg(word, bg, main, dark)
    if theme == "object":
        return object_svg(word, bg, main, dark)
    if theme == "shape":
        return shape_svg(word, bg, main, dark)
    if theme == "action":
        return action_svg(word, bg, main, dark)
    return abstract_svg(word, bg, main, dark)


def safe_icon_name(card: dict) -> str:
    base = re.sub(r"[^a-z0-9-]+", "-", card["id"].lower()).strip("-")
    return f"{base}.svg"


KANJI_RE = re.compile(r"[\u3400-\u9fff]")

MEANING_RUBY_OVERRIDES = {
    "男の人": "<ruby>男<rt>おとこ</rt></ruby>の<ruby>人<rt>ひと</rt></ruby>",
    "男の人たち": "<ruby>男<rt>おとこ</rt></ruby>の<ruby>人<rt>ひと</rt></ruby>たち",
    "女の子": "<ruby>女<rt>おんな</rt></ruby>の<ruby>子<rt>こ</rt></ruby>",
    "動物の子": "<ruby>動物<rt>どうぶつ</rt></ruby>の<ruby>子<rt>こ</rt></ruby>",
    "木の実": "<ruby>木<rt>き</rt></ruby>の<ruby>実<rt>み</rt></ruby>",
    "手に入れた": "<ruby>手<rt>て</rt></ruby>に<ruby>入<rt>い</rt></ruby>れた",
    "パンの耳・地殻": "パンの<ruby>耳<rt>みみ</rt></ruby>・<ruby>地殻<rt>ちかく</rt></ruby>",
    "10セント硬貨": "10セント<ruby>硬貨<rt>こうか</rt></ruby>",
    "6月": "6<ruby>月<rt>がつ</rt></ruby>",
}

MEANING_READING_OVERRIDES = {
    "男の人": "おとこのひと",
    "男の人たち": "おとこのひとたち",
    "女の子": "おんなのこ",
    "動物の子": "どうぶつのこ",
    "木の実": "きのみ",
    "手に入れた": "てにいれた",
    "パンの耳・地殻": "ぱんのみみ・ちかく",
    "10セント硬貨": "10せんとこうか",
    "6月": "6がつ",
}


def has_kanji(text: str) -> bool:
    return bool(KANJI_RE.search(text))


def meaning_furigana(meaning: str, kks: pykakasi.kakasi) -> tuple[str, str]:
    if meaning in MEANING_RUBY_OVERRIDES:
        return MEANING_RUBY_OVERRIDES[meaning], MEANING_READING_OVERRIDES[meaning]

    ruby_parts: list[str] = []
    reading_parts: list[str] = []
    for token in kks.convert(meaning):
        original = token["orig"]
        hira = token["hira"]
        reading_parts.append(hira)
        if has_kanji(original):
            ruby_parts.append(f"<ruby>{escape(original)}<rt>{escape(hira)}</rt></ruby>")
        else:
            ruby_parts.append(escape(original))
    return "".join(ruby_parts), "".join(reading_parts)


def main() -> int:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    ICON_DIR.mkdir(parents=True, exist_ok=True)
    kks = pykakasi.kakasi()

    generated = 0
    furigana_updates = 0
    removed_word_kana = 0
    for card in data["words"]:
        if "kana" in card:
            del card["kana"]
            removed_word_kana += 1

        meaning_ruby, meaning_reading = meaning_furigana(card["meaning"], kks)
        if card.get("meaningRuby") != meaning_ruby:
            card["meaningRuby"] = meaning_ruby
            furigana_updates += 1
        if card.get("meaningReading") != meaning_reading:
            card["meaningReading"] = meaning_reading
            furigana_updates += 1

        if not card.get("image"):
            icon_path = ICON_DIR / safe_icon_name(card)
            icon_path.write_text(icon_svg(card), encoding="utf-8")
            card["image"] = str(icon_path)
            generated += 1

    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {generated} SVG icons")
    print(f"Removed {removed_word_kana} English pronunciation kana readings")
    print(f"Updated {furigana_updates} Japanese meaning furigana fields")
    print(f"Total word cards: {len(data['words'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
