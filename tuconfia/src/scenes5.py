"""Historia 4 (Steve Jobs): del despido al regreso."""
import math, random
import numpy as np
from PIL import Image, ImageDraw
from lib import *
import scenes as S0
import scenes2 as S2
import scenes3 as S3
from scenes3 import rpg, bat, place, shrink, shadow


def _sign(c, x, y, txt, col, k=3):
    w = ptext_w(txt, k)
    c.R(x - 4, y - 4, w + 8, 5 * k + 8, (14, 10, 26)); c.R(x - 4, y - 4, w + 8, 1, col, c.ed); c.R(x - 4, y + 5 * k + 3, w + 8, 1, col, c.ed)
    ptext(c.ed, x, y, txt, col, k)
    c.light(x + w // 2, y + 6, w, 40, col, .45)


# ============================================================ 1 + 9. la puerta (Jobs con la caja / tú con la caja)
def door(t, u, who='jobs85', sign='APPLE', col=(255, 216, 74)):
    c = Canvas(vgrad([(0, '#2b1a4a'), (.45, '#d8784f'), (.62, '#e8a060'), (1, '#2a2038')]))
    hope = ease((u - .35) / .5) if who == 'you' else 0          # el final: amanece desde la caja
    c.R(0, 96, WW, 120, (34, 40, 74)); c.R(0, 96, WW, 3, (90, 100, 150))
    rnd = random.Random(5)
    for r in range(4):
        for k in range(8):
            on = rnd.random() < .3 or (hope > .5 and rnd.random() < .6)
            x0, y0 = 8 + k * 19, 104 + r * 22
            c.R(x0 - 1, y0 - 1, 16, 18, (24, 28, 56))
            c.R(x0, y0, 14, 16, (236, 176, 98) if on else (46, 54, 98))
            c.R(x0 + 6, y0, 2, 16, (24, 28, 56)); c.R(x0, y0 + 7, 14, 1, (24, 28, 56))
    c.light(80, 120, 90, 90, (255, 180, 100), .25)
    _sign(c, 24, 74, sign, col, 3 if len(sign) < 7 else 2)
    c.R(0, 204, WW, 90, (70, 58, 82)); c.R(0, 204, WW, 3, (130, 116, 140))
    for x in range(0, WW, 20): c.R(x, 207, 1, 90, (54, 44, 66))
    c.R(46, 152, 68, 52, (24, 28, 52)); c.R(48, 154, 64, 48, (120, 84, 70)); c.R(48, 154, 64, 5, (200, 150, 100)); c.R(79, 154, 2, 48, (24, 28, 52))
    c.light(80, 190, 60, 50, (255, 190, 110), .6)
    if who == 'you':
        x = 62 + 38 * ease(u * 1.1)                       # camina hacia la puerta (donde empieza el bucle)
    else:
        x = 112 - 56 * ease(u * 1.15)                     # sale por la puerta y camina
    bob = math.sin(t * 6) * .8
    if hope > .3:                                         # rayos suaves detrás del personaje
        for i in range(9):
            a = -math.pi / 2 + (i - 4) * .26
            c.d.polygon([(x, 170), (x + 110 * math.cos(a - .07), 170 + 110 * math.sin(a - .07)), (x + 110 * math.cos(a + .07), 170 + 110 * math.sin(a + .07))], fill=(150, 112, 120))
    place(c, bat(who, 'box'), x, 208 + bob)
    if hope > .3: _sign(c, 24, 74, sign, col, 3 if len(sign) < 7 else 2)
    if hope > 0: c.light(x, 175, 50, 50, (255, 214, 140), .45 * hope)
    for i in range(9 if not hope else 18):
        ph = (t * (.25 if not hope else .45) + i * .11) % 1
        px = (i * 37 + ph * 60) % WW; py = (70 + (1 - ph) * 130) if hope else (70 + ph * 130)
        c.R(px, py, 2 if hope else 3, 2, (255, 236, 170) if hope else (250, 248, 240))
    c.amb = (.95 + .08 * hope, .86 + .1 * hope, .92); c.vig = .75
    return c.render()


# ============================================================ 2. la junta (chibis, 1985)
def boardroom(t, u):
    c = Canvas(vgrad([(0, '#16283a'), (1, '#0e1824')]))
    c.R(8, 76, 144, 58, (36, 62, 96)); c.R(8, 76, 144, 2, (100, 140, 190))
    for i in range(12):
        h = 12 + (i * 17) % 28; c.R(10 + i * 12, 134 - h, 9, h, (22, 36, 62))
        for j in range(h // 8):
            if (i + j) % 2: c.R(12 + i * 12, 134 - h + 3 + j * 8, 2, 3, (255, 214, 120))
    c.R(78, 76, 3, 58, (16, 24, 40))
    w = ptext_w('1985', 5)
    c.R(80 - w // 2 - 6, 60, w + 12, 34, (14, 22, 40)); ptext(c.ed, 80 - w // 2, 66, '1985', (255, 216, 74), 5)
    c.light(80, 100, 90, 50, (140, 180, 255), .35)
    # suelo con tablones
    c.R(0, 198, WW, 100, (58, 38, 30)); c.R(0, 198, WW, 2, (110, 74, 50))
    for yy in range(208, 290, 12): c.R(0, yy, WW, 1, (44, 28, 22))
    # junta: tres sentados detrás de la mesa (la mesa tapa las piernas)
    for k, (who, x) in enumerate((('prod1', 56), ('prod2', 92), ('prod1', 128))):
        place(c, rpg(who, 0), x, 176 + math.sin(t * 2 + k) * .6, sh=False)
    c.R(14, 164, 132, 16, (136, 88, 54)); c.R(14, 164, 132, 2, (196, 136, 90)); c.R(14, 180, 132, 14, (86, 54, 36)); c.R(14, 192, 132, 2, (50, 30, 22))
    for k, x in enumerate((56, 92, 128)):
        ph = (u * 3.2 - k * .55)
        if 0 < ph < 1: ptext(c.ed, x - 2, 104 - int(ph * 4), '!', (255, 90, 90), 3)
    # Jobs de pie delante, entra desde la izquierda
    k = ease(u * 1.6)
    place(c, rpg('jobs85', int(t * 4) % 2 if u < .6 else 0), 40 + 8 * k, 222, sh=True)
    c.light(80, 140, 80, 70, (255, 200, 120), .35)
    c.amb = (.86, .9, 1); c.vig = .75
    return c.render()


# ============================================================ 4. NeXT + Pixar (chibi, de noche)
def next_pixar(t, u):
    c = Canvas(vgrad([(0, '#0a0c24'), (.6, '#241a4a'), (1, '#1a1228')]))
    stars(c, t, 60, 8, 110)
    c.R(0, 206, WW, 90, (34, 30, 54)); c.R(0, 206, WW, 2, (90, 80, 120))
    for x0, name, col, on in ((12, 'NEXT', (90, 220, 255), .25), (76, 'PIXAR', (255, 150, 220), .6)):
        c.R(x0, 110, 60, 96, (40, 40, 84)); c.R(x0, 110, 60, 3, (100, 100, 160))
        lit = u > on
        for r in range(4):
            for k in range(3):
                w_ = lit and (r + k) % 3
                c.R(x0 + 6 + k * 17, 120 + r * 21, 10, 12, (255, 220, 130) if w_ else (30, 30, 62))
        if lit: _sign(c, x0 + 30 - ptext_w(name, 3) // 2, 84, name, col, 3)
    k = ease(u * 1.15)
    x = 128 - 74 * k
    place(c, rpg('jobs85', int(t * 5) % 2), x, 214, flip=True)
    if u > .1: c.R(x + 8, 196, 10, 8, (190, 150, 98)); c.R(x + 8, 196, 10, 2, (222, 184, 130))
    c.light(80, 200, 100, 70, (160, 140, 255), .3)
    c.amb = (.85, .86, 1); c.vig = .7
    return c.render()


# ============================================================ 5. Apple se hunde (gráfica)
def crash(t, u):
    c = Canvas(vgrad([(0, '#2a0c14'), (1, '#12060a')]))
    c.R(12, 76, 136, 112, (22, 12, 20)); c.R(12, 76, 136, 2, (120, 40, 50)); c.R(12, 186, 136, 2, (120, 40, 50))
    for i in range(1, 6): c.R(12, 76 + i * 18, 136, 1, (60, 24, 32))
    pts = [(x, int(76 + (y - 64) * .73)) for x, y in [(16, 84), (34, 92), (50, 80), (66, 112), (82, 108), (98, 148), (114, 142), (130, 196), (144, 204)]]
    n = min(len(pts), max(2, int(2 + (len(pts) - 2) * min(1, u * 1.5))))
    for a, b in zip(pts[:n - 1], pts[1:n]): c.d.line([a, b], fill=(255, 70, 80), width=2)
    for i in range(n): c.ed.ellipse([pts[i][0] - 2, pts[i][1] - 2, pts[i][0] + 2, pts[i][1] + 2], fill=(255, 190, 190, 255))
    ex, ey = pts[min(n - 1, len(pts) - 1)]
    c.d.polygon([(ex - 6, ey - 2), (ex + 6, ey - 2), (ex, ey + 10)], fill=(255, 70, 80))
    ptext(c.ed, 86, 82, 'APPLE', (255, 120, 120), 3)
    for i in range(10):
        ph = (t * .5 + i * .1) % 1
        c.R((i * 29) % WW, 20 + ph * 250, 4, 3, (250, 246, 236)); 
    sh = math.sin(t * 40) * 1.2 if .4 < u < .6 else 0
    c.light(80, 140, 90, 100, (255, 40, 60), .35)
    c.amb = (1, .8, .85); c.vig = .85
    return c.render()


# ============================================================ 6. el teléfono suena (1997)
def phone(t, u):
    c = Canvas(vgrad([(0, '#0c1230'), (1, '#1a2450')]))
    w = ptext_w('1997', 6)
    ptext(c.ed, 80 - w // 2, 64, '1997', (255, 216, 74), 6)
    c.light(80, 70, 80, 40, (255, 216, 74), .5)
    c.R(0, 182, WW, 114, (26, 22, 44))
    ring = int(t * 4) % 2 == 0
    sh = int(math.sin(t * 60) * 1.5) if ring else 0
    # base roja con disco giratorio
    c.R(36, 152, 88, 30, (190, 58, 62)); c.R(36, 152, 88, 3, (240, 120, 110)); c.R(36, 179, 88, 3, (120, 32, 40))
    c.R(44, 144, 72, 12, (170, 48, 54))
    cx_, cy_ = 80, 168
    c.d.ellipse([cx_ - 15, cy_ - 15, cx_ + 15, cy_ + 15], fill=(236, 232, 222), outline=(120, 120, 130))
    for i in range(9):
        a = math.pi * (.15 + i * .2)
        c.d.ellipse([cx_ + 10 * math.cos(a) - 2, cy_ + 10 * math.sin(a) - 2, cx_ + 10 * math.cos(a) + 2, cy_ + 10 * math.sin(a) + 2], fill=(60, 60, 74))
    c.d.ellipse([cx_ - 3, cy_ - 3, cx_ + 3, cy_ + 3], fill=(190, 58, 62))
    # auricular encima (vibra al sonar)
    c.R(40, 130 + sh, 80, 8, (210, 70, 72)); c.R(40, 130 + sh, 80, 2, (250, 150, 140))
    c.R(36, 134 + sh, 16, 16, (210, 70, 72)); c.R(108, 134 + sh, 16, 16, (210, 70, 72))
    c.R(36, 134 + sh, 16, 2, (250, 150, 140)); c.R(108, 134 + sh, 16, 2, (250, 150, 140))
    c.R(40, 138 + sh, 80, 3, (150, 40, 48))
    for i in range(3):
        ph_ = (t * 1.6 + i * .33) % 1
        r = 10 + ph_ * 18
        a = int(255 * (1 - ph_))
        c.ed.arc([80 - r, 124 - r, 80 + r, 124 + r], 215, 325, fill=(255, 255, 255, a), width=2)
    c.amb = (.9, .92, 1); c.vig = .8
    return c.render()


# ============================================================ 7. iMac, iPod, iPhone (genéricos)
def devices(t, u):
    c = Canvas(vgrad([(0, '#3a1858'), (.5, '#c8506a'), (1, '#ffb060')]))
    for i in range(16):
        a = i / 16 * math.pi * 2 + t * .25
        c.d.polygon([(80, 150), (80 + 260 * math.cos(a), 150 + 260 * math.sin(a)), (80 + 260 * math.cos(a + .15), 150 + 260 * math.sin(a + .15))], fill=(255, 190, 120))
    def pop(k0): return ease((u - k0) / .12)
    # all-in-one translúcido
    k = pop(0.0); s = .6 + .4 * k
    if k > 0:
        w, h = int(70 * s), int(54 * s); x, y = 80 - w // 2, 62
        c.R(x, y, w, h, (70, 200, 220)); c.R(x, y, w, 2, (170, 240, 250)); c.R(x + 4, y + 4, w - 8, h - 14, (210, 236, 255), c.ed)
        c.R(x + 6, y + 6, w - 12, 3, (120, 170, 240), c.ed); c.R(x + w // 2 - 3, y + h - 7, 6, 3, (255, 255, 255))
        c.R(80 - 8, y + h, 16, 6, (70, 200, 220)); c.R(80 - 14, y + h + 6, 28, 3, (50, 150, 170))
    # reproductor blanco con rueda
    k = pop(0.33)
    if k > 0:
        s = .6 + .4 * k; w, h = int(24 * s), int(40 * s); x, y = 34, 136
        c.R(x, y, w, h, (244, 244, 250)); c.R(x, y, w, 1, (255, 255, 255)); c.R(x + 3, y + 3, w - 6, int(14 * s), (120, 200, 160), c.ed)
        c.ed.ellipse([x + w // 2 - int(8 * s), y + int(24 * s), x + w // 2 + int(8 * s), y + int(40 * s)], outline=(180, 180, 196, 255), width=1)
    # teléfono delgado
    k = pop(0.66)
    if k > 0:
        s = .6 + .4 * k; w, h = int(24 * s), int(46 * s); x, y = 104, 132
        c.R(x, y, w, h, (28, 28, 36)); c.R(x, y, w, 1, (110, 110, 130)); c.R(x + 2, y + 4, w - 4, h - 12, (90, 170, 255), c.ed)
        c.R(x + 4, y + 7, w - 8, 3, (255, 255, 255), c.ed); c.R(x + w // 2 - 2, y + h - 5, 4, 2, (180, 180, 190))
    for i in range(14):
        ph = (t * .6 + i * .07) % 1; xx = 10 + (i * 47) % 140; yy = 260 - ph * 220
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)): c.d.point((xx + dx, yy + dy), fill=(255, 240, 180))
    c.light(80, 120, 90, 90, (255, 220, 150), .5)
    c.amb = (1, .96, .96); c.vig = .6
    return c.render()
