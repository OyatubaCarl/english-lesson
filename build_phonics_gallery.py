"""Scan phonics-songs/ and emit a single-page HTML gallery for review.

Run anytime new images are dropped into phonics-songs/. The output
phonics_gallery.html opens locally in any browser; images are grouped by
subfolder, click-to-zoom, with filename + size shown.
"""
from __future__ import annotations

import html
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "phonics-songs"
OUT = ROOT / "phonics_gallery.html"

EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def collect() -> dict[str, list[Path]]:
    groups: dict[str, list[Path]] = {}
    if not SRC.exists():
        return groups
    for p in sorted(SRC.rglob("*")):
        if p.is_file() and p.suffix.lower() in EXTS:
            rel_parent = p.parent.relative_to(SRC)
            key = str(rel_parent) if str(rel_parent) != "." else "(root)"
            groups.setdefault(key, []).append(p)
    return groups


def fmt_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f}{unit}"
        n /= 1024
    return f"{n:.1f}TB"


CSS = """
:root {
  --bg: oklch(98% 0.005 95);
  --panel: oklch(100% 0 0);
  --ink: oklch(20% 0.01 250);
  --muted: oklch(45% 0.01 250);
  --accent: oklch(62% 0.18 30);
  --border: oklch(90% 0.005 250);
  --shadow: 0 1px 3px oklch(0% 0 0 / 0.06), 0 4px 12px oklch(0% 0 0 / 0.04);
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: -apple-system, "Hiragino Sans", "Yu Gothic", system-ui, sans-serif;
  background: var(--bg);
  color: var(--ink);
  line-height: 1.5;
}
header {
  position: sticky; top: 0; z-index: 10;
  background: var(--panel);
  border-bottom: 1px solid var(--border);
  padding: 16px 24px;
  display: flex; align-items: center; gap: 16px;
  box-shadow: var(--shadow);
}
h1 { margin: 0; font-size: 1.25rem; letter-spacing: 0.01em; }
.count { color: var(--muted); font-size: 0.9rem; }
.controls { margin-left: auto; display: flex; gap: 8px; align-items: center; }
.controls input[type="search"] {
  padding: 6px 10px; border: 1px solid var(--border);
  border-radius: 6px; background: var(--bg);
  font-size: 0.9rem; width: 200px;
}
.controls select {
  padding: 6px 10px; border: 1px solid var(--border);
  border-radius: 6px; background: var(--bg); font-size: 0.9rem;
}
main { padding: 24px; }
section.group { margin-bottom: 40px; }
section.group h2 {
  margin: 0 0 12px 0;
  font-size: 1rem;
  color: var(--accent);
  letter-spacing: 0.02em;
  text-transform: uppercase;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}
.card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  display: flex; flex-direction: column;
  cursor: zoom-in;
}
.card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}
.card img {
  width: 100%; aspect-ratio: 1 / 1; object-fit: cover;
  display: block; background: oklch(95% 0.005 95);
}
.card .meta {
  padding: 8px 10px;
  font-size: 0.78rem;
  display: flex; justify-content: space-between; gap: 8px;
}
.card .name {
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  flex: 1; min-width: 0;
}
.card .size { color: var(--muted); flex-shrink: 0; }
/* Lightbox */
.lightbox {
  position: fixed; inset: 0;
  background: oklch(0% 0 0 / 0.85);
  display: none; align-items: center; justify-content: center;
  z-index: 100; padding: 24px; cursor: zoom-out;
}
.lightbox.open { display: flex; }
.lightbox img { max-width: 100%; max-height: 100%; box-shadow: 0 8px 40px oklch(0% 0 0 / 0.5); }
.lightbox .caption {
  position: fixed; bottom: 16px; left: 50%; transform: translateX(-50%);
  color: white; background: oklch(20% 0.01 250 / 0.85);
  padding: 8px 16px; border-radius: 6px; font-size: 0.9rem;
}
.empty {
  text-align: center; padding: 80px 24px; color: var(--muted);
}
"""

JS = """
const lb = document.getElementById('lightbox');
const lbImg = lb.querySelector('img');
const lbCap = lb.querySelector('.caption');
document.querySelectorAll('.card').forEach(c => {
  c.addEventListener('click', () => {
    lbImg.src = c.dataset.full;
    lbCap.textContent = c.dataset.label;
    lb.classList.add('open');
  });
});
lb.addEventListener('click', () => lb.classList.remove('open'));
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') lb.classList.remove('open');
});

const search = document.getElementById('q');
search.addEventListener('input', e => {
  const q = e.target.value.toLowerCase();
  document.querySelectorAll('.card').forEach(c => {
    const hit = !q || c.dataset.label.toLowerCase().includes(q);
    c.style.display = hit ? '' : 'none';
  });
  document.querySelectorAll('section.group').forEach(s => {
    const visible = s.querySelectorAll('.card:not([style*="display: none"])').length;
    s.style.display = visible === 0 ? 'none' : '';
  });
});

const sortSel = document.getElementById('sort');
sortSel.addEventListener('change', e => {
  const mode = e.target.value;
  document.querySelectorAll('section.group .grid').forEach(grid => {
    const cards = Array.from(grid.querySelectorAll('.card'));
    cards.sort((a, b) => {
      if (mode === 'name') return a.dataset.label.localeCompare(b.dataset.label);
      if (mode === 'newest') return Number(b.dataset.mtime) - Number(a.dataset.mtime);
      if (mode === 'size') return Number(b.dataset.bytes) - Number(a.dataset.bytes);
      return 0;
    });
    cards.forEach(c => grid.appendChild(c));
  });
});
"""


def main() -> None:
    groups = collect()
    total = sum(len(v) for v in groups.values())

    parts: list[str] = []
    parts.append("<!DOCTYPE html>")
    parts.append('<html lang="ja"><head><meta charset="utf-8">')
    parts.append("<title>Phonics Songs Gallery</title>")
    parts.append(f"<style>{CSS}</style>")
    parts.append("</head><body>")
    parts.append("<header>")
    parts.append("<h1>🎵 Phonics Songs Gallery</h1>")
    parts.append(f'<span class="count">{total} images / {len(groups)} groups</span>')
    parts.append('<div class="controls">')
    parts.append('<input type="search" id="q" placeholder="ファイル名で検索…">')
    parts.append('<select id="sort">'
                 '<option value="name">名前順</option>'
                 '<option value="newest">新しい順</option>'
                 '<option value="size">サイズ順</option>'
                 '</select>')
    parts.append("</div></header>")
    parts.append("<main>")

    if not groups:
        parts.append('<div class="empty">phonics-songs/ に画像がありません。</div>')
    else:
        for group_name in sorted(groups.keys()):
            files = groups[group_name]
            parts.append(f'<section class="group" data-group="{html.escape(group_name)}">')
            parts.append(
                f'<h2>📁 {html.escape(group_name)} '
                f'<span style="color:var(--muted);font-size:0.8rem;">'
                f'({len(files)})</span></h2>'
            )
            parts.append('<div class="grid">')
            for f in files:
                rel = f.relative_to(ROOT).as_posix()
                stat = f.stat()
                bytes_ = stat.st_size
                mtime = int(stat.st_mtime)
                size_str = fmt_size(bytes_)
                label = f.stem
                parts.append(
                    f'<div class="card" '
                    f'data-full="{html.escape(rel)}" '
                    f'data-label="{html.escape(label)}" '
                    f'data-mtime="{mtime}" '
                    f'data-bytes="{bytes_}">'
                    f'<img src="{html.escape(rel)}" alt="{html.escape(label)}" loading="lazy">'
                    f'<div class="meta">'
                    f'<span class="name">{html.escape(label)}</span>'
                    f'<span class="size">{size_str}</span>'
                    f'</div></div>'
                )
            parts.append("</div></section>")

    parts.append("</main>")
    parts.append('<div id="lightbox" class="lightbox"><img alt=""><div class="caption"></div></div>')
    parts.append(f"<script>{JS}</script>")
    parts.append("</body></html>")

    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} ({total} images, {len(groups)} groups)")


if __name__ == "__main__":
    main()
