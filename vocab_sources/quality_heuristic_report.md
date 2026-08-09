# WordTacos ヒューリスティック品質検出 (2026-06-15)

## サマリ

- **stage5 対象**: 2720問
- **stage6 対象**: 2394問
- **総検出件数**: 101件

## type別件数

| type | 件数 |
|---|---|
| choices_len_unbalanced | 58 |
| correct_contains_choice | 22 |
| choice_contains_correct | 21 |

## choices_len_unbalanced (58件、上位20件)

| id | stage | word | detail |
|---|---|---|---|
| s5_014 | stage5 | boyfriend | 長さ [1, 5, 2, 2] |
| s5_020 | stage5 | butterfly | 長さ [1, 2, 3, 6] |
| s5_065 | stage5 | girlfriend | 長さ [1, 6, 1, 8] |
| s5_217 | stage5 | barbecue | 長さ [3, 2, 6, 9] |
| s5_291 | stage5 | comb | 長さ [5, 2, 1, 4] |
| s5_362 | stage5 | drug | 長さ [4, 5, 1, 3] |
| s5_453 | stage5 | granny | 長さ [6, 6, 4, 1] |
| s5_537 | stage5 | mall | 長さ [2, 7, 9, 4] |
| s5_538 | stage5 | manager | 長さ [5, 8, 1, 2] |
| s5_539 | stage5 | mark | 長さ [2, 5, 1, 2] |
| s5_545 | stage5 | melon | 長さ [3, 6, 3, 1] |
| s5_561 | stage5 | musical | 長さ [3, 10, 2, 6] |
| s5_587 | stage5 | pan | 長さ [1, 3, 3, 5] |
| s5_659 | stage5 | recipe | 長さ [3, 1, 5, 4] |
| s5_693 | stage5 | rifle | 長さ [1, 5, 1, 1] |
| s5_731 | stage5 | sausage | 長さ [4, 3, 1, 5] |
| s5_744 | stage5 | secret | 長さ [7, 2, 1, 2] |
| s5_910 | stage5 | accessory | 長さ [3, 6, 3, 1] |
| s5_956 | stage5 | alcohol | 長さ [5, 1, 2, 3] |
| s5_997 | stage5 | approach | 長さ [2, 5, 1, 2] |

...残り 38 件 ({quality_heuristic_issues.json} 参照)

## correct_contains_choice (22件、上位20件)

| id | stage | word | detail |
|---|---|---|---|
| s5_350 | stage5 | dishonest | correct='不正直な' contains choices[0]='正直な' |
| s5_858 | stage5 | unnecessary | correct='不必要な' contains choices[0]='必要な' |
| s5_1385 | stage5 | dioxide | correct='二酸化物' contains choices[0]='酸化物' |
| s5_1435 | stage5 | duvet | correct='羽毛布団' contains choices[0]='毛布' |
| s5_1748 | stage5 | improper | correct='不適切な' contains choices[1]='適切な' |
| s5_2020 | stage5 | notorious | correct='悪名高い' contains choices[0]='名高い' |
| s5_2189 | stage5 | pronoun | correct='代名詞' contains choices[1]='名詞' |
| s5_2607 | stage5 | uncertainty | correct='不確実性' contains choices[1]='確実性' |
| s5_2608 | stage5 | unclear | correct='不明瞭な' contains choices[1]='明瞭な' |
| s5_2620 | stage5 | unfairly | correct='不公平に' contains choices[1]='公平に' |
| s6_0135 | stage6 | atypical | correct='非典型的な' contains choices[1]='典型的な' |
| s6_0322 | stage6 | clumsy | correct='不器用な' contains choices[0]='器用な' |
| s6_1026 | stage6 | impractical | correct='非実用的な' contains choices[0]='実用的な' |
| s6_1033 | stage6 | improperly | correct='不適切に' contains choices[0]='適切に' |
| s6_1037 | stage6 | inaccurate | correct='不正確な' contains choices[1]='正確な' |
| s6_1038 | stage6 | inadequate | correct='不十分な' contains choices[0]='十分な' |
| s6_1096 | stage6 | insufficient | correct='不十分な' contains choices[0]='十分な' |
| s6_1359 | stage6 | needless | correct='不必要な' contains choices[3]='必要な' |
| s6_1873 | stage6 | semi-final | correct='準決勝' contains choices[0]='決勝' |
| s6_2216 | stage6 | unclearly | correct='不明瞭に' contains choices[0]='明瞭に' |

...残り 2 件 ({quality_heuristic_issues.json} 参照)

## choice_contains_correct (21件、上位20件)

| id | stage | word | detail |
|---|---|---|---|
| s5_190 | stage5 | appropriate | choices[0]='不適切な' contains correct '適切な' |
| s5_442 | stage5 | gram | choices[0]='キログラム' contains correct 'グラム' |
| s5_522 | stage5 | liter | choices[3]='ミリリットル' contains correct 'リットル' |
| s5_638 | stage5 | proper | choices[1]='不適切な' contains correct '適切な' |
| s5_736 | stage5 | scientific | choices[1]='非科学的な' contains correct '科学的な' |
| s5_957 | stage5 | alcoholic | choices[0]='ノンアルコールの' contains correct 'アルコールの' |
| s5_978 | stage5 | annual | choices[2]='10年に一度の' contains correct '年に一度の' |
| s5_1440 | stage5 | earnest | choices[2]='不真面目な' contains correct '真面目な' |
| s5_1510 | stage5 | evenly | choices[0]='不均等に' contains correct '均等に' |
| s5_2043 | stage5 | officially | choices[1]='非公式に' contains correct '公式に' |
| s5_2166 | stage5 | president | choices[0]='副大統領' contains correct '大統領' |
| s5_2191 | stage5 | properly | choices[0]='不適切に' contains correct '適切に' |
| s5_2241 | stage5 | realistic | choices[2]='非現実的な' contains correct '現実的な' |
| s5_2371 | stage5 | sheriff | choices[2]='保安官代理事務員' contains correct '保安官' |
| s6_0096 | stage6 | appropriately | choices[0]='不適切に' contains correct '適切に' |
| s6_0337 | stage6 | colon | choices[3]='セミコロン' contains correct 'コロン' |
| s6_0416 | stage6 | cooperative | choices[1]='非協力的な' contains correct '協力的な' |
| s6_1055 | stage6 | industrialise | choices[0]='脱工業化する' contains correct '工業化する' |
| s6_2052 | stage6 | sufficiently | choices[1]='不十分に' contains correct '十分に' |
| s6_2053 | stage6 | suitably | choices[1]='不適切に' contains correct '適切に' |

...残り 1 件 ({quality_heuristic_issues.json} 参照)
