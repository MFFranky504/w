"""Peinados de hombre que siguen la forma del cráneo (sin «casco de hongo»): la frente y las orejas quedan a la vista.
Cada peinado se define una sola vez en coordenadas del retrato (96 px de ancho, cráneo = elipse cx±21, y 6..58)
y se escala al sprite de cuerpo entero (×0.43) y al chibi (×0.9 / ×0.67).

Estilos: crew (corto), slick (engominado hacia atrás), sidepart (raya al lado), messy (despeinado),
wavy (ondulado con raya al medio, tapa las orejas), curly (rizado), receding (con entradas)."""
import math
import numpy as np
from PIL import Image, ImageDraw

STYLES = ('buzz', 'crew', 'slick', 'sidepart', 'messy', 'wavy', 'curly', 'receding', 'pulled')
ALIAS = {'side': 'sidepart', 'part': 'wavy'}
PW, PH, CX = 96, 80, 48
_CACHE = {}


def style_of(CS):
    """peinado nuevo que corresponde al personaje, o None si se dibuja con el sistema anterior."""
    if not CS.get('v2'): return None                       # solo personajes del sistema nuevo (reparto de Cantinflas en adelante)
    h = CS.get('hair2')
    h = ALIAS.get(h, h)
    if h in STYLES: return h
    if h == 'buzz': return 'buzz'
    if h is None and CS.get('style') in ('short', 'shag') and not CS.get('kid_old'):
        return 'crew' if CS['style'] == 'short' else 'messy'
    return None


def _hairline(pts):
    """polígono que borra todo lo que queda por debajo de la línea del pelo (de izquierda a derecha)."""
    return [(CX - 40, PH)] + [(CX + x, y) for x, y in pts] + [(CX + 40, PH)]


def build(style):
    """máscaras en coordenadas del retrato: base (pelo), dark (sombra), back (nuca, detrás de la cara) y líneas."""
    if style in _CACHE: return _CACHE[style]
    base = Image.new('L', (PW, PH)); d = ImageDraw.Draw(base)
    back = Image.new('L', (PW, PH)); bd = ImageDraw.Draw(back)
    lines = []                                   # (puntos, 'd' oscuro | 'l' claro)
    c = CX
    pads = {'pulled': 2, 'buzz': 0, 'crew': 2, 'slick': 2, 'sidepart': 3, 'messy': 3, 'wavy': 3, 'curly': 4, 'receding': 1}
    p = pads[style]
    d.ellipse([c - 21 - p, 6 - p, c + 21 + p, 58 + p], fill=255)
    side = [(-40, 44), (-23, 44), (-21, 44), (-18, 44)]
    sideR = [(18, 44), (21, 44), (23, 44), (40, 44)]
    if style == 'buzz':                                                          # rapado: sigue el cráneo, textura de pelo cortito
        d.polygon(_hairline(side + [(-17, 30), (-13, 26), (-6, 24), (6, 24), (13, 26), (17, 30)] + sideR), fill=0)
        for k in range(16): lines.append(([(c - 16 + (k * 13) % 32, 8 + (k * 7) % 16)], 'd'))
    elif style == 'crew':
        d.rectangle([0, 0, PW, 5], fill=0)                                    # copa algo plana
        d.polygon(_hairline(side + [(-17, 30), (-13, 27), (-6, 24), (6, 24), (13, 27), (17, 30)] + sideR), fill=0)
        for k in range(26): lines.append(([(c - 17 + (k * 13) % 34, 8 + (k * 7) % 16)], 'l' if k % 3 else 'd'))
    elif style == 'slick':
        d.ellipse([c - 15, 1, c + 11, 15], fill=255)                           # volumen delante
        d.polygon(_hairline([(-40, 40), (-21, 40), (-18, 40), (-17, 28), (-12, 24), (-5, 22), (5, 22), (12, 24), (17, 28), (18, 40), (21, 40), (40, 40)]), fill=0)
        for a in ([(-10, 22), (-12, 13), (-8, 5)], [(-3, 22), (-4, 12), (0, 4)], [(5, 22), (5, 12), (9, 5)], [(12, 24), (14, 15), (17, 9)]):
            lines.append(([(c + x, y) for x, y in a], 'd'))
        lines += [([(c - 14, 12), (c - 6, 4)], 'l'), ([(c - 9, 11), (c - 2, 4)], 'l')]
    elif style == 'sidepart':
        d.polygon(_hairline(side + [(-17, 30), (-13, 26), (-9, 23), (-4, 26), (4, 27), (11, 27), (16, 30)] + sideR), fill=0)   # sin volumen extra: no hay bulto
        lines += [([(c - 9, 6), (c - 9, 22)], 'k'), ([(c - 7, 12), (c + 4, 20), (c + 14, 26)], 'd'), ([(c - 6, 8), (c + 8, 14), (c + 18, 22)], 'd'),
                  ([(c - 4, 9), (c + 6, 13)], 'l'), ([(c - 18, 14), (c - 12, 8)], 'l')]
    elif style == 'messy':
        for tri in ([(-16, 10), (-24, 2), (-10, 6)], [(-9, 6), (-6, 0), (-2, 5)], [(1, 5), (6, 0), (8, 6)], [(9, 7), (17, 1), (15, 10)],
                    [(17, 12), (26, 9), (21, 18)], [(-21, 22), (-28, 19), (-22, 30)], [(21, 24), (28, 24), (22, 32)]):
            d.polygon([(c + x, y) for x, y in tri], fill=255)
        d.polygon(_hairline(side + [(-17, 30), (-13, 26), (-6, 24), (6, 24), (13, 26), (17, 30)] + sideR), fill=0)
        for tri in ([(-12, 22), (-9, 32), (-6, 23)], [(-2, 23), (1, 31), (4, 23)], [(8, 24), (12, 30), (13, 25)]):
            d.polygon([(c + x, y) for x, y in tri], fill=255)                   # mechones sueltos sobre la frente
        lines += [([(c - 14, 10), (c - 8, 18)], 'd'), ([(c - 2, 7), (c, 18)], 'd'), ([(c + 9, 9), (c + 7, 19)], 'd'), ([(c - 10, 8), (c - 4, 6)], 'l')]
    elif style == 'wavy':
        d.polygon(_hairline([(-40, 54), (-24, 54), (-20, 50), (-18, 40), (-14, 32), (-7, 26), (-1, 22), (1, 22), (7, 26), (14, 32), (18, 40), (20, 50), (24, 54), (40, 54)]), fill=0)
        for x0 in (-22, 22):
            for k in range(3): d.ellipse([c + x0 - 4, 38 + k * 6, c + x0 + 4, 46 + k * 6], fill=255)   # puntas onduladas
        bd.ellipse([c - 25, 26, c + 25, 66], fill=255)
        lines += [([(c, 6), (c, 22)], 'd'), ([(c - 4, 10), (c - 14, 22), (c - 19, 36)], 'd'), ([(c + 4, 10), (c + 14, 22), (c + 19, 36)], 'd'),
                  ([(c - 9, 9), (c - 17, 18)], 'l'), ([(c + 6, 8), (c + 12, 13)], 'l')]
    elif style == 'curly':
        for a in range(190, 351, 16):
            r = math.radians(a); x = c + math.cos(r) * (21 + p); y = 32 + math.sin(r) * (26 + p)
            d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=255)
        d.polygon(_hairline([(-40, 42), (-22, 42), (-18, 42), (-17, 30), (-12, 26), (-5, 25), (5, 25), (12, 26), (17, 30), (18, 42), (22, 42), (40, 42)]), fill=0)
        for k in range(18):
            x, y = c - 16 + (k * 11) % 32, 6 + (k * 5) % 18
            lines.append(([(x, y), (x + 2, y - 1), (x + 3, y + 1)], 'd' if k % 2 else 'l'))
    elif style == 'pulled':                                                      # recogido con raya al medio (trenzas): frente despejada, sin flequillo
        d.polygon(_hairline([(-40, 46), (-23, 46), (-20, 46), (-18, 34), (-13, 27), (-6, 24), (0, 23), (6, 24), (13, 27), (18, 34), (20, 46), (23, 46), (40, 46)]), fill=0)
        lines += [([(c, 5), (c, 22)], 'k'), ([(c - 3, 8), (c - 15, 20)], 'd'), ([(c + 3, 8), (c + 15, 20)], 'd'), ([(c - 7, 8), (c - 13, 13)], 'l'), ([(c + 6, 7), (c + 11, 11)], 'l')]
    elif style == 'receding':
        d.polygon(_hairline([(-40, 40), (-21, 40), (-18, 40), (-16, 22), (-12, 15), (-7, 19), (-3, 22), (0, 23), (3, 22), (7, 19), (12, 15), (16, 22), (18, 40), (21, 40), (40, 40)]), fill=0)
        for k in range(14): lines.append(([(c - 15 + (k * 11) % 30, 6 + (k * 7) % 10)], 'l' if k % 2 else 'd'))
    a = np.array(base) > 0
    dk = np.zeros_like(a); xs = np.arange(PW)[None, :]; ys = np.arange(PH)[:, None]
    dk |= (xs > CX + 11 + (ys - 20) * .15) & a                                 # sombra del lado derecho (luz desde la izquierda)
    _CACHE[style] = (a, dk, np.array(back) > 0, lines)
    return _CACHE[style]


def _scaled(m, sx, sy, oy):
    """máscara del retrato → máscara a otra escala (promedio por área y umbral, sin dientes de sierra)."""
    w, h = max(1, round(PW * sx)), max(1, round(PH * sy))
    im = Image.fromarray((m * 255).astype('uint8')).resize((w, h), Image.BOX)
    return (np.array(im) > 110), w, h


def _place(P, m, x0, y0):
    """copia una máscara en la posición (x0, y0) del lienzo de P (recortando lo que se sale)."""
    H, W = P.a.shape[:2]; out = np.zeros((H, W), bool)
    h, w = m.shape
    xa, ya = max(0, x0), max(0, y0); xb, yb = min(W, x0 + w), min(H, y0 + h)
    if xb > xa and yb > ya: out[ya:yb, xa:xb] = m[ya - y0:yb - y0, xa - x0:xb - x0]
    return out


def _skin_cap(P, cx, sk, ell, rows_max, rows_min=0):
    """piel del cráneo bajo el pelo (para las entradas y la frente alta)."""
    from lib import shade
    rows = np.arange(P.a.shape[0])[:, None]
    cap = P.mask(lambda d: d.ellipse(ell, fill=255)) & (rows < rows_max) & (rows >= rows_min)
    x0, y0, x1, y1 = ell
    olm = P.mask(lambda d: d.ellipse([x0 - 1, y0 - 1, x1 + 1, y1 + 1], fill=255)) & (rows < rows_max) & (rows >= rows_min) & ~cap
    P.a[olm] = (*shade(sk, .5), 255); P.a[cap] = (*sk, 255)


def _hat_clip(a, CS):
    """con sombrero, el ala tapa la raíz: no queda pelo por encima de la línea del ala (y < 24 en el retrato)."""
    if not CS.get('hat'): return a
    a = a.copy(); a[:24] = False
    return a


def _draw_small(P, style, cx, hc, sk, sx, sy, oy, cap, CS=None):
    a, dk, _, lines = build(style)
    a = _hat_clip(a, CS or {})
    ell, rmax = cap
    _skin_cap(P, cx, sk, ell, rmax, int(round(oy + 24 * sy)) if (CS or {}).get('hat') else 0)   # con sombrero, nada de cráneo por encima del ala
    ma, w, h = _scaled(a, sx, sy, oy); md, _, _ = _scaled(dk, sx, sy, oy)
    x0 = int(round(cx - CX * sx)); y0 = int(round(oy))
    full = _place(P, ma, x0, y0); shadow = _place(P, md & ma, x0, y0)
    P.add(lambda d: d.bitmap((0, 0), Image.fromarray((full * 255).astype('uint8')), fill=255), hc['b'], edge_k=.45)
    P.a[shadow & (P.a[..., 3] > 0)] = (*hc['d'], 255)
    for pts, k in lines[:6]:
        q = [(int(round(cx + (x - CX) * sx)), int(round(oy + y * sy))) for x, y in pts]
        col = hc['d'] if k == 'd' else (sk if k == 'k' else hc['l'])
        for x, y in q:
            if 0 <= y < P.a.shape[0] and 0 <= x < P.a.shape[1] and full[y, x]: P.a[y, x] = (*col, 255)


def front_b(P, CS, cx, hc, sk):
    st = style_of(CS)
    if not st: return False
    _draw_small(P, st, cx, hc, sk, .43, .44, -6 * .44, ([cx - 9, 1, cx + 9, 21], 11), CS)
    return True


def front_r(P, CS, cx, HR, sk):
    st = style_of(CS)
    if not st: return False
    wide = st in ('pulled', 'wavy')
    _draw_small(P, st, cx, HR, sk, .9 if wide else .78, .67, 1 - 6 * .67, ([cx - 18, 1, cx + 18, 31] if wide else [cx - 16, 2, cx + 16, 30], 15), CS)
    return True


def front_p(d, CS, cx, hb, hd, hl):
    st = style_of(CS)
    if not st: return False
    a, dk, _, lines = build(st)
    a = _hat_clip(a, CS); dk = dk & a
    ox = cx - CX; sk = CS['skin']
    d.bitmap((ox, 0), Image.fromarray((a * 255).astype('uint8')), fill=hb)
    d.bitmap((ox, 0), Image.fromarray((dk * 255).astype('uint8')), fill=hd)
    for pts, k in lines:                                                         # textura y mechones: solo dentro del pelo
        for x, y in _raster(pts):
            if 0 <= y < PH and 0 <= x < PW and a[y, x]: d.point((x + ox, y), fill=hd if k == 'd' else (sk if k == 'k' else hl))
    return True


def _raster(pts):
    """píxeles de una polilínea (Bresenham)."""
    if len(pts) == 1: return [tuple(int(v) for v in pts[0])]
    out = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1); n = max(abs(x1 - x0), abs(y1 - y0), 1)
        out += [(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n)) for i in range(n + 1)]
    return out


def back_p(bd, CS, cx, hb, hd):
    st = style_of(CS)
    if not st: return False
    _, _, bk, _ = build(st)
    if bk.any(): bd.bitmap((cx - CX, 0), Image.fromarray((bk * 255).astype('uint8')), fill=hd)
    return True


def skull_p(d, CS, cx, sk):
    """cráneo de piel en la capa de la cara: la frente sube hasta la línea del pelo."""
    if style_of(CS): d.ellipse([cx - 19, 8, cx + 19, 50], fill=sk)
