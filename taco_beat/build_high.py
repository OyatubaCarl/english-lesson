#!/usr/bin/env python3
"""高校生編（高1 L1〜L45）のレッスン動画から、タコビートの曲・譜面・背景動画を作る。

対応表は taco_course_mockup/high_lessons.json の `video`（YouTube ID）をそのまま使う。
高校は 160 課あるが、動画があるのは序盤の 45 課だけ。動画のない課はビート具材を
「レッスン動画＋本文リスニング」で代替する（アプリ側が判断する）。

出力（曲ID = h<N>）:
    taco_beat/songs/h<N>.mp3     … 96kbps mp3（make_chart.py が作る）
    taco_beat/charts/h<N>.js     … 譜面（同上）
    taco_beat/videos/h<N>.mp4    … 360p・ミュート・低ビットレート（同一オリジン配信）
    taco_beat/songlist.js        … h<N> を追記

既にあるものはスキップ（再実行安全）。

usage:
    python3 build_high.py            # 全部
    python3 build_high.py 1 2 3      # レッスン番号を指定
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent                 # taco_beat/
PROJ = ROOT.parent                                     # 英語学習教材作成/
VENV_PY = PROJ / "venv" / "bin" / "python3"            # whisper/torch/torchaudio 入り
LESSONS = PROJ / "taco_course_mockup" / "high_lessons.json"

SONGS = ROOT / "songs"
CHARTS = ROOT / "charts"
VIDEOS = ROOT / "videos"
TMP = Path("/tmp/tb_high")
for d in (SONGS, CHARTS, VIDEOS, TMP):
    d.mkdir(parents=True, exist_ok=True)

MAX_LESSON = 45      # 動画があるのはここまで


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True)


def targets(only: list[int]) -> list[tuple[int, str, str]]:
    """[(レッスン番号, YouTube ID, タイトル)]"""
    data = json.load(open(LESSONS, encoding="utf-8"))
    out = []
    for x in data:
        n = int(x.get("b", 0))
        vid = (x.get("video") or "").strip()
        if not vid or n < 1 or n > MAX_LESSON:
            continue
        if only and n not in only:
            continue
        out.append((n, vid, (x.get("title") or f"Lesson {n}").strip()))
    return sorted(out)


def fetch_audio(vid: str, dst: Path) -> bool:
    """譜面生成用の音源。可逆でなくてよいが、Whisper に通すので 44.1kHz mp3 にしておく。"""
    if dst.exists():
        return True
    r = run(["yt-dlp", "--no-warnings", "-f", "bestaudio",
             "-x", "--audio-format", "mp3", "--audio-quality", "0",
             "-o", str(dst.with_suffix("")) + ".%(ext)s",
             f"https://youtu.be/{vid}"])
    if not dst.exists():
        print(f"    ✗ 音声DL失敗: {(r.stderr or '').strip()[-160:]}")
        return False
    return True


def build_video(vid: str, dst: Path) -> bool:
    """背景動画。360p・音声なし・低ビットレート（同一オリジンで配信＝広告なし・精密同期）。"""
    if dst.exists():
        return True
    src = TMP / f"src_{vid}.mp4"
    if not src.exists():
        r = run(["yt-dlp", "--no-warnings",
                 "-f", "bestvideo[height<=480][ext=mp4]/best[height<=480][ext=mp4]/best",
                 "-o", str(src), f"https://youtu.be/{vid}"])
        if not src.exists():
            print(f"    ✗ 動画DL失敗: {(r.stderr or '').strip()[-160:]}")
            return False
    r = run(["ffmpeg", "-y", "-i", str(src), "-an",
             "-vf", "scale=-2:360", "-c:v", "libx264", "-preset", "slow",
             "-crf", "30", "-movflags", "+faststart", str(dst)])
    if not dst.exists():
        print(f"    ✗ 変換失敗: {(r.stderr or '').strip()[-160:]}")
        return False
    src.unlink(missing_ok=True)
    return True


def build_chart(n: int, mp3: Path) -> bool:
    """make_chart.py（Whisper + 強制アライメント）。--inject はしない（index.html は songlist で引く）。"""
    sid = f"h{n}"
    if (CHARTS / f"{sid}.js").exists() and (SONGS / f"{sid}.mp3").exists():
        return True
    r = subprocess.run([str(VENV_PY), str(ROOT / "make_chart.py"), str(mp3),
                        "--id", sid, "--outdir", str(ROOT)],
                       capture_output=True, text=True)
    ok = (CHARTS / f"{sid}.js").exists() and (SONGS / f"{sid}.mp3").exists()
    if not ok:
        print(f"    ✗ 譜面生成失敗:\n{(r.stdout or '')[-400:]}\n{(r.stderr or '')[-400:]}")
    return ok


def short_title(t: str) -> str:
    """'高1 L7 現在形の多様な用法「日々のリズム」' → 'L7 日々のリズム'（曲名は短く）。"""
    m = re.search(r"L(\d+)", t)
    num = f"L{m.group(1)}" if m else ""
    q = re.search(r"「([^」]+)」", t)
    name = q.group(1) if q else re.sub(r"^高\d\s*L\d+\s*", "", t)
    return f"{num} {name}".strip()


def update_songlist(made: list[tuple[int, str]]) -> None:
    """songlist.js に h<N> を追記（既存の h<N> は上書き。b/m の順は保つ）。"""
    p = ROOT / "songlist.js"
    s = p.read_text(encoding="utf-8")
    body = re.search(r"const SONGLIST=\[(.*)\];", s, re.S).group(1)
    entries = re.findall(r"\{id:'([^']+)',title:'([^']*)'\}", body)
    table = {i: t for i, t in entries}
    order = [i for i, _ in entries]
    for n, title in made:
        sid = f"h{n}"
        if sid not in table:
            order.append(sid)
        table[sid] = title.replace("'", "’")
    out = ",".join(f"{{id:'{i}',title:'{table[i]}'}}" for i in order)
    p.write_text(f"const SONGLIST=[{out}];\n", encoding="utf-8")
    print(f"songlist.js 更新: 全 {len(order)} 曲")


def main() -> int:
    only = [int(a) for a in sys.argv[1:] if a.isdigit()]
    items = targets(only)
    print(f"対象: {len(items)} 課（高1 L1〜L{MAX_LESSON}）", flush=True)

    made, failed = [], []
    for n, vid, title in items:
        sid = f"h{n}"
        done = (CHARTS / f"{sid}.js").exists() and (SONGS / f"{sid}.mp3").exists() and (VIDEOS / f"{sid}.mp4").exists()
        if done:
            print(f"[{sid}] スキップ（既にある）", flush=True)
            made.append((n, short_title(title)))
            continue

        print(f"[{sid}] {title}  ({vid})", flush=True)
        mp3 = TMP / f"{sid}.mp3"
        if not fetch_audio(vid, mp3):
            failed.append(sid); continue
        if not build_chart(n, mp3):
            failed.append(sid); continue
        if not build_video(vid, VIDEOS / f"{sid}.mp4"):
            failed.append(sid); continue

        made.append((n, short_title(title)))
        print(f"    ✓ 譜面・曲・動画  {(VIDEOS / f'{sid}.mp4').stat().st_size / 1e6:.1f}MB", flush=True)

    if made:
        update_songlist(sorted(made))
    print(f"\n完了: {len(made)} 曲 / 失敗: {len(failed)}" + (f" → {failed}" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
