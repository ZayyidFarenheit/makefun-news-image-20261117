#!/usr/bin/env python3
"""Entry point for the news-image-20261117 entry.

Copies the pre-rendered front page (entry.png, drawn by draw.py) into
the output directory the grader provides. Standard library only.
"""
import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "entry.png"


def main():
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / "entry.png"
    shutil.copyfile(SRC, dest)
    if dest.stat().st_size != SRC.stat().st_size:
        raise SystemExit("copy mismatch: %s != %s" % (dest, SRC))
    print("copied", SRC, "->", dest, "(%d bytes)" % dest.stat().st_size)


if __name__ == "__main__":
    main()
