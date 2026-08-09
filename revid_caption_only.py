#!/usr/bin/env python3
"""Submit a public video URL to Revid 'caption-video' workflow.

This adds captions to an EXISTING video URL — it does NOT regenerate
visuals. Much cheaper than music-to-video. Required: source.url is a
public HTTPS mp4.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
ENV = (ROOT / ".env").read_text()
m = re.search(r'REVID_API_KEY="?([^"\n]+)"?', ENV)
if not m:
    print("ERROR: REVID_API_KEY missing from .env"); sys.exit(1)
API_KEY = m.group(1)

HDR = {
    "Content-Type": "application/json",
    "key": API_KEY,
    "User-Agent": (
        "Mozilla/5.0 (Macintosh) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/17.0 Safari/605.1.15"
    ),
    "Accept": "application/json",
}

# ── Edit these per project ────────────────────────────────────────
VIDEO_URL = "https://tmpfiles.org/dl/36019528/baker_bear_long_a_480p.mp4"
NAME = "Baker Bear and Magic E — Long A (captioned)"
# ──────────────────────────────────────────────────────────────────


def post(url: str, body: dict) -> tuple[int, dict | str]:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=HDR, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def get(url: str) -> tuple[int, dict | str]:
    req = urllib.request.Request(url, headers=HDR)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


payload = {
    "workflow": "caption-video",
    "source": {"url": VIDEO_URL},
    "captions": {
        "enabled": True,
        "preset": "Wrap 1",
        "position": "bottom",
        "autoCrop": False,
    },
    "options": {"hasToGenerateCover": False},
    "metadata": {"title": NAME, "name": NAME, "projectName": NAME},
    "aspectRatio": "16 / 9",
}

print(f"Submitting Revid caption-video: {NAME}")
print(f"  source: {VIDEO_URL}")
code, body = post("https://www.revid.ai/api/public/v3/render", payload)
print(f"  [{code}] response")
if isinstance(body, dict):
    pid = body.get("pid")
else:
    pid = None
if not pid:
    print("FAILED:", body); sys.exit(1)
print(f"  pid={pid}")

start = time.time()
while True:
    time.sleep(15)
    code, body = get(f"https://www.revid.ai/api/public/v3/status?pid={pid}")
    st = body.get("status") if isinstance(body, dict) else None
    print(f"  [{int(time.time() - start):4d}s] status={st}")
    if st == "ready":
        break
    if st in ("failed", "error"):
        print("FAILED:", body); sys.exit(1)

bd = {"pid": pid, "name": NAME, "projectName": NAME, "title": NAME}
c1, _ = post("https://www.revid.ai/api/public/v2/rename-project", bd)
time.sleep(3)
c2, _ = post("https://www.revid.ai/api/public/v2/rename-project", bd)
print(f"  rename: [{c1}][{c2}]")
print(f"\nDone. pid={pid}, total {int(time.time() - start)}s")
print(f"View on Revid: https://www.revid.ai/projects/{pid}")
