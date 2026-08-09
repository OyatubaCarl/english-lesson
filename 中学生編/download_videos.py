#!/usr/bin/env python3
"""中学生編（L1〜L45）のレッスン動画を YouTube からダウンロードする。

- 対応表: 英語学習教材作成/youtube-map.json の "middle"（レッスン番号 → 動画ID。L4のみ2本）
- 出力:
    中学生編/videos/L{n}.mp4        … 動画（mp4・最良品質）
    中学生編/audio/L{n}.mp3         … 音声（動画から ffmpeg で抽出。タコビート譜面生成用）
    中学生編/videos/manifest.json   … レッスン→動画ID/タイトル/尺/ファイルパス
- 既にファイルがある分はスキップ（再実行安全）
"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # 英語学習教材作成/
MID  = Path(__file__).resolve().parent                 # 中学生編/
VID  = MID / "videos"
AUD  = MID / "audio"
VID.mkdir(parents=True, exist_ok=True)
AUD.mkdir(parents=True, exist_ok=True)

mapping = json.load(open(ROOT / "youtube-map.json", encoding="utf-8"))["middle"]

def entries():
    """[(key, lesson_no, video_id)] を返す。複数動画のレッスンは L4-1 / L4-2 のように連番。"""
    out = []
    for k in sorted(mapping, key=lambda x: int(x)):
        v = mapping[k]
        ids = v if isinstance(v, list) else [v]
        for i, vid in enumerate(ids):
            key = f"L{k}" if len(ids) == 1 else f"L{k}-{i+1}"
            out.append((key, int(k), vid))
    return out

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

def meta(vid):
    r = run(["yt-dlp", "--no-warnings", "--skip-download",
             "--print", "%(title)s\t%(duration)s", f"https://youtu.be/{vid}"])
    if r.returncode != 0:
        return None, None
    line = (r.stdout or "").strip().split("\n")[0]
    parts = line.split("\t")
    title = parts[0] if parts else ""
    dur = float(parts[1]) if len(parts) > 1 and parts[1] not in ("NA", "") else None
    return title, dur

def main():
    items = entries()
    print(f"対象: {len(items)} 本（{len(mapping)} レッスン）", flush=True)
    manifest, ok, fail = [], 0, 0
    for n, (key, lesson, vid) in enumerate(items, 1):
        mp4 = VID / f"{key}.mp4"
        mp3 = AUD / f"{key}.mp3"
        title, dur = (None, None)
        if not mp4.exists():
            r = run(["yt-dlp", "--no-warnings",
                     "-f", "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b",
                     "--merge-output-format", "mp4",
                     "-o", str(mp4), f"https://youtu.be/{vid}"])
            if r.returncode != 0 or not mp4.exists():
                print(f"[{n}/{len(items)}] ❌ {key} ({vid}) 動画DL失敗: {(r.stderr or '')[-160:]}", flush=True)
                fail += 1
                continue
        # 音声抽出（動画から。再ダウンロードしない）
        if not mp3.exists():
            r = run(["ffmpeg", "-y", "-i", str(mp4), "-vn",
                     "-acodec", "libmp3lame", "-b:a", "128k", str(mp3)])
            if r.returncode != 0 or not mp3.exists():
                print(f"[{n}/{len(items)}] ⚠️ {key} 音声抽出失敗", flush=True)
        title, dur = meta(vid)
        manifest.append({"key": key, "lesson": lesson, "video_id": vid,
                         "url": f"https://youtu.be/{vid}", "title": title, "duration": dur,
                         "video": f"videos/{key}.mp4", "audio": f"audio/{key}.mp3",
                         "video_bytes": mp4.stat().st_size if mp4.exists() else 0,
                         "audio_bytes": mp3.stat().st_size if mp3.exists() else 0})
        ok += 1
        print(f"[{n}/{len(items)}] ✅ {key} {vid} {mp4.stat().st_size//1024}KB / mp3 {(mp3.stat().st_size//1024) if mp3.exists() else 0}KB  {title}", flush=True)

    (VID / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n完了: 成功 {ok} / 失敗 {fail}  → {VID/'manifest.json'}", flush=True)

if __name__ == "__main__":
    sys.exit(main())
