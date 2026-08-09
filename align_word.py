"""文の中の1語の区間（開始・終了秒）を強制アライメントで得る。

同音異義語（live=住む など）は単語単体で読ませると誤読される（espeak が /laɪv/ を選ぶ）。
文脈があれば正しく読めるので「文で合成 → その語の区間だけ切り出す」ために使う。

torchaudio(MMS_FA) は venv にしか入っていないため、このスクリプトは venv の python で動かす:
  venv/bin/python3 align_word.py <wav(16k mono)> <文> <対象語>
出力: "<start> <end>"（秒）
"""
import re
import sys

import numpy as np
import torch
import torchaudio
from scipy.io import wavfile

SR = 16000


def main() -> int:
    wav_path, sentence, target = sys.argv[1], sys.argv[2], sys.argv[3]
    sr, x = wavfile.read(wav_path)
    if sr != SR:
        print("ERR sample rate", file=sys.stderr)
        return 1
    x = x.astype(np.float32)
    if x.ndim > 1:
        x = x.mean(axis=1)
    peak = float(np.abs(x).max()) or 1.0
    wav = torch.tensor(x / peak).unsqueeze(0)

    words = sentence.split()
    norm = [re.sub(r"[^a-z]", "", w.lower()) for w in words]
    keep = [i for i, n in enumerate(norm) if n]
    transcript = [norm[i] for i in keep]

    bundle = torchaudio.pipelines.MMS_FA
    model = bundle.get_model()
    tokenizer = bundle.get_tokenizer()
    aligner = bundle.get_aligner()
    with torch.inference_mode():
        emission, _ = model(wav)
        spans = aligner(emission[0], tokenizer(transcript))

    ratio = (wav.shape[1] / SR) / emission.shape[1]
    tnorm = re.sub(r"[^a-z]", "", target.lower())
    for i, span in zip(keep, spans):
        if norm[i] == tnorm:
            start = span[0].start * ratio
            end = span[-1].end * ratio
            print(f"{start:.4f} {end:.4f}")
            return 0
    print("ERR word not found", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
