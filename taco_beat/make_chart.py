#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_chart.py — タコス・ビート 譜面生成パイプライン（1曲ぶん）

使い方:
    python3 make_chart.py <入力mp3> --id b2 [--outdir .] [--inject index.html] [--force]

    ※ python3 は必ず venv のものを使う:
       /Users/masaki/Documents/ClaudeCode/英語学習教材作成/venv/bin/python3
       (whisper / torch / torchaudio / scipy / numpy 入り)

処理の流れ:
    [1] ffmpeg で 96kbps mp3 化      → <outdir>/songs/<id>.mp3
    [2] ffmpeg で 16kHz mono wav 化   → <outdir>/.cache/<id>/<id>_16k.wav
    [3] Whisper medium word_timestamps → 実際に歌われた語列（綴り補正込み）
    [4] torchaudio MMS_FA 強制アライメント → 各単語の高精度タイミング
    [5] spectral-flux オンセット検出 → 機能語だけ ±0.14s でオンセットに吸着
    [6] BPM / 位相 推定（粗0.5BPM → 細0.02BPM・8ms）
    [7] ホールド焼き込み（次語まで >0.95s）＋ 間奏🫓フィラー（拍グリッド）
    [8] <outdir>/charts/<id>.js に `const BEAT=...; const SONG_BPM=...;` を出力
        --inject 指定時は index.html の BEAT/SONG_BPM ブロックと <audio src> を置換

設計方針:
    - 乱数不使用・全ローカル実行（API 料金ゼロ）・再実行安全（冪等）
    - Whisper は遅いので結果を .cache にキャッシュ（曲の md5 が変われば自動再実行）
    - 落とし穴対策:
        * whisper CLI ラッパーはシェバン破損 → `python -m whisper` で実行
        * torchaudio.load は torchcodec 不在で使えない → scipy.io.wavfile で読む
"""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

# ============================================================================
# 編集しやすいように定数はすべてここに置く
# ============================================================================

# --- 綴り補正マップ（Whisper の聞き取りブレ → 正式表記。キーは小文字） ---
# 新しい曲で固有名詞が変な綴りになったらここに追加する。
SPELL_FIX = {
    "phonics": "Funnics",   # Whisper は Funnics を Phonics と聞き取る
    "funnics": "Funnics",
    "fonix": "Funnics",
    "island": "Island",
    "tom": "Tom",
    "teacher": "Teacher",
    "tacos": "Tacos",
}

# --- オンセット吸着対象の機能語（短い語は強制アライメントがズレやすい） ---
# TASK-20260707-001「改良5」: この16語だけ spectral-flux オンセットに吸着する。
SNAP_WORDS = {
    "i", "am", "a", "the", "to", "is", "are", "you", "your", "my",
    "oh", "hi", "wow", "too", "here", "what's",
}

# --- key=0（機能語扱い＝小さいノーツ）にする語。それ以外は key=1（内容語） ---
FUNCTION_WORDS = SNAP_WORDS | {"this"}

# --- タイミング系パラメータ（現行 b1 譜面を生成した値。安易に変えない） ---
SNAP_WINDOW = 0.14    # 機能語オンセット吸着の探索窓 [s]
MIN_GAP = 0.05        # ノーツ間の最小間隔 [s]（吸着で順序が壊れないように）
HOLD_GAP = 0.95       # 次の単語までこれより空いたらホールドにする [s]
HOLD_PAD = 0.30       # ホールド終端は次の単語の 0.3s 手前 [s]
HOLD_MAX = 1.50       # ホールド長の上限 [s]
HOLD_TAIL = 0.15      # ホールド終端は曲末尾のこの秒数手前までにクランプ [s]
HOLD_MIN = 0.35       # クランプ後これより短いホールドは通常ノーツに戻す [s]
FILLER_GAP = 1.20     # 単語間がこれより空いた区間だけ🫓フィラー候補 [s]
FILLER_EXCLUDE = 0.38 # 拍の±この範囲に単語があればフィラーを置かない [s]
END_MARGIN = 0.60     # 曲の末尾この秒数にはフィラーを置かない [s]
BPM_MIN, BPM_MAX = 55.0, 110.0  # BPM 探索範囲（範囲外の曲はここを調整）

# --- Whisper の伴奏誤認識を除外する条件 ---
# 長い間奏で、同じ低信頼の1語（例: "Music"）を何度も返す場合だけ除外する。
# 単発の低信頼語は実際の歌詞である可能性があるため、この条件では消さない。
HALLUCINATION_NO_SPEECH = 0.75
HALLUCINATION_WORD_PROB = 0.01
HALLUCINATION_REPEAT_COUNT = 3
OUTRO_HALLUCINATION_RE = re.compile(
    r"^thanks?(?:\s+you)?\s+for\s+watching[.!?]*$", re.IGNORECASE)

# --- オンセット検出（spectral flux）パラメータ ---
SR = 16000            # 解析サンプルレート [Hz]
N_FFT = 1024          # STFT 窓長
HOP = 160             # STFT ホップ長（=10ms）
ONSET_LOCAL_WIN = 10  # 適応しきい値の局所平均窓（±フレーム）
ONSET_DELTA = 1.5     # しきい値 = 局所平均 × この係数
ONSET_MIN_SEP = 0.05  # オンセット同士の最小間隔 [s]

MP3_BITRATE = "96k"   # ゲーム同梱用 mp3 のビットレート


def log(step, msg):
    print(f"[{step}] {msg}", flush=True)


def die(msg):
    print(f"\nERROR: {msg}", file=sys.stderr, flush=True)
    sys.exit(1)


def run(cmd, what):
    """外部コマンドを実行。失敗したら stderr を添えて明確に止める。"""
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        die(f"{what} に失敗しました。\n  cmd: {' '.join(map(str, cmd))}\n"
            f"  stderr: {proc.stderr.strip()[-2000:]}")
    return proc


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ============================================================================
# [1][2] 音声変換
# ============================================================================

def encode_song(src, dst):
    """入力を 96kbps mp3 にして songs/ へ。既に mp3・96kbps 以下ならコピーで済ます
    （再エンコードの劣化とデコーダ遅延ズレを避ける）。"""
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a:0",
         "-show_entries", "stream=codec_name,bit_rate",
         "-of", "json", str(src)], capture_output=True, text=True)
    codec, bitrate = "", 10**9
    if probe.returncode == 0:
        try:
            st = json.loads(probe.stdout)["streams"][0]
            codec = st.get("codec_name", "")
            bitrate = int(st.get("bit_rate") or 10**9)
        except (KeyError, IndexError, ValueError):
            pass
    if codec == "mp3" and bitrate <= 100_000:
        shutil.copyfile(src, dst)
        log("1/8", f"入力は既に mp3 {bitrate//1000}kbps → そのままコピー: {dst}")
    else:
        run(["ffmpeg", "-y", "-i", str(src), "-c:a", "libmp3lame",
             "-b:a", MP3_BITRATE, str(dst)], "mp3 変換 (ffmpeg)")
        log("1/8", f"96kbps mp3 を生成: {dst}")


def make_wav16k(mp3, wav):
    run(["ffmpeg", "-y", "-i", str(mp3), "-ac", "1", "-ar", str(SR), str(wav)],
        "16kHz wav 変換 (ffmpeg)")
    log("2/8", f"16kHz mono wav を生成: {wav}")


# ============================================================================
# [3] Whisper（キャッシュつき）
# ============================================================================

def whisper_words(mp3, cache_dir, song_id, force):
    """Whisper medium で word_timestamps。結果は .cache に保存し再実行時は再利用。"""
    json_path = cache_dir / f"{song_id}.json"
    md5_path = cache_dir / "song.md5"
    song_md5 = md5_of(mp3)

    if (not force and json_path.exists() and md5_path.exists()
            and md5_path.read_text().strip() == song_md5):
        log("3/8", f"Whisper 結果をキャッシュから再利用: {json_path}")
    else:
        log("3/8", "Whisper medium で単語タイミングを認識中…（初回は数分かかる）")
        # 注意: `whisper` CLI はシェバン破損のため必ず `python -m whisper` を使う
        run([sys.executable, "-m", "whisper", str(mp3),
             "--model", "medium", "--language", "en",
             "--word_timestamps", "True",
             "--output_format", "json", "--output_dir", str(cache_dir),
             "--fp16", "False"], "Whisper 音声認識")
        if not json_path.exists():
            die(f"Whisper の出力 {json_path} が見つかりません")
        md5_path.write_text(song_md5)
        log("3/8", f"Whisper 完了: {json_path}")

    data = json.loads(json_path.read_text())
    segments = data.get("segments", [])

    # Whisper は長い伴奏を、非常に低い単語確率で "Music" や "Thank" などの
    # 1語として繰り返し誤認することがある。同じ曲内で3回以上繰り返された
    # 「高い無音確率 + 低い単語確率 + 1語だけ」のセグメントに限って除外する。
    suspicious = {}
    for i, seg in enumerate(segments):
        seg_words = seg.get("words", [])
        if len(seg_words) != 1:
            continue
        word = seg_words[0]
        token = display_word(word.get("word", ""))
        if (token
                and float(seg.get("no_speech_prob", 0.0)) >= HALLUCINATION_NO_SPEECH
                and float(word.get("probability", 1.0)) < HALLUCINATION_WORD_PROB):
            suspicious.setdefault(token, []).append(i)
    repeated_rejected = {
        i for indices in suspicious.values()
        if len(indices) >= HALLUCINATION_REPEAT_COUNT
        for i in indices
    }
    outro_rejected = {
        i for i, seg in enumerate(segments)
        if float(seg.get("no_speech_prob", 0.0)) >= HALLUCINATION_NO_SPEECH
        and OUTRO_HALLUCINATION_RE.fullmatch(seg.get("text", "").strip())
    }
    rejected = repeated_rejected | outro_rejected
    if rejected:
        details = []
        if repeated_rejected:
            labels = sorted({display_word(segments[i]["words"][0]["word"])
                             for i in repeated_rejected})
            details.append(f"反復語 {', '.join(labels)}: {len(repeated_rejected)}件")
        if outro_rejected:
            details.append(f"終端定型句: {len(outro_rejected)}件")
        log("3/8", f"音声認識の誤認識を除外 ({'; '.join(details)})")

    words = [(w["word"].strip(), float(w["start"]))
             for i, seg in enumerate(segments) if i not in rejected
             for w in seg.get("words", [])]
    if not words:
        die("Whisper が単語を1つも検出できませんでした（音源を確認してください）")
    log("3/8", f"認識単語数: {len(words)}  先頭: "
              f"{' '.join(w for w, _ in words[:6])} …")
    return words


def display_word(raw):
    """表示用の綴り: 句読点を除去し、小文字化して綴り補正マップを適用。"""
    stripped = raw.strip().strip('.,!?;:"()…').lower()
    cleaned = re.sub(r"[^a-z']", "", stripped)
    return SPELL_FIX.get(cleaned, cleaned)


# ============================================================================
# [4] MMS_FA 強制アライメント
# ============================================================================

def force_align(wav_path, words):
    """torchaudio MMS_FA(wav2vec2) で各単語の開始時刻を得る。
    torchaudio.load は使えない(torchcodec不在)ので scipy で読む。"""
    log("4/8", "MMS_FA 強制アライメント中…（初回はモデル約1.18GBをDL）")
    import numpy as np
    import torch
    import torchaudio
    from scipy.io import wavfile

    sr, x = wavfile.read(str(wav_path))
    if sr != SR:
        die(f"wav のサンプルレートが {sr} です（{SR} を想定）")
    x = x.astype(np.float32)
    if x.ndim > 1:
        x = x.mean(axis=1)
    peak = float(np.abs(x).max()) or 1.0
    wav = torch.tensor(x / peak).unsqueeze(0)

    # transcript は小文字 a-z のみに正規化（what's → whats）
    norm = [re.sub(r"[^a-z]", "", w.lower()) for w, _ in words]
    keep = [i for i, n in enumerate(norm) if n]
    transcript = [norm[i] for i in keep]

    bundle = torchaudio.pipelines.MMS_FA
    model = bundle.get_model()
    tokenizer = bundle.get_tokenizer()
    aligner = bundle.get_aligner()
    with torch.inference_mode():
        emission, _ = model(wav)
        spans = aligner(emission[0], tokenizer(transcript))

    ratio = (wav.shape[1] / SR) / emission.shape[1]
    times = {}
    for k, span in zip(keep, spans):
        times[k] = round(span[0].start * ratio, 3)
    aligned = [(display_word(words[i][0]), times[i])
               for i in range(len(words)) if i in times]
    log("4/8", f"アライメント完了: {len(aligned)} 語  "
              f"先頭: {aligned[0][0]}={aligned[0][1]}s")
    return aligned


# ============================================================================
# [5] オンセット検出 → 機能語スナップ
# ============================================================================

def onset_envelope(wav_path):
    """spectral flux のエンベロープ（10ms グリッド）とオンセット時刻列を返す。"""
    import numpy as np
    from scipy.io import wavfile

    sr, x = wavfile.read(str(wav_path))
    x = x.astype(np.float32)
    if x.ndim > 1:
        x = x.mean(axis=1)
    x /= (np.abs(x).max() or 1.0)

    n_frames = 1 + (len(x) - N_FFT) // HOP
    idx = np.arange(N_FFT)[None, :] + HOP * np.arange(n_frames)[:, None]
    frames = x[idx] * np.hanning(N_FFT)[None, :]
    mag = np.abs(np.fft.rfft(frames, axis=1))
    flux = np.maximum(0.0, np.diff(mag, axis=0)).sum(axis=1)
    flux = np.concatenate([[0.0], flux])
    flux /= (flux.max() or 1.0)
    frame_t = (np.arange(n_frames) * HOP + N_FFT / 2) / sr  # フレーム中心時刻

    # 適応しきい値 + 局所最大でピーク抽出、放物線補間でサブフレーム精度に
    onsets = []
    w = ONSET_LOCAL_WIN
    min_sep_frames = int(round(ONSET_MIN_SEP * sr / HOP))
    last = -10**9
    for i in range(1, n_frames - 1):
        lo, hi = max(0, i - w), min(n_frames, i + w + 1)
        if flux[i] < np.mean(flux[lo:hi]) * ONSET_DELTA:
            continue
        if flux[i] < flux[i - 1] or flux[i] < flux[i + 1]:
            continue
        if i - last < min_sep_frames:
            continue
        denom = flux[i - 1] - 2 * flux[i] + flux[i + 1]
        shift = 0.0 if denom == 0 else 0.5 * (flux[i - 1] - flux[i + 1]) / denom
        onsets.append(frame_t[i] + shift * HOP / sr)
        last = i
    log("5/8", f"オンセット検出: {len(onsets)} 個")
    return flux, frame_t, onsets


def snap_function_words(aligned, onsets):
    """機能語だけ ±SNAP_WINDOW 秒以内のオンセットに吸着。
    未使用オンセット優先・語順と最小間隔 MIN_GAP は必ず保持。"""
    result = [list(wt) for wt in aligned]  # [word, t]
    used = set()
    snapped = 0
    for i, (word, t) in enumerate(aligned):
        if word not in SNAP_WORDS:
            continue
        prev_t = result[i - 1][1] if i > 0 else -1e9
        next_t = aligned[i + 1][1] if i + 1 < len(aligned) else 1e9
        cands = sorted((c for c in onsets if abs(c - t) <= SNAP_WINDOW),
                       key=lambda c: (c in used, abs(c - t)))
        for c in cands:
            if prev_t + MIN_GAP <= c <= next_t - MIN_GAP:
                result[i][1] = round(c, 3)
                used.add(c)
                if abs(c - t) > 1e-4:
                    snapped += 1
                break
    log("5/8", f"機能語スナップ: {snapped} 語を補正")
    return [(w, t) for w, t in result]


# ============================================================================
# [6] BPM / 位相 推定
# ============================================================================

def estimate_bpm(flux, frame_t):
    """オンセットエンベロープに対する拍グリッドのグリッドサーチ。
    粗探索 0.5BPM → 細探索 0.02BPM・位相 8ms。乱数不使用で決定的。
    ※ flux は生のまま使う（平滑化すると位相推定が別の極大に流れる。b1 実測で確認済み）"""
    import numpy as np

    log("6/8", "BPM / 位相を推定中…")
    env = flux
    dur = frame_t[-1]

    def score(bpm, phase):
        period = 60.0 / bpm
        beats = np.arange(phase, dur, period)
        return float(np.interp(beats, frame_t, env).mean())

    def search(bpms, phase_step):
        best = (-1.0, 0.0, 0.0)
        for bpm in bpms:
            period = 60.0 / bpm
            for phase in np.arange(0.0, period, phase_step):
                s = score(bpm, phase)
                if s > best[0]:
                    best = (s, bpm, phase)
        return best

    _, bpm_c, _ = search(np.arange(BPM_MIN, BPM_MAX, 0.5), 0.016)
    lo = max(BPM_MIN, bpm_c - 0.5)
    hi = min(BPM_MAX, bpm_c + 0.5)
    _, bpm, phase = search(np.arange(lo, hi, 0.02), 0.008)
    bpm = round(bpm, 2)
    phase = round(phase, 3)
    log("6/8", f"BPM={bpm}  位相={phase}s")
    return bpm, phase


# ============================================================================
# [7] ホールド焼き込み + 🫓フィラー
# ============================================================================

def build_beat(words, bpm, phase, duration):
    """BEAT 行列 [[t, word|"", key, holdEnd], ...] を組み立てる。"""
    # ホールド: 次の単語まで HOLD_GAP より空いたら焼き込み
    # 最後の単語は「次の単語」が無いので、曲の残り時間を gap にする（曲より長く伸びるホールドを作らない）。
    # ホールド終端は必ず曲末尾の HOLD_TAIL 秒手前までにクランプ＝伸ばし切る前に曲が終わるのを防ぐ。
    limit = duration - HOLD_TAIL
    rows = []
    for i, (word, t) in enumerate(words):
        gap = (words[i + 1][1] - t) if i + 1 < len(words) else max(0.0, limit - t)
        hold_end = round(min(t + min(gap - HOLD_PAD, HOLD_MAX), limit), 3) if gap > HOLD_GAP else 0
        if hold_end and hold_end - t < HOLD_MIN:   # クランプで短くなりすぎたら通常ノーツに
            hold_end = 0
        key = 0 if word in FUNCTION_WORDS else 1
        rows.append([round(t, 3), word, key, hold_end])

    # 🫓フィラー: 単語間 > FILLER_GAP の区間（曲頭・曲末含む）の拍のみ。
    # ±FILLER_EXCLUDE に単語がある拍・ホールド中の拍には置かない。
    period = 60.0 / bpm
    word_times = [t for _, t in words]
    holds = [(r[0], r[3]) for r in rows if r[3]]
    fillers = []
    t = phase
    while t < duration - END_MARGIN:
        tb = round(t, 3)
        prev_w = max((wt for wt in word_times if wt <= tb), default=None)
        next_w = min((wt for wt in word_times if wt > tb), default=None)
        in_big_gap = (prev_w is None or next_w is None
                      or (next_w - prev_w) > FILLER_GAP)
        near_word = any(abs(wt - tb) <= FILLER_EXCLUDE for wt in word_times)
        in_hold = any(h0 <= tb <= h1 for h0, h1 in holds)
        if in_big_gap and not near_word and not in_hold:
            fillers.append([tb, "", 0, 0])
        t += period

    beat = sorted(rows + fillers, key=lambda r: r[0])
    n_hold = sum(1 for r in beat if r[3])
    log("7/8", f"譜面: 単語 {len(rows)} + 🫓フィラー {len(fillers)} = "
              f"{len(beat)} ノーツ（ホールド {n_hold} 本）")
    return beat


# ============================================================================
# [8] 出力 / 注入
# ============================================================================

def render_js(beat, bpm):
    rows = ",".join(
        json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in beat)
    return f"const BEAT=[{rows}];\nconst SONG_BPM={bpm};\n"


def inject(index_path, chart_js, mp3_path):
    html = index_path.read_text(encoding="utf-8")
    block = chart_js.rstrip("\n")
    pattern = r"const BEAT=\[.*?\];\s*\nconst SONG_BPM=[0-9.]+;"
    if not re.search(pattern, html, flags=re.S):
        die(f"{index_path} に BEAT/SONG_BPM ブロックが見つかりません")
    html = re.sub(pattern, block.replace("\\", r"\\"), html, count=1, flags=re.S)

    try:
        rel = mp3_path.resolve().relative_to(index_path.resolve().parent)
    except ValueError:
        rel = mp3_path.resolve()
    audio_pat = r'(<audio id="song"[^>]*\bsrc=")[^"]*(")'
    if not re.search(audio_pat, html):
        die(f'{index_path} に <audio id="song" src=...> が見つかりません')
    html = re.sub(audio_pat, lambda m: m.group(1) + str(rel) + m.group(2),
                  html, count=1)
    index_path.write_text(html, encoding="utf-8")
    log("8/8", f"{index_path} に注入完了（audio src → {rel}）")


# ============================================================================
# main
# ============================================================================

def main():
    ap = argparse.ArgumentParser(
        description="タコス・ビート譜面生成（詳細は CONTENT.md 参照）")
    ap.add_argument("input_mp3", help="入力音源 (Suno mp3 など)")
    ap.add_argument("--id", required=True, help="曲ID (例: b2)")
    ap.add_argument("--outdir", default=".", help="出力先 (既定: カレント)")
    ap.add_argument("--inject", metavar="INDEX_HTML", default=None,
                    help="指定した index.html の BEAT/SONG_BPM と audio src を置換")
    ap.add_argument("--force", action="store_true",
                    help="Whisper キャッシュを無視して再認識")
    args = ap.parse_args()

    src = Path(args.input_mp3)
    if not src.exists():
        die(f"入力ファイルがありません: {src}")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.id):
        die(f"--id は英数字・-_ のみ使用可: {args.id}")
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        die("ffmpeg / ffprobe が見つかりません（brew install ffmpeg）")

    outdir = Path(args.outdir)
    songs_dir = outdir / "songs"
    charts_dir = outdir / "charts"
    cache_dir = outdir / ".cache" / args.id
    for d in (songs_dir, charts_dir, cache_dir):
        d.mkdir(parents=True, exist_ok=True)

    mp3 = songs_dir / f"{args.id}.mp3"
    wav = cache_dir / f"{args.id}_16k.wav"

    encode_song(src, mp3)                                     # [1]
    make_wav16k(mp3, wav)                                     # [2]
    words_raw = whisper_words(mp3, cache_dir, args.id, args.force)  # [3]
    aligned = force_align(wav, words_raw)                     # [4]
    flux, frame_t, onsets = onset_envelope(wav)               # [5]
    snapped = snap_function_words(aligned, onsets)
    bpm, phase = estimate_bpm(flux, frame_t)                  # [6]
    duration = float(frame_t[-1]) + N_FFT / 2 / SR
    beat = build_beat(snapped, bpm, phase, duration)          # [7]

    chart_js = render_js(beat, bpm)                           # [8]
    chart_path = charts_dir / f"{args.id}.js"
    chart_path.write_text(chart_js, encoding="utf-8")
    log("8/8", f"譜面を出力: {chart_path}")

    if args.inject:
        index_path = Path(args.inject)
        if not index_path.exists():
            die(f"--inject 先がありません: {index_path}")
        inject(index_path, chart_js, mp3)

    print("\n完了 ✅")
    print(f"  曲   : {mp3}")
    print(f"  譜面 : {chart_path}")
    if not args.inject:
        print(f"  ゲームに載せるには: python3 make_chart.py ... --inject index.html")


if __name__ == "__main__":
    main()
