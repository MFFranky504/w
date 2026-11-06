"""Personajes detallados (busto) dibujados a resolución nativa de la escena, escalables (sc)."""
from PIL import Image, ImageDraw
from lib import C, shade

PAL = {
    'king': dict(skin='#e4b690', hair='#15121a', hl='#4a4458', iris='#3a6aa8', blush=None),
    'tab': dict(skin='#f0c4a4', hair='#6a3c28', hl='#a8683c', iris='#6a4228', blush='#f0a090'),
    'you': dict(skin='#d8a47c', hair='#1c2036', hl='#5868a8', iris='#3a2a22', blush='#d88a70'),
}


def portrait(who='king', expr='n', look=(0, 0), blink=False, sc=1.0, outfit=None, cap=False):
    p = PAL[who]
    skin, skd, skl = C(p['skin']), shade(p['skin'], .8), shade(p['skin'], 1.07)
    hair, hl = C(p['hair']), C(p['hl'])
    W, H = int(72 * sc) + 2, int(92 * sc) + 2
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    S = lambda v: v * sc
    poly = lambda pts, f: d.polygon([(S(x), S(y)) for x, y in pts], fill=f)
    rect = lambda x0, y0, x1, y1, f: d.rectangle([S(x0), S(y0), S(x1), S(y1)], fill=f)
    line = lambda pts, f, w=1: d.line([(S(x), S(y)) for x, y in pts], fill=f, width=max(1, round(w * sc)))
    ell = lambda x0, y0, x1, y1, f: d.ellipse([S(x0), S(y0), S(x1), S(y1)], fill=f)
    pt = lambda x, y, f: d.rectangle([S(x), S(y), S(x) + max(0, round(sc) - 1), S(y) + max(0, round(sc) - 1)], fill=f)
    cx, h = 36, 92
    outfit = outfit or {'king': 'plaid', 'tab': 'cardigan', 'you': 'hoodie'}[who]

    # ---------- pelo trasero
    if who == 'tab':
        poly([(cx - 24, 24), (cx - 28, h - 22), (cx - 14, h - 17), (cx + 14, h - 17), (cx + 28, h - 22), (cx + 24, 24), (cx + 14, 9), (cx, 4), (cx - 14, 9)], hair)
    if who == 'you':
        poly([(cx - 20, 30), (cx - 19, 12), (cx, 4), (cx + 19, 12), (cx + 20, 30), (cx + 16, 44), (cx - 16, 44)], shade(p['hair'], .8))
    # ---------- ropa
    tp, tp2 = {'plaid': ('#b2443a', '#6a2428'), 'teacher': ('#d8d2c0', '#b8b2a0'), 'cardigan': ('#d6a03c', '#a67a24'),
               'uniform': ('#f06a98', '#c84878'), 'hoodie': ('#4a56c8', '#343e94')}[outfit]
    tp, tp2 = C(tp), C(tp2)
    if outfit == 'hoodie':  # capucha detrás del cuello
        poly([(cx - 20, h - 36), (cx - 12, h - 44), (cx + 12, h - 44), (cx + 20, h - 36), (cx + 22, h - 24), (cx - 22, h - 24)], shade('#343e94', .85))
    poly([(0, h), (4, h - 20), (cx - 14, h - 27), (cx + 14, h - 27), (68, h - 20), (72, h)], tp)
    poly([(cx + 14, h - 27), (68, h - 20), (72, h), (cx + 22, h)], shade(tp, .82))   # sombra lado derecho
    poly([(0, h), (4, h - 20), (9, h - 22), (8, h)], shade(tp, 1.12))
    # cuello
    poly([(cx - 8, h - 40), (cx + 8, h - 40), (cx + 9, h - 27), (cx, h - 21), (cx - 9, h - 27)], skd)
    poly([(cx - 8, h - 40), (cx + 8, h - 40), (cx + 8, h - 33), (cx, h - 29), (cx - 8, h - 33)], shade(p['skin'], .68))  # sombra barbilla
    if outfit == 'plaid':
        for yy in range(h - 25, h, 5): line([(2, yy), (70, yy)], tp2)
        for xx in range(6, 70, 7): line([(xx, h - 24), (xx - 1, h)], tp2)
        poly([(cx - 10, h - 28), (cx, h - 20), (cx + 10, h - 28), (cx + 6, h - 29), (cx, h - 24), (cx - 6, h - 29)], (238, 236, 230))
    elif outfit == 'teacher':
        poly([(cx - 10, h - 28), (cx, h - 17), (cx + 10, h - 28), (cx + 6, h - 29), (cx, h - 25), (cx - 6, h - 29)], (250, 250, 246))
        poly([(cx - 2, h - 25), (cx + 2, h - 25), (cx + 3, h - 6), (cx, h - 3), (cx - 3, h - 6)], (40, 70, 130))
        rect(cx - 2, h - 26, cx + 2, h - 23, (60, 96, 164))
    elif outfit == 'cardigan':
        poly([(cx - 10, h - 28), (cx, h - 16), (cx + 10, h - 28), (cx + 6, h - 29), (cx, h - 23), (cx - 6, h - 29)], (244, 232, 212))
        line([(cx, h - 17), (cx, h)], tp2)
        for yy in (h - 12, h - 6): pt(cx + 2, yy, (92, 60, 24))
        line([(cx - 11, h - 28), (cx - 2, h - 17)], tp2); line([(cx + 11, h - 28), (cx + 2, h - 17)], tp2)
    elif outfit == 'uniform':
        poly([(cx - 11, h - 28), (cx, h - 18), (cx + 11, h - 28), (cx + 7, h - 30), (cx, h - 25), (cx - 7, h - 30)], (252, 252, 252))
        rect(cx + 8, h - 14, cx + 20, h - 9, (252, 252, 252)); line([(cx + 10, h - 12), (cx + 18, h - 12)], tp2)
    elif outfit == 'hoodie':
        poly([(cx - 11, h - 28), (cx, h - 21), (cx + 11, h - 28), (cx + 8, h - 32), (cx, h - 26), (cx - 8, h - 32)], shade('#343e94', .9))
        line([(cx - 5, h - 23), (cx - 6, h - 6)], (240, 240, 250), 1.3); line([(cx + 5, h - 23), (cx + 6, h - 8)], (240, 240, 250), 1.3)
        rect(cx - 8, h - 13, cx + 8, h - 12, shade('#343e94', .9))
        # auriculares al cuello
        line([(cx - 17, h - 31), (cx - 12, h - 24), (cx, h - 21), (cx + 12, h - 24), (cx + 17, h - 31)], (22, 22, 30), 2)
        ell(cx - 22, h - 36, cx - 14, h - 26, (36, 36, 48)); ell(cx + 14, h - 36, cx + 22, h - 26, (36, 36, 48))
        ell(cx - 20, h - 34, cx - 16, h - 28, (255, 160, 50)); ell(cx + 16, h - 34, cx + 20, h - 28, (255, 160, 50))
    # ---------- cara
    face = [(cx - 16, 21), (cx - 13, 14), (cx + 13, 14), (cx + 16, 21), (cx + 17, 40), (cx + 14, 54), (cx + 8, 61), (cx, 64), (cx - 8, 61), (cx - 14, 54), (cx - 17, 40)]
    ell(cx - 20, 35, cx - 14, 46, skin); ell(cx + 14, 35, cx + 20, 46, skd)          # orejas
    ell(cx - 18.5, 38, cx - 16, 43, skd)
    poly(face, skin)
    poly([(cx + 9, 16), (cx + 16, 22), (cx + 17, 40), (cx + 14, 54), (cx + 8, 61), (cx + 5, 61), (cx + 10, 51), (cx + 11, 34), (cx + 10, 22)], skd)
    poly([(cx - 16, 24), (cx - 15, 40), (cx - 13, 50), (cx - 12, 36)], skl)
    if p['blush']:
        ell(cx - 14, 48, cx - 7, 53, shade(p['blush'], 1)); ell(cx + 7, 48, cx + 14, 53, shade(p['blush'], .9))
    # ---------- pelo frontal
    if who == 'king':
        poly([(cx - 20, 42), (cx - 21, 22), (cx - 15, 10), (cx - 7, 4), (cx + 2, 2), (cx + 11, 4), (cx + 18, 11), (cx + 21, 22), (cx + 20, 42), (cx + 17, 32), (cx + 14, 23), (cx + 6, 19), (cx - 2, 21), (cx - 9, 19), (cx - 15, 25), (cx - 18, 33)], hair)
        poly([(cx - 9, 5), (cx - 4, -2), (cx + 1, 4)], hair); poly([(cx + 3, 3), (cx + 9, -1), (cx + 12, 5)], hair)
        for (a, b) in [((-12, 9), (-3, 6)), ((2, 6), (11, 9)), ((-16, 17), (-12, 12))]: line([(cx + a[0], a[1]), (cx + b[0], b[1])], hl)
    elif who == 'tab':
        poly([(cx - 19, 40), (cx - 20, 18), (cx - 11, 9), (cx + 4, 6), (cx + 15, 10), (cx + 20, 20), (cx + 19, 40), (cx + 16, 29), (cx + 9, 22), (cx - 4, 18), (cx - 13, 24), (cx - 17, 32)], hair)
        for (a, b) in [((-12, 11), (2, 8)), ((4, 8), (15, 13)), ((-17, 20), (-14, 14))]: line([(cx + a[0], a[1]), (cx + b[0], b[1])], hl)
        if cap:
            poly([(cx - 19, 22), (cx - 17, 10), (cx, 4), (cx + 17, 10), (cx + 19, 22)], C('#f06a98'))
            poly([(cx - 22, 22), (cx + 24, 22), (cx + 26, 26), (cx - 24, 26)], C('#c84878')); line([(cx - 8, 8), (cx + 6, 6)], (255, 190, 214))
    else:  # you: mechones desordenados con flequillo
        poly([(cx - 20, 40), (cx - 22, 20), (cx - 14, 8), (cx - 3, 2), (cx + 9, 3), (cx + 19, 10), (cx + 22, 22), (cx + 20, 40), (cx + 17, 30), (cx + 13, 22), (cx + 4, 21), (cx - 4, 25), (cx - 11, 29), (cx - 16, 36)], hair)
        poly([(cx - 4, 3), (cx + 2, -3), (cx + 6, 4)], hair)
        poly([(cx - 12, 22), (cx - 2, 20), (cx - 7, 31)], hair)
        for (a, b) in [((-14, 9), (-2, 5)), ((4, 6), (15, 11)), ((-9, 24), (-5, 29))]: line([(cx + a[0], a[1]), (cx + b[0], b[1])], hl)
        # auricular
        pt(cx + 15, 41, (250, 250, 250)); pt(cx + 15, 42, (250, 250, 250))
    # ---------- ojos
    ex, ey = [cx - 8.5, cx + 8.5], 39
    lx, ly = look
    col = C(p['iris'])
    for e in ex:
        if blink:
            line([(e - 5, ey + .5), (e, ey + 1.6), (e + 5, ey + .5)], (50, 30, 34), 1.2)
        else:
            poly([(e - 5.2, ey), (e - 2.4, ey - 3), (e + 2.4, ey - 3), (e + 5.2, ey), (e + 2.4, ey + 2.8), (e - 2.4, ey + 2.8)], (252, 250, 252))
            ell(e - 2.6 + lx, ey - 3 + ly * .5, e + 2.6 + lx, ey + 2.7 + ly * .3, col)
            ell(e - 1.2 + lx, ey - 1.4 + ly * .5, e + 1.2 + lx, ey + 1.1 + ly * .3, (14, 12, 22))
            pt(e + .8 + lx, ey - 2 + ly * .5, (255, 255, 255)); pt(e - 1.4 + lx, ey + .6 + ly * .3, (200, 220, 255))
            line([(e - 5.4, ey - .2), (e - 2.4, ey - 3.2), (e + 2.4, ey - 3.2), (e + 5.4, ey - .2)], (40, 26, 34), 1.2)
            if who != 'king': line([(e + 5.2, ey - .3), (e + 7, ey - 2)], (40, 26, 34), 1)
    # cejas
    bc = hair if who != 'you' else C('#141828')
    by = 31
    if expr in ('sad', 'worry'):
        line([(ex[0] - 6, by + 1.5), (ex[0] + 5, by - 2)], bc, 2); line([(ex[1] - 5, by - 2), (ex[1] + 6, by + 1.5)], bc, 2)
    elif expr == 'wow':
        line([(ex[0] - 5, by - 3), (ex[0] + 5, by - 4)], bc, 2); line([(ex[1] - 5, by - 4), (ex[1] + 5, by - 3)], bc, 2)
    else:
        line([(ex[0] - 6, by), (ex[0] + 5, by - 1.5)], bc, 2); line([(ex[1] - 5, by - 1.5), (ex[1] + 6, by)], bc, 2)
    if who == 'king':  # gafas
        for e in ex:
            d.rounded_rectangle([S(e - 8.4), S(ey - 6), S(e + 8.4), S(ey + 6)], radius=S(2), outline=(20, 18, 30), width=max(1, round(1.2 * sc)))
            line([(e - 6, ey + 4), (e - 2, ey - 3)], (200, 220, 255), 1)
        line([(ex[0] + 8.4, ey - 2), (ex[1] - 8.4, ey - 2)], (20, 18, 30), 1.2)
        line([(ex[0] - 8.4, ey - 3), (cx - 19, ey - 2)], (20, 18, 30), 1.2); line([(ex[1] + 8.4, ey - 3), (cx + 19, ey - 2)], (20, 18, 30), 1.2)
    # nariz y boca
    line([(cx + .5, 43), (cx + 2.5, 50)], skd, 1.2); line([(cx - 2, 51), (cx + 3, 51)], shade(p['skin'], .7), 1.2)
    pt(cx - 2, 51, shade(p['skin'], .6)); pt(cx + 2, 51, shade(p['skin'], .6))
    my = 56; lip = (172, 84, 84) if who != 'king' else (170, 96, 84)
    if expr == 'sad':
        line([(cx - 5, my + 2), (cx - 2, my), (cx + 3, my), (cx + 6, my + 2)], lip, 1.4)
    elif expr == 'smile':
        poly([(cx - 7, my - 1), (cx - 3, my + 2.5), (cx + 3, my + 2.5), (cx + 7, my - 1), (cx + 3, my), (cx - 3, my)], (250, 244, 240))
        line([(cx - 7, my - 1), (cx - 3, my + 3), (cx + 3, my + 3), (cx + 7, my - 1)], lip, 1.3)
    elif expr == 'wow':
        ell(cx - 3, my - 1, cx + 3, my + 5, (110, 44, 54))
    elif expr == 'worry':
        line([(cx - 5, my + 1), (cx - 2, my + 2), (cx + 2, my), (cx + 5, my - 1)], lip, 1.4)
    else:
        line([(cx - 5, my), (cx + 5, my)], lip, 1.4); line([(cx - 3, my + 1.5), (cx + 3, my + 1.5)], shade(lip, 1.2), 1)
    return im


def arm(c, sx, sy, hx, hy, w, sleeve, skin, hand=3.2, nohand=False):
    """brazo grueso con manga y mano (coordenadas de mundo)."""
    c.d.line([(sx, sy), (hx, hy)], fill=sleeve, width=int(w))
    c.d.line([(sx + 1, sy), (hx + 1, hy)], fill=shade(sleeve, .85), width=max(1, int(w) // 3))
    if nohand: return
    c.d.ellipse([hx - hand, hy - hand * .8, hx + hand, hy + hand * .8], fill=skin)
    c.d.point((hx - 1, hy - 1), fill=shade(skin, 1.12))
