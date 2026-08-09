"""chunk_8 ふりがな品質スキャナ。
パターンマッチで疑わしい誤読を抽出し、各項目を確認用に出力する。
判定は後段でマニュアルレビューする想定。
"""
from __future__ import annotations

import json
import re
from pathlib import Path

INPUT = Path(__file__).parent / 'chunk_8.json'

with open(INPUT, encoding='utf-8') as f:
    data = json.load(f)

# 全パターン正規表現
PATTERNS: list[tuple[str, re.Pattern[str], str]] = [
    # A: 動詞訓読み誤読
    ('verb_furi', re.compile(r'降《ふ》'), '降《ふ》り (雨が降る文脈なら ふ で正しい / 山を降りる文脈なら お)'),
    ('verb_ori', re.compile(r'降《お》り'), '降《お》り (雨が降る/エンジンがかかる は ふ)'),
    ('verb_jou', re.compile(r'乗《じょう》'), '乗《じょう》った (動詞は の)'),
    ('verb_majiwasu', re.compile(r'交《まじ》わ'), '交《まじ》わす (挨拶などは か)'),
    ('verb_kudaru', re.compile(r'下《くだ》ろ|下《くだ》し'), '下《くだ》ろした (荷物を下ろす は お)'),
    ('verb_hou_a', re.compile(r'放《ほう》っ'), '放《ほう》った (動詞は はな)'),
    ('verb_keiyaka', re.compile(r'軽《けい》やか'), '軽《けい》やか (やかは かろやか)'),
    ('verb_naberu', re.compile(r'並《な》べ'), '並《な》べ (ならべ)'),
    ('verb_shinwa', re.compile(r'震《しん》わ'), '震《しん》わせ (ふるわせ)'),
    ('verb_michikiru', re.compile(r'断《だん》ち'), '断《だん》ち (たち)'),

    # B: 熟語分割誤読  「○《音》○《訓》」のような怪しい組合せを広く拾う
    ('cpd_sora_minato', re.compile(r'空《そら》港《みなと》'), '空港=くうこう'),
    ('cpd_sora_kan', re.compile(r'空《そら》間《かん》'), '空間=くうかん'),
    ('cpd_sora_naka', re.compile(r'空《そら》中《なか》'), '空中=くうちゅう'),
    ('cpd_sora_iki', re.compile(r'空《そら》域《いき》'), '空域=くういき'),
    ('cpd_kou_sora', re.compile(r'航《こう》空《そら》'), '航空=こうくう'),
    ('cpd_yoru_sora', re.compile(r'夜《よる》空《そら》'), '夜空=よぞら'),
    ('cpd_aoi_sora', re.compile(r'青《あお》空《そら》'), '青空=あおぞら'),
    ('cpd_hana_bin', re.compile(r'花《はな》瓶《びん》'), '花瓶=かびん'),
    ('cpd_tsushin_mono', re.compile(r'通勤《つうきん》者《もの》'), '通勤者=つうきんしゃ'),
    ('cpd_zenkin', re.compile(r'勤《きん》者《もの》'), '○勤者=○きんしゃ'),
    ('cpd_irai_mono', re.compile(r'依頼《いらい》者《もの》'), '依頼者=いらいしゃ'),
    ('cpd_riyou_mono', re.compile(r'利用《りよう》者《もの》'), '利用者=りようしゃ'),
    ('cpd_kanja_mono', re.compile(r'患者《かんじゃ》ごと'), '(普通)患者ごと=かんじゃごと (OK)'),
    ('cpd_keiyaka', re.compile(r'軽《けい》快'), '軽快=けいかい (OK)'),
    ('cpd_hi_no_de', re.compile(r'日の出《ひので》来'), '日の出来事=ひのできごと'),
    ('cpd_e_iri', re.compile(r'絵《え》入《はい》り'), '絵入り=えいり (はいりは誤)'),

    # C: 助数詞 vs 訓読み
    ('cnt_karadaru', re.compile(r'体《からだ》(?![一-龯])'), '15体《からだ》→たい'),
    ('cnt_kaiten_split', re.compile(r'回《かい》転《こか》'), '1回転=いっかいてん'),
    ('cnt_ni_karada', re.compile(r'[一二三四五六七八九十0-9０-９]\s*体《からだ》'), '数+体は たい'),

    # D: 「後」誤読 (~後で 震災後 など は ご)
    ('go_nochi_disaster', re.compile(r'震災《しんさい》後《のち》'), '震災後=しんさいご'),
    ('go_nochi_jikan', re.compile(r'時間《じかん》後《のち》'), 'N時間後=Nじかんご'),
    ('go_nochi_general', re.compile(r'後《のち》(に|の|は|も|で|、)'), '後《のち》(さまざま)→ご? 要確認'),
    ('go_nochi_year', re.compile(r'年《ねん》後《のち》'), 'N年後=Nねんご'),
    ('go_nochi_half', re.compile(r'半年後《はんとしご》'), '(参考) 半年後=はんとしご OK'),

    # E: 「者」誤読
    ('mono_kankan', re.compile(r'(館|院|校|社|店|寺|所|室)者《もの》'), 'XX者=しゃ'),
    ('mono_raikan', re.compile(r'来館《らいかん》者《もの》'), '来館者=らいかんしゃ'),
    ('mono_kanren_he', re.compile(r'者《もの》(の|たちは|たちが|は)'), '者《もの》→しゃ?'),
    ('mono_kankan_he', re.compile(r'関係《かんけい》者《もの》'), '関係者=かんけいしゃ'),
    ('mono_kanren_he2', re.compile(r'担当《たんとう》者《もの》'), '担当者=たんとうしゃ'),
    ('mono_kourei_he', re.compile(r'高齢《こうれい》者《もの》'), '高齢者=こうれいしゃ'),
    ('mono_otozure_mono', re.compile(r'訪《おとず》れる者《もの》'), '訪れる者=ひと/しゃ?要確認'),

    # F: 「人」誤読
    ('nin_general', re.compile(r'(の|た|る|む|つ|い)人《にん》'), '名詞句の人=ひと'),

    # G: 「日」誤読
    ('nichi_ichinichi', re.compile(r'一日《ついたち》'), '一日=いちにち (時間量)'),
    ('nichi_taiin_bi', re.compile(r'退院《たいいん》日《び》'), '退院日=たいいんび'),
    ('nichi_x_ka_go', re.compile(r'日後《にちご》'), 'N日後=Nにちご (3日後はみっかご)'),
    ('nichi_mikkago', re.compile(r'3日後《にちご》'), '3日後=みっかご'),
    ('nichi_konichi', re.compile(r'本日《ほんにち》'), '本日=ほんじつ'),

    # H: 「方」誤読
    ('hou_hataraki', re.compile(r'働《はたら》き方《ほう》'), '働き方=はたらきかた'),
    ('hou_eraburi', re.compile(r'選び方《えらびほう》'), '選び方=えらびかた'),
    ('hou_kata_general', re.compile(r'(し|い|り|き|み)方《ほう》(?!向|位|針|策|程|程式|法|案|程式|程|程度|程式)'), '~方《ほう》→かた?'),

    # I: 「際」誤読
    ('sai_kiwa', re.compile(r'際《きわ》'), '~する際=さい (窓際=まどぎわは正)'),

    # J: 連濁
    ('rendaku_aozora', re.compile(r'青《あお》空《そら》'), '青空=あおぞら'),
    ('rendaku_takibi', re.compile(r'焚《た》き火《ひ》'), '焚き火=たきび'),
    ('rendaku_yozora', re.compile(r'夜《よる》空《そら》'), '夜空=よぞら'),

    # K: その他特殊
    ('mae_no_mae', re.compile(r'年《ねん》前《まえ》'), 'N年前=Nねんまえ (普通) OK'),
    ('rai_ko', re.compile(r'来《らい》事《こと》'), '来事=こと (出来事分割)'),
    ('honyaku', re.compile(r'本《ほん》人《にん》'), '本人=ほんにん (OK 通常)'),
    ('ge_kudasu', re.compile(r'下《くだ》ろ'), '下ろす=おろす'),
    ('ge_kuda', re.compile(r'下《さ》(?:が|げ)'), '下=さ がる/ げる (普通OK)'),
    ('uri_minato', re.compile(r'地元《じもと》産《う》'), '地元産=じもとさん'),
    ('strand_un', re.compile(r'産《う》'), '産《う》 (~産=~さん が普通)'),

    # 4時間後 4時間 にち
    ('jikan_nichi', re.compile(r'時間《じかん》後《のち》'), 'X時間後=ご'),
    ('hannen', re.compile(r'半年後《はんとしご》'), '半年後=はんとしご'),

    # 3章分=さんしょうぶん (分はぶん)
    ('shoubun', re.compile(r'章《しょう》分《ふん》'), '章分=しょうぶん? ぶん'),

    # 何十年もかかる
    ('nan_juu', re.compile(r'何十年《なんじゅうねん》'), '何十年=なんじゅうねん (OK)'),

    # 古都の駅前 + 4時間後 (4時間のち)
    ('jikanno', re.compile(r'時間《じかん》'), '時間=じかん (OK)'),

    # 人ひとり、何十、五十 などはOK

    # 一日一杯
    ('ippai_nochi', re.compile(r'一杯《いっぱい》'), '一杯=いっぱい (OK)'),

    # 朝の一杯 午後の一杯  もOK
    # 「半年後《はんとしご》」OK

    # 上《うえ》/上《うわ》
    ('uwagi_uwagi', re.compile(r'上着《うわぎ》'), '上着=うわぎ (OK)'),
    ('uebu_above', re.compile(r'表示法《ひょうじほう》上《うえ》'), '表示法上=ひょうじほうじょう'),
    ('jou_general', re.compile(r'上《うえ》(?:の|に|で)'), '~の上 (位置) は普通OKだが、抽象は じょう'),

    # 3章分=ぶん
    # 校長 (こうちょう) 通常OK

    # 「種馬」「母馬」訓読みは普通OK (たねうま/ははうま)

    # 「同様」=どうよう
    # 「お《え》得」 → お得は おとく
    ('otoku_oe', re.compile(r'お得《え》'), 'お得=おとく'),

    # 「3冊《さつ》」 OK
    # 「弁当《べんとう》」 OK

    # 「人々」=ひとびと OK

    # 「3章分」分=ふん か ぶん
    # 「30分続けたら」 30分=さんじっぷん OK

    # 「家族会議《かぞくかいぎ》」 OK
    # 「30分」=さんじっぷん OK

    # 「来年度=らいねんど」 OK

    # 種馬《たねうま》は普通OK
    # 「種《たね》馬《うま》」「母《はは》馬《うま》」 確認
    ('compound_taneuma', re.compile(r'種馬《たねうま》'), '種馬=たねうま OK'),

    # 「皮目《かわめ》」=かわめ OK
    # 「3冊《さつ》」 OK

    # 「集落=しゅうらく」 OK
    # 「移住=いじゅう」 OK

    # 「上着《うわぎ》」 OK
    # 「足袋」 等
    # 「保存食《ほぞんしょく》」 OK

    # 「強豪校《きょうごうこう》」 強豪校 確認 強豪/校
    ('compound_kyou', re.compile(r'強豪《きょうごう》校《こう》'), '強豪校=きょうごうこう (正しい)'),

    # 「波打ち際《なみうちぎわ》」 OK
    # 「玄関=げんかん」 OK
    # 「鍵=かぎ」 OK
    # 「一本=いっぽん」 OK
]

# 各項目をスキャン
hits: list[dict] = []
for it in data:
    body_ruby = it['body_ruby']
    body_kana = it['body_kana']
    word = it['word']
    iid = it['id']

    for tag, pat, comment in PATTERNS:
        for m in pat.finditer(body_ruby):
            start = max(0, m.start() - 20)
            end = min(len(body_ruby), m.end() + 20)
            context = body_ruby[start:end]
            hits.append({
                'id': iid,
                'word': word,
                'tag': tag,
                'match': m.group(0),
                'context': context,
                'comment': comment,
                'body_ruby': body_ruby,
                'body_kana': body_kana,
            })

print(f'Total items: {len(data)}')
print(f'Total hits: {len(hits)}')

# タグ別カウント
from collections import Counter
tag_count: Counter[str] = Counter(h['tag'] for h in hits)
for tag, c in tag_count.most_common():
    print(f'  {tag}: {c}')

# JSONダンプ
OUT = Path(__file__).parent / '_chunk_8_hits.json'
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(hits, f, ensure_ascii=False, indent=2)
print(f'Wrote: {OUT}')
