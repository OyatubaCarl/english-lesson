# H047 ImageGen 最終プロンプト設計

共通: `modern-social-documentary` / 16:9 / 画風01「光彩・劇場アニメ背景」 / 同じ架空の海辺の都市 / 下45%字幕余白 / 読める文字・価格・ロゴなし。

1. `market_square_overview_master` — 朝の屋内外市場。goodsの青果・パン・生活用品と、修理・配達などservicesが同じ空間で取引され、同じ17歳男子が観察する。
2. `demand_surge_master` — 同じ青緑色ボトルに多くの消費者が集まり、棚の在庫が少なくなる。価格上昇は文字や矢印ではなく、店員の判断と在庫の希少さで示す。
3. `demand_fall_master` — 同じボトルが棚に多く残り、客足が減り、店員が販売条件を見直す。値札の数値は見せない。
4. `company_factory_chain_master` — capitalを集める会議、工場production、製品の出荷、販売収入を設備・賃金へ戻す循環を一つの現実的な工場景観で示す。
5. `competition_quality_master` — 二つの生活用品メーカーが、模倣や敵対でなく、試験・設計・品質検査・消費者比較を通じて品質を高める。
6. `labor_wages_master` — 工場作業員と事務職員が安全に働き、勤務記録と給与処理を経てwagesやsalariesを受け取る。札束演出なし。
7. `household_income_master` — 安定雇用を得た家庭が、夕方の食卓で家計を確認し、食料・住居・学用品を無理なく準備する。豪華さではなく安定を描く。
8. `tax_public_services_master` — 市役所の予算審議を手前に、同じ都市の公立学校・診療所・図書館・公共交通が市民を支える。税から公共サービスへの制度的な流れ。
9. `bank_investment_master` — 銀行員と中小企業経営者が契約を確認し、融資を受けた企業が安全な新設備と人材訓練へinvestmentする。
10. `global_trade_port_master` — 現代の港で輸出品と輸入品が双方向に船・鉄道・トラックへ移る。作業員、防護具、コンテナ、倉庫を現実的に描く。
11. `interconnected_economies_master` — 夕暮れの高台から同じ男子高校生が港・工場・市場・列車・船を見渡す。国境を越える相互依存を光の連なりで示し、ホログラムや地球儀は使わない。

実行方式: 組み込みImageGen。選定画像は `scenes/character_refs/` に保存し、寄り画・クロップ・明度調整で約48カットへ展開する。
