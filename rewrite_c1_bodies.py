"""stage_toeic_expert (200語) の body / body_ruby / explanation_ruby を、
文脈に即した独自の例文に書き直す。

各文は編者 (Teacher Tacos English) のオリジナルライティング。
語彙リストや他文献からの転載ではない。
"""
from __future__ import annotations

import json
from pathlib import Path

JSON_PATH = Path(__file__).resolve().parent / "vocab_sources" / "stage_toeic_expert_quizzes_clean.json"

# word -> body sentence (with <word> embed marker)
BODIES: dict[str, str] = {
    "hypothesize": "教授は『記憶は感情に依存する』と<hypothesize>し、3年がかりの実験を組んだ。",
    "postulate": "経済学では合理的個人を出発点に<postulate>するが、現実はかなりズレる。",
    "substantiate": "売上が伸びたという主張を、四半期データで<substantiate>するように上司から求められた。",
    "corroborate": "監視カメラの映像が目撃者の話を<corroborate>したので、判決は早かった。",
    "rebut": "反対派の論点を一つずつ<rebut>するため、登壇者は資料を3冊用意してきた。",
    "contention": "今日の議題の最大の<contention>は、リモートワークを継続するかどうかだ。",
    "paradigm": "AIが文書作成を肩代わりすることで、業務の<paradigm>が大きく書き換わった。",
    "rationale": "予算削減の<rationale>を一言で説明してほしいと社員から問われた。",
    "conjecture": "決算前のアナリストの<conjecture>は、しばしば株価を不安定にする。",
    "dialectic": "ヘーゲルの<dialectic>では、対立する考えの衝突から新しい統合が生まれるとされる。",
    "syllogism": "AはB、BはC、ゆえにAはCというのが古典的な<syllogism>だ。",
    "axiom": "幾何学はいくつかの<axiom>から出発して、定理を積み上げていく。",
    "tenet": "『顧客第一』は、創業当初から変わらない我が社の<tenet>だ。",
    "epistemology": "『何を知ったと言えるのか』を問うのが<epistemology>の中心テーマだ。",
    "heuristic": "最適解を探す時間がない時、人はざっくりした<heuristic>に頼ることが多い。",
    "delineate": "新しい役割の責任範囲を会議で<delineate>しておかないと、後で揉める。",
    "elucidate": "教授は黒板を埋め尽くしながら、複雑な式の意味を<elucidate>してくれた。",
    "expound": "新方針の意図を社員総会で<expound>するため、CEOは1時間枠を取った。",
    "encompass": "今回の改正案は、雇用契約から在宅勤務まで広く<encompass>している。",
    "comprise": "新組織は5つの部門を<comprise>する設計だ。",
    "entail": "海外赴任は、家族の引っ越しと教育環境の変化を<entail>する。",
    "denote": "プログラム中のxはユーザーの年齢を<denote>している。",
    "connote": "『中立』という言葉は『無関心』を<connote>することがある。",
    "epitomize": "彼の作品は、戦後日本の都市デザインを<epitomize>するものとして語られる。",
    "exemplify": "効率と気配りの両立を<exemplify>するスタッフとして、彼女は表彰された。",
    "paraphrase": "研究発表では、引用元の文章を<paraphrase>して自分の言葉に置き換える必要がある。",
    "synthesize": "複数の調査結果を<synthesize>し、最終報告書を1枚にまとめた。",
    "juxtapose": "賛成派と反対派の主張を<juxtapose>すると、争点が一目で見える。",
    "dichotomy": "『仕事vs家庭』という<dichotomy>は、もう古い考えだと言える。",
    "scrutinize": "予算案の各項目を経理が一晩かけて<scrutinize>した。",
    "appraise": "中古マンションを売る前に、不動産会社に物件を<appraise>してもらった。",
    "ascertain": "出張前に、現地の交通機関の運行状況を<ascertain>しておいた方がよい。",
    "discern": "本物の真珠と模造品を<discern>するには、長年の経験が要る。",
    "construe": "条文の『正当な理由』を厳格に<construe>するか緩く読むかで、判決が割れた。",
    "conjure": "昔通った駄菓子屋の匂いが、小学校時代の風景を<conjure>した。",
    "intuit": "ベテランの店長は、客の表情だけで購入の有無を<intuit>する。",
    "salient": "今期決算の<salient>な特徴は、海外売上の比率が逆転した点だ。",
    "pivotal": "彼女はプロジェクトで<pivotal>な役割を果たし、評価も急上昇した。",
    "seminal": "1970年代の<seminal>な論文が、現代の認知科学の出発点になっている。",
    "paramount": "顧客の安全は、コストや効率より<paramount>であるべきだ。",
    "preponderant": "国内市場ではまだ紙の本が<preponderant>だが、電子書籍の追い上げが続く。",
    "predominant": "東京の街路樹で<predominant>なのは、イチョウとケヤキだ。",
    "integral": "リモート対応は、今や採用活動に<integral>な要素となった。",
    "intrinsic": "学ぶ楽しさは、報酬では生まれない<intrinsic>な動機から来る。",
    "inherent": "どの投資手法にも、避けられない<inherent>なリスクがある。",
    "germane": "彼の指摘は、議題に<germane>で、誰も反論できなかった。",
    "pertinent": "会議では、その瞬間に<pertinent>な情報だけを共有してください。",
    "ostensible": "退職の<ostensible>な理由は健康問題だが、本当の事情は別にあるらしい。",
    "tentative": "次の会議の日程はまだ<tentative>で、来週確定する見込みだ。",
    "plausible": "彼の説明は<plausible>に聞こえたが、数字を見たら矛盾だらけだった。",
    "dubious": "突然の値引きには、私はかなり<dubious>な気持ちになった。",
    "equivocal": "答弁が<equivocal>すぎて、結局イエスかノーかわからなかった。",
    "ambivalent": "転職するかどうか、本人もまだ<ambivalent>な気持ちでいるようだ。",
    "nuanced": "賛否を二択にするのではなく、もう少し<nuanced>な議論をしたい。",
    "detrimental": "毎日の長時間残業は、長期的に見て生産性に<detrimental>だ。",
    "deleterious": "睡眠不足は、思考の柔軟性に<deleterious>な影響を与える。",
    "pernicious": "SNSの常時通知は、集中力を<pernicious>に削っていく。",
    "inimical": "保護主義的な関税は、自由貿易の精神に<inimical>だ。",
    "noxious": "倉庫の換気が悪く、<noxious>なガスが滞留していたと指摘された。",
    "inadvertent": "発送ミスは故意ではなく、<inadvertent>な操作ミスから生じたものだ。",
    "erroneous": "報告書には<erroneous>な数値が混ざっていたので、全部差し替えになった。",
    "flawed": "前提が<flawed>な議論は、結論まで読まなくても結果が見える。",
    "untenable": "売上下落の原因を天候だけのせいにする説明は、もう<untenable>だ。",
    "counterintuitive": "値段を上げたら売れた、という<counterintuitive>な結果が報告された。",
    "paradoxical": "節約のために買い込むセール品で、結果的に支出が増えるのは<paradoxical>だ。",
    "augment": "営業力を<augment>するため、新たに3名のメンバーを採用する。",
    "escalate": "顧客の不満を放置すると、軽い問い合わせがやがて<escalate>して大きな問題になる。",
    "propagate": "誤情報は、訂正情報よりも早くSNSで<propagate>することがある。",
    "perpetuate": "古い慣習を疑わずに従うと、それを次の世代にも<perpetuate>することになる。",
    "instigate": "改革を<instigate>したのは新しく着任した部長だ。",
    "catalyze": "海外進出の決断が、社内全体の意識改革を<catalyze>した。",
    "expedite": "通関手続きを<expedite>するため、書類を事前に整えておいた。",
    "alleviate": "夜間の道路混雑を<alleviate>する目的で、新しいバイパスが計画された。",
    "mitigate": "災害リスクを<mitigate>するための備蓄ルールが、各部署に通達された。",
    "subdue": "抗議の場では、まずは熱気を<subdue>することから始める必要があった。",
    "curtail": "予算超過の影響で、出張回数を半分に<curtail>することになった。",
    "attenuate": "厳しい指摘は、本人のやる気を<attenuate>しないよう柔らかく伝えたい。",
    "forestall": "問題が大きくなる前に、早めの対応で<forestall>できた。",
    "preclude": "規約の文言が、自由な発想での提案を<preclude>している面がある。",
    "impede": "古いシステムが、新しいワークフローの導入を<impede>している。",
    "obfuscate": "責任の所在を<obfuscate>するような報告書は、信頼を失う原因になる。",
    "hinder": "過剰なメール通知は、集中作業を<hinder>する大きな要因だ。",
    "mandate": "新しい労働法は、各社にハラスメント研修を<mandate>している。",
    "stipulate": "契約書には、納期と支払条件を必ず<stipulate>してください。",
    "ratify": "国会は来週、新しい条約を<ratify>する見通しだ。",
    "nullify": "署名漏れがあったため、その契約は法的に<nullify>される可能性がある。",
    "rescind": "発令済みの異動指示を、会社は週末に<rescind>した。",
    "repeal": "時代遅れの規制を<repeal>する動きが、各業界から強まっている。",
    "enact": "国会は今月末、新しいプライバシー法を<enact>する予定だ。",
    "promulgate": "改正された規則は、官報で<promulgate>された日から施行される。",
    "ordinance": "市が独自に<ordinance>を設け、路上喫煙を禁止した。",
    "statute": "労働者の権利は、複数の<statute>によって重層的に守られている。",
    "compliance": "業界全体で<compliance>を強めようと、定期的な研修が義務化された。",
    "prerogative": "最終決定権はCEOの<prerogative>として残されている。",
    "jurisdiction": "海外取引のトラブルは、どの国の<jurisdiction>に入るかで対応が変わる。",
    "constituency": "新人議員は、自分の<constituency>の意見を週末ごとに聞いて回った。",
    "franchise": "コンビニ事業は<franchise>方式で全国に広がっていった。",
    "conglomerate": "巨大<conglomerate>の中で、各事業部の独立性をどう守るかが課題だ。",
    "subsidiary": "海外法人は本社の<subsidiary>として、現地で意思決定する権限を持つ。",
    "affiliate": "今回のキャンペーンは、複数の<affiliate>と連動して進める予定だ。",
    "divestiture": "不採算部門の<divestiture>で、グループ全体の収益性が回復した。",
    "liquidation": "経営破綻した子会社は、来月から正式に<liquidation>手続きに入る。",
    "solvency": "決算書の<solvency>比率を、銀行は融資判断で重視する。",
    "insolvent": "資金繰りが行き詰まり、ついに<insolvent>と認定された。",
    "creditor": "和解協議には、主要な<creditor>全員が出席する必要がある。",
    "debtor": "<debtor>は、返済計画を書面で提出することが求められる。",
    "collateral": "融資を受けるには、不動産を<collateral>として差し入れる必要があった。",
    "amortize": "新しい設備は、5年で<amortize>する計画になっている。",
    "depreciate": "新車は、購入した瞬間から<depreciate>し始める。",
    "dividend": "今期の<dividend>は、業績好調を受けて1株あたり50円増額される。",
    "portfolio": "リスク分散のため、<portfolio>に複数地域の資産を組み入れた。",
    "leverage": "ブランド力を<leverage>することで、新事業への参入障壁を下げた。",
    "arbitrage": "為替相場のわずかな差を狙った<arbitrage>で、短時間で利益が出た。",
    "annuity": "退職後の収入源として、終身<annuity>を契約する人が増えている。",
    "escrow": "決済リスクを下げるため、代金は<escrow>口座で一時保管された。",
    "covenant": "ローン契約には、追加借入を制限する<covenant>が含まれている。",
    "indemnify": "事故が起きた場合、保険会社が被害者に<indemnify>する仕組みだ。",
    "liability": "新事業の損害賠償<liability>を、誰がどこまで負うか明確にしておきたい。",
    "fiduciary": "資産運用者は顧客に対して<fiduciary>な責任を負っている。",
    "derivative": "金融市場では、株価そのものより<derivative>取引のほうが大きく動く。",
    "commodity": "原油や小麦などの<commodity>価格は、地政学リスクに連動しやすい。",
    "backlog": "受注の<backlog>が積み上がっていて、新規案件を取れない状態だ。",
    "attrition": "意図的な解雇ではなく、自然な<attrition>で人員を縮小していく方針だ。",
    "monetary": "<monetary>政策の方向転換が、市場のあらゆる動きを左右している。",
    "stagnation": "賃金の長期<stagnation>が、若年層の消費低迷の原因とされる。",
    "deflation": "物価が下がり続ける<deflation>は、企業の投資意欲も冷やしてしまう。",
    "tariff": "新たな輸入<tariff>の導入で、国内農家には追い風が吹いた。",
    "subsidy": "再生可能エネルギー導入には、政府の<subsidy>が大きな後押しとなる。",
    "austerity": "<austerity>政策を貫いた結果、財政再建は進んだが格差は広がった。",
    "affluence": "戦後の高度成長で、社会全体に<affluence>が広がっていった時期がある。",
    "disparity": "都市と地方の医療<disparity>を解消するため、遠隔診療が広がりつつある。",
    "plummet": "悪い決算発表を受けて、翌日の株価は10%以上<plummet>した。",
    "plunge": "規制発表の直後、暗号資産の価格は一斉に<plunge>した。",
    "downturn": "景気<downturn>を見越して、企業は早めに在庫を圧縮し始めた。",
    "upturn": "受注量がじわじわ増え始め、ようやく<upturn>の兆しが見えてきた。",
    "rebound": "下げ続けた指数も、月末にようやく<rebound>に転じた。",
    "trough": "売上は3月で<trough>を打ち、その後はゆるやかに回復していった。",
    "apex": "彼女のキャリアの<apex>は、国際大会での金メダル獲得だった。",
    "empirical": "理論はあくまで仮説で、判断は<empirical>なデータで補強したい。",
    "anecdotal": "<anecdotal>な事例だけでは、政策の効果は判断できない。",
    "quantitative": "売上数や顧客数といった<quantitative>な指標で進捗を測る。",
    "qualitative": "数値だけでは見えない満足度は、<qualitative>な調査で補う。",
    "longitudinal": "同じ被験者を10年追跡する<longitudinal>調査が、新しい知見を生んだ。",
    "cohort": "1990年代生まれの<cohort>は、デジタル環境と共に育った最初の世代だ。",
    "aggregate": "店舗ごとの売上を<aggregate>すると、全体の傾向が見えてくる。",
    "benchmark": "同業他社の数字を<benchmark>として、自社の伸びしろを測った。",
    "threshold": "売上が一定の<threshold>を超えると、自動的に予算枠が拡大する。",
    "disparate": "<disparate>な部門を一つの会議に集めるのは、調整が大変だ。",
    "homogeneous": "サンプルが<homogeneous>だと、研究結果の一般化には注意が要る。",
    "heterogeneous": "<heterogeneous>なチームの方が、創造的な解決策が出やすいと言われる。",
    "variance": "実績と予算の<variance>を月次で確認し、ズレの原因を洗い出す。",
    "correlation": "睡眠時間と集中力には強い<correlation>があると報告されている。",
    "causation": "相関があるからといって、すぐ<causation>を断定するのは危険だ。",
    "extrapolate": "過去3年のデータから来年を<extrapolate>するのは、リスクの大きい予測だ。",
    "interpolate": "欠損データは、前後の値から<interpolate>して埋めることが多い。",
    "regression": "売上の変化を要因別に分けるため、重<regression>分析を行った。",
    "ascribe": "失敗の原因を、運の悪さだけに<ascribe>するのは早計だ。",
    "trajectory": "新人の入社後の<trajectory>を、3年単位で観察する仕組みを作った。",
    "hierarchy": "意思決定の<hierarchy>を簡素化したら、現場のスピードが上がった。",
    "topology": "ネットワークの<topology>を見直し、ボトルネックを解消した。",
    "framework": "プロジェクト管理の共通<framework>を導入して、部署間の連携を改善した。",
    "scaffold": "新人の学習を支える<scaffold>として、メンター制度を作った。",
    "infrastructure": "災害に強い<infrastructure>を整備することが、長期的な復興の鍵となる。",
    "juncture": "現在の<juncture>で焦って決めるより、半年待つ方が判断材料が増える。",
    "milestone": "プロジェクト開始3か月の<milestone>では、進捗を全社に共有する。",
    "epoch": "AIの本格普及は、職業観における新たな<epoch>を切り開いた。",
    "paradigm shift": "電子書籍の登場は、出版業界の<paradigm shift>を象徴する出来事だった。",
    "contend": "彼は、改革の遅さこそ最大の問題だと会議で<contend>した。",
    "posit": "本論文は、需要が価格を決めるのではなく価格が需要を作ると<posit>する。",
    "relinquish": "経営陣は、過半数株の保有を<relinquish>することで合意した。",
    "acquiesce": "本心では反対だったが、彼は会議の流れに<acquiesce>した。",
    "dissent": "計画には強い<dissent>があり、決議は来週に持ち越された。",
    "unanimous": "理事会は、新議長の選出について<unanimous>な賛成で決議した。",
    "polarized": "<polarized>した世論の中で、中間派の声は届きにくくなった。",
    "contentious": "賃上げの規模は、今期もっとも<contentious>な論点になっている。",
    "vehement": "新ルールへの<vehement>な抗議が、SNS上で広がっている。",
    "staunch": "彼女は環境保全運動の<staunch>な支持者として知られる。",
    "equivocate": "責任の所在を問われた幹部は、<equivocate>するばかりだった。",
    "prevaricate": "事実を聞かれた時に<prevaricate>すると、後で信頼を失う。",
    "reconcile": "理想と現実を<reconcile>するのが、政策担当者の役割だ。",
    "reciprocate": "受けた厚意を別の場面で<reciprocate>することは、長く続く関係の基本だ。",
    "normative": "『こうあるべきだ』と語る<normative>な議論と、実態の記述は区別したい。",
    "utilitarian": "最大多数の幸福を基準にする考え方は、典型的な<utilitarian>立場だ。",
    "deontological": "結果ではなく行為の善悪を見るのが、<deontological>な倫理学だ。",
    "axiomatic": "顧客の安全が最優先という点は、私たちにとって<axiomatic>な前提だ。",
    "teleological": "歴史を目的の実現過程として捉えるのは、<teleological>な見方だ。",
    "autonomy": "現場の<autonomy>を尊重することで、判断スピードが上がった。",
    "sovereignty": "デジタルデータの<sovereignty>を巡り、各国の規制が分岐し始めている。",
    "paternalism": "従業員を子ども扱いするような<paternalism>は、いまや組織運営にそぐわない。",
    "populism": "短期的な人気を狙う<populism>は、長期政策を遠ざける危険がある。",
    "ubiquitous": "スマホは今や<ubiquitous>で、電車の中でも誰もが操作している。",
    "pervasive": "監視カメラは、街のあらゆる場所に<pervasive>に設置されている。",
    "prevalent": "夏になると、子どもたちの間で手足口病が<prevalent>になる。",
    "rampant": "オンライン詐欺が<rampant>で、警察も注意喚起を強めている。",
    "scant": "新興市場についての<scant>な情報を元に、慎重な判断を迫られた。",
    "paltry": "今回の昇給は、物価上昇に比べれば<paltry>な額にすぎない。",
    "copious": "彼の発表は<copious>な資料に支えられ、説得力があった。",
    "voluminous": "裁判で提出された<voluminous>な証拠を、弁護団は数週間かけて精査した。",
    "preeminent": "彼は分子生物学の世界で<preeminent>な研究者として知られている。",
    "vestigial": "現代社会には、戦後の制度がまだ<vestigial>な形で残っている。",
}


def main() -> None:
    d = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    quizzes = d["quizzes"]

    # まずカバー漏れチェック
    json_words = {q["word"]: q for q in quizzes}
    missing = [w for w in json_words if w not in BODIES]
    extra = [w for w in BODIES if w not in json_words]
    if missing:
        print(f"[警告] BODIES に存在しない単語 ({len(missing)}): {missing[:10]}")
    if extra:
        print(f"[警告] JSON に存在しない単語が BODIES にある ({len(extra)}): {extra[:10]}")

    rewritten = 0
    for q in quizzes:
        w = q["word"]
        if w in BODIES:
            body = BODIES[w]
            q["body"] = body
            q["body_ruby"] = body  # ルビは後段で再生成可能だが、現状は同一文を使う
            # explanation_ruby はバグ修正: 旧版では body をコピーしていた
            q["explanation_ruby"] = q.get("explanation", "")
            rewritten += 1

    d["quizzes"] = quizzes
    JSON_PATH.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n書き換え完了: {rewritten} / {len(quizzes)} 語")


if __name__ == "__main__":
    main()
