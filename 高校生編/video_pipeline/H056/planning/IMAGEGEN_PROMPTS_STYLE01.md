# H056 ImageGen 最終プロンプト設計

共通: press freedom and journalism documentary / 16:9 / H15基準の画風01「光彩・劇場アニメ背景」 / 精密な2D線画とセル塗り人物 / 群青の影と自然な暖色光 / 下45%字幕余白 / 読める文字・数字・ロゴなし。現代はH15基準の17歳男子高校生、29歳の女性調査記者、52歳の男性編集者を連続させる。Watergateは1972〜1974年の服装・紙・固定電話・タイプライターに限定する。

1. democratic_fourth_estate_master — 現代日本の朝。新聞社のnewsroomを中心に、窓外に国会に似た議会建築、行政庁舎、裁判所を別々に配置。pressは建物の外側から監視し市民へ情報を渡す。法的な第四機関や巨大な柱の図解にしない。
2. pillars_and_citizens_master — 立法の公開審議、行政の記者会見、司法の公開法廷の入口、市民が新聞・放送・図書館で情報を受け取る一続きの公共空間。記者は国家機関の一員ではない。
3. investigative_journalists_master — 29歳女性記者が政府調達記録と企業契約を照合し、現場を撮影し、複数sourceに会う。疑惑だけで断罪せず、52歳editorと反論機会を確認。
4. verification_and_editorial_review_master — newsroomで複数の記者が文書、写真metadata、地図、録音、独立sourceを照合。editorが公開前の根拠、公共性、安全、訂正欄を確認。読める文字なし。
5. investigative_report_public_response_master — 検証済みのinvestigative reportが公開され、市民、監査機関、議会、企業内部の是正担当がそれぞれ行動を始める。記者一人の勝利ではなく制度と市民の応答。
6. watergate_newsroom_master — 1972年Washingtonの新聞社。二人の若い男性reportersが固定電話、紙のメモ、タイプライター、索引カードで侵入事件と選挙運動組織の関係を追う。実在人物の肖像模写・現代機器なし。
7. watergate_sources_evidence_master — 同じ二人が裁判記録、公開文書、複数の電話source、編集会議で事実をcross-check。匿名sourceは影の悪人にせず、身元を守った上で文書と別sourceで裏付ける。
8. watergate_institutions_resignation_master — 1973〜1974年の時系列。上院公聴会、裁判所、捜査資料、最高裁判断、下院の弾劾手続、最後に1974年8月の辞任書を置く手。二人の記者だけで辞任にしたり、同日出来事にしない。
9. accountable_authority_master — 現代の行政・企業双方が検証済み報道を受け、公開の場で説明し、監査と是正へ進む。pressは証拠を示して質問するが、裁判官のように判決を下さない。
10. modern_information_reliability_master — 速報が流れる現代newsroomで、古い画像、切り抜き、偽アカウント、一次資料が混在。記者が日時・場所・原sourceを確認し、未確認情報を保留にする。
11. disinformation_spread_master — 意図的に文脈を切った画像が複数端末へ広がり、市民の判断材料を乱す。一方で訂正、照合、会話へ戻る経路も描く。催眠やSNS悪魔化なし。
12. censorship_imprisonment_master — 架空の権威主義体制。独立newsroomが閉鎖され機材を押収され、記者が拘束施設で弁護士と面会。流血・拷問・国旗なし。別地域では自由な小さなnewsroomが活動を続ける。
13. media_literacy_student_master — H15基準の17歳男子高校生が図書室で、同じ出来事の原source、日付、場所、複数報道、訂正履歴を確認。友人と根拠を話し合い、信じたい情報だけを選ばない。
14. press_freedom_final_master — 朝の地域公開討論。記者が事実を伝え、市民、行政、企業、学生、少数意見の話者が安全に質問し合う。新聞、放送、図書館、公開記録が自由な判断を支える静かな結末。

実行方式: 組み込みImageGen。選定画像は scenes/character_refs/ に原寸のまま保存し、寄り画・クロップ・明度調整で約88〜92カットへ展開する。
