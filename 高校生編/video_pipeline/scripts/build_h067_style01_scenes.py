#!/usr/bin/env python3
"""Create H067 dense Style01 crops from the nineteen accepted master images."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "H067" / "scenes" / "character_refs"
OUT = ROOT / "H067" / "scenes" / "final_style01"


@dataclass(frozen=True)
class Series:
    master: str
    start: int
    prefix: str
    crops: tuple[str | None, ...]


FULL = None
WL = "1420x799+0+10"
WR = "1420x799+252+10"
ML = "1320x743+0+35"
MR = "1320x743+352+35"
L = "1180x664+0+65"
R = "1180x664+492+65"
C = "1180x664+246+65"


SERIES = (
    Series("modern_brain_gallery_intro_master.png", 1, "gallery_intro", (FULL, WL, WR, ML, MR, L, C)),
    Series("brain_weight_scale_master.png", 8, "brain_weight", (FULL, ML, C)),
    Series("neuron_count_estimation_master.png", 11, "neuron_count", (FULL, ML, MR, C)),
    Series("neuron_synapse_micro_world_master.png", 15, "synapse_micro", (FULL, WL, WR, ML, C)),
    Series("network_scale_data_lab_master.png", 20, "network_scale", (FULL, ML, MR, C)),
    Series("cognition_domains_lab_master.png", 24, "cognition_domains", (FULL, ML, C)),
    Series("self_emergence_network_master.png", 27, "self_network", (FULL, ML, MR, C)),
    Series("consciousness_research_ethics_master.png", 31, "consciousness_ethics", (FULL, WL, WR, ML, MR, C)),
    Series("imaging_history_1990s_master.png", 37, "imaging_history", (FULL, WL, WR, ML, C)),
    Series("fmri_bold_experiment_master.png", 42, "fmri_bold", (FULL, WL, WR, ML, C)),
    Series("vision_memory_signal_inference_master.png", 47, "signal_inference", (FULL, WL, WR, ML, MR, L, R, C)),
    Series("plasticity_evidence_lab_master.png", 55, "plasticity_evidence", (FULL, WL, WR, ML, MR, L, C)),
    Series("adult_brain_old_belief_master.png", 62, "old_belief", (FULL, ML, MR, C)),
    Series("lifelong_learning_change_master.png", 66, "lifelong_learning", (FULL, WL, WR, ML, MR, L, R, C)),
    Series("disease_care_continuum_master.png", 74, "disease_care", (FULL, WL, WR, ML, C)),
    Series("treatment_research_global_master.png", 79, "treatment_research", (FULL, WL, WR, ML, MR, C)),
    Series("personalized_recovery_limits_master.png", 85, "personalized_recovery", (FULL, WL, WR, ML, MR, L, C)),
    Series("rehabilitation_team_plasticity_master.png", 92, "rehabilitation", (FULL, WL, WR, ML, MR, L, R, C)),
    Series("human_question_interdisciplinary_master.png", 100, "human_question", (FULL, WL, WR, ML, MR, L, C)),
)


def render(source: Path, target: Path, crop: str | None) -> None:
    if target.is_file() and target.stat().st_size:
        return
    if crop is None:
        shutil.copyfile(source, target)
        return
    subprocess.run([
        "magick", str(source), "-crop", crop, "+repage",
        "-resize", "1672x941^", "-gravity", "center", "-extent", "1672x941",
        str(target),
    ], check=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    expected: list[Path] = []
    for series in SERIES:
        source = REF / series.master
        if not source.is_file():
            raise FileNotFoundError(source)
        for offset, crop in enumerate(series.crops):
            number = series.start + offset
            target = OUT / f"{number:03d}_{series.prefix}_{offset + 1:02d}.png"
            render(source, target, crop)
            expected.append(target)
    actual = sorted(OUT.glob("[0-9][0-9][0-9]_*.png"))
    if len(actual) != 106 or actual != expected:
        raise RuntimeError(f"H067 scene mismatch: actual={len(actual)} expected=106")
    for path in actual:
        size = subprocess.run(
            ["magick", "identify", "-format", "%wx%h", str(path)],
            check=True, capture_output=True, text=True,
        ).stdout
        if size != "1672x941":
            raise RuntimeError(f"unexpected size {size}: {path}")
    print("H067 final_style01 files verified: 106")


if __name__ == "__main__":
    main()
