"""Miniatura 1280x720 (YouTube) del video de Hawking: retrato a la izquierda, texto grande a la derecha, alto contraste.
Uso: TC_LAND=1 python3 -I src/miniatura_hawking.py   ->  out/miniatura_hawking.png"""
import os, sys, math
os.environ['TC_LAND'] = '1'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from lib import *
import scenes10 as S
import props as PR
from scenes2 import bust

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = f'{ROOT}/assets/fonts/silkscreen-latin-700-normal.woff'
t = 1.0
g = vgrad([(0, '#06082a'), (.55, '#2a1a7a'), (1, '#6a2a8a')])
c = Canvas(g)
stars(c, t, 220, 11, 170); S_bg = __import__('bg'); S_bg.nebula_l(c, t, 5)
for i in range(16):                                           # rayos de luz detrás del retrato
    a = i / 16 * math.pi * 2 + .3
    c.ed.polygon([(86, 92), (86 + 420 * math.cos(a), 92 + 420 * math.sin(a)), (86 + 420 * math.cos(a + .14), 92 + 420 * math.sin(a + .14))], fill=(255, 190, 120, 26))
b = bust('hawking_y', 'sad', (0, 1), 1.0, 1.75, None)
c.blit(b, 86 - b.width / 2, 22)
c.light(86, 80, 90, 80, (160, 190, 255), .35); c.amb = (1.0, .96, 1.06); c.vig = .5
img = c.render().resize((1280, 720), Image.NEAREST).convert('RGBA')
d = ImageDraw.Draw(img); d.fontmode = '1'


def fit(s, size, maxw):
    while ImageFont.truetype(FONT, size).getlength(s) + 30 > maxw and size > 20: size -= 2
    return size


def txt(xy, s, size, fill, stroke=14, sh=(8, 8), maxw=740):
    size = fit(s, size, maxw)
    f = ImageFont.truetype(FONT, size)
    d.text((xy[0] + sh[0], xy[1] + sh[1]), s, font=f, fill=(0, 0, 0, 255), stroke_width=stroke, stroke_fill=(0, 0, 0, 255), anchor='lm')
    d.text(xy, s, font=f, fill=fill, stroke_width=stroke, stroke_fill=(14, 10, 26, 255), anchor='lm')


txt((520, 150), '2 AÑOS', 150, (255, 70, 80))
txt((520, 290), 'DE VIDA', 150, (255, 255, 255))
d.rounded_rectangle([500, 395, 1250, 555], radius=18, fill=(255, 216, 74, 255), outline=(14, 10, 26, 255), width=10)
txt((530, 475), 'VIVIÓ 55 MÁS', 90, (20, 10, 40), stroke=0, sh=(0, 0), maxw=690)
txt((520, 640), 'STEPHEN HAWKING', 60, (200, 220, 255), stroke=9, sh=(5, 5), maxw=740)
# logo
f = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Black.otf', 40)
d.fontmode = 'L'
d.text((30, 28), 'TU CONF', font=f, fill=(255, 255, 255, 255))
w1 = d.textlength('TU CONF', font=f); w2 = d.textlength('.IA', font=f)
d.rounded_rectangle([30 + w1 - 2, 26, 30 + w1 + w2 + 8, 76], radius=8, fill=(139, 92, 246, 255)); d.text((30 + w1 + 4, 28), '.IA', font=f, fill=(255, 255, 255, 255))
os.makedirs(f'{ROOT}/out', exist_ok=True)
img.convert('RGB').save(f'{ROOT}/out/miniatura_hawking.png'); print('ok', img.size)
