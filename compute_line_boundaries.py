"""For each verse, find the 5 lyric line boundaries via Whisper transcript.

Output: /tmp/phonics_lines.json with per-letter line timings.
"""
import json, re
from pathlib import Path

with open('/tmp/phonics_transcript_v3.json') as f:
    data = json.load(f)
words = data['words']
with open('/tmp/phonics_segments_v5.json') as f:
    seg = json.load(f)


# Char definitions: letter, name, action_verbs (one per action line)
CHARS = [
    ('A','aunt ant',('asks','adds','applauds')),
    ('B','baker bear',('bakes','blows','builds')),
    ('C','cowboy cat',('catches','climbs','counts')),
    ('D','doctor dragon',('draws','digs','dives')),
    ('E','engineer egg',('edits','enters','exercises')),
    ('F','fisher frog',('finds','flips','flies')),
    ('G','guardian goat',('grows','gives','grabs')),
    ('H','hiker hippo',('holds','hugs','hides')),
    ('I','inventor ice',('invents','imagines','imitates')),
    ('J','juggler jellyfish',('juggles','jumps','joins')),
    ('K','king kangaroo',('kicks','keeps','kisses')),
    ('L','librarian lion',('lifts','learns','likes')),
    ('M','magician mouse',('makes','mixes','moves')),
    ('N','ninja nut',('nibbles','names','needs')),
    ('O','outlaw octopus',('opens','offers','orders')),
    ('P','pilot panda',('paints','pulls','packs')),
    ('Q','queen quiz',('quizzes','questions','quacks')),
    ('R','runner rabbit',('reads','rolls','rides')),
    ('S','singer snake',('sings','sees','sips')),
    ('T','teacher tacos',('teaches','taps','throws')),
    ('U','uncle unicorn',('unzips','unties','unfolds')),
    ('V','viking virus',('visits','vacuums','vanishes')),
    ('W','waiter wolf',('washes','waves','walks')),
    ('X','boxer fox',('fixes','mixes','waxes')),
    ('Y','yoga yeti',('yells','yanks','yawns')),
    ('Z','zigzag zebra',('zips','swims','zonks')),
]

# Each verse range comes from segments_v2 boundaries (letter triple → next letter triple)
# Verse starts: index 1..26 in seg['boundaries']; verse end = boundaries[i+1]
verse_starts = seg['verse_starts']  # 26 entries
boundaries = seg['boundaries']      # 28 entries
outro_start = seg['outro_start']

def norm(w): return w.lower().strip(",.!?-_'")

def find_word_in_range(words, target, start_idx, end_idx, prefer_capital=False):
    """Return (idx, time) of first match of target word in [start_idx, end_idx)."""
    target_l = target.lower()
    for i in range(start_idx, end_idx):
        if norm(words[i]['word']) == target_l:
            return i, words[i]['start']
    return None, None

def index_of_time(words, t):
    """Index of first word with start >= t."""
    for i, w in enumerate(words):
        if w['start'] >= t - 0.05:
            return i
    return len(words)

result = {}
for v in verse_starts:
    letter = v['letter']
    name = v['name']
    verse_start = v['start']
    # next verse start (or outro)
    next_v = next((x for x in verse_starts if x['start'] > verse_start), None)
    verse_end = next_v['start'] if next_v else outro_start

    s_idx = index_of_time(words, verse_start)
    e_idx = index_of_time(words, verse_end)

    # Look up action verbs for this letter
    char_def = next((c for c in CHARS if c[0]==letter), None)
    if not char_def: continue
    _, _, verbs = char_def

    # Find "What" position (line 2 start)
    _, t_what = find_word_in_range(words, 'what', s_idx, e_idx)
    # Find each verb position (line 3, 4, 5 start)
    _, t_v0 = find_word_in_range(words, verbs[0], s_idx, e_idx)
    _, t_v1 = find_word_in_range(words, verbs[1], s_idx, e_idx)
    _, t_v2 = find_word_in_range(words, verbs[2], s_idx, e_idx)

    line_times = [verse_start, t_what, t_v0, t_v1, t_v2, verse_end]
    # Sanity: any None?
    missing = [i for i,t in enumerate(line_times) if t is None]
    if missing:
        # fallback: even split for missing entries
        valid = [t for t in line_times if t is not None]
        # interpolate
        new = []
        for i,t in enumerate(line_times):
            if t is None:
                # avg of neighbors
                left = next((line_times[j] for j in range(i-1,-1,-1) if line_times[j] is not None), verse_start)
                right = next((line_times[j] for j in range(i+1,len(line_times)) if line_times[j] is not None), verse_end)
                # estimate proportion
                missing_count = 1
                t = (left + right) / 2
            new.append(t)
        line_times = new

    result[letter] = {
        'name': name,
        'verse_start': verse_start,
        'verse_end': verse_end,
        'line_times': line_times,  # 6 boundaries → 5 lines
        'durations': [line_times[i+1]-line_times[i] for i in range(5)],
    }
    print(f"{letter} {name}: {[f'{t:.2f}' for t in line_times]} (durs: {[f'{d:.2f}' for d in result[letter]['durations']]})")

with open('/tmp/phonics_lines.json','w') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
print(f'\nSaved /tmp/phonics_lines.json — {len(result)} verses')
