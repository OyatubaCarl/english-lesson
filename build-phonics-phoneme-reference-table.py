#!/usr/bin/env python3
"""Build an HTML work table for required phonics phonemes.

The page is a local recording/reference aid. Jolly Phonics files are linked as
reference audio only and should not be copied into published distributable
materials unless permission is obtained.
"""
from __future__ import annotations

import html
import json
from collections import Counter, defaultdict
from pathlib import Path


DATA_PATH = Path("phonics-audio-items.json")
OUT_PATH = Path("phonics-phoneme-reference-table.html")


SOUND_TO_ID = {
    "æ": "ae",
    "ɛ": "eh",
    "ɪ": "ih",
    "ɑ": "ah",
    "ʌ": "uh",
    "θ": "th_voiceless",
    "ð": "th_voiced",
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


JOLLY_ALL = [
    ("a", "short a", "group1/a.mp3"),
    ("i", "short i", "group1/i.mp3"),
    ("n", "n", "group1/n.mp3"),
    ("p", "p", "group1/p.mp3"),
    ("s", "s", "group1/s.mp3"),
    ("t", "t", "group1/t.mp3"),
    ("ck", "c/k", "group2/ck.mp3"),
    ("d", "d", "group2/d.mp3"),
    ("e", "short e", "group2/e.mp3"),
    ("h", "h", "group2/h.mp3"),
    ("m", "m", "group2/m.mp3"),
    ("r", "r", "group2/r.mp3"),
    ("b", "b", "group3/b.mp3"),
    ("f", "f", "group3/f.mp3"),
    ("g", "g", "group3/g.mp3"),
    ("l", "l", "group3/l.mp3"),
    ("o", "short o", "group3/o.mp3"),
    ("u", "short u", "group3/u.mp3"),
    ("ai", "long a", "group4/ai.mp3"),
    ("ee", "long e", "group4/ee.mp3"),
    ("ie", "long i", "group4/ie.mp3"),
    ("j", "j", "group4/j.mp3"),
    ("oa", "long o", "group4/oa.mp3"),
    ("or", "or", "group4/or.mp3"),
    ("book", "short oo", "group5/book.mp3"),
    ("moon", "long oo", "group5/moon.mp3"),
    ("ng", "ng", "group5/ng.mp3"),
    ("v", "v", "group5/v.mp3"),
    ("w", "w", "group5/w.mp3"),
    ("z", "z", "group5/z.mp3"),
    ("ch", "ch", "group6/ch.mp3"),
    ("sh", "sh", "group6/sh.mp3"),
    ("three", "th /θ/", "group6/three.mp3"),
    ("this", "th /ð/", "group6/this.mp3"),
    ("x", "x /ks/", "group6/x.mp3"),
    ("y", "y", "group6/y.mp3"),
    ("ar", "ar", "group7/ar.mp3"),
    ("er", "er", "group7/er.mp3"),
    ("oi", "oi", "group7/oi.mp3"),
    ("ou", "ou", "group7/ou.mp3"),
    ("qu", "qu /kw/", "group7/qu.mp3"),
    ("ue", "ue", "group7/ue.mp3"),
]


GROUPS = {
    "vowel": ("短母音", "A"),
    "stop": ("破裂音", "B"),
    "nasal": ("鼻音", "C"),
    "fricative": ("摩擦音", "D"),
    "approximant": ("接近音", "E"),
    "affricate": ("破擦音", "F"),
    "cluster": ("ブレンド", "G"),
}


RECORDING_NOTES = {
    "vowel": "短く明るく。文字名にしない。",
    "stop": "母音を足さず、息の破裂だけを短く。",
    "nasal": "声は入れるが伸ばしすぎない。",
    "fricative": "息の摩擦を一定に。母音を足さない。",
    "approximant": "短い導入音。日本語の母音を後ろに置かない。",
    "affricate": "破裂から摩擦へ一息で短く。",
    "cluster": "2音をなめらかに連結。別々に読ませすぎない。",
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def phoneme_id_for_sound(sound: str) -> str:
    return SOUND_TO_ID.get(sound, sound)


def audio_button(label: str, path: str | None, kind: str) -> str:
    if not path:
        return '<span class="missing">なし</span>'
    return (
        f'<button class="sound-button {kind}" type="button" '
        f'data-audio="{esc(path)}" data-label="{esc(label)}">'
        f'<span class="play-icon" aria-hidden="true">▶</span>{esc(label)}</button>'
    )


def build_rows(data: dict) -> tuple[str, dict[str, int]]:
    examples: dict[str, list[str]] = defaultdict(list)
    counts: Counter[str] = Counter()
    for word in data["words"]:
        seen_in_word = set()
        for segment in word["segments"]:
            sound_id = phoneme_id_for_sound(segment["sound"])
            counts[sound_id] += 1
            if sound_id not in seen_in_word:
                examples[sound_id].append(f'{word["word"]} /{word["ipa"]}/')
                seen_in_word.add(sound_id)

    rows = []
    phonemes = sorted(
        data["phonemes"],
        key=lambda item: (GROUPS[item["type"]][1], -counts[item["id"]], item["id"]),
    )
    for item in phonemes:
        sound_id = item["id"]
        group_label = GROUPS[item["type"]][0]
        example_text = "、".join(examples[sound_id][:8]) or "追加予定"
        generated = f"audio/phonics-generated/phonemes/{sound_id}.mp3"
        jolly = JOLLY_PATHS.get(sound_id)
        priority = "高" if counts[sound_id] >= 10 or item["type"] in ("vowel", "stop") else "中"
        rows.append(
            f"""
            <tr data-group="{esc(item['type'])}">
              <td><span class="pill">{esc(group_label)}</span></td>
              <td>
                <strong class="grapheme">{esc(item['label'])}</strong>
                <span class="id">{esc(sound_id)}</span>
              </td>
              <td><span class="ipa">/{esc(item['ipa'])}/</span></td>
              <td>{esc(priority)}</td>
              <td>{esc(counts[sound_id])}</td>
              <td>{esc(example_text)}</td>
              <td>{audio_button('Jolly参照', jolly, 'jolly')}</td>
              <td>{audio_button('現在音源', generated, 'current')}</td>
              <td>{esc(RECORDING_NOTES[item["type"]])}</td>
            </tr>
            """.strip()
        )
    return "\n".join(rows), dict(counts)


def build_jolly_board() -> str:
    items = []
    base = "reference-audio/jolly-letter-sounds/northamerican_english"
    for grapheme, label, rel_path in JOLLY_ALL:
        path = f"{base}/{rel_path}"
        items.append(
            f"""
            <button class="jolly-tile" type="button" data-audio="{esc(path)}" data-label="Jolly {esc(grapheme)}">
              <span>{esc(grapheme)}</span>
              <small>{esc(label)}</small>
            </button>
            """.strip()
        )
    return "\n".join(items)


def main() -> int:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    rows, counts = build_rows(data)
    total_required = len(data["phonemes"])
    total_words = len(data["words"])
    jolly_board = build_jolly_board()
    html_text = f"""<!doctype html>
<html lang="ja">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Phonics 音素一覧表</title>
    <style>
      :root {{
        --ink: #17202a;
        --muted: #5f6f7e;
        --line: #d8e0e7;
        --paper: #f6f8fb;
        --white: #ffffff;
        --green: #1f8a70;
        --orange: #c76a1a;
        --blue: #2364aa;
      }}

      * {{ box-sizing: border-box; }}

      body {{
        margin: 0;
        background: var(--paper);
        color: var(--ink);
        font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Yu Gothic", "Segoe UI", sans-serif;
      }}

      main {{
        width: min(1280px, calc(100% - 32px));
        margin: 0 auto;
        padding: 28px 0 48px;
      }}

      header {{
        display: grid;
        grid-template-columns: 1fr auto;
        gap: 16px;
        align-items: end;
        margin-bottom: 18px;
      }}

      h1 {{
        margin: 0;
        font-size: clamp(2rem, 4vw, 4rem);
        letter-spacing: 0;
      }}

      h2 {{
        margin: 0 0 12px;
        font-size: 1.35rem;
        letter-spacing: 0;
      }}

      p {{
        margin: 8px 0 0;
        color: var(--muted);
        line-height: 1.7;
      }}

      .status {{
        min-width: 180px;
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 10px 12px;
        background: var(--white);
        color: var(--muted);
        font-weight: 800;
        text-align: center;
      }}

      .notice,
      .panel {{
        border: 1px solid var(--line);
        border-radius: 8px;
        background: var(--white);
      }}

      .notice {{
        padding: 14px 16px;
        margin-bottom: 16px;
      }}

      .notice strong {{
        color: var(--orange);
      }}

      .stats {{
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 10px;
        margin: 16px 0;
      }}

      .stat {{
        border: 1px solid var(--line);
        border-radius: 8px;
        background: var(--white);
        padding: 14px;
      }}

      .stat strong {{
        display: block;
        font-size: 1.8rem;
        line-height: 1;
      }}

      .stat span {{
        display: block;
        margin-top: 4px;
        color: var(--muted);
        font-size: 0.86rem;
        font-weight: 750;
      }}

      .toolbar {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 18px 0 12px;
      }}

      .filter-button,
      .sound-button,
      .jolly-tile {{
        border: 1px solid var(--line);
        border-radius: 8px;
        background: var(--white);
        color: var(--ink);
        cursor: pointer;
        font: inherit;
        font-weight: 800;
      }}

      .filter-button {{
        min-height: 38px;
        padding: 8px 12px;
      }}

      .filter-button.is-active {{
        border-color: var(--ink);
        background: var(--ink);
        color: var(--white);
      }}

      .table-wrap {{
        overflow-x: auto;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: var(--white);
      }}

      table {{
        width: 100%;
        border-collapse: collapse;
        min-width: 1120px;
      }}

      th,
      td {{
        border-bottom: 1px solid var(--line);
        padding: 12px;
        vertical-align: middle;
        text-align: left;
      }}

      th {{
        position: sticky;
        top: 0;
        background: #edf3f8;
        z-index: 1;
        color: #34495e;
        font-size: 0.82rem;
        letter-spacing: 0;
      }}

      tr:last-child td {{
        border-bottom: 0;
      }}

      .pill {{
        display: inline-block;
        min-width: 70px;
        border-radius: 999px;
        padding: 5px 8px;
        background: #e8f4f1;
        color: #17624f;
        font-size: 0.8rem;
        font-weight: 850;
        text-align: center;
      }}

      .grapheme {{
        display: block;
        font-size: 1.35rem;
      }}

      .id {{
        display: block;
        color: var(--muted);
        font-size: 0.78rem;
      }}

      .ipa {{
        font-family: "Charis SIL", "Noto Sans", "Segoe UI", sans-serif;
        font-size: 1.2rem;
        font-weight: 850;
      }}

      .sound-button {{
        min-width: 104px;
        min-height: 38px;
        padding: 8px 10px;
      }}

      .sound-button.jolly {{
        border-color: rgba(199, 106, 26, 0.45);
        color: var(--orange);
      }}

      .sound-button.current {{
        border-color: rgba(35, 100, 170, 0.45);
        color: var(--blue);
      }}

      .play-icon {{
        display: inline-block;
        margin-right: 6px;
      }}

      .missing {{
        color: var(--muted);
        font-weight: 700;
      }}

      .panel {{
        margin-top: 22px;
        padding: 16px;
      }}

      .jolly-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(92px, 1fr));
        gap: 8px;
      }}

      .jolly-tile {{
        min-height: 72px;
        padding: 10px;
        text-align: left;
      }}

      .jolly-tile span {{
        display: block;
        font-size: 1.35rem;
      }}

      .jolly-tile small {{
        display: block;
        margin-top: 4px;
        color: var(--muted);
        font-weight: 750;
      }}

      @media (max-width: 760px) {{
        main {{
          width: min(100% - 20px, 1280px);
          padding-top: 18px;
        }}

        header,
        .stats {{
          grid-template-columns: 1fr;
        }}

        .status {{
          text-align: left;
        }}
      }}
    </style>
  </head>
  <body>
    <main>
      <header>
        <div>
          <h1>Phonics 音素一覧表</h1>
          <p>このページは、録音・音源選定・カード実装のための作業台です。</p>
        </div>
        <div class="status" id="audioStatus">音声待機中</div>
      </header>

      <section class="notice">
        <strong>Jolly Phonics音源は参照専用です。</strong>
        <p>
          ここでは発音確認と自録りガイドとして再生できます。公開教材や配布物へそのまま組み込む場合は、
          Jolly Learning から利用許可を取る必要があります。
        </p>
      </section>

      <section class="stats" aria-label="音素数">
        <div class="stat"><strong>{total_required}</strong><span>必要音素</span></div>
        <div class="stat"><strong>{total_words}</strong><span>登録単語カード</span></div>
        <div class="stat"><strong>{len(JOLLY_ALL)}</strong><span>Jolly参照音源</span></div>
      </section>

      <nav class="toolbar" aria-label="音素フィルター">
        <button class="filter-button is-active" type="button" data-filter="all">すべて</button>
        <button class="filter-button" type="button" data-filter="vowel">短母音</button>
        <button class="filter-button" type="button" data-filter="stop">破裂音</button>
        <button class="filter-button" type="button" data-filter="nasal">鼻音</button>
        <button class="filter-button" type="button" data-filter="fricative">摩擦音</button>
        <button class="filter-button" type="button" data-filter="approximant">接近音</button>
        <button class="filter-button" type="button" data-filter="affricate">破擦音</button>
        <button class="filter-button" type="button" data-filter="cluster">ブレンド</button>
      </nav>

      <section class="table-wrap" aria-label="必要音素一覧">
        <table>
          <thead>
            <tr>
              <th>区分</th>
              <th>文字</th>
              <th>IPA</th>
              <th>録音優先</th>
              <th>使用数</th>
              <th>例単語</th>
              <th>Jolly参照</th>
              <th>現在音源</th>
              <th>録音メモ</th>
            </tr>
          </thead>
          <tbody id="phonemeRows">
            {rows}
          </tbody>
        </table>
      </section>

      <section class="panel" aria-labelledby="jollyBoardTitle">
        <h2 id="jollyBoardTitle">Jolly Phonics 42音源 参照ボード</h2>
        <p>現在ページで扱う音素以外も、後続レッスンの録音参照として聞けます。</p>
        <div class="jolly-grid">
          {jolly_board}
        </div>
      </section>
    </main>

    <script>
      const status = document.querySelector("#audioStatus");
      let activeAudio = null;

      function setStatus(text) {{
        status.textContent = text;
      }}

      async function playAudio(path, label) {{
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

      document.addEventListener("click", (event) => {{
        const audioButton = event.target.closest("[data-audio]");
        if (audioButton) {{
          playAudio(audioButton.dataset.audio, audioButton.dataset.label || audioButton.textContent.trim());
          return;
        }}

        const filterButton = event.target.closest("[data-filter]");
        if (filterButton) {{
          const value = filterButton.dataset.filter;
          document.querySelectorAll("[data-filter]").forEach((button) => button.classList.toggle("is-active", button === filterButton));
          document.querySelectorAll("#phonemeRows tr").forEach((row) => {{
            row.hidden = value !== "all" && row.dataset.group !== value;
          }});
        }}
      }});
    </script>
  </body>
</html>
"""
    OUT_PATH.write_text(html_text, encoding="utf-8")
    print(f"wrote {OUT_PATH} ({total_required} phonemes)")
    print(f"most used: {sorted(counts.items(), key=lambda item: item[1], reverse=True)[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
