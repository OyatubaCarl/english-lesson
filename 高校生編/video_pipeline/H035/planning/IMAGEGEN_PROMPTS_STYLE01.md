# H035 ImageGen計画 — 画風01

## 共通指定

- H15基準の画風01「光彩・劇場アニメ背景」。精密な2D線画、抑制したセル塗り、劇場アニメ級の海・木造船・溶岩・鳥・標本・ヴィクトリア朝室内。
- 史実・生物種・人物年齢・時系列を美しさより優先。主要物は画面下部45%の字幕帯より上。読める文字、透かし、ロゴ、分割画面なし。
- 1835年のダーウィンは26歳前後、濃茶の短髪、長い顔、ひげなし。1859年は50歳、深い生え際ともみあげ、顎ひげなし。後年の白い大ひげ姿は禁止。
- フィンチを「島で即座に進化理論へ気づいた象徴」として描かない。マネシツグミの島差への注目、標本収集、帰国後のグールドによるフィンチ再同定、長年の思索の順にする。

## 採用基準画12枚

1. `beagle_departure_master.png` — 1831年、英国の冬の港から出る小型三本マスト測量船と若いダーウィン。
2. `beagle_voyage_cabin_master.png` — 南米沿岸を航行する甲板と、狭い共同作業室の製図台・標本・若いダーウィン。
3. `galapagos_arrival_master.png` — 1835年9月、黒い溶岩海岸と低い火山丘へ上陸する若いダーウィン。
4. `mockingbirds_tortoise_master.png` — 枝上のガラパゴスマネシツグミをノートに記すダーウィン、別焦点にゾウガメ。
5. `field_collection_master.png` — 収集済み標本を流血なしで木箱へ整理し、島別に注意深く記録する作業。
6. `gould_finches_london_master.png` — 1837年前後のロンドン、ジョン・グールドとダーウィンが異なる嘴のフィンチ標本を比較。
7. `down_house_thought_master.png` — 1840〜1850年代、書斎で標本・手紙・ノートを何年も照合するダーウィン。
8. `finch_adaptation_master.png` — 太い嘴で種子、細い嘴で昆虫、長い嘴でサボテンを利用する近縁フィンチ。人物なし。
9. `origin_printing_master.png` — 1859年、顎ひげのない50歳のダーウィン、印刷機、深緑の布装本。
10. `criticism_acceptance_master.png` — ヴィクトリア朝講演室の厳しい議論から、標本を検討する研究者へ。暴力・風刺なし。
11. `later_acceptance_master.png` — 次世代の研究者が標本・嘴・緑の本を共同で検討する作業室。
12. `nature_generations_master.png` — 朝のガラパゴス、親鳥と若鳥、成体と若いゾウガメ、静かな世代の連続。

実際の講演室基準画は `criticism_lecture_master.png` の名称で保存した。1837年のロンドン作業室に後年の時計塔が入った初稿は `gould_finches_london_rejected_big_ben.png` として保持し、曇りガラスと煉瓦壁だけの `gould_finches_london_master.png` へ修正した。採用12枚から44場面を `scripts/build_h035_style01_scenes.sh` で切り出した。

## 公式参照

- https://darwin-online.org.uk/EditorialIntroductions/Chancellor_Keynes_Galapagos.html
- https://www.nhm.ac.uk/our-science/services/collections/zoology/birds/skins/hms-beagle.html
- https://www.nhm.ac.uk/schools/teaching-resources/galapagos-finches-show-beak-differences.html
- https://www.darwinproject.ac.uk/letters/darwins-life-letters/darwin-letters-1821-1836-childhood-beagle-voyage
- https://www.darwinproject.ac.uk/people/about-darwin/darwin-s-photographic-portraits
- https://www.darwinproject.ac.uk/about-darwin/origin-species
