#!/usr/bin/env python3
"""Append rule-based phonics word cards beyond short vowels."""
import json
from pathlib import Path


DATA_PATH = Path("phonics-audio-items.json")

RULE_LABELS = {
    "magic-e-a": "magic e long a",
    "magic-e-i": "magic e long i",
    "magic-e-o": "magic e long o",
    "magic-e-u": "magic e long u",
    "vowel-team-ai-ay": "ai/ay long a",
    "vowel-team-ee-ea": "ee/ea long e",
    "vowel-team-oa-ow": "oa/ow long o",
    "vowel-team-oo-long": "oo long",
    "vowel-team-oo-short": "oo short",
    "diphthong-oi-oy": "oi/oy",
    "diphthong-ou-ow": "ou/ow",
    "r-controlled-ar": "r-controlled ar",
    "r-controlled-or": "r-controlled or",
    "r-controlled-er": "r-controlled er/ir/ur",
}

TOKENS = {
    "a_e": ("a_e", "/eɪ/", "eɪ"),
    "i_e": ("i_e", "/aɪ/", "aɪ"),
    "o_e": ("o_e", "/oʊ/", "oʊ"),
    "u_e": ("u_e", "/juː/", "juː"),
    "ai": ("ai", "/eɪ/", "eɪ"),
    "ay": ("ay", "/eɪ/", "eɪ"),
    "ee": ("ee", "/iː/", "iː"),
    "ea": ("ea", "/iː/", "iː"),
    "oa": ("oa", "/oʊ/", "oʊ"),
    "ow_long": ("ow", "/oʊ/", "oʊ"),
    "oo_long": ("oo", "/uː/", "uː"),
    "oo_short": ("oo", "/ʊ/", "ʊ"),
    "oi": ("oi", "/ɔɪ/", "ɔɪ"),
    "oy": ("oy", "/ɔɪ/", "ɔɪ"),
    "ou": ("ou", "/aʊ/", "aʊ"),
    "ow": ("ow", "/aʊ/", "aʊ"),
    "ar": ("ar", "/ɑr/", "ɑr"),
    "or": ("or", "/ɔr/", "ɔr"),
    "er": ("er", "/ɜr/", "ɜr"),
    "ir": ("ir", "/ɜr/", "ɜr"),
    "ur": ("ur", "/ɜr/", "ɜr"),
    "b": ("b", "/b/", "b"),
    "c": ("c", "/k/", "k"),
    "ck": ("ck", "/k/", "k"),
    "d": ("d", "/d/", "d"),
    "f": ("f", "/f/", "f"),
    "g": ("g", "/g/", "g"),
    "h": ("h", "/h/", "h"),
    "j": ("j", "/dʒ/", "j"),
    "k": ("k", "/k/", "k"),
    "l": ("l", "/l/", "l"),
    "m": ("m", "/m/", "m"),
    "n": ("n", "/n/", "n"),
    "p": ("p", "/p/", "p"),
    "r": ("r", "/r/", "r"),
    "s": ("s", "/s/", "s"),
    "sh": ("sh", "/ʃ/", "sh"),
    "t": ("t", "/t/", "t"),
    "th": ("th", "/θ/", "th"),
    "v": ("v", "/v/", "v"),
    "w": ("w", "/w/", "w"),
    "y": ("y", "/j/", "y"),
    "z": ("z", "/z/", "z"),
    "ch": ("ch", "/tʃ/", "ch"),
}

EXTRA_WORDS = [
    ("cake", "keɪk", "ケーキ", "magic-e-a", ["c", "a_e", "k"]),
    ("make", "meɪk", "作る", "magic-e-a", ["m", "a_e", "k"]),
    ("lake", "leɪk", "湖", "magic-e-a", ["l", "a_e", "k"]),
    ("bake", "beɪk", "焼く", "magic-e-a", ["b", "a_e", "k"]),
    ("name", "neɪm", "名前", "magic-e-a", ["n", "a_e", "m"]),
    ("game", "geɪm", "ゲーム", "magic-e-a", ["g", "a_e", "m"]),
    ("gate", "geɪt", "門", "magic-e-a", ["g", "a_e", "t"]),
    ("date", "deɪt", "日付", "magic-e-a", ["d", "a_e", "t"]),
    ("late", "leɪt", "遅い", "magic-e-a", ["l", "a_e", "t"]),
    ("tape", "teɪp", "テープ", "magic-e-a", ["t", "a_e", "p"]),
    ("cape", "keɪp", "マント", "magic-e-a", ["c", "a_e", "p"]),
    ("cane", "keɪn", "つえ", "magic-e-a", ["c", "a_e", "n"]),
    ("lane", "leɪn", "小道・車線", "magic-e-a", ["l", "a_e", "n"]),
    ("plane", "pleɪn", "飛行機", "magic-e-a", ["p", "l", "a_e", "n"]),
    ("plate", "pleɪt", "皿", "magic-e-a", ["p", "l", "a_e", "t"]),
    ("snake", "sneɪk", "ヘビ", "magic-e-a", ["s", "n", "a_e", "k"]),
    ("brave", "breɪv", "勇敢な", "magic-e-a", ["b", "r", "a_e", "v"]),
    ("cave", "keɪv", "洞窟", "magic-e-a", ["c", "a_e", "v"]),
    ("wave", "weɪv", "波・手を振る", "magic-e-a", ["w", "a_e", "v"]),
    ("save", "seɪv", "救う・保存する", "magic-e-a", ["s", "a_e", "v"]),
    ("bike", "baɪk", "自転車", "magic-e-i", ["b", "i_e", "k"]),
    ("like", "laɪk", "好き", "magic-e-i", ["l", "i_e", "k"]),
    ("hike", "haɪk", "ハイキングする", "magic-e-i", ["h", "i_e", "k"]),
    ("kite", "kaɪt", "たこ", "magic-e-i", ["k", "i_e", "t"]),
    ("ride", "raɪd", "乗る", "magic-e-i", ["r", "i_e", "d"]),
    ("side", "saɪd", "側", "magic-e-i", ["s", "i_e", "d"]),
    ("wide", "waɪd", "広い", "magic-e-i", ["w", "i_e", "d"]),
    ("time", "taɪm", "時間", "magic-e-i", ["t", "i_e", "m"]),
    ("dime", "daɪm", "10セント硬貨", "magic-e-i", ["d", "i_e", "m"]),
    ("fine", "faɪn", "元気な・細かい", "magic-e-i", ["f", "i_e", "n"]),
    ("line", "laɪn", "線", "magic-e-i", ["l", "i_e", "n"]),
    ("pine", "paɪn", "松", "magic-e-i", ["p", "i_e", "n"]),
    ("nine", "naɪn", "9", "magic-e-i", ["n", "i_e", "n"]),
    ("shine", "ʃaɪn", "輝く", "magic-e-i", ["sh", "i_e", "n"]),
    ("slide", "slaɪd", "すべる", "magic-e-i", ["s", "l", "i_e", "d"]),
    ("smile", "smaɪl", "ほほえむ", "magic-e-i", ["s", "m", "i_e", "l"]),
    ("stripe", "straɪp", "しま", "magic-e-i", ["s", "t", "r", "i_e", "p"]),
    ("prize", "praɪz", "賞", "magic-e-i", ["p", "r", "i_e", "z"]),
    ("home", "hoʊm", "家", "magic-e-o", ["h", "o_e", "m"]),
    ("note", "noʊt", "メモ・音符", "magic-e-o", ["n", "o_e", "t"]),
    ("rope", "roʊp", "ロープ", "magic-e-o", ["r", "o_e", "p"]),
    ("hope", "hoʊp", "望み", "magic-e-o", ["h", "o_e", "p"]),
    ("bone", "boʊn", "骨", "magic-e-o", ["b", "o_e", "n"]),
    ("cone", "koʊn", "円すい", "magic-e-o", ["c", "o_e", "n"]),
    ("stone", "stoʊn", "石", "magic-e-o", ["s", "t", "o_e", "n"]),
    ("joke", "dʒoʊk", "冗談", "magic-e-o", ["j", "o_e", "k"]),
    ("smoke", "smoʊk", "煙", "magic-e-o", ["s", "m", "o_e", "k"]),
    ("globe", "gloʊb", "地球儀", "magic-e-o", ["g", "l", "o_e", "b"]),
    ("broke", "broʊk", "壊した", "magic-e-o", ["b", "r", "o_e", "k"]),
    ("code", "koʊd", "コード", "magic-e-o", ["c", "o_e", "d"]),
    ("mode", "moʊd", "方法・モード", "magic-e-o", ["m", "o_e", "d"]),
    ("cube", "kjuːb", "立方体", "magic-e-u", ["c", "u_e", "b"]),
    ("cute", "kjuːt", "かわいい", "magic-e-u", ["c", "u_e", "t"]),
    ("mule", "mjuːl", "ラバ", "magic-e-u", ["m", "u_e", "l"]),
    ("tune", "tjuːn", "曲・調子", "magic-e-u", ["t", "u_e", "n"]),
    ("June", "dʒuːn", "6月", "magic-e-u", ["j", "u_e", "n"]),
    ("tube", "tuːb", "チューブ", "magic-e-u", ["t", "u_e", "b"]),
    ("use", "juːz", "使う", "magic-e-u", ["u_e", "z"]),
    ("rain", "reɪn", "雨", "vowel-team-ai-ay", ["r", "ai", "n"]),
    ("train", "treɪn", "電車", "vowel-team-ai-ay", ["t", "r", "ai", "n"]),
    ("mail", "meɪl", "郵便", "vowel-team-ai-ay", ["m", "ai", "l"]),
    ("tail", "teɪl", "しっぽ", "vowel-team-ai-ay", ["t", "ai", "l"]),
    ("sail", "seɪl", "帆・航海する", "vowel-team-ai-ay", ["s", "ai", "l"]),
    ("paint", "peɪnt", "絵の具・塗る", "vowel-team-ai-ay", ["p", "ai", "n", "t"]),
    ("brain", "breɪn", "脳", "vowel-team-ai-ay", ["b", "r", "ai", "n"]),
    ("day", "deɪ", "日", "vowel-team-ai-ay", ["d", "ay"]),
    ("play", "pleɪ", "遊ぶ", "vowel-team-ai-ay", ["p", "l", "ay"]),
    ("stay", "steɪ", "とどまる", "vowel-team-ai-ay", ["s", "t", "ay"]),
    ("tray", "treɪ", "トレイ", "vowel-team-ai-ay", ["t", "r", "ay"]),
    ("clay", "kleɪ", "粘土", "vowel-team-ai-ay", ["c", "l", "ay"]),
    ("gray", "greɪ", "灰色", "vowel-team-ai-ay", ["g", "r", "ay"]),
    ("say", "seɪ", "言う", "vowel-team-ai-ay", ["s", "ay"]),
    ("way", "weɪ", "道・方法", "vowel-team-ai-ay", ["w", "ay"]),
    ("see", "siː", "見る", "vowel-team-ee-ea", ["s", "ee"]),
    ("seed", "siːd", "種", "vowel-team-ee-ea", ["s", "ee", "d"]),
    ("tree", "triː", "木", "vowel-team-ee-ea", ["t", "r", "ee"]),
    ("green", "griːn", "緑", "vowel-team-ee-ea", ["g", "r", "ee", "n"]),
    ("feet", "fiːt", "足", "vowel-team-ee-ea", ["f", "ee", "t"]),
    ("sheep", "ʃiːp", "羊", "vowel-team-ee-ea", ["sh", "ee", "p"]),
    ("bee", "biː", "ハチ", "vowel-team-ee-ea", ["b", "ee"]),
    ("team", "tiːm", "チーム", "vowel-team-ee-ea", ["t", "ea", "m"]),
    ("leaf", "liːf", "葉", "vowel-team-ee-ea", ["l", "ea", "f"]),
    ("seat", "siːt", "席", "vowel-team-ee-ea", ["s", "ea", "t"]),
    ("beach", "biːtʃ", "浜辺", "vowel-team-ee-ea", ["b", "ea", "ch"]),
    ("peach", "piːtʃ", "桃", "vowel-team-ee-ea", ["p", "ea", "ch"]),
    ("boat", "boʊt", "ボート", "vowel-team-oa-ow", ["b", "oa", "t"]),
    ("coat", "koʊt", "コート", "vowel-team-oa-ow", ["c", "oa", "t"]),
    ("road", "roʊd", "道路", "vowel-team-oa-ow", ["r", "oa", "d"]),
    ("goat", "goʊt", "ヤギ", "vowel-team-oa-ow", ["g", "oa", "t"]),
    ("soap", "soʊp", "せっけん", "vowel-team-oa-ow", ["s", "oa", "p"]),
    ("snow", "snoʊ", "雪", "vowel-team-oa-ow", ["s", "n", "ow_long"]),
    ("grow", "groʊ", "育つ", "vowel-team-oa-ow", ["g", "r", "ow_long"]),
    ("blow", "bloʊ", "吹く", "vowel-team-oa-ow", ["b", "l", "ow_long"]),
    ("show", "ʃoʊ", "見せる", "vowel-team-oa-ow", ["sh", "ow_long"]),
    ("low", "loʊ", "低い", "vowel-team-oa-ow", ["l", "ow_long"]),
    ("row", "roʊ", "列・こぐ", "vowel-team-oa-ow", ["r", "ow_long"]),
    ("moon", "muːn", "月", "vowel-team-oo-long", ["m", "oo_long", "n"]),
    ("soon", "suːn", "すぐに", "vowel-team-oo-long", ["s", "oo_long", "n"]),
    ("food", "fuːd", "食べ物", "vowel-team-oo-long", ["f", "oo_long", "d"]),
    ("boot", "buːt", "ブーツ", "vowel-team-oo-long", ["b", "oo_long", "t"]),
    ("look", "lʊk", "見る", "vowel-team-oo-short", ["l", "oo_short", "k"]),
    ("book", "bʊk", "本", "vowel-team-oo-short", ["b", "oo_short", "k"]),
    ("foot", "fʊt", "足", "vowel-team-oo-short", ["f", "oo_short", "t"]),
    ("cook", "kʊk", "料理する", "vowel-team-oo-short", ["c", "oo_short", "k"]),
    ("coin", "kɔɪn", "硬貨", "diphthong-oi-oy", ["c", "oi", "n"]),
    ("boil", "bɔɪl", "沸かす", "diphthong-oi-oy", ["b", "oi", "l"]),
    ("soil", "sɔɪl", "土", "diphthong-oi-oy", ["s", "oi", "l"]),
    ("toy", "tɔɪ", "おもちゃ", "diphthong-oi-oy", ["t", "oy"]),
    ("boy", "bɔɪ", "男の子", "diphthong-oi-oy", ["b", "oy"]),
    ("joy", "dʒɔɪ", "喜び", "diphthong-oi-oy", ["j", "oy"]),
    ("cow", "kaʊ", "牛", "diphthong-ou-ow", ["c", "ow"]),
    ("now", "naʊ", "今", "diphthong-ou-ow", ["n", "ow"]),
    ("brown", "braʊn", "茶色", "diphthong-ou-ow", ["b", "r", "ow", "n"]),
    ("cloud", "klaʊd", "雲", "diphthong-ou-ow", ["c", "l", "ou", "d"]),
    ("loud", "laʊd", "大きな音の", "diphthong-ou-ow", ["l", "ou", "d"]),
    ("found", "faʊnd", "見つけた", "diphthong-ou-ow", ["f", "ou", "n", "d"]),
    ("car", "kɑr", "車", "r-controlled-ar", ["c", "ar"]),
    ("far", "fɑr", "遠い", "r-controlled-ar", ["f", "ar"]),
    ("star", "stɑr", "星", "r-controlled-ar", ["s", "t", "ar"]),
    ("park", "pɑrk", "公園", "r-controlled-ar", ["p", "ar", "k"]),
    ("farm", "fɑrm", "農場", "r-controlled-ar", ["f", "ar", "m"]),
    ("card", "kɑrd", "カード", "r-controlled-ar", ["c", "ar", "d"]),
    ("corn", "kɔrn", "とうもろこし", "r-controlled-or", ["c", "or", "n"]),
    ("fork", "fɔrk", "フォーク", "r-controlled-or", ["f", "or", "k"]),
    ("storm", "stɔrm", "嵐", "r-controlled-or", ["s", "t", "or", "m"]),
    ("bird", "bɜrd", "鳥", "r-controlled-er", ["b", "ir", "d"]),
    ("girl", "gɜrl", "女の子", "r-controlled-er", ["g", "ir", "l"]),
    ("turn", "tɜrn", "曲がる・順番", "r-controlled-er", ["t", "ur", "n"]),
    ("nurse", "nɜrs", "看護師", "r-controlled-er", ["n", "ur", "s"]),
]


def segment_for(token):
    grapheme, ipa, sound = TOKENS[token]
    return {"grapheme": grapheme, "ipa": ipa, "sound": sound}


def card(word, ipa, meaning, rule, tokens):
    return {
        "id": word.lower().replace(" ", "-"),
        "word": word,
        "ipa": ipa,
        "meaning": meaning,
        "rule": rule,
        "ruleLabel": RULE_LABELS[rule],
        "segments": [segment_for(token) for token in tokens],
    }


def main():
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    existing = {item["id"]: index for index, item in enumerate(data["words"])}
    added = 0
    updated = 0
    for args in EXTRA_WORDS:
        item = card(*args)
        if item["id"] in existing:
            index = existing[item["id"]]
            if data["words"][index].get("image"):
                item["image"] = data["words"][index]["image"]
            if data["words"][index] != item:
                data["words"][index] = item
                updated += 1
            continue
        data["words"].append(item)
        existing[item["id"]] = len(data["words"]) - 1
        added += 1

    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Added {added} cards, updated {updated}. Total: {len(data['words'])}")


if __name__ == "__main__":
    main()
