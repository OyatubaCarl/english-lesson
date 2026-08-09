#!/usr/bin/env python3
"""Funnics Island「時間と数」ストーリー集 ドラフト生成。

文法に縛られず、生活に根ざした内容＋慣用表現で、時刻・数・曜日・月・序数を
自然に学べる短い物語を5本。既存B-seriesの会話形式・キャラを踏襲。
※ index.html は編集しない。レビュー用スタンドアロンHTMLを出力。
出力: funnics_時間と数_stories_draft.html
"""
import re, html as _html

OUT = "funnics_時間と数_stories_draft.html"

# 既存キャラ（phonics-island-roster.md より）＋ Tom
STORIES = [
 dict(
  id="T1", title_en="What Time Is It, Tom?", title_ja="いま何時、トム？",
  scene="朝のFunnicsアイランドBig Clock前。トムはちょっと寝坊ぎみ。",
  cast=["Tom（トム）","Big Clock（大時計）","Cowboy Cat","Singer Snake","Teacher Tacos"],
  aim="時刻の言い方（o'clock / half past / a.m.・p.m. / noon）と、朝のあいさつ・時間の慣用表現。",
  lines=[
   ("Big Clock","Tick-tock, tick-tock! Good morning, Funnics Island!","チクタク、チクタク！おはよう、ファニックスアイランド！"),
   ("Cowboy Cat","Wake up, Tom! It's seven o'clock. I count the stars every night and the birds every morning!","起きて、トム！7時だよ。ぼくは毎晩星を、毎朝鳥を数えてるんだ！"),
   ("Tom","Seven o'clock? Oh no, I'm late!","7時？うわ、遅刻だ！"),
   ("Singer Snake","Take it easy, Tom. School starts at half past eight. You're still on time.","落ち着いて、トム。学校は8時半から。まだ間に合うよ。"),
   ("Tom","Half past eight? Phew. I have time for breakfast.","8時半？ほっ。朝ごはんの時間があるね。"),
   ("Teacher Tacos","Good morning! It's almost noon for me — I wake up at five a.m.!","おはよう！ぼくはもうすぐお昼の気分だよ。午前5時に起きるからね！"),
   ("Tom","Five a.m.? That's so early!","午前5時？早すぎる！"),
   ("Cowboy Cat","On the island, the early bird catches the worm.","この島ではね、早起きは三文の徳だよ。"),
   ("Big Clock","It's eight o'clock now. Hurry up, or you'll be late!","もう8時だよ。急がないと遅れるよ！"),
   ("Tom","Just a minute! I need my shoes.","ちょっと待って！くつをはかなきゃ。"),
   ("Singer Snake","Don't worry. Step by step. We still have thirty minutes.","だいじょうぶ。一歩ずつね。まだ30分あるよ。"),
   ("Tom","Thank you, everyone. It's time to go. See you at noon!","みんなありがとう。もう行く時間だ。お昼にね！"),
   ("All","Have a nice day!","いってらっしゃい、よい一日を！"),
  ],
  chant=[
   ("Tick-tock, tick-tock, what time is it?","チクタク、いま何時？"),
   ("Seven, eight, nine — it's time to go!","7時、8時、9時、もう行こう！"),
   ("On time, on time, never late,","時間どおり、遅れない、"),
   ("Wake up, Funnics, the day is great!","起きて、ファニックス、今日もすてき！"),
  ],
  keys=[("o'clock","〜時ちょうど"),("half past","〜時半"),("a.m.","午前"),("noon","正午・お昼"),
   ("It's time to go","もう行く時間"),("on time","時間どおりに"),("wake up","起きる"),
   ("take it easy","気楽に・落ち着いて"),("the early bird catches the worm","早起きは三文の徳"),
   ("hurry up","急いで"),("just a minute","ちょっと待って"),("step by step","一歩ずつ"),
   ("I'm late","遅刻だ"),("almost","もうすぐ"),("thirty","30"),("minutes","分"),
   ("Have a nice day","よい一日を"),("every morning","毎朝"),("every night","毎晩"),
  ],
 ),
 dict(
  id="T2", title_en="Seven Days, Seven Friends", title_ja="7日間、7人のなかま",
  scene="島の大きな予定ボードの前。トムが今週の予定を読む。",
  cast=["Tom","Teacher Tacos","Baker Bear","Librarian Lion","Runner Rabbit","Waiter Wolf","Yoga Yeti","Singer Snake"],
  aim="曜日（Monday〜Sunday）と、週の生活リズムの慣用表現（every〜 / day off / once a week / weekend）。",
  lines=[
   ("Tom","Wow, a big schedule board! What do we do this week?","わあ、大きな予定表！今週は何をするの？"),
   ("Teacher Tacos","On Monday, we teach and learn together.","月曜は、みんなで教えあって学ぶよ。"),
   ("Baker Bear","Every Tuesday, I bake fresh bread. Come and try some!","毎週火曜は、焼きたてパンを作るんだ。食べにおいで！"),
   ("Librarian Lion","On Wednesday, we read quietly in the library.","水曜は、図書室で静かに本を読むよ。"),
   ("Runner Rabbit","Thursday is race day! I run, run, run!","木曜はかけっこの日！走って、走って、走るよ！"),
   ("Waiter Wolf","On Friday, the café is open late. I wait on everyone with a smile.","金曜はカフェが夜おそくまで開いてる。笑顔でみんなをおもてなしするよ。"),
   ("Yoga Yeti","Saturday is my day off — a little holiday every week.","土曜はぼくの休みの日。毎週ちょっとした休日さ。"),
   ("Singer Snake","And on Sunday, we all sing together!","そして日曜は、みんなで歌うよ！"),
   ("Tom","Seven days, seven friends! Which day is today?","7日間、7人のなかま！今日は何曜日？"),
   ("Teacher Tacos","Today is Tuesday. So...?","今日は火曜だよ。ということは…？"),
   ("Tom","So it's bread day! Baker Bear, here I come!","パンの日だ！ベイカーベア、今行くよ！"),
   ("Baker Bear","Once a week is not enough? Then come every day!","週に一度じゃ足りない？じゃあ毎日おいで！"),
   ("Tom","See you on the weekend, everyone!","みんな、週末にまたね！"),
   ("All","See you! Have a great week!","またね！よい一週間を！"),
  ],
  chant=[
   ("Monday, Tuesday, Wednesday, too,","月曜、火曜、水曜も、"),
   ("Thursday, Friday, just for you,","木曜、金曜、きみのため、"),
   ("Saturday, Sunday, off we go —","土曜、日曜、さあ行こう、"),
   ("Seven happy days in a row!","しあわせな7日が続くよ！"),
  ],
  keys=[("Monday","月曜日"),("Tuesday","火曜日"),("Wednesday","水曜日"),("Thursday","木曜日"),
   ("Friday","金曜日"),("Saturday","土曜日"),("Sunday","日曜日"),
   ("this week","今週"),("today","今日"),("every Tuesday","毎週火曜"),("every day","毎日"),
   ("day off","休みの日"),("holiday","休日"),("once a week","週に一度"),
   ("weekend","週末"),("See you","またね"),("here I come","今行くよ"),("Have a great week","よい一週間を"),
  ],
 ),
 dict(
  id="T3", title_en="Happy Birthday Month!", title_ja="お誕生日の月！",
  scene="島のカレンダーの前。みんなで誕生日パーティーの相談。",
  cast=["Tom","Queen Quiz","Aunt Ant","Baker Bear","Pilot Panda","Teacher Tacos"],
  aim="月（January〜November）・日付・序数（first〜twelfth）と、予定の慣用表現（look forward to / save the date / count down）。",
  lines=[
   ("Queen Quiz","Quiz time! When is your birthday, Tom?","クイズの時間！トム、誕生日はいつ？"),
   ("Tom","My birthday is in September — September tenth!","ぼくの誕生日は9月、9月10日だよ！"),
   ("Aunt Ant","Mine is in January — January first, the first day of the year!","わたしは1月。1月1日、一年の最初の日よ！"),
   ("Baker Bear","February for me. I'll bake a big cake on the fourteenth!","ぼくは2月。14日に大きなケーキを焼くよ！"),
   ("Pilot Panda","I was born in October. I fly a little higher every year!","ぼくは10月生まれ。毎年ちょっと高く飛べるようになるんだ！"),
   ("Teacher Tacos","November is my month — the eleventh month of the year.","11月がぼくの月。一年の11番目の月だね。"),
   ("Queen Quiz","And December is the twelfth and last month!","そして12月は12番目、最後の月よ！"),
   ("Tom","So many birthdays! What's the date today?","誕生日がいっぱい！今日は何日？"),
   ("Queen Quiz","Today is October the eighth.","今日は10月8日よ。"),
   ("Tom","Then Pilot Panda's birthday is soon! Let's count down.","じゃあパイロットパンダの誕生日はもうすぐ！カウントダウンしよう。"),
   ("Aunt Ant","Let's save the date and have a party!","日にちを空けておいて、パーティーをひらきましょう！"),
   ("Pilot Panda","Really? I can't wait! I look forward to it.","ほんと？待ちきれない！楽しみにしてるよ。"),
   ("Baker Bear","First the cake, second the song, third the games!","まずケーキ、次に歌、3番目はゲーム！"),
   ("All","Happy birthday month! Let's celebrate one by one!","お誕生日の月、おめでとう！ひとりずつお祝いしよう！"),
  ],
  chant=[
   ("January, February, off we run,","1月、2月、さあ走ろう、"),
   ("September, October, autumn sun,","9月、10月、秋の日ざし、"),
   ("November comes, then one, two, three —","11月が来て、1、2、3、"),
   ("Happy birthday month, sing with me!","お誕生日の月、いっしょに歌おう！"),
  ],
  keys=[("January","1月"),("February","2月"),("September","9月"),("October","10月"),("November","11月"),
   ("December","12月"),("first","1番目・1日"),("second","2番目"),("third","3番目"),
   ("eighth","8番目・8日"),("tenth","10番目・10日"),("eleventh","11番目"),("twelfth","12番目"),
   ("fourteenth","14番目・14日"),("the date","日付"),("What's the date today","今日は何日"),
   ("look forward to","楽しみにする"),("can't wait","待ちきれない"),
   ("save the date","日にちを空けておく"),("count down","カウントダウンする"),
   ("one by one","ひとつずつ"),("Happy birthday","お誕生日おめでとう"),("every year","毎年"),
  ],
 ),
 dict(
  id="T4", title_en="How Much at the Market?", title_ja="市場でいくら？",
  scene="お昼すぎの島の市場（Island Market）。トムがお買い物。",
  cast=["Tom","Waiter Wolf","Fisher Frog","Baker Bear","Cowboy Cat"],
  aim="11〜20・90 の数と、お金・買い物の生活表現（How much / a few / a lot of / half price / for free / It's a deal）。",
  lines=[
   ("Tom","Good afternoon! How much is one apple?","こんにちは！りんご1つ、いくら？"),
   ("Waiter Wolf","One apple is three coins. A few apples? Even better!","りんご1つで3コイン。いくつか買う？もっとお得だよ！"),
   ("Tom","Then I'll take thirteen apples, please.","じゃあ、りんごを13個ください。"),
   ("Fisher Frog","Thirteen?! That's a lot of apples! Here, take two fish for free.","13個！？すごい量だね！はい、おまけに魚を2匹ただであげる。"),
   ("Baker Bear","My bread is half price today — sixteen coins for two loaves.","ぼくのパンは今日は半額。2本で16コインだよ。"),
   ("Tom","Sixteen coins... here is twenty.","16コイン…はい、20コイン。"),
   ("Baker Bear","Thank you! Here is your change: four coins.","ありがとう！おつりは4コインね。"),
   ("Cowboy Cat","I have ninety shells. Want some? Count with me!","ぼくは貝がらを90個持ってるよ。いる？いっしょに数えよう！"),
   ("Tom","Eleven, twelve, thirteen, fourteen, fifteen, sixteen, seventeen, eighteen, nineteen!","11、12、13、14、15、16、17、18、19！"),
   ("Waiter Wolf","Well counted! You have a good eye. It's a deal!","お見事！きみは見る目があるね。これで決まりだ！"),
   ("Fisher Frog","Little by little, your basket is full.","少しずつ、かごがいっぱいになったね。"),
   ("Tom","Thank you! I saved a lot today.","ありがとう！今日はたくさん得しちゃった。"),
   ("All","Come again! See you soon!","またおいで！近いうちにね！"),
  ],
  chant=[
   ("Eleven, twelve, thirteen, four,","11、12、13、14、"),
   ("Count your coins and buy some more!","コインを数えて、もっと買おう！"),
   ("Sixteen, seventeen, eighteen too,","16、17、18も、"),
   ("Nineteen, twenty — that's for you!","19、20、きみにあげる！"),
  ],
  keys=[("How much","いくら"),("eleven","11"),("twelve","12"),("thirteen","13"),("fourteen","14"),
   ("sixteen","16"),("seventeen","17"),("eighteen","18"),("nineteen","19"),("twenty","20"),("ninety","90"),
   ("a few","少しの"),("a lot of","たくさんの"),("for free","ただで"),("half price","半額"),
   ("change","おつり"),("It's a deal","これで決まり"),("a good eye","見る目"),
   ("little by little","少しずつ"),("Come again","またおいで"),("See you soon","近いうちにね"),
   ("Good afternoon","こんにちは（午後）"),
  ],
 ),
 dict(
  id="T5", title_en="Ready, Set, Go! The Funnics Race", title_ja="位置について、よーい、ドン！ファニックス・レース",
  scene="島のかけっこ大会。スタートラインに14人のランナー。",
  cast=["Teacher Tacos（審判）","Runner Rabbit","Hiker Hippo","Pilot Panda","Boxer Fox","Zigzag Zebra","Tom"],
  aim="序数（first〜fourteenth）と、がんばり・応援の慣用表現（do my best / step by step / give up / neck and neck / well done）。",
  lines=[
   ("Teacher Tacos","Welcome to the Funnics Race! Fourteen runners today!","ファニックス・レースへようこそ！今日は14人のランナーだ！"),
   ("Runner Rabbit","I'll do my best! Ready, set, go!","ベストをつくすぞ！位置について、よーい、ドン！"),
   ("Tom","Wow, they're fast! Runner Rabbit is first!","わあ、速い！ランナーラビットが1位だ！"),
   ("Hiker Hippo","I'm slow, but step by step, I never give up.","ぼくはおそいけど、一歩ずつ、あきらめないよ。"),
   ("Boxer Fox","Pilot Panda and I are neck and neck — second and third!","パイロットパンダとぼくは接戦だ。2位と3位！"),
   ("Zigzag Zebra","I zigzag a lot... so I'm only eighth! Ha-ha!","ぼくはジグザグしすぎて…やっと8位！ははっ！"),
   ("Tom","Where am I? ... Sixth! Not bad!","ぼくは何位？…6位だ！悪くないね！"),
   ("Teacher Tacos","Almost there, everyone! The finish line!","みんな、もうすぐだ！ゴールだよ！"),
   ("Runner Rabbit","First place! I did it!","1位！やったあ！"),
   ("Hiker Hippo","And I came in... fourteenth — but I finished! Hooray!","そしてぼくは…14位。でも完走したよ！ばんざい！"),
   ("Tom","From first to fourteenth, everyone did great.","1位から14位まで、みんなよくやった。"),
   ("Teacher Tacos","Well done! In the Funnics Race, we are all winners.","よくやった！ファニックス・レースでは、みんなが勝者だよ。"),
   ("All","Step by step, little by little — we did it!","一歩ずつ、少しずつ、ぼくたちやったね！"),
  ],
  chant=[
   ("First and second, third and fourth,","1番、2番、3番、4番、"),
   ("Step by step, we all go forth!","一歩ずつ、みんな前へ！"),
   ("Sixth and eighth and tenth, you'll see —","6番、8番、10番、ほら、"),
   ("We're all winners, one, two, three!","みんな勝者、1、2、3！"),
  ],
  keys=[("first","1番目・1位"),("second","2番目・2位"),("third","3番目・3位"),("fourth","4番目"),
   ("sixth","6番目・6位"),("eighth","8番目・8位"),("tenth","10番目"),("fourteenth","14番目・14位"),
   ("fourteen","14"),("do my best","ベストをつくす"),("Ready, set, go","位置について、よーい、ドン"),
   ("step by step","一歩ずつ"),("give up","あきらめる"),("neck and neck","接戦で"),
   ("Almost there","もうすぐ"),("finish line","ゴール"),("came in","〜位だった"),
   ("Well done","よくやった"),("Not bad","悪くない"),("we did it","やったね"),
  ],
 ),
]

# ---- 「時間と数」ギャップ24語（前回分析）→ 物語での網羅確認用 ----
GAP24 = ["eleven","thirteen","fourteen","sixteen","seventeen","eighteen","nineteen","ninety",
 "sixth","eighth","tenth","eleventh","twelfth","fourteenth","january","february","september",
 "october","november","tuesday","thursday","date","pm","holiday"]

def esc(s): return _html.escape(s, quote=True)

def build():
    # 全 keys を統合してハイライト辞書に（長いものから優先）
    GLOSS={}
    for s in STORIES:
        for k,j in s["keys"]:
            GLOSS.setdefault(k.lower(), (k,j))
    keys_sorted=sorted(GLOSS.keys(), key=len, reverse=True)
    rx=re.compile("|".join(re.escape(k) for k in keys_sorted), re.IGNORECASE)
    def hi(line):
        out=[]; i=0
        for m in rx.finditer(line):
            out.append(esc(line[i:m.start()]))
            disp,ja=GLOSS[m.group(0).lower()]
            out.append(f'<mark class="t" data-ja="{esc(ja)}">{esc(m.group(0))}</mark>')
            i=m.end()
        out.append(esc(line[i:]))
        return "".join(out)

    secs=[]
    cover=set()
    for n,s in enumerate(STORIES,1):
        for _,en,_ja in s["lines"]:
            low=re.sub(r"[.,!?']"," ",en.lower())
            for g in GAP24:
                if re.search(rf"\b{g}\b", low): cover.add(g)
            if "p.m." in en.lower() or "a.m." in en.lower(): cover.add("pm")
        rows="".join(
          f'<div class="line"><span class="who">{esc(w)}</span>'
          f'<div class="bubble"><p class="en">{hi(en)}</p><p class="ja">{esc(ja)}</p></div></div>'
          for w,en,ja in s["lines"])
        chant="".join(f'<p><span class="en">{hi(e)}</span><span class="ja">{esc(j)}</span></p>'
                      for e,j in s["chant"])
        keys="".join(f'<tr><td>{esc(k)}</td><td>{esc(j)}</td></tr>' for k,j in s["keys"])
        cast=" ".join(f'<span class="chip">{esc(c)}</span>' for c in s["cast"])
        secs.append(f'''
<section class="story">
  <div class="story-head">
    <span class="num">Story {s['id']}</span>
    <h2>{esc(s['title_en'])} <small>／ {esc(s['title_ja'])}</small></h2>
  </div>
  <p class="scene">📍 {esc(s['scene'])}</p>
  <p class="cast">🎭 {cast}</p>
  <p class="aim">🎯 <b>ねらい：</b>{esc(s['aim'])}</p>
  <div class="dialogue">{rows}</div>
  <div class="chant"><span class="chant-label">🎵 みんなで チャント</span>{chant}</div>
  <details class="keys"><summary>🔑 重要表現・慣用句（{len(s['keys'])}）</summary>
    <table><tbody>{keys}</tbody></table></details>
</section>''')

    miss=[g for g in GAP24 if g not in cover]
    body="\n".join(secs)
    doc=f'''<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Funnics Island — 時間と数のおはなし</title>
<style>
:root{{--ink:#2b2b3a;--muted:#8a8aa0;--sea:#0ea5b7;--sun:#f59e0b;--coral:#ff6b6b;--line:#e7e7ef;}}
*{{box-sizing:border-box}}
body{{font-family:"Hiragino Maru Gothic ProN","Hiragino Kaku Gothic ProN",system-ui,sans-serif;
 color:var(--ink);line-height:1.8;max-width:780px;margin:0 auto;padding:22px 16px 80px;
 background:linear-gradient(180deg,#eafaff,#fff 320px)}}
h1{{font-size:1.5rem;text-align:center;color:var(--sea)}}
.lead{{background:#fff;border:1px solid var(--line);border-radius:14px;padding:14px 18px;font-size:.92rem;
 box-shadow:0 2px 10px rgba(14,165,183,.07)}}
.lead b{{color:var(--coral)}}
.cover{{font-size:.84rem;color:var(--muted);margin-top:8px}}
.cover .ok{{display:inline-block;background:#e0f7ee;color:#0a8a5a;border-radius:6px;padding:0 6px;margin:2px}}
.story{{background:#fff;border:1px solid var(--line);border-radius:18px;padding:18px 18px 14px;
 margin:26px 0;box-shadow:0 4px 16px rgba(20,30,60,.06)}}
.story-head{{display:flex;align-items:baseline;gap:10px;border-bottom:2px dashed #ffe0b2;padding-bottom:8px}}
.num{{background:var(--sun);color:#fff;font-weight:800;border-radius:999px;padding:2px 12px;font-size:.78rem;white-space:nowrap}}
.story h2{{font-size:1.18rem;margin:.1em 0}}
.story h2 small{{color:var(--muted);font-weight:500;font-size:.78rem}}
.scene,.cast,.aim{{font-size:.86rem;margin:.4em 0}}
.aim{{background:#fff7ed;border-radius:8px;padding:6px 10px}}
.chip{{display:inline-block;background:#eef6ff;color:#2563eb;border:1px solid #cfe0ff;border-radius:999px;
 padding:1px 9px;margin:2px;font-size:.78rem}}
.dialogue{{margin:12px 0}}
.line{{display:flex;gap:10px;align-items:flex-start;margin:9px 0}}
.who{{flex:0 0 90px;font-size:.74rem;font-weight:700;color:var(--sea);text-align:right;padding-top:8px}}
.bubble{{flex:1;background:#f4fbfd;border:1px solid #d9eef2;border-radius:4px 14px 14px 14px;padding:7px 12px}}
.bubble .en{{margin:0;font-size:1.02rem}}
.bubble .ja{{margin:.15em 0 0;font-size:.82rem;color:var(--muted)}}
mark.t{{background:linear-gradient(transparent 55%,#fff3a8 55%);color:inherit;padding:0 1px;border-radius:3px;
 font-weight:700;position:relative;cursor:help}}
mark.t::after{{content:"("attr(data-ja)")";font-size:.62em;color:var(--coral);font-weight:600;margin-left:1px;
 vertical-align:super}}
.chant{{background:linear-gradient(135deg,#fff0f3,#fff7e6);border:1px dashed #ffc1cc;border-radius:14px;
 padding:10px 16px;margin:12px 0}}
.chant-label{{display:block;font-weight:800;color:var(--coral);font-size:.82rem;margin-bottom:4px}}
.chant p{{margin:.15em 0;display:flex;gap:10px;flex-wrap:wrap;align-items:baseline}}
.chant .en{{font-weight:700}}
.chant .ja{{font-size:.78rem;color:var(--muted)}}
.keys{{margin-top:8px;font-size:.86rem}}
.keys summary{{cursor:pointer;font-weight:700;color:var(--sea)}}
.keys table{{border-collapse:collapse;width:100%;margin-top:6px}}
.keys td{{border:1px solid var(--line);padding:4px 9px}}
.keys td:first-child{{font-weight:600;width:46%}}
.note{{font-size:.8rem;color:var(--muted);text-align:center;margin-top:30px}}
</style></head>
<body>
<h1>🏝️ Funnics Island ―「時間と数」のおはなし</h1>
<div class="lead">
<p>トムと Funnics Island のなかまたちが、<b>時刻・曜日・月・数・順番</b>を、暮らしの場面と<b>慣用表現</b>の中で学ぶ短い物語集です（全5話）。文法の順番にはこだわらず、自然な会話・あいさつ・かけ声を大切にしました。各話に<b>チャント（歌）</b>と<b>重要表現リスト</b>つき。</p>
<p class="cover">「時間と数」不足語24のうち <b>{len(cover)}語</b>を物語内でカバー：
{" ".join(f'<span class="ok">{esc(g)}</span>' for g in GAP24 if g in cover)}
{"／未カバー: "+", ".join(miss) if miss else "（全語カバー）"}</p>
</div>
{body}
<p class="note">生成: build_funnics_time_stories.py ／ index.html は未編集（レビュー用ドラフト）</p>
</body></html>'''
    open(OUT,"w",encoding="utf-8").write(doc)
    print(f"5話を出力: {OUT}")
    print(f"ギャップ24語カバー: {len(cover)}/24  未カバー={miss or 'なし'}")
    print(f"総セリフ数: {sum(len(s['lines']) for s in STORIES)}  チャント: {len(STORIES)}本")

if __name__=="__main__":
    build()
