"""Miniatura 1280x720 de Disney. Variante A «PERDIÓ SU CONEJO» / B «78 AÑOS DESPUÉS». Sin Mickey, sin Oswald real, sin logos.
Uso: python3 -I src/miniatura_disney.py  ->  out/miniatura_disney_A.png y _B.png"""
import os, sys, math
os.environ['TC_LAND'] = '1'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from lib import *
import bg, props as PR
from scenes2 import bust
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = f'{ROOT}/assets/fonts/silkscreen-latin-700-normal.woff'


def base(variant):
    c = Canvas(vgrad([(0, '#0e1236'), (.5, '#2a2a7a'), (1, '#6a2a5a')]))
    stars(c, 1.0, 140, 5, 120)
    bg.skyline(c, 0, 150, cols=((30, 28, 80), (46, 40, 104)), seed=7, lit=.5, t=1.0, wmin=16, wmax=30, hmin=40, hmax=100)
    c.R(0, 150, WW, 30, (24, 20, 50)); c.R(0, 150, WW, 3, (150, 140, 200))
    # puerta de oficina iluminada con silueta de conejo gris genérico alejándose
    c.R(236, 28, 76, 122, (14, 10, 22)); c.R(239, 31, 70, 116, (255, 214, 130)); c.R(272, 31, 2, 116, (14, 10, 22))
    c.light(274, 90, 90, 80, (255, 214, 130), .7)
    RC = (90, 74, 58)                                                                                              # silueta genérica de un solo tono
    ex = 258 if variant == 'A' else 262
    c.d.ellipse([ex - 14, 100, ex + 14, 130], fill=RC); c.d.ellipse([ex - 9, 118, ex + 9, 140], fill=RC)
    c.d.polygon([(ex - 8, 104), (ex - 12, 74), (ex - 3, 74), (ex - 2, 104)], fill=RC); c.d.polygon([(ex + 2, 104), (ex + 4, 74), (ex + 13, 74), (ex + 8, 104)], fill=RC)
    b = bust('disney_y', 'sad', (0, 1), 1.0, 1.75, None)
    b = b.resize((int(b.width * 1.2), int(b.height * 1.2)), Image.NEAREST)
    c.blit(b, 64 - b.width / 2, 20)
    c.light(62, 80, 70, 70, (255, 200, 150), .35); c.amb = (1.0, .96, 1.04); c.vig = .55
    return c.render().resize((1280, 720), Image.NEAREST).convert('RGBA')


def txt(d, xy, s, size, fill, stroke=14, sh=(8, 8), maxw=520):
    """texto Silkscreen; las tildes se dibujan aparte, pegadas a la letra (la fuente las deja flotando)."""
    ACC = {'Ó': 'O', 'É': 'E', 'Á': 'A', 'Í': 'I', 'Ú': 'U', 'Ñ': 'N'}
    plain = ''.join(ACC.get(ch, ch) for ch in s)
    while ImageFont.truetype(FONT, size).getlength(plain) + 30 > maxw and size > 20: size -= 2
    f = ImageFont.truetype(FONT, size)
    for (dx, dy, col, sw) in ((sh[0], sh[1], (0, 0, 0, 255), stroke), (0, 0, fill, stroke)):
        d.text((xy[0] + dx, xy[1] + dy), plain, font=f, fill=(0, 0, 0, 255) if col == (0, 0, 0, 255) else (14, 10, 26, 255), stroke_width=sw, stroke_fill=(0, 0, 0, 255) if col == (0, 0, 0, 255) else (14, 10, 26, 255), anchor='lm')
        d.text((xy[0] + dx, xy[1] + dy), plain, font=f, fill=col if col != (0, 0, 0, 255) else (0, 0, 0, 255), anchor='lm')
    for k, ch in enumerate(s):
        if ch in ACC:
            x0 = xy[0] + f.getlength(plain[:k]); w = f.getlength(plain[k]); top = xy[1] - size * .36
            ax = x0 + w * .55
            for dx, dy, col in ((sh[0], sh[1], (0, 0, 0, 255)), (0, 0, fill)):
                pts = [(ax - size * .08 + dx, top + size * .12 + dy), (ax + size * .12 + dx, top - size * .06 + dy), (ax + size * .2 + dx, top + size * .02 + dy), (ax + dx, top + size * .2 + dy)] if ch != 'Ñ' else [(ax - size * .26 + dx, top + size * .1 + dy), (ax - size * .26 + dx, top - size * .02 + dy), (ax + size * .26 + dx, top - size * .02 + dy), (ax + size * .26 + dx, top + size * .1 + dy)]
                if col != (0, 0, 0, 255): d.polygon([(p[0], p[1]) for p in pts], outline=(14, 10, 26, 255), width=0)
                d.polygon(pts, fill=col)


def make(variant):
    img = base(variant); d = ImageDraw.Draw(img); d.fontmode = '1'
    if variant == 'A':
        txt(d, (480, 100), 'SU CONEJO', 120, (255, 255, 255), maxw=640)
        txt(d, (480, 225), 'NO ERA SUYO', 110, (255, 210, 63), maxw=740)
    else:
        txt(d, (480, 105), '78 AÑOS', 140, (255, 210, 63), maxw=600)
        txt(d, (480, 235), 'DESPUÉS', 130, (255, 255, 255), maxw=640)
    f = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Black.otf', 40); d.fontmode = 'L'
    d.text((30, 28), 'TU CONF', font=f, fill=(255, 255, 255, 255)); w1 = d.textlength('TU CONF', font=f); w2 = d.textlength('.IA', font=f)
    d.rounded_rectangle([30 + w1 - 2, 26, 30 + w1 + w2 + 8, 76], radius=8, fill=(139, 92, 246, 255)); d.text((30 + w1 + 4, 28), '.IA', font=f, fill=(255, 255, 255, 255))
    img.convert('RGB').save(f'{ROOT}/out/miniatura_disney_{variant}.png')


for v in 'AB': make(v)
print('ok')
