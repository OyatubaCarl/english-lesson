"""WordTacosアプリ用 英語音声生成 (piper-tts / lessac)
使い方: python3 gen_app_audio_en_piper.py stage1_quizzes_clean.json stage1
出力: app_audio/{stage}_en/{word}.mp3 + manifest_en.json
"""
import json, subprocess, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import piper_synth  # noqa: E402  共通の合成パイプライン（先頭無音・歯擦音・同音異義語）

def synth(word: str, out_mp3: Path) -> bool:
    """単語を合成（piper_synth の共通パイプライン）。

    先頭無音120ms（再生開始で /s/ が飲まれるのを防ぐ）＋ 歯擦音の候補選定
    ＋ 同音異義語の音素上書き。詳細は ../piper_synth.py を参照。
    """
    if out_mp3.exists() and out_mp3.stat().st_size > 500:
        return True
    return piper_synth.synth_word(word, out_mp3)

def main(quiz_json: str, stage_id: str):
    data = json.loads(open(quiz_json, encoding="utf-8").read())
    quizzes = data["quizzes"]
    out_dir = Path(__file__).parent / "app_audio" / f"{stage_id}_en"
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / "manifest_en.json"
    manifest = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    total = len(quizzes)
    t0 = time.time()
    ok = ng = skip = 0
    for i, q in enumerate(quizzes, 1):
        qid = q["id"]
        word = q["word"]
        # ファイル名は安全に(スラッシュや空白を_に)
        safe = word.replace("/", "_").replace(" ", "_").replace(".", "_")
        mp3 = out_dir / f"{safe}.mp3"
        if mp3.exists() and mp3.stat().st_size > 500:
            manifest[qid] = {"word": word, "file": mp3.name}
            skip += 1; continue
        if synth(word, mp3):
            manifest[qid] = {"word": word, "file": mp3.name, "voice": "lessac"}
            ok += 1
        else:
            ng += 1
        if i % 20 == 0:
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
            elapsed = time.time() - t0
            eta = (total - i) * elapsed / max(i, 1)
            print(f"  進捗 {i}/{total} ok={ok} ng={ng} skip={skip} / {elapsed:.0f}s (残り{eta:.0f}s)")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✅ 完了: {ok}生成 + {skip}既存 / 失敗{ng} / {time.time()-t0:.0f}s")
    print(f"   → {out_dir}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: gen_app_audio_en_piper.py <quiz.json> <stage_id>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
