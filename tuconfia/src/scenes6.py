"""Historia 5 (J. K. Rowling): del fondo a la saga. Sprites nativos (1 px del sprite = 1 px del mundo) sobre fondos con detalle."""
import math, random
import numpy as np
from PIL import Image, ImageDraw
from lib import *
import bg
import props as PR
from scenes3 import rpg, place
from scenes5 import bubble, _sign
from scenes3 import bat


def top_half(img, f=.72):
    return img.crop((0, 0, img.width, int(img.height * f)))


# ============================================================ 1. calle de Edimburgo, noche de lluvia (hook)
def street_wide(t, u):
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
    c.R(112, 150, 14, 2, (30, 30, 50)); c.R(124, 150, 2, 10, (30, 30, 50)); bg.sign2(c, 122, 120, 'CAFE', (255, 176, 96), 16)
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
def flat_wide(t, u):
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
    zz = (t * 1.2) % 1; bg.wtext(c, 140 + int(zz * 4), 134 - int(zz * 12), 'Z', (200, 220, 255), 8, outline=None)
    PR.keep(c, PR.barrel(), 134, 184)
    if u > .42:
        bg.sign2(c, 80, 66, 'SIN EMPLEO', (255, 70, 80), 16, plate=(50, 14, 26))
    b = 1.5 * max(0, math.sin(t * 2))
    place(c, rpg('rowling', 0), 74, 212 + b)
    c.amb = (.92, .92, 1.06); c.vig = .75
    return c.render()


# ============================================================ 4. la cafetería (escribe mientras la niña duerme)
def cafe_wide(t, u):
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
    c.R(60, 78, 54, 30, (60, 44, 36)); c.R(62, 80, 50, 26, (36, 56, 52)); bg.wtext(c, 87, 82, 'CAFE', (250, 240, 200), 16, outline=None, center=True)
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
    zz = (t * 1.1) % 1; bg.wtext(c, 124 + int(zz * 4), 148 - int(zz * 10), 'Z', (200, 220, 255), 8, outline=None)
    c.light(56, 156, 56, 46, (255, 210, 130), .3)
    c.amb = (1.02, .93, .86); c.vig = .7
    return c.render()


# ============================================================ 5. doce rechazos
def rejections_wide(t, u):
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
        if k >= 1 and ease((u * 14 - idx - 1.2) / .6) > 0: bg.wtext(c, sx + 11, sy + 17, 'NO', (230, 40, 60), 8, outline=(250, 240, 230), center=True)
    n = min(12, int(u * 14))
    c.R(80 - 34, 56, 68, 36, (20, 12, 30)); c.R(80 - 34, 56, 68, 2, (250, 200, 90)); c.R(80 - 34, 90, 68, 2, (140, 100, 40)); bg.wtext(c, 80, 60, str(n), (255, 216, 74), 24, outline=None, center=True)
    bg.planks(c, 0, 206, WW, 90, (90, 58, 52), seed=41, pw=9); c.R(0, 204, WW, 3, (40, 26, 30))
    place(c, rpg('rowling_rain', int(t * 3) % 2 if u < .3 else 0), 80, 214 + math.sin(t * 2))
    c.light(80, 130, 90, 80, (200, 140, 255), .35)
    c.amb = (.92, .88, 1.05); c.vig = .8
    return c.render()


# ============================================================ 6. la niña que pidió el siguiente capítulo
def alice_wide(t, u):
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
    if u > .25: bg.wtext(c, 22, 110 - int(((u - .25) * 8) % 2), '?', (255, 220, 90), 24)
    if u > .5: bg.bubble2(c, 104, 104 - int(2 * ease((u - .5) / .1)), '¡MÁS!', 16)
    for i in range(10):
        ph = (t * .5 + i * .1) % 1; xx = 60 + i * 5 + math.sin(t * 3 + i) * 4; yy = 190 - ph * 70
        c.R(xx, yy, 2, 2, (255, 236, 160))
    c.amb = (1.03, .94, .88); c.vig = .65
    return c.render()


# ============================================================ 7. 1997: la librería
def bookstore_wide(t, u):
    c = Canvas(vgrad([(0, '#2a1a5a'), (.5, '#c04a8a'), (1, '#ffb060')]))
    bg.wallpaper(c, 0, 0, WW, 206, (176, 74, 120), (164, 66, 110), (210, 120, 150))
    for i in range(14):                                                                                             # rayos de fiesta
        a = i / 14 * math.pi * 2 + t * .2
        c.d.polygon([(80, 130), (80 + 260 * math.cos(a), 130 + 260 * math.sin(a)), (80 + 260 * math.cos(a + .12), 130 + 260 * math.sin(a + .12))], fill=(214, 110, 146))
    bg.shelf(c, 4, 60, 34, 120, seed=61, rows=4); bg.shelf(c, 122, 60, 34, 120, seed=62, rows=4)
    bg.sign2(c, 80, 56, '1997', (255, 240, 120), 24, plate=(50, 20, 70))
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
def finale_wide(t, u):
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


# ====================================================================== TOMAS MEDIAS (modelos "trainer", tamaño de batalla)
def _tile_x(period, off, n=4):
    return [k * period - off for k in range(-1, n)]


def street_med(t, u):
    c = Canvas(vgrad([(0, '#0c1850'), (.4, '#24409a'), (.62, '#8a56b0'), (1, '#161224')]))
    off = (t * 34) % 160
    # fachada de ladrillo grande con ventanas altas que pasan (paralaje) y farolas
    bg.brick(c, 0, 40, WW, 170, base=(142, 78, 66), mortar=(70, 38, 40), seed=81, bh=8, bw=16)
    for x in _tile_x(80, off % 80, 3):
        bg.window(c, x + 14, 82, 38, 60, t=t, curtain=(210, 120, 70) if int(x) % 160 else (120, 80, 170), rain=False, lights=False, seed=int(x) % 7,
                  glass=((255, 214, 130), (240, 170, 90)))
        c.R(x + 8, 150, 50, 3, (200, 190, 170))
    c.R(0, 204, WW, 4, (190, 180, 220))
    bg.cobble(c, 0, 208, WW, 90, base=(88, 88, 146), seed=83)
    bg.puddle_reflections(c, 218, 50, t * 3)
    for x in _tile_x(160, (off * 1.6) % 160, 2):
        bg.lamp_post(c, x + 30, 212, t, h=118)
    step = int(t * 4) % 2
    place(c, bat('rowling_rain', 'stand'), 70, 218 + (1 if step else 0))
    rain(c, t, 190, 4, 220)
    c.amb = (.86, .9, 1.1); c.vig = .7
    return c.render()


def flat_med(t, u):
    c = Canvas(vgrad([(0, '#2a2a46'), (1, '#1a1a2c')]))
    bg.wallpaper(c, 0, 0, WW, 200, (84, 96, 156), (74, 86, 146), (110, 126, 190))
    c.R(0, 176, WW, 24, (110, 74, 54)); c.R(0, 176, WW, 2, (200, 150, 104))
    bg.planks(c, 0, 200, WW, 100, (122, 80, 58), seed=21, pw=8)
    bg.window(c, 96, 56, 48, 80, t=t, curtain=(196, 72, 96), seed=3)
    sw = math.sin(t * 2) * 4
    c.R(30, 0, 1, 40, (20, 20, 30)); c.d.ellipse([25 + sw, 40, 36 + sw, 52], fill=(255, 232, 150) if int(t * 7) % 9 else (130, 110, 80))
    c.light(31 + sw, 46, 70, 70, (255, 214, 130), .9 if int(t * 7) % 9 else .25)
    PR.keep(c, PR.baby_crib(), 4, 170)
    for i in range(7):                                                  # facturas que caen alrededor
        ph = (t * .5 + i * .14) % 1; xx = 20 + (i * 47) % 120
        if not (50 < xx < 100): PR.keep(c, PR.bill_red(), xx + int(math.sin(t * 3 + i) * 5), int(ph * 220) - 10)
    k = ease((u - .5) / .12)
    if u > .55: bg.sign2(c, 80, 66, 'SIN EMPLEO', (255, 70, 80), 16, plate=(50, 14, 26))
    place(c, bat('rowling', 'hip'), 74, 218 + 1.2 * math.sin(t * 2))
    c.amb = (.92, .92, 1.06); c.vig = .75
    return c.render()


def cafe_med(t, u):
    c = Canvas(vgrad([(0, '#4a2a1e'), (1, '#2a160e')]))
    bg.brick(c, 0, 0, WW, 160, base=(172, 92, 66), mortar=(84, 46, 40), seed=31, bh=8, bw=16)
    c.R(0, 124, WW, 4, (240, 190, 110)); bg.planks(c, 0, 128, WW, 80, (130, 82, 52), seed=32, horizontal=False, pw=10)
    bg.window(c, 12, 40, 62, 74, t=t, curtain=(230, 150, 70), seed=5)
    bg.shelf(c, 96, 40, 52, 66, seed=9, rows=2, pal=((236, 120, 60), (240, 196, 70), (200, 80, 90), (90, 170, 120)))
    for lx in (84, 132):
        sw = math.sin(t * 1.7 + lx) * 1.2
        c.R(lx, 0, 1, 24, (30, 20, 20)); PR.keep(c, PR.pendant((255, 196, 96)), lx - 9 + sw, 24)
        c.light(lx + sw, 42, 36, 32, (255, 200, 110), .7)
    bg.planks(c, 0, 206, WW, 100, (110, 68, 46), seed=33, pw=10)
    c.R(0, 204, WW, 3, (60, 38, 30))
    place(c, bat('rowling', 'hold').crop((0, 0, 86, 98)), 78, 190, sh=False)      # sentada: la mesa tapa las piernas
    c.R(14, 184, 128, 8, (160, 108, 70)); c.R(14, 184, 128, 2, (222, 164, 112)); c.R(14, 192, 128, 20, (110, 68, 46)); c.R(14, 192, 128, 1, (80, 50, 36))
    PR.keep(c, PR.teacup(), 112, 172)
    for i in range(3):
        ph = (t * .8 + i * .33) % 1; c.R(119 + int(math.sin(t * 3 + i) * 1.5), 166 - int(ph * 12), 1, 2, (255, 255, 255))
    c.R(24, 176, 40, 8, (250, 244, 224)); c.R(24, 176, 40, 1, (210, 200, 176))                  # cuaderno grande
    n = int(u * 24)
    for i in range(n): c.R(26 + (i % 6) * 6, 178 + (i // 12) * 2, 5, 1, (40, 40, 100))
    px = 26 + (t * 16) % 30; c.R(px, 172 + int(math.sin(t * 12) * 1), 1, 7, (30, 30, 80))
    c.light(78, 150, 64, 50, (255, 210, 130), .3)
    c.amb = (1.02, .93, .86); c.vig = .7
    return c.render()


def rejections_med(t, u):
    c = Canvas(vgrad([(0, '#2a1a3a'), (1, '#140c1e')]))
    bg.wallpaper(c, 0, 0, WW, 206, (66, 46, 96), (58, 40, 86), (92, 70, 132))
    c.R(0, 118, WW, 80, (86, 54, 38)); c.R(0, 118, WW, 3, (190, 130, 90))
    for i in range(7):
        for j in range(2): c.R(4 + i * 23, 123 + j * 36, 20, 32, (34, 22, 26))
    bg.planks(c, 0, 206, WW, 90, (90, 58, 52), seed=41, pw=9); c.R(0, 204, WW, 3, (40, 26, 30))
    n = min(12, int(u * 24) - 12) if u > .5 else 0
    n = max(0, min(12, int((u - .5) * 2 * 14)))
    bg.sign2(c, 80, 68, str(n), (255, 216, 74), 24, plate=(20, 12, 30))
    for i in range(8):                                                  # sobres que vuelan y sellos NO que golpean
        ph = (t * .7 + i * .125) % 1; xx = 10 + ph * 150; yy = 60 + 70 * math.sin(ph * math.pi) + (i % 3) * 14
        PR.keep(c, PR.envelope(20, 14), xx, yy)
    place(c, bat('rowling_rain', 'hold'), 80, 218 + math.sin(t * 2))
    for i, (xx, yy) in enumerate(((22, 130), (118, 120), (26, 176), (114, 170))):
        if int(t * 3 + i) % 4 < 2: bg.wtext(c, xx, yy, 'NO', (236, 44, 64), 24, outline=(250, 240, 230))
    c.light(80, 140, 90, 80, (200, 140, 255), .35)
    c.amb = (.92, .88, 1.05); c.vig = .8
    return c.render()


def alice_med(t, u):
    c = Canvas(vgrad([(0, '#3a2018'), (1, '#24120e')]))
    bg.wallpaper(c, 0, 0, WW, 206, (150, 78, 70), (138, 68, 62), (176, 104, 90))
    bg.shelf(c, 6, 34, 148, 104, seed=51, rows=3)
    c.R(0, 150, WW, 2, (240, 190, 120)); bg.planks(c, 0, 152, WW, 150, (150, 92, 60), seed=53, pw=9)
    c.R(14, 226, 132, 28, (186, 66, 80)); c.R(14, 226, 132, 2, (240, 130, 140)); c.R(18, 230, 124, 20, (150, 46, 66))
    for xx in range(24, 140, 12): c.R(xx, 238, 6, 2, (250, 210, 140))
    PR.keep(c, PR.lamp_table(), 136, 128); c.light(144, 136, 50, 40, (255, 214, 130), .8)
    place(c, bat('rexach', 'stand', 'blazer'), 122, 216)
    sway = math.sin(t * 2) * .8
    place(c, bat('alice', 'hold'), 56, 218 + sway)
    if u > .55: bg.bubble2(c, 52, 84 - int(2 * ease((u - .55) / .1)), '¡MÁS!', 16)
    if u > .7: bg.wtext(c, 118, 70 - int(((u - .7) * 8) % 2), '!', (255, 220, 90), 24)
    for i in range(10):
        ph = (t * .5 + i * .1) % 1; xx = 30 + i * 9 + math.sin(t * 3 + i) * 4; yy = 200 - ph * 90
        c.R(xx, yy, 2, 2, (255, 236, 160))
    c.amb = (1.03, .94, .88); c.vig = .65
    return c.render()


def books_med(t, u):
    c = Canvas(vgrad([(0, '#2a1a5a'), (.5, '#c04a8a'), (1, '#ffb060')]))
    bg.wallpaper(c, 0, 0, WW, 206, (176, 74, 120), (164, 66, 110), (210, 120, 150))
    for i in range(14):
        a = i / 14 * math.pi * 2 + t * .25
        c.d.polygon([(80, 120), (80 + 260 * math.cos(a), 120 + 260 * math.sin(a)), (80 + 260 * math.cos(a + .12), 120 + 260 * math.sin(a + .12))], fill=(214, 110, 146))
    bg.shelf(c, 2, 70, 40, 110, seed=61, rows=4); bg.shelf(c, 118, 70, 40, 110, seed=62, rows=4)
    bg.sign2(c, 80, 58, '1997', (255, 240, 120), 24, plate=(50, 20, 70))
    for yy in range(206, 296, 10):
        for xx in range(-(yy // 10 % 2) * 10, WW, 20): c.R(xx, yy, 10, 10, (236, 226, 206)); c.R(xx + 10, yy, 10, 10, (150, 70, 80))
    c.R(0, 204, WW, 3, (90, 50, 40))
    for i, w_ in enumerate(('kid_a', 'kid_b', 'kid_c')):                      # lectores al fondo (chibi: lejos)
        place(c, rpg(w_, int(t * 4 + i) % 2), 20 + i * 62 + (t * 8) % 12, 200, sh=False)
    place(c, bat('rowling', 'trophy'), 80, 220 + abs(math.sin(t * 5)) * -2)
    PR.keep(c, PR.book_closed((220, 70, 90), 24, 8, True), 91, 100 + int(math.sin(t * 6) * 2))   # el libro en alto
    cols2 = ((255, 90, 120), (90, 220, 255), (255, 230, 90), (140, 255, 140))
    for i in range(44):
        ph = (t * .6 + i * .023) % 1; xx = (i * 53 + math.sin(t * 3 + i) * 6) % 150 + 4; yy = ph * 280
        c.R(xx, yy, 2, 3, cols2[i % 4])
    c.light(80, 130, 90, 90, (255, 220, 150), .5)
    c.amb = (1.03, .98, .98); c.vig = .55
    return c.render()


def finale_med(t, u):
    k = ease(u * 1.1)
    c = Canvas(vgrad([(0, '#1a1a5a'), (.35, '#c0408a'), (.55, '#ff9a50'), (.75, '#ffd080'), (1, '#3a2438')]))
    sy = 112 - 26 * k
    c.d.ellipse([58, sy - 26, 102, sy + 22], fill=(255, 244, 180))
    for i in range(12):
        a = i / 12 * math.pi * 2 + t * .15
        c.d.polygon([(80, sy), (80 + 200 * math.cos(a), sy + 200 * math.sin(a)), (80 + 200 * math.cos(a + .1), sy + 200 * math.sin(a + .1))], fill=(255, 206, 140))
    bg.castle_sil(c, 118, col=(78, 44, 96))
    c.R(0, 0, 8, 190, (120, 70, 56)); c.R(152, 0, 8, 190, (120, 70, 56))
    for kx in range(8):
        col = (200, 70, 100) if kx % 2 else (170, 50, 84)
        c.R(8 + kx, 0, 1, 190, col); c.R(151 - kx, 0, 1, 190, col)
    bg.planks(c, 0, 190, WW, 110, (110, 66, 50), seed=73, pw=8); c.R(0, 188, WW, 3, (200, 140, 100))
    place(c, bat('you', 'hold').crop((0, 0, 86, 92)), 50, 176, sh=False)
    c.R(10, 172, 140, 8, (176, 112, 74)); c.R(10, 172, 140, 2, (236, 176, 124)); c.R(10, 180, 140, 26, (116, 70, 50)); c.R(10, 180, 140, 2, (90, 52, 40))
    PR.keep(c, PR.book_open(80, 34, 7), 70, 142)
    nl = int(ease((u - .15) / .6) * 7)
    for i in range(nl): c.R(112, 152 + i * 3 - 3, 28 - (i * 5) % 10, 1, (60, 50, 110))
    fl = (t * .6) % 1
    if fl < .5: c.d.polygon([(110, 144), (110 + 34 * math.sin(fl * math.pi), 142 - 8 * math.sin(fl * math.pi)), (110 + 34 * math.sin(fl * math.pi), 164 - 6 * math.sin(fl * math.pi)), (110, 168)], fill=(255, 252, 244))
    c.light(110, 154, 80, 50, (255, 230, 150), .9)
    for i in range(18):
        ph = (t * .45 + i * .056) % 1; xx = 60 + (i * 37 + math.sin(t * 2 + i) * 5) % 90; yy = 170 - ph * 120
        c.R(xx, yy, 2, 2, (255, 236, 170))
    c.amb = (1.0 + .06 * k, .94 + .08 * k, .95); c.vig = .6
    return c.render()


# ---- cada escena: toma ancha (chibi, lejos) y toma media (trainer) con corte duro
CUT = .5
def street(t, u): return street_wide(t, u / CUT) if u < CUT else street_med(t, u)
def flat(t, u): return flat_wide(t, u / CUT) if u < CUT else flat_med(t, u)
def cafe(t, u): return cafe_wide(t, u / CUT) if u < CUT else cafe_med(t, u)
def rejections(t, u): return rejections_wide(t, u / CUT) if u < CUT else rejections_med(t, u)
def alice(t, u): return alice_wide(t, u / CUT) if u < CUT else alice_med(t, u)
def bookstore(t, u): return bookstore_wide(t, u / CUT) if u < CUT else books_med(t, u)
def finale(t, u): return finale_wide(t, u / .45) if u < .45 else finale_med(t, u)
