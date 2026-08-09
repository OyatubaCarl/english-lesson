"""Build kinetic captions for aunt_ant_short_a (1080p, Funnics Island style).

Mirrors build_baker_subtitles.py:
  - Layer 0: rounded-rect coral box for active word only
  - Layer 1: per-word crisp white text (shadowed) for full cue duration
  - PIL pre-computes layout; \\N inserted manually for multi-line wrap
  - Multi-line aware (PlayResY positioning)
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import librosa  # type: ignore
import numpy as np
from PIL import ImageFont

ROOT = Path(__file__).parent
# OpenAI Whisper API is the primary transcript (audio-aligned segment ends).
# whisper.cpp turbo is consulted only for the 4-rep Black bag cluster where
# OpenAI merged all 4 reps into one segment.
TRANSCRIPT = ROOT / "aunt_ant_short_a_transcript_auto.json"
TRANSCRIPT_WCPP = ROOT / "aunt_ant_short_a_transcript_wcpp.json"
AUDIO = ROOT / "aunt_ant_short_a.mp3"
SRC = Path("/Users/masaki/Library/CloudStorage/GoogleDrive-sarosaro36@gmail.com/"
           "マイドライブ/個人用/ClaudeCode/Funnics Island/songs/"
           "02_aunt_ant_short_a/final.mp4")
OUT = Path("/Users/masaki/Library/CloudStorage/GoogleDrive-sarosaro36@gmail.com/"
           "マイドライブ/個人用/ClaudeCode/Funnics Island/songs/"
           "02_aunt_ant_short_a/final_captioned.mp4")
ASS_PATH = Path("/Users/masaki/Library/CloudStorage/GoogleDrive-sarosaro36@gmail.com/"
                "マイドライブ/個人用/ClaudeCode/Funnics Island/songs/"
                "02_aunt_ant_short_a/captions.ass")

PLAY_W = 1920
PLAY_H = 1080
FONT_PATH_EN = "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"
FONT_PATH_JP = "/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc"
FONT_NAME_EN = "Arial Rounded MT Bold"
FONT_NAME_JP = "Hiragino Maru Gothic ProN W4"
FONT_SIZE_PX = 90
JP_SIZE_PX = 78
LINE_HEIGHT = int(FONT_SIZE_PX * 1.25)
JP_LINE_HEIGHT = int(JP_SIZE_PX * 1.4)

MARGIN_L = 60
MARGIN_R = 60
MARGIN_V = 130
MAX_WIDTH = PLAY_W - MARGIN_L - MARGIN_R

BOX_PAD_X = 18
BOX_PAD_Y = 8
CORNER_R = 22
BOX_COLOR_BGR = "6080FF"


# (start, end, text, is_english)
CUES: list[tuple[float, float, str, bool]] = [
    # ── Intro narration (JP, hiragana) — actual Whisper timings ─────
    ( 0.00,  3.84, "ねえ しってる？ \"A\" の もじ。", False),
    ( 3.84,  5.24, "ABC の \"A\"。", False),
    ( 5.24,  9.26, "でも、べつの よみかたも あるんだよ。", False),
    ( 9.26, 12.28, "アントおばさんの みじかい「あ」。", False),
    # ── English chant ─────────────────────────────────────────────
    (12.42, 14.72, "Cat, hat, ant, bag.", True),
    (14.72, 16.44, "Fat, mad, sad, black.", True),
    # ── JP narration ──────────────────────────────────────────────
    (16.46, 19.18, "ぜんぶ みじかい A の おと。", False),
    (19.34, 22.18, "じゃあ、きいてみて！", False),
    # ── Hook 1 (OpenAI Whisper) ───────────────────────────────────
    (23.06, 27.48, "A! A! A! A! Aunt Ant!", True),
    (27.48, 30.84, "Short A! Short A! Aunt Ant Ant!", True),
    # ── Verse 1 (OpenAI segment boundaries — audio-aligned) ────────
    (30.84, 32.51, "Fat cat in a hat,", True),
    (32.51, 34.18, "Fat cat in a hat,", True),
    (34.18, 36.00, "Mad rat on a mat,", True),
    (36.00, 37.82, "Mad rat on a mat,", True),
    (37.82, 39.61, "Sad ant at a plant,", True),
    (39.61, 41.40, "Sad ant at a plant,", True),
    # V1L4 + V2L1: 4 reps of Black bag (whisper.cpp split — only place wcpp wins)
    (41.50, 43.05, "Black bag with a flag,", True),
    (43.10, 44.85, "Black bag with a flag,", True),
    (45.20, 46.70, "Black bag with a flag,", True),
    (46.80, 48.45, "Black bag with a flag!", True),
    # ── Verse 2 (OpenAI: Sad / Mad / Fat ×2 each) ─────────────────
    (48.32, 50.20, "Sad ant at a plant,", True),
    (50.20, 52.08, "Sad ant at a plant,", True),
    (52.08, 53.89, "Mad rat on a mat,", True),
    (53.89, 55.70, "Mad rat on a mat,", True),
    (55.70, 57.53, "Fat cat in a hat!", True),
    (57.53, 59.36, "Fat cat in a hat!", True),
    # ── Verse 3 (whisper.cpp boundaries — OpenAI was 1.22s late on V3L1) ─
    (59.32, 61.08, "Mad cat in a hat,", True),
    (61.08, 63.00, "Mad cat in a hat,", True),
    (63.00, 64.63, "Sad rat on a mat,", True),
    (64.63, 66.46, "Sad rat on a mat,", True),
    (66.46, 68.20, "Black ant at a plant,", True),
    (68.20, 70.00, "Black ant at a plant,", True),
    (70.00, 71.74, "Fat bag with a flag,", True),
    (71.74, 73.64, "Fat bag with a flag!", True),
    # ── Verse 4 (OpenAI: rapid attribute parade — 8 words / line) ─
    (73.64, 77.28, "Fat! Fat! Mad! Mad! Sad! Sad! Black! Black!", True),
    (77.28, 80.76, "Cat! Cat! Rat! Rat! Ant! Ant! Bag! Bag!", True),
    (80.76, 84.34, "In! In! On! On! At! At! With! With!", True),
    (84.34, 87.96, "Hat! Hat! Mat! Mat! Plant! Plant! Flag! Flag!", True),
    # ── Bridge (whisper.cpp accurate boundaries — OpenAI mis-segmented) ─
    # Each line has 2 cycles of 3 syllables. Canonical = 2 hyphenated tokens.
    (87.84, 90.50, "Fat-cat-hat! Fat-cat-hat!", True),    # cycle1 87.84-89.10, cycle2 89.30-90.50
    (90.90, 94.08, "Mad-rat-mat! Mad-rat-mat!", True),    # cycle1 90.90-92.36, cycle2 92.67-94.08
    (94.48, 97.68, "Sad-ant-plant! Sad-ant-plant!", True), # cycle1 94.48-95.95, cycle2 96.21-97.68
    (98.08, 101.60, "Black-bag-flag! Black-bag-flag!", True), # cycle1 98.08-99.80, cycle2 99.94-101.60
    # ── Hook 2 (OpenAI Whisper) ───────────────────────────────────
    (102.04, 106.10, "A! A! A! A! Aunt Ant!", True),
    (106.14, 109.46, "Short A! Short A! Aunt Ant Ant!", True),
    # ── Outro JP narration + chant ────────────────────────────────
    (109.46, 112.54, "これが みじかい \"A\" の おと！", False),
    (112.80, 114.62, "Cat, hat, ant, bag,", True),
    (114.62, 116.70, "Fat, mad, sad, black.", True),
    # ── Final Hook (OpenAI Whisper) ───────────────────────────────
    (116.64, 119.92, "A! A! A! A! Aunt Ant!", True),
    (119.92, 123.46, "Short A! Short A! Aunt Ant Ant!", True),
]


_pil_en = ImageFont.truetype(FONT_PATH_EN, FONT_SIZE_PX)
_pil_jp = ImageFont.truetype(FONT_PATH_JP, JP_SIZE_PX)


def measure(font: ImageFont.FreeTypeFont, s: str) -> int:
    bb = font.getbbox(s)
    return bb[2] - bb[0]


SPACE_W = measure(_pil_en, " ")


def wrap_words(words: list[str], font, space_w: int, max_w: int) -> list[list[str]]:
    lines: list[list[str]] = [[]]
    cur_w = 0
    for w in words:
        ww = measure(font, w)
        delta = ww + (space_w if lines[-1] else 0)
        if lines[-1] and cur_w + delta > max_w:
            lines.append([w])
            cur_w = ww
        else:
            lines[-1].append(w)
            cur_w += delta
    return lines


def fit_one_line(words: list[str], font_path: str, default_size: int,
                 max_w: int, min_size: int = 64
                 ) -> tuple[int, "ImageFont.FreeTypeFont", int]:
    """Pick the largest size in [min_size, default_size] that fits one line.

    Returns (size, font, space_w).
    """
    size = default_size
    while size >= min_size:
        f = ImageFont.truetype(font_path, size)
        space_w = measure(f, " ")
        widths = [measure(f, w) for w in words]
        total = sum(widths) + space_w * (len(words) - 1)
        if total <= max_w:
            return size, f, space_w
        size -= 4
    f = ImageFont.truetype(font_path, min_size)
    return min_size, f, measure(f, " ")


def word_positions(lines: list[list[str]], font, space_w: int,
                   line_h: int, baseline_y: int,
                   play_w: int) -> list[tuple[int, int]]:
    n = len(lines)
    bottom_cy = baseline_y
    top_cy = bottom_cy - (n - 1) * line_h
    out: list[tuple[int, int]] = []
    for li, line_words in enumerate(lines):
        widths = [measure(font, w) for w in line_words]
        total = sum(widths) + space_w * (len(line_words) - 1)
        left = play_w // 2 - total // 2
        cursor = left
        cy = top_cy + li * line_h
        for i, _w in enumerate(line_words):
            cx = cursor + widths[i] // 2
            out.append((cx, cy))
            cursor += widths[i] + space_w
    return out


def rounded_rect_path(w: int, h: int, r: int) -> str:
    k = 0.5523
    kr = int(round(r * k))
    return (
        f"m {r} 0 "
        f"l {w - r} 0 "
        f"b {w - r + kr} 0 {w} {r - kr} {w} {r} "
        f"l {w} {h - r} "
        f"b {w} {h - r + kr} {w - r + kr} {h} {w - r} {h} "
        f"l {r} {h} "
        f"b {r - kr} {h} 0 {h - r + kr} 0 {h - r} "
        f"l 0 {r} "
        f"b 0 {r - kr} {r - kr} 0 {r} 0"
    )


def fmt_ts(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t - h * 3600 - m * 60
    return f"{h}:{m:02d}:{s:05.2f}"


def split_words(s: str) -> list[str]:
    return [t for t in re.split(r"\s+", s.strip()) if t]


def clean_whisper_words(words: list[dict]) -> list[dict]:
    """Merge Whisper artifacts where it splits 'Fat'→'F'+'at', 'Cat'→'C'+'at',
    'Hat'→'H'+'at'. Also drops zero-duration boundary residue words."""
    out: list[dict] = []
    i = 0
    while i < len(words):
        w = words[i]
        token = w["word"].rstrip("!.,?\"'")
        nxt = words[i + 1] if i + 1 < len(words) else None
        # Pattern: single capital letter followed by 'at' fragment
        if (
            nxt is not None
            and len(token) == 1
            and token.isupper()
            and nxt["word"].lower().rstrip("!.,?\"'") == "at"
        ):
            merged = dict(w)
            merged["word"] = token + "at"
            merged["end"] = nxt.get("end", w.get("end", w["start"]))
            out.append(merged)
            i += 2
            continue
        out.append(w)
        i += 1
    return out


def whisper_in_range(words: list[dict], start: float, end: float) -> list[dict]:
    out: list[dict] = []
    for w in words:
        wstart = w["start"]
        wend = w.get("end", wstart)
        is_zero = wend == wstart
        # Skip 0-duration residue at exact cue start (carry-over from prev cue)
        if is_zero and abs(wstart - start) < 0.05:
            continue
        # Include 0-duration sentinel at exact cue end (Whisper places the
        # last word's "end-marker" here when audio sustains until next cue)
        if is_zero and abs(wstart - end) < 0.05:
            out.append(w)
            continue
        # Standard half-open range
        if start - 0.05 <= wstart < end - 0.02:
            out.append(w)
    return out


# ── Audio onset detection (librosa) ──────────────────────────────
_audio_y: "np.ndarray | None" = None
_audio_sr: int = 22050


def _load_audio() -> None:
    global _audio_y, _audio_sr
    if _audio_y is None:
        _audio_y, _audio_sr = librosa.load(str(AUDIO), sr=22050)


def audio_word_starts(cstart: float, cend: float, n_target: int,
                      min_gap: float = 0.20) -> list[float]:
    """Return up-to-N strongest onset times (sec) inside [cstart, cend].

    Pads with even-spaced fallbacks to length n_target if onset count short.
    """
    _load_audio()
    assert _audio_y is not None
    sr = _audio_sr
    s_start = max(0, int(cstart * sr))
    s_end = min(len(_audio_y), int(cend * sr))
    if s_end <= s_start:
        return [cstart + i * (cend - cstart) / max(1, n_target)
                for i in range(n_target)]
    seg = _audio_y[s_start:s_end]
    hop = 256
    strength = librosa.onset.onset_strength(y=seg, sr=sr, hop_length=hop)
    pre_max = max(1, int(min_gap * sr / hop / 2))
    wait = int(min_gap * sr / hop)
    peaks = librosa.util.peak_pick(
        strength,
        pre_max=pre_max, post_max=pre_max,
        pre_avg=pre_max, post_avg=pre_max,
        delta=0.10, wait=wait,
    )
    if len(peaks) > n_target:
        # Take top-N by strength, then sort chronologically
        sorted_peaks = sorted(peaks, key=lambda p: -strength[p])[:n_target]
        sorted_peaks.sort()
        peaks = sorted_peaks
    times = [float(t + cstart) for t in
             librosa.frames_to_time(peaks, sr=sr, hop_length=hop)]
    # If short, pad by interpolation
    if len(times) < n_target:
        # Build target evenly-spaced grid covering [cstart, cend]
        grid = [cstart + i * (cend - cstart) / n_target
                for i in range(n_target)]
        # Fill missing slots with grid points not too close to existing onsets
        existing = list(times)
        for g in grid:
            if len(existing) >= n_target:
                break
            if all(abs(g - e) > min_gap * 0.8 for e in existing):
                existing.append(g)
        existing.sort()
        times = existing[:n_target]
    return times


def is_blackbag_cue(text: str) -> bool:
    """4-rep Black bag cluster — OpenAI merged all reps, whisper.cpp split
    them cleanly so we use whisper.cpp for these."""
    return "Black bag" in text


def _norm_token(s: str) -> str:
    return s.lower().strip().rstrip("!.,?\"'-").lstrip("\"'-")


def _tokens_match(canonical: list[str], wcpp_words: list[dict]) -> bool:
    """Check if wcpp_words match the canonical sequence (case-insensitive,
    Aunt/Ant equivalence, hyphen-compound expansion handled by caller)."""
    if len(canonical) != len(wcpp_words):
        return False
    for c, w in zip(canonical, wcpp_words):
        c_n = _norm_token(c)
        w_n = _norm_token(w["word"])
        if c_n == w_n:
            continue
        # Aunt/Ant — Whisper.cpp transcribes both as 'ant'
        if {c_n, w_n} <= {"aunt", "ant"}:
            continue
        # Hyphen compound: canonical "fat-cat-hat" matches single token
        if "-" in c_n and w_n in c_n.split("-"):
            continue
        return False
    return True


def find_best_cluster(words_wcpp: list[dict], canonical: list[str],
                      cstart: float, cend: float,
                      look_back: float = 3.0,
                      look_after: float = 2.0) -> list[dict]:
    """Find the cluster of consecutive whisper.cpp words that semantically
    matches the canonical sequence and is closest in time to the cue.

    Falls back to nearest-by-time selection if no semantic match found.
    """
    n = len(canonical)
    if n == 0:
        return []
    # First gather all wcpp words within an extended window
    nearby = [
        w for w in words_wcpp
        if cstart - look_back <= w["start"] < cend + look_after
    ]
    if len(nearby) < n:
        return nearby

    # Semantic matching — find clusters whose tokens match canonical
    matches: list[list[dict]] = []
    for i in range(len(nearby) - n + 1):
        cluster = nearby[i:i + n]
        if _tokens_match(canonical, cluster):
            matches.append(cluster)

    if matches:
        # Pick cluster whose first word start is closest to cstart
        best = min(matches, key=lambda c: abs(c[0]["start"] - cstart))
        return best

    # Loose fallback: hyphen-compound expand canonical (e.g. "fat-cat-hat" → 3 tokens)
    expanded: list[str] = []
    for c in canonical:
        if "-" in _norm_token(c):
            for piece in _norm_token(c).split("-"):
                expanded.append(piece)
        else:
            expanded.append(_norm_token(c))
    if len(expanded) != len(canonical) and len(expanded) > 0:
        for i in range(len(nearby) - len(expanded) + 1):
            cluster = nearby[i:i + len(expanded)]
            if _tokens_match([*expanded], cluster):
                # Found expanded match — collapse back to canonical-len groups
                ratio = len(expanded) // n
                if ratio * n == len(expanded):
                    grouped = [cluster[j * ratio] for j in range(n)]
                    return grouped

    # Final fallback: nearest-by-time cluster
    best_idx = 0
    best_diff = abs(nearby[0]["start"] - cstart)
    for i in range(1, len(nearby) - n + 1):
        diff = abs(nearby[i]["start"] - cstart)
        if diff < best_diff:
            best_idx = i
            best_diff = diff
    return nearby[best_idx:best_idx + n]


def stretch_align_timings(chosen: list[dict], cstart: float,
                          cend: float) -> list[tuple[float, float]]:
    """Linearly stretch a whisper.cpp word pattern to fit the cue range.

    Each word's box ends at the scaled audio offset (showing silence as
    no-highlight gap), not at the next word's start.
    """
    n = len(chosen)
    if n == 0:
        return []
    p_start = chosen[0]["start"]
    p_end = chosen[-1].get("end", chosen[-1]["start"])
    p_dur = p_end - p_start
    cue_dur = cend - cstart
    if p_dur <= 0:
        per = cue_dur / max(n, 1)
        return [(cstart + i * per, cstart + (i + 1) * per) for i in range(n)]
    scale = cue_dur / p_dur
    GAP = 0.05
    timings: list[tuple[float, float]] = []
    for i, w in enumerate(chosen):
        rel_s = w["start"] - p_start
        ws = cstart + rel_s * scale
        # Use word's actual audio offset for box end (silence-aware)
        rel_e = w.get("end", w["start"]) - p_start
        we_audio = cstart + rel_e * scale
        # Cap by next word's scaled start - gap (so silence is silent)
        if i + 1 < n:
            next_rel = chosen[i + 1]["start"] - p_start
            next_scaled = cstart + next_rel * scale
            we = min(we_audio + 0.10, next_scaled - GAP)
        else:
            we = min(we_audio + 0.10, cend)
        if we - ws < 0.10:
            we = ws + 0.10
        timings.append((ws, we))
    return timings


def main() -> None:
    # Primary: OpenAI Whisper API (audio-aligned segment boundaries)
    transcript = json.loads(TRANSCRIPT.read_text())
    all_words = clean_whisper_words(transcript["words"])
    # Secondary: whisper.cpp turbo (used only for the 4-rep Black bag cluster)
    transcript_wcpp = json.loads(TRANSCRIPT_WCPP.read_text())
    all_words_wcpp = clean_whisper_words(transcript_wcpp["words"])

    ass: list[str] = []
    ass.append("[Script Info]")
    ass.append("ScriptType: v4.00+")
    ass.append(f"PlayResX: {PLAY_W}")
    ass.append(f"PlayResY: {PLAY_H}")
    ass.append("ScaledBorderAndShadow: yes")
    ass.append("WrapStyle: 2")
    ass.append("")
    ass.append("[V4+ Styles]")
    ass.append("Format: Name, Fontname, Fontsize, PrimaryColour, "
               "SecondaryColour, OutlineColour, BackColour, Bold, "
               "Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, "
               "Angle, BorderStyle, Outline, Shadow, Alignment, "
               "MarginL, MarginR, MarginV, Encoding")
    ass.append(
        f"Style: FullLine,{FONT_NAME_EN},{FONT_SIZE_PX},"
        "&H00FFFFFF,&H00FFFFFF,&H00202020,&H80000000,"
        "1,0,0,0,100,100,0,0,1,5,3,5,0,0,0,1"
    )
    ass.append(
        f"Style: FullLineJP,{FONT_NAME_JP},{JP_SIZE_PX},"
        "&H00FFFFFF,&H00FFFFFF,&H00202020,&H80000000,"
        "1,0,0,0,100,100,0,0,1,5,3,5,0,0,0,1"
    )
    ass.append(
        f"Style: Box,{FONT_NAME_EN},1,"
        f"&H00{BOX_COLOR_BGR},&H00{BOX_COLOR_BGR},"
        f"&H00{BOX_COLOR_BGR},&H00000000,"
        "0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1"
    )
    ass.append("")
    ass.append("[Events]")
    ass.append("Format: Layer, Start, End, Style, Name, MarginL, "
               "MarginR, MarginV, Effect, Text")

    OVERHANG = 0.10
    n_lines = 0
    n_boxes = 0

    last_baseline_en = PLAY_H - MARGIN_V
    last_baseline_jp = PLAY_H - MARGIN_V

    for cstart, cend, text, is_en in CUES:
        if cend <= cstart:
            continue
        baseline_y = last_baseline_en if is_en else last_baseline_jp

        words = split_words(text)

        if is_en:
            # Adaptive font: shrink to keep on one line within MAX_WIDTH
            cur_size, cur_font, cur_space = fit_one_line(
                words, FONT_PATH_EN, FONT_SIZE_PX, MAX_WIDTH
            )
            font = cur_font
            line_h = int(cur_size * 1.25)
            lines = [words]    # one line, fit_one_line guarantees this
            fs_tag = f"\\fs{cur_size}" if cur_size != FONT_SIZE_PX else ""
            positions = word_positions(lines, font, cur_space,
                                       line_h, baseline_y, PLAY_W)
            flat: list[str] = [w for line_words in lines for w in line_words]
            for tok, (cx, cy) in zip(flat, positions):
                tok_safe = tok.replace("{", "\\{").replace("}", "\\}")
                ass.append(
                    f"Dialogue: 1,{fmt_ts(cstart)},{fmt_ts(cend)},FullLine,,"
                    f"0,0,0,,{{\\an5\\pos({cx},{cy}){fs_tag}\\fad(80,80)}}"
                    f"{tok_safe}"
                )
                n_lines += 1
        else:
            font = _pil_jp
            line_h = JP_LINE_HEIGHT
            lines = wrap_words(words, font, SPACE_W, MAX_WIDTH)
            line_strs = [" ".join(line_words) for line_words in lines]
            full_text = "\\N".join(line_strs)
            full_safe = full_text.replace("{", "\\{").replace("}", "\\}")
            anchor_y = baseline_y + (line_h // 2)
            ass.append(
                f"Dialogue: 1,{fmt_ts(cstart)},{fmt_ts(cend)},FullLineJP,,"
                f"0,0,0,,{{\\an2\\pos({PLAY_W // 2},{anchor_y})"
                f"\\fad(80,80)}}{full_safe}"
            )
            n_lines += 1
            continue

        # Word-box timings — multi-strategy:
        #   1) Black bag → whisper.cpp 1:1 (only place wcpp wins)
        #   2) OpenAI 1:1 if word count matches (most accurate)
        #   3) whisper.cpp pattern stretched to fit OpenAI cue
        #   4) librosa onset detection as last resort
        flat_words: list[str] = [w for line_words in lines for w in line_words]
        timings: list[tuple[float, float]] = []
        n = len(flat_words)

        def _from_whisper_words(wsp: list[dict]) -> list[tuple[float, float]]:
            """Compute box (start, end) per word, respecting silence gaps.

            - Real audio offset (end > start + 0.05): use end + small overhang
            - Whisper "filled" the gap (end == next.start): treat as staccato,
              give a typical 0.40s box duration so silence between words
              shows no highlight.
            - 0-duration with long gap to next: word is elongated (e.g. Aunt
              held to "あーんと"), extend until next.start - small gap.
            - 0-duration with short gap to next: typical short word, 0.30s.
            """
            EFFECTIVE_ZERO = 0.05
            DEFAULT_DUR = 0.40
            ZERO_SHORT_DUR = 0.30
            GAP_BEFORE_NEXT = 0.05
            ELONG_GAP_THRESHOLD = 0.50
            out: list[tuple[float, float]] = []
            for i, ww in enumerate(wsp):
                w_start = ww["start"]
                w_end_audio = ww.get("end", w_start)
                next_start = (
                    wsp[i + 1]["start"] if i + 1 < len(wsp) else cend
                )
                gap = next_start - w_start

                is_last = (i + 1 == len(wsp))
                # Special case: last word sitting at exact cue end (Whisper
                # 0-duration sentinel) — give it brief display past cend
                if is_last and abs(w_start - cend) < 0.05:
                    out.append((w_start, w_start + 0.35))
                    continue

                if w_end_audio - w_start < EFFECTIVE_ZERO:
                    # 0-duration word
                    if gap > ELONG_GAP_THRESHOLD:
                        # Elongated (like "Aunt" held)
                        end = next_start - GAP_BEFORE_NEXT
                    else:
                        end = w_start + ZERO_SHORT_DUR
                elif abs(w_end_audio - next_start) < 0.05:
                    # Whisper extended this word to the next — staccato gap
                    end = w_start + DEFAULT_DUR
                else:
                    # Real audio offset detected
                    end = w_end_audio + OVERHANG

                # Cap at next_start - gap so silence shows no highlight
                end = min(end, next_start - GAP_BEFORE_NEXT)
                # Ensure minimum visible duration
                if end - w_start < 0.10:
                    end = min(w_start + 0.10, next_start)
                out.append((w_start, end))
            return out

        if is_blackbag_cue(text):
            wsp_w = whisper_in_range(all_words_wcpp, cstart, cend)
            if len(wsp_w) == n:
                timings = _from_whisper_words(wsp_w)
            else:
                # Black bag with mismatch → stretch+offset
                chosen = find_best_cluster(all_words_wcpp, flat_words, cstart, cend)
                if len(chosen) == n:
                    timings = stretch_align_timings(chosen, cstart, cend)
        else:
            wsp_o = whisper_in_range(all_words, cstart, cend)
            has_collision = any(
                wsp_o[i + 1]["start"] - wsp_o[i]["start"] < 0.05
                for i in range(len(wsp_o) - 1)
            )
            if len(wsp_o) == n and n > 0 and not has_collision:
                # OpenAI 1:1 — best when count matches
                timings = _from_whisper_words(wsp_o)
            else:
                # OpenAI mismatched → use whisper.cpp stretched to OpenAI cue
                chosen = find_best_cluster(all_words_wcpp, flat_words, cstart, cend)
                if len(chosen) == n:
                    timings = stretch_align_timings(chosen, cstart, cend)

        if not timings:
            # Final fallback: librosa onset detection
            starts = audio_word_starts(cstart, cend, max(1, n))
            for i, ws in enumerate(starts):
                we = starts[i + 1] if i + 1 < len(starts) else cend
                timings.append((ws, we))

        for (tok, (cx, cy), (w_start, w_end)) in zip(
            flat_words, positions, timings
        ):
            if w_end <= w_start:
                continue
            cw = measure(font, tok)
            box_w = cw + 2 * BOX_PAD_X
            box_h = cur_size + 2 * BOX_PAD_Y
            box_left = cx - box_w // 2
            box_top = cy - box_h // 2
            path = rounded_rect_path(box_w, box_h, CORNER_R)
            ass.append(
                f"Dialogue: 0,{fmt_ts(w_start)},{fmt_ts(w_end)},Box,,"
                f"0,0,0,,{{\\an7\\pos({box_left},{box_top})\\p1"
                f"\\1c&H{BOX_COLOR_BGR}&\\bord0\\shad0\\fad(40,60)}}{path}"
            )
            n_boxes += 1

    ASS_PATH.write_text("\n".join(ass), encoding="utf-8")
    print(f"  {n_lines} line cues + {n_boxes} word-box cues")
    print(f"  wrote {ASS_PATH.name}")

    if not SRC.exists():
        print(f"ERR: source not found: {SRC}")
        return
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(SRC),
        "-vf", f"subtitles={ASS_PATH}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-profile:v", "main", "-level", "4.0",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(OUT),
    ]
    print("burning subtitles via libass…")
    subprocess.run(cmd, check=True)
    print(f"done: {OUT.name} ({OUT.stat().st_size // 1024 // 1024} MB)")


if __name__ == "__main__":
    main()
