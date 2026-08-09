#!/usr/bin/env python3
"""Download free phonics audio from Wikimedia Commons.

This script pulls two different kinds of audio:

* IPA/phonetics samples from Wikimedia Commons "General phonetics"
* ordinary English word pronunciations from Commons/Wiktionary audio files

It writes a manifest with attribution and license metadata for later display.
"""
import argparse
import html
import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import unquote, urlparse

import requests


COMMONS_API = "https://commons.wikimedia.org/w/api.php"
DEFAULT_DATA = "phonics-audio-items.json"
DEFAULT_OUT = "audio/phonics-free"
USER_AGENT = "CodexPhonicsAudioPrototype/0.1 (local educational prototype)"


# English /r/ in this beginner phonics page is better represented by [ɹ] than
# the IPA trill [r].
PHONEME_COMMONS_TITLES = {
    "p": "File:Voiceless bilabial plosive.ogg",
    "b": "File:Voiced bilabial plosive.ogg",
    "t": "File:Voiceless alveolar plosive.ogg",
    "d": "File:Voiced alveolar plosive.ogg",
    "k": "File:Voiceless velar plosive.ogg",
    "g": "File:Voiced velar plosive.ogg",
    "m": "File:Bilabial nasal.ogg",
    "n": "File:Alveolar nasal.ogg",
    "ng": "File:Velar nasal.ogg",
    "f": "File:Voiceless labiodental fricative.ogg",
    "v": "File:Voiced labiodental fricative.ogg",
    "s": "File:Voiceless alveolar fricative.ogg",
    "z": "File:Voiced alveolar fricative.ogg",
    "h": "File:Voiceless glottal fricative.ogg",
    "l": "File:Alveolar lateral approximant.ogg",
    "r": "File:Alveolar approximant.ogg",
    "w": "File:Voiced labio-velar approximant.ogg",
    "y": "File:Palatal approximant.ogg",
    "sh": "File:Voiceless postalveolar fricative.ogg",
    "ch": "File:Voiceless palato-alveolar affricate.ogg",
    "th_voiceless": "File:Voiceless dental fricative.ogg",
    "th_voiced": "File:Voiced dental fricative.ogg",
    "ae": "File:Near-open front unrounded vowel.ogg",
    "eh": "File:Open-mid front unrounded vowel.ogg",
    "ih": "File:Near-close near-front unrounded vowel.ogg",
    "ah": "File:Open back unrounded vowel.ogg",
    "uh": "File:Open-mid back unrounded vowel.ogg",
}


WORD_COMMONS_TITLE_CANDIDATES = {
    "pat": ["File:En-us-pat.ogg", "File:En-au-pat.ogg"],
    "map": ["File:En-us-map.ogg"],
    "sat": ["File:En-us-sat.ogg"],
    "fan": ["File:En-us-fan.ogg", "File:En-uk-fan.ogg", "File:En-au-fan.ogg"],
    "pen": ["File:En-us-pen.ogg"],
    "red": ["File:En-us-red.ogg", "File:En-red.ogg", "File:En-uk-red.ogg"],
    "bed": ["File:En-us-bed.ogg", "File:En-uk-bed.ogg"],
    "hen": ["File:En-us-hen.ogg"],
    "sit": ["File:En-us-sit.ogg", "File:En-au-sit.ogg"],
    "pin": ["File:En-us-pin.ogg"],
    "lip": ["File:En-us-lip.ogg"],
    "win": ["File:En-us-win.ogg"],
    "hot": ["File:En-us-hot.ogg", "File:En-uk-hot.ogg"],
    "mop": ["File:En-us-mop.ogg"],
    "pot": ["File:En-us-pot.ogg", "File:En-au-pot.ogg"],
    "dog": ["File:En-us-dog.ogg", "File:En-uk-dog.ogg"],
    "cup": ["File:En-us-cup.ogg"],
    "sun": ["File:En-us-sun.ogg", "File:En-uk-sun.ogg", "File:En-Sun.ogg"],
    "run": ["File:En-us-run.ogg", "File:En-run.ogg", "File:En-au-run.ogg"],
    "bus": ["File:En-us-bus.ogg"],
    "van": ["File:En-us-van.ogg"],
    "zip": ["File:En-us-zip.ogg"],
    "yes": ["File:En-us-yes.ogg"],
    "ship": ["File:En-us-ship.ogg"],
    "chip": ["File:En-us-chip.ogg"],
    "thin": ["File:En-us-thin.ogg"],
    "this": ["File:En-us-this.ogg"],
    "ring": ["File:En-us-ring.ogg"],
    "quick": ["File:En-us-quick.ogg"],
    "fox": ["File:En-us-fox.ogg"],
}


def clean_html(value: Optional[str]) -> str:
    if not value:
        return ""
    text = re.sub(r"<[^>]+>", "", value)
    return html.unescape(re.sub(r"\s+", " ", text)).strip()


def commons_request(session: requests.Session, params: Dict[str, Any], retries: int = 5) -> Dict[str, Any]:
    for attempt in range(retries):
        response = session.get(COMMONS_API, params=params, timeout=30)
        if response.status_code == 429:
            time.sleep(2 + attempt * 2)
            continue
        response.raise_for_status()
        try:
            return response.json()
        except ValueError:
            if attempt == retries - 1:
                raise
            time.sleep(1 + attempt)
    raise RuntimeError("Commons API request failed")


def chunked(items: List[str], size: int) -> Iterable[List[str]]:
    for index in range(0, len(items), size):
        yield items[index : index + size]


def query_file_pages(session: requests.Session, titles: List[str]) -> Dict[str, Dict[str, Any]]:
    pages_by_title: Dict[str, Dict[str, Any]] = {}
    normalized: Dict[str, str] = {}
    redirects: Dict[str, str] = {}

    for title_chunk in chunked(titles, 45):
        data = commons_request(
            session,
            {
                "action": "query",
                "format": "json",
                "redirects": "1",
                "titles": "|".join(title_chunk),
                "prop": "imageinfo|info",
                "inprop": "url",
                "iiprop": "url|mime|size|user|extmetadata|canonicaltitle",
            },
        )

        for item in data.get("query", {}).get("normalized", []):
            normalized[item["from"]] = item["to"]
        for item in data.get("query", {}).get("redirects", []):
            redirects[item["from"]] = item["to"]

        for page in data.get("query", {}).get("pages", {}).values():
            if "missing" in page or not page.get("imageinfo"):
                continue
            pages_by_title[page["title"]] = page

    result: Dict[str, Dict[str, Any]] = {}
    for original in titles:
        key = redirects.get(normalized.get(original, original), normalized.get(original, original))
        if key in pages_by_title:
            result[original] = pages_by_title[key]
    return result


def extension_from_url(url: str, fallback: str = ".ogg") -> str:
    path = unquote(urlparse(url).path)
    suffix = Path(path).suffix.lower()
    return suffix if suffix else fallback


def download_file(session: requests.Session, url: str, out_path: Path, force: bool) -> bool:
    if out_path.exists() and not force:
        return True

    out_path.parent.mkdir(parents=True, exist_ok=True)
    last_status = ""
    for attempt in range(5):
        response = session.get(url, timeout=60)
        last_status = f"{response.status_code} {response.text[:60]}"
        if response.status_code == 429:
            time.sleep(5 + attempt * 5)
            continue
        if not response.ok:
            time.sleep(2 + attempt * 2)
            continue
        out_path.write_bytes(response.content)
        return True
    print(f"download skipped: {url} ({last_status})")
    return False


def metadata_for(page: Dict[str, Any], local_path: str, kind: str, item_id: str) -> Dict[str, Any]:
    imageinfo = page["imageinfo"][0]
    ext = imageinfo.get("extmetadata", {})

    def meta(name: str) -> str:
        value = ext.get(name, {}).get("value", "")
        return clean_html(value)

    title = page["title"]
    return {
        "id": item_id,
        "kind": kind,
        "title": title,
        "page_url": f"https://commons.wikimedia.org/wiki/{title.replace(' ', '_')}",
        "source_url": imageinfo["url"],
        "audio": local_path,
        "mime": imageinfo.get("mime", ""),
        "size": imageinfo.get("size", 0),
        "duration": meta("Duration"),
        "description": meta("ImageDescription"),
        "artist": meta("Artist"),
        "credit": meta("Credit"),
        "license": meta("LicenseShortName") or meta("UsageTerms"),
        "license_url": meta("LicenseUrl"),
        "attribution": meta("Attribution"),
    }


def pick_first_existing(pages: Dict[str, Dict[str, Any]], candidates: List[str]) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    for title in candidates:
        if title in pages:
            return title, pages[title]
    return None, None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=DEFAULT_DATA)
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    data = json.loads(Path(args.data).read_text(encoding="utf-8"))
    out_root = Path(args.out)
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    phoneme_items = {item["id"]: item for item in data["phonemes"]}
    word_items = {item["id"]: item for item in data["words"]}

    titles: List[str] = []
    titles.extend(PHONEME_COMMONS_TITLES.values())
    for candidates in WORD_COMMONS_TITLE_CANDIDATES.values():
        titles.extend(candidates)
    # Preserve order but remove duplicates.
    titles = list(dict.fromkeys(titles))

    if args.dry_run:
        print(f"Would query {len(titles)} Commons file titles and write to {out_root}")
        return 0

    pages = query_file_pages(session, titles)
    manifest: Dict[str, Any] = {
        "provider": "Wikimedia Commons",
        "source_pages": [
            "https://commons.wikimedia.org/wiki/General_phonetics",
            "https://commons.wikimedia.org/wiki/Category:U.S._English_pronunciation",
        ],
        "phonemes": [],
        "words": [],
        "missing": {"phonemes": [], "words": []},
    }

    for item_id, title in PHONEME_COMMONS_TITLES.items():
        item = phoneme_items.get(item_id)
        page = pages.get(title)
        if not item or not page:
            manifest["missing"]["phonemes"].append({"id": item_id, "title": title})
            continue

        imageinfo = page["imageinfo"][0]
        extension = extension_from_url(imageinfo["url"])
        out_path = out_root / "phonemes" / f"{item_id}{extension}"
        if not download_file(session, imageinfo["url"], out_path, args.force):
            manifest["missing"]["phonemes"].append({"id": item_id, "title": title, "reason": "download_failed"})
            continue
        manifest["phonemes"].append(
            {
                **metadata_for(page, str(out_path), "phoneme", item_id),
                "label": item["label"],
                "ipa": item["ipa"],
                "type": item["type"],
            }
        )
        print(f"phoneme {item_id}: {out_path}")
        time.sleep(0.08)

    for item_id, item in word_items.items():
        candidates = WORD_COMMONS_TITLE_CANDIDATES.get(item_id, [])
        picked_title, page = pick_first_existing(pages, candidates)
        if not picked_title or not page:
            manifest["missing"]["words"].append({"id": item_id, "word": item["word"], "candidates": candidates})
            continue

        imageinfo = page["imageinfo"][0]
        extension = extension_from_url(imageinfo["url"])
        out_path = out_root / "words" / f"{item_id}{extension}"
        if not download_file(session, imageinfo["url"], out_path, args.force):
            manifest["missing"]["words"].append({"id": item_id, "word": item["word"], "title": picked_title, "reason": "download_failed"})
            continue
        manifest["words"].append(
            {
                **metadata_for(page, str(out_path), "word", item_id),
                "word": item["word"],
                "ipa": item["ipa"],
                "segments": item["segments"],
            }
        )
        print(f"word {item_id}: {out_path}")
        time.sleep(0.08)

    out_root.mkdir(parents=True, exist_ok=True)
    (out_root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"manifest: {out_root / 'manifest.json'}")
    print(f"missing phonemes: {len(manifest['missing']['phonemes'])}")
    print(f"missing words: {len(manifest['missing']['words'])}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
