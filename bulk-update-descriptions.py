#!/usr/bin/env python3
"""Bulk-update YouTube video descriptions via YouTube Data API v3.

Flow:
 1. Authenticate via OAuth2 (credentials.json) → token.json (cached).
 2. Fetch all uploads on @songandmixture channel.
 3. For each video, infer (book, lesson) from title.
 4. Read descriptions/{book}_L{N}.txt → PATCH video description (+ optionally title).

Options:
 --dry-run       : Show what would change, do not call the API update endpoint.
 --only-missing  : Only update videos whose current description is empty.
 --title         : Also overwrite video title with the lesson's h2 text.
 --book BOOK     : Limit to one book (beginner|middle|high1|high2|high3).

First-time setup:
  1. Place credentials.json in this directory (OAuth client ID for Desktop app).
  2. pip3 install google-api-python-client google-auth-httplib2 google-auth-oauthlib
  3. python3 bulk-update-descriptions.py --dry-run   # opens browser for consent
"""
import argparse, json, os, re, sys

BASE = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS = os.path.join(BASE, 'credentials.json')
TOKEN = os.path.join(BASE, 'token.json')
DESC_DIR = os.path.join(BASE, 'descriptions')
INDEX = os.path.join(BASE, 'index.html')

SCOPES = ['https://www.googleapis.com/auth/youtube']  # full manage (needed for update)

def classify(title):
    """Return (book, lesson_num_str) or (None, None)."""
    m = re.match(r'Lesson\s*H(\d+)', title)
    if m:
        n = int(m.group(1))
        if n <= 45: return ('high1', str(n))
        if n <= 107: return ('high2', str(n - 45))
        return ('high3', str(n - 107))
    m = re.match(r'Lesson\s*B(\d+)', title)
    if m:
        return ('beginner', m.group(1))
    m = re.match(r'Lesson\s*(\d+)', title)
    if m:
        return ('middle', m.group(1))
    return (None, None)

def get_h2_map():
    """{book: {num: h2_text}} — to reuse as title if --title is passed."""
    with open(INDEX, encoding='utf-8') as f:
        t = f.read()
    result = {}
    for book in ['beginner', 'middle', 'high1', 'high2', 'high3']:
        m = re.search(rf'id="book-{book}"(.+?)(?=<div class="book|</body>)', t, re.DOTALL)
        if not m:
            result[book] = {}
            continue
        result[book] = {}
        for sec in re.finditer(r'<section[^>]*data-lesson="(\d+)"[^>]*>(.*?)(?=<section\b|</div>\s*<div class="book|$)', m.group(1), re.DOTALL):
            h2 = re.search(r'<h2[^>]*>(.*?)</h2>', sec.group(2), re.DOTALL)
            if h2:
                result[book][sec.group(1)] = re.sub(r'<[^>]+>', '', h2.group(1)).strip()
    return result

def authenticate():
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        print('ERROR: required packages not installed. Run:', file=sys.stderr)
        print('  pip3 install google-api-python-client google-auth-httplib2 google-auth-oauthlib', file=sys.stderr)
        sys.exit(1)
    creds = None
    if os.path.exists(TOKEN):
        creds = Credentials.from_authorized_user_file(TOKEN, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS):
                print(f'ERROR: {CREDENTIALS} not found. See file header for setup steps.', file=sys.stderr)
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN, 'w') as f:
            f.write(creds.to_json())
    return build('youtube', 'v3', credentials=creds)

def fetch_all_uploads(youtube):
    """Return list of {id, title, description} for all uploads of the authenticated channel."""
    # Get uploads playlist ID
    ch = youtube.channels().list(part='contentDetails', mine=True).execute()
    if not ch.get('items'):
        raise RuntimeError('No channel found for authenticated user')
    uploads = ch['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    videos = []
    page_token = None
    while True:
        r = youtube.playlistItems().list(
            part='snippet,contentDetails',
            playlistId=uploads,
            maxResults=50,
            pageToken=page_token,
        ).execute()
        for it in r.get('items', []):
            sn = it['snippet']
            videos.append({
                'id': it['contentDetails']['videoId'],
                'title': sn['title'],
                # playlistItems snippet has truncated description; fetch real one below
            })
        page_token = r.get('nextPageToken')
        if not page_token: break

    # Fetch full description + categoryId in batches of 50
    for i in range(0, len(videos), 50):
        batch = videos[i:i+50]
        ids = ','.join(v['id'] for v in batch)
        r = youtube.videos().list(part='snippet', id=ids).execute()
        info = {it['id']: it['snippet'] for it in r.get('items', [])}
        for v in batch:
            s = info.get(v['id'], {})
            v['description'] = s.get('description', '')
            v['categoryId'] = s.get('categoryId', '27')  # 27 = Education
            v['tags'] = s.get('tags', [])
            v['defaultLanguage'] = s.get('defaultLanguage', 'ja')
            v['title'] = s.get('title', v['title'])
    return videos

def update_video(youtube, video, new_description, new_title=None):
    body = {
        'id': video['id'],
        'snippet': {
            'title': new_title or video['title'],
            'description': new_description,
            'categoryId': video['categoryId'],
            'tags': video.get('tags') or ['英語学習', '中学英語', '高校英語', '英文法'],
            'defaultLanguage': video.get('defaultLanguage') or 'ja',
        }
    }
    youtube.videos().update(part='snippet', body=body).execute()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--only-missing', action='store_true', help='Only update if current description is empty')
    ap.add_argument('--title', action='store_true', help='Also overwrite the video title with index.html h2 text')
    ap.add_argument('--book', choices=['beginner','middle','high1','high2','high3'])
    args = ap.parse_args()

    youtube = authenticate()
    print('Fetching all uploads ...', flush=True)
    videos = fetch_all_uploads(youtube)
    print(f'Found {len(videos)} videos')

    h2_map = get_h2_map() if args.title else {}

    updated = skipped = missing = 0
    for v in videos:
        book, num = classify(v['title'])
        if not book:
            print(f'  SKIP (unclassifiable): {v["title"][:60]}')
            skipped += 1
            continue
        if args.book and book != args.book:
            continue

        desc_path = os.path.join(DESC_DIR, f'{book}_L{num}.txt')
        if not os.path.exists(desc_path):
            print(f'  MISS desc file: {v["title"][:60]}  ({desc_path})')
            missing += 1
            continue

        new_desc = open(desc_path, encoding='utf-8').read().strip()
        new_title = h2_map.get(book, {}).get(num) if args.title else None

        if args.only_missing and v['description'].strip():
            continue

        print(f'  {book} L{num}: {v["id"]}  "{v["title"][:40]}..."  ({len(v["description"])} → {len(new_desc)} chars)')
        if not args.dry_run:
            try:
                update_video(youtube, v, new_desc, new_title)
                updated += 1
            except Exception as e:
                print(f'    ✗ failed: {e}')

    print(f'\nDone. Updated: {updated}, Skipped: {skipped}, Missing desc: {missing}')
    if args.dry_run:
        print('(dry-run: no API updates made)')

if __name__ == '__main__':
    main()
