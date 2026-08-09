#!/usr/bin/env python3
"""WordTacos v2 動画ビルダー — 白地クイズカード中心 + テロップ構成。

構成: [裏技フック] → [文読み+コメント誘導] → [3-2-1カウント] → [正解] → [WordTacos CM]
音声: 日本語=VoicePeak / 英単語=Piper(lessac) を繋いで文を読む。
サムネ: 序盤〜カウントまで同じカードなので、先頭フレーム=クリーンなクイズ画像。

usage:
    python3 build_wordtacos_v2.py            # 既定(obfuscate)を試作
    python3 build_wordtacos_v2.py quiz.json  # {word,prefix,suffix,choices,correct,meaning}
"""
from __future__ import annotations
import json, os, shutil, subprocess, sys, time, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
WORK = ROOT / "_v2_work"; WORK.mkdir(exist_ok=True)
CARD_URL = f"file://{ROOT}/quiz_card_v2.html"
# 末尾は旧・約10秒のナレ付きCM(cm_card_v2.html)ではなく、2.6秒の無音ブランドカードに差し替え。
# 正解の直後で終わってショートがループしやすくなる(2026-07-10 ユーザー決定)。
CM_URL = f"file://{ROOT}/cm_card_short_v2.html"
RENDER_JS = ROOT / "render_card_v2.js"
VP = "/Applications/voicepeak.app/Contents/MacOS/voicepeak"
VP_NARRATOR = "Japanese Female 1"
PIPER = "/Users/masaki/Library/Python/3.9/bin/piper"
PIPER_VOICE = ROOT.parent / "vocab_sources/piper_test/voices/lessac.onnx"
# 既定BGM = 歌付きタコスソング(¡Viva!タコス)。ダッキング(V2_DUCK既定ON)でナレ中だけ自動で下がり、
# 無音区間は歌が前に出る → 視聴継続を稼ぎつつ言葉もクリア(2026-07-03 ユーザー決定)。
# V2_BGM でアプリ theme.mp3 等に差し替え可、V2_BGM_VOL/V2_DUCK=0 で調整。
_SONG = "/Users/masaki/Documents/ClaudeCode/FunnicsIsland/songs/21_tacos_fiesta_dance/audio/tacos_fiesta_suno_SX3pVWTGGFxEsIHW.mp3"
BGM = Path(os.environ.get("V2_BGM", _SONG))
BGM_VOL = os.environ.get("V2_BGM_VOL", "0.30")
SFX_CORRECT = ROOT.parent / "vocab_sources/app_assets/sounds/correct.mp3"  # 正解SFX
FONT = "Hiragino Sans"
W, H, FPS = 1080, 1920, 30
# 背景イラスト(bg_v3/bg1..8.png)。存在すれば「角丸カード+背景+軽いズーム」構成に(静止画感の解消)。
# 無ければ従来の白カード全面(後方互換)。V2_NO_BG=1 で強制オフ。
BG_DIR = ROOT / "assets" / "bg_v3"
def pick_bg(word: str) -> Path | None:
    if os.environ.get("V2_NO_BG"):
        return None
    import hashlib
    n = int(hashlib.md5(word.encode()).hexdigest(), 16) % 8 + 1
    p = BG_DIR / f"bg{n}.png"
    return p if (p.exists() and p.stat().st_size > 50_000) else None
# CMナレは全動画で固定テキスト → 1回だけ生成してキャッシュ再利用(速度向上+ハング源削減)。
CM_NARRATION = "日本語に包んで、やさしく英単語。ワードタコスで、毎日一問。ブラウザだけ、完全無料。"
CM_CACHE = WORK / "_cm_cache.wav"
VP_TIMEOUT = 60  # VoicePeak 1呼び出しの上限秒。超過=ハングとみなし掃除→リトライ

# 既定クイズ (obfuscate)
DEFAULT_QUIZ = {
    "word": "obfuscate",
    "prefix": "政治家の答弁は問題を",
    "suffix": "していて、誰も真相が分からなくなった。",
    "choices": ["明確に示す", "わざと曖昧にする", "誇張する", "撤回する"],
    "correct": 1,
    "meaning": "わざと曖昧にする",
}


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def render_card(quiz: dict, reveal: bool, out: Path, inset: bool = False):
    sentence = f"{quiz['prefix']}<{quiz['word']}>{quiz['suffix']}"
    params = {
        "sentence": sentence, "word": quiz["word"],
        "choices": "|".join(quiz["choices"]), "correct": str(quiz["correct"]),
        "reveal": "1" if reveal else "0",
    }
    if inset:
        params["inset"] = "1"   # 角丸カード+透過余白(背景合成用)
    if quiz.get("tag"):
        params["tag"] = quiz["tag"]
    qs = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    run(["node", str(RENDER_JS), f"{CARD_URL}?{qs}", str(out)])


def composite_bg(card: Path, bg: Path, out: Path):
    """透過余白付きカードPNGを背景イラストに重ねる。"""
    run(["ffmpeg", "-y", "-i", str(bg), "-i", str(card),
         "-filter_complex", f"[0:v]scale={W}:{H},format=rgba[b];[b][1:v]overlay=0:0:format=auto",
         "-frames:v", "1", str(out)])


def render_cm(out: Path):
    run(["node", str(RENDER_JS), CM_URL, str(out)])


def vp(text: str, out: Path):
    # VoicePeakは稀にSIGSEGVで落ちる/ハングして固まるためタイムアウト付きリトライ。
    # timeout超過時は残プロセス(voicepeak -s ...)を掃除してからリトライ。連続実行を避けるため軽くsleep。
    out.unlink(missing_ok=True)
    for attempt in range(5):
        try:
            run([VP, "-s", text, "-n", VP_NARRATOR, "-o", str(out), "--speed", "110"],
                timeout=VP_TIMEOUT)
        except subprocess.TimeoutExpired:
            # ハング: subprocess側でSIGKILL済みだが取りこぼしを pkill で確実に掃除
            subprocess.run(["pkill", "-f", "voicepeak -s"], capture_output=True)
            time.sleep(1.5)
        except subprocess.CalledProcessError:
            pass
        if out.exists() and out.stat().st_size > 2000:
            return
        time.sleep(1.5)
    raise RuntimeError(f"VoicePeak failed after retries: {text[:30]}")


def vp_cm(out: Path):
    # CMナレは固定テキスト。キャッシュがあればコピー再利用、無ければ1回だけ生成してキャッシュ。
    if not (CM_CACHE.exists() and CM_CACHE.stat().st_size > 2000):
        vp(CM_NARRATION, CM_CACHE)
    shutil.copyfile(CM_CACHE, out)


def piper(word: str, out: Path):
    subprocess.run([PIPER, "-m", str(PIPER_VOICE), "-f", str(out)],
                   input=word.encode(), check=True, capture_output=True)


def dur(path: Path) -> float:
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", str(path)])
    return float(r.stdout.strip())


def silence(seconds: float, out: Path):
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
         "-t", f"{seconds:.3f}", str(out)])


def concat_audio(parts: list[Path], out: Path):
    inputs = []
    for p in parts:
        inputs += ["-i", str(p)]
    n = len(parts)
    filt = "".join(f"[{i}:a]aresample=44100,aformat=channel_layouts=stereo[a{i}];" for i in range(n))
    filt += "".join(f"[a{i}]" for i in range(n)) + f"concat=n={n}:v=0:a=1[out]"
    run(["ffmpeg", "-y", *inputs, "-filter_complex", filt, "-map", "[out]", str(out)])


def img_clip(img: Path, seconds: float, out: Path, zoom: bool = False):
    if zoom:
        # Ken Burns: 1.5倍解像度に上げてから中心へゆっくりズーム(≈1.0→1.12/15s)。静止画感を消す
        frames = max(1, int(seconds * FPS))
        vf = (f"scale={int(W*1.5)}:-1,"
              f"zoompan=z='1+0.00028*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
              f":d={frames}:s={W}x{H}:fps={FPS},format=yuv420p")
        run(["ffmpeg", "-y", "-i", str(img), "-vf", vf, "-t", f"{seconds:.3f}",
             "-c:v", "libx264", "-pix_fmt", "yuv420p", str(out)])
        return
    run(["ffmpeg", "-y", "-loop", "1", "-i", str(img), "-t", f"{seconds:.3f}",
         "-r", str(FPS), "-vf", f"scale={W}:{H},format=yuv420p", "-c:v", "libx264",
         "-pix_fmt", "yuv420p", str(out)])


def concat_video(clips: list[Path], out: Path):
    lst = WORK / "concat.txt"
    lst.write_text("".join(f"file '{c}'\n" for c in clips))
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-c", "copy", str(out)])


# ---------- ASS テロップ ----------
def ts(s: float) -> str:
    h = int(s // 3600); m = int((s % 3600) // 60); sec = s - h * 3600 - m * 60
    return f"{h}:{m:02d}:{sec:05.2f}"


def ass(segments, total):
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Hook,{FONT},76,&H00FFFFFF,&H00FFFFFF,&H001B14D6,&H64000000,-1,0,0,0,100,100,1,0,1,7,3,8,60,60,60,1
Style: CTA,{FONT},58,&H0020140B,&H0020140B,&H00FFFFFF,&H64000000,-1,0,0,0,100,100,1,0,1,5,2,2,60,60,90,1
Style: Count,{FONT},300,&H001B14D6,&H001B14D6,&H00FFFFFF,&H64000000,-1,0,0,0,100,100,1,0,1,10,6,5,0,0,0,1
Style: Correct,{FONT},120,&H00528A2F,&H00528A2F,&H00FFFFFF,&H64000000,-1,0,0,0,100,100,1,0,1,9,5,8,0,0,120,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [head]
    for s in segments:
        lines.append(f"Dialogue: 0,{ts(s['start'])},{ts(s['end'])},{s['style']},,0,0,0,,{s['text']}")
    p = WORK / "telop.ass"
    p.write_text("\n".join(lines), encoding="utf-8")
    return p


def build(quiz: dict, out_path: Path):
    w = quiz["word"]
    print(f"=== build v2: {w} ===")
    a = WORK
    card_q = a / "card_q.png"; card_a = a / "card_a.png"; card_cm = a / "card_cm.png"
    # V2_SKIP_GEN=1 かつ中間ファイルが揃っていれば カード/音声/base を再利用(BGM差し替えA/B等)
    skip = bool(os.environ.get("V2_SKIP_GEN")) and (a/"voice.wav").exists() and (a/"base.mp4").exists()
    bg = pick_bg(w)   # 背景があれば角丸カード+ズーム構成
    if skip:
        print("  ⏩ 中間ファイル再利用 (cards/audio/base をスキップ)")
    else:
        # 1) カード描画（背景合成時は inset=角丸+透過余白で描き、背景に重ねる）
        render_card(quiz, False, card_q, inset=bool(bg))
        render_card(quiz, True, card_a, inset=bool(bg))
        if bg:
            composite_bg(card_q, bg, a / "card_q_bg.png"); card_q = a / "card_q_bg.png"
            composite_bg(card_a, bg, a / "card_a_bg.png"); card_a = a / "card_a_bg.png"
        render_cm(card_cm)
        print(f"  ✓ cards{'(+bg '+bg.name+')' if bg else ''}")
        # 2) 音声生成 (VoicePeak=日本語, Piper=英単語)
        piper(w, a / "w.wav")
        vp(quiz["prefix"], a / "b_pre.wav")
        vp(quiz["suffix"], a / "b_suf.wav")
        vp("の意味は？", a / "q_suf.wav")
        vp(f"正解は、{quiz['meaning']}。", a / "ans.wav")
        # 末尾CMは無音ブランドカードに変更 → CMナレ(vp_cm)は生成しない
        concat_audio([a / "b_pre.wav", a / "w.wav", a / "b_suf.wav"], a / "narr_body.wav")
        concat_audio([a / "w.wav", a / "q_suf.wav"], a / "narr_quiz.wav")
        print("  ✓ audio (VoicePeak+Piper)")

    # 3) タイムライン (音声長から算出)
    INTRO = 1.9
    body = dur(a / "narr_body.wav"); BODY = body + 0.6
    quizd = dur(a / "narr_quiz.wav"); QUIZ = quizd + 0.5
    COUNT = 3.2
    ansd = dur(a / "ans.wav"); REVEAL = ansd + 0.9
    CM = float(os.environ.get("V2_CM_SEC", "2.6"))  # 末尾ブランドカード(無音・短縮)。V2_CM_SEC で調整可
    t_intro, t_body, t_quiz, t_count, t_reveal, t_cm = 0, INTRO, INTRO+BODY, INTRO+BODY+QUIZ, INTRO+BODY+QUIZ+COUNT, INTRO+BODY+QUIZ+COUNT+REVEAL
    total = t_cm + CM
    card_secs = INTRO + BODY + QUIZ + COUNT

    if not skip:
        # 4) 音声トラック(無音で整列 → 連結)
        silence(INTRO, a / "s_intro.wav")
        silence(0.6, a / "s_b.wav"); silence(0.5, a / "s_q.wav")
        silence(COUNT, a / "s_count.wav"); silence(0.9, a / "s_ans.wav"); silence(CM, a / "s_cm.wav")
        # 末尾CMは無音(BGMのみ) → cm.wav を挟まず s_cm.wav(=CM尺の無音)で締める
        concat_audio([a/"s_intro.wav", a/"narr_body.wav", a/"s_b.wav", a/"narr_quiz.wav", a/"s_q.wav",
                      a/"s_count.wav", a/"ans.wav", a/"s_ans.wav", a/"s_cm.wav"], a/"voice.wav")
        # 5) ベース動画(画像セグメント連結)。背景合成時は問題/正解に軽いズーム(静止画感の解消)
        img_clip(card_q, card_secs, a / "clip_card.mp4", zoom=bool(bg))
        img_clip(card_a, REVEAL, a / "clip_ans.mp4", zoom=bool(bg))
        img_clip(card_cm, CM, a / "clip_cm.mp4")
        concat_video([a/"clip_card.mp4", a/"clip_ans.mp4", a/"clip_cm.mp4"], a/"base.mp4")
    print(f"  ✓ base video ({total:.1f}s)")

    # 6) テロップ
    # 注: libass は絵文字を描画できない(豆腐化)ため、テロップは絵文字なしのテキストのみ。
    segs = [
        {"start": 0.1, "end": t_quiz, "style": "Hook", "text": "超・難単語を覚える裏技"},
        {"start": t_body+0.3, "end": t_count, "style": "CTA", "text": "答えがわかったら コメントで！"},
    ]
    for i, n in enumerate(["3", "2", "1"]):
        s = t_count + i * ((COUNT-0.2) / 3)
        segs.append({"start": s, "end": s + (COUNT-0.2)/3, "style": "Count",
                     "text": "{\\pos(540,900)\\fad(120,150)\\t(\\fscx115\\fscy115)}" + n})
    segs.append({"start": t_reveal+0.05, "end": t_cm, "style": "Correct",
                 "text": "{\\pos(540,150)\\fad(150,150)}正解！"})
    ass_path = ass(segs, total)

    # 7) 合成: base + ASS + (voice + BGM + 正解SFX)。V2_DUCK=1 でナレ中だけBGMを自動ダッキング
    ass_esc = str(ass_path).replace(":", "\\:")
    sfx_delay = int(t_reveal * 1000)
    duck = os.environ.get("V2_DUCK", "1") != "0"   # 既定ON。V2_DUCK=0 で無効
    fc = f"[0:v]ass={ass_esc}[v];"
    fc += f"[2:a]aloop=loop=-1:size=2e9,atrim=0:{total:.2f},volume={BGM_VOL},afade=t=out:st={total-1.2:.2f}:d=1.2[bgmraw];"
    fc += f"[3:a]adelay={sfx_delay}|{sfx_delay},volume=0.55[sfx];"
    if duck:
        # ナレ(vo)をサイドチェーンにBGMを圧縮(=声の時だけ音楽が下がる)
        fc += "[1:a]volume=1.3,asplit=2[vo][vosc];"
        fc += "[bgmraw][vosc]sidechaincompress=threshold=0.028:ratio=9:attack=12:release=320[bgm];"
    else:
        fc += "[1:a]volume=1.2[vo];[bgmraw]anull[bgm];"
    fc += "[vo][bgm][sfx]amix=inputs=3:duration=first:dropout_transition=0:normalize=0,alimiter=limit=0.95[a]"
    run(["ffmpeg", "-y", "-i", str(a/"base.mp4"), "-i", str(a/"voice.wav"),
         "-i", str(BGM), "-i", str(SFX_CORRECT),
         "-filter_complex", fc,
         "-map", "[v]", "-map", "[a]", "-t", f"{total:.2f}",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
         "-c:a", "aac", "-b:a", "192k", "-shortest", str(out_path)])
    print(f"  ✓ 完成: {out_path.name} ({total:.1f}s)")


def main():
    quiz = DEFAULT_QUIZ
    if len(sys.argv) > 1:
        quiz = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    tag = os.environ.get("V2_TAG", "")   # 出力名サフィックス(A/B比較用)
    out = ROOT / f"wordtacos_v2_{quiz['word']}{tag}.mp4"
    build(quiz, out)


if __name__ == "__main__":
    main()
