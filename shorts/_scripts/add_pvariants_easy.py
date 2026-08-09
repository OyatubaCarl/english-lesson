#!/usr/bin/env python3
"""quizzes.json の 12-21 に intro_overlay と paper_variant を追加。"""
import json
from pathlib import Path

PATH = Path("/Users/masaki/Documents/ClaudeCode/英語学習教材作成/shorts/quizzes.json")
data = json.loads(PATH.read_text(encoding="utf-8"))

INTRO_HEADER = "知らない 単語 でも 一発で 覚える 裏技 !"

PVAR = {
    "12_gentle": {
        "header": "▷  偶発 的 学習",
        "lines": [
            {"text": "日本語 の 中 に 英単語 が 混じる と、", "y": 880},
            {"text": "1 日 3 個 を 自然 に", "y": 1020, "emphasis": True, "fs": 78},
            {"text": "覚えられる こと が 多い 。", "y": 1180},
        ],
        "cite": "偶発 的 語彙 学習 研究",
    },
    "13_nervous": {
        "header": "▷  感情 と 単語",
        "lines": [
            {"text": "自分 の 経験 と 結びついた 単語 は、", "y": 880},
            {"text": "圧倒的 に 忘れ にくい", "y": 1020, "emphasis": True, "fs": 78},
            {"text": "こと が 知られている 。", "y": 1180},
        ],
        "cite": "感情 的 刺激 仮説",
    },
    "14_huge": {
        "header": "▷  視覚 イメージ",
        "lines": [
            {"text": "強い 視覚 イメージ を 伴う 単語 は、", "y": 880},
            {"text": "長期 記憶 に 定着 しやすい", "y": 1020, "emphasis": True, "fs": 72},
            {"text": "こと が 実証 されている 。", "y": 1180},
        ],
        "cite": "Paivio  デュアル コーディング 理論",
    },
    "15_silent": {
        "header": "▷  集中 と 学習",
        "lines": [
            {"text": "集中 できる 短時間 学習 は、", "y": 880},
            {"text": "長時間 より 効率 的", "y": 1020, "emphasis": True, "fs": 78},
            {"text": "だ と 言われている 。", "y": 1180},
        ],
        "cite": "分散 学習 効果 ( Ebbinghaus )",
    },
    "16_delicious": {
        "header": "▷  物語 と 記憶",
        "lines": [
            {"text": "短い ストーリー に 乗せる と、", "y": 880},
            {"text": "単語 が 忘れ にくく なる", "y": 1020, "emphasis": True, "fs": 78},
            {"text": "こと が 報告 されている 。", "y": 1180},
        ],
        "cite": "エピソード 記憶 研究",
    },
    "17_disappear": {
        "header": "▷  思い 出す 力",
        "lines": [
            {"text": "クイズ で 思い出す 行為 が、", "y": 880},
            {"text": "最強 の 記憶 定着 法", "y": 1020, "emphasis": True, "fs": 78},
            {"text": "と され ている 。", "y": 1180},
        ],
        "cite": "アクティブ リコール ( Roediger )",
    },
    "18_whisper": {
        "header": "▷  声 に 出すと",
        "lines": [
            {"text": "自分 の 声 で 英単語 を 読む と、", "y": 880},
            {"text": "黙読 より 深く 記憶 される", "y": 1020, "emphasis": True, "fs": 72},
            {"text": "こと が 確認 されている 。", "y": 1180},
        ],
        "cite": "プロダクション 効果",
    },
    "19_brave": {
        "header": "▷  共感 の 力",
        "lines": [
            {"text": "主人公 の 感情 に 共感 した 瞬間、", "y": 880},
            {"text": "単語 は 脳 に 焼きつく", "y": 1020, "emphasis": True, "fs": 78},
            {"text": "こと が 知られている 。", "y": 1180},
        ],
        "cite": "物語 の 記憶 効果",
    },
    "20_lonely": {
        "header": "▷  復習 の タイミング",
        "lines": [
            {"text": "1 日 後、3 日 後、1 週間 後 の", "y": 880},
            {"text": "3 回 復習", "y": 1020, "emphasis": True, "fs": 110, "color": "&H00FF66&"},
            {"text": "で 長期 記憶 へ 移行 する 。", "y": 1200},
        ],
        "cite": "間隔 反復 学習",
    },
    "21_honest": {
        "header": "▷  自分 を 観察",
        "lines": [
            {"text": "自分 が 何 を 覚えた か を 意識 する だけ で、", "y": 880},
            {"text": "定着率 は 2 倍", "y": 1020, "emphasis": True, "fs": 110, "color": "&H00FF66&"},
            {"text": "に なる と 言われている 。", "y": 1200},
        ],
        "cite": "メタ 認知 学習",
    },
}

for q in data:
    if q["id"] in PVAR:
        q["intro_overlay"] = {
            "header": INTRO_HEADER,
            "word_position_y": 1100,
        }
        q["paper_variant"] = PVAR[q["id"]]

PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8")
print(f"updated {len(PVAR)} easy quizzes")
for qid in PVAR:
    print(f"  ✓ {qid}")
