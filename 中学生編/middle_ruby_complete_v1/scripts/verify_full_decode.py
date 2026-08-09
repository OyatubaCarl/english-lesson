#!/usr/bin/env python3
"""Decode every current-edition middle video through EOF and record results."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "output"
COMBINED = ROOT / "combined"
EDITION = "v4_inline_canonical_vocab"


def probe(path: Path) -> dict:
    command = [
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration,size:stream=codec_type,codec_name,width,height,sample_rate,channels",
        "-of", "json", str(path),
    ]
    return json.loads(subprocess.run(command, check=True, capture_output=True, text=True).stdout)


def decode(path: Path) -> dict:
    command = [
        "ffmpeg", "-hide_banner", "-v", "error", "-xerror", "-i", str(path),
        "-map", "0:v:0", "-map", "0:a:0", "-f", "null", "-",
    ]
    completed = subprocess.run(command, capture_output=True, text=True)
    details = probe(path)
    return {
        "file": str(path),
        "status": "PASS" if completed.returncode == 0 else "FAIL",
        "video_audio_decode_through_eof": completed.returncode == 0,
        "returncode": completed.returncode,
        "stderr": completed.stderr.strip(),
        "probe": details,
    }


def individual_files() -> list[Path]:
    result = []
    for lesson in range(1, 46):
        matches = sorted(
            (OUTPUT / f"L{lesson:02d}").glob(
                f"*_mixed_japanese_full_ruby_{EDITION}.mp4"
            )
        )
        if len(matches) != 1:
            raise RuntimeError(f"L{lesson:02d}: expected one current-edition video, found {len(matches)}")
        result.append(matches[0])
    return result


def combined_files() -> list[Path]:
    result = []
    for start in (1, 16, 31):
        end = start + 14
        path = COMBINED / (
            f"middle_L{start:02d}-L{end:02d}_mixed_japanese_full_ruby_{EDITION}.mp4"
        )
        if not path.exists():
            raise RuntimeError(f"combined video is missing: {path}")
        result.append(path)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scope", choices=("individual", "combined", "all"), default="all"
    )
    args = parser.parse_args()
    paths = []
    if args.scope in {"individual", "all"}:
        paths.extend(individual_files())
    if args.scope in {"combined", "all"}:
        paths.extend(combined_files())

    results = []
    for index, path in enumerate(paths, start=1):
        print(f"[{index}/{len(paths)}] {path.name}", flush=True)
        results.append(decode(path))

    report = {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "edition": EDITION,
        "method": "ffmpeg -v error -xerror; decode video stream 0 and audio stream 0 through EOF",
        "scope": args.scope,
        "counts": {
            "total": len(results),
            "pass": sum(row["status"] == "PASS" for row in results),
            "fail": sum(row["status"] == "FAIL" for row in results),
        },
        "results": results,
    }
    suffix = {"individual": "INDIVIDUAL", "combined": "COMBINED", "all": "ALL"}[args.scope]
    report_path = COMBINED / f"FULL_DECODE_{suffix}_{EDITION.upper()}_20260803.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report["counts"], ensure_ascii=False))
    print(report_path)
    if report["counts"]["fail"]:
        raise SystemExit("one or more videos failed full decode")


if __name__ == "__main__":
    main()
