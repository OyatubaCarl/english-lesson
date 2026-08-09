#!/usr/bin/env python3
"""Add captions to the Outlaw Octopus video via Revid caption-video.

Based on the proven revid_caption_only.py flow in this project
(www.revid.ai/api/public/v3, workflow=caption-video, key header + UA).
Adds captions to an EXISTING public video URL — does NOT regenerate visuals.

Edit VIDEO_URL to the public (tmpfiles) mp4, then run:
    python3 revid_caption_octopus.py
"""
from __future__ import annotations

import json
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

# ── octopus params ────────────────────────────────────────────────
VIDEO_URL = "https://tmpfiles.org/dl/wWwswyDFFrgX/outlaw_octopus_1080p_nosubs.mp4"
NAME = "Outlaw Octopus — Short O (captioned)"
# Download captioned result here if the status exposes a URL:
OUT = Path("/Users/masaki/Documents/ClaudeCode/FunnicsIsland/songs/22_outlaw_octopus_short_o/final_captioned.mp4")
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


def find_video_url(d: dict) -> str | None:
    """Search a status dict for a downloadable mp4 URL under common keys."""
    for k in ("videoUrl", "video_url", "url", "downloadUrl", "resultUrl",
              "output", "outputUrl", "renderUrl", "mp4"):
        v = d.get(k)
        if isinstance(v, str) and v.startswith("http"):
            return v
    # nested
    for v in d.values():
        if isinstance(v, dict):
            found = find_video_url(v)
            if found:
                return found
    return None


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
pid = body.get("pid") if isinstance(body, dict) else None
if not pid:
    print("FAILED:", body); sys.exit(1)
print(f"  pid={pid}")

start = time.time()
ready_body: dict = {}
while True:
    time.sleep(15)
    code, body = get(f"https://www.revid.ai/api/public/v3/status?pid={pid}")
    st = body.get("status") if isinstance(body, dict) else None
    print(f"  [{int(time.time() - start):4d}s] status={st}")
    if st == "ready":
        ready_body = body if isinstance(body, dict) else {}
        break
    if st in ("failed", "error"):
        print("FAILED:", body); sys.exit(1)
    if time.time() - start > 900:
        print("TIMEOUT after 900s"); sys.exit(1)

bd = {"pid": pid, "name": NAME, "projectName": NAME, "title": NAME}
c1, _ = post("https://www.revid.ai/api/public/v2/rename-project", bd)
time.sleep(3)
c2, _ = post("https://www.revid.ai/api/public/v2/rename-project", bd)
print(f"  rename: [{c1}][{c2}]")

print("\n--- ready status payload ---")
print(json.dumps(ready_body, ensure_ascii=False, indent=2)[:1500])

dl = find_video_url(ready_body)
if dl:
    print(f"\nDownloading captioned video: {dl}")
    try:
        req = urllib.request.Request(dl, headers={"User-Agent": HDR["User-Agent"]})
        with urllib.request.urlopen(req, timeout=300) as r, OUT.open("wb") as f:
            f.write(r.read())
        print(f"  saved -> {OUT} ({OUT.stat().st_size // 1024 // 1024} MB)")
    except Exception as e:
        print(f"  download failed ({e}); get it from the Revid UI link below.")
else:
    print("\nNo direct download URL in status; download from the Revid UI.")

print(f"\nDone. pid={pid}, total {int(time.time() - start)}s")
print(f"View / download on Revid: https://www.revid.ai/projects/{pid}")
