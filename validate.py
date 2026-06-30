#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Valida os outputs de uma mesa: dimensões, dpi e existência."""
import sys, os
from PIL import Image

def check(path):
    if not os.path.exists(path):
        return f"FALTA: {path}"
    im = Image.open(path)
    dpi = im.info.get('dpi', None)
    ok = im.size == (1748, 2480)
    return f"{'OK ' if ok else 'ERR'} {os.path.basename(path)} size={im.size} dpi={dpi}"

if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(check(p))
