#!/usr/bin/env python3
"""Prepare exact-lyric, mixed-Japanese captions with complete ruby for H1-H160."""

from __future__ import annotations

import argparse
import html as htmlmod
import importlib.util
import json
import re
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


HERE = Path(__file__).resolve().parent
PIPELINE = HERE.parent
HIGH = PIPELINE.parent
PROJECT = HIGH.parent
MANIFEST = PIPELINE / "planning" / "adopted_songs_h001_h160.json"
LESSONS = PROJECT / "taco_course_mockup" / "high_lessons.json"
CACHE = PIPELINE / "planning" / "exact_lyrics_ja_translation_cache.json"
SUMMARY = PIPELINE / "planning" / "mixed_ruby_manifest.json"
REVIEW = PIPELINE / "planning" / "mixed_ruby_review.md"
SOURCE_HTML = PROJECT / "index.html"
MIDDLE_PREP = (
    PROJECT / "中学生編" / "middle_ruby_complete_v1" / "scripts" / "prepare_middle_ruby.py"
)


def load_middle_helpers():
    spec = importlib.util.spec_from_file_location("middle_ruby_helpers", MIDDLE_PREP)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {MIDDLE_PREP}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


HELPERS = load_middle_helpers()


EXTRA_GLOSSARY = {
    "ai": "人工知能",
    "sns": "SNS",
    "nasa": "アメリカ航空宇宙局",
    "dna": "DNA",
    "ddt": "DDT",
    "npt": "核拡散防止条約",
    "mri": "磁気共鳴画像法",
    "ptsd": "心的外傷後ストレス障害",
    "lgbtq": "性的少数者",
    "sora": "ソラ",
    "deepl": "ディープエル",
    "eu": "欧州連合",
    "ngo": "非政府組織",
    "serendipity": "思いがけない幸運",
    "nostalgia": "郷愁",
    "privacy": "プライバシー",
    "intelligence": "知能",
    "innocent": "無罪の",
    "proven": "証明された",
    "guilty": "有罪の",
    "traffic jam": "交通渋滞",
    "black lives matter": "黒人の命も大切だ",
    "rite of passage": "通過儀礼",
    "spoke": "話した",
    "stood": "立っていた",
    "noticed": "気づいた",
    "vanished": "消えた",
    "lived": "生きていた",
    "continued": "続けた",
    "trusted": "信頼した",
    "proposed": "提案した",
    "wished": "願った",
    "wonder": "思う",
    "hope": "願う",
    "mind": "決心",
}

FALLBACK_STOPWORDS = HELPERS.STOPWORDS | {
    "no", "one", "nothing", "everything", "something", "someone", "anyone",
    "everyone", "every", "sometimes", "first", "then", "there", "here",
    "really", "just", "even", "yet", "still",
}


# Reviewed canonical-word phrasing for places where the exact Japanese
# translation uses a synonym.  These forms preserve the adopted lyric meaning
# while making the lesson's actual new words visible; no easy/global terms are
# introduced.
CANONICAL_MANUAL_MIXED: dict[tuple[int, int], dict] = {
    (1, 4): {"mixed": "世界は静かに breathed。", "ruby": {"breathed": "息づいていた"}},
    (1, 6): {"mixed": "太陽が emerged。", "ruby": {"emerged": "立ち現れた"}},
    (1, 7): {"mixed": "その光は pure な空気に広がりました。", "ruby": {"pure": "澄んだ"}},
    (1, 14): {"mixed": "森の depths から、かすかな presence が動きました。", "ruby": {"depths": "奥深く", "presence": "気配"}},
    (1, 15): {"mixed": "私は一頭の鹿を noticed。", "ruby": {"noticed": "見つけて気づいた"}},
    (1, 18): {"mixed": "私は風景を、ただ静かに observed。", "ruby": {"observed": "観察した"}},
    (1, 21): {"mixed": "新しい一日が arose。", "ruby": {"arose": "始まった"}},
    (5, 2): {"mixed": "母はその子を adopt することに決め、僕たちはソラと名付けました。", "ruby": {"adopt": "家族に迎える"}},
    (5, 4): {"mixed": "父はソラを僕たちの家族の一員だと declare し、僕たちは皆で歓迎しました。", "ruby": {"declare": "宣言"}},
    (5, 5): {"mixed": "母はソラが gentle な子だと気づきました。", "ruby": {"gentle": "優しい"}},
    (5, 8): {"mixed": "僕はソラを protect すると誓いました。", "ruby": {"protect": "守る"}},
    (5, 10): {"mixed": "父は『この犬を家族として迎えよう』と言い、僕たちは一緒にソラを embrace しました。", "ruby": {"embrace": "抱きしめる"}},
    (5, 11): {"mixed": "数週間後、僕たちの世話のおかげで、ソラは calm で満ち足りた犬になりました。", "ruby": {"calm": "穏やか"}},
    (5, 12): {"mixed": "好奇心旺盛で affection に満ちたソラは僕たちの家の中心となり、みんなの心に温かな bond をもたらしました。", "ruby": {"affection": "愛情", "bond": "絆"}},
    (6, 12): {"mixed": "彼女は、私に彼を思い出すよう encourage しようとしているのだと感じました。", "ruby": {"encourage": "励ます"}},
    (6, 13): {"mixed": "やがて夕日が、屋根を gentle な色調に染めました。", "ruby": {"gentle": "やわらかな"}},
    (6, 14): {"mixed": "庭は calm で、黄金色になりました。", "ruby": {"calm": "穏やか"}},
    (13, 2): {"mixed": "息を整えてベンチに座り、exhausted な状態でした。", "ruby": {"exhausted": "疲れ切った"}},
    (13, 5): {"mixed": "Meanwhile、友人は定刻に駅へ着いていました。", "ruby": {"Meanwhile": "一方で"}},
    (13, 12): {"mixed": "彼がいつも示してくれた gentle な優しさを、今になって realize しました。", "ruby": {"gentle": "優しい", "realize": "気づく"}},
    (13, 14): {"mixed": "気持ちは eventually settled。", "ruby": {"eventually": "ついに", "settled": "落ち着いた"}},
    (14, 1): {"mixed": "あと5年で、私は何を accomplish しているでしょうか。", "ruby": {"accomplish": "達成する"}},
    (14, 3): {"mixed": "私の ambition は大きくありませんが、他の人の人生に静かに contribute したいです。", "ruby": {"ambition": "大望", "contribute": "貢献する"}},
    (14, 5): {"mixed": "日々の progress が、静かに一本の道になっているでしょう。", "ruby": {"progress": "進歩"}},
    (14, 6): {"mixed": "それまでに、小さな achievements を積み重ね、多くのものを seeking。", "ruby": {"achievements": "達成", "seeking": "求め続けている"}},
    (14, 8): {"mixed": "私はもう少し mature になっているでしょう。", "ruby": {"mature": "成熟した"}},
    (14, 9): {"mixed": "大きな prospect が、いつも必要なわけではありません。", "ruby": {"prospect": "見通し"}},
    (14, 10): {"mixed": "小さな goals を fulfill できる人になりたいです。", "ruby": {"goals": "目標", "fulfill": "実現する"}},
    (14, 11): {"mixed": "私の未来は likely、目の前に静かに開いていくでしょう。今はそう信じています。", "ruby": {"likely": "おそらく"}},
    (15, 3): {"mixed": "これは、自分を見つめ直す reflection の時間です。", "ruby": {"reflection": "内省"}},
    (15, 8): {"mixed": "それを recall するたびに、恥ずかしくなります。", "ruby": {"recall": "思い出す"}},
    (15, 10): {"mixed": "新しい年は、もっと modest に過ごしたいです。", "ruby": {"modest": "控えめに"}},
    (15, 11): {"mixed": "家族への感謝を、もっと express したいです。", "ruby": {"express": "表現する"}},
    (15, 12): {"mixed": "少し早起きして深呼吸するという、小さな habit を adopt したいです。", "ruby": {"habit": "習慣", "adopt": "取り入れる"}},
    (15, 14): {"mixed": "僕は手を合わせ、亡くなった祖父を静かに recall しました。", "ruby": {"recall": "思い出す"}},
    (16, 1): {"mixed": "その日、僕は小さな店の前で hesitated。", "ruby": {"hesitated": "ためらった"}},
    (16, 3): {"mixed": "それは素早い decision の瞬間でした。", "ruby": {"decision": "決断"}},
    (16, 5): {"mixed": "妹の誕生日に間に合うよう、もっと早く decision を下しておくべきでした。", "ruby": {"decision": "決定"}},
    (16, 7): {"mixed": "店主は『昨日、別のお客様が purchase しました』と言いました。", "ruby": {"purchase": "購入する"}},
    (16, 8): {"mixed": "僕はその regret を、妹に confess できませんでした。", "ruby": {"regret": "後悔", "confess": "打ち明ける"}},
    (16, 11): {"mixed": "でも、妹はもう僕を forgive してくれていました。", "ruby": {"forgive": "許す"}},
    (16, 12): {"mixed": "その小さな出来事で、妹の mature な優しさがはっきり見えました。", "ruby": {"mature": "成熟した"}},
    (16, 13): {"mixed": "人は regret しても、誰かの affection に救われることがあります。", "ruby": {"regret": "後悔する", "affection": "愛情"}},
    (17, 2): {"mixed": "長い間忘れられていましたが、ある年、町の人たちは建物を restore することに決めました。", "ruby": {"restore": "修復"}},
    (17, 3): {"mixed": "その家は約80年前に construct されました。", "ruby": {"construct": "建設"}},
    (17, 4): {"mixed": "戦後は長い間 abandoned のままでした。", "ruby": {"abandoned": "放棄された"}},
    (17, 6): {"mixed": "町の人たちは、この建物を地域の heritage として preserve すべきだと声を上げました。", "ruby": {"heritage": "遺産", "preserve": "保存する"}},
    (17, 7): {"mixed": "この家は歴史的に重要なものとして recognize されました。", "ruby": {"recognize": "認める"}},
    (17, 8): {"mixed": "最終的には市から修復予算が付けられ、家は徐々に repair されていきました。", "ruby": {"repair": "修理"}},
    (18, 3): {"mixed": "最初は exhausted で10キロも走れず、途中で歩いてしまうこともありました。", "ruby": {"exhausted": "疲れ切って"}},
    (18, 5): {"mixed": "それでも妹は地道な effort を続け、少しずつ呼吸を整える方法を learn しました。", "ruby": {"effort": "努力", "learn": "身につける"}},
    (18, 8): {"mixed": "目標に reach するために、妹は毎日走っています。", "ruby": {"reach": "到達する"}},
    (18, 9): {"mixed": "このように明確な purpose を持つ姿は、まぶしく、尊敬できます。", "ruby": {"purpose": "目的"}},
    (18, 11): {"mixed": "その日、妹は単なるランナーではなく、地道な effort を本当の自信に変えた人になるでしょう。", "ruby": {"effort": "努力"}},
    (19, 1): {"mixed": "父の机の引き出しの奥で、僕は古い日記を discover しました。", "ruby": {"discover": "発見する"}},
    (19, 2): {"mixed": "父は長い間、その writing を続けていたようです。", "ruby": {"writing": "書くこと"}},
    (19, 3): {"mixed": "僕はそれを開こうとして hesitated。", "ruby": {"hesitated": "ためらった"}},
    (19, 6): {"mixed": "でも僕は、その誘惑を avoid できませんでした。", "ruby": {"avoid": "避ける"}},
    (19, 8): {"mixed": "若い頃、父は詩を compose していました。", "ruby": {"compose": "作る"}},
    (19, 9): {"mixed": "言葉の端々に人生の喜びがありましたが、胸の底には小さな regret もありました。", "ruby": {"regret": "後悔"}},
    (19, 13): {"mixed": "父の過去を垣間見て、僕は父への新たな respect を抱きました。", "ruby": {"respect": "敬意"}},
    (20, 2): {"mixed": "疲れていたのに、足取りは軽く feel ました。", "ruby": {"feel": "感じられ"}},
    (20, 3): {"mixed": "細い alley を抜け、小さな広場を渡ると、街の雰囲気を feel ました。", "ruby": {"alley": "路地", "feel": "感じ"}},
    (20, 6): {"mixed": "芳醇な香りが漂ってきて、僕の気分は improve していきました。", "ruby": {"improve": "良くなる"}},
    (20, 9): {"mixed": "その encounter は思いがけない喜びでした。", "ruby": {"encounter": "出会い"}},
    (20, 10): {"mixed": "彼と二言三言交わすと、その日の疲れが完全に vanish したと feel ました。", "ruby": {"vanish": "消えた", "feel": "感じ"}},
    (20, 11): {"mixed": "街を歩きながら、日常の小さな delight が僕を静かに embrace するのを feel ました。", "ruby": {"delight": "喜び", "embrace": "包み込む", "feel": "感じ"}},
    (21, 5): {"mixed": "僕たちは短く hug し、小さな promise を交わした。", "ruby": {"hug": "抱き合い", "promise": "約束"}},
    (21, 10): {"mixed": "僕たちは contact を取り続けることを promised。", "ruby": {"contact": "連絡", "promised": "約束していました"}},
    (21, 11): {"mixed": "空港の大きなガラス窓越しに、僕は彼の飛行機が depart するのを見つめました。", "ruby": {"depart": "出発"}},
    (21, 13): {"mixed": "友人を待ち受ける未来は、雲の beyond に広がっているようでした。", "ruby": {"beyond": "彼方"}},
    (22, 1): {"mixed": "大学時代に僕を指導してくださった先生のお宅を visit しました。", "ruby": {"visit": "訪問"}},
    (22, 3): {"mixed": "先生は僕と同世代の学生たちが最も respect していた人物でした。", "ruby": {"respect": "尊敬"}},
    (22, 7): {"mixed": "その中には、先生自身が書いた manuscript もありました。", "ruby": {"manuscript": "原稿"}},
    (22, 8): {"mixed": "先生は一冊の本を僕に recommend し、『これは君が若い頃に読んでほしかった本です』と言いました。", "ruby": {"recommend": "勧め"}},
    (22, 11): {"mixed": "僕が discover したのは、先生が長年 correspond してきた scholar たちからの手紙の束でした。", "ruby": {"discover": "発見", "correspond": "文通", "scholar": "学者"}},
    (22, 12): {"mixed": "それらの手紙が、先生の wisdom の源でした。", "ruby": {"wisdom": "知恵"}},
    (23, 2): {"mixed": "最も matter するのは、essential なものだけのようです。", "ruby": {"matter": "大切である", "essential": "本質的な"}},
    (23, 3): {"mixed": "僕が長い間 pursue してきたものが、いつも significant だったわけではありません。", "ruby": {"pursue": "追い求める", "significant": "重要な"}},
    (23, 4): {"mixed": "本当に matter するのは、家族との小さな食事、友人からの電話、寝る前の一冊の本。", "ruby": {"matter": "大切である"}},
    (23, 6): {"mixed": "友人が以前こう言いました。『experience を通して learn したことが、自分の value の中心になる』。", "ruby": {"experience": "経験", "learn": "学んだ", "value": "価値観"}},
    (23, 7): {"mixed": "そう、僕が learn したことこそが matter するのです。", "ruby": {"learn": "学んだ", "matter": "大切である"}},
    (23, 8): {"mixed": "何が僕を fulfill してくれるのか、もう一度、自分の中で reveal したかったのです。", "ruby": {"fulfill": "満たす", "reveal": "明らかにする"}},
    (23, 9): {"mixed": "Friendship、静かな時間、そして僕自身が長く大切にしてきたもの。", "ruby": {"Friendship": "友情"}},
    (24, 1): {"mixed": "僕の祖父は、海辺の町で lighthouse の管理人として長年働いていました。", "ruby": {"lighthouse": "灯台"}},
    (24, 3): {"mixed": "祖父は毎晩、塔の階段を climb しました。", "ruby": {"climb": "登りました"}},
    (24, 4): {"mixed": "祖父はランプを点検し、窓を拭き、storm が近づくと一晩中眠らずに働きました。", "ruby": {"storm": "嵐"}},
    (24, 6): {"mixed": "lighthouse が輝き始める瞬間こそ、僕が最もそこにいたいと願う時間でした。", "ruby": {"lighthouse": "灯台"}},
    (24, 7): {"mixed": "ある時、祖父はなぜこの仕事を続けてきたのか、その理由を僕に reveal してくれました。", "ruby": {"reveal": "明かして"}},
    (24, 8): {"mixed": "『海の向こうから帰ってくる船が、safe に港へ入れるようにするためだ』と祖父は言いました。", "ruby": {"safe": "安全に"}},
    (24, 9): {"mixed": "僕はよく、祖父が sailors を guide した、その way を思います。", "ruby": {"sailors": "船乗りたち", "guide": "導いた", "way": "やり方"}},
    (24, 10): {"mixed": "祖父と lighthouse は、言葉を交わさず長い年月 correspond していました。", "ruby": {"lighthouse": "灯台", "correspond": "対応し合って"}},
    (24, 11): {"mixed": "storm の夜に、祖父の光がどれほど多くの sailors を guide したのか、僕には想像もできません。", "ruby": {"storm": "嵐", "sailors": "船乗り", "guide": "導いた"}},
    (25, 1): {"mixed": "町のホールで、小さな concert が開かれました。", "ruby": {"concert": "音楽会"}},
    (25, 2): {"mixed": "来た人は誰でも、admission は無料でした。", "ruby": {"admission": "入場"}},
    (25, 3): {"mixed": "誰が perform しても、audience は温かく迎えました。", "ruby": {"perform": "演奏", "audience": "観客"}},
    (25, 4): {"mixed": "最初に perform したのは、バイオリンを持った10歳の女の子でした。", "ruby": {"perform": "演奏"}},
    (25, 5): {"mixed": "彼女が弾き終えると、どんなに小さな音で弾いても、一つ一つの note が会場の聴く人すべてに届きました。", "ruby": {"note": "音符"}},
    (25, 6): {"mixed": "何度も applause が湧き起こりました。", "ruby": {"applause": "拍手"}},
    (25, 7): {"mixed": "どの楽章を perform しても、彼女の音色には purity がありました。", "ruby": {"perform": "演奏", "purity": "純粋さ"}},
    (25, 8): {"mixed": "聴いた人は誰でも、彼女の音の purity を admire せずにはいられませんでした。", "ruby": {"purity": "純粋さ", "admire": "感嘆する"}},
    (25, 9): {"mixed": "その夜のホールは、僕が今まで見たどの時よりも peaceful で、人々は互いに smile を交わしていました。", "ruby": {"peaceful": "穏やか", "smile": "ほほえみ"}},
    (25, 10): {"mixed": "このような場所が存在するなら、それは僕が treasure したい地域の小さな heritage です。", "ruby": {"treasure": "大切にする", "heritage": "伝統"}},
    (26, 1): {"mixed": "もし僕が鳥なら、望む場所へ freely 飛んでいくだろう。", "ruby": {"freely": "自由に"}},
    (26, 3): {"mixed": "もし翼があれば、雲の上へ soar するだろう。", "ruby": {"soar": "舞い上がる"}},
    (26, 4): {"mixed": "遠い町までの distance に縛られることもないだろう。", "ruby": {"distance": "距離"}},
    (26, 5): {"mixed": "地面に縛られていなければ、風に運ばれるまま wherever 旅するだろう。", "ruby": {"wherever": "どこへでも"}},
    (26, 8): {"mixed": "僕には imagine することしかできない。", "ruby": {"imagine": "想像する"}},
    (26, 9): {"mixed": "それでも imagine することは、小さな freedom の形だ。", "ruby": {"imagine": "想像する", "freedom": "自由"}},
    (26, 10): {"mixed": "夕暮れの空を見上げながら、僕は思う。もし鳥だったなら、この空にどれほど深く admire するだろう。", "ruby": {"admire": "感嘆する"}},
    (26, 12): {"mixed": "その代わりに、想像力が僕を embrace してくれる。", "ruby": {"embrace": "抱きしめる"}},
    (27, 1): {"mixed": "もしあの日、僕が letter を出していたなら、すべては違っていたかもしれない。", "ruby": {"letter": "手紙"}},
    (27, 3): {"mixed": "僕がすべきだったのは、ただ一言『ありがとう』と書き、気持ちを tell することだけだった。", "ruby": {"tell": "告げる"}},
    (27, 4): {"mixed": "一通の letter だけで十分だったのだ。", "ruby": {"letter": "手紙"}},
    (27, 5): {"mixed": "もしあのとき、僕にもう少し courage があれば、letter は彼女に届き、彼女はもっと長く僕を remember してくれたかもしれない。", "ruby": {"courage": "勇気", "letter": "手紙", "remember": "覚えている"}},
    (27, 7): {"mixed": "僕は言葉を大切にしすぎて、しまい込んだまま hide してしまった。", "ruby": {"hide": "隠す"}},
    (27, 9): {"mixed": "もしあの一通の letter を書いていたら、僕は今でも彼女と correspond していたかもしれない。", "ruby": {"letter": "手紙", "correspond": "文通する"}},
    (27, 10): {"mixed": "ずっと後、彼女の結婚の知らせを聞いたとき、僕はあの小さな regret をもう一度味わった。", "ruby": {"regret": "後悔"}},
    (27, 11): {"mixed": "一通の letter を送る courage が、人生を変えることもあるのだと僕は学んだ。", "ruby": {"letter": "手紙", "courage": "勇気"}},
    (28, 1): {"mixed": "ペニシリンの discovery は、ある偶然から始まりました。", "ruby": {"discovery": "発見"}},
    (28, 2): {"mixed": "1928年、ロンドンの laboratory に、一人の科学者が休暇から戻ってきました。", "ruby": {"laboratory": "研究室"}},
    (28, 3): {"mixed": "アレクサンダー・フレミングは、研究台に残した培養皿の一つに奇妙な mold が生えていることを notice しました。", "ruby": {"mold": "カビ", "notice": "気づく"}},
    (28, 4): {"mixed": "mold の周囲では、細菌が消えていました。", "ruby": {"mold": "カビ"}},
    (28, 5): {"mixed": "もしフレミングがその小さな observation を見逃していたら、世界はどれほど多くを lose していたことでしょう。", "ruby": {"observation": "観察", "lose": "失う"}},
    (28, 6): {"mixed": "もし彼がその mold を notice していなければ、多くの infection は治療されず、戦場の wound によって数え切れない命を lose していたかもしれません。", "ruby": {"mold": "カビ", "notice": "気づく", "infection": "感染", "wound": "傷", "lose": "失う"}},
    (28, 7): {"mixed": "その一枚の培養皿が、抗生物質という medicine の時代を切り開く助けとなりました。", "ruby": {"medicine": "薬"}},
    (28, 8): {"mixed": "フレミングの注意深い observation と、それに続く多くの科学者の研究は、やがて何百万もの命を save する助けとなりました。", "ruby": {"observation": "観察", "save": "救う"}},
    (28, 9): {"mixed": "もしその chance の observation がなされていなければ、科学の歴史はまったく違っていたでしょう。", "ruby": {"chance": "偶然", "observation": "観察"}},
    (29, 3): {"mixed": "けれど、どの樫の木よりもはるかに古い ancient な木があります。", "ruby": {"ancient": "古代からの"}},
    (29, 4): {"mixed": "カリフォルニアの高山に、4000年以上 survive してきたブリッスルコーンパインがあります。", "ruby": {"survive": "生き延びる"}},
    (29, 7): {"mixed": "他の松と compare すると、一年に数ミリしか成長しないこともあります。", "ruby": {"compare": "比較する"}},
    (29, 10): {"mixed": "それでも、そのような harsh な環境こそが、この木の長命を可能にしました。", "ruby": {"harsh": "厳しい"}},
    (29, 11): {"mixed": "科学者たちは、木材内部の年輪から、これらの木の年齢を measure します。", "ruby": {"measure": "測定する"}},
    (29, 13): {"mixed": "僕たちは、多くの文明よりも古い一本の木を admire せずにはいられません。", "ruby": {"admire": "感嘆する"}},
    (29, 14): {"mixed": "それは、静けさと強さを併せ持つ、最も remarkable な生き物の一つです。", "ruby": {"remarkable": "注目すべき"}},
    (30, 1): {"mixed": "1969年7月20日、humanity は月に立ちました。", "ruby": {"humanity": "人類"}},
    (30, 2): {"mixed": "アポロ11号の mission は、長年にわたる準備を経て始まりました。", "ruby": {"mission": "任務"}},
    (30, 3): {"mixed": "1961年のケネディ大統領の演説がなければ、このような technology への挑戦は始まらなかったかもしれません。", "ruby": {"technology": "技術"}},
    (30, 4): {"mixed": "アームストロングが月面に降り立った瞬間、世界中の人々がその光景を watched。", "ruby": {"watched": "見守った"}},
    (30, 5): {"mixed": "彼の短い言葉は、全 humanity への贈り物となりました。", "ruby": {"humanity": "人類"}},
    (30, 6): {"mixed": "数え切れない engineer たちの dedication がなければ、その瞬間は起こりえませんでした。", "ruby": {"engineer": "技師", "dedication": "献身"}},
    (30, 7): {"mixed": "一人一人の contribution が、このたった一つの偉業を支えました。", "ruby": {"contribution": "貢献"}},
    (30, 8): {"mixed": "その日、humanity は地球の beyond に新たな歴史を書き始めました。", "ruby": {"humanity": "人類", "beyond": "向こう側"}},
    (30, 9): {"mixed": "これは本当に historic な瞬間でした。", "ruby": {"historic": "歴史的な"}},
    (30, 10): {"mixed": "乗組員たちは safely 地球へ帰還し、遠い世界の記憶を持ち帰りました。", "ruby": {"safely": "安全に"}},
    (31, 2): {"mixed": "マリー・キュリーは、科学史上最も有名な physicists の一人です。", "ruby": {"physicists": "物理学者たち"}},
    (31, 3): {"mixed": "彼女の passion、つまり科学への devotion は、並外れたものでした。", "ruby": {"passion": "情熱", "devotion": "献身"}},
    (31, 4): {"mixed": "彼女は夫ピエールとともに、人生の多くを research に捧げました。", "ruby": {"research": "研究"}},
    (31, 5): {"mixed": "新しい element である radium を単離して研究する目標には、何年もの終わりなき困難が伴いました。", "ruby": {"element": "元素", "radium": "ラジウム"}},
    (31, 7): {"mixed": "夫婦は risk を冒し、radiation にさらされながらも研究を続けました。", "ruby": {"risk": "危険", "radiation": "放射線"}},
    (31, 8): {"mixed": "二度の Nobel 受賞という偉業は、研究への純粋な愛、つまり彼女の passion なしには成し遂げられませんでした。", "ruby": {"Nobel": "ノーベル", "passion": "情熱"}},
    (31, 9): {"mixed": "女性、母親、科学者として、彼女は後の generations への道を切り開きました。", "ruby": {"generations": "世代"}},
    (32, 5): {"mixed": "彼女はその場で arrest を受けました。", "ruby": {"arrest": "逮捕"}},
    (32, 6): {"mixed": "当時は law によって人種が分けられており、黒人は特定の席にしか座ることができませんでした。", "ruby": {"law": "法律"}},
    (32, 7): {"mixed": "差別を制度化した law は、長らく society に影を落としてきました。", "ruby": {"law": "法律", "society": "社会"}},
    (32, 8): {"mixed": "パークスの refusal が、モンゴメリーのバスボイコットを引き起こしました。", "ruby": {"refusal": "拒否"}},
    (32, 9): {"mixed": "キング牧師が先導し、町の黒人 citizens はバスに乗ることをやめました。", "ruby": {"citizens": "市民たち"}},
    (32, 10): {"mixed": "なんと力強い protest だったのでしょう。", "ruby": {"protest": "抗議"}},
    (32, 12): {"mixed": "一人の citizen の「No」が、society を変える力になりました。", "ruby": {"citizen": "市民", "society": "社会"}},
    (32, 13): {"mixed": "courage に満ちたこの一言を、決して忘れないようにしましょう。", "ruby": {"courage": "勇気"}},
    (33, 2): {"mixed": "これほど偉大な knowledge を人類に与えた人は、ほとんどいません。", "ruby": {"knowledge": "知識"}},
    (33, 3): {"mixed": "重力の law、三つの運動法則、微積分の発展。", "ruby": {"law": "法則"}},
    (33, 4): {"mixed": "ニュートン以前には、落下物体と惑星の orbits の両方を説明する単一の theory はありませんでした。", "ruby": {"orbits": "軌道", "theory": "理論"}},
    (33, 5): {"mixed": "彼の mathematics 自体が、科学の言語そのものを再構築しました。", "ruby": {"mathematics": "数学"}},
    (33, 8): {"mixed": "彼の前には、広大な真実の ocean が、ほとんど未踏のまま残っている、と彼は語りました。", "ruby": {"ocean": "大海"}},
    (33, 9): {"mixed": "ニュートンの humility は、どれほど知っていても決して十分ではないことを教えてくれます。", "ruby": {"humility": "謙虚"}},
    (33, 10): {"mixed": "theory は遠くまで及んでも、knowledge の ocean は、なお深いのです。", "ruby": {"theory": "理論", "knowledge": "知識", "ocean": "大海"}},
    (34, 1): {"mixed": "アントニ・ガウディは、19世紀末から20世紀初頭にかけて、スペインのバルセロナで独特の architecture を生み出した建築家です。", "ruby": {"architecture": "建築"}},
    (34, 3): {"mixed": "100年以上にわたり、中断を繰り返しながら construction が続けられてきました。", "ruby": {"construction": "建設"}},
    (34, 5): {"mixed": "ガウディは自然の中から design の inspiration を得ました。", "ruby": {"design": "設計", "inspiration": "着想"}},
    (34, 7): {"mixed": "すべての柱、すべての curve は、自然界に見られる形をもとに design されました。", "ruby": {"curve": "曲線", "design": "設計"}},
    (34, 9): {"mixed": "彼にとって、自然そのものが architecture の一種でした。", "ruby": {"architecture": "建築"}},
    (34, 11): {"mixed": "しかし大聖堂は、世界中の訪問者からの donation と支援によって、幾つもの century を越え、今も construction が続いています。", "ruby": {"donation": "寄付", "century": "世紀", "construction": "建設"}},
    (34, 12): {"mixed": "おそらく、その未完成の状態自体が、建物の historic な歩みの一部になっているのでしょう。", "ruby": {"historic": "歴史的な"}},
    (35, 1): {"mixed": "1831年、チャールズ・ダーウィンはイギリスの測量船で世界一周の voyage に出ました。", "ruby": {"voyage": "航海"}},
    (35, 2): {"mixed": "5年間にわたる expedition の間、彼は南アメリカ沿岸の多くの islands を訪れました。", "ruby": {"expedition": "遠征", "islands": "島々"}},
    (35, 3): {"mixed": "ガラパゴス諸島で、彼は island ごとに動物がどう異なるかを注意深く observed しました。", "ruby": {"island": "島", "observed": "観察"}},
    (35, 4): {"mixed": "彼が collected した鳥は、後にイギリスで、異なる beaks を持つ近縁のフィンチ species だと判明しました。", "ruby": {"collected": "収集", "beaks": "くちばし", "species": "種"}},
    (35, 5): {"mixed": "ダーウィンは多くの specimens を collected し、帰国後、長い年月を思索に費やしました。", "ruby": {"specimens": "標本", "collected": "収集"}},
    (35, 6): {"mixed": "なぜ islands ごとに異なる動物がいたのでしょうか。", "ruby": {"islands": "島々"}},
    (35, 7): {"mixed": "なぜ動物たちは、それぞれの environment にあれほど見事に adapted していたのでしょうか。", "ruby": {"environment": "環境", "adapted": "適応"}},
    (35, 8): {"mixed": "1859年、species の起源を論じた著書『種の起源』の publication が世界を震撼させました。", "ruby": {"species": "生物の種", "publication": "出版"}},
    (35, 9): {"mixed": "evolution という考え方は、その時代の belief を揺るがしました。", "ruby": {"evolution": "進化", "belief": "信念"}},
    (35, 10): {"mixed": "激しい批判があったものの、ダーウィンの theory は、時間をかけて受け入れられました。", "ruby": {"theory": "理論"}},
    (35, 11): {"mixed": "自然は、静かに、しかし深く、generation を重ねながら変化し続けます。", "ruby": {"generation": "世代"}},
    (40, 1): {"mixed": "1953年、ジェームズ・ワトソンとフランシス・クリックは、DNAが二重らせん構造を持つという discovery を published しました。", "ruby": {"discovery": "発見", "published": "発表"}},
    (40, 2): {"mixed": "しかし、不可欠な contribution をしたもう一人の scientist がいました。ロザリンド・フランクリンです。", "ruby": {"contribution": "貢献", "scientist": "科学者"}},
    (40, 3): {"mixed": "キングス・カレッジ・ロンドンの研究室で、彼女はX線回折の technique を使い、DNAの images を作成していました。", "ruby": {"technique": "技法", "images": "画像"}},
    (40, 4): {"mixed": "「写真51」として知られる一枚の photograph は、らせん構造の重要な証拠となるX字型の模様を明らかにしました。", "ruby": {"photograph": "写真"}},
    (40, 5): {"mixed": "しかし、その photograph は、彼女の知らないうちにワトソンへ見せられました。", "ruby": {"photograph": "写真"}},
    (40, 10): {"mixed": "ロザリンド・フランクリンの dedication は、長い間過小評価されていました。", "ruby": {"dedication": "献身"}},
    (40, 11): {"mixed": "今、私たちは彼女の静かな contribution を覚えておかなければなりません。", "ruby": {"contribution": "貢献"}},
    (41, 1): {"mixed": "第二次世界大戦中、英国のブレッチリー・パークで、若い数学者アラン・チューリングはドイツのエニグマ暗号を crack しようとしていました。", "ruby": {"crack": "破る"}},
    (41, 2): {"mixed": "ドイツの submarine 艦隊は毎日、encrypted 通信を交わしていました。", "ruby": {"submarine": "潜水艦", "encrypted": "暗号化された"}},
    (41, 3): {"mixed": "それらを解読できなければ、連合国 navy の艦船が次々と沈められるおそれがありました。", "ruby": {"navy": "海軍"}},
    (41, 4): {"mixed": "チューリングは同僚たちとともに、ボンベと呼ばれる machine を作りました。", "ruby": {"machine": "機械"}},
    (41, 5): {"mixed": "その machine は、logic によって不可能なエニグマ設定をすばやく除外し、チームが多くの通信を解読するのを助けました。", "ruby": {"machine": "機械", "logic": "論理"}},
    (41, 6): {"mixed": "戦後、チューリングは reason を働かせ、「machine は考えられるか」という問いを探究しました。", "ruby": {"reason": "理性", "machine": "機械"}},
    (41, 7): {"mixed": "彼の theory はコンピューター科学の foundation となり、のちの人工知能をめぐる議論につながりました。", "ruby": {"theory": "理論", "foundation": "基礎"}},
    (41, 8): {"mixed": "しかし当時の法律では同性愛が犯罪とされ、彼は prosecuted されました。", "ruby": {"prosecuted": "起訴された"}},
    (41, 11): {"mixed": "2013年、エリザベス2世女王は彼に正式な pardon を与えました。", "ruby": {"pardon": "恩赦"}},
    (41, 12): {"mixed": "その pardon は、あまりにも遅すぎました。", "ruby": {"pardon": "恩赦"}},
    (42, 1): {"mixed": "シルクロードは古代から、東のアジアと西のヨーロッパを結ぶ connection でした。", "ruby": {"connection": "つながり"}},
    (42, 2): {"mixed": "それは一本の道ではなく、多くの routes が結びつく網の目でした。", "ruby": {"routes": "ルート"}},
    (42, 4): {"mixed": "merchants はラクダに荷を積み、砂漠や山々を越えました。", "ruby": {"merchants": "商人たち"}},
    (42, 5): {"mixed": "しかし、この道を通って exchange されたのは、商品だけではありませんでした。", "ruby": {"exchange": "交換"}},
    (42, 6): {"mixed": "religion もまた、この道に沿って広まりました。", "ruby": {"religion": "宗教"}},
    (42, 7): {"mixed": "仏教はインドから中国へ spread し、イスラム教はアラビアから中央アジアへ spread しました。", "ruby": {"spread": "広まる"}},
    (42, 8): {"mixed": "言語や芸術も exchange されました。", "ruby": {"exchange": "交換"}},
    (42, 9): {"mixed": "中国の製紙法は西へ伝わり、のちにヨーロッパの学問と culture に貢献しました。", "ruby": {"culture": "文化"}},
    (42, 10): {"mixed": "シルクロードは、歴史上の偉大な exchange を支えた交流網の一つでした。", "ruby": {"exchange": "交流"}},
    (42, 11): {"mixed": "砂漠の風が運んだ言葉は、幾世紀を越え、今も多くの civilizations の根を静かに支えています。", "ruby": {"civilizations": "文明"}},
    (43, 2): {"mixed": "それは、化学 pesticides の使用がどれほど自然を破壊しているかを警告する本でした。", "ruby": {"pesticides": "農薬"}},
    (43, 4): {"mixed": "しかし、pesticides は昆虫だけを殺すわけではありません。", "ruby": {"pesticides": "農薬"}},
    (43, 6): {"mixed": "カーソンは、鳥の鳴き声も聞こえないまま春が来るかもしれないと warning を発しました。", "ruby": {"warning": "警告"}},
    (43, 7): {"mixed": "カーソンの言葉は、国民に広く awareness を呼び起こしました。", "ruby": {"awareness": "意識"}},
    (43, 8): {"mixed": "化学業界は彼女を激しく攻撃し、その仕事を criticized しました。", "ruby": {"criticized": "批判した"}},
    (43, 9): {"mixed": "しかし、彼女の warning は最終的に受け入れられ、米国はDDTのほとんどの使用を禁止しました。", "ruby": {"warning": "警告"}},
    (43, 10): {"mixed": "カーソンの本は、現代の environmental 運動の発展を後押ししました。", "ruby": {"environmental": "環境の"}},
    (43, 11): {"mixed": "ecological balance を保つことは、人類そのものを守ることでもあります。", "ruby": {"ecological balance": "生態学的な均衡"}},
    (44, 7): {"mixed": "当時、イギリスの植民地 rule は塩の monopoly を維持し、インド人が独自に塩を製造または販売することを禁止していました。", "ruby": {"rule": "支配", "monopoly": "独占"}},
    (44, 9): {"mixed": "ガンジーが砂から一握りの塩を拾った瞬間、イギリスの rule は静かに、しかし深く揺さぶられました。", "ruby": {"rule": "支配"}},
    (44, 10): {"mixed": "これは規律ある nonviolent protest であり、武器は一切携行していませんでした。", "ruby": {"nonviolent protest": "非暴力の抗議"}},
    (44, 11): {"mixed": "ガンジーはイギリスによって何度も imprisoned されました。", "ruby": {"imprisoned": "投獄された"}},
    (44, 12): {"mixed": "しかし、彼の nonviolent movement はインドの independence に貢献し、世界中の運動を inspired しました。", "ruby": {"nonviolent movement": "非暴力の運動", "independence": "独立", "inspired": "鼓舞した"}},
    (44, 13): {"mixed": "マーティン・ルーサー・キング・ジュニアは後に、ガンジーの nonviolent 抵抗哲学から深く学びました。", "ruby": {"nonviolent": "非暴力の"}},
    (44, 14): {"mixed": "世界中の movement が、その教訓を自らの正義を求める闘いに取り入れました。", "ruby": {"movement": "運動"}},
    (45, 4): {"mixed": "それは約230万個の block で constructed されました。", "ruby": {"block": "石材", "constructed": "建設された"}},
    (45, 7): {"mixed": "有力な説明では、重い limestone block を運ぶ傾斜路と組織的な作業班が想定されていますが、正確な方法は今も議論されています。", "ruby": {"limestone block": "石灰岩の石材"}},
    (45, 11): {"mixed": "ancient 王国はずっと前に終わりましたが、その silence は今でも僕たちに語りかけてくるようです。", "ruby": {"ancient": "古代", "silence": "沈黙"}},
    (45, 12): {"mixed": "不老不死を求めた人々の願いは石に刻まれ、今も survive しています。", "ruby": {"survive": "生き延びる"}},
    (47, 1): {"mixed": "market economy では、ほとんどの goods や services の price は demand と supply によって決まります。", "ruby": {"market economy": "市場経済", "goods": "商品", "services": "サービス", "price": "価格", "demand": "需要", "supply": "供給"}},
    (47, 2): {"mixed": "消費者が特定の product を強く demand すると、prices が上昇します。", "ruby": {"product": "製品", "demand": "需要", "prices": "価格"}},
    (47, 3): {"mixed": "demand が減れば prices も下がります。", "ruby": {"demand": "需要", "prices": "価格"}},
    (47, 4): {"mixed": "これが market の最も基本的な仕組みです。", "ruby": {"market": "市場"}},
    (47, 5): {"mixed": "企業は capital を集めて工場で production を行い、products を販売して profit を得ます。", "ruby": {"capital": "資本", "production": "生産", "products": "製品", "profit": "利益"}},
    (47, 6): {"mixed": "competition が激しい industry では、企業は品質の向上を迫られています。", "ruby": {"competition": "競争", "industry": "産業"}},
    (47, 7): {"mixed": "労働者は労働力を提供し、その見返りとして wages や salaries を受け取ります。", "ruby": {"wages": "賃金", "salaries": "給料"}},
    (47, 8): {"mixed": "employment が安定すれば家計の income も安定します。", "ruby": {"employment": "雇用", "income": "所得"}},
    (47, 9): {"mixed": "国は taxes で資金を集め、それを教育や福祉に充てます。", "ruby": {"taxes": "税金"}},
    (47, 10): {"mixed": "bank は loans を提供し、企業は investment によって成長します。", "ruby": {"bank": "銀行", "loans": "融資", "investment": "投資"}},
    (47, 11): {"mixed": "グローバル化が進む現代では、一国の economy は他国の markets と密接に結びついています。", "ruby": {"economy": "経済", "markets": "市場"}},
    (47, 12): {"mixed": "exports と imports が growth を支えます。", "ruby": {"exports": "輸出", "imports": "輸入", "growth": "成長"}},
    (47, 13): {"mixed": "各国の Economies は国境を越えて、絶えず互いに影響し合います。", "ruby": {"Economies": "経済"}},
    (48, 2): {"mixed": "テレビ、新聞、雑誌、インターネットなどの media を通じて、毎日数え切れないほどの advertisements が僕たちの元に届きます。", "ruby": {"media": "メディア", "advertisements": "広告"}},
    (48, 3): {"mixed": "advertisement の目的は、consumer の attention を引き、その人を購入へ persuade することです。", "ruby": {"advertisement": "広告", "consumer": "消費者", "attention": "注目", "persuade": "説得する"}},
    (48, 4): {"mixed": "製品の品質と同様に、brand の image も僕たちの choice に influence を与えます。", "ruby": {"brand": "ブランド", "image": "イメージ", "choice": "選択", "influence": "影響"}},
    (48, 9): {"mixed": "今日の社会では、consumption をめぐって corporations、consumers、国家が互いを監視する三角関係で結びついています。", "ruby": {"consumption": "消費", "corporations": "企業", "consumers": "消費者"}},
    (48, 10): {"mixed": "僕たち自身も、示されているものに対して批判的な目を保つことが求められています。", "ruby": {}},
    (49, 3): {"mixed": "主な原因の一つは、化石 fuel の燃焼によって生じる二酸化 carbon の emission です。", "ruby": {"fuel": "燃料", "carbon": "炭素", "emission": "排出"}},
    (49, 5): {"mixed": "その結果、海面は rise し、洪水や干ばつが頻繁に発生し、台風もかつてないほど強くなっています。", "ruby": {"rise": "上昇する"}},
    (49, 8): {"mixed": "2015年にパリ Agreement が結ばれ、世界は気温の rise を1.5度以内に抑える goal を設定しました。", "ruby": {"Agreement": "協定", "rise": "上昇する", "goal": "目標"}},
    (49, 9): {"mixed": "各国は renewable なエネルギーへの投資を増やし、自動車や工場からの emissions を regulate し始めています。", "ruby": {"renewable": "再生可能な", "emissions": "排出", "regulate": "規制する"}},
    (49, 10): {"mixed": "しかし、climate の変動はもはや一国だけで解決できる問題ではありません。", "ruby": {"climate": "気候"}},
    (49, 11): {"mixed": "international な cooperation なしに、地球の未来を守ることはできません。", "ruby": {"international": "国際的な", "cooperation": "協力"}},
    (49, 12): {"mixed": "sustainable な社会の実現は、今や世代を超えた共通の goal となっています。", "ruby": {"sustainable": "持続可能な", "goal": "目標"}},
    (50, 2): {"mixed": "国連は education を受ける権利を universal な人権の一つとして declared しました。", "ruby": {"education": "教育", "universal": "普遍的な", "declared": "宣言した"}},
    (50, 3): {"mixed": "しかし実際には、生まれた国や家庭の income によって education の opportunity は大きく異なります。", "ruby": {"income": "所得", "education": "教育", "opportunity": "機会"}},
    (50, 5): {"mixed": "先進国の中でも、education の quality や access には大きな格差があります。", "ruby": {"education": "教育", "quality": "質", "access": "アクセス"}},
    (50, 6): {"mixed": "家庭の経済状況は、子供の将来の career を大きく左右します。", "ruby": {"career": "職業"}},
    (50, 8): {"mixed": "これは、individual が identity を形成し、社会で responsibility のある一員に成長する過程です。", "ruby": {"individual": "個人", "identity": "アイデンティティ", "responsibility": "責任"}},
    (50, 9): {"mixed": "多くの国が、奨学金や授業料減免を通じて、より多くの若者に高等 education の opportunity を開こうとしています。", "ruby": {"education": "教育", "opportunity": "機会"}},
    (50, 11): {"mixed": "真の equality がある社会を築くには、すべての子どもに同じ education の opportunity が与えられなければなりません。", "ruby": {"equality": "平等", "education": "教育", "opportunity": "機会"}},
    (50, 12): {"mixed": "education に equality が実現して初めて、社会の格差は縮まり始めるのです。", "ruby": {"education": "教育", "equality": "平等"}},
    (51, 1): {"mixed": "artificial な知能、つまりAIはこの10年間で目覚ましい progress を遂げました。", "ruby": {"artificial": "人工の", "progress": "進展"}},
    (51, 4): {"mixed": "それぞれの application が僕たちの生活を変えています。", "ruby": {"application": "応用"}},
    (51, 5): {"mixed": "一部の industry では、automation によって労働の風景がすでに変化しています。", "ruby": {"industry": "産業", "automation": "自動化"}},
    (51, 6): {"mixed": "しかし、急速な技術の progress には深刻な risks も伴います。", "ruby": {"progress": "進展", "risks": "危険"}},
    (51, 8): {"mixed": "僕たちの社会は、こうした consequences に正面から向き合わなければなりません。", "ruby": {"consequences": "結果"}},
    (51, 10): {"mixed": "自動運転車が事故を起こした場合、法廷では誰が accountable となるのでしょうか？", "ruby": {"accountable": "責任を負うべき"}},
    (51, 12): {"mixed": "世界中の政府が、AIに関する regulations の整備を始めています。", "ruby": {"regulations": "規制"}},
    (51, 13): {"mixed": "欧州連合はすでに、AIの ethical な使用に関する包括的な法律を制定しています。", "ruby": {"ethical": "倫理的な"}},
    (51, 15): {"mixed": "ethical な目的に使うかどうかは、僕たち人間の judgment にかかっています。", "ruby": {"ethical": "倫理的な", "judgment": "判断"}},
    (51, 16): {"mixed": "AIは、僕たちの代わりに考えるためではなく、僕たちが以前よりよく考えられるように存在しなければなりません。", "ruby": {}},
    (52, 3): {"mixed": "2020年3月、世界保健機関はこれを pandemic だと declared しました。", "ruby": {"pandemic": "パンデミック", "declared": "宣言"}},
    (52, 4): {"mixed": "各国はそれぞれ lockdowns を実施し、学校や多くの企業が閉鎖されました。", "ruby": {"lockdowns": "外出制限"}},
    (52, 5): {"mixed": "感染した patients は、各地域の hospitals に搬送されました。", "ruby": {"patients": "患者", "hospitals": "病院"}},
    (52, 11): {"mixed": "研究者たちは前例のない速さで vaccine を developed しました。", "ruby": {"vaccine": "ワクチン", "developed": "開発"}},
    (52, 12): {"mixed": "1年あまりのうちに複数の vaccines が承認され、世界各地で接種が始まりました。", "ruby": {"vaccines": "ワクチン"}},
    (52, 13): {"mixed": "pandemic は僕たちに多くの lessons を残しました。", "ruby": {"pandemic": "パンデミック", "lessons": "教訓"}},
    (52, 14): {"mixed": "public な衛生体制への備えが、いかに重要であるかということです。", "ruby": {"public": "公的な"}},
    (52, 15): {"mixed": "international な協力がなければ、感染症を食い止めることはできません。", "ruby": {"international": "国際的な"}},
    (52, 16): {"mixed": "次の crisis に備えるため、僕たちはこれらの lessons を忘れてはなりません。", "ruby": {"crisis": "危機", "lessons": "教訓"}},
    (53, 1): {"mixed": "20世紀初頭、世界の population のうち urban な地域に住んでいたのは、約10人に1人だけでした。", "ruby": {"population": "人口", "urban": "都市の"}},
    (53, 3): {"mixed": "Urbanization は雇用、教育、医療の機会を集中させる一方、深刻な問題ももたらしました。", "ruby": {"Urbanization": "都市化"}},
    (53, 4): {"mixed": "Traffic の渋滞、住宅価格の高騰、大気 pollution などがその例です。", "ruby": {"Traffic": "交通", "pollution": "汚染"}},
    (53, 6): {"mixed": "これら世界の主要都市は、それぞれ population の density や infrastructure の限界に直面しています。", "ruby": {"population": "人口", "density": "密度", "infrastructure": "インフラ"}},
    (53, 7): {"mixed": "近年、各都市は、より sustainable な urban 計画を試み始めています。", "ruby": {"sustainable": "持続可能な", "urban": "都市の"}},
    (53, 8): {"mixed": "歩行者や cyclists のための道を増やし、緑の公園を復元し、公共 transportation への investment を増やしています。", "ruby": {"cyclists": "自転車利用者", "transportation": "交通", "investment": "投資"}},
    (53, 9): {"mixed": "同時に、人々は都市中心部から suburbs へ移り始めています。", "ruby": {"suburbs": "郊外"}},
    (53, 10): {"mixed": "リモートワークの普及により、urban な暮らしと田園の暮らしの区別は、以前ほど明確ではなくなりました。", "ruby": {"urban": "都市の"}},
    (54, 3): {"mixed": "世界中から集まった athlete たちは、長年の training を経て、competition に臨みます。", "ruby": {"athlete": "選手", "training": "訓練", "competition": "競技"}},
    (54, 4): {"mixed": "彼らの discipline と dedication は、何よりも貴重です。", "ruby": {"discipline": "規律", "dedication": "献身"}},
    (54, 6): {"mixed": "相手を尊重し、ルールを守る精神、Sportsmanship こそがスポーツの本来の姿です。", "ruby": {"Sportsmanship": "スポーツマンシップ"}},
    (54, 7): {"mixed": "近年、ドーピング問題が世界中の competition を揺るがしてきました。", "ruby": {"competition": "競技"}},
    (54, 8): {"mixed": "禁止薬物を使用した athlete は、メダルを剥奪され、競技から除外されます。", "ruby": {"athlete": "選手"}},
    (54, 9): {"mixed": "fair なプレーの原則を守るためには、厳格な検査が不可欠です。", "ruby": {"fair": "公正な"}},
    (54, 10): {"mixed": "勝ったチームには熱狂的な fan が集まり、負けたチームには静かな拍手が送られます。", "ruby": {"fan": "ファン"}},
    (54, 11): {"mixed": "defeat を受け入れて次の挑戦に向かうこと、それがスポーツの本当の美しさです。", "ruby": {"defeat": "敗北"}},
    (54, 12): {"mixed": "テレビの前の子どもたちは、そんな athletes たちに憧れています。", "ruby": {"athletes": "選手"}},
    (54, 13): {"mixed": "彼らは模範となる role を担い、努力は実を結ぶという message を若い世代に伝えています。", "ruby": {"role": "役割", "message": "メッセージ"}},
    (55, 1): {"mixed": "日本は、世界で最も急速に aging が進む社会の一つです。", "ruby": {"aging": "高齢化"}},
    (55, 4): {"mixed": "workforce は縮小し、pension 制度を維持することが難しくなっています。", "ruby": {"workforce": "労働力", "pension": "年金"}},
    (55, 5): {"mixed": "高齢者の medical 費用は年々増え、国の budget を圧迫しています。", "ruby": {"medical": "医療の", "budget": "予算"}},
    (55, 6): {"mixed": "welfare をどう維持するかは、すべての先進国に共通する課題です。", "ruby": {"welfare": "福祉"}},
    (55, 8): {"mixed": "子どもや孫と離れて暮らす elderly が増え、loneliness という新たな問題が現れています。", "ruby": {"elderly": "高齢者", "loneliness": "孤独"}},
    (55, 9): {"mixed": "一人暮らしの elderly を支えるため、地域ではさまざまな取り組みが始まっています。", "ruby": {"elderly": "高齢者"}},
    (55, 10): {"mixed": "volunteer たちが定期的に訪問し、介護施設は職員不足を新しい技術で補おうとしています。", "ruby": {"volunteer": "ボランティア"}},
    (55, 11): {"mixed": "generations 間の支え合いが、これからの社会の基盤となります。", "ruby": {"generations": "世代"}},
    (56, 1): {"mixed": "民主主義社会において、press は「第四の権力」とも呼ばれてきました。", "ruby": {"press": "報道機関"}},
    (56, 3): {"mixed": "Journalists は政府や企業の不正行為を reveal し、それを市民に伝える役割を担っています。", "ruby": {"Journalists": "記者", "reveal": "明らかにする"}},
    (56, 4): {"mixed": "investigative な報道は、社会を変えるきっかけとなることがよくあります。", "ruby": {"investigative": "調査報道の"}},
    (56, 6): {"mixed": "これは、press が最高位の authority にさえ説明責任を求められることを示す一例でした。", "ruby": {"press": "報道機関", "authority": "権力者"}},
    (56, 8): {"mixed": "source を確認せずに発信された情報、そして意図的な disinformation。", "ruby": {"source": "情報源", "disinformation": "偽情報"}},
    (56, 10): {"mixed": "独裁政権下では censorship が広く行われ、journalists が投獄されることも珍しくありません。", "ruby": {"censorship": "検閲", "journalists": "記者"}},
    (56, 11): {"mixed": "press の freedom は、どの国でも当然に保障されているわけではありません。", "ruby": {"press": "報道", "freedom": "自由"}},
    (56, 12): {"mixed": "情報を受け取る側として、僕たちは何が reliable な source かを判断する力を養わなければなりません。", "ruby": {"reliable": "信頼できる", "source": "情報源"}},
    (56, 13): {"mixed": "press の freedom を守ることは、結局、僕たち自身の freedom を守ることです。", "ruby": {"press": "報道", "freedom": "自由"}},
    (57, 2): {"mixed": "その後、彼はアメリカへ渡り、19世紀後半から20世紀初頭にかけて、immigrant として electricity の世界を変革する発明家となりました。", "ruby": {"immigrant": "移民", "electricity": "電気"}},
    (57, 3): {"mixed": "彼の最大の貢献は、交流方式の electricity を実用化したことでした。", "ruby": {"electricity": "電力"}},
    (57, 7): {"mixed": "今日、僕たちの家庭に届くほぼすべての electricity は、テスラが追求した vision に大きく支えられています。", "ruby": {"electricity": "電力", "vision": "構想"}},
    (57, 11): {"mixed": "彼の事業上の partnership はうまくいかず、ウォーデンクリフ・タワー計画は資金不足で頓挫しました。", "ruby": {"partnership": "提携"}},
    (57, 12): {"mixed": "彼の多くの patents は、十分な報酬をもたらしませんでした。", "ruby": {"patents": "特許"}},
    (57, 14): {"mixed": "彼の genius が広く認められたのは、死後になってからです。", "ruby": {"genius": "天才"}},
    (58, 1): {"mixed": "現代社会の court 制度は、暴力ではなく法によって紛争を解決する方法です。", "ruby": {"court": "法廷"}},
    (58, 2): {"mixed": "事件が発生すると、警察はまず捜査を開始し、suspect を arrest します。", "ruby": {"suspect": "容疑者", "arrest": "逮捕"}},
    (58, 13): {"mixed": "評決が有罪であれば、sentence が言い渡されます。", "ruby": {"sentence": "刑"}},
    (58, 14): {"mixed": "punishment には、prison での服役、罰金、社会奉仕などがあります。", "ruby": {"punishment": "刑罰", "prison": "刑務所"}},
    (58, 15): {"mixed": "defendant が判決に同意しない場合は、上級の court に appeal することができます。", "ruby": {"defendant": "被告", "court": "裁判所", "appeal": "控訴"}},
    (59, 8): {"mixed": "彼の理論は多くの議論を引き起こしましたが、彼の大きな貢献は unconscious という概念を世界に広めたことです。", "ruby": {"unconscious": "無意識"}},
    (59, 11): {"mixed": "最近の研究では、私たちの decisions が多くの biases によってどれほど頻繁に歪められているかが明らかになりました。", "ruby": {"decisions": "決定", "biases": "偏見"}},
    (59, 12): {"mixed": "私たちは rational でありたいと願っていますが、emotion や assumption によって簡単に判断を曲げられてしまいます。", "ruby": {"rational": "合理的", "emotion": "感情", "assumption": "思い込み"}},
    (59, 13): {"mixed": "anxiety や depression を経験している人々への therapy も、心理学の大きな貢献です。", "ruby": {"anxiety": "不安", "depression": "うつ病", "therapy": "治療"}},
    (60, 1): {"mixed": "1945年8月6日、人類史上初めて戦争で使われた atomic 爆弾が広島に投下されました。", "ruby": {"atomic": "原子の"}},
    (60, 4): {"mixed": "戦後、世界は核 weapon の時代に入りました。", "ruby": {"weapon": "兵器"}},
    (60, 5): {"mixed": "アメリカとソ連は核兵器の開発を競い、両陣営の conflict は『冷戦』と呼ばれました。", "ruby": {"conflict": "対立"}},
    (60, 7): {"mixed": "核戦争の危険におびえる中、1968年に核不拡散 treaty、NPTが署名のために開放され、多くの国が署名しました。", "ruby": {"treaty": "条約"}},
    (60, 10): {"mixed": "地域戦争が続く中、refugees の数は長期的に増加し、今なお極めて高い水準です。", "ruby": {"refugees": "難民"}},
    (60, 12): {"mixed": "多くの victims が故郷を追われています。", "ruby": {"victims": "被害者"}},
    (60, 14): {"mixed": "しかし、安全保障理事会で常任理事国の拒否権などにより合意できないと、安保理の決定と国連の対応力は大きく制限されます。", "ruby": {}},
    (60, 17): {"mixed": "真の平和は、互いを尊重し、語り合い、reconciliation を求める意志があって初めて生まれます。", "ruby": {"reconciliation": "和解"}},
    (60, 18): {"mixed": "広島と長崎の記憶を世代を超えて伝えていくことは、僕たちの未来に対する責任です。", "ruby": {}},
    (61, 1): {"mixed": "1856年、オーストリア帝国領ブルノのアウグスチノ会修道院で、一人の monk がエンドウ豆の交配実験を始めました。", "ruby": {"monk": "修道士"}},
    (61, 3): {"mixed": "メンデルは、エンドウ豆の trait、つまり茎の長さ、種子の色、種子の形など、明確に区別できる特徴に注目しました。", "ruby": {"trait": "形質"}},
    (61, 4): {"mixed": "約9年にわたり、彼は2万7000株を超える植物を育て、交配し、結果を注意深く記録しました。", "ruby": {}},
    (61, 5): {"mixed": "純系の背の高い親と純系の背の低い親を掛け合わせると、第1世代はすべて背が高くなりました。", "ruby": {}},
    (61, 6): {"mixed": "しかし、その背の高い第1世代を自家受粉させると、第2世代には背の低い植物が再び現れました。", "ruby": {}},
    (61, 7): {"mixed": "単一の形質を調べた第2世代では、現れる特徴の比率はおよそ3対1でした。", "ruby": {}},
    (61, 8): {"mixed": "この観察から、メンデルは一つの trait が、親から一つずつ受け継ぐ二つの要素によって決まると考えました。", "ruby": {"trait": "形質"}},
    (61, 9): {"mixed": "一方の dominant な要素の形質が現れ、もう一方の recessive な要素の形質は同じ世代では隠れました。", "ruby": {"dominant": "優性の", "recessive": "劣性の"}},
    (61, 10): {"mixed": "1865年、彼はその成果をブルノ自然科学協会の二度の会合で発表しました。", "ruby": {}},
    (61, 11): {"mixed": "しかし、その意義は当時の scientists に広く理解されませんでした。", "ruby": {"scientists": "科学者"}},
    (61, 12): {"mixed": "1866年に刊行された論文は、数十年間ほとんど注目されませんでした。", "ruby": {}},
    (61, 13): {"mixed": "20世紀の初め、三人の researchers が相次いでメンデルの論文に注目し、その法則は再評価されました。", "ruby": {"researchers": "研究者"}},
    (61, 14): {"mixed": "彼の experiments は、後に現代 genetics の重要な基礎の一つとして認められました。", "ruby": {"experiments": "実験", "genetics": "遺伝学"}},
    (61, 15): {"mixed": "静かな修道院でエンドウ豆と向き合った一人の monk は、遺伝の規則性を数で示し、生命の理解に大きな科学の光を当てました。", "ruby": {"monk": "修道士"}},
    (62, 1): {"mixed": "この歌詞で用いる推計では、毎年約800万トンの plastic が世界の ocean へ流れ込みます。", "ruby": {"plastic": "プラスチック", "ocean": "海洋"}},
    (62, 2): {"mixed": "歌詞では、その規模を毎分トラック1台分という比喩で示しています。", "ruby": {}},
    (62, 3): {"mixed": "北太平洋には、Great Pacific Garbage Patch と呼ばれる garbage の高濃度海域があります。固いごみ島ではなく、ocean 上で広がりも変動します。", "ruby": {"garbage": "ごみ", "ocean": "海洋"}},
    (62, 4): {"mixed": "海流に運ばれた debris が、長年かけてその広い海域へ集まり、動き続けています。", "ruby": {"debris": "破片"}},
    (62, 5): {"mixed": "大きな plastic の一部は、波・塩・風・紫外線で細かくなり、やがて microplastic になります。", "ruby": {"plastic": "プラスチック", "microplastic": "マイクロプラスチック"}},
    (62, 6): {"mixed": "これらの小さな粒子はプランクトンや魚に取り込まれ、食物網へ入ります。食卓への経路と人への健康影響には、まだ未解明な点があります。", "ruby": {}},
    (62, 7): {"mixed": "海洋生物とその生息地への影響は深刻です。", "ruby": {}},
    (62, 8): {"mixed": "クジラや海鳥が plastic 袋などを餌と confused し、飲み込みによる傷害や死亡につながる例があります。", "ruby": {"plastic": "プラスチック", "confused": "混同する"}},
    (62, 9): {"mixed": "coral 礁は、高水温、海洋酸性化、陸からの化学汚染、海洋ごみなど複数の threat にさらされています。", "ruby": {"coral": "サンゴ", "threat": "脅威"}},
    (62, 10): {"mixed": "各国政府は、レジ袋の有料化や一部の使い捨て plastic の ban などの政策を導入しています。", "ruby": {"plastic": "プラスチック", "ban": "禁止"}},
    (62, 11): {"mixed": "企業は代替素材と recycling 技術へ投資しています。ただし、「生分解性」という表示だけで、海洋中で十分に分解するとは限りません。", "ruby": {"recycling": "再利用"}},
    (62, 12): {"mixed": "個人の選択は重要ですが、それだけでなく、政府・企業・地域を含む仕組み全体の変化が必要です。", "ruby": {}},
    (62, 13): {"mixed": "まず reduce、次に再使用、そして recycling。", "ruby": {"reduce": "減らす", "recycling": "再利用"}},
    (62, 14): {"mixed": "日々の小さな選択は、制度や企業の変化を支え、ocean の未来を変える力になります。", "ruby": {"ocean": "海洋"}},
    (63, 1): {"mixed": "1960年、26歳の英国人ジェーン・グドールは、母ヴァンヌとともに東アフリカの Tanzania にあるゴンベへ到着しました。調査には現地の人々の協力もありました。", "ruby": {"Tanzania": "タンザニア"}},
    (63, 2): {"mixed": "目的は、野生の chimpanzee を本来の自然環境で観察することでした。", "ruby": {"chimpanzee": "チンパンジー"}},
    (63, 3): {"mixed": "当時、若い女性がこの現地調査を率いることは異例でした。ただし、彼女が単身でアフリカ奥地へ入ったわけではありません。", "ruby": {}},
    (63, 4): {"mixed": "その時点で大学の学位はありませんでしたが、のちに学部課程を経ずケンブリッジ大学の博士課程へ進みました。", "ruby": {}},
    (63, 5): {"mixed": "古人類学者ルイス・リーキーは、彼女の passion と patience、動物を注意深く見る力を信じ、研究を支えました。", "ruby": {"passion": "情熱", "patience": "忍耐"}},
    (63, 6): {"mixed": "ゴンベの森で、彼女は何か月も丘や木立から静かに観察を続け、詳細な記録を残しました。", "ruby": {}},
    (63, 7): {"mixed": "やがて chimpanzee は彼女を危険でない存在として受け入れ、日々の行動を観察できる距離が縮まりました。", "ruby": {"chimpanzee": "チンパンジー"}},
    (63, 8): {"mixed": "重要な observation の一つは、chimpanzee が草の茎や小枝を加工し、シロアリを取り出す tool として使う姿でした。", "ruby": {"observation": "観察", "chimpanzee": "チンパンジー", "tool": "道具"}},
    (63, 9): {"mixed": "tool の製作と使用を人間だけの特徴とみなす当時の有力な考えは、この発見によって大きく揺さぶられました。", "ruby": {"tool": "道具"}},
    (63, 10): {"mixed": "グドールは、chimpanzee に異なる個性、複雑な家族関係、喜びや悲しみ、協力と激しい争いがあることも記録しました。", "ruby": {"chimpanzee": "チンパンジー"}},
    (63, 11): {"mixed": "長期にわたる observations は、人類とほかの動物を隔てる線が単純ではないことを示しました。", "ruby": {"observations": "観察"}},
    (63, 12): {"mixed": "その後グドールは、野生動物の conservation と地域主体の保全活動に力を注ぎました。", "ruby": {"conservation": "保全"}},
    (63, 13): {"mixed": "1991年にタンザニアの生徒たちと始めた Roots & Shoots は、現在75か国で youth が地域の人・動物・環境の課題に取り組む活動へ広がっています。", "ruby": {"youth": "若者"}},
    (63, 14): {"mixed": "希望は、行動の中にあります。", "ruby": {}},
    (63, 15): {"mixed": "2025年に生涯を終えた後も、その言葉は未来を案じる多くの youth に、行動へ向かう確かな励ましを残しています。", "ruby": {"youth": "若者"}},
    (64, 1): {"mixed": "パブロ・ピカソは1881年10月25日、スペインのマラガに生まれました。", "ruby": {}},
    (64, 2): {"mixed": "20世紀を代表する painter の一人で、sculpture、版画、陶芸、舞台美術を含む2万点を超える多様な作品を残しました。", "ruby": {"painter": "画家", "sculpture": "彫刻"}},
    (64, 3): {"mixed": "1900年に初めてパリを訪れ、1904年にモンマルトルへ定住しました。Blue Period の painting は1901年ごろから、パリとバルセロナを往復した時期にも描かれました。", "ruby": {"painting": "絵画"}},
    (64, 4): {"mixed": "Rose Period を経た後も、彼の style は古典的表現、Cubism、彫刻、版画、陶芸などへ何度も大きく変化しました。", "ruby": {"style": "様式", "Cubism": "キュビズム"}},
    (64, 5): {"mixed": "ピカソは1907年に『アヴィニョンの娘たち』を完成させました。ただちに一般公開したのではなく、初の公的展示は1916年でした。", "ruby": {}},
    (64, 6): {"mixed": "この作品は、自然主義的な人体と遠近法を崩し、強く様式化した幾何学的な shape へ再構成して美術界を揺さぶりました。", "ruby": {"shape": "形"}},
    (64, 7): {"mixed": "それは Cubism の重要な先駆けの一つとなり、ピカソとジョルジュ・ブラックの緊密な共同実験から新しい運動が発展しました。", "ruby": {"Cubism": "キュビズム"}},
    (64, 8): {"mixed": "Cubism は、一つの perspective に基づく自然主義的な再現を揺さぶり、画面の平面性と対象の構造を探りました。", "ruby": {"Cubism": "キュビズム", "perspective": "遠近法"}},
    (64, 9): {"mixed": "ピカソとブラックは、複数の角度や時間の知覚から得た shape を、一枚の canvas 上で分解し再構成しました。", "ruby": {"shape": "形", "canvas": "キャンバス"}},
    (64, 10): {"mixed": "1937年4月26日、フランコ側を支援するドイツのコンドル軍団とイタリア義勇航空隊が、バスク地方の町ゲルニカを爆撃しました。", "ruby": {}},
    (64, 11): {"mixed": "爆撃による suffering を受け、ピカソは既に依頼されていたスペイン館の巨大な painting『ゲルニカ』を、5月1日から6月4日にかけて制作しました。", "ruby": {"suffering": "苦しみ", "painting": "絵画"}},
    (64, 12): {"mixed": "作品は1937年のパリ万国博覧会スペイン館で公開され、戦争と民間人への暴力を告発する国際的な symbol になりました。", "ruby": {"symbol": "象徴"}},
    (64, 13): {"mixed": "ピカソは一つの style に留まらず、媒体と表現を生涯にわたって変え続けました。", "ruby": {"style": "様式"}},
    (64, 14): {"mixed": "「子どものように描くことを学ぶには長い時間がかかった」という趣旨の言葉は広くピカソの発言とされますが、逐語的な出典は確かではありません。", "ruby": {}},
    (64, 15): {"mixed": "ピカソが20世紀と contemporary 美術の表現領域を大きく広げたことは確かですが、その作品と人物像は今も多面的・批判的に検討されています。", "ruby": {"contemporary": "現代の"}},
    (65, 1): {"mixed": "1990年代半ば、多くの国で家庭からのインターネット接続が広がり始めました。ただし、普及時期は国や地域で異なります。", "ruby": {}},
    (65, 2): {"mixed": "それから約30年で、僕たちの生活、仕事、人とのつながり方は根本から transformed されました。", "ruby": {"transformed": "変えられた"}},
    (65, 3): {"mixed": "手紙や固定電話が担っていた communication の一部は、今ではメッセージアプリやソーシャルメディアを通じて瞬時に行われます。", "ruby": {"communication": "意思疎通"}},
    (65, 4): {"mixed": "十分な回線、端末、技能があれば、地球の反対側の友人ともリアルタイムで顔を見て話せます。", "ruby": {}},
    (65, 5): {"mixed": "仕事の形も変わりました。", "ruby": {}},
    (65, 6): {"mixed": "新型コロナウイルスの流行期、遠隔で行える職種では在宅勤務が急速に広がりました。", "ruby": {}},
    (65, 7): {"mixed": "自宅や共同作業空間で働く人が増えた一方、現場の仕事は置き換えられず、通信環境、住環境、管理方法によって利点と負担が変わります。", "ruby": {}},
    (65, 8): {"mixed": "同時に、新しい課題も明らかになりました。", "ruby": {}},
    (65, 9): {"mixed": "個人情報が、いつ、誰に、何の目的で使われるかという privacy の問題です。", "ruby": {"privacy": "個人情報保護"}},
    (65, 10): {"mixed": "詐欺、認証情報の盗難、端末やサービスの弱点に備える security の課題です。", "ruby": {"security": "安全対策"}},
    (65, 11): {"mixed": "誤りを意図せず広める misinformation と、意図的に作って広める偽情報が、急速に拡散します。", "ruby": {"misinformation": "誤情報"}},
    (65, 12): {"mixed": "情報の質を一者だけで保証することはできません。僕たちは発信元、根拠、日付、別資料を確かめ、報道機関、研究者、プラットフォームも説明責任を負います。", "ruby": {}},
    (65, 13): {"mixed": "ソーシャルメディアの algorithm にはさまざまな目的がありますが、多くは閲覧時間や反応を増やす推薦に使われます。", "ruby": {"algorithm": "計算手順"}},
    (65, 14): {"mixed": "気づかないまま長時間スマートフォンを見続けることはありますが、長時間利用だけで病気と決めつけることはできません。", "ruby": {}},
    (65, 15): {"mixed": "自分で制御できず生活に重大な支障が続く addiction に似た問題的利用や digital dependency は、睡眠、学業、心身に影響し得ます。", "ruby": {"addiction": "依存症", "digital": "デジタルの", "dependency": "依存"}},
    (65, 16): {"mixed": "インターネットは有用な基盤ですが、中立な道具だけではありません。設計、事業モデル、規則、利用環境も結果を形づくります。", "ruby": {}},
    (65, 17): {"mixed": "僕たち一人ひとりの judgment は重要ですが、企業、政府、学校、家庭にも、安全で健全な環境をつくる責任があります。", "ruby": {"judgment": "判断"}},
    (65, 18): {"mixed": "digital 時代に人間らしく生きることは、接続できる人とできない人の格差も含め、次世代とともに取り組む challenge です。", "ruby": {"digital": "デジタルの", "challenge": "課題"}},
    (66, 1): {"mixed": "紀元前753年の建国はロムルスとレムスの伝承上の年代で、考古学的に確定した創建日ではありません。", "ruby": {}},
    (66, 2): {"mixed": "初期のローマは王政を経て、紀元前509年と伝えられるころから共和政となりました。共和政では市民集会、毎年選ばれる政務官、元老院が関わりましたが、政治的影響力は富裕層へ偏っていました。", "ruby": {}},
    (66, 3): {"mixed": "紀元前264年までにローマはイタリア半島の有力勢力となり、カルタゴとのポエニ戦争後に西地中海の覇権を握りました。地中海全域の支配は、さらに後の征服を経たものです。", "ruby": {}},
    (66, 4): {"mixed": "共和政では senate、毎年選ばれる二人の consuls、市民集会、ほかの政務官、属州総督が、拡大する territory を分担して統治しました。", "ruby": {"senate": "元老院", "consuls": "執政官", "territory": "領土"}},
    (66, 5): {"mixed": "紀元前1世紀、内戦と社会対立が深まる中で、ユリウス・カエサルが軍事と政治の中心人物となりました。", "ruby": {}},
    (66, 6): {"mixed": "カエサルはガリアを征服し、大きな富と territory をローマへもたらしましたが、戦争は現地の人々に大量の死、捕虜、奴隷化をもたらしました。", "ruby": {"territory": "領土"}},
    (66, 7): {"mixed": "カエサルは終身独裁官となり、紀元前44年3月15日、共和政を守ると主張した元老院議員らの陰謀で暗殺されました。", "ruby": {}},
    (66, 8): {"mixed": "カエサルの養子で遺言上の相続人だったオクタウィアヌスは、内戦の唯一の後継者ではなく競争者の一人でしたが、勝利後の紀元前27年に senate からアウグストゥスの称号を受け、最初の emperor とされます。", "ruby": {"senate": "元老院", "emperor": "皇帝"}},
    (66, 9): {"mixed": "共和政が一日で empire に変わったのではありません。内戦の後、アウグストゥスは共和政の制度を残したまま、実権を集中させた元首政を築きました。", "ruby": {"empire": "帝国"}},
    (66, 10): {"mixed": "紀元前27年ごろから西暦180年ごろはパクス・ロマーナと呼ばれ、帝国内の相対的安定と繁栄が続きました。しかし辺境の戦争、征服、反乱、奴隷制は続き、恩恵も均等ではありませんでした。", "ruby": {}},
    (66, 11): {"mixed": "最盛期には地中海沿岸のほぼ全域がローマ支配下に入りました。道路、水道橋、浴場が各地に建てられ、コロッセウムは西暦80年にローマで完成しました。", "ruby": {}},
    (66, 12): {"mixed": "3世紀の empire は、内戦、短命な軍人皇帝、疫病、経済不安、国境への圧力に直面しましたが、その後に再編と回復もありました。", "ruby": {"empire": "帝国"}},
    (66, 13): {"mixed": "395年、テオドシウス1世の死後、empire の統治は二人の息子の東西宮廷へ再び分担されました。東西は以前にも分けられており、東の帝国はその後も約千年続きました。", "ruby": {"empire": "帝国"}},
    (66, 14): {"mixed": "476年、ゲルマン系の軍司令官オドアケルが西の少年皇帝を退位させました。西の empire は一度に滅びたのではなく、権力、軍、住民、制度が長い時間をかけて変化しました。", "ruby": {"empire": "帝国"}},
    (66, 15): {"mixed": "西の empire が消えた後も、その legacy はラテン語系言語、法、都市、建築、キリスト教制度などに残りました。ただし、その遺産には征服と奴隷制も含まれ、ヨーロッパだけでなく地中海、北アフリカ、西アジアの歴史にも連なります。", "ruby": {"empire": "帝国", "legacy": "遺産"}},
    (67, 1): {"mixed": "人間の brain は平均約1.3キログラムですが、個人差があります。", "ruby": {"brain": "脳"}},
    (67, 2): {"mixed": "重さは体重の一部にすぎません。その中には約860億個と推計される neurons と、それらがつくる巨大な network があります。ただし860億は、すべての人に共通する厳密な値ではありません。", "ruby": {"neurons": "神経細胞", "network": "つながり"}},
    (67, 3): {"mixed": "一つひとつの neuron は、synapses を介して何千ものほかのニューロンとつながります。", "ruby": {"neuron": "神経細胞", "synapses": "接合部"}},
    (67, 4): {"mixed": "brain 全体には100兆を超えるとも推計される synapses があり、網目状の network を形作ります。数は測定法によって幅があります。", "ruby": {"brain": "脳", "synapses": "接合部", "network": "つながり"}},
    (67, 5): {"mixed": "記憶、知覚、感情、判断。", "ruby": {}},
    (67, 6): {"mixed": "私たちが『自己』と呼ぶものを形作る働きには、複雑な neural network の活動が関わっています。", "ruby": {"neural network": "神経回路網"}},
    (67, 7): {"mixed": "物質である brain から consciousness がどのように生じるかは、科学の大きな未解明問題の一つです。", "ruby": {"brain": "脳", "consciousness": "意識"}},
    (67, 8): {"mixed": "20世紀末以降、機能的磁気共鳴画像法などの imaging を使い、研究者は brain の活動に伴う血流や血中酸素の変化を調べられるようになりました。神経活動を直接見ているわけではありません。", "ruby": {"imaging": "画像化", "brain": "脳"}},
    (67, 9): {"mixed": "何かを見るときや思い出すときに brain のどの領域が関わるかは、時間とともに変わる信号から推定できます。ただし神経活動を完全なリアルタイムで直接追跡しているわけではありません。", "ruby": {"brain": "脳"}},
    (67, 10): {"mixed": "かつての常識を改めた重要な発見の一つは、brain の plasticity です。", "ruby": {"brain": "脳", "plasticity": "可塑性"}},
    (67, 11): {"mixed": "かつて成人の brain は、ほとんど変化しないと広く考えられていました。", "ruby": {"brain": "脳"}},
    (67, 12): {"mixed": "現在では、新しい経験と学習により、neurons 間の結合を含む回路が生涯にわたり変化し得ると分かっています。ただし子どもと同じ速さや範囲ではありません。", "ruby": {"neurons": "神経細胞"}},
    (67, 13): {"mixed": "アルツハイマー病、パーキンソン病、脳卒中。", "ruby": {}},
    (67, 14): {"mixed": "brain diseases や brain injuries に苦しむ人々のため、病気や損傷に応じた治療と支援が、今も世界中で研究されています。", "ruby": {"brain diseases": "脳疾患", "brain injuries": "脳損傷"}},
    (67, 15): {"mixed": "brain の recovery を最大限に引き出すためですが、回復の程度や速さには大きな個人差があります。", "ruby": {"brain": "脳", "recovery": "回復"}},
    (67, 16): {"mixed": "brain の研究は、人間とは何かという最も深い問いへ私たちを導きます。しかし、その答えは神経科学だけで決まるものではありません。", "ruby": {"brain": "脳"}},
    (68, 1): {"mixed": "18世紀末、フランスは財政危機に加え、凶作とパン価格高騰による深刻な famine に苦しみました。飢餓の程度は地域や時期で異なります。", "ruby": {"famine": "飢饉"}},
    (68, 2): {"mixed": "tax 負担や高いパン価格は peasants と都市貧困層を圧迫しました。聖職者・貴族の特権、王室と庶民の格差も不満を深めましたが、マリー・アントワネット一人が危機の原因ではありません。", "ruby": {"tax": "税", "peasants": "農民"}},
    (68, 3): {"mixed": "ヴォルテールやルソーを含む啓蒙思想は教養層へ広まりましたが、財政危機、アメリカ独立革命、三部会の対立、民衆行動も革命を動かしました。", "ruby": {}},
    (68, 4): {"mixed": "Liberty、平等、そして人間の尊厳。", "ruby": {"Liberty": "自由"}},
    (68, 5): {"mixed": "こうした ideals は revolution を動かした要因の一つでした。単独の引き金ではありません。", "ruby": {"ideals": "理想", "revolution": "革命"}},
    (68, 6): {"mixed": "1789年7月14日、パリの群衆は武器と火薬を求め、国王権力の象徴だった要塞兼監獄バスティーユを襲撃しました。解放された囚人はわずかでした。", "ruby": {}},
    (68, 7): {"mixed": "この事件は revolution の象徴的な転換点ですが、三部会、国民議会、球戯場の誓いは既に始まっていました。", "ruby": {"revolution": "革命"}},
    (68, 8): {"mixed": "同年8月、国民 Assembly は『人および市民の権利の宣言』を採択し、人は自由で権利において平等だと declared しました。けれど女性や植民地の奴隷に、その平等は実現しませんでした。", "ruby": {"Assembly": "議会", "declared": "宣言"}},
    (68, 9): {"mixed": "共和政の宣言は1792年9月で、ルイ16世はその後の1793年1月21日に処刑されました。", "ruby": {}},
    (68, 10): {"mixed": "フランスは1792年に君主制を廃して republic となりました。王の処刑より先です。", "ruby": {"republic": "共和国"}},
    (68, 11): {"mixed": "revolution の恐怖政治期、内外戦争と内戦の中で公安委員会と革命政府が弾圧を強めました。多くの死刑判決に加え、裁判外の殺害や獄死、内戦の犠牲も生じ、ロベスピエール一人だけの行為ではありません。", "ruby": {"revolution": "革命"}},
    (68, 12): {"mixed": "1799年、若い将軍ナポレオン・ボナパルトは協力者とともにブリュメール18日のクーデターで総裁政府を倒し、統領政府を築きました。これを revolution の終結とみなすかは議論があります。", "ruby": {"revolution": "革命"}},
    (68, 13): {"mixed": "その reform は法の統一、信仰の自由、財産保護を進め、revolution の一部原則を各地へ広げました。ただし戦争と占領を伴い、民法は家父長権を強め、1802年には植民地奴隷制を復活させました。", "ruby": {"reform": "改革", "revolution": "革命"}},
    (68, 14): {"mixed": "Liberty、平等、友愛。三語は革命期に結びつきましたが、共和国の原則として定着したのは1848年以後です。", "ruby": {"Liberty": "自由"}},
    (68, 15): {"mixed": "revolution の ideals は各国の権利思想や政治運動へ大きな影響を与えましたが、すべての民主社会の唯一の基礎ではなく、植民地主義や人種・性別の排除を伴う矛盾も残しました。", "ruby": {"revolution": "革命", "ideals": "理想"}},
    (69, 1): {"mixed": "1929年、エドウィン・ハッブルとミルトン・ヒューマソンの観測は、遠い galaxy ほど速く遠ざかる関係を示しました。1927年にはジョルジュ・ルメートルも膨張と関係式を論じていました。", "ruby": {"galaxy": "銀河"}},
    (69, 2): {"mixed": "これは universe 全体の空間が expanding いることを示す重要な観測証拠となりました。", "ruby": {"universe": "宇宙", "expanding": "膨張して"}},
    (69, 3): {"mixed": "現在も expanding いる universe を過去へたどると、物質と放射は極めて高温・高密度でした。空間内の一地点から起きた爆発という意味ではありません。", "ruby": {"expanding": "膨張して", "universe": "宇宙"}},
    (69, 4): {"mixed": "膨張する宇宙という theory は、フリードマンやルメートルらの理論と、その後の観測から発展しました。", "ruby": {"theory": "理論"}},
    (69, 5): {"mixed": "現在の universe は、約138億年前の非常に高温・高密度な初期状態から膨張してきたと考えられています。", "ruby": {"universe": "宇宙"}},
    (69, 6): {"mixed": "最初の数分に水素・ヘリウムなどの原子核が生まれ、約38万年後に原子ができ、数億年後に最初の stars が輝き始めました。", "ruby": {"stars": "星"}},
    (69, 7): {"mixed": "ペンジアスとウィルソンは1964年に、どこへ向けても残る弱いマイクロ波へ気づき、原因を確かめたうえで1965年に報告しました。", "ruby": {}},
    (69, 8): {"mixed": "宇宙マイクロ波 background 放射は、ビッグバンから約38万年後、宇宙が透明になって自由に進み始めた光の名残です。", "ruby": {"background": "背景"}},
    (69, 9): {"mixed": "これはビッグバン theory を宇宙論の標準モデルへ導いた、極めて重要な証拠の一つとなりました。", "ruby": {"theory": "理論"}},
    (69, 10): {"mixed": "天の川 galaxy の stars は、およそ1000億から4000億と推計されます。歌詞の2000億から4000億も概数です。", "ruby": {"galaxy": "銀河", "stars": "星"}},
    (69, 11): {"mixed": "観測可能な universe の galaxies は少なくとも1000億、推計によっては約2兆です。天の川の星数と厳密に同じではありません。", "ruby": {"universe": "宇宙", "galaxies": "銀河"}},
    (69, 12): {"mixed": "universe の質量・エネルギー収支では、通常物質は約5パーセントで、残る約95パーセントの正体には大きな謎があります。", "ruby": {"universe": "宇宙"}},
    (69, 13): {"mixed": "光では直接見えず重力の影響から推定される dark 物質と、universe の加速膨張に対応づけられる暗黒エネルギー。どちらも正体は未解明です。", "ruby": {"dark": "暗黒の", "universe": "宇宙"}},
    (69, 14): {"mixed": "それらの性質を明らかにすることは、現代 physics の最大級の challenge です。", "ruby": {"physics": "物理学", "challenge": "課題"}},
    (69, 15): {"mixed": "2021年に打ち上げられたジェームズ・ウェッブ宇宙望遠鏡は、universe 誕生後わずか数億年の早期 galaxies から届く光を観測しています。", "ruby": {"universe": "宇宙の", "galaxies": "銀河"}},
    (69, 16): {"mixed": "その光は約135億年を旅して地球へ届きます。ビッグバンそのものの光ではなく、宇宙誕生から約3億年後の銀河が放った光です。", "ruby": {}},
    (70, 1): {"mixed": "18世紀後半のイギリスで、技術・労働・市場・帝国が絡む長期的な社会経済の変化が加速しました。", "ruby": {}},
    (70, 2): {"mixed": "これが industrial 革命の始まりでした。", "ruby": {"industrial": "産業の"}},
    (70, 3): {"mixed": "ジェームズ・ワットは既存の steam 機関を改良し、燃料効率と動力利用を大きく変えました。彼が蒸気機関を最初に発明したわけではありません。", "ruby": {"steam": "蒸気"}},
    (70, 4): {"mixed": "水力利用は続きましたが、coal を燃料とする機関により manufacturing は立地と稼働の制約を減らしました。", "ruby": {"coal": "石炭", "manufacturing": "製造業"}},
    (70, 5): {"mixed": "マンチェスターなどランカシャーで綿 textile 工場が増え、リバプールは原綿輸入と綿製品輸出の港として結びつきました。", "ruby": {"textile": "繊維"}},
    (70, 6): {"mixed": "田園からの移住、自然増加、アイルランドなどからの移民が urban 人口を増やしました。", "ruby": {"urban": "都市の"}},
    (70, 7): {"mixed": "Urbanization は急速に進み、住宅、上下水道、衛生の整備が人口増加に追いつきませんでした。", "ruby": {"Urbanization": "都市化"}},
    (70, 8): {"mixed": "工場の condition は場所や時期で異なりましたが、多くは危険で劣悪でした。", "ruby": {"condition": "状況"}},
    (70, 9): {"mixed": "12時間を超える日もある長時間労働、低い wages、鉱山や工場で働かされる子どもたちがいました。", "ruby": {"wages": "賃金"}},
    (70, 10): {"mixed": "当時、child まで長時間働かされ、児童労働は社会の深刻な暗部でした。ただし貧困下の家計を支えた現実もありました。", "ruby": {"child": "子ども"}},
    (70, 11): {"mixed": "労働者は18世紀末から union を組織し、規制や弾圧を受けながら賃金と労働時間をめぐって strike を行いました。1871年に組合は法的承認を得ました。", "ruby": {"union": "労働組合", "strike": "ストライキ"}},
    (70, 12): {"mixed": "社会改革者と労働者の運動を背景に、child の労働を制限する法律は1833年以後、段階的に整備されました。但し違反と適用の穴は長く残りました。", "ruby": {"child": "子ども"}},
    (70, 13): {"mixed": "Industrial 革命後、長期的には生産性と生活水準が上がりました。平均寿命の伸びには、公衆衛生、食料、医療など複数の要因があります。", "ruby": {"Industrial": "産業の"}},
    (70, 14): {"mixed": "同時に格差、過密都市の汚染、化石燃料依存を深めました。イギリスの綿業は、帝国主義と大西洋の奴隷労働にも結びついていました。", "ruby": {}},
    (70, 15): {"mixed": "今日の社会もこの transformation の延長線上にあり、利益と犠牲の両方を学ぶ必要があります。", "ruby": {"transformation": "変容"}},
    (71, 13): {"mixed": "metaphor や象徴を通して、詩は私たちの心の奥底に直接届きます。", "ruby": {"metaphor": "隠喩"}},
    (71, 16): {"mixed": "reader と書き手の間に生まれる静かな対話こそ、literature の真の力である。", "ruby": {"reader": "読者", "literature": "文学"}},
    (72, 1): {"mixed": "日本は世界でも有数の earthquake 多発国です。", "ruby": {"earthquake": "地震"}},
    (72, 3): {"mixed": "2011年3月11日、東北地方で巨大な earthquake が発生しました。", "ruby": {"earthquake": "地震"}},
    (72, 4): {"mixed": "モーメントマグニチュード9.0で、日本の観測史上最大、世界でも最大級の earthquake でした。", "ruby": {"earthquake": "地震"}},
    (72, 5): {"mixed": "岩手・宮城・福島などの沿岸を襲った tsunami を主因として、死者・行方不明者が2万人を超える甚大な被害が生じました。", "ruby": {"tsunami": "津波"}},
    (72, 6): {"mixed": "福島第一原子力発電所では、earthquake による外部電源喪失と tsunami による設備損傷が重なり、冷却機能を失って1〜3号機で炉心溶融が起きました。", "ruby": {"earthquake": "地震", "tsunami": "津波"}},
    (72, 7): {"mixed": "震災直後、全国の避難者は約47万人に達し、住み慣れた土地から evacuation を余儀なくされました。", "ruby": {"evacuation": "避難"}},
    (72, 8): {"mixed": "発災直後、消防・警察・自衛隊などの responders が、がれきの中から人々を rescue し続けました。", "ruby": {"responders": "初動対応者", "rescue": "救助する"}},
    (72, 9): {"mixed": "世界各地から多くの aid も届けられました。", "ruby": {"aid": "援助"}},
    (72, 10): {"mixed": "Preparedness は、個人だけでなく地域・行政も担う社会全体の備えです。", "ruby": {"Preparedness": "備え"}},
    (72, 11): {"mixed": "多くの家庭が非常食と水を備え、学校や職場では定期的に evacuation・drills を行っています。", "ruby": {"evacuation": "避難", "drills": "訓練"}},
    (72, 12): {"mixed": "気象庁は緊急地震速報などの warning 情報を運用していますが、速報には時間と精度の限界もあります。", "ruby": {"warning": "警告"}},
    (72, 13): {"mixed": "発災から15年以上が過ぎ、被災地では reconstruction が進む一方、避難生活が続く人もいます。", "ruby": {"reconstruction": "復興"}},
    (72, 15): {"mixed": "私たちには、災害から学んだ lessons を次世代へ正確に引き継ぐ責任があります。", "ruby": {"lessons": "教訓"}},
    (73, 1): {"mixed": "人間の body は、成人で約37兆個と推定される cells から成る複雑な仕組みです。", "ruby": {"body": "体", "cells": "細胞"}},
    (73, 2): {"mixed": "心拍と呼吸の回数は人や活動で変わりますが、目安として心臓は1日に約10万回鼓動し、約2万回呼吸します。", "ruby": {}},
    (73, 3): {"mixed": "食べ物は胃や腸で消化・吸収され、栄養素が血液で body 全体の tissues に運ばれ、エネルギーや材料として使われます。", "ruby": {"body": "体", "tissues": "組織"}},
    (73, 4): {"mixed": "タンパク質、ビタミン、ミネラルなどの栄養素は、body の修復と成長に欠かせません。", "ruby": {"body": "体"}},
    (73, 5): {"mixed": "運動・食事・睡眠は健康の重要な三要素ですが、健康は医療へのアクセスや生活環境、社会的条件にも左右されます。", "ruby": {}},
    (73, 6): {"mixed": "これらが崩れると、さまざまな diseases のリスクが高まることがあります。", "ruby": {"diseases": "病気"}},
    (73, 7): {"mixed": "運動不足は、心臓 disease や2型糖尿病のリスクを高める要因です。", "ruby": {"disease": "病気"}},
    (73, 8): {"mixed": "塩分のとりすぎは高血圧のリスクを高め、糖分のとりすぎは体重増加や肥満に関わります。作用は同じではありません。", "ruby": {}},
    (73, 9): {"mixed": "睡眠不足は immune 機能に影響し、病気のリスクを高めることがあります。", "ruby": {"immune": "免疫の"}},
    (73, 10): {"mixed": "強い、または長く続くストレスは、心と体の両方に影響します。", "ruby": {}},
    (73, 11): {"mixed": "慢性的なストレスは、消化器の不調、頭痛、睡眠障害を悪化させることがあり、うつ病とも関連します。", "ruby": {}},
    (73, 12): {"mixed": "健診や検診は対象や検査に応じて disease の早期発見に役立ちますが、すべての病気を見つけるものではありません。", "ruby": {"disease": "病気"}},
    (73, 13): {"mixed": "Physicians は患者の生活・症状・希望を聞き、必要なら検査や treatment の選択肢を一緒に検討します。", "ruby": {"Physicians": "医師", "treatment": "治療"}},
    (73, 14): {"mixed": "body は人それぞれに異なる大切な存在であり、単なる道具ではありません。", "ruby": {"body": "体"}},
    (73, 15): {"mixed": "日々の小さな選択は健康を支えますが、個人だけに責任を負わせず、周囲の支援や環境も大切です。", "ruby": {}},
    (73, 16): {"mixed": "健康は特別な時だけ気を配るものではなく、体・心・人とのつながりを含む日々の暮らしに根付くものです。", "ruby": {}},
    (74, 1): {"mixed": "世界の各地域には、その土地に固有の ritual や祭りがあります。", "ruby": {"ritual": "儀式"}},
    (74, 2): {"mixed": "それらは、人々の世界観や宗教観、自然との関係を映すことがあります。", "ruby": {}},
    (74, 3): {"mixed": "日本では、初詣、節分、お盆、各地の祭りが、形を変えながら受け継がれています。", "ruby": {}},
    (74, 4): {"mixed": "京都の祇園祭は869年にさかのぼる千年以上の歴史を持ち、青森のねぶた祭では夜の街を大型灯籠、囃子、跳人が彩ります。", "ruby": {}},
    (74, 5): {"mixed": "こうした traditions は、単なる過去の習慣ではありません。", "ruby": {"traditions": "伝統"}},
    (74, 6): {"mixed": "地域の人々が、自分たちは何者かという identity を確かめる場にもなります。", "ruby": {"identity": "アイデンティティ"}},
    (74, 7): {"mixed": "世界には、誕生、成人、結婚、死に関わる rites があります。", "ruby": {"rites": "通過儀礼"}},
    (74, 8): {"mixed": "こうした儀礼は、人生の節目にある人を共同体が支え、新たな段階へ送り出す役割を果たすことがあります。", "ruby": {}},
    (74, 9): {"mixed": "しかし globalization は交流を生む一方、地域文化の継承を難しくすることもあります。", "ruby": {"globalization": "グローバル化"}},
    (74, 10): {"mixed": "都市化や人口移動により、一部地域では祭りの担い手が減っています。", "ruby": {}},
    (74, 11): {"mixed": "衰退・消滅した伝統工芸もありますが、新しい形で続くものもあります。", "ruby": {}},
    (74, 12): {"mixed": "一方で、担い手を中心に、文化を記録・実践・継承する動きもあります。", "ruby": {}},
    (74, 13): {"mixed": "ユネスコの無形 heritage の一覧には、地域社会が継承する各地の文化要素が記載されています。", "ruby": {"heritage": "文化遺産"}},
    (74, 14): {"mixed": "和食、能楽、和紙作りも、日本から記載された別々の文化要素です。", "ruby": {}},
    (74, 15): {"mixed": "Tradition は過去の遺物ではなく、担い手が今も作り直す生きた文化です。", "ruby": {"Tradition": "伝統"}},
    (74, 16): {"mixed": "今を生きる僕たちが、地域の人々とともに次の generation へ手渡す、生きた贈り物です。", "ruby": {"generation": "世代"}},
    (75, 1): {"mixed": "現在、世界では話し言葉や手話を含む約7000の languages が使われています。", "ruby": {"languages": "言語"}},
    (75, 2): {"mixed": "それぞれの language は、話す人々の世界の見方や知識を映すことがあります。", "ruby": {"language": "言語"}},
    (75, 3): {"mixed": "Translation は、ある language の意味を別の言語の言葉で組み立て直す作業です。", "ruby": {"Translation": "翻訳", "language": "言語"}},
    (75, 4): {"mixed": "ただし、単語を一対一で置き換えるだけではありません。", "ruby": {}},
    (75, 5): {"mixed": "例えば「もったいない」「いただきます」「お疲れ様」などの expressions は、英語へ literally 訳すだけでは意味を伝えきれません。", "ruby": {"expressions": "表現", "literally": "文字どおりに"}},
    (75, 6): {"mixed": "それぞれに、日本の文化や場面ごとの気持ちが深く結びついています。", "ruby": {}},
    (75, 7): {"mixed": "逆に、セレンディピティ、ノスタルジア、プライバシーなども、文脈によっては一つの日本語で意味の幅を表しきれません。", "ruby": {}},
    (75, 8): {"mixed": "それぞれの language は、固有の文化的 context の中で意味を持ちます。", "ruby": {"language": "言語", "context": "文脈"}},
    (75, 9): {"mixed": "poetry の translation は、特に難しい課題の一つです。", "ruby": {"poetry": "詩", "translation": "翻訳"}},
    (75, 10): {"mixed": "詩のリズム、音、行間の沈黙まで、別の language で再現するのは極めて難しいことです。", "ruby": {"language": "言語"}},
    (75, 11): {"mixed": "それでも translators は、原文の精神を別の言語で生かすため、長い時間を注ぎます。", "ruby": {"translators": "翻訳者"}},
    (75, 12): {"mixed": "近年、AIによる machine translation は向上しましたが、精度は言語・文脈・分野で異なります。", "ruby": {"machine": "機械", "translation": "翻訳"}},
    (75, 13): {"mixed": "Google翻訳やDeepLは日常のやり取りを助けますが、結果の確認も必要です。", "ruby": {}},
    (75, 14): {"mixed": "文化的 nuance や文学的な美しさの translation では、人間の translator による判断が今も重要です。", "ruby": {"nuance": "ニュアンス", "translation": "翻訳", "translator": "翻訳者"}},
    (75, 15): {"mixed": "Translation は、二つの世界の間に橋を架ける行為です。", "ruby": {"Translation": "翻訳"}},
    (75, 16): {"mixed": "完璧な translation はなくても、作業を続ければ、僕たちは互いの心に少しずつ近づけます。", "ruby": {"translation": "翻訳"}},
    (76, 1): {"mixed": "なぜ人は、生まれた土地を離れるのでしょうか。", "ruby": {}},
    (76, 2): {"mixed": "戦争、貧困、迫害などです。", "ruby": {}},
    (76, 3): {"mixed": "また、より良い暮らしを望んで移住する人もいます。", "ruby": {}},
    (76, 4): {"mixed": "理由はさまざまで、故郷を abandon することを強いられる場合も、自ら移住を選ぶ場合も、その決断は重いものです。", "ruby": {"abandon": "捨てる"}},
    (76, 5): {"mixed": "19世紀から20世紀初頭、ヨーロッパから何百万人もの人々が海を渡って米国へ移住しました。", "ruby": {}},
    (76, 6): {"mixed": "家族が accompany する人も、一人で渡る人もおり、新しい生活を目指しました。", "ruby": {"accompany": "同行する"}},
    (76, 7): {"mixed": "到着後、多くの移民は言葉の壁や手続きに苦労しました。", "ruby": {}},
    (76, 8): {"mixed": "頼れる acquaintance がいない人は、孤独を感じることもありました。", "ruby": {"acquaintance": "知り合い"}},
    (76, 9): {"mixed": "多くの人は、渡航費を afford するのがやっとでした。", "ruby": {"afford": "余裕がある"}},
    (76, 10): {"mixed": "actual な米国での生活は、多くの人にとって想像以上に厳しいものでした。", "ruby": {"actual": "実際の"}},
    (76, 11): {"mixed": "低賃金、過密で衛生状態の悪い住宅、そして差別に直面した人々がいました。", "ruby": {}},
    (76, 12): {"mixed": "それでも、多くの移民は支え合いながら新しい社会へ徐々に adjust しました。", "ruby": {"adjust": "適応する"}},
    (76, 13): {"mixed": "子どもたちは学校で英語を学ぶ一方、家庭の言語も使い、地域の community と関わりました。", "ruby": {"community": "共同体"}},
    (76, 14): {"mixed": "新しい環境に accustomed になるにつれ、自分たちの暮らしを築きました。", "ruby": {"accustomed": "慣れた"}},
    (76, 15): {"mixed": "同時に、移民は ancestors の文化や言語も受け継ぎました。", "ruby": {"ancestors": "先祖"}},
    (76, 16): {"mixed": "料理、音楽、祭り。", "ruby": {}},
    (76, 17): {"mixed": "移民自身が担い手となり、その diversity は社会の文化や経済を豊かにしました。", "ruby": {"diversity": "多様性"}},
    (76, 18): {"mixed": "今日、世界中の多くの都市は多文化社会です。", "ruby": {}},
    (76, 19): {"mixed": "異なる文化が共に生きるには、互いへの tolerance、prejudice と差別を減らす教育・制度・対話が必要です。", "ruby": {"tolerance": "寛容", "prejudice": "偏見"}},
    (76, 20): {"mixed": "社会が diversity を力にできるかは、住民だけでなく、制度や政策を担う側にもかかっています。", "ruby": {"diversity": "多様性"}},
    (77, 1): {"mixed": "私たちは毎日、膨大な量の情報にさらされています。", "ruby": {}},
    (77, 2): {"mixed": "新聞、テレビ、インターネットの articles、ソーシャルメディアの投稿です。", "ruby": {"articles": "記事"}},
    (77, 3): {"mixed": "しかし、そのうち本当に accurate なものは、どれくらいあるでしょうか。", "ruby": {"accurate": "正確な"}},
    (77, 4): {"mixed": "ad は、単に事実を伝えるだけでなく、購入を促すためにも作られます。", "ruby": {"ad": "広告"}},
    (77, 5): {"mixed": "政治 propaganda は、特定の見解を広めるために情報を操作します。", "ruby": {"propaganda": "プロパガンダ"}},
    (77, 6): {"mixed": "今では、誰でもソーシャルメディアで情報を発信できます。", "ruby": {}},
    (77, 7): {"mixed": "その結果、未確認の噂や misleading な情報が、瞬時に広がります。", "ruby": {"misleading": "誤解を招く"}},
    (77, 8): {"mixed": "見出しが sensational であるほど、注目を集めます。", "ruby": {"sensational": "扇情的な"}},
    (77, 9): {"mixed": "では、何を信じればよいのでしょうか。", "ruby": {}},
    (77, 10): {"mixed": "まず、情報の source を確かめます。", "ruby": {"source": "情報源"}},
    (77, 11): {"mixed": "誰が発信し、どの evidence に基づいているのかを見ます。", "ruby": {"evidence": "証拠"}},
    (77, 12): {"mixed": "statistics が引用されていたら、データの集め方を批判的に analyze します。", "ruby": {"statistics": "統計", "analyze": "分析する"}},
    (77, 13): {"mixed": "一つの出来事について、複数の sources を比べることも大切です。", "ruby": {"sources": "情報源"}},
    (77, 14): {"mixed": "一つの perspective だけで判断すると、偏った結論に至ります。", "ruby": {"perspective": "視点"}},
    (77, 15): {"mixed": "critical な思考は、この情報の海で私たちを守る唯一の力です。", "ruby": {"critical": "批判的な"}},
    (77, 16): {"mixed": "メディアリテラシーは、現代を生きる全ての人に欠かせない skill です。", "ruby": {"skill": "技能"}},
    (77, 17): {"mixed": "それは、全ての情報を疑うことではなく、情報に正しく向き合うことです。", "ruby": {}},
    (78, 1): {"mixed": "地球上には、推定870万の species が存在します。", "ruby": {"species": "生物種"}},
    (78, 2): {"mixed": "しかし、そのうち約100万種が、いま extinction の危機に直面していると推定されています。", "ruby": {"extinction": "絶滅"}},
    (78, 3): {"mixed": "最大の原因は、人間活動による habitat の破壊です。", "ruby": {"habitat": "生息地"}},
    (78, 4): {"mixed": "森林破壊、農地への転換、都市化です。", "ruby": {}},
    (78, 5): {"mixed": "動物たちの生息場所が、急速に失われつつあります。", "ruby": {}},
    (78, 6): {"mixed": "密猟も深刻な問題です。", "ruby": {}},
    (78, 7): {"mixed": "象の ivory、サイの角、トラの毛皮です。", "ruby": {"ivory": "象牙"}},
    (78, 8): {"mixed": "違法な取引は、世界各地で続いています。", "ruby": {}},
    (78, 9): {"mixed": "気候変動が、この問題をさらに深刻にしています。", "ruby": {}},
    (78, 10): {"mixed": "海水温の上昇はサンゴ礁の白化を引き起こし、北極の海氷が解ければホッキョクグマは狩り場を失います。", "ruby": {}},
    (78, 11): {"mixed": "環境は、急速に変えられつつあります。", "ruby": {}},
    (78, 12): {"mixed": "しかし、希望もあります。", "ruby": {}},
    (78, 13): {"mixed": "政府やNGOは保護区を設け、絶滅危惧 species の breeding プログラムを運営しています。", "ruby": {"species": "生物種", "breeding": "繁殖"}},
    (78, 14): {"mixed": "科学者は個体数を monitor し、慎重な assessment に基づいて保全計画を作ります。", "ruby": {"monitor": "監視する", "assessment": "評価"}},
    (78, 15): {"mixed": "Biodiversity は、私たちの食料、医薬品、そして地球の気候を支える基盤です。", "ruby": {"Biodiversity": "生物多様性"}},
    (78, 16): {"mixed": "それを守ることは、結局は私たち自身を守ることです。", "ruby": {}},
    (79, 1): {"mixed": "1969年、人類は月に到達しました。", "ruby": {}},
    (79, 2): {"mixed": "50年以上が経過した現在、宇宙 exploration の目標はさらに遠くに設定されています。", "ruby": {"exploration": "探査"}},
    (79, 3): {"mixed": "次の目標は火星です。", "ruby": {}},
    (79, 4): {"mixed": "NASAは2030年代の有人火星 mission に向けた計画を進めています。", "ruby": {"mission": "ミッション"}},
    (79, 5): {"mixed": "民間企業も宇宙開発に本格的に参入しています。", "ruby": {}},
    (79, 6): {"mixed": "SpaceXは再利用可能な rocket を開発し、打ち上げコストを大幅に削減しました。", "ruby": {"rocket": "ロケット"}},
    (79, 7): {"mixed": "しかし、火星への旅は obstacles に満ちています。", "ruby": {"obstacles": "障害"}},
    (79, 8): {"mixed": "地球から火星までの距離は、最も近い時でも約5,500万キロメートルです。", "ruby": {}},
    (79, 9): {"mixed": "6～9か月の飛行中、宇宙飛行士は radiation、微小 gravity、心理的孤立にさらされます。", "ruby": {"radiation": "放射線", "gravity": "重力"}},
    (79, 10): {"mixed": "人類が火星で暮らすためには、oxygen、水、食料の供給が不可欠です。", "ruby": {"oxygen": "酸素"}},
    (79, 11): {"mixed": "将来的には、地下から水を取り出し、温室で作物を育てる colony が構想されています。", "ruby": {"colony": "居住地"}},
    (79, 12): {"mixed": "宇宙 exploration には莫大な費用がかかります。", "ruby": {"exploration": "探査"}},
    (79, 13): {"mixed": "この予算を地球上の問題解決に使うべきだという argument もあります。", "ruby": {"argument": "論点"}},
    (79, 14): {"mixed": "しかし支持者らは、宇宙 exploration が技術革新を生み、地球の問題にも alternative な解決策をもたらすと argue します。", "ruby": {"exploration": "探査", "alternative": "代替の", "argue": "論じる"}},
    (79, 15): {"mixed": "宇宙は人類にとって最後の frontier であり続けるでしょう。", "ruby": {"frontier": "辺境"}},
    (79, 16): {"mixed": "そこに行くという課題は、科学の問題だけではありません。", "ruby": {}},
    (79, 17): {"mixed": "それはまた、人類はどこまで行けるのかという哲学的な問いでもあります。", "ruby": {}},
    (80, 1): {"mixed": "哲学は、当たり前だと思っていることを疑うことから始まります。", "ruby": {}},
    (80, 2): {"mixed": "正義とは何でしょうか？", "ruby": {}},
    (80, 3): {"mixed": "良い人生とは何でしょうか？", "ruby": {}},
    (80, 4): {"mixed": "私たちは何を知ることができるのでしょうか？", "ruby": {}},
    (80, 5): {"mixed": "これらの問いは、2,500年前の古代ギリシャから今日まで問い続けられています。", "ruby": {}},
    (80, 6): {"mixed": "プラトンは、目に見える世界の向こうに完全なイデアの世界があると argue しました。", "ruby": {"argue": "論じる"}},
    (80, 7): {"mixed": "アリストテレスは、concrete な経験を通してのみ真実に近づけると考えました。", "ruby": {"concrete": "具体的な"}},
    (80, 8): {"mixed": "両者の対照は、哲学史の原型となりました。", "ruby": {}},
    (80, 9): {"mixed": "17世紀、デカルトは『我思う、ゆえに我あり』という有名な言葉を書きました。", "ruby": {}},
    (80, 10): {"mixed": "すべてを疑っても、疑っている自分の存在まで疑うことはできません。", "ruby": {}},
    (80, 11): {"mixed": "これが近代哲学の出発点となり、consciousness の問題が中心に置かれました。", "ruby": {"consciousness": "意識"}},
    (80, 12): {"mixed": "カントは、本当に moral な行為とは何かを問いました。", "ruby": {"moral": "道徳的な"}},
    (80, 13): {"mixed": "彼は『自分の行為の原則が、すべての人の原則になり得るかを自問しなさい』と述べました。", "ruby": {}},
    (80, 14): {"mixed": "彼は、善悪の基準を absolute に定めようとしました。", "ruby": {"absolute": "絶対的に"}},
    (80, 15): {"mixed": "ニーチェは、既存の moral な価値観そのものを疑いました。", "ruby": {"moral": "道徳的な"}},
    (80, 16): {"mixed": "彼の『神は死んだ』という宣言は、伝統的価値観が崩壊した近代社会に投げかけられた radical な問いでした。", "ruby": {"radical": "根本的な"}},
    (80, 17): {"mixed": "哲学では、答えを見つけること以上に、問い続けるという行為に意味があります。", "ruby": {}},
    (80, 18): {"mixed": "abstract な問いに向き合うことは、自分たちが何者かを深く理解するための、最も基本的な行為です。", "ruby": {"abstract": "抽象的な"}},
    (81, 1): {"mixed": "探検の歴史は、人類がまだ見たことのない場所を目指してきた歴史でもあります。", "ruby": {}},
    (81, 2): {"mixed": "15世紀末、コロンブスは大西洋を横断し、アメリカ大陸に到達しました。", "ruby": {}},
    (81, 3): {"mixed": "16世紀、マゼラン艦隊は初の世界一周を達成しました。", "ruby": {}},
    (81, 4): {"mixed": "多くの船員が命を落としましたが、彼らの voyage は世界地図を書き換えました。", "ruby": {"voyage": "航海"}},
    (81, 5): {"mixed": "20世紀に入ると、探検の舞台は極地、最高峰、深海、そして空へと移りました。", "ruby": {}},
    (81, 6): {"mixed": "1911年、ノルウェーのアムンゼンが世界初の南極点到達者となりました。", "ruby": {}},
    (81, 7): {"mixed": "約1か月後、スコットの英国隊も到達しましたが、5人全員が帰路で命を落としました。", "ruby": {}},
    (81, 8): {"mixed": "それは harsh な環境での endurance と sacrifice の物語でした。", "ruby": {"harsh": "厳しい", "endurance": "持久力", "sacrifice": "犠牲"}},
    (81, 9): {"mixed": "1953年、エドモンド・ヒラリーとテンジン・ノルゲイは、初めてエベレスト登頂を成し遂げました。", "ruby": {}},
    (81, 10): {"mixed": "二人の determination は、人間の精神が最も困難な obstacles に対してどれほど強くなれるかを示しました。", "ruby": {"determination": "決意", "obstacles": "障害"}},
    (81, 11): {"mixed": "アーネスト・シャクルトンの expedition は、今日でも語り継がれるもう一つの物語です。", "ruby": {"expedition": "遠征"}},
    (81, 12): {"mixed": "彼の船は氷に閉じ込められ、救助の見込みもない中、それでも乗組員全員を生還させました。", "ruby": {}},
    (81, 13): {"mixed": "それは極限で示されたリーダーシップと courage でした。", "ruby": {"courage": "勇気"}},
    (81, 14): {"mixed": "今日、探検は深海、宇宙、そして人体の限界に向かっています。", "ruby": {}},
    (81, 15): {"mixed": "なぜ人は boundary を越えようとするのでしょうか？", "ruby": {"boundary": "境界"}},
    (81, 16): {"mixed": "おそらく、『その先に何があるのか』という問いそのものが、私たちを人間たらしめているからでしょう。", "ruby": {}},
    (82, 1): {"mixed": "30年前、地方都市に小さな電子機器会社が設立されました。", "ruby": {}},
    (82, 2): {"mixed": "創業者は capable なエンジニアで、その commitment は誰よりも強かった。", "ruby": {"capable": "有能な", "commitment": "献身"}},
    (82, 3): {"mixed": "最初の数年間、会社は debt を抱えていました。", "ruby": {"debt": "負債"}},
    (82, 4): {"mixed": "決算の数字は厳しく、revenue もわずかでした。", "ruby": {"revenue": "収入"}},
    (82, 5): {"mixed": "しかし、彼は次々と investor を説得し、少しずつ funds を集めました。", "ruby": {"investor": "投資家", "funds": "資金"}},
    (82, 6): {"mixed": "やがて、その会社は competitive な市場で地位を確立しました。", "ruby": {"competitive": "競争の激しい"}},
    (82, 7): {"mixed": "海外 clients との contracts を獲得し、expansion の波に乗りました。", "ruby": {"clients": "顧客", "contracts": "契約", "expansion": "拡大"}},
    (82, 8): {"mixed": "創業者は chairman として、年次 conference で全 employee に語りかけました。", "ruby": {"chairman": "会長", "conference": "会議", "employee": "従業員"}},
    (82, 9): {"mixed": "『私たちの強みは strategy ではなく、一人ひとりの誠実さだ』と彼は言いました。", "ruby": {"strategy": "戦略"}},
    (82, 10): {"mixed": "現在、同社は commercial な成功を収めながら、地域社会への貢献も忘れていません。", "ruby": {"commercial": "商業の"}},
    (82, 11): {"mixed": "経営の透明性、employees が公平に promoted されること。", "ruby": {"employees": "従業員", "promoted": "昇進する"}},
    (82, 12): {"mixed": "この小さな会社の物語は、ビジネスの成功は数字だけでは測れないことを教えてくれます。", "ruby": {}},
    (83, 1): {"mixed": "映画は最も新しい芸術の一つで、20世紀初頭に芸術・産業として広がりました。", "ruby": {}},
    (83, 2): {"mixed": "わずか100年余りで、映画はあらゆる entertainment の中心になりました。", "ruby": {"entertainment": "娯楽"}},
    (83, 3): {"mixed": "映画の力は、物語を目の前に再現することにあります。", "ruby": {}},
    (83, 4): {"mixed": "dramatic な場面は観客の心を揺さぶり、comedy は laughter を生み出します。", "ruby": {"dramatic": "劇的な", "comedy": "喜劇", "laughter": "笑い"}},
    (83, 5): {"mixed": "優れた映画は、見る人を fascinate し、考えさせる方法で社会問題を提示します。", "ruby": {"fascinate": "魅了する"}},
    (83, 6): {"mixed": "歴史上の出来事を creative な視点から語り直すことで、教科書では表現できない emotional な真実を伝えます。", "ruby": {"creative": "創造的な", "emotional": "感情的な"}},
    (83, 7): {"mixed": "映画 critics は作品を多面的に evaluate します。", "ruby": {"critics": "批評家", "evaluate": "評価する"}},
    (83, 8): {"mixed": "アカデミー賞などの awards は、映画の質を世界に知らせる役割を果たしてきました。", "ruby": {"awards": "賞"}},
    (83, 9): {"mixed": "映画を見ることは単なる娯楽ではありません。", "ruby": {}},
    (83, 10): {"mixed": "暗い劇場で、私たちは他人の人生を追体験します。", "ruby": {}},
    (83, 11): {"mixed": "私たちを impress するのは、映像の美しさだけではありません。", "ruby": {"impress": "感動させる"}},
    (83, 12): {"mixed": "それは登場人物たちの選択や葛藤が、私たち自身の生き方に問いを投げかけるものだからです。", "ruby": {}},
    (83, 13): {"mixed": "デジタル時代では、映画の制作方法と視聴方法が変わりました。", "ruby": {}},
    (83, 14): {"mixed": "しかし、物語を通じて人の心を動かすという本質は、1世紀前に映画が enthusiasm とともに広がって以来、少しも変わっていません。", "ruby": {"enthusiasm": "熱狂"}},
    (84, 1): {"mixed": "世界の population は80億人を超えました。", "ruby": {"population": "人口"}},
    (84, 2): {"mixed": "この歌詞で用いる推計では、今も8億人以上が十分な食料を得られず、hunger に苦しんでいます。", "ruby": {"hunger": "飢餓"}},
    (84, 3): {"mixed": "Agriculture は人類最古の産業の一つで、文明の基盤です。", "ruby": {"Agriculture": "農業"}},
    (84, 4): {"mixed": "古代メソポタミアで灌漑農業が始まって以来、人類は品種改良と新技術により crop の収量を何倍にも増やしてきました。", "ruby": {"crop": "作物"}},
    (84, 5): {"mixed": "20世紀の『緑の革命』では、高収量品種と化学 fertilizers により、特にアジアで食料生産が大きく増え、アフリカの一部にも影響が及びました。", "ruby": {"fertilizers": "肥料"}},
    (84, 6): {"mixed": "しかし同時に、pesticides と fertilizers の過剰使用により土壌や水が汚染され、長期的な問題が生じました。", "ruby": {"pesticides": "農薬", "fertilizers": "肥料"}},
    (84, 7): {"mixed": "近年は、organic な農業と、gene を組み換えた crops の両方が注目されています。", "ruby": {"organic": "有機の", "gene": "遺伝子", "crops": "作物"}},
    (84, 8): {"mixed": "前者は環境への負荷を抑えやすい一方、大量生産には課題があります。後者は収量向上が期待される一方、安全性への懸念も議論されています。", "ruby": {}},
    (84, 9): {"mixed": "もう一つの大きな問題は食品 waste です。", "ruby": {"waste": "廃棄"}},
    (84, 10): {"mixed": "この歌詞では、先進国で生産された食料の約3分の1が捨てられると説明しています。", "ruby": {}},
    (84, 11): {"mixed": "飢えに苦しむ人がいる世界で、これは深刻な矛盾です。", "ruby": {}},
    (84, 12): {"mixed": "食料問題の解決に必要なのは、増産だけではありません。", "ruby": {}},
    (84, 13): {"mixed": "流通の改善、waste の reduction、そして消費者一人ひとりの意識の変化が必要です。", "ruby": {"waste": "廃棄", "reduction": "削減"}},
    (84, 14): {"mixed": "持続可能な方法で世界に食料を行き渡らせることは、これからの世紀における最大の challenge です。", "ruby": {"challenge": "課題"}},
    (85, 1): {"mixed": "今も世界には、elementary な教育さえ十分に受けられない子どもたちがいます。", "ruby": {"elementary": "初等の"}},
    (85, 2): {"mixed": "サハラ以南アフリカや南アジアの多くの地域では、absence や中途退学が深刻な問題です。", "ruby": {"absence": "欠席"}},
    (85, 3): {"mixed": "教育へのアクセスを妨げるものは何でしょうか。", "ruby": {}},
    (85, 4): {"mixed": "貧困、紛争、地理的な孤立、そして男女間の inequality です。", "ruby": {"inequality": "不平等"}},
    (85, 5): {"mixed": "必要な fees を払えない家族、学校まで何時間も歩かなければならない村、女子の通学を妨げる差別的な慣行です。", "ruby": {"fees": "学費"}},
    (85, 6): {"mixed": "こうした disadvantages が、深い inequality を生み出します。", "ruby": {"disadvantages": "不利な条件", "inequality": "不平等"}},
    (85, 7): {"mixed": "多くの研究は、教育が貧困の連鎖を断つための、非常に effective な手段であることを示しています。", "ruby": {"effective": "効果的な"}},
    (85, 8): {"mixed": "十分に educate された女性は、より健康に子どもを育て、より高い所得を得る傾向があります。", "ruby": {"educate": "教育を受けた"}},
    (85, 9): {"mixed": "国連は2030年までに、すべての人へ包摂的で公正な質の高い教育を提供する目標を掲げています。", "ruby": {}},
    (85, 10): {"mixed": "scholarships、digital な学習環境、教師研修を通じて、各国は目標の achievement へそれぞれの道を進めています。", "ruby": {"scholarships": "奨学金", "digital": "デジタルの", "achievement": "達成"}},
    (85, 11): {"mixed": "タブレットとインターネットの普及により、remote な地域でも educational な内容へアクセスしやすくなっています。", "ruby": {"remote": "遠隔の", "educational": "教育の"}},
    (85, 12): {"mixed": "技術は、教育の gap を縮める大きな力になり得ます。", "ruby": {"gap": "格差"}},
    (85, 13): {"mixed": "教育には、一人の人生だけでなく、社会全体を変える力があります。", "ruby": {}},
    (85, 14): {"mixed": "だからこそ、教育への投資は、未来に向けた最も efficient な投資の一つです。", "ruby": {"efficient": "効率の良い"}},
    (86, 1): {"mixed": "法の支配とは、すべての人と国家を含む組織が法に従い、誰も法の上に立たないという principle です。", "ruby": {"principle": "原則"}},
    (86, 2): {"mixed": "この principle は古代ローマの法思想にも見られ、現代の民主社会を支える基盤の一つです。", "ruby": {"principle": "原則"}},
    (86, 3): {"mixed": "成文憲法を最高法規とする国では、constitution の下に他の法律が位置づけられます。", "ruby": {"constitution": "憲法"}},
    (86, 4): {"mixed": "しかし現実には、法の支配が十分に機能しない国や状況があります。", "ruby": {}},
    (86, 5): {"mixed": "Corruption が広がり、権力者が自分の利益のために法をゆがめることがあります。", "ruby": {"Corruption": "汚職"}},
    (86, 6): {"mixed": "裁判官が政治的圧力を受け、independent な判断が難しくなることがあります。", "ruby": {"independent": "独立した"}},
    (86, 7): {"mixed": "犯罪を commit した人は裁判を受け、有罪と判断された場合、法律に基づき confine されることがあります。", "ruby": {"commit": "犯した", "confine": "拘禁される"}},
    (86, 8): {"mixed": "近年、一部の刑事司法制度では、刑罰の目的として単なる懲罰だけでなく rehabilitation も重視されています。", "ruby": {"rehabilitation": "更生"}},
    (86, 9): {"mixed": "元受刑者の社会復帰を支え、犯罪に関わる conduct を繰り返すのを防ぐことが目的です。", "ruby": {"conduct": "行為"}},
    (86, 10): {"mixed": "市民にも、法の支配を支える責任があります。", "ruby": {}},
    (86, 11): {"mixed": "市民が不正に声を上げ、制度の transparency を求めることは、民主社会の健全性を支えます。", "ruby": {"transparency": "透明性"}},
    (86, 12): {"mixed": "法は、社会が交わす約束です。", "ruby": {}},
    (86, 13): {"mixed": "その約束を守り、必要に応じて reform する意志が、自由で公正な社会の基盤を築きます。", "ruby": {"reform": "改革する"}},
    (87, 1): {"mixed": "ある朝、目覚ましが鳴っても僕は起きる気になれず、ただ bored だったのです。", "ruby": {"bored": "退屈していた"}},
    (87, 2): {"mixed": "毎日同じ繰り返しが続くことに、僕は annoyed でした。", "ruby": {"annoyed": "いらいらしていた"}},
    (87, 3): {"mixed": "コーヒーをいれようとしましたが、豆を切らしていました。", "ruby": {}},
    (87, 4): {"mixed": "僕は近所のカフェまで歩き、顔見知りの clerk にコーヒーを注文しました。", "ruby": {"clerk": "店員"}},
    (87, 5): {"mixed": "cash がなかったので、カードで支払いました。", "ruby": {"cash": "現金"}},
    (87, 6): {"mixed": "帰り道、隣に住む年配の女性に会いました。", "ruby": {}},
    (87, 7): {"mixed": "『昨日、庭で大切な指輪をなくしてしまったの』と彼女は言いました。", "ruby": {}},
    (87, 8): {"mixed": "『虫に手を刺されて振り払った拍子に、指輪が飛んでいったの』", "ruby": {}},
    (87, 9): {"mixed": "僕は手伝うことを嫌だとは思いませんでした。", "ruby": {}},
    (87, 10): {"mixed": "むしろ、手伝えてうれしかったのです。", "ruby": {}},
    (87, 11): {"mixed": "シャベルで15分ほど digging すると、土の中から金色の指輪が現れました。", "ruby": {"digging": "掘ること"}},
    (87, 12): {"mixed": "彼女は笑って、『まあ、若い方。あなたは幸運を運んでくれるのね』と言いました。", "ruby": {}},
    (87, 13): {"mixed": "家に戻ると、友人から電話がありました。", "ruby": {}},
    (87, 14): {"mixed": "『来週、キャンプに来ない？』", "ruby": {}},
    (87, 15): {"mixed": "と、彼は尋ねました。", "ruby": {}},
    (87, 16): {"mixed": "僕はすぐに、その誘いを受けました。", "ruby": {}},
    (87, 17): {"mixed": "テントを borrow する必要がありそうでした。", "ruby": {"borrow": "借りる"}},
    (87, 18): {"mixed": "boring だと思っていた一日は、最後には思いがけない circumstance に恵まれた良い一日になりました。", "ruby": {"boring": "退屈な", "circumstance": "成り行き"}},
    (87, 19): {"mixed": "何気ない日常の流れの中で、小さな出来事や conversation がいつも待っています。", "ruby": {"conversation": "会話"}},
    (87, 20): {"mixed": "結局、毎日は僕たちが思うより少し comfortable なのかもしれません。", "ruby": {"comfortable": "心地よい"}},
    (88, 1): {"mixed": "嵐の夜、古い屋敷の ceiling から奇妙な音が聞こえました。", "ruby": {"ceiling": "天井"}},
    (88, 2): {"mixed": "屋敷の主人は書斎から disappear していました。", "ruby": {"disappear": "姿を消す"}},
    (88, 3): {"mixed": "扉は内側から施錠され、窓は brick の壁で塞がれていました。", "ruby": {"brick": "れんが"}},
    (88, 4): {"mixed": "通報を受けた inspector は、急いで現場へ向かいました。", "ruby": {"inspector": "警部"}},
    (88, 5): {"mixed": "彼は長い corridor を歩き、書斎へ入りました。", "ruby": {"corridor": "廊下"}},
    (88, 6): {"mixed": "部屋には、ほとんど何もありませんでした。", "ruby": {}},
    (88, 7): {"mixed": "壁に固定された棚だけが、場違いに見えました。", "ruby": {}},
    (88, 8): {"mixed": "しかし、彼はその違和感を dismiss しませんでした。", "ruby": {"dismiss": "退ける"}},
    (88, 9): {"mixed": "棚の後ろには、隠し通路への入口がありました。", "ruby": {}},
    (88, 10): {"mixed": "inspector は hesitate せず、中へ入りました。", "ruby": {"inspector": "警部", "hesitate": "ためらう"}},
    (88, 11): {"mixed": "暗い corridor は、地下へ続いていました。", "ruby": {"corridor": "廊下"}},
    (88, 12): {"mixed": "地下室では、屋敷の主人が capture されていました。", "ruby": {"capture": "捕らえられて"}},
    (88, 13): {"mixed": "犯人は、主人の former 共同経営者でした。", "ruby": {"former": "以前の"}},
    (88, 14): {"mixed": "金銭をめぐる dispute が動機でした。", "ruby": {"dispute": "争い"}},
    (88, 15): {"mixed": "inspector は immediately 容疑者を identify しました。", "ruby": {"inspector": "警部", "immediately": "ただちに", "identify": "特定する"}},
    (88, 16): {"mixed": "明確な動機、物的証拠、捨てられた鍵の仕掛けが、すべて彼を指し示していました。", "ruby": {}},
    (88, 17): {"mixed": "事件は、一夜のうちに resolved しました。", "ruby": {"resolved": "解決された"}},
    (88, 18): {"mixed": "真実は、誰の目にも見える場所に隠れていました。", "ruby": {}},
    (89, 1): {"mixed": "民主国家では、投票は最も基本的な市民参加の一つです。", "ruby": {}},
    (89, 2): {"mixed": "有権者は定期的な選挙で投票し、代表者を選びます。", "ruby": {}},
    (89, 3): {"mixed": "選挙運動が始まると、各 candidate は agenda を掲げ、有権者へ訴えます。", "ruby": {"candidate": "候補者", "agenda": "政策課題"}},
    (89, 4): {"mixed": "医療、教育、経済、環境などが主な論点になります。", "ruby": {}},
    (89, 5): {"mixed": "どの論点を emphasize するかが、各 candidate の特徴になります。", "ruby": {"emphasize": "強調する", "candidate": "候補者"}},
    (89, 6): {"mixed": "選挙によっては、単独政党が majority を得られないことがあります。", "ruby": {"majority": "過半数"}},
    (89, 7): {"mixed": "その場合、複数政党が coalition を組み、権力と責任を分担します。", "ruby": {"coalition": "連立"}},
    (89, 8): {"mixed": "coalition 政権では、compromise が欠かせません。", "ruby": {"coalition": "連立", "compromise": "妥協"}},
    (89, 9): {"mixed": "制度によっては、選挙で elect された指導者が閣僚を appoint し、federal 政府の各 department を率います。", "ruby": {"elect": "選出する", "appoint": "任命する", "federal": "連邦の", "department": "部門"}},
    (89, 10): {"mixed": "新しい法案は、立法府の approval を得て初めて法律になります。", "ruby": {"approval": "承認"}},
    (89, 11): {"mixed": "近年、一部の国では選挙への関心が低下しています。", "ruby": {}},
    (89, 12): {"mixed": "投票率が下がり、「自分には関係ない」と政治を ignore する若者もいます。", "ruby": {"ignore": "無視する"}},
    (89, 13): {"mixed": "しかし、投票しない人は結果を形づくる重要な機会を失います。", "ruby": {}},
    (89, 14): {"mixed": "民主主義は、市民の継続的な参加によって機能します。", "ruby": {}},
    (89, 15): {"mixed": "一方、世界には自由で真正な選挙が行われていない国もあります。", "ruby": {}},
    (89, 16): {"mixed": "投票権を advocate する人々は、すべての成人市民が不合理な制限なく投票できる権利を求め続けています。", "ruby": {"advocate": "支持する"}},
    (89, 17): {"mixed": "選挙は完璧ではありませんが、今も私たちが持つ crucial な手段の一つです。", "ruby": {"crucial": "極めて重要な"}},
    (93, 2): {"mixed": "しかしその代償として、体と心の健康が neglect されがちです。", "ruby": {"neglect": "おろそかにする"}},
    (93, 3): {"mixed": "Lung の機能は運動をしないと衰え、使わない muscle の量は diminish します。", "ruby": {"Lung": "肺", "muscle": "筋肉", "diminish": "減少"}},
    (93, 4): {"mixed": "座りっぱなしの生活は、糖尿病や心臓 disease の factor となります。", "ruby": {"disease": "病気", "factor": "要因"}},
    (93, 5): {"mixed": "睡眠の質も crucial です。", "ruby": {"crucial": "極めて重要"}},
    (93, 6): {"mixed": "深夜にスマホの screen を見つめると、脳は intense な光にさらされ、眠りが浅くなります。", "ruby": {"screen": "画面", "intense": "強い"}},
    (93, 7): {"mixed": "Consequently、翌日の集中力は considerably 低下します。", "ruby": {"Consequently": "そのため", "considerably": "著しく"}},
    (93, 8): {"mixed": "精神面では、anxiety や depression を抱える人が増えています。", "ruby": {"anxiety": "不安", "depression": "うつ病"}},
    (93, 9): {"mixed": "社会の競争が intense になるほど、その burden は重くなります。", "ruby": {"intense": "激しく", "burden": "負担"}},
    (93, 10): {"mixed": "健康を maintain するために necessary なことは、特別なことではありません。", "ruby": {"maintain": "維持する", "necessary": "必要な"}},
    (93, 12): {"mixed": "そして、困ったときは hesitate せずに助けを求めましょう。", "ruby": {"hesitate": "ためらう"}},
    (93, 13): {"mixed": "体と心は inseparable です。", "ruby": {"inseparable": "切り離せない"}},
    (93, 15): {"mixed": "心が安定すれば、体も recover します。", "ruby": {"recover": "回復"}},
    (94, 4): {"mixed": "不動産価格は earnings の伸びをはるかに上回るペースで increase しています。", "ruby": {"earnings": "収入", "increase": "上昇"}},
    (94, 5): {"mixed": "この問題は、多くの国で domestic な政策課題として intense な議論を引き起こしました。", "ruby": {"domestic": "国内の", "intense": "激しい"}},
    (94, 6): {"mixed": "mayor や governor は対策を propose しますが、その effect は限定的です。", "ruby": {"mayor": "市長", "governor": "知事", "propose": "提案", "effect": "効果"}},
    (94, 7): {"mixed": "多くの residents が、より安い suburbs へ移っています。", "ruby": {"residents": "住民", "suburbs": "郊外"}},
    (94, 8): {"mixed": "しかし通勤時間は considerably 長くなり、生活の quality が低下するという outcome は無視できません。", "ruby": {"considerably": "かなり", "quality": "質", "outcome": "結果"}},
    (94, 10): {"mixed": "安定した住まいは、子どもの教育、residents の健康、地域の stability に直結します。", "ruby": {"residents": "住民", "stability": "安定"}},
    (94, 11): {"mixed": "adequate な住居は、すべての人の right であるべきです。", "ruby": {"adequate": "十分で適切な", "right": "権利"}},
    (95, 3): {"mixed": "仕事は、その人らしさを形作る大きな factor でもあります。", "ruby": {"factor": "要因"}},
    (95, 4): {"mixed": "学生は大学を卒業し、求人に apply して、hire されます。", "ruby": {"apply": "応募", "hire": "採用"}},
    (95, 5): {"mixed": "新しい employer のもとで働き始め、同僚や上司と associate しながら、仕事のスキルを学びます。", "ruby": {"employer": "雇用主", "associate": "関わる"}},
    (95, 7): {"mixed": "fail することもあります。", "ruby": {"fail": "失敗"}},
    (95, 8): {"mixed": "仕事に suitable でないと判断されれば、fire されることもあります。", "ruby": {"suitable": "適した", "fire": "解雇"}},
    (95, 9): {"mixed": "Unemployment は、経済面だけでなく心の健康にも大きな impact を与えます。", "ruby": {"Unemployment": "失業", "impact": "影響"}},
    (95, 10): {"mixed": "一方、自分の talent を生かして enterprise を立ち上げる人もいます。", "ruby": {"talent": "才能", "enterprise": "企業"}},
    (95, 11): {"mixed": "venture には risk が伴いますが、potentially 大きな reward にもつながります。", "ruby": {"venture": "冒険的事業", "risk": "危険", "potentially": "潜在的に", "reward": "報酬"}},
    (95, 12): {"mixed": "キャリアの途中で profession を変える人が増えています。", "ruby": {"profession": "職業"}},
    (95, 13): {"mixed": "人生100年時代には、一つの仕事に cling する必要はありません。", "ruby": {"cling": "しがみつく"}},
    (95, 14): {"mixed": "priority は、人生のステージごとに変わります。", "ruby": {"priority": "優先事項"}},
    (95, 15): {"mixed": "大切なのは、自分の仕事に meaning を見出すことです。", "ruby": {"meaning": "意味"}},
    (95, 16): {"mixed": "Satisfaction は給料の額ではなく、自分が社会に contribute しているという実感の中にあります。", "ruby": {"Satisfaction": "満足", "contribute": "貢献"}},
    (96, 1): {"mixed": "国際関係は国家間の complex な網の目です。", "ruby": {"complex": "複雑な"}},
    (96, 2): {"mixed": "Alliances、treaties、貿易協定は、世界の秩序を支える枠組みを形成します。", "ruby": {"Alliances": "同盟", "treaties": "条約"}},
    (96, 3): {"mixed": "しかし、国家間の利害が conflict すると、tension が高まります。", "ruby": {"conflict": "衝突", "tension": "緊張"}},
    (96, 4): {"mixed": "aggression に転じる国もあれば、negotiate することを選ぶ国もあります。", "ruby": {"aggression": "侵略", "negotiate": "交渉"}},
    (96, 6): {"mixed": "その目的は、交渉を通じて紛争を平和的に resolve することでした。", "ruby": {"resolve": "解決"}},
    (96, 7): {"mixed": "しかし、安全保障理事会の veto が、しばしば obstacle となってきました。", "ruby": {"veto": "拒否権", "obstacle": "障害"}},
    (96, 8): {"mixed": "冷戦中、世界は二つの opposite な陣営に分かれていました。", "ruby": {"opposite": "対立する"}},
    (96, 9): {"mixed": "核兵器の脅威は overwhelming な抑止力として機能しましたが、世界は constantly 危機の瀬戸際にありました。", "ruby": {"overwhelming": "圧倒的な", "constantly": "絶えず"}},
    (96, 10): {"mixed": "冷戦終結後も、地域紛争、テロ、サイバー攻撃など、新たな脅威が emerge し続けています。", "ruby": {"emerge": "現れ"}},
    (96, 11): {"mixed": "どのような問題も、一国だけでは resolve できません。", "ruby": {"resolve": "解決"}},
    (96, 12): {"mixed": "diplomat の仕事は、対立する利害の間に橋を架けることです。", "ruby": {"diplomat": "外交官"}},
    (96, 13): {"mixed": "互いに oppose する国家が mutual な利益を見いだすこと、それが外交の ultimate objective です。", "ruby": {"oppose": "反対", "mutual": "相互の", "ultimate": "究極の", "objective": "目的"}},
    (97, 1): {"mixed": "地球上には、既知の mammals だけでも6,000 species 以上が存在します。", "ruby": {"mammals": "哺乳類", "species": "種"}},
    (97, 3): {"mixed": "Tropical 雨林は地球表面の約6%しか占めませんが、全 species の半分以上がそこに dwell しています。", "ruby": {"Tropical": "熱帯の", "species": "種", "dwell": "生息"}},
    (97, 5): {"mixed": "原因は numerous です。", "ruby": {"numerous": "数多く"}},
    (97, 9): {"mixed": "Plastic 汚染は whales や turtles に被害を与え、tide によって運ばれる化学物質は食物連鎖を threaten しています。", "ruby": {"Plastic": "プラスチック", "whales": "クジラ", "turtles": "カメ", "tide": "潮", "threaten": "脅かして"}},
    (97, 10): {"mixed": "しかし、保全活動は成果を yield し始めています。", "ruby": {"yield": "もたらし"}},
    (97, 11): {"mixed": "ある先住民コミュニティは、先祖たちの森林を保護し、コミュニティ主導の pioneering な保全モデルを確立しました。", "ruby": {"pioneering": "先駆的な"}},
    (97, 12): {"mixed": "エコシステムは subtle なバランスの上に成り立っています。", "ruby": {"subtle": "微妙な"}},
    (97, 14): {"mixed": "自然と coexist する知恵を見つけられるかどうかが、この地球の未来を左右します。", "ruby": {"coexist": "共生"}},
    (98, 2): {"mixed": "私たちが目覚めた瞬間から眠るまで、Electronic devices はそばにあります。", "ruby": {"Electronic": "電子の", "devices": "機器"}},
    (98, 3): {"mixed": "朝は alarm が鳴り、スマホでニュースを check します。", "ruby": {"alarm": "目覚まし", "check": "確認"}},
    (98, 4): {"mixed": "朝食は electronic 決済で支払い、automobile のナビでオフィスまで案内されます。", "ruby": {"electronic": "電子の", "automobile": "自動車"}},
    (98, 5): {"mixed": "オフィスには、膨大なデータを handle する equipment が installed されています。", "ruby": {"handle": "扱う", "equipment": "機器", "installed": "導入"}},
    (98, 7): {"mixed": "vehicles の電動化は排気ガスを減らし、都市の空気を considerably きれいにすると期待されています。", "ruby": {"vehicles": "車両", "considerably": "かなり"}},
    (98, 8): {"mixed": "Battery 技術の性能は急速に enhanced されています。", "ruby": {"Battery": "電池", "enhanced": "高められて"}},
    (98, 9): {"mixed": "一方で、privacy の喪失やデジタル divide の問題は深刻さを増しています。", "ruby": {"privacy": "プライバシー", "divide": "格差"}},
    (98, 10): {"mixed": "テクノロジーの恩恵を fairly 分配することは、社会の obligation です。", "ruby": {"fairly": "公正に", "obligation": "義務"}},
    (98, 11): {"mixed": "テクノロジーは私たちの可能性を enables するものであり、支配するものではありません。", "ruby": {"enables": "広げる"}},
    (98, 12): {"mixed": "私たちがテクノロジーを master するのか、それに dominated されるのか。その選択は常に私たちの手の中にあります。", "ruby": {"master": "使いこなす", "dominated": "支配される"}},
    (99, 2): {"mixed": "朝何を食べるかという小さな選択から、どの profession に就くか、誰と暮らすかという重大な decision まで。", "ruby": {"profession": "職業", "decision": "決断"}},
    (99, 3): {"mixed": "私たちは常に correct な選択をできるとは限りません。", "ruby": {"correct": "正しい"}},
    (99, 4): {"mixed": "私たちは間違いを犯し、regret を感じます。", "ruby": {"regret": "後悔"}},
    (99, 5): {"mixed": "しかし多くの場合、failure は次の一歩への insight をもたらします。", "ruby": {"failure": "失敗", "insight": "洞察"}},
    (99, 6): {"mixed": "Fear はしばしば、私たちの歩みを止めます。", "ruby": {"Fear": "恐れ"}},
    (99, 9): {"mixed": "その Fear を乗り越えて一歩 forward に踏み出すのが courage です。", "ruby": {"Fear": "恐れ", "forward": "前へ", "courage": "勇気"}},
    (99, 10): {"mixed": "fate という言葉があります。", "ruby": {"fate": "運命"}},
    (99, 11): {"mixed": "しかし fate は、あらかじめ determined されたものではありません。", "ruby": {"fate": "運命", "determined": "決められた"}},
    (99, 12): {"mixed": "日々の decision を通じて、私たちは自分の道を determine します。", "ruby": {"decision": "決断", "determine": "決める"}},
    (99, 13): {"mixed": "かつてある philosopher は、人生は forward にしか生きられず、backward にしか理解できないと言いました。", "ruby": {"philosopher": "哲学者", "forward": "前へ", "backward": "後ろから"}},
    (99, 14): {"mixed": "それは precisely その通りかもしれません。", "ruby": {"precisely": "まさに"}},
    (99, 16): {"mixed": "Occasionally、私たちは立ち止まり、振り返り、また歩き出します。", "ruby": {"Occasionally": "時折"}},
    (99, 17): {"mixed": "人生に guarantee はありません。", "ruby": {"guarantee": "保証"}},
    (99, 18): {"mixed": "でも precisely だからこそ、一日一日が precious なのです。", "ruby": {"precisely": "まさに", "precious": "大切"}},
    (100, 1): {"mixed": "その日、美術館では特別 exhibition が開かれていました。", "ruby": {"exhibition": "展覧会"}},
    (100, 2): {"mixed": "ヨーロッパから運ばれた valuable な絵画が、日本で初めて exhibit されていました。", "ruby": {"valuable": "貴重な", "exhibit": "展示"}},
    (100, 4): {"mixed": "最初の部屋には、15世紀の portrait が展示されていました。", "ruby": {"portrait": "肖像画"}},
    (100, 5): {"mixed": "王や貴族の顔が、primitive でありながら力強い筆致で描かれていました。", "ruby": {"primitive": "素朴な"}},
    (100, 6): {"mixed": "次の部屋には impression 派の絵画がありました。", "ruby": {"impression": "印象"}},
    (100, 8): {"mixed": "光を capture しようとする試みが、画家それぞれの個性とともに現れていました。", "ruby": {"capture": "捉える"}},
    (100, 9): {"mixed": "私は一枚の絵の前で立ち止まり、長い間 gaze していました。", "ruby": {"gaze": "見つめて"}},
    (100, 10): {"mixed": "ほかの来館者は whisper しながら通り過ぎていきました。", "ruby": {"whisper": "ささやき"}},
    (100, 11): {"mixed": "その絵が inspire した何かが、私の中に残りました。", "ruby": {"inspire": "心を動かす"}},
    (100, 12): {"mixed": "女性ガイドは、新たに来館した学生たちへ、絵の歴史的背景を explain していました。", "ruby": {"explain": "説明"}},
    (100, 13): {"mixed": "学生たちは eager にメモを取っていました。", "ruby": {"eager": "熱心に"}},
    (100, 14): {"mixed": "美術館を出たとき、私は心に profound な満足感を抱いていました。", "ruby": {"profound": "深い"}},
    (100, 15): {"mixed": "芸術は時代や場所を超えて、見る人の心に静かな relief をもたらします。", "ruby": {"relief": "安らぎ"}},
    (100, 16): {"mixed": "それは luxury ではなく、人間に必要な nutrition の一つの形です。", "ruby": {"luxury": "贅沢", "nutrition": "栄養"}},
}

# A sung line can contain canonical vocabulary without admitting a natural
# Japanese mixed sentence.  Keep these reviewed lines Japanese-only instead of
# forcing fragments such as “ought だった” or a bare “used” into the caption.
CANONICAL_JAPANESE_ONLY: set[tuple[int, int]] = {
    (15, 4),
    (15, 5),
    (15, 6),
    (15, 7),
    (15, 15),
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def translate_block(lines: list[str]) -> list[str]:
    query = "\n".join(lines)
    params = urllib.parse.urlencode(
        {"client": "gtx", "sl": "en", "tl": "ja", "dt": "t", "q": query}
    )
    request = urllib.request.Request(
        f"https://translate.googleapis.com/translate_a/single?{params}",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    last_error = None
    for attempt in range(1, 5):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = json.loads(response.read().decode("utf-8"))
            translated = "".join(part[0] for part in payload[0]).strip().splitlines()
            if len(translated) == len(lines):
                return [line.strip() for line in translated]
            break
        except Exception as error:  # pragma: no cover - network retry
            last_error = error
            if attempt < 4:
                time.sleep(attempt * 1.5)
    # Preserve one-to-one line integrity if the service reflows a block.
    if len(lines) > 1:
        return [translate_block([line])[0] for line in lines]
    raise RuntimeError(f"translation failed for {lines[0]!r}: {last_error}")


def ensure_translations(manifest: dict, requested: list[int], workers: int) -> dict:
    cache = read_json(CACHE) if CACHE.exists() else {"source": "exact adopted lyrics", "lessons": {}}
    tasks = []
    for number in requested:
        row = manifest["lessons"][number - 1]
        key = row["lesson"]
        cached = cache["lessons"].get(key, [])
        if [item.get("en") for item in cached] != row["lyrics_lines"]:
            tasks.append((number, row["lyrics_lines"]))
    if tasks:
        with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
            futures = {
                executor.submit(translate_block, lines): (number, lines)
                for number, lines in tasks
            }
            for future in as_completed(futures):
                number, lines = futures[future]
                translated = future.result()
                cache["lessons"][f"H{number:03d}"] = [
                    {"en": en, "ja": ja} for en, ja in zip(lines, translated)
                ]
                print(f"translated H{number:03d}: {len(lines)} lines", flush=True)
        CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return cache


def canonical_pos_index() -> dict[tuple[str, str], str]:
    """Read the author-assigned POS without modifying shared lesson JSON."""
    source = SOURCE_HTML.read_text(encoding="utf-8")
    output = {}
    for attrs, body in re.findall(r'<span class="w"([^>]*)>([\s\S]*?)</span>', source):
        def attribute(name: str) -> str:
            match = re.search(rf'{name}="([^"]*)"', attrs)
            return htmlmod.unescape(match.group(1)) if match else ""

        word = htmlmod.unescape(re.sub(r"<[^>]+>", "", body)).strip()
        meaning = attribute("data-ja")
        if word and meaning:
            output[(HELPERS.normalize_en(word), meaning)] = attribute("data-pos")
    return output


def build_dictionaries(lesson_data: list[dict]):
    """Build current-lesson canonical glossaries only.

    Whole-course and WordTacos dictionaries are intentionally excluded: they
    caused easy known words to displace each lesson's actual new vocabulary.
    """
    pos_index = canonical_pos_index()
    local_rows: dict[int, list[dict]] = {}
    for lesson in lesson_data:
        number = int(lesson["b"])
        rows = []
        for paragraph in lesson["vocabSentences"]:
            for item in paragraph["words"]:
                row = {
                    "word": item["w"],
                    "ja": item["ja"],
                    "pos": pos_index.get(
                        (HELPERS.normalize_en(item["w"]), item["ja"]),
                        "",
                    ),
                    "priority": 10,
                    "source": "canonical_new_word",
                }
                rows.append(row)
        local_rows[number] = rows
    return {}, local_rows


def find_high_candidates(
    english: str,
    japanese: str,
    local_rows: list[dict],
    supplemental_rows: list[dict],
) -> list[dict]:
    """Preserve the established high-school weaving policy.

    The shared middle-school helper now requires author-assigned POS metadata,
    but ``high_lessons.json`` intentionally contains only ``w`` and ``ja``.
    Calling the newer helper directly therefore silently changed the full high
    manifest from 1,038 mixed lines to only the hand-written exceptions.  Keep
    the previously established high-school behavior here while retaining its
    morphology-boundary and overlap safety checks.
    """
    candidates = []
    morph_boundaries = {0, len(japanese)}
    for morph in HELPERS.japanese_morphs(japanese):
        morph_boundaries.add(morph["start"])
        morph_boundaries.add(morph["end"])
    sung_targets = HELPERS.english_targets(english, local_rows)
    sung_word_keys = {
        HELPERS.normalize_en(target["row"]["word"])
        for target in sung_targets
    }
    targets = [dict(target, match_origin="sung") for target in sung_targets]

    # The lower caption is a teaching sentence, so a current-lesson canonical
    # word may be woven in when its Japanese meaning is explicitly present,
    # even if the adopted lyric uses an inflection or a close synonym.  This
    # remains lesson-local and meaning-aligned; it never pulls in easy/global
    # words merely to increase the English count.
    for row in supplemental_rows:
        word_key = HELPERS.normalize_en(row["word"])
        if word_key in sung_word_keys or word_key in {"years", "like", "likes"}:
            continue
        targets.append(
            {
                "english": row["word"],
                "row": row,
                "token_orders": (),
                "match_origin": "translation",
            }
        )

    for target in targets:
        row = target["row"]
        if HELPERS.normalize_en(row["word"]) in {"years"}:
            continue
        exact_matches = []
        for surface in HELPERS.japanese_candidates(row["ja"]):
            for match in re.finditer(re.escape(surface), japanese):
                if match.start() not in morph_boundaries or match.end() not in morph_boundaries:
                    continue
                if len(surface) == 1 and HELPERS.KANJI_RE.fullmatch(surface):
                    before = japanese[match.start() - 1] if match.start() else ""
                    after = japanese[match.end()] if match.end() < len(japanese) else ""
                    if HELPERS.KANJI_RE.fullmatch(before) or HELPERS.KANJI_RE.fullmatch(after):
                        continue
                surface_morphs = [
                    item for item in HELPERS.japanese_morphs(surface) if item["content"]
                ]
                last_pos = surface_morphs[-1]["pos"] if surface_morphs else ""
                if HELPERS.normalize_en(row["word"]) in {"like", "likes"} and surface == "好き":
                    continue
                if (
                    last_pos in {"動詞", "形容詞", "形状詞"}
                    and japanese[match.end() :].startswith(("が", "けれど", "けれども", "のに"))
                ):
                    continue
                if last_pos == "動詞" and japanese[match.end() :].startswith(("んだ", "のだ")):
                    continue
                exact_matches.append((match.start(), match.end(), ""))
        if exact_matches:
            source = (
                "canonical_new_word_exact"
                if target["match_origin"] == "sung"
                else "canonical_new_word_translation_exact"
            )
            spans = [(*match, source) for match in exact_matches]
        else:
            spans = []
            for surface in HELPERS.japanese_candidates(row["ja"]):
                match = HELPERS.japanese_morph_span(japanese, surface)
                if match:
                    source = (
                        "canonical_new_word_morph"
                        if target["match_origin"] == "sung"
                        else "canonical_new_word_translation_morph"
                    )
                    spans.append((*match, source))
                    break
        for start, end, suffix, source in spans:
            candidates.append(
                {
                    "start": start,
                    "end": end,
                    "surface": japanese[start:end],
                    "english": target["english"],
                    "reading": japanese[start:end],
                    "priority": (
                        row["priority"]
                        + int(source.endswith("exact"))
                        + (2 if target["match_origin"] == "sung" else 0)
                    ),
                    "source": source,
                    "canonical_word": row["word"],
                    "canonical_meaning": row["ja"],
                    "suffix": suffix,
                    "token_orders": target["token_orders"],
                }
            )
    candidates.sort(
        key=lambda item: (
            item["priority"],
            len(item["surface"]),
            len(item["english"]),
            -(item["token_orders"][0] if item["token_orders"] else 10_000),
        ),
        reverse=True,
    )
    selected = []
    occupied: list[tuple[int, int]] = []
    used_tokens: set[int] = set()
    for item in candidates:
        if used_tokens.intersection(item["token_orders"]):
            continue
        if any(item["start"] < stop and start < item["end"] for start, stop in occupied):
            continue
        selected.append(item)
        occupied.append((item["start"], item["end"]))
        used_tokens.update(item["token_orders"])
        if len(selected) == 4:
            break
    return sorted(selected, key=lambda item: item["start"])


def lookup_word(token: str, global_index: dict, local_rows: list[dict]) -> dict | None:
    candidates = []
    for row in local_rows:
        if HELPERS.stems(row["word"]) & HELPERS.stems(token):
            candidates.append(row)
    for stem in HELPERS.stems(token):
        candidates.extend(global_index.get(stem, []))
    if not candidates:
        return None
    return max(candidates, key=lambda row: (row["priority"], len(row["ja"])))


def fallback_runs(english: str, japanese: str, global_index: dict, local_rows: list[dict]):
    tokens = [token for token in HELPERS.sentence_tokens(english) if token.lower() not in FALLBACK_STOPWORDS]
    for token in tokens:
        row = lookup_word(token, global_index, local_rows)
        if row:
            raw = [
                {"type": "en", "text": token, "ruby": HELPERS.japanese_candidates(row["ja"])[0]},
                {"type": "ja", "text": " — " + japanese},
            ]
            return HELPERS.finalize_runs(raw), token, row["ja"], row["source"]
    # Last-resort exact-line ruby keeps the meaning correct and visible even
    # when the lesson glossary has no safe one-word replacement.
    raw = [
        {"type": "ja", "text": "内容："},
        {"type": "en", "text": english, "ruby": japanese},
    ]
    return HELPERS.finalize_runs(raw), english, japanese, "exact_line_fallback"


def prepare_lesson(number: int, manifest_row: dict, plan: dict, translations: list[dict], global_index, local_rows):
    if len(plan["captions"]) != len(translations):
        raise RuntimeError(f"H{number:03d}: caption/translation count mismatch")
    lyric_stems = {
        stem
        for caption in plan["captions"]
        for token in HELPERS.sentence_tokens(re.sub(r"</?k>", "", caption["en"]))
        for stem in HELPERS.stems(token)
    }
    supplemental_rows = [
        row
        for row in local_rows
        if row.get("pos") in {"noun", "adv"}
        and not (HELPERS.stems(row["word"]) & lyric_stems)
    ]

    lines = []
    canonical_target_lines = mixed_lines = japanese_only_lines = 0
    for index, (caption, translation) in enumerate(zip(plan["captions"], translations), start=1):
        english = re.sub(r"</?k>", "", caption["en"]).replace(r"\N", " ")
        if english != translation["en"]:
            raise RuntimeError(f"H{number:03d} line {index}: exact lyric mismatch")
        japanese = translation["ja"]
        targets = HELPERS.english_targets(english, local_rows)
        manual = CANONICAL_MANUAL_MIXED.get((number, index))
        force_japanese_only = (number, index) in CANONICAL_JAPANESE_ONLY
        if manual:
            target_by_stem = {
                stem: target
                for target in targets
                for stem in HELPERS.stems(target["english"])
            }
            local_by_stem = {
                stem: row
                for row in local_rows
                for stem in HELPERS.stems(row["word"])
            }
            replacements = []
            for actual, reading in manual["ruby"].items():
                target = next(
                    (target_by_stem[stem] for stem in HELPERS.stems(actual) if stem in target_by_stem),
                    None,
                )
                if target is None:
                    row = next(
                        (local_by_stem[stem] for stem in HELPERS.stems(actual) if stem in local_by_stem),
                        None,
                    )
                    # Adjacent current-lesson words can be rendered as one
                    # phrase atom so their visible space is preserved beneath
                    # a single phrase-level meaning ruby.  Accept this only
                    # when every component is independently canonical here.
                    if row is None and " " in actual.strip():
                        phrase_rows = []
                        for word in actual.split():
                            phrase_row = next(
                                (
                                    local_by_stem[stem]
                                    for stem in HELPERS.stems(word)
                                    if stem in local_by_stem
                                ),
                                None,
                            )
                            if phrase_row is None:
                                phrase_rows = []
                                break
                            phrase_rows.append(phrase_row)
                        if phrase_rows:
                            row = {
                                "word": actual,
                                "ja": reading,
                                "source": "canonical_new_word_phrase",
                            }
                    if row is None:
                        raise RuntimeError(
                            f"H{number:03d} line {index}: manual word {actual!r} is not current-lesson canonical vocabulary"
                        )
                    target = {"row": row}
                replacements.append(
                    {
                        "english": actual,
                        "reading": reading,
                        "source": "canonical_new_word_manual",
                        "canonical_word": target["row"]["word"],
                        "canonical_meaning": target["row"]["ja"],
                    }
                )
            runs = HELPERS.runs_from_manual(manual["mixed"], manual["ruby"])
            if manual["ruby"]:
                source = "canonical_new_words_manual"
                mixed_lines += 1
            else:
                source = "japanese_only_manual_translation"
                japanese_only_lines += 1
        elif force_japanese_only:
            runs = HELPERS.finalize_runs([{"type": "ja", "text": japanese}])
            replacements = []
            source = "japanese_only_reviewed_for_naturalness"
            japanese_only_lines += 1
        else:
            spans = find_high_candidates(english, japanese, local_rows, supplemental_rows)
            if spans:
                runs = HELPERS.runs_from_spans(japanese, spans)
                replacements = [
                    {
                        "english": span["english"],
                        "reading": span["reading"],
                        "source": span["source"],
                        "canonical_word": span["canonical_word"],
                        "canonical_meaning": span["canonical_meaning"],
                    }
                    for span in spans
                ]
                source = "canonical_new_words"
                mixed_lines += 1
            else:
                runs = HELPERS.finalize_runs([{"type": "ja", "text": japanese}])
                replacements = []
                source = (
                    "japanese_only_no_safe_canonical_span"
                    if targets
                    else "japanese_only_no_canonical_target"
                )
                japanese_only_lines += 1
        canonical_target_lines += int(bool(targets or replacements))
        lines.append(
            {
                "line": index,
                "start": caption["start"],
                "end": caption["end"],
                "english": english,
                "japanese": japanese,
                "mixed": "".join(run["text"] for run in runs),
                "runs": runs,
                "canonical_targets": [
                    {
                        "english": target["english"],
                        "canonical_word": target["row"]["word"],
                        "meaning": target["row"]["ja"],
                    }
                    for target in targets
                ],
                "replacements": replacements,
                "preparation": source,
            }
        )
    return {
        "lesson": f"H{number:03d}",
        "title_ja": manifest_row["title"].split("—", 1)[-1].strip(),
        "policy": "Exact adopted lyric; word-synchronous fixed-size color-only lyric highlight. Canonical new vocabulary from the current lesson is woven into the Japanese meaning line wherever the meaning remains clear and natural, including meaning-aligned inflections or close lyric synonyms. No whole-course or easy-word fallback. Lines without a safe canonical replacement remain natural Japanese. Japanese-meaning ruby appears on every English segment and hiragana ruby on every Japanese kanji.",
        "translation_source": "Exact adopted lyric Japanese translation; current-lesson canonical Teacher Tacos English vocabulary replacement and ruby validation",
        "line_count": len(lines),
        "canonical_target_lines": canonical_target_lines,
        "mixed_lines": mixed_lines,
        "japanese_only_lines": japanese_only_lines,
        "noncanonical_replacements": 0,
        "lines": lines,
    }


def parse_range(value: str) -> list[int]:
    numbers = set()
    for part in value.split(","):
        if "-" in part:
            start, end = (int(item) for item in part.split("-", 1))
            numbers.update(range(start, end + 1))
        else:
            numbers.add(int(part))
    if not numbers or min(numbers) < 1 or max(numbers) > 160:
        raise argparse.ArgumentTypeError("lessons must be within H1-H160")
    return sorted(numbers)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lessons", default="1-160")
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    requested = parse_range(args.lessons)
    manifest = read_json(MANIFEST)
    lesson_data = read_json(LESSONS)
    cache = ensure_translations(manifest, requested, args.workers)
    global_index, local = build_dictionaries(lesson_data)
    summary_rows = []
    review = [
        "# 高校生編 H001〜H160 採用歌詞・英語混じり全ルビ字幕",
        "",
        "- 上段は採用歌詞を一字句も変えず、歌唱中の語を順に強調。",
        "- 下段は同じ行の意味を表す英語混じり日本語。英語には日本語の意味ルビ、日本語の漢字には読みルビ。",
        "",
    ]
    total_lines = total_targets = total_mixed = total_japanese_only = 0
    for number in requested:
        row = manifest["lessons"][number - 1]
        plan_path = PIPELINE / f"H{number:03d}" / "planning" / "video_plan.json"
        if not plan_path.exists():
            raise FileNotFoundError(plan_path)
        plan = read_json(plan_path)
        prepared = prepare_lesson(
            number, row, plan, cache["lessons"][f"H{number:03d}"], global_index, local[number]
        )
        output = PIPELINE / f"H{number:03d}" / "planning" / "mixed_ruby.json"
        output.write_text(json.dumps(prepared, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        summary_rows.append(
            {
                "lesson": prepared["lesson"],
                "path": str(output.relative_to(PROJECT)),
                "lines": prepared["line_count"],
                "canonical_target_lines": prepared["canonical_target_lines"],
                "mixed_lines": prepared["mixed_lines"],
                "japanese_only_lines": prepared["japanese_only_lines"],
                "noncanonical_replacements": 0,
            }
        )
        total_lines += prepared["line_count"]
        total_targets += prepared["canonical_target_lines"]
        total_mixed += prepared["mixed_lines"]
        total_japanese_only += prepared["japanese_only_lines"]
        review.extend([f"## {prepared['lesson']} {prepared['title_ja']}", ""])
        for line in prepared["lines"]:
            review.append(f"{line['line']:02d}. `{line['mixed']}`")
            review.append(f"    - EN: {line['english']}")
            review.append("    - ルビ: " + " / ".join(f"{item['english']}→{item['reading']}" for item in line["replacements"]))
        review.append("")
    summary = {
        "range": args.lessons,
        "counts": {
            "lessons": len(summary_rows),
            "lines": total_lines,
            "canonical_target_lines": total_targets,
            "mixed_lines": total_mixed,
            "japanese_only_lines": total_japanese_only,
            "noncanonical_replacements": 0,
        },
        "lessons": summary_rows,
    }
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REVIEW.write_text("\n".join(review) + "\n", encoding="utf-8")
    print(json.dumps(summary["counts"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
