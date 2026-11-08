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
    c.R(206, 28, 76, 122, (14, 10, 22)); c.R(209, 31, 70, 116, (255, 214, 130)); c.R(242, 31, 2, 116, (14, 10, 22))
    c.light(244, 90, 90, 80, (255, 214, 130), .7)
    if variant == 'A':
        c.d.ellipse([228, 96, 258, 124], fill=(70, 72, 90)); c.d.ellipse([234, 112, 252, 132], fill=(70, 72, 90))      # silueta genérica de espaldas
        c.d.polygon([(236, 98), (232, 70), (240, 70), (242, 98)], fill=(70, 72, 90)); c.d.polygon([(246, 98), (248, 70), (256, 70), (252, 98)], fill=(70, 72, 90))
        c.d.polygon([(228, 126), (222, 138), (236, 138)], fill=(70, 72, 90))
    else:
        c.d.ellipse([226, 98, 260, 128], fill=(110, 112, 130)); c.d.polygon([(234, 100), (230, 66), (240, 66), (242, 100)], fill=(110, 112, 130)); c.d.polygon([(246, 100), (248, 66), (258, 66), (252, 100)], fill=(110, 112, 130))
        c.R(238, 112, 3, 3, (20, 20, 30)); c.R(247, 112, 3, 3, (20, 20, 30))
    b = bust('disney_y', 'sad', (0, 1), 1.0, 1.75, None)
    c.blit(b, 62 - b.width / 2, 24)
    PR.keep(c, PR.doodle_page(False), 120, 110)
    c.light(62, 80, 70, 70, (255, 200, 150), .35); c.amb = (1.0, .96, 1.04); c.vig = .55
    return c.render().resize((1280, 720), Image.NEAREST).convert('RGBA')


def txt(d, xy, s, size, fill, stroke=14, sh=(8, 8), maxw=520):
    while ImageFont.truetype(FONT, size).getlength(s) + 30 > maxw and size > 20: size -= 2
    f = ImageFont.truetype(FONT, size)
    d.text((xy[0] + sh[0], xy[1] + sh[1]), s, font=f, fill=(0, 0, 0, 255), stroke_width=stroke, stroke_fill=(0, 0, 0, 255), anchor='lm')
    d.text(xy, s, font=f, fill=fill, stroke_width=stroke, stroke_fill=(14, 10, 26, 255), anchor='lm')


def make(variant):
    img = base(variant); d = ImageDraw.Draw(img); d.fontmode = '1'
    if variant == 'A':
        txt(d, (470, 130), 'PERDIÓ', 140, (255, 255, 255), maxw=520)
        txt(d, (470, 290), 'SU CONEJO', 120, (255, 210, 63), maxw=600)
    else:
        txt(d, (470, 130), '78 AÑOS', 140, (255, 210, 63), maxw=600)
        txt(d, (470, 290), 'DESPUÉS', 130, (255, 255, 255), maxw=600)
    f = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Black.otf', 40); d.fontmode = 'L'
    d.text((30, 28), 'TU CONF', font=f, fill=(255, 255, 255, 255)); w1 = d.textlength('TU CONF', font=f); w2 = d.textlength('.IA', font=f)
    d.rounded_rectangle([30 + w1 - 2, 26, 30 + w1 + w2 + 8, 76], radius=8, fill=(139, 92, 246, 255)); d.text((30 + w1 + 4, 28), '.IA', font=f, fill=(255, 255, 255, 255))
    img.convert('RGB').save(f'{ROOT}/out/miniatura_disney_{variant}.png')


for v in 'AB': make(v)
print('ok')
