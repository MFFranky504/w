"""Historia 5 (J. K. Rowling): del fondo a la saga."""
import math, random
import numpy as np
from PIL import Image, ImageDraw
from lib import *
import scenes as S0
import scenes2 as S2
from scenes3 import rpg, bat, place, shadow
from scenes5 import fig, bubble, _sign


def poly_sil(c, pts, col): c.d.polygon(pts, fill=col)


def stroller(c, x, y, rock=0):
    """cochecito: capota, cuerpo y ruedas. (x,y) = suelo bajo las ruedas."""
    c.d.polygon([(x - 2, y - 18 + rock), (x + 16, y - 18 + rock), (x + 14, y - 30 + rock), (x + 2, y - 30 + rock)], fill=(90, 80, 130))
    c.R(x - 4, y - 18 + rock, 24, 10, (150, 130, 190)); c.R(x - 4, y - 18 + rock, 24, 2, (190, 170, 230))
    c.R(x + 20, y - 34, 2, 18, (60, 56, 80)); c.R(x + 18, y - 36, 8, 2, (60, 56, 80))                      # manillar
    for wx in (x + 1, x + 16): c.d.ellipse([wx - 4, y - 8, wx + 4, y], fill=(30, 30, 44), outline=(120, 120, 140))


# ============================================================ 1. calle de Edimburgo, noche de lluvia (hook)
def street(t, u):
    c = Canvas(vgrad([(0, '#0a1a3a'), (.35, '#1c3a7a'), (.6, '#5a4a9a'), (.78, '#2a2250'), (1, '#161224')]))
    stars(c, t, 40, 5, 70)
    # colina y castillo
    poly_sil(c, [(0, 190), (16, 150), (40, 122), (70, 112), (96, 114), (124, 128), (150, 156), (160, 190)], (26, 24, 62))
    for x0, h in ((46, 30), (62, 44), (80, 56), (98, 40), (114, 28)):
        c.R(x0, 112 - h, 14, h + 4, (34, 30, 76)); c.d.polygon([(x0 - 1, 112 - h), (x0 + 7, 112 - h - 12), (x0 + 15, 112 - h)], fill=(34, 30, 76))
        c.R(x0 + 5, 112 - h + 8, 3, 6, (255, 206, 110), c.ed); c.R(x0 + 5, 112 - h + 22, 3, 6, (255, 206, 110), c.ed)
    c.R(40, 110, 90, 8, (40, 34, 86))
    # edificios laterales
    for x0, w, h, col in ((0, 40, 72, (42, 34, 80)), (116, 44, 84, (46, 36, 84))):
        c.R(x0, 206 - h, w, h, col); c.R(x0, 206 - h, w, 3, (80, 70, 130))
        for r in range(h // 22):
            for k in range(w // 16):
                on = (r * 5 + k * 3 + int(x0)) % 4 != 0
                c.R(x0 + 5 + k * 16, 206 - h + 10 + r * 22, 9, 12, (255, 190, 100) if on else (28, 26, 60))
    # cartel de café
    _sign(c, 100, 132, 'CAFE', (255, 170, 90), 3)
    # suelo mojado con reflejos
    c.R(0, 206, WW, 90, (30, 26, 52)); c.R(0, 206, WW, 2, (90, 80, 140))
    for i in range(10): c.R((i * 17 + int(t * 6)) % WW, 222 + (i * 7) % 40, 12, 1, (110, 100, 190))
    # farola
    c.R(38, 120, 3, 86, (20, 20, 36)); c.R(30, 118, 20, 3, (20, 20, 36)); c.R(32, 121, 6, 5, (255, 220, 140), c.ed)
    c.light(35, 126, 40, 50, (255, 210, 130), .8)
    # Rowling empuja el cochecito
    x = 40 + 52 * ease(u * 1.05)
    step = int(t * 4) % 2
    stroller(c, x + 30, 214, rock=int(math.sin(t * 8) > .5))
    place(c, fig(rpg('rowling_rain', step), .8), x, 214)
    rain(c, t, 130, 3, 170)
    fl = 0.0
    if int(t * 10) % 37 == 0: fl = .35
    c.amb = (.8 + fl, .86 + fl, 1.1 + fl); c.vig = .7
    return c.render()


# ============================================================ 2. el piso (sin trabajo, cuna, facturas)
def flat(t, u):
    c = Canvas(vgrad([(0, '#2a2a46'), (1, '#1a1a2c')]))
    c.R(0, 0, WW, 206, (66, 74, 118)); c.R(0, 0, WW, 206 - 206 + 4, (50, 56, 96))
    for x in range(0, WW, 14): c.R(x, 0, 1, 206, (58, 66, 108))                       # papel pintado
    # ventana con lluvia y luces
    c.R(96, 70, 52, 56, (24, 32, 70)); c.R(96, 70, 52, 2, (140, 150, 200)); c.R(120, 70, 2, 56, (140, 150, 200)); c.R(96, 96, 52, 2, (140, 150, 200))
    for i in range(6): c.R(100 + i * 8, 108 + (i * 7) % 12, 3, 3, (255, 200, 110))
    for i in range(14): c.R(98 + (i * 11) % 48, 72 + ((t * 70 + i * 13) % 52), 1, 4, (150, 190, 255))
    # bombilla colgante que se balancea (parpadea)
    sw = math.sin(t * 2) * 3
    c.R(40, 0, 1, 60, (20, 20, 30)); c.d.ellipse([36 + sw, 58, 46 + sw, 68], fill=(255, 230, 150) if int(t * 7) % 9 else (120, 100, 70))
    c.light(41 + sw, 66, 60, 60, (255, 210, 130), .9 if int(t * 7) % 9 else .25)
    # suelo
    c.R(0, 206, WW, 90, (92, 64, 54)); c.R(0, 206, WW, 2, (150, 110, 80))
    for yy in range(216, 290, 14): c.R(0, yy, WW, 1, (70, 48, 42))
    # mesa con facturas (llegan una a una)
    c.R(20, 170, 70, 6, (140, 98, 62)); c.R(20, 170, 70, 2, (190, 140, 90)); c.R(26, 176, 4, 30, (100, 70, 46)); c.R(80, 176, 4, 30, (100, 70, 46))
    for i in range(6):
        k = ease((u * 3 - i * .22) / .3)
        if k <= 0: continue
        px, py = 24 + i * 11, 168 - i % 3 * 2 - int((1 - k) * 40)
        c.R(px, py, 14, 3, (250, 248, 240)); c.R(px + 1, py + 1, 6, 1, (210, 60, 60))
    # cuna con bebé
    c.R(100, 160, 44, 4, (170, 120, 80)); c.R(100, 160, 44, 1, (220, 170, 120))
    for i in range(8): c.R(102 + i * 5, 164, 1, 24, (200, 150, 100))
    c.R(98, 186, 48, 4, (170, 120, 80)); c.R(100, 190, 3, 16, (120, 84, 54)); c.R(142, 190, 3, 16, (120, 84, 54))
    c.d.ellipse([112, 168, 124, 180], fill=(255, 220, 190)); c.R(110, 178, 20, 8, (255, 160, 180)); c.R(114, 172, 2, 1, (60, 40, 40)); c.R(119, 172, 2, 1, (60, 40, 40))
    zz = (t * 1.2) % 1
    ptext(c.ed, 128 + int(zz * 4), 156 - int(zz * 12), 'Z', (200, 220, 255), 2)
    # sello rojo
    if u > .42:
        k = ease((u - .42) / .08); kk = max(2, int(5 - 3 * k)); w = ptext_w('SIN TRABAJO', kk)
        c.R(20 - 4, 128 - 4, w + 8, 5 * kk + 8, (60, 16, 28)); ptext(c.ed, 20, 128, 'SIN TRABAJO', (255, 70, 80), kk)
    # Rowling de pie junto a la cuna (mirando abajo)
    b = 1.5 * max(0, math.sin(t * 2))
    place(c, fig(rpg('rowling', 0), .85), 66, 214 + b)
    c.amb = (.9, .9, 1.05); c.vig = .75
    return c.render()


# ============================================================ 4. la cafetería (escribe mientras la niña duerme)
def cafe(t, u):
    c = Canvas(vgrad([(0, '#4a2a1e'), (1, '#2a160e')]))
    c.R(0, 0, WW, 206, (120, 70, 46))
    for y in range(0, 206, 12): c.R(0, y, WW, 1, (96, 54, 36))                         # madera
    # ventana con lluvia
    c.R(14, 70, 60, 70, (30, 40, 86)); c.R(14, 70, 60, 3, (210, 160, 100)); c.R(14, 137, 60, 3, (210, 160, 100)); c.R(14, 70, 3, 70, (210, 160, 100)); c.R(71, 70, 3, 70, (210, 160, 100))
    for i in range(18): c.R(18 + (i * 9) % 52, 74 + ((t * 80 + i * 17) % 62), 1, 5, (160, 200, 255))
    c.R(20, 120, 6, 10, (255, 190, 90)); c.R(40, 112, 5, 8, (255, 110, 160)); c.R(54, 122, 6, 8, (120, 220, 255))
    # lámparas cálidas
    for lx in (96, 136):
        sw = math.sin(t * 1.7 + lx) * 1.2
        c.R(lx, 0, 1, 52, (30, 20, 20)); c.d.polygon([(lx - 8 + sw, 62), (lx + 8 + sw, 62), (lx + 5 + sw, 52), (lx - 5 + sw, 52)], fill=(255, 190, 80))
        c.light(lx + sw, 66, 34, 30, (255, 200, 110), .8)
    # cuadro/estantería
    c.R(92, 84, 50, 4, (90, 54, 34)); 
    for i in range(7): c.R(94 + i * 7, 70 + (i % 2) * 3, 5, 14 - (i % 2) * 3, ((220, 80, 80), (80, 150, 220), (240, 200, 80), (120, 200, 120))[i % 4])
    c.R(0, 206, WW, 90, (70, 40, 30)); c.R(0, 206, WW, 2, (130, 80, 56))
    # Rowling sentada: torso (la mesa tapa las piernas)
    full = fig(rpg('rowling', 0), .9)
    top = full.crop((0, 0, full.width, int(full.height * .72)))
    place(c, top, 54, 178, sh=False)
    # mesa redonda
    c.R(26, 172, 62, 6, (150, 100, 64)); c.R(26, 172, 62, 2, (206, 150, 100)); c.R(54, 178, 6, 28, (110, 72, 46)); c.R(44, 204, 26, 3, (110, 72, 46))
    # taza con vapor
    c.R(72, 166, 8, 6, (250, 248, 240)); c.R(80, 168, 2, 3, (250, 248, 240))
    for i in range(3):
        ph = (t * .8 + i * .33) % 1; c.R(75 + math.sin(t * 3 + i) * 1.5, 160 - ph * 12, 1, 2, (255, 255, 255))
    # cuaderno y pluma: aparecen líneas escritas
    c.R(34, 166, 22, 6, (250, 244, 224)); c.R(34, 166, 22, 1, (200, 190, 170))
    n = int(u * 14)
    for i in range(n): c.R(36 + (i % 3) * 6, 167 + (i // 3) % 3 * 1 if False else 168 + (i // 7), 5, 1, (40, 40, 100))
    px = 38 + (t * 14) % 14; c.R(px, 163 + int(math.sin(t * 12) * 1), 1, 5, (30, 30, 80))
    # cochecito con la bebé durmiendo
    stroller(c, 108, 210)
    zz = (t * 1.1) % 1; ptext(c.ed, 124 + int(zz * 4), 168 - int(zz * 10), 'Z', (200, 220, 255), 2)
    c.light(60, 160, 50, 40, (255, 210, 130), .7)
    c.amb = (1.0, .92, .86); c.vig = .7
    return c.render()


# ============================================================ 5. doce rechazos
def rejections(t, u):
    c = Canvas(vgrad([(0, '#2a1a3a'), (1, '#140c1e')]))
    c.R(12, 92, 136, 92, (58, 44, 80)); c.R(12, 92, 136, 3, (140, 110, 190))
    for i in range(1, 4): c.R(12 + i * 34, 95, 1, 89, (40, 30, 60))
    for j in range(1, 3): c.R(12, 92 + j * 30, 136, 1, (40, 30, 60))
    for idx in range(12):
        col_, row_ = idx % 4, idx // 4
        ex, ey = 14 + col_ * 34, 94 + row_ * 30
        k = ease((u * 14 - idx) / 1.2)
        if k <= 0: continue
        off = int((1 - k) * 60)
        c.R(ex + 2, ey + 4 - off, 26, 18, (244, 236, 214)); c.R(ex + 2, ey + 4 - off, 26, 1, (255, 252, 240))
        c.d.polygon([(ex + 2, ey + 4 - off), (ex + 28, ey + 4 - off), (ex + 15, ey + 15 - off)], outline=(190, 176, 150))
        if k >= 1:
            st = ease((u * 14 - idx - 1.2) / .6)
            if st > 0: ptext(c.ed, ex + 7, ey + 10, 'NO', (230, 40, 60), 2)
    n = min(12, int(u * 14))
    w = ptext_w(str(n), 6)
    c.R(80 - 30, 56, 60, 34, (14, 10, 26)); ptext(c.ed, 80 - w // 2, 62, str(n), (255, 216, 74), 6)
    c.R(0, 206, WW, 90, (30, 20, 44)); c.R(0, 206, WW, 2, (100, 80, 140))
    place(c, fig(rpg('rowling_rain', int(t * 3) % 2 if u < .3 else 0), .5), 80, 212 + 1.0 * math.sin(t * 2))
    c.light(80, 140, 90, 90, (200, 140, 255), .35)
    c.amb = (.9, .86, 1.05); c.vig = .8
    return c.render()


# ============================================================ 6. la niña que pidió el siguiente capítulo
def alice(t, u):
    c = Canvas(vgrad([(0, '#3a2018'), (1, '#24120e')]))
    c.R(0, 0, WW, 206, (150, 90, 60))
    for y in range(0, 206, 16): c.R(0, y, WW, 1, (120, 70, 46))
    # estantería con libros
    for sh_ in range(4):
        y0 = 40 + sh_ * 40
        c.R(6, y0 + 28, 148, 4, (96, 58, 38)); c.R(6, y0 + 28, 148, 1, (150, 100, 66))
        x = 8
        rnd = random.Random(sh_ * 7 + 1)
        while x < 150:
            w_ = rnd.randint(4, 8); h_ = rnd.randint(18, 27)
            c.R(x, y0 + 28 - h_, w_, h_, ((200, 70, 70), (70, 120, 200), (230, 190, 70), (90, 170, 110), (170, 90, 190))[rnd.randint(0, 4)]); x += w_ + 1
    c.R(0, 206, WW, 90, (96, 54, 44)); c.R(0, 206, WW, 2, (160, 100, 70))
    # alfombra
    c.R(30, 218, 100, 24, (190, 70, 80)); c.R(30, 218, 100, 3, (230, 120, 130))
    # lámpara de pie cálida
    c.R(138, 120, 3, 86, (50, 36, 30)); c.d.polygon([(130, 120), (150, 120), (146, 106), (134, 106)], fill=(255, 210, 110))
    c.light(140, 112, 60, 50, (255, 210, 130), .9)
    # el padre (editor) observa, la niña lee
    place(c, fig(rpg('rexach', 0, 'blazer'), .8), 30, 206)
    if int(u * 4) % 2 == 0 or u > .6: pass
    sway = math.sin(t * 2) * .8
    place(c, fig(rpg('alice', 0), .78), 80, 206 + sway)
    # páginas que lee
    pg = ease(u * 3)
    for i in range(3):
        c.R(70 + i * 6, 186 - int(pg * 3) - i, 12, 12, (250, 248, 240)); c.R(70 + i * 6, 186 - int(pg * 3) - i, 12, 1, (200, 196, 188))
        for j in range(3): c.R(72 + i * 6, 189 + j * 3 - int(pg * 3) - i, 8, 1, (110, 110, 130))
    if u > .25: ptext(c.ed, 24, 134 - int(((u - .25) * 8) % 2), '?', (255, 220, 90), 3)
    if u > .5: bubble(c, 100, 120 - int(2 * ease((u - .5) / .1)), 'MAS!', 3)
    for i in range(10):
        ph = (t * .5 + i * .1) % 1; xx = 60 + i * 5 + math.sin(t * 3 + i) * 4; yy = 200 - ph * 70
        c.R(xx, yy, 2, 2, (255, 236, 160))
    c.amb = (1.02, .94, .88); c.vig = .65
    return c.render()


# ============================================================ 7. 1997: la librería
def bookstore(t, u):
    c = Canvas(vgrad([(0, '#2a1a5a'), (.5, '#c04a8a'), (1, '#ffb060')]))
    for i in range(16):
        a = i / 16 * math.pi * 2 + t * .2
        c.d.polygon([(80, 130), (80 + 260 * math.cos(a), 130 + 260 * math.sin(a)), (80 + 260 * math.cos(a + .14), 130 + 260 * math.sin(a + .14))], fill=(255, 180, 140))
    # estantes laterales con libros de colores
    for side, x0 in ((0, 4), (1, 118)):
        for sh_ in range(3):
            y0 = 94 + sh_ * 28
            c.R(x0, y0 + 26, 40, 3, (96, 58, 38))
            rnd = random.Random(sh_ + side * 9); x = x0 + 1
            while x < x0 + 38:
                w_ = rnd.randint(3, 6); h_ = rnd.randint(14, 24)
                c.R(x, y0 + 26 - h_, w_, h_, ((230, 70, 90), (70, 130, 230), (250, 210, 70), (100, 200, 120), (190, 100, 220))[rnd.randint(0, 4)]); x += w_ + 1
    w = ptext_w('1997', 6)
    c.R(80 - w // 2 - 6, 60, w + 12, 40, (50, 20, 70)); ptext(c.ed, 80 - w // 2, 66, '1997', (255, 240, 120), 6)
    # pila de libros que crece
    n = 1 + int(ease(u * 1.4) * 7)
    for i in range(n):
        wb = 30 - i * 2; c.R(80 - wb // 2, 190 - (i + 1) * 6, wb, 6, ((230, 70, 90), (70, 130, 230), (250, 210, 70), (100, 200, 120))[i % 4]); c.R(80 - wb // 2, 190 - (i + 1) * 6, wb, 1, (255, 255, 255))
    # fila de lectores avanzando
    cast = ('kid_a', 'kid_b', 'kid_c', 'alice', 'messi_kid')
    for i, w_ in enumerate(cast):
        xx = (20 + i * 34 + t * 18) % 190 - 18
        place(c, fig(rpg(w_, int(t * 4 + i) % 2), .65), xx, 214, sh=False)
        c.R(xx - 3, 190, 8, 7, (250, 210, 70)); c.R(xx - 3, 190, 8, 1, (255, 250, 200))
    c.R(0, 214, WW, 80, (70, 40, 60)); c.R(0, 214, WW, 2, (130, 80, 100))

    cols = ((255, 90, 120), (90, 220, 255), (255, 230, 90), (140, 255, 140))
    for i in range(34):
        ph = (t * .5 + i * .03) % 1; xx = (i * 53 + math.sin(t * 3 + i) * 6) % 150 + 4; yy = ph * 270
        c.R(xx, yy, 2, 3, cols[i % 4])
    c.light(80, 140, 90, 90, (255, 220, 150), .5)
    c.amb = (1.02, .98, .98); c.vig = .55
    return c.render()


# ============================================================ 9. el libro en blanco al amanecer
def finale(t, u):
    k = ease(u * 1.1)
    c = Canvas(vgrad([(0, '#1a1a5a'), (.35, '#c0408a'), (.55, '#ff9a50'), (.75, '#ffd080'), (1, '#3a2438')]))
    sy = 138 - 36 * k                                                           # el sol sube
    c.d.ellipse([60, sy - 22, 100, sy + 18], fill=(255, 240, 170))
    for i in range(12):
        a = i / 12 * math.pi * 2 + t * .15
        c.d.polygon([(80, sy), (80 + 200 * math.cos(a), sy + 200 * math.sin(a)), (80 + 200 * math.cos(a + .1), sy + 200 * math.sin(a + .1))], fill=(255, 200, 130))
    poly_sil(c, [(0, 160), (14, 140), (30, 134), (46, 146), (80, 126), (112, 146), (130, 136), (146, 142), (160, 160)], (60, 34, 70))
    for x0, h in ((58, 18), (72, 28), (88, 20), (100, 14)):
        c.R(x0, 130 - h, 10, h, (50, 28, 62)); c.d.polygon([(x0 - 1, 130 - h), (x0 + 5, 130 - h - 9), (x0 + 11, 130 - h)], fill=(50, 28, 62))
    c.R(0, 160, WW, 50, (50, 28, 62))
    # escritorio con el libro enorme abierto y brillante (alto: queda sobre los subtítulos)
    c.R(0, 180, WW, 120, (96, 56, 44)); c.R(0, 180, WW, 3, (170, 110, 80))
    c.R(16, 166, 128, 16, (150, 84, 60))
    c.d.polygon([(22, 158), (78, 150), (78, 172), (22, 174)], fill=(252, 248, 236)); c.d.polygon([(82, 150), (138, 158), (138, 174), (82, 172)], fill=(246, 242, 226))
    c.R(78, 150, 4, 22, (200, 150, 110))
    nl = int(ease((u - .15) / .6) * 7)
    for i in range(nl): c.R(88, 157 + i * 2, 40 - (i * 5) % 14, 1, (60, 50, 110))
    for i in range(5): c.R(28, 159 + i * 2, 38 - (i * 7) % 16, 1, (120, 110, 150))
    fl = (t * .6) % 1
    if fl < .5: c.d.polygon([(82, 150), (82 + 50 * math.sin(fl * math.pi), 148 - 8 * math.sin(fl * math.pi)), (82 + 50 * math.sin(fl * math.pi), 170 - 6 * math.sin(fl * math.pi)), (82, 172)], fill=(255, 252, 244))
    c.light(80, 156, 70, 46, (255, 230, 150), 1.0)
    # el espectador, detrás del escritorio (se le ve de la cintura para arriba), mirando el libro
    full = fig(rpg('you', 0), .95)
    top = full.crop((0, 0, full.width, int(full.height * .78)))
    place(c, top, 46, 166, sh=False)
    c.R(16, 166, 128, 16, (150, 84, 60)); c.R(16, 166, 128, 2, (206, 140, 100))
    for i in range(16):
        ph = (t * .45 + i * .063) % 1; xx = 44 + (i * 37 + math.sin(t * 2 + i) * 5) % 90; yy = 160 - ph * 100
        c.R(xx, yy, 2, 2, (255, 236, 170))
    c.amb = (1.0 + .06 * k, .94 + .08 * k, .95); c.vig = .6
    return c.render()
