"""toeic_high (116語) と toeic_mid (2語) のテンプレ例文を、
TOEIC B2.1〜B2.2 レベルのビジネス文脈に基づいた独自例文に置き換える。

すべて編者 (Teacher Tacos English) のオリジナル。
"""
from __future__ import annotations

import json
from pathlib import Path

VOCAB_DIR = Path(__file__).resolve().parent / "vocab_sources"

# 共通の置換 dict (toeic_high 用 + toeic_mid 用)
BODIES: dict[str, str] = {
    # toeic_high - 接続詞・副詞
    "however": "部長は懸念を示した。<however>、最終的にプロジェクト続行を承認した。",
    "though": "値段は高い<though>、品質を考えれば妥当だと取引先は説明した。",
    "probably": "在庫切れの製品は来週<probably>入荷するという連絡を仕入先から受けた。",
    "although": "<although>営業利益は伸びたが、為替の影響で純利益は前年並みにとどまった。",
    "least": "出席者の反応を見るかぎり、新方針への反対意見は<least>30%はいると見込まれる。",
    "throughout": "新しい人事制度は会社<throughout>すべての部署で同時に運用が始まった。",
    "unless": "<unless>追加の指示がなければ、明日中に最終版を提出します。",
    "perhaps": "工期の遅れの原因は、<perhaps>部材の調達遅延が大きい。",
    "whether": "出席するか<whether>か、月曜の朝までに事務局へ返答してください。",
    "accounting": "月末の<accounting>処理が立て込んでおり、経理部は深夜まで残業が続いている。",
    "billboard": "駅前の大型<billboard>は、新製品の発売告知に2週間借り切る計画になった。",
    "banknotes": "海外出張前に、現地通貨の<banknotes>を空港の両替所で受け取った。",
    "toward": "新CEOは、組織の柔軟化<toward>と全社員に向けてビジョンを共有した。",
    "upcoming": "<upcoming>の四半期決算に向けて、各事業部から数字の集計が急ピッチで進んでいる。",
    "along": "川<along>に並ぶカフェの中から、商談に使えそうな静かな店を一軒選んだ。",
    "except": "全員参加の研修だが、当日出張の数名<except>、ほぼ全員が会場に集まった。",
    "discovered": "監査の過程で、過去5年分の請求書に小さな誤記が複数<discovered>された。",
    "beyond": "売上目標は予算<beyond>に達成され、ボーナス支給の根拠資料が更新された。",
    "pier": "漁港の<pier>で水揚げを待つ間、私はノートに帰社後の連絡事項を書き留めた。",
    "via": "海外支社からの連絡は、社内ポータル<via>で本社の全担当者に一斉に届く仕組みだ。",
    "odor": "倉庫の隅から強い<odor>が漂ってきたので、すぐに換気と原因調査を始めた。",
    "enclosed": "契約書の控えと請求書の写しを<enclosed>した封筒を、書留で本社に送った。",
    "confidential": "取締役会の議事録は<confidential>扱いで、社外への持ち出しは厳しく禁止されている。",
    "inventory": "月次の<inventory>棚卸しでは、システム上の在庫と実数が必ず一致するかを確認する。",
    "otherwise": "期日までに書類を提出してください。<otherwise>、申請は無効になる恐れがあります。",
    "secretarｙ": "役員会の議事録は、<secretarｙ>が事前に整理してから配布される。",
    "quarterly": "<quarterly>レポートの締切が近く、データ分析チームは週末出勤を予定している。",
    "efficiently": "業務をより<efficiently>に進めるため、繰り返し作業は社内ツールで自動化した。",
    "technician": "サーバー障害の通知を受け、社内の<technician>がすぐに復旧作業に取り掛かった。",
    "attendant": "国際会議の受付には英語が話せる<attendant>が配置され、参加者の案内を担当した。",
    "subscription": "業界誌の年間<subscription>を更新するため、申込書を郵送で送った。",
    "automated": "倉庫の入出庫管理は<automated>システムに切り替わり、人為的ミスが激減した。",
    "congress": "三日間の医療<congress>で、世界中の研究者が最新の治験結果を共有した。",
    "renovation": "本社ビルの大規模<renovation>工事のため、社員は半年ほど別ビルで業務を続ける。",
    "moreover": "新製品は機能性に優れ、<moreover>、競合より3割安い価格設定で市場に投入された。",
    "optimum": "在庫水準を<optimum>に保つには、需要予測の精度がカギになる。",
    "expire": "パスポートの有効期限が来月で<expire>するため、海外出張の前に更新の手続きを進めた。",
    "commercially": "試作品は技術的には成功したが、<commercially>に成立させるには量産コストの削減が課題だ。",
    "comply": "新しい個人情報保護法に<comply>するため、社内の運用マニュアルを全面改定した。",
    "specification": "機材の<specification>を細部まで確認した上で、調達リストを購買部に提出した。",
    "vice president": "海外事業の責任者として、新たに<vice president>が一人増員されることが正式発表された。",
    "authorized": "上司から<authorized>された支出のみ、経費精算で全額が承認される。",
    "funding": "新規プロジェクトの<funding>を確保するため、複数の投資家への提案資料を準備した。",
    "installation": "新型機械の<installation>には専門業者が立ち会い、工場のラインに合わせて調整が行われた。",
    "archive": "過去10年の社内文書は地下の<archive>に保管され、必要に応じて閲覧申請ができる。",
    "secretarial": "役員フロアの<secretarial>業務は、スケジュール管理から来客対応まで幅広い。",
    "equipped": "新しい会議室は最新の音響設備に<equipped>され、海外との同時通話も問題なくこなせる。",
    "equivalent": "海外赴任手当は、現地給与に日本の家賃補助の<equivalent>を加えた金額で計算されている。",
    "defect": "出荷前の検品で複数の<defect>が見つかったため、その日の出荷は一旦保留になった。",
    "everywhere": "新サービスの広告が<everywhere>に出て、街中のサイネージや SNS でも見かけるようになった。",
    "chairperson": "取締役会の<chairperson>は、議論を時間内に収めるため発言時間を厳格に管理する。",
    "dedicated": "顧客対応に<dedicated>な社員が増員され、応答時間が大幅に短縮された。",
    "imperial": "訪日した英国王室の<imperial>ファミリーの動静は、世界中のメディアが追った。",
    "productivity": "フレックス制度の導入後、社員の<productivity>は前年同期比で18%向上した。",
    "recommended": "上司から<recommended>された業界紙を、毎週金曜の朝に部内全員で回し読みしている。",
    "performed": "第三者機関による品質試験が<performed>され、最終的な合格証が発行された。",
    "itinerary": "海外出張の<itinerary>には、移動手段と会議時刻を分単位で書き込んでおく。",
    "warehouse": "物流の<warehouse>を関東から関西へ移転することで、配送リードタイムを半日短縮できた。",
    "surplus": "生産計画の見直しで、年末に積み上がった<surplus>を最小限に抑えることに成功した。",
    "appliance": "オフィスの省エネ対応で、給湯室の古い<appliance>を最新の省電力モデルに更新した。",
    "thousands": "新サービスの開始初日、登録者数は<thousands>単位で増えたとマーケティング部から報告があった。",
    "capstone": "長年の研究開発の<capstone>として、ついに自社初の特許製品が市場に出た。",
    "extracted": "大量の顧客データから、購買傾向を示す主要な指標が<extracted>された。",
    "firsthand": "海外子会社の現場を<firsthand>で見てこそ、本社からの指示が現実離れしていないか判断できる。",
    "gained": "新サービスは半年で5万人の利用者を<gained>し、当初予算の倍に達した。",
    "encouraged": "上司から<encouraged>された若手は、社内提案制度に初めて自分の企画を提出した。",
    "foster": "部門間の風通しを<foster>するため、毎月クロスファンクショナルな勉強会を開いている。",
    "clientele": "老舗料理店の<clientele>には政財界の重鎮が多く、予約は数ヶ月先まで埋まっている。",
    "cargo": "大型コンテナ船の<cargo>を税関で検査するには、書類と現物の照合を一つひとつ行う。",
    "CEO": "新<CEO>は就任直後の全社員ミーティングで、5年計画の骨子を熱意を持って語った。",
    "directions": "取扱説明書の<directions>に従って組み立てれば、家具は1時間ほどで完成する。",
    "foam": "コーヒーマシンの<foam>機能が壊れたため、修理業者を呼ぶ手配を朝一番でした。",
    "patent": "新製造法に関する<patent>を申請するため、社内の知財部が技術資料の確認に追われている。",
    "inadvertently": "部内メールの『全員に返信』で<inadvertently>機密情報が外部に送られかけ、寸前で止まった。",
    "malfunctioning": "工場のセンサーが<malfunctioning>して、稼働ラインが一時的に停止する事態になった。",
    "invoice": "月末締めの<invoice>を経理部に提出する前に、必ず担当者の押印が必要だ。",
    "gladiator": "古代ローマの<gladiator>の歴史をテーマにした特別展が、来月から博物館で始まる。",
    "landfill": "製品パッケージの見直しは、最終的に<landfill>へ廃棄される量の削減にもつながった。",
    "inconvenience": "システムメンテナンスのお時間にご<inconvenience>をおかけしましたことをお詫び申し上げます。",
    "granger": "19世紀後半の米国西部で、<granger>たちは小麦の長距離輸送費に苦しんでいた。",
    "plaque": "創立50周年記念の<plaque>がエントランスに掲げられ、来訪者の目を引くようになった。",
    "namely": "当社の主力商品は2つ、<namely>家庭用洗剤と業務用洗剤だ。",
    "subscribe": "業界の動向を追うため、専門誌を3誌<subscribe>している。",
    "till": "受付は午後5時<till>営業しているので、書類は今日中に持参してほしい。",
    "replicate": "海外で成功したマーケティング手法を国内市場で<replicate>するのは、簡単ではない。",
    "thereby": "工程を見直して無駄な動きをなくし、<thereby>製造時間を15%短縮することができた。",
    "reimbursement": "出張に伴う交通費の<reimbursement>は、申請後10営業日以内に振り込まれる。",
    "architectural": "老舗ホテルの<architectural>な美しさは、海外からの観光客を強く惹きつけている。",
    "underlying": "業績不振の<underlying>な原因を探るため、外部コンサルタントに調査を依頼した。",
    "trustee": "信託契約に基づき、<trustee>が遺族の代わりに資産の管理運用を行う。",
    "arid": "<arid>な地域での農業支援は、灌漑技術と耐乾性作物の両面から進める必要がある。",
    "authorization": "機密情報へのアクセスには、上長の事前<authorization>が必須だ。",
    "aptitude": "採用試験では、応募者の英語力に加えて論理的思考の<aptitude>も測定される。",
    "complimentary": "ホテルの会員には、朝食の<complimentary>サービスが付くプランがある。",
    "grocery": "出張先のホテルから近い<grocery>店で、夕食用の総菜と水を買い込んだ。",
    "accommodate": "新しいオフィスは最大200人の社員を<accommodate>できる広さで設計された。",
    "vendor": "部品供給<vendor>との価格交渉が長引き、契約締結は来週に持ち越された。",
    "therefore": "想定より受注が伸びている。<therefore>、生産ラインを夜間も稼働させる方針だ。",
    "either": "提案された二案のうち、<either>を選ぶかは来週の会議で最終決定する。",
    "verify": "取引先からの請求金額が見積もりと一致するか、経理担当が一件ずつ<verify>する。",
    "eatery": "駅前に新しくオープンした<eatery>は、ランチタイムには行列ができるほどの人気だ。",
    "directory": "社内の電話<directory>はイントラに掲載され、検索すれば内線番号がすぐ分かる。",
    "whenever": "新システムに不具合が出たら、<whenever>でも構わないので IT 部に連絡してください。",
    "cuisine": "取引先との会食では、和食の<cuisine>店を選ぶことが多いのが我が社の慣例だ。",
    "autograph": "引退するスター選手の<autograph>付きユニフォームが、社内チャリティオークションに出品された。",
    "auditorium": "全社集会のため、本社の<auditorium>には500脚の椅子が朝から並べられた。",
    "recipient": "表彰式の<recipient>は、長年の品質改善活動で顕著な貢献をした製造部の係長だ。",
    "durable": "業務用の<durable>な家具を新オフィスに導入し、長期的な経費削減を狙った。",
    "municipal": "<municipal>な助成金を活用して、地元商店街は街灯を全面 LED に切り替えた。",
    "premise": "我が社の<premise>は「顧客の信頼を裏切らない」という一言に集約される。",
    "enlarge": "写真を<enlarge>する作業を頼まれたので、解像度の高いオリジナルを探してきた。",
    "fluctuate": "為替レートが日替わりで<fluctuate>するため、海外取引のリスクヘッジは欠かせない。",
    "consecutive": "売上は3<consecutive>四半期で前年同期を上回り、決算発表は好調と評された。",
    "urgency": "顧客クレームの対応は<urgency>が高いため、担当者は他業務を一旦止めて取り掛かる。",
    "proficiency": "海外駐在を希望する社員には、業務遂行に必要な英語<proficiency>のレベルが課されている。",
    "discontinue": "売上不振の旧モデルは、来年度から段階的に<discontinue>することが決定された。",
    # toeic_mid
    "quite": "新人研修の評価は<quite>好評で、来年は受講人数の枠を増やす方針が示された。",
    "found": "創業者は1962年に、5名の同志と共にこの会社を<found>した。",
}


def main() -> None:
    for stage_json in ["stage_toeic_high_quizzes_clean.json", "stage_toeic_mid_quizzes_clean.json"]:
        path = VOCAB_DIR / stage_json
        d = json.loads(path.read_text(encoding="utf-8"))
        rewritten = 0
        unmatched = []
        for q in d["quizzes"]:
            body = q.get("body", "")
            if "会議の資料に" in body or "という単語が出てきたら" in body:
                w = q["word"]
                if w in BODIES:
                    q["body"] = BODIES[w]
                    q["body_ruby"] = BODIES[w]  # ルビは Phase 3 で再生成
                    # explanation_ruby のバグ修正
                    q["explanation_ruby"] = q.get("explanation", "")
                    rewritten += 1
                else:
                    unmatched.append(w)
        path.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{stage_json}: {rewritten} 件書き換え, 未マッチ {len(unmatched)} 件")
        if unmatched:
            print(f"  未マッチ単語: {unmatched}")


if __name__ == "__main__":
    main()
