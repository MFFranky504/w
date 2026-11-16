"""Miniatura de «5 famosos que lo perdieron casi todo y volvieron»: cinco caras con su NO y texto corto."""
import os, sys, math
os.environ['TC_LAND'] = '1'; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont
import scenes19 as S
from scenes2 import bust
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FL = lambda s: ImageFont.truetype(f'{ROOT}/assets/fonts/silkscreen-latin-700-normal.woff', s)
c = S.cv('#140a20', '#2a1648')
for i in range(3): S.bg.beam(c, 60 + i * 100, 0, 5, 50, S.FLY, (255, 246, 210), 26)
for i, w in enumerate(S.CAST5):
    b = S.spr(bust(w, 'worry' if i % 2 else 'n', (0, 0), 1.0, 1.0)); c.im.paste(b, (36 + i * 62 - b.width // 2, 52), b)
img = S.fin(c, 'day', (1.05, 1, 1.05), .35).convert('RGB').resize((1280, 720), Image.NEAREST)
dr = ImageDraw.Draw(img)
for i in range(5):                                                         # sellos NO sobre cada cara
    x = (36 + i * 62) * 4 - 52; dr.rectangle([x, 470, x + 104, 545], fill=(250, 244, 240)); dr.rectangle([x + 4, 474, x + 100, 541], fill=(220, 40, 60))
    dr.text((x + 52, 508), 'NO', font=FL(48), fill=(255, 255, 255), anchor='mm')
for dx, dy, col in ((8, 8, (200, 20, 60)), (0, 0, None)):
    dr.text((640 + dx, 70 + dy), '5 FAMOSOS', font=FL(110), anchor='mm', fill=col or (255, 255, 255), stroke_width=10, stroke_fill=col or (14, 10, 26))
    dr.text((640 + dx, 200 + dy), 'VOLVIERON', font=FL(120), anchor='mm', fill=col or (90, 220, 120), stroke_width=11, stroke_fill=col or (14, 10, 26))
img.save(f'{ROOT}/out/miniatura_famosos.png'); print('ok')
