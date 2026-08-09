#!/usr/bin/env python3
"""中学生編・語彙補強ドラフト生成。

小中学校.xlsx にあるが index.html のどこにも出てこない 129 語を、
既存「エクストラ語彙」レッスン(L31-45)のテーマに沿った追加本文として執筆し、
index.html と同じ <span class="w" data-base data-ipa data-ja data-pos> マークアップで
スタンドアロン HTML を出力する。

※ index.html 本体は一切編集しない。本ドラフトはレビュー用＋将来の貼り付け素材。
出力: 中学生編_語彙補強ドラフト.html
"""
import re, html as _html

OUT = "中学生編_語彙補強ドラフト.html"

# ---- 語彙辞書: base -> (ipa, ja, pos, disp) ----  disp 省略時は base を表示
V = {
 # 時間と数
 "eleven":("/ɪˈlɛvən/","11","num"),"thirteen":("/ˌθɜːrˈtiːn/","13","num"),
 "fourteen":("/ˌfɔːrˈtiːn/","14","num"),"sixteen":("/ˌsɪksˈtiːn/","16","num"),
 "seventeen":("/ˌsɛvənˈtiːn/","17","num"),"eighteen":("/ˌeɪˈtiːn/","18","num"),
 "nineteen":("/ˌnaɪnˈtiːn/","19","num"),"ninety":("/ˈnaɪnti/","90","num"),
 "sixth":("/sɪksθ/","6番目の","adj"),"eighth":("/eɪtθ/","8番目の","adj"),
 "tenth":("/tɛnθ/","10番目の","adj"),"eleventh":("/ɪˈlɛvənθ/","11番目の","adj"),
 "twelfth":("/twɛlfθ/","12番目の","adj"),"fourteenth":("/ˌfɔːrˈtiːnθ/","14番目の","adj"),
 "january":("/ˈdʒænjuˌɛri/","1月","noun","January"),"february":("/ˈfɛbruˌɛri/","2月","noun","February"),
 "september":("/sɛpˈtɛmbər/","9月","noun","September"),"october":("/ɑːkˈtoʊbər/","10月","noun","October"),
 "november":("/noʊˈvɛmbər/","11月","noun","November"),
 "tuesday":("/ˈtuːzdeɪ/","火曜日","noun","Tuesday"),"thursday":("/ˈθɜːrzdeɪ/","木曜日","noun","Thursday"),
 "date":("/deɪt/","日付","noun"),"pm":("/ˌpiːˈɛm/","午後","adv","p.m."),
 "holiday":("/ˈhɑːlədeɪ/","休日","noun"),
 # 体と健康
 "tooth":("/tuːθ/","歯","noun"),"neck":("/nɛk/","首","noun"),
 "injure":("/ˈɪndʒər/","傷める","verb"),"blind":("/blaɪnd/","目の見えない","adj"),
 "disabled":("/dɪsˈeɪbəld/","体の不自由な","adj"),
 # 家の中・身の回り
 "candle":("/ˈkændəl/","ろうそく","noun"),"doll":("/dɑːl/","人形","noun"),
 "toy":("/tɔɪ/","おもちゃ","noun"),"towel":("/ˈtaʊəl/","タオル","noun"),
 "iron":("/ˈaɪərn/","アイロン","noun"),"apron":("/ˈeɪprən/","エプロン","noun"),
 "cap":("/kæp/","ぼうし","noun"),"shirt":("/ʃɜːrt/","シャツ","noun"),
 "oil":("/ɔɪl/","油","noun"),"list":("/lɪst/","リスト","noun"),
 "stationery":("/ˈsteɪʃəˌnɛri/","文房具","noun"),"trash":("/træʃ/","ごみ","noun"),
 "pair":("/pɛər/","ひと組","noun"),
 # 町と乗り物
 "airplane":("/ˈɛərˌpleɪn/","飛行機","noun"),"subway":("/ˈsʌbˌweɪ/","地下鉄","noun"),
 "railway":("/ˈreɪlˌweɪ/","鉄道","noun"),"sidewalk":("/ˈsaɪdˌwɔːk/","歩道","noun"),
 "dam":("/dæm/","ダム","noun"),"palace":("/ˈpæləs/","宮殿","noun"),
 "hole":("/hoʊl/","穴","noun"),"extinguisher":("/ɪkˈstɪŋɡwɪʃər/","消火器","noun"),
 # 職業と人
 "actor":("/ˈæktər/","俳優","noun"),"professor":("/prəˈfɛsər/","教授","noun"),
 "policeman":("/pəˈliːsmən/","警察官","noun"),"prince":("/prɪns/","王子","noun"),
 "host":("/hoʊst/","司会・主人役","noun"),"barber":("/ˈbɑːrbər/","理髪師","noun"),
 "pal":("/pæl/","仲間","noun"),
 # 動物と自然
 "monkey":("/ˈmʌŋki/","サル","noun"),"dinosaur":("/ˈdaɪnəˌsɔːr/","恐竜","noun"),
 "feather":("/ˈfɛðər/","羽根","noun"),"nest":("/nɛst/","巣","noun"),
 "sunshine":("/ˈsʌnˌʃaɪn/","日光","noun"),"shade":("/ʃeɪd/","日かげ","noun"),
 "glacier":("/ˈɡleɪʃər/","氷河","noun"),"rainwater":("/ˈreɪnˌwɔːtər/","雨水","noun"),
 "seasonal":("/ˈsiːzənəl/","季節の","adj"),"pork":("/pɔːrk/","ぶた肉","noun"),
 # 気持ち・様子
 "lucky":("/ˈlʌki/","幸運な","adj"),"luck":("/lʌk/","運","noun"),
 "hopeful":("/ˈhoʊpfəl/","希望に満ちた","adj"),"helpful":("/ˈhɛlpfəl/","助けになる","adj"),
 "playful":("/ˈpleɪfəl/","遊び好きな","adj"),"scary":("/ˈskɛri/","こわい","adj"),
 "sleepy":("/ˈsliːpi/","眠い","adj"),"dear":("/dɪər/","親愛なる","adj"),
 "fond":("/fɑːnd/","好んで","adj"),"unhappy":("/ʌnˈhæpi/","不幸な","adj"),
 "unfair":("/ʌnˈfɛər/","不公平な","adj"),"awesome":("/ˈɔːsəm/","すばらしい","adj"),
 "crazy":("/ˈkreɪzi/","夢中の","adj"),"noisy":("/ˈnɔɪzi/","うるさい","adj"),
 "foolish":("/ˈfuːlɪʃ/","おろかな","adj"),"fool":("/fuːl/","おろか者","noun"),
 "successful":("/səkˈsɛsfəl/","成功した","adj"),"stylish":("/ˈstaɪlɪʃ/","おしゃれな","adj"),
 "mini":("/ˈmɪni/","小型の","adj"),"flat":("/flæt/","平らな","adj"),
 "dry":("/draɪ/","乾いた","adj"),
 # 学校・ことば
 "absent":("/ˈæbsənt/","欠席の","adj"),"spell":("/spɛl/","つづる","verb"),
 "spelling":("/ˈspɛlɪŋ/","つづり","noun"),"syllable":("/ˈsɪləbəl/","音節","noun"),
 "rhyme":("/raɪm/","韻（いん）","noun"),"fiction":("/ˈfɪkʃən/","作り話・小説","noun"),
 "musical":("/ˈmjuːzɪkəl/","音楽の","adj"),"feedback":("/ˈfiːdˌbæk/","助言・反応","noun"),
 "selection":("/sɪˈlɛkʃən/","選ぶこと","noun"),
 # 連絡・行動
 "announce":("/əˈnaʊns/","知らせる","verb"),"announcement":("/əˈnaʊnsmənt/","お知らせ","noun"),
 "invite":("/ɪnˈvaɪt/","招待する","verb"),"lend":("/lɛnd/","貸す","verb"),
 "advise":("/ədˈvaɪz/","助言する","verb"),"pull":("/pʊl/","引く","verb"),
 "stick":("/stɪk/","はりつける","verb"),"row":("/roʊ/","列","noun"),
 "donate":("/ˈdoʊneɪt/","寄付する","verb"),"reservation":("/ˌrɛzərˈveɪʃən/","予約","noun"),
 "sold":("/soʊld/","売れた(sellの過去)","verb"),"satisfy":("/ˈsætɪsˌfaɪ/","満足させる","verb"),
 "misunderstand":("/ˌmɪsʌndərˈstænd/","誤解する","verb"),
}

# ---- 付録（高校編向き・発展語: 本文には織り込まず一覧表で提示）----
APPENDIX = {
 "heaven":("/ˈhɛvən/","天国","noun"),"sacred":("/ˈseɪkrɪd/","神聖な","adj"),
 "army":("/ˈɑːrmi/","軍隊","noun"),"populous":("/ˈpɑːpjələs/","人口の多い","adj"),
 "illiterate":("/ɪˈlɪtərət/","読み書きできない","adj"),
 "interdependent":("/ˌɪntərdɪˈpɛndənt/","相互に依存した","adj"),
 "kindliness":("/ˈkaɪndlinəs/","親切","noun"),"lullaby":("/ˈlʌləˌbaɪ/","子守歌","noun"),
 "arrow":("/ˈæroʊ/","矢","noun"),"jewel":("/ˈdʒuːəl/","宝石","noun"),
 "custom-made":("/ˈkʌstəmˈmeɪd/","あつらえの","adj"),"next-door":("/ˈnɛkstˈdɔːr/","となりの","adj"),
 "well-off":("/ˈwɛlˈɔːf/","裕福な","adj"),"unused":("/ʌnˈjuːzd/","使われていない","adj"),
 "ahead":("/əˈhɛd/","前方に","adv"),"anyway":("/ˈɛniˌweɪ/","とにかく","adv"),
 "everywhere":("/ˈɛvriˌwɛər/","どこでも","adv"),"forth":("/fɔːrθ/","前へ","adv"),
 "tightly":("/ˈtaɪtli/","きつく","adv"),
}

# ---- 本文（jp-body は @base で新出語をマーク）----
PASSAGES = [
 dict(lesson="L39", theme="時間と数", title="カレンダーと数の一週間",
   desc="新出文法なし。月・曜日・数や順番をあらわす語を確認します。",
   ex=[("School starts again in September.","9月にまた学校が始まる。"),
       ("My grandmother is ninety years old.","祖母は90歳だ。")],
   jp=[
    "新しい手帳を開くと、一年の暦が目に入ります。学校がいちばん忙しくなるのは、@september に新学期が始まってから、@october、@november と続く秋です。",
    "年が明けた @january の最初の登校日は @tuesday でした。冬休み明けのテストは、その週の @thursday です。わたしは大切な @date を、赤いペンで大きくかこみました。",
    "家族の年齢もちょうど節目です。姉は @eighteen 歳、兄は @nineteen 歳、わたしはこの @february で @fourteen 歳になります。祖母は今年、なんと @ninety 歳のお祝いをします。",
    "発表の順番は出席番号で決まりました。わたしは前から @sixth 番目、親友は @eighth 番目、転校生は @tenth 番目です。最後の三人は @eleventh、@twelfth、そして @fourteenth 番目に並びました。",
    "合唱に参加するのは @eleven 人。歌う曲は、@thirteen、@sixteen、@seventeen と番号のついた三曲です。練習はいつも放課後、@pm 三時から。次の @holiday には、三曲を通して歌う予定です。",
   ],
   en="When I open my new planner, the whole year's calendar comes into view. School gets busiest in autumn, after the new term starts in September and continues through October and November. The first school day in January was a Tuesday, and the test after winter break is on Thursday that week, so I circled the important date in red. My family's ages are at turning points too: my older sister is eighteen, my brother is nineteen, and I will turn fourteen this February. My grandmother will even celebrate her ninetieth birthday this year. The order of the presentations was decided by our class numbers. I am sixth from the front, my best friend is eighth, and the new student is tenth; the last three stood in the eleventh, twelfth, and fourteenth places. Eleven of us join the chorus, and we sing three songs numbered thirteen, sixteen, and seventeen. We always practice after school from three p.m., and next holiday we plan to sing all three songs straight through."),

 dict(lesson="L34", theme="体と健康", title="ぐらぐらの歯",
   desc="新出文法なし。体の部位や、体の状態に関する語を確認します。",
   ex=[("One back tooth feels loose.","奥歯が一本ぐらつく。"),
       ("Don't injure your neck.","首を傷めないで。")],
   jp=[
    "朝、鏡の前で歯をみがいていると、奥の @tooth が一本ぐらぐらしているのに気づきました。ゆうべ転んで @neck も少しひねったようで、振り向くと鈍く痛みます。",
    "保健室の先生は『無理に動かすと、かえって筋を @injure することがあるよ』と言って、冷たいタオルをそっと当ててくれました。",
    "保健の授業では、目の見えない、つまり @blind の人や、体の不自由な、つまり @disabled の人が、安心して町を歩けるくふうを学びました。点字ブロックや音の出る信号は、その大切なくふうのひとつです。",
   ],
   en="This morning, while I was brushing my teeth in front of the mirror, I noticed that one back tooth was loose. I had fallen the night before and seemed to have twisted my neck a little, so it ached dully when I turned around. The school nurse said, \"If you move it too hard, you may injure the muscle even more,\" and she gently placed a cold towel on it. In our health class, we learned about clever ideas that help blind people and disabled people walk around town safely. Braille blocks and sound-making traffic lights are some of these important ideas."),

 dict(lesson="L41", theme="家の中・身の回り", title="日曜日のかたづけ",
   desc="新出文法なし。家の中の道具や身の回りの物をあらわす語を確認します。",
   ex=[("Mother put on her apron.","母はエプロンをつけた。"),
       ("I ironed a wrinkled shirt.","しわのシャツにアイロンをかけた。")],
   jp=[
    "日曜日の朝、母は @apron をつけて台所に立ち、フライパンに @oil をひいて朝食を作っています。わたしは洗面所から、乾いた @towel を運びました。",
    "自分の部屋をかたづけます。たなには、小さな @doll と、昔よく遊んだ @toy が並んでいます。引き出しには、ペンやノートなどの @stationery と、やることを書いた @list が入っています。",
    "クローゼットからは、しわになった @shirt を出して @iron をかけ、おそろいの @pair のくつ下をそろえました。お気に入りの @cap も、たなにもどします。",
    "夜、机の上で小さな @candle をともすと、部屋がやわらかい光につつまれました。いらない紙は、まとめて @trash に捨てて、一日が終わります。",
   ],
   en="On Sunday morning, my mother stood in the kitchen with her apron on, putting oil in the pan to make breakfast. I carried a dry towel from the washroom. Then I tidied my own room. On the shelf stood a small doll and a toy I used to play with a lot. In the drawer were stationery such as pens and notebooks, and a list of things to do. From the closet I took out a wrinkled shirt and pressed it with an iron, and I matched a pair of socks. I put my favorite cap back on the shelf too. At night, when I lit a small candle on my desk, the room was wrapped in soft light. I threw all the wastepaper into the trash, and the day came to an end."),

 dict(lesson="L32", theme="町と乗り物", title="遠い町への旅",
   desc="新出文法なし。乗り物や町の施設をあらわす語を確認します。",
   ex=[("We took the subway downtown.","地下鉄で中心街へ行った。"),
       ("Watch the hole in the road.","道の穴に気をつけて。")],
   jp=[
    "夏休み、家族で遠くの町へ出かけました。空港から大きな @airplane に乗り、着いてからは @subway や @railway を乗りついで、目的地へ向かいます。",
    "駅を出て @sidewalk を歩いていくと、道のとちゅうに工事中の @hole があり、係の人が『足もとに気をつけて』と声をかけてくれました。",
    "丘の上には、昔の王さまが住んでいたという立派な @palace が建っています。遠くの谷には大きな @dam が見え、町の電気と水をささえているそうです。",
    "建物の入り口には、赤い消火器、つまり @extinguisher が置かれていました。『もしものときの備えだよ』と父が教えてくれました。",
   ],
   en="During summer vacation, my family traveled to a faraway town. We boarded a big airplane at the airport, and after we arrived we changed between the subway and the railway to reach our destination. As we walked along the sidewalk from the station, there was a hole in the road under construction, and a worker called out, \"Watch your step.\" On top of a hill stood a grand palace where an old king was said to have lived. In the distant valley we could see a large dam, which supports the town's electricity and water. At the entrance of the building, a red fire extinguisher was placed. \"It's a preparation for emergencies,\" my father told me."),

 dict(lesson="L43", theme="職業と人", title="文化祭の大人たち",
   desc="新出文法なし。職業や人の役わりをあらわす語を確認します。",
   ex=[("She used to be an actor.","彼女は俳優だった。"),
       ("A kind policeman helped us.","親切な警察官が助けてくれた。")],
   jp=[
    "町の文化祭には、いろいろな大人が集まります。劇の指導をするのは、もとは舞台の @actor だった人。科学の話をしてくれるのは、大学の @professor です。",
    "会場の入り口では、やさしい @policeman が交通整理をし、司会の @host が元気な声でお客さんをむかえています。",
    "髪を切る体験コーナーでは、町の @barber が、子どもたちに道具の使い方を見せてくれました。",
    "わたしの幼なじみ、つまり仲のよい @pal は、王子、つまり @prince の役で劇に出ます。少し照れながらも、堂々と演じていました。",
   ],
   en="Many kinds of grown-ups gather at the town culture festival. The person who directs the play used to be a stage actor, and the one who talks about science is a university professor. At the entrance of the hall, a kind policeman directs the traffic, and the host welcomes the guests in a cheerful voice. At the hands-on haircut corner, the town barber shows the children how to use the tools. My childhood friend, my close pal, appears in the play as a prince. Though a little shy, he performed with great confidence."),

 dict(lesson="L36", theme="動物と自然", title="祖父の裏山で",
   desc="新出文法なし。動物や自然をあらわす語を確認します。",
   ex=[("A monkey sat in the tree.","サルが木にすわっていた。"),
       ("We rested in the shade.","日かげで休んだ。")],
   jp=[
    "祖父の家の裏山を歩くと、木の上で @monkey が遊んでいました。枝のあいだには、鳥が小枝を集めて作った @nest があり、一枚の白い @feather が落ちていました。",
    "明るい @sunshine の下は暑いので、わたしたちは大きな木の @shade で休みました。葉のすきまから、@seasonal な草花の色が見えます。",
    "博物館では、大昔に生きていた @dinosaur の骨と、はるか北の @glacier の写真が展示されていました。",
    "畑のわきには、@rainwater をためる大きなおけがあります。昼食には、祖母が育てた野菜と @pork を使った、温かい料理が並びました。",
   ],
   en="As I walked up the hill behind my grandfather's house, a monkey was playing in a tree. Among the branches was a nest that a bird had built from small twigs, and a single white feather had fallen below. It was hot under the bright sunshine, so we rested in the shade of a large tree. Through the gaps in the leaves, we could see the colors of the seasonal flowers. At the museum, the bones of a dinosaur that lived long ago and photographs of a far-northern glacier were on display. Beside the field there is a large barrel that collects rainwater. For lunch, warm dishes made with vegetables my grandmother grew and some pork were lined up on the table."),

 dict(lesson="L31", theme="気持ち・様子", title="運のいい一日",
   desc="新出文法なし。気持ちや様子をあらわす形容詞を中心に確認します。",
   ex=[("I felt very lucky today.","今日はとても運がよかった。"),
       ("That story was a little scary.","その話は少しこわかった。")],
   jp=[
    "今日はとても運がいい、つまり @lucky な一日でした。朝いちばんに見つけた四つ葉のクローバーが、きっと @luck を運んでくれたのだと思います。",
    "親友はいつも前向きで @hopeful、そして困っている人にすぐ手を貸す @helpful な人です。妹は子犬のように @playful で、家の中はいつも少し @noisy です。弟は新しいゲームに @crazy なほど夢中で、うまくいくたびに『@awesome！』と大声をあげます。",
    "夜、こわい、つまり @scary な話を聞いたあとは、なかなか眠れません。それでも次の朝には、@sleepy な顔のまま食卓に着きます。",
    "祖母からの手紙は、いつも『@dear なわたしのまごへ』で始まります。祖母は古い物を大切にするのが @fond で、その気持ちがとてもうれしいのです。",
    "試合に負けて @unhappy になった日もありました。判定が @unfair に思えてくやしくて、つい @foolish なことを言い、@fool のようにふるまってしまったのです。",
    "それでも、最後までやりぬいた発表は @successful に終わりました。姉が @lend してくれた @stylish で @mini なバッグを持ち、底の @flat なくつをはいて、@dry な秋風の中を、胸を張って歩いて帰りました。",
   ],
   en="Today was a very lucky day. I think the four-leaf clover I found first thing in the morning surely brought me luck. My best friend is always positive and hopeful, and she is the helpful kind who lends a hand to anyone in trouble. My little sister is playful like a puppy, so our house is always a little noisy. My little brother is crazy about a new game, and every time it goes well he shouts, \"Awesome!\" After hearing a scary story at night, I can hardly fall asleep, yet the next morning I sit at the table with a sleepy face. My grandmother's letters always begin with \"To my dear grandchild.\" She is fond of taking good care of old things, and that feeling makes me very happy. There were days when I became unhappy after losing a game. The decision seemed unfair, and feeling bitter, I said something foolish and acted like a fool. Even so, the presentation I carried through to the end was successful. Carrying the stylish, mini bag my sister lent me and wearing flat-soled shoes, I walked home with my chest held high through the dry autumn wind."),

 dict(lesson="L37", theme="学校・ことば", title="ことばの教室",
   desc="新出文法なし。学校生活やことばの学習に関する語を確認します。",
   ex=[("He was absent for three days.","彼は3日間欠席した。"),
       ("How do you spell this word?","この語はどうつづりますか。")],
   jp=[
    "かぜで三日 @absent だった友だちが、今日ひさしぶりに登校しました。みんな笑顔でむかえます。",
    "国語と英語の時間は、ことばの学習です。新しい単語を一文字ずつ @spell して、正しい @spelling を覚えます。先生は『この語は二つの @syllable に分かれるよ』と手をたたいて教えてくれました。",
    "詩の授業では、行の終わりの音をそろえる @rhyme のおもしろさを学びました。",
    "図書の時間、わたしは物語、つまり @fiction のたなから一冊を選びました。たくさんの本の中からの @selection は、いつもわくわくします。",
    "放課後の @musical クラブでは、先生が一人ひとりの歌に、ていねいな @feedback をくれます。",
   ],
   en="A friend who had been absent for three days with a cold came to school today after a long time, and everyone welcomed her with a smile. In our Japanese and English classes, we study words. We spell new words one letter at a time and learn the correct spelling. The teacher clapped her hands and taught us, \"This word breaks into two syllables.\" In the poetry lesson, we learned how interesting rhyme is, matching the sounds at the ends of the lines. During library time, I chose a book from the fiction shelf. Making a selection from so many books is always exciting. In the after-school musical club, the teacher gives careful feedback on each person's singing."),

 dict(lesson="L44", theme="連絡・行動", title="お祝いの準備",
   desc="新出文法なし。連絡や行動をあらわす動詞を中心に確認します。",
   ex=[("The school announced the trip.","学校は遠足を知らせた。"),
       ("I invited my friend.","友だちを招待した。")],
   jp=[
    "校内放送が、来週の遠足について @announce しました。その @announcement を聞いて、みんなわくわくしています。",
    "わたしは仲のよい友だちを、家のお祝いに @invite することにしました。先生は『早めに会場の @reservation をしておくといいよ』と @advise してくれました。",
    "準備の日、重い机を友だちと二人で、片方が @pull し、もう片方が押して、ひと @row にきれいに並べます。かべには、飾りをテープで @stick しました。",
    "去年使った品物のうち、まだ使えるものは施設に @donate しました。残りはバザーで売られ、午前中にはほとんど @sold になりました。",
    "みんなが笑顔で帰っていく姿を見て、わたしはとても @satisfy しました。『きみのおかげだよ』という言葉を、はじめは冗談かと @misunderstand しましたが、本気だと分かって、胸が温かくなりました。",
   ],
   en="The school broadcast announced next week's field trip. Hearing that announcement, everyone got excited. I decided to invite my close friends to a celebration at my house. The teacher advised me, \"You'd better make a reservation for the hall early.\" On the day of preparation, my friend and I lined up the heavy desks neatly in one row, with one of us pulling and the other pushing. We stuck the decorations on the wall with tape. Among the items we used last year, those still usable we donated to a care home. The rest were sold at the bazaar, and most were sold out by the morning. Seeing everyone go home with a smile, I felt very satisfied. At first I misunderstood the words \"It's all thanks to you\" as a joke, but when I realized they were sincere, my heart grew warm."),
]

# ---------- レンダリング ----------
def esc(s): return _html.escape(s, quote=True)

TOKEN = re.compile(r"@([A-Za-z]+)")
def render_jp(text):
    used=[]
    def rep(m):
        b=m.group(1).lower()
        if b not in V:
            raise SystemExit(f"未定義の@語: {b}")
        ipa,ja,pos=V[b][0],V[b][1],V[b][2]
        disp=V[b][3] if len(V[b])>3 else b
        used.append(b)
        return (f'<span class="w" data-base="{esc(b)}" data-ipa="{esc(ipa)}" '
                f'data-ja="{esc(ja)}" data-pos="{esc(pos)}">{esc(disp)}</span>')
    out=TOKEN.sub(rep, text)
    return out, used

def build():
    blocks=[]; all_used=[]
    for p in PASSAGES:
        paras=[]; pu=[]
        for para in p["jp"]:
            h,u=render_jp(para); paras.append(f"        <p>{h}</p>"); pu+=u
        all_used+=pu
        ex="".join(f'<li><em>{esc(e)}</em> <span class="ja">― {esc(j)}</span></li>' for e,j in p["ex"])
        chips=" ".join(f'<span class="chip">{esc(V[b][3] if len(V[b])>3 else b)}</span>'
                       for b in dict.fromkeys(pu))
        blocks.append(f'''
<section class="lesson" data-augments="{p['lesson']}">
  <h2>{esc(p['theme'])} ― 追加本文「{esc(p['title'])}」 <small>（{p['lesson']} に追記想定 / 新出 {len(dict.fromkeys(pu))} 語）</small></h2>
  <div class="newwords">新出語: {chips}</div>
  <div class="grammar-box">
    <span class="g-title">文法ターゲット：エクストラ語彙：{esc(p['theme'])}</span>
    <p class="g-desc">{esc(p['desc'])}</p>
    <p class="g-ex-label">例文：</p>
    <ul>{ex}</ul>
  </div>
  <h3 class="passage-title">本文「{esc(p['title'])}」（日本語混じり / index貼り付け用 .w マークアップ）</h3>
  <div class="jp-body">
{chr(10).join(paras)}
  </div>
  <h3 class="passage-title">英語本文（統合時に <code>en-body</code> として we タグ付け）</h3>
  <div class="en-plain"><p>{esc(p['en'])}</p></div>
</section>''')

    # 付録表
    rows="".join(
      f'<tr><td>{esc(d if len(V.get(d,()))<4 else d)}</td><td class="ipa">{esc(a[0])}</td>'
      f'<td>{esc(a[1])}</td><td>{esc(a[2])}</td></tr>'
      for d,a in sorted(APPENDIX.items()))

    covered=sorted(set(all_used))
    body="\n".join(blocks)
    doc=f'''<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>中学生編 語彙補強ドラフト</title>
<style>
:root{{--ink:#222;--muted:#777;--accent:#2563eb;--line:#e5e7eb;--bg:#fafafa;}}
*{{box-sizing:border-box}}
body{{font-family:"Hiragino Kaku Gothic ProN",system-ui,sans-serif;color:var(--ink);
 line-height:1.95;max-width:840px;margin:0 auto;padding:24px 18px 80px;background:#fff}}
h1{{font-size:1.5rem;border-bottom:3px solid var(--accent);padding-bottom:.4em}}
.lead{{background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:14px 18px;font-size:.95rem}}
.lead b{{color:var(--accent)}}
section.lesson{{margin:34px 0;padding:18px;border:1px solid var(--line);border-radius:12px}}
section.lesson h2{{font-size:1.15rem;margin:.2em 0 .6em}}
section.lesson h2 small{{color:var(--muted);font-weight:400;font-size:.72rem}}
.newwords{{font-size:.82rem;color:var(--muted);margin-bottom:10px}}
.chip{{display:inline-block;background:#eff6ff;color:#1d4ed8;border:1px solid #bfdbfe;
 border-radius:999px;padding:1px 9px;margin:2px;font-size:.82rem}}
.grammar-box{{background:#fff7ed;border:1px solid #fed7aa;border-radius:8px;padding:10px 14px;margin:10px 0;font-size:.9rem}}
.g-title{{font-weight:700;color:#c2410c}}
.g-desc{{margin:.3em 0}}
.g-ex-label{{margin:.4em 0 .1em;font-size:.85rem;color:var(--muted)}}
.grammar-box ul{{margin:.2em 0;padding-left:1.2em}}
.grammar-box .ja{{color:var(--muted);font-size:.85em}}
.passage-title{{font-size:.92rem;color:var(--accent);margin:16px 0 4px;border-left:4px solid var(--accent);padding-left:8px}}
.jp-body p{{margin:.5em 0}}
/* index未読込でも読めるよう .w に語義を表示（index統合時はindex側CSSが上書き）*/
.jp-body .w{{font-weight:700;color:#0f766e;white-space:nowrap}}
.jp-body .w::after{{content:"("attr(data-ja)")";font-size:.7em;color:#94a3b8;font-weight:400;margin-left:1px}}
.en-plain{{background:#f8fafc;border:1px dashed #cbd5e1;border-radius:8px;padding:8px 14px;font-size:.9rem}}
table{{border-collapse:collapse;width:100%;font-size:.88rem;margin-top:8px}}
th,td{{border:1px solid var(--line);padding:5px 9px;text-align:left}}
th{{background:var(--bg)}}
td.ipa{{color:var(--muted);font-family:ui-monospace,monospace}}
code{{background:#f1f5f9;padding:1px 5px;border-radius:4px;font-size:.85em}}
.note{{font-size:.82rem;color:var(--muted)}}
</style></head>
<body>
<h1>📘 中学生編 ― 語彙補強ドラフト</h1>
<div class="lead">
<p>小中学校.xlsx の語のうち、<b>index.html のどこにも出てこなかった 129 語</b>を、既存「エクストラ語彙」レッスン（L31–45）のテーマに沿った<b>追加本文</b>として執筆したものです。本ファイルは<b>レビュー用ドラフト</b>で、<b>index.html は未編集</b>です。</p>
<p>本文中の英単語は index と同じ <code>&lt;span class="w" data-base data-ipa data-ja data-pos&gt;</code> でマークアップ済み（そのまま該当レッスンの <code>jp-body</code> に貼り付け可能）。語義は確認用に括弧で表示しています（index 統合時は index 側 CSS が上書き）。</p>
<p>このドラフトで本文化＝ <b>{len(covered)} 語</b> ／ 付録（高校編向き・発展語）＝ <b>{len(APPENDIX)} 語</b> ／ 合計 <b>{len(covered)+len(APPENDIX)} 語</b>。</p>
</div>
{body}

<section class="lesson">
  <h2>付録：発展語（高校編向き／本文未収録 {len(APPENDIX)} 語）</h2>
  <p class="note">中学レベルの物語には収まりにくい抽象語・低頻度語です。高校編への配置、または別途要否をご判断ください（IPA・語義は用意済み）。</p>
  <table><thead><tr><th>語</th><th>発音</th><th>語義</th><th>品詞</th></tr></thead>
  <tbody>{rows}</tbody></table>
</section>

<p class="note">生成: build_vocab_reinforcement_draft.py ／ 対象ギャップ語リスト: vocab_gap_TRUE_missing_everywhere.txt</p>
</body></html>'''
    open(OUT,"w",encoding="utf-8").write(doc)

    # 自己点検
    target=set(open("vocab_gap_TRUE_missing_everywhere.txt").read().split())
    handled=set(covered)|set(APPENDIX.keys())
    missing=sorted(target-handled); extra=sorted(handled-target)
    print(f"本文化 {len(covered)}語, 付録 {len(APPENDIX)}語, 計 {len(handled)}")
    print(f"対象129との差分  未処理={missing}  対象外={extra}")
    print(f"出力: {OUT}")

if __name__=="__main__":
    build()
