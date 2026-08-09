import json
import glob
import os
import yaml
import shutil

os.chdir('/Users/masaki/Documents/ClaudeCode/英語学習教材作成')
V = '/Users/masaki/workspace-local/Obsidian/MainVault/_AI-Workspace/_x-posts'
y6 = os.path.join(V, '2026-06.yaml')
y7 = os.path.join(V, '2026-07.yaml')
shutil.copy2(y6, y6 + '.bak-20260623')
posts = yaml.safe_load(open(y6))


def latest(p):
    return sorted(glob.glob(p))[-1]


night = json.load(open('shorts/_analytics/redo_upload_log_20260622_000102.json'))
morn = json.load(open(latest('shorts/_analytics/redo_upload_log_redo_design_morning_*.json')))
ups = {r['quiz_id']: r for r in night['results'] + morn['results'] if r['status'] == 'ok'}
qid2vid = {k: v['new_video_id'] for k, v in ups.items()}
# upload log の publish_jst はリスケ前のスケジュール。design.json が正(リスケ済み)。
night_design_pre = json.load(open('shorts/_analytics/redo_design.json'))
morn_design_pre = json.load(open('shorts/_analytics/redo_design_morning.json'))
qid2pub = {x['id']: x['publish_jst'] for x in night_design_pre + morn_design_pre}
new_words = {v['word'] for v in ups.values()}

dead = 0
for p in posts:
    sid = str(p.get('id') or '')
    if not sid.startswith('quiz_') or p.get('status') != 'pending':
        continue
    parts = sid.split('_')
    if len(parts) < 3:
        continue
    if parts[2] in new_words:
        p['status'] = 'failed'
        p['error'] = 'Linked video deleted/replaced on 2026-06-22 redo.'
        dead += 1

night_design = night_design_pre
morn_design = morn_design_pre


def tweet_text(d, vid):
    word = d['word']
    T = d['title_pattern']
    hooks = {
        'T13': '「' + word + '」\n見た瞬間に意味言える?',
        'T01': '「' + word + '」\nこれ、読める?',
        'T04': '「' + word + '」\n意味、わかる?',
    }
    return hooks[T] + '\n\n意味とコツは動画で30秒\n→ https://www.youtube.com/shorts/' + vid + '\n\n#英単語 #英語学習'


new_entries = []
for d in night_design + morn_design:
    vid = qid2vid.get(d['id'])
    if not vid:
        continue
    new_entries.append({
        'id': 'redo_' + d['id'] + '_' + vid,
        'scheduled': qid2pub.get(d['id'], d['publish_jst']),
        'text': tweet_text(d, vid),
        'reply_text': None,
        'media': [],
        'status': 'pending',
        'posted_at': None,
        'tweet_id': None,
        'error': None,
        'media_youtube_url': 'https://www.youtube.com/shorts/' + vid,
        'source': 'lou_quiz_shorts_v4_redo_20260622',
    })

n6 = [e for e in new_entries if e['scheduled'][:7] == '2026-06']
n7 = [e for e in new_entries if e['scheduled'][:7] == '2026-07']

posts.extend(n6)
posts.sort(key=lambda p: str(p.get('scheduled') or ''))
yaml.safe_dump(posts, open(y6, 'w'), allow_unicode=True, default_flow_style=False, sort_keys=False, width=1000)

if os.path.exists(y7):
    j = yaml.safe_load(open(y7)) or []
    shutil.copy2(y7, y7 + '.bak-20260623')
else:
    j = []
j.extend(n7)
j.sort(key=lambda p: str(p.get('scheduled') or ''))
yaml.safe_dump(j, open(y7, 'w'), allow_unicode=True, default_flow_style=False, sort_keys=False, width=1000)

print('dead=%d new06=%d new07=%d 06total=%d 07total=%d' % (dead, len(n6), len(n7), len(posts), len(j)))
