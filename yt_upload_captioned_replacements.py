"""Upload captioned replacement videos for Funnics Island lessons 1 and 2."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parent
SCOPES = ["https://www.googleapis.com/auth/youtube"]

ABC_VIDEO = ROOT / "dist" / "phonics-video" / "phonics_island_FINAL_480p_captioned.mp4"
ANT_VIDEO = ROOT / "dist" / "phonics-video" / "aunt_ant_short_a_480p_captioned.mp4"
BAKER_ID = "qvtc6srq1TI"

ABC_TITLE = (
    "ファニックス・アイランド　フォニックスとABCの仲間たち"
    "　〜Funnics Island ABC Song〜【歌詞字幕つき】"
)
ANT_TITLE = (
    "アントおばさんのみじかい「a」のおと "
    "〜Funnics Island Short A Song〜【歌詞字幕つき】"
)

ABC_TAGS = [
    "ABCソング", "FunnicsIsland", "ファニックスアイランド",
    "こども英語", "アルファベット", "フォニックス",
    "幼児英語", "英語の歌", "英語入門", "英語学習",
]
ANT_TAGS = [
    "FunnicsIsland", "ファニックスアイランド", "ShortA", "こども英語",
    "アルファベット", "フォニックス", "幼児英語", "短いA",
    "英語の歌", "英語入門", "英語学習",
]


def abc_description(ant_id: str) -> str:
    return (
        "🌈 ファニックス・アイランド〜A から Z までの26人のなかまたち〜 🌈\n"
        "\n"
        "A から Z までのアルファベットそれぞれに、ぴったりの動物キャラクターが登場！\n"
        "それぞれの音から始まる単語と動作を、リズムと歌で楽しく覚えられる、こども向けフォニックス・ソングです。\n"
        "この動画は、歌詞字幕を画面に入れた新しい版です。\n"
        "\n"
        "──────────────\n"
        "📖 歌詞・キャラクター紹介はこちら（公式ページ）\n"
        "──────────────\n"
        "👉 https://english-lesson.gasflare.workers.dev/?book=phonics\n"
        "動画と一緒に、26 人全員のイラスト・名前・歌詞を見られます。\n"
        "\n"
        "──────────────\n"
        "📚 関連動画（Funnics Island シリーズ） / サイト\n"
        "──────────────\n"
        "🐜 アントおばさんの みじかい「a」の おと（Short A）:\n"
        f"https://youtu.be/{ant_id}\n"
        "\n"
        "🐻 ベイカーベアと まほうの e（Long A / Magic E）:\n"
        f"https://youtu.be/{BAKER_ID}\n"
        "\n"
        "🌐 中学・高校英語の体系的学習サイト「うたとミックス」:\n"
        "https://english-lesson.gasflare.workers.dev/\n"
        "\n"
        "#フォニックス #英語の歌 #ABCソング #こども英語 #幼児英語 "
        "#アルファベット #FunnicsIsland #ファニックスアイランド #英語学習"
    )


def ant_description(abc_id: str) -> str:
    return (
        "🐜 アントおばさんと いっしょに、みじかい「a」の おとを おぼえよう！🐜\n"
        "\n"
        "「Cat」「Hat」「Ant」「Bag」…ぜんぶ おなじ、みじかい「あ」の おと（/æ/）。\n"
        "たった 4つの ぶんを、いれかえながら なんども くりかえして、リズムで おぼえるフォニックス ソングです。\n"
        "この動画は、歌詞字幕を画面に入れた新しい版です。\n"
        "\n"
        "──────────────\n"
        "📖 歌詞・くわしい解説はこちら（公式ページ）\n"
        "──────────────\n"
        "👉 https://english-lesson.gasflare.workers.dev/?book=phonics&lesson=2\n"
        "うたの ぜんぶの 歌詞、たんごのいちらん、クリックで はつおんを きける ページです。\n"
        "\n"
        "──────────────\n"
        "🎵 きょうの 4 つの ぶん 🎵\n"
        "──────────────\n"
        "① Fat cat in a hat\n"
        "② Mad rat on a mat\n"
        "③ Sad ant at a plant\n"
        "④ Black bag with a flag\n"
        "\n"
        "──────────────\n"
        "📚 関連動画（Funnics Island シリーズ） / サイト\n"
        "──────────────\n"
        "🎵 ABC ソング（26 人のなかまたち / Funnics Island ABC Song）:\n"
        f"https://youtu.be/{abc_id}\n"
        "\n"
        "🐻 ベイカーベアと まほうの e（Long A / Magic E）:\n"
        f"https://youtu.be/{BAKER_ID}\n"
        "\n"
        "🌐 中学・高校英語の体系的学習サイト「うたとミックス」:\n"
        "https://english-lesson.gasflare.workers.dev/\n"
        "\n"
        "#フォニックス #ShortA #英語の歌 #こども英語 #幼児英語 "
        "#アルファベット #FunnicsIsland #ファニックスアイランド #英語学習"
    )


def auth():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

    creds = Credentials.from_authorized_user_file(str(ROOT / "token.json"), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        (ROOT / "token.json").write_text(creds.to_json())
    from googleapiclient.discovery import build

    return build("youtube", "v3", credentials=creds)


def upload(yt, video: Path, title: str, description: str, tags: list[str]) -> str:
    from googleapiclient.http import MediaFileUpload

    if not video.exists():
        raise FileNotFoundError(video)
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "27",
            "defaultLanguage": "ja",
            "defaultAudioLanguage": "ja",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": True,
        },
    }
    media = MediaFileUpload(str(video), mimetype="video/mp4",
                            resumable=True, chunksize=8 * 1024 * 1024)
    request = yt.videos().insert(part="snippet,status", body=body,
                                 media_body=media)
    print(f"Uploading {video.name} ({video.stat().st_size // 1024 // 1024} MB)...")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  {int(status.progress() * 100)}%")
    vid = response["id"]
    print(f"Uploaded: https://youtu.be/{vid}")
    return vid


def update_description(yt, vid: str, title: str, description: str,
                       tags: list[str]) -> None:
    cur = yt.videos().list(part="snippet", id=vid).execute()
    if not cur["items"]:
        raise RuntimeError(f"video not found: {vid}")
    snip = cur["items"][0]["snippet"]
    snip["title"] = title
    snip["description"] = description
    snip["tags"] = tags
    snip["categoryId"] = "27"
    yt.videos().update(part="snippet", body={"id": vid, "snippet": snip}).execute()
    print(f"Updated description: https://youtu.be/{vid}")


def main() -> None:
    yt = auth()
    abc_id = upload(yt, ABC_VIDEO, ABC_TITLE, abc_description("pending"), ABC_TAGS)
    ant_id = upload(yt, ANT_VIDEO, ANT_TITLE, ant_description(abc_id), ANT_TAGS)
    update_description(yt, abc_id, ABC_TITLE, abc_description(ant_id), ABC_TAGS)
    print("")
    print(f"ABC_ID={abc_id}")
    print(f"ANT_ID={ant_id}")


if __name__ == "__main__":
    main()
