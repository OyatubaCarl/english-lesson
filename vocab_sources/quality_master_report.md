# WordTacos 品質マスター監査レポート (2026-06-16)

## 全体サマリ

### データ規模
- **stage5**: 2720問 (B1)
- **stage6**: 2394問 (B2)
- 合計 5114問

### 監査3手法を併用

| 手法 | 対象 | 検出件数 |
|---|---|---|
| ヒューリスティック (`quality_heuristics.py`) | 全5114問 | 101件 (修正後) |
| 品詞ミスマッチ (`quality_pos_check.py`) | 全5114問 | 240件 (修正後) |
| LLM並列レビュー (1000問サンプル / 4並列) | 1000問 | bad 22, warn 89 |

### 今セッションで修正済み (134問)

更新: 2026-06-16時点で機械検出bad=0件、副詞+に問題はステージ別方針で整理完了。



| 種類 | 件数 | 内容 |
|---|---|---|
| choices重複 | 1 | s5_2469 studio (倉庫×2 → 倉庫+画廊) |
| explanation短すぎ | 1 | s5_2228 railway (英国式。→ rail+way 補強) |
| 動詞+な | 3 | s5_1719 hop, s5_1870 limp, s5_2536 tend |
| 副詞+な | 1 | s5_2455 strangely |
| 形容詞+の/形容詞構文誤 | 2 | s5_706 remote, s5_540 married |
| 前置詞構文誤 | 1 | s5_1364 despite (despite + 名詞句) |
| 自動詞構造誤 | 1 | s5_1779 insist (insist on / 目的語化) |
| 形容詞→動詞誤用 | 2 | s6_0413 convinced, s5_946 afford |
| 副詞→形容詞誤用 | 2 | s5_2675 vividly+と, s6_0795 figurative+に |
| 副詞+に(LLM明示) | 12 | undoubtedly/desperately/adequately/bitterly/severely/literally/widely/pleasantly/freely/irresistibly/legally/similarly |
| stage6 副詞+に厳格化 | 106 | 161件をLLM個別判断 → 106件fix / 55件keep |
| 形容詞+のような | 2 | s5_1123 burning, s5_2625 unheard |
| 引用符明示 | 1 | s5_900 absolutely (「<absolutely>」と答え) |

## 残課題

### 体系的問題: 副詞+「に」(adverb_redundant_ni) 236件
- wordtacos全体に共通する傾向。LLMチャンク間でも判定が分かれた(chunk3はスタイル許容、chunk4はwarn)
- 例: `<carefully>に進めた`、`<quickly>に向かった`
- 一律修正は副詞訳の「親切に」「丁寧に」等で必須な「に」も削ってしまうリスクあり
- **判断オプション**:
  - **A**: 個別LLMで全件チェックして残すべき「に」と削るべき「に」を仕分け
  - **B**: wordtacosのスタイルとして許容
  - **C**: ステージ別に方針決め(stage5は許容、stage6は厳格化など)

### LLMレビューで挙がった軽微な問題 (warn 89件)

| カテゴリ | 件数 | 例 |
|---|---|---|
| body自然さ | 15 | 冗長表現、重複モチーフ |
| 副詞+に(warn判定) | 12 | (上記236件のうちサンプルされた12件) |
| 単複ミス | 5 | eyebrow→eyebrows, schoolchild→schoolchildren等 |
| 文化的配慮 | 5 | aborigine→Aboriginal Australian, policeman→police officer等 |
| etymology誤り | 3 | classification は classify+-cation でなく classif+-ication等 |
| explanation不足/誤 | 4 | jeopardize の英米綴り説明等 |
| meaning_jp冗長 | 2 | pawnshop=質屋の店, micrometer=マイクロメーター(米) |
| 大文字小文字 | 2 | <dna>→DNA, <olympia>→Olympia |
| choices品質 | 3 | 造語ダミー (s5_2649 usage の「故障法」等) |

### ヒューリスティック残 (warn相当 101件)

| 種類 | 件数 |
|---|---|
| choices_len_unbalanced (長さ不均等) | 58 |
| correct_contains_choice (正解がダミーを部分包含) | 22 |
| choice_contains_correct (ダミーが正解を部分包含) | 21 |

これらはユーザビリティの観点で「正解が露見しやすい」というだけで、内容的に間違いではない。改善余地はあるが優先度低い。

## 次の対応候補

1. **副詞+に問題の方針決定** (236件): A/B/Cいずれを採るか
2. **大文字/小文字+単複ミス**: 機械修正可能 (例: `<dna>` → `<DNA>` のregex置換)
3. **explanation誤りの個別修正** (4件): 短時間で対応可能
4. **cultural awareness修正** (5件): 用語の置換 (policeman→police officer など、ただしwordtacos的にpolicemanで学習させたい意図かも)
5. **新規LLM並列レビューを残4114問にも実施** (現在1000問のみサンプル): 残り bad 推定 90件程度

## 出力ファイル
- `quality_heuristic_issues.json` / `quality_heuristic_report.md`
- `quality_pos_issues.json` / `quality_pos_report.md`
- `_review/review_result_{1-4}.json` (LLM結果)
- 本ファイル: `quality_master_report.md`
