#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Motor de composição do estacionário de casamento (estilo místico-luminoso).

Constrói as peças finais SOBRE as bases originais e fixas do repositório,
inserindo apenas os elementos variáveis. As bases nunca são redesenhadas.

Inspirado nos exemplos validados (Moliceiro / Sé de Aveiro):
  - título prateado grande com brilho metálico subtil
  - "MESA XX" em maiúsculas com tracking largo (apenas convidados)
  - localização em maiúsculas com tracking muito largo
  - ilustração mestre luminosa com glow, integrada e generosa
  - frase poética em itálico
  - nomes em duas colunas, ladeando o monograma (apenas convidados)

Resultado: 1748 x 2480 px, 300 dpi.
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# -------------------- Caminhos --------------------
REPO = "/home/ubuntu/imagens"
FONTS = "/home/ubuntu/fonts"
BASE_CONV = os.path.join(REPO, "BASE_Convidados_A5_1748x2480_300dpi.png")
BASE_MESA = os.path.join(REPO, "Mesa_Base_A5_1748x2480_300dpi.png")

W, H = 1748, 2480
DPI = (300, 300)

SILVER = (228, 234, 244)
SILVER_SOFT = (198, 208, 226)
WHITE = (244, 248, 253)

# -------------------- Fontes --------------------
F_TITLE = os.path.join(FONTS, "Cormorant.ttf")
F_ITALIC = os.path.join(FONTS, "Cormorant-Italic.ttf")
F_BODY = os.path.join(FONTS, "EBGaramond[wght].ttf")
F_BODY_IT = os.path.join(FONTS, "EBGaramond-Italic[wght].ttf")


def font(path, size, variation=None):
    f = ImageFont.truetype(path, size)
    if variation:
        try:
            f.set_variation_by_name(variation)
        except Exception:
            pass
    return f


def text_w(draw, s, fnt, tracking=0):
    if tracking == 0:
        return draw.textlength(s, font=fnt)
    return sum(draw.textlength(ch, font=fnt) for ch in s) + tracking * max(0, len(s) - 1)


# ---------- desenho com brilho prateado ----------

def _metallic_gradient(size, top=(250, 252, 255), mid=(196, 205, 222), bot=(232, 238, 248)):
    """Cria um gradiente vertical prateado para preencher texto (efeito metálico)."""
    w, h = size
    grad = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / max(1, h - 1)
        if t < 0.5:
            k = t / 0.5
            r = int(top[0] + (mid[0] - top[0]) * k)
            g = int(top[1] + (mid[1] - top[1]) * k)
            b = int(top[2] + (mid[2] - top[2]) * k)
        else:
            k = (t - 0.5) / 0.5
            r = int(mid[0] + (bot[0] - mid[0]) * k)
            g = int(mid[1] + (bot[1] - mid[1]) * k)
            b = int(mid[2] + (bot[2] - mid[2]) * k)
        grad.putpixel((0, y), (r, g, b))
    return grad.resize((w, h))


def draw_metallic_text(canvas, xc, y, text, fnt, glow=True, tracking=0):
    """Desenha texto com preenchimento metálico prateado e leve glow."""
    tmp = Image.new("L", (W, H), 0)
    td = ImageDraw.Draw(tmp)
    # medir
    if tracking:
        total = text_w(td, text, fnt, tracking)
        x = xc - total / 2
        for ch in text:
            td.text((x, y), ch, font=fnt, fill=255)
            x += td.textlength(ch, font=fnt) + tracking
    else:
        tw = td.textlength(text, font=fnt)
        td.text((xc - tw / 2, y), text, font=fnt, fill=255)

    bbox = tmp.getbbox()
    if not bbox:
        return
    # glow
    if glow:
        glow_layer = tmp.filter(ImageFilter.GaussianBlur(10))
        glow_rgba = Image.new("RGBA", (W, H), (210, 222, 245, 0))
        glow_rgba.putalpha(glow_layer.point(lambda p: int(p * 0.55)))
        canvas.alpha_composite(glow_rgba)
    # preenchimento metálico
    grad = _metallic_gradient((W, H)).convert("RGBA")
    grad.putalpha(tmp)
    canvas.alpha_composite(grad)


def draw_centered(draw, xc, y, s, fnt, fill):
    w = draw.textlength(s, font=fnt)
    draw.text((xc - w / 2, y), s, font=fnt, fill=fill)
    return w


def draw_tracked(draw, xc, y, s, fnt, fill, tracking):
    total = text_w(draw, s, fnt, tracking)
    x = xc - total / 2
    for ch in s:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking
    return total


def fit_title(draw, text, max_w, start_size, path, variation):
    size = start_size
    while size > 60:
        f = font(path, size, variation)
        if draw.textlength(text, font=f) <= max_w:
            return f, size
        size -= 4
    return font(path, size, variation), size


def add_illustration(canvas, illo_path, center_x, center_y, target_h, max_w=1320):
    illo = Image.open(illo_path).convert("RGBA")
    bbox = illo.getbbox()
    if bbox:
        illo = illo.crop(bbox)
    iw, ih = illo.size
    scale = target_h / ih
    new_w, new_h = int(iw * scale), int(ih * scale)
    if new_w > max_w:
        scale = max_w / iw
        new_w, new_h = int(iw * scale), int(ih * scale)
    illo = illo.resize((new_w, new_h), Image.LANCZOS)
    x = int(center_x - new_w / 2)
    y = int(center_y - new_h / 2)
    canvas.alpha_composite(illo, (x, y))
    return (x, y, new_w, new_h)


def split_two_columns(names):
    n = len(names)
    left_n = (n + 1) // 2
    return names[:left_n], names[left_n:]


def build_guest_piece(data, illo_path, out_path):
    base = Image.open(BASE_CONV).convert("RGBA")
    canvas = base.copy()
    draw = ImageDraw.Draw(canvas)
    xc = W // 2

    # MESA XX
    f_mesa = font(F_TITLE, 78, "Medium")
    draw_tracked(draw, xc, 150, f"MESA {data['num']}", f_mesa, SILVER_SOFT, 20)

    # Título metálico
    f_title, ts = fit_title(draw, data["nome"], 1360, 168, F_TITLE, "Bold")
    ty = 250
    draw_metallic_text(canvas, xc, ty, data["nome"], f_title, glow=True)
    draw = ImageDraw.Draw(canvas)

    # Localização
    f_loc = font(F_TITLE, 56, "Medium")
    loc_y = ty + ts + 12
    draw_tracked(draw, xc, loc_y, data["local"].upper(), f_loc, SILVER_SOFT, 30)

    # Ilustração
    illo_center_y = 1070
    add_illustration(canvas, illo_path, xc, illo_center_y, target_h=1060, max_w=1360)
    draw = ImageDraw.Draw(canvas)

    # Frase poética
    f_phrase = font(F_ITALIC, 60, "Medium")
    phrase_y = 1605
    draw_centered(draw, xc, phrase_y, data["frase"], f_phrase, SILVER)

    # Nomes em duas colunas
    left, right = split_two_columns(data["convidados"])
    f_name = font(F_BODY, 54, "Medium")
    line_h = 78
    names_top = 1880
    col_left_x = int(W * 0.30)
    col_right_x = int(W * 0.70)
    for i, nm in enumerate(left):
        draw_centered(draw, col_left_x, names_top + i * line_h, nm, f_name, WHITE)
    for i, nm in enumerate(right):
        draw_centered(draw, col_right_x, names_top + i * line_h, nm, f_name, WHITE)

    canvas.convert("RGB").save(out_path, dpi=DPI)
    return out_path


def build_table_piece(data, illo_path, out_path):
    base = Image.open(BASE_MESA).convert("RGBA")
    canvas = base.copy()
    draw = ImageDraw.Draw(canvas)
    xc = W // 2

    # Título metálico
    f_title, ts = fit_title(draw, data["nome"], 1360, 180, F_TITLE, "Bold")
    ty = 250
    draw_metallic_text(canvas, xc, ty, data["nome"], f_title, glow=True)
    draw = ImageDraw.Draw(canvas)

    # Localização
    f_loc = font(F_TITLE, 56, "Medium")
    loc_y = ty + ts + 12
    draw_tracked(draw, xc, loc_y, data["local"].upper(), f_loc, SILVER_SOFT, 30)

    # Ilustração (maior, mais centrada)
    illo_center_y = 1260
    add_illustration(canvas, illo_path, xc, illo_center_y, target_h=1280, max_w=1420)
    draw = ImageDraw.Draw(canvas)

    # Frase poética
    f_phrase = font(F_ITALIC, 64, "Medium")
    phrase_y = 1980
    draw_centered(draw, xc, phrase_y, data["frase"], f_phrase, SILVER)

    canvas.convert("RGB").save(out_path, dpi=DPI)
    return out_path


if __name__ == "__main__":
    import sys, json
    mode = sys.argv[1]
    data = json.loads(sys.argv[2])
    illo = sys.argv[3]
    out = sys.argv[4]
    if mode == "guest":
        build_guest_piece(data, illo, out)
    elif mode == "table":
        build_table_piece(data, illo, out)
    print("saved", out)
