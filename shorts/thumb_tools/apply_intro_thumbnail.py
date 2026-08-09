#!/usr/bin/env python3
"""新規Shorts動画の冒頭にサムネ画像をオーバーレイする後処理。

Shortsフィードのサムネは動画の最初のフレームから自動生成されるため、
カスタムサムネを設定しても無効化されることが多い。
この後処理を build_*.py の最終ステップとして呼び出すと、
動画の冒頭 N 秒間だけサムネ画像で画面を覆い、Shortsフィードでも
カスタムデザインのサムネが表示されるようになる。

動画長と音声は変わらない(オーバーレイのみ)。

usage:
    python3 apply_intro_thumbnail.py --word fragile --video lou_quiz_short_v4_07_fragile.mp4
    python3 apply_intro_thumbnail.py --word fragile  # video省略時はshorts/直下のlou_quiz_short_v4_<id>.mp4を自動推測
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SHORTS_DIR = BASE_DIR.parent
MANIFEST_PATH = BASE_DIR / "manifest_thumbs.json"
THUMBNAILS_DIR = BASE_DIR / "thumbnails"


def thumbnail_filename(item: dict) -> str:
    item_id = item["id"]
    word = item["word"]
    if item_id.lower().endswith(f"_{word.lower()}"):
        return f"{item_id}.jpg"
    return f"{item_id}_{word}.jpg"


def find_item(word: str) -> dict:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    matches = [item for item in manifest if item["word"].casefold() == word.casefold()]
    if not matches:
        raise SystemExit(f"manifestに該当する単語がありません: {word}")
    if len(matches) > 1:
        raise SystemExit(f"manifest内で単語が重複しています: {word}")
    return matches[0]


def guess_video_path(item: dict) -> Path:
    candidate = SHORTS_DIR / f"lou_quiz_short_v4_{item['id']}.mp4"
    if not candidate.is_file():
        raise SystemExit(
            f"動画が見つかりません(--videoで明示してください): {candidate}"
        )
    return candidate


def apply_overlay(video: Path, thumbnail: Path, output: Path, duration: float) -> None:
    if output.exists():
        output.unlink()
    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(video),
        "-i", str(thumbnail),
        "-filter_complex",
        f"[1:v]scale=1080:1920,setsar=1[thumb];"
        f"[0:v][thumb]overlay=enable='between(t,0,{duration})'[v]",
        "-map", "[v]",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        "-movflags", "+faststart",
        str(output),
    ]
    print(" ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise SystemExit("ffmpeg failed")
    print(f"完了: {output} ({output.stat().st_size / 1024 / 1024:.2f} MB)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--word", required=True, help="manifestに登録された英単語")
    parser.add_argument("--video", type=Path, help="入力動画(省略時は自動推測)")
    parser.add_argument("--out", type=Path, help="出力動画(省略時は <stem>_thumbed.mp4)")
    parser.add_argument("--duration", type=float, default=1.0, help="オーバーレイ秒数")
    parser.add_argument(
        "--thumbnail",
        type=Path,
        help="使うサムネJPEG(省略時は manifest から自動)",
    )
    args = parser.parse_args()

    item = find_item(args.word)

    if args.thumbnail:
        thumb = args.thumbnail
    else:
        thumb = THUMBNAILS_DIR / thumbnail_filename(item)
    if not thumb.is_file():
        raise SystemExit(f"サムネJPEGがありません: {thumb}")

    video = args.video if args.video else guess_video_path(item)
    if not video.is_file():
        raise SystemExit(f"入力動画がありません: {video}")

    if args.out:
        output = args.out
    else:
        output = video.with_name(f"{video.stem}_thumbed{video.suffix}")

    apply_overlay(video, thumb, output, args.duration)


if __name__ == "__main__":
    main()
