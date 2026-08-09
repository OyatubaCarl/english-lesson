# ImageGen最終プロンプト記録

## 生成モード

- Codex組み込みImageGen
- 外部画像生成API、CLIフォールバックは不使用
- 生成画像は会話の既定保存先に残し、採用画像を各 `L*/scenes/` へコピー

## 全画像の共通プロンプト

> Create one polished 16:9 cinematic educational story illustration, 1920x1080 composition. Warm contemporary Japanese anime picture-book style, soft painterly light, expressive natural faces, clean anatomy, no split panels, no collage, no captions, no subtitles, no speech bubbles, no readable text, no logos. Preserve each referenced character's face, hair, age, and body proportions exactly; references lock identity only, not clothing. Clothing must match the setting, season, activity and lesson continuity.

人物参照は `shared/face_references/`、Funnics Island参照は `shared/funnics_references/` を使用した。Tomと兄Kentaを混同しないよう、Kentaには「年上・長身・無そばかす」、Tomには「同級生・そばかす・青緑系の差し色」を毎回指定した。

以下の各Scene briefを共通プロンプトと服装指定へ追加したものが最終プロンプトセット。

## 物語整合性の必須判定

画像生成前に、各英文について次を個別に決める。

1. 英文の主語・動作・感情・対象を特定し、その文を最も直接表す瞬間を選ぶ。
2. 時間と層を、現在・過去・未来・計画・回想・想像のいずれかに分ける。計画や想像を実際に起きている出来事として描かない。
3. 登場人物は英文に必要な人物だけにする。「家族の話だから毎回全員」のような固定配置をしない。背景人物も意味を補う場合だけ使う。
4. 小道具は英文理解を助ける場合だけ置く。写真、額縁、手紙、カレンダーなどを定型的に足さず、不自然な連想を生む物は削除する。
5. 場所、時刻、天候、季節、服装、人物の位置関係を前後Sceneと照合する。
6. 一枚だけで英文の中心が読み取れ、同時にレッスン全体の物語を壊さない構図を採用する。

生成後は、キャラクターの似顔だけでなく上記6項目をコンタクトシートで再確認し、状況にそぐわない描写は画像の一貫性より物語整合性を優先して修正する。

## L2 A Day at the Sea

服装固定: Mioは薄黄色半袖＋紺の膝丈短パン、Sakiは珊瑚色の夏ワンピース、Kentaは紺の半袖ラッシュガード＋水着、両親は軽い夏服。

1. `01_last_sunday.png` — Last Sundayの朝、海へ出かける準備をする家族。
2. `02_family_went_to_sea.png` — 家族が山村から海へ到着する広い導入画。
3. `03_blue_beautiful_sea.png` — 青く美しい海をMioが見渡す。
4. `04_bright_clear_sky.png` — 明るく澄んだ空と海辺の家族。
5. `05_kenta_swimming.png` — Kentaがラッシュガード姿で泳ぐ。Tomではなく、年上・無そばかす。
6. `06_kenta_happy_water.png` — 水の中で楽しむKenta。
7. `07_sisters_on_beach.png` — MioとSakiが砂浜で遊ぶ。
8. `08_together_all_day.png` — 家族が一日を通して海辺で過ごす。
9. `09_lunch_bread_fish.png` — 海辺でパンと魚の昼食。
10. `10_delicious_lunch.png` — 昼食をおいしそうに食べる家族。
11. `11_evening_full_hearts.png` — 夕日の海を背に満ち足りて帰る家族。

## L3 A Rainy Afternoon

服装固定: Mioは青灰色の長袖＋チャコールパンツ、Sakiは珊瑚色ニット＋クリーム色スカート、Kentaは紺Tシャツ＋灰色パンツ、Yukaはアイボリーのブラウス＋マスタード色エプロン、Hiroshiは淡青シャツ＋濃色パンツ。

1. `01_rain_falling_outside.png` — 山村の家の外に雨が降る導入画。
2. `02_family_all_in_house.png` — 雨の家を外から見た広角画。窓ごとに別の部屋が見え、Mio、Saki、Kenta、Yuka、Hiroshi、Pochiが一人ずつ別室にいる。
3. `03_mio_reading_room.png` — Mioが自室で本を読む。
4. `04_interesting_forgot_time.png` — 閉じたドアの自室で、Mioだけが面白い物語に夢中になり時計を忘れる。背景人物を出さない。
5. `05_saki_playing_music.png` — 閉じたドアの隣室で、Sakiだけが小さなキーボードを弾く。
6. `06_brother_watching_tv.png` — 別の居間でKentaだけがテレビを見る。年上・無そばかす・紺Tシャツ。
7. `07_pochi_sleeping_chair.png` — 人のいない静かな一角で、Pochiだけが椅子で気持ちよさそうに眠る。
8. `08_mother_cooking_dinner.png` — 台所でYukaが夕食を作る。
9. `09_father_working_study.png` — 書斎でHiroshiが仕事をする。
10. `10_quiet_afternoon_same_house.png` — 壁・床・廊下で分けた一つの家の断面図。各部屋に一人だけを置き、全員が別々のことをする静かな午後を表す。

2026-07-31修正: 「同じ家にいる」を「同じ部屋にいる」と誤読させないよう、個別行動のSceneから家族の見物人を除去。全員を出すのは英文が全員を主語にするScene 2と総括のScene 10だけに限定した。

## L4 My New Friend Tom

服装固定: Mioは紺ブレザー＋白シャツ＋紺リボン＋チェックのスカート、Tomは紺ブレザー＋白シャツ＋青緑ベスト／ネクタイ＋ベージュパンツ。Tomはそばかすを維持し、パーカー禁止。

1. `01_new_boy_came.png` — 先生が新しい生徒Tomを教室前方で紹介。窓外に小さなTeacher Tacos。
2. `02_name_is_tom.png` — Tomが胸に手を当てて自己紹介。Mioは前景から見る。
3. `03_kind_friendly_voice.png` — TomがMioと級友へ親切に話す。掲示物に小さなAunt Ant。
4. `04_tom_felt_shy.png` — Tomが新しい席で緊張してあまり話さない。壁時計にClock character。
5. `05_lunch_tom_happy.png` — 昼休み、TomがMioたちと食事して明るくなる。窓外にTeacher Tacos。
6. `06_funny_stories_laughed.png` — Tomの面白い話でクラスメートが笑う。弁当箱に小さなAunt Ant。
7. `07_became_good_friends.png` — 放課後、MioとTomが荷物をまとめながら友達になったことを示す。廊下遠景にTeacher Tacos。
8. `08_way_home_dark_sky.png` — 暗くなった山村の空の下をMioとTomが歩く。道端遠景にTeacher Tacos。
9. `09_mio_very_happy.png` — 分かれ道でTomが手を振り、Mioが幸せそうに振り返る。生け垣にTeacher Tacos。

## L5 Planning to Visit Grandmother

服装固定: Mioは薄ベージュのカーディガン＋淡青ブラウス＋紺スカート＋濃色タイツ、Sakiは珊瑚色カーディガン＋クリーム色ワンピース＋レギンス、Fumiは薄紫ブラウス＋灰緑カーディガン＋クリーム色エプロン。

L5全体は金曜日の夜に考えている「明日の計画」。全7枚で共通の二層構成を使う。下側の不透明な現実層ではMioとSakiが自宅で計画し、上側にはクリーム色に光る雲形の想像吹き出しを置く。実際の移動や祖母宅での出来事は吹き出しの中だけに描く。

1. `01_tomorrow_saturday.png` — 現実層で姉妹が文字なしカレンダーの翌日を確認。吹き出し内は土曜の朝日と、玄関に準備された2つの旅行鞄。
2. `02_visit_grandmother.png` — 現実層で姉妹が荷造り。吹き出し内は、翌日に祖母Fumiが玄関で2人を迎える想像。
3. `03_early_train_town.png` — 現実層で切符、文字なし路線図、早朝の目覚まし時計を確認。吹き出し内は、翌朝に姉妹だけがローカル列車へ乗る想像。
4. `04_hot_soup_together.png` — 現実層でスープの絵を含む計画ノートを見る姉妹。吹き出し内は、祖母と3人で温かいスープを食べる想像。本シリーズの吹き出し基準画像。
5. `05_read_books_quietly.png` — 現実層で姉妹が本を鞄に詰める。吹き出し内は、翌日の午後に祖母を含む3人が別々の椅子で静かに読む想像。
6. `06_tell_about_tom.png` — 現実層でMioがTomの学校写真と絵だけのノートを使って話す内容を練習し、Sakiが聞く。吹き出し内は、Mioが祖母へTomの写真を見せて話す想像。Tom本人はどちらの空間にも出さない。
7. `07_grandmother_happy.png` — 現実層でMioが写真や小道具を持たず、開いた手で未来の吹き出しを示しながらSakiと計画を終える。吹き出し内は、喜ぶ祖母が姉妹を抱きしめる想像。

2026-07-31最終修正: Scene 4の「妹と一緒に計画し、光る吹き出しで未来を想像する」演出をL5全体へ展開。Scene 4を維持し、それ以外の6枚を同じ吹き出し形状、光、現実／未来の配置で再生成した。

2026-07-31 Scene 7局所修正: 現実層の祖母の額入り写真が遺影を連想させるため完全に除去。組み込みImageGenの編集モードで、Mioの片手を膝に置き、もう片方の開いた手で未来の吹き出しを示す自然な姿勢へ変更した。写真・肖像・額縁・追悼物への置き換えは禁止し、祖母の喜びは吹き出し内の抱擁だけで表現する。

最終局所編集プロンプト要旨: `Change only the lower-left foreground Mio: remove the framed photograph entirely. Do not replace it with any photo, portrait, frame, memorial item, or other prop. Repose her arms and hands naturally while seated cross-legged: one hand relaxed on her lap or knee, the other making a small open-palm hopeful gesture toward the glowing future thought bubble. Preserve Mio, Saki, bags, planning notebook, calendar, room, lighting, composition, and the complete future bubble. No photo, portrait, picture frame, memorial/funeral motif, text, logo, or watermark.`

## L6 Grandmother's Birthday

L5の秋服を継続。Yukaはアイボリーブラウス＋錆茶スカート＋キャメルカーディガン、Hiroshiは淡青シャツ＋茶カーディガン＋濃色パンツ。

1. `01_arrived_birthday.png` — 祖母宅へ到着し、ケーキで今日が誕生日だと気づく。
2. `02_special_gift.png` — 家族が花、写真、本など特別な贈り物を考える。
3. `03_mother_flower.png` — 庭の縁側でYukaが一輪のきれいな花をFumiへ渡す。
4. `04_father_old_picture.png` — Hiroshiが古い家族写真のアルバムを見せ、Fumiが微笑む。
5. `05_saki_story_all_laughed.png` — Sakiが学校の長く面白い話をし、家族全員が笑う。英文2字幕行を1画像に統合。
6. `06_mio_new_book.png` — Mioが新しい本を両手で贈る。
7. `07_grandmother_thank_you.png` — Fumiが家族一人ずつを見て感謝を伝える。
8. `08_very_warm_day.png` — 黄金色の縁側で花、写真、本、ケーキを囲む温かな家族全景。

## L7 My Future Dream

現在場面はL5〜L6の秋服を継続。将来場面の成人Mioは同じ目と肩までの黒髪を残し、20代半ば、セージ色ブラウス＋紺カーディガン＋チャコールスカート。

1. `01_future_dreams.png` — 祖母宅でMio、Saki、Fumiが将来の夢を話し始める。
2. `02_dream_english_teacher.png` — 現在の中学生Mioが小さな黒板と英語絵本を使い、教師の夢を説明する。
3. `03_study_english_daily.png` — 夜の自室で英語を毎日勉強するMio。
4. `04_important_language.png` — 本、地球儀、世界地図を前に英語の大切さを考える。
5. `05_talk_many_countries.png` — 地域交流会で多様な国の若者と話す中学生Mio。
6. `06_many_books_shelf.png` — 自室の大きな本棚から読む本を選ぶ。
7. `07_teach_children.png` — 将来の成人Mioが田舎の明るい教室で子どもに絵カードを教える。
8. `08_help_many_people.png` — 将来の成人Mioが多文化交流センターで高齢者と家族を助ける。
9. `09_keep_that_dream.png` — 現在へ戻り、FumiがMioの手を取って夢を持ち続けるよう励ます。

## L8 Tomorrow's Class Trip

家庭服: Mioは薄黄色半袖ニット＋紺パンツ、Sakiは珊瑚色半袖＋クリーム色スカート、Yukaはアイボリーブラウス＋マスタード色エプロン。

登山服: Mioは薄ベージュの通気性シャツ＋オリーブ色パンツ＋青リュック＋日よけ帽、Tomは青緑の速乾シャツ＋ベージュパンツ＋灰色リュック、Yuukaはクリーム色トレイルジャケット＋濃色パンツ＋緑リュック。

1. `01_class_trip_mountain.png` — 制服の教室で山の写真と登山装備を見ながら遠足説明。窓外にTeacher Tacos。
2. `02_climb_walk_forest.png` — 登山服のMio、Tom、Yuukaが頂上へ続く森の道を登る。遠景にHiker Hippo。
3. `03_lunch_and_hat.png` — 家でMioが弁当と帽子を青いリュックへ入れる。
4. `04_will_it_rain_saki.png` — 心配そうなSakiが雨を尋ね、Mioが聞く。引用と `asked my sister` を1画像に統合。
5. `05_mother_weather_fine.png` — Yukaが縁側から晴れゆく空を見上げる。
6. `06_not_forget_umbrella.png` — Mioが折り畳み傘をリュックの横ポケットへ入れる。
7. `07_fun_day.png` — 山の展望台でMio、Tom、Yuukaが楽しい一日を想像。遠景にTeacher TacosとHiker Hippo。

## L9 A School Day

学校服はL4と同じ。宿題時のMioは紫灰色の長袖＋チャコールパンツ。Sakiは珊瑚色スウェット。日曜のMioはアイボリーの腕まくりシャツ＋青エプロン＋紺パンツ。

1. `01_students_uniform.png` — 朝の昇降口で全生徒が制服を着る。外に小さなTeacher Tacos。
2. `02_classroom_on_time.png` — MioとTomが授業開始前に教室へ入り、Clock characterの壁時計を見る。
3. `03_many_subjects.png` — 一つの教室で幾何模型、理科器具、英語絵本を使う。掲示にAunt Ant、窓外にTeacher Tacos。
4. `04_homework_before_dinner.png` — 私服のMioが夕食前に宿題をする。
5. `05_saki_asks_finish_tonight.png` — 最終差し替え。制服を完全に除き、紫灰色の私服Mioと珊瑚色スウェットのSaki。Sakiが宿題の山を指して尋ねる。
6. `06_yes_i_do.png` — 私服のMioがSakiへ決意を持ってうなずく。
7. `07_sunday_wash_dishes.png` — 日曜、制服は廊下に掛け、エプロン姿のMioが皿を洗う。
8. `08_helping_family_important.png` — Mioが洗い、Yukaが拭き、Sakiがカップを運ぶ。

## L10 The Mountain Promise

登山服はL8と同じ。先生は40歳前後、細い楕円眼鏡、ベージュのつば付き帽、深緑の登山ジャケット、灰茶パンツ、オレンジの安全笛。先生参照は旧L10画像から顔と上半身だけを切り出した `teacher_face.png`。

1. `01_teacher_promise.png` — 登山口で先生が指を一本上げ、クラスと大切な約束をする。遠景にTeacher Tacos。
2. `02_protect_nature.png` — 森と小川を示し、自然を一緒に守ると説明。花のそばに小さなTeacher Tacos。
3. `03_not_hurt_animals.png` — Mio、Tom、Yuukaが鹿と鳥から距離を取り、手で制止する。木陰にTeacher Tacos。
4. `04_read_signs_rules.png` — 道、動物、火気禁止などの絵記号標識を一つずつ確認。遠景にHiker Hippo。
5. `05_friend_asks_every_sign.png` — Tomが木製標識の前で手を上げ、全標識を読むのか先生へ尋ねる。引用と `asked my friend` を1画像に統合。標識裏にTeacher Tacos。
6. `06_teacher_yes_must.png` — 先生がTomへうなずき、絵記号標識を指す。木の後ろにTeacher Tacos。
7. `07_not_touch_flames.png` — 正式な焚き火場。先生が手のひらで止め、生徒は安全線の外。水バケツと防火布。
8. `08_very_dangerous.png` — 管理された火の熱と火の粉を前景にし、MioとTomが真剣に後退。先生と水バケツ。
9. `09_road_careful.png` — 山道から横断歩道へ出る前に先生が左右確認し、生徒は縁石で待つ。ガードレール脇に小さなRoad character。
10. `10_never_forget_words.png` — 夕方の展望台でMioがノートを胸に抱き、先生の言葉を覚えている。背景にTom、Teacher Tacos、Hiker Hippo。
