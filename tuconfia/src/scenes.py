import math, random
import numpy as np
from PIL import Image, ImageDraw
from lib import *

SPR = {}
def sp(name, fn, *a, **k):
    key = (name, repr(a), repr(sorted(k.items())))
    if key not in SPR: SPR[key] = fn(*a, **k)
    return SPR[key]


def bricks(c, y0, y1, seed=5, base=(62, 48, 66)):
    rnd = random.Random(seed)
    for row, y in enumerate(range(y0, y1, 5)):
        off = 0 if row % 2 == 0 else 5
        for x in range(-10 + off, WW, 10):
            v = rnd.uniform(.8, 1.18)
            col = tuple(int(b * v) for b in base)
            c.R(x, y, 9, 4, col)
            c.R(x, y, 9, 1, shade(col, 1.18))


# =============================================================== 1. CALLEJÓN (hook)
def alley(t):
    bg = vgrad([(0, '#080b1c'), (.5, '#171c3a'), (1, '#0c0c18')])
    c = Canvas(bg)
    bricks(c, 40, 210)
    c.R(0, 206, WW, 80, (30, 32, 48))
    for x in range(0, WW, 14): c.R(x, 208 + (x // 14 % 3) * 9, 12, 1, (40, 44, 64))
    c.R(34, 214, 64, 12, (46, 56, 94))  # charco
    c.R(40, 216, 52, 1, (70, 86, 130))
    # cajas y contenedor lateral
    c.R(116, 176, 28, 30, (44, 70, 80)); c.R(116, 176, 28, 3, (70, 104, 112)); c.R(118, 183, 24, 1, (30, 50, 60))
    c.R(8, 190, 14, 16, (88, 66, 52)); c.R(8, 190, 14, 2, (118, 90, 70))
    # farola
    c.R(23, 70, 3, 138, (34, 36, 54)); c.R(23, 70, 14, 3, (34, 36, 54)); c.R(33, 72, 7, 3, (250, 220, 150), c.ed)
    c.light(36, 78, 70, 100, (230, 170, 80), .55)
    c.light(82, 168, 40, 46, (255, 210, 130), .55)
    # bote
    shake = 0
    imp = 1.05
    if t > imp and t < imp + .5: shake = int(round(math.sin((t - imp) * 50) * 2 * (1 - (t - imp) / .5)))
    can = sp('can', trash_can)
    c.blit(can, 70 + shake, 178)
    # basura asomando
    for (dx, dy, s) in [(3, -3, 7), (9, -5, 8), (14, -2, 6)]:
        c.blit(sp('pb', paper_ball, s, (200, 198, 190)), 70 + dx + shake, 178 + dy)
    # papel que cae
    if t < imp:
        k = ease(t / imp) ** 1.6
        py = -14 + (170 - -14) * k
        px = 82 + math.sin(t * 6) * 3 * (1 - k)
        s = 8
        c.blit(sp('pb', paper_ball, s, (252, 250, 240)), px, py)
        c.R(int(px) + 3, int(py) - 6, 1, 4, (210, 210, 230))
    else:
        c.blit(sp('pb', paper_ball, 8, (252, 250, 240)), 79 + shake, 172)
        # polvo/chispas
        tt = t - imp
        if tt < .6:
            for i in range(10):
                a = i / 10 * 6.28; r = tt * 30
                c.d.point((82 + math.cos(a) * r, 176 + math.sin(a) * r * .6 - tt * 8), fill=(200, 205, 230))
        # brillo sobre el papel (tras "no fue él")
        g = .5 + .5 * math.sin((t - imp) * 3)
        c.light(83, 172, 22, 22, (255, 230, 170), .35 + .3 * g)
        if int(t * 4) % 2 == 0:
            c.d.point((86, 166), fill=(255, 255, 255)); c.d.point((85, 166), fill=(255, 240, 200)); c.d.point((86, 165), fill=(255, 240, 200)); c.d.point((86, 167), fill=(255, 240, 200)); c.d.point((87, 166), fill=(255, 240, 200))
    rain(c, t, 80, 11)
    # gotas en el suelo
    for i in range(8):
        ph = (t * 3 + i * .37) % 1
        x = 20 + i * 17 % 120; y = 220 + (i * 7) % 40
        r = int(ph * 4)
        c.d.ellipse([x - r * 2, y - r, x + r * 2, y + r], outline=(100, 120, 170)) if r else None
    c.amb = (.55, .62, .85)
    c.vig = .7
    return c.render()


# =============================================================== 2. REMOLQUE
def trailer_night(t):
    c = Canvas(vgrad([(0, '#050818'), (.45, '#13204a'), (.62, '#2a3a6a'), (1, '#0c1226')]))
    stars(c, t, 90, 4, 120)
    # luna
    c.d.ellipse([112, 36, 134, 58], fill=(246, 244, 222)); c.d.ellipse([118, 40, 124, 46], fill=(222, 220, 200)); c.d.ellipse([124, 48, 128, 52], fill=(222, 220, 200))
    c.light(123, 47, 55, 55, (120, 140, 220), .55)
    # colinas
    pts = [(0, 150)] + [(x, 138 + 8 * math.sin(x / 19) + 5 * math.sin(x / 7.3)) for x in range(0, WW + 6, 6)] + [(WW, 220), (0, 220)]
    c.d.polygon(pts, fill=(26, 44, 74))
    pts = [(0, 160)] + [(x, 160 + 5 * math.sin(x / 13 + 1)) for x in range(0, WW + 6, 6)] + [(WW, 240), (0, 240)]
    c.d.polygon(pts, fill=(38, 58, 92))
    # pinos
    for (x, y, h) in [(6, 160, 46), (24, 168, 38), (134, 158, 50), (148, 170, 40), (-4, 176, 54), (120, 172, 36)]:
        c.blit(sp('pine', pine, h), x, y - h + 40)
    # suelo nevado
    c.R(0, 196, WW, 90, (176, 196, 232))
    for x in range(0, WW, 3): c.R(x, 196 + int(2 * math.sin(x / 5)), 3, 2, (214, 226, 248))
    c.R(0, 240, WW, 50, (140, 160, 204))
    # camino de huellas
    for i in range(7): c.R(78 + i * 6 - (i * i), 232 + i * 7, 4, 2, (110, 130, 176))
    # remolque
    c.blit(sp('trl', trailer), 38, 152)
    wl = (255, 214, 120)
    for (x, w) in [(46, 12), (64, 12), (86, 12)]:
        c.R(x, 164, w, 9, wl, c.ed); c.R(x + w // 2, 164, 1, 9, (160, 120, 60), c.ed)
        c.light(x + w // 2, 170, 26, 22, (255, 190, 90), .6)
    c.R(106, 160, 10, 24, (96, 70, 56)); c.R(112, 172, 1, 1, (255, 220, 140), c.ed)
    # chimenea y humo
    c.R(54, 146, 5, 7, (80, 70, 74))
    for i in range(7):
        ph = (t * .5 + i / 7) % 1
        r = 2 + ph * 5
        a = 1 - ph
        col = tuple(int(v) for v in (60 + 110 * a, 70 + 110 * a, 100 + 110 * a))
        c.d.ellipse([56 - r + math.sin(ph * 6 + i) * 4 + ph * 8, 146 - ph * 38 - r, 56 + r + math.sin(ph * 6 + i) * 4 + ph * 8, 146 - ph * 38 + r], fill=col)
    # buzón
    c.R(132, 204, 2, 12, (70, 50, 40)); c.R(128, 200, 10, 6, (60, 90, 150)); c.R(128, 200, 10, 1, (120, 150, 210))
    snow(c, t, 100, 7)
    c.amb = (.72, .78, 1)
    c.vig = .55
    return c.render()


# =============================================================== 3. AULA
def classroom(t):
    c = Canvas(vgrad([(0, '#3a4a40'), (1, '#2a3630')]))
    c.R(0, 0, WW, 215, (92, 108, 94))
    for x in range(0, WW, 20): c.R(x, 0, 1, 215, (80, 96, 84))
    c.R(0, 210, WW, 80, (118, 86, 58))
    for y in range(214, 284, 9): c.R(0, y, WW, 1, (96, 68, 44))
    # pizarra
    c.R(18, 62, 124, 78, (96, 64, 40)); c.R(22, 66, 116, 70, (28, 62, 52)); c.R(22, 66, 116, 2, (20, 44, 38))
    rnd = random.Random(8)
    for i in range(7):
        y = 74 + i * 8
        x = 28; n = rnd.randint(5, 11)
        for j in range(n):
            w = rnd.randint(3, 9)
            c.R(x, y + rnd.randint(0, 2), w, 1, (222, 230, 224)); x += w + 3
    c.R(24, 133, 112, 2, (110, 80, 52))
    # reloj
    c.d.ellipse([70, 26, 90, 46], fill=(240, 236, 220), outline=(40, 32, 30)); c.d.line([(80, 36), (80, 29)], fill=(30, 30, 30)); c.d.line([(80, 36), (85, 38)], fill=(30, 30, 30))
    # ventana
    c.R(116, 18, 34, 36, (150, 200, 240), c.ed) if False else None
    # pupitres
    for (x, y) in [(10, 196), (60, 202), (112, 196), (30, 236), (90, 240)]:
        c.R(x, y, 34, 5, (150, 108, 70)); c.R(x, y, 34, 1, (190, 140, 92)); c.R(x + 3, y + 5, 2, 18, (60, 56, 64)); c.R(x + 29, y + 5, 2, 18, (60, 56, 64))
        c.R(x + 6, y - 3, 8, 3, (230, 230, 220)); c.R(x + 18, y - 3, 6, 3, (200, 80, 70))
    # King
    sw = int(math.sin(t * 5) * 2)
    arm_r = [(19, 16), (25, 11), (31 + sw, 5 + abs(sw))]
    k = sp('kingT', person, **KING_T, arm_r=arm_r, arm_l=[(9, 16), (6, 22), (6, 29)])
    k = person(**KING_T, arm_r=arm_r)
    c.blit(k, 62, 148, flip=False)
    # polvo de tiza
    for i in range(6):
        ph = (t * .8 + i * .17) % 1
        c.d.point((92 + (i * 3) % 7 + ph * 4, 152 + ph * 30), fill=(230, 232, 226))
    c.light(80, 80, 90, 80, (255, 236, 190), .35)
    c.amb = (.95, .95, .88)
    c.vig = .5
    return c.render()


# =============================================================== 4. CAFETERÍA
def donut_shop(t):
    c = Canvas(vgrad([(0, '#1a1030'), (1, '#10142a')]))
    c.R(0, 0, WW, 92, (24, 22, 52))
    # ventana nocturna
    c.R(6, 30, 148, 56, (12, 20, 48)); c.R(6, 30, 148, 2, (200, 170, 130)); c.R(6, 84, 148, 2, (200, 170, 130)); c.R(78, 30, 3, 56, (200, 170, 130))
    stars(c, t, 20, 5, 70)
    # cartel neón
    flick = 1 if (int(t * 12) % 23 != 0) else 0
    col = (255, 90, 170) if flick else (120, 50, 90)
    c.R(40, 6, 80, 20, (20, 10, 26)); c.R(40, 6, 80, 1, col, c.ed); c.R(40, 25, 80, 1, col, c.ed); c.R(40, 6, 1, 20, col, c.ed); c.R(119, 6, 1, 20, col, c.ed)
    ptext(c.ed, 52, 11, 'DONAS', col, 3)
    c.light(80, 16, 80, 40, (255, 70, 160), .55 * flick + .15)
    # pared y barra
    c.R(0, 92, WW, 80, (232, 196, 190))
    for x in range(0, WW, 12): c.R(x, 92, 1, 80, (214, 176, 172))
    c.R(0, 172, WW, 112, (60, 50, 76))
    for yy in range(0, 112, 12):
        for xx in range(0, WW, 12):
            if ((xx // 12) + (yy // 12)) % 2 == 0: c.R(xx, 172 + yy, 12, 12, (230, 226, 232))
    # mostrador
    c.R(0, 170, WW, 14, (255, 140, 180)); c.R(0, 170, WW, 2, (255, 210, 226)); c.R(0, 184, WW, 56, (240, 240, 246)); c.R(0, 184, WW, 2, (200, 200, 214))
    # vitrina de donas
    c.R(14, 138, 62, 32, (150, 190, 220)); c.R(14, 138, 62, 2, (230, 244, 255))
    rnd = random.Random(2)
    cols = [(222, 120, 150), (120, 70, 50), (250, 230, 130), (130, 200, 170)]
    for r in range(2):
        for i in range(6):
            x = 18 + i * 10; y = 146 + r * 12
            cc = cols[(i + r) % 4]
            c.d.ellipse([x, y, x + 7, y + 6], fill=cc); c.d.rectangle([x + 3, y + 2, x + 4, y + 3], fill=(40, 30, 40))
            for _ in range(3): c.d.point((x + rnd.randint(0, 7), y + rnd.randint(0, 3)), fill=(255, 255, 255))
    # cafetera
    c.R(124, 130, 14, 40, (60, 60, 76)); c.R(126, 140, 10, 12, (190, 80, 50)); c.R(126, 140, 10, 2, (240, 140, 90))
    # Tabitha
    sw = int(math.sin(t * 3) * 2)
    tb = person(**TAB_UNI, arm_r=[(19, 16), (23, 22), (24 + sw, 26)], arm_l=[(9, 16), (6, 22), (6, 29)], legs=False)
    c.blit(tb, 80, 128)
    c.R(0, 166, WW, 4, (255, 150, 188))
    # taza que humea
    c.R(100, 160, 6, 6, (250, 250, 250)); c.R(106, 161, 2, 3, (250, 250, 250))
    for i in range(3):
        ph = (t + i / 3) % 1; c.d.point((103 + math.sin(ph * 8) * 2, 158 - ph * 12), fill=(230, 230, 240))
    # reloj tarde
    c.d.ellipse([140, 100, 152, 112], fill=(250, 250, 240), outline=(40, 30, 30)); c.d.line([(146, 106), (146, 101)], fill=(30, 30, 30)); c.d.line([(146, 106), (143, 109)], fill=(30, 30, 30))
    c.light(80, 140, 110, 90, (255, 200, 220), .25)
    c.amb = (.8, .76, .92)
    c.vig = .55
    return c.render()


# =============================================================== 5. CUARTITO (lavadero)
def room_base(c, t, morning=False):
    wall = (92, 70, 62) if not morning else (140, 112, 96)
    c.R(0, 0, WW, 210, wall)
    for x in range(0, WW, 8): c.R(x, 0, 1, 210, shade(wall, .84)); c.R(x + 1, 0, 1, 210, shade(wall, 1.08))
    c.R(0, 206, WW, 80, (74, 56, 50) if not morning else (118, 90, 74))
    for y in range(210, 284, 10): c.R(0, y, WW, 1, (54, 40, 36) if not morning else (90, 66, 54))
    # tuberías
    c.R(0, 18, WW, 4, (122, 128, 140)); c.R(0, 18, WW, 1, (176, 182, 196)); c.R(110, 22, 4, 40, (122, 128, 140)); c.R(0, 60, 24, 3, (122, 128, 140))
    # ventana
    wx, wy = 100, 64
    c.R(wx - 3, wy - 3, 40, 44, (60, 44, 40))
    skyc = (14, 22, 50) if not morning else (255, 226, 160)
    c.R(wx, wy, 34, 38, skyc, c.ed)
    c.R(wx + 16, wy, 2, 38, (60, 44, 40)); c.R(wx, wy + 18, 34, 2, (60, 44, 40))
    if not morning:
        for i in range(20):
            x = wx + (i * 7) % 33; y = wy + ((i * 13 + int(t * 20)) % 37); c.ed.point((x, y), fill=(240, 246, 255, 255))
    else:
        c.light(wx + 17, wy + 18, 90, 120, (255, 214, 140), .9)
    # lavadero (sin lavadora: solo un fregadero)
    c.R(6, 150, 30, 10, (170, 176, 186)); c.R(6, 150, 30, 2, (214, 220, 230)); c.R(8, 160, 26, 50, (90, 78, 80))


def room(t, phase='type', pages=1, thr=None, morning=False):
    c = Canvas(vgrad([(0, '#241c20'), (1, '#161014')]))
    room_base(c, t, morning)
    # papelera
    bin_x, bin_y = 24, 192
    c.R(bin_x, bin_y, 16, 18, (96, 100, 120)); c.R(bin_x, bin_y, 16, 2, (150, 156, 176)); c.R(bin_x + 2, bin_y + 6, 12, 1, (66, 70, 90))
    # escritorio
    c.R(44, 172, 76, 5, (160, 112, 70)); c.R(44, 172, 76, 1, (204, 150, 96)); c.R(46, 177, 72, 30, (110, 76, 50)); c.R(48, 207, 4, 28, (80, 54, 36)); c.R(112, 207, 4, 28, (80, 54, 36))
    # silla
    c.R(66, 150, 30, 5, (60, 40, 40))
    # King (sentado)
    sad = phase in ('slump', 'lift', 'throw')
    base = dict(KING); base['expr'] = 'sad' if sad else 'n'
    y_off = 1 if phase == 'slump' else 0
    ph = int(t * 9) % 2
    if phase == 'type':
        arm_l = [(9, 16), (8, 24), (11, 31 + ph)]
        arm_r = [(19, 16), (20, 24), (17, 31 + (1 - ph))]
    elif phase == 'lift':
        arm_l = [(9, 16), (8, 24), (11, 31)]
        arm_r = [(19, 16), (24, 12), (24, 5)]
    elif phase == 'throw':
        arm_l = [(9, 16), (8, 24), (11, 31)]
        arm_r = [(19, 16), (27, 14), (31, 9)]
    else:
        arm_l = [(9, 16), (8, 24), (11, 31)]
        arm_r = [(19, 16), (20, 24), (17, 31)]
    k = person(**base, legs=False, arm_l=arm_l, arm_r=arm_r)
    k = k.crop((0, 0, 28, 33))
    c.blit(k, 66, 138 + y_off)
    # máquina de escribir y hoja
    c.blit(sp('tw', typewriter), 74, 160)
    sheet_h = 12 + (int(t * 3) % 4 if phase == 'type' else 3)
    c.R(80, 160 - sheet_h + 2, 11, sheet_h, (246, 244, 234)); c.R(80, 160 - sheet_h + 2, 11, 1, (200, 196, 190))
    for i in range(3): c.R(82, 160 - sheet_h + 5 + i * 3, 7, 1, (120, 120, 130))
    # pilas de hojas
    if pages: c.blit(sp('stk', stack_pages, max(1, pages)), 104, 163)
    # lámpara
    c.R(52, 150, 2, 22, (40, 40, 48)); c.R(48, 146, 12, 5, (230, 170, 70)); c.R(49, 150, 10, 2, (255, 240, 180), c.ed)
    c.light(54, 156, 62, 62, (255, 190, 100), 1.0 if not morning else .5)
    # lanzamiento
    if thr is not None and thr >= 1:
        c.blit(sp('pb', paper_ball, 7, (240, 238, 228)), 28, 194)
    elif thr is not None:
        tt = max(0, min(1, thr))
        x = 98 + (30 - 98) * tt
        y = 150 + (-60 * 4 * tt * (1 - tt)) + (196 - 150) * tt
        c.blit(sp('pb', paper_ball, 7, (240, 238, 228)), x, y)
    # polvo en la luz
    for i in range(14):
        a = (t * .15 + i * .071) % 1
        c.d.point((44 + (i * 17) % 38 + math.sin(t + i) * 3, 130 + (i * 29) % 40), fill=(255, 226, 170))
    c.amb = (.66, .6, .66) if not morning else (.85, .8, .78)
    c.vig = .65
    return c.render()


# =============================================================== retratos
def portrait_scene(t, who='king', expr='n', look=(0, 0), tone='cold', ball=False, pages_in=False, sparkle=False, topc=None):
    if tone == 'cold': g = vgrad([(0, '#0a1a2a'), (1, '#1c2c44')]); amb = (.85, .9, 1)
    elif tone == 'warm': g = vgrad([(0, '#3a1e10'), (.5, '#a05a28'), (1, '#e0a040')]); amb = (1, .94, .85)
    else: g = vgrad([(0, '#2a1840'), (1, '#6a3a60')]); amb = (1, 1, 1)
    c = Canvas(g)
    # rayos de fondo
    for i in range(14):
        a = i / 14 * math.pi * 2 + t * .15
        c.d.polygon([(80, 120), (80 + 220 * math.cos(a), 120 + 220 * math.sin(a)), (80 + 220 * math.cos(a + .18), 120 + 220 * math.sin(a + .18))],
                    fill=tuple(int(v) for v in np.array(g[100, 0]) * 1.12 + 6))
    blink = (t % 3.2) < .12
    pt = portrait(who, expr, look, blink, top=topc, w=72, h=92)
    pt = pt.resize((pt.width * 2, pt.height * 2), Image.NEAREST)
    bob = int(math.sin(t * 1.8) * 1.2)
    c.blit(pt, 80 - pt.width // 2, 74 + bob)
    if ball:
        pb = sp('pbL', paper_ball, 22, (240, 238, 228))
        c.blit(pb, 22, 214 + int(math.sin(t * 2) * 1.2))
    if pages_in:
        pg = Image.new('RGBA', (64, 40), (0, 0, 0, 0)); d = ImageDraw.Draw(pg)
        d.polygon([(6, 38), (14, 0), (58, 4), (60, 40)], fill=(246, 244, 232))
        for i in range(5): d.line([(18 - i // 2, 8 + i * 6), (54, 10 + i * 6)], fill=(120, 120, 134))
        c.blit(pg, 48, 214 + int(math.sin(t * 2) * 1))
    if sparkle:
        for i in range(10):
            ph = (t * .7 + i * .1) % 1
            x = 20 + (i * 53) % 120; y = 250 - ph * 200
            col = (255, 232, 160)
            c.d.point((x, y), fill=col); c.d.point((x + 1, y), fill=col); c.d.point((x, y + 1), fill=col); c.d.point((x - 1, y), fill=col); c.d.point((x, y - 1), fill=col)
    c.light(80, 120, 80, 100, (255, 210, 150) if tone != 'cold' else (120, 160, 230), .35)
    c.amb = amb
    c.vig = .8
    return c.render()


# =============================================================== mañana + Tabitha rescata
def morning(t, u):
    c = Canvas(vgrad([(0, '#3a2a28'), (1, '#241a18')]))
    room_base(c, t, True)
    # escritorio vacío con luz
    c.R(44, 172, 76, 5, (160, 112, 70)); c.R(46, 177, 72, 30, (110, 76, 50))
    c.blit(sp('tw', typewriter), 74, 160)
    # papelera grande al frente
    bx, by = 66, 186
    c.blit(sp('can2', trash_can, 28, 32), bx, by)
    # hojas arrugadas dentro
    for (dx, dy, s) in [(4, -3, 8), (12, -5, 9), (17, -2, 7)]:
        c.blit(sp('pb', paper_ball, s, (222, 220, 210)), bx + dx, by + dy)
    # Tabitha se acerca y rescata
    k = ease(u * 1.6)
    tx = 120 - 40 * k
    lift = ease((u - .45) * 2.2)
    arm_r = [(19, 16), (17, 24 - lift * 6), (14 - lift * 2, 30 - lift * 14)]
    tb = person(**TAB, arm_r=arm_r, arm_l=[(9, 16), (6, 22), (6, 29)])
    c.blit(tb, tx, 190 - 40 if False else 164)
    # hoja que sale de la papelera
    if u > .45:
        py = by - 2 - lift * 26
        c.R(bx + 10, int(py), 9, 11, (246, 244, 232)); c.R(bx + 10, int(py), 9, 1, (180, 176, 168))
        for i in range(3): c.R(bx + 12, int(py) + 3 + i * 3, 5, 1, (120, 120, 134))
        # ceniza
        for i in range(12):
            ph = (u * 1.5 + i * .09) % 1
            c.d.point((bx + 8 + (i * 5) % 14 + math.sin(ph * 9) * 2, py + 8 + ph * 26), fill=(110, 110, 120))
    c.light(130, 100, 90, 110, (255, 220, 150), .55)
    c.amb = (.82, .76, .74)
    c.vig = .6
    return c.render()


# =============================================================== dinero / libro
def payoff(t, u, mode='adv', txt='$2.500'):
    c = Canvas(vgrad([(0, '#1a0e32'), (1, '#4a1a52')]))
    # rayos
    n = 18
    for i in range(n):
        a = i / n * 6.28 + t * .25
        if i % 2 == 0:
            c.d.polygon([(80, 130), (80 + 260 * math.cos(a), 130 + 260 * math.sin(a)), (80 + 260 * math.cos(a + 6.28 / n), 130 + 260 * math.sin(a + 6.28 / n))], fill=(110, 40, 90))
    # monedas / billetes que caen
    rnd = random.Random(9)
    for i in range(34 if mode == 'big' else 14):
        x = rnd.uniform(0, WW); y0 = rnd.uniform(0, WH); sp_ = rnd.uniform(40, 90)
        y = (y0 + t * sp_) % (WH + 20) - 10
        if i % 2 == 0:
            c.R(int(x), int(y), 9, 5, (60, 170, 90)); c.R(int(x), int(y), 9, 1, (120, 220, 140)); c.R(int(x) + 4, int(y) + 2, 1, 1, (20, 70, 40))
        else:
            c.d.ellipse([x, y, x + 5, y + 5], fill=(255, 210, 60)); c.d.point((x + 2, y + 2), fill=(255, 250, 180))
    # texto grande
    k = 5 if mode == 'adv' else 4
    pop = ease(u * 6)
    kk = max(1, int(k * (.5 + .5 * pop)))
    w = ptext_w(txt, kk)
    ptext(c.d, 80 - w // 2, 112 - kk * 3, txt, (255, 226, 90), kk, sh=(120, 40, 20))
    c.light(80, 118, 90, 60, (255, 200, 80), .5 * pop)
    # libro
    bk = sp('book', book)
    by_ = 168 + int(math.sin(t * 2) * 2) + (1 - ease(u * 3)) * 80
    if mode == 'adv':
        c.blit(bk, 80 - 17, by_)
        c.light(80, 190, 50, 50, (255, 140, 100), .3)
    else:
        for i in range(5):
            c.blit(bk, 8 + i * 28 + (i % 2) * 2, 176 + (i % 2) * 6)
    c.amb = (1, 1, 1)
    c.vig = .6
    return c.render()


# =============================================================== amanecer
def dawn(t, u):
    c = Canvas(vgrad([(0, '#1c2a66'), (.35, '#7a4a8c'), (.55, '#ff8a5a'), (.68, '#ffd070'), (1, '#ffe8a0')]))
    sy = 164 - ease(u) * 26
    c.d.ellipse([60, sy - 20, 100, sy + 20], fill=(255, 244, 190)); c.d.ellipse([66, sy - 14, 94, sy + 14], fill=(255, 252, 226))
    c.light(80, sy, 100, 100, (255, 190, 100), 1.0)
    stars(c, t, 30, 6, 60)
    # nubes
    rnd = random.Random(12)
    for i in range(6):
        x = (rnd.uniform(0, WW) + t * (3 + i)) % (WW + 60) - 30; y = rnd.uniform(60, 130)
        for j in range(4): c.d.ellipse([x + j * 8, y - (j % 2) * 3, x + j * 8 + 16, y + 6], fill=(255, 170 + i * 8, 140 + i * 10))
    # lejos
    c.d.polygon([(0, 188)] + [(x, 180 + 6 * math.sin(x / 14) + 3 * math.sin(x / 5)) for x in range(0, WW + 4, 4)] + [(WW, 230), (0, 230)], fill=(110, 70, 100))
    for (x, h) in [(8, 40), (28, 30), (132, 44), (150, 34)]:
        c.blit(sp('pineD', pine, h, snow=False), x, 188 - h + 30, tint=(50, 36, 70))
    c.d.polygon([(0, 206)] + [(x, 204 + 4 * math.sin(x / 11)) for x in range(0, WW + 4, 4)] + [(WW, 290), (0, 290)], fill=(70, 46, 76))
    c.R(0, 214, WW, 80, (50, 34, 60))
    # remolque pequeño
    c.blit(sp('trs', lambda: trailer().resize((60, 31), Image.NEAREST)), 14, 180, tint=(70, 44, 80))
    c.R(26, 192, 6, 5, (255, 214, 120), c.ed); c.R(36, 192, 6, 5, (255, 214, 120), c.ed)
    # siluetas
    sil = (40, 26, 52)
    kk = person(**KING, legs=True)
    tt = person(**TAB)
    c.blit(kk, 92, 190, tint=sil); c.blit(tt, 112, 192, tint=sil)
    # contraluz
    c.light(100, 200, 60, 70, (255, 190, 110), .6)
    c.amb = (1, 1, 1)
    c.vig = .5
    return c.render()


# =============================================================== cierre con mascota
def outro(t):
    c = Canvas(vgrad([(0, '#070a1e'), (.6, '#1c2250'), (1, '#2a2a66')]))
    stars(c, t, 100, 21, 200)
    c.light(80, 180, 120, 110, (110, 120, 240), .6)
    c.amb = (1, 1, 1)
    c.vig = .6
    return c.render()
