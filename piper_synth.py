"""Piper 音声合成の共通モジュール（タコスパーティー / WordTacos 共用）

## これまでの音声の欠陥と、その対処

1. **語頭の /s/ が消える** — 原因は2つ。
   (a) 再生時のクリップ: 生成音声の 12% が「先頭無音 10ms 未満」（音が 0ms から始まる）。
       Audio 要素に src を入れて即再生する構造では再生開始の数十msが飲まれることがあり
       （特に iOS はマイク使用後のオーディオセッション切替で顕著）、0ms から始まる /s/ は丸ごと消える。
       → **先頭に 120ms の無音を必ず入れる**。
   (b) 声（モデル）による当たり外れ: 従来の lessac は語頭 /s/ が極端に弱い
       （実測の平均: lessac 99 / ryan 160 / jenny 264 / amy 309。sport・stop は 0＝完全に無音だった）。
       → **既定を ryan にし、/s/ が潰れる語だけ他の声を実測して差し替える**（下の WORD_VOICE / pick_voice）。
       ※ 音素入力（[[...]]）も試したが不自然になるため不採用。

2. **同音異義語の誤読** — 単語単体だと espeak が別語義の読みを選ぶ（live: 住む=/lɪv/ のはずが /laɪv/）。
   文中なら文脈で正しく読める。→ **キャリア文で合成し、その語の区間だけ強制アライメントで切り出す**（CARRIER）。

3. 歯擦音がスマホのスピーカーで埋もれる → 高域シェルフ +5dB、リミッタで音量維持、96kbps。

## 声の使い分け（ユーザーの試聴で決定）
- **単語は既定 lessac**（従来の聞き慣れた声のまま）。
- **文はすべて ryan**（サルサの読み上げ・チーズの音読で使うため統一）。
- **ユーザーが指定した語**は WORD_VOICE で固定（lessac だと読みが崩れる語）。
- **それ以外の新しい語も同じ基準で判定**: lessac の語頭 /s/ が SIB_MIN 未満なら 4声を実測して最良に差し替える。
- **live は amy のキャリア文から切り出し**（単語単体だと「ライヴ」になるため）。

使い方:
    from piper_synth import synth_word, synth_text
    synth_word("student", Path("out.mp3"))
    synth_text("I am a student.", Path("out.mp3"))
"""
from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from scipy.io import wavfile

BASE = Path(__file__).parent
PIPER = "/Users/masaki/Library/Python/3.9/bin/piper"
VOICE_DIR = BASE / "vocab_sources/piper_test/voices"
VENV_PY = BASE / "venv/bin/python3"          # torchaudio(MMS_FA) は venv にのみ在る
ALIGNER = BASE / "align_word.py"
TIMEOUT = 40
MIN_BYTES = 500
RETRIES = 2

VOICES = ("ryan", "amy", "jenny", "lessac")
SENT_VOICE = "ryan"                          # 文は全部この声（サルサの読み上げ・チーズの音読）
WORD_VOICE_DEFAULT = "lessac"                # 単語の既定は従来どおり lessac（聞き慣れた声を維持）

# ユーザーが試聴して指定した語（既定 lessac では読みが崩れる語）
WORD_VOICE: dict[str, str] = {
    "student": "ryan",
    "school": "jenny",
    "sport": "amy",
    "stop": "ryan",
    "study": "ryan",
    "speak": "amy",
    # sister は lessac のままで可（語頭 /s/ が 355 と十分に出ている）
}

# 同音異義語: 単語単体だと誤読される → この文で合成し、語の区間だけ切り出す（語, 文, 声）
CARRIER: dict[str, tuple[str, str]] = {
    "live": ("I live in Tokyo.", "amy"),      # 住む=/lɪv/（単体だと「ライヴ」になる）
}

LEAD_MS = 120        # 先頭に入れる無音 [ms]
TAIL_S = 0.08        # 末尾に足す無音 [s]
TREBLE_DB = 5        # 歯擦音帯の持ち上げ [dB]
TREBLE_HZ = 4200
BITRATE = "96k"
SAMPLE_RATE = "22050"
CARRIER_PAD = 0.05   # 切り出しの前後マージン [s]

AF = (f"adelay={LEAD_MS},"
      f"treble=g={TREBLE_DB}:f={TREBLE_HZ}:width_type=q:width=0.9,"
      f"alimiter=limit=0.97,"
      f"apad=pad_dur={TAIL_S}")

# 今後の語も「同じ基準」で判断する: 既定(lessac)で語頭 /s/ がこの値未満＝潰れている とみなし、
# 4声を実測して最も明瞭なものへ差し替える。閾値はユーザーの指定から逆算した（差し替え指定のあった
# student 92 / speak 100 / study 42 / school 18 / sport 18 は全て 150 未満、据え置きの sister は 355）。
SIB_MIN = 150.0
_S_INITIAL = re.compile(r"^s", re.I)         # s で始まる語だけ /s/ の実測をかける


def voice_path(voice: str) -> Path:
    return VOICE_DIR / f"{voice}.onnx"


def _piper(text: str, wav: Path, voice: str) -> bool:
    for _ in range(RETRIES):
        try:
            subprocess.run([PIPER, "-m", str(voice_path(voice)), "-f", str(wav)],
                           input=text, text=True, capture_output=True, timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            subprocess.run(["pkill", "-f", "piper"], capture_output=True)
            continue
        if wav.exists() and wav.stat().st_size > MIN_BYTES:
            return True
    return False


def _encode(wav: Path, mp3: Path, ss: float | None = None, to: float | None = None) -> bool:
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    if ss is not None:
        cmd += ["-ss", f"{ss:.3f}"]
    if to is not None:
        cmd += ["-to", f"{to:.3f}"]
    cmd += ["-i", str(wav), "-af", AF, "-ar", SAMPLE_RATE, "-ac", "1", "-b:a", BITRATE, str(mp3)]
    subprocess.run(cmd, check=True)
    return mp3.exists() and mp3.stat().st_size > MIN_BYTES


def onset_sibilance(mp3: Path) -> float:
    """語頭 100ms の 4-10kHz エネルギー（= /s/ の明瞭さ）。先頭の無音は読み飛ばす。"""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        tmp = Path(f.name)
    try:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp3),
                        "-ac", "1", "-ar", "22050", str(tmp)], check=True)
        sr, d = wavfile.read(tmp)
        d = d.astype(np.float32) / 32768.0
        if not np.any(np.abs(d) > 0.01):
            return 0.0
        start = int(np.argmax(np.abs(d) > 0.01))
        n = int(sr * 0.02)
        best = 0.0
        for i in range(start, min(start + int(sr * 0.10), len(d) - n), n):
            seg = d[i:i + n] * np.hanning(n)
            F = np.abs(np.fft.rfft(seg))
            fr = np.fft.rfftfreq(n, 1 / sr)
            best = max(best, float(F[(fr >= 4000) & (fr <= 10000)].sum()))
        return best
    except Exception:
        return 0.0
    finally:
        tmp.unlink(missing_ok=True)


def _carrier_word(word: str, out_mp3: Path) -> bool:
    """キャリア文で合成 → 強制アライメントでその語の区間を切り出す（同音異義語の誤読対策）"""
    sentence, voice = CARRIER[word.lower()]
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        wav, w16 = tmp / "c.wav", tmp / "c16.wav"
        if not _piper(sentence, wav, voice):
            return False
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav),
                        "-ac", "1", "-ar", "16000", str(w16)], check=True)
        r = subprocess.run([str(VENV_PY), str(ALIGNER), str(w16), sentence, word],
                           capture_output=True, text=True)
        if r.returncode != 0:
            return False
        s, e = (float(x) for x in r.stdout.split())
        return _encode(wav, out_mp3, ss=max(0.0, s - CARRIER_PAD), to=e + CARRIER_PAD)


def synth_word(word: str, out_mp3: Path) -> bool:
    """単語1語を合成。声は WORD_VOICE → 既定(ryan)。s始まりで /s/ が潰れる語は4声から最良を採る。"""
    key = word.strip().lower()
    if key in CARRIER:
        return _carrier_word(key, out_mp3)

    voice = WORD_VOICE.get(key, WORD_VOICE_DEFAULT)
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        wav = tmp / "w.wav"
        if not _piper(word, wav, voice) or not _encode(wav, out_mp3):
            return False
        # 指定のある語・s以外で始まる語はここで確定（声を無闇に混ぜない）
        if key in WORD_VOICE or not _S_INITIAL.match(key):
            return True
        if onset_sibilance(out_mp3) >= SIB_MIN:
            return True
        # 語頭の /s/ が潰れている → 他の声を実測して最良を採用
        best_mp3, best_val = out_mp3.read_bytes(), onset_sibilance(out_mp3)
        for v in VOICES:
            if v == voice:
                continue
            w2, m2 = tmp / f"{v}.wav", tmp / f"{v}.mp3"
            if not _piper(word, w2, v) or not _encode(w2, m2):
                continue
            val = onset_sibilance(m2)
            if val > best_val:
                best_val, best_mp3 = val, m2.read_bytes()
        out_mp3.write_bytes(best_mp3)
        return True


def synth_text(text: str, out_mp3: Path) -> bool:
    """文を合成（声は ryan 固定。文脈があるので同音異義語も正しく読める）。"""
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "s.wav"
        if not _piper(text, wav, SENT_VOICE):
            return False
        return _encode(wav, out_mp3)
