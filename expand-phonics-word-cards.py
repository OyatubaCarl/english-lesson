#!/usr/bin/env python3
"""Append beginner short-vowel word cards to phonics-audio-items.json."""
import json
from pathlib import Path


DATA_PATH = Path("phonics-audio-items.json")

VOWELS = {
    "a": ("/æ/", "æ"),
    "e": ("/ɛ/", "ɛ"),
    "i": ("/ɪ/", "ɪ"),
    "o": ("/ɑ/", "ɑ"),
    "u": ("/ʌ/", "ʌ"),
}

CONSONANTS = {
    "b": ("/b/", "b"),
    "c": ("/k/", "k"),
    "ck": ("/k/", "k"),
    "d": ("/d/", "d"),
    "dd": ("/d/", "d"),
    "f": ("/f/", "f"),
    "ff": ("/f/", "f"),
    "g": ("/g/", "g"),
    "g_j": ("/dʒ/", "j"),
    "h": ("/h/", "h"),
    "j": ("/dʒ/", "j"),
    "k": ("/k/", "k"),
    "l": ("/l/", "l"),
    "ll": ("/l/", "l"),
    "m": ("/m/", "m"),
    "n": ("/n/", "n"),
    "p": ("/p/", "p"),
    "qu": ("/kw/", "kw"),
    "r": ("/r/", "r"),
    "s": ("/s/", "s"),
    "ss": ("/s/", "s"),
    "sh": ("/ʃ/", "sh"),
    "t": ("/t/", "t"),
    "tt": ("/t/", "t"),
    "th": ("/θ/", "th"),
    "v": ("/v/", "v"),
    "w": ("/w/", "w"),
    "x": ("/ks/", "ks"),
    "y": ("/j/", "y"),
    "z": ("/z/", "z"),
    "zz": ("/z/", "z"),
    "ch": ("/tʃ/", "ch"),
}

EXTRA_WORDS = [
    ("am", "æm", "am・be動詞", "short-a", ["a", "m"]),
    ("an", "æn", "ひとつの", "short-a", ["a", "n"]),
    ("at", "æt", "〜で・〜に", "short-a", ["a", "t"]),
    ("ax", "æks", "斧", "short-a", ["a", "x"]),
    ("bad", "bæd", "悪い", "short-a", ["b", "a", "d"]),
    ("dad", "dæd", "お父さん", "short-a", ["d", "a", "d"]),
    ("mad", "mæd", "怒った", "short-a", ["m", "a", "d"]),
    ("sad", "sæd", "悲しい", "short-a", ["s", "a", "d"]),
    ("pad", "pæd", "パッド・詰め物", "short-a", ["p", "a", "d"]),
    ("had", "hæd", "持っていた", "short-a", ["h", "a", "d"]),
    ("lad", "læd", "少年", "short-a", ["l", "a", "d"]),
    ("cab", "kæb", "タクシー", "short-a", ["c", "a", "b"]),
    ("dab", "dæb", "軽く塗る", "short-a", ["d", "a", "b"]),
    ("gab", "gæb", "おしゃべりする", "short-a", ["g", "a", "b"]),
    ("jab", "dʒæb", "突く", "short-a", ["j", "a", "b"]),
    ("lab", "læb", "実験室", "short-a", ["l", "a", "b"]),
    ("pal", "pæl", "友だち", "short-a", ["p", "a", "l"]),
    ("gal", "gæl", "女の子", "short-a", ["g", "a", "l"]),
    ("gas", "gæs", "ガス", "short-a", ["g", "a", "s"]),
    ("gap", "gæp", "すき間", "short-a", ["g", "a", "p"]),
    ("tack", "tæk", "画びょう", "short-a", ["t", "a", "ck"]),
    ("sack", "sæk", "袋", "short-a", ["s", "a", "ck"]),
    ("rack", "ræk", "棚", "short-a", ["r", "a", "ck"]),
    ("jack", "dʒæk", "ジャック", "short-a", ["j", "a", "ck"]),
    ("yak", "jæk", "ヤク", "short-a", ["y", "a", "k"]),
    ("yam", "jæm", "ヤムいも", "short-a", ["y", "a", "m"]),
    ("yap", "jæp", "キャンキャン鳴く", "short-a", ["y", "a", "p"]),
    ("tan", "tæn", "日焼けした色", "short-a", ["t", "a", "n"]),
    ("ran", "ræn", "走った", "short-a", ["r", "a", "n"]),
    ("ban", "bæn", "禁止する", "short-a", ["b", "a", "n"]),
    ("dam", "dæm", "ダム", "short-a", ["d", "a", "m"]),
    ("ant", "ænt", "アリ", "short-a", ["a", "n", "t"]),
    ("and", "ænd", "そして", "short-a", ["a", "n", "d"]),
    ("hand", "hænd", "手", "short-a", ["h", "a", "n", "d"]),
    ("sand", "sænd", "砂", "short-a", ["s", "a", "n", "d"]),
    ("band", "bænd", "バンド", "short-a", ["b", "a", "n", "d"]),
    ("land", "lænd", "土地", "short-a", ["l", "a", "n", "d"]),
    ("ash", "æʃ", "灰", "short-a", ["a", "sh"]),
    ("cash", "kæʃ", "現金", "short-a", ["c", "a", "sh"]),
    ("dash", "dæʃ", "ダッシュする", "short-a", ["d", "a", "sh"]),
    ("rash", "ræʃ", "発疹", "short-a", ["r", "a", "sh"]),
    ("bash", "bæʃ", "強く打つ", "short-a", ["b", "a", "sh"]),
    ("trash", "træʃ", "ごみ", "short-a", ["t", "r", "a", "sh"]),
    ("bath", "bæθ", "お風呂", "short-a", ["b", "a", "th"]),
    ("math", "mæθ", "算数", "short-a", ["m", "a", "th"]),
    ("path", "pæθ", "小道", "short-a", ["p", "a", "th"]),
    ("mask", "mæsk", "マスク", "short-a", ["m", "a", "s", "k"]),
    ("fast", "fæst", "速い", "short-a", ["f", "a", "s", "t"]),
    ("flat", "flæt", "平らな", "short-a", ["f", "l", "a", "t"]),
    ("glad", "glæd", "うれしい", "short-a", ["g", "l", "a", "d"]),
    ("plan", "plæn", "計画", "short-a", ["p", "l", "a", "n"]),
    ("plant", "plænt", "植物", "short-a", ["p", "l", "a", "n", "t"]),
    ("stamp", "stæmp", "切手・スタンプ", "short-a", ["s", "t", "a", "m", "p"]),
    ("get", "gɛt", "得る", "short-e", ["g", "e", "t"]),
    ("met", "mɛt", "会った", "short-e", ["m", "e", "t"]),
    ("set", "sɛt", "置く・セット", "short-e", ["s", "e", "t"]),
    ("let", "lɛt", "〜させる", "short-e", ["l", "e", "t"]),
    ("bet", "bɛt", "賭ける", "short-e", ["b", "e", "t"]),
    ("yet", "jɛt", "まだ", "short-e", ["y", "e", "t"]),
    ("den", "dɛn", "巣穴", "short-e", ["d", "e", "n"]),
    ("fed", "fɛd", "食べ物を与えた", "short-e", ["f", "e", "d"]),
    ("led", "lɛd", "導いた", "short-e", ["l", "e", "d"]),
    ("wed", "wɛd", "結婚する", "short-e", ["w", "e", "d"]),
    ("gem", "dʒɛm", "宝石", "short-e", ["g_j", "e", "m"]),
    ("hem", "hɛm", "すそ", "short-e", ["h", "e", "m"]),
    ("beg", "bɛg", "頼む", "short-e", ["b", "e", "g"]),
    ("keg", "kɛg", "小たる", "short-e", ["k", "e", "g"]),
    ("bell", "bɛl", "ベル", "short-e", ["b", "e", "ll"]),
    ("sell", "sɛl", "売る", "short-e", ["s", "e", "ll"]),
    ("fell", "fɛl", "落ちた", "short-e", ["f", "e", "ll"]),
    ("tell", "tɛl", "話す", "short-e", ["t", "e", "ll"]),
    ("well", "wɛl", "井戸・元気な", "short-e", ["w", "e", "ll"]),
    ("yell", "jɛl", "叫ぶ", "short-e", ["y", "e", "ll"]),
    ("neck", "nɛk", "首", "short-e", ["n", "e", "ck"]),
    ("deck", "dɛk", "デッキ", "short-e", ["d", "e", "ck"]),
    ("peck", "pɛk", "つつく", "short-e", ["p", "e", "ck"]),
    ("check", "tʃɛk", "チェックする", "short-e", ["ch", "e", "ck"]),
    ("rest", "rɛst", "休む", "short-e", ["r", "e", "s", "t"]),
    ("vest", "vɛst", "ベスト", "short-e", ["v", "e", "s", "t"]),
    ("west", "wɛst", "西", "short-e", ["w", "e", "s", "t"]),
    ("nest", "nɛst", "巣", "short-e", ["n", "e", "s", "t"]),
    ("test", "tɛst", "テスト", "short-e", ["t", "e", "s", "t"]),
    ("tent", "tɛnt", "テント", "short-e", ["t", "e", "n", "t"]),
    ("went", "wɛnt", "行った", "short-e", ["w", "e", "n", "t"]),
    ("sent", "sɛnt", "送った", "short-e", ["s", "e", "n", "t"]),
    ("sled", "slɛd", "そり", "short-e", ["s", "l", "e", "d"]),
    ("stem", "stɛm", "茎", "short-e", ["s", "t", "e", "m"]),
    ("step", "stɛp", "一歩", "short-e", ["s", "t", "e", "p"]),
    ("smell", "smɛl", "におい", "short-e", ["s", "m", "e", "ll"]),
    ("dress", "drɛs", "ドレス", "short-e", ["d", "r", "e", "ss"]),
    ("press", "prɛs", "押す", "short-e", ["p", "r", "e", "ss"]),
    ("it", "ɪt", "それ", "short-i", ["i", "t"]),
    ("in", "ɪn", "〜の中に", "short-i", ["i", "n"]),
    ("if", "ɪf", "もし", "short-i", ["i", "f"]),
    ("ill", "ɪl", "病気の", "short-i", ["i", "ll"]),
    ("did", "dɪd", "した", "short-i", ["d", "i", "d"]),
    ("hid", "hɪd", "隠れた", "short-i", ["h", "i", "d"]),
    ("rid", "rɪd", "取り除く", "short-i", ["r", "i", "d"]),
    ("fit", "fɪt", "合う", "short-i", ["f", "i", "t"]),
    ("bit", "bɪt", "少し・かんだ", "short-i", ["b", "i", "t"]),
    ("pit", "pɪt", "穴", "short-i", ["p", "i", "t"]),
    ("mitt", "mɪt", "ミット", "short-i", ["m", "i", "tt"]),
    ("kiss", "kɪs", "キス", "short-i", ["k", "i", "ss"]),
    ("miss", "mɪs", "逃す", "short-i", ["m", "i", "ss"]),
    ("hiss", "hɪs", "シューと言う", "short-i", ["h", "i", "ss"]),
    ("hill", "hɪl", "丘", "short-i", ["h", "i", "ll"]),
    ("will", "wɪl", "〜するつもり", "short-i", ["w", "i", "ll"]),
    ("mill", "mɪl", "製粉所", "short-i", ["m", "i", "ll"]),
    ("fill", "fɪl", "満たす", "short-i", ["f", "i", "ll"]),
    ("pill", "pɪl", "薬", "short-i", ["p", "i", "ll"]),
    ("bill", "bɪl", "請求書", "short-i", ["b", "i", "ll"]),
    ("tick", "tɪk", "カチカチいう", "short-i", ["t", "i", "ck"]),
    ("kick", "kɪk", "ける", "short-i", ["k", "i", "ck"]),
    ("lick", "lɪk", "なめる", "short-i", ["l", "i", "ck"]),
    ("pick", "pɪk", "選ぶ", "short-i", ["p", "i", "ck"]),
    ("sick", "sɪk", "病気の", "short-i", ["s", "i", "ck"]),
    ("wick", "wɪk", "芯", "short-i", ["w", "i", "ck"]),
    ("thick", "θɪk", "厚い", "short-i", ["th", "i", "ck"]),
    ("chick", "tʃɪk", "ひよこ", "short-i", ["ch", "i", "ck"]),
    ("rich", "rɪtʃ", "豊かな", "short-i", ["r", "i", "ch"]),
    ("quiz", "kwɪz", "クイズ", "short-i", ["qu", "i", "z"]),
    ("twin", "twɪn", "双子", "short-i", ["t", "w", "i", "n"]),
    ("gift", "gɪft", "贈り物", "short-i", ["g", "i", "f", "t"]),
    ("milk", "mɪlk", "牛乳", "short-i", ["m", "i", "l", "k"]),
    ("silk", "sɪlk", "絹", "short-i", ["s", "i", "l", "k"]),
    ("print", "prɪnt", "印刷する", "short-i", ["p", "r", "i", "n", "t"]),
    ("crisp", "krɪsp", "パリッとした", "short-i", ["c", "r", "i", "s", "p"]),
    ("split", "splɪt", "分ける", "short-i", ["s", "p", "l", "i", "t"]),
    ("on", "ɑn", "〜の上に", "short-o", ["o", "n"]),
    ("ox", "ɑks", "雄牛", "short-o", ["o", "x"]),
    ("odd", "ɑd", "奇妙な", "short-o", ["o", "dd"]),
    ("cop", "kɑp", "警官", "short-o", ["c", "o", "p"]),
    ("rob", "rɑb", "盗む", "short-o", ["r", "o", "b"]),
    ("sob", "sɑb", "すすり泣く", "short-o", ["s", "o", "b"]),
    ("job", "dʒɑb", "仕事", "short-o", ["j", "o", "b"]),
    ("pod", "pɑd", "さや", "short-o", ["p", "o", "d"]),
    ("rod", "rɑd", "棒", "short-o", ["r", "o", "d"]),
    ("nod", "nɑd", "うなずく", "short-o", ["n", "o", "d"]),
    ("sod", "sɑd", "芝土", "short-o", ["s", "o", "d"]),
    ("dock", "dɑk", "波止場", "short-o", ["d", "o", "ck"]),
    ("lock", "lɑk", "鍵をかける", "short-o", ["l", "o", "ck"]),
    ("clock", "klɑk", "時計", "short-o", ["c", "l", "o", "ck"]),
    ("block", "blɑk", "ブロック", "short-o", ["b", "l", "o", "ck"]),
    ("spot", "spɑt", "点・場所", "short-o", ["s", "p", "o", "t"]),
    ("plot", "plɑt", "筋書き・区画", "short-o", ["p", "l", "o", "t"]),
    ("blob", "blɑb", "しずくのかたまり", "short-o", ["b", "l", "o", "b"]),
    ("clog", "klɑg", "詰まらせる", "short-o", ["c", "l", "o", "g"]),
    ("drop", "drɑp", "落とす", "short-o", ["d", "r", "o", "p"]),
    ("crop", "krɑp", "作物", "short-o", ["c", "r", "o", "p"]),
    ("prop", "prɑp", "支える", "short-o", ["p", "r", "o", "p"]),
    ("pond", "pɑnd", "池", "short-o", ["p", "o", "n", "d"]),
    ("font", "fɑnt", "フォント", "short-o", ["f", "o", "n", "t"]),
    ("fond", "fɑnd", "好きな", "short-o", ["f", "o", "n", "d"]),
    ("soft", "sɑft", "やわらかい", "short-o", ["s", "o", "f", "t"]),
    ("up", "ʌp", "上へ", "short-u", ["u", "p"]),
    ("us", "ʌs", "私たちを", "short-u", ["u", "s"]),
    ("but", "bʌt", "しかし", "short-u", ["b", "u", "t"]),
    ("hut", "hʌt", "小屋", "short-u", ["h", "u", "t"]),
    ("rut", "rʌt", "わだち", "short-u", ["r", "u", "t"]),
    ("tug", "tʌg", "引っぱる", "short-u", ["t", "u", "g"]),
    ("dug", "dʌg", "掘った", "short-u", ["d", "u", "g"]),
    ("jug", "dʒʌg", "水差し", "short-u", ["j", "u", "g"]),
    ("hug", "hʌg", "抱きしめる", "short-u", ["h", "u", "g"]),
    ("lug", "lʌg", "引きずる", "short-u", ["l", "u", "g"]),
    ("bud", "bʌd", "つぼみ", "short-u", ["b", "u", "d"]),
    ("cub", "kʌb", "動物の子", "short-u", ["c", "u", "b"]),
    ("rub", "rʌb", "こする", "short-u", ["r", "u", "b"]),
    ("scrub", "skrʌb", "こすって洗う", "short-u", ["s", "c", "r", "u", "b"]),
    ("snug", "snʌg", "居心地のよい", "short-u", ["s", "n", "u", "g"]),
    ("slug", "slʌg", "ナメクジ", "short-u", ["s", "l", "u", "g"]),
    ("sum", "sʌm", "合計", "short-u", ["s", "u", "m"]),
    ("bump", "bʌmp", "ぶつかる", "short-u", ["b", "u", "m", "p"]),
    ("dump", "dʌmp", "捨てる", "short-u", ["d", "u", "m", "p"]),
    ("jump", "dʒʌmp", "跳ぶ", "short-u", ["j", "u", "m", "p"]),
    ("pump", "pʌmp", "ポンプ", "short-u", ["p", "u", "m", "p"]),
    ("lump", "lʌmp", "かたまり", "short-u", ["l", "u", "m", "p"]),
    ("dust", "dʌst", "ほこり", "short-u", ["d", "u", "s", "t"]),
    ("must", "mʌst", "〜しなければならない", "short-u", ["m", "u", "s", "t"]),
    ("just", "dʒʌst", "ちょうど", "short-u", ["j", "u", "s", "t"]),
    ("crust", "krʌst", "パンの耳・地殻", "short-u", ["c", "r", "u", "s", "t"]),
    ("trust", "trʌst", "信頼する", "short-u", ["t", "r", "u", "s", "t"]),
    ("truck", "trʌk", "トラック", "short-u", ["t", "r", "u", "ck"]),
    ("luck", "lʌk", "運", "short-u", ["l", "u", "ck"]),
    ("puck", "pʌk", "パック", "short-u", ["p", "u", "ck"]),
    ("buck", "bʌk", "雄ジカ・ドル", "short-u", ["b", "u", "ck"]),
    ("suck", "sʌk", "吸う", "short-u", ["s", "u", "ck"]),
    ("tuck", "tʌk", "押し込む", "short-u", ["t", "u", "ck"]),
    ("yuck", "jʌk", "うわっ", "short-u", ["y", "u", "ck"]),
    ("much", "mʌtʃ", "たくさんの", "short-u", ["m", "u", "ch"]),
    ("such", "sʌtʃ", "そのような", "short-u", ["s", "u", "ch"]),
    ("lunch", "lʌntʃ", "昼食", "short-u", ["l", "u", "n", "ch"]),
    ("punch", "pʌntʃ", "パンチ", "short-u", ["p", "u", "n", "ch"]),
    ("bunch", "bʌntʃ", "束", "short-u", ["b", "u", "n", "ch"]),
    ("blush", "blʌʃ", "赤面する", "short-u", ["b", "l", "u", "sh"]),
    ("brush", "brʌʃ", "ブラシ", "short-u", ["b", "r", "u", "sh"]),
    ("crush", "krʌʃ", "押しつぶす", "short-u", ["c", "r", "u", "sh"]),
    ("stuck", "stʌk", "動けない", "short-u", ["s", "t", "u", "ck"]),
    ("cluck", "klʌk", "コッコッと鳴く", "short-u", ["c", "l", "u", "ck"]),
]


def segment_for(token: str):
    grapheme = token.split("_", 1)[0]
    if token in VOWELS:
        ipa, sound = VOWELS[token]
    else:
        ipa, sound = CONSONANTS[token]
    return {"grapheme": grapheme, "ipa": ipa, "sound": sound}


def card(word, ipa, meaning, rule, tokens):
    suffix = ""
    if len(tokens) > 3:
        suffix = " + blend"
    if any(token in {"sh", "ch", "th", "qu"} for token in tokens):
        suffix = " + digraph"
    if any(token in {"x", "ck", "ll", "ss", "ff", "zz"} for token in tokens):
        suffix = " + pattern"
    return {
        "id": word.replace(" ", "-"),
        "word": word,
        "ipa": ipa,
        "meaning": meaning,
        "rule": rule,
        "ruleLabel": rule.replace("short-", "short ") + suffix,
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
            if data["words"][index] != item:
                if data["words"][index].get("image"):
                    item["image"] = data["words"][index]["image"]
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
