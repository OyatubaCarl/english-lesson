#!/usr/bin/env python3
"""Build the clean public asset directory used by Wrangler.

Phase 2 layout:
- index.html is the lightweight shell: head + chrome + per-book containers,
  but each <div class="book"> has its lesson <template class="lesson-tmpl">
  children stripped out. Each container gets `data-lessons-src="lessons/<id>.html"`.
- dist-public/lessons/<book-id>.html holds the lesson templates for that book.
- Runtime JS (in index.html + b_series_book_replacement.js) fetches the per-book
  fragment the first time a book is opened, injects it, then promotes individual
  lessons out of their <template> wrappers on demand.

Result: the first paint downloads ~150KB instead of ~8MB, and the browser doesn't
have to parse 60k lines of lesson markup before the page becomes interactive.
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "dist-public"
DIST = ROOT / "dist"
B_ASSETS = ROOT / "funnics-beginner-assets"


SECTION_OPEN_RE = re.compile(r"<section\b([^>]*)>", re.IGNORECASE)
SECTION_CLOSE_RE = re.compile(r"</section\s*>", re.IGNORECASE)
CLASS_ATTR_RE = re.compile(r'\bclass="([^"]*)"', re.IGNORECASE)
TEMPLATE_RE = re.compile(
    r'<template\s+class="lesson-tmpl">.*?</template>',
    re.IGNORECASE | re.DOTALL,
)
BOOK_OPEN_RE = re.compile(
    r'<div\s+class="book\b[^"]*"\s+id="book-([^"]+)"[^>]*data-book="([^"]+)"[^>]*>',
    re.IGNORECASE,
)
DIV_OPEN_RE = re.compile(r"<div\b[^>]*>", re.IGNORECASE)
DIV_CLOSE_RE = re.compile(r"</div\s*>", re.IGNORECASE)


def _is_lesson_open_tag(attrs: str) -> bool:
    m = CLASS_ATTR_RE.search(attrs)
    if not m:
        return False
    return "lesson" in m.group(1).split()


def lazify_lesson_sections(html: str) -> tuple[str, int]:
    """Wrap each `<section class="lesson ...">` in `<template class="lesson-tmpl">`."""
    parts: list[str] = []
    pos = 0
    wrapped = 0
    length = len(html)
    while pos < length:
        m_open = SECTION_OPEN_RE.search(html, pos)
        if not m_open:
            parts.append(html[pos:])
            break
        start = m_open.start()
        attrs = m_open.group(1)
        scan_pos = m_open.end()
        depth = 1
        while depth > 0:
            n_open = SECTION_OPEN_RE.search(html, scan_pos)
            n_close = SECTION_CLOSE_RE.search(html, scan_pos)
            if not n_close:
                scan_pos = length
                break
            if n_open and n_open.start() < n_close.start():
                depth += 1
                scan_pos = n_open.end()
            else:
                depth -= 1
                scan_pos = n_close.end()
        end = scan_pos
        parts.append(html[pos:start])
        section_html = html[start:end]
        if _is_lesson_open_tag(attrs):
            parts.append('<template class="lesson-tmpl">')
            parts.append(section_html)
            parts.append("</template>")
            wrapped += 1
        else:
            parts.append(section_html)
        pos = end
    return "".join(parts), wrapped


def parse_book_ranges(html: str) -> list[tuple[int, int, int, int, str]]:
    """For each `<div class="book" id="book-X" data-book="X">`, find its content range.

    Returns a list of (open_tag_start, content_start, content_end, container_end, book_id),
    where content_end is the position of the matching `</div>` and container_end is just
    after it.
    """
    results: list[tuple[int, int, int, int, str]] = []
    for m in BOOK_OPEN_RE.finditer(html):
        book_id = m.group(2)
        start = m.start()
        content_start = m.end()
        scan = content_start
        depth = 1
        content_end = scan
        container_end = scan
        length = len(html)
        while depth > 0 and scan < length:
            n_open = DIV_OPEN_RE.search(html, scan)
            n_close = DIV_CLOSE_RE.search(html, scan)
            if not n_close:
                break
            if n_open and n_open.start() < n_close.start():
                depth += 1
                scan = n_open.end()
            else:
                depth -= 1
                content_end = n_close.start()
                container_end = n_close.end()
                scan = container_end
        results.append((start, content_start, content_end, container_end, book_id))
    return results


def _inject_lessons_src(open_tag: str, book_id: str, lessons_path: str) -> str:
    """Add `data-lessons-src` to the opening `<div ...>` for the book container."""
    inject = f' data-lessons-src="{lessons_path}"'
    # Insert before the closing ">". Use rfind so attribute strings with ">" inside quoted
    # values would still work, though that shouldn't happen for a static template.
    idx = open_tag.rfind(">")
    if idx < 0:
        return open_tag
    return open_tag[:idx] + inject + open_tag[idx:]


def split_books_into_fragments(html: str, lessons_dir: Path) -> dict[str, dict]:
    """For each book container, extract its lesson templates into a side file and
    replace them with nothing in the skeleton. Also tag the container with
    `data-lessons-src`.

    Returns: {book_id: {'count': N, 'src': 'lessons/<id>.html', 'bytes': B}}.
    The input `html` is mutated as a string; the rewritten skeleton is returned by
    the caller via the explicit return value below.
    """
    raise RuntimeError("use split_books_returning_skeleton")  # safety: not used directly


def split_books_returning_skeleton(
    html: str, lessons_dir: Path
) -> tuple[str, dict[str, dict]]:
    """Strip <template class="lesson-tmpl"> children from each book container, write
    them to lessons_dir/<book_id>.html, and tag the container with `data-lessons-src`.
    """
    lessons_dir.mkdir(parents=True, exist_ok=True)
    ranges = parse_book_ranges(html)
    # Process in reverse so earlier offsets stay valid as we splice.
    ranges_sorted = sorted(ranges, key=lambda r: r[0], reverse=True)
    stats: dict[str, dict] = {}

    new_html = html
    for start, content_start, content_end, container_end, book_id in ranges_sorted:
        open_tag = new_html[start:content_start]
        content = new_html[content_start:content_end]

        templates = TEMPLATE_RE.findall(content)
        if not templates:
            # Container has no lesson templates (e.g., phonics container that we
            # don't lesson-split). Skip both the file write and the attribute.
            continue

        lessons_path = f"lessons/{book_id}.html"
        fragment = "".join(templates)
        out_file = lessons_dir / f"{book_id}.html"
        out_file.write_text(fragment, encoding="utf-8")

        # Replace the FIRST template span with a mount anchor so the lessons
        # fetched at runtime land where the original <section>s used to live
        # (between the lesson selector and the common tools). Drop the rest.
        first_match = TEMPLATE_RE.search(content)
        anchor = '<template data-lessons-mount></template>'
        if first_match:
            head = content[: first_match.start()]
            tail_clean = TEMPLATE_RE.sub("", content[first_match.start():])
            new_content = head + anchor + tail_clean
        else:
            new_content = content
        new_open_tag = _inject_lessons_src(open_tag, book_id, lessons_path)
        # content_end is exactly at `</div>`, so splicing `[content_end:]` keeps it.
        new_html = (
            new_html[:start] + new_open_tag + new_content + new_html[content_end:]
        )

        stats[book_id] = {
            "count": len(templates),
            "src": lessons_path,
            "bytes": len(fragment.encode("utf-8")),
        }

    return new_html, stats


def write_lazified_index(source: Path, target: Path, lessons_dir: Path) -> dict:
    raw = source.read_text(encoding="utf-8")
    wrapped, wrap_count = lazify_lesson_sections(raw)
    skeleton, stats = split_books_returning_skeleton(wrapped, lessons_dir)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(skeleton, encoding="utf-8")
    return {
        "wrapped_lessons": wrap_count,
        "skeleton_bytes": target.stat().st_size,
        "source_bytes": source.stat().st_size,
        "per_book": stats,
    }


def copy_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def copy_optional_tree(source: Path, target: Path, **kwargs: object) -> bool:
    """Copy a locally generated asset tree when it is available.

    Large lesson artwork is intentionally kept outside Git. Cloudflare builds run
    from a source-only checkout, so those optional trees may not exist there.
    """
    if not source.is_dir():
        print(f"Skipping optional local assets: {source.relative_to(ROOT)}")
        return False
    shutil.copytree(source, target, **kwargs)
    return True


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    info = write_lazified_index(ROOT / "index.html", OUT / "index.html", OUT / "lessons")
    print(
        f"Lazified index.html: wrapped {info['wrapped_lessons']} lessons; "
        f"shell {info['skeleton_bytes']:,} B "
        f"(was {info['source_bytes']:,} B; "
        f"shrinkage {(1 - info['skeleton_bytes'] / max(info['source_bytes'], 1)) * 100:.1f}%)"
    )
    for book_id, meta in sorted(info["per_book"].items()):
        print(
            f"  lessons/{book_id}.html: {meta['count']} lessons, "
            f"{meta['bytes']:,} B"
        )

    for name in (
        "phonics-dictionary.html",
        "phonics-characters.html",
        "youtube-map.json",
        "funnics-island-links.html",
    ):
        copy_file(ROOT / name, OUT / name)

    shutil.copytree(
        ROOT / "audio",
        OUT / "audio",
        ignore=shutil.ignore_patterns(".DS_Store", "__pycache__"),
    )

    for phonics_dir in (
        "phonics-chars",
        "phonics-ai-ay",
        "phonics-long-a",
        "phonics-short-a",
        "phonics-short-o",
        "cowboy-counting",
    ):
        copy_optional_tree(
            DIST / phonics_dir,
            OUT / phonics_dir,
            ignore=shutil.ignore_patterns(".DS_Store", "__pycache__", "sheets"),
        )

    shutil.copytree(
        ROOT / "assets" / "card-generated",
        OUT / "assets" / "card-generated",
        ignore=shutil.ignore_patterns(".DS_Store", "__pycache__"),
    )

    b_target = OUT / "funnics-beginner-assets"
    b_target.mkdir(parents=True, exist_ok=True)
    for name in (
        "b_series_book_replacement.css",
        "b_series_book_replacement.js",
        "b_series_picturebook_thumbnails.json",
    ):
        copy_file(B_ASSETS / name, b_target / name)
    shutil.copytree(
        B_ASSETS / "picturebook-thumbs",
        b_target / "picturebook-thumbs",
        ignore=shutil.ignore_patterns(".DS_Store", "__pycache__"),
    )

    print(f"Built clean public assets in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
