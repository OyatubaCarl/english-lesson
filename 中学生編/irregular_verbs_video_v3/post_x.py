#!/usr/bin/env python3
"""Post the newly published irregular-verbs v6 URL to Teacher Tacos on X."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import tweepy


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output"
METADATA = OUTPUT / "youtube_x_metadata.json"
RESULT = OUTPUT / "publish_result.json"
ENV = Path("/Users/masaki/Workspace/projects/x-scheduler/.env")
EXPECTED_NAME = "ティーチャータコス"
EXPECTED_USERNAME = "iHzKyC6Sdt2632"


def main() -> None:
    for raw in ENV.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())

    client = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_SECRET"],
    )
    me = client.get_me(user_auth=True, user_fields=["name", "username"]).data
    if me.name != EXPECTED_NAME or me.username != EXPECTED_USERNAME:
        raise SystemExit(f"Wrong X account: {me.name} (@{me.username})")
    print(f"X account: {me.name} (@{me.username})", flush=True)

    spec = json.loads(METADATA.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    youtube = result["youtube"]
    if youtube.get("privacy_status") != "public":
        raise SystemExit("YouTube video is not recorded as public")

    text = spec["x"]["text_template"].format(youtube_url=youtube["url"])
    if len(text) > 280:
        raise SystemExit(f"X text is too long: {len(text)} characters")
    response = client.create_tweet(text=text)
    tweet_id = str(response.data["id"])
    result["x"] = {
        "tweet_id": tweet_id,
        "url": f"https://x.com/{me.username}/status/{tweet_id}",
        "account_name": me.name,
        "account_username": me.username,
        "text": text,
        "posted_at": datetime.now(timezone.utc).isoformat(),
    }
    result["updated_at"] = datetime.now(timezone.utc).isoformat()
    RESULT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"POSTED: {result['x']['url']}", flush=True)


if __name__ == "__main__":
    main()
