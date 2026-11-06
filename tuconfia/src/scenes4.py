"""Historia 3 (Stallone / Rocky)."""
import math, random
import numpy as np
from PIL import Image, ImageDraw
from lib import *
import sprites as SP
import scenes as S0
import scenes2 as S2
import scenes3 as S3
from scenes3 import rpg, bat, place, shrink, cached, shadow

def dog(sc=1, step=0): return cached(('dog', sc, step), lambda: SP.dog(sc, step))


# ================================================================ 1. HOOK: el perro en venta
def liquor(t, u):
    c = Canvas(vgrad([(0, '#3a2250'), (.5, '#c8624a'), (1, '#5a3a40')]))
    S0.bricks(c, 30, 214, 11, (96, 62, 62))
    # escaparate con neón
    c.R(14, 56, 132, 62, (24, 18, 30)); c.R(18, 60, 124, 54, (60, 40, 70)); c.R(18, 60, 124, 54, (60, 40, 70))
    flick = 1 if int(t * 10) % 19 else 0
    col = (255, 80, 90) if flick else (120, 50, 60)
    c.R(36, 28, 88, 20, (20, 12, 26)); c.R(36, 28, 88, 1, col, c.ed); c.R(36, 47, 88, 1, col, c.ed); c.R(36, 28, 1, 20, col, c.ed); c.R(123, 28, 1, 20, col, c.ed)
    ptext(c.ed, 44, 33, 'LICORES', col, 3)
    c.light(80, 40, 90, 50, (255, 70, 90), .6 * flick + .1)
    for i in range(5):
        x = 26 + i * 24; c.R(x, 78, 8, 28, (90, 150, 110)); c.R(x + 2, 70, 4, 9, (90, 150, 110)); c.R(x + 1, 80, 2, 16, (160, 220, 170))
    c.R(0, 214, WW, 80, (82, 70, 84))
    for x in range(0, WW, 24): c.R(x, 214, 1, 80, (66, 54, 68))
    c.R(0, 214, WW, 3, (130, 116, 130))
    # poste y cartel
    c.R(112, 120, 4, 98, (50, 50, 66)); c.R(112, 120, 4, 3, (110, 110, 130))
    sg = Image.new('RGBA', (72, 30), (0, 0, 0, 0)); d = ImageDraw.Draw(sg)
    d.rectangle([0, 0, 71, 29], fill=(204, 160, 104)); d.rectangle([0, 0, 71, 2], fill=(226, 188, 130))
    ptext(d, 5, 10, 'SE VENDE', (40, 30, 40), 2)
    sway = math.sin(t * 2) * 1.5
    c.im.paste(S0.outline(sg) if hasattr(S0, 'outline') else sg, (34, 130 + int(sway)), S0.outline(sg) if hasattr(S0, 'outline') else sg)
    # Butkus
    dg = dog(2, 0)
    bb = dg.getbbox()
    shadow(c, 80, 234, 80)
    c.im.alpha_composite(dg, (50, 232 - bb[3] + 1 + int(math.sin(t * 2.4) * 1))) if False else c.im.paste(dg, (50, 232 - bb[3] + 1 + int(math.sin(t * 2.4) * 1)), dg)
    c.light(80, 170, 70, 80, (255, 170, 120), .35)
    c.amb = (.85, .78, .9)
    c.vig = .7
    return c.render()


# ================================================================ 2. EL GUION (prop) + NO
def script_prop(t, u):
    c = Canvas(vgrad([(0, '#241418'), (.5, '#4a2c26'), (1, '#2e1a18')]))
    rnd = random.Random(4)
    for i in range(24):
        x, y, r = rnd.uniform(0, WW), rnd.uniform(10, 80), rnd.uniform(4, 9)
        c.d.ellipse([x - r, y - r, x + r, y + r], fill=(int(120 + rnd.random() * 40), int(70 + rnd.random() * 30), 40))
    c.R(0, 96, WW, 200, (118, 74, 46))
    for y in range(100, 290, 9): c.R(0, y, WW, 1, (92, 56, 36)); c.R(0, y + 1, WW, 1, (136, 90, 58))
    c.R(0, 96, WW, 3, (166, 116, 76))
    # pila de páginas con título
    shake = 0
    if .5 < u < .65: shake = math.sin((u - .5) * 200) * 2 * (1 - (u - .5) / .15)
    px0 = 14 + int(shake)
    for i in range(5):
        c.R(px0 + i, 136 + (4 - i) * 2, 70, 86, (252 - i * 4, 250 - i * 4, 242 - i * 4)); c.R(px0 + i, 136 + (4 - i) * 2, 70, 1, (200, 196, 188))
    c.R(px0 + 4, 134, 70, 86, (252, 250, 244)); c.R(px0 + 4, 134, 70, 1, (210, 206, 198))
    w = ptext_w('ROCKY', 3)
    ptext(c.d, px0 + 4 + 35 - w // 2, 150, 'ROCKY', (30, 30, 40), 3)
    for i in range(7): c.R(px0 + 12, 184 + i * 4, 40 + (i * 7) % 18, 1, (120, 120, 134))
    # fajos de billetes que entran por la derecha
    slide = 1 - ease(u * 2.2)
    for i in range(4):
        bx = 92 + i * 10 + slide * 80; by = 168 + i * 6
        c.R(int(bx), by, 40, 14, (70, 170, 96)); c.R(int(bx), by, 40, 2, (130, 224, 150)); c.R(int(bx) + 16, by + 3, 8, 8, (44, 120, 70)); c.R(int(bx) + 10, by, 3, 14, (240, 230, 200))
    # sello NO
    if u > .45:
        k = ease((u - .45) / .1)
        kk = max(2, int(10 - 6 * k)); w2 = ptext_w('NO', kk)
        ang_x, ang_y = 80 - w2 // 2, 108 - kk
        for ox, oy in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
            ptext(c.d, ang_x + ox, ang_y + oy, 'NO', (90, 10, 20), kk)
        ptext(c.d, ang_x, ang_y, 'NO', (230, 40, 56), kk)
        c.light(80, 112, 80, 50, (255, 60, 70), .4 * k)
    c.light(80, 150, 90, 100, (255, 200, 120), .5)
    c.amb = (.9, .78, .72)
    c.vig = .75
    return c.render()


# ================================================================ 4. LA PELEA EN EL CINE (RPG)
def cinema(t, u):
    c = Canvas(vgrad([(0, '#07060f'), (1, '#120c1c')]))
    # pantalla
    c.R(16, 40, 128, 84, (230, 226, 214)); c.R(16, 40, 128, 2, (255, 255, 250))
    c.R(20, 44, 120, 76, (30, 28, 48), c.ed)
    # ring: cuerdas y lona
    c.R(20, 100, 120, 20, (60, 60, 120), c.ed)
    for yy in (70, 80, 90): c.R(20, yy, 120, 1, (230, 60, 70), c.ed)
    for xx in (22, 138): c.R(xx, 62, 2, 40, (200, 200, 210), c.ed)
    # boxeadores
    ph = t * 3
    def boxer(x, col, trunk, dirn):
        pun = max(0, math.sin(ph + (0 if dirn > 0 else 1.6))) * 8
        c.ed.ellipse([x - 6, 74, x + 6, 88], fill=(*col, 255))                                    # cabeza
        c.ed.rectangle([x - 8, 88, x + 8, 106], fill=(*col, 255)); c.ed.rectangle([x - 8, 104, x + 8, 112], fill=(*trunk, 255))
        c.ed.rectangle([x - 5, 112, x - 2, 120], fill=(*col, 255)); c.ed.rectangle([x + 2, 112, x + 5, 120], fill=(*col, 255))
        gx = x + dirn * (12 + pun)
        c.ed.line([(x + dirn * 6, 92), (gx, 90)], fill=(*col, 255), width=3); c.ed.ellipse([gx - 5, 86, gx + 5, 96], fill=(230, 40, 50, 255))
    boxer(64 + math.sin(ph * .7) * 4, (92, 62, 48), (250, 250, 252), 1)
    boxer(104 - math.sin(ph * .7) * 4, (220, 176, 140), (30, 30, 40), -1)
    c.light(80, 90, 100, 80, (200, 210, 255), .7)
    # público: siluetas
    for row in range(3):
        y = 180 + row * 30
        for x in range(-6, WW + 10, 22):
            xx = x + (row % 2) * 11
            c.d.ellipse([xx, y, xx + 14, y + 14], fill=(18, 12, 26)); c.R(xx - 2, y + 12, 18, 20, (18, 12, 26))
    # Stallone mirando la pantalla (chibi) a un lado
    place(c, rpg('stallone', int(t * 2) % 2), 36, 258, sh=False)
    c.light(40, 220, 60, 70, (160, 180, 255), .35)
    c.amb = (.9, .9, 1)
    c.vig = .75
    return c.render()


# ================================================================ 5. ESCRIBIENDO (batalla)
def typing(t, u):
    c = Canvas(vgrad([(0, '#241c20'), (1, '#161014')]))
    S0.room_base(c, t)
    place(c, bat('stallone', 'stand'), 78, 214, sh=False)
    c.R(40, 172, 88, 5, (160, 112, 70)); c.R(40, 172, 88, 1, (204, 150, 96)); c.R(42, 177, 84, 40, (110, 76, 50)); c.R(44, 217, 4, 30, (80, 54, 36)); c.R(120, 217, 4, 30, (80, 54, 36))
    tw = S2.typewriter_big()
    c.blit(tw, 64, 160)
    sh = 14 + int(t * 6) % 6
    c.R(72, 158 - sh + 6, 14, sh, (246, 244, 234)); c.R(72, 158 - sh + 6, 14, 1, (200, 196, 190))
    n = 1 + int(u * 5)
    c.blit(SP.Paint(1, 1).final.__self__.final() if False else S2._pages_sprite(), 104, 160)
    for i in range(n): c.R(100 + (i % 3) * 5, 168 - i * 2, 12, 2, (246, 244, 234))
    # cartel del día
    day = 1 + min(2, int(u * 3))
    txt = f'DIA {day}'; w = ptext_w(txt, 3)
    c.R(80 - w // 2 - 5, 40, w + 10, 22, (20, 10, 26)); c.R(80 - w // 2 - 5, 40, w + 10, 2, (255, 216, 74))
    ptext(c.d, 80 - w // 2, 46, txt, (255, 255, 255), 3)
    # lámpara y café
    c.R(24, 146, 2, 26, (40, 40, 48)); c.R(15, 140, 20, 7, (230, 170, 70)); c.R(16, 146, 18, 2, (255, 240, 180), c.ed)
    c.light(26, 158, 80, 80, (255, 190, 100), 1.0)
    for i in range(12): c.d.point((44 + (i * 17) % 60 + math.sin(t + i) * 3, 110 + (i * 29) % 56), fill=(255, 226, 170))
    c.amb = (.66, .6, .66)
    c.vig = .65
    return c.render()


# ================================================================ 6/8/10. OFICINA (batalla)
def office(t, u, mode='offer'):
    c = Canvas(vgrad([(0, '#d8e6f0'), (1, '#a8b8c8')]))
    c.R(0, 0, WW, 214, (206, 196, 180))
    for x in range(0, WW, 20): c.R(x, 0, 1, 214, (190, 180, 164))
    # ventana con skyline
    c.R(20, 30, 70, 64, (60, 52, 46)); c.R(23, 33, 64, 58, (150, 200, 240), c.ed)
    rnd = random.Random(6); x = 23
    while x < 85:
        w = rnd.randint(6, 12); h = rnd.randint(10, 34); c.R(x, 91 - h, w, h, (90, 110, 150), c.ed); x += w + 1
    c.R(54, 33, 2, 58, (60, 52, 46)); c.R(23, 62, 64, 2, (60, 52, 46))
    c.R(106, 40, 34, 44, (140, 100, 66)); c.R(108, 42, 30, 40, (226, 214, 190))                 # cuadro
    c.R(0, 214, WW, 80, (96, 70, 52))
    for y in range(220, 284, 12): c.R(0, y, WW, 1, (76, 54, 40))
    # productores
    place(c, bat('prod1', 'stand'), 112, 224, flip=True)
    place(c, bat('prod2', 'stand'), 146, 224, flip=True)
    # escritorio grande
    c.R(78, 176, 90, 7, (136, 92, 58)); c.R(78, 176, 90, 1, (176, 128, 84)); c.R(80, 183, 86, 50, (104, 68, 44))
    # Stallone al frente
    pose = 'hold' if mode != 'slam' else 'toss'
    sx = 36
    shake = 0
    if mode == 'slam' and .25 < u < .45: shake = math.sin((u - .25) * 160) * 2 * (1 - (u - .25) / .2)
    place(c, bat('stallone', pose), sx, 244)
    if mode == 'offer':
        for i in range(4):
            bx = 98 + i * 11; c.R(bx, 168 - i % 2 * 2, 18, 8, (70, 170, 96)); c.R(bx, 168 - i % 2 * 2, 18, 1, (130, 224, 150)); c.R(bx + 7, 169 - i % 2 * 2, 4, 5, (44, 120, 70))
        c.R(94, 164, 56, 12, (40, 36, 44)); c.R(94, 164, 56, 2, (90, 86, 100))
    elif mode == 'slam':
        # el guion golpea el escritorio
        k = ease((u - .2) / .1) if u > .2 else 0
        py = 130 + k * 40 if u < .3 else 170
        c.R(84, int(py), 20, 24, (252, 250, 244)); c.R(84, int(py), 20, 1, (200, 196, 188))
        ptext(c.d, 88, int(py) + 5, 'ROCKY', (30, 30, 40), 1)
        if u > .3:
            for i in range(10):
                a = i / 10 * 6.28; r = (u - .3) * 40
                c.d.point((94 + math.cos(a) * r, 172 + math.sin(a) * r * .5), fill=(255, 240, 200))
        c.light(94, 168, 40, 30, (255, 240, 200), .6 * max(0, 1 - abs(u - .35) * 6))
    else:
        c.R(88, 166, 36, 10, (252, 250, 244)); c.R(88, 166, 36, 1, (200, 196, 188))
        for i in range(3): c.R(92, 169 + i * 2, 24, 1, (120, 120, 134))
        k = ease(u * 2)
        c.d.line([(108, 175), (108 + 12 * k, 172), (112 + 16 * k, 175), (118 + 20 * k, 171)], fill=(30, 44, 140))
        c.light(100, 150, 70, 60, (255, 232, 170), .5)
    c.light(80, 70, 110, 80, (255, 248, 230), .45)
    c.amb = (.95, .9, .86)
    c.vig = .5
    img = c.render()
    if shake:
        img = img.transform(img.size, Image.AFFINE, (1, 0, shake, 0, 1, 0))
    return img


# ================================================================ NO en grande (retrato)
def portrait_no(t, u):
    img = S2.portrait_scene(t, 'stallone', 'n', (0, 0), 'purple', tag='SYLVESTER STALLONE' if False else None)
    d = ImageDraw.Draw(img)
    if u > .45:
        k = ease((u - .45) / .12)
        kk = max(3, int(12 - 4 * k)); w = ptext_w('NO', kk)
        x, y = 80 - w // 2, 190 + (1 - k) * 14
        for ox, oy in ((-3, -3), (3, -3), (-3, 3), (3, 3), (0, 4)):
            ptext(d, x + ox, y + oy, 'NO', (60, 6, 16), kk)
        ptext(d, x, y, 'NO', (255, 60, 70), kk)
    return img


# ================================================================ 9. OSCAR
def oscars(t, u):
    c = Canvas(vgrad([(0, '#2a0a14'), (.5, '#6a1424'), (1, '#3a0c18')]))
    for x in range(0, WW, 16):
        c.d.polygon([(x, 0), (x + 16, 0), (x + 20, 200), (x + 4, 200)], fill=(150 + (x // 16 % 2) * 16, 24, 40))
        c.R(x + 6, 0, 1, 200, (190, 50, 64))
    c.R(0, 228, WW, 80, (60, 30, 40)); c.R(0, 228, WW, 3, (220, 170, 90))
    for x in range(0, WW, 14): c.R(x, 232, 1, 60, (46, 22, 32))
    # focos
    for k, (x0, col) in enumerate([(20, (255, 232, 170)), (140, (255, 232, 170))]):
        c.light(x0, 40, 90, 140, col, .7)
    # cartel
    txt = 'MEJOR PELICULA'; w = ptext_w(txt, 2)
    k = ease(u * 4)
    c.R(80 - w // 2 - 6, 26, w + 12, 20, (20, 10, 26)); c.R(80 - w // 2 - 6, 26, w + 12, 2, (255, 216, 74)); c.R(80 - w // 2 - 6, 44, w + 12, 2, (255, 216, 74))
    ptext(c.d, 80 - w // 2, 32, txt, (255, 236, 150), 2)
    place(c, bat('stallone_tux', 'trophy'), 80, 252)
    hx, hy = 80 + 15 - 2, 252 - 116 + 10
    st = Image.new('RGBA', (12, 28), (0, 0, 0, 0)); d = ImageDraw.Draw(st)
    d.ellipse([3, 0, 8, 5], fill=(255, 214, 70)); d.rectangle([3, 5, 8, 18], fill=(255, 214, 70)); d.rectangle([0, 7, 2, 10], fill=(255, 214, 70)); d.rectangle([9, 7, 11, 10], fill=(255, 214, 70))
    d.rectangle([2, 18, 9, 21], fill=(232, 176, 40)); d.rectangle([0, 22, 11, 27], fill=(200, 140, 30)); d.line([(4, 6), (4, 16)], fill=(255, 248, 190))
    c.blit(st, hx - 6, hy - 26)
    c.light(hx, hy - 12, 26, 26, (255, 220, 120), .6)
    rnd = random.Random(21)
    for i in range(70):
        x = rnd.uniform(0, WW); y0 = rnd.uniform(0, WH); s_ = rnd.uniform(20, 60)
        y = (y0 + t * s_) % (WH + 10) - 5
        c.R(int(x + math.sin(t * 2 + i) * 3), int(y), 2, 3, [(255, 214, 70), (255, 255, 255), (255, 160, 60)][i % 3])
    c.amb = (1, .96, .94)
    c.vig = .55
    return c.render()


# ================================================================ 10. REENCUENTRO (RPG)
def reunion(t, u):
    c = Canvas(np.zeros((WH, WW, 3)))
    S3.potrero_bg(c, t)
    sx = 56; dx = 116 - ease(u * 1.6) * 40
    place(c, rpg('stallone', int(t * 3) % 2), sx, 238)
    jump = abs(math.sin(t * 7)) * 5
    d_ = dog(1, int(t * 8) % 2)
    bb = d_.getbbox(); shadow(c, dx, 238, 40)
    c.im.paste(d_.transpose(Image.FLIP_LEFT_RIGHT), (int(dx - d_.width / 2), int(238 - bb[3] + 1 - jump)), d_.transpose(Image.FLIP_LEFT_RIGHT))
    for i in range(6):
        ph = (t * .7 + i / 6) % 1; x = 70 + i * 6 + math.sin(ph * 6 + i) * 4; y = 190 - ph * 50
        c.d.polygon([(x, y + 2), (x + 3, y - 1), (x + 5, y + 1), (x + 7, y - 1), (x + 10, y + 2), (x + 5, y + 8)], fill=(255, 90, 120))
    c.light(110, 70, 90, 90, (255, 220, 150), .5)
    c.amb = (1, .98, .94)
    c.vig = .35
    return c.render()


# ================================================================ 11. ATARDECER (RPG)
def sunset(t, u):
    c = Canvas(vgrad([(0, '#1c2a66'), (.3, '#8a4a8c'), (.5, '#ff8a5a'), (.65, '#ffd070'), (1, '#ffe8a0')]))
    sy = 168 - ease(u) * 6
    c.d.ellipse([60, sy - 20, 100, sy + 20], fill=(255, 238, 180)); c.light(80, sy, 110, 100, (255, 190, 100), .9)
    stars(c, t, 30, 8, 60)
    rnd = random.Random(12)
    for i in range(6):
        x = (rnd.uniform(0, WW) + t * (3 + i)) % (WW + 60) - 30; y = rnd.uniform(60, 130)
        for j in range(4): c.d.ellipse([x + j * 8, y - (j % 2) * 3, x + j * 8 + 16, y + 6], fill=(255, 170 + i * 8, 140 + i * 10))
    # skyline en silueta
    x = 0; rnd = random.Random(9)
    while x < WW:
        w = rnd.randint(8, 16); h = rnd.randint(16, 44); c.R(x, 188 - h, w, h, (84, 56, 92))
        for yy in range(188 - h + 4, 186, 6):
            for xx in range(x + 2, x + w - 2, 5):
                if rnd.random() < .4: c.R(xx, yy, 2, 2, (255, 214, 120), c.ed)
        x += w + 1
    c.R(0, 188, WW, 100, (70, 52, 80)); c.R(0, 188, WW, 2, (130, 96, 120))
    for x in range(0, WW, 30): c.R(x + 4, 240, 18, 3, (240, 220, 120))
    wx = 30 + ease(u) * 90
    place(c, rpg('stallone', int(t * 4) % 2), wx, 252)
    d_ = dog(1, int(t * 6) % 2); bb = d_.getbbox(); shadow(c, wx + 36, 250, 40)
    c.im.paste(d_, (int(wx + 36 - d_.width / 2), int(250 - bb[3] + 1)), d_)
    c.amb = (1, .96, 1)
    c.vig = .5
    return c.render()


# ================================================================ 12. TÚ con el guion (batalla)
def tu_script(t, u):
    c = Canvas(vgrad([(0, '#080b1c'), (.5, '#171c3a'), (1, '#0c0c18')]))
    S0.bricks(c, 40, 210)
    c.R(0, 206, WW, 80, (30, 32, 48))
    for x in range(0, WW, 14): c.R(x, 208 + (x // 14 % 3) * 9, 12, 1, (40, 44, 64))
    c.R(23, 70, 3, 138, (34, 36, 54)); c.R(23, 70, 14, 3, (34, 36, 54)); c.R(33, 72, 7, 3, (250, 220, 150), c.ed)
    c.light(36, 78, 70, 100, (230, 170, 80), .55); c.light(86, 170, 70, 90, (255, 214, 140), .55)
    place(c, bat('you', 'hold'), 80, 228)
    c.R(54, 206, 52, 4, (60, 60, 80)); c.R(54, 206, 52, 1, (110, 110, 140)); c.R(78, 210, 4, 36, (50, 50, 66)); c.R(66, 244, 28, 3, (50, 50, 66))
    bob = math.sin(t * 3) * 1.2
    c.R(60, 188 + bob, 30, 19, (252, 250, 244)); c.R(60, 188 + bob, 30, 1, (200, 196, 188))
    ptext(c.d, 70, 192 + bob, '?', (30, 30, 80), 4)
    bb = math.sin(t * 3) * 1.5
    c.R(60, 50 + bb, 40, 20, (255, 216, 74)); c.R(60, 50 + bb, 40, 2, (255, 244, 170)); c.R(60, 68 + bb, 40, 2, (190, 150, 30))
    ptext(c.d, 66, 56 + bb, 'TU', (20, 10, 26), 3); c.R(68, 53 + bb, 3, 2, (20, 10, 26))
    c.d.polygon([(76, 70 + bb), (84, 70 + bb), (80, 78 + bb)], fill=(255, 216, 74))
    rain(c, t, 70, 11)
    c.amb = (.66, .7, .92)
    c.vig = .7
    return c.render()
