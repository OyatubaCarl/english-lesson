"""Generate review frames and script data for H1-H10 explainers."""
from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REVIEW_DIR = ROOT / "review_h1_h10"
FRAME_DIR = REVIEW_DIR / "assets" / "frames"
DATA_PATH = REVIEW_DIR / "review_data.json"
EDITS_PATH = REVIEW_DIR / "review_edits.json"


def infer_part(name: str) -> str:
    if name == "theme":
        return "導入"
    if name.startswith(("scene", "examples", "example")):
        return "例文"
    if name.startswith(("compare", "contrast", "patterns", "door", "i_opened")):
        return "比較"
    if name.startswith(("flip", "build", "modifier")):
        return "文を作る"
    if name.startswith("rule"):
        return "見つけ方"
    if any(key in name for key in ("text", "h1_", "h3_", "h4_", "sentence")):
        return "本文"
    if name.startswith(("parallel", "summary")):
        return "まとめ"
    return "その他"


def step_record(lesson_id: int, idx: int, step, image_rel: str) -> dict:
    audio_text = step.speech if step.kind != "silent" else f"[無音 {step.seconds:.2f}秒]"
    return {
        "id": step.name,
        "index": idx + 1,
        "part": infer_part(step.name),
        "kind": step.kind,
        "audioText": audio_text,
        "durationHint": step.seconds,
        "image": image_rel,
        "lessonId": lesson_id,
    }


def render_lesson_frames(lesson_id: int, steps: list, force: bool = True) -> list[dict]:
    lesson_frame_dir = FRAME_DIR / f"h{lesson_id:02d}"
    if force and lesson_frame_dir.exists():
        shutil.rmtree(lesson_frame_dir)
    lesson_frame_dir.mkdir(parents=True, exist_ok=True)

    records = []
    for idx, step in enumerate(steps):
        image_rel = f"assets/frames/h{lesson_id:02d}/frame_{idx:03d}_{step.name}.png"
        image_path = REVIEW_DIR / image_rel
        frame = step.render()
        frame.save(image_path)
        records.append(step_record(lesson_id, idx, step, image_rel))
    return records


def main() -> None:
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    FRAME_DIR.mkdir(parents=True, exist_ok=True)

    import build_h3_svo_plain_explainer as h3
    h3_steps = list(h3.STEPS)
    import build_h4_svoo_plain_explainer as h4
    h4_steps = list(h4.STEPS)
    import build_h1_h10_plain_explainers as h1_h10
    import build_h1_sv_plain_explainer as h1
    h1_steps = list(h1.base.STEPS)

    common_by_id = {cfg.lesson_id: cfg for cfg in h1_h10.LESSONS}

    lessons = []
    lesson_sources = {
        1: ("H1", "第1文型 SV", "主語と動詞だけで成り立つ文", h1_steps),
        3: ("H3", "第3文型 SVO", "動作が対象へ向かう文", h3_steps),
        4: ("H4", "第4文型 SVOO", "受け手と授与物を並べる文", h4_steps),
    }

    for lesson_id in range(1, 11):
        if lesson_id in lesson_sources:
            code, title, focus, steps = lesson_sources[lesson_id]
        else:
            cfg = common_by_id[lesson_id]
            code = f"H{lesson_id}"
            title = cfg.pattern
            focus = cfg.target
            steps = h1_h10.make_steps(cfg)

        slides = render_lesson_frames(lesson_id, steps)
        lessons.append(
            {
                "id": f"h{lesson_id}",
                "lessonId": lesson_id,
                "code": code,
                "title": title,
                "focus": focus,
                "slides": slides,
            }
        )

    data = {
        "version": 1,
        "generatedBy": Path(__file__).name,
        "lessons": lessons,
        "saveShape": {
            "overallComment": "レッスン全体への修正コメント",
            "audioText": "音声テキストを直接修正",
            "slideComment": "スライドごとの修正コメント",
        },
    }
    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    if not EDITS_PATH.exists():
        EDITS_PATH.write_text(json.dumps({"version": 1, "lessons": {}}, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"wrote {DATA_PATH}")
    print(f"wrote frames under {FRAME_DIR}")


if __name__ == "__main__":
    main()
