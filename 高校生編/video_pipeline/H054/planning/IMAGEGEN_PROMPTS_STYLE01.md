# H054 ImageGen 最終プロンプト設計

共通: `sports and fair play documentary` / 16:9 / 画風01「光彩・劇場アニメ背景」 / 精密な2D線画とセル塗り人物 / 群青の影と自然な暖色光 / 下45%字幕余白 / 読める文字・数字・ロゴなし。現代場面は20歳の日本人女性短距離・リレー選手、46歳の女性コーチ、H15基準の17歳男子高校生で連続させる。

1. `ancient_truce_safe_passage_master` — 古代ギリシャ。Elisのheraldsがekecheiriaを告げ、武器を置いた使者、選手、観客がオリーブ林の道を安全にOlympiaへ進む。世界中の戦争停止にはしない。
2. `ancient_olympia_games_master` — 古代Olympiaの土の競走路。古代ギリシャの男性競技者、観客、審判、神殿とオリーブ。現代国旗・女性競技者・近代装備なし。
3. `modern_olympic_spirit_master` — 現代の国際競技場。多地域の成人athletes、車いす競技者、役員が入場前に互いを認める。五輪リング・国旗・大会名なし。
4. `years_of_training_master` — 同じ女性短距離選手の夜明けのtraining。スタート練習、フォーム確認、筋力、回復を同じ現実的施設で示す。
5. `discipline_dedication_master` — 選手、女性coach、理学療法士が反復、休養、栄養、けが予防を地道に管理。読める日誌や数値なし。
6. `victory_not_everything_master` — 国際短距離決勝直後。勝者、僅差の敗者、完走を喜ぶ選手、車いす選手が異なる感情を見せ、メダルだけを中心にしない。
7. `sportsmanship_master` — 競技後、主人公が転倒したopponentの安全を確かめ、審判の下で手を差し伸べ、その後互いに握手。競技妨害や自己犠牲にはしない。
8. `doping_system_master` — 競技会のdoping control station。成人選手が通知を受け、representative同席で権利と手順を確認。薬物使用を外見で断定しない。
9. `results_management_hearing_master` — 匿名コードの検体結果を独立panel、科学者、選手と代理人が検討するfair hearing。確認済み判断後にmedalを静かに保管し、即断・見せしめにしない。
10. `strict_testing_chain_master` — 本人がA/B容器を封印し、tamper-evident kit、chain of custody、輸送、認定laboratoryの分析へつなぐ。採尿行為そのものは描かない。
11. `winning_losing_teams_master` — リレー決勝後。winning teamをfansが祝福し、losing teamにも静かなapplause。両teamが互いを称える。
12. `accept_defeat_next_challenge_master` — 主人公がdefeatを受け入れ勝者と握手し、翌朝coachと再びスタートラインへ向かう決意。敗者の屈辱なし。
13. `children_watch_athletes_master` — 地域センターのテレビで競技とsportsmanshipを見る子どもたち。男子高校生も同席し、勝敗より行動に注目。
14. `role_model_final_master` — 夜明けの地域トラックで主人公とcoachが多様な子どもへ安全な走り方を教える。努力、respect、継続のmessageを行動で渡す結末。

実行方式: 組み込みImageGen。選定画像は `scenes/character_refs/` に保存し、寄り画・クロップ・明度調整で約50〜56カットへ展開する。
