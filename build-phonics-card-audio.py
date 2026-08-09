#!/usr/bin/env python3
"""Build the phonics card mockup data and preview audio."""
import subprocess
import sys


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def main() -> int:
    run([sys.executable, "sync-phonics-mockup-data.py"])
    run([sys.executable, "generate-phonics-espeak-audio.py", "--force"])
    run([sys.executable, "generate-phonics-pure-sound-audio.py", "--force"])
    run([sys.executable, "build-phonics-commons-cut-audio.py", "--force"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
