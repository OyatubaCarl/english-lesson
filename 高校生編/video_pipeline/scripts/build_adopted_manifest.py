#!/usr/bin/env python3
"""Build one canonical H001-H160 video-production manifest.

The selection logs remain the source of truth.  This script only normalizes
their different shapes and records the exact local audio file used by video
production.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PROJECT = ROOT.parent.parent
SUNO_READY = PROJECT / "高校生編" / "suno_ready"
GENERATED = SUNO_READY / "generated"
OUT = ROOT / "planning" / "adopted_songs_h001_h160.json"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def probe_duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nw=1:nk=1",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return round(float(result.stdout.strip()), 6)


def extract_lesson_sheet(lesson: int) -> dict:
    folder = "H001-H045" if lesson <= 45 else "H046-H160"
    path = SUNO_READY / folder / f"H{lesson:03d}.md"
    source = path.read_text(encoding="utf-8")

    title_match = re.search(r"## Suno Title\s+```text\s*(.*?)\s*```", source, re.S)
    lyrics_match = re.search(r"## Lyrics\s+```text\s*(.*?)\s*```", source, re.S)
    style_match = re.search(r"## Styles\s+```text\s*(.*?)\s*```", source, re.S)
    if not title_match or not lyrics_match or not style_match:
        raise RuntimeError(f"Incomplete Suno sheet: {path}")

    lyrics_block = lyrics_match.group(1).strip()
    lyric_lines = [
        line.strip()
        for line in lyrics_block.splitlines()
        if line.strip() and not re.fullmatch(r"\[[^]]+\]", line.strip())
    ]
    sections: list[dict] = []
    current = {"name": "Lyrics", "lines": []}
    for raw in lyrics_block.splitlines():
        line = raw.strip()
        if not line:
            continue
        if re.fullmatch(r"\[[^]]+\]", line):
            if current["lines"]:
                sections.append(current)
            current = {"name": line[1:-1], "lines": []}
        else:
            current["lines"].append(line)
    if current["lines"]:
        sections.append(current)

    return {
        "sheet": str(path.relative_to(PROJECT)),
        "title": title_match.group(1).strip(),
        "style": style_match.group(1).strip(),
        "lyrics_block": lyrics_block,
        "lyrics_lines": lyric_lines,
        "sections": sections,
    }


def local_audio_row(path: Path) -> dict:
    row = {"path": str(path.relative_to(PROJECT)), "exists": path.exists()}
    if path.exists():
        row.update(
            {
                "bytes": path.stat().st_size,
                "duration_seconds": probe_duration(path),
                "sha256": sha256(path),
            }
        )
    return row


def h001_h045() -> dict[int, dict]:
    log = read_json(GENERATED / "H001-H045_song_selection_log.json")
    rows: dict[int, dict] = {}
    for item in log["songs"]:
        lesson = int(item["lesson"][1:])
        adopted = item["adopted_candidate"]
        # Rewritten H009/H035 have their own audio directory.  Do not alias
        # them to the earlier third candidates: those contain the pre-rewrite
        # lyrics even though both happen to be numbered after candidates 1/2.
        if adopted == "rewrite_candidate1":
            local_candidate = "rewrite_candidate1"
            audio = GENERATED / "rewrite_audio" / f"H{lesson:03d}" / "candidate1-full.mp3"
        elif adopted == "rewrite_candidate2":
            local_candidate = "rewrite_candidate2"
            audio = GENERATED / "rewrite_audio" / f"H{lesson:03d}" / "candidate2-full.mp3"
        else:
            local_candidate = int(adopted)
            audio = GENERATED / "audio" / f"H{lesson:03d}" / f"candidate{local_candidate}-full.mp3"
        rows[lesson] = {
            "adopted_candidate": adopted,
            "local_candidate": local_candidate,
            "adopted_url": item["share_url"],
            "song_id": item["song_id"],
            "qa_status": item["lyrics_match"]["status"],
            "qa_note": item["pronunciation_notes"],
            "selection_reason": item["selection_reason"],
            "audio": local_audio_row(audio),
        }
    return rows


def h046_h047() -> dict[int, dict]:
    fixed = {
        46: {
            "adopted_candidate": "user_selected",
            "adopted_url": "https://suno.com/song/30352330-1365-42ff-910f-3d0467ae68dc",
            "share_url": "https://suno.com/s/YyNYeSPYvPCL8USO",
            "qa_status": "USER_ADOPTED_ASR_REVIEWED",
            "qa_note": "ユーザー指定の採用曲。H46試作動画で字幕タイミングを二系統ASRにより確認済み。",
            "audio_path": PROJECT / "高校生編" / "h46_imagen_video" / "source_audio" / "h46_democracy_constitution.mp3",
        },
        47: {
            "adopted_candidate": "user_selected",
            "adopted_url": "https://suno.com/song/5eeb0380-9f6b-4bdf-95b0-1bed2e551af8",
            "share_url": "https://suno.com/s/77R5ot3BepYu8GSX",
            "qa_status": "USER_ADOPTED",
            "qa_note": "ユーザー指定の採用曲。映像化前にローカル音源の存在と歌詞終端を確認する。",
            "audio_path": ROOT / "source_audio" / "H047" / "h047_market_economy_adopted.mp3",
        },
    }
    rows = {}
    for lesson, item in fixed.items():
        song_id = item["adopted_url"].rsplit("/", 1)[-1]
        rows[lesson] = {
            "adopted_candidate": item["adopted_candidate"],
            "local_candidate": item["adopted_candidate"],
            "adopted_url": item["adopted_url"],
            "share_url": item["share_url"],
            "song_id": song_id,
            "qa_status": item["qa_status"],
            "qa_note": item["qa_note"],
            "selection_reason": "ユーザーが共有リンクから採用を指定。",
            "audio": local_audio_row(item["audio_path"]),
        }
    return rows


def h048_h160() -> dict[int, dict]:
    log = read_json(GENERATED / "adopted_songs.json")["lessons"]
    rows = {}
    for key, item in log.items():
        lesson = int(key)
        candidate = int(item["adopted_candidate"])
        audio = GENERATED / "audio" / f"H{lesson:03d}" / f"candidate{candidate}-full.mp3"
        rows[lesson] = {
            "adopted_candidate": candidate,
            "local_candidate": candidate,
            "adopted_url": item["adopted_url"],
            "song_id": item["adopted_url"].rsplit("/", 1)[-1],
            "qa_status": item["qa_status"],
            "qa_note": item["note"],
            "selection_reason": item["note"],
            "audio": local_audio_row(audio),
        }
    return rows


def main() -> None:
    rows = {}
    rows.update(h001_h045())
    rows.update(h046_h047())
    rows.update(h048_h160())
    if sorted(rows) != list(range(1, 161)):
        raise RuntimeError("Adopted-song range is incomplete")

    lessons = []
    for lesson in range(1, 161):
        sheet = extract_lesson_sheet(lesson)
        item = {"lesson": f"H{lesson:03d}", **sheet, **rows[lesson]}
        lessons.append(item)

    missing_audio = [row["lesson"] for row in lessons if not row["audio"]["exists"]]
    qa_counts: dict[str, int] = {}
    for row in lessons:
        qa_counts[row["qa_status"]] = qa_counts.get(row["qa_status"], 0) + 1
    manifest = {
        "range": "H001-H160",
        "policy": "Use exactly one adopted song per lesson; never substitute an unadopted candidate.",
        "counts": {
            "lessons": len(lessons),
            "local_audio_ready": len(lessons) - len(missing_audio),
            "missing_audio": missing_audio,
            "qa_status": qa_counts,
        },
        "lessons": lessons,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["counts"], ensure_ascii=False, indent=2))
    print(OUT)


if __name__ == "__main__":
    main()
