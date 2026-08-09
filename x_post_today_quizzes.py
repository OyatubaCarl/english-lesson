"""本日public化したクイズ動画(02-05)のX投稿を10分間隔で実行。

- YAMLから対象4件のtextを読む
- 1本目即投稿、以降10分間隔で計4本
- ローカル .env (x-scheduler/.env) を使って tweepy 経由でX APIへ
"""
from __future__ import annotations
import os
import sys
import time
from pathlib import Path

import yaml
import tweepy


ENV_PATH = Path("/Users/masaki/Workspace/projects/x-scheduler/.env")
YAML_PATH = Path("/Users/masaki/Documents/ClaudeCode/英語学習教材作成/shorts/x_posts/quizzes_2026-06.yaml")
LOG_PATH = Path("/Users/masaki/Documents/ClaudeCode/英語学習教材作成/shorts/x_posts/posted_log.txt")
TARGET_IDS = ["02_resilient", "03_ubiquitous", "04_scrutinize", "05_profound"]
INTERVAL_SEC = 600  # 10分


def load_env():
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def log(msg: str):
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def main():
    load_env()
    for k in ("X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET"):
        if not os.environ.get(k):
            sys.exit(f"ERROR: missing env {k}")

    entries = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8"))
    selected = []
    for tid in TARGET_IDS:  # 順序を保つ
        match = next((e for e in entries if tid in e["id"]), None)
        if match:
            selected.append(match)
    if len(selected) != 4:
        sys.exit(f"ERROR: 4件揃わず {len(selected)}件のみ")

    client = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_SECRET"],
    )

    log(f"開始: 計{len(selected)}件、{INTERVAL_SEC}秒間隔")
    for i, entry in enumerate(selected):
        if i > 0:
            log(f"  待機 {INTERVAL_SEC}秒 ({INTERVAL_SEC//60}分)...")
            time.sleep(INTERVAL_SEC)
        text = entry["text"].rstrip()
        chars = len(text)
        log(f"[{i+1}/{len(selected)}] {entry['id']} ({chars}字) 投稿中...")
        try:
            res = client.create_tweet(text=text)
            tid = res.data.get("id")
            log(f"  ✓ tweet_id={tid}  https://x.com/i/web/status/{tid}")
        except tweepy.TweepyException as e:
            log(f"  ✗ FAILED: {e}")
    log("完了。")


if __name__ == "__main__":
    main()
