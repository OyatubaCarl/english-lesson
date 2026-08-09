#!/usr/bin/env python3
"""Build the isolated Mio edition without modifying the original Ken edition."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_BUILDER = ROOT.parent / "l1_codex_video" / "scripts" / "build_video.py"

spec = importlib.util.spec_from_file_location("l1_original_builder", ORIGINAL_BUILDER)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load the original builder: {ORIGINAL_BUILDER}")

builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

# Repoint every output and input to the separate Mio workspace. The original
# builder and all Ken-edition artifacts remain untouched.
builder.ROOT = ROOT
builder.PLAN_PATH = ROOT / "planning" / "scene_plan.json"
builder.LYRICS_PATH = ROOT / "planning" / "lyrics_timing.json"
builder.SCENES_DIR = ROOT / "scenes"
builder.CAPTIONS_DIR = ROOT / "captions"
builder.WORK_DIR = ROOT / "work"
builder.OUTPUT_DIR = ROOT / "output"
builder.ASS_PATH = builder.CAPTIONS_DIR / "l1_mio_bilingual_word_highlight.ass"
builder.SCENES_VIDEO = builder.WORK_DIR / "l1_mio_scenes.mp4"
builder.FINAL_VIDEO = (
    builder.OUTPUT_DIR / "l1_my_family_and_pochi_mio_bilingual.mp4"
)
builder.CONTACT_SHEET = builder.OUTPUT_DIR / "l1_mio_scene_contact_sheet.jpg"


if __name__ == "__main__":
    builder.main()

