#!/usr/bin/env python3
"""Build the H080 133-cut video plan and verify lyric-to-image alignment."""
from __future__ import annotations

from bisect import bisect_right
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "H080"
PLAN = LESSON / "planning/video_plan.json"
SCENE_COUNT = 133
NAME_RE = re.compile(r"^\d{3}_(.+)_\d{2}\.png$")
EXPECTED_AT = {
    11.0: "taken_for_granted_assumptions",
    16.0: "justice_community_deliberation",
    18.0: "good_life_ordinary_relations",
    20.0: "what_can_we_know_inquiry",
    23.0: "ancient_greece_museum_bridge",
    28.0: "ancient_agora_dialogue",
    32.0: "questions_across_centuries",
    36.0: "plato_academy_teaching",
    39.0: "plato_visible_intelligible_model",
    42.0: "aristotle_lyceum_observation",
    46.0: "aristotle_observation_reasoning",
    50.0: "plato_aristotle_teaching_contrast",
    55.0: "philosophy_history_archive",
    60.0: "descartes_seventeenth_century_study",
    64.0: "methodic_doubt_reflection",
    68.0: "cogito_writing_closeup",
    72.0: "self_that_doubts",
    86.0: "modern_philosophy_starting_point",
    91.0: "consciousness_crossdisciplinary_dialogue",
    97.0: "kant_eighteenth_century_study",
    99.0: "moral_act_everyday_dilemma",
    102.0: "universal_maxim_test",
    107.0: "universal_rule_people_as_ends",
    111.0: "unconditional_moral_standard",
    115.0: "moral_judgment_in_context",
    118.0: "nietzsche_nineteenth_century_study",
    121.0: "nietzsche_values_genealogy",
    124.0: "god_is_dead_cultural_shift",
    131.0: "modern_disorientation_value_rethinking",
    136.0: "continuing_questions_seminar",
    141.0: "questions_before_answers_notebook",
    146.0: "abstract_question_observatory",
    154.0: "self_understanding_reflection",
    161.0: "shared_inquiry_dawn_finale",
}


def purpose(image: Path) -> str:
    match = NAME_RE.match(image.name)
    if not match:
        raise RuntimeError(f"unexpected H080 scene filename: {image.name}")
    return match.group(1)


def main() -> None:
    plan = json.loads(PLAN.read_text())
    duration = float(plan["duration"])
    if abs(duration - 172.360167) > 0.02:
        raise RuntimeError(f"unexpected H080 adopted duration: {duration}")
    unit = duration / SCENE_COUNT
    images = sorted((LESSON / "scenes/final_style01").glob("[0-9][0-9][0-9]_*.png"))
    if len(images) != SCENE_COUNT:
        raise RuntimeError(f"H080 scene count: {len(images)} != {SCENE_COUNT}")

    scenes = [
        {
            "start": round(unit * ordinal, 3),
            "image": str(image.relative_to(LESSON)),
            "purpose": purpose(image),
        }
        for ordinal, image in enumerate(images)
    ]
    gaps = [float(b["start"]) - float(a["start"]) for a, b in zip(scenes, scenes[1:])]
    gaps.append(duration - float(scenes[-1]["start"]))
    if min(gaps) < 1.292 or max(gaps) > 1.300:
        raise RuntimeError((len(scenes), min(gaps), max(gaps)))

    scene_starts = [float(scene["start"]) for scene in scenes]
    for time, expected in EXPECTED_AT.items():
        scene = scenes[bisect_right(scene_starts, time) - 1]
        if scene["purpose"] != expected:
            raise RuntimeError(
                f"H080 alignment at {time:.2f}s: {scene['purpose']} != {expected}"
            )

    plan["title_en"] = "An Introduction to Philosophy"
    plan["scenes"] = scenes
    plan["qa_status"] = "READY_TO_RENDER_STYLE01_PHILOSOPHY_LYRIC_ALIGNED"
    plan["output_name"] = "h080_adopted_song_cinematic_v1.mp4"
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n")
    print(
        f"H080 video plan: {len(scenes)} scenes, min {min(gaps):.3f}s "
        f"max {max(gaps):.3f}s; lyric checkpoints PASS"
    )


if __name__ == "__main__":
    main()
