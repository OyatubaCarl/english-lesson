#!/usr/bin/env python3
"""Validate L17-L45 assets, captions inputs, and optional video outputs."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ALLOWED_BOKU = {(22, 6), (43, 3)}


def probe(path: Path) -> dict:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration:stream=codec_name,width,height,r_frame_rate",
            "-of", "json", str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def main() -> None:
    errors: list[str] = []
    summary: list[dict] = []
    for lesson in range(17, 46):
        lesson_dir = ROOT / f"L{lesson}"
        config_path = lesson_dir / "planning" / "lesson.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        lines = config["lines"]
        shots = config["shots"]
        if not (len(lines) == len(shots) == config["sentence_image_count"]):
            errors.append(f"L{lesson}: line/shot/count mismatch")
        expected = {lesson_dir / shot["image"] for shot in shots}
        actual = set((lesson_dir / "scenes").glob("*.png"))
        missing = sorted(expected - actual)
        if missing:
            errors.append(f"L{lesson}: missing {len(missing)} scene images")
        for index, line in enumerate(lines, start=1):
            if len(line["en_words"]) != len(line.get("word_indices", [])):
                errors.append(f"L{lesson} S{index}: display/timing group mismatch")
            flat = [item for group in line.get("word_indices", []) for item in group]
            if flat != line["indices"]:
                errors.append(f"L{lesson} S{index}: timing groups do not cover indices")
            if "ぼく" in line["ja"] and (lesson, index) not in ALLOWED_BOKU:
                errors.append(f"L{lesson} S{index}: unexpected ぼく in Mio narration")
        output = lesson_dir / "output" / f"{config['slug']}_mio_bilingual_camera.mp4"
        video_status = "pending"
        if output.exists():
            try:
                metadata = probe(output)
                video = next(stream for stream in metadata["streams"] if stream.get("width"))
                audio = next((stream for stream in metadata["streams"] if stream.get("codec_name") == "aac"), None)
                duration = float(metadata["format"]["duration"])
                if (video["width"], video["height"], video["r_frame_rate"]) != (1920, 1080, "30/1"):
                    errors.append(f"L{lesson}: invalid video geometry/rate")
                if audio is None:
                    errors.append(f"L{lesson}: AAC audio missing")
                if abs(duration - float(config["duration"])) > 0.12:
                    errors.append(f"L{lesson}: duration mismatch {duration}")
                video_status = "verified"
            except Exception as exc:  # noqa: BLE001
                errors.append(f"L{lesson}: video probe failed: {exc}")
        summary.append(
            {
                "lesson": lesson,
                "planned_images": len(expected),
                "present_images": len(expected & actual),
                "video": video_status,
            }
        )

    report = {"summary": summary, "errors": errors}
    report_path = ROOT / "shared" / "validation_l17_l45.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
