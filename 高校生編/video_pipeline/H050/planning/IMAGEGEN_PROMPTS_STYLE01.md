# H050 ImageGen 最終プロンプト設計

共通: `education-rights and equal-opportunity documentary` / 16:9 / 画風01「光彩・劇場アニメ背景」 / 精密な2D線画とセル塗り人物 / 群青の影と自然な暖色光 / 下45%字幕余白 / 読める文字・数字・ロゴなし。現代場面はH15基準の17歳男子、えんじ色カーディガンの同年代女子、濃紺ジャケットの女性教員で連続させる。

1. `education_basic_right_master` — 夜明けの公立学校へ、年齢・家庭背景・身体条件の異なる子どもたちが同じ開いた入口から入る。教員と17歳男子が迎え、educationがevery personのbasic rightであることを具体的な場面で示す。
2. `un_declaration_1948_master` — 1948年12月の国連総会を参考にした歴史的会議場。多地域の代表が世界人権宣言を採択し、Article 26の教育権を一枚の無地文書と静かな挙手で示す。実在人物の肖像や読める文書本文なし。
3. `birthplace_income_opportunity_master` — 同年齢の子どもたちが、都市の近距離通学、山間部の長い通学、家族の限られた教育費を比べる現実的な連作構図。出生国・地域・family incomeでopportunityが違うが、尊厳と主体性は等しく描く。
4. `out_of_school_children_master` — 遠い学校を見渡す地方の少女、避難先の仮設学習スペース、弟を世話する少年、車椅子で段差に阻まれる子を一つの地域支援拠点で結ぶ。泣き顔や児童労働の見世物化なし。
5. `developed_country_access_quality_master` — 同じ豊かな都市圏の二校。片方は図書・実験・支援員が充実し、もう片方は古い設備・長い通学・不安定な通信環境。qualityとaccessのgapを、学生の能力差ではなく資源差として示す。
6. `family_income_career_master` — 同じ17歳男子と女子が進路相談。片方の家庭では学費・交通・生活費を慎重に計算し、もう片方には静かな学習机と進学資料がある。careerの選択肢がincomeの影響を受けるが決定済みではない。
7. `education_beyond_knowledge_master` — 同じ教室で、教科書の学習に加え、科学実験、討論、音楽・美術、共同問題解決を行う。educationがknowledge伝達だけでないことを、手と表情の交流で示す。
8. `identity_responsibility_master` — 17歳男子と女子が自分の意見を発表し、仲間の違いを聞き、地域の高齢者と防災地図を作る。individualのidentity形成とresponsible memberへの成長を示す。
9. `scholarship_tuition_master` — 女子高校生と家族が教員・支援担当者と奨学金、授業料減免、住居・通学支援を相談し、後景に開かれた大学実習室。封筒の札束や一発逆転の祝賀なし。
10. `slow_reform_master` — 同じ地域の数年にわたる改善を一方向の時間軸で示す。古い階段へスロープ、遠隔地へのスクールバス、図書室の整備、教員研修、少しずつ埋まる教室。reformは遅いが進んでいる。
11. `same_opportunity_every_child_master` — 幼い子どもから高校生までが、段差のない入口、十分な机、教材、支援員、静かな学習環境へ等しく到達する。結果の同一化ではなくsame opportunityを描く。
12. `education_gap_closing_master` — 以前は離れていた二つの学校・家庭・地域が、交通、通信、教員交流、奨学金で結ばれ、進学・職業訓練・地域参加へ続く。gapが一瞬で消えるのではなく縮まり始める途中を示す。
13. `equal_society_final_master` — 夕暮れの地域学習センター。子ども、高校生、大学生、働く世代、高齢者が同じ灯りの下で学び教え合い、17歳男子・女子・女性教員が見守る。equal educationからinclusive societyへ続く静かな希望で結ぶ。

実行方式: 組み込みImageGen。選定画像は `scenes/character_refs/` に保存し、寄り画・クロップ・明度調整で約75〜80カットへ展開する。
