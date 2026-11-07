"""Historia 7 (Dolly Parton): el NO que valió millones. Toma ancha (chibi) + toma media (trainer) con corte duro.
Capas (de atrás a delante): fondo -> escenografía -> props -> personajes -> efectos (papeles, billetes, notas) -> carteles."""
import math, random
import numpy as np
from PIL import Image, ImageDraw
from lib import *
import bg
import props as PR
from scenes3 import rpg, bat, place
from scenes6 import top_half

GOLD = (230, 190, 90)


def _stage(c, t, wall=(120, 30, 90), wall2=(104, 24, 80), curtains=(176, 30, 62), spots=None, crowd_on=True, rays=False):
    """escenario de teatro: telón de fondo con motivo, cortinas con pliegues, truss con focos, bocinas, suelo barnizado con reflejos y público."""
    bg.wallpaper(c, 0, 0, WW, 206, wall, wall2, tuple(min(255, v + 56) for v in wall))
    # arco de proscenio dorado y estrellas del telón
    for i in range(7): c.d.polygon([(80 + (i - 3) * 20, 70), (84 + (i - 3) * 20, 80), (80 + (i - 3) * 20, 90), (76 + (i - 3) * 20, 80)], fill=shade(wall, 1.5))
    bg.curtain(c, 0, 22, 196, curtains); bg.curtain(c, 138, 22, 196, curtains)
    bg.truss(c, 18, spots or [(255, 130, 170), (130, 210, 255), (255, 226, 130), (170, 255, 170), (255, 130, 170)], t)
    bg.planks(c, 0, 204, WW, 96, (150, 98, 62), seed=61, pw=9); c.R(0, 202, WW, 3, GOLD); c.R(0, 205, WW, 1, (90, 56, 36))
    for i in range(10):                                                         # reflejos de los focos en el suelo
        c.R(18 + i * 14, 212 + (i % 3) * 8, 6, 1, (255, 230, 190))
    bg.speaker(c, 24, 160, 20, 36); bg.speaker(c, 116, 160, 20, 36)
    if rays:
        for i in range(14):
            a = i / 14 * math.pi * 2 + t * .25
            c.ed.polygon([(80, 140), (80 + 260 * math.cos(a), 140 + 260 * math.sin(a)), (80 + 260 * math.cos(a + .12), 140 + 260 * math.sin(a + .12))], fill=(255, 150, 200, 20))
    if crowd_on: bg.crowd(c, 266, t, seed=4)


# ============================================================ 1. el NO a Elvis (hook)
def duel_wide(t, u):
    c = Canvas(vgrad([(0, '#2a1a3a'), (1, '#12081e')]))
    _stage(c, t)
    c.light(80, 150, 110, 120, (255, 220, 160), .6)
    place(c, rpg('dolly', int(t * 3) % 2), 44, 232)
    place(c, rpg('elvis', 0), 118, 232, flip=True)
    PR.keep(c, PR.mic_stand(), 82, 166)
    if u > .3: bg.bubble2(c, 44, 122 - int(2 * math.sin(t * 8)), 'NO', 16)
    c.amb = (1.0, .94, .98); c.vig = .65
    return c.render()


def duel_med(t, u):
    c = Canvas(vgrad([(0, '#2a1a3a'), (1, '#12081e')]))
    _stage(c, t, rays=True)
    c.light(80, 150, 100, 110, (255, 220, 160), .6)
    PR.keep(c, PR.mic_stand(), 78, 178)
    place(c, bat('elvis', 'stand'), 128, 238)
    place(c, bat('dolly', 'toss'), 52, 242 + abs(math.sin(t * 6)) * -2)
    if int(t * 5) % 2 == 0 or u > .8: bg.sign2(c, 54, 66, 'NO', (255, 70, 90), 24, plate=(40, 14, 40))
    c.amb = (1.0, .94, .98); c.vig = .65
    return c.render()


# ============================================================ 2. cabaña pobre -> Nashville
def cabin_wide(t, u):
    c = Canvas(vgrad([(0, '#12204f'), (.3, '#4a3a9a'), (.5, '#e0708a'), (.68, '#ffc880'), (1, '#2a3a2a')]))
    stars(c, t, 40, 11, 70)
    c.d.ellipse([112, 34, 128, 50], fill=(250, 244, 214))
    for k, (col, base) in enumerate((((60, 66, 128), 150), ((46, 70, 104), 168), ((40, 84, 80), 184))):         # colinas en capas
        c.d.polygon([(0, base), (24, base - 22 + k * 4), (60, base - 6), (96, base - 28 + k * 6), (130, base - 8), (160, base - 20), (160, 210), (0, 210)], fill=col)
    for x, h, kind in ((10, 40, 'pine'), (30, 34, 'pine'), (128, 44, 'pine'), (146, 36, 'pine'), (112, 30, 'round')): bg.tree(c, x, 196, h, kind, (36, 96, 70))
    c.R(0, 196, WW, 110, (66, 112, 58)); c.R(0, 196, WW, 3, (130, 186, 100))
    for x in range(2, WW, 6): c.R(x, 202 + (x * 7) % 40, 1, 3, (98, 156, 84))
    # cabaña de troncos con porche, chimenea con humo, ventanas con luz cálida
    for y in range(140, 196, 7):
        c.R(32, y, 96, 6, (130, 84, 52)); c.R(32, y, 96, 1, (176, 122, 82)); c.R(32, y + 5, 96, 1, (84, 52, 34))
        c.d.ellipse([28, y, 36, y + 6], fill=(150, 100, 64)); c.d.ellipse([124, y, 132, y + 6], fill=(150, 100, 64))
    c.d.polygon([(24, 142), (136, 142), (112, 108), (48, 108)], fill=(96, 56, 42)); c.R(24, 140, 112, 3, (150, 100, 72))
    for k in range(48, 112, 6): c.R(k, 110, 1, 30, (70, 40, 32))
    c.R(104, 94, 9, 22, (110, 100, 108)); c.R(103, 92, 11, 3, (150, 140, 150)); bg.smoke(c, 108, 92, t)
    c.R(66, 156, 20, 40, (66, 40, 30)); c.R(68, 158, 16, 36, (96, 62, 46)); c.R(81, 176, 2, 2, (240, 200, 110))
    for wx in (40, 102):
        c.R(wx - 1, 158, 22, 20, (70, 44, 34)); c.R(wx, 159, 20, 18, (255, 214, 130)); c.R(wx + 9, 159, 2, 18, (70, 44, 34)); c.R(wx, 167, 20, 2, (70, 44, 34))
        c.light(wx + 10, 168, 30, 24, (255, 214, 130), .6)
    c.R(26, 190, 108, 6, (150, 100, 66)); c.R(26, 190, 108, 1, (200, 150, 104))                                  # porche
    bg.fence(c, 0, 30, 204); bg.fence(c, 130, 160, 204)
    for i in range(7):                                                                                        # luciérnagas
        ph = (t * .4 + i * .15) % 1; fx = 20 + (i * 53) % 120 + math.sin(t * 2 + i) * 6; fy = 150 + (i * 31) % 50
        if int(t * 3 + i) % 4: c.R(fx, fy, 2, 2, (255, 246, 150), c.ed)
    for i, f in enumerate(('kid_a', 'kid_b', 'kid_c', 'dolly_y')):
        place(c, rpg(f, int(t * 2 + i) % 2), 22 + i * 34, 238, sh=True)
    c.amb = (1.0, .96, .96); c.vig = .6
    return c.render()


def bus_med(t, u):
    c = Canvas(vgrad([(0, '#1a2a6a'), (.4, '#e0508a'), (.7, '#ffc880'), (1, '#2a2038')]))
    off = (t * 24) % 160
    bg.skyline(c, 0, 196, cols=((66, 40, 110), (84, 52, 128)), seed=8, lit=.5, t=t, hmin=40, hmax=110)
    # fachadas de ladrillo de Nashville con rótulos de neón y toldos
    for x in range(-int(off) % 80 - 80, WW, 80):
        bg.brick(c, x, 120, 76, 86, base=(170, 90, 74), mortar=(90, 50, 46), seed=int(x) % 9 + 1, bh=7, bw=14)
        c.R(x + 6, 150, 28, 30, (30, 20, 40)); c.R(x + 8, 152, 24, 26, (255, 214, 130)); c.R(x + 19, 152, 2, 26, (30, 20, 40))
        c.R(x + 6, 142, 28, 6, (196, 60, 80)); [c.R(x + 6 + k, 142, 4, 6, (240, 220, 200)) for k in range(0, 28, 8)]
        c.R(x + 42, 150, 26, 30, (30, 20, 40)); c.R(x + 44, 152, 22, 26, (255, 160, 110))
    for x in range(-int(off * 1.4) % 160 - 160, WW + 40, 160): bg.sign2(c, x + 60, 92, 'HONKY TONK', (255, 100, 170), 8, plate=(40, 14, 40), emissive=True)
    c.R(0, 196, WW, 6, (160, 150, 180)); bg.cobble(c, 0, 202, WW, 98, base=(88, 88, 146), seed=83)
    bg.puddle_reflections(c, 214, 60, t * 3)
    for x in range(-int(off * 1.7) % 160 - 160, WW + 40, 160): bg.lamp_post(c, x + 20, 206, t, h=100)
    bg.sign2(c, 80, 62, 'NASHVILLE', (255, 230, 120), 16, plate=(40, 20, 60))
    PR.keep(c, PR.bus(), 62 + int(math.sin(t * 7)), 170)
    place(c, bat('dolly_y', 'stand'), 46, 240)
    PR.keep(c, PR.box_cardboard(24, 18), 82, 224)
    c.amb = (1.0, .94, .98); c.vig = .6
    return c.render()


# ============================================================ 3. la canción (estudio de grabación)
def _studio(c, t):
    bg.wallpaper(c, 0, 0, WW, 206, (60, 56, 110), (52, 48, 102), (90, 86, 150))
    bg.foam(c, 6, 40, 44, 56, (70, 66, 132)); bg.foam(c, 110, 40, 44, 56, (70, 66, 132)); bg.foam(c, 6, 100, 44, 56, (60, 56, 120)); bg.foam(c, 110, 100, 44, 56, (60, 56, 120))
    c.R(52, 56, 56, 84, (22, 20, 40)); c.R(54, 58, 52, 80, (120, 170, 210)); c.R(54, 58, 52, 4, (200, 230, 250)); c.R(79, 58, 2, 80, (22, 20, 40))       # cristal de la cabina
    bg.console(c, 58, 112, 44, t)
    bg.sign2(c, 80, 30, 'EN EL AIRE', (255, 70, 70), 8, plate=(40, 10, 16), emissive=True)
    bg.gold_record(c, 18, 166, 18); bg.gold_record(c, 124, 166, 18)
    bg.planks(c, 0, 206, WW, 90, (110, 80, 60), seed=73, pw=9); c.R(0, 204, WW, 3, (60, 40, 30))
    c.R(34, 232, 92, 30, (186, 66, 80)); c.R(34, 232, 92, 2, (240, 130, 140)); c.R(38, 236, 84, 22, (150, 46, 66))      # alfombra
    PR.keep(c, PR.plant(), 128, 176)
    c.light(80, 140, 80, 80, (255, 214, 140), .45)


def song_wide(t, u):
    c = Canvas(vgrad([(0, '#2a1a3a'), (1, '#12081e')]))
    _studio(c, t)
    PR.keep(c, PR.mic_stand(), 96, 176)
    place(c, rpg('dolly', int(t * 2) % 2), 66, 238)
    PR.keep(c, PR.guitar(), 84, 192)
    for i in range(6):
        ph = (t * .5 + i * .17) % 1; xx = 20 + (i * 29) % 120; yy = 200 - ph * 120
        c.d.ellipse([xx, yy, xx + 4, yy + 3], fill=(255, 230, 120)); c.R(xx + 3, yy - 6, 1, 7, (255, 230, 120))
    c.amb = (1.0, .96, .98); c.vig = .65
    return c.render()


def song_med(t, u):
    c = Canvas(vgrad([(0, '#2a1a3a'), (1, '#12081e')]))
    _studio(c, t)
    PR.keep(c, PR.mic_stand(), 12, 160)
    place(c, bat('dolly', 'hold'), 80, 244 + math.sin(t * 3))
    for i in range(10):
        ph = (t * .5 + i * .1) % 1; xx = 10 + (i * 31) % 140; yy = 200 - ph * 130
        c.d.ellipse([xx, yy, xx + 5, yy + 4], fill=(255, 230, 120)); c.R(xx + 4, yy - 8, 1, 9, (255, 230, 120)); c.R(xx + 4, yy - 8, 4, 2, (255, 230, 120))
    c.amb = (1.0, .96, .98); c.vig = .65
    return c.render()


# ============================================================ 4. el manager pide la mitad
def _office(c, t):
    bg.wallpaper(c, 0, 0, WW, 206, (70, 90, 70), (62, 82, 62), (96, 120, 96))
    c.R(0, 150, WW, 56, (96, 60, 40)); c.R(0, 150, WW, 3, (170, 120, 84))                                        # paneles de madera
    for x in range(0, WW, 20): c.R(x + 2, 156, 16, 44, (110, 70, 48)); c.R(x + 2, 156, 16, 1, (150, 100, 72)); c.R(x + 2, 199, 16, 1, (70, 44, 32))
    c.R(96, 40, 52, 66, (50, 36, 30)); c.R(98, 42, 48, 62, (40, 54, 110))                                       # ventana con ciudad
    bg.skyline(c, 0, 104, cols=((30, 30, 70), (44, 40, 90)), seed=15, lit=.5, t=t, wmin=6, wmax=10, hmin=10, hmax=40)
    c.R(96, 40, 52, 66, (0, 0, 0, 0)) if False else None
    c.R(96, 40, 52, 3, (50, 36, 30)); c.R(120, 42, 2, 62, (50, 36, 30)); c.R(96, 104, 52, 3, (50, 36, 30))
    bg.gold_record(c, 14, 62, 20); bg.gold_record(c, 44, 62, 20)
    PR.keep(c, PR.plant(), 6, 126)
    bg.planks(c, 0, 206, WW, 90, (96, 64, 48), seed=79, pw=9); c.R(0, 204, WW, 3, (50, 30, 24))
    c.R(26, 232, 108, 28, (80, 50, 70)); c.R(26, 232, 108, 2, (150, 100, 130))
    c.light(120, 120, 60, 60, (255, 214, 140), .35)


def office_wide(t, u):
    c = Canvas(vgrad([(0, '#2a2a46'), (1, '#1a1a2c')]))
    _office(c, t)
    c.R(20, 176, 120, 6, (130, 84, 54)); c.R(26, 182, 108, 30, (96, 60, 40))
    place(c, rpg('prod1', 0, 'tux'), 118, 176)
    PR.keep(c, PR.lamp_table(), 126, 150)
    c.R(20, 176, 120, 6, (130, 84, 54)); c.R(20, 176, 120, 2, (200, 150, 100))
    PR.keep(c, PR.contract(), 60, 156)
    place(c, rpg('dolly', 0), 36, 232)
    bg.sign2(c, 62, 112, 'MITAD', (255, 90, 90), 16, plate=(40, 14, 20))
    c.amb = (.96, .96, .94); c.vig = .7
    return c.render()


def office_med(t, u):
    c = Canvas(vgrad([(0, '#2a2a46'), (1, '#1a1a2c')]))
    _office(c, t)
    PR.keep(c, PR.contract(), 22, 150 + int(math.sin(t * 4) * 2))
    place(c, bat('prod1', 'hold', 'tux'), 104, 238)
    bg.sign2(c, 40, 112, 'MITAD', (255, 90, 90), 16, plate=(40, 14, 20))
    c.amb = (.96, .96, .94); c.vig = .7
    return c.render()


# ============================================================ 6. Whitney y los millones
def _arena(c, t):
    bg.wallpaper(c, 0, 0, WW, 206, (50, 34, 128), (44, 30, 116), (96, 76, 200))
    for i in range(14):                                                           # pantalla LED con rayos
        a = i / 14 * math.pi * 2 + t * .3
        c.ed.polygon([(80, 120), (80 + 260 * math.cos(a), 120 + 260 * math.sin(a)), (80 + 260 * math.cos(a + .12), 120 + 260 * math.sin(a + .12))], fill=(150, 130, 255, 24))
    bg.curtain(c, 0, 18, 196, (90, 40, 170)); bg.curtain(c, 142, 18, 196, (90, 40, 170))
    bg.truss(c, 16, [(255, 130, 220), (130, 220, 255), (255, 240, 130), (140, 255, 170), (255, 130, 220)], t)
    bg.planks(c, 0, 204, WW, 96, (110, 80, 130), seed=87, pw=9); c.R(0, 202, WW, 3, (200, 170, 255))
    bg.speaker(c, 22, 164, 20, 36); bg.speaker(c, 118, 164, 20, 36)
    for i in range(24):                                                           # billetes (detrás de los personajes)
        ph = (t * .7 + i * .04) % 1; PR.keep(c, PR.money_bill(), (i * 37) % 140 + 4, int(ph * 260) - 10)
    for i in range(5):
        PR.keep(c, PR.vinyl(9), 10 + i * 32, 124 + (i % 2) * 18 + int(math.sin(t * 4 + i) * 2))
    c.light(80, 140, 100, 110, (200, 200, 255), .6)


def whitney_wide(t, u):
    c = Canvas(vgrad([(0, '#1a1a5a'), (1, '#12081e')]))
    _arena(c, t)
    PR.keep(c, PR.mic_stand(), 100, 170)
    place(c, rpg('whitney', int(t * 2) % 2), 76, 232)
    bg.crowd(c, 262, t, seed=9, cols=((16, 10, 36), (24, 14, 48), (12, 8, 30)))
    c.amb = (1.0, .96, 1.02); c.vig = .6
    return c.render()


def whitney_med(t, u):
    c = Canvas(vgrad([(0, '#1a1a5a'), (1, '#12081e')]))
    _arena(c, t)
    PR.keep(c, PR.mic_stand(), 108, 178)
    place(c, bat('whitney', 'stand'), 74, 240 + math.sin(t * 3))
    bg.sign2(c, 80, 60, 'MILLONES', (255, 230, 120), 16, plate=(40, 20, 80))
    c.amb = (1.0, .96, 1.02); c.vig = .6
    return c.render()


# ============================================================ 8. romper el contrato
def _torn_bg(c, t):
    c.R(0, 0, WW, 206, (150, 70, 110))
    bg.wallpaper(c, 0, 0, WW, 206, (150, 70, 110), (138, 62, 100), (196, 116, 156))
    bg.curtain(c, 0, 20, 196, (200, 50, 80)); bg.curtain(c, 140, 20, 196, (200, 50, 80))
    for i in range(16):                                                           # guirnalda de banderines
        x = 22 + i * 7; y = 44 + int(8 * math.sin(i / 15 * math.pi))
        c.d.polygon([(x, y), (x + 6, y), (x + 3, y + 8)], fill=((255, 214, 90), (90, 220, 255), (255, 130, 170), (140, 255, 150))[i % 4])
    c.R(22, 44, 118, 1, (60, 40, 50))
    bg.planks(c, 0, 206, WW, 90, (150, 96, 60), seed=83, pw=9); c.R(0, 204, WW, 3, GOLD)
    bg.beam(c, 80, 20, 8, 70, 206, (255, 240, 200), 40)
    c.light(80, 170, 90, 90, (255, 220, 170), .6)


def torn_wide(t, u):
    c = Canvas(vgrad([(0, '#1a2a6a'), (.5, '#e0608a'), (1, '#2a2038')]))
    _torn_bg(c, t)
    for i in range(14):
        ph = (t * .6 + i * .07) % 1; xx = (i * 41 + math.sin(t * 3 + i) * 8) % 140 + 6; yy = int(ph * 260) - 10
        c.R(xx, yy, 8, 10, (252, 248, 236)); c.R(xx, yy, 8, 1, (210, 206, 190)); c.R(xx + 2, yy + 4, 4, 1, (150, 146, 170))
    place(c, rpg('dolly', int(t * 3) % 2), 80, 232)
    c.amb = (1.0, .94, .98); c.vig = .6
    return c.render()


def torn_med(t, u):
    c = Canvas(vgrad([(0, '#1a2a6a'), (.5, '#e0608a'), (1, '#2a2038')]))
    _torn_bg(c, t)
    for i in range(22):
        ph = (t * .8 + i * .045) % 1; xx = (i * 37 + math.sin(t * 3 + i) * 8) % 140 + 6; yy = int(ph * 280) - 10
        c.R(xx, yy, 9, 11, (252, 248, 236)); c.R(xx, yy, 9, 1, (210, 206, 190)); c.R(xx + 2, yy + 4, 5, 1, (150, 146, 170))
    place(c, bat('dolly', 'toss'), 80, 242 + abs(math.sin(t * 5)) * -2)
    bg.sign2(c, 80, 72, 'NO', (255, 90, 110), 24, plate=(40, 14, 40))
    c.amb = (1.0, .94, .98); c.vig = .6
    return c.render()


# ============================================================ 9. tú: ¿sí o no?
def _finale_bg(c, t, k, sy):
    c.d.ellipse([60, sy - 24, 100, sy + 20], fill=(255, 244, 180))
    for i in range(12):
        a = i / 12 * math.pi * 2 + t * .15
        c.d.polygon([(80, sy), (80 + 200 * math.cos(a), sy + 200 * math.sin(a)), (80 + 200 * math.cos(a + .1), sy + 200 * math.sin(a + .1))], fill=(255, 190, 130))
    for i in range(3):                                                            # nubes
        cx = (t * (3 + i) + i * 60) % 200 - 30; c.R(cx, 40 + i * 18, 30, 5, (255, 190, 200)); c.R(cx + 6, 36 + i * 18, 18, 5, (255, 214, 220))
    bg.skyline(c, 0, 172, cols=((86, 46, 110), (104, 58, 128)), seed=21, lit=.2, t=t)
    for kx, col in ((0, (200, 70, 100)), (1, (170, 50, 84))): pass
    bg.curtain(c, 0, 12, 184, (190, 56, 92), valance=False); bg.curtain(c, 148, 12, 184, (190, 56, 92), valance=False)
    bg.planks(c, 0, 190, WW, 110, (110, 66, 50), seed=73, pw=8); c.R(0, 188, WW, 3, (200, 140, 100))


def finale_wide(t, u):
    k = ease(u * 1.1); c = Canvas(vgrad([(0, '#1a1a5a'), (.35, '#c0408a'), (.55, '#ff9a50'), (.75, '#ffd080'), (1, '#3a2438')]))
    _finale_bg(c, t, k, 130 - 30 * k)
    c.R(14, 160, 132, 8, (176, 112, 74)); c.R(14, 160, 132, 2, (236, 176, 124)); c.R(14, 168, 132, 22, (116, 70, 50))
    PR.keep(c, PR.contract(), 70, 118); PR.keep(c, PR.contract(), 98, 120)
    bg.wtext(c, 87, 128, 'SÍ', (40, 130, 70), 16, outline=None, center=True); bg.wtext(c, 115, 130, 'NO', (190, 50, 60), 16, outline=None, center=True)
    PR.keep(c, PR.lamp_table(), 128, 134)
    place(c, top_half(rpg('you', 0), .8), 38, 162, sh=False)
    c.R(14, 160, 132, 8, (176, 112, 74)); c.R(14, 160, 132, 2, (236, 176, 124))
    c.light(100, 140, 70, 40, (255, 230, 150), .35)
    c.amb = (1.0 + .06 * k, .94 + .08 * k, .95); c.vig = .6
    return c.render()


def finale_med(t, u):
    k = ease(u * 1.1); c = Canvas(vgrad([(0, '#1a1a5a'), (.35, '#c0408a'), (.55, '#ff9a50'), (.75, '#ffd080'), (1, '#3a2438')]))
    _finale_bg(c, t, k, 118 - 24 * k)
    place(c, bat('you', 'hold').crop((0, 0, 86, 92)), 40, 176, sh=False)
    c.R(10, 172, 140, 8, (176, 112, 74)); c.R(10, 172, 140, 2, (236, 176, 124)); c.R(10, 180, 140, 26, (116, 70, 50))
    PR.keep(c, PR.contract(), 74, 126); PR.keep(c, PR.contract(), 110, 128)
    bg.wtext(c, 91, 138, 'SÍ', (40, 130, 70), 16, outline=None, center=True); bg.wtext(c, 127, 140, 'NO', (190, 50, 60), 16, outline=None, center=True)
    c.light(104, 146, 80, 50, (255, 230, 150), .35)
    for i in range(18):
        ph = (t * .45 + i * .056) % 1; xx = 60 + (i * 37 + math.sin(t * 2 + i) * 5) % 90; yy = 170 - ph * 120
        c.R(xx, yy, 2, 2, (255, 236, 170))
    c.amb = (1.0 + .06 * k, .94 + .08 * k, .95); c.vig = .6
    return c.render()


CUT = .5
def duel(t, u): return duel_wide(t, u / CUT) if u < CUT else duel_med(t, u)
def cabin(t, u): return cabin_wide(t, u / CUT) if u < CUT else bus_med(t, u)
def song(t, u): return song_wide(t, u / CUT) if u < CUT else song_med(t, u)
def office(t, u): return office_wide(t, u / CUT) if u < CUT else office_med(t, u)
def whitney(t, u): return whitney_wide(t, u / CUT) if u < CUT else whitney_med(t, u)
def torn(t, u): return torn_wide(t, u / CUT) if u < CUT else torn_med(t, u)
def finale(t, u): return finale_wide(t, u / .45) if u < .45 else finale_med(t, u)
