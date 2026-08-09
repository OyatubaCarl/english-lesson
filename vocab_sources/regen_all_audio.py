"""WordTacos の全単語音声を、修正済みパイプラインで作り直す。

修正内容（詳細は ../piper_synth.py）:
  - 先頭に120msの無音 … 再生開始で頭が飲まれて語頭の /s/ が消えるのを防ぐ
  - 歯擦音の候補選定 …… Piper がテキスト入力で語頭 /s/ をほぼ無音にする語（sport/stop/school 等）を
                        音素入力の候補と比較し、/s/ が最も明瞭なものを自動採用
  - 同音異義語の上書き … live(住む) など、単語単体だと誤読される語を音素指定で矯正
  - 高域シェルフ+リミッタ・96kbps … スマホのスピーカーでも /s/ が埋もれない

対象: app_audio/*_en/manifest_en.json に載っている全語（既存mp3は上書き）
使い方: python3 regen_all_audio.py [--dry]
"""
from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import piper_synth  # noqa: E402

BASE = Path(__file__).parent
AUDIO = BASE / "app_audio"
WORKERS = 6


def jobs() -> list[tuple[str, Path]]:
    """[(word, mp3path)] を全ステージから集める（重複ファイルは1回だけ）"""
    out: dict[Path, str] = {}
    for mf in sorted(AUDIO.glob("*_en/manifest_en.json")):
        data = json.loads(mf.read_text(encoding="utf-8"))
        for entry in data.values():
            word, fname = entry.get("word"), entry.get("file")
            if not word or not fname:
                continue
            out[mf.parent / fname] = word
    return [(w, p) for p, w in out.items()]


def main() -> int:
    dry = "--dry" in sys.argv
    js = jobs()
    print(f"対象: {len(js)} 語（{len(list(AUDIO.glob('*_en')))} ステージ）", flush=True)
    if dry:
        for w, p in js[:10]:
            print(f"  {w} -> {p.relative_to(BASE)}")
        return 0

    t0 = time.time()
    done = [0]
    fails: list[str] = []

    def work(job: tuple[str, Path]):
        word, mp3 = job
        mp3.parent.mkdir(parents=True, exist_ok=True)
        mp3.unlink(missing_ok=True)                 # 旧音声を消してから作り直す
        ok = False
        try:
            ok = piper_synth.synth_word(word, mp3)
        except Exception:
            ok = False
        if not ok:
            fails.append(word)
        done[0] += 1
        i = done[0]
        if i % 100 == 0 or i == len(js):
            el = time.time() - t0
            eta = (len(js) - i) * el / max(i, 1)
            print(f"  進捗 {i}/{len(js)} ng={len(fails)} / {el:.0f}s (残り{eta:.0f}s)", flush=True)

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        list(pool.map(work, js))

    print(f"✅ 完了: {len(js) - len(fails)}/{len(js)} 生成 / 失敗{len(fails)} / {time.time() - t0:.0f}s")
    if fails:
        print("⚠️ 失敗:", ", ".join(fails[:20]))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
