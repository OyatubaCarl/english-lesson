"""Upload the Outlaw Octopus Short O video (box-highlight captions) to YouTube.

Uploads as 'unlisted' by default (set PRIVACY env to 'public' to publish directly).
Uses the box-highlight (kinetic) bilingual caption build.
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent
VIDEO = Path(
    "/Users/masaki/Documents/ClaudeCode/FunnicsIsland/songs/"
    "22_outlaw_octopus_short_o/final_captioned_kinetic.mp4"
)
SCOPES = ["https://www.googleapis.com/auth/youtube"]
PRIVACY = os.environ.get("PRIVACY", "unlisted")  # 'unlisted' or 'public'

TITLE = (
    "アウトローオクトパスのみじかい「o」のおと "
    "〜Funnics Island Short O Song〜【歌詞字幕つき】"
)

DESCRIPTION = (
    "🐙 アウトローオクトパスと いっしょに、みじかい「o」の おとを おぼえよう！🐙\n"
    "\n"
    "「octopus」「hot」「pot」「stop」「mop」「rock」「frog」「fox」「box」「clock」…\n"
    "ぜんぶ おなじ、くちを おおきく あけて いう みじかい「お＝あっ」の おと（/ɒ/）です。\n"
    "みかけは こわそうな outlaw（アウトロー）、でも こころは やさしい オクトパスが、\n"
    "こまっている なかまを つぎつぎ たすけます。リズムで おぼえる フォニックス ソング。\n"
    "\n"
    "👉 単語ごとに リズムに 合わせた キネティック字幕（四角ハイライト）＋日本語訳つき！\n"
    "\n"
    "──────────────\n"
    "📖 歌詞・くわしい解説はこちら（公式ページ）\n"
    "──────────────\n"
    "👉 https://english-lesson.gasflare.workers.dev/?book=phonics&lesson=5\n"
    "うたの ぜんぶの 歌詞、たんごのいちらん、クリックで はつおんを きける ページです。\n"
    "\n"
    "──────────────\n"
    "🎵 ストーリー（3つの たすけ）🎵\n"
    "──────────────\n"
    "① あつい なべの そばの かえるを たすける（-ot / -op）\n"
    "② きりの なかで まいごの いぬを さがす（-og / -ox）\n"
    "③ いわの うえで うごけない きつねを たすける（-ock）\n"
    "\n"
    "──────────────\n"
    "🔤 きょう おぼえる みじかい O の たんご\n"
    "──────────────\n"
    "-ot / -op: hot / pot / stop / mop / top / drop / pop\n"
    "-og / -ox: dog / log / frog / fog / fox / box\n"
    "-ock: rock / knock / sock / block / clock\n"
    "\n"
    "──────────────\n"
    "👶 おすすめの つかいかた\n"
    "──────────────\n"
    "✅ くちを 大きく あけて「あっ」と いってみる\n"
    "✅ 「O」は「オー」では なく みじかい「あ」！\n"
    "✅ Short A（アントおばさん）の レッスンと くらべて ちがいに きづく\n"
    "\n"
    "──────────────\n"
    "📚 関連動画（Funnics Island シリーズ） / サイト\n"
    "──────────────\n"
    "🎵 ABC ソング（26 人のなかまたち / Funnics Island ABC Song）:\n"
    "https://youtu.be/pAt-35463Kk\n"
    "\n"
    "🐜 アントおばさんの みじかい「a」の おと（Short A）:\n"
    "https://youtu.be/eGTZmwdWmA0\n"
    "\n"
    "🐻 ベイカーベアと まほうの e（Long A / Magic E）:\n"
    "https://youtu.be/qvtc6srq1TI\n"
    "\n"
    "🌐 公式サイト（うたとミックス / Teacher Tacos English）:\n"
    "https://english-lesson.gasflare.workers.dev/\n"
    "\n"
    "#フォニックス #ShortO #ショートO #英語の歌 #こども英語 #幼児英語 "
    "#FunnicsIsland #ファニックスアイランド #OutlawOctopus #ティーチャータコス #英語学習"
)

TAGS = [
    "FunnicsIsland", "ファニックスアイランド", "ShortO", "ショートO",
    "こども英語", "フォニックス", "幼児英語", "短いO",
    "英語の歌", "英語入門", "英語学習", "OutlawOctopus", "アウトローオクトパス",
    "ティーチャータコス", "Teacher Tacos", "TeacherTacos",
]


def auth():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    creds = Credentials.from_authorized_user_file(str(ROOT / "token.json"),
                                                  SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        (ROOT / "token.json").write_text(creds.to_json())
    from googleapiclient.discovery import build
    return build("youtube", "v3", credentials=creds)


def main() -> None:
    if not VIDEO.exists():
        print(f"ERROR: {VIDEO} not found", file=sys.stderr)
        sys.exit(1)
    yt = auth()

    body = {
        "snippet": {
            "title": TITLE,
            "description": DESCRIPTION,
            "tags": TAGS,
            "categoryId": "27",          # Education
            "defaultLanguage": "ja",
            "defaultAudioLanguage": "ja",
        },
        "status": {
            "privacyStatus": PRIVACY,
            "selfDeclaredMadeForKids": True,
        },
    }

    from googleapiclient.http import MediaFileUpload
    media = MediaFileUpload(str(VIDEO), mimetype="video/mp4",
                            resumable=True, chunksize=8 * 1024 * 1024)
    request = yt.videos().insert(part="snippet,status", body=body,
                                 media_body=media)
    print(f"Uploading {VIDEO.name} ({VIDEO.stat().st_size // 1024 // 1024} MB) as {PRIVACY}…")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  {int(status.progress() * 100)}%")
    print(f"\nUploaded video id: {response['id']}")
    print(f"  https://youtu.be/{response['id']}")


if __name__ == "__main__":
    main()
