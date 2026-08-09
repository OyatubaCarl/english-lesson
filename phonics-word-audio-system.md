# Phonics Word Audio System

## Source of truth

`phonics-audio-items.json` is the single source of truth for:

- word cards shown in `phonics-first-page-mockup.html`
- word-level preview audio
- segment labels and IPA display
- future image and attribution metadata

Each word entry should include:

```json
{
  "id": "pat",
  "word": "pat",
  "ipa": "pæt",
  "meaning": "軽くたたく",
  "rule": "short-a",
  "ruleLabel": "short a",
  "segments": [
    { "grapheme": "p", "ipa": "/p/", "sound": "p" },
    { "grapheme": "a", "ipa": "/æ/", "sound": "æ" },
    { "grapheme": "t", "ipa": "/t/", "sound": "t" }
  ],
  "image": "assets/card-icons/pat.png"
}
```

## Preview audio

Word-card preview audio now uses the browser Web Speech API first. This keeps the word-card system independent from the unfinished phoneme-recording workflow.

Local generated word audio remains optional fallback data. If needed, it can still be generated locally with `espeak-ng`:

```bash
python3 generate-phonics-espeak-audio.py --force
```

Output:

```text
audio/phonics-card-demo/words/{word_id}.mp3
audio/phonics-card-demo/phonemes/{phoneme_id}.mp3
audio/phonics-card-demo/manifest.json
```

## One-command build

After editing `phonics-audio-items.json`, sync the mockup HTML:

```bash
python3 sync-phonics-mockup-data.py
```

To append the current beginner short-vowel card set, run:

```bash
python3 expand-phonics-word-cards.py
python3 sync-phonics-mockup-data.py
```

## Playback policy

- `単語音`: use browser Web Speech first.
- `単語音`: fall back to word recording files, then synthetic preview only if Web Speech is unavailable.
- `分解音`: do not use unreviewed downloaded phoneme recordings.
- `分解音`: currently uses the mockup's short synthetic phoneme sounds unless a phoneme is added to `approvedSegmentAudioIds` in the HTML.

This avoids bad phoneme assets such as `/p/` being heard as `pa`, `puh`, or multiple syllables.

## Production replacement

When better word recordings are available, put them in:

```text
audio/phonics-free/words/{word_id}.ogg
```

Then add the approved id to `freeWordAudioIds` in the HTML or migrate the HTML to read `manifest.json`.

When better phoneme recordings are approved, put them in:

```text
audio/phonics-free/phonemes/{phoneme_id}.ogg
```

Then add the phoneme id to `approvedSegmentAudioIds`.
