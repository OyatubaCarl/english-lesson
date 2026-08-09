#!/usr/bin/env python3
"""Verify rendered high-school videos against adopted audio and exact lyrics."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path


HERE = Path(__file__).resolve().parent
PIPELINE = HERE.parent
PROJECT = PIPELINE.parent.parent
MANIFEST = PIPELINE / "planning" / "adopted_songs_h001_h160.json"
PROGRESS = PIPELINE / "planning" / "high_video_progress.json"


def plain_caption(text: str) -> str:
    text = re.sub(r"</?k>", "", text)
    return text.replace(r"\N", " ").strip()


def probe(path: Path) -> dict:
    command = [
        "ffprobe", "-v", "error", "-show_streams", "-show_format",
        "-of", "json", str(path),
    ]
    return json.loads(subprocess.run(command, check=True, capture_output=True, text=True).stdout)


def verify_lesson(number: int, manifest_row: dict) -> dict:
    lesson = f"H{number:03d}"
    root = PIPELINE / lesson
    plan_path = root / "planning" / "video_plan.json"
    checks: dict[str, bool] = {"plan_exists": plan_path.exists()}
    result: dict = {"lesson": lesson, "checks": checks, "status": "NOT_RENDERED"}
    if not plan_path.exists():
        return result

    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    expected_lyrics = manifest_row["lyrics_lines"]
    actual_lyrics = [plain_caption(row["en"]) for row in plan["captions"]]
    checks["exact_adopted_lyrics"] = actual_lyrics == expected_lyrics
    checks["caption_times_valid"] = all(
        0 <= float(row["start"]) < float(row["end"]) <= float(plan["duration"]) + 0.05
        for row in plan["captions"]
    )
    checks["caption_times_monotonic"] = all(
        float(current["start"]) >= float(previous["start"])
        for previous, current in zip(plan["captions"], plan["captions"][1:])
    )
    checks["scene_times_monotonic"] = (
        float(plan["scenes"][0]["start"]) == 0.0
        and all(
            float(current["start"]) > float(previous["start"])
            for previous, current in zip(plan["scenes"], plan["scenes"][1:])
        )
    )
    checks["scene_images_exist"] = all((root / row["image"]).exists() for row in plan["scenes"])
    audio_path = (root / plan["audio"]).resolve()
    manifest_audio = (PROJECT / manifest_row["audio"]["path"]).resolve()
    checks["adopted_audio_selected"] = audio_path == manifest_audio
    checks["adopted_audio_exists"] = audio_path.exists()
    checks["source_qa_recorded"] = bool(plan.get("source_qa")) or number == 1
    # The canonical manifest also records the user's stop-after-three rule and
    # manually adopted songs as accepted terminal statuses.
    checks["adoption_status_recorded"] = bool(manifest_row.get("qa_status"))

    output_path = root / "output" / plan["output_name"]
    result["output"] = str(output_path.relative_to(PROJECT))
    checks["output_exists"] = output_path.exists()
    if output_path.exists():
        info = probe(output_path)
        video = next((row for row in info["streams"] if row.get("codec_type") == "video"), {})
        audio = next((row for row in info["streams"] if row.get("codec_type") == "audio"), {})
        actual_duration = float(info["format"]["duration"])
        expected_duration = float(plan["duration"])
        result["media"] = {
            "duration_seconds": actual_duration,
            "expected_seconds": expected_duration,
            "duration_delta_seconds": round(actual_duration - expected_duration, 6),
            "width": video.get("width"),
            "height": video.get("height"),
            "video_codec": video.get("codec_name"),
            "audio_codec": audio.get("codec_name"),
        }
        checks["duration_matches"] = abs(actual_duration - expected_duration) <= 0.08
        checks["video_1920x1080_h264"] = (
            video.get("width") == 1920 and video.get("height") == 1080 and video.get("codec_name") == "h264"
        )
        checks["audio_aac"] = audio.get("codec_name") == "aac"

    result["status"] = "PASS" if checks.get("output_exists") and all(checks.values()) else (
        "FAIL" if checks.get("output_exists") else "NOT_RENDERED"
    )
    verification_path = root / "output" / "VERIFICATION.json"
    verification_path.parent.mkdir(parents=True, exist_ok=True)
    verification_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("lessons", nargs="*", type=int, help="lesson numbers; default H1-H160 except H46")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = {int(row["lesson"][1:]): row for row in manifest["lessons"]}
    numbers = args.lessons or [number for number in range(1, 161) if number != 46]
    results = [verify_lesson(number, rows[number]) for number in numbers]
    completed = [row["lesson"] for row in results if row["status"] == "PASS"]
    failed = [row["lesson"] for row in results if row["status"] == "FAIL"]
    not_rendered = [row["lesson"] for row in results if row["status"] == "NOT_RENDERED"]
    progress = {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "scope": "H001-H160; H046 is tracked in its established ImageGen project",
        "counts": {
            "verified_pass": len(completed),
            "failed": len(failed),
            "not_rendered": len(not_rendered),
        },
        "verified_pass": completed,
        "failed": failed,
        "not_rendered": not_rendered,
        "results": results,
    }
    PROGRESS.write_text(json.dumps(progress, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(progress["counts"], ensure_ascii=False))
    if failed:
        raise SystemExit(f"verification failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
