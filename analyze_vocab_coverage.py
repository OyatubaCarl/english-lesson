#!/usr/bin/env python3
"""小中学校.xlsx / 高校.xlsx の単語が index.html の各教材でどの程度網羅されているか調べる。

各英単語は <span class="w" data-base="LEMMA" ...> で原形タグ付けされているため、
data-base 値（=その教材が扱う語彙）を正本として網羅率を測る。
活用形のズレを吸収するため、簡易な形態素正規化で variant マッチも行う。
"""
import re, sys
import openpyxl

HTML = "index.html"

# ---------- 1. 単語リスト読み込み ----------
def load_wordlist(path, col=1):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb.worksheets[0]
    words = []
    for r in ws.iter_rows(min_row=2, max_col=col, values_only=True):
        v = r[0]
        if v is None:
            continue
        s = str(v).strip()
        if s:
            words.append(s)
    return words

# ---------- 2. 教材語彙抽出 ----------
def book_ranges(html):
    bounds = {}
    for m in re.finditer(r'<div class="book[^"]*" id="book-(\w+)"', html):
        bounds[m.group(1)] = m.start()
    order = sorted(bounds.items(), key=lambda kv: kv[1])
    ranges = {}
    for i, (name, start) in enumerate(order):
        end = order[i + 1][1] if i + 1 < len(order) else len(html)
        ranges[name] = (start, end)
    return ranges

def extract_bases(segment):
    return [b for b in re.findall(r'data-base="([^"]*)"', segment)]

WORD_RE = re.compile(r"[A-Za-z][A-Za-z'\-]*")
def extract_surface(segment):
    """タグを除去した英語表層トークン（例文・選択肢など data-base 外も拾う）。"""
    text = re.sub(r"<[^>]+>", " ", segment)
    return [w.lower() for w in WORD_RE.findall(text)]

# ---------- 3. 形態素正規化（簡易） ----------
def variants(w):
    """w とその活用/派生候補の集合を返す（原形寄せ）。"""
    w = w.lower()
    out = {w}
    def add(x):
        if len(x) >= 2:
            out.add(x)
    # plural / 3sg
    if w.endswith("ies") and len(w) > 4:
        add(w[:-3] + "y")
    if w.endswith("es") and len(w) > 3:
        add(w[:-2]); add(w[:-1])
    if w.endswith("s") and not w.endswith("ss") and len(w) > 2:
        add(w[:-1])
    # past
    if w.endswith("ied") and len(w) > 4:
        add(w[:-3] + "y")
    if w.endswith("ed") and len(w) > 3:
        add(w[:-2]); add(w[:-1]); add(w[:-3])          # stop(p)ed
    # progressive
    if w.endswith("ing") and len(w) > 4:
        add(w[:-3]); add(w[:-3] + "e"); add(w[:-4])    # run(n)ing / mak(e)ing
    # comparative / superlative
    if w.endswith("est") and len(w) > 4:
        add(w[:-3]); add(w[:-2])
    if w.endswith("er") and len(w) > 3:
        add(w[:-2]); add(w[:-1])
    # adverb
    if w.endswith("ly") and len(w) > 3:
        add(w[:-2])
    return out

def build_index(words):
    """content 語の全 variant -> True の索引。"""
    idx = set()
    for w in words:
        idx |= variants(w)
    return idx

def covered(word, content_index, content_set):
    wl = word.lower()
    if wl in content_set:
        return True
    # variant 同士の交差
    for v in variants(wl):
        if v in content_index:
            return True
    return False

# ---------- main ----------
def main():
    html = open(HTML, encoding="utf-8").read()
    ranges = book_ranges(html)

    # 教材語彙
    book_bases = {}     # name -> set(lower lemmas)
    book_surface = {}   # name -> set(lower surface tokens)
    for name, (s, e) in ranges.items():
        seg = html[s:e]
        book_bases[name] = set(b.lower() for b in extract_bases(seg) if b.strip())
        book_surface[name] = set(extract_surface(seg))

    # 単語リスト
    raw = load_wordlist("小中学校.xlsx")
    uniq = sorted(set(w.lower() for w in raw))
    singles = [w for w in uniq if " " not in w and "-" not in w.strip()]
    phrases = [w for w in uniq if " " in w]
    print(f"# 小中学校.xlsx  生エントリ={len(raw)}  ユニーク(小文字)={len(uniq)}  単一語={len(singles)}  句={len(phrases)}")
    print()

    groups = {
        "中学生編 (middle)": ["middle"],
        "中学生編＋高校編 (middle+high1+high2+high3)": ["middle", "high1", "high2", "high3"],
        "入門(beginner)＋中学生編": ["beginner", "middle"],
        "全教材(beginner+middle+high1-3)": ["beginner", "middle", "high1", "high2", "high3"],
    }

    target = singles  # 句は別集計
    for label, books in groups.items():
        bases = set()
        surf = set()
        for b in books:
            bases |= book_bases.get(b, set())
            surf |= book_surface.get(b, set())
        base_index = build_index(bases)
        surf_index = build_index(surf)

        # 厳密一致（data-base 原形に対する活用許容マッチ）
        miss_base = [w for w in target if not covered(w, base_index, bases)]
        # 表層も含めて「どこかに出現」
        miss_any = [w for w in miss_base
                    if not covered(w, surf_index, surf)]

        n = len(target)
        cov_base = n - len(miss_base)
        cov_any = n - len(miss_any)
        print(f"## {label}")
        print(f"   教材ユニーク原形語数 = {len(bases)}")
        print(f"   語彙タグ網羅(data-base) : {cov_base}/{n} = {cov_base/n*100:.1f}%   (未収載 {len(miss_base)})")
        print(f"   表層含む出現         : {cov_any}/{n} = {cov_any/n*100:.1f}%   (未出現 {len(miss_any)})")
        print()
        if books == ["middle"]:
            global MIDDLE_MISS
            MIDDLE_MISS = miss_any
            MIDDLE_MISS_BASE = miss_base
            with open("vocab_gap_middle.txt", "w", encoding="utf-8") as f:
                f.write("# 中学生編(middle)に語彙タグとして未収載の語（活用許容）\n")
                f.write("\n".join(miss_base))
            with open("vocab_gap_middle_any.txt", "w", encoding="utf-8") as f:
                f.write("# 中学生編(middle)にどこにも出現しない語（表層含む・活用許容）\n")
                f.write("\n".join(miss_any))

    print("# 句エントリ（参考・middle表層での出現判定）:")
    mid_text = re.sub(r"<[^>]+>", " ", html[ranges['middle'][0]:ranges['middle'][1]]).lower()
    mid_text = re.sub(r"\s+", " ", mid_text)
    for p in phrases:
        hit = p in mid_text
        print(f"   [{'o' if hit else 'x'}] {p}")

if __name__ == "__main__":
    main()
