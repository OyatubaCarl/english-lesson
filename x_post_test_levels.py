"""4段階の切り分けテスト投稿。失敗したらそこで停止。
- Level1: クイズ本文+選択肢のみ (URL/タグなし)
- Level2: +YouTube URL 1つ
- Level3: +公式サイトURL もう1つ
- Level4: +ハッシュタグ
"""
import os
import time
from pathlib import Path
import tweepy

ENV = Path("/Users/masaki/Workspace/projects/x-scheduler/.env")
for line in ENV.read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

client = tweepy.Client(
    consumer_key=os.environ["X_API_KEY"],
    consumer_secret=os.environ["X_API_SECRET"],
    access_token=os.environ["X_ACCESS_TOKEN"],
    access_token_secret=os.environ["X_ACCESS_SECRET"],
)

BASE = """【超難単語が一発で覚えられる裏技】

あの町は大きな被害を受けたけれど、人々は驚くほど resilient で、たった3年で復興した。

“resilient” の意味は?
A 脆い  B 怒りっぽい  C 立ち直る力のある  D 平凡な"""

YT = "https://youtube.com/shorts/3KWf9Y3nUx0"
SITE = "https://english-lesson.gasflare.workers.dev/"
TAGS = "#英語学習 #英単語 #英語クイズ #resilient"

LEVELS = [
    ("L1: 本文+選択肢のみ", BASE),
    ("L2: +YouTube URL", BASE + f"\n\n📺 答え→ {YT}"),
    ("L3: +サイトURL", BASE + f"\n\n📺 答え→ {YT}\n🌐 {SITE}"),
    ("L4: +ハッシュタグ(本物の投稿想定)", BASE + f"\n\n📺 答え→ {YT}\n🌐 {SITE}\n\n{TAGS}"),
]

tweet_ids = []
for label, text in LEVELS:
    print(f"\n{label}  ({len(text)}字)")
    print("-" * 50)
    print(text[:120] + ("..." if len(text) > 120 else ""))
    try:
        res = client.create_tweet(text=text)
        tid = res.data["id"]
        tweet_ids.append((label, tid))
        print(f"  ✓ OK  tweet_id={tid}")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        print(f"\n→ {label} で停止。これ以降のテストは行わない。")
        break
    time.sleep(45)  # 連投制限回避のため少し間隔

print("\n=== 投稿された tweet_ids (あとで削除可能) ===")
for label, tid in tweet_ids:
    print(f"  {label}: https://x.com/i/web/status/{tid}")
