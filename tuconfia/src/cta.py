"""Llamada a la acción al final de cada Short: guardar + suscribirse/seguir. COMPACTA y en zona segura.
Va justo bajo el logo (y=330..500), centrada en x=500, ~480 px de ancho: deja libre la escena y el subtítulo.
Aparece con un deslizamiento corto y se retira antes del bucle."""
import math
from PIL import Image, ImageDraw, ImageFont

FONT = '/home/user/w/tuconfia/assets/fonts/silkscreen-latin-700-normal.woff'
PURPLE, WHITE, DARK, YEL = (139, 92, 246), (255, 255, 255), (14, 10, 26), (255, 216, 74)
LABEL = {'yt': 'SUSCRÍBETE', 'tt': 'SÍGUEME', 'ig': 'SÍGUEME'}
W, H = 560, 170


def _txt(d, xy, text, size, fill, stroke=5):
    f = ImageFont.truetype(FONT, size); d.fontmode = '1'
    d.text(xy, text, font=f, fill=fill, anchor='mm', stroke_width=stroke, stroke_fill=DARK)
    d.text(xy, text, font=f, fill=fill, anchor='mm')


def draw_cta(img, t, t0, total, platform='yt', loop_d=0.9, ytop=330, show=2.6):
    t1 = min(total - loop_d - .1, t0 + show)
    if not (t0 <= t < t1): return
    k = min(1, (t - t0) / .3); out = min(1, (t1 - t) / .25)
    slide = int((1 - (1 - k) ** 3) * 0 + (1 - k) * -40)                      # entra desde arriba
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    # marcador + frase de guardar (2 líneas pequeñas)
    d.polygon([(6, 8), (30, 8), (30, 50), (18, 40), (6, 50)], fill=YEL, outline=DARK)
    _txt(d, (W // 2 + 22, 16), 'GUÁRDALO PARA', 26, WHITE, 5)
    _txt(d, (W // 2 + 22, 46), 'CUANDO LO NECESITES', 26, WHITE, 5)
    # botón
    bounce = int(math.sin((t - t0) * 6) * 3)
    bw, bh = 420, 76; x0, y0 = (W - bw) // 2, 82 + bounce
    d.rounded_rectangle([x0 + 5, y0 + 6, x0 + bw + 5, y0 + bh + 6], radius=14, fill=(10, 6, 24, 190))
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=14, fill=PURPLE, outline=DARK, width=5)
    d.rounded_rectangle([x0 + 6, y0 + 6, x0 + bw - 6, y0 + 24], radius=8, fill=(176, 140, 255))
    d.rectangle([x0 + 24, y0 + 40, x0 + 54, y0 + 47], fill=WHITE); d.rectangle([x0 + 36, y0 + 28, x0 + 42, y0 + 58], fill=WHITE)
    _txt(d, (x0 + bw // 2 + 26, y0 + bh // 2 + 6), LABEL.get(platform, 'SÍGUEME'), 40, WHITE, 6)
    lay.putalpha(lay.getchannel('A').point(lambda v: int(v * min(1, k * 2) * out)))
    img.alpha_composite(lay, (500 - W // 2, ytop + slide))
