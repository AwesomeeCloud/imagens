#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Converte a ilustração mestre (desenho luminoso branco/prateado sobre fundo azul)
numa imagem RGBA transparente, PRESERVANDO o brilho/glow.

A luminosidade acima do azul de fundo define o canal alfa (mantém halos e
reflexos translúcidos). A cor é empurrada para branco/prata luminoso.
Guarda com dpi=300.
"""
import sys
import numpy as np
from PIL import Image


def to_transparent(in_path, out_path, bg=(20, 35, 110)):
    im = Image.open(in_path).convert("RGB")
    a = np.array(im).astype(np.float32)
    bgv = np.array(bg, dtype=np.float32)

    lum = a.mean(axis=2)
    bg_lum = bgv.mean()
    alpha = np.clip((lum - bg_lum) / (180.0), 0, 1)
    alpha = np.power(alpha, 0.85)

    out_rgb = np.clip(a * 1.10 + 18, 0, 255)
    mask_bright = lum > 200
    for c in range(3):
        ch = out_rgb[..., c]
        ch[mask_bright] = np.clip(ch[mask_bright] + 25, 0, 255)
        out_rgb[..., c] = ch

    rgba = np.zeros((a.shape[0], a.shape[1], 4), dtype=np.uint8)
    rgba[..., 0] = out_rgb[..., 0].astype(np.uint8)
    rgba[..., 1] = out_rgb[..., 1].astype(np.uint8)
    rgba[..., 2] = out_rgb[..., 2].astype(np.uint8)
    rgba[..., 3] = (alpha * 255).astype(np.uint8)

    Image.fromarray(rgba, "RGBA").save(out_path, dpi=(300, 300))
    print("saved", out_path)


if __name__ == "__main__":
    to_transparent(sys.argv[1], sys.argv[2])
