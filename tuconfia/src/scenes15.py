"""Documental piloto: Guillermo del Toro. HORIZONTAL (mundo 320x180, x6). TC_LAND=1.
Sin logos, carteles reales ni parecidos con actores: personajes y criaturas originales.
Cada escena: plano ancho (chibi) y plano medio (trainer); los momentos clave tienen primer plano (retrato con expresión)."""
import math, random
import numpy as np
from PIL import Image
from lib import *
import bg
import props as PR
from scenes3 import rpg, bat, place
from scenes9 import phased
from scenes10 import cv, sign, FL, FW, FM
from scenes10 import portrait_land as _pl

assert WW == 320 and WH == 180
BLK = '#000000'


def close(who, expr, look=(0, 0), tone='cold'):
    """primer plano con expresión (retrato)."""
    return lambda t, u: _pl(t, who, expr, look, tone)


# ---------------------------------------------------------------- utilidades de dibujo
def _sketch(c, x, y, w, h, kind, seed=1):
    """hoja con boceto de criatura original (insecto, vampiro, fantasma, fauno, pez)."""
    c.R(x, y, w, h, (236, 226, 200)); c.R(x, y, w, 1, (255, 248, 226)); c.R(x, y + h - 1, w, 1, (180, 168, 140))
    ink = (60, 46, 50); cx, cy = x + w // 2, y + h // 2; d = c.d
    if kind == 'bug':
        d.ellipse([cx - 4, cy - 3, cx + 4, cy + 5], outline=ink); d.ellipse([cx - 2, cy - 7, cx + 2, cy - 3], outline=ink)
        for k in (-1, 1):
            for j in range(3): d.line([(cx + 3 * k, cy - 1 + j * 2), (cx + 8 * k, cy - 3 + j * 3)], fill=ink)
    elif kind == 'vamp':
        d.ellipse([cx - 4, cy - 6, cx + 4, cy + 2], outline=ink); d.polygon([(cx - 8, cy + 8), (cx, cy + 1), (cx + 8, cy + 8)], outline=ink)
        d.point((cx - 2, cy - 3), fill=(180, 30, 40)); d.point((cx + 2, cy - 3), fill=(180, 30, 40))
    elif kind == 'ghost':
        d.ellipse([cx - 5, cy - 7, cx + 5, cy + 3], outline=ink); d.line([(cx - 5, cy - 2), (cx - 6, cy + 8)], fill=ink); d.line([(cx + 5, cy - 2), (cx + 6, cy + 8)], fill=ink)
        d.point((cx - 2, cy - 3), fill=ink); d.point((cx + 2, cy - 3), fill=ink)
    elif kind == 'faun':
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 5], outline=ink); d.arc([cx - 9, cy - 10, cx - 1, cy - 2], 180, 300, fill=ink); d.arc([cx + 1, cy - 10, cx + 9, cy - 2], 240, 360, fill=ink)
        d.point((cx - 2, cy), fill=(200, 160, 60)); d.point((cx + 2, cy), fill=(200, 160, 60))
    else:
        d.ellipse([cx - 6, cy - 3, cx + 6, cy + 3], outline=ink); d.polygon([(cx + 6, cy), (cx + 10, cy - 3), (cx + 10, cy + 3)], outline=ink); d.point((cx - 3, cy - 1), fill=ink)


def _desk_room(c, t, cold=0.0):
    """estudio de noche: pared con bocetos, ventana con lluvia, escritorio y lámpara. cold: 0 cálido, 1 frío."""
    c.im.paste(Image.fromarray(vgrad([(0, '#1a1420'), (1, '#2a1e28')]).astype('uint8')), (0, 0))
    bg.wallpaper(c, 0, 0, WW, FL, (58, 44, 52), (52, 40, 48), (78, 60, 70))
    bg.window(c, 214, 20, 70, 62, t=t, night=True, rain=True, lights=True, seed=9)
    for i, k in enumerate(('bug', 'vamp', 'ghost', 'faun', 'bug', 'fish', 'vamp')):
        x = 20 + (i % 4) * 44; y = 18 + (i // 4) * 34 + (i % 2) * 3; _sketch(c, x, y, 30, 26, k, i)
        c.R(x + 13, y - 1, 4, 2, (180, 40, 40))
    bg.planks(c, 0, FL, WW, 44, (70, 48, 40), seed=31, pw=9); c.R(0, FL - 2, WW, 3, (34, 24, 22))
    lamp = (255, int(206 - 60 * cold), int(120 + 120 * cold))
    c.light(150, 92, 110, 70, lamp, .9 - .3 * cold)
    if cold: c.light(250, 50, 90, 70, (120, 160, 255), .6 * cold)


def _desk_front(c, t, paper=True):
    c.R(96, 112, 128, 6, (120, 78, 52)); c.R(96, 112, 128, 2, (186, 136, 92)); c.R(100, 118, 6, 26, (90, 58, 40)); c.R(214, 118, 6, 26, (90, 58, 40))
    c.R(118, 106, 2, 8, (40, 40, 50)); c.d.polygon([(110, 98), (126, 98), (122, 92), (114, 92)], fill=(60, 70, 60))
    if paper: c.R(140, 108, 26, 5, (236, 226, 200)); c.R(146, 109, 12, 1, (60, 46, 50))


def _phone(c, x, y, t, ring=False):
    dx = int(math.sin(t * 60) * 1.2) if ring else 0
    c.R(x + dx, y + 4, 16, 6, (30, 28, 34)); c.R(x + 2 + dx, y, 12, 4, (40, 38, 46)); c.R(x + 6 + dx, y + 5, 4, 3, (200, 200, 210))
    if ring and int(t * 6) % 2:
        for k in (1, 2): c.d.arc([x - 4 * k + dx, y - 3 * k, x + 16 + 4 * k + dx, y + 8 + 3 * k], 200, 340, fill=(255, 230, 140))


# ================================================================ 0. cold open
def desk_a(t, u):            # primer fotograma: plano medio, dibuja bajo la lámpara (acción desde el fotograma 0)
    c = cv((0, BLK), (1, BLK)); _desk_room(c, t)
    place(c, bat('gdt', 'hold'), 160, FM + 2)
    _desk_front(c, t); x = 150 + int(math.sin(t * 9) * 4); c.R(x, 104, 2, 6, (250, 220, 120))     # lápiz en movimiento
    _phone(c, 196, 102, t)
    c.amb = (1.0, .92, .86); c.vig = .85
    return c.render()


def desk_b(t, u):
    c = cv((0, BLK), (1, BLK)); _desk_room(c, t)
    place(c, rpg('gdt', 0), 160, 116, sh=False); _desk_front(c, t); _phone(c, 196, 102, t)
    c.amb = (1.0, .92, .86); c.vig = .8
    return c.render()


desk = phased(desk_a, desk_b, cuts=(.55,))


def phone_a(t, u):            # suena: la luz cambia a fría
    c = cv((0, BLK), (1, BLK)); _desk_room(c, t, cold=ease(min(1, u * 3)))
    place(c, bat('gdt', 'stand'), 160, FM + 2); _desk_front(c, t); _phone(c, 196, 102, t, ring=True)
    c.amb = (.86, .9, 1.04); c.vig = .9
    return c.render()


phone = phased(phone_a, close('gdt', 'worry', (1, 0), 'cold'), cuts=(.55,))


def _set_dark(c, t):
    c.im.paste(Image.fromarray(vgrad([(0, '#0c0a14'), (1, '#1a1424')]).astype('uint8')), (0, 0))
    bg.truss(c, 14, ((200, 60, 60), (120, 120, 200), (255, 210, 120)), t, x0=10, x1=310)
    c.R(0, FL, WW, 44, (30, 26, 34)); c.R(0, FL, WW, 2, (60, 54, 66))
    for x in (40, 270):
        c.R(x, 60, 3, 76, (60, 60, 70)); c.R(x - 10, 50, 24, 12, (40, 40, 48))
        if int(t * 7 + x) % 5: c.light(x + 2, 70, 40, 60, (255, 240, 200), .45)


def teaser_a(t, u):           # la peor experiencia: rodaje oscuro, silla de director vacía, película tirada
    c = cv((0, BLK), (1, BLK)); _set_dark(c, t)
    c.R(150, 110, 22, 3, (150, 40, 40)); c.R(150, 96, 22, 14, (60, 30, 30)); c.R(152, 113, 2, 23, (90, 70, 50)); c.R(168, 113, 2, 23, (90, 70, 50))
    PR.keep(c, PR.film_reel(10), 196, 118); c.R(206, 132, 60, 2, (40, 36, 30))
    PR.keep(c, PR.clapper(), 100, 112)
    c.amb = (.82, .82, .96); c.vig = .95
    return c.render()


def _oscar_stage(c, t, crowd=True):
    c.im.paste(Image.fromarray(vgrad([(0, '#100818'), (1, '#2a1030')]).astype('uint8')), (0, 0))
    bg.curtain(c, 0, 70, 140, (150, 30, 50)); bg.curtain(c, 250, 70, 140, (150, 30, 50))
    for i in range(7): PR.keep(c, PR.statuette(40), 84 + i * 24, 54) if i in (0, 6) else None
    c.R(60, 130, 200, 8, (210, 170, 70)); c.R(60, 138, 200, 6, (120, 90, 40))
    bg.beam(c, 160, 0, 10, 60, 136, (255, 240, 200), 40)
    if crowd: bg.crowd(c, 150, t, seed=4)


def teaser_b(t, u):           # el escenario de los Óscar: figura pequeña bajo el foco
    c = cv((0, BLK), (1, BLK)); _oscar_stage(c, t)
    place(c, rpg('gdt', 0), 160, 132, sh=False); c.light(160, 110, 50, 50, (255, 240, 200), .7)
    c.amb = (1.0, .96, .9); c.vig = .85
    return c.render()


teaser = phased(teaser_a, teaser_b, cuts=(.42,))


# ================================================================ 1. el niño de las pesadillas
def _gdl(c, t, k=0.0):
    c.im.paste(Image.fromarray(vgrad([(0, '#ffb070'), (.5, '#ffd8a0'), (1, '#f0c8a0')]).astype('uint8')), (0, 0))
    sy = 40 + 10 * k; c.d.ellipse([250, sy, 276, sy + 26], fill=(255, 236, 190))
    bg.skyline(c, 0, 116, cols=((176, 110, 96), (196, 130, 110)), seed=64, lit=0, t=t, hmin=14, hmax=36)
    for x in (140, 170):                                                         # catedral: dos torres agujas
        c.R(x, 50, 12, 66, (226, 196, 150)); c.d.polygon([(x - 1, 50), (x + 13, 50), (x + 6, 24)], fill=(80, 140, 170)); c.R(x + 4, 60, 4, 8, (90, 60, 50))
    c.R(138, 80, 46, 36, (232, 204, 160)); c.d.ellipse([150, 84, 172, 106], fill=(120, 80, 60))
    bg.cobble(c, 0, FL - 20, WW, 64, base=(176, 150, 120), seed=8)


def gdl_a(t, u):
    c = cv((0, BLK), (1, BLK)); _gdl(c, t, u)
    sign(c, 160, 36, 'GUADALAJARA · 1964', (255, 236, 160), 16, (60, 30, 30))
    place(c, rpg('gdt_k', int(t * 3) % 2), 60 + 120 * u, FW)
    c.amb = (1.04, .98, .9); c.vig = .55
    return c.render()


gdl = phased(gdl_a)


def _home(c, t):
    c.im.paste(Image.fromarray(vgrad([(0, '#3a2418'), (1, '#24160e')]).astype('uint8')), (0, 0))
    bg.wallpaper(c, 0, 0, WW, FL, (120, 74, 54), (110, 68, 50), (150, 100, 70))
    c.R(156, 20, 8, 34, (90, 60, 30)); c.R(146, 28, 28, 8, (90, 60, 30))                                     # cruz de madera
    for x in (128, 186):
        c.R(x, 92, 6, 20, (240, 230, 210)); c.d.ellipse([x + 1, 86 + math.sin(t * 9 + x) * 1, x + 5, 92], fill=(255, 200, 90)); c.light(x + 3, 88, 26, 26, (255, 190, 100), .8)
    c.R(110, 112, 100, 4, (130, 86, 54)); c.R(114, 116, 92, 20, (96, 62, 40))
    bg.planks(c, 0, FL, WW, 44, (100, 64, 44), seed=12, pw=9)


def abuela_a(t, u):
    c = cv((0, BLK), (1, BLK)); _home(c, t)
    place(c, rpg('abuela', 0), 120, FW); place(c, rpg('gdt_k', 0), 194, FW)
    c.amb = (1.04, .94, .86); c.vig = .75
    return c.render()


def abuela_b(t, u):
    c = cv((0, BLK), (1, BLK)); _home(c, t)
    place(c, bat('abuela', 'hold'), 116, FM); place(c, bat('gdt_k', 'stand'), 210, FM)
    c.amb = (1.04, .94, .86); c.vig = .8
    return c.render()


abuela = phased(abuela_a, abuela_b, cuts=(.5,))


def night_a(t, u):            # niño solitario; las sombras de monstruos crecen en la pared
    c = cv((0, '#0a0c22'), (1, '#141026'))
    bg.wallpaper(c, 0, 0, WW, FL, (34, 36, 70), (30, 32, 64), (46, 48, 90)); bg.window(c, 30, 20, 56, 60, t=t, night=True, rain=False, lights=False, seed=3)
    c.d.ellipse([46, 30, 62, 46], fill=(236, 232, 200)); c.light(58, 50, 90, 70, (150, 170, 255), .5)
    k = ease(u)
    for i, (x, kind) in enumerate(((150, 0), (210, 1), (262, 2))):          # sombras en la pared
        h = int(30 + 40 * k); col = (16, 14, 34)
        if kind == 0: c.d.polygon([(x - 14, 110), (x, 110 - h), (x + 14, 110)], fill=col); c.d.ellipse([x - 8, 104 - h, x + 8, 120 - h], fill=col)
        elif kind == 1: c.d.ellipse([x - 16, 112 - h, x + 16, 112], fill=col); [c.R(x - 20 + j * 8, 100 - h // 2, 3, 20, col) for j in range(6)]
        else: c.d.polygon([(x - 12, 112), (x - 8, 112 - h), (x + 8, 112 - h), (x + 12, 112)], fill=col); c.d.ellipse([x - 10, 104 - h, x + 10, 124 - h], fill=col)
    c.R(110, 112, 84, 14, (110, 70, 60)); c.R(110, 108, 84, 6, (200, 200, 220)); c.R(110, 126, 4, 10, (80, 50, 40)); c.R(190, 126, 4, 10, (80, 50, 40))
    c.R(114, 104, 18, 6, (240, 240, 250)); bust = rpg('gdt_k', 0).crop((0, 0, 46, 40)); c.blit(bust, 112, 82)
    c.R(130, 106, 64, 10, (70, 90, 150)); c.R(130, 106, 64, 2, (100, 120, 190))
    bg.planks(c, 0, FL, WW, 44, (50, 40, 60), seed=4, pw=9)
    c.amb = (.76, .8, 1.06); c.vig = .9
    return c.render()


night = phased(night_a, close('gdt_k', 'worry', (0, -1), 'cold'), cuts=(.7,))


def _taller(c, t):
    c.im.paste(Image.fromarray(vgrad([(0, '#202a24'), (1, '#121812')]).astype('uint8')), (0, 0))
    bg.wallpaper(c, 0, 0, WW, FL, (56, 70, 60), (50, 64, 54), (76, 92, 80))
    for row in range(2):                                                       # estantes con cabezas y máscaras de látex
        y = 30 + row * 40; c.R(14, y + 22, 120, 4, (110, 76, 50))
        for i in range(5):
            x = 22 + i * 22; col = [(196, 160, 140), (120, 160, 110), (180, 110, 110), (210, 200, 180), (130, 120, 160)][(i + row) % 5]
            c.d.ellipse([x, y + 4, x + 14, y + 22], fill=col); c.R(x + 3, y + 10, 3, 2, (30, 20, 20)); c.R(x + 8, y + 10, 3, 2, (30, 20, 20))
    c.R(180, 4, 110, 26, (30, 24, 26)); bg.wtext(c, 235, 10, 'NECROPIA', (190, 230, 160), 16, center=True)
    c.R(150, 104, 150, 6, (130, 86, 54)); c.R(156, 110, 6, 26, (90, 58, 40)); c.R(290, 110, 6, 26, (90, 58, 40))
    c.light(220, 90, 90, 60, (220, 255, 210), .4)
    bg.planks(c, 0, FL, WW, 44, (70, 56, 44), seed=21, pw=9)


def taller_a(t, u):
    c = cv((0, BLK), (1, BLK)); _taller(c, t)
    place(c, rpg('gdt_y', 0), 222, 104, sh=False); c.R(150, 104, 150, 6, (130, 86, 54)); c.R(150, 104, 150, 2, (190, 140, 96))
    c.d.ellipse([186, 92, 200, 108], fill=(120, 160, 110)); c.R(196 + int(math.sin(t * 7) * 2), 96, 2, 6, (200, 60, 60))
    c.amb = (.96, 1.02, .96); c.vig = .75
    return c.render()


def taller_b(t, u):
    c = cv((0, BLK), (1, BLK)); _taller(c, t)
    place(c, bat('gdt_y', 'hold'), 200, FM)
    c.amb = (.96, 1.02, .96); c.vig = .8
    return c.render()


taller = phased(taller_a, taller_b, cuts=(.5,))


def camara_a(t, u):           # la pregunta: frente a una cámara de cine bajo un foco
    c = cv((0, '#0c0c18'), (1, '#16121e')); c.R(0, FL, WW, 44, (26, 24, 32))
    bg.beam(c, 190, 0, 8, 70, 136, (255, 240, 200), 36)
    c.R(212, 70, 30, 20, (40, 40, 50)); c.d.ellipse([206, 74, 216, 84], fill=(80, 90, 110)); PR.keep(c, PR.film_reel(8), 214, 52); PR.keep(c, PR.film_reel(8), 230, 52)
    for dx in (-10, 0, 10): c.d.line([(227, 90), (227 + dx, 136)], fill=(70, 70, 80))
    place(c, rpg('gdt_y', 0), 150, FW)
    c.light(190, 110, 50, 40, (255, 240, 200), .5); c.amb = (.9, .9, 1.0); c.vig = .9
    return c.render()


camara = phased(camara_a, close('gdt_y', 'n', (1, 0), 'warm'), cuts=(.6,))


# ================================================================ 2. Cronos
def _cronos_device(c, x, y, t):
    """artefacto dorado de relojería (diseño original)."""
    c.d.ellipse([x - 12, y - 8, x + 12, y + 8], fill=(200, 160, 60), outline=(120, 90, 30)); c.d.ellipse([x - 6, y - 4, x + 6, y + 4], fill=(240, 210, 110))
    a = t * 3
    for k in range(4):
        ang = a + k * math.pi / 2; c.d.line([(x, y), (x + 9 * math.cos(ang), y + 6 * math.sin(ang))], fill=(120, 80, 20))
    for k in (-1, 1): c.d.line([(x + 10 * k, y), (x + 16 * k, y + 6)], fill=(170, 130, 50))
    c.light(x, y, 30, 22, (255, 220, 120), .6)


def cronos_a(t, u):
    c = cv((0, '#0a0806'), (1, '#1a120a')); c.R(0, FL, WW, 44, (30, 22, 16))
    for i in range(9): c.R(14 + i * 34, 30, 26, 80, (44, 32, 22)); c.R(16 + i * 34, 34, 22, 72, (30, 22, 16))     # vitrinas de un anticuario
    c.R(130, 100, 60, 6, (90, 60, 40)); _cronos_device(c, 160, 92, t)
    place(c, rpg('gdt_y', 0), 230, FW)
    c.amb = (1.0, .92, .8); c.vig = .9
    return c.render()


cronos = phased(cronos_a, lambda t, u: _cronos_close(t), cuts=(.5,))


def _cronos_close(t):
    c = cv((0, '#0a0806'), (1, '#1a120a')); _cronos_device(c, 160, 90, t)
    c.R(0, 0, WW, WH, (0, 0, 0)) if False else None
    big = c.render().crop((120, 66, 200, 114)).resize((320, 192), Image.NEAREST).crop((0, 6, 320, 186))
    return big


def _money_street(c, t):
    c.im.paste(Image.fromarray(vgrad([(0, '#7aa0d0'), (1, '#c8d8e8')]).astype('uint8')), (0, 0))
    bg.house(c, 40, 60, 110, 76, (220, 196, 160), (150, 70, 60), seed=3, lit=0)
    bg.cobble(c, 0, FL, WW, 44, base=(150, 140, 130), seed=5)


def money_a(t, u):            # hipotecó la casa y vendió el coche
    c = cv((0, BLK), (1, BLK)); _money_street(c, t)
    sign(c, 96, 40, 'HIPOTECADA', (255, 90, 90), 8, (40, 10, 24))
    k = ease(min(1, u * 1.4)); PR.keep(c, PR.car(), int(200 + 130 * k), 112)
    place(c, rpg('gdt_y', 0), 170, FW)
    for i in range(6): PR.keep(c, PR.money_bill(), 150 + i * 9 + int(math.sin(t * 3 + i) * 3), 70 - int((t * 20 + i * 9) % 50))
    c.amb = (1.02, 1.0, 1.0); c.vig = .6
    return c.render()


money = phased(money_a, close('gdt_y', 'worry', (0, 0), 'warm'), cuts=(.72,))


def _cine(c, t, light=True):
    c.im.paste(Image.fromarray(vgrad([(0, '#100a16'), (1, '#1e1226')]).astype('uint8')), (0, 0))
    c.R(60, 14, 200, 84, (20, 20, 30)); c.R(64, 18, 192, 76, (60, 70, 100) if light else (10, 10, 16))
    if light: c.light(160, 56, 120, 50, (180, 200, 255), .5)
    bg.curtain(c, 40, 24, 110, (150, 30, 50), valance=False); bg.curtain(c, 256, 24, 110, (150, 30, 50), valance=False)


def estreno_a(t, u):           # 1993: la crítica la celebra
    c = cv((0, BLK), (1, BLK)); _cine(c, t); _cronos_device(c, 160, 56, t)
    bg.crowd(c, 120, t, seed=2, hands=u > .3)
    if u > .45:                                                          # reseñas: estrellas dibujadas (la fuente no tiene ★)
        for i in range(5):
            x0, y0 = 40 + i * 60, 98 - (i % 2) * 6; c.R(x0 - 2, y0 - 2, 44, 12, (40, 30, 10))
            for j in range(4):
                cx_, cy_ = x0 + 5 + j * 10, y0 + 4
                c.d.polygon([(cx_ + 4.5 * math.cos(a_ * math.pi / 5 - math.pi / 2) * (1 if a_ % 2 == 0 else .45), cy_ + 4.5 * math.sin(a_ * math.pi / 5 - math.pi / 2) * (1 if a_ % 2 == 0 else .45)) for a_ in range(10)], fill=(255, 220, 90))
    c.amb = (.96, .96, 1.04); c.vig = .75
    return c.render()


def hollywood_call(t, u):      # llama Hollywood: el teléfono suena en el taller
    c = cv((0, BLK), (1, BLK)); _taller(c, t)
    place(c, rpg('gdt_y', 0), 210, FW); _phone(c, 160, 96, t, ring=True)
    c.amb = (.96, 1.0, .96); c.vig = .8
    return c.render()


estreno = phased(estreno_a, hollywood_call, cuts=(.78,))


# ================================================================ 3. Mimic
def _la(c, t):
    c.im.paste(Image.fromarray(vgrad([(0, '#ff9a60'), (.6, '#ffc890'), (1, '#e8b080')]).astype('uint8')), (0, 0))
    bg.hill_l(c, 96, (150, 110, 100), t)
    for x in (30, 90, 250, 300): PR.keep(c, PR.palm(), x - 20, 66)
    c.R(110, 66, 100, 70, (230, 220, 200)); c.R(110, 66, 100, 6, (190, 170, 140)); c.R(144, 96, 32, 40, (70, 60, 60))     # puerta de estudio
    sign(c, 160, 76, 'ESTUDIO', (60, 50, 50), 8, (230, 220, 200))
    bg.cobble(c, 0, FL, WW, 44, base=(170, 160, 150), seed=9)


def la_a(t, u):
    c = cv((0, BLK), (1, BLK)); _la(c, t)
    sign(c, 160, 36, 'HOLLYWOOD · 1997', (255, 236, 160), 16, (60, 30, 30))
    place(c, rpg('gdt_y', int(t * 3) % 2), 40 + 110 * u, FW)
    c.amb = (1.04, 1.0, .94); c.vig = .55
    return c.render()


def la_b(t, u):                # más gente opinando: productores rodeándolo
    c = cv((0, BLK), (1, BLK)); _la(c, t)
    place(c, rpg('productor', 0), 110, FW); place(c, rpg('prod1', 0), 210, FW); place(c, rpg('mintz', 0), 250, FW); place(c, rpg('gdt_y', 0), 160, FW + 2)
    c.amb = (1.04, 1.0, .94); c.vig = .6
    return c.render()


la = phased(la_a, la_b, cuts=(.5,))


def _meeting(c, t):
    c.im.paste(Image.fromarray(vgrad([(0, '#1c2030'), (1, '#2a2e40')]).astype('uint8')), (0, 0))
    bg.wallpaper(c, 0, 0, WW, FL, (70, 74, 90), (64, 68, 84), (90, 94, 112))
    for x in range(30, 300, 60): c.R(x, 6, 40, 3, (220, 230, 255)); c.light(x + 20, 14, 30, 20, (220, 230, 255), .35)
    c.R(60, 108, 200, 6, (60, 50, 50)); c.R(60, 114, 200, 22, (44, 36, 36))
    bg.planks(c, 0, FL, WW, 44, (60, 60, 70), seed=6, pw=12)


def pelea_a(t, u):
    c = cv((0, BLK), (1, BLK)); _meeting(c, t)
    place(c, rpg('productor', 0), 110, 110, sh=False); place(c, rpg('prod1', 0), 210, 110, sh=False)
    c.R(60, 108, 200, 6, (60, 50, 50)); PR.keep(c, PR.contract(), 146, 76)
    place(c, rpg('gdt_y', 0), 160, FW + 8)
    c.amb = (.92, .94, 1.04); c.vig = .75
    return c.render()


def pelea_b(t, u):
    c = cv((0, BLK), (1, BLK)); _meeting(c, t)
    place(c, bat('productor', 'hold'), 230, FM); place(c, bat('gdt_y', 'stand'), 100, FM)
    c.amb = (.9, .92, 1.04); c.vig = .85
    return c.render()


pelea = phased(pelea_a, pelea_b, close('gdt_y', 'sad', (0, 1), 'cold'), cuts=(.36, .7))


def lluvia_a(t, u):            # decide no volver a sus historias oscuras en Hollywood: camina solo bajo la lluvia
    c = cv((0, '#0a1020'), (1, '#18203a'))
    bg.skyline(c, 0, 110, cols=((30, 34, 60), (40, 44, 76)), seed=31, lit=.4, t=t, hmin=30, hmax=90)
    bg.cobble(c, 0, FL - 6, WW, 50, base=(50, 56, 80), seed=3); bg.puddle_reflections(c, FL, 40, t)
    bg.lamp_post(c, 70, FL, t); bg.lamp_post(c, 250, FL, t)
    place(c, rpg('gdt_y', int(t * 2) % 2), 280 - 200 * u, FW)
    rain(c, t, n=110, seed=5)
    c.amb = (.8, .86, 1.06); c.vig = .85
    return c.render()


lluvia = phased(lluvia_a, close('gdt_y', 'sad', (-1, 0), 'cold'), cuts=(.62,))


def hotel_a(t, u):             # "y lo que vino después... fue el teléfono"
    c = cv((0, BLK), (1, BLK)); _desk_room(c, t, cold=.6)
    place(c, rpg('gdt_y', 0), 230, FW); _desk_front(c, t, paper=False); _phone(c, 150, 102, t, ring=u > .3)
    c.amb = (.86, .9, 1.04); c.vig = .9
    return c.render()


hotel = phased(hotel_a)


# ================================================================ 4. La llamada
def _gdl_night(c, t):
    c.im.paste(Image.fromarray(vgrad([(0, '#060818'), (1, '#121428')]).astype('uint8')), (0, 0))
    stars(c, t, 30, 4, 60)
    bg.skyline(c, 0, 118, cols=((20, 22, 40), (28, 30, 52)), seed=64, lit=.15, t=t, hmin=14, hmax=36)
    for x in (140, 170): c.R(x, 50, 12, 68, (40, 40, 60)); c.d.polygon([(x - 1, 50), (x + 13, 50), (x + 6, 24)], fill=(30, 34, 56))
    bg.cobble(c, 0, FL - 14, WW, 58, base=(44, 44, 64), seed=8); bg.lamp_post(c, 60, FL, t); bg.lamp_post(c, 270, FL, t)


def secuestro_a(t, u):
    c = cv((0, BLK), (1, BLK)); _gdl_night(c, t)
    PR.keep(c, PR.car(), 130, 112)
    c.amb = (.74, .78, 1.0); c.vig = .95
    return c.render()


secuestro = phased(secuestro_a, close('gdt', 'sad', (0, 0), 'cold'), cuts=(.55,))


def dias_a(t, u):              # pasa un día, una semana, un mes: calendario que cae hoja a hoja
    c = cv((0, '#0a0a14'), (1, '#14141e'))
    c.R(110, 30, 100, 110, (230, 226, 214)); c.R(110, 30, 100, 18, (170, 40, 50))
    n = [1, 7, 30][min(2, int(u * 3))]
    bg.wtext(c, 160, 70, str(n), (40, 30, 40), 40, center=True); bg.wtext(c, 160, 116, 'DÍA' if n == 1 else 'DÍAS', (90, 80, 90), 16, center=True)
    for i in range(6):
        y = (t * 70 + i * 40) % 200 - 20; x = 60 + i * 40 + math.sin(t * 2 + i) * 10; c.R(int(x), int(y), 14, 16, (220, 216, 204))
    c.light(160, 80, 90, 80, (200, 210, 255), .3); c.amb = (.86, .88, 1.0); c.vig = .9
    return c.render()


dias = phased(dias_a)


def cameron_a(t, u):           # un amigo: dinero para contratar a un negociador
    c = cv((0, BLK), (1, BLK)); _desk_room(c, t, cold=.4)
    c.R(80, 112, 160, 6, (120, 78, 52)); c.R(80, 112, 160, 2, (186, 136, 92))
    place(c, rpg('gdt', 0), 120, 114, sh=False); place(c, rpg('amigo_dir', 0), 200, 114, sh=False)
    c.R(80, 112, 160, 6, (120, 78, 52)); PR.keep(c, PR.envelope(), 152, 102)
    c.amb = (.96, .94, 1.0); c.vig = .8
    return c.render()


def cameron_b(t, u):
    c = cv((0, BLK), (1, BLK)); _desk_room(c, t, cold=.4)
    place(c, bat('amigo_dir', 'hold'), 220, FM); place(c, bat('gdt', 'stand'), 100, FM)
    c.amb = (.96, .94, 1.0); c.vig = .85
    return c.render()


cameron = phased(cameron_a, cameron_b, cuts=(.5,))


def dia72_a(t, u):             # 72 días... y la puerta se abre: vuelve con vida
    c = cv((0, '#0a0a14'), (1, '#14141e'))
    if u < .4:
        c.R(110, 30, 100, 110, (230, 226, 214)); c.R(110, 30, 100, 18, (170, 40, 50))
        bg.wtext(c, 160, 70, '72', (40, 30, 40), 40, center=True); bg.wtext(c, 160, 116, 'DÍAS', (90, 80, 90), 16, center=True)
        c.amb = (.86, .88, 1.0); c.vig = .9
        return c.render()
    k = ease((u - .4) / .6)
    _home(c, t); c.R(240, 40, 50, 96, (20, 14, 10)); c.R(240, 40, int(50 * (1 - k)) + 2, 96, (90, 60, 40))
    c.light(265, 90, 70, 60, (255, 220, 160), .9 * k)
    place(c, rpg('papa_gdt', 0), int(266 - 60 * k), FW); place(c, rpg('gdt', 0), 150, FW)
    c.amb = (1.04, .96, .88); c.vig = .7
    return c.render()


dia72 = phased(dia72_a, close('gdt', 'warm', (0, 0), 'warm'), cuts=(.72,))


def adios_a(t, u):             # se va de México: avión al atardecer
    c = cv((0, '#2a1a4a'), (.5, '#c0506a'), (1, '#ff9a50'))
    bg.hill_l(c, 130, (60, 30, 50), t); c.R(0, 150, WW, 30, (40, 24, 40))
    x = -40 + 380 * u; y = 120 - 90 * u
    c.d.polygon([(x, y), (x + 30, y - 4), (x + 34, y), (x + 4, y + 4)], fill=(230, 230, 240)); c.d.polygon([(x + 12, y), (x + 18, y - 10), (x + 22, y - 1)], fill=(200, 200, 220))
    sign(c, 160, 36, 'SE VA DE MÉXICO', (255, 236, 160), 8, (60, 20, 40))
    c.amb = (1.0, .9, .9); c.vig = .7
    return c.render()


adios = phased(adios_a)


# ================================================================ 5. El laberinto
def espana_a(t, u):            # España: patio de un orfanato con una bomba sin estallar clavada en el suelo
    c = cv((0, '#f0c070'), (1, '#e0a050'))
    c.R(0, 40, WW, 96, (214, 180, 130))
    for x in range(20, 300, 40): c.R(x, 60, 22, 40, (110, 70, 50)); c.d.ellipse([x, 52, x + 22, 70], fill=(110, 70, 50))
    c.R(0, FL - 10, WW, 54, (196, 160, 110))
    c.d.polygon([(150, 128), (170, 128), (166, 84), (154, 84)], fill=(70, 70, 64)); c.d.polygon([(154, 84), (166, 84), (160, 74)], fill=(90, 90, 82))
    c.R(150, 126, 20, 4, (140, 110, 80))
    place(c, rpg('gdt_y', 0), 240, FW); sign(c, 160, 36, 'ESPAÑA · 2001', (255, 236, 160), 16, (60, 30, 30))
    c.amb = (1.04, .98, .9); c.vig = .6
    return c.render()


espana = phased(espana_a, close('gdt', 'smile', (0, 0), 'warm'), cuts=(.7,))


def libreta_a(t, u):           # la libreta: cuatro años de notas
    c = cv((0, BLK), (1, BLK)); _desk_room(c, t)
    c.R(70, 96, 180, 70, (120, 78, 52))
    c.R(96, 100, 128, 70, (236, 226, 200)); c.R(158, 100, 4, 70, (180, 168, 140))
    for i, k in enumerate(('faun', 'bug', 'ghost', 'vamp')): _sketch(c, 102 + (i % 2) * 64, 106 + (i // 2) * 34, 50, 30, k, i)
    c.amb = (1.02, .94, .86); c.vig = .85
    return c.render()


def taxi_a(t, u):              # el taxi británico se aleja con la libreta en el asiento
    c = cv((0, '#3a4258'), (1, '#5a6278'))
    bg.brick(c, 0, 20, WW, 100, base=(120, 90, 80), mortar=(70, 54, 50), seed=11)
    for x in (40, 150, 260): bg.window(c, x, 34, 40, 44, t=t, night=False, rain=True, lights=False, seed=x)
    bg.cobble(c, 0, FL - 16, WW, 60, base=(80, 80, 96), seed=7); rain(c, t, n=80, seed=3)
    x = int(170 + 200 * ease(u))
    c.R(x - 40, 104, 80, 20, (24, 24, 28)); c.R(x - 28, 92, 52, 14, (24, 24, 28)); c.R(x - 24, 95, 20, 8, (90, 110, 140)); c.R(x + 2, 95, 18, 8, (90, 110, 140))
    c.R(x - 20, 98, 10, 4, (236, 226, 200))                                     # la libreta en el asiento
    for k in (-26, 22): c.d.ellipse([x + k - 6, 118, x + k + 6, 130], fill=(14, 14, 16))
    c.R(x - 6, 88, 12, 4, (240, 200, 60))
    place(c, rpg('gdt', 0), 90, FW)
    c.amb = (.9, .92, 1.0); c.vig = .75
    return c.render()


def recupera_a(t, u):
    c = cv((0, BLK), (1, BLK)); _desk_room(c, t)
    place(c, bat('gdt', 'hold'), 160, FM + 2)
    c.amb = (1.02, .94, .86); c.vig = .8
    return c.render()


libreta = phased(libreta_a, taxi_a, recupera_a, cuts=(.32, .78))


def _cannes(c, t, dark=False):
    c.im.paste(Image.fromarray(vgrad([(0, '#0c0816'), (1, '#1c1224')]).astype('uint8')), (0, 0))
    c.R(50, 10, 220, 80, (20, 20, 30)); c.R(54, 14, 212, 72, (10, 10, 16) if dark else (60, 80, 70))
    if not dark: _sketch(c, 140, 30, 40, 36, 'faun')
    c.R(0, 100, WW, 80, (70, 20, 30))
    for x in range(0, WW, 8): c.R(x, 100, 1, 80, (90, 30, 40))


def cannes_a(t, u):            # se apagan las luces
    c = cv((0, BLK), (1, BLK)); _cannes(c, t, dark=u < .3)
    bg.crowd(c, 118, t, seed=6, hands=False, phones=False)
    sign(c, 160, 36, 'CANNES · 27-05-2006', (255, 236, 160), 8, (60, 20, 40))
    c.amb = (.86, .86, 1.0) if u < .3 else (.96, .96, 1.04); c.vig = .9
    return c.render()


def ovacion_a(t, u):            # de pie y aplaude: reloj que corre hasta 22 minutos
    c = cv((0, BLK), (1, BLK)); _cannes(c, t)
    bg.crowd(c, 104 - int(math.sin(t * 8) * 2), t, seed=6, hands=True, phones=False)
    m = min(22, int(u * 26)); bg.wtext(c, 160, 40, f'{m:02d}:00', (255, 236, 160), 32, center=True)
    for i in range(20): c.R(int((i * 37 + t * 40) % WW), int((t * 60 + i * 23) % 100), 2, 2, (255, 230, 150))
    c.amb = (1.02, .98, 1.04); c.vig = .7
    return c.render()


cannes = phased(cannes_a, ovacion_a, close('gdt', 'smile', (0, -1), 'warm'), cuts=(.38, .8))


# ================================================================ 6. Las puertas cerradas
def _design(c, t):
    c.im.paste(Image.fromarray(vgrad([(0, '#1a2a2a'), (1, '#0e1a1a')]).astype('uint8')), (0, 0))
    bg.wallpaper(c, 0, 0, WW, FL, (50, 70, 64), (44, 64, 58), (70, 92, 86))
    for i in range(6):                                                         # láminas de diseño: montañas, castillos, criaturas
        x = 16 + i * 50; y = 18 + (i % 2) * 6; c.R(x, y, 40, 32, (226, 216, 190))
        c.d.polygon([(x + 4, y + 28), (x + 16, y + 8), (x + 26, y + 20), (x + 36, y + 28)], fill=(120, 140, 120)) if i % 2 == 0 else _sketch(c, x, y, 40, 32, 'faun' if i == 1 else 'bug')
    bg.planks(c, 0, FL, WW, 44, (60, 70, 66), seed=17, pw=9)


def hobbit_a(t, u):
    c = cv((0, BLK), (1, BLK)); _design(c, t)
    PR.keep(c, PR.drawing_desk(), 140, 94); place(c, rpg('gdt', int(t * 2) % 2 if u < .4 else 0), 120, FW)
    c.amb = (.96, 1.0, .98); c.vig = .75
    return c.render()


def retraso_a(t, u):           # la fecha se mueve: calendario que no avanza y una puerta que se cierra
    c = cv((0, '#0a0a14'), (1, '#14141e'))
    c.R(60, 30, 90, 100, (230, 226, 214)); c.R(60, 30, 90, 16, (170, 40, 50))
    bg.wtext(c, 105, 70, 'RODAJE', (40, 30, 40), 8, center=True); bg.wtext(c, 105, 90, '¿?', (170, 40, 50), 32, center=True)
    k = ease(u); c.R(200, 30, 60, 106, (14, 10, 20)); c.R(202, 32, 56, 102, (255, 210, 120)); c.R(200 + int(k * 58), 30, 60 - int(k * 58), 106, (60, 40, 30))
    place(c, rpg('gdt', 0), 230, FW + 2) if k < .9 else None
    c.amb = (.9, .9, 1.0); c.vig = .85
    return c.render()


hobbit = phased(hobbit_a, retraso_a, cuts=(.5,))


def montana_a(t, u):           # En las montañas de la locura: montañas heladas (diseño original)
    c = cv((0, '#1a2a4a'), (.6, '#6a8ab0'), (1, '#c0d0e0'))
    for i, (x, h) in enumerate(((40, 100), (110, 140), (190, 120), (270, 150))):
        c.d.polygon([(x - 70, 140), (x, 140 - h), (x + 70, 140)], fill=(90 + i * 10, 110 + i * 10, 150 + i * 6))
        c.d.polygon([(x - 18, 140 - h + 26), (x, 140 - h), (x + 18, 140 - h + 26)], fill=(236, 240, 250))
    c.R(0, 140, WW, 40, (220, 230, 240))
    for i in range(40): c.R(int((i * 53 + t * 30) % WW), int((t * 40 + i * 17) % 180), 1, 1, (255, 255, 255))
    place(c, rpg('gdt', 0), 70, 150)
    c.amb = (.9, .96, 1.08); c.vig = .7
    return c.render()


def archivo_a(t, u):           # el proyecto se archiva: caja que se cierra
    c = cv((0, '#14101a'), (1, '#20182a')); c.R(0, FL, WW, 44, (40, 32, 40))
    for x in range(20, 300, 56): c.R(x, 40, 44, 96, (70, 60, 50)); [c.R(x + 4, 44 + j * 24, 36, 18, (150, 120, 80)) for j in range(4)]
    PR.keep(c, PR.box_cardboard(60, 40), 130, 96); sign(c, 160, 86, 'ARCHIVADO · 2011', (255, 90, 90), 8, (40, 10, 24)) if u > .3 else None
    c.amb = (.9, .88, .96); c.vig = .9
    return c.render()


montana = phased(montana_a, archivo_a, close('gdt', 'sad', (0, 1), 'cold'), cuts=(.4, .78))


# ================================================================ 7. El Óscar
def _lab(c, t):
    c.im.paste(Image.fromarray(vgrad([(0, '#0a2a2a'), (1, '#063030')]).astype('uint8')), (0, 0))
    bg.wallpaper(c, 0, 0, WW, FL, (30, 70, 70), (26, 64, 64), (44, 96, 96))
    c.R(170, 30, 110, 106, (60, 110, 110)); c.R(174, 34, 102, 98, (40, 140, 160)); c.light(225, 80, 70, 60, (120, 220, 230), .6)
    for i in range(8): c.d.ellipse([186 + (i * 13) % 80, 120 - int((t * 20 + i * 15) % 80), 189 + (i * 13) % 80, 123 - int((t * 20 + i * 15) % 80)], outline=(180, 240, 250))
    bg.planks(c, 0, FL, WW, 44, (40, 60, 60), seed=27, pw=12)


def _criatura(c, x, y, t):
    """criatura anfibia de diseño original (silueta con agallas y escamas)."""
    col = (40, 110, 110); hi = (90, 190, 180)
    c.d.ellipse([x - 9, y - 40, x + 9, y - 20], fill=col); c.R(x - 8, y - 22, 16, 30, col)
    for j in range(4): c.R(x - 6 + j * 4, y - 16, 2, 20, hi)
    c.R(x - 14, y - 18, 6, 22, col); c.R(x + 8, y - 18, 6, 22, col); c.R(x - 7, y + 8, 5, 20, col); c.R(x + 2, y + 8, 5, 20, col)
    for k in (-1, 1): c.d.polygon([(x + 9 * k, y - 34), (x + 15 * k, y - 38), (x + 12 * k, y - 28)], fill=hi)
    c.R(x - 5, y - 33, 3, 2, (255, 230, 120)); c.R(x + 2, y - 33, 3, 2, (255, 230, 120))


def agua_a(t, u):
    c = cv((0, BLK), (1, BLK)); _lab(c, t)
    _criatura(c, 225, 100 + int(math.sin(t * 1.5) * 2), t)
    place(c, rpg('elisa', 0), 120, FW)
    c.amb = (.9, 1.02, 1.04); c.vig = .75
    return c.render()


def agua_b(t, u):
    c = cv((0, BLK), (1, BLK)); _lab(c, t)
    _criatura(c, 225, 100 + int(math.sin(t * 1.5) * 2), t); place(c, bat('elisa', 'stand'), 120, FM)
    c.amb = (.9, 1.02, 1.04); c.vig = .8
    return c.render()


agua = phased(agua_a, agua_b, cuts=(.5,))


def oscar_a(t, u):
    c = cv((0, BLK), (1, BLK)); _oscar_stage(c, t)
    place(c, rpg('gdt', int(t * 3) % 2 if u < .5 else 0), 60 + 100 * ease(min(1, u * 1.6)), 132, sh=False)
    c.light(160, 110, 50, 50, (255, 240, 200), .7 * ease(u)); c.amb = (1.0, .96, .9); c.vig = .8
    return c.render()


def oscar_b(t, u):
    c = cv((0, BLK), (1, BLK)); _oscar_stage(c, t, crowd=False)
    place(c, bat('gdt', 'hold'), 160, FM + 4); PR.keep(c, PR.statuette(30), 172, 92)
    for i in range(30): c.R(int((i * 37 + t * 30) % WW), int((t * 60 + i * 31) % 180), 2, 3, [(255, 220, 100), (255, 255, 255), (255, 180, 80)][i % 3])
    c.amb = (1.04, 1.0, .94); c.vig = .7
    return c.render()


oscar = phased(oscar_a, oscar_b, close('gdt', 'smile', (0, 0), 'warm'), cuts=(.42, .8))


def camino_a(t, u):            # mira el camino: las tres puertas (Mimic, El Hobbit, las montañas) y una cuarta abierta
    c = cv((0, '#0c0a14'), (1, '#1a1424')); c.R(0, FL, WW, 44, (30, 26, 34))
    labels = ('MIMIC', 'HOBBIT', 'MONTAÑAS', 'EL AGUA')
    for i, lb in enumerate(labels):
        x = 20 + i * 76; op = i == 3 or u < .2 + i * .2
        c.R(x, 44, 56, 92, (14, 10, 20)); c.R(x + 2, 46, 52, 88, (60, 200, 210) if i == 3 else ((255, 210, 120) if op else (60, 40, 30)))
        if i == 3: c.light(x + 28, 90, 50, 60, (120, 220, 230), .6)
        bg.wtext(c, x + 28, 30, lb, (255, 236, 160), 8, center=True)
    place(c, rpg('gdt', int(t * 2) % 2), 20 + 260 * u, FW)
    c.amb = (.96, .96, 1.02); c.vig = .8
    return c.render()


camino = phased(camino_a)


def final_a(t, u):              # vuelve al escritorio del principio: sigue dibujando monstruos (cierre del bucle)
    c = cv((0, BLK), (1, BLK)); _desk_room(c, t)
    place(c, bat('gdt', 'hold'), 160, FM + 2); _desk_front(c, t); x = 150 + int(math.sin(t * 9) * 4); c.R(x, 104, 2, 6, (250, 220, 120))
    PR.keep(c, PR.statuette(26), 200, 86)
    c.amb = (1.0, .92, .86); c.vig = .85
    return c.render()


final = phased(close('gdt', 'warm', (0, 1), 'warm'), final_a, cuts=(.45,))
