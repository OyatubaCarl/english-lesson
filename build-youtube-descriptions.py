#!/usr/bin/env python3
"""Generate per-lesson YouTube descriptions into descriptions/{book}_L{N}.txt

Inputs:
 - index.html         (auto-extract h2, grammar name, theme, grammar explanation)
 - lesson-descriptions.json  (optional per-lesson overrides)
 - youtube-map.json   (for prev/next video links)

Output:
 - descriptions/{book}_L{N}.txt  (one plain-text file per lesson)

Usage:  python3 build-youtube-descriptions.py
"""
import json, os, re, sys

BASE = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(BASE, 'index.html')
OVERRIDES = os.path.join(BASE, 'lesson-descriptions.json')
YT_MAP = os.path.join(BASE, 'youtube-map.json')
OUT_DIR = os.path.join(BASE, 'descriptions')

SITE_URL = 'https://english-lesson.gasflare.workers.dev/'
CHANNEL_URL = 'https://www.youtube.com/@songandmixture'

# Book labels for readability
BOOK_LABEL = {
    'beginner': '入門編',
    'middle':   '中学生編',
    'high1':    '高校編 1（文法基礎）',
    'high2':    '高校編 2（文法応用）',
    'high3':    '高校編 3（読解・総合）',
}
# Default target level per book (overridable per lesson in lesson-descriptions.json)
DEFAULT_LEVEL = {
    'beginner': '中1レベル（英語に初めて触れる方）',
    'middle':   '中学生レベル',
    'high1':    '高校1年 基礎〜標準',
    'high2':    '高校1〜2年 応用',
    'high3':    '高校2〜3年 読解・総合',
}

def load_lessons():
    """Return {book: {lesson_num_str: {'h2', 'grammar_name', 'theme', 'grammar_explanation'}}}."""
    with open(INDEX, encoding='utf-8') as f:
        t = f.read()
    result = {}
    for book in BOOK_LABEL:
        m = re.search(rf'id="book-{book}"(.+?)(?=<div class="book|</body>)', t, re.DOTALL)
        if not m:
            result[book] = {}
            continue
        book_html = m.group(1)
        result[book] = {}
        for sec in re.finditer(r'<section[^>]*class="[^"]*lesson[^"]*"[^>]*data-lesson="(\d+)"[^>]*>(.*?)(?=<section\b|</div>\s*<div class="book|$)', book_html, re.DOTALL):
            num = sec.group(1)
            content = sec.group(2)
            h2 = re.search(r'<h2[^>]*>(.*?)</h2>', content, re.DOTALL)
            gd = re.search(r'class="g-desc"[^>]*>(.*?)</p>', content, re.DOTALL)
            gt = re.search(r'class="g-title"[^>]*>(.*?)</', content, re.DOTALL)
            h2_text = re.sub(r'<[^>]+>', '', h2.group(1)).strip() if h2 else ''
            gd_text = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', gd.group(1))).strip() if gd else ''
            gt_text = re.sub(r'<[^>]+>', '', gt.group(1)).strip() if gt else ''
            # Parse grammar_name and theme from h2
            gm = re.match(r'Lesson\s*[HB]?\d+\s*[—\-–]\s*(?:＋\s*)?(.+?)「(.+?)」', h2_text)
            grammar_name = gm.group(1).strip() if gm else gt_text.replace('文法ターゲット：', '').strip()
            theme = gm.group(2).strip() if gm else ''
            result[book][num] = {
                'h2': h2_text,
                'grammar_name': grammar_name,
                'theme': theme,
                'grammar_explanation': gd_text,
            }
    return result

def load_json(path, default):
    if not os.path.exists(path): return default
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def build_description(book, num, lesson, yt_map, overrides):
    """Assemble the description text for one lesson."""
    # Per-lesson overrides
    ov = ((overrides.get(book) or {}).get(str(num))) or {}
    target_level = ov.get('target_level') or DEFAULT_LEVEL.get(book, '')
    grammar_expl = ov.get('grammar_explanation') or lesson['grammar_explanation'] or f'{lesson["grammar_name"]} を学びます。'
    extra_note = ov.get('extra_note') or ''

    # Prev/next links
    book_map = yt_map.get(book, {}) or {}
    prev_vid = book_map.get(str(int(num) - 1))
    next_vid = book_map.get(str(int(num) + 1))
    prev_next_lines = []
    if prev_vid or next_vid:
        prev_next_lines.append('\n▼ 関連動画')
        if prev_vid:
            prev_next_lines.append(f'前のレッスン: https://youtu.be/{prev_vid}')
        if next_vid:
            prev_next_lines.append(f'次のレッスン: https://youtu.be/{next_vid}')
    prev_next_block = '\n'.join(prev_next_lines)

    # Deep-link URL (requires ?book= / ?lesson= support on site; fallback is base URL)
    deep_link = f'{SITE_URL}?book={book}&lesson={num}'

    parts = [
        lesson['h2'],
        f'対象: {target_level}',
        '',
        '▼ 学習サイト（本文・解説・単語テスト）',
        SITE_URL,
        f'このレッスンのページ: {deep_link}',
        '',
        '▼ 生成AIについて（注意）',
        'このコンテンツは以下のAIを使って作成しています：',
        '　英文・訳・解説 … Claude（Anthropic）',
        '　楽曲 … Suno AI',
        '　映像 … revid.ai',
        'AIの特性上、人物の見た目が場面によって変わる、細部が不自然などの点があります。',
        '英文もまれに不自然な表現が残ることがあります。',
        '英語学習の補助としてお使いください。',
        '',
        '▼ おすすめの使い方',
        '1. サイトで本文を読む（日本語訳・発音記号つき）',
        '2. この動画で耳と目から定着',
        '3. サイトで単語テストに挑戦',
        '',
        '▼ このレッスンで学ぶこと',
        grammar_expl,
    ]
    if extra_note:
        parts += ['', extra_note]
    if prev_next_block:
        parts += ['', prev_next_block.lstrip()]
    parts += [
        '',
        f'チャンネル登録で新着レッスンのお知らせ → {CHANNEL_URL}',
        '',
        '#英語学習 #中学英語 #高校英語 #英文法 #英語リスニング #Suno #revidai',
    ]
    return '\n'.join(parts).strip() + '\n'

def main():
    lessons = load_lessons()
    overrides = load_json(OVERRIDES, {})
    yt_map = load_json(YT_MAP, {})

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for book, bk_lessons in lessons.items():
        for num, lesson in sorted(bk_lessons.items(), key=lambda kv: int(kv[0])):
            desc = build_description(book, num, lesson, yt_map, overrides)
            fn = os.path.join(OUT_DIR, f'{book}_L{num}.txt')
            with open(fn, 'w', encoding='utf-8') as f:
                f.write(desc)
            total += 1
    print(f'Wrote {total} description files to {OUT_DIR}/')
    print(f'Sample: {os.path.join(OUT_DIR, "middle_L1.txt")}')

if __name__ == '__main__':
    main()
