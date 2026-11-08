"""Historia 9 (Walt Disney) HORIZONTAL (mundo 320x180, x6). TC_LAND=1. Sin personajes ni logos reales de Disney: solo dibujos originales.
Capas (atrás->delante): fondo -> escenografía -> props -> personajes -> efectos -> carteles."""
import math, random
import numpy as np
from PIL import Image, ImageDraw
from lib import *
import bg
import props as PR
from scenes3 import rpg, bat, place
from scenes9 import phased, GOLD
from scenes10 import cv, sign, FL, FW, FM

assert WW == 320 and WH == 180
BLK = '#000000'


def _office(c, t, night=True):
    c.im.paste(Image.fromarray(vgrad([(0, '#14183a'), (1, '#2a2a46')]).astype('uint8')), (0, 0))
    bg.wallpaper(c, 0, 0, WW, FL, (60, 78, 70), (54, 70, 62), (86, 108, 96))
    c.R(0, 96, WW, 40, (92, 58, 40)); c.R(0, 96, WW, 3, (170, 120, 84))
    for x in range(0, WW, 24): c.R(x + 2, 102, 20, 30, (108, 68, 46)); c.R(x + 2, 102, 20, 1, (150, 100, 72))
    c.R(20, 14, 90, 70, (44, 34, 30)); c.R(23, 17, 84, 64, (30, 40, 96))
    bg.skyline(c, 0, 80, cols=((24, 26, 66), (40, 38, 90)), seed=15, lit=.55, t=t, wmin=8, wmax=14, hmin=12, hmax=52)
    c.R(23, 17, 84, 3, (44, 34, 30)); c.R(64, 17, 2, 64, (44, 34, 30)); c.R(20, 82, 90, 3, (170, 130, 90))
    sw = math.sin(t * 1.6) * 1.5
    for lx in (190, 270):
        c.R(lx, 0, 1, 18, (20, 20, 30)); c.d.polygon([(lx - 11 + sw, 30), (lx + 11 + sw, 30), (lx + 6 + sw, 18), (lx - 6 + sw, 18)], fill=(255, 196, 96)); c.light(lx + sw, 34, 50, 40, (255, 200, 110), .7)
    bg.planks(c, 0, FL, WW, 44, (96, 64, 48), seed=79, pw=9); c.R(0, FL - 2, WW, 3, (50, 30, 24))


def office_a(t, u):
    c = cv((0, BLK), (1, BLK)); _office(c, t)
    c.R(150, 112, 130, 6, (130, 84, 54)); c.R(150, 112, 130, 2, (200, 150, 100)); c.R(156, 118, 118, 24, (96, 60, 40))
    place(c, rpg('mintz', 0), 250, 114, sh=False)
    PR.keep(c, PR.contract(), 190, 90)
    c.R(150, 112, 130, 6, (130, 84, 54)); c.R(150, 112, 130, 2, (200, 150, 100))
    place(c, rpg('disney_y', int(t * 2) % 2 if u < .3 else 0), 120, FW + 8)
    if u > .35: bg.bubble2(c, 120, 62, 'NO', 16)
    c.amb = (.94, .94, 1.0); c.vig = .7
    return c.render()


def office_b(t, u):
    c = cv((0, BLK), (1, BLK)); _office(c, t)
    PR.keep(c, PR.contract(), 220, 100)
    place(c, bat('mintz', 'stand'), 250, FM)
    place(c, bat('disney_y', 'stand'), 110, FM + math.sin(t * 2))
    if int(t * 4) % 3: sign(c, 160, 6, '¡SE NEGÓ!', (255, 90, 90), 24, (40, 10, 24))
    c.amb = (.94, .94, 1.0); c.vig = .7
    return c.render()


def office_c(t, u):
    c = cv((0, BLK), (1, BLK)); _office(c, t)
    place(c, bat('disney_y', 'hold'), 160, FM + 2)
    k = ease(u); c.R(262, 40, 40, 70, (14, 10, 20)); c.R(264, 42, 36, 66, (255, 210, 120))
    c.R(262 + int(k * 34), 40, 40 - int(k * 34), 70, (14, 10, 20)) if k > 0 else None                  # puerta que se cierra
    bg.wtext(c, 282, 62, '?', (255, 90, 90), 24, center=True)
    c.amb = (.9, .92, 1.0); c.vig = .75
    return c.render()


office = phased(office_a, office_b, office_c, cuts=(.34, .67))


# ---------------------------------------------------------------- 2. Nueva York 1928
def _ny(c, t):
    c.im.paste(Image.fromarray(vgrad([(0, '#14204f'), (.5, '#4a4a9a'), (1, '#d07a6a')]).astype('uint8')), (0, 0))
    stars(c, t, 60, 6, 40)
    bg.skyline(c, 0, FL, cols=((30, 30, 74), (46, 42, 98), (60, 50, 110)), seed=23, lit=.5, t=t, wmin=14, wmax=26, hmin=50, hmax=130)
    bg.cobble(c, 0, FL, WW, 44, base=(84, 84, 126), seed=84); c.R(0, FL - 2, WW, 3, (150, 150, 180))
    for x in (60, 250): bg.lamp_post(c, x, FL, t, h=76)
    for i in range(70):
        ph = (t * .6 + i * .0143) % 1; c.R((i * 53) % 320, int(ph * 180), 1, 2, (236, 242, 255))        # nieve


def ny_a(t, u):
    c = cv((0, BLK), (1, BLK)); _ny(c, t)
    sign(c, 160, 8, 'NUEVA YORK · 1928', (255, 230, 120), 16, (30, 20, 60))
    place(c, rpg('disney_y', int(t * 4) % 2), 40 + 200 * u, FW + 8)
    PR.keep(c, PR.film_reel(10), 236, 100); PR.keep(c, PR.marquee_light(12), 220, 94)
    c.amb = (.94, .94, 1.04); c.vig = .65
    return c.render()


def ny_b(t, u):
    c = cv((0, BLK), (1, BLK)); _ny(c, t)
    sign(c, 160, 8, '1928', (255, 230, 120), 24, (30, 20, 60))
    place(c, bat('disney_y', 'stand'), 120 + 40 * u, FM)
    c.amb = (.94, .94, 1.04); c.vig = .65
    return c.render()


nyork = phased(ny_a, ny_b, cuts=(.5,))


# ---------------------------------------------------------------- 3. el trato peor
def worse_a(t, u):
    c = cv((0, BLK), (1, BLK)); _office(c, t)
    place(c, rpg('mintz', 0), 240, FW + 6)
    for i in range(7):
        ph = (t * .4 + i * .14) % 1; PR.keep(c, PR.money_bill(), 80 + (i * 29) % 100, int(30 + ph * 110))
    sign(c, 140, 8, 'MENOS DINERO', (255, 90, 90), 16, (40, 10, 24))
    place(c, rpg('disney_y', 0), 120, FW + 12)
    c.amb = (.94, .94, 1.0); c.vig = .7
    return c.render()


def worse_b(t, u):
    c = cv((0, BLK), (1, BLK)); _office(c, t)
    PR.keep(c, PR.contract(), 130, 60); sign(c, 160, 8, 'LOS DERECHOS NO SON TUYOS', (255, 90, 90), 8, (40, 10, 24))
    place(c, bat('mintz', 'hold'), 250, FM)
    c.amb = (.94, .94, 1.0); c.vig = .7
    return c.render()


def worse_c(t, u):
    c = cv((0, BLK), (1, BLK)); _office(c, t)
    for i, x in enumerate((50, 110, 170, 230)):
        PR.keep(c, PR.drawing_desk(), x - 20, 118); PR.keep(c, PR.chair_wait(), x + 22, 130)
        sc = ease(u * 5 - i * .6); 
        if sc > 0: bg.wtext(c, x, 100 - int((1 - sc) * 10), 'X', (255, 70, 70), 24, center=True)
    sign(c, 160, 8, 'SE LLEVÓ A SU EQUIPO', (255, 200, 90), 16, (40, 20, 10))
    place(c, bat('disney_y', 'stand'), 160, FM + 8, sh=False)
    c.amb = (.9, .9, .98); c.vig = .75
    return c.render()


worse = phased(worse_a, worse_b, worse_c, cuts=(.3, .62))


# ---------------------------------------------------------------- 4. dijo no
def _hall(c, t):
    c.im.paste(Image.fromarray(vgrad([(0, '#201830'), (1, '#0e0a18')]).astype('uint8')), (0, 0))
    bg.brick(c, 0, 0, WW, FL, base=(120, 80, 70), mortar=(64, 40, 40), seed=91, bh=8, bw=16)
    for x in (40, 130, 220):
        c.R(x, 20, 40, 90, (30, 20, 40)); c.R(x + 2, 22, 36, 86, (255, 200, 120)); c.R(x + 19, 22, 2, 86, (30, 20, 40))
        c.light(x + 20, 70, 50, 50, (255, 200, 120), .5)
    bg.planks(c, 0, FL, WW, 44, (70, 46, 40), seed=92, pw=9); c.R(0, FL - 2, WW, 3, (40, 26, 24))


def no_a(t, u):
    c = cv((0, BLK), (1, BLK)); _hall(c, t)
    place(c, rpg('disney_y', int(t * 3) % 2), 80 + 160 * u, FW + 8)
    PR.keep(c, PR.contract(), 80 + 160 * u - 30, FW - 20 + int(u * 24))
    c.amb = (.9, .9, 1.0); c.vig = .75
    return c.render()


def no_b(t, u):
    c = cv((0, BLK), (1, BLK)); _hall(c, t)
    PR.keep(c, PR.contract(), 200, 96 + int(u * 60))
    place(c, bat('disney_y', 'stand'), 140, FM)
    if int(t * 5) % 2 == 0 or u > .7: sign(c, 160, 6, '¡Y DIJO NO!', (255, 90, 90), 24, (40, 10, 24))
    c.amb = (.9, .9, 1.0); c.vig = .75
    return c.render()


def no_c(t, u):
    c = cv((0, BLK), (1, BLK)); _hall(c, t)
    place(c, bat('disney_y', 'hold'), 160, FM + 2)
    c.light(160, 90, 110, 80, (200, 210, 255), .25); c.amb = (.8, .84, .98); c.vig = .9
    if u > .3: bg.sign2(c, 160, 8, '¿Y TÚ?', (255, 230, 120), 24, plate=(20, 12, 30))
    return c.render()


dijo_no = phased(no_a, no_b, no_c, cuts=(.34, .67))


# ---------------------------------------------------------------- 5. Kansas City 1923 (sepia)
def _sepia(c):
    return c


def kansas_a(t, u):
    c = cv((0, '#3a2a20'), (1, '#1a120e')); bg.wallpaper(c, 0, 0, WW, FL, (110, 88, 66), (100, 80, 60), (140, 114, 86))
    bg.planks(c, 0, FL, WW, 44, (86, 62, 44), seed=61, pw=9); c.R(0, FL - 2, WW, 3, (50, 34, 24))
    for x in (40, 120): PR.keep(c, PR.drawing_desk(), x, 108)
    c.R(200, 40, 100, 60, (200, 180, 150)); sign(c, 250, 52, 'QUIEBRA', (230, 60, 60), 16, (60, 20, 20)); bg.wtext(c, 250, 80, '1923', (255, 230, 120), 24, center=True)
    place(c, rpg('disney_y', 0), 170, FW + 8)
    c.amb = (1.1, .96, .8); c.vig = .8
    return c.render()


def kansas_b(t, u):
    c = cv((0, '#3a2a20'), (1, '#1a120e')); bg.wallpaper(c, 0, 0, WW, FL, (110, 88, 66), (100, 80, 60), (140, 114, 86))
    bg.planks(c, 0, FL, WW, 44, (86, 62, 44), seed=61, pw=9)
    sign(c, 160, 8, 'KANSAS CITY · 1923', (255, 200, 120), 16, (50, 30, 10))
    place(c, bat('disney_k', 'hip'), 160, FM)
    c.amb = (1.1, .96, .8); c.vig = .8
    return c.render()


kansas = phased(kansas_a, kansas_b, cuts=(.5,))


# ---------------------------------------------------------------- 6. hermanos en Los Ángeles
def _la(c, t):
    c.im.paste(Image.fromarray(vgrad([(0, '#3a2a7a'), (.5, '#e0708a'), (.75, '#ffc880'), (1, '#4a3a30')]).astype('uint8')), (0, 0))
    for x in (30, 270): bg.tree(c, x, FL, 60, 'pine', (40, 120, 70))
    bg.brick(c, 70, 40, 180, 96, base=(190, 130, 98), mortar=(110, 70, 60), seed=95, bh=8, bw=16)
    c.R(70, 36, 180, 5, (140, 80, 60)); c.R(96, 56, 36, 38, (40, 30, 50)); c.R(98, 58, 32, 34, (255, 214, 130)); c.R(113, 58, 2, 34, (40, 30, 50))
    c.R(190, 56, 36, 38, (40, 30, 50)); c.R(192, 58, 32, 34, (255, 214, 130)); c.R(207, 58, 2, 34, (40, 30, 50))
    c.R(0, FL, WW, 44, (74, 70, 96)); c.R(0, FL - 2, WW, 3, (150, 140, 180))


def bros_a(t, u):
    c = cv((0, BLK), (1, BLK)); _la(c, t)
    sign(c, 160, 8, 'LO QUE LE QUEDÓ', (255, 230, 120), 16, (50, 24, 60))
    place(c, rpg('roy', int(t * 2) % 2), 110, FW + 10); place(c, rpg('disney_y', int(t * 2) % 2), 210, FW + 10)
    PR.keep(c, PR.drawing_desk(), 140, FW - 20)
    c.amb = (1.02, .96, .96); c.vig = .6
    return c.render()


def bros_b(t, u):
    c = cv((0, BLK), (1, BLK)); _la(c, t)
    c.R(80, 60, 70, 40, (240, 240, 232)); bg.wtext(c, 115, 66, '+ + +', (60, 80, 120), 16, outline=None, center=True)
    place(c, bat('roy', 'hold'), 120, FM); place(c, bat('disney_y', 'stand'), 220, FM)
    sign(c, 160, 6, 'ROY', (180, 220, 255), 16, (20, 24, 60))
    c.amb = (1.02, .96, .96); c.vig = .6
    return c.render()


bros = phased(bros_a, bros_b, cuts=(.5,))


# ---------------------------------------------------------------- 7. el amigo Ub
def _train(c, t):
    c.im.paste(Image.fromarray(vgrad([(0, '#0a0f30'), (1, '#1a1a40')]).astype('uint8')), (0, 0))
    stars(c, t, 120, 6, 120)
    off = (t * 90) % 120
    for x in range(-int(off) % 120 - 120, WW, 120): bg.tree(c, x + 60, FL, 70, 'pine', (24, 70, 56))
    c.R(0, 100, WW, 80, (60, 40, 30)); c.R(0, 100, WW, 4, (120, 80, 56))
    c.R(20, 30, 90, 56, (14, 18, 44)); c.R(22, 32, 86, 52, (20, 26, 70)); c.R(64, 32, 2, 52, (60, 40, 30))
    stars(c, t, 20, 9, 60)
    bg.planks(c, 0, FL, WW, 44, (70, 46, 36), seed=33, pw=10)


def ub_a(t, u):
    c = cv((0, BLK), (1, BLK)); _train(c, t)
    place(c, rpg('disney_y', 0), 150, FW + 10)
    n = int(u * 8)
    for i in range(n): PR.keep(c, PR.doodle_page(), 190 + (i % 4) * 22, 40 + (i // 4) * 28)
    sign(c, 160, 6, 'EN EL TREN', (255, 230, 120), 16, (30, 20, 60))
    c.amb = (.9, .92, 1.04); c.vig = .75
    return c.render()


def _studio(c, t):
    bg.wallpaper(c, 0, 0, WW, FL, (86, 70, 56), (78, 64, 50), (116, 96, 74))
    bg.planks(c, 0, FL, WW, 44, (96, 70, 50), seed=71, pw=9); c.R(0, FL - 2, WW, 3, (50, 34, 24))
    bg.window(c, 230, 20, 60, 56, t=t, curtain=(200, 150, 80), rain=False, seed=5)
    c.light(110, 80, 100, 70, (255, 214, 140), .45)


def ub_b(t, u):
    c = cv((0, BLK), (1, BLK)); _studio(c, t)
    PR.keep(c, PR.drawing_desk(), 110, 112)
    place(c, bat('ub', 'hold'), 160, FM); place(c, bat('disney_y', 'stand'), 250, FM)
    sign(c, 160, 6, 'UB IWERKS', (180, 220, 255), 16, (20, 24, 60))
    for i in range(3): PR.keep(c, PR.doodle_page(), 60 + i * 30, 60 + int(math.sin(t * 2 + i) * 3))
    c.amb = (1.02, .96, .94); c.vig = .65
    return c.render()


amigo = phased(ub_a, ub_b, cuts=(.45,))


# ---------------------------------------------------------------- 8. rechazo (sala vacía) y 9. sonido
def _theater_in(c, t):
    bg.wallpaper(c, 0, 0, WW, FL, (80, 24, 40), (72, 20, 36), (120, 56, 72))
    bg.curtain(c, 0, 26, 170, (160, 30, 50)); bg.curtain(c, 294, 26, 170, (160, 30, 50))
    bg.planks(c, 0, FL, WW, 44, (60, 40, 40), seed=44, pw=9); c.R(0, FL - 2, WW, 3, GOLD)


def reject_a(t, u):
    c = cv((0, BLK), (1, BLK)); _theater_in(c, t)
    c.R(70, 20, 180, 80, (240, 240, 236)); c.R(70, 20, 180, 3, (200, 200, 196))
    for i, x in enumerate((60, 120, 200, 260)):
        place(c, rpg(('mintz', 'prod1', 'prod2', 'rexach')[i], 0), x, FW + 10 + (i % 2) * 6, sh=False)
        if int(t * 2 + i) % 3 == 0: bg.wtext(c, x, 100, 'NO', (255, 90, 90), 16, center=True)
    sign(c, 160, 4, 'OTRO RECHAZO', (255, 90, 90), 16, (40, 10, 24))
    c.amb = (.96, .94, .98); c.vig = .7
    return c.render()


def reject_b(t, u):
    c = cv((0, BLK), (1, BLK)); _theater_in(c, t)
    PR.keep(c, PR.film_reel(14), 40 + int((t * 30) % 20), 40); PR.keep(c, PR.clapper(), 250, 110)
    place(c, bat('disney_y', 'hold'), 160, FM)
    for i in range(3): bg.wtext(c, 70 + i * 90, 36 + int(math.sin(t * 3 + i) * 4), 'NO', (255, 90, 90), 24, center=True)
    c.amb = (.96, .94, .98); c.vig = .7
    return c.render()


rechazo = phased(reject_a, reject_b, cuts=(.5,))


def sound_a(t, u):
    c = cv((0, BLK), (1, BLK)); bg.wallpaper(c, 0, 0, WW, FL, (50, 56, 100), (44, 50, 92), (80, 90, 150))
    bg.foam(c, 10, 20, 60, 70, (70, 66, 132)); bg.foam(c, 250, 20, 60, 70, (70, 66, 132))
    bg.planks(c, 0, FL, WW, 44, (100, 74, 56), seed=83, pw=9); c.R(0, FL - 2, WW, 3, (50, 30, 24))
    PR.keep(c, PR.mic_stand(), 190, 100)
    place(c, rpg('disney_y', int(t * 3) % 2), 160, FW + 8)
    for i in range(10):
        ph = (t * .7 + i * .1) % 1; bg.wtext(c, 200 + int(ph * 100), 70 - int(ph * 40), '♪' if False else '~', (120, 255, 190), 16, outline=None)
    sign(c, 160, 6, 'AHORA, CON SONIDO', (120, 255, 190), 8, (10, 40, 30))
    c.amb = (1.0, .98, 1.04); c.vig = .65
    return c.render()


def sound_b(t, u):
    c = cv((0, BLK), (1, BLK)); bg.wallpaper(c, 0, 0, WW, FL, (50, 56, 100), (44, 50, 92), (80, 90, 150))
    bg.planks(c, 0, FL, WW, 44, (100, 74, 56), seed=83, pw=9)
    PR.keep(c, PR.mic_stand(), 210, 90)
    place(c, bat('disney_y', 'hold'), 150, FM)
    for k in range(4):
        r = 14 + ((t * 40 + k * 18) % 72); c.ed.arc([232 - r, 80 - r, 232 + r, 80 + r], 300, 60, fill=(120, 255, 190, int(200 * (1 - r / 90))), width=2)
    c.amb = (1.0, .98, 1.04); c.vig = .65
    return c.render()


sonido = phased(sound_a, sound_b, cuts=(.5,))


# ---------------------------------------------------------------- 10. estreno
def _premiere(c, t):
    c.im.paste(Image.fromarray(vgrad([(0, '#14103a'), (1, '#2a1a4a')]).astype('uint8')), (0, 0))
    bg.skyline(c, 0, 110, cols=((30, 24, 70), (44, 34, 96)), seed=31, lit=.6, t=t, hmin=30, hmax=90)
    c.R(40, 30, 240, 80, (60, 24, 40)); c.R(40, 30, 240, 4, (230, 190, 90)); c.R(40, 106, 240, 4, (230, 190, 90))
    for i in range(0, 240, 12): c.R(44 + i, 34, 4, 4, (255, 236, 140) if int(t * 4 + i / 12) % 2 else (150, 120, 60), c.ed)
    c.R(0, FL - 20, WW, 64, (110, 24, 40)); c.R(0, FL - 20, WW, 3, (230, 90, 100))


def prem_a(t, u):
    c = cv((0, BLK), (1, BLK)); _premiere(c, t)
    sign(c, 160, 44, '18 · NOV · 1928', (255, 236, 140), 16, (50, 20, 30))
    for i, f in enumerate(('kid_a', 'kid_b', 'mom', 'dad', 'kid_c', 'alice', 'prod1', 'prod2')): place(c, rpg(f, int(t * 3 + i) % 2), 30 + i * 38, FW + 22 + (i % 2) * 6, sh=False)
    for i in range(40): c.R((i * 53 + math.sin(t * 3 + i) * 6) % 310 + 4, ((t * .5 + i * .025) % 1) * 176, 2, 3, ((255, 90, 120), (90, 220, 255), (255, 230, 90), (140, 255, 140))[i % 4])
    c.amb = (1.02, .98, 1.02); c.vig = .6
    return c.render()


def prem_b(t, u):
    c = cv((0, BLK), (1, BLK)); _premiere(c, t)
    sign(c, 160, 6, '¡ÉXITO!', (255, 236, 140), 24, (50, 20, 30))
    place(c, bat('disney_y', 'trophy'), 160, FM + abs(math.sin(t * 5)) * -2)
    for i in range(50): c.R((i * 47 + math.sin(t * 3 + i) * 8) % 310 + 4, ((t * .6 + i * .02) % 1) * 176, 2, 3, ((255, 90, 120), (90, 220, 255), (255, 230, 90), (140, 255, 140))[i % 4])
    c.amb = (1.02, .98, 1.02); c.vig = .6
    return c.render()


estreno = phased(prem_a, prem_b, cuts=(.5,))


# ---------------------------------------------------------------- 11. el amigo se va (1930)
def leave_a(t, u):
    c = cv((0, BLK), (1, BLK)); _studio(c, t)
    PR.keep(c, PR.drawing_desk(), 60, 112)
    x = 150 + 150 * u
    place(c, rpg('ub', int(t * 4) % 2), x, FW + 10); PR.keep(c, PR.box_cardboard(), x - 32, FW - 12)
    place(c, rpg('disney_y', 0), 90, FW + 10)
    sign(c, 160, 6, '1930', (255, 230, 120), 24, (40, 20, 40))
    c.amb = (.96, .94, .98); c.vig = .7
    return c.render()


def leave_b(t, u):
    c = cv((0, BLK), (1, BLK)); _studio(c, t)
    PR.keep(c, PR.drawing_desk(), 200, 112); PR.keep(c, PR.chair_wait(), 240, 126)
    place(c, bat('disney_y', 'stand'), 120, FM)
    c.R(270, 60, 44, 76, (20, 14, 24)); c.R(272, 62, 40, 72, (255, 210, 120)) if u < .6 else None
    c.amb = (.9, .9, .98); c.vig = .8
    return c.render()


amigo_va = phased(leave_a, leave_b, cuts=(.5,))


# ---------------------------------------------------------------- 12. derrumbe y regreso
def _night_office(c, t):
    c.im.paste(Image.fromarray(vgrad([(0, '#0a0f2a'), (1, '#1a1a36')]).astype('uint8')), (0, 0))
    bg.wallpaper(c, 0, 0, WW, FL, (50, 56, 70), (44, 50, 62), (70, 78, 96))
    bg.planks(c, 0, FL, WW, 44, (80, 58, 44), seed=21, pw=9); c.R(0, FL - 2, WW, 3, (40, 26, 20))
    c.R(120, 112, 100, 6, (110, 72, 46)); c.R(126, 118, 88, 22, (84, 54, 36))
    PR.keep(c, PR.lamp_table(), 130, 86); c.light(140, 100, 70, 60, (255, 214, 130), .6)


def down_a(t, u):
    c = cv((0, BLK), (1, BLK)); _night_office(c, t)
    for i in range(8): PR.keep(c, PR.stamp_paper(), 40 + (i * 37) % 240, FW - 6 + (i % 3) * 8)
    place(c, rpg('disney_y', 0), 170, 116, sh=False); c.R(120, 112, 100, 6, (110, 72, 46)); c.R(120, 112, 100, 2, (180, 130, 90))
    sign(c, 160, 6, '1931', (255, 230, 120), 24, (20, 20, 50))
    c.amb = (.84, .88, 1.0); c.vig = .85
    return c.render()


def down_b(t, u):
    c = cv((0, BLK), (1, BLK)); _night_office(c, t)
    place(c, bat('disney_y', 'hip'), 130, FM); place(c, bat('nurse', 'hold'), 230, FM)
    sign(c, 160, 6, 'DESCANSO', (140, 220, 255), 16, (10, 30, 60))
    c.amb = (.84, .88, 1.0); c.vig = .85
    return c.render()


def down_c(t, u):
    c = cv((0, '#2a1a5a'), (1, '#ffb070')); bg.wallpaper(c, 0, 0, WW, FL, (96, 64, 70), (88, 58, 64), (140, 100, 100))
    bg.planks(c, 0, FL, WW, 44, (110, 78, 56), seed=33, pw=9)
    c.R(20, 20, 70, 76, (255, 190, 120)); c.R(22, 22, 66, 72, (255, 220, 160))
    place(c, bat('ub', 'stand'), 220 - 60 * ease(u), FM); place(c, bat('disney_y', 'stand'), 110, FM)
    sign(c, 160, 6, '1940 · VOLVIÓ', (255, 230, 120), 16, (40, 20, 40))
    c.light(160, 90, 150, 80, (255, 220, 160), .4); c.amb = (1.04, .98, .94); c.vig = .6
    return c.render()


derrumbe = phased(down_a, down_b, down_c, cuts=(.34, .6))


# ---------------------------------------------------------------- 13. huelga 1941 (gris, sin logos)
def strike_a(t, u):
    c = cv((0, '#2a2a30'), (1, '#18181c')); bg.brick(c, 0, 0, WW, FL, base=(110, 110, 120), mortar=(60, 60, 70), seed=51, bh=8, bw=16)
    c.R(110, 20, 100, 60, (40, 40, 50)); c.R(112, 22, 96, 56, (180, 190, 210))
    place(c, rpg('disney_y', 0), 160, 70, sh=False)
    bg.planks(c, 0, FL, WW, 44, (80, 80, 90), seed=71, pw=9); c.R(0, FL - 2, WW, 3, (50, 50, 60))
    for i in range(7):
        x = 30 + i * 40 + int(math.sin(t * 2 + i) * 3)
        place(c, rpg(('kid_a', 'prod1', 'prod2', 'rexach', 'dad', 'ub', 'kid_c')[i], int(t * 2 + i) % 2), x, FW + 18 + (i % 2) * 6, sh=False)
        c.R(x + 8, FW - 18, 2, 18, (140, 100, 70)); c.R(x - 2, FW - 34, 22, 16, (240, 240, 230))            # cartel en blanco
    sign(c, 160, 6, '1941', (220, 220, 230), 24, (30, 30, 40))
    c.amb = (.84, .84, .88); c.vig = .85
    return c.render()


def strike_b(t, u):
    c = cv((0, '#2a2a30'), (1, '#18181c')); bg.brick(c, 0, 0, WW, FL, base=(110, 110, 120), mortar=(60, 60, 70), seed=51, bh=8, bw=16)
    bg.planks(c, 0, FL, WW, 44, (80, 80, 90), seed=71, pw=9)
    place(c, bat('disney_y', 'hip'), 100, FM); place(c, bat('ub', 'stand'), 230, FM)
    c.R(180, 70, 2, 70, (140, 100, 70)); c.R(160, 40, 44, 32, (240, 240, 230))
    bg.wtext(c, 182, 50, 'NO FUE', (60, 60, 80), 8, outline=None, center=True); bg.wtext(c, 182, 60, 'PERFECTO', (60, 60, 80), 8, outline=None, center=True)
    c.amb = (.84, .84, .88); c.vig = .85
    return c.render()


huelga = phased(strike_a, strike_b, cuts=(.5,))


# ---------------------------------------------------------------- 14. el conejo vuelve en 2006
def _tv(c, t):
    bg.wallpaper(c, 0, 0, WW, FL, (36, 40, 90), (30, 34, 80), (60, 66, 140))
    c.R(10, 14, 90, 70, (20, 20, 30)); c.R(13, 17, 84, 64, (40, 90, 200)); bg.wtext(c, 55, 38, 'EN VIVO', (255, 255, 255), 16, center=True)
    bg.planks(c, 0, FL, WW, 44, (70, 70, 100), seed=87, pw=9); c.R(0, FL - 2, WW, 3, (140, 140, 220))
    c.light(55, 50, 70, 50, (120, 160, 255), .45)


def back_a(t, u):
    c = cv((0, BLK), (1, BLK)); _tv(c, t)
    sign(c, 220, 8, '2006 · 78 AÑOS DESPUÉS', (255, 230, 120), 8, (30, 20, 60))
    PR.keep(c, PR.mic_stand(), 150, 100)
    place(c, rpg('dad', int(t * 2) % 2), 130, FW + 10)
    c.R(210, 90, 4, 46, (150, 150, 170)); c.R(180, 86, 64, 4, (150, 150, 170))                              # balanza
    c.R(176, 90, 24, 3, (230, 230, 240)); PR.keep(c, PR.mic_stand(), 244, 84)
    c.amb = (.96, .98, 1.06); c.vig = .65
    return c.render()


def back_b(t, u):
    c = cv((0, BLK), (1, BLK)); _tv(c, t)
    place(c, bat('dad', 'hold'), 120, FM)
    PR.keep(c, PR.mic_stand(), 160, 80)
    sign(c, 220, 8, 'UN NARRADOR', (255, 230, 120), 16, (30, 20, 60)); sign(c, 220, 40, 'POR UN CONEJO', (255, 255, 255), 16, (30, 20, 60))
    c.amb = (.96, .98, 1.06); c.vig = .65
    return c.render()


def back_c(t, u):
    c = cv((0, '#1a1a5a'), (1, '#3a2438')); stars(c, t, 220, 7, 170)
    bg.hill_l(c, 140, (14, 12, 34))
    c.R(150, 120, 20, 20, (130, 84, 54)); c.R(150, 120, 20, 2, (200, 150, 100)); c.R(152, 140, 3, 20, (110, 72, 46)); c.R(165, 140, 3, 20, (110, 72, 46))   # silla vacía
    sign(c, 160, 8, 'WALT NO LO VIO', (255, 230, 120), 16, (30, 20, 60))
    c.amb = (.9, .92, 1.1); c.vig = .75
    return c.render()


conejo = phased(back_a, back_b, back_c, cuts=(.35, .7))


# ---------------------------------------------------------------- 15. cierre
def _dawn(c, t, k):
    c.im.paste(Image.fromarray(vgrad([(0, '#1a1a5a'), (.35, '#c0408a'), (.55, '#ff9a50'), (.75, '#ffd080'), (1, '#3a2438')]).astype('uint8')), (0, 0))
    sy = 138 - 30 * k; c.d.ellipse([140, sy - 22, 180, sy + 18], fill=(255, 244, 180))
    for i in range(12):
        a = i / 12 * math.pi * 2 + t * .15
        c.d.polygon([(160, sy), (160 + 340 * math.cos(a), sy + 340 * math.sin(a)), (160 + 340 * math.cos(a + .1), sy + 340 * math.sin(a + .1))], fill=(255, 190, 130))
    bg.skyline(c, 0, 128, cols=((86, 46, 110), (104, 58, 128)), seed=21, lit=.2, t=t, hmin=20, hmax=60)
    bg.curtain(c, 0, 18, 140, (190, 56, 92), valance=False); bg.curtain(c, 302, 18, 140, (190, 56, 92), valance=False)
    bg.planks(c, 0, FL, WW, 44, (110, 66, 50), seed=73, pw=8); c.R(0, FL - 2, WW, 3, (200, 140, 100))


def close_a(t, u):
    k = ease(u); c = cv((0, BLK), (1, BLK)); _dawn(c, t, k)
    c.R(70, 104, 180, 8, (176, 112, 74)); c.R(70, 104, 180, 2, (236, 176, 124)); c.R(70, 112, 180, 24, (116, 70, 50))
    PR.keep(c, PR.doodle_page(False), 144, 66); c.light(157, 82, 60, 40, (255, 230, 150), .8)
    place(c, rpg('roy', 0), 100, 108, sh=False); place(c, rpg('ub', 0), 220, 108, sh=False); place(c, rpg('disney_y', int(t * 2) % 2 if u < .2 else 0), 160, 108, sh=False)
    c.R(70, 104, 180, 8, (176, 112, 74)); c.R(70, 104, 180, 2, (236, 176, 124))
    c.amb = (1.0 + .06 * k, .94 + .08 * k, .95); c.vig = .6
    return c.render()


def close_b(t, u):
    k = ease(u); c = cv((0, BLK), (1, BLK)); _dawn(c, t, k)
    c.R(40, 150, 240, 8, (176, 112, 74)); c.R(40, 158, 240, 22, (116, 70, 50))
    place(c, bat('you', 'hold').crop((0, 0, 86, 92)), 96, 150, sh=False)
    PR.keep(c, PR.book_open(90, 32, 6), 140, 124); c.light(184, 138, 80, 40, (255, 230, 150), .8)
    for i in range(18): c.R(130 + (i * 37 + math.sin(t * 2 + i) * 5) % 110, 130 - ((t * .45 + i * .056) % 1) * 90, 2, 2, (255, 236, 170))
    c.amb = (1.0 + .06 * k, .94 + .08 * k, .95); c.vig = .6
    return c.render()


cierre = phased(close_a, close_b, cuts=(.55,))


def portrait_land(t, who='disney_y', expr='n', look=(0, 0), tone='cold'):
    from scenes10 import portrait_land as P
    return P(t, who, expr, look, tone)
