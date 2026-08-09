#!/usr/bin/env python3
"""Create H080 dense Style01 crops aligned to the philosophy lyric timeline."""
from __future__ import annotations

from bisect import bisect_right
import shutil
import subprocess
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "H080/scenes/character_refs"
OUT = ROOT / "H080/scenes/final_style01"
DURATION = 172.360167
SCENE_COUNT = 133
UNIT = DURATION / SCENE_COUNT

# Every master begins with a hold, then moves in one direction only. This keeps
# the approved camera language: stable hold or a straight push-in, without
# shake, lateral wandering, or handheld-style movement.
CROP_SEQUENCES = {
    "C": (
        None,
        "1460x821+106+30",
        "1280x720+196+45",
        "1100x619+286+60",
        "980x551+346+70",
    ),
    "L": (
        None,
        "1460x821+0+30",
        "1280x720+0+45",
        "1100x619+0+60",
        "980x551+0+70",
    ),
    "R": (
        None,
        "1460x821+212+30",
        "1280x720+392+45",
        "1100x619+572+60",
        "980x551+692+70",
    ),
}


def snap_before(time: float) -> float:
    """Move a lyric cue back to the preceding 1.296-second cut boundary."""
    return int(time / UNIT) * UNIT


# Raw thresholds follow the sung meaning. Snapping them to the previous cut
# makes the intended subject visible as the corresponding phrase begins.
RAW_MASTERS = (
    (0.0, "philosophy_seminar_intro_master.png", "philosophy_seminar_intro", "C"),
    (10.3, "taken_for_granted_assumptions_master.png", "taken_for_granted_assumptions", "L"),
    (15.3, "justice_community_deliberation_master.png", "justice_community_deliberation", "C"),
    (17.0, "good_life_ordinary_relations_master.png", "good_life_ordinary_relations", "C"),
    (19.5, "what_can_we_know_inquiry_master.png", "what_can_we_know_inquiry", "C"),
    (22.2, "ancient_greece_museum_bridge_master.png", "ancient_greece_museum_bridge", "C"),
    (27.0, "ancient_agora_dialogue_master.png", "ancient_agora_dialogue", "C"),
    (31.0, "questions_across_centuries_master.png", "questions_across_centuries", "C"),
    (35.0, "plato_academy_teaching_master.png", "plato_academy_teaching", "C"),
    (38.5, "plato_visible_intelligible_model_master.png", "plato_visible_intelligible_model", "C"),
    (41.2, "aristotle_lyceum_observation_master.png", "aristotle_lyceum_observation", "C"),
    (45.0, "aristotle_observation_reasoning_master.png", "aristotle_observation_reasoning", "C"),
    (49.6, "plato_aristotle_teaching_contrast_master.png", "plato_aristotle_teaching_contrast", "C"),
    (54.5, "philosophy_history_archive_master.png", "philosophy_history_archive", "C"),
    (59.0, "descartes_seventeenth_century_study_master.png", "descartes_seventeenth_century_study", "R"),
    (63.5, "methodic_doubt_reflection_master.png", "methodic_doubt_reflection", "L"),
    (67.0, "cogito_writing_closeup_master.png", "cogito_writing_closeup", "C"),
    (71.3, "self_that_doubts_master.png", "self_that_doubts", "C"),
    (85.5, "modern_philosophy_starting_point_master.png", "modern_philosophy_starting_point", "R"),
    (90.8, "consciousness_crossdisciplinary_dialogue_master.png", "consciousness_crossdisciplinary_dialogue", "C"),
    (96.3, "kant_eighteenth_century_study_master.png", "kant_eighteenth_century_study", "C"),
    (98.5, "moral_act_everyday_dilemma_master.png", "moral_act_everyday_dilemma", "L"),
    (101.0, "universal_maxim_test_master.png", "universal_maxim_test", "C"),
    (106.0, "universal_rule_people_as_ends_master.png", "universal_rule_people_as_ends", "C"),
    (110.3, "unconditional_moral_standard_master.png", "unconditional_moral_standard", "R"),
    (114.0, "moral_judgment_in_context_master.png", "moral_judgment_in_context", "C"),
    (117.6, "nietzsche_nineteenth_century_study_master.png", "nietzsche_nineteenth_century_study", "C"),
    (120.3, "nietzsche_values_genealogy_master.png", "nietzsche_values_genealogy", "R"),
    (123.3, "god_is_dead_cultural_shift_master.png", "god_is_dead_cultural_shift", "C"),
    (130.0, "modern_disorientation_value_rethinking_master.png", "modern_disorientation_value_rethinking", "R"),
    (135.6, "continuing_questions_seminar_master.png", "continuing_questions_seminar", "C"),
    (140.3, "questions_before_answers_notebook_master.png", "questions_before_answers_notebook", "C"),
    (145.0, "abstract_question_observatory_master.png", "abstract_question_observatory", "C"),
    (153.0, "self_understanding_reflection_master.png", "self_understanding_reflection", "C"),
    (160.0, "shared_inquiry_dawn_finale_master.png", "shared_inquiry_dawn_finale", "R"),
)
MASTERS = tuple((snap_before(t), image, prefix, anchor) for t, image, prefix, anchor in RAW_MASTERS)


def render(src: Path, dst: Path, crop: str | None) -> None:
    if crop is None:
        shutil.copyfile(src, dst)
        return
    subprocess.run(
        [
            "magick", str(src), "-crop", crop, "+repage", "-resize", "1672x941^",
            "-gravity", "center", "-extent", "1672x941", str(dst),
        ],
        check=True,
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    if any(OUT.iterdir()):
        raise RuntimeError(f"H080 output directory must be empty before rebuilding: {OUT}")

    for _, master, _, _ in MASTERS:
        src = REF / master
        if not src.is_file():
            raise FileNotFoundError(src)

    starts = [item[0] for item in MASTERS]
    usage: Counter[str] = Counter()
    expected: list[Path] = []
    for ordinal in range(SCENE_COUNT):
        time = UNIT * ordinal
        master_index = bisect_right(starts, time + 1e-9) - 1
        _, master, prefix, anchor = MASTERS[master_index]
        usage[prefix] += 1
        crop_number = usage[prefix]
        sequence = CROP_SEQUENCES[anchor]
        crop = sequence[min(crop_number - 1, len(sequence) - 1)]
        dst = OUT / f"{ordinal + 1:03d}_{prefix}_{crop_number:02d}.png"
        render(REF / master, dst, crop)
        expected.append(dst)

    actual = sorted(OUT.glob("[0-9][0-9][0-9]_*.png"))
    missing = [prefix for _, _, prefix, _ in MASTERS if usage[prefix] == 0]
    if actual != expected or len(actual) != SCENE_COUNT or missing:
        raise RuntimeError(
            f"H080 scene mismatch actual={len(actual)} expected={SCENE_COUNT} missing={missing}"
        )
    print(f"H080 final_style01 files verified: {len(actual)}; masters used: {len(usage)}")


if __name__ == "__main__":
    main()
