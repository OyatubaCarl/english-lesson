"""Generate QR PNG for theory ending. OpenCV based (qrcode pkg unavailable)."""
from pathlib import Path
import cv2
import numpy as np

URL = "https://english-lesson.gasflare.workers.dev/"
OUT = Path(__file__).resolve().parent / "qr.png"


def make_qr_png(url: str, scale: int = 16, quiet: int = 4) -> np.ndarray:
    enc = cv2.QRCodeEncoder_create()
    qr = enc.encode(url)
    if qr.ndim == 3:
        qr = cv2.cvtColor(qr, cv2.COLOR_BGR2GRAY)
    modules = (qr < 128).astype(np.uint8)
    modules = np.pad(modules, quiet, mode="constant", constant_values=0)
    pixels = np.kron(modules, np.ones((scale, scale), dtype=np.uint8))
    img = np.where(pixels == 1, 0, 255).astype(np.uint8)
    return img


def main() -> None:
    img = make_qr_png(URL)
    cv2.imwrite(str(OUT), img)
    decoded, _, _ = cv2.QRCodeDetector().detectAndDecode(cv2.imread(str(OUT)))
    assert decoded == URL, f"QR decode mismatch: {decoded!r}"
    print(f"{OUT} ({img.shape}) decoded={decoded}")


if __name__ == "__main__":
    main()
