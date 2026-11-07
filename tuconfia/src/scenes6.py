"""Historia 5 (J. K. Rowling): del fondo a la saga. Sprites nativos (1 px del sprite = 1 px del mundo) sobre fondos con detalle."""
import math, random
import numpy as np
from PIL import Image, ImageDraw
from lib import *
import bg
import props as PR
from scenes3 import rpg, place
from scenes5 import bubble, _sign


def top_half(img, f=.72):
    return img.crop((0, 0, img.width, int(img.height * f)))


# ============================================================ 1. calle de Edimburgo, noche de lluvia (hook)
def street(t, u):
    c = Canvas(vgrad([(0, '#0c1850'), (.3, '#24409a'), (.5, '#6a4eb0'), (.66, '#d0709a'), (.78, '#2a2250'), (1, '#161224')]))
    stars(c, t, 50, 5, 80)
    c.d.ellipse([122, 26, 140, 44], fill=(248, 244, 214)); c.d.ellipse([127, 24, 145, 42], fill=(36, 64, 154))     # luna creciente
    bg.castle_sil(c, 128, col=(40, 30, 88))                                                                       # castillo sobre la roca
    bg.house(c, -6, 108, 50, 100, (150, 82, 70), (60, 52, 110), seed=11, lit=.5)
    bg.house(c, 116, 112, 50, 96, (130, 92, 76), (70, 58, 116), seed=12, lit=.45)
    bg.cobble(c, 0, 206, WW, 90, base=(84, 84, 138), seed=7)
    c.R(0, 204, WW, 3, (150, 140, 196)); c.R(0, 207, WW, 1, (60, 56, 100))                                         # bordillo
    bg.puddle_reflections(c, 214, 40, t)
    # cartel de café colgando de un brazo de hierro
    c.R(112, 150, 14, 2, (30, 30, 50)); c.R(124, 150, 2, 10, (30, 30, 50)); _sign(c, 108, 160, 'CAFE', (255, 176, 96), 3)
    bg.lamp_post(c, 56, 206, t, h=70)
    bg.lamp_post(c, 104, 206, t + .4, h=60)
    x = 36 + 54 * ease(u * 1.05)
    step = int(t * 4) % 2
    PR.keep(c, PR.stroller(), x + 17, 206 - 44 + int(math.sin(t * 8) > .6))
    place(c, rpg('rowling_rain', step), x, 212)
    rain(c, t, 150, 3, 180)
    fl = .3 if int(t * 10) % 41 == 0 else 0
    c.amb = (.84 + fl, .88 + fl, 1.1 + fl); c.vig = .7
    return c.render()


# ============================================================ 2. el piso (sin trabajo, cuna, facturas)
def flat(t, u):
    c = Canvas(vgrad([(0, '#2a2a46'), (1, '#1a1a2c')]))
    bg.wallpaper(c, 0, 0, WW, 200, (84, 96, 156), (74, 86, 146), (110, 126, 190))
    c.R(0, 176, WW, 24, (110, 74, 54)); c.R(0, 176, WW, 2, (200, 150, 104)); c.R(0, 198, WW, 2, (60, 40, 32))        # zócalo de madera
    bg.planks(c, 0, 200, WW, 100, (122, 80, 58), seed=21, pw=8)
    bg.window(c, 100, 78, 36, 52, t=t, curtain=(196, 72, 96), seed=3)                                              # ventana con cortinas y lluvia
    sw = math.sin(t * 2) * 3                                                                                       # bombilla que se balancea y parpadea
    c.R(40, 0, 1, 56, (20, 20, 30)); c.d.ellipse([36 + sw, 56, 46 + sw, 66], fill=(255, 232, 150) if int(t * 7) % 9 else (130, 110, 80))
    c.light(41 + sw, 62, 64, 64, (255, 214, 130), .9 if int(t * 7) % 9 else .25)
    # cuadro torcido, perchero y caja de mudanza
    c.R(16, 70, 22, 18, (70, 44, 34)); c.R(18, 72, 18, 14, (126, 170, 120)); c.R(18, 80, 18, 6, (190, 150, 90)); c.R(21, 75, 5, 5, (250, 220, 120))
    c.R(150, 96, 2, 80, (60, 44, 40)); c.R(146, 96, 10, 2, (60, 44, 40)); c.R(145, 108, 4, 6, (190, 70, 70))
    # mesa con facturas rojas que van llegando
    c.R(14, 160, 74, 5, (170, 118, 76)); c.R(14, 160, 74, 1, (230, 180, 124)); c.R(18, 165, 5, 36, (110, 72, 50)); c.R(79, 165, 5, 36, (110, 72, 50)); c.R(18, 186, 66, 3, (126, 84, 58))
    for i in range(5):
        k = ease((u * 3 - i * .22) / .3)
        if k > 0: PR.keep(c, PR.bill_red(), 18 + i * 13, 146 - (i % 2) * 2 - int((1 - k) * 40))
    PR.keep(c, PR.lamp_table(), 20, 134)
    PR.keep(c, PR.baby_crib(), 100, 158)                                   # cuna con bebé
    zz = (t * 1.2) % 1; ptext(c.ed, 140 + int(zz * 4), 142 - int(zz * 12), 'Z', (200, 220, 255), 2)
    PR.keep(c, PR.barrel(), 134, 184)
    if u > .42:
        k = ease((u - .42) / .08); kk = max(2, int(5 - 3 * k)); w = ptext_w('SIN TRABAJO', kk)
        c.R(80 - w // 2 - 4, 40 - 4, w + 8, 5 * kk + 8, (60, 16, 28)); ptext(c.ed, 80 - w // 2, 40, 'SIN TRABAJO', (255, 70, 80), kk)
    b = 1.5 * max(0, math.sin(t * 2))
    place(c, rpg('rowling', 0), 74, 212 + b)
    c.amb = (.92, .92, 1.06); c.vig = .75
    return c.render()


# ============================================================ 4. la cafetería (escribe mientras la niña duerme)
def cafe(t, u):
    c = Canvas(vgrad([(0, '#4a2a1e'), (1, '#2a160e')]))
    bg.brick(c, 0, 0, WW, 150, base=(172, 92, 66), mortar=(84, 46, 40), seed=31)
    c.R(0, 118, WW, 4, (240, 190, 110)); bg.planks(c, 0, 122, WW, 80, (130, 82, 52), seed=32, horizontal=False, pw=8)      # friso de madera
    bg.window(c, 14, 62, 44, 50, t=t, curtain=(230, 150, 70), seed=5, lights=True)
    bg.shelf(c, 96, 52, 52, 56, seed=9, rows=2, pal=((236, 120, 60), (240, 196, 70), (200, 80, 90), (90, 170, 120)))
    for lx in (78, 128):                                                                                           # lámparas colgantes
        sw = math.sin(t * 1.7 + lx) * 1.2
        c.R(lx, 0, 1, 34, (30, 20, 20)); PR.keep(c, PR.pendant((255, 196, 96)), lx - 9 + sw, 34)
        c.light(lx + sw, 52, 36, 32, (255, 200, 110), .85)
    # pizarra del menú
    c.R(64, 82, 24, 22, (60, 44, 36)); c.R(66, 84, 20, 18, (36, 56, 52)); ptext(c.d, 69, 87, 'CAFE', (250, 240, 200), 2); c.R(69, 96, 14, 1, (250, 240, 200)); c.R(69, 98, 10, 1, (250, 240, 200))
    bg.planks(c, 0, 202, WW, 100, (110, 68, 46), seed=33, pw=9)
    c.R(0, 200, WW, 3, (60, 38, 30))
    PR.keep(c, PR.plant(), 136, 176)
    # mesa redonda con Rowling sentada (la mesa tapa las piernas)
    place(c, top_half(rpg('rowling', 0), .74), 56, 176, sh=False)
    c.R(26, 170, 62, 6, (160, 108, 70)); c.R(26, 170, 62, 2, (222, 164, 112)); c.R(54, 176, 6, 26, (110, 72, 46)); c.R(42, 200, 30, 3, (110, 72, 46))
    PR.keep(c, PR.teacup(), 70, 158)
    for i in range(3):
        ph = (t * .8 + i * .33) % 1; c.R(75 + int(math.sin(t * 3 + i) * 1.5), 154 - int(ph * 12), 1, 2, (255, 255, 255))
    c.R(30, 164, 24, 6, (250, 244, 224)); c.R(30, 164, 24, 1, (210, 200, 176))                                       # cuaderno
    n = int(u * 14)
    for i in range(n): c.R(32 + (i % 3) * 7, 166 + (i // 7), 5, 1, (40, 40, 100))
    px = 34 + (t * 14) % 14; c.R(px, 160 + int(math.sin(t * 12) * 1), 1, 5, (30, 30, 80))
    PR.keep(c, PR.stroller(), 104, 164)
    zz = (t * 1.1) % 1; ptext(c.ed, 124 + int(zz * 4), 156 - int(zz * 10), 'Z', (200, 220, 255), 2)
    c.light(56, 156, 56, 46, (255, 210, 130), .3)
    c.amb = (1.02, .93, .86); c.vig = .7
    return c.render()


# ============================================================ 5. doce rechazos
def rejections(t, u):
    c = Canvas(vgrad([(0, '#2a1a3a'), (1, '#140c1e')]))
    bg.wallpaper(c, 0, 0, WW, 206, (66, 46, 96), (58, 40, 86), (92, 70, 132))
    # armario de casilleros de madera (6 x 2)
    c.R(6, 78, 148, 68, (86, 54, 38)); c.R(6, 78, 148, 3, (190, 130, 90)); c.R(4, 144, 152, 4, (60, 38, 28))
    for i in range(6):
        for j in range(2):
            sx, sy = 9 + i * 24, 82 + j * 31
            c.R(sx, sy, 22, 28, (34, 22, 26)); c.R(sx, sy, 22, 1, (20, 12, 16)); c.R(sx, sy + 27, 22, 1, (176, 120, 80))
    for idx in range(12):
        col_, row_ = idx % 6, idx // 6
        sx, sy = 9 + col_ * 24, 82 + row_ * 31
        k = ease((u * 14 - idx) / 1.2)
        if k <= 0: continue
        off = int((1 - k) * 70)
        PR.keep(c, PR.envelope(20, 14), sx + 1, sy + 12 - off)
        if k >= 1 and ease((u * 14 - idx - 1.2) / .6) > 0: ptext(c.ed, sx + 4, sy + 18, 'NO', (230, 40, 60), 2)
    n = min(12, int(u * 14))
    w = ptext_w(str(n), 6)
    c.R(80 - 34, 38, 68, 36, (20, 12, 30)); c.R(80 - 34, 38, 68, 2, (250, 200, 90)); c.R(80 - 34, 72, 68, 2, (140, 100, 40)); ptext(c.ed, 80 - w // 2, 46, str(n), (255, 216, 74), 6)
    bg.planks(c, 0, 206, WW, 90, (90, 58, 52), seed=41, pw=9); c.R(0, 204, WW, 3, (40, 26, 30))
    place(c, rpg('rowling_rain', int(t * 3) % 2 if u < .3 else 0), 80, 214 + math.sin(t * 2))
    c.light(80, 130, 90, 80, (200, 140, 255), .35)
    c.amb = (.92, .88, 1.05); c.vig = .8
    return c.render()


# ============================================================ 6. la niña que pidió el siguiente capítulo
def alice(t, u):
    c = Canvas(vgrad([(0, '#3a2018'), (1, '#24120e')]))
    bg.wallpaper(c, 0, 0, WW, 206, (150, 78, 70), (138, 68, 62), (176, 104, 90))
    bg.shelf(c, 8, 40, 60, 100, seed=51, rows=3); bg.shelf(c, 92, 40, 60, 100, seed=52, rows=3)
    c.R(70, 40, 20, 100, (96, 60, 44))                                                                              # cuadro entre las estanterías
    c.R(72, 46, 16, 22, (40, 40, 70)); c.R(74, 48, 12, 18, (240, 190, 90)); c.R(78, 52, 4, 10, (90, 60, 140))
    c.R(0, 150, WW, 2, (240, 190, 120))
    bg.planks(c, 0, 152, WW, 150, (150, 92, 60), seed=53, pw=9)
    c.R(20, 226, 120, 26, (186, 66, 80)); c.R(20, 226, 120, 2, (240, 130, 140)); c.R(24, 230, 112, 18, (150, 46, 66))
    for xx in range(28, 136, 12): c.R(xx, 236, 6, 2, (250, 210, 140))                                              # alfombra con motivo
    PR.keep(c, PR.lamp_table(), 128, 128); c.light(136, 136, 50, 40, (255, 214, 130), .9)
    PR.keep(c, PR.plant(), 6, 128)
    place(c, rpg('rexach', 0, 'blazer'), 36, 212)
    sway = math.sin(t * 2) * .8
    PR.keep(c, PR.armchair(), 62, 176)
    place(c, top_half(rpg('alice', 0), .74), 82, 192 + sway, sh=False)
    pg = ease(u * 3)
    for i in range(3):
        PR.keep(c, PR.stamp_paper(), 71 + i * 4, 186 - int(pg * 3) - i)                                              # páginas del manuscrito
    if u > .25: ptext(c.ed, 22, 120 - int(((u - .25) * 8) % 2), '?', (255, 220, 90), 3)
    if u > .5: bubble(c, 100, 118 - int(2 * ease((u - .5) / .1)), 'MAS!', 3)
    for i in range(10):
        ph = (t * .5 + i * .1) % 1; xx = 60 + i * 5 + math.sin(t * 3 + i) * 4; yy = 190 - ph * 70
        c.R(xx, yy, 2, 2, (255, 236, 160))
    c.amb = (1.03, .94, .88); c.vig = .65
    return c.render()


# ============================================================ 7. 1997: la librería
def bookstore(t, u):
    c = Canvas(vgrad([(0, '#2a1a5a'), (.5, '#c04a8a'), (1, '#ffb060')]))
    bg.wallpaper(c, 0, 0, WW, 206, (176, 74, 120), (164, 66, 110), (210, 120, 150))
    for i in range(14):                                                                                             # rayos de fiesta
        a = i / 14 * math.pi * 2 + t * .2
        c.d.polygon([(80, 130), (80 + 260 * math.cos(a), 130 + 260 * math.sin(a)), (80 + 260 * math.cos(a + .12), 130 + 260 * math.sin(a + .12))], fill=(214, 110, 146))
    bg.shelf(c, 4, 60, 34, 120, seed=61, rows=4); bg.shelf(c, 122, 60, 34, 120, seed=62, rows=4)
    w = ptext_w('1997', 6)
    c.R(80 - w // 2 - 6, 54, w + 12, 40, (50, 20, 70)); c.R(80 - w // 2 - 6, 54, w + 12, 2, (255, 220, 100)); ptext(c.ed, 80 - w // 2, 60, '1997', (255, 240, 120), 6)
    # tablero de baldosas y mesa de novedades con torres de libros
    for yy in range(206, 296, 10):
        for xx in range(-(yy // 10 % 2) * 10, WW, 20): c.R(xx, yy, 10, 10, (236, 226, 206)); c.R(xx + 10, yy, 10, 10, (150, 70, 80))
    c.R(0, 204, WW, 3, (90, 50, 40))
    c.R(40, 168, 80, 6, (176, 112, 70)); c.R(40, 168, 80, 1, (240, 190, 130)); c.R(44, 174, 72, 30, (110, 68, 50)); c.R(44, 174, 72, 1, (150, 100, 70))
    n = 1 + int(ease(u * 1.4) * 7); cols = ((220, 70, 90), (70, 120, 220), (240, 196, 70), (90, 176, 110))
    for i in range(n): PR.keep(c, PR.book_closed(cols[i % 4], 26 - i * 2, 7, False), 80 - (26 - i * 2) // 2, 168 - (i + 1) * 7)
    for k, xx in enumerate((50, 104)):
        for i in range(3 + k): PR.keep(c, PR.book_closed(cols[(i + k) % 4], 20, 7, False), xx, 168 - (i + 1) * 7)
    cast = ('kid_a', 'kid_b', 'kid_c', 'alice')
    for i, w_ in enumerate(cast):
        xx = (24 + i * 36 + t * 14) % 200 - 20
        place(c, rpg(w_, int(t * 4 + i) % 2), xx, 218, sh=False)
    cols2 = ((255, 90, 120), (90, 220, 255), (255, 230, 90), (140, 255, 140))
    for i in range(34):
        ph = (t * .5 + i * .03) % 1; xx = (i * 53 + math.sin(t * 3 + i) * 6) % 150 + 4; yy = ph * 270
        c.R(xx, yy, 2, 3, cols2[i % 4])
    c.light(80, 140, 90, 90, (255, 220, 150), .5)
    c.amb = (1.03, .98, .98); c.vig = .55
    return c.render()


# ============================================================ 9. el libro en blanco al amanecer
def finale(t, u):
    k = ease(u * 1.1)
    c = Canvas(vgrad([(0, '#1a1a5a'), (.35, '#c0408a'), (.55, '#ff9a50'), (.75, '#ffd080'), (1, '#3a2438')]))
    sy = 126 - 30 * k
    c.d.ellipse([62, sy - 22, 98, sy + 18], fill=(255, 244, 180))
    for i in range(12):
        a = i / 12 * math.pi * 2 + t * .15
        c.d.polygon([(80, sy), (80 + 200 * math.cos(a), sy + 200 * math.sin(a)), (80 + 200 * math.cos(a + .1), sy + 200 * math.sin(a + .1))], fill=(255, 206, 140))
    bg.castle_sil(c, 128, col=(78, 44, 96))
    bg.house(c, -10, 120, 42, 70, (150, 80, 76), (80, 50, 110), seed=71, lit=.2, chimneys=True)
    bg.house(c, 128, 124, 44, 66, (140, 86, 80), (84, 54, 114), seed=72, lit=.2)
    # marco de la ventana con cortinas
    c.R(0, 0, 8, 190, (120, 70, 56)); c.R(152, 0, 8, 190, (120, 70, 56))
    for kx in range(8):
        col = (200, 70, 100) if kx % 2 else (170, 50, 84)
        c.R(8 + kx, 0, 1, 190, col); c.R(151 - kx, 0, 1, 190, col)
    bg.planks(c, 0, 186, WW, 120, (110, 66, 50), seed=73, pw=8)
    c.R(0, 184, WW, 3, (200, 140, 100))
    # escritorio con el libro enorme abierto y brillante
    c.R(14, 160, 132, 8, (176, 112, 74)); c.R(14, 160, 132, 2, (236, 176, 124)); c.R(14, 168, 132, 22, (116, 70, 50)); c.R(14, 168, 132, 2, (90, 52, 40))
    book = PR.book_open(96, 34, 7)
    PR.keep(c, book, 40, 128)
    nl = int(ease((u - .15) / .6) * 7)
    for i in range(nl): c.R(84, 138 + i * 3 - 3, 32 - (i * 5) % 12, 1, (60, 50, 110))
    fl = (t * .6) % 1
    if fl < .5: c.d.polygon([(88, 130), (88 + 40 * math.sin(fl * math.pi), 128 - 8 * math.sin(fl * math.pi)), (88 + 40 * math.sin(fl * math.pi), 150 - 6 * math.sin(fl * math.pi)), (88, 154)], fill=(255, 252, 244))
    c.light(88, 140, 80, 50, (255, 230, 150), 1.0)
    PR.keep(c, PR.lamp_table(), 18, 134); PR.keep(c, PR.plant(), 124, 130)
    place(c, top_half(rpg('you', 0), .8), 30, 162, sh=False)
    c.R(14, 160, 132, 8, (176, 112, 74)); c.R(14, 160, 132, 2, (236, 176, 124))
    for i in range(16):
        ph = (t * .45 + i * .063) % 1; xx = 44 + (i * 37 + math.sin(t * 2 + i) * 5) % 90; yy = 156 - ph * 110
        c.R(xx, yy, 2, 2, (255, 236, 170))
    c.amb = (1.0 + .06 * k, .94 + .08 * k, .95); c.vig = .6
    return c.render()
