# H040 ImageGen 最終プロンプト設計

共通: `historical-scene` / 16:9 / 画風01 / 1950年代の英国科学史 / 下45%字幕余白 / 読める文字なし。

1. `dna_double_helix_publication_master` — 1953年キャヴェンディッシュ研究所。若いワトソンとクリックが金属板と棒のDNA模型を慎重に確認する。模型は科学器具として描き、巨大な発光DNAは出さない。
2. `rosalind_lab_identity_master` — 1951〜53年のKing's College London。公式肖像を人物参照に、ロザリンド・フランクリンがX線回折装置の横で実験記録を確認する。
3. `xray_diffraction_experiment_master` — フランクリンと大学院生レイモンド・ゴスリングが、細い水和DNA繊維をX線カメラへ正確に設置する。
4. `photo51_analysis_master` — 暗室の安全灯下、現像したPhoto 51をフランクリンが測定・分析する。X字パターンはKCL参照画像に準拠する。
5. `photo51_shown_without_knowledge_master` — 1953年1月、ウィルキンスが研究室でワトソンへ回折写真を見せる。密かな盗難や悪役芝居にはしない。
6. `nobel_1962_master` — 1962年ストックホルム。クリック、ワトソン、ウィルキンスの三人だけが医学賞受賞者として壇上に立つ。
7. `birkbeck_science_master` — 1950年代後半のBirkbeck。フランクリンがウイルス構造研究を率いる。DNAだけの人物として閉じない。
8. `empty_birkbeck_lab_master` — 1958年のBirkbeck。白衣、研究ノート、ウイルス回折像、未完成模型だけが残る夕方の研究室。病床や墓ではなく、途切れた科学研究で不在を示す。
9. `nobel_rule_archive_master` — 1962年、三つのメダル、三つの賞状、三人分の資料だけを整える係員。架空の四人目や受賞拒否は描かない。
10. `legacy_modern_science_master` — 現代の若い研究者たちがPhoto 51、分子模型、回折像を比較し、フランクリンの仕事を実践の中で記憶する。
11. `quiet_voices_history_master` — 静かな資料室で一人の高校生が、フランクリンの無記名肖像とX線回折像を見つめる。科学史は大声だけで作られないという余韻。

実行方式: 組み込み ImageGen。生成した選定画像は `scenes/character_refs/` に保存し、`final_style01` の動画用場面へ展開する。
