# Phonics Island 動画化プラン

`phonics island.mp3` ＋ 26キャラ画像 → Revid で水彩風アニメ動画を生成する計画書。
着手前にここで合意を取る。

最終更新: 2026-04-29

---

## 1. 素材インベントリ

### 音源
- ファイル: `phonics island.mp3`（リポジトリ直下）
- 長さ: **404.232秒（≈6分44秒）**
- 形式: 48kHz / 2ch / 191kbps MP3（Suno 由来推定）

### キャラクター画像（26音）
- 場所: `/地学基礎漫画作成/phonics_island/{char}/`
- 各フォルダ最低 2 枚: `charactersheet.png`（横長／設定画）, `single.png`（単独立ち絵）
- 一部のキャラ（aunt_ant, baker_bear, teacher_tacos, waiter_wolf, boxer_fox など）はバリエーションあり
- 解像度: 1376–1380 × 752–768 8-bit RGB（Revid の最低 1024² は満たす）
- 詳細ロースター: `phonics-island-roster.md`（138行の通し歌詞付き）

### Revid 既登録キャラ（2026-04-29 時点）
`/api/public/v2/consistent-characters` GET の結果:
- `aunt ant` （id: `ece21d83-…`）
- `teacher tacos` （id: `35eb1ec9-…`）
- 残り **24 体未登録**

---

## 2. やりたいこと（ユーザ要望の確認）

1. ✅ `phonics island.mp3` を音源とする
2. ✅ 26 キャラの設定画を Revid に登録して使う
3. ✅ 絵柄は **水彩風**（既存のアニメ風スタイルとは別）
4. ✅ 長尺（6:44）なので **コスト・品質・整合性のリスクを潰してから着手**

---

## 3. Revid の仕様確認・未確認事項

### 確認済み
- `consistent-characters` 一覧 GET は動く → 24 体追加登録は API でも可能（要 PNG/JPG ＋ 名前）
- music-to-video のテスト見積（ダミー URL）で **約 45 クレジット**。実際の 6:44 で何カット生成されるかで増減
- `imageModel: cheap` で 1キャラ 9–12 クレジット、`good` は約 4 倍

### 未確認（着手前に潰したい）
| 項目 | 重要度 | 検証方法 |
|---|---|---|
| **音源にローカル mp3 が直接使えるか**（Suno URL 必須か） | 🔴 高 | テスト 1本（小額）で確認 |
| **music-to-video で `characters[]` 引数を取るか**（複数キャラの同一性） | 🔴 高 | Revid サポート / 公式ドキュメント要確認 |
| **`stylePrompt` で水彩風が再現できるか** | 🟡 中 | テスト 1本で確認 |
| **6:44 全尺で何カット生成されるか → 実クレジット** | 🟡 中 | テストで実測 |
| **キャラクター順序を歌詞のアルファベット順に揃えられるか** | 🟢 低 | 揃えられない可能性高（後述） |

---

## 4. 想定される技術的制約

### 🔴 大きな制約：カット順は制御できない
Revid music-to-video は「歌詞・音楽の盛り上がり」を解析して自動的にカットを切る。**「A の verse には Aunt Ant、B の verse には Baker Bear」** のような厳密な対応はできないと思われる（過去の lesson 動画でもキャラが特定タイミングに出現する制御はできていない）。

これは厳しい制約。回避策:
- **A案**: Revid 自動生成のまま受け入れる（キャラがランダムに混ざる動画になる）
- **B案**: 26 本に分割して個別レンダリング → 後で結合（厳密な順序制御）
- **C案**: Revid を諦め、別の手段（手動編集 / ffmpeg / 動画編集ツール）でカット並べ替え

### 🟡 キャラ同一性
- `consistent-characters` は **1 リクエスト＝1 キャラ参照**。music-to-video で複数キャラを同時参照できるかは未確認
- できなければ、26 キャラ別レンダリング（B案）に近づく

### 🟡 水彩風スタイルプロンプト
既存の anime stylePrompt と差し替え。例:
```
Hand-painted watercolor illustration style throughout. Soft watercolor washes,
visible paper texture, gentle blended edges, warm pastel tones, light brush strokes.
Children's picture-book aesthetic. No photorealistic images, no 3D renders, no anime line art.
```

---

## 5. 3 つの実行プラン（コスト・品質・手間）

### プラン A: 一発レンダー（楽、ただしカット順制御なし）
1. 24 体追加登録（API バッチ）
2. mp3 をどこかに公開 HTTPS で置く（Cloudflare Pages 利用可能）
3. music-to-video に丸投げ
4. Revid 生成のままダウンロード

- 推定クレジット: 50–80 程度（6:44 全尺・cheap）
- 所要時間: 制作 30 分、レンダー 5–10 分
- 仕上がり: キャラがランダムに混ざる。教育用としては妥協が必要

### プラン B: 26 分割レンダー → 結合（厳密な順序）★推奨
1. 24 体追加登録
2. mp3 を 26 区間に分割（各 ~14秒、イントロ/アウトロ込みで 28 区間）
3. 各区間を **prompt-to-video** または **image-to-video** ワークフローでレンダー
4. ffmpeg で結合 ＋ 元音声を被せる

- 推定クレジット: 26 × 9 = ~234 クレジット（cheap）
- 所要時間: 制作 2–3 時間（タイミング合わせ含む）、レンダー並列 30 分
- 仕上がり: アルファベット順で正しいキャラが正しいタイミングで出る

### プラン C: Revid 不使用、別手段
- 26 キャラ画像をスライドショー化（ffmpeg / Keynote / iMovie）
- アニメーションは Ken Burns（ズーム・パン）程度
- クレジット 0、ただし「動的な水彩」表現は出ない

- 推定コスト: 0 円
- 所要時間: 1–2 時間
- 仕上がり: シンプルなスライドショー教材

---

## 6. 推奨ステップ（Phase 0 — 着手前テスト）

**いきなり 24 体登録 ＋ 全尺レンダーは危険**。先にコスト・品質を確認したい。

### Step 0.1: 1 キャラテストレンダー（10 クレジット程度）
- 既登録の `aunt ant` を使い、Aunt Ant の verse 部分（推定 14秒）だけを切り出した mp3 でテスト
- stylePrompt に水彩記述を入れて 1 本回す
- 確認: 水彩風の出方／クレジット消費量／キャラ同一性

### Step 0.2: 結果を見て判断
- 水彩 OK → プラン B へ進む
- 水彩 NG → stylePrompt を再調整 → 再テスト
- キャラ同一性 NG → Revid サポートに問い合わせ／別ワークフロー検討

### Step 0.3: ユーザ確認 → 本番
合意後に 24 キャラ追加登録 ＋ 本番レンダー。

---

## 7. 着手前に決めてほしいこと

- [ ] **プラン A / B / C どれで進めるか**（推奨: B、ただしコスト 234 クレジット）
- [ ] **mp3 のホスティング先**（Cloudflare Pages に上げて公開して良いか）
- [ ] **水彩 stylePrompt の文言**（上記ドラフトで OK か、調整したいか）
- [ ] **Phase 0 のテストレンダーを先に走らせて良いか**（10 クレジット消費）

---

## 8. 参考資料

- 既存の Revid レシピ: `revid-workflow.md`
- 過去のレッスン動画事例: H21–H45 / L1–L4 など（11本実績、平均 10 クレジット）
- stylePrompt の経験則: キャラ説明を入れると崩れる → スタイル記述だけにする
- `consistent-characters` API: 単発登録は確認済み、複数同時参照は未確認

---

## 9. テスト #1 の結果と反省（2026-04-29 22:00）

### やってしまったこと
- Suno URL `zEyTiHQOoR6J6DCh`（og:title "phonics island" 一致）で全尺レンダーを投入
- **payload に `characterIds` を含め忘れた** → 登録済みキャラが反映されず
- **音源が 6:44 全尺**だったため、画像 ~118 枚生成 → **119 クレジット消費**（見積 45 の 2.6 倍）
- リネームのみ完了、出力は使い物にならない

### 学んだこと（重要）
1. **`characterIds` 配列で登録キャラを引用する**（`selectedCharacters` という legacy alias もあり）
   - 公式 API ドキュメント `GET /api/public/v3/render` の parameterReference で確認
   - 例:
     ```json
     "characterIds": ["ece21d83-b88a-47ae-9d88-36e584734b9c"]
     ```
2. **見積 API（calculate-credits）は長尺で当てにならない**。45 と返ってきても実消費 119 になる
3. 短尺テストには prompt-to-video が向くが、**`quality: "pro"` だと 10秒 × 3カット = 209 cr**（音楽より高い）
4. キャラ単独テストの最安経路は **prompt-to-video + moving-image + cheap imageModel + 短尺**

### 残クレジット注意
- 119 既に消費済み。次のテストは最小コストで進める
- Phase 0 の 1キャラ確認テストは **prompt-to-video + cheap + 5–10秒 + 単一画像** 想定で **5–15 cr** 目標

---

## 10. 改訂プラン（2026-04-29 更新）

### Phase 0 改訂（最小コストでキャラ反映を確認）
**目的のみ**: `characterIds` 指定で登録画像が出力に反映されるかを確認

候補 A: prompt-to-video + 静止画 1 枚相当
```python
{
    'workflow': 'prompt-to-video',
    'source': {
        'prompt': 'Aunt Ant character holding a hand up to ask, simple watercolor scene',
        'stylePrompt': WATERCOLOR_STYLE,
        'durationSeconds': 5
    },
    'media': {'type': 'moving-image', 'imageModel': 'cheap', 'videoModel': 'base'},
    'options': {'promptTargetDuration': 5, 'disableAudio': True},
    'characterIds': ['ece21d83-b88a-47ae-9d88-36e584734b9c'],   # aunt ant
    'aspectRatio': '16 / 9'
}
```
- 見積を先に取り、5–15 cr 範囲ならゴーサイン
- 出力で aunt ant の登録画像が再現されているか確認 → されていれば本番に進める

### 本番プラン（再考）
キャラ反映が確認できたら:
- **B-1案**: 26 区間別 prompt-to-video レンダー → ffmpeg で結合（厳密順序）
  - 推定 cr: 1区間 5–15 cr × 26 = **130–390 cr**（cheap）
  - 音は phonics island.mp3 を後で被せる
- **B-2案**: music-to-video + characterIds=[全26ID] で一発（ただし全キャラ詰め込みで崩れる懸念）
  - 推定 cr: 100–150 cr（既に 119 で実証）
  - 順序制御不可

→ B-1 が現実解。Phase 0 確認後に着手判断。
