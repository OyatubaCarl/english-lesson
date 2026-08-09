#!/usr/bin/env python3
"""Download recorded Suno candidates from the official Suno audio CDN."""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


def download_one(lesson: int, url: str, output: Path) -> dict:
    song_id_match = re.search(r"/song/([0-9a-f-]+)", url)
    if not song_id_match:
        raise ValueError(f"Could not extract song id from {url}")
    song_id = song_id_match.group(1)
    cdn_url = f"https://cdn1.suno.ai/{song_id}.mp3"
    output.parent.mkdir(parents=True, exist_ok=True)

    if output.exists() and output.stat().st_size > 50_000:
        return {"lesson": lesson, "status": "existing", "bytes": output.stat().st_size}

    temporary = output.with_suffix(output.suffix + ".part")
    request = urllib.request.Request(cdn_url, headers={"User-Agent": "Mozilla/5.0"})
    last_error = None
    for attempt in range(1, 5):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                data = response.read()
            break
        except Exception as error:
            last_error = error
            if attempt == 4:
                raise
            time.sleep(attempt * 3)
    else:
        raise RuntimeError(f"Download failed: {last_error}")
    if len(data) <= 50_000:
        raise ValueError(f"Downloaded audio is unexpectedly small: H{lesson:03d}, {len(data)} bytes")
    temporary.write_bytes(data)
    temporary.replace(output)
    return {"lesson": lesson, "status": "downloaded", "bytes": len(data)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--progress", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--candidate", choices=("first", "backup", "third"), default="first")
    parser.add_argument("--start", type=int, default=48)
    parser.add_argument("--end", type=int, default=160)
    parser.add_argument("--lessons", help="Comma-separated lesson numbers; overrides start/end")
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()

    data = json.loads(args.progress.read_text(encoding="utf-8"))
    label = {"first": "candidate1", "backup": "candidate2", "third": "candidate3"}[args.candidate]
    lessons = (
        [int(value) for value in args.lessons.split(",") if value.strip()]
        if args.lessons
        else list(range(args.start, args.end + 1))
    )
    tasks = []
    for lesson in lessons:
        row = data["lessons"][str(lesson)]
        output = args.output_root / f"H{lesson:03d}" / f"{label}-full.mp3"
        tasks.append((lesson, row[args.candidate], output))

    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(download_one, lesson, url, output): lesson
            for lesson, url, output in tasks
        }
        for future in as_completed(futures):
            lesson = futures[future]
            try:
                result = future.result()
                results.append(result)
                print(
                    f"H{lesson:03d} {result['status']} {result['bytes']} bytes",
                    flush=True,
                )
            except Exception as error:
                print(f"H{lesson:03d} ERROR {error}", flush=True)
                raise

    total_bytes = sum(row["bytes"] for row in results)
    print(json.dumps({
        "candidate": args.candidate,
        "count": len(results),
        "bytes": total_bytes,
    }, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
