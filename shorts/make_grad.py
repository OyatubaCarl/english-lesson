#!/usr/bin/env python3
"""全画面ショート用の上下グラデPNG（中央は透明・上下だけ暗く）を生成。"""
from PIL import Image

W, H = 1080, 1920
TOP_H, TOP_A = 340, 170      # 上: タイトル可読用
BOT_START, BOT_A = 1150, 205  # 下: 訳＋英語ラベル可読用

img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
px = img.load()
for y in range(H):
    a = 0
    if y < TOP_H:
        a = int(TOP_A * (1 - y / TOP_H))
    elif y >= BOT_START:
        a = int(BOT_A * ((y - BOT_START) / (H - BOT_START)))
    if a:
        for x in range(W):
            px[x, y] = (0, 0, 0, a)
img.save("/tmp/grad_overlay.png")
print("grad_overlay.png saved")
