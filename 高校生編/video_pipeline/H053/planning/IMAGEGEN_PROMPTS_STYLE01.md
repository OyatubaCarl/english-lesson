# H053 ImageGen 最終プロンプト設計

共通: `urban evolution and challenges documentary` / 16:9 / 画風01「光彩・劇場アニメ背景」 / 精密な2D線画とセル塗り人物 / 群青の影と自然な暖色光 / 下45%字幕余白 / 読める文字・数字・ロゴなし。現在場面はH15基準の17歳男子と、肩までの黒髪・濃紺ジャケット・無地の図面を持つ38歳前後の女性都市計画家で連続させる。

1. `early_twentieth_century_master` — 20世紀初頭、農村から鉄道で小規模な工業都市へ向かう家族と、まだ低層のurban area。世界人口の大多数が都市外だった変化の入口。数値表示なし。
2. `modern_urban_population_master` — 現代の大都市圏を、中心市街地、集合住宅、郊外、通勤鉄道、周辺の町まで連続する景観で描き、urban areasに多くの人が暮らすことを示す。
3. `urban_opportunities_master` — 同じ駅周辺に雇用の職場、学校、病院・診療所を配置し、異なる住民がaccessする。機会の集中と、混雑・距離・費用によるaccess差もさりげなく残す。
4. `traffic_congestion_master` — 朝の道路渋滞、遅れるbus、混雑する交差点、救急車の進路を都市計画家と高校生が歩道橋から観察。車だけを悪者にしない。
5. `housing_cost_master` — 高額な中心部住宅、狭い賃貸、郊外の建設、相談窓口、長い通勤を一つの住宅市場として描き、住民の能力不足にしない。
6. `air_pollution_master` — 交通・建物暖房・工場など複数源を背景に、計測局、街路樹、歩行者、子ども・高齢者を描く。煙突一本だけを原因にしない。
7. `global_cities_infrastructure_master` — Tokyo、New York、London、Shanghaiを想起させる異なる鉄道・高層格子・歴史街区・河川沿い高層群を、都市計画展示の大きな無地模型として一つの会場に置く。地名やランドマークの誇張なし。
8. `density_infrastructure_master` — 高密度地区の駅、上下水道工事、電力、病院、学校、住宅、parksを同じ断面のような深い街区で描き、densityとcapacityの関係を示す。
9. `sustainable_street_master` — 歩道拡幅、保護された自転車道、低床bus、street trees、横断歩道、荷さばき、車椅子利用者を共存させる実装中のstreet redesign。
10. `green_park_transit_master` — 復元されたgreen parkと雨水池、pedestrians、cyclists、tram・train・bus hub、公共transportationへのinvestmentを一つの地区で描く。
11. `suburbs_move_master` — 一部の家族・若者がcity centerからsuburbsへ移る。住宅費、広さ、家族事情、通勤を示し、全員の一方向移動にしない。
12. `remote_work_urban_rural_master` — urban apartment、suburb home、rural townの三地点を通信で結ぶremote work。高速通信や職種に差が残り、地域の学校・診療所・transportも必要と示す。
13. `inclusive_city_final_master` — 夜明けの市民参加型planning workshop。男子高校生、女性planner、子ども、高齢者、車椅子利用者、商店主、bus運転士が、affordable housing、public transport、green space、安全な歩道を含む無地模型を共同で修正し、everyoneが安心して暮らせるspaceへ締める。

実行方式: 組み込みImageGen。選定画像は `scenes/character_refs/` に保存し、寄り画・クロップ・明度調整で約55〜65カットへ展開する。
