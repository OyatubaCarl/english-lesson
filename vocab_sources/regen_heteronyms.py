"""ヘテロニム/同綴異音語の音声を macOS say + 文脈ラップ+無音切り出しで再生成。

各エントリの実際のPOS+意味で発音が出る短文を say に渡し、
[[slnc 300]] で前後に明確な無音を挿入、ffmpeg silencedetect で
単語境界を検出して中央のターゲット語だけを切り出す。

Samantha 音声で .aiff → ffmpeg trim → .mp3 (64kbps mono)。
出力先は既存 app_audio/{stage}_en/{word}.mp3 を上書き。
manifest_en.json も "voice":"samantha-wrap" で更新。

使い方:
  python3 regen_heteronyms.py            # 全エントリ
  python3 regen_heteronyms.py word1 ...  # 指定語だけ
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VOICE = "Samantha"
PAUSE_MS = 300  # [[slnc ...]] silence padding
SILENCE_THRESHOLD_DB = -38
SILENCE_MIN_S = 0.15
EDGE_PAD_S = 0.04  # extra padding around extracted word so we don't clip transient

# (word_lower, intended_variant) -> 文脈ラップ。target語の前後に [[slnc 300]] を入れる。
# WRAPS[key] = (prefix_text, target_word, suffix_text) — そのまま結合される
# target_word は **必ず1単語** に保つ (空白を含む場合は複数語スパンになるので注意)
WRAPS = {
    # 完全別単語級 (heteronym 別音)
    ("live", "verb_住む"): ("I will", "live", "in Tokyo"),
    ("read", "verb_読む"): ("I like to", "read", "books"),
    ("lead", "verb_導く"): ("she will", "lead", "the team"),
    ("wind", "noun_風"): ("a strong", "wind", "blew today"),
    ("bow", "verb_お辞儀"): ("please", "bow", "politely"),
    ("tear", "noun_涙"): ("a single", "tear", "fell down"),
    ("wound", "noun_傷"): ("a deep", "wound", "healed slowly"),
    ("dove", "noun_鳩"): ("a white", "dove", "flew away"),
    ("minute", "noun_分"): ("one", "minute", "passed quickly"),
    # /s/⇔/z/ 系
    ("abuse", "noun_乱用"): ("a serious", "abuse", "of power"),
    ("use", "verb_使う"): ("I will", "use", "this tool"),
    ("excuse", "noun_言い訳"): ("a poor", "excuse", "was given"),
    ("house", "noun_家"): ("a big", "house", "stood there"),
    ("refuse", "verb_拒否"): ("they will", "refuse", "the offer"),
    ("close", "verb_閉める"): ("please", "close", "the door"),
    # 動詞ストレス系 (名詞=先頭強 / 動詞=語末強)
    ("address", "noun_住所"): ("my home", "address", "is here"),
    ("addict", "noun_中毒者"): ("a coffee", "addict", "drinks daily"),
    ("associate", "verb_関連づける"): ("I will", "associate", "them together"),
    ("attribute", "verb_帰する"): ("they will", "attribute", "it to luck"),
    ("compress", "verb_圧縮"): ("I will", "compress", "the file"),
    ("compound", "noun_化合物"): ("a chemical", "compound", "was formed"),
    ("concert", "noun_コンサート"): ("a rock", "concert", "begins soon"),
    ("concrete", "adj_具体的"): ("a", "concrete", "plan is needed"),
    ("condemn", "verb_非難"): ("they will", "condemn", "the action"),
    ("conduct", "verb_実施"): ("I will", "conduct", "the survey"),
    ("conflict", "noun_対立"): ("an armed", "conflict", "began there"),
    ("console", "verb_慰める"): ("please", "console", "your friend"),
    ("content", "noun_中身"): ("the book", "content", "was helpful"),
    ("contest", "noun_競技"): ("a singing", "contest", "was held"),
    ("contract", "noun_契約"): ("a written", "contract", "was signed"),
    ("converse", "noun_逆"): ("the", "converse", "is also true"),
    ("convert", "verb_変換"): ("I will", "convert", "the file"),
    ("deliberate", "adj_意図的"): ("a", "deliberate", "choice was made"),
    ("desert", "noun_砂漠"): ("a hot", "desert", "stretches far"),
    ("detail", "noun_詳細"): ("every", "detail", "was checked"),
    ("digest", "noun_要約"): ("a weekly", "digest", "was sent"),
    ("discount", "noun_割引"): ("a big", "discount", "was offered"),
    ("document", "noun_書類"): ("an old", "document", "was found"),
    ("duplicate", "noun_複製"): ("a", "duplicate", "key was made"),
    ("estimate", "verb_見積"): ("I will", "estimate", "the cost"),
    ("export", "verb_輸出"): ("they", "export", "rice abroad"),
    ("extract", "verb_抽出"): ("I will", "extract", "the data"),
    ("finance", "noun_財政"): ("corporate", "finance", "is complex"),
    ("frequent", "adj_頻繁"): ("a", "frequent", "visitor came back"),
    ("graduate", "verb_卒業"): ("I will", "graduate", "next spring"),
    ("impact", "noun_衝撃"): ("a strong", "impact", "was felt"),
    ("import", "verb_輸入"): ("they", "import", "oil cheaply"),
    ("incense", "noun_お香"): ("burning", "incense", "smelled sweet"),
    ("increase", "verb_増える"): ("prices", "increase", "every year"),
    ("insult", "verb_侮辱"): ("do not", "insult", "anyone here"),
    ("intimate", "adj_親密"): ("an", "intimate", "dinner was held"),
    ("moderate", "adj_適度"): ("a", "moderate", "amount is fine"),
    ("object", "noun_物"): ("a small", "object", "was found"),
    ("overlap", "noun_重なり"): ("a slight", "overlap", "was noted"),
    ("overthrow", "verb_転覆"): ("they will", "overthrow", "the regime"),
    ("overweight", "adj_太りすぎ"): ("an", "overweight", "bag was tagged"),
    ("perfect", "adj_完璧"): ("a", "perfect", "day passed quickly"),
    ("permit", "verb_許可"): ("they", "permit", "smoking outside"),
    ("pirate", "noun_海賊"): ("a fierce", "pirate", "sailed away"),
    ("polish", "noun_つや出し"): ("shoe", "polish", "was applied"),
    ("pollute", "verb_汚染"): ("do not", "pollute", "the river"),
    ("present", "noun_贈り物"): ("a birthday", "present", "was opened"),
    ("process", "noun_過程"): ("a slow", "process", "was followed"),
    ("produce", "verb_生産"): ("farmers", "produce", "fresh food"),
    ("progress", "noun_進歩"): ("good", "progress", "was made today"),
    ("project", "noun_計画"): ("a school", "project", "was assigned"),
    ("protest", "noun_抗議"): ("a peaceful", "protest", "was held"),
    ("rebel", "noun_反逆者"): ("a young", "rebel", "stood alone"),
    ("recall", "verb_思い出す"): ("I cannot", "recall", "her name"),
    ("record", "noun_記録"): ("a world", "record", "was broken"),
    ("refund", "noun_返金"): ("a full", "refund", "was given"),
    ("reject", "verb_拒否"): ("they will", "reject", "the offer"),
    ("reprint", "noun_再版"): ("a new", "reprint", "is coming"),
    ("research", "noun_研究"): ("recent", "research", "shows results"),
    ("rewrite", "verb_書き直す"): ("I will", "rewrite", "the essay"),
    ("separate", "verb_分ける"): ("I will", "separate", "the items"),
    ("subject", "noun_教科"): ("a school", "subject", "was chosen"),
    ("suspect", "verb_疑う"): ("I", "suspect", "a leak there"),
    ("transfer", "verb_移す"): ("I will", "transfer", "the money"),
    ("transport", "verb_輸送"): ("they", "transport", "the cargo"),
    ("update", "verb_更新"): ("I will", "update", "the file"),
    ("upgrade", "noun_格上げ"): ("a free", "upgrade", "was offered"),
    ("upset", "adj_動揺"): ("an", "upset", "child was crying"),
    ("complex", "adj_複雑"): ("a", "complex", "problem appeared"),
    # spirit はヘテロニムではないがTTSのクセ補正
    ("spirit", "noun_精神"): ("the team", "spirit", "stays strong"),
}

# 各エントリ id → (key tuple) のマップ
ENTRY_MAP: dict[str, tuple[str, str]] = {
    "s1_192": ("live", "verb_住む"),
    "s1_264": ("read", "verb_読む"),
    "s3_160": ("lead", "verb_導く"),
    "s3_301": ("wind", "noun_風"),
    "s5_1093": ("bow", "verb_お辞儀"),
    "s4_535": ("tear", "noun_涙"),
    "s5_2715": ("wound", "noun_傷"),
    "s6_0619": ("dove", "noun_鳩"),
    "s2_195": ("minute", "noun_分"),
    "s6_0008": ("abuse", "noun_乱用"),
    "s1_374": ("use", "verb_使う"),
    "s1_104": ("excuse", "noun_言い訳"),
    "s1_167": ("house", "noun_家"),
    "s5_2261": ("refuse", "verb_拒否"),
    "s1_065": ("close", "verb_閉める"),
    "s4_002": ("address", "noun_住所"),
    "s6_0021": ("addict", "noun_中毒者"),
    "s5_1016": ("associate", "verb_関連づける"),
    "s6_0134": ("attribute", "verb_帰する"),
    "s6_0362": ("compress", "verb_圧縮"),
    "s5_1230": ("compound", "noun_化合物"),
    "s2_066": ("concert", "noun_コンサート"),
    "s6_0374": ("concrete", "adj_具体的"),
    "s6_0375": ("condemn", "verb_非難"),
    "s5_1236": ("conduct", "verb_実施"),
    "s5_1240": ("conflict", "noun_対立"),
    "s6_0394": ("console", "verb_慰める"),
    "s3_058": ("content", "noun_中身"),
    "s4_110": ("contest", "noun_競技"),
    "s6_0401": ("contract", "noun_契約"),
    "s6_0409": ("converse", "noun_逆"),
    "s6_0412": ("convert", "verb_変換"),
    "s6_0518": ("deliberate", "adj_意図的"),
    "s5_337": ("desert", "noun_砂漠"),
    "s5_339": ("detail", "noun_詳細"),
    "s6_0552": ("digest", "noun_要約"),
    "s4_142": ("discount", "noun_割引"),
    "s5_1420": ("document", "noun_書類"),
    "s6_0637": ("duplicate", "noun_複製"),
    "s5_1507": ("estimate", "verb_見積"),
    "s6_0755": ("export", "verb_輸出"),
    "s6_0761": ("extract", "verb_抽出"),
    "s5_1562": ("finance", "noun_財政"),
    "s5_1600": ("frequent", "adj_頻繁"),
    "s3_117": ("graduate", "verb_卒業"),
    "s5_476": ("impact", "noun_衝撃"),
    "s6_1023": ("import", "verb_輸入"),
    "s6_1041": ("incense", "noun_お香"),
    "s4_271": ("increase", "verb_増える"),
    "s4_277": ("insult", "verb_侮辱"),
    "s6_1108": ("intimate", "adj_親密"),
    "s5_1952": ("moderate", "adj_適度"),
    "s5_2028": ("object", "noun_物"),
    "s6_1459": ("overlap", "noun_重なり"),
    "s6_1466": ("overthrow", "verb_転覆"),
    "s5_584": ("overweight", "adj_太りすぎ"),
    "s2_218": ("perfect", "adj_完璧"),
    "s5_2107": ("permit", "verb_許可"),
    "s6_1562": ("pirate", "noun_海賊"),
    "s6_1577": ("polish", "noun_つや出し"),
    "s5_620": ("pollute", "verb_汚染"),
    "s1_257": ("present", "noun_贈り物"),
    "s5_2178": ("process", "noun_過程"),
    "s4_409": ("produce", "verb_生産"),
    "s5_2184": ("progress", "noun_進歩"),
    "s6_1645": ("project", "noun_計画"),
    "s5_2200": ("protest", "noun_抗議"),
    "s6_1714": ("rebel", "noun_反逆者"),
    "s5_2245": ("recall", "verb_思い出す"),
    "s5_661": ("record", "noun_記録"),
    "s5_2259": ("refund", "noun_返金"),
    "s5_2267": ("reject", "verb_拒否"),
    "s6_1772": ("reprint", "noun_再版"),
    "s3_232": ("research", "noun_研究"),
    "s5_685": ("research", "noun_研究"),
    "s5_2304": ("rewrite", "verb_書き直す"),
    "s4_462": ("separate", "verb_分ける"),
    "s1_327": ("subject", "noun_教科"),
    "s5_2502": ("suspect", "verb_疑う"),
    "s5_2581": ("transfer", "verb_移す"),
    "s5_2585": ("transport", "verb_輸送"),
    "s5_2642": ("update", "verb_更新"),
    "s6_2277": ("upgrade", "noun_格上げ"),
    "s3_295": ("upset", "adj_動揺"),
    "s5_1224": ("complex", "adj_複雑"),
    "s1_420": ("spirit", "noun_精神"),
}


def stage_of(qid: str) -> str | None:
    for n in range(1, 7):
        if qid.startswith(f"s{n}_"):
            return f"stage{n}"
    return None


def find_silence_gaps(aiff: Path) -> list[tuple[float, float]]:
    """ffmpeg silencedetect で無音区間 (start, end) のリストを返す。"""
    r = subprocess.run(
        [
            "ffmpeg", "-i", str(aiff),
            "-af", f"silencedetect=noise={SILENCE_THRESHOLD_DB}dB:d={SILENCE_MIN_S}",
            "-f", "null", "-",
        ],
        capture_output=True, timeout=30,
    )
    out = r.stderr.decode()
    starts = [float(m.group(1)) for m in re.finditer(r"silence_start:\s*([\d.]+)", out)]
    ends = [float(m.group(1)) for m in re.finditer(r"silence_end:\s*([\d.]+)", out)]
    return list(zip(starts, ends))


def synth_and_trim(prefix: str, target: str, suffix: str, out_mp3: Path) -> bool:
    """文脈ラップ → say → silencedetect → 真ん中スパンを切り出して mp3 化。"""
    tmp_aiff = out_mp3.with_suffix(".wrap.aiff")
    tmp_target_aiff = out_mp3.with_suffix(".target.aiff")
    say_text = f"{prefix} [[slnc {PAUSE_MS}]] {target} [[slnc {PAUSE_MS}]] {suffix}"
    r = subprocess.run(
        ["say", "-v", VOICE, say_text, "-o", str(tmp_aiff)],
        capture_output=True, timeout=15,
    )
    if r.returncode != 0 or not tmp_aiff.exists():
        print(f"  say FAIL: {r.stderr.decode()[:200]}")
        return False
    gaps = find_silence_gaps(tmp_aiff)
    # 期待: 2つ以上の無音区間。先頭/末尾の境界=最初の silence_end と 2番目の silence_start
    if len(gaps) < 2:
        print(f"  silence gap count={len(gaps)} (expected >=2) → fallback skip")
        tmp_aiff.unlink(missing_ok=True)
        return False
    start_s = max(0.0, gaps[0][1] - EDGE_PAD_S)  # 1番目の無音の終わり
    end_s = gaps[1][0] + EDGE_PAD_S                # 2番目の無音の始まり
    if end_s - start_s < 0.10 or end_s - start_s > 1.50:
        print(f"  abnormal target span {start_s:.2f}→{end_s:.2f} → fallback skip")
        tmp_aiff.unlink(missing_ok=True)
        return False
    # 切り出し → mp3
    r = subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp_aiff),
            "-ss", f"{start_s:.3f}", "-to", f"{end_s:.3f}",
            "-ac", "1", "-b:a", "64k", str(out_mp3),
        ],
        capture_output=True,
    )
    tmp_aiff.unlink(missing_ok=True)
    tmp_target_aiff.unlink(missing_ok=True)
    return out_mp3.exists() and out_mp3.stat().st_size > 500


def main() -> None:
    only = set(s.lower() for s in sys.argv[1:])
    ok, ng, skip = 0, 0, 0
    quizzes_cache: dict[str, dict] = {}
    manifest_cache: dict[str, dict] = {}
    for qid, key in ENTRY_MAP.items():
        word_lc, _ = key
        if only and word_lc not in only:
            skip += 1
            continue
        if key not in WRAPS:
            print(f"  {qid} {word_lc}: NO WRAP")
            ng += 1
            continue
        prefix, target, suffix = WRAPS[key]
        stage = stage_of(qid)
        if not stage:
            print(f"  {qid}: unknown stage")
            ng += 1
            continue
        d = quizzes_cache.get(stage)
        if d is None:
            d = json.loads((ROOT / f"{stage}_quizzes_clean.json").read_text(encoding="utf-8"))
            quizzes_cache[stage] = d
        entry = next((q for q in d["quizzes"] if q["id"] == qid), None)
        if not entry:
            print(f"  {qid}: not found in {stage}")
            ng += 1
            continue
        safe = entry["word"].replace("/", "_").replace(" ", "_").replace(".", "_")
        out_dir = ROOT / "app_audio" / f"{stage}_en"
        mp3 = out_dir / f"{safe}.mp3"
        if not mp3.parent.exists():
            print(f"  {qid}: missing dir {mp3.parent}")
            ng += 1
            continue
        print(f"  {qid} {entry['word']:14} ← '{prefix} <{target}> {suffix}'")
        if synth_and_trim(prefix, target, suffix, mp3):
            manif_path = out_dir / "manifest_en.json"
            m = manifest_cache.get(stage)
            if m is None:
                m = json.loads(manif_path.read_text(encoding="utf-8")) if manif_path.exists() else {}
                manifest_cache[stage] = m
            m[qid] = {
                "word": entry["word"],
                "file": mp3.name,
                "voice": "samantha-wrap",
                "wrap": f"{prefix} | {target} | {suffix}",
            }
            ok += 1
        else:
            ng += 1
    for stage, m in manifest_cache.items():
        (ROOT / "app_audio" / f"{stage}_en" / "manifest_en.json").write_text(
            json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8"
        )
    print(f"\n✅ 完了: ok={ok} ng={ng} skip={skip}")


if __name__ == "__main__":
    main()
