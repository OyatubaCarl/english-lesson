"""アプリ同梱用の日本語音声を VOICEPEAK で生成する.

- body_kana を <word> で分割した日本語セグメントごとに合成
  (再生時: seg0 → アプリ内蔵英語TTSで word → seg1 ... の順で繋ぐ)
- 商用利用可(VOICEPEAK ライセンス)。mac内蔵 say は商用不可のため使わない
- 出力: app_audio/<stage>/<quiz_id>_seg<N>.m4a + manifest.json

usage: python3 gen_app_audio_vp.py stage1_quizzes_clean.json stage1
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

VP_BIN = "/Applications/voicepeak.app/Contents/MacOS/voicepeak"
NARRATOR = "Japanese Female 1"
CHAR_LIMIT = 140   # これ以上は無音になる(既存パイプライン知見)
SLEEP_SEC = 1.5    # 連続実行の詰まり対策

ROOT = Path("/Users/masaki/Documents/ClaudeCode/英語学習教材作成/vocab_sources")


def synth(text: str, out_wav: Path) -> bool:
    if len(text) > CHAR_LIMIT:
        # 句点で分割して結合する(稀ケース)
        parts = re.split(r"(?<=。)", text)
        chunks, cur = [], ""
        for p in parts:
            if len(cur) + len(p) <= CHAR_LIMIT:
                cur += p
            else:
                if cur: chunks.append(cur)
                cur = p
        if cur: chunks.append(cur)
        tmp_files = []
        for ci, c in enumerate(chunks):
            t = out_wav.with_suffix(f".part{ci}.wav")
            if not synth(c, t):
                return False
            tmp_files.append(t)
        concat = "|".join(str(t) for t in tmp_files)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error",
                        "-i", f"concat:{concat}", str(out_wav)], check=True)
        for t in tmp_files:
            t.unlink()
        return True
    for attempt in range(2):
        try:
            subprocess.run([VP_BIN, "-s", text, "-o", str(out_wav),
                            "--narrator", NARRATOR],
                           capture_output=True, text=True, timeout=60)
        except subprocess.TimeoutExpired:
            subprocess.run(["pkill", "-f", "voicepeak.*-s"], capture_output=True)
            time.sleep(3)
            continue
        time.sleep(SLEEP_SEC)
        if out_wav.exists():
            return True
        time.sleep(2)
    return out_wav.exists()


def main() -> None:
    src = ROOT / sys.argv[1]
    stage = sys.argv[2]
    out_dir = ROOT / "app_audio" / stage
    out_dir.mkdir(parents=True, exist_ok=True)

    data = json.loads(src.read_text(encoding="utf-8"))
    quizzes = data["quizzes"]

    manifest_path = out_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}

    done = 0
    for q in quizzes:
        qid = q["id"]
        if qid in manifest:
            done += 1
            continue
        kana = q["body_kana"]
        segs = [s.strip() for s in re.split(r"<[^>]+>", kana)]
        entry = {"word": q["word"], "segments": []}
        ok = True
        for si, seg in enumerate(segs):
            if not seg:
                entry["segments"].append(None)  # 文頭/文末に語が来るケース
                continue
            wav = out_dir / f"{qid}_seg{si}.wav"
            m4a = out_dir / f"{qid}_seg{si}.m4a"
            if not m4a.exists():
                if not synth(seg, wav):
                    print(f"  ✗ 合成失敗: {qid} seg{si}")
                    ok = False
                    break
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav),
                                "-ac", "1", "-b:a", "64k", str(m4a)], check=True)
                wav.unlink()
            entry["segments"].append(m4a.name)
        if ok:
            manifest[qid] = entry
            done += 1
            if done % 20 == 0:
                manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
                print(f"  進捗: {done}/{len(quizzes)}")

    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✅ 完了: {done}/{len(quizzes)} → {out_dir}/")


if __name__ == "__main__":
    main()
