"""Historia 9 (Walt Disney) SHORT VERTICAL (mundo 160x284, x8). Dibujos originales, sin personajes ni logos reales.
Suelo y=206; pies chibi y=232; pies trainer y=252. Capas: fondo -> escenografia -> props -> personajes -> efectos -> carteles."""
import math
import numpy as np
from PIL import Image
from lib import *
import bg
import props as PR
from scenes3 import rpg, bat, place
from scenes9 import phased

assert WW == 160 and WH == 284
BLK = '#000000'
FLR, FW, FM = 206, 232, 252


def cv(*stops): return Canvas(vgrad(list(stops)))


def sign(c, x, y, txt, col, size=16, plate=(16, 12, 30)): return bg.sign2(c, x, y, txt, col, size, plate=plate)


def _hall(c, t):
    c.im.paste(Image.fromarray(vgrad([(0, '#201830'), (1, '#0e0a18')]).astype('uint8')), (0, 0))
    bg.brick(c, 0, 0, WW, FLR, base=(120, 80, 70), mortar=(64, 40, 40), seed=91, bh=8, bw=16)
    for x in (22, 98):
        c.R(x, 60, 40, 130, (30, 20, 40)); c.R(x + 2, 62, 36, 126, (255, 200, 120)); c.R(x + 19, 62, 2, 126, (30, 20, 40))
        c.light(x + 20, 120, 50, 80, (255, 200, 120), .5)
    bg.planks(c, 0, FLR, WW, 90, (70, 46, 40), seed=92, pw=9); c.R(0, FLR - 2, WW, 3, (40, 26, 24))


def hall_a(t, u):
    c = cv((0, BLK), (1, BLK)); _hall(c, t)
    place(c, rpg('disney_y', int(t * 3) % 2), 110 - 60 * u, FW)
    c.amb = (.9, .9, 1.0); c.vig = .75
    return c.render()


def hall_b(t, u):
    c = cv((0, BLK), (1, BLK)); _hall(c, t)
    PR.keep(c, PR.contract(), 104, 120 + int(u * 24))
    place(c, bat('disney_y', 'stand'), 70, FM)
    c.amb = (.9, .9, 1.0); c.vig = .75
    return c.render()


hall = phased(hall_a, hall_b, cuts=(.45,))


def _office(c, t):
    c.im.paste(Image.fromarray(vgrad([(0, '#14183a'), (1, '#2a2a46')]).astype('uint8')), (0, 0))
    bg.wallpaper(c, 0, 0, WW, FLR, (60, 78, 70), (54, 70, 62), (86, 108, 96))
    c.R(0, 120, WW, 86, (92, 58, 40)); c.R(0, 120, WW, 3, (170, 120, 84))
    for x in range(0, WW, 24): c.R(x + 2, 128, 20, 70, (108, 68, 46)); c.R(x + 2, 128, 20, 1, (150, 100, 72))
    c.R(14, 30, 70, 64, (44, 34, 30)); c.R(17, 33, 64, 58, (30, 40, 96))
    bg.skyline(c, 0, 90, cols=((24, 26, 66), (40, 38, 90)), seed=15, lit=.55, t=t, wmin=8, wmax=14, hmin=12, hmax=40)
    c.R(17, 33, 64, 3, (44, 34, 30)); c.R(48, 33, 2, 58, (44, 34, 30)); c.R(14, 94, 70, 3, (170, 130, 90))
    sw = math.sin(t * 1.6) * 1.5
    for lx in (110, 146):
        c.R(lx, 0, 1, 28, (20, 20, 30)); c.d.polygon([(lx - 10 + sw, 40), (lx + 10 + sw, 40), (lx + 6 + sw, 28), (lx - 6 + sw, 28)], fill=(255, 196, 96)); c.light(lx + sw, 44, 44, 40, (255, 200, 110), .7)
    bg.planks(c, 0, FLR, WW, 90, (96, 64, 48), seed=79, pw=9); c.R(0, FLR - 2, WW, 3, (50, 30, 24))


def office_a(t, u):
    c = cv((0, BLK), (1, BLK)); _office(c, t)
    c.R(70, 170, 80, 6, (130, 84, 54)); c.R(70, 170, 80, 2, (200, 150, 100)); c.R(74, 176, 72, 40, (96, 60, 40))
    place(c, rpg('mintz', 0), 124, 172, sh=False)
    PR.keep(c, PR.contract(), 84, 140)
    c.R(70, 170, 80, 6, (130, 84, 54)); c.R(70, 170, 80, 2, (200, 150, 100))
    place(c, rpg('disney_y', 0), 40, FW + 4)
    c.amb = (.94, .94, 1.0); c.vig = .7
    return c.render()


def office_b(t, u):
    c = cv((0, BLK), (1, BLK)); _office(c, t)
    place(c, bat('mintz', 'stand'), 112, FM)
    PR.keep(c, PR.contract(), 50, 150)
    c.amb = (.94, .94, 1.0); c.vig = .7
    return c.render()


def office_c(t, u):
    c = cv((0, BLK), (1, BLK)); _office(c, t)
    place(c, bat('disney_y', 'hold'), 80, FM + 2)
    c.amb = (.88, .9, 1.0); c.vig = .8
    return c.render()


office = phased(office_a, office_b, cuts=(.55,))


def _studio(c, t):
    c.im.paste(Image.fromarray(vgrad([(0, '#241a38'), (1, '#120e20')]).astype('uint8')), (0, 0))
    bg.wallpaper(c, 0, 0, WW, FLR, (70, 62, 96), (64, 56, 90), (96, 88, 130))
    bg.planks(c, 0, FLR, WW, 90, (86, 60, 50), seed=33, pw=9); c.R(0, FLR - 2, WW, 3, (40, 26, 24))
    for i, y in enumerate((120, 160)):
        c.R(10, y, 140, 5, (130, 84, 54)); c.R(10, y, 140, 2, (200, 150, 100))
        for k in range(4): PR.keep(c, PR.doodle_page(False), 20 + k * 34, y - 22)


def anim_a(t, u):
    c = cv((0, BLK), (1, BLK)); _studio(c, t)
    place(c, rpg('mintz', 0), 80, 214, sh=False)
    c.amb = (.94, .94, 1.0); c.vig = .7
    return c.render()


anim = phased(anim_a)


def stay_a(t, u):
    c = cv((0, BLK), (1, BLK)); _hall(c, t)
    place(c, bat('disney_y', 'hold'), 80, FM + 2)
    c.light(80, 150, 110, 80, (200, 210, 255), .25); c.amb = (.8, .84, .98); c.vig = .9
    return c.render()


stay = phased(stay_a)


def _tv(c, t):
    bg.wallpaper(c, 0, 0, WW, FLR, (36, 40, 90), (30, 34, 80), (60, 66, 140))
    c.R(14, 40, 100, 66, (20, 20, 30)); c.R(17, 43, 94, 60, (40, 90, 200)); bg.wtext(c, 64, 66, 'EN VIVO', (255, 255, 255), 8, center=True)
    c.light(64, 72, 80, 50, (120, 160, 255), .45)
    bg.planks(c, 0, FLR, WW, 90, (70, 70, 100), seed=87, pw=9); c.R(0, FLR - 2, WW, 3, (140, 140, 220))


def tv_a(t, u):
    c = cv((0, BLK), (1, BLK)); _tv(c, t)
    sign(c, 80, 128, '2006', (255, 230, 120), 16, (30, 20, 60))
    PR.keep(c, PR.mic_stand(), 108, 152)
    place(c, rpg('prod2', int(t * 2) % 2), 70, FW)
    c.amb = (.96, .98, 1.06); c.vig = .65
    return c.render()


def tv_b(t, u):
    c = cv((0, BLK), (1, BLK)); _tv(c, t)
    place(c, bat('prod2', 'hold'), 60, FM)
    PR.keep(c, PR.mic_stand(), 112, 150)
    c.amb = (.96, .98, 1.06); c.vig = .65
    return c.render()


tv = phased(tv_a)
trade = phased(tv_b)


def empty_a(t, u):
    c = cv((0, '#1a1a5a'), (1, '#3a2438')); stars(c, t, 90, 7, 200)
    bg.hill(c, 210, (14, 12, 34))
    c.R(66, 176, 28, 24, (130, 84, 54)); c.R(66, 176, 28, 2, (200, 150, 100)); c.R(70, 200, 3, 26, (110, 72, 46)); c.R(88, 200, 3, 26, (110, 72, 46))
    if u > .35: sign(c, 80, 125, '1966', (255, 230, 120), 32, (30, 20, 60))
    c.amb = (.9, .92, 1.1); c.vig = .75
    return c.render()


empty = phased(empty_a)


def _dawn(c, t, k):
    c.im.paste(Image.fromarray(vgrad([(0, '#1a1a5a'), (.35, '#c0408a'), (.55, '#ff9a50'), (.75, '#ffd080'), (1, '#3a2438')]).astype('uint8')), (0, 0))
    sy = 190 - 30 * k; c.d.ellipse([60, sy - 22, 100, sy + 18], fill=(255, 244, 180))
    for i in range(12):
        a = i / 12 * math.pi * 2 + t * .15
        c.d.polygon([(80, sy), (80 + 340 * math.cos(a), sy + 340 * math.sin(a)), (80 + 340 * math.cos(a + .1), sy + 340 * math.sin(a + .1))], fill=(255, 190, 130))
    bg.skyline(c, 0, 200, cols=((86, 46, 110), (104, 58, 128)), seed=21, lit=.2, t=t, hmin=20, hmax=60)
    bg.planks(c, 0, FLR, WW, 90, (110, 66, 50), seed=73, pw=8); c.R(0, FLR - 2, WW, 3, (200, 140, 100))


def close_a(t, u):
    k = ease(u); c = cv((0, BLK), (1, BLK)); _dawn(c, t, k)
    c.R(20, 180, 120, 8, (176, 112, 74)); c.R(20, 188, 120, 24, (116, 70, 50))
    PR.keep(c, PR.doodle_page(False), 64, 140); c.light(77, 156, 60, 40, (255, 230, 150), .8)
    place(c, rpg('you', int(t * 2) % 2 if u < .2 else 0), 80, 182, sh=False)
    c.R(20, 180, 120, 8, (176, 112, 74)); c.R(20, 180, 120, 2, (236, 176, 124))
    c.amb = (1.0 + .06 * k, .94 + .08 * k, .95); c.vig = .6
    return c.render()


def close_b(t, u):
    k = ease(u); c = cv((0, BLK), (1, BLK)); _dawn(c, t, k)
    place(c, bat('you', 'stand'), 80, FM, sh=True)
    for i in range(18): c.R(30 + (i * 37 + math.sin(t * 2 + i) * 5) % 100, 200 - ((t * .45 + i * .056) % 1) * 110, 2, 2, (255, 236, 170))
    c.amb = (1.0 + .06 * k, .94 + .08 * k, .95); c.vig = .6
    return c.render()


cierre = phased(close_a, close_b, cuts=(.5,))
