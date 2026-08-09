"""タコスパーティー(app.html)用 英語音声一括生成 (piper-tts / lessac)

lessons.json (B1〜B20) から speak() に渡り得る全英語テキストを収集し、
Piper で合成 → party_audio/*.mp3 + party_audio/manifest.json を出力する。

収集対象:
  - vocab の英単語 (testVocab は全vocab なので同一。重複排除)
  - jp_mixed の <マーカー> 英単語 (vocab フォールバックに使われる)
  - sentences の各英文 (シャドウイングのお手本)
  - grammar.examples の各英文
  - 上記英文の単語トークン (並べ替えタイルの読み上げ用。句読点表層形は
    manifest の normalized キーで解決する)
  - SUPPLEMENT: app.html 内ハードコード分 (厨房ラッシュ RUSH_POOL 基本語・
    手作り Lesson1 = L12 の passage/並べ替えタイル)。lessons.json に無い分の保険。

manifest.json 仕様 (app.html 組込み側への引き継ぎ):
  { "exact":      { "<原文そのまま>": "party_audio/<md5先頭12桁>.mp3", ... },
    "normalized": { "<正規化キー>":   "party_audio/<md5先頭12桁>.mp3", ... } }
  - 正規化 = 小文字化・前後空白除去・末尾の .,!? 除去 (下の normalize() と同一)
  - exact には 英文全文 / 単語 / 文中トークンの表層形("Hello!" 等) を登録済み
  - 衝突時の優先: exact は「全文」優先 / normalized は「単語クリップ」優先
  - ファイル名 = md5(合成テキスト)の先頭12桁。単語の合成テキストは小文字形

使い方: python3 gen_party_audio.py
再実行時は既存 mp3 (500バイト超) をスキップして差分のみ生成する。
"""
import hashlib
import json
import sys as _sys
from concurrent.futures import ThreadPoolExecutor
import re
import subprocess
import sys
import time
from pathlib import Path

_sys.path.insert(0, str(Path(__file__).parent.parent))
import piper_synth  # noqa: E402  共通の合成パイプライン

BASE = Path(__file__).parent
PIPER = "/Users/masaki/Library/Python/3.9/bin/piper"
VOICE = BASE.parent / "vocab_sources/piper_test/voices/lessac.onnx"
OUT_DIR = BASE / "party_audio"
MANIFEST = OUT_DIR / "manifest.json"
TIMEOUT = 30
MIN_MP3_BYTES = 500
RETRIES = 2

# --- app.html 内ハードコード分の保険 (lessons.json に無いテキスト) ---
# 厨房ラッシュ RUSH_POOL 基本語 (app.html L799)
SUPPLEMENT_WORDS = [
    "dog", "water", "school", "book", "friend", "hello", "today", "place",
    "island", "gate", "welcome", "name", "guide", "excited", "amazing", "strange",
    # L12 並べ替えタイル(ダミー含む)のうち念のため
    "was", "very", "the", "my", "this", "is", "are", "am", "you",
]
# 手作り Lesson1 (L12) passage のうち lessons.json と表記が異なる文
SUPPLEMENT_SENTENCES = [
    "This island is a little strange, too.",
]


def normalize(text: str) -> str:
    """manifest の normalized キー: 小文字化・前後空白除去・末尾の .,!? 除去"""
    t = text.strip().lower()
    t = re.sub(r"[.,!?]+$", "", t)
    return t.strip()


def clean_token(tok: str) -> str:
    """文中トークン → 発音対象の単語 (前後の記号を除去。内部の ' は残す)"""
    return re.sub(r"^[^A-Za-z0-9']+|[^A-Za-z0-9']+$", "", tok)


def collect(lessons: list) -> tuple[dict, dict]:
    """収集して {単語小文字形: 表層形集合}, {英文: None} を返す"""
    words: dict[str, set] = {}   # 小文字形 -> exact登録する表層形の集合
    sentences: dict[str, None] = {}  # 英文(原文) -> None (順序保持dict)

    def add_word(surface: str):
        w = clean_token(surface)
        if not w or not re.search(r"[A-Za-z]", w):
            return
        key = w.lower()
        words.setdefault(key, set()).add(surface)
        words[key].add(w)
        words[key].add(key)

    def add_sentence(en: str):
        en = (en or "").strip()
        if not en:
            return
        sentences.setdefault(en)
        # 並べ替えタイル用: 文中トークン(表層形のまま)も単語として登録
        for tok in en.split():
            add_word(tok)

    for ls in lessons:
        for v in ls.get("vocab", []):
            add_word(v.get("w", ""))
        for m in ls.get("jp_mixed", []):
            for w in m.get("words", []):
                add_word(w.get("w", ""))
        for s in ls.get("sentences", []):
            add_sentence(s.get("en", ""))
        for ex in ls.get("grammar", {}).get("examples", []):
            add_sentence(ex.get("en", ""))

    for w in SUPPLEMENT_WORDS:
        add_word(w)
    for s in SUPPLEMENT_SENTENCES:
        add_sentence(s)

    # --- 🥫サルサグラマー: 選択肢の単語（選んだ瞬間に発音）＋ 正解を入れた完成文（正解時に通し読み） ---
    for path in ("grammar_questions.json", "middle_grammar.json", "high_grammar.json"):
        f = BASE / path
        if not f.exists():
            continue
        data = json.loads(f.read_text(encoding="utf-8"))
        for les in data.values():
            for q in les.get("questions", []):
                for c in q.get("choices", []):
                    add_word(str(c))
                add_sentence(filled_sentence(q))

    # --- 中学生編・高校生編: トマトの単語 / チーズの本文 / レタスの文法例文 ---
    for path in ("middle_lessons.json", "high_lessons.json"):
        f = BASE / path
        if not f.exists():
            continue
        for ml in json.loads(f.read_text(encoding="utf-8")):
            for s in ml.get("vocabSentences", []):
                for w in s.get("words", []):
                    add_word(w.get("w", ""))
            for en in ml.get("enSentences", []):
                add_sentence(en)
            for ex in ml.get("grammar", {}).get("examples", []):
                add_sentence(ex.get("en", ""))

    return words, sentences


def filled_sentence(q: dict) -> str:
    """穴埋め問題 → 正解を空所に入れた完成文（サルサ正解時の読み上げ用）"""
    en = str(q.get("q", "")).strip()
    choices = q.get("choices", [])
    a = q.get("a", 0)
    if "___" not in en or not (0 <= a < len(choices)):
        return en
    s = en.replace("___", str(choices[a]))
    return re.sub(r"\s+([.,!?])", r"\1", re.sub(r"\s+", " ", s)).strip()


def mp3_name(tts_text: str) -> str:
    return hashlib.md5(tts_text.encode("utf-8")).hexdigest()[:12] + ".mp3"


def synth(text: str, out_mp3: Path, kind: str = "sentence") -> bool:
    """piper_synth（共通パイプライン）で合成。

    単語は「先頭無音120ms + 歯擦音の候補選定 + 同音異義語の音素上書き」、
    文はテキスト入力のまま（文脈で同音異義語も正しく読める）。詳細は piper_synth.py 参照。
    """
    if out_mp3.exists() and out_mp3.stat().st_size > MIN_MP3_BYTES:
        return True
    if kind == "word":
        return piper_synth.synth_word(text, out_mp3)
    return piper_synth.synth_text(text, out_mp3)


def main() -> int:
    lessons = json.loads((BASE / "lessons.json").read_text(encoding="utf-8"))
    words, sentences = collect(lessons)
    OUT_DIR.mkdir(exist_ok=True)

    # 合成ジョブ: (合成テキスト, 種別, exact登録キー集合)
    jobs: list[tuple[str, str, set]] = []
    for key in sorted(words):
        jobs.append((key, "word", words[key]))
    for en in sentences:
        jobs.append((en, "sentence", {en}))

    exact: dict[str, str] = {}
    normalized: dict[str, str] = {}
    failed: list[str] = []
    ok = skip = 0
    t0 = time.time()
    total = len(jobs)

    def register(tts_text: str, kind: str, surfaces: set):
        rel = f"party_audio/{mp3_name(tts_text)}"
        for s in surfaces:
            # exact: 全文を優先 (単語が先に埋めた同名キーは文が上書き)
            if kind == "sentence" or s not in exact:
                exact[s] = rel
        for s in surfaces:
            n = normalize(s)
            if not n:
                continue
            # normalized: 単語クリップを優先 (文は未登録キーのみ埋める)
            if kind == "word" or n not in normalized:
                normalized[n] = rel

    # 単語→文 の順に処理しつつ、上書き優先規則は register() 内で制御
    # 合成は外部プロセス(piper/ffmpeg)待ちが大半なのでスレッドで並列化する
    WORKERS = 6
    done = [0]

    def work(job):
        tts_text, kind, surfaces = job
        mp3 = OUT_DIR / mp3_name(tts_text)
        exists = mp3.exists() and mp3.stat().st_size > MIN_MP3_BYTES
        got = True if exists else synth(tts_text, mp3, kind)
        done[0] += 1
        i = done[0]
        if i % 50 == 0 or i == total:
            elapsed = time.time() - t0
            eta = (total - i) * elapsed / max(i, 1)
            print(f"  進捗 {i}/{total} / {elapsed:.0f}s (残り{eta:.0f}s)", flush=True)
        return job, got, exists

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        for (tts_text, kind, surfaces), got, exists in pool.map(work, jobs):
            if not got:
                failed.append(tts_text)
                continue
            register(tts_text, kind, surfaces)
            if exists:
                skip += 1
            else:
                ok += 1

    MANIFEST.write_text(
        json.dumps({"exact": exact, "normalized": normalized},
                   ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    n_words = sum(1 for j in jobs if j[1] == "word")
    n_sents = total - n_words
    print(f"✅ 完了: 単語{n_words} + 文{n_sents} = 計{total}"
          f" / 生成{ok} 既存{skip} 失敗{len(failed)} / {time.time()-t0:.0f}s")
    if failed:
        print("⚠️ 失敗一覧:")
        for f in failed:
            print("  -", f)
    print(f"   → {MANIFEST}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
