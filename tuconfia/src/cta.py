"""Llamada a la acción al final de cada Short: guardar + suscribirse/seguir, con botón pixel-art animado.
Zona segura: centrado en x=500, entre y=560 y y=980 (por encima de los subtítulos, lejos de la interfaz de YouTube/TikTok)."""
import math
from PIL import Image, ImageDraw, ImageFont

FONT = '/home/user/w/tuconfia/assets/fonts/silkscreen-latin-700-normal.woff'
PURPLE, WHITE, DARK, YEL = (139, 92, 246), (255, 255, 255), (14, 10, 26), (255, 216, 74)
LABEL = {'yt': 'SUSCRÍBETE', 'tt': 'SÍGUEME', 'ig': 'SÍGUEME'}


def _txt(d, xy, text, size, fill, stroke=6, anchor='mm'):
    f = ImageFont.truetype(FONT, size); d.fontmode = '1'
    d.text(xy, text, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=DARK)
    d.text(xy, text, font=f, fill=fill, anchor=anchor)


def draw_cta(img, t, t0, total, platform='yt', loop_d=0.9, ytop=560):
    """img RGBA 1080x1920. Aparece en [t0, total-loop_d]: marcador + 'Guárdalo para cuando lo necesites' + botón."""
    if not (t0 <= t < total - loop_d + .25): return
    k = min(1, (t - t0) / .35); pop = 1 - (1 - k) ** 3 + .12 * math.sin(k * math.pi) * (1 - k)
    out = min(1, (total - loop_d + .25 - t) / .25)
    a = int(255 * min(1, k * 2) * out)
    lay = Image.new('RGBA', (1080, 460), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    cx = 500
    # marcador de guardar (pixel-art) + texto
    bx, by = cx - 330, 20
    d.polygon([(bx, by), (bx + 44, by), (bx + 44, by + 76), (bx + 22, by + 56), (bx, by + 76)], fill=YEL, outline=DARK)
    _txt(d, (cx + 30, 38), 'GUÁRDALO PARA', 52, WHITE, 8)
    _txt(d, (cx + 30, 100), 'CUANDO LO NECESITES', 52, WHITE, 8)
    # botón de suscribirse / seguir con "+" y rebote
    bounce = int(math.sin((t - t0) * 6) * 5)
    w, h = 640, 140; x0, y0 = cx - w // 2, 190 + bounce
    d.rounded_rectangle([x0 + 8, y0 + 10, x0 + w + 8, y0 + h + 10], radius=18, fill=(10, 6, 24, 190))
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=18, fill=PURPLE, outline=DARK, width=6)
    d.rounded_rectangle([x0 + 8, y0 + 8, x0 + w - 8, y0 + 34], radius=10, fill=(176, 140, 255))
    d.rectangle([x0 + 34, y0 + 66, x0 + 78, y0 + 76], fill=WHITE); d.rectangle([x0 + 51, y0 + 49, x0 + 61, y0 + 93], fill=WHITE)
    _txt(d, (x0 + w // 2 + 36, y0 + h // 2 + 8), LABEL.get(platform, 'SÍGUEME'), 64, WHITE, 9)
    if pop != 1: lay = lay.resize((int(1080 * pop), int(460 * pop)), Image.BILINEAR)
    lay.putalpha(lay.getchannel('A').point(lambda v: int(v * a / 255)))
    img.alpha_composite(lay, (500 - int(500 * pop), ytop + (460 - lay.height) // 2))
