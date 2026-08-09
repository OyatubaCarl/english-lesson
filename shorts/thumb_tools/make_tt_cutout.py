#!/usr/bin/env python3
"""Teacher Tacosのwelcoming素材から端に連結したオレンジ背景だけを透過する。"""

from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage


SOURCE = Path(
    "/Users/masaki/Documents/ClaudeCode/FunnicsIsland/characters/"
    "T_teacher_tacos/reference_pack/actions/welcoming.png"
)
OUTPUT = Path(__file__).resolve().parent / "tt_welcoming_cutout.png"


def main() -> None:
    rgb = Image.open(SOURCE).convert("RGB")
    hsv = np.asarray(rgb.convert("HSV"))

    # PillowのHSV値域（各チャンネル0..255）で背景候補を抽出する。
    candidate = (
        (hsv[:, :, 0] >= 10)
        & (hsv[:, :, 0] <= 40)
        & (hsv[:, :, 1] > 80)
        & (hsv[:, :, 2] > 80)
    )

    labels, _ = ndimage.label(candidate, structure=np.ones((3, 3), dtype=np.uint8))
    edge_labels = np.unique(
        np.concatenate(
            (labels[0, :], labels[-1, :], labels[:, 0], labels[:, -1])
        )
    )
    edge_labels = edge_labels[edge_labels != 0]
    background = np.isin(labels, edge_labels)

    # この素材は背景とキャラがほぼ同じ暖色域にあり、暗い輪郭にも上記HSV条件が
    # 当たる。端連結マスクだけではキャラまで連結するため、GrabCutで得た前景を
    # 保護する（実際に透過する領域は引き続き端連結ラベルの部分集合のみ）。
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError(
            "この素材の前景保護にはopencv-python（cv2）が必要です"
        ) from exc
    bgr = np.asarray(rgb)[:, :, ::-1].copy()
    grabcut_mask = np.zeros(bgr.shape[:2], dtype=np.uint8)
    bg_model = np.zeros((1, 65), dtype=np.float64)
    fg_model = np.zeros((1, 65), dtype=np.float64)
    cv2.grabCut(
        bgr,
        grabcut_mask,
        (35, 185, 955, 1190),
        bg_model,
        fg_model,
        8,
        cv2.GC_INIT_WITH_RECT,
    )
    protected_foreground = (grabcut_mask == cv2.GC_FGD) | (
        grabcut_mask == cv2.GC_PR_FGD
    )
    background &= ~protected_foreground

    alpha_binary = np.where(background, 0, 255).astype(np.uint8)
    alpha = Image.fromarray(alpha_binary).filter(
        ImageFilter.GaussianBlur(radius=1.5)
    )

    rgba = rgb.convert("RGBA")
    rgba.putalpha(alpha)
    rgba.save(OUTPUT)

    print(f"mask率: {background.mean() * 100:.2f}%")
    print(f"ファイルパス: {OUTPUT}")


if __name__ == "__main__":
    main()
