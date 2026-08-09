#!/usr/bin/env python3
"""Build an index.html-like B-series drop-in pack without editing index.html."""
from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ASSET_DIR = ROOT / "funnics-beginner-assets"
LESSONS_JSON = ASSET_DIR / "b_series_lessons_ja.json"
YOUTUBE_JSON = ASSET_DIR / "b_series_youtube_urls.json"
INDEX_HTML = ROOT / "index.html"


POS_JA = {
    "adj": "形容詞",
    "adv": "副詞",
    "aux": "助動詞",
    "conj": "接続詞",
    "det": "限定詞",
    "noun": "名詞",
    "num": "数詞",
    "phrase": "フレーズ",
    "prep": "前置詞",
    "pron": "代名詞",
    "verb": "動詞",
    "interj": "間投詞",
}


FORCED_NEW_BY_B: dict[int, set[str]] = {
    2: {"yes"},
}


MANUAL_WORDS: dict[str, dict[str, str]] = {
    "aunt": {"ja": "おばさん", "ipa": "/ænt/", "pos": "noun"},
    "ant": {"ja": "アリ", "ipa": "/ænt/", "pos": "noun"},
    "baker": {"ja": "パン職人", "ipa": "/ˈbeɪkər/", "pos": "noun"},
    "bear": {"ja": "クマ", "ipa": "/ber/", "pos": "noun"},
    "blue": {"ja": "青い", "ipa": "/bluː/", "pos": "adj"},
    "boat": {"ja": "ボート", "ipa": "/boʊt/", "pos": "noun"},
    "bridge": {"ja": "橋", "ipa": "/brɪdʒ/", "pos": "noun"},
    "bug": {"ja": "虫", "ipa": "/bʌɡ/", "pos": "noun"},
    "coconut": {"ja": "ココナッツ", "ipa": "/ˈkoʊkənʌt/", "pos": "noun"},
    "correct": {"ja": "正しい", "ipa": "/kəˈrekt/", "pos": "adj"},
    "dragon": {"ja": "ドラゴン", "ipa": "/ˈdræɡən/", "pos": "noun"},
    "every": {"ja": "毎〜", "ipa": "/ˈevri/", "pos": "det"},
    "funnics": {"ja": "ファニックス", "ipa": "", "pos": "noun"},
    "gate": {"ja": "門", "ipa": "/ɡeɪt/", "pos": "noun"},
    "guide": {"ja": "案内役", "ipa": "/ɡaɪd/", "pos": "noun"},
    "island": {"ja": "島", "ipa": "/ˈaɪlənd/", "pos": "noun"},
    "just": {"ja": "ただ", "ipa": "/dʒʌst/", "pos": "adv"},
    "machine": {"ja": "機械", "ipa": "/məˈʃiːn/", "pos": "noun"},
    "make": {"ja": "作る", "ipa": "/meɪk/", "pos": "verb"},
    "map": {"ja": "地図", "ipa": "/mæp/", "pos": "noun"},
    "music": {"ja": "音楽", "ipa": "/ˈmjuːzɪk/", "pos": "noun"},
    "road": {"ja": "道", "ipa": "/roʊd/", "pos": "noun"},
    "right": {"ja": "その通り", "ipa": "/raɪt/", "pos": "adj"},
    "run": {"ja": "走る", "ipa": "/rʌn/", "pos": "verb"},
    "race": {"ja": "競走", "ipa": "/reɪs/", "pos": "noun"},
    "salsa": {"ja": "サルサ", "ipa": "/ˈsɑːlsə/", "pos": "noun"},
    "shell": {"ja": "貝がら", "ipa": "/ʃel/", "pos": "noun"},
    "shells": {"ja": "貝がら（複数）", "ipa": "/ʃelz/", "pos": "noun"},
    "singer": {"ja": "歌い手", "ipa": "/ˈsɪŋər/", "pos": "noun"},
    "snake": {"ja": "ヘビ", "ipa": "/sneɪk/", "pos": "noun"},
    "slow": {"ja": "ゆっくりした", "ipa": "/sloʊ/", "pos": "adj"},
    "sound": {"ja": "音", "ipa": "/saʊnd/", "pos": "noun"},
    "speed": {"ja": "速さ", "ipa": "/spiːd/", "pos": "noun"},
    "taco": {"ja": "タコス", "ipa": "/ˈtɑːkoʊ/", "pos": "noun"},
    "tacos": {"ja": "タコス", "ipa": "/ˈtɑːkoʊz/", "pos": "noun"},
    "teacher": {"ja": "先生", "ipa": "/ˈtiːtʃər/", "pos": "noun"},
    "tom": {"ja": "トム", "ipa": "/tɑːm/", "pos": "noun"},
    "volcano": {"ja": "火山", "ipa": "/vɑːlˈkeɪnoʊ/", "pos": "noun"},
    "walk": {"ja": "歩く", "ipa": "/wɔːk/", "pos": "verb"},
    "way": {"ja": "道順", "ipa": "/weɪ/", "pos": "noun"},
    "welcome": {"ja": "歓迎されている", "ipa": "/ˈwelkəm/", "pos": "adj"},
    "very": {"ja": "とても", "ipa": "/ˈveri/", "pos": "adv"},
    "wow": {"ja": "わあ", "ipa": "/waʊ/", "pos": "interj"},
    "yesterday": {"ja": "昨日", "ipa": "/ˈjestərdeɪ/", "pos": "adv"},
    "yes": {"ja": "はい", "ipa": "/jes/", "pos": "interj"},
    "no": {"ja": "いいえ", "ipa": "/noʊ/", "pos": "interj"},
    "what": {"ja": "何", "ipa": "/wʌt/", "pos": "pron"},
    "who": {"ja": "だれ", "ipa": "/huː/", "pos": "pron"},
    "when": {"ja": "いつ", "ipa": "/wen/", "pos": "adv"},
    "where": {"ja": "どこ", "ipa": "/wer/", "pos": "adv"},
    "how": {"ja": "どう", "ipa": "/haʊ/", "pos": "adv"},
    "know": {"ja": "知っている", "ipa": "/noʊ/", "pos": "verb"},
    "worry": {"ja": "心配する", "ipa": "/ˈwɜːri/", "pos": "verb"},
    "talks": {"ja": "話す", "ipa": "/tɔːks/", "pos": "verb"},
    "hello": {"ja": "こんにちは", "ipa": "/həˈloʊ/", "pos": "interj"},
    "hi": {"ja": "やあ", "ipa": "/haɪ/", "pos": "interj"},
    "hmm": {"ja": "うーん", "ipa": "/həm/", "pos": "interj"},
    "ok": {"ja": "わかった", "ipa": "/ˌoʊˈkeɪ/", "pos": "interj"},
    "okay": {"ja": "わかった", "ipa": "/ˌoʊˈkeɪ/", "pos": "interj"},
    "what's": {"ja": "何ですか", "ipa": "/wʌts/", "pos": "phrase"},
    "that's": {"ja": "それは〜です", "ipa": "/ðæts/", "pos": "phrase"},
    "it's": {"ja": "それは〜です", "ipa": "/ɪts/", "pos": "phrase"},
    "don't": {"ja": "〜しない", "ipa": "/doʊnt/", "pos": "aux"},
    "doesn't": {"ja": "〜しない", "ipa": "/ˈdʌzənt/", "pos": "aux"},
    "can't": {"ja": "〜できない", "ipa": "/kænt/", "pos": "aux"},
    "let's": {"ja": "〜しよう", "ipa": "/lets/", "pos": "phrase"},
    "ready": {"ja": "準備ができた", "ipa": "/ˈredi/", "pos": "adj"},
    "hungry": {"ja": "おなかがすいた", "ipa": "/ˈhʌŋɡri/", "pos": "adj"},
    "curious": {"ja": "気になっている", "ipa": "/ˈkjʊriəs/", "pos": "adj"},
    "nervous": {"ja": "緊張している", "ipa": "/ˈnɜːrvəs/", "pos": "adj"},
    "friendly": {"ja": "親切な", "ipa": "/ˈfrendli/", "pos": "adj"},
    "alone": {"ja": "ひとりで", "ipa": "/əˈloʊn/", "pos": "adj"},
    "talking": {"ja": "話している", "ipa": "/ˈtɔːkɪŋ/", "pos": "verb"},
    "strange": {"ja": "不思議な", "ipa": "/streɪndʒ/", "pos": "adj"},
    "amazing": {"ja": "すごい", "ipa": "/əˈmeɪzɪŋ/", "pos": "adj"},
    "excited": {"ja": "わくわくしている", "ipa": "/ɪkˈsaɪtɪd/", "pos": "adj"},
    "need": {"ja": "必要とする", "ipa": "/niːd/", "pos": "verb"},
    "want": {"ja": "欲しい", "ipa": "/wɑːnt/", "pos": "verb"},
    "follow": {"ja": "ついて行く", "ipa": "/ˈfɑːloʊ/", "pos": "verb"},
    "smell": {"ja": "におい", "ipa": "/smel/", "pos": "noun"},
    "dance": {"ja": "踊る", "ipa": "/dæns/", "pos": "verb"},
    "dancing": {"ja": "踊っている", "ipa": "/ˈdænsɪŋ/", "pos": "verb"},
    "count": {"ja": "数える", "ipa": "/kaʊnt/", "pos": "verb"},
    "flags": {"ja": "旗（複数）", "ipa": "/flæɡz/", "pos": "noun"},
    "open": {"ja": "開ける", "ipa": "/ˈoʊpən/", "pos": "verb"},
    "close": {"ja": "閉じる", "ipa": "/kloʊz/", "pos": "verb"},
    "give": {"ja": "与える", "ipa": "/ɡɪv/", "pos": "verb"},
    "me": {"ja": "私に／私を", "ipa": "/miː/", "pos": "pron"},
    "him": {"ja": "彼に／彼を", "ipa": "/hɪm/", "pos": "pron"},
    "her": {"ja": "彼女に／彼女を", "ipa": "/hɜːr/", "pos": "pron"},
    "us": {"ja": "私たちに／私たちを", "ipa": "/ʌs/", "pos": "pron"},
}


GRAMMAR_NOTES: dict[int, dict[str, object]] = {
    1: {
        "title": "I am 〜 / You are 〜",
        "desc": "自分の名前や気持ちは I am 〜、相手について言うときは You are 〜 を使います。be動詞は「主語 = 説明」をつなぐ役目です。",
        "examples": [
            ("I am Teacher Tacos.", "私はティーチャータコスです。"),
            ("You are welcome here.", "きみはここで歓迎されています。"),
            ("I am excited.", "ぼくはわくわくしています。"),
        ],
    },
    2: {
        "title": "Are you ...? / Yes, I am. / No, I am not.",
        "desc": "相手に「あなたは〜ですか」とたずねるときは Are you ...? を使います。答えは Yes, I am. / No, I am not. が基本です。",
        "examples": [
            ("Are you ready?", "準備はできていますか。"),
            ("Yes, I am.", "はい、できています。"),
            ("No, I am not.", "いいえ、そうではありません。"),
        ],
    },
    3: {
        "title": "not / alone / welcome",
        "desc": "be動詞や文の中心になる語のあとに not を置くと「〜ではない」を表せます。not alone は「ひとりではない」という安心の表現です。",
        "examples": [
            ("I am not from this island.", "私はこの島の出身ではありません。"),
            ("You are not alone.", "きみはひとりではありません。"),
            ("This island is not only for tacos.", "この島はタコスだけの場所ではありません。"),
        ],
    },
    4: {
        "title": "I like / I eat / I follow",
        "desc": "like, eat, follow などの一般動詞は、主語のあとにそのまま置いて「〜する」を表します。I like 〜 は「私は〜が好き」です。",
        "examples": [
            ("I like this market.", "私はこの市場が好きです。"),
            ("I eat coconuts.", "私はココナッツを食べます。"),
            ("I follow the road.", "私は道について行きます。"),
        ],
    },
    5: {
        "title": "is not just / You are ...",
        "desc": "is not just 〜 は「ただの〜ではない」という言い方です。見た目以上の役割や意味があることを表します。",
        "examples": [
            ("Teacher Tacos is not just a name.", "ティーチャータコスはただの名前ではありません。"),
            ("You are a real teacher.", "あなたは本物の先生です。"),
            ("This is not just a taco.", "これはただのタコスではありません。"),
        ],
    },
    6: {
        "title": "don't / need / want",
        "desc": "I don't + 動詞で「私は〜しない」。need は「必要とする」、want は「ほしい／〜したい」です。",
        "examples": [
            ("Don't worry, Tom.", "心配しないで、トム。"),
            ("I know the way.", "私は道を知っています。"),
            ("I don't need a map.", "私は地図を必要としません。"),
        ],
    },
    7: {
        "title": "this / that",
        "desc": "近くのものは this、少し離れたものは that で指します。This is 〜 / That is 〜 は「これは〜です／あれは〜です」です。",
        "examples": [
            ("This is the blue gate.", "これは青い門です。"),
            ("That is the old road.", "あれは古い道です。"),
            ("This map is strange.", "この地図は不思議です。"),
        ],
    },
    8: {
        "title": "what / this / that",
        "desc": "what は「何」をたずねる疑問詞です。What is this? は「これは何ですか」、What is that? は「あれは何ですか」です。",
        "examples": [
            ("What is this?", "これは何ですか。"),
            ("What is that sound?", "あの音は何ですか。"),
            ("It is a sound machine.", "それは音の機械です。"),
        ],
    },
    9: {
        "title": "who / by / on",
        "desc": "who は「だれ」をたずねます。by は作った人や近くを表し、on は「〜の上に」を表します。",
        "examples": [
            ("Who is that?", "あれはだれですか。"),
            ("The old book is by Singer Snake.", "その古い本はシンガースネイクによるものです。"),
            ("It is on the table.", "それはテーブルの上にあります。"),
        ],
    },
    10: {
        "title": "he / she / it",
        "desc": "男性や男の子は he、女性や女の子は she、ものや動物を受けるときは it を使います。",
        "examples": [
            ("Who is he?", "彼はだれですか。"),
            ("She is Doctor Dragon.", "彼女はドクタードラゴンです。"),
            ("It is a small bug.", "それは小さな虫です。"),
        ],
    },
    11: {
        "title": "does / doesn't",
        "desc": "he / she / it など三人称単数の疑問文では Does he ...?、否定文では He doesn't ... を使います。doesn't のあとは動詞の原形です。",
        "examples": [
            ("Does Baker Bear bake bread?", "ベイカーベアはパンを焼きますか。"),
            ("Yes, he does.", "はい、焼きます。"),
            ("He doesn't dance now.", "彼は今は踊りません。"),
        ],
    },
    12: {
        "title": "when / at",
        "desc": "when は「いつ」をたずねる疑問詞です。時刻には at を使い、at three のように言います。",
        "examples": [
            ("When is the show?", "ショーはいつですか。"),
            ("It is at three.", "それは3時です。"),
            ("When do we go?", "私たちはいつ行きますか。"),
        ],
    },
    13: {
        "title": "where / under / on",
        "desc": "where は「どこ」をたずねます。under は「〜の下に」、on は「〜の上に」を表す前置詞です。",
        "examples": [
            ("Where is Teacher Tacos?", "ティーチャータコスはどこですか。"),
            ("He is under the table.", "彼はテーブルの下にいます。"),
            ("The salsa is on the chair.", "サルサは椅子の上にあります。"),
        ],
    },
    14: {
        "title": "how / do",
        "desc": "how は「どのように／どんな状態で」をたずねます。How are you? は気分をたずねる基本表現です。",
        "examples": [
            ("How are you?", "元気ですか。"),
            ("How do we open it?", "どうやってそれを開けますか。"),
            ("I am fine.", "私は元気です。"),
        ],
    },
    15: {
        "title": "plural nouns and numbers",
        "desc": "数が2つ以上の名詞は、多くの場合 s をつけて複数形にします。one shell / two shells のように数と一緒に使います。",
        "examples": [
            ("one shell", "1つの貝がら"),
            ("two flags", "2本の旗"),
            ("There are many shells.", "たくさんの貝がらがあります。"),
        ],
    },
    16: {
        "title": "imperatives / don't",
        "desc": "動詞から始めると「〜しなさい」という命令文になります。Don't + 動詞で「〜しないで」と伝えます。",
        "examples": [
            ("Open the gate.", "門を開けなさい。"),
            ("Close your eyes.", "目を閉じなさい。"),
            ("Don't touch the blue stone.", "青い石に触らないで。"),
        ],
    },
    17: {
        "title": "pronouns / give",
        "desc": "I / my / me のように、同じ人でも文の中で形が変わります。give it to me は「それを私にください」です。",
        "examples": [
            ("Give it to me.", "それを私にください。"),
            ("This is my map.", "これは私の地図です。"),
            ("Give it to her.", "それを彼女に渡してください。"),
        ],
    },
    18: {
        "title": "present progressive",
        "desc": "am / is / are + 動詞ing で「今〜している」を表します。now と一緒に使われることが多いです。",
        "examples": [
            ("I am dancing.", "私は踊っています。"),
            ("Teacher Tacos is moving.", "ティーチャータコスは動いています。"),
            ("They are singing.", "彼らは歌っています。"),
        ],
    },
    19: {
        "title": "can / cannot",
        "desc": "can + 動詞の原形で「〜できる」。cannot / can't は「〜できない」。疑問文は Can you ...? です。",
        "examples": [
            ("Can I help?", "手伝えますか。"),
            ("I can carry this.", "私はこれを運べます。"),
            ("I cannot fly.", "私は飛べません。"),
        ],
    },
    20: {
        "title": "past tense",
        "desc": "過去のことは動詞を過去形にします。規則動詞は -ed、不規則動詞は went / ate / saw / made のように形が変わります。",
        "examples": [
            ("I played yesterday.", "私は昨日遊びました。"),
            ("We went to the gate.", "私たちは門へ行きました。"),
            ("Did you see it?", "それを見ましたか。"),
        ],
    },
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def normalize_base(word: str) -> str:
    return word.lower().strip("'").replace("’", "'")


def load_word_bank() -> dict[str, dict[str, str]]:
    bank: dict[str, dict[str, str]] = {}
    if INDEX_HTML.exists():
        text = INDEX_HTML.read_text(encoding="utf-8")
        for match in re.finditer(r'<span class="w[^"]*"([^>]*)>(.*?)</span>', text):
            attrs, inner = match.groups()
            base_m = re.search(r'data-base="([^"]+)"', attrs)
            ja_m = re.search(r'data-ja="([^"]*)"', attrs)
            ipa_m = re.search(r'data-ipa="([^"]*)"', attrs)
            pos_m = re.search(r'data-pos="([^"]*)"', attrs)
            raw_base = html.unescape(base_m.group(1)) if base_m else re.sub(r"<[^>]+>", "", inner)
            base = normalize_base(raw_base)
            if not base or base in bank:
                continue
            bank[base] = {
                "ja": html.unescape(ja_m.group(1)) if ja_m else "",
                "ipa": html.unescape(ipa_m.group(1)) if ipa_m else "",
                "pos": html.unescape(pos_m.group(1)) if pos_m else "",
            }
    bank.update(MANUAL_WORDS)
    return bank


WORD_RE = re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)?|\d+|[^A-Za-z\d]+")

MIX_JA_PATTERNS: dict[str, list[str]] = {
    "a": [],
    "an": [],
    "the": [],
    "to": [],
    "of": [],
    "in": [],
    "on": [],
    "at": [],
    "for": [],
    "with": [],
    "and": [],
    "or": [],
    "but": [],
    "is": [],
    "are": [],
    "am": [],
    "be": [],
    "do": [],
    "does": [],
    "did": [],
    "i": [],
    "you": [],
    "he": [],
    "she": [],
    "it": [],
    "we": [],
    "they": [],
    "my": [],
    "your": [],
    "his": [],
    "her": [],
    "our": [],
    "tom": [],
    "teacher": [],
    "taco": [],
    "tacos": [],
    "hello": ["こんにちは"],
    "hi": ["やあ"],
    "yes": ["うん", "はい"],
    "no": ["いいえ"],
    "ok": ["よし", "わかった"],
    "hmm": ["うーん"],
    "wow": ["わあ"],
    "welcome": ["ようこそ", "大歓迎", "歓迎"],
    "island": ["アイランド", "島"],
    "what": ["何"],
    "who": ["だれ", "誰"],
    "when": ["いつ"],
    "where": ["どこ"],
    "how": ["どう", "どんな"],
    "this": ["これ", "この", "ここ"],
    "that": ["あれ", "あの", "それ"],
    "name": ["名前"],
    "ready": ["準備"],
    "hungry": ["おなか", "すいている", "すいて"],
    "not": ["じゃない", "ではない", "ない", "ません"],
    "just": ["ただ"],
    "curious": ["気になっている"],
    "nervous": ["緊張している", "緊張"],
    "friendly": ["親切"],
    "alone": ["一人", "ひとり"],
    "road": ["道"],
    "way": ["道"],
    "know": ["知って", "わかって", "わかる"],
    "need": ["必要", "いらない", "いる"],
    "want": ["ほしい", "したい"],
    "talk": ["話", "しゃべ"],
    "talks": ["話", "しゃべ"],
    "map": ["地図"],
    "blue": ["青い", "青"],
    "gate": ["門"],
    "sound": ["音"],
    "machine": ["機械"],
    "dragon": ["ドラゴン"],
    "baker": ["ベイカー", "パン職人"],
    "bear": ["ベア", "クマ"],
    "salsa": ["サルサ"],
    "shell": ["貝がら"],
    "shells": ["貝がら"],
    "flags": ["旗"],
    "open": ["開け"],
    "give": ["渡して", "ちょうだい", "ください"],
    "dance": ["ダンス", "踊"],
    "dancing": ["踊って"],
    "yesterday": ["昨日"],
}


def token_bases(text: str) -> list[str]:
    bases: list[str] = []
    for token in WORD_RE.findall(text):
        if re.fullmatch(r"[A-Za-z]+(?:['’][A-Za-z]+)?|\d+", token):
            bases.append(normalize_base(token))
    return bases


def repeat_core(text: str) -> str:
    core = text.lower().replace("'", "").replace("’", "")
    core = re.sub(r"[^a-z0-9 ]+", " ", core)
    # Drop short conversational fillers so near-repeat lyric padding collapses.
    fillers = [
        "thats right",
        "ok",
        "yes",
        "no",
        "wow",
        "hmm",
        "aha",
        "oh",
        "hi",
        "hello",
        "great",
        "good",
        "look",
        "wait",
        "ta da",
        "tada",
        "whoa",
        "easy",
        "phew",
        "yikes",
        "ding",
        "dong",
        "oops",
        "please",
        "now",
    ]
    for filler in fillers:
        core = re.sub(rf"\b{re.escape(filler)}\b", " ", core)
    return re.sub(r"\s+", " ", core).strip()


def prepare_lessons(lessons: list[dict]) -> list[dict]:
    """Remove repeated lyric lines and precompute first-appearance words."""
    seen_vocab: set[str] = set()
    prepared: list[dict] = []
    for lesson in lessons:
        lesson_copy = dict(lesson)
        seen_lines: set[tuple[str, str, str]] = set()
        display_lines: list[dict] = []
        lesson_vocab: set[str] = set()
        last_display_speaker = ""
        last_display_core = ""
        for line in lesson["lines"]:
            speaker_key = str(line["speaker"]).strip().lower()
            key = (
                speaker_key,
                re.sub(r"\s+", " ", str(line["english"]).strip().lower()),
                re.sub(r"\s+", " ", str(line["japanese"]).strip()),
            )
            if key in seen_lines:
                continue
            core = repeat_core(str(line["english"]))
            if (
                speaker_key == last_display_speaker
                and core
                and core == last_display_core
                and len(core) >= 10
            ):
                continue
            seen_lines.add(key)
            display_lines.append(line)
            lesson_vocab.update(token_bases(line["english"]))
            last_display_speaker = speaker_key
            last_display_core = core
        new_bases = (lesson_vocab - seen_vocab) | FORCED_NEW_BY_B.get(int(lesson["b"]), set())
        lesson_copy["display_lines"] = display_lines
        lesson_copy["new_bases"] = sorted(new_bases)
        lesson_copy["removed_repeated_lines"] = len(lesson["lines"]) - len(display_lines)
        prepared.append(lesson_copy)
        seen_vocab.update(lesson_vocab)
    return prepared


def span_words(text: str, class_name: str, bank: dict[str, dict[str, str]]) -> str:
    out: list[str] = []
    for token in WORD_RE.findall(text):
        if re.fullmatch(r"[A-Za-z]+(?:['’][A-Za-z]+)?|\d+", token):
            base = normalize_base(token)
            info = bank.get(base, {"ja": "", "ipa": "", "pos": ""})
            attrs = [
                f'class="{class_name}"',
                f'data-base="{esc(base)}"',
                f'data-ja="{esc(info.get("ja", ""))}"',
            ]
            if class_name == "w":
                attrs.append(f'data-ipa="{esc(info.get("ipa", ""))}"')
                attrs.append(f'data-pos="{esc(info.get("pos", ""))}"')
            out.append(f"<span {' '.join(attrs)}>{esc(token)}</span>")
        else:
            out.append(esc(token))
    return "".join(out)


def word_span(token: str, class_name: str, bank: dict[str, dict[str, str]]) -> str:
    base = normalize_base(token)
    info = bank.get(base, {"ja": "", "ipa": "", "pos": ""})
    attrs = [
        f'class="{class_name}"',
        f'data-base="{esc(base)}"',
        f'data-ja="{esc(info.get("ja", ""))}"',
    ]
    if class_name == "w":
        attrs.append(f'data-ipa="{esc(info.get("ipa", ""))}"')
        attrs.append(f'data-pos="{esc(info.get("pos", ""))}"')
    return f"<span {' '.join(attrs)}>{esc(token)}</span>"


def mixed_word(token: str, new_bases: set[str], bank: dict[str, dict[str, str]], base: str | None = None) -> str:
    resolved = normalize_base(base or token)
    if resolved in new_bases:
        return word_span(token, "w", bank)
    return esc(token)


def mixed_phrase(text: str, new_bases: set[str], bank: dict[str, dict[str, str]]) -> str:
    out: list[str] = []
    for token in WORD_RE.findall(text):
        if re.fullmatch(r"[A-Za-z]+(?:['’][A-Za-z]+)?|\d+", token):
            out.append(mixed_word(token, new_bases, bank))
        else:
            out.append(esc(token))
    return "".join(out)


def norm_line_text(text: object) -> str:
    return re.sub(r"\s+", " ", str(text).replace("’", "'").strip().lower())


def mixed_line_override(line: dict, new_bases: set[str], bank: dict[str, dict[str, str]]) -> str | None:
    en = norm_line_text(line["english"])
    w = lambda token, base=None: mixed_word(token, new_bases, bank, base)
    wj = lambda token, ja, base=None: word_span(token, "w", bank) if normalize_base(base or token) in new_bases else esc(ja)
    wv = lambda token, ja, suffix, base=None: (
        word_span(token, "w", bank) + esc(suffix) if normalize_base(base or token) in new_bases else esc(ja)
    )
    p = lambda text: mixed_phrase(text, new_bases, bank)

    if en == "hello! welcome to funnics island.":
        return f"{w('Hello')}！{w('Funnics')} {w('Island')}へ{w('Welcome')}。"
    if en == "what's your name?":
        whats = w("What's")
        return f"{whats}、あなたの{w('name')}？"
    if en == "hi! my name is tom.":
        return f"{w('Hi')}！ぼくの{w('name')}はトムです。"
    if en == "nice to meet you, tom.":
        return "はじめまして、トム。"
    if en == "i am teacher tacos.":
        return "私はティーチャータコスです。"
    if en == "oh! a talking taco!":
        return f"えっ！{w('talking')}タコスだ！"
    if en == "i am the gate guide today.":
        return f"今日は私が{w('gate')}の{w('guide')}です。"
    if en == "you are welcome here.":
        return f"ここでは、きみは{w('welcome')}だよ。"
    if en == "wow! i am excited.":
        return f"わあ！{w('excited')}してきた。"
    if en == "this place is amazing.":
        return f"ここは{w('amazing')}場所だね。"
    if en == "yes. this island is a little strange, too.":
        return f"うん。この島はちょっと{w('strange')}でもあるんだ。"

    if en == "ok, tom, are you ready?":
        return f"{w('OK')}、トム、{w('ready')}はできた？"
    if en == "hmm... yes, i am.":
        return f"{wj('Hmm', 'うーん')}……{wj('Yes', 'うん')}、できたよ。"
    if en == "are you hungry?":
        return f"{w('hungry')}なの？"
    if en == "no, i am not.":
        return f"{w('No')}、{w('not')} {w('hungry')}だよ。"
    if en == "i am just curious. wow.":
        return f"{w('just')} {w('curious')}なだけ。わあ。"
    if en == "are you nervous?":
        return f"{w('nervous')}なの？"
    if en == "hmm... are the island friends friendly?":
        return f"うーん……島の仲間たちは{w('friendly')}かな？"
    if en == "yes. very friendly.":
        return f"{wj('Yes', 'うん')}。{w('Very', 'very')} {w('friendly')}だよ。"
    if en == "don't worry.":
        if "don't" in new_bases or "worry" in new_bases:
            dont = w("Don't")
            return f"{dont} {w('worry')}。"
        return "心配しないで。"
    if en == "ok. then i am ready.":
        return f"{w('OK')}。じゃあ{w('ready')}だよ。"

    if en == "teacher taco, i am not from this island.":
        return "ティーチャータコス、ぼくはこの島の出身じゃないんだ。"
    if en == "i know, tom. don't worry.":
        return "わかっているよ、トム。心配しないで。"
    if en == "you are not alone.":
        return f"きみは{w('alone')}じゃないよ。"
    if en == "hello, tom. i am aunt ant.":
        return f"こんにちは、トム。私は{p('Aunt Ant')}です。"
    if en == "hi, aunt ant. you are not a taco!":
        return f"やあ、{p('Aunt Ant')}。あなたはタコスじゃないね！"
    if en == "that's right! i am an ant.":
        thats = w("That's")
        return f"{thats} {w('right')}！私は{w('ant')}だよ。"
    if en == "that's right! that's right! i am an ant.":
        thats = w("That's")
        return f"{thats} {w('right')}！{thats} {w('right')}！私は{w('ant')}だよ。"
    if en == "this island is not only for tacos.":
        return f"この島はタコス{w('only')}の場所じゃないんだ。"
    if en == "you are not a taco, but you are welcome here.":
        return "きみはタコスじゃないけれど、ここでは大歓迎だよ。"
    if en == "wow! i am not alone. i have new friends here.":
        return f"わあ！ぼくは{w('alone')}じゃない。ここには{w('new')}友だちがいるんだ。"

    if en == "teacher tacos, i don't know the road.":
        return f"ティーチャータコス、ぼくは{wj('road', '道')}がわからないよ。"
    if en == "don't worry. you don't need a big map. the road talks.":
        return f"心配しないで。大きな{wj('map', '地図')}はいらないよ。{wj('road', '道')}が{wv('talks', '話してくれる', 'してくれる')}んだ。"
    if en == "don't worry, tom. i know the way.":
        return f"心配しないで、トム。{wj('way', '道')}はわかっているよ。"
    if en == "ok. i don't run on a new road.":
        return f"わかった。新しい{wj('road', '道')}では{wv('run', '走らない', 'しない')}よ。"
    if en == "hi, tom. i run every day.":
        return f"やあ、トム。ぼくは{wj('every', '毎')}日{wv('run', '走っている', 'している')}よ。"
    if en == "easy, tom. you don't need speed today.":
        return f"落ち着いて、トム。今日は{wj('speed', '速さ')}はいらないよ。"
    if en == "phew. i don't want a race. i want a slow walk.":
        return f"ふう。{wj('race', '競走')}はしたくないんだ。{wj('slow', 'ゆっくり')} {wj('walk', '歩き')}がしたい。"
    if en == "a slow walk? so strange!":
        return f"{wj('slow', 'ゆっくり')} {wj('walk', '歩く')}？変わっているね！"
    if en == "oh! the road is talking, so i walk slowly.":
        return f"あっ！{wj('road', '道')}が{wv('talking', '話している', 'している')}から、ぼくはゆっくり{wv('walk', '歩くんだ', 'するんだ')}。"

    if en == "hi, tom. look! this is a map.":
        return f"やあ、トム。見て！これは{wj('map', '地図')}だよ。"
    if en == "yes. good. that is the blue gate.":
        return f"うん、いいね。あれが{w('blue')}の{wj('gate', '門')}だよ。"
    if en == "is that the sound hill?":
        return f"あれが{w('sound')}の丘なの？"
    if en == "yes, that is the sound hill.":
        return f"うん、あれが{w('sound')}の丘だよ。"
    if en == "hi, tom. that is a boat by the gate.":
        return f"やあ、トム。あれは{wj('gate', '門')}のそばの{w('boat')}だよ。"

    return None


def new_word_chips(text: str, new_bases: set[str], bank: dict[str, dict[str, str]]) -> list[str]:
    chips: list[str] = []
    seen: set[str] = set()
    for token in WORD_RE.findall(text):
        if not re.fullmatch(r"[A-Za-z]+(?:['’][A-Za-z]+)?|\d+", token):
            continue
        base = normalize_base(token)
        if base not in new_bases or base in seen:
            continue
        seen.add(base)
        chips.append(word_span(token, "w", bank))
    return chips


def ja_candidates(base: str, bank: dict[str, dict[str, str]]) -> list[str]:
    manual = MIX_JA_PATTERNS.get(base)
    if manual is not None:
        return manual
    info = bank.get(base, {})
    raw = info.get("ja", "")
    if not raw:
        return []
    candidates: list[str] = []
    for part in re.split(r"[／/、,]", raw):
        part = re.sub(r"（.*?）", "", part).strip()
        part = part.replace("〜", "").strip()
        if not part:
            continue
        candidates.append(part)
        particle = re.match(r"^(.+?)(?:が|は|を|に|へ|で|の|と).+$", part)
        if particle:
            candidates.append(particle.group(1))
        for suffix in ["している", "して", "されている", "されて", "できた", "できる", "な", "い"]:
            if part.endswith(suffix) and len(part) > len(suffix):
                candidates.append(part[: -len(suffix)])
    deduped: list[str] = []
    for item in sorted(candidates, key=len, reverse=True):
        if item and item not in deduped:
            deduped.append(item)
    return deduped


def mixed_japanese_sentence(line: dict, new_bases: set[str], bank: dict[str, dict[str, str]]) -> str:
    override = mixed_line_override(line, new_bases, bank)
    if override is not None:
        return override

    text = str(line["japanese"])
    placeholders: dict[str, str] = {}
    used: set[str] = set()
    for token in WORD_RE.findall(str(line["english"])):
        if not re.fullmatch(r"[A-Za-z]+(?:['’][A-Za-z]+)?|\d+", token):
            continue
        base = normalize_base(token)
        if base not in new_bases or base in used:
            continue
        candidates = ja_candidates(base, bank)
        if not candidates:
            continue
        span = word_span(token, "w", bank)
        for candidate in candidates:
            if candidate and candidate in text:
                marker = f"\uFFF0{len(placeholders)}\uFFF1"
                text = text.replace(candidate, marker, 1)
                placeholders[marker] = span
                used.add(base)
                break

    if not placeholders:
        return esc(text)
    pattern = re.compile("|".join(re.escape(k) for k in placeholders))
    parts: list[str] = []
    pos = 0
    for match in pattern.finditer(text):
        parts.append(esc(text[pos : match.start()]))
        parts.append(placeholders[match.group(0)])
        pos = match.end()
    parts.append(esc(text[pos:]))
    return "".join(parts)


def youtube_embed(video_id: str) -> str:
    return f"https://www.youtube.com/embed/{esc(video_id)}?rel=0"


def youtube_watch(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={esc(video_id)}"


def grammar_box(b: int) -> str:
    note = GRAMMAR_NOTES[b]
    examples = "\n".join(
        f'      <li><em>{esc(en)}</em> <span class="ja">{esc(ja)}</span></li>'
        for en, ja in note["examples"]  # type: ignore[index]
    )
    return f"""      <div class="grammar-box">
        <span class="g-title">文法ターゲット：{esc(note["title"])}</span>
        <p class="g-desc">{esc(note["desc"])}</p>
        <p class="g-ex-label">例文：</p>
        <ul>
{examples}
        </ul>
      </div>"""


def mode_toolbar() -> str:
    return """      <div class="toolbar" role="group" aria-label="表示モード">
        <button class="btn-mode" data-mode="ipa" type="button" aria-pressed="false">① 発音 (IPA)</button>
        <button class="btn-mode" data-mode="ja" type="button" aria-pressed="false">② 語義 (日本語)</button>
        <button class="btn-mode" data-mode="plain" type="button" aria-pressed="true">③ ルビなし</button>
        <button class="btn-mode" data-mode="en" type="button" aria-pressed="false">④ 英語のみ</button>
        <button class="btn-mode" data-mode="en-ja" type="button" aria-pressed="false">⑤ 英語＋日本語ルビ</button>
        <button class="btn-mode" data-mode="jp-full" type="button" aria-pressed="false">⑥ 日本語訳</button>
        <button class="btn-mode" data-mode="picturebook" type="button" aria-pressed="false">⑦ 絵本</button>
      </div>"""


def picturebook_thumb(b: int, cue_index: int) -> str:
    return f"picturebook-thumbs/B{b:02d}/c{cue_index:03d}.jpg"


def beginner_audio_path(b: int, display_index: int) -> str:
    return f"audio/beginner/L{b}/s{display_index}.mp3"


def line_html(
    b: int,
    display_index: int,
    line: dict,
    bank: dict[str, dict[str, str]],
    new_bases: set[str],
) -> tuple[str, str, str]:
    speaker = esc(line["speaker"])
    speaker_ja = esc(line["speaker_ja"])
    english_en = span_words(line["english"], "we", bank)
    ja = esc(line["japanese"])
    mixed_ja = mixed_japanese_sentence(line, new_bases, bank)
    audio = esc(beginner_audio_path(b, display_index))
    mixed = f'        <p data-audio="{audio}" data-cue="{esc(line["cue_index"])}">({speaker_ja}) {mixed_ja}</p>'
    en = f'        <p data-audio="{audio}" data-cue="{esc(line["cue_index"])}">({speaker}) {english_en}</p>'
    jp = f"        <p>({speaker_ja}) {ja}</p>"
    return mixed, en, jp


def picturebook_card(b: int, display_index: int, line: dict) -> str:
    cue = int(line["cue_index"])
    thumb = picturebook_thumb(b, cue)
    audio = esc(beginner_audio_path(b, display_index))
    speaker = esc(line["speaker"])
    speaker_ja = esc(line["speaker_ja"])
    english = esc(line["english"])
    japanese = esc(line["japanese"])
    return f"""        <article class="picture-card" data-cue="{cue}">
          <div class="picture-frame"><img data-thumb="{esc(thumb)}" alt="B{b} cue {cue} thumbnail" loading="lazy"></div>
          <button class="picture-line" type="button" data-audio="{audio}" data-cue="{cue}">
            <span class="picture-speaker">{speaker}</span>
            <span class="picture-english">{english}</span>
            <span class="picture-japanese">{speaker_ja}: {japanese}</span>
          </button>
        </article>"""


def lesson_section(lesson: dict, youtube_by_code: dict, bank: dict[str, dict[str, str]]) -> str:
    b = int(lesson["b"])
    yt = youtube_by_code[f"B{b}"]
    mixed_rows, en_rows, jp_rows, picture_rows = [], [], [], []
    new_bases = set(lesson.get("new_bases", []))
    for display_index, line in enumerate(lesson.get("display_lines", lesson["lines"]), start=1):
        mixed, en, jp = line_html(b, display_index, line, bank, new_bases)
        mixed_rows.append(mixed)
        en_rows.append(en)
        jp_rows.append(jp)
        picture_rows.append(picturebook_card(b, display_index, line))
    return f"""    <section class="lesson hidden b-series-lesson" data-lesson="{b}" data-funnics-b="{b}" data-lesson-id="{esc(lesson["lesson_id"])}" data-video-id="{esc(yt["video_id"])}" data-youtube-url="{esc(yt["url"])}">
      <h2>Lesson B{b} — {esc(lesson["title"])}</h2>
{grammar_box(b)}

{mode_toolbar()}

      <div class="jp-body">
{chr(10).join(mixed_rows)}
      </div>

      <div class="en-body hidden">
{chr(10).join(en_rows)}
      </div>

      <div class="jp-full hidden">
{chr(10).join(jp_rows)}
      </div>

      <div class="picturebook-body hidden" aria-label="絵本モード">
{chr(10).join(picture_rows)}
      </div>
    </section>"""


def summary_section(lessons: list[dict], youtube_data: dict) -> str:
    joined = youtube_data["joined"]
    youtube_by_code = {item["code"]: item for item in youtube_data["lessons"]}
    tacos_mv = youtube_data.get("tacos_mv", {})
    tacos_rows: list[str] = []
    for key, label in (("ja", "日本語版MV"), ("en", "English Ver. MV")):
        item = tacos_mv.get(key, {})
        if item.get("url"):
            tacos_rows.append(
                f'          <li><a class="summary-extra-link" href="{esc(item["url"])}" target="_blank" rel="noopener">'
                f'<span class="summary-extra-label">{esc(label)}</span>'
                f'<strong>{esc(item.get("title", "¡Viva! Tacos"))}</strong>'
                f'<span class="summary-open">動画を見る</span>'
                f"</a></li>"
            )
    tacos_block = ""
    if tacos_rows:
        tacos_block = f"""
      <section class="summary-block summary-extra-links" aria-labelledby="b-summary-tacos-mv">
        <h3 id="b-summary-tacos-mv">関連MV：¡Viva! タコス 手のひらの宇宙</h3>
        <p class="summary-extra-note">キャラクターたちが活躍するミュージックビデオです。日本語版と英語版を見比べながら、リズムに乗って言葉の違いを楽しめます。</p>
        <ul class="summary-extra-list">
{chr(10).join(tacos_rows)}
        </ul>
      </section>
"""
    summary_rows: list[str] = []
    for lesson in lessons:
        b = int(lesson["b"])
        yt = youtube_by_code[f"B{b}"]
        summary_rows.append(
            f'          <li><a class="summary-combined-link" href="{esc(yt["url"])}" target="_blank" rel="noopener">'
            f'<span class="summary-code">B{b}</span>'
            f'<strong class="summary-title">{esc(lesson["title"])}</strong>'
            f'<span class="summary-grammar">{esc(lesson["grammar_target"])}</span>'
            f'<span class="summary-open">動画を見る</span>'
            f"</a></li>"
        )
    combined_rows = "\n".join(summary_rows)
    return f"""    <section class="lesson hidden b-series-lesson b-series-summary" data-lesson="21" data-funnics-b="21" data-summary="true" data-video-id="{esc(joined["video_id"])}" data-video-label="B1〜B20 一気見" data-youtube-url="{esc(joined["url"])}">
      <h2>Lesson B21 — Bシリーズまとめ</h2>
      <div class="summary-lead">
        <p>B1〜B20で練習した文法事項と各レッスン動画を、1つの一覧にまとめています。</p>
        <a class="summary-primary-link" href="{esc(joined["url"])}" target="_blank" rel="noopener">B1〜B20 一気見動画を開く</a>
      </div>
{tacos_block}

      <section class="summary-block" aria-labelledby="b-summary-combined">
        <h3 id="b-summary-combined">B1〜B20 文法事項・YouTubeリンク</h3>
        <ol class="summary-combined-list">
{combined_rows}
        </ol>
      </section>
    </section>"""


def shared_controls(joined_video_id: str) -> str:
    return f"""      <div class="toolbar b-series-hide-on-summary" role="group" aria-label="表示モード（下）">
        <button class="btn-mode" data-mode="ipa" type="button" aria-pressed="false">① 発音 (IPA)</button>
        <button class="btn-mode" data-mode="ja" type="button" aria-pressed="false">② 語義 (日本語)</button>
        <button class="btn-mode" data-mode="plain" type="button" aria-pressed="true">③ ルビなし</button>
        <button class="btn-mode" data-mode="en" type="button" aria-pressed="false">④ 英語のみ</button>
        <button class="btn-mode" data-mode="en-ja" type="button" aria-pressed="false">⑤ 英語＋日本語ルビ</button>
        <button class="btn-mode" data-mode="jp-full" type="button" aria-pressed="false">⑥ 日本語訳</button>
        <button class="btn-mode" data-mode="picturebook" type="button" aria-pressed="false">⑦ 絵本</button>
      </div>
      <div class="toolbar b-series-hide-on-summary" role="group" aria-label="読み上げ（下）">
        <label>🔊 読み上げ:</label>
        <button class="btn-tts-passage" type="button">▶ 例文</button>
        <button class="btn-tts-stop" type="button">■ 停止</button>
        <label>速度:</label>
        <select class="sel-tts-rate">
          <option value="0.7">0.7x</option>
          <option value="0.85" selected>0.85x</option>
          <option value="1.0">1.0x</option>
          <option value="1.2">1.2x</option>
        </select>
        <label>音声:</label>
        <select class="sel-tts-voice" title="読み上げに使う音声を選択"></select>
      </div>

      <div class="yt-section b-series-yt-section" data-yt-book="beginner">
        <div class="yt-label">🎵 歌で覚える英文動画（YouTube）</div>
        <div class="yt-videos"></div>
        <div class="b-series-joined-link">
          <a class="yt-watch-link" href="{youtube_watch(joined_video_id)}" target="_blank" rel="noopener">B1〜B20 一気見を開く</a>
        </div>
      </div>

      <div class="vocab-quiz b-series-hide-on-summary" data-quiz-book="beginner">
        <h2 class="quiz-heading">📝 単語確認テスト（このレッスンの新出語）</h2>
        <div class="vocab-quiz-content" id="quiz-beginner"></div>
      </div>

      <div class="shadowing b-series-hide-on-summary" data-sh-book="beginner" data-b-series-shadowing>
        <h2 class="sh-heading">🎤 シャドウイング練習</h2>
        <div class="sh-intro">
          <p>英文を1文ずつ聞いて、声に出して真似してみましょう。聞こえた単語を確認しながら次の文へ進みます。</p>
          <button class="btn-sh-start" type="button">▶ シャドウイング練習を始める</button>
        </div>
        <div class="sh-active hidden">
          <div class="sh-progress">文 <span class="sh-index">1</span> / <span class="sh-total">0</span></div>
          <div class="sh-target"></div>
          <div class="sh-feedback"></div>
          <div class="sh-controls">
            <div class="sh-status sh-status-idle">認識停止中</div>
            <button class="btn-sh-replay" type="button">🔊 もう一度再生</button>
            <button class="btn-sh-stop" type="button">■ 停止</button>
            <button class="btn-sh-skip" type="button">スキップ →</button>
            <button class="btn-sh-end" type="button">✕ 終了</button>
          </div>
        </div>
        <div class="sh-done hidden">
          <p class="sh-done-msg">🎉 シャドウイング練習完了！</p>
          <div style="text-align:center;"><button class="btn-sh-retry" type="button">🔄 もう一度挑戦する</button></div>
        </div>
      </div>
      <p class="sh-note b-series-hide-on-summary">※ 固有名詞や数詞などがうまく認識できない時には「スキップ」をお願いします。</p>

      <div class="next-lesson-wrap b-series-hide-on-summary">
        <button class="btn-next-lesson" type="button" data-book="beginner">次のレッスンへ →</button>
      </div>

      <h2 class="b-series-hide-on-summary">このレッスンの新出単語（本文で赤字）</h2>
      <div class="vocab-current b-series-hide-on-summary" id="vocab-beginner"></div>

      <h2 class="cumulative-heading b-series-hide-on-summary">このレッスンまでに累計で出た単語</h2>
      <div class="vocab-cumulative b-series-hide-on-summary" id="vocab-cum-beginner"></div>"""


def lesson_option(lesson: dict) -> str:
    b = int(lesson["b"])
    return f'          <option value="{b}">Lesson B{b} — {esc(lesson["title"])} / {esc(lesson["grammar_target"])}</option>'


def summary_option() -> str:
    return '          <option value="21">Lesson B21 — Bシリーズまとめ / 文法・動画リンク</option>'


def build_fragment(lessons: list[dict], youtube_data: dict, bank: dict[str, dict[str, str]]) -> str:
    youtube_by_code = {item["code"]: item for item in youtube_data["lessons"]}
    options = "\n".join([*(lesson_option(lesson) for lesson in lessons), summary_option()])
    sections = "\n\n".join([*(lesson_section(lesson, youtube_by_code, bank) for lesson in lessons), summary_section(lessons, youtube_data)])
    joined = youtube_data["joined"]["video_id"]
    return f"""    <div class="book hidden b-series-book" id="book-beginner" data-book="beginner" data-b-series>
      <h2 class="book-title">📒 入門英語（Funnics Island） — B1-B20</h2>
      <p class="book-about">トムが Funnics Island を進みながら、中1英語の基本表現を歌と会話で練習します。日本語混じり文、英語のみ、日本語訳、文法説明、シャドウイング、単語チェックを既存の教材構造に合わせてまとめています。</p>
      <div class="toolbar" role="group" aria-label="レッスン選択">
        <label for="sel-beginner">レッスン:</label>
        <select id="sel-beginner" class="lesson-select" data-book="beginner">
{options}
        </select>
      </div>

{sections}

{shared_controls(joined)}
    </div>"""


CSS = """/* Funnics Island B1-B20 index-like drop-in styles. */
.b-series-book .book-about {
  margin: -6px 0 16px;
  color: var(--fg-soft, #374151);
}
.b-series-book .lesson p[data-audio] {
  position: relative;
}
.b-series-book .lesson p[data-audio].is-playing {
  background: #f0fdf4;
  outline: 1px solid #86efac;
  border-radius: 6px;
  padding: 2px 5px;
}
.b-series-book .yt-section {
  display: block;
}
.b-series-joined-link {
  text-align: center;
  margin-top: 8px;
}
.b-series-book .vocab-current table,
.b-series-book .vocab-cumulative table {
  table-layout: fixed;
}
.b-series-book .vocab-current td:first-child,
.b-series-book .vocab-cumulative td:first-child {
  font-weight: 700;
}
.b-series-book .new-word {
  color: var(--new, #dc2626);
  font-weight: 700;
}
.b-series-book .picturebook-body {
  display: grid;
  gap: 14px;
  margin: 14px 0 18px;
}
.b-series-book .picture-card {
  display: grid;
  grid-template-columns: minmax(170px, 240px) minmax(0, 1fr);
  gap: 14px;
  align-items: stretch;
  padding: 10px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: var(--shadow-sm, 0 1px 2px rgba(0,0,0,.04));
}
.b-series-book .picture-frame {
  position: relative;
  overflow: hidden;
  border-radius: 6px;
  background: #0f172a;
  aspect-ratio: 16 / 9;
}
.b-series-book .picture-frame img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.b-series-book .picture-line {
  display: grid;
  gap: 6px;
  align-content: center;
  width: 100%;
  border: 1px solid #dbeafe;
  border-radius: 8px;
  background: #f8fafc;
  color: var(--fg, #111827);
  padding: 12px 14px;
  font-family: inherit;
  text-align: left;
  cursor: pointer;
}
.b-series-book .picture-line:hover {
  border-color: #60a5fa;
  background: #eff6ff;
}
.b-series-book .picture-line.is-playing {
  border-color: #22c55e;
  background: #f0fdf4;
  box-shadow: 0 0 0 3px rgba(34,197,94,.18);
}
.b-series-book .picture-speaker {
  font-size: .82rem;
  font-weight: 800;
  color: #0369a1;
}
.b-series-book .picture-english {
  font-size: 1.02rem;
  font-weight: 800;
  line-height: 1.45;
}
.b-series-book .picture-japanese {
  color: var(--fg-soft, #374151);
  line-height: 1.55;
}
.b-series-summary .summary-lead {
  margin: 10px 0 16px;
  padding: 14px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}
.b-series-summary .summary-lead p {
  margin: 0 0 10px;
}
.b-series-summary .summary-primary-link,
.b-series-summary .summary-combined-link {
  text-decoration: none;
}
.b-series-summary .summary-primary-link {
  display: inline-block;
  padding: 8px 14px;
  background: #fff;
  border: 2px solid #ef4444;
  border-radius: 6px;
  color: #991b1b;
  font-weight: 800;
}
.b-series-summary .summary-block h3 {
  margin: 0 0 10px;
  font-size: 1rem;
}
.b-series-summary .summary-combined-list {
  display: grid;
  gap: 6px;
  margin: 0;
  padding: 0;
  list-style: none;
}
.b-series-summary .summary-extra-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 8px;
  margin: 0;
  padding: 0;
  list-style: none;
}
.b-series-summary .summary-extra-note {
  margin: 0 0 10px;
  color: #4b5563;
  line-height: 1.65;
}
.b-series-summary .summary-extra-link {
  display: grid;
  grid-template-columns: 92px minmax(0, 1fr) auto;
  gap: 10px;
  align-items: center;
  padding: 10px 12px;
  border: 1px solid #fed7aa;
  border-radius: 8px;
  background: #fff7ed;
  color: var(--fg, #111827);
}
.b-series-summary .summary-extra-label {
  font-weight: 800;
  color: #c2410c;
}
.b-series-summary .summary-combined-link {
  display: grid;
  grid-template-columns: 48px minmax(120px, 1.1fr) minmax(160px, 1.4fr) auto;
  gap: 10px;
  align-items: center;
  padding: 8px 10px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #fff;
  color: var(--fg, #111827);
}
.b-series-summary .summary-code {
  font-weight: 800;
  color: #0369a1;
}
.b-series-summary .summary-title {
  color: var(--fg, #111827);
}
.b-series-summary .summary-grammar {
  color: var(--fg-soft, #374151);
}
.b-series-summary .summary-open {
  justify-self: end;
  padding: 4px 9px;
  border: 1px solid #bae6fd;
  border-radius: 999px;
  color: #0369a1;
  font-weight: 700;
  font-size: .82rem;
  background: #f0f9ff;
  white-space: nowrap;
}
.b-series-summary .summary-combined-link:hover {
  border-color: #38bdf8;
}
@media (max-width: 760px) {
  .b-series-book .picture-card {
    grid-template-columns: 1fr;
  }
  .b-series-summary .summary-combined-link {
    grid-template-columns: 42px minmax(0, 1fr);
  }
  .b-series-summary .summary-grammar,
  .b-series-summary .summary-open {
    grid-column: 2;
    justify-self: start;
  }
}
"""


JS = r"""// Funnics Island B1-B20 behavior for the index-like drop-in.
(function(){
  const ROOT_SELECTOR = '[data-b-series]';
  const KEY_MODE = 'displayMode_unified';
  const POS_MAP = {
    adj:'形容詞', adv:'副詞', aux:'助動詞', conj:'接続詞', det:'限定詞',
    noun:'名詞', num:'数詞', phrase:'フレーズ', prep:'前置詞', pron:'代名詞', verb:'動詞', interj:'間投詞'
  };
  let currentAudio = null;
  let currentSpeech = null;
  let activeLine = null;
  let queue = [];
  let queueIndex = 0;
  let voicesCache = [];
  const shadowState = new WeakMap();
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  const USE_RECORDED_BEGINNER_AUDIO = true;
  const RECOGNITION_STOP_TIMEOUT_MS = 1000;
  const RECOGNITION_SETTLE_MS = 120;
  const PRELISTEN_MIN_WORDS = 4;
  const EARLY_RESULT_GRACE_MS = 320;
  const MOBILE_RECOGNITION_START_DELAY_MS = 650;
  const SH_PASS_THRESHOLDS = [0.7, 0.55, 0.4, 0.3, 0.2];

  function root(){ return document.querySelector(ROOT_SELECTOR); }
  function sharedShadowing(){
    return window.FunnicsPractice && window.FunnicsPractice.shadowing;
  }
  function sharedQuiz(){
    return window.FunnicsPractice && window.FunnicsPractice.quiz;
  }
  function requestPracticeEvent(name, detail){
    if(typeof CustomEvent !== 'function') return false;
    const event = new CustomEvent(name, { detail });
    document.dispatchEvent(event);
    return !!event.detail && event.detail.handled === true;
  }
  function requestSharedQuiz(book, lesson){
    return requestPracticeEvent('funnics:quiz', { book, lesson: String(lesson) });
  }
  function requestSharedShadow(action, book, userGesture){
    return requestPracticeEvent('funnics:shadowing', { action, book, userGesture: !!userGesture });
  }
  function requestSharedYoutube(book, lesson){
    return requestPracticeEvent('funnics:youtube', { book, lesson: String(lesson) });
  }
  function lessons(){
    const r = root();
    return r ? Array.from(r.querySelectorAll(':scope > section.lesson')).sort((a,b)=>Number(a.dataset.lesson)-Number(b.dataset.lesson)) : [];
  }
  function currentLesson(){
    const r = root();
    return r ? r.querySelector(':scope > section.lesson:not(.hidden)') : null;
  }
  function makeRuby(text, rt){
    const ruby = document.createElement('ruby');
    ruby.appendChild(document.createTextNode(text));
    const rtEl = document.createElement('rt');
    rtEl.appendChild(document.createTextNode(rt));
    ruby.appendChild(rtEl);
    return ruby;
  }
  function saveWordDisplays(){
    const r = root();
    if(!r) return;
    r.querySelectorAll('.w, .we').forEach(el => {
      const text = el.textContent.trim();
      if(!el.getAttribute('data-base-saved')) el.setAttribute('data-base-saved', el.getAttribute('data-base') || text.toLowerCase());
      if(!el.getAttribute('data-display')) el.setAttribute('data-display', text);
    });
  }
  function markNewWords(){
    const seen = new Set();
    lessons().forEach(lesson => {
      const words = new Set();
      lesson.querySelectorAll('.w, .we').forEach(el => {
        const base = (el.getAttribute('data-base-saved') || el.getAttribute('data-base') || '').toLowerCase();
        if(base) words.add(base);
      });
      const newOnes = new Set();
      words.forEach(w => { if(!seen.has(w)) newOnes.add(w); });
      lesson.querySelectorAll('.w, .we').forEach(el => {
        const base = (el.getAttribute('data-base-saved') || el.getAttribute('data-base') || '').toLowerCase();
        el.classList.toggle('new-word', newOnes.has(base));
      });
      words.forEach(w => seen.add(w));
    });
  }
  function applyModeToLesson(mode, lesson){
    if(!lesson) return;
    lesson.querySelectorAll('.w').forEach(el => {
      const display = el.getAttribute('data-display') || el.textContent;
      const ipa = el.getAttribute('data-ipa') || '';
      const ja = el.getAttribute('data-ja') || '';
      el.replaceChildren(document.createTextNode(display));
      if(mode === 'ipa' && ipa) el.replaceChildren(makeRuby(display, ipa));
      else if(mode === 'ja' && ja) el.replaceChildren(makeRuby(display, ja));
    });
    lesson.querySelectorAll('.we').forEach(el => {
      const display = el.getAttribute('data-display') || el.textContent;
      const ja = el.getAttribute('data-ja') || '';
      el.replaceChildren(document.createTextNode(display));
      if(mode === 'en-ja' && ja) el.replaceChildren(makeRuby(display, ja));
    });
  }
  function applyMode(mode){
    const r = root();
    if(!r) return;
    localStorage.setItem(KEY_MODE, mode);
    r.querySelectorAll('.btn-mode').forEach(btn => btn.setAttribute('aria-pressed', String(btn.dataset.mode === mode)));
    r.querySelectorAll(':scope > section.lesson').forEach(lesson => {
      const jp = lesson.querySelector('.jp-body');
      const en = lesson.querySelector('.en-body');
      const jpf = lesson.querySelector('.jp-full');
      const pic = lesson.querySelector('.picturebook-body');
      if(mode === 'jp-full'){
        jp && jp.classList.add('hidden');
        en && en.classList.add('hidden');
        jpf && jpf.classList.remove('hidden');
        pic && pic.classList.add('hidden');
      } else if(mode === 'picturebook'){
        jp && jp.classList.add('hidden');
        en && en.classList.add('hidden');
        jpf && jpf.classList.add('hidden');
        pic && pic.classList.remove('hidden');
      } else if(mode === 'en' || mode === 'en-ja'){
        jp && jp.classList.add('hidden');
        en && en.classList.remove('hidden');
        jpf && jpf.classList.add('hidden');
        pic && pic.classList.add('hidden');
      } else {
        jp && jp.classList.remove('hidden');
        en && en.classList.add('hidden');
        jpf && jpf.classList.add('hidden');
        pic && pic.classList.add('hidden');
      }
    });
    applyModeToLesson(mode, currentLesson());
    hydratePicturebookImages(currentLesson());
  }
  function stopAudio(options){
    const keepQueue = options && options.keepQueue;
    if(currentAudio){
      const audio = currentAudio;
      currentAudio = null;
      audio.onended = null;
      audio.onerror = null;
      audio.onloadedmetadata = null;
      audio.ontimeupdate = null;
      audio.pause();
      audio.removeAttribute('src');
      audio.load();
    }
    if(currentSpeech){
      currentSpeech.onend = null;
      currentSpeech.onerror = null;
      currentSpeech = null;
    }
    if(window.speechSynthesis) window.speechSynthesis.cancel();
    if(activeLine) activeLine.classList.remove('is-playing');
    activeLine = null;
    if(!keepQueue){
      queue = [];
      queueIndex = 0;
    }
  }
  function rate(){
    const r = root();
    const sel = r && r.querySelector('.sel-tts-rate');
    return sel ? parseFloat(sel.value) || 0.85 : 0.85;
  }
  function resolveAudioUrl(url){
    if(!url) return '';
    if(/^(?:https?:|file:|data:|blob:|\/)/.test(url)) return url;
    if(document.body && document.body.dataset.bSeriesPreview === 'true' && url.startsWith('audio/')){
      return '../' + url;
    }
    return url;
  }
  function resolveThumbUrl(url){
    if(!url) return '';
    if(/^(?:https?:|file:|data:|blob:|\/)/.test(url)) return url;
    if(document.body && document.body.dataset.bSeriesPreview === 'true') return url;
    return 'funnics-beginner-assets/' + url;
  }
  function hydratePicturebookImages(scope){
    if(!scope) return;
    scope.querySelectorAll('img[data-thumb]').forEach(img => {
      if(!img.getAttribute('src')) img.setAttribute('src', resolveThumbUrl(img.getAttribute('data-thumb')));
    });
  }
  function textForPlayback(line){
    if(!line) return '';
    const pictureEnglish = line.querySelector && line.querySelector('.picture-english');
    if(pictureEnglish) return pictureEnglish.textContent.replace(/\s+/g, ' ').trim();
    return textFromLine(line);
  }
  function clearPlayingLine(line){
    if(line) line.classList.remove('is-playing');
    activeLine = null;
  }
  function speakElement(line, onend, options){
    const text = textForPlayback(line);
    stopAudio({ keepQueue: options && options.keepQueue });
    if(line){
      activeLine = line;
      line.classList.add('is-playing');
    }
    if(!window.speechSynthesis || !text){
      clearPlayingLine(line);
      if(onend) setTimeout(onend, 0);
      return;
    }
    const u = new SpeechSynthesisUtterance(text);
    u.lang = 'en-US';
    u.rate = rate();
    const r = root();
    const sel = r && r.querySelector('.sel-tts-voice');
    if(sel && sel.value){
      const v = voicesCache.find(x => ((x.name || '') + '|' + (x.lang || '')) === sel.value);
      if(v){ u.voice = v; u.lang = v.lang; }
    }
    let done = false;
    const finish = () => {
      if(done) return;
      done = true;
      clearPlayingLine(line);
      currentSpeech = null;
      if(onend) onend();
    };
    u.onend = finish;
    u.onerror = finish;
    currentSpeech = u;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(u);
  }
  function playAudio(url, line, onend, options){
    if(!USE_RECORDED_BEGINNER_AUDIO || !url){
      speakElement(line, onend, options);
      return;
    }
    stopAudio({ keepQueue: options && options.keepQueue });
    if(line){
      activeLine = line;
      line.classList.add('is-playing');
    }
    const audio = new Audio(resolveAudioUrl(url));
    audio.playbackRate = rate();
    let done = false;
    let almostEndFired = false;
    const fireAlmostEnd = () => {
      if(almostEndFired || done) return;
      almostEndFired = true;
      if(options && options.onAlmostEnd) options.onAlmostEnd(audio);
    };
    const checkAlmostEnd = () => {
      if(!options || !options.onAlmostEnd || !Number.isFinite(audio.duration)) return;
      const lead = options.almostEndSeconds == null ? 0.55 : options.almostEndSeconds;
      if(audio.duration - audio.currentTime <= lead) fireAlmostEnd();
    };
    const finish = (ok) => {
      if(done || currentAudio !== audio) return;
      done = true;
      if(line) line.classList.remove('is-playing');
      activeLine = null;
      currentAudio = null;
      audio.onended = null;
      audio.onerror = null;
      audio.onloadedmetadata = null;
      audio.ontimeupdate = null;
      if(ok){
        if(onend) onend();
      } else {
        speakElement(line, onend, options);
      }
    };
    audio.onloadedmetadata = checkAlmostEnd;
    audio.ontimeupdate = checkAlmostEnd;
    audio.onended = () => finish(true);
    audio.onerror = () => finish(false);
    currentAudio = audio;
    audio.play().catch(() => finish(false));
  }
  function playQueue(lines){
    stopAudio();
    queue = lines.filter(Boolean);
    queueIndex = 0;
    function next(){
      if(queueIndex >= queue.length){ stopAudio(); return; }
      const line = queue[queueIndex++];
      const url = line.getAttribute('data-audio');
      playAudio(url, line, next, { keepQueue: true });
    }
    next();
  }
  function populateVoices(){
    voicesCache = window.speechSynthesis ? window.speechSynthesis.getVoices() : [];
    const sorted = voicesCache.filter(v => (v.lang || '').toLowerCase().startsWith('en'));
    const r = root();
    if(!r) return;
    r.querySelectorAll('.sel-tts-voice').forEach(sel => {
      const prev = sel.value;
      sel.innerHTML = '';
      sorted.forEach(v => {
        const opt = document.createElement('option');
        opt.value = (v.name || '') + '|' + (v.lang || '');
        opt.textContent = `${v.name} [${v.lang}]`;
        sel.appendChild(opt);
      });
      if(prev) sel.value = prev;
    });
  }
  function speakWord(text){
    stopAudio();
    if(!window.speechSynthesis || !text) return;
    const u = new SpeechSynthesisUtterance(text);
    u.lang = 'en-US';
    u.rate = rate();
    const r = root();
    const sel = r && r.querySelector('.sel-tts-voice');
    if(sel && sel.value){
      const v = voicesCache.find(x => ((x.name || '') + '|' + (x.lang || '')) === sel.value);
      if(v){ u.voice = v; u.lang = v.lang; }
    }
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(u);
  }
  function renderVideo(){
    const r = root();
    const lesson = currentLesson();
    if(r && lesson && requestSharedYoutube(r, lesson.dataset.lesson)) return;
    const sec = r && r.querySelector('.yt-section');
    const container = sec && sec.querySelector('.yt-videos');
    if(!lesson || !container) return;
    const videoId = lesson.dataset.videoId;
    const label = lesson.dataset.videoLabel || ('Lesson B' + lesson.dataset.lesson);
    container.innerHTML = '';
    if(!videoId){ sec.hidden = true; return; }
    sec.hidden = false;
    container.innerHTML =
      '<div class="yt-video-item">' +
        '<span class="yt-video-label">' + label + '</span>' +
        '<div class="yt-embed-wrap"><iframe loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen src="https://www.youtube.com/embed/' + encodeURIComponent(videoId) + '?rel=0"></iframe></div>' +
        '<div style="text-align:center;"><a class="yt-watch-link" href="https://www.youtube.com/watch?v=' + encodeURIComponent(videoId) + '" target="_blank" rel="noopener">▶ YouTube で開く</a></div>' +
      '</div>';
  }
  function renderVocab(){
    const r = root();
    const lesson = currentLesson();
    if(!r || !lesson) return;
    const current = new Map();
    lesson.querySelectorAll('.jp-body .w').forEach(el => {
      const base = (el.getAttribute('data-base-saved') || el.getAttribute('data-base') || '').toLowerCase();
      if(!base || current.has(base)) return;
      current.set(base, {
        base,
        ipa: el.getAttribute('data-ipa') || '',
        ja: el.getAttribute('data-ja') || '',
        pos: POS_MAP[el.getAttribute('data-pos') || ''] || '',
        isNew: el.classList.contains('new-word')
      });
    });
    const cumulative = new Map();
    for(const l of lessons()){
      l.querySelectorAll('.jp-body .w').forEach(el => {
        const base = (el.getAttribute('data-base-saved') || el.getAttribute('data-base') || '').toLowerCase();
        if(!base || cumulative.has(base)) return;
        cumulative.set(base, {
          base,
          ipa: el.getAttribute('data-ipa') || '',
          ja: el.getAttribute('data-ja') || '',
          pos: POS_MAP[el.getAttribute('data-pos') || ''] || '',
          isNew: l === lesson && el.classList.contains('new-word')
        });
      });
      if(l === lesson) break;
    }
    function table(rows){
      const t = document.createElement('table');
      t.innerHTML = '<thead><tr><th>Word</th><th>IPA</th><th>日本語</th><th>品詞</th><th>区分</th></tr></thead>';
      const tb = document.createElement('tbody');
      rows.sort((a,b)=>a.base.localeCompare(b.base)).forEach(row => {
        const tr = document.createElement('tr');
        if(row.isNew) tr.classList.add('new-row');
        tr.classList.add('clickable-word');
        tr.innerHTML = '<td>' + row.base + '</td><td>' + row.ipa + '</td><td>' + row.ja + '</td><td>' + row.pos + '</td><td>' + (row.isNew ? '新出' : '既出') + '</td>';
        tr.addEventListener('click', () => speakWord(row.base));
        tb.appendChild(tr);
      });
      t.appendChild(tb);
      return t;
    }
    const vc = r.querySelector('.vocab-current');
    const cum = r.querySelector('.vocab-cumulative');
    if(vc) vc.replaceChildren(table(Array.from(current.values())));
    if(cum) cum.replaceChildren(table(Array.from(cumulative.values())));
  }
  function toggleSummaryControls(){
    const r = root();
    const lesson = currentLesson();
    if(!r || !lesson) return;
    const isSummary = lesson.dataset.summary === 'true';
    r.querySelectorAll('.b-series-hide-on-summary').forEach(el => {
      el.classList.toggle('hidden', isSummary);
    });
  }
  function showLesson(id){
    const r = root();
    if(!r) return;
    stopAudio();
    lessons().forEach(l => l.classList.toggle('hidden', l.dataset.lesson !== String(id)));
    const sel = r.querySelector('.lesson-select');
    if(sel && sel.value !== String(id)) sel.value = String(id);
    applyMode(localStorage.getItem(KEY_MODE) || 'plain');
    renderVideo();
    renderVocab();
    if(!requestSharedQuiz(r, id) && sharedQuiz()) sharedQuiz().build(r, String(id));
    toggleSummaryControls();
    resetShadowing();
  }
  function textFromLine(line){
    if(!line) return '';
    const clone = line.cloneNode(true);
    clone.querySelectorAll('rt').forEach(rt => rt.remove());
    return clone.textContent.replace(/^\([^)]+\)\s*/, '').replace(/\s+/g, ' ').trim();
  }
  function shadowLines(){
    const lesson = currentLesson();
    return lesson ? Array.from(lesson.querySelectorAll('.en-body p')) : [];
  }
  function stopShadowRecognition(sh, opts){
    const s = sh && shadowState.get(sh);
    if(!s) return Promise.resolve();
    if(s.stopRecognitionPromise) return s.stopRecognitionPromise;
    if(!s.recognition){
      if(!opts || !opts.silent) setShadowStatus(sh, '認識停止中', 'sh-status-idle');
      return Promise.resolve();
    }
    const rec = s.recognition;
    s.recognition = null;
    let done = false;
    let resolveStop;
    const promise = new Promise(resolve => { resolveStop = resolve; });
    s.stopRecognitionPromise = promise;
    const finish = () => {
      if(done) return;
      done = true;
      rec.onresult = null;
      rec.onerror = null;
      rec.onspeechend = null;
      rec.onspeechstart = null;
      rec.onaudioend = null;
      rec.onaudiostart = null;
      rec.onstart = null;
      rec.onend = null;
      if(shadowState.get(sh) === s && s.stopRecognitionPromise === promise) s.stopRecognitionPromise = null;
      if(!opts || !opts.silent) setShadowStatus(sh, '認識停止中', 'sh-status-idle');
      resolveStop();
    };
    rec.onend = finish;
    rec.onerror = finish;
    rec.onresult = null;
    rec.onspeechend = null;
    rec.onspeechstart = null;
    rec.onaudioend = null;
    rec.onaudiostart = null;
    rec.onstart = null;
    try { rec.abort(); } catch(e){ finish(); }
    setTimeout(finish, RECOGNITION_STOP_TIMEOUT_MS);
    return promise;
  }
  function resetShadowing(){
    const r = root();
    if(!r) return;
    if(requestSharedShadow('reset', r)){
      stopAudio();
      return;
    }
    if(sharedShadowing()){
      stopAudio();
      sharedShadowing().reset(r);
      return;
    }
    const sh = r.querySelector('.shadowing');
    if(!sh) return;
    const s = shadowState.get(sh);
    stopAudio();
    if(s && s.recognition) stopShadowRecognition(sh, { silent: true });
    releaseShadowMic(s);
    shadowState.delete(sh);
    sh.querySelector('.sh-intro')?.classList.remove('hidden');
    sh.querySelector('.sh-active')?.classList.add('hidden');
    sh.querySelector('.sh-done')?.classList.add('hidden');
    const fb = sh.querySelector('.sh-feedback');
    if(fb){ fb.textContent = ''; fb.className = 'sh-feedback'; }
  }
  const CONTRACTIONS = {
    "i'm":["i","am"],"you're":["you","are"],"he's":["he","is","has"],"she's":["she","is","has"],"it's":["it","is","has"],
    "we're":["we","are"],"they're":["they","are"],"that's":["that","is","has"],"what's":["what","is","has"],"who's":["who","is","has"],
    "can't":["can","not","cannot"],"don't":["do","not"],"doesn't":["does","not"],"isn't":["is","not"],"aren't":["are","not"],
    "won't":["will","not"],"couldn't":["could","not"],"wouldn't":["would","not"],"shouldn't":["should","not"],"let's":["let","us"]
  };
  const ALWAYS_MATCHED_NAMES = new Set(['tom','teacher','tacos','runner','rabbit','engineer','egg','pilot','panda','singer','snake','baker','bear','funnics']);
  function normWord(w){ return String(w).toLowerCase().replace(/[.,!?;:"“”'’()]/g, ''); }
  function norm(w){ return normWord(w); }
  function isLikelyProperNoun(word, index, allWords){
    const clean = normWord(word);
    if(ALWAYS_MATCHED_NAMES.has(clean)) return true;
    if(index === 0) return false;
    const prev = allWords[index - 1] || '';
    if(/[.!?]$/.test(prev)) return false;
    return /^[A-Z][a-z]+/.test(word);
  }
  function levenshtein(a, b){
    if(a === b) return 0;
    if(!a.length) return b.length;
    if(!b.length) return a.length;
    const dp = Array.from({length: b.length + 1}, (_, i) => i);
    for(let i = 1; i <= a.length; i++){
      let prev = dp[0];
      dp[0] = i;
      for(let j = 1; j <= b.length; j++){
        const tmp = dp[j];
        dp[j] = a[i - 1] === b[j - 1] ? prev : 1 + Math.min(prev, dp[j - 1], dp[j]);
        prev = tmp;
      }
    }
    return dp[b.length];
  }
  function fuzzyMatch(targetWord, recognizedSet){
    const t = normWord(targetWord);
    if(!t || t.length < 5) return false;
    const thr = Math.min(2, Math.floor(t.length / 4));
    for(const r of recognizedSet){
      if(!r || Math.abs(r.length - t.length) > thr) continue;
      if(levenshtein(t, r) <= thr) return true;
    }
    return false;
  }
  function createMatchSet(words){
    const s = new Set();
    for(const w of words){
      const n = normWord(w);
      if(!n) continue;
      s.add(n);
      s.add(n.replace(/'/g, ''));
      s.add(n.replace(/'s$/, ''));
      if(CONTRACTIONS[n]) CONTRACTIONS[n].forEach(x => s.add(x));
    }
    return s;
  }
  function wordMatched(target, set){
    const n = normWord(target);
    if(!n) return false;
    if(set.has(n) || set.has(n.replace(/'/g, '')) || set.has(n.replace(/'s$/, ''))) return true;
    if(CONTRACTIONS[n] && CONTRACTIONS[n].slice(0, 2).every(x => set.has(x))) return true;
    return fuzzyMatch(target, set);
  }
  function recognitionDelay(ms){ return new Promise(resolve => setTimeout(resolve, ms)); }
  function isMobileShadowDevice(){
    const ua = navigator.userAgent || '';
    return /Android|iPhone|iPad|iPod|Mobile|CriOS|FxiOS|EdgiOS/i.test(ua) ||
      (/Macintosh/i.test(ua) && navigator.maxTouchPoints > 1);
  }
  function shouldPrelistenShadow(){
    return !isMobileShadowDevice();
  }
  function shadowRecognitionStartDelay(){
    return shouldPrelistenShadow() ? EARLY_RESULT_GRACE_MS : MOBILE_RECOGNITION_START_DELAY_MS;
  }
  function canAcceptRecognitionResult(s){
    return !!s.acceptRecognitionResults && performance.now() >= (s.acceptResultsAfter || 0);
  }
  function releaseShadowMic(s){
    if(!s || !s.micWarmupStream) return;
    s.micWarmupStream.getTracks().forEach(track => track.stop());
    s.micWarmupStream = null;
  }
  function warmupShadowMic(sh){
    const s = shadowState.get(sh);
    if(isMobileShadowDevice()) return;
    if(!s || s.micWarmupStarted || !navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) return;
    s.micWarmupStarted = true;
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(stream => {
        if(shadowState.get(sh) !== s || !s.active){
          stream.getTracks().forEach(track => track.stop());
          return;
        }
        s.micWarmupStream = stream;
      })
      .catch(err => {
        console.warn('shadowing mic warmup failed:', err && (err.name || err.message || err));
      });
  }
  function renderShadowTarget(sh){
    const s = shadowState.get(sh);
    if(!s) return;
    sh.querySelector('.sh-index').textContent = String(s.index + 1);
    sh.querySelector('.sh-total').textContent = String(s.lines.length);
    const target = sh.querySelector('.sh-target');
    target.innerHTML = '';
    const words = textFromLine(s.lines[s.index]).split(/\s+/).filter(Boolean);
    s.targetWords = words;
    s.recognizedWords = [];
    s.failedAttempts = 0;
    s.autoMatched = new Set();
    words.forEach((w, i) => {
      const span = document.createElement('span');
      span.className = 'sh-word';
      span.textContent = w;
      if(isLikelyProperNoun(w, i, words)){
        span.classList.add('matched', 'auto-matched');
        s.autoMatched.add(i);
      }
      target.appendChild(span);
      if(i < words.length - 1) target.appendChild(document.createTextNode(' '));
    });
    const fb = sh.querySelector('.sh-feedback');
    if(fb){ fb.textContent = ''; fb.className = 'sh-feedback'; }
  }
  function setShadowStatus(sh, text, cls){
    const el = sh.querySelector('.sh-status');
    if(!el) return;
    el.className = 'sh-status ' + (cls || '');
    el.textContent = text;
  }
  function updateShadowMatched(sh){
    const s = shadowState.get(sh);
    if(!s) return;
    const set = createMatchSet(s.recognizedWords || []);
    sh.querySelectorAll('.sh-target .sh-word').forEach((span, i) => {
      if(wordMatched(s.targetWords[i], set)) span.classList.add('matched');
    });
  }
  function shadowMatchStats(sh){
    const s = shadowState.get(sh);
    if(!s) return { hit: 0, total: 0, ratio: 0, targetLetters: 0, recognizedCount: 0 };
    const set = createMatchSet(s.recognizedWords || []);
    const targetWords = s.targetWords || [];
    if(!targetWords.length) return { hit: 0, total: 0, ratio: 0, targetLetters: 0, recognizedCount: 0 };
    let hit = 0;
    targetWords.forEach((w, i) => {
      if(s.autoMatched && s.autoMatched.has(i)) hit++;
      else if(wordMatched(w, set)) hit++;
    });
    const targetLetters = targetWords.map(normWord).filter(Boolean).join('').length;
    const recognizedCount = (s.recognizedWords || []).map(normWord).filter(Boolean).length;
    return { hit, total: targetWords.length, ratio: hit / targetWords.length, targetLetters, recognizedCount };
  }
  function shadowPassThreshold(s){
    return SH_PASS_THRESHOLDS[Math.min(s.failedAttempts || 0, SH_PASS_THRESHOLDS.length - 1)];
  }
  function shadowAllMatched(sh){
    const s = shadowState.get(sh);
    if(!s) return false;
    const stats = shadowMatchStats(sh);
    if(!stats.total) return false;
    if(stats.ratio >= shadowPassThreshold(s)) return true;
    if(stats.targetLetters <= 3 && stats.recognizedCount > 0) return true;
    if(stats.total <= 2 && stats.hit >= 1) return true;
    if(stats.total <= 4 && stats.hit >= 1 && (s.failedAttempts || 0) >= 1) return true;
    if(stats.recognizedCount > 0 && (s.failedAttempts || 0) >= 3) return true;
    return false;
  }
  async function listen(sh, options){
    const opts = options || {};
    const s = shadowState.get(sh);
    if(!s || !s.active) return;
    if(!SR){
      const fb = sh.querySelector('.sh-feedback');
      fb.textContent = '⚠️ このブラウザは音声認識に対応していません（ChromeかEdgeを使用してください）';
      fb.className = 'sh-feedback forward';
      return;
    }
    const listenToken = (s.listenToken || 0) + 1;
    s.listenToken = listenToken;
    await stopShadowRecognition(sh, { silent: true });
    await recognitionDelay(RECOGNITION_SETTLE_MS);
    if(shadowState.get(sh) !== s || !s.active || s.listenToken !== listenToken) return;
    const rec = new SR();
    rec.lang = 'en-US';
    rec.continuous = false;
    rec.interimResults = false;
    rec.maxAlternatives = 5;
    s.recognition = rec;
    s.resultHandled = false;
    s.errorOccurred = false;
    s.manualStop = false;
    s.ignoredEarlyResult = false;
    rec.onresult = ev => {
      if(s.recognition !== rec) return;
      if(!canAcceptRecognitionResult(s)){
        s.ignoredEarlyResult = true;
        try { rec.abort(); } catch(e){}
        return;
      }
      const spoken = ev.results[0][0].transcript.split(/\s+/).map(normWord).filter(Boolean);
      s.recognizedWords = (s.recognizedWords || []).concat(spoken);
      updateShadowMatched(sh);
      s.resultHandled = true;
      const fb = sh.querySelector('.sh-feedback');
      if(shadowAllMatched(sh)){
        s.failedAttempts = 0;
        fb.textContent = '◯';
        fb.className = 'sh-feedback ok';
        setTimeout(() => {
          if(shadowState.get(sh) === s && s.active && s.listenToken === listenToken) advanceShadow(sh);
        }, 900);
      } else {
        s.failedAttempts++;
        if(s.failedAttempts < 5){
          fb.textContent = 'もう一度';
          fb.className = 'sh-feedback again';
          setTimeout(() => {
            if(shadowState.get(sh) === s && s.active && s.listenToken === listenToken) listen(sh);
          }, 900);
        } else {
          s.failedAttempts = 0;
          fb.textContent = '先に進みます';
          fb.className = 'sh-feedback forward';
          setTimeout(() => {
            if(shadowState.get(sh) === s && s.active && s.listenToken === listenToken) advanceShadow(sh);
          }, 1000);
        }
      }
    };
    rec.onspeechend = () => {
      setShadowStatus(sh, '⏳ 判別中', 'sh-status-processing');
    };
    rec.onerror = ev => {
      if(s.recognition !== rec) return;
      console.warn('shadowing recognition error:', ev.error);
      if(ev.error === 'no-speech'){
        s.errorOccurred = false;
        return;
      }
      if(ev.error === 'aborted') return;
      s.errorOccurred = true;
      if(ev.error === 'not-allowed' || ev.error === 'service-not-allowed'){
        const fb = sh.querySelector('.sh-feedback');
        fb.textContent = '⚠️ マイクの使用が許可されていません。ブラウザの設定で許可してください。';
        fb.className = 'sh-feedback forward';
      }
    };
    rec.onend = () => {
      if(s.recognition === rec){
        s.recognition = null;
        setShadowStatus(sh, '認識停止中', 'sh-status-idle');
        if(s.resultHandled || s.manualStop || s.errorOccurred) return;
        if(shadowState.get(sh) === s && s.active && s.listenToken === listenToken && canAcceptRecognitionResult(s)){
          setTimeout(() => {
            if(shadowState.get(sh) === s && s.active && s.listenToken === listenToken) listen(sh);
          }, 300);
        }
      }
    };
    const startCurrentRecognition = (attempt) => {
      if(shadowState.get(sh) !== s || !s.active || s.recognition !== rec || s.listenToken !== listenToken) return;
      if(!opts.prelisten) setShadowStatus(sh, '🎤 英文を読み上げてください', 'sh-status-active');
      try { rec.start(); }
      catch(e){
        if(attempt < 2){
          setShadowStatus(sh, '⏳ 判別中', 'sh-status-processing');
          setTimeout(() => startCurrentRecognition(attempt + 1), 250 + attempt * 250);
          return;
        }
        console.warn('rec.start threw:', e);
        if(s.recognition === rec) s.recognition = null;
        const fb = sh.querySelector('.sh-feedback');
        fb.textContent = '⚠️ 認識を開始できませんでした: ' + (e.message || e);
        fb.className = 'sh-feedback forward';
        setShadowStatus(sh, '認識停止中', 'sh-status-idle');
      }
    };
    startCurrentRecognition(0);
  }
  async function playShadowCurrent(sh, thenListen){
    const s = shadowState.get(sh);
    if(!s) return;
    const playbackToken = (s.playbackToken || 0) + 1;
    s.playbackToken = playbackToken;
    s.listenToken = (s.listenToken || 0) + 1;
    s.playbackActive = true;
    s.acceptRecognitionResults = false;
    s.acceptResultsAfter = Infinity;
    s.ignoredEarlyResult = false;
    await stopShadowRecognition(sh, { silent: true });
    await recognitionDelay(RECOGNITION_SETTLE_MS);
    if(shadowState.get(sh) !== s || !s.active || s.playbackToken !== playbackToken) return;
    const line = s.lines[s.index];
    const url = line.getAttribute('data-audio');
    setShadowStatus(sh, '🔊 読み上げ中', 'sh-status-tts');
    let prelistenStarted = false;
    const beginPrelisten = () => {
      if(!shouldPrelistenShadow()) return;
      if(prelistenStarted || shadowState.get(sh) !== s || !s.active || s.playbackToken !== playbackToken) return;
      if((s.targetWords || []).length < PRELISTEN_MIN_WORDS) return;
      prelistenStarted = true;
      listen(sh, { prelisten: true });
    };
    const resumeListening = () => {
      if(shadowState.get(sh) !== s || !s.active || s.playbackToken !== playbackToken) return;
      s.playbackActive = false;
      if(!thenListen){
        setShadowStatus(sh, '認識停止中', 'sh-status-idle');
        return;
      }
      const startDelay = shadowRecognitionStartDelay();
      s.acceptResultsAfter = performance.now() + startDelay;
      setTimeout(() => {
        if(shadowState.get(sh) !== s || !s.active || s.playbackToken !== playbackToken) return;
        s.acceptRecognitionResults = true;
        if(s.recognition && s.ignoredEarlyResult){
          stopShadowRecognition(sh, { silent: true }).then(() => {
            if(shadowState.get(sh) === s && s.active && s.playbackToken === playbackToken) listen(sh);
          });
        } else if(s.recognition){
          setShadowStatus(sh, '🎤 英文を読み上げてください', 'sh-status-active');
        } else {
          listen(sh);
        }
      }, startDelay);
    };
    playAudio(url, line, resumeListening, {
      onAlmostEnd: beginPrelisten,
      almostEndSeconds: 0.65
    });
  }
  function startShadowing(){
    const r = root();
    const sh = r && r.querySelector('.shadowing');
    if(!sh) return;
    if(requestSharedShadow('start', r, true)){
      stopAudio();
      return;
    }
    if(sharedShadowing()){
      stopAudio();
      sharedShadowing().start(r);
      return;
    }
    const lines = shadowLines();
    if(!lines.length) return;
    shadowState.set(sh, {
      lines,
      index: 0,
      targetWords: [],
      recognizedWords: [],
      active: true,
      recognition: null,
      failedAttempts: 0,
      stopRecognitionPromise: null,
      listenToken: 0,
      playbackToken: 0,
      playbackActive: false,
      acceptRecognitionResults: false,
      acceptResultsAfter: Infinity,
      micWarmupStarted: false,
      micWarmupStream: null
    });
    sh.querySelector('.sh-intro')?.classList.add('hidden');
    sh.querySelector('.sh-active')?.classList.remove('hidden');
    sh.querySelector('.sh-done')?.classList.add('hidden');
    renderShadowTarget(sh);
    warmupShadowMic(sh);
    playShadowCurrent(sh, true);
  }
  async function advanceShadow(sh){
    const s = shadowState.get(sh);
    if(!s || s.advancing) return;
    s.advancing = true;
    s.listenToken = (s.listenToken || 0) + 1;
    await stopShadowRecognition(sh, { silent: true });
    if(shadowState.get(sh) !== s || !s.active) return;
    s.index++;
    if(s.index >= s.lines.length){
      s.active = false;
      s.advancing = false;
      releaseShadowMic(s);
      sh.querySelector('.sh-active')?.classList.add('hidden');
      sh.querySelector('.sh-done')?.classList.remove('hidden');
      stopAudio();
      return;
    }
    renderShadowTarget(sh);
    setTimeout(() => {
      if(shadowState.get(sh) !== s || !s.active) return;
      s.advancing = false;
      playShadowCurrent(sh, true);
    }, 180);
  }
  function init(){
    const r = root();
    if(!r) return;
    saveWordDisplays();
    markNewWords();
    populateVoices();
    if(window.speechSynthesis && typeof window.speechSynthesis.onvoiceschanged !== 'undefined') window.speechSynthesis.onvoiceschanged = populateVoices;
    if(document.body.dataset.bSeriesPreview === 'true') r.classList.remove('hidden');
    const sel = r.querySelector('.lesson-select');
    showLesson(sel && sel.value ? sel.value : '1');
  }
  function intercept(e){
    const r = root();
    if(!r) return;
    const target = e.target;
    if(!(target instanceof Element)) return;
    if(!r.contains(target)) return;
    if(target.closest('.btn-mode')){
      e.preventDefault(); e.stopImmediatePropagation();
      applyMode(target.closest('.btn-mode').dataset.mode);
      return;
    }
    if(target.closest('.btn-tts-passage')){
      e.preventDefault(); e.stopImmediatePropagation();
      playQueue(shadowLines());
      return;
    }
    if(target.closest('.btn-tts-stop')){
      e.preventDefault(); e.stopImmediatePropagation();
      stopAudio();
      return;
    }
    if(target.closest('.btn-next-lesson')){
      e.preventDefault(); e.stopImmediatePropagation();
      const sel = r.querySelector('.lesson-select');
      if(sel && sel.selectedIndex < sel.options.length - 1){
        sel.selectedIndex += 1;
        showLesson(sel.value);
        r.scrollIntoView({behavior:'smooth', block:'start'});
      }
      return;
    }
    if(target.closest('.btn-sh-start') || target.closest('.btn-sh-retry')){
      e.preventDefault(); e.stopImmediatePropagation();
      startShadowing();
      return;
    }
    if(target.closest('.btn-sh-replay')){
      e.preventDefault(); e.stopImmediatePropagation();
      const sh = r.querySelector('.shadowing');
      if(requestSharedShadow('replay', r, true)){
        stopAudio();
      } else if(sharedShadowing()){
        stopAudio();
        sharedShadowing().replay(r);
      } else {
        stopShadowRecognition(sh, { silent: true }).then(() => playShadowCurrent(sh, true));
      }
      return;
    }
    if(target.closest('.btn-sh-stop')){
      e.preventDefault(); e.stopImmediatePropagation();
      const sh = r.querySelector('.shadowing');
      if(requestSharedShadow('stop', r, true)) stopAudio();
      else if(sharedShadowing()) sharedShadowing().stop(r);
      else {
        stopShadowRecognition(sh);
        stopAudio();
      }
      return;
    }
    if(target.closest('.btn-sh-skip')){
      e.preventDefault(); e.stopImmediatePropagation();
      if(requestSharedShadow('skip', r, true)) return;
      if(sharedShadowing()) sharedShadowing().skip(r);
      else advanceShadow(r.querySelector('.shadowing'));
      return;
    }
    if(target.closest('.btn-sh-end')){
      e.preventDefault(); e.stopImmediatePropagation();
      if(requestSharedShadow('end', r, true)) stopAudio();
      else if(sharedShadowing()) sharedShadowing().end(r);
      else {
        resetShadowing();
        stopAudio();
      }
      return;
    }
    const word = target.closest('.w, .we');
    if(word){
      e.preventDefault(); e.stopImmediatePropagation();
      speakWord(word.getAttribute('data-display') || word.textContent.trim());
    }
    const pictureLine = target.closest('.picture-line');
    if(pictureLine){
      e.preventDefault(); e.stopImmediatePropagation();
      playAudio(pictureLine.getAttribute('data-audio'), pictureLine);
    }
  }
  document.addEventListener('click', intercept, true);
  document.addEventListener('change', function(e){
    const r = root();
    const target = e.target;
    if(r && target instanceof Element && r.contains(target) && target.matches('.lesson-select')){
      e.preventDefault(); e.stopImmediatePropagation();
      showLesson(target.value);
    }
  }, true);
  document.addEventListener('click', function(e){
    const btn = e.target instanceof Element && e.target.closest('.btn-book[data-book="beginner"]');
    if(btn) setTimeout(() => {
      const r = root();
      const sel = r && r.querySelector('.lesson-select');
      if(sel) showLesson(sel.value);
    }, 0);
  });
  document.addEventListener('visibilitychange', () => {
    if(document.hidden) resetShadowing();
  });
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
"""


def build_preview(fragment: str) -> str:
    preview_fragment = fragment.replace('class="book hidden b-series-book"', 'class="book b-series-book"')
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>入門英語（Funnics Island） B1-B20 Preview</title>
<style>
  :root {{
    --fg: #1f2937;
    --fg-soft: #374151;
    --muted: #6b7280;
    --accent: #2563eb;
    --accent-dark: #1d4ed8;
    --accent-soft: #eff6ff;
    --new: #dc2626;
    --bg: #fafafa;
    --card: #ffffff;
    --border: #e5e7eb;
    --border-soft: #f3f4f6;
    --shadow-sm: 0 1px 2px rgba(0,0,0,.04), 0 1px 3px rgba(0,0,0,.06);
    --shadow-md: 0 4px 10px rgba(0,0,0,.04), 0 2px 6px rgba(0,0,0,.05);
  }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: "Hiragino Sans","Yu Gothic",Meiryo,system-ui,-apple-system,"Segoe UI",sans-serif;
    line-height: 1.85;
    color: var(--fg);
    background: var(--bg);
    margin: 0;
  }}
  .wrap {{ max-width: 960px; margin: 0 auto; padding: 24px 18px 48px; }}
  .hidden {{ display: none !important; }}
  .book-title {{ color: #1e3a8a; font-size: 1.2rem; font-weight: 800; padding: .9em 1.1em; background: linear-gradient(135deg, #eff6ff, #dbeafe); border-radius: 10px; margin: .4em 0 1.2em; border-left: 5px solid var(--accent); box-shadow: var(--shadow-sm); }}
  h2 {{ font-size: 1.15rem; font-weight: 700; margin-top: 2rem; padding-top: .6rem; border-top: 1px solid var(--border); }}
  h3 {{ font-size: 1rem; margin: .6em 0 .3em; color: var(--fg-soft); font-weight: 700; }}
  .toolbar {{ display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin: 10px 0 14px; padding: 10px 12px; background: #fff; border: 1px solid var(--border); border-radius: 10px; }}
  .toolbar button, .toolbar select {{ border: 1px solid #d1d5db; background: #fff; padding: 8px 14px; border-radius: 8px; cursor: pointer; font-size: .93rem; color: var(--fg-soft); font-family: inherit; }}
  .toolbar select {{ min-width: 0; max-width: 100%; }}
  .toolbar .lesson-select {{ flex: 1 1 18rem; width: min(100%, 34rem); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
  .toolbar button[aria-pressed="true"] {{ border-color: var(--accent); color: #fff; background: var(--accent); font-weight: 600; }}
  @media (max-width: 640px) {{
    .toolbar {{ min-width: 0; width: 100%; max-width: 100%; }}
    .toolbar label {{ flex: 0 0 auto; }}
    .toolbar .lesson-select {{ flex: 1 1 100%; width: 100%; max-width: 100%; }}
    .toolbar button, .toolbar select {{ min-width: 0; }}
  }}
  ruby rt {{ font-size: .62em; color: var(--muted); font-weight: 400; }}
  .grammar-box {{ background: #fefce8; border: 1px solid #fde68a; border-left: 4px solid #f59e0b; border-radius: 10px; padding: 14px 18px; margin: 14px 0 18px; font-size: .93rem; box-shadow: var(--shadow-sm); }}
  .grammar-box .g-title {{ color: #b45309; font-weight: 700; font-size: 1rem; display: block; margin-bottom: .4em; }}
  .grammar-box ul {{ margin: .3em 0 .2em 1.3em; padding: 0; }}
  .grammar-box .ja {{ color: #64748b; }}
  .jp-full {{ font-size: 1rem; line-height: 1.9; color: var(--fg); background: #fffbea; border: 1px solid #fde68a; border-radius: 10px; padding: 14px 18px; margin: 12px 0; }}
  table {{ width: 100%; border-collapse: collapse; font-size: .93rem; margin: .6em 0 1.2em; background: #fff; border-radius: 10px; overflow: hidden; box-shadow: var(--shadow-sm); }}
  th, td {{ border-bottom: 1px solid var(--border-soft); padding: .55rem .7rem; text-align: left; vertical-align: top; }}
  th {{ background: #f9fafb; font-weight: 700; color: var(--fg-soft); font-size: .9rem; }}
  .new-row td {{ color: var(--new); font-weight: 600; }}
  .yt-section {{ margin: 18px 0; padding: 14px; background: linear-gradient(135deg, #fff1f2, #fee2e2); border: 2px solid #fca5a5; border-radius: 12px; }}
  .yt-label {{ font-size: .95rem; color: #991b1b; margin-bottom: 10px; font-weight: 700; text-align: center; }}
  .yt-embed-wrap {{ position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; border-radius: 8px; background: #000; }}
  .yt-embed-wrap iframe {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0; }}
  .yt-watch-link {{ display: inline-block; margin-top: 10px; padding: 6px 14px; background: #fff; border: 2px solid #ef4444; border-radius: 6px; color: #991b1b; font-size: .88rem; font-weight: 700; text-decoration: none; }}
  .shadowing {{ background: #f0fdf4; border: 2px solid #86efac; border-radius: 12px; padding: 18px 22px; margin: 20px 0; }}
  .shadowing .sh-heading {{ border-top: none; padding-top: 0; margin: 0 0 .6em; color: #166534; font-size: 1.12rem; }}
  .shadowing .btn-sh-start, .btn-next-lesson {{ display: inline-block; border: 2px solid #16a34a; background: #16a34a; color: #fff; padding: 12px 28px; border-radius: 10px; cursor: pointer; font-size: 1rem; font-weight: 700; }}
  .shadowing .sh-target {{ font-size: 1.25rem; font-weight: 600; color: #14532d; background: #fff; padding: 14px 18px; border-radius: 10px; margin: 6px 0 12px; line-height: 1.8; }}
  .shadowing .sh-word {{ display: inline-block; padding: 2px 6px; margin: 1px 1px; border-radius: 5px; }}
  .shadowing .sh-word.matched {{ background: #bbf7d0; color: #14532d; }}
  .shadowing .sh-controls {{ display: flex; gap: 10px; flex-wrap: wrap; align-items: center; margin-top: 8px; }}
  .shadowing .sh-controls button {{ border: 2px solid #16a34a; background: #fff; color: #14532d; padding: 9px 16px; border-radius: 8px; cursor: pointer; font-size: .93rem; font-weight: 600; }}
  .sh-status {{ display: inline-block; padding: 7px 16px; border-radius: 50px; font-size: .88rem; font-weight: 700; border: 1px solid #cbd5e1; background: #f1f5f9; color: #64748b; }}
  .sh-feedback.ok {{ color: #059669; font-size: 2.2rem; text-align:center; font-weight:800; }}
  .sh-feedback.again {{ color: #f59e0b; text-align:center; font-weight:800; }}
  .next-lesson-wrap {{ text-align: center; margin: 0 0 18px; }}
  .btn-next-lesson {{ background: #2563eb; border-color: #2563eb; display: block; margin: 12px auto 0; }}
</style>
<link rel="stylesheet" href="b_series_book_replacement.css">
</head>
<body data-b-series-preview="true">
  <main class="wrap">
{preview_fragment}
  </main>
<script src="b_series_book_replacement.js"></script>
</body>
</html>
"""


def build_notes() -> str:
    return """# Bシリーズ移植メモ

`index.html` はまだ変更していません。このフォルダ内のファイルを使うと、現在の入門編Bシリーズ部分を、既存の教材構造に合わせて置き換えられます。

## 使うファイル

- `b_series_book_replacement.html`: `div#book-beginner` の置き換え用HTML
- `b_series_book_replacement.css`: Bシリーズ専用の最小追加スタイル
- `b_series_book_replacement.js`: Bシリーズ用の動画表示、読み上げ、シャドウイング、単語チェック補助
- `b_series_book_preview.html`: 単体プレビュー
- `b_series_lessons_ja.json`: 元データ
- `b_series_youtube_urls.json`: YouTube URL一覧

## index.html に移植するとき

1. `<head>` 内に次を追加します。

```html
<link rel="stylesheet" href="funnics-beginner-assets/b_series_book_replacement.css">
```

2. 既存の `<div class="book hidden" id="book-beginner" data-book="beginner"> ... </div>` を、`b_series_book_replacement.html` の中身で置き換えます。

3. 既存のメイン `<script>` の後ろ、`</body>` の前に次を追加します。

```html
<script src="funnics-beginner-assets/b_series_book_replacement.js"></script>
```

## 含めた要素

- 各Bレッスンの文法説明と例文
- 日本語混じり文（`jp-body`）: 新出語だけ英語で残し、それ以外は日本語訳
- 英語だけの文（`en-body`）
- 日本語訳（`jp-full`）
- 本文では歌詞の繰り返し行を省略
- YouTube個別動画とB1〜B20一気見リンク
- 21ページ目のまとめページ（文法事項とB1〜B20個別YouTubeリンクを一体化した一覧、一気見動画リンク）
- シャドウイング練習
- このレッスンの新出単語チェック

## 補足

- 既存の `id="book-beginner"` と `data-book="beginner"` はそのまま残しています。
- `data-audio` の録音音声を優先して再生し、音源が見つからない場合だけ Web Speech にフォールバックします。
- `index.html` 本体はこの生成処理では変更しません。
"""


def main() -> int:
    lessons = prepare_lessons(json.loads(LESSONS_JSON.read_text(encoding="utf-8"))["lessons"])
    youtube_data = json.loads(YOUTUBE_JSON.read_text(encoding="utf-8"))
    bank = load_word_bank()
    fragment = build_fragment(lessons, youtube_data, bank)
    outputs = {
        "b_series_book_replacement.html": fragment + "\n",
        "b_series_book_replacement.css": CSS,
        "b_series_book_replacement.js": JS,
        "b_series_book_preview.html": build_preview(fragment),
        "b_series_migration_notes.md": build_notes(),
    }
    for name, text in outputs.items():
        path = ASSET_DIR / name
        path.write_text(text, encoding="utf-8")
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
