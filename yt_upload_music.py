"""
「英語は歌で覚えるとなぜ脳に残るのか」ナレーション動画を YouTube に限定公開(unlisted)でアップロード。
認証は同ディレクトリの token.json（OAuth・refresh_token入り）を再利用。
実行: python3 yt_upload_music.py
"""
from __future__ import annotations
import sys
from pathlib import Path

PROJ = Path(__file__).resolve().parent
VIDEO = PROJ / "英語は歌で覚える_narrated.mp4"
TOKEN = PROJ / "token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]

TITLE = "英語は「歌で覚える」となぜ脳に残るのか｜音楽と第二言語習得の神経科学"

DESCRIPTION = (
    "歌で英語を覚えるのは「楽しいだけ」なのでしょうか。覚えたい英文そのものを歌として聴くとき、"
    "音楽は学習の邪魔ではなく、音韻・リズム・記憶・発声・感情をひとつに束ねる「足場」になります。"
    "その理由を、第二言語習得・認知心理学・神経科学の知見から順番に解説します。\n"
    "\n"
    "最後に、この考え方を教材にした英語学習サイト「Teacher Tacos English / Funnics Island」の"
    "「歌で覚える」入り口も紹介します。\n"
    "\n"
    "──────────────\n"
    "🔗 Teacher Tacos English / Funnics Island\n"
    "──────────────\n"
    "🌐 サイト: https://english-lesson.gasflare.workers.dev/\n"
    "▶️ チャンネル（動画一覧）: https://www.youtube.com/@teachertacosenglish\n"
    "🎵 フォニックスの歌（ABC・発音・英語の音）: https://www.youtube.com/playlist?list=PLES7tSW4fjkYWBcZBHORh65_EEwdo3dEw\n"
    "📘 入門 Funnics Island（B1–B20）: https://www.youtube.com/playlist?list=PLES7tSW4fjkZP5l_t3N0oMy3o89VtcHIL\n"
    "\n"
    "──────────────\n"
    "📌 章立て\n"
    "──────────────\n"
    "0:00 オープニング\n"
    "0:18 結論：歌は「第二の記憶ルート」\n"
    "0:38 「音韻は右脳」は半分だけ正しい\n"
    "1:02 言語と音楽は脳の資源を共有する（SSIRH）\n"
    "1:26 歌は英文を「二重に」記憶させる\n"
    "2:01 英語のリズムは歌と相性がいい\n"
    "2:20 頭の中で勝手に流れる（din in the head）\n"
    "2:39 ただしBGMの歌詞入り音楽は別問題\n"
    "3:02 音楽は新しい言語回路の「足場」になる\n"
    "3:26 「楽しい」は最強の学習条件\n"
    "3:46 Teacher Tacos English / Funnics Island\n"
    "4:05 フォニックス：歌で音を覚える\n"
    "4:27 おすすめの学習順\n"
    "4:48 まとめ\n"
    "5:15 参考文献\n"
    "\n"
    "──────────────\n"
    "📚 主な参考文献\n"
    "──────────────\n"
    "・Patel, A. D. (2003). Language, music, syntax and the brain. Nature Neuroscience.\n"
    "・Ludke, Ferreira & Overy (2014). Singing can facilitate foreign language learning. Memory & Cognition.\n"
    "・Salcedo (2010). The Effects of Songs ... Involuntary Mental Rehearsal.\n"
    "・Merrett, Peretz & Wilson (2014). Mechanisms in Melodic Intonation Therapy.\n"
    "・Herholz & Zatorre (2012). Musical training as a framework for brain plasticity. Neuron.\n"
    "・Lehmann & Seufert (2017). The Influence of Background Music on Learning.\n"
    "\n"
    "⚠️ 本動画は教育目的の一般的な解説です。神経科学・第二言語習得には研究途上の知見も含まれます。\n"
    "\n"
    "#英語学習 #フォニックス #歌で覚える英語 #第二言語習得 #リスニング #発音 #FunnicsIsland"
)

TAGS = [
    "英語学習", "フォニックス", "歌で覚える英語", "第二言語習得",
    "音楽と言語", "神経科学", "リスニング", "発音", "英語の歌",
    "強勢拍リズム", "二重符号化", "Funnics Island", "Teacher Tacos English",
]


def auth():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN.write_text(creds.to_json())
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
            "categoryId": "27",  # Education
            "defaultLanguage": "ja",
            "defaultAudioLanguage": "ja",
        },
        "status": {
            "privacyStatus": "unlisted",
            "selfDeclaredMadeForKids": False,
        },
    }
    from googleapiclient.http import MediaFileUpload
    media = MediaFileUpload(str(VIDEO), mimetype="video/mp4",
                            resumable=True, chunksize=8 * 1024 * 1024)
    request = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    print(f"Uploading {VIDEO.name} ({VIDEO.stat().st_size // 1024 // 1024} MB)…", flush=True)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  {int(status.progress() * 100)}%", flush=True)
    vid = response["id"]
    print(f"\nUploaded video id: {vid}", flush=True)
    print(f"  https://youtu.be/{vid}", flush=True)
    print("  (privacy: unlisted／限定公開 — 確認後 YouTube Studio で公開に変更できます)", flush=True)


if __name__ == "__main__":
    main()
