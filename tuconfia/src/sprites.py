"""Sprites de personaje por escala de plano.
 - overworld(): chibi RPG (muy lejano)      ~ 28x38
 - battle():    cuerpo completo (medio/lejano) ~ 64x104
 Técnica: cada pieza se pinta como máscara con sombreado automático (borde claro arriba-izq, sombra abajo-der)
 y un contorno de color propio, para que lea como pixel-art de sprite de entrenador."""
import numpy as np
from PIL import Image, ImageDraw
from lib import shade

OUT = (30, 22, 40)


class Paint:
    def __init__(s, w, h):
        s.w, s.h = w, h
        s.a = np.zeros((h, w, 4), np.uint8)

    def mask(s, fn):
        im = Image.new('L', (s.w, s.h), 0); d = ImageDraw.Draw(im); fn(d)
        return np.array(im) > 0

    def add(s, fn, base, edge=True, sh=True, hi=True, shade_k=.78, edge_k=.5):
        m = s.mask(fn) if callable(fn) else fn
        base = tuple(base)
        if edge:
            dil = np.zeros_like(m)
            dil[:-1] |= m[1:]; dil[1:] |= m[:-1]; dil[:, :-1] |= m[:, 1:]; dil[:, 1:] |= m[:, :-1]
            e = dil & ~m
            s.a[e] = (*shade(base, edge_k), 255)
        s.a[m] = (*base, 255)
        if sh:
            up = np.zeros_like(m); up[:-2, :-2] = m[2:, 2:]          # objeto desplazado arriba-izq
            low = m & ~up
            s.a[low] = (*shade(base, shade_k), 255)
        if hi:
            dn = np.zeros_like(m); dn[2:, 2:] = m[:-2, :-2]          # desplazado abajo-der
            top = m & ~dn
            s.a[top] = (*shade(base, 1.14), 255)
        return m

    def px(s, x, y, c):
        if 0 <= x < s.w and 0 <= y < s.h: s.a[y, x] = (*c, 255)

    def rect(s, x0, y0, x1, y1, c):
        s.a[max(0, y0):y1 + 1, max(0, x0):x1 + 1] = (*c, 255)

    def line(s, pts, c):
        im = Image.fromarray(s.a); d = ImageDraw.Draw(im); d.line(pts, fill=(*c, 255)); s.a[:] = np.array(im)

    def final(s, col=OUT):
        al = s.a[..., 3] > 0
        p = np.pad(al, 1)
        dil = np.zeros_like(p)
        dil[:-1] |= p[1:]; dil[1:] |= p[:-1]; dil[:, :-1] |= p[:, 1:]; dil[:, 1:] |= p[:, :-1]
        edge = dil & ~p
        out = np.pad(s.a, ((1, 1), (1, 1), (0, 0)))
        out[edge] = (*col, 255)
        return Image.fromarray(out, 'RGBA')


# ------------------------------------------------------------------ paletas
SKIN = {'king': (250, 212, 178), 'tab': (254, 220, 192), 'you': (244, 200, 164)}
HAIR = {'king': (46, 44, 66), 'tab': (150, 88, 54), 'you': (62, 74, 138)}
BLUSH = (246, 160, 156)


def thick(d, pts, w, fill):
    d.line(pts, fill=fill, width=w)
    r = w // 2
    for x, y in (pts[0], pts[-1]):
        d.ellipse([x - r, y - r, x + r, y + r], fill=fill)
    for x, y in pts[1:-1]:
        d.ellipse([x - r, y - r, x + r, y + r], fill=fill)


# ------------------------------------------------------------------ SPRITE DE BATALLA (cuerpo completo)
def battle(who='king', pose='hold', outfit=None, W=72, H=112):
    P = Paint(W, H)
    cx = W // 2
    sk = SKIN[who]; hr = HAIR[who]
    outfit = outfit or {'king': 'plaid', 'tab': 'cardigan', 'you': 'hoodie'}[who]
    if outfit == 'teacher': top, top2, pants, shoes = (232, 228, 214), None, (118, 96, 74), (74, 52, 42)
    elif outfit == 'plaid': top, top2, pants, shoes = (204, 70, 62), (150, 42, 46), (64, 98, 164), (96, 62, 44)
    elif outfit == 'cardigan': top, top2, pants, shoes = (230, 176, 74), (190, 134, 48), (78, 108, 150), (110, 66, 52)
    elif outfit == 'uniform': top, top2, pants, shoes = (246, 124, 164), (210, 86, 128), (250, 250, 252), (200, 200, 208)
    else: top, top2, pants, shoes = (80, 96, 206), (54, 66, 152), (46, 52, 96), (244, 244, 250)
    yb = 106            # suela
    # ---- pelo trasero (Tabitha)
    if who == 'tab':
        P.add(lambda d: d.polygon([(cx - 14, 14), (cx - 17, 52), (cx - 10, 60), (cx + 10, 60), (cx + 17, 52), (cx + 14, 14)], fill=255), hr)
    # ---- brazo trasero (izquierdo del dibujo)
    arm_b = lambda d: thick(d, [(cx - 16, 36), (cx - 20, 54), (cx - 15, 70)], 8, 255)
    if pose in ('hold', 'toss', 'hold_up'):
        P.add(arm_b, top)
        P.add(lambda d: d.ellipse([cx - 19, 68, cx - 11, 76], fill=255), sk)
    else:
        P.add(arm_b, top); P.add(lambda d: d.ellipse([cx - 19, 68, cx - 11, 76], fill=255), sk)
    # ---- piernas
    sp_ = 2 if pose != 'toss' else 5
    P.add(lambda d: d.polygon([(cx - 10, 62), (cx - 1, 62), (cx - 2, 98), (cx - 11 - sp_ // 2, 98)], fill=255), pants)
    P.add(lambda d: d.polygon([(cx + 1, 62), (cx + 10, 62), (cx + 11 + sp_ // 2, 98), (cx + 2, 98)], fill=255), pants)
    # costura
    P.line([(cx - 5, 66), (cx - 6, 96)], shade(pants, 1.2)) if outfit not in ('uniform',) else None
    # zapatos
    P.add(lambda d: d.polygon([(cx - 12 - sp_ // 2, 97), (cx - 1, 97), (cx, 105), (cx - 16 - sp_ // 2, 105), (cx - 16 - sp_ // 2, 101)], fill=255), shoes)
    P.add(lambda d: d.polygon([(cx + 2, 97), (cx + 12 + sp_ // 2, 97), (cx + 16 + sp_ // 2, 101), (cx + 16 + sp_ // 2, 105), (cx + 1, 105)], fill=255), shoes)
    P.rect(cx - 15 - sp_ // 2, 104, cx - 1, 104, shade(shoes, .55)); P.rect(cx + 2, 104, cx + 15 + sp_ // 2, 104, shade(shoes, .55))
    # ---- torso
    if who == 'tab' and outfit != 'uniform':
        torso = lambda d: d.polygon([(cx - 14, 31), (cx + 14, 31), (cx + 13, 66), (cx - 13, 66)], fill=255)
    else:
        torso = lambda d: d.polygon([(cx - 14, 31), (cx + 14, 31), (cx + 12, 66), (cx - 12, 66)], fill=255)
    P.add(torso, top)
    if outfit == 'plaid':
        for y in range(36, 66, 6): P.rect(cx - 13, y, cx + 12, y, top2)
        for x in range(cx - 10, cx + 12, 7): P.rect(x, 31, x, 65, top2)
        P.add(lambda d: d.polygon([(cx - 4, 31), (cx + 4, 31), (cx + 3, 66), (cx - 3, 66)], fill=255), (250, 248, 244), edge=True, edge_k=.7)  # camiseta
        P.line([(cx - 10, 31), (cx - 3, 40)], (250, 248, 244)); P.line([(cx + 10, 31), (cx + 3, 40)], top)
    elif outfit == 'teacher':
        P.add(lambda d: d.polygon([(cx - 4, 31), (cx + 4, 31), (cx + 2, 56), (cx, 60), (cx - 2, 56)], fill=255), (52, 90, 164))
        P.line([(cx - 10, 31), (cx, 38), (cx + 10, 31)], (250, 250, 248))
    elif outfit == 'cardigan':
        P.add(lambda d: d.polygon([(cx - 6, 31), (cx + 6, 31), (cx, 48)], fill=255), (252, 242, 224), sh=False)
        P.line([(cx - 8, 31), (cx, 48), (cx, 66)], top2); P.line([(cx + 8, 31), (cx, 48)], top2)
        for y in (54, 60): P.px(cx + 2, y, (124, 82, 34))
    elif outfit == 'uniform':
        P.add(lambda d: d.polygon([(cx - 8, 31), (cx + 8, 31), (cx, 40)], fill=255), (255, 255, 255), sh=False)
        P.add(lambda d: d.rectangle([cx + 4, 46, cx + 10, 50], fill=255), (255, 255, 255), sh=False)
        P.add(lambda d: d.polygon([(cx - 13, 56), (cx + 13, 56), (cx + 13, 66), (cx - 13, 66)], fill=255), (255, 176, 112))  # delantal
    else:  # hoodie
        P.line([(cx - 4, 36), (cx - 5, 50)], (246, 246, 252)); P.line([(cx + 4, 36), (cx + 5, 48)], (246, 246, 252))
        P.add(lambda d: d.polygon([(cx - 9, 54), (cx + 9, 54), (cx + 11, 64), (cx - 11, 64)], fill=255), top2, edge_k=.7)
    # ---- cuello
    P.add(lambda d: d.rectangle([cx - 4, 24, cx + 4, 32], fill=255), sk, edge=False)
    P.add(lambda d: d.rectangle([cx - 4, 24, cx + 4, 28], fill=255), shade(sk, .8), edge=False, sh=False, hi=False)
    if outfit == 'hoodie':   # auriculares al cuello
        P.add(lambda d: d.arc([cx - 13, 18, cx + 13, 44], 10, 170, fill=255, width=3), (40, 40, 54), sh=False, hi=False)
        P.add(lambda d: d.ellipse([cx - 17, 28, cx - 10, 38], fill=255), (52, 52, 70)); P.add(lambda d: d.ellipse([cx + 10, 28, cx + 17, 38], fill=255), (52, 52, 70))
        P.rect(cx - 15, 31, cx - 12, 35, (255, 168, 62)); P.rect(cx + 12, 31, cx + 15, 35, (255, 168, 62))
    # ---- brazo delantero
    if pose in ('hold', 'toss', 'hold_up'):
        if pose == 'toss':
            pts = [(cx + 16, 36), (cx + 24, 24), (cx + 22, 10)]
        elif pose == 'hold_up':
            pts = [(cx + 16, 36), (cx + 26, 40), (cx + 20, 24)]
        else:
            pts = [(cx + 16, 36), (cx + 23, 52), (cx + 14, 56)]
        P.add(lambda d: thick(d, pts, 8, 255), top)
        hx, hy = pts[-1]
        P.add(lambda d: d.ellipse([hx - 4, hy - 4, hx + 4, hy + 4], fill=255), sk)
    else:
        P.add(lambda d: thick(d, [(cx + 16, 36), (cx + 20, 54), (cx + 16, 70)], 8, 255), top)
        P.add(lambda d: d.ellipse([cx + 12, 68, cx + 20, 76], fill=255), sk)
    # ---- cabeza
    face = lambda d: d.polygon([(cx - 12, 8), (cx + 12, 8), (cx + 13, 20), (cx + 10, 27), (cx + 5, 31), (cx, 32), (cx - 5, 31), (cx - 10, 27), (cx - 13, 20)], fill=255)
    P.add(face, sk, sh=False, hi=False)
    sh_m = P.mask(lambda d: d.polygon([(cx + 7, 12), (cx + 13, 20), (cx + 10, 27), (cx + 5, 31), (cx + 4, 29), (cx + 8, 22)], fill=255))
    P.a[sh_m & (P.a[..., 3] > 0)] = (*shade(sk, .86), 255)
    for ex in (cx - 15, cx + 12): P.add(lambda d, ex=ex: d.ellipse([ex, 17, ex + 4, 24], fill=255), sk, sh=False, hi=False)
    # ojos estilo sprite: 2x3 oscuros con brillo
    for ex in (cx - 8, cx + 4):
        P.rect(ex, 18, ex + 3, 22, (255, 255, 255))
        P.rect(ex + 1, 18, ex + 3, 22, shade(HAIR[who] if who != 'king' else (58, 96, 168), 1.0) if who != 'king' else (58, 96, 168))
        P.rect(ex + 2, 19, ex + 3, 21, (26, 20, 34)); P.px(ex + 1, 18, (255, 255, 255))
        P.rect(ex, 16, ex + 3, 16, shade(hr, .7))
    if who != 'king': pass
    P.px(cx + 1, 24, shade(sk, .7)); P.rect(cx - 2, 28, cx + 2, 28, (196, 90, 94))
    if who != 'king':
        for bx in (cx - 10, cx + 7): P.rect(bx, 25, bx + 2, 25, BLUSH)
    if who == 'king':   # gafas
        for ex in (cx - 10, cx + 3): P.add(lambda d, ex=ex: d.rectangle([ex, 16, ex + 6, 22], outline=255, width=1), (36, 32, 50), edge=False, sh=False, hi=False)
        P.rect(cx - 3, 18, cx + 2, 18, (36, 32, 50))
        P.px(cx - 8, 21, (210, 230, 255)); P.px(cx + 5, 21, (210, 230, 255))
    # ---- pelo
    if who == 'king':
        P.add(lambda d: d.polygon([(cx - 14, 22), (cx - 15, 10), (cx - 8, 2), (cx - 1, 0), (cx + 8, 2), (cx + 14, 9), (cx + 15, 22), (cx + 12, 12), (cx + 6, 15), (cx + 2, 9), (cx - 3, 15), (cx - 7, 10), (cx - 12, 15)], fill=255), hr, edge_k=.55)
        P.add(lambda d: d.polygon([(cx - 6, 3), (cx - 2, -3 + 3), (cx + 1, 3)], fill=255), hr, edge=False)
        P.add(lambda d: d.polygon([(cx + 4, 2), (cx + 10, -2 + 3), (cx + 11, 6)], fill=255), hr, edge=False)
    elif who == 'tab':
        P.add(lambda d: d.polygon([(cx - 15, 40), (cx - 16, 12), (cx - 8, 3), (cx + 3, 1), (cx + 12, 5), (cx + 16, 14), (cx + 15, 40), (cx + 13, 24), (cx + 11, 14), (cx + 6, 11), (cx + 2, 16), (cx - 4, 10), (cx - 10, 14), (cx - 13, 24)], fill=255), hr, edge_k=.55)
        if outfit == 'uniform':
            P.add(lambda d: d.polygon([(cx - 14, 14), (cx - 11, 4), (cx, 0), (cx + 11, 4), (cx + 14, 14)], fill=255), (246, 124, 164))
            P.add(lambda d: d.polygon([(cx - 16, 14), (cx + 18, 14), (cx + 21, 18), (cx - 14, 18)], fill=255), (206, 82, 124))
    else:
        P.add(lambda d: d.polygon([(cx - 15, 24), (cx - 17, 10), (cx - 9, 2), (cx, 0), (cx + 9, 2), (cx + 15, 9), (cx + 15, 24), (cx + 12, 14), (cx + 7, 18), (cx + 3, 10), (cx - 2, 17), (cx - 6, 10), (cx - 12, 16)], fill=255), hr, edge_k=.55)
        P.add(lambda d: d.polygon([(cx - 2, 3), (cx + 2, -1 + 2), (cx + 5, 3)], fill=255), hr, edge=False)
    # ---- objeto en mano
    if pose == 'hold':
        hx, hy = cx + 14, 56
        P.add(lambda d: d.polygon([(hx - 5, hy - 12), (hx + 6, hy - 11), (hx + 5, hy + 1), (hx - 6, hy)], fill=255), (250, 248, 238), edge_k=.6)
        for i in range(3): P.rect(hx - 3, hy - 9 + i * 3, hx + 3, hy - 9 + i * 3, (130, 132, 150))
        P.add(lambda d: d.ellipse([hx - 4, hy - 3, hx + 4, hy + 4], fill=255), sk)
    if pose == 'toss':
        P.add(lambda d: d.ellipse([cx + 18, 0, cx + 28, 10], fill=255), (246, 244, 236))
    return P.final()


# ------------------------------------------------------------------ SPRITE RPG (chibi, planos muy lejanos)
def overworld(who='king', outfit=None, step=0, W=30, H=40):
    P = Paint(W, H)
    cx = W // 2
    sk = SKIN[who]; hr = HAIR[who]
    outfit = outfit or {'king': 'plaid', 'tab': 'cardigan', 'you': 'hoodie'}[who]
    top, top2, pants, shoes = {'plaid': ((204, 70, 62), (150, 42, 46), (64, 98, 164), (96, 62, 44)), 'teacher': ((232, 228, 214), None, (118, 96, 74), (74, 52, 42)),
                               'cardigan': ((230, 176, 74), (190, 134, 48), (78, 108, 150), (110, 66, 52)), 'uniform': ((246, 124, 164), (210, 86, 128), (250, 250, 252), (200, 200, 208)),
                               'hoodie': ((80, 96, 206), (54, 66, 152), (46, 52, 96), (244, 244, 250))}[outfit]
    # pelo trasero
    if who == 'tab': P.add(lambda d: d.rectangle([cx - 8, 8, cx + 8, 26], fill=255), hr, sh=False, edge=False)
    # piernas
    lo = step
    P.add(lambda d: d.rectangle([cx - 5, 28, cx - 1, 35 - lo], fill=255), pants, edge=False)
    P.add(lambda d: d.rectangle([cx + 1, 28, cx + 5, 35 + lo - 0], fill=255), pants, edge=False)
    P.add(lambda d: d.rectangle([cx - 6, 34 - lo, cx - 1, 36 - lo], fill=255), shoes, edge=False, sh=False)
    P.add(lambda d: d.rectangle([cx + 1, 34 + lo, cx + 6, 36 + lo], fill=255), shoes, edge=False, sh=False)
    # brazos
    P.add(lambda d: d.rectangle([cx - 8, 21, cx - 6, 28], fill=255), top, edge=False)
    P.add(lambda d: d.rectangle([cx + 6, 21, cx + 8, 28], fill=255), top, edge=False)
    P.rect(cx - 8, 28, cx - 6, 29, sk); P.rect(cx + 6, 28, cx + 8, 29, sk)
    # torso
    P.add(lambda d: d.rectangle([cx - 6, 20, cx + 6, 29], fill=255), top, edge=False)
    if outfit == 'plaid':
        for y in (22, 25, 28): P.rect(cx - 6, y, cx + 6, y, top2)
        P.rect(cx - 1, 20, cx + 1, 29, (250, 248, 244))
    if outfit == 'hoodie': P.rect(cx - 1, 22, cx - 1, 26, (246, 246, 252)); P.rect(cx + 2, 22, cx + 2, 26, (246, 246, 252)); P.rect(cx - 5, 18, cx + 5, 19, (40, 40, 54))
    if outfit == 'uniform': P.rect(cx - 6, 26, cx + 6, 29, (255, 176, 112))
    if outfit == 'cardigan': P.rect(cx - 1, 20, cx + 1, 24, (252, 242, 224))
    # cabeza grande
    P.add(lambda d: d.rounded_rectangle([cx - 9, 4, cx + 9, 21], radius=5, fill=255), sk, sh=False, hi=False, edge=False)
    P.add(lambda d: d.rectangle([cx + 5, 10, cx + 9, 20], fill=255), shade(sk, .88), edge=False, sh=False, hi=False)
    for ex in (cx - 6, cx + 3):
        P.rect(ex, 13, ex + 2, 16, (255, 255, 255))
        P.rect(ex + 1, 13, ex + 2, 16, (26, 20, 34) if who != 'king' else (58, 96, 168))
        P.rect(ex + 1, 14, ex + 2, 15, (26, 20, 34)); P.px(ex + 1, 13, (255, 255, 255))
    if who != 'king':
        P.rect(cx - 8, 17, cx - 6, 17, BLUSH); P.rect(cx + 6, 17, cx + 8, 17, BLUSH)
    P.rect(cx - 1, 19, cx + 1, 19, (196, 90, 94))
    if who == 'king':
        for ex in (cx - 7, cx + 2): P.rect(ex, 12, ex + 4, 12, (36, 32, 50)); P.rect(ex, 17, ex + 4, 17, (36, 32, 50)); P.rect(ex, 12, ex, 17, (36, 32, 50)); P.rect(ex + 4, 12, ex + 4, 17, (36, 32, 50))
    # pelo
    if who == 'king':
        P.add(lambda d: d.polygon([(cx - 10, 13), (cx - 10, 5), (cx - 5, 1), (cx + 1, 0), (cx + 6, 2), (cx + 10, 6), (cx + 10, 13), (cx + 7, 8), (cx + 3, 10), (cx, 6), (cx - 4, 10), (cx - 7, 7)], fill=255), hr, edge=False)
        P.add(lambda d: d.polygon([(cx - 4, 2), (cx, -2 + 2), (cx + 2, 2)], fill=255), hr, edge=False)
    elif who == 'tab':
        P.add(lambda d: d.polygon([(cx - 10, 22), (cx - 10, 6), (cx - 4, 1), (cx + 4, 1), (cx + 10, 6), (cx + 10, 22), (cx + 8, 12), (cx + 4, 8), (cx, 11), (cx - 5, 8), (cx - 8, 12)], fill=255), hr, edge=False)
        if outfit == 'uniform':
            P.add(lambda d: d.polygon([(cx - 9, 8), (cx - 6, 2), (cx + 6, 2), (cx + 9, 8)], fill=255), (246, 124, 164), edge=False)
            P.rect(cx - 10, 8, cx + 11, 9, (206, 82, 124))
    else:
        P.add(lambda d: d.polygon([(cx - 10, 14), (cx - 11, 6), (cx - 5, 1), (cx + 2, 0), (cx + 8, 3), (cx + 10, 7), (cx + 10, 14), (cx + 7, 8), (cx + 3, 11), (cx, 6), (cx - 4, 10), (cx - 8, 8)], fill=255), hr, edge=False)
        P.add(lambda d: d.polygon([(cx - 1, 2), (cx + 3, -1 + 2), (cx + 4, 3)], fill=255), hr, edge=False)
    return P.final()


# ------------------------------------------------------------------ CHIBI RPG v2 (estilo del sprite de referencia: cabeza grande, 4 tonos, accesorios)
def rpg(who='king', outfit=None, step=0, W=46, H=70):
    P = Paint(W, H)
    cx = W // 2
    from cast import resolve
    CS = resolve(who); style = CS['style']
    sk = CS['skin']
    outfit = outfit or CS['outfit']
    skd = shade(sk, .84); skdd = shade(sk, .68); sk_l = shade(sk, 1.06)
    NAVY = (30, 34, 78)
    HR = CS['hair']
    cl = {'plaid': dict(b=(214, 74, 66), d=(158, 44, 52), l=(246, 124, 108), pants=(70, 106, 176), boots=(110, 70, 52)),
          'teacher': dict(b=(236, 232, 218), d=(190, 186, 176), l=(255, 255, 250), pants=(128, 104, 80), boots=(84, 58, 46)),
          'cardigan': dict(b=(236, 182, 76), d=(188, 134, 48), l=(255, 220, 124), pants=(84, 112, 160), boots=(116, 70, 54)),
          'uniform': dict(b=(248, 126, 166), d=(208, 86, 128), l=(255, 176, 204), pants=(252, 252, 254), boots=(206, 206, 216)),
          'tee_blue': dict(b=(70, 130, 220), d=(40, 86, 170), l=(130, 180, 250), pants=(60, 70, 100), boots=(60, 50, 56)),
          'tee_green': dict(b=(80, 190, 110), d=(40, 140, 76), l=(150, 230, 170), pants=(70, 76, 110), boots=(100, 70, 50)),
          'tee_yellow': dict(b=(250, 210, 70), d=(206, 160, 30), l=(255, 240, 150), pants=(76, 86, 130), boots=(70, 56, 56)),
          'tee_red': dict(b=(230, 80, 70), d=(170, 44, 48), l=(255, 140, 120), pants=(60, 74, 110), boots=(90, 66, 52)),
          'blazer': dict(b=(52, 70, 120), d=(34, 46, 86), l=(96, 120, 180), pants=(70, 70, 82), boots=(60, 44, 40)),
          'polo': dict(b=(210, 150, 80), d=(160, 104, 50), l=(250, 200, 130), pants=(80, 84, 100), boots=(70, 52, 44)),
          'coat': dict(b=(246, 248, 252), d=(196, 206, 224), l=(255, 255, 255), pants=(70, 90, 130), boots=(60, 50, 50)),
          'argentina': dict(b=(150, 206, 246), d=(100, 160, 214), l=(230, 246, 255), pants=(30, 30, 40), boots=(40, 40, 52)),
          'hoodie': dict(b=(86, 102, 212), d=(56, 68, 156), l=(134, 154, 244), pants=(52, 58, 106), boots=(248, 248, 252))}[outfit]
    cb, cd, clt = cl['b'], cl['d'], cl['l']
    pants, boots = cl['pants'], cl['boots']
    mint = (126, 232, 196)
    lo = step
    # ---------- pelo trasero (largo en Tabitha, mechón lateral en los demás)
    if style == 'tab':
        P.add(lambda d: d.polygon([(2, 14), (3, 6), (12, 1), (32, 1), (41, 6), (42, 14), (43, 40), (38, 46), (33, 44), (33, 30), (11, 30), (11, 44), (6, 46), (1, 40)], fill=255), HR['d'], edge_k=.4)
    elif style == 'you':
        P.add(lambda d: d.polygon([(3, 18), (4, 8), (12, 3), (32, 3), (40, 8), (41, 18), (40, 30), (34, 30), (11, 30), (5, 30)], fill=255), HR['dd'], edge_k=.4)
    # ---------- piernas
    P.add(lambda d: d.rectangle([cx - 10, 50, cx - 1, 61 - lo], fill=255), pants, edge_k=.45)
    P.add(lambda d: d.rectangle([cx + 1, 50, cx + 10, 61 + lo], fill=255), pants, edge_k=.45)
    # botas con puño y suela
    for sx, dy in ((-1, -lo), (1, lo)):
        x0 = cx - 11 if sx < 0 else cx + 1
        y0 = 60 + dy
        P.add(lambda d, x0=x0, y0=y0: d.rectangle([x0, y0, x0 + 10, y0 + 6], fill=255), boots, edge_k=.4)
        if outfit != 'hoodie': P.rect(x0 + 1, y0, x0 + 9, y0 + 1, mint if outfit in ('plaid', 'cardigan') else shade(boots, 1.2))
        P.rect(x0, y0 + 6, x0 + 10, y0 + 6, (238, 228, 206) if outfit != 'hoodie' else (210, 210, 224))
    # ---------- torso y brazos
    P.add(lambda d: d.rounded_rectangle([cx - 12, 34, cx + 12, 52], radius=3, fill=255), cb, edge_k=.42)
    P.add(lambda d: d.rounded_rectangle([cx - 17, 35, cx - 11, 47], radius=2, fill=255), cb, edge_k=.42)
    P.add(lambda d: d.rounded_rectangle([cx + 11, 35, cx + 17, 47], radius=2, fill=255), cb, edge_k=.42)
    P.rect(cx - 17, 45, cx - 11, 46, mint if outfit in ('plaid', 'cardigan', 'uniform') else cd); P.rect(cx + 11, 45, cx + 17, 46, mint if outfit in ('plaid', 'cardigan', 'uniform') else cd)
    P.add(lambda d: d.ellipse([cx - 18, 46, cx - 10, 53], fill=255), sk, edge_k=.45)
    P.add(lambda d: d.ellipse([cx + 10, 46, cx + 18, 53], fill=255), sk, edge_k=.45)
    P.rect(cx - 14, 50, cx - 12, 51, skdd); P.rect(cx + 14, 50, cx + 16, 51, skdd)
    # detalles de la ropa
    if outfit == 'plaid':
        for y in (38, 42, 46, 50): P.rect(cx - 11, y, cx + 11, y, cd)
        for x in (cx - 10, cx - 4, cx + 6, cx + 11): P.rect(x, 36, x, 51, cd)
        P.add(lambda d: d.polygon([(cx - 4, 34), (cx + 4, 34), (cx + 3, 52), (cx - 3, 52)], fill=255), (250, 248, 244), edge_k=.6)   # camiseta
        P.rect(cx - 12, 51, cx + 12, 52, (74, 52, 44)); P.rect(cx - 1, 51, cx + 1, 52, (240, 200, 90))   # cinturón
        P.rect(cx + 6, 40, cx + 11, 44, (250, 248, 238)); P.rect(cx + 7, 41, cx + 10, 41, (140, 140, 156)); P.rect(cx + 7, 43, cx + 10, 43, (140, 140, 156))  # hojas en el bolsillo
    elif outfit == 'teacher':
        P.add(lambda d: d.polygon([(cx - 2, 36), (cx + 2, 36), (cx + 3, 48), (cx, 51), (cx - 3, 48)], fill=255), (56, 94, 170), edge_k=.5)
        P.line([(cx - 8, 34), (cx, 40), (cx + 8, 34)], (252, 252, 250)); P.rect(cx - 12, 51, cx + 12, 52, (74, 52, 44))
    elif outfit == 'cardigan':
        P.add(lambda d: d.polygon([(cx - 7, 34), (cx + 7, 34), (cx, 50)], fill=255), (252, 242, 226), sh=False, edge_k=.55)
        P.line([(cx - 8, 34), (cx, 51)], cd); P.line([(cx + 8, 34), (cx, 51)], cd)
        for y in (44, 48): P.rect(cx + 2, y, cx + 3, y, (124, 82, 34))
        P.rect(cx - 12, 51, cx + 12, 52, cd)
    elif outfit == 'uniform':
        P.add(lambda d: d.polygon([(cx - 8, 34), (cx + 8, 34), (cx, 42)], fill=255), (255, 255, 255), sh=False, edge_k=.6)
        P.add(lambda d: d.rectangle([cx - 12, 44, cx + 12, 52], fill=255), (255, 178, 114), edge_k=.5)
        P.rect(cx + 5, 38, cx + 10, 41, (255, 255, 255)); P.rect(cx + 6, 40, cx + 9, 40, cd)
    else:  # hoodie
        P.rect(cx - 5, 38, cx - 5, 48, (246, 246, 252)); P.rect(cx + 5, 38, cx + 5, 46, (246, 246, 252))
        P.add(lambda d: d.polygon([(cx - 9, 44), (cx + 9, 44), (cx + 11, 51), (cx - 11, 51)], fill=255), clt, edge_k=.55)
        P.add(lambda d: d.rounded_rectangle([cx - 11, 29, cx + 11, 35], radius=3, fill=255), cd, edge_k=.5)
        P.rect(cx - 12, 51, cx + 12, 52, cd)
    if outfit == 'argentina':
        for x in range(cx - 11, cx + 12, 6): P.rect(x, 36, x + 2, 50, (252, 252, 255))
        P.rect(cx - 12, 51, cx + 12, 52, (30, 30, 40))
    elif outfit == 'blazer':
        P.add(lambda d: d.polygon([(cx - 6, 34), (cx + 6, 34), (cx + 3, 51), (cx - 3, 51)], fill=255), (250, 250, 250), edge_k=.55)
        P.line([(cx - 9, 34), (cx - 3, 46)], cd); P.line([(cx + 9, 34), (cx + 3, 46)], cd)
    elif outfit == 'coat':
        P.rect(cx - 1, 36, cx, 51, cd); P.rect(cx + 5, 40, cx + 9, 43, (190, 214, 240))
    elif outfit == 'polo':
        P.add(lambda d: d.polygon([(cx - 5, 34), (cx + 5, 34), (cx, 41)], fill=255), (250, 240, 220), sh=False, edge_k=.55)
    elif outfit.startswith('tee'):
        P.rect(cx - 12, 44, cx + 12, 44, cd)
    # ---------- bufanda / cuello (grande como en la referencia)
    if style == 'tab':
        P.add(lambda d: d.rounded_rectangle([cx - 14, 31, cx + 14, 39], radius=3, fill=255), (250, 240, 222), edge_k=.5)
        P.add(lambda d: d.rectangle([cx - 14, 37, cx - 7, 48], fill=255), (250, 240, 222), edge_k=.5)
        for y in (33, 36): P.rect(cx - 15, y, cx + 15, y, (226, 206, 176))
        for y in (40, 43, 46): P.rect(cx - 13, y, cx - 8, y, (226, 206, 176))
    elif style == 'you':
        P.add(lambda d: d.arc([cx - 13, 28, cx + 13, 48], 20, 160, fill=255, width=2), (46, 46, 60), sh=False, hi=False, edge_k=.4)
        P.add(lambda d: d.ellipse([cx - 16, 33, cx - 9, 43], fill=255), (60, 60, 80)); P.add(lambda d: d.ellipse([cx + 9, 33, cx + 16, 43], fill=255), (60, 60, 80))
        P.rect(cx - 14, 36, cx - 11, 40, (255, 170, 64)); P.rect(cx + 11, 36, cx + 14, 40, (255, 170, 64))
        P.rect(cx - 14, 36, cx - 13, 37, (255, 218, 140)); P.rect(cx + 11, 36, cx + 12, 37, (255, 218, 140))
    else:
        P.add(lambda d: d.rounded_rectangle([cx - 12, 31, cx + 12, 36], radius=3, fill=255), (250, 248, 244) if outfit == 'plaid' else (252, 252, 250), edge_k=.55)
    # ---------- cabeza
    P.add(lambda d: d.polygon([(cx - 17, 13), (cx + 17, 13), (cx + 18, 21), (cx + 16, 28), (cx + 11, 32), (cx - 11, 32), (cx - 16, 28), (cx - 18, 21)], fill=255), sk, sh=False, hi=False, edge_k=.42)
    m = P.mask(lambda d: d.polygon([(cx + 10, 15), (cx + 17, 16), (cx + 18, 21), (cx + 16, 28), (cx + 11, 32), (cx + 6, 32), (cx + 12, 27), (cx + 13, 21)], fill=255))
    P.a[m & (P.a[..., 3] > 0)] = (*skd, 255)
    m2 = P.mask(lambda d: d.polygon([(cx - 15, 22), (cx - 13, 22), (cx - 12, 29), (cx - 15, 27)], fill=255)); P.a[m2 & (P.a[..., 3] > 0)] = (*sk_l, 255)
    # ojos grandes
    for ex in (cx - 10, cx + 7):
        P.rect(ex, 19, ex + 3, 19, (30, 22, 40))
        P.rect(ex, 20, ex + 2, 24, CS['iris']); P.rect(ex + 3, 20, ex + 3, 23, (255, 255, 255))
        P.rect(ex, 20, ex, 20, (255, 255, 255)); P.rect(ex + 1, 20, ex + 1, 20, (255, 255, 255)); P.rect(ex + 1, 21, ex + 1, 22, tuple(int(v*1.15) for v in CS['iris']))
        P.rect(ex, 25, ex + 2, 25, skd)
    # cejas gruesas
    br = HR['dd']
    P.rect(cx - 11, 16, cx - 6, 17, br); P.rect(cx + 6, 16, cx + 11, 17, br)
    P.rect(cx - 6, 17, cx - 5, 17, br); P.rect(cx + 5, 17, cx + 6, 17, br)
    # nariz, boca, rubor
    P.px(cx + 1, 26, skdd); P.rect(cx - 1, 28, cx + 2, 28, (176, 72, 84)); P.px(cx + 2, 27, (176, 72, 84))
    if style != 'king':
        for bx in (cx - 13, cx + 10): P.rect(bx, 26, bx + 2, 26, (246, 150, 150)); P.rect(bx + 1, 27, bx + 2, 27, (246, 150, 150))
    if CS['glasses']:   # gafas redondas
        for ex in (cx - 12, cx + 5):
            P.rect(ex, 18, ex + 7, 18, (34, 30, 48)); P.rect(ex, 26, ex + 7, 26, (34, 30, 48))
            P.rect(ex, 18, ex, 26, (34, 30, 48)); P.rect(ex + 7, 18, ex + 7, 26, (34, 30, 48))
            P.rect(ex + 1, 25, ex + 2, 25, (210, 232, 255))
        P.rect(cx - 4, 21, cx + 3, 21, (34, 30, 48))
    # ---------- pelo frontal (4 tonos)
    if style == 'short':
        P.add(lambda d: d.polygon([(cx - 19, 24), (cx - 20, 11), (cx - 14, 4), (cx - 6, 1), (cx + 4, 0), (cx + 13, 3), (cx + 19, 9), (cx + 20, 24), (cx + 17, 15), (cx + 10, 11), (cx + 2, 10), (cx - 6, 12), (cx - 13, 15), (cx - 17, 20)], fill=255), HR['b'], edge_k=.45)
        P.line([(cx - 4, 3), (cx - 6, 10)], HR['d'])
    elif style == 'king':
        P.add(lambda d: d.polygon([(cx - 19, 22), (cx - 20, 11), (cx - 14, 4), (cx - 6, 1), (cx + 4, 0), (cx + 13, 3), (cx + 19, 9), (cx + 20, 22), (cx + 16, 15), (cx + 13, 19), (cx + 9, 13), (cx + 4, 19), (cx, 13), (cx - 5, 18), (cx - 9, 13), (cx - 14, 19), (cx - 17, 14)], fill=255), HR['b'], edge_k=.45)
        P.add(lambda d: d.polygon([(cx - 8, 3), (cx - 3, -3 + 3), (cx + 1, 3)], fill=255), HR['b'], edge=False)
        P.add(lambda d: d.polygon([(cx + 5, 2), (cx + 12, -2 + 3), (cx + 13, 8)], fill=255), HR['b'], edge=False)
    elif style == 'tab':
        P.add(lambda d: d.polygon([(cx - 20, 34), (cx - 21, 12), (cx - 14, 4), (cx - 2, 1), (cx + 12, 3), (cx + 20, 10), (cx + 21, 34), (cx + 17, 22), (cx + 15, 17), (cx + 10, 16), (cx + 5, 12), (cx, 17), (cx - 6, 12), (cx - 11, 17), (cx - 16, 16), (cx - 17, 24)], fill=255), HR['b'], edge_k=.45)
    else:
        P.add(lambda d: d.polygon([(cx - 19, 24), (cx - 20, 11), (cx - 12, 3), (cx - 2, 1), (cx + 10, 2), (cx + 18, 8), (cx + 20, 22), (cx + 17, 15), (cx + 13, 20), (cx + 10, 13), (cx + 5, 19), (cx + 1, 12), (cx - 5, 19), (cx - 9, 13), (cx - 14, 20), (cx - 17, 16)], fill=255), HR['b'], edge_k=.45)
        P.add(lambda d: d.polygon([(cx - 2, 3), (cx + 3, -3 + 3), (cx + 6, 3)], fill=255), HR['b'], edge=False)
    # sombra lateral derecha + brillos
    mh = P.mask(lambda d: d.polygon([(cx + 10, 4), (cx + 19, 9), (cx + 20, 22), (cx + 17, 15), (cx + 14, 8)], fill=255))
    P.a[mh & (P.a[..., 3] > 0) & (P.a[..., :3] == HR['b']).all(-1)] = (*HR['d'], 255)
    for (x0, y0, x1, y1) in [(cx - 14, 6, cx - 8, 4), (cx - 6, 4, cx, 3), (cx - 16, 12, cx - 14, 9)]:
        P.line([(x0, y0), (x1, y1)], HR['l'])
    P.line([(cx - 12, 14), (cx - 9, 13)], HR['dd']); P.line([(cx + 2, 14), (cx + 5, 13)], HR['dd'])
    if style == 'tab' and outfit == 'uniform':
        P.add(lambda d: d.polygon([(cx - 19, 14), (cx - 15, 3), (cx, 0), (cx + 15, 3), (cx + 19, 14)], fill=255), cb, edge_k=.45)
        P.add(lambda d: d.polygon([(cx - 21, 14), (cx + 24, 14), (cx + 26, 18), (cx - 19, 18)], fill=255), cd, edge_k=.45)
        P.rect(cx - 8, 5, cx - 2, 5, clt)
    if CS['beard']:
        P.add(lambda d: d.polygon([(cx - 14, 24), (cx - 13, 31), (cx - 6, 34), (cx + 6, 34), (cx + 13, 31), (cx + 14, 24), (cx + 9, 27), (cx + 4, 29), (cx - 4, 29), (cx - 9, 27)], fill=255), HR['d'], edge_k=.5, sh=False)
        P.rect(cx - 3, 28, cx + 3, 28, (176, 72, 84))
    if who == 'king':   # lápiz tras la oreja
        P.rect(cx + 18, 20, cx + 19, 26, (255, 200, 70)); P.rect(cx + 18, 27, cx + 19, 27, (240, 150, 140)); P.px(cx + 18, 19, (60, 50, 60))
    if style == 'tab':    # horquilla
        P.rect(cx - 17, 14, cx - 14, 15, (255, 240, 170)); P.px(cx - 15, 14, (255, 255, 255))
    return P.final()
