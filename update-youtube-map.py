#!/usr/bin/env python3
"""Regenerate youtube-map.json from the YouTube channel @songandmixture.

Usage:  python3 update-youtube-map.py

Requires yt-dlp (brew install yt-dlp).

Maps YouTube video titles to book + lesson number based on these patterns:
  "Lesson 1 — 中1文法すべて..."            → middle, lesson "1"
  "Lesson H1 — 第1文型 [SV]..."           → high1, lesson "1"
  "Lesson H46 — ..."                       → high2, lesson "1" (H46 = high2 #1)
  "Lesson H108 — ..."                      → high3, lesson "1" (H108 = high3 #1)
  "Lesson B1 — ..."                        → beginner, lesson "1"

Adjust book ranges below if channel naming diverges.
"""
import json, subprocess, re, sys

CHANNEL = 'https://www.youtube.com/@songandmixture/videos'
OUT = 'youtube-map.json'

def fetch_videos():
    r = subprocess.run(
        ['yt-dlp', '--flat-playlist', '--print', '%(id)s\t%(title)s', CHANNEL],
        capture_output=True, text=True, check=True
    )
    videos = []
    for line in r.stdout.splitlines():
        if '\t' in line:
            vid, title = line.split('\t', 1)
            videos.append((vid.strip(), title.strip()))
    return videos

def classify(title):
    """Return (book, lesson_number_str) or (None, None) if no match."""
    # "Lesson H{n} ..." → high book
    m = re.match(r'Lesson\s*H(\d+)', title)
    if m:
        n = int(m.group(1))
        if n <= 45:
            return ('high1', str(n))
        elif n <= 107:
            return ('high2', str(n - 45))
        else:
            return ('high3', str(n - 107))
    # "Lesson B{n} ..." → beginner book
    m = re.match(r'Lesson\s*B(\d+)', title)
    if m:
        return ('beginner', m.group(1))
    # "Lesson {n} ..." → middle book
    m = re.match(r'Lesson\s*(\d+)', title)
    if m:
        return ('middle', m.group(1))
    return (None, None)

def main():
    print(f'Fetching videos from {CHANNEL}...')
    try:
        videos = fetch_videos()
    except subprocess.CalledProcessError as e:
        print(f'yt-dlp failed: {e.stderr}', file=sys.stderr)
        sys.exit(1)
    print(f'Found {len(videos)} videos')

    mp = {'beginner': {}, 'middle': {}, 'high1': {}, 'high2': {}, 'high3': {}}
    unmatched = []
    for vid, title in videos:
        book, lesson = classify(title)
        if book:
            # If multiple videos match same slot, keep the NEWEST (first in yt-dlp output, which is most recent)
            if lesson not in mp[book]:
                mp[book][lesson] = vid
                print(f'  {book} L{lesson}: {vid}  ({title[:60]})')
            else:
                print(f'  SKIP dup: {title[:60]}  (already have {book}/{lesson})')
        else:
            unmatched.append((vid, title))

    if unmatched:
        print(f'\n{len(unmatched)} unmatched titles:')
        for vid, t in unmatched:
            print(f'  {vid}: {t[:80]}')

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(mp, f, ensure_ascii=False, indent=2)
    total = sum(len(v) for v in mp.values())
    print(f'\nWrote {OUT}: {total} lessons mapped across {len(mp)} books.')

if __name__ == '__main__':
    main()
