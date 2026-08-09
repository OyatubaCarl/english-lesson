"""URL/ハッシュタグなしの最小限テキストで投稿テスト。"""
import os
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

text = "テスト投稿"
print(f"posting: {text!r}")
try:
    res = client.create_tweet(text=text)
    print(f"OK tweet_id={res.data['id']}")
    print(f"URL: https://x.com/i/web/status/{res.data['id']}")
except Exception as e:
    print(f"FAILED: {e}")
