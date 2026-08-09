#!/usr/bin/env python3
"""レッスン動画を YouTube から取得し、タコビート用に 360p・ミュート・低ビットレートの mp4 に。

- 出力: taco_beat/videos/b<N>.mp4（同一オリジンで配信＝広告なし・高速・精密同期）
- 絵本アニメは動きが穏やかで良く圧縮される（実測 360p muted ≈ 2MB/本）
- 既存 mp4 はスキップ（再開可能）

usage: python3 build_videos.py
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "videos"
OUT.mkdir(exist_ok=True)

# b<N> -> YouTube ID（lessons.json の video フィールドと一致）
VIDEOS = {
    1: "JG6OjXpvUiM", 2: "3fjUpy7dnLY", 3: "Nel8DoUk-XQ", 4: "ZabZz2GjH38",
    5: "IbthcUUN8Ww", 6: "vnxgjGSlSkY", 7: "6zDqphJdnpM", 8: "1dYrHcNMpiw",
    9: "JiMWgNb9mmw", 10: "oEApDAGtw0M", 11: "PKmYYUphi7o", 12: "N4i7CCaKLYk",
    13: "sxzrUpaT_LI", 14: "UtlFCJIFWPo", 15: "mSlr0lJNXRU", 16: "SeyB9cFN-5U",
    17: "vGm8YydxUdE", 18: "TGQ5OG6Hkng", 19: "MsZYJLY3n-o", 20: "nxaX_YktiXU",
}
TMP = Path("/tmp/tb_vid_src.mp4")


def build_one(n: int, vid: str) -> str:
    out = OUT / f"b{n}.mp4"
    if out.exists() and out.stat().st_size > 200_000:
        return "skip"
    TMP.unlink(missing_ok=True)
    Path(str(TMP) + ".part").unlink(missing_ok=True)
    dl = subprocess.run(
        ["yt-dlp", "-f", "bv*[height<=480]+ba/b[height<=480]",
         "--merge-output-format", "mp4", "-o", str(TMP),
         f"https://youtu.be/{vid}"],
        capture_output=True, text=True,
    )
    if not TMP.exists():
        return f"dl-fail: {dl.stderr[-200:]}"
    enc = subprocess.run(
        ["ffmpeg", "-y", "-i", str(TMP), "-an",
         "-vf", "scale=-2:360", "-c:v", "libx264", "-crf", "28",
         "-preset", "veryfast", "-movflags", "+faststart", str(out)],
        capture_output=True, text=True,
    )
    TMP.unlink(missing_ok=True)
    if enc.returncode != 0 or not out.exists():
        return f"enc-fail: {enc.stderr[-200:]}"
    return f"OK {out.stat().st_size//1024}KB"


def main() -> None:
    print(f"=== レッスン動画ビルド: {len(VIDEOS)}本 ===", flush=True)
    done = skipped = 0
    fails = []
    for n in sorted(VIDEOS):
        r = build_one(n, VIDEOS[n])
        print(f"  b{n}: {r}", flush=True)
        if r.startswith("OK"):
            done += 1
        elif r == "skip":
            skipped += 1
        else:
            fails.append(f"b{n}")
    total = sum(f.stat().st_size for f in OUT.glob("b*.mp4"))
    print(f"\n=== 完了: 生成{done} / スキップ{skipped} / 失敗{len(fails)} / 合計{total/1048576:.1f}MB ===", flush=True)
    if fails:
        print("失敗:", ", ".join(fails), flush=True)


if __name__ == "__main__":
    main()
