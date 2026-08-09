# H039 ImageGen 最終プロンプト設計

共通: `historical-scene` または `scientific-educational` / 16:9 / 画風01 / 下45%字幕余白 / 読める文字なし。

1. `modern_night_sky_master` — H015/H036と同じ高校生が山の天文台外で夜空を見上げる。
2. `galileo_telescope_workshop_master` — 1609年パドヴァ、ガリレオが細長い屈折望遠鏡のレンズを調整する。
3. `galileo_observes_sky_master` — 屋上で月へ望遠鏡を向ける。遠景に1609年のパドヴァ。
4. `moon_jupiter_discovery_master` — 月の山地と木星の四衛星を観測ノートと視線で結ぶ。読める文字は出さない。
5. `galileo_inquisition_master` — 1633年ローマ異端審問。高齢のガリレオ、会議式の室内、書籍を禁じる判断。
6. `voyager_launch_master` — 1977年、タイタンIIIE/セントールの打上げと管制室。
7. `voyager_jupiter_master` — 大赤斑とイオを背景に、実機構成のVoyagerを描く。
8. `voyager_saturn_master` — 土星の環を横切るVoyager。太陽電池パネルは付けない。
9. `voyager_neptune_master` — 海王星とトリトンを背景にしたVoyager 2。
10. `voyager_interstellar_master` — ヘリオポーズの外で稼働するVoyager。太陽は小さい明るい星。
11. `golden_record_master` — NASA参照画像に準拠した金メッキ銅レコードと保護カバー、1977年の技術者の手。
12. `earth_message_master` — 保護カバー付きレコードを機体側面に固定し、遠い地球と月を背景に置く。
13. `curiosity_centuries_master` — 同じ高校生と小型望遠鏡、深い夜空と遠い星。ガリレオの幽霊やVoyagerの巨大幻影は出さない。

実行: 組み込み ImageGen を使用し、基準画13枚を生成。`final_style01` へ45場面を展開した。
