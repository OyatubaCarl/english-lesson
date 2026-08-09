"""譜面のノーツ位置を、FunnicsIsland 側の歌詞ベース単語タイミングで作り直す。

背景（2026-07-10）:
`make_chart.py` の Whisper は `condition_on_previous_text` を切っていないため、
B 系の歌が各行を 2 回繰り返す構造の **2 回目（コーラス）を丸ごと落とす**。
その結果、既存の譜面はコーラス部分にノーツが無い（B3 は 95 語しか無い）。

FunnicsIsland の字幕パイプライン
(`FunnicsIsland/scripts/40_beginner_neural_word_alignment.py`) は、この問題を
「Whisper には行の繰り返し回数だけを判定させ、強制アライメントは**歌詞の語**に対して行う」
という設計で解決済みで、`alignment_neural/b<N>_words.json` に全歌詞語の時刻を持っている。
そこで **単語列だけをそちらに差し替え**、BPM 推定・ホールド・🫓フィラー・出力は
`make_chart.py` の実装をそのまま再利用する（パラメータを二重に持たない）。

使い方:
    python3 rebuild_charts_from_lyrics.py --dry-run   # 旧譜面との差分だけ見る
    python3 rebuild_charts_from_lyrics.py             # charts/b<N>.js を書き換える
    python3 rebuild_charts_from_lyrics.py b3 --dry-run
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_chart as mc  # noqa: E402

FUNNICS = Path("/Users/masaki/Documents/ClaudeCode/FunnicsIsland")
CHARTS = HERE / "charts"
CACHE = HERE / ".cache"
SONGS = HERE / "songs"

MIN_NOTE_GAP = 0.001   # 同時刻ノーツを避けるための最小差
MERGE_WINDOW = 0.15    # 旧譜面の語がこの秒数以内に無ければ「歌詞に無い実唱語」とみなして残す


def words_json(song_id: str) -> Path:
    hits = sorted(glob.glob(str(FUNNICS / "songs" / f"*_beginner_tom_{song_id}")))
    if len(hits) != 1:
        sys.exit(f"{song_id}: 曲ディレクトリが一意に決まりません -> {hits}")
    p = Path(hits[0]) / "alignment_neural" / f"{song_id}_words.json"
    if not p.exists():
        sys.exit(f"{song_id}: {p} が無い。先に FunnicsIsland の 40_ を流すこと")
    return p


def load_words(song_id: str) -> list[tuple[str, float]]:
    """歌詞ベースの単語タイミングを (譜面表記, start) 列にする。

    綴りは make_chart.display_word を通す。譜面の word はノーツ上に出るので、
    句読点を落として既存譜面と同じ表記（Tom / Funnics / Island …）に揃える。
    """
    data = json.loads(words_json(song_id).read_text(encoding="utf-8"))
    out: list[tuple[str, float]] = []
    for line in data["lines"]:
        for w in line["words"]:
            if not w.get("timed"):
                continue
            disp = mc.display_word(w["tok"])
            if disp:
                out.append((disp, float(w["start"])))
    out.sort(key=lambda x: x[1])

    # 丸めで同時刻になった語をわずかにずらす（ノーツの重なり防止）
    for i in range(1, len(out)):
        if out[i][1] <= out[i - 1][1]:
            out[i] = (out[i][0], round(out[i - 1][1] + MIN_NOTE_GAP, 3))
    return out


def old_chart(song_id: str) -> tuple[list, float] | None:
    p = CHARTS / f"{song_id}.js"
    if not p.exists():
        return None
    s = p.read_text(encoding="utf-8")
    rows = re.findall(r'\[([\d.]+),"([^"]*)",(\d),([\d.]+)\]', s)
    bpm = re.search(r"const SONG_BPM=([\d.]+);", s)
    return [(float(a), b, int(c), float(d)) for a, b, c, d in rows], float(bpm.group(1))


def extra_sung_words(song_id: str, new_times: list[float]) -> list[tuple[str, float]]:
    """旧譜面にあって歌詞に無い語を拾う。

    音ゲーは字幕と違って**実際に歌われた音**にノーツを置くのが正しい
    （TASK-20260707-001 の設計判断）。歌詞ベースの単語列だけだと、
    B1 の "Tom, Tom" の 2 つ目や、B8 の "da da"・B16 の "hee hee" のような
    スキャットが落ちて叩ける音が減ってしまう。
    新旧とも同じ強制アライメントなので、対応する語の時刻差は中央値 0ms・90%tile 1ms。
    ±MERGE_WINDOW に相手がいなければ「歌詞に無い実唱語」と判断して残す。
    """
    prev = old_chart(song_id)
    if not prev:
        return []
    return [(w, t) for t, w, _k, _he in prev[0]
            if w and all(abs(t - x) > MERGE_WINDOW for x in new_times)]


def rebuild(song_id: str, dry_run: bool, merge: bool) -> dict:
    wav = CACHE / song_id / f"{song_id}_16k.wav"
    if not wav.exists():
        mp3 = SONGS / f"{song_id}.mp3"
        if not mp3.exists():
            sys.exit(f"{song_id}: {mp3} も {wav} も無い")
        wav.parent.mkdir(parents=True, exist_ok=True)
        mc.make_wav16k(mp3, wav)

    words = load_words(song_id)
    n_extra = 0
    if merge:
        extra = extra_sung_words(song_id, [t for _w, t in words])
        n_extra = len(extra)
        words = sorted(words + extra, key=lambda x: x[1])
        for i in range(1, len(words)):
            if words[i][1] <= words[i - 1][1]:
                words[i] = (words[i][0], round(words[i - 1][1] + MIN_NOTE_GAP, 3))

    flux, frame_t, _onsets = mc.onset_envelope(wav)
    bpm, phase = mc.estimate_bpm(flux, frame_t)
    duration = float(frame_t[-1]) + mc.N_FFT / 2 / mc.SR
    beat = mc.build_beat(words, bpm, phase, duration)

    prev = old_chart(song_id)
    stat = {
        "song": song_id,
        "new_words": len(words),
        "extra": n_extra,
        "new_notes": len(beat),
        "new_holds": sum(1 for r in beat if r[3]),
        "new_fillers": sum(1 for r in beat if not r[1]),
        "new_bpm": bpm,
        "old_words": sum(1 for r in prev[0] if r[1]) if prev else 0,
        "old_notes": len(prev[0]) if prev else 0,
        "old_bpm": prev[1] if prev else 0.0,
    }
    if not dry_run:
        CHARTS.mkdir(exist_ok=True)
        (CHARTS / f"{song_id}.js").write_text(mc.render_js(beat, bpm), encoding="utf-8")
    return stat


def inject_inline(song_id: str) -> None:
    """index.html に埋め込まれた b1 の譜面を差し替える。

    ゲームは `if(id===INLINE_ID){ BEAT=INLINE_BEAT; }` で b1 だけインライン譜面を使う
    （file:// やオフラインでも動くように）。charts/b1.js を更新しても、ここを直さないと
    b1 は古い譜面のまま鳴る。make_chart.inject() は `const BEAT=` を探すが、
    index.html の実体は `let BEAT=` なのでそのままでは一致しない。
    """
    idx = HERE / "index.html"
    js = (CHARTS / f"{song_id}.js").read_text(encoding="utf-8")
    beat = re.search(r"const BEAT=(\[.*?\]);", js, re.S).group(1)
    bpm = re.search(r"const SONG_BPM=([\d.]+);", js).group(1)

    html = idx.read_text(encoding="utf-8")
    new_html, n = re.subn(
        r"let BEAT=\[.*?\];\s*\nlet SONG_BPM=[\d.]+;",
        f"let BEAT={beat};\nlet SONG_BPM={bpm};",
        html, count=1, flags=re.S,
    )
    if n != 1:
        sys.exit("index.html のインライン譜面が見つかりませんでした（形式が変わった？）")
    idx.write_text(new_html, encoding="utf-8")
    print(f"index.html のインライン譜面を {song_id} で更新")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("songs", nargs="*", help="例: b1 b3（省略時は b1〜b20）")
    ap.add_argument("--dry-run", action="store_true", help="書き換えず差分だけ表示")
    ap.add_argument("--no-merge", action="store_true",
                    help="旧譜面にしか無い実唱語（スキャット等）を引き継がない")
    ap.add_argument("--inject", action="store_true",
                    help="index.html のインライン譜面(b1)も更新する")
    args = ap.parse_args()
    songs = args.songs or [f"b{i}" for i in range(1, 21)]

    rows = [rebuild(s, args.dry_run, merge=not args.no_merge) for s in songs]

    print("\n曲    単語 旧→新  (歌詞外)  ノーツ 旧→新   hold  🫓   BPM 旧→新")
    tot_o = tot_n = tot_e = 0
    for r in rows:
        tot_o += r["old_words"]
        tot_n += r["new_words"]
        tot_e += r["extra"]
        bpm_mark = "" if abs(r["new_bpm"] - r["old_bpm"]) < 0.01 else "  ⚠BPM変化"
        print(f"  {r['song']:>4} {r['old_words']:>4} -> {r['new_words']:>4}  {r['extra']:>4}"
              f"    {r['old_notes']:>4} -> {r['new_notes']:>4}"
              f"   {r['new_holds']:>3}  {r['new_fillers']:>3}"
              f"   {r['old_bpm']:>6.2f} -> {r['new_bpm']:>6.2f}{bpm_mark}")
    print(f"  合計 {tot_o:>4} -> {tot_n:>4}  {tot_e:>4}   ({tot_n - tot_o:+d} 語)")
    if args.dry_run:
        print("\n--dry-run のため charts/ は書き換えていません")
    elif args.inject:
        inject_inline("b1")


if __name__ == "__main__":
    main()
