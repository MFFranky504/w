"""Rasgos para parecido con famosos, comunes a los tres dibujantes (chibi «r», cuerpo entero «b», retrato «p»).
Claves opcionales del reparto (cast.py):
  hair2: bald | buzz | pompadour | volume | wild | bun | afro   (sustituye al peinado frontal del estilo)
  nose: bool (nariz ancha)   mustache: bool   unibrow: bool   brows: 'thick'   age: bool (arrugas)   smirk: bool (media sonrisa)   chin: bool (papada)
  build: slim | average | athletic | heavy | muscular   height: short | average | tall   (solo cuerpo entero)"""
import numpy as np
from PIL import Image
from lib import shade

B4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
BUILD = {'slim': (.88, .9, .9), 'average': (1.0, 1.0, 1.0), 'athletic': (1.1, 1.0, 1.12), 'heavy': (1.16, 1.42, 1.15), 'muscular': (1.34, 1.06, 1.35)}   # hombros, cintura, grosor
HEIGHT = {'short': .84, 'average': .9, 'tall': .97}


def dither_cap(P, mask, col_a, col_b, k=.5):
    yy, xx = np.nonzero(mask); sel = B4[yy % 4, xx % 4] < k
    P.a[yy[sel], xx[sel]] = (*col_b, 255); P.a[yy[~sel], xx[~sel]] = (*col_a, 255)


# ------------------------------------------------------------------ cuerpo entero (84x124, cabeza ~ cx±9, y 0-27)
def back_b(P, CS, cx, hc):
    h = CS.get('hair2')
    if h == 'volume':
        P.add(lambda d: d.ellipse([cx - 19, -3, cx + 19, 36], fill=255), hc['b'], edge_k=.4)
        P.add(lambda d: d.ellipse([cx - 16, 22, cx + 16, 44], fill=255), hc['d'], edge_k=.4)
    elif h == 'afro':
        P.add(lambda d: d.ellipse([cx - 15, -1, cx + 15, 24], fill=255), hc['b'], edge_k=.4)
    elif h == 'wild':
        P.add(lambda d: d.polygon([(cx - 9, 4), (cx - 15, 3), (cx - 12, 9), (cx - 17, 12), (cx - 12, 15), (cx - 16, 20), (cx - 10, 21), (cx + 10, 21), (cx + 16, 20), (cx + 12, 15), (cx + 17, 12), (cx + 12, 9), (cx + 15, 3), (cx + 9, 4)], fill=255), hc['b'], edge_k=.4)
    elif h == 'bun':
        P.add(lambda d: d.ellipse([cx - 6, -1, cx + 6, 8], fill=255), hc['b'], edge_k=.4)


def front_b(P, CS, cx, hc, sk):
    """devuelve True si dibujó el pelo (y el estilo normal no debe dibujarse)."""
    h = CS.get('hair2')
    if not h: return False
    if h in ('bald', 'buzz'):
        rows = np.arange(P.a.shape[0])[:, None]
        cap = P.mask(lambda d: d.ellipse([cx - 9, 1, cx + 9, 21], fill=255)) & (rows < 11)
        olm = P.mask(lambda d: d.ellipse([cx - 10, 0, cx + 10, 22], fill=255)) & (rows < 11) & ~cap
        P.a[olm] = (*shade(sk, .5), 255); P.a[cap] = (*sk, 255)
        if h == 'buzz': dither_cap(P, cap & (rows < 9), hc['b'], shade(sk, .9), .3)
        else: P.rect(cx - 5, 3, cx - 3, 3, shade(sk, 1.12)); P.px(cx - 6, 4, shade(sk, 1.12))
        sm = P.mask(lambda d: d.polygon([(cx + 4, 2), (cx + 9, 7), (cx + 9, 11), (cx + 6, 9)], fill=255)) & cap
        P.a[sm] = (*shade(sk if h == 'bald' else hc['b'], .86), 255)
    elif h == 'pompadour':
        P.add(lambda d: d.polygon([(cx - 10, 16), (cx - 10, 7), (cx - 6, 2), (cx, 0), (cx + 8, 0), (cx + 13, 3), (cx + 11, 7), (cx + 6, 8), (cx + 9, 11), (cx + 10, 16), (cx + 7, 10), (cx + 1, 9), (cx - 5, 10), (cx - 8, 12)], fill=255), hc['b'], edge_k=.45)
        P.line([(cx - 4, 2), (cx + 7, 1)], hc['l']); P.line([(cx - 2, 4), (cx + 9, 3)], hc['l'])
        P.rect(cx - 10, 12, cx - 9, 19, hc['d']); P.rect(cx + 9, 12, cx + 10, 19, hc['d'])          # patillas
    elif h == 'volume':
        P.add(lambda d: d.polygon([(cx - 11, 22), (cx - 12, 8), (cx - 6, 1), (cx + 6, 1), (cx + 12, 8), (cx + 11, 22), (cx + 9, 12), (cx + 4, 9), (cx - 1, 11), (cx - 5, 8), (cx - 9, 12)], fill=255), hc['b'], edge_k=.45)
        for x0 in (cx - 9, cx - 3, cx + 3): P.line([(x0, 3), (x0 + 3, 8)], hc['l'])
    elif h == 'afro':
        P.add(lambda d: d.polygon([(cx - 9, 12), (cx - 9, 6), (cx + 9, 6), (cx + 9, 12), (cx + 6, 9), (cx - 6, 9)], fill=255), hc['b'], edge_k=.45)
        for k in range(10): P.px(cx - 12 + (k * 5) % 24, 1 + (k * 7) % 14, hc['l'])
    elif h == 'wild':
        P.add(lambda d: d.polygon([(cx - 9, 10), (cx - 9, 5), (cx - 4, 2), (cx + 4, 2), (cx + 9, 5), (cx + 9, 10), (cx + 5, 7), (cx - 5, 7)], fill=255), hc['b'], edge_k=.45)
        P.line([(cx - 13, 6), (cx - 9, 9)], hc['l']); P.line([(cx + 9, 9), (cx + 14, 5)], hc['l'])
    elif h == 'bun':
        P.add(lambda d: d.polygon([(cx - 9, 14), (cx - 9, 6), (cx - 4, 2), (cx + 4, 2), (cx + 9, 6), (cx + 9, 14), (cx + 6, 8), (cx + 1, 6), (cx, 8), (cx - 1, 6), (cx - 6, 8)], fill=255), hc['b'], edge_k=.45)
        for fx, col in ((cx - 7, (230, 60, 80)), (cx - 3, (250, 190, 60)), (cx + 2, (230, 60, 80))): P.add(lambda d, fx=fx: d.ellipse([fx, -1, fx + 4, 3], fill=255), col, edge_k=.5)
    return True


def face_b(P, CS, cx, hc, sk):
    if CS.get('brows') == 'thick': P.rect(cx - 7, 11, cx - 3, 11, hc['b']); P.rect(cx + 3, 11, cx + 7, 11, hc['b'])
    if CS.get('raise'): P.rect(cx + 3, 12, cx + 6, 12, sk); P.rect(cx + 3, 10, cx + 6, 10, hc['dd'])          # ceja levantada
    if CS.get('earring'): P.px(cx - 10, 20, (250, 210, 70))
    if CS.get('age'): P.px(cx - 4, 22, shade(sk, .78)); P.px(cx + 5, 22, shade(sk, .78))
    if CS.get('chin'): P.rect(cx - 4, 27, cx + 4, 27, shade(sk, .8))
    if CS.get('smirk'): P.px(cx + 2, 22, (182, 78, 90))
    if CS.get('nose'): P.px(cx - 2, 20, shade(sk, .72)); P.px(cx + 2, 20, shade(sk, .72))
    if CS.get('unibrow'): P.rect(cx - 6, 12, cx + 6, 12, hc['dd']); P.rect(cx - 6, 11, cx + 6, 11, hc['dd'])
    if CS.get('mustache'): P.rect(cx - 3, 22, cx + 3, 22, hc['d']); P.rect(cx - 2, 21, cx + 2, 21, hc['d'])


# ------------------------------------------------------------------ chibi (46x70, cara cx±18, y 13-32)
def back_r(P, CS, cx, HR):
    h = CS.get('hair2')
    if h == 'volume':
        P.add(lambda d: d.ellipse([cx - 25, -4, cx + 25, 44], fill=255), HR['b'], edge_k=.4)
    elif h == 'afro':
        P.add(lambda d: d.ellipse([cx - 23, -3, cx + 23, 30], fill=255), HR['b'], edge_k=.4)
    elif h == 'wild':
        P.add(lambda d: d.polygon([(cx - 16, 6), (cx - 23, 4), (cx - 19, 12), (cx - 25, 17), (cx - 18, 22), (cx - 22, 28), (cx - 15, 28), (cx + 15, 28), (cx + 22, 28), (cx + 18, 22), (cx + 25, 17), (cx + 19, 12), (cx + 23, 4), (cx + 16, 6)], fill=255), HR['b'], edge_k=.4)
    elif h == 'bun':
        P.add(lambda d: d.ellipse([cx - 8, -2, cx + 8, 10], fill=255), HR['b'], edge_k=.4)


def front_r(P, CS, cx, HR, sk):
    h = CS.get('hair2')
    if not h: return False
    if h in ('bald', 'buzz'):
        rows = np.arange(P.a.shape[0])[:, None]
        cap = P.mask(lambda d: d.ellipse([cx - 18, 1, cx + 18, 31], fill=255)) & (rows < 15)
        olm = P.mask(lambda d: d.ellipse([cx - 19, 0, cx + 19, 32], fill=255)) & (rows < 15) & ~cap
        P.a[olm] = (*shade(sk, .5), 255); P.a[cap] = (*sk, 255)
        if h == 'buzz': dither_cap(P, cap & (rows < 12), HR['b'], shade(sk, .9), .3)
        else: P.rect(cx - 10, 4, cx - 5, 4, shade(sk, 1.12)); P.rect(cx - 12, 6, cx - 11, 7, shade(sk, 1.12))
        sm = P.mask(lambda d: d.polygon([(cx + 9, 3), (cx + 18, 10), (cx + 18, 15), (cx + 13, 10)], fill=255)) & cap
        P.a[sm] = (*shade(sk if h == 'bald' else HR['b'], .86), 255)
    elif h == 'pompadour':
        P.add(lambda d: d.polygon([(cx - 19, 22), (cx - 20, 10), (cx - 13, 3), (cx - 3, 0), (cx + 10, 0), (cx + 22, 3), (cx + 20, 9), (cx + 12, 11), (cx + 18, 14), (cx + 19, 22), (cx + 15, 15), (cx + 4, 12), (cx - 6, 13), (cx - 14, 16)], fill=255), HR['b'], edge_k=.45)
        P.line([(cx - 8, 2), (cx + 14, 2)], HR['l']); P.line([(cx - 6, 5), (cx + 16, 5)], HR['l'])
        P.rect(cx - 19, 18, cx - 17, 26, HR['d']); P.rect(cx + 17, 18, cx + 19, 26, HR['d'])
    elif h == 'volume':
        P.add(lambda d: d.polygon([(cx - 20, 30), (cx - 21, 10), (cx - 12, 2), (cx + 12, 2), (cx + 21, 10), (cx + 20, 30), (cx + 17, 18), (cx + 8, 13), (cx, 16), (cx - 8, 13), (cx - 17, 18)], fill=255), HR['b'], edge_k=.45)
        for x0 in (cx - 16, cx - 8, cx, cx + 8): P.line([(x0, 4), (x0 + 4, 11)], HR['l'])
    elif h == 'afro':
        P.add(lambda d: d.polygon([(cx - 18, 18), (cx - 18, 10), (cx + 18, 10), (cx + 18, 18), (cx + 12, 13), (cx - 12, 13)], fill=255), HR['b'], edge_k=.45)
        for k in range(16): P.px(cx - 20 + (k * 7) % 40, 1 + (k * 11) % 22, HR['l'])
    elif h == 'wild':
        P.add(lambda d: d.polygon([(cx - 18, 16), (cx - 18, 8), (cx - 9, 3), (cx + 9, 3), (cx + 18, 8), (cx + 18, 16), (cx + 10, 11), (cx - 10, 11)], fill=255), HR['b'], edge_k=.45)
        for (a, b) in (((cx - 23, 8), (cx - 17, 13)), ((cx + 17, 13), (cx + 24, 8)), ((cx - 4, 3), (cx - 7, -1)), ((cx + 4, 3), (cx + 8, -1))): P.line([a, b], HR['l'])
    elif h == 'bun':
        P.add(lambda d: d.polygon([(cx - 18, 20), (cx - 19, 10), (cx - 10, 3), (cx + 10, 3), (cx + 19, 10), (cx + 18, 20), (cx + 12, 13), (cx + 2, 11), (cx, 14), (cx - 2, 11), (cx - 12, 13)], fill=255), HR['b'], edge_k=.45)
        for fx, col in ((cx - 13, (230, 60, 80)), (cx - 6, (250, 190, 60)), (cx + 2, (230, 60, 80))): P.add(lambda d, fx=fx: d.ellipse([fx, -2, fx + 6, 4], fill=255), col, edge_k=.5)
    return True


def face_r(P, CS, cx, HR, sk):
    if CS.get('brows') == 'thick': P.rect(cx - 12, 15, cx - 5, 15, HR['b']); P.rect(cx + 5, 15, cx + 12, 15, HR['b'])
    if CS.get('raise'): P.rect(cx + 5, 16, cx + 11, 17, sk); P.rect(cx + 5, 13, cx + 11, 14, HR['dd'])
    if CS.get('earring'): P.rect(cx - 19, 26, cx - 18, 27, (250, 210, 70))
    if CS.get('chin'): P.rect(cx - 8, 32, cx + 8, 32, shade(sk, .8))
    if CS.get('smirk'): P.px(cx + 3, 27, (176, 72, 84))
    if CS.get('nose'): P.rect(cx - 3, 24, cx - 2, 24, shade(sk, .72)); P.rect(cx + 2, 24, cx + 3, 24, shade(sk, .72))
    if CS.get('unibrow'): P.rect(cx - 11, 16, cx + 11, 17, HR['dd'])
    if CS.get('mustache'): P.rect(cx - 5, 27, cx + 5, 27, HR['d']); P.rect(cx - 4, 26, cx + 4, 26, HR['d'])


# ------------------------------------------------------------------ retrato (cara cx±19, y 24-69; pelo 0-52)
def back_p(bd, CS, cx, hb, hd):
    h = CS.get('hair2')
    if h == 'volume':
        bd.ellipse([cx - 40, -6, cx + 40, 92], fill=hb); bd.ellipse([cx - 32, 52, cx + 32, 98], fill=hd)
    elif h == 'afro':
        bd.ellipse([cx - 36, -6, cx + 36, 60], fill=hb)
    elif h == 'wild':
        bd.polygon([(cx - 20, 14), (cx - 38, 8), (cx - 30, 26), (cx - 42, 36), (cx - 30, 44), (cx - 38, 58), (cx - 22, 56), (cx + 22, 56), (cx + 38, 58), (cx + 30, 44), (cx + 42, 36), (cx + 30, 26), (cx + 38, 8), (cx + 20, 14)], fill=hb)
    elif h == 'bun':
        bd.ellipse([cx - 14, -6, cx + 14, 18], fill=hb)
    return h in ('volume', 'afro', 'wild', 'bun', 'bald', 'buzz', 'pompadour')


def front_p(d, CS, cx, hb, hd, hl, sk):
    h = CS.get('hair2')
    if not h: return False
    if h in ('bald', 'buzz'):
        col = hb if h == 'buzz' else sk
        d.ellipse([cx - 21, 9, cx + 21, 64], fill=col)                         # cráneo más bajo: no queda en forma de huevo
        d.rectangle([cx - 30, 37, cx + 30, 80], fill=(0, 0, 0, 0))              # solo por encima de las cejas: no tapa la cara
        if h == 'bald':
            d.ellipse([cx - 13, 8, cx - 4, 14], fill=shade(sk, 1.1)); d.polygon([(cx + 10, 8), (cx + 21, 22), (cx + 21, 36), (cx + 14, 18)], fill=shade(sk, .86))
        else:
            for k in range(60): d.point((cx - 18 + (k * 13) % 36, 8 + (k * 7) % 26), fill=shade(hb, 1.25))
            d.polygon([(cx + 12, 10), (cx + 21, 22), (cx + 21, 36), (cx + 14, 20)], fill=hd)
    elif h == 'pompadour':
        d.polygon([(cx - 22, 48), (cx - 23, 26), (cx - 16, 10), (cx - 4, 0), (cx + 12, -2), (cx + 30, 4), (cx + 26, 14), (cx + 14, 20), (cx + 22, 26), (cx + 22, 48), (cx + 18, 32), (cx + 6, 26), (cx - 8, 28), (cx - 16, 34)], fill=hb)
        for k in range(4): d.line([(cx - 10 + k * 2, 4 + k * 3), (cx + 22 - k * 2, 4 + k * 3)], fill=hl)
        d.rectangle([cx - 22, 34, cx - 19, 52], fill=hd); d.rectangle([cx + 19, 34, cx + 22, 52], fill=hd)
    elif h == 'volume':
        d.polygon([(cx - 26, 60), (cx - 28, 24), (cx - 16, 6), (cx + 16, 6), (cx + 28, 24), (cx + 26, 60), (cx + 20, 40), (cx + 10, 30), (cx, 34), (cx - 10, 30), (cx - 20, 40)], fill=hb)
        for x0 in (cx - 20, cx - 10, cx, cx + 10): d.line([(x0, 10), (x0 + 6, 26)], fill=hl)
    elif h == 'afro':
        d.polygon([(cx - 22, 34), (cx - 22, 24), (cx + 22, 24), (cx + 22, 34), (cx + 14, 28), (cx - 14, 28)], fill=hb)
        for k in range(40): d.point((cx - 32 + (k * 13) % 64, 2 + (k * 7) % 40), fill=hl)
    elif h == 'wild':
        d.polygon([(cx - 21, 34), (cx - 21, 20), (cx - 10, 10), (cx + 10, 10), (cx + 21, 20), (cx + 21, 34), (cx + 12, 24), (cx - 12, 24)], fill=hb)
        for a, b in (((cx - 36, 20), (cx - 22, 30)), ((cx + 22, 30), (cx + 38, 20)), ((cx - 6, 10), (cx - 12, 2)), ((cx + 6, 10), (cx + 14, 2))): d.line([a, b], fill=hl)
    elif h == 'bun':
        d.polygon([(cx - 22, 44), (cx - 23, 24), (cx - 12, 8), (cx + 12, 8), (cx + 23, 24), (cx + 22, 44), (cx + 14, 30), (cx + 2, 26), (cx, 30), (cx - 2, 26), (cx - 14, 30)], fill=hb)
        for fx, col in ((cx - 18, (230, 60, 80)), (cx - 8, (250, 190, 60)), (cx + 4, (230, 60, 80))): d.ellipse([fx, -4, fx + 10, 6], fill=col)
    return True


def face_p(d, CS, cx, hd, brow, by, sk=(230, 190, 160), hb=None):
    if CS.get('brows') == 'thick':
        for x0 in (cx - 15, cx + 5): d.rectangle([x0, by - 3, x0 + 10, by - 1], fill=hb or brow)
    if CS.get('raise'):
        d.line([(cx + 6, by - 1), (cx + 14, by)], fill=sk); d.line([(cx + 6, by - 4), (cx + 10, by - 6), (cx + 14, by - 5)], fill=brow)
    if CS.get('earring'): d.ellipse([cx - 22, 54, cx - 18, 58], fill=(250, 210, 70))
    if CS.get('age'):
        lc = shade(sk, .76)
        d.line([(cx - 8, 55), (cx - 10, 62)], fill=lc); d.line([(cx + 8, 55), (cx + 10, 62)], fill=lc)          # surcos nasogenianos
        d.line([(cx - 8, 30), (cx + 6, 30)], fill=lc)                                                         # arruga de la frente
    if CS.get('chin'): d.line([(cx - 9, 70), (cx, 72), (cx + 9, 70)], fill=shade(sk, .76))                 # papada
    if CS.get('smirk'): d.line([(cx + 2, 61), (cx + 4, 60)], fill=(196, 88, 92))
    if CS.get('nose'):                                                                                        # nariz ancha (aletas marcadas)
        nc = shade(sk, .7); d.line([(cx - 6, 54), (cx - 3, 56)], fill=nc); d.line([(cx + 6, 54), (cx + 3, 56)], fill=nc); d.line([(cx - 2, 56), (cx + 2, 56)], fill=shade(sk, .82))
    if CS.get('unibrow'): d.line([(cx - 14, by), (cx + 14, by)], fill=brow); d.line([(cx - 13, by - 1), (cx + 13, by - 1)], fill=brow)
    if CS.get('mustache'): d.polygon([(cx - 9, 59), (cx + 9, 59), (cx + 7, 62), (cx + 2, 61), (cx - 2, 61), (cx - 7, 62)], fill=hd)


def fix_p(final, CS, cx, sk, ol):
    """retrato calvo o rapado: borra la línea de contorno donde el cráneo se junta con la frente (si no, parece un gorro)."""
    if CS.get('hair2') not in ('bald', 'buzz'): return
    a = np.array(final); band = a[36:40, cx - 22:cx + 23]
    m = (np.abs(band[..., :3].astype(int) - np.array(ol)).sum(-1) < 30) & (band[..., 3] > 0)
    band[m, :3] = sk; a[36:40, cx - 22:cx + 23] = band
    final.paste(Image.fromarray(a), (0, 0))
