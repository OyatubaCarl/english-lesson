"""1本だけテスト投稿 (引数で quiz_id 指定)。
動作確認用。投稿成功なら tweet_id を出す。

usage: python3 x_post_test_one.py 02_resilient
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

import yaml
import tweepy

ENV_PATH = Path("/Users/masaki/Workspace/projects/x-scheduler/.env")
YAML_PATH = Path("/Users/masaki/Documents/ClaudeCode/英語学習教材作成/shorts/x_posts/quizzes_2026-06.yaml")
LOG_PATH = Path("/Users/masaki/Documents/ClaudeCode/英語学習教材作成/shorts/x_posts/posted_log.txt")


def load_env():
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def log(msg: str):
    import time
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: python3 x_post_test_one.py <quiz_id>")
    target = sys.argv[1]
    load_env()
    entries = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8"))
    entry = next((e for e in entries if target in e["id"]), None)
    if not entry:
        sys.exit(f"not found: {target}")

    client = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_SECRET"],
    )
    text = entry["text"].rstrip()
    log(f"テスト投稿 [{entry['id']}] ({len(text)}字)...")
    try:
        res = client.create_tweet(text=text)
        tid = res.data.get("id")
        log(f"  ✓ tweet_id={tid}  https://x.com/i/web/status/{tid}")
    except Exception as e:
        log(f"  ✗ FAILED: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
