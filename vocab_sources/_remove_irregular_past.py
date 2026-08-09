"""不規則変化動詞の過去形・過去分詞を全ステージから除去し、order を詰めて count を更新する。

実行: python3 _remove_irregular_past.py
"""
from __future__ import annotations
import json
from pathlib import Path

REMOVE_SET = {
    # 過去形 (現在形と異なる)
    'said','got','ran','sat','saw','made','came','went','met','swam','ate','drew','bought','fell','wrote',
    'broke','became','sang','knew','thought','took','spoke','built','caught','gave','forgot',
    'grew','paid','drank','felt','told','lost','meant','led','sent','stood','fought','wore','taught',
    'flew','sold','blew','rode','rang','threw','mistook','kept',
    'bent','left','heard','held','sought','dug','found','spent','wept','clung','swept','crept','slept',
    'wound','withdrew','withheld','withstood','shrank','rebuilt','laid',
    # 過去分詞 (現在形と異なる, 形容詞用法でも語彙混乱を招くので除外)
    'gone','done','eaten','seen','spoken','known','born','sung','drunk','begun',
    'won','worn','given','thrown','broken','frozen','fallen','stuck','forbidden','hidden','shaken',
}

# wound は 名詞=傷 でも使うので、文脈別判定: pos が "名" のみなら残す
NAME_KEEP_IF_POS_NOUN_ONLY = {'wound', 'ground', 'rose', 'shed', 'bit', 'shot'}


def is_remove(q: dict) -> bool:
    w = (q.get('word') or '').strip().lower()
    if w not in REMOVE_SET:
        return False
    if w in NAME_KEEP_IF_POS_NOUN_ONLY:
        pos = (q.get('pos') or '')
        # 動 を含まないなら残す (純粋な名詞用法)
        if '動' not in pos:
            return False
    return True


def main() -> None:
    total_removed = 0
    for n in range(1, 7):
        p = Path(f'stage{n}_quizzes_clean.json')
        if not p.is_file():
            continue
        d = json.loads(p.read_text(encoding='utf-8'))
        quizzes = d.get('quizzes', [])
        before = len(quizzes)

        kept = [q for q in quizzes if not is_remove(q)]
        removed_words = [q['word'] for q in quizzes if is_remove(q)]
        removed_count = before - len(kept)

        # order を 1..N に詰め直す
        # 既存 order の昇順で再採番 (元順序を保つ)
        kept.sort(key=lambda q: q.get('order') or 0)
        for i, q in enumerate(kept, 1):
            q['order'] = i

        d['quizzes'] = kept
        d['count'] = len(kept)

        p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
        total_removed += removed_count
        print(f'stage{n}: {before} → {len(kept)} (-{removed_count})')
        if removed_words:
            print(f'  removed: {", ".join(removed_words)}')

    print(f'\n総削除数: {total_removed}')


if __name__ == '__main__':
    main()
