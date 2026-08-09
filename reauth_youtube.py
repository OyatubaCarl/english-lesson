"""YouTube OAuth 再認証 — コメント投稿に必要な youtube.force-ssl スコープを追加する。

これまでの token.json は `youtube` スコープのみで、コメント投稿(commentThreads.insert)が
403 (insufficient scopes) になる。このスクリプトで youtube + youtube.force-ssl を要求し直す。
アップロード等の既存機能もそのまま使える(force-ssl は上位互換)。

使い方:
    cd /Users/masaki/Documents/ClaudeCode/英語学習教材作成
    .venv/bin/python reauth_youtube.py
  → ブラウザが自動で開く → 対象のYouTubeアカウントでログイン → 「許可」
  → token.json が更新される(既存はバックアップ)
"""
from pathlib import Path
import shutil
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]
ROOT = Path(__file__).resolve().parent
CRED = ROOT / "credentials.json"
TOKEN = ROOT / "token.json"


def main() -> None:
    if not CRED.exists():
        raise SystemExit(f"credentials.json が見つかりません: {CRED}")
    if TOKEN.exists():
        bak = TOKEN.with_name("token.json.bak-reauth")
        shutil.copy(TOKEN, bak)
        print(f"既存 token.json をバックアップ: {bak.name}")
    flow = InstalledAppFlow.from_client_secrets_file(str(CRED), SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent")
    TOKEN.write_text(creds.to_json())
    print("\n✓ token.json を更新しました")
    print("  scopes:", creds.scopes)


if __name__ == "__main__":
    main()
