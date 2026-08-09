#!/usr/bin/env python3
"""Download Jolly Phonics letter sounds for local reference only.

The files downloaded by this script are not used by the mockup and should not
be redistributed. They are kept as pronunciation-quality references while we
build an original phoneme audio set.
"""
from __future__ import annotations

import json
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path


JOLLY_NA_URL = "https://jolly2.s3.amazonaws.com/northamerican_english/northamerican_english.zip"
DEFAULT_OUT = Path("reference-audio/jolly-letter-sounds")


def download(url: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=60) as response:
        out_path.write_bytes(response.read())


def main() -> int:
    out_root = DEFAULT_OUT
    zip_path = out_root / "northamerican_english.zip"
    extract_dir = out_root / "northamerican_english"

    print(f"download: {JOLLY_NA_URL}")
    download(JOLLY_NA_URL, zip_path)

    if extract_dir.exists():
        shutil.rmtree(extract_dir)

    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(out_root)

    mp3_files = sorted(path for path in extract_dir.rglob("*.mp3") if "__MACOSX" not in path.parts)
    manifest = {
        "source": "Jolly Learning Hear the Sounds resource bank",
        "url": JOLLY_NA_URL,
        "status": "reference-only; not redistributed by the mockup",
        "files": [str(path.relative_to(out_root)) for path in mp3_files],
    }
    (out_root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_root / "SOURCE_AND_LICENSE_NOTE.txt").write_text(
        "\n".join(
            [
                "Jolly Phonics letter sounds reference download",
                "",
                "These files were downloaded from Jolly Learning's public resource bank for local pronunciation reference only.",
                "The Jolly Learning pages show the sounds as downloadable resources, but no license granting redistribution",
                "or embedding in a separate published app was found.",
                "",
                "Do not copy these files into the app's served audio directory or distribute them with the project unless",
                "written permission is obtained from Jolly Learning.",
                "",
                f"Source URL: {JOLLY_NA_URL}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"zip: {zip_path}")
    print(f"extracted mp3 files: {len(mp3_files)}")
    print(f"note: {out_root / 'SOURCE_AND_LICENSE_NOTE.txt'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
