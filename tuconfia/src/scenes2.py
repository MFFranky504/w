"""Escenas con personajes detallados (busto grande sobre los fondos)."""
import math, random
import numpy as np
from PIL import Image, ImageDraw
from lib import *
from chars_anime import portrait, arm
from portrait2 import portrait2
from portrait3 import portrait3
import scenes as S0
from scenes import alley, trailer_night, room_base, sp  # noqa (fondos originales)

SK = {'king': (246, 206, 170), 'tab': (252, 214, 186), 'you': (242, 196, 158)}


def bust(who, expr='n', look=(0, 0), t=0.0, sc=1.3, outfit=None, cap=False):
    blink = (t % 3.4) < .12
    key = ('bust', who, expr, look, blink, sc, outfit, cap)
    if key not in S0.SPR:
        p3 = portrait3(who, expr, blink, outfit)
        S0.SPR[key] = p3.resize((p3.width * 2, p3.height * 2), Image.NEAREST)   # retrato pixel-art a x2
    return S0.SPR[key]


def _pages_sprite(w=12, h=14):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w - 1, h - 1], fill=(246, 244, 232))
    for i in range(4): d.line([(2, 3 + i * 3), (w - 3, 3 + i * 3)], fill=(120, 120, 134))
    return im


# ================================================================ cuartito
def room(t, phase='type', pages=1, thr=None):
    c = Canvas(vgrad([(0, '#241c20'), (1, '#161014')]))
    room_base(c, t)
    # papelera de la derecha
    c.R(120, 190, 18, 20, (96, 100, 120)); c.R(120, 190, 18, 2, (150, 156, 176)); c.R(122, 197, 14, 1, (66, 70, 90))
    # King (busto)
    expr = 'sad' if phase in ('lift', 'throw', 'slump') else 'n'
    look = (0, 2) if phase in ('type', 'slump') else (1, 0)
    b = bust('king', expr, look, t, 1.3)
    ytop = 76 + (2 if phase == 'slump' else 0)
    c.blit(b, 78 - b.width / 2, ytop)
    sl, sk = (198, 66, 60), SK['king']
    ph = int(t * 9) % 2
    # escritorio
    c.R(36, 172, 92, 5, (160, 112, 70)); c.R(36, 172, 92, 1, (204, 150, 96)); c.R(38, 177, 88, 40, (110, 76, 50)); c.R(40, 217, 4, 30, (80, 54, 36)); c.R(120, 217, 4, 30, (80, 54, 36))
    # hoja en la máquina
    sheet = 16 + (int(t * 3) % 5 if phase == 'type' else 2)
    c.R(72, 158 - sheet + 6, 14, sheet, (246, 244, 234)); c.R(72, 158 - sheet + 6, 14, 1, (200, 196, 190))
    for i in range(4): c.R(74, 158 - sheet + 9 + i * 3, 9, 1, (120, 120, 130))
    tw = sp('tw2', lambda: typewriter_big())
    c.blit(tw, 64, 160)
    if phase == 'type':
        arm(c, 40, 168, 70, 164 + ph * 2, 9, sl, sk); arm(c, 118, 168, 88, 164 + (1 - ph) * 2, 9, sl, sk)
    elif phase == 'lift':
        arm(c, 40, 168, 70, 166, 9, sl, sk); arm(c, 118, 170, 136, 150, 9, sl, sk, nohand=True); arm(c, 136, 150, 128, 122, 8, sl, sk, 3.6)
        c.blit(sp('pb', paper_ball, 9, (240, 238, 228)), 123, 112)
    elif phase == 'throw':
        arm(c, 40, 168, 70, 166, 9, sl, sk); arm(c, 118, 170, 138, 146, 9, sl, sk, nohand=True); arm(c, 138, 146, 134, 114, 8, sl, sk, 3.4)
    else:
        arm(c, 40, 168, 70, 168, 9, sl, sk); arm(c, 118, 168, 90, 168, 9, sl, sk)
    if pages: c.blit(sp('stk', stack_pages, max(1, pages)), 102, 163)
    # lámpara
    c.R(24, 146, 2, 26, (40, 40, 48)); c.R(15, 140, 20, 7, (230, 170, 70)); c.R(16, 146, 18, 2, (255, 240, 180), c.ed)
    c.light(26, 158, 70, 70, (255, 190, 100), 1.0)
    if thr is not None:
        tt = max(0, min(1, thr))
        if tt >= 1: c.blit(sp('pb', paper_ball, 8, (240, 238, 228)), 125, 184)
        else:
            x = 134 - 6 * tt; y = 110 + (-30 * 4 * tt * (1 - tt)) + (184 - 110) * tt
            c.blit(sp('pb', paper_ball, 9, (240, 238, 228)), x - 3 * math.sin(tt * 3), y)
    for i in range(14):
        c.d.point((40 + (i * 17) % 50 + math.sin(t + i) * 3, 110 + (i * 29) % 56), fill=(255, 226, 170))
    c.amb = (.68, .62, .68)
    c.vig = .65
    return c.render()


def typewriter_big():
    im = Image.new('RGBA', (34, 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([3, 7, 30, 19], fill=(70, 96, 90)); d.rectangle([3, 7, 30, 9], fill=(116, 148, 138))
    d.rectangle([0, 16, 33, 19], fill=(52, 72, 70)); d.rectangle([1, 4, 32, 6], fill=(40, 52, 52))
    for r, yy in enumerate((11, 14)):
        for xx in range(5, 29, 3): d.rectangle([xx, yy, xx + 1, yy + 1], fill=(228, 228, 216))
    d.rectangle([7, 0, 10, 4], fill=(30, 40, 40)); d.rectangle([24, 0, 27, 4], fill=(30, 40, 40))
    return im


# ================================================================ aula
def classroom(t):
    c = Canvas(vgrad([(0, '#3a4a40'), (1, '#2a3630')]))
    c.R(0, 0, WW, 215, (92, 108, 94))
    for x in range(0, WW, 20): c.R(x, 0, 1, 215, (80, 96, 84))
    c.R(0, 210, WW, 80, (118, 86, 58))
    for y in range(214, 284, 9): c.R(0, y, WW, 1, (96, 68, 44))
    c.R(18, 62, 124, 78, (96, 64, 40)); c.R(22, 66, 116, 70, (28, 62, 52)); c.R(22, 66, 116, 2, (20, 44, 38))
    rnd = random.Random(8)
    for i in range(7):
        y = 74 + i * 8; x = 28
        for j in range(rnd.randint(5, 11)):
            w = rnd.randint(3, 9); c.R(x, y + rnd.randint(0, 2), w, 1, (222, 230, 224)); x += w + 3
    c.R(24, 133, 112, 2, (110, 80, 52))
    c.d.ellipse([70, 24, 90, 44], fill=(240, 236, 220), outline=(40, 32, 30)); c.d.line([(80, 34), (80, 27)], fill=(30, 30, 30)); c.d.line([(80, 34), (85, 36)], fill=(30, 30, 30))
    b = bust('king', 'n', (1, 0), t, 1.3, 'teacher')
    c.blit(b, 56 - b.width / 2, 90)
    sw = math.sin(t * 6) * 2
    arm(c, 90, 172, 108 + sw, 112 + abs(sw), 9, (236, 232, 220), SK['king'], 3.2)
    c.R(int(108 + sw) + 2, int(112 + abs(sw)) - 2, 3, 2, (250, 250, 250))
    # escritorio del profesor
    c.R(0, 188, 120, 6, (150, 108, 70)); c.R(0, 188, 120, 1, (190, 140, 92)); c.R(0, 194, 120, 40, (110, 76, 50))
    c.R(14, 182, 6, 6, (210, 60, 50)); c.R(15, 180, 2, 2, (60, 120, 50))
    c.R(40, 183, 16, 5, (230, 230, 220)); c.R(70, 182, 8, 6, (250, 250, 250))
    for i in range(6):
        ph = (t * .8 + i * .17) % 1
        c.d.point((106 + (i * 3) % 7 + ph * 4, 118 + ph * 40), fill=(230, 232, 226))
    c.light(70, 90, 100, 90, (255, 236, 190), .35)
    c.amb = (.95, .95, .88)
    c.vig = .5
    return c.render()


# ================================================================ cafetería
def donut_shop(t):
    c = Canvas(vgrad([(0, '#1a1030'), (1, '#10142a')]))
    c.R(0, 0, WW, 92, (24, 22, 52))
    c.R(6, 30, 148, 56, (12, 20, 48)); c.R(6, 30, 148, 2, (200, 170, 130)); c.R(6, 84, 148, 2, (200, 170, 130)); c.R(78, 30, 3, 56, (200, 170, 130))
    stars(c, t, 20, 5, 70)
    flick = 1 if (int(t * 12) % 23 != 0) else 0
    col = (255, 90, 170) if flick else (120, 50, 90)
    c.R(40, 6, 80, 20, (20, 10, 26)); c.R(40, 6, 80, 1, col, c.ed); c.R(40, 25, 80, 1, col, c.ed); c.R(40, 6, 1, 20, col, c.ed); c.R(119, 6, 1, 20, col, c.ed)
    ptext(c.ed, 52, 11, 'DONAS', col, 3)
    c.light(80, 16, 80, 40, (255, 70, 160), .55 * flick + .15)
    c.R(0, 92, WW, 80, (232, 196, 190))
    for x in range(0, WW, 12): c.R(x, 92, 1, 80, (214, 176, 172))
    c.R(0, 172, WW, 112, (60, 50, 76))
    for yy in range(0, 112, 12):
        for xx in range(0, WW, 12):
            if ((xx // 12) + (yy // 12)) % 2 == 0: c.R(xx, 172 + yy, 12, 12, (230, 226, 232))
    c.d.ellipse([16, 100, 28, 112], fill=(250, 250, 240), outline=(40, 30, 30)); c.d.line([(22, 106), (22, 101)], fill=(30, 30, 30)); c.d.line([(22, 106), (19, 109)], fill=(30, 30, 30))
    # cafetera detrás
    c.R(128, 118, 16, 50, (60, 60, 76)); c.R(130, 130, 12, 14, (190, 80, 50)); c.R(130, 130, 12, 2, (240, 140, 90))
    # Tabitha
    b = bust('tab', 'n', (-1, 1), t, 1.25, 'uniform', True)
    c.blit(b, 96 - b.width / 2, 88)
    # mostrador
    c.R(0, 170, WW, 14, (255, 140, 180)); c.R(0, 170, WW, 2, (255, 210, 226)); c.R(0, 184, WW, 56, (240, 240, 246)); c.R(0, 184, WW, 2, (200, 200, 214))
    # vitrina
    c.R(8, 136, 62, 34, (150, 190, 220)); c.R(8, 136, 62, 2, (230, 244, 255))
    rnd = random.Random(2)
    cols = [(222, 120, 150), (120, 70, 50), (250, 230, 130), (130, 200, 170)]
    for r in range(2):
        for i in range(6):
            x = 12 + i * 10; y = 144 + r * 12; cc = cols[(i + r) % 4]
            c.d.ellipse([x, y, x + 7, y + 6], fill=cc); c.d.rectangle([x + 3, y + 2, x + 4, y + 3], fill=(40, 30, 40))
            for _ in range(3): c.d.point((x + rnd.randint(0, 7), y + rnd.randint(0, 3)), fill=(255, 255, 255))
    # manos con taza
    sw = math.sin(t * 2) * 1.5
    c.R(114, 160, 8, 9, (250, 250, 250)); c.R(122, 162, 2, 4, (250, 250, 250)); c.R(115, 161, 6, 2, (110, 70, 50))
    c.d.ellipse([108, 164 + sw, 116, 170 + sw], fill=SK['tab'])
    for i in range(3):
        ph = (t + i / 3) % 1; c.d.point((118 + math.sin(ph * 8) * 2, 158 - ph * 14), fill=(230, 230, 240))
    c.light(96, 120, 110, 90, (255, 200, 220), .3)
    c.amb = (.8, .76, .92)
    c.vig = .55
    return c.render()


# ================================================================ retratos grandes
def portrait_scene(t, who='king', expr='n', look=(0, 0), tone='cold', pages_in=False, sparkle=False, outfit=None, tag=None):
    if tone == 'cold': g = vgrad([(0, '#0a1a2a'), (1, '#1c2c44')]); amb = (.9, .94, 1)
    elif tone == 'warm': g = vgrad([(0, '#3a1e10'), (.5, '#a05a28'), (1, '#e0a040')]); amb = (1, .95, .88)
    else: g = vgrad([(0, '#2a1840'), (1, '#6a3a60')]); amb = (1, 1, 1)
    c = Canvas(g)
    base = np.array(g[100, 0])
    for i in range(14):
        a = i / 14 * math.pi * 2 + t * .15
        c.d.polygon([(80, 120), (80 + 220 * math.cos(a), 120 + 220 * math.sin(a)), (80 + 220 * math.cos(a + .18), 120 + 220 * math.sin(a + .18))], fill=tuple(int(v) for v in base * 1.12 + 6))
    b = bust(who, expr, look, t, 1.75, outfit)
    bob = math.sin(t * 1.8) * 1.2
    c.blit(b, 80 - b.width / 2, 100 + bob)
    if pages_in:
        pg = Image.new('RGBA', (70, 44), (0, 0, 0, 0)); d = ImageDraw.Draw(pg)
        d.polygon([(6, 42), (14, 0), (64, 4), (66, 44)], fill=(246, 244, 232))
        for i in range(6): d.line([(18 - i // 2, 8 + i * 6), (58, 10 + i * 6)], fill=(120, 120, 134))
        c.blit(pg, 44, 194 + math.sin(t * 2) * 1)
    if sparkle:
        for i in range(12):
            ph = (t * .7 + i * .09) % 1
            x = 14 + (i * 53) % 132; y = 255 - ph * 215
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)): c.d.point((x + dx, y + dy), fill=(255, 232, 160))
    if tag:
        w = ptext_w(tag, 2)
        c.R(80 - w // 2 - 5, 236, w + 10, 18, (20, 10, 26)); c.R(80 - w // 2 - 5, 236, w + 10, 2, (255, 216, 74))
        ptext(c.d, 80 - w // 2, 242, tag, (255, 255, 255), 2)
    c.light(80, 120, 80, 100, (255, 210, 150) if tone != 'cold' else (120, 160, 230), .35)
    c.amb = amb
    c.vig = .8
    return c.render()


# ================================================================ mañana
def morning(t, u):
    c = Canvas(vgrad([(0, '#3a2a28'), (1, '#241a18')]))
    room_base(c, t, True)
    c.R(36, 172, 92, 5, (160, 112, 70)); c.R(38, 177, 88, 40, (110, 76, 50))
    k = ease(u * 1.5)
    lift = ease((u - .35) * 1.8)
    b = bust('tab', 'n', (0, 2), t, 1.3, 'cardigan')
    c.blit(b, 80 - b.width / 2 + (1 - k) * 40, 102 + (1 - ease(u * 2)) * 6)
    # hoja que sale de la papelera
    py = 206 - lift * 44
    sl, sk = (226, 172, 70), SK['tab']
    if u > .3:
        c.R(70, int(py), 18, 22, (246, 244, 232)); c.R(70, int(py), 18, 1, (180, 176, 168))
        for i in range(4): c.R(73, int(py) + 4 + i * 4, 12, 1, (120, 120, 134))
    arm(c, 44 + (1 - k) * 40, 176, 70, int(py) + 14, 9, sl, sk); arm(c, 118 + (1 - k) * 40, 176, 90, int(py) + 14, 9, sl, sk)
    # papelera al frente
    bn = sp('can3', trash_can, 40, 46)
    c.blit(bn, 60, 206)
    for (dx, dy, s) in [(4, -4, 12), (16, -8, 13), (26, -3, 10)]:
        c.blit(sp('pb', paper_ball, s, (222, 220, 210)), 60 + dx, 206 + dy)
    if u > .35:
        for i in range(14):
            ph = (u * 1.5 + i * .09) % 1
            c.d.point((66 + (i * 5) % 30 + math.sin(ph * 9) * 2, py + 10 + ph * 30), fill=(110, 110, 120))
    c.light(130, 100, 90, 110, (255, 220, 150), .55)
    c.amb = (.88, .82, .8)
    c.vig = .6
    return c.render()


# ================================================================ dinero / libro
def payoff(t, u, mode='adv'):
    c = Canvas(vgrad([(0, '#1a0e32'), (1, '#4a1a52')]))
    n = 18
    for i in range(n):
        a = i / n * 6.28 + t * .25
        if i % 2 == 0:
            c.d.polygon([(80, 130), (80 + 260 * math.cos(a), 130 + 260 * math.sin(a)), (80 + 260 * math.cos(a + 6.28 / n), 130 + 260 * math.sin(a + 6.28 / n))], fill=(110, 40, 90))
    rnd = random.Random(9)
    for i in range(34 if mode == 'big' else 16):
        x = rnd.uniform(0, WW); y0 = rnd.uniform(0, WH); s_ = rnd.uniform(40, 90)
        y = (y0 + t * s_) % (WH + 20) - 10
        if i % 2 == 0:
            c.R(int(x), int(y), 9, 5, (60, 170, 90)); c.R(int(x), int(y), 9, 1, (120, 220, 140)); c.R(int(x) + 4, int(y) + 2, 1, 1, (20, 70, 40))
        else:
            c.d.ellipse([x, y, x + 5, y + 5], fill=(255, 210, 60)); c.d.point((x + 2, y + 2), fill=(255, 250, 180))
    pop = ease(u * 5)
    if mode == 'book':
        bk = sp('book', book).resize((102, 144), Image.NEAREST)
        bob = math.sin(t * 2.4) * 3
        c.light(80, 140, 80, 90, (255, 150, 110), .6 * pop)
        c.blit(bk, 80 - 51, 80 + bob + (1 - pop) * 120)
        for i in range(10):
            ph = (t * .8 + i * .1) % 1; x = 30 + (i * 37) % 100; y = 230 - ph * 160
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)): c.d.point((x + dx, y + dy), fill=(255, 230, 170))
    else:
        txt = '$2.500' if mode == 'adv' else '$400.000'
        k = 5 if mode == 'adv' else 4
        kk = max(1, int(k * (.4 + .6 * pop)))
        w = ptext_w(txt, kk)
        ptext(c.d, 80 - w // 2, 128 - kk * 3, txt, (255, 226, 90), kk, sh=(120, 40, 20))
        c.light(80, 128, 90, 60, (255, 200, 80), .5 * pop)
        sub = 'ANTICIPO' if mode == 'adv' else 'DERECHOS'
        ws = ptext_w(sub, 2)
        ptext(c.d, 80 - ws // 2, 160 + kk, sub, (255, 255, 255), 2, sh=(40, 10, 40))
    c.amb = (1, 1, 1)
    c.vig = .6
    return c.render()


# ================================================================ amanecer
def dawn(t, u):
    c = Canvas(vgrad([(0, '#1c2a66'), (.35, '#7a4a8c'), (.55, '#ff8a5a'), (.68, '#ffd070'), (1, '#ffe8a0')]))
    sy = 168 - ease(u) * 30
    c.d.ellipse([62, sy - 18, 98, sy + 18], fill=(255, 244, 190)); c.d.ellipse([68, sy - 12, 92, sy + 12], fill=(255, 252, 226))
    c.light(80, sy, 100, 100, (255, 190, 100), .8)
    stars(c, t, 30, 6, 60)
    rnd = random.Random(12)
    for i in range(6):
        x = (rnd.uniform(0, WW) + t * (3 + i)) % (WW + 60) - 30; y = rnd.uniform(60, 130)
        for j in range(4): c.d.ellipse([x + j * 8, y - (j % 2) * 3, x + j * 8 + 16, y + 6], fill=(255, 170 + i * 8, 140 + i * 10))
    c.d.polygon([(0, 188)] + [(x, 180 + 6 * math.sin(x / 14) + 3 * math.sin(x / 5)) for x in range(0, WW + 4, 4)] + [(WW, 230), (0, 230)], fill=(110, 70, 100))
    for (x, h) in [(8, 40), (28, 30), (132, 44), (150, 34)]:
        c.blit(sp('pineD', pine, h, snow=False), x, 188 - h + 30, tint=(50, 36, 70))
    c.d.polygon([(0, 206)] + [(x, 204 + 4 * math.sin(x / 11)) for x in range(0, WW + 4, 4)] + [(WW, 290), (0, 290)], fill=(70, 46, 76))
    c.R(0, 214, WW, 80, (50, 34, 60))
    c.blit(sp('trs2', lambda: trailer().resize((84, 44), Image.NEAREST)), 38, 176, tint=(70, 44, 80))
    c.R(52, 190, 8, 7, (255, 214, 120), c.ed); c.R(66, 190, 8, 7, (255, 214, 120), c.ed); c.R(86, 190, 8, 7, (255, 214, 120), c.ed)
    c.R(58, 168, 5, 8, (60, 44, 70))
    for i in range(6):
        ph = (t * .4 + i / 6) % 1
        c.d.ellipse([60 + ph * 14, 168 - ph * 40, 64 + ph * 14 + ph * 4, 172 - ph * 40], fill=(200, 150, 150))
    c.light(100, 200, 60, 70, (255, 190, 110), .5)
    c.amb = (1, 1, 1)
    c.vig = .5
    return c.render()


# ================================================================ final: "tú"
def final_you(t, u):
    c = Canvas(vgrad([(0, '#080b1c'), (.5, '#171c3a'), (1, '#0c0c18')]))
    S0.bricks(c, 40, 210)
    c.R(0, 206, WW, 80, (30, 32, 48))
    for x in range(0, WW, 14): c.R(x, 208 + (x // 14 % 3) * 9, 12, 1, (40, 44, 64))
    c.R(34, 214, 64, 12, (46, 56, 94)); c.R(40, 216, 52, 1, (70, 86, 130))
    c.R(116, 176, 28, 30, (44, 70, 80)); c.R(116, 176, 28, 3, (70, 104, 112)); c.R(8, 190, 14, 16, (88, 66, 52)); c.R(8, 190, 14, 2, (118, 90, 70))
    c.R(23, 70, 3, 138, (34, 36, 54)); c.R(23, 70, 14, 3, (34, 36, 54)); c.R(33, 72, 7, 3, (250, 220, 150), c.ed)
    c.light(36, 78, 70, 100, (230, 170, 80), .55)
    c.light(82, 150, 55, 70, (255, 210, 130), .5)
    # tú
    rel = ease((u - .9) / .1) if u > .9 else 0
    expr = 'wow' if u < .35 else 'worry'
    look = (0, 0)
    b = bust('you', expr, look, t, 1.3)
    c.blit(b, 80 - b.width / 2, 110)
    sl, sk = C('#4c5cc8'), SK['you']
    tremble = math.sin(t * 25) * .8 if rel == 0 else 0
    hx, hy = 112 + tremble, 164
    arm(c, 126, 186, hx + 2, hy + 4, 10, sl, sk, 3.6)
    # papel en la mano / cayendo
    if rel == 0:
        c.blit(sp('pb', paper_ball, 11, (246, 244, 236)), hx - 5, hy - 10)
    else:
        c.blit(sp('pb', paper_ball, 11, (246, 244, 236)), hx - 5 - 30 * rel, hy - 10 + rel * rel * 20 - 14 * rel * (1 - rel))
    # papelera delante
    c.blit(sp('can', trash_can), 70, 178)
    for (dx, dy, s) in [(3, -3, 7), (9, -5, 8), (14, -2, 6)]:
        c.blit(sp('pb', paper_ball, s, (200, 198, 190)), 70 + dx, 178 + dy)
    # etiqueta TÚ
    bob = math.sin(t * 3) * 1.5
    c.R(60, 66 + bob, 40, 20, (255, 216, 74)); c.R(60, 66 + bob, 40, 2, (255, 244, 170)); c.R(60, 84 + bob, 40, 2, (190, 150, 30))
    ptext(c.d, 66, 72 + bob, 'TU', (20, 10, 26), 3)
    c.R(68, 69 + bob, 3, 2, (20, 10, 26))   # tilde de la Ú
    c.d.polygon([(76, 86 + bob), (84, 86 + bob), (80, 94 + bob)], fill=(255, 216, 74))
    rain(c, t, 80, 11)
    c.amb = (.62, .68, .9)
    c.vig = .7
    return c.render()
