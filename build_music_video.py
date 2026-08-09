"""
「英語は歌で覚える」スライド動画ビルド。
- 各スライドのナレーションを Voicepeak で生成（チャンク分割→concat、ハング対策つき）
- スライドPNG（16:9）+ 音声を ffmpeg で 1スライド=1セグメント化（静止）
- 全セグメントを結合して最終MP4を出力

前提: tmp_music_slides/frames/slide-01.png … slide-15.png（shoot_music_slides.py で生成）
実行: python3 build_music_video.py
"""
from __future__ import annotations
import subprocess
import shutil
from pathlib import Path

PROJ = Path(__file__).resolve().parent
FRAMES = PROJ / "tmp_music_slides" / "frames"
AUDIO = PROJ / "tmp_music_audio"
SEGS = PROJ / "tmp_music_segs"
OUT = PROJ / "英語は歌で覚える_narrated.mp4"

VOICEPEAK = "/Applications/voicepeak.app/Contents/MacOS/voicepeak"
NARRATOR = "Japanese Female 1"
W, H, FPS = 1920, 1080, 30

NARRATION = {
    1: "英語は歌で覚えると、なぜ脳に残るのか。音楽は英語学習の邪魔ではなく、音韻・リズム・記憶・発声・感情をひとつに束ねる足場になります。音楽と第二言語習得の神経科学を、順番に見ていきましょう。",
    2: "まず核心から。覚えたい英文そのものが歌になっているとき、音楽はノイズではなく、第二の記憶ルートになります。関係のない歌詞入りBGMとは別物です。歌詞と学習対象が一致するからこそ、メロディー・リズム・意味が同じ方向へ働きます。",
    3: "「音は右脳」というイメージは、半分だけ正しいです。音素の区別や文法の分析は、主に左半球が担います。一方で、イントネーションやリズム、声の表情といったプロソディは、右半球が主役です。歌は、その両方を同時に動かし、文字で読むだけでは届かない領域に触れます。",
    4: "では、左脳の言語処理と音楽は、ぶつからないのでしょうか。実は、文法と和声の知識は別々に保管されますが、それをその場で組み立てる作業システムは共通しています。文法ミスも不協和音も、同じ脳波成分で検出されることがわかっています。つまり両者は競合せず、予測と統合の回路を二重に鍛え合います。",
    5: "歌には記憶の面でも利点があります。英文を歌として聴くと、歌詞の意味という言語ルートと、メロディーやリズムという音楽ルートの、二つの経路で覚えられます。あとで意味が出てこなくても、出だしのメロディーが手がかりになります。ルートケら2014の実験では、成人60名を3条件に無作為に割り当て、音声の長さをそろえた上で、歌唱群がスポークン産出系の2つのテストで有意に高い成績を示しました。ただし単一研究の短期的な効果です。",
    6: "英語のリズムは、そもそも歌と相性がいい言語です。大事な語は強い拍に乗り、冠詞や前置詞は短く弱く流れます。歌では、この強弱と圧縮が拍とメロディーに乗るので、リンキングやリダクションを、理屈ではなく体のタイミングとして覚えられます。",
    7: "歌のもうひとつの強みは、頭に残ることです。聴いて、口ずさむと、意識しなくても頭の中で勝手に再生される。これは不随意の心的リハーサルと呼ばれます。机を離れた時間にも反復が起こり、フレーズが使える回路へと自動化していきます。",
    8: "ただし、ひとつだけ例外があります。歌で覚えることと、勉強中のBGMは別物です。覚えたい英文そのものの歌なら強い促進になりますが、別の英文を学習している横で歌詞入り音楽を流すと、耳から入る歌詞が割り込んで干渉します。同じ英文の歌なら、この競合は起きません。",
    9: "音楽は、新しい言語回路の足場にもなります。失語症のリハビリでは、メロディーとリズムが右半球を活性化させ、発話を支えます。長期的な音楽訓練は脳梁や弓状束を強化し、聴いて発音するループを速めます。さらに、報酬系のドーパミンが出た瞬間の音は、記憶に定着しやすくなります。",
    10: "そして、楽しいことは最強の学習条件でもあります。不安や退屈が高いと、良いインプットも脳に届きません。歌はその心理的なフィルターを下げ、音楽的・身体的な入口を開きます。何より、苦痛なく繰り返せるので、学習量が自然に増えていきます。",
    11: "この考え方を教材にしたのが、ティーチャー・タコス・イングリッシュ、ファニックス・アイランドです。フォニックスから高校読解まで、同じサイトで段階的に学べます。どのレッスンにも、歌で英語を覚える入り口があり、本文をそのまま歌にした動画がついています。",
    12: "フォニックスでは、エーからゼットまで、二十六人のなかまと歌で音を学びます。アント・アント、ベイカー・ベア、シンガー・スネイク、ティーチャー・タコス。音とキャラクター、単語、動作がひとつに結びつき、音・意味・イメージ・リズムをまとめて覚えられます。",
    13: "おすすめの学習順です。まず歌として聴き、次に歌詞を見て、音と文字を対応させます。そして意味を確認し、最後に声に出して歌う、またはシャドウイングします。音として入り、意味がつながり、構造が見え、声として出る。この往復を繰り返します。",
    14: "まとめます。音素と文法の左半球、リズムとプロソディの右半球、記憶を支えるメロディー、声に出す運動回路、報酬系のドーパミン、頭に残る反復。これらが同じ英文に向かって働くとき、音楽は英語学習の強力な足場になります。英語の第一歩は、まず一曲、耳に残る英文から始めてみてください。",
    15: "本日の内容は、ここに挙げた研究にもとづいています。教育目的の一般的な解説であり、神経科学や第二言語習得には研究途上の知見も含まれます。ティーチャー・タコス・イングリッシュで、ぜひ歌から英語を始めてみてください。ご視聴ありがとうございました。",
}


def split_text(text: str, limit: int = 135) -> list[str]:
    chunks, current = [], ""
    for ch in text:
        current += ch
        if ch in ("。", "．", "！", "？") and len(current) >= 20:
            chunks.append(current.strip()); current = ""
        elif len(current) >= limit:
            pos = max(current.rfind("、"), current.rfind("，"))
            if pos > 10:
                chunks.append(current[:pos + 1].strip()); current = current[pos + 1:]
            else:
                chunks.append(current.strip()); current = ""
    if current.strip():
        chunks.append(current.strip())
    return [c for c in chunks if c]


def voicepeak_one(text: str, out_path: Path, timeout: int = 90, retries: int = 2) -> bool:
    cmd = [VOICEPEAK, "-s", text, "-n", NARRATOR, "-o", str(out_path), "--speed", "100"]
    for attempt in range(1, retries + 1):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            if r.returncode == 0 and out_path.exists():
                return True
            print(f"    voicepeak rc={r.returncode} (試行{attempt}/{retries})")
        except subprocess.TimeoutExpired:
            print(f"    voicepeakタイムアウト{timeout}s (試行{attempt}/{retries}) → kill")
            subprocess.run(["pkill", "-f", "voicepeak -s"], capture_output=True)
            out_path.unlink(missing_ok=True)
    return False


def generate_audio(text: str, out_path: Path) -> None:
    chunks = split_text(text)
    tmp = out_path.parent / f"_tmp_{out_path.stem}"
    tmp.mkdir(exist_ok=True)
    parts = []
    for j, chunk in enumerate(chunks):
        p = tmp / f"part_{j:02d}.wav"
        if voicepeak_one(chunk, p) and p.exists():
            parts.append(p)
        else:
            print(f"    チャンク{j}失敗: {chunk[:24]}...")
    if not parts:
        raise RuntimeError(f"音声生成失敗: {out_path.name}")
    if len(parts) == 1:
        shutil.copy(parts[0], out_path)
    else:
        cf = tmp / "concat.txt"
        cf.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                        "-i", str(cf), "-c", "copy", str(out_path)], capture_output=True)
    shutil.rmtree(tmp, ignore_errors=True)


def get_duration(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
                         capture_output=True, text=True).stdout.strip()
    try:
        return float(out)
    except ValueError:
        return 4.0


def build_segment(img: Path, audio: Path, out: Path) -> None:
    # 16:9スライドを白背景にフィットさせて静止表示（末尾に少し余白を持たせる）
    dur = get_duration(audio) + 0.7
    vf = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:white"
    subprocess.run([
        "ffmpeg", "-y", "-loop", "1", "-i", str(img), "-i", str(audio),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "20",
        "-vf", vf, "-r", str(FPS), "-c:a", "aac", "-b:a", "192k",
        "-t", f"{dur:.2f}", "-shortest", str(out),
    ], capture_output=True)


def main() -> None:
    AUDIO.mkdir(exist_ok=True)
    SEGS.mkdir(exist_ok=True)
    n = len(NARRATION)
    seg_paths = []
    for i in range(1, n + 1):
        num = f"{i:02d}"
        img = FRAMES / f"slide-{num}.png"
        if not img.exists():
            raise FileNotFoundError(img)
        wav = AUDIO / f"slide-{num}.wav"
        seg = SEGS / f"seg-{num}.mp4"
        if wav.exists():
            print(f"[{i}/{n}] 音声は既存を再利用 slide-{num}")
        else:
            print(f"[{i}/{n}] 音声生成 slide-{num}")
            generate_audio(NARRATION[i], wav)
        print(f"        セグメント生成 seg-{num}")
        build_segment(img, wav, seg)
        if not seg.exists():
            raise RuntimeError(f"セグメント生成失敗: {seg}")
        seg_paths.append(seg)

    concat = SEGS / "concat.txt"
    concat.write_text("".join(f"file '{p.resolve()}'\n" for p in seg_paths))
    print("結合中 ->", OUT.name)
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                    "-i", str(concat), "-c", "copy", str(OUT)], capture_output=True)
    if OUT.exists():
        size = OUT.stat().st_size // 1024 // 1024
        dur = get_duration(OUT)
        print(f"完成: {OUT} ({size}MB, {dur:.0f}s)")
    else:
        raise RuntimeError("最終MP4の生成に失敗")


if __name__ == "__main__":
    main()
