#!/usr/bin/env python3
"""manifest_thumbs.jsonの全項目を順次サムネイル化する。"""

from __future__ import annotations

import json

from build_thumbnail import (
    MANIFEST_PATH,
    THUMBNAILS_DIR,
    generate_thumbnail,
    thumbnail_filename,
)


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    success = 0
    failures: list[tuple[str, str]] = []

    for item in manifest:
        output = THUMBNAILS_DIR / thumbnail_filename(item)
        try:
            generate_thumbnail(item, output)
            success += 1
        except Exception as exc:  # 1件の失敗でバッチ全体を止めない
            failures.append((item.get("id", "<unknown>"), str(exc)))
            print(f"失敗: {item.get('id', '<unknown>')}: {exc}")

    print(f"\n成功: {success} / 失敗: {len(failures)} / 合計: {len(manifest)}")
    if failures:
        print("失敗一覧:")
        for item_id, message in failures:
            print(f"  {item_id}: {message}")


if __name__ == "__main__":
    main()
