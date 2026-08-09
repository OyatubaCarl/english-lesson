#!/usr/bin/env python3
"""Build standalone phonics phoneme dictionary pages."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import quote


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "phonics-audio-items.json"
STARTER_PATHS = [
    BASE_DIR / "phonics-starter.html",
    BASE_DIR / "dist" / "phonics-starter.html",
]
OUT_PATHS = [
    BASE_DIR / "phonics-phoneme-dictionary.html",
    BASE_DIR / "phonics-phoneme-dictionary-preview.html",
]


SOUND_TO_ID = {
    "æ": "ae",
    "ɛ": "eh",
    "ɪ": "ih",
    "ɑ": "ah",
    "ʌ": "uh",
    "th": "th_voiceless",
    "θ": "th_voiceless",
    "ð": "th_voiced",
}


GROUPS = {
    "vowel": ("短母音", "A"),
    "stop": ("破裂音", "B"),
    "nasal": ("鼻音", "C"),
    "fricative": ("摩擦音", "D"),
    "approximant": ("接近音", "E"),
    "affricate": ("破擦音", "F"),
    "cluster": ("ブレンド", "G"),
}


GROUP_ORDER = ["vowel", "stop", "nasal", "fricative", "approximant", "affricate", "cluster"]
EXAMPLE_LIMIT = 6


RECORDING_NOTES = {
    "vowel": "短く明るく。文字名にしない。",
    "stop": "母音を足さず、息の破裂だけを短く。",
    "nasal": "声は入れるが伸ばしすぎない。",
    "fricative": "息の摩擦を一定に。母音を足さない。",
    "approximant": "短い導入音。日本語の母音を後ろに置かない。",
    "affricate": "破裂から摩擦へ一息で短く。",
    "cluster": "2音をなめらかに連結。別々に読ませすぎない。",
}


JOLLY_PATHS = {
    "p": "reference-audio/jolly-letter-sounds/northamerican_english/group1/p.mp3",
    "b": "reference-audio/jolly-letter-sounds/northamerican_english/group3/b.mp3",
    "t": "reference-audio/jolly-letter-sounds/northamerican_english/group1/t.mp3",
    "d": "reference-audio/jolly-letter-sounds/northamerican_english/group2/d.mp3",
    "k": "reference-audio/jolly-letter-sounds/northamerican_english/group2/ck.mp3",
    "g": "reference-audio/jolly-letter-sounds/northamerican_english/group3/g.mp3",
    "m": "reference-audio/jolly-letter-sounds/northamerican_english/group2/m.mp3",
    "n": "reference-audio/jolly-letter-sounds/northamerican_english/group1/n.mp3",
    "ng": "reference-audio/jolly-letter-sounds/northamerican_english/group5/ng.mp3",
    "f": "reference-audio/jolly-letter-sounds/northamerican_english/group3/f.mp3",
    "v": "reference-audio/jolly-letter-sounds/northamerican_english/group5/v.mp3",
    "s": "reference-audio/jolly-letter-sounds/northamerican_english/group1/s.mp3",
    "z": "reference-audio/jolly-letter-sounds/northamerican_english/group5/z.mp3",
    "h": "reference-audio/jolly-letter-sounds/northamerican_english/group2/h.mp3",
    "l": "reference-audio/jolly-letter-sounds/northamerican_english/group3/l.mp3",
    "r": "reference-audio/jolly-letter-sounds/northamerican_english/group2/r.mp3",
    "w": "reference-audio/jolly-letter-sounds/northamerican_english/group5/w.mp3",
    "y": "reference-audio/jolly-letter-sounds/northamerican_english/group6/y.mp3",
    "sh": "reference-audio/jolly-letter-sounds/northamerican_english/group6/sh.mp3",
    "ch": "reference-audio/jolly-letter-sounds/northamerican_english/group6/ch.mp3",
    "j": "reference-audio/jolly-letter-sounds/northamerican_english/group4/j.mp3",
    "th_voiceless": "reference-audio/jolly-letter-sounds/northamerican_english/group6/three.mp3",
    "th_voiced": "reference-audio/jolly-letter-sounds/northamerican_english/group6/this.mp3",
    "kw": "reference-audio/jolly-letter-sounds/northamerican_english/group7/qu.mp3",
    "ks": "reference-audio/jolly-letter-sounds/northamerican_english/group6/x.mp3",
    "ae": "reference-audio/jolly-letter-sounds/northamerican_english/group1/a.mp3",
    "eh": "reference-audio/jolly-letter-sounds/northamerican_english/group2/e.mp3",
    "ih": "reference-audio/jolly-letter-sounds/northamerican_english/group1/i.mp3",
    "ah": "reference-audio/jolly-letter-sounds/northamerican_english/group3/o.mp3",
    "uh": "reference-audio/jolly-letter-sounds/northamerican_english/group3/u.mp3",
}


def phoneme_id_for_sound(sound: str) -> str:
    return SOUND_TO_ID.get(sound, sound)


def extract_json_array_after(text: str, marker: str) -> list[dict]:
    marker_index = text.index(marker)
    array_start = text.index("[", marker_index)
    depth = 0
    in_string = False
    escaped = False
    for index, char in enumerate(text[array_start:], array_start):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return json.loads(text[array_start : index + 1])

    raise ValueError(f"Could not find array for {marker}")


def load_starter_cards() -> list[dict] | None:
    for starter_path in STARTER_PATHS:
        if starter_path.exists():
            return extract_json_array_after(starter_path.read_text(encoding="utf-8"), "const cards = [")
    return None


def resolve_word_image(word: dict) -> str | None:
    image = word.get("image")
    if image and (BASE_DIR / image).exists():
        return image

    fallback = Path("assets/card-generated") / f"{word['id']}.png"
    if (BASE_DIR / fallback).exists():
        return fallback.as_posix()

    return image


def build_example_word(word: dict) -> dict:
    return {
        "word": word["word"],
        "ipa": word["ipa"],
        "meaning": word.get("meaning", ""),
        "ruleLabel": word.get("ruleLabel", ""),
        "rule": word.get("rule", ""),
        "image": resolve_word_image(word),
    }


def build_phonemes(data: dict, words: list[dict]) -> list[dict]:
    examples: dict[str, list[dict]] = defaultdict(list)
    counts: Counter[str] = Counter()
    starter_filter_sounds: dict[str, str] = {}
    for word in words:
        seen_in_word = set()
        for segment in word["segments"]:
            raw_sound = segment["sound"]
            sound_id = phoneme_id_for_sound(raw_sound)
            counts[sound_id] += 1
            starter_filter_sounds.setdefault(sound_id, raw_sound)
            if sound_id not in seen_in_word:
                examples[sound_id].append(build_example_word(word))
                seen_in_word.add(sound_id)

    phonemes = sorted(
        data["phonemes"],
        key=lambda item: (GROUPS[item["type"]][1], -counts[item["id"]], item["id"]),
    )
    result = []
    for item in phonemes:
        sound_id = item["id"]
        group_key = item["type"]
        priority = "高" if counts[sound_id] >= 10 or group_key in ("vowel", "stop") else "中"
        starter_filter = f"sound:{starter_filter_sounds.get(sound_id, sound_id)}"
        result.append(
            {
                "id": sound_id,
                "label": item["label"],
                "ipa": item["ipa"],
                "group": group_key,
                "groupLabel": GROUPS[group_key][0],
                "priority": priority,
                "count": counts[sound_id],
                "examples": examples[sound_id][:EXAMPLE_LIMIT],
                "totalExamples": len(examples[sound_id]),
                "note": RECORDING_NOTES[group_key],
                "currentAudio": f"audio/phonics-generated/phonemes/{sound_id}.mp3",
                "jollyAudio": JOLLY_PATHS.get(sound_id),
                "starterFilter": starter_filter,
                "starterHref": f"phonics-starter.html#cards/{quote(starter_filter, safe='')}",
            }
        )
    return result


def build_html(phonemes: list[dict]) -> str:
    phoneme_json = json.dumps(phonemes, ensure_ascii=False, indent=6)
    group_json = json.dumps(
        [{"key": key, "label": GROUPS[key][0]} for key in GROUP_ORDER],
        ensure_ascii=False,
        indent=6,
    )
    return f"""<!doctype html>
<html lang="ja">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>フォニックス音素辞典</title>
    <style>
      :root {{
        color-scheme: light;
        --ink: #17202a;
        --muted: #5f6f7e;
        --line: #d7e0e8;
        --paper: #f5f7f9;
        --surface: #ffffff;
        --soft: #edf3f8;
        --blue: #235d9f;
        --blue-soft: #e8f1fb;
        --green: #247965;
        --green-soft: #e8f4f1;
        --orange: #b85f18;
        --orange-soft: #fff0e3;
        --rose: #a33b55;
        --rose-soft: #fae9ee;
        --shadow: 0 10px 28px rgba(23, 32, 42, 0.08);
      }}

      * {{
        box-sizing: border-box;
      }}

      html {{
        background: var(--paper);
      }}

      body {{
        margin: 0;
        min-height: 100vh;
        background:
          linear-gradient(180deg, #ffffff 0, var(--paper) 220px),
          var(--paper);
        color: var(--ink);
        font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Yu Gothic", "Segoe UI", sans-serif;
        line-height: 1.65;
        letter-spacing: 0;
      }}

      button,
      select {{
        font: inherit;
      }}

      button {{
        cursor: pointer;
      }}

      button:disabled {{
        cursor: not-allowed;
        opacity: 0.58;
      }}

      .shell {{
        width: min(1120px, calc(100% - 32px));
        margin: 0 auto;
        padding: 18px 0 48px;
      }}

      .app-bar {{
        position: sticky;
        top: 0;
        z-index: 10;
        display: grid;
        grid-template-columns: auto 1fr auto;
        gap: 14px;
        align-items: center;
        min-height: 66px;
        margin: 0 calc(50% - 50vw) 22px;
        padding: 10px max(16px, calc((100vw - 1120px) / 2));
        border-bottom: 1px solid var(--line);
        background: rgba(255, 255, 255, 0.94);
        backdrop-filter: blur(10px);
      }}

      .nav-actions {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        align-items: center;
      }}

      .brand {{
        min-width: 0;
      }}

      .brand strong {{
        display: block;
        overflow: hidden;
        color: var(--ink);
        font-size: 1rem;
        line-height: 1.2;
        text-overflow: ellipsis;
        white-space: nowrap;
      }}

      .brand span {{
        display: block;
        overflow: hidden;
        color: var(--muted);
        font-size: 0.82rem;
        line-height: 1.3;
        text-overflow: ellipsis;
        white-space: nowrap;
      }}

      .audio-status {{
        min-width: 156px;
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 8px 10px;
        background: var(--soft);
        color: var(--muted);
        font-size: 0.84rem;
        font-weight: 800;
        text-align: center;
      }}

      .btn {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        min-height: 38px;
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 8px 12px;
        background: var(--surface);
        color: var(--ink);
        font-weight: 850;
        text-decoration: none;
      }}

      .btn:hover,
      .btn:focus-visible {{
        border-color: var(--blue);
        outline: 0;
      }}

      .btn.primary {{
        border-color: var(--blue);
        background: var(--blue);
        color: #ffffff;
      }}

      .btn.secondary {{
        border-color: rgba(36, 121, 101, 0.36);
        background: var(--green-soft);
        color: var(--green);
      }}

      .btn.sound {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        min-width: 138px;
      }}

      .btn.jolly {{
        border-color: rgba(184, 95, 24, 0.34);
        background: var(--orange-soft);
        color: var(--orange);
      }}

      .btn.current {{
        border-color: rgba(35, 93, 159, 0.34);
        background: var(--blue-soft);
        color: var(--blue);
      }}

      .btn.card-link {{
        border-color: rgba(36, 121, 101, 0.36);
        background: var(--green-soft);
        color: var(--green);
      }}

      .view[hidden] {{
        display: none;
      }}

      .top-panel {{
        display: grid;
        grid-template-columns: minmax(0, 1fr) minmax(280px, 380px);
        gap: 22px;
        align-items: stretch;
        padding: 30px;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: var(--surface);
        box-shadow: var(--shadow);
      }}

      .kicker {{
        margin: 0 0 10px;
        color: var(--green);
        font-size: 0.82rem;
        font-weight: 900;
      }}

      h1,
      h2,
      h3,
      p {{
        letter-spacing: 0;
      }}

      h1 {{
        margin: 0;
        font-size: 2.15rem;
        line-height: 1.18;
      }}

      .lead {{
        max-width: 680px;
        margin: 12px 0 0;
        color: var(--muted);
        font-size: 1rem;
      }}

      .entry-panel {{
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        gap: 16px;
        border-left: 4px solid var(--orange);
        padding: 4px 0 4px 20px;
      }}

      .entry-panel h2 {{
        margin: 0;
        font-size: 1rem;
      }}

      .lesson-row {{
        display: grid;
        grid-template-columns: 1fr;
        gap: 8px;
      }}

      label {{
        color: var(--muted);
        font-size: 0.83rem;
        font-weight: 850;
      }}

      select {{
        width: 100%;
        min-height: 42px;
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 8px 10px;
        background: var(--surface);
        color: var(--ink);
      }}

      .entry-actions {{
        display: grid;
        grid-template-columns: 1fr;
        gap: 8px;
      }}

      .page-head {{
        display: grid;
        grid-template-columns: minmax(0, 1fr) auto;
        gap: 14px;
        align-items: end;
        margin-bottom: 18px;
      }}

      .page-head h1 {{
        font-size: 1.85rem;
      }}

      .count-line {{
        margin: 6px 0 0;
        color: var(--muted);
        font-size: 0.92rem;
        font-weight: 750;
      }}

      .toc-section {{
        margin-top: 22px;
      }}

      .toc-section h2 {{
        display: flex;
        gap: 8px;
        align-items: center;
        margin: 0 0 10px;
        font-size: 1rem;
      }}

      .section-mark {{
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: var(--green);
      }}

      .toc-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(168px, 1fr));
        gap: 10px;
      }}

      .phoneme-tile {{
        display: grid;
        grid-template-columns: minmax(0, 1fr) auto;
        gap: 8px;
        align-items: center;
        min-height: 92px;
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 12px;
        background: var(--surface);
        color: var(--ink);
        text-align: left;
      }}

      .phoneme-tile:hover,
      .phoneme-tile:focus-visible {{
        border-color: var(--blue);
        box-shadow: 0 8px 18px rgba(35, 93, 159, 0.12);
        outline: 0;
      }}

      .tile-label {{
        display: block;
        overflow-wrap: anywhere;
        font-size: 1.35rem;
        font-weight: 900;
        line-height: 1.1;
      }}

      .tile-meta {{
        display: block;
        margin-top: 5px;
        color: var(--muted);
        font-size: 0.82rem;
        font-weight: 750;
      }}

      .tile-ipa {{
        min-width: 54px;
        border-radius: 8px;
        padding: 7px 8px;
        background: var(--soft);
        color: var(--blue);
        font-family: "Charis SIL", "Noto Sans", "Segoe UI", sans-serif;
        font-weight: 900;
        text-align: center;
      }}

      .detail-layout {{
        display: grid;
        grid-template-columns: minmax(260px, 0.72fr) minmax(0, 1.28fr);
        gap: 18px;
        align-items: start;
      }}

      .sound-hero,
      .detail-panel {{
        border: 1px solid var(--line);
        border-radius: 8px;
        background: var(--surface);
        box-shadow: var(--shadow);
      }}

      .sound-hero {{
        padding: 18px;
      }}

      .tag-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        align-items: center;
      }}

      .tag {{
        display: inline-flex;
        align-items: center;
        min-height: 28px;
        border-radius: 999px;
        padding: 4px 9px;
        background: var(--green-soft);
        color: var(--green);
        font-size: 0.78rem;
        font-weight: 900;
      }}

      .tag.priority {{
        background: var(--rose-soft);
        color: var(--rose);
      }}

      .sound-label {{
        margin: 18px 0 0;
        overflow-wrap: anywhere;
        font-size: 4rem;
        font-weight: 950;
        line-height: 1;
      }}

      .sound-id {{
        margin: 8px 0 0;
        color: var(--muted);
        font-size: 0.92rem;
        font-weight: 800;
      }}

      .sound-ipa {{
        display: inline-block;
        margin-top: 16px;
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 8px 12px;
        background: var(--soft);
        color: var(--blue);
        font-family: "Charis SIL", "Noto Sans", "Segoe UI", sans-serif;
        font-size: 1.45rem;
        font-weight: 900;
      }}

      .sound-tools {{
        margin-top: 18px;
      }}

      .detail-panel {{
        padding: 18px;
      }}

      .detail-panel h2 {{
        margin: 0 0 10px;
        font-size: 1.05rem;
      }}

      .example-card-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(138px, 1fr));
        gap: 10px;
      }}

      .example-word-card {{
        display: grid;
        grid-template-rows: auto 1fr auto;
        gap: 8px;
        border: 1px solid var(--line);
        border-radius: 8px;
        min-height: 178px;
        padding: 9px;
        background: #ffffff;
        color: var(--ink);
      }}

      .example-word-card[data-rule="short-a"] {{
        border-top: 4px solid var(--green);
      }}

      .example-word-card[data-rule="short-e"] {{
        border-top: 4px solid var(--rose);
      }}

      .example-word-card[data-rule="short-i"] {{
        border-top: 4px solid var(--blue);
      }}

      .example-word-card[data-rule="short-o"] {{
        border-top: 4px solid var(--orange);
      }}

      .example-word-card[data-rule="short-u"] {{
        border-top: 4px solid #6952b8;
      }}

      .example-art {{
        display: grid;
        min-height: 82px;
        place-items: center;
        overflow: hidden;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: var(--soft);
      }}

      .example-art img {{
        width: 100%;
        height: 86px;
        object-fit: contain;
        padding: 4px;
      }}

      .example-art-fallback {{
        display: grid;
        width: 54px;
        height: 54px;
        place-items: center;
        border-radius: 50%;
        background: #ffffff;
        color: var(--blue);
        font-size: 1.55rem;
        font-weight: 950;
      }}

      .example-word {{
        display: block;
        margin: 0;
        overflow-wrap: anywhere;
        font-size: 1.35rem;
        font-weight: 950;
        line-height: 1.05;
      }}

      .example-ipa {{
        display: block;
        margin-top: 3px;
        color: var(--muted);
        font-family: "Charis SIL", "Noto Sans", "Segoe UI", sans-serif;
        font-size: 0.86rem;
        font-weight: 850;
      }}

      .example-meaning {{
        margin: 0;
        color: var(--muted);
        font-size: 0.78rem;
        font-weight: 750;
        line-height: 1.45;
      }}

      .note-box {{
        margin: 0 0 18px;
        border-left: 4px solid var(--green);
        padding: 9px 0 9px 14px;
        color: var(--ink);
      }}

      .audio-row,
      .detail-actions {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        align-items: center;
      }}

      .detail-actions {{
        justify-content: space-between;
        margin-top: 20px;
        padding-top: 16px;
        border-top: 1px solid var(--line);
      }}

      .progress {{
        color: var(--muted);
        font-size: 0.9rem;
        font-weight: 850;
      }}

      .empty-state {{
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 28px;
        background: var(--surface);
      }}

      @media (max-width: 820px) {{
        .shell {{
          width: min(100% - 20px, 1120px);
          padding-top: 10px;
        }}

        .app-bar {{
          grid-template-columns: 1fr;
          align-items: stretch;
          padding: 10px;
        }}

        .audio-status {{
          text-align: left;
        }}

        .top-panel,
        .page-head,
        .detail-layout {{
          grid-template-columns: 1fr;
        }}

        .top-panel {{
          padding: 18px;
        }}

        .entry-panel {{
          border-left: 0;
          border-top: 4px solid var(--orange);
          padding: 16px 0 0;
        }}

        h1 {{
          font-size: 1.72rem;
        }}

        .sound-label {{
          font-size: 3.2rem;
        }}

        .btn.sound {{
          min-width: 100%;
        }}
      }}
    </style>
  </head>
  <body>
    <div class="shell">
      <header class="app-bar">
        <div class="nav-actions">
          <a class="btn" href="phonics-starter.html#soundIndex">音の目次へ戻る</a>
          <button class="btn secondary" type="button" data-route="toc" data-toc-button>目次に戻る</button>
        </div>
        <div class="brand" aria-live="polite">
          <strong id="barTitle">音素辞典</strong>
          <span id="barSubtitle">目次</span>
        </div>
        <div class="audio-status" id="audioStatus">音声待機中</div>
      </header>

      <section class="view" id="tocView" aria-labelledby="tocTitle" hidden>
        <div class="page-head">
          <div>
            <p class="kicker">Phoneme Dictionary</p>
            <h1 id="tocTitle">音素辞典 目次</h1>
            <p class="count-line" id="tocCount"></p>
          </div>
        </div>
        <div id="tocRoot"></div>
      </section>

      <section class="view" id="detailView" aria-labelledby="detailTitle" hidden>
        <div class="page-head">
          <div>
            <p class="kicker">Phoneme Detail</p>
            <h1 id="detailTitle">音素辞典</h1>
            <p class="count-line" id="detailProgress"></p>
          </div>
        </div>
        <div class="detail-layout" id="detailRoot"></div>
      </section>
    </div>

    <script>
      const PHONEMES = {phoneme_json};
      const GROUPS = {group_json};

      const views = {{
        toc: document.querySelector("#tocView"),
        detail: document.querySelector("#detailView"),
      }};
      const barTitle = document.querySelector("#barTitle");
      const barSubtitle = document.querySelector("#barSubtitle");
      const audioStatus = document.querySelector("#audioStatus");
      const tocRoot = document.querySelector("#tocRoot");
      const tocCount = document.querySelector("#tocCount");
      const detailRoot = document.querySelector("#detailRoot");
      const detailProgress = document.querySelector("#detailProgress");
      const tocButton = document.querySelector("[data-toc-button]");

      let activeAudio = null;
      let tocRendered = false;

      function setRoute(name, id) {{
        if (name === "toc") location.hash = "phoneme-index";
        if (name === "detail" && id) location.hash = `phoneme:${{encodeURIComponent(id)}}`;
      }}

      function getRoute() {{
        const hash = decodeURIComponent(location.hash.replace(/^#/, "")) || "phoneme-index";
        if (hash === "phoneme-index") return {{ name: "toc" }};
        if (hash.startsWith("phoneme:")) return {{ name: "detail", id: hash.slice("phoneme:".length) }};
        return {{ name: "toc" }};
      }}

      function showView(name) {{
        Object.entries(views).forEach(([viewName, node]) => {{
          node.hidden = viewName !== name;
        }});
        tocButton.hidden = name === "toc";
        barTitle.textContent = "音素辞典";
        barSubtitle.textContent = name === "detail" ? "選択中の音素" : "目次";
      }}

      function createText(tagName, className, text) {{
        const node = document.createElement(tagName);
        if (className) node.className = className;
        node.textContent = text;
        return node;
      }}

      function renderToc() {{
        if (tocRendered) return;
        tocCount.textContent = `${{PHONEMES.length}} 音素`;
        const fragment = document.createDocumentFragment();
        GROUPS.forEach((group) => {{
          const items = PHONEMES.filter((item) => item.group === group.key);
          if (!items.length) return;

          const section = document.createElement("section");
          section.className = "toc-section";
          const heading = document.createElement("h2");
          heading.append(createText("span", "section-mark", ""));
          heading.append(document.createTextNode(`${{group.label}} ${{items.length}}`));

          const grid = document.createElement("div");
          grid.className = "toc-grid";
          items.forEach((item) => {{
            const button = document.createElement("button");
            button.className = "phoneme-tile";
            button.type = "button";
            button.dataset.phonemeId = item.id;
            button.setAttribute("aria-label", `${{item.label}} /${{item.ipa}}/`);

            const text = document.createElement("span");
            text.append(createText("span", "tile-label", item.label));
            text.append(createText("span", "tile-meta", `例 ${{item.totalExamples}}`));
            button.append(text);
            button.append(createText("span", "tile-ipa", `/${{item.ipa}}/`));
            grid.append(button);
          }});

          section.append(heading, grid);
          fragment.append(section);
        }});
        tocRoot.replaceChildren(fragment);
        tocRendered = true;
      }}

      function renderDetail(id) {{
        const index = PHONEMES.findIndex((item) => item.id === id);
        if (index === -1) {{
          detailProgress.textContent = "";
          const empty = document.createElement("div");
          empty.className = "empty-state";
          empty.append(createText("p", "", "指定された音素が見つかりません。"));
          detailRoot.replaceChildren(empty);
          return;
        }}

        const item = PHONEMES[index];
        const next = PHONEMES[(index + 1) % PHONEMES.length];
        detailProgress.textContent = `${{index + 1}} / ${{PHONEMES.length}}`;

        const hero = document.createElement("aside");
        hero.className = "sound-hero";
        const tags = document.createElement("div");
        tags.className = "tag-row";
        tags.append(createText("span", "tag", item.groupLabel));
        hero.append(tags);
        hero.append(createText("div", "sound-label", item.label));
        hero.append(createText("div", "sound-id", item.id));
        hero.append(createText("div", "sound-ipa", `/${{item.ipa}}/`));

        const heroTools = document.createElement("div");
        heroTools.className = "audio-row sound-tools";
        heroTools.append(audioButton("音を聞く", item.currentAudio, "current"));
        if (item.starterHref) {{
          const cardLink = document.createElement("a");
          cardLink.className = "btn card-link";
          cardLink.href = item.starterHref;
          cardLink.textContent = "単語カードで見る";
          heroTools.append(cardLink);
        }}
        hero.append(heroTools);

        const panel = document.createElement("article");
        panel.className = "detail-panel";
        panel.append(createText("h2", "", "例単語"));
        if (item.totalExamples > item.examples.length) {{
          panel.append(createText("p", "count-line", `${{item.totalExamples}}件から代表例 ${{item.examples.length}}件を表示`));
        }}
        const examples = document.createElement("div");
        examples.className = "example-card-grid";
        if (item.examples.length) {{
          item.examples.forEach((example) => examples.append(renderExampleCard(example)));
        }} else {{
          examples.append(createText("p", "note-box", "追加予定"));
        }}
        panel.append(examples);

        const actions = document.createElement("div");
        actions.className = "detail-actions";
        actions.append(createText("span", "progress", `次: ${{next.label}}`));
        const nextButton = document.createElement("button");
        nextButton.className = "btn primary";
        nextButton.type = "button";
        nextButton.dataset.nextId = next.id;
        nextButton.textContent = "次へ";
        actions.append(nextButton);
        panel.append(actions);

        detailRoot.replaceChildren(hero, panel);
      }}

      function renderExampleCard(example) {{
        const card = document.createElement("section");
        card.className = "example-word-card";
        card.dataset.rule = example.rule || "";

        const art = document.createElement("div");
        art.className = "example-art";
        const fallback = createText("span", "example-art-fallback", (example.word || "?").slice(0, 1).toUpperCase());
        if (example.image) {{
          const image = document.createElement("img");
          image.src = example.image;
          image.alt = "";
          image.loading = "lazy";
          image.setAttribute("aria-hidden", "true");
          image.addEventListener("error", () => {{
            image.remove();
            art.append(fallback);
          }}, {{ once: true }});
          art.append(image);
        }} else {{
          art.append(fallback);
        }}

        const body = document.createElement("div");
        body.append(createText("strong", "example-word", example.word));
        body.append(createText("span", "example-ipa", `/${{example.ipa}}/`));

        const meaning = createText("p", "example-meaning", example.meaning || example.ruleLabel || "");
        card.append(art, body, meaning);
        return card;
      }}

      function audioButton(label, path, kind) {{
        const button = document.createElement("button");
        button.className = `btn sound ${{kind}}`;
        button.type = "button";
        button.disabled = !path;
        button.dataset.audio = path || "";
        button.dataset.audioLabel = label;
        button.textContent = path ? label : `${{label}}なし`;
        return button;
      }}

      function setStatus(text) {{
        audioStatus.textContent = text;
      }}

      async function playAudio(path, label) {{
        if (!path) return;
        if (activeAudio) {{
          activeAudio.pause();
          activeAudio.currentTime = 0;
        }}
        activeAudio = new Audio(path);
        setStatus(`${{label}} 再生中`);
        try {{
          await activeAudio.play();
        }} catch (error) {{
          setStatus(`${{label}} を再生できません`);
          return;
        }}
        activeAudio.addEventListener("ended", () => setStatus("音声待機中"), {{ once: true }});
        activeAudio.addEventListener("error", () => setStatus(`${{label}} を再生できません`), {{ once: true }});
      }}

      function route() {{
        const current = getRoute();
        if (current.name === "toc") {{
          renderToc();
          showView("toc");
        }} else if (current.name === "detail") {{
          renderDetail(current.id);
          showView("detail");
        }}
        window.scrollTo(0, 0);
      }}

      document.addEventListener("click", (event) => {{
        const routeButton = event.target.closest("[data-route]");
        if (routeButton) {{
          setRoute(routeButton.dataset.route);
          return;
        }}

        const tile = event.target.closest("[data-phoneme-id]");
        if (tile) {{
          setRoute("detail", tile.dataset.phonemeId);
          return;
        }}

        const nextButton = event.target.closest("[data-next-id]");
        if (nextButton) {{
          setRoute("detail", nextButton.dataset.nextId);
          return;
        }}

        const audio = event.target.closest("[data-audio]");
        if (audio) {{
          playAudio(audio.dataset.audio, audio.dataset.audioLabel || audio.textContent.trim());
        }}
      }});

      window.addEventListener("hashchange", route);
      route();
    </script>
  </body>
</html>
"""


def main() -> int:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    words = load_starter_cards() or data["words"]
    html = build_html(build_phonemes(data, words))
    for out_path in OUT_PATHS:
        out_path.write_text(html, encoding="utf-8")
        print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
