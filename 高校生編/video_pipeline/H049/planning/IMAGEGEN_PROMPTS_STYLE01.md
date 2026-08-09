# H049 ImageGen 最終プロンプト設計

共通: `climate-science and international-cooperation documentary` / 16:9 / 画風01「光彩・劇場アニメ背景」 / 群青の影と自然な暖色光 / 下45%字幕余白 / 読める文字・数値・ロゴなし。現代場面はH15基準の同じ17歳男子高校生と、濃紺ジャケット・低い位置で束ねた黒髪の40歳前後の女性気候科学者で連続させる。

1. `industrial_climate_timeline_master` — 左の18〜19世紀の石炭工場から右の現代都市・港・気象観測所までを同じ大気でつなぎ、industrial revolution以来の急速なclimate変化を時系列で示す。未来都市や燃える地球なし。
2. `global_temperature_observation_master` — 女性科学者と男子高校生が、古い海洋・陸上観測記録、現代の気象観測器、氷床コア、世界平均を示す無地の温暖化ストライプを比較する。約1.1度の正確な数値は字幕に任せ、画像内に数字なし。
3. `fossil_fuel_emissions_master` — 石炭・石油・天然ガスが工場・発電・交通で燃焼しcarbon dioxide emissionを生む現実的な連鎖。煙を過剰な黒雲にせず、科学者が煙道測定を行う。
4. `land_use_agriculture_master` — 森林減少の縁、残された森林、農地、家畜、稲作、水・土壌管理を同じ流域で描き、deforestationとagricultural practicesの関与を示す。農家を悪役にしない。
5. `climate_impacts_master` — 同じ沿岸地域の高潮・海面上昇、内陸の洪水、乾燥した貯水池、強い熱帯低気圧への備えを現実的に示す。犠牲者や破滅的な煽りなし。
6. `ecosystems_species_master` — 沿岸湿地、白化したサンゴの一部、森林、渡り鳥、両生類など複数ecosystemsとspeciesを科学者が調査し、extinction riskを生息地の縮小で示す。
7. `kyoto_protocol_1997_master` — 1997年の京都の国際会議。実在人物を特定せず、多国の代表が一つのProtocolを採択し、先進国等の代表へ異なる厚み・色の削減目標フォルダーが渡る。国旗や読める条約名なし。
8. `paris_agreement_2015_master` — 2015年パリの国際会議。多くの国の代表、女性科学者、共通のAgreement、産業革命前基準からwell below 2度・1.5度への努力を示す文字なしの二本の抑えた温度帯。達成済みの祝賀にしない。
9. `renewable_energy_investment_master` — 太陽光・風力・地熱または小水力、送電網、蓄電、保守訓練、投資判断を同じ地域計画として描く。設備を自然破壊なしの魔法として見せない。
10. `emissions_regulation_master` — 自動車検査、公共交通・電動車への移行、工場煙道の測定と設備改善を行政・技術者・企業が共同で進め、carsとfactoriesのemissionsをregulateする。
11. `transboundary_climate_master` — 一つの国境を越えて続く河川・大気・海岸で、上流の豪雨、下流の洪水、遠方の煙、海流が複数地域を結ぶ。一国だけでは解けないことを実景で示す。
12. `international_cooperation_master` — 複数地域の科学者、技術者、防災担当、地域住民が観測装置、早期警戒、再生可能設備、適応計画を共有する。外交官の握手だけにしない。
13. `sustainable_generations_final_master` — 同じ男子高校生、子ども、働く世代、高齢者が、公共交通、断熱住宅、緑地、再生可能電力、復元された湿地のある現実的な海辺の街で協力する。sustainable societyを世代共通のgoalとして結ぶ。

実行方式: 組み込みImageGen。選定画像は `scenes/character_refs/` に保存し、寄り画・クロップ・明度調整で約80カットへ展開する。
