"""Update Funnics Island video descriptions with site-first links."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parent
SCOPES = ["https://www.googleapis.com/auth/youtube"]

SITE = "https://english-lesson.gasflare.workers.dev"
LINKS = f"{SITE}/funnics-island-links.html"

ABC_ID = "3B5yLO1HJGs"
ANT_ID = "eGTZmwdWmA0"
BAKER_ID = "qvtc6srq1TI"
AIDER_ID = "q5fMrJvYsXU"

TITLES = {
    ABC_ID: "ファニックス・アイランド　フォニックスとABCの仲間たち　〜Funnics Island ABC Song〜【歌詞字幕つき】",
    ANT_ID: "アントおばさんのみじかい「a」のおと 〜Funnics Island Short A Song〜【歌詞字幕つき】",
    BAKER_ID: "ベイカーベアとまほうのe 〜ながいAのおと〜 〜Funnics Island Long A Song〜",
    AIDER_ID: "エイダースネイルの AI・AY のおと 〜Funnics Island AI/AY Song〜【歌詞字幕つき】",
}

COMMON_TAGS = [
    "FunnicsIsland",
    "ファニックスアイランド",
    "フォニックス",
    "英語の歌",
    "こども英語",
    "幼児英語",
    "英語入門",
    "英語学習",
]

TAGS = {
    ABC_ID: ["ABCソング", "アルファベット", *COMMON_TAGS],
    ANT_ID: ["ShortA", "短いA", *COMMON_TAGS],
    BAKER_ID: ["LongA", "MagicE", "ロングA", "マジックE", "BakerBear", "EngineerEgg", *COMMON_TAGS],
    AIDER_ID: ["AI", "AY", "LongA", "AiderSnail", "TeacherTacos", *COMMON_TAGS],
}


def site_line(lesson: int) -> str:
    return f"{SITE}/?book=phonics&lesson={lesson}"


def related(current_id: str) -> str:
    rows = [
        ("🎵 ABC ソング", ABC_ID),
        ("🐜 Short A", ANT_ID),
        ("🐻 Long A / Magic E", BAKER_ID),
        ("🐌 AI・AY", AIDER_ID),
    ]
    lines = []
    for label, vid in rows:
        if vid == current_id:
            continue
        lines.append(f"{label}: https://youtu.be/{vid}")
    return "\n".join(lines)


def desc_abc() -> str:
    return (
        f"{site_line(1)}\n"
        "↑ 歌詞・キャラクター紹介はこちら（公式ページ）\n"
        "\n"
        "🌈 ファニックス・アイランド〜A から Z までの26人のなかまたち〜 🌈\n"
        "\n"
        "A から Z までのアルファベットそれぞれに、ぴったりのキャラクターが登場！\n"
        "それぞれの音から始まる単語と動作を、リズムと歌で楽しく覚えられる、こども向けフォニックス・ソングです。\n"
        "\n"
        "──────────────\n"
        "👶 おすすめの使い方\n"
        "──────────────\n"
        "✅ 朝の会・帰りの会の BGM に\n"
        "✅ おうちで親子いっしょに歌って覚える\n"
        "✅ 各キャラの動作をまねしてみる\n"
        "\n"
        "──────────────\n"
        "📚 Funnics Island シリーズ\n"
        "──────────────\n"
        f"{related(ABC_ID)}\n"
        f"🔗 シリーズ一覧: {LINKS}\n"
        "\n"
        "#フォニックス #ABCソング #こども英語 #幼児英語 #FunnicsIsland #英語学習"
    )


def desc_ant() -> str:
    return (
        f"{site_line(2)}\n"
        "↑ 歌詞・単語カード・解説はこちら（公式ページ）\n"
        "\n"
        "🐜 アントおばさんと いっしょに、みじかい「a」の おとを おぼえよう！\n"
        "\n"
        "Cat / hat / ant / bag。\n"
        "Fat / mad / sad / black。\n"
        "ぜんぶ同じ、みじかい「あ」のおと（/æ/）です。\n"
        "\n"
        "──────────────\n"
        "🎵 きょうの 4 つの ぶん\n"
        "──────────────\n"
        "Fat cat in a hat\n"
        "Mad rat on a mat\n"
        "Sad ant at a plant\n"
        "Black bag with a flag\n"
        "\n"
        "──────────────\n"
        "📚 Funnics Island シリーズ\n"
        "──────────────\n"
        f"{related(ANT_ID)}\n"
        f"🔗 シリーズ一覧: {LINKS}\n"
        "\n"
        "#フォニックス #ShortA #こども英語 #幼児英語 #FunnicsIsland #英語学習"
    )


def desc_baker() -> str:
    return (
        f"{site_line(3)}\n"
        "↑ 歌詞・単語カード・解説はこちら（公式ページ）\n"
        "\n"
        "🐻 ベイカーベアと ふしぎな e で、ながい「A」の おとを おぼえよう！\n"
        "\n"
        "cap → cape、mat → mate、plan → plane。\n"
        "たんごのうしろに e をつけると、A のおとが「ア」から「エイ」にへんしんします。\n"
        "\n"
        "──────────────\n"
        "🪄 Magic E の 変身ペア\n"
        "──────────────\n"
        "cap → cape\n"
        "can → cane\n"
        "mat → mate\n"
        "plan → plane\n"
        "slat → slate\n"
        "\n"
        "──────────────\n"
        "📚 Funnics Island シリーズ\n"
        "──────────────\n"
        f"{related(BAKER_ID)}\n"
        f"🔗 シリーズ一覧: {LINKS}\n"
        "\n"
        "#フォニックス #LongA #MagicE #こども英語 #幼児英語 #FunnicsIsland #英語学習"
    )


def desc_aider() -> str:
    return (
        f"{site_line(4)}\n"
        "↑ 歌詞・単語カード・解説はこちら（公式ページ）\n"
        "\n"
        "🐌 エイダースネイルといっしょに、AI と AY の「エイ」のおとをおぼえよう！\n"
        "\n"
        "A と I がならぶと ay。\n"
        "A と Y がならんでも ay。\n"
        "バラバラではなく、ひとかたまりで見るのがポイントです。\n"
        "\n"
        "──────────────\n"
        "🔤 AI のたんご\n"
        "──────────────\n"
        "snail / trail / rain / train\n"
        "mail / pail / tail / sail\n"
        "paint / brain\n"
        "\n"
        "──────────────\n"
        "🔤 AY のたんご\n"
        "──────────────\n"
        "day / play / way / stay\n"
        "say / tray / May / hooray\n"
        "clay / gray\n"
        "\n"
        "──────────────\n"
        "📚 Funnics Island シリーズ\n"
        "──────────────\n"
        f"{related(AIDER_ID)}\n"
        f"🔗 シリーズ一覧: {LINKS}\n"
        "\n"
        "#フォニックス #AI #AY #LongA #こども英語 #幼児英語 #FunnicsIsland #英語学習"
    )


DESCRIPTIONS = {
    ABC_ID: desc_abc,
    ANT_ID: desc_ant,
    BAKER_ID: desc_baker,
    AIDER_ID: desc_aider,
}


def auth():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials

    creds = Credentials.from_authorized_user_file(str(ROOT / "token.json"), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        (ROOT / "token.json").write_text(creds.to_json())
    from googleapiclient.discovery import build

    return build("youtube", "v3", credentials=creds)


def update(yt, vid: str) -> None:
    cur = yt.videos().list(part="snippet", id=vid).execute()
    if not cur.get("items"):
        raise RuntimeError(f"Video not found: {vid}")
    snip = cur["items"][0]["snippet"]
    snip["title"] = TITLES[vid]
    snip["description"] = DESCRIPTIONS[vid]()
    snip["tags"] = TAGS[vid]
    snip["categoryId"] = "27"
    yt.videos().update(part="snippet", body={"id": vid, "snippet": snip}).execute()
    print(f"updated {vid}: {TITLES[vid]}")


def main() -> None:
    yt = auth()
    for vid in [ABC_ID, ANT_ID, BAKER_ID, AIDER_ID]:
        update(yt, vid)


if __name__ == "__main__":
    main()
