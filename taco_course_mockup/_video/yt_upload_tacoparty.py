#!/usr/bin/env python3
"""タコス・パーティーの動画2本を Teacher Tacos English チャンネルへ公開アップロード。
 - 縦型ショート（Public / #Shorts）
 - フル版プレイ動画（Public）
"""
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

PROJ = Path("/Users/masaki/Documents/ClaudeCode/英語学習教材作成")
TOKEN = PROJ / "token.json"
VID = PROJ / "taco_course_mockup/_video"

APP_URL = "https://taco-course.pages.dev"
WT_URL = "https://words.teachertacos.com"

SHORT = {
    "file": VID / "taco_party_short_vertical.mp4",
    "title": "英語の1レッスンを“まるごと完食”する無料アプリ🌮 タコス・パーティー #Shorts",
    "description": (
        "歌・単語・文法・音読・並べ替え。5つのミニゲームで具材を集めて、"
        "英語の1レッスンを1個のタコスに“完食”する無料アプリ「タコス・パーティー」。\n\n"
        f"▶ ブラウザだけで無料で遊べます: {APP_URL}\n"
        f"▶ 姉妹アプリ WordTacos（英単語クイズ）: {WT_URL}\n\n"
        "#英語学習 #Shorts #英語 #タコス #無料アプリ #英単語 #中学英語"
    ),
    "tags": ["英語学習", "英語", "タコス", "無料アプリ", "英単語", "中学英語", "Shorts"],
}

FULL = {
    "file": VID / "taco_party_lesson1.mp4",
    "title": "タコス・パーティー｜英語の1レッスンを5つのミニゲームで“完食”【無料アプリ・プレイ動画】",
    "description": (
        "「タコス・パーティー」は、歌とミニゲームで英語を学ぶ無料アプリです。"
        "ひとつのレッスン（1つの英文）を、5つのミニゲームで具材を集めながら、最後に1個のタコスに仕上げます。\n\n"
        "この動画では、入門レッスン「Tom at the Gate」を最初から最後まで通してプレイしています。\n"
        "・タコビート（リズム）／トマトマト（新出単語）／チーズ・シャドウイング（音読）／"
        "サルサ・グラマー（文法）／シャキシャキ・レタス（並べ替え）→ タコス完成\n\n"
        f"▶ 無料で遊べます: {APP_URL}\n"
        f"▶ WordTacos（英単語クイズ）: {WT_URL}\n\n"
        "#英語学習 #英語 #タコス #無料アプリ #英文法 #中学英語"
    ),
    "tags": ["英語学習", "英語", "タコス", "無料アプリ", "英文法", "中学英語", "Teacher Tacos"],
}


def auth():
    creds = Credentials.from_authorized_user_file(str(TOKEN))
    if not creds.valid:
        creds.refresh(Request())
        json.dump(json.loads(creds.to_json()), open(TOKEN, "w"))
    return build("youtube", "v3", credentials=creds)


def upload(yt, spec, privacy="public"):
    body = {
        "snippet": {
            "title": spec["title"],
            "description": spec["description"],
            "tags": spec["tags"],
            "categoryId": "27",           # Education
        },
        "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False},
    }
    media = MediaFileUpload(str(spec["file"]), chunksize=-1, resumable=True, mimetype="video/mp4")
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
    vid = resp["id"]
    print(f"  UPLOADED {spec['file'].name} -> https://youtu.be/{vid}")
    return vid


def main():
    yt = auth()
    out = {}
    print("[1/2] short (public)")
    out["short_id"] = upload(yt, SHORT, "public")
    print("[2/2] full (public)")
    out["full_id"] = upload(yt, FULL, "public")
    out["short_url"] = "https://youtu.be/" + out["short_id"]
    out["full_url"] = "https://youtu.be/" + out["full_id"]
    json.dump(out, open(VID / "upload_result.json", "w"), ensure_ascii=False, indent=2)
    print("RESULT:", json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
