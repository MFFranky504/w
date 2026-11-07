"""Historia 6 (Jim Carrey): de la furgoneta al cheque. Toma ancha (chibi) + toma media (trainer) con corte duro."""
import math, random
import numpy as np
from PIL import Image, ImageDraw
from lib import *
import bg
import props as PR
from scenes3 import rpg, bat, place
from scenes6 import top_half


def _sky_night(t):
    c = Canvas(vgrad([(0, '#0a1040'), (.45, '#2a2a8a'), (.7, '#c0508a'), (.85, '#ff9a60'), (1, '#1a1228')]))
    stars(c, t, 60, 7, 90)
    return c


# ============================================================ 1. la furgoneta (hook)
def van_wide(t, u):
    c = _sky_night(t)
    c.d.ellipse([20, 28, 40, 48], fill=(248, 244, 214))
    for k in range(2):                                                    # montañas lejanas
        c.d.polygon([(0, 150 - k * 14), (30, 120 - k * 10), (60, 148 - k * 12), (96, 112 - k * 8), (130, 146 - k * 10), (160, 126 - k * 10), (160, 190), (0, 190)], fill=(40 - k * 10, 30 - k * 8, 88 - k * 18))
    for x in (12, 118, 140): PR.keep(c, PR.palm(), x, 120)
    c.R(0, 190, WW, 110, (60, 56, 86)); c.R(0, 190, WW, 3, (120, 110, 160))
    for x in range(0, WW, 24): c.R(x + int(t * 20) % 24, 244, 12, 2, (240, 220, 110))
    bg.van_side(c, 40, 150, 100, 52, t=t)
    c.light(90, 170, 60, 40, (255, 214, 130), .6)
    place(c, rpg('carrey_y', int(t * 3) % 2), 28, 214)
    PR.keep(c, PR.box_cardboard(), 6, 200)
    c.amb = (.9, .9, 1.08); c.vig = .7
    return c.render()


def van_med(t, u):
    c = _sky_night(t)
    for x in (6, 130): PR.keep(c, PR.palm(), x, 100)
    c.R(0, 206, WW, 94, (60, 56, 86)); c.R(0, 206, WW, 3, (120, 110, 160))
    bg.van_side(c, -20, 84, 220, 128, t=t)
    c.light(120, 140, 70, 60, (255, 214, 130), .7)
    place(c, bat('carrey_y', 'stand'), 62, 220 + 1.2 * math.sin(t * 2))
    c.amb = (.9, .9, 1.08); c.vig = .7
    return c.render()


# ============================================================ 2. la casa en venta
def house_wide(t, u):
    c = Canvas(vgrad([(0, '#2a1a5a'), (.5, '#c0608a'), (.8, '#ffb070'), (1, '#2a2038')]))
    bg.house(c, 20, 118, 90, 86, (190, 150, 110), (150, 60, 60), seed=91, lit=.0, chimneys=True)
    c.R(0, 204, WW, 96, (70, 110, 70)); c.R(0, 204, WW, 3, (120, 170, 110))
    for x in range(4, WW, 14): c.R(x, 214 + (x * 3) % 20, 3, 2, (100, 150, 96))
    c.R(116, 170, 3, 40, (110, 72, 50)); bg.sign2(c, 128, 150, 'SE VENDE', (255, 240, 220), 8, plate=(190, 50, 60))
    for i, (x, f) in enumerate(((60, 'dad'), (78, 'mom'), (96, 'carrey_y'))):
        place(c, rpg(f, int(t * 2 + i) % 2), x, 222)
    PR.keep(c, PR.box_cardboard(), 36, 206); PR.keep(c, PR.box_cardboard(26, 20), 12, 196)
    c.amb = (1.0, .92, .94); c.vig = .65
    return c.render()


def house_med(t, u):
    c = Canvas(vgrad([(0, '#2a1a5a'), (.5, '#c0608a'), (.8, '#ffb070'), (1, '#2a2038')]))
    bg.brick(c, 0, 80, WW, 126, base=(190, 130, 98), mortar=(110, 70, 60), seed=93, bh=8, bw=16)
    bg.window(c, 8, 100, 40, 54, t=t, night=False, rain=False, lights=False, glass=((90, 80, 90), (70, 60, 80)), curtain=(200, 120, 90))
    c.R(0, 206, WW, 94, (70, 110, 70)); c.R(0, 206, WW, 3, (120, 170, 110))
    c.R(94, 124, 4, 96, (110, 72, 50)); bg.sign2(c, 96, 100, 'SE VENDE', (255, 240, 220), 16, plate=(190, 50, 60))
    PR.keep(c, PR.box_cardboard(34, 26), 112, 192)
    place(c, bat('carrey_y', 'hip'), 54, 220 + math.sin(t * 2))
    c.amb = (1.0, .92, .94); c.vig = .65
    return c.render()


# ============================================================ 4. Los Ángeles
def la_wide(t, u):
    c = Canvas(vgrad([(0, '#1a2a7a'), (.4, '#e0508a'), (.65, '#ffb060'), (1, '#2a2038')]))
    c.d.ellipse([64, 90, 100, 126], fill=(255, 236, 170))
    for i, (x0, h) in enumerate(((0, 70), (16, 96), (34, 60), (52, 110), (74, 80), (96, 120), (118, 66), (136, 90))):
        c.R(x0, 200 - h, 18, h, (60, 40, 96)); c.R(x0, 200 - h, 18, 2, (110, 80, 150))
        for r in range(h // 12):
            for k in range(3):
                if (r * 3 + k + i) % 3: c.R(x0 + 2 + k * 5, 200 - h + 6 + r * 12, 3, 5, (255, 220, 120))
    c.R(0, 196, WW, 100, (74, 70, 96)); c.R(0, 196, WW, 3, (150, 140, 180))
    for x in range(0, WW, 32): c.R(x + int(t * 24) % 32, 246, 18, 2, (240, 220, 110))
    for x in (8, 130): PR.keep(c, PR.palm(), x, 130)
    bg.sign2(c, 80, 86, 'LOS ANGELES', (255, 236, 150), 8, plate=(120, 30, 80))
    xw = 30 + 70 * ease(u * 1.1)
    place(c, rpg('carrey_y2', int(t * 4) % 2), xw, 222)
    PR.keep(c, PR.box_cardboard(18, 14), xw + 18, 212)
    c.amb = (1.0, .94, .98); c.vig = .6
    return c.render()


def la_med(t, u):
    c = Canvas(vgrad([(0, '#1a2a7a'), (.4, '#e0508a'), (.65, '#ffb060'), (1, '#2a2038')]))
    off = (t * 30) % 160
    for i in range(-1, 3):
        x = i * 160 - off + 80
        PR.keep(c, PR.palm(), x - 20, 90); PR.keep(c, PR.palm(), x + 54, 96)
    bg.brick(c, 0, 130, WW, 76, base=(200, 120, 100), mortar=(120, 70, 70), seed=95, bh=7, bw=14)
    for x in _tiles(70, off, 3):
        c.R(x + 8, 146, 40, 36, (30, 20, 40)); c.R(x + 10, 148, 36, 32, (255, 214, 130)); c.R(x + 28, 148, 2, 32, (30, 20, 40))
        bg.sign2(c, x + 28, 118, 'CINE', (255, 120, 170), 8, plate=(40, 14, 40), emissive=False)
    c.R(0, 206, WW, 94, (74, 70, 96)); c.R(0, 206, WW, 3, (150, 140, 180))
    place(c, bat('carrey_y2', 'hold'), 70, 220 + (1 if int(t * 4) % 2 else 0))
    c.amb = (1.0, .94, .98); c.vig = .6
    return c.render()


def _tiles(period, off, n):
    return [k * period - (off % period) for k in range(-1, n + 1)]


# ============================================================ 5. pasan los años (casting)
def years_wide(t, u):
    c = Canvas(vgrad([(0, '#2a2a46'), (1, '#1a1a2c')]))
    bg.wallpaper(c, 0, 0, WW, 206, (110, 100, 70), (100, 92, 64), (140, 130, 96))
    bg.planks(c, 0, 206, WW, 90, (96, 74, 56), seed=97, pw=9)
    c.R(60, 90, 40, 76, (70, 46, 36)); c.R(62, 92, 36, 72, (126, 84, 60)); bg.sign2(c, 80, 72, 'CASTING', (255, 230, 120), 8, plate=(40, 20, 20))
    c.d.ellipse([112, 70, 140, 98], fill=(250, 246, 236), outline=(40, 30, 30)); a_ = t * 6
    c.d.line([(126, 84), (126 + 9 * math.cos(a_), 84 + 9 * math.sin(a_))], fill=(200, 40, 50)); c.d.line([(126, 84), (126 + 6 * math.cos(a_ / 12), 84 + 6 * math.sin(a_ / 12))], fill=(30, 30, 40))
    for i, f in enumerate(('kid_a', 'messi', 'dad', 'carrey_y2')):
        xx = 22 + i * 36
        PR.keep(c, PR.chair_wait(), xx - 10, 186)
        place(c, top_half(rpg(f, 0), .78), xx, 200, sh=False)
        PR.keep(c, PR.chair_wait(), xx - 10, 196) if False else None
    for i in range(4):
        ph = (t * .8 + i * .25) % 1; PR.keep(c, PR.calendar_page(), 14 + i * 40 + int(math.sin(t * 3 + i) * 6), int(ph * 120) + 20)
    c.amb = (1.0, .96, .9); c.vig = .7
    return c.render()


def years_med(t, u):
    c = Canvas(vgrad([(0, '#2a2a46'), (1, '#1a1a2c')]))
    bg.wallpaper(c, 0, 0, WW, 206, (110, 100, 70), (100, 92, 64), (140, 130, 96))
    bg.planks(c, 0, 206, WW, 90, (96, 74, 56), seed=97, pw=9)
    yr = 1980 + min(7, int((u - .5) * 2 * 8))
    for i in range(8):
        ph = (t * .9 + i * .125) % 1; PR.keep(c, PR.calendar_page(), 8 + (i * 41) % 130, int(ph * 250) - 20)
    bg.sign2(c, 80, 66, str(yr), (255, 230, 120), 24, plate=(40, 20, 20))
    c.d.ellipse([112, 100, 148, 136], fill=(250, 246, 236), outline=(40, 30, 30)); a_ = t * 9
    c.d.line([(130, 118), (130 + 14 * math.cos(a_), 118 + 14 * math.sin(a_))], fill=(200, 40, 50)); c.d.line([(130, 118), (130 + 9 * math.cos(a_ / 12), 118 + 9 * math.sin(a_ / 12))], fill=(30, 30, 40))
    place(c, bat('carrey_y2', 'hip'), 56, 218 + math.sin(t * 2))
    c.amb = (1.0, .96, .9); c.vig = .7
    return c.render()


# ============================================================ 6. la colina (el cheque)
def _city_lights(c, t, y0):
    rnd = random.Random(5)
    for i in range(260):
        x = rnd.randint(0, WW - 1); y = y0 + rnd.randint(0, 70)
        if rnd.random() < .95 or int(t * 4 + i) % 7: c.R(x, y, 1, 1, rnd.choice(((255, 214, 130), (255, 160, 110), (140, 200, 255), (255, 240, 190))))


def hill_wide(t, u):
    c = _sky_night(t)
    c.d.ellipse([110, 36, 130, 56], fill=(248, 244, 214))
    c.d.polygon([(0, 160), (40, 150), (90, 156), (160, 146), (160, 220), (0, 220)], fill=(22, 18, 46))
    _city_lights(c, t, 150)
    c.d.polygon([(0, 200), (50, 182), (110, 190), (160, 176), (160, 300), (0, 300)], fill=(40, 52, 40))
    c.R(0, 238, WW, 3, (90, 100, 80))
    PR.keep(c, PR.car(), 96, 212)
    c.R(98, 220, 6, 6, (255, 236, 150), c.ed); c.light(120, 224, 30, 14, (255, 236, 150), .5)
    place(c, rpg('carrey_y2', 0), 56, 226 + 1.2 * math.sin(t * 2))
    c.amb = (.9, .92, 1.1); c.vig = .65
    return c.render()


def hill_med(t, u):
    c = _sky_night(t)
    c.d.ellipse([20, 40, 44, 64], fill=(248, 244, 214))
    c.d.polygon([(0, 150), (50, 138), (100, 146), (160, 134), (160, 220), (0, 220)], fill=(22, 18, 46))
    _city_lights(c, t, 138)
    c.d.polygon([(0, 190), (60, 176), (120, 184), (160, 170), (160, 300), (0, 300)], fill=(40, 52, 40))
    place(c, bat('carrey_y2', 'hold'), 52, 224 + math.sin(t * 2))
    # el cheque aparece y se "escribe"
    k = ease((u - .5) / .12)
    if k > 0:
        ck = PR.check_prop(132, 52)
        PR.keep(c, ck, 14, 70 - int((1 - k) * 30) + int(math.sin(t * 3) * 1.5))
        bg.wtext(c, 70, 84 - int((1 - k) * 30), '$10.000.000', (60, 96, 60), 16, outline=None, center=True)
        bg.wtext(c, 70, 104 - int((1 - k) * 30), 'DIEZ MILLONES', (60, 96, 60), 8, outline=None, center=True)
    c.amb = (.9, .92, 1.1); c.vig = .65
    return c.render()


# ============================================================ 7. el estreno
def premiere_wide(t, u):
    c = Canvas(vgrad([(0, '#2a1a5a'), (1, '#12081e')]))
    bg.wallpaper(c, 0, 0, WW, 206, (110, 30, 70), (98, 26, 62), (160, 80, 110))
    bg.sign2(c, 80, 72, 'ESTRENO', (255, 220, 100), 16, plate=(40, 10, 30), emissive=False)
    c.R(0, 206, WW, 94, (150, 24, 44)); c.R(0, 206, WW, 3, (230, 90, 100))
    for x in range(8, WW, 30): c.R(x, 190, 2, 20, (230, 190, 90)); c.d.ellipse([x - 2, 186, x + 4, 192], fill=(240, 210, 110))
    c.R(8, 194, WW - 16, 2, (150, 24, 44))
    for i, x in enumerate((12, 52, 108, 144)):
        place(c, rpg(('kid_a', 'dad', 'mom', 'kid_c')[i], int(t * 3 + i) % 2), x, 190, sh=False)
        PR.keep(c, PR.camera_pro(), x - 6, 154)
        if int(t * 4 + i * 1.3) % 5 == 0: c.light(x, 158, 40, 40, (255, 255, 255), 1.4)
    place(c, rpg('carrey', int(t * 3) % 2), 80, 232)
    c.amb = (1.0, .94, .98); c.vig = .65
    return c.render()


def premiere_med(t, u):
    c = Canvas(vgrad([(0, '#2a1a5a'), (1, '#12081e')]))
    bg.wallpaper(c, 0, 0, WW, 206, (110, 30, 70), (98, 26, 62), (160, 80, 110))
    for i in range(14):
        a = i / 14 * math.pi * 2 + t * .25
        c.d.polygon([(80, 130), (80 + 260 * math.cos(a), 130 + 260 * math.sin(a)), (80 + 260 * math.cos(a + .12), 130 + 260 * math.sin(a + .12))], fill=(150, 56, 100))
    c.R(0, 206, WW, 94, (150, 24, 44)); c.R(0, 206, WW, 3, (230, 90, 100))
    for i, x in enumerate((14, 134)):
        PR.keep(c, PR.camera_pro(), x, 170)
        if int(t * 5 + i * 2) % 4 == 0: c.light(x + 8, 176, 50, 50, (255, 255, 255), 1.6)
    place(c, bat('carrey', 'trophy'), 80, 220 + abs(math.sin(t * 5)) * -2)
    PR.keep(c, PR.check_prop(60, 28), 96, 70 + int(math.sin(t * 6) * 2))
    bg.wtext(c, 126, 80 + int(math.sin(t * 6) * 2), '$10M', (60, 96, 60), 8, outline=None, center=True)
    cols2 = ((255, 90, 120), (90, 220, 255), (255, 230, 90), (140, 255, 140))
    for i in range(44):
        ph = (t * .6 + i * .023) % 1; xx = (i * 53 + math.sin(t * 3 + i) * 6) % 150 + 4; yy = ph * 280
        c.R(xx, yy, 2, 3, cols2[i % 4])
    c.amb = (1.0, .94, .98); c.vig = .65
    return c.render()


# ============================================================ 9. el cheque en blanco al amanecer
def finale_wide(t, u):
    k = ease(u * 1.1)
    c = Canvas(vgrad([(0, '#1a1a5a'), (.35, '#c0408a'), (.55, '#ff9a50'), (.75, '#ffd080'), (1, '#3a2438')]))
    sy = 130 - 30 * k
    c.d.ellipse([62, sy - 22, 98, sy + 18], fill=(255, 244, 180))
    for i in range(12):
        a = i / 12 * math.pi * 2 + t * .15
        c.d.polygon([(80, sy), (80 + 200 * math.cos(a), sy + 200 * math.sin(a)), (80 + 200 * math.cos(a + .1), sy + 200 * math.sin(a + .1))], fill=(255, 206, 140))
    c.d.polygon([(0, 150), (40, 140), (90, 146), (160, 136), (160, 200), (0, 200)], fill=(70, 40, 90))
    _city_lights(c, t, 142)
    c.R(0, 0, 8, 190, (120, 70, 56)); c.R(152, 0, 8, 190, (120, 70, 56))
    for kx in range(8):
        col = (200, 70, 100) if kx % 2 else (170, 50, 84)
        c.R(8 + kx, 0, 1, 190, col); c.R(151 - kx, 0, 1, 190, col)
    bg.planks(c, 0, 186, WW, 120, (110, 66, 50), seed=73, pw=8); c.R(0, 184, WW, 3, (200, 140, 100))
    c.R(14, 160, 132, 8, (176, 112, 74)); c.R(14, 160, 132, 2, (236, 176, 124)); c.R(14, 168, 132, 22, (116, 70, 50))
    PR.keep(c, PR.check_prop(70, 32), 70, 128)
    c.light(105, 142, 70, 40, (255, 230, 150), .9)
    PR.keep(c, PR.lamp_table(), 18, 134)
    place(c, top_half(rpg('you', 0), .8), 36, 162, sh=False)
    c.R(14, 160, 132, 8, (176, 112, 74)); c.R(14, 160, 132, 2, (236, 176, 124))
    for i in range(14):
        ph = (t * .45 + i * .07) % 1; xx = 44 + (i * 37 + math.sin(t * 2 + i) * 5) % 90; yy = 156 - ph * 110
        c.R(xx, yy, 2, 2, (255, 236, 170))
    c.amb = (1.0 + .06 * k, .94 + .08 * k, .95); c.vig = .6
    return c.render()


def finale_med(t, u):
    k = ease(u * 1.1)
    c = Canvas(vgrad([(0, '#1a1a5a'), (.35, '#c0408a'), (.55, '#ff9a50'), (.75, '#ffd080'), (1, '#3a2438')]))
    sy = 118 - 24 * k
    c.d.ellipse([58, sy - 26, 102, sy + 22], fill=(255, 244, 180))
    for i in range(12):
        a = i / 12 * math.pi * 2 + t * .15
        c.d.polygon([(80, sy), (80 + 200 * math.cos(a), sy + 200 * math.sin(a)), (80 + 200 * math.cos(a + .1), sy + 200 * math.sin(a + .1))], fill=(255, 206, 140))
    c.d.polygon([(0, 140), (40, 128), (90, 136), (160, 124), (160, 200), (0, 200)], fill=(70, 40, 90))
    _city_lights(c, t, 130)
    c.R(0, 0, 8, 190, (120, 70, 56)); c.R(152, 0, 8, 190, (120, 70, 56))
    for kx in range(8):
        col = (200, 70, 100) if kx % 2 else (170, 50, 84)
        c.R(8 + kx, 0, 1, 190, col); c.R(151 - kx, 0, 1, 190, col)
    bg.planks(c, 0, 190, WW, 110, (110, 66, 50), seed=73, pw=8); c.R(0, 188, WW, 3, (200, 140, 100))
    place(c, bat('you', 'hold').crop((0, 0, 86, 92)), 40, 176, sh=False)
    c.R(10, 172, 140, 8, (176, 112, 74)); c.R(10, 172, 140, 2, (236, 176, 124)); c.R(10, 180, 140, 26, (116, 70, 50))
    PR.keep(c, PR.check_prop(96, 44), 56, 128)
    nl = int(ease((u - .2) / .5) * 3)
    bg.wtext(c, 66, 148, '$', (60, 96, 60), 16, outline=None)
    for i in range(nl): c.R(76, 150 + i * 4, 40 - i * 6, 1, (60, 96, 60))
    bg.wtext(c, 124, 132, '?', (200, 150, 60), 16, outline=None)
    c.light(104, 150, 80, 50, (255, 230, 150), .9)
    for i in range(18):
        ph = (t * .45 + i * .056) % 1; xx = 60 + (i * 37 + math.sin(t * 2 + i) * 5) % 90; yy = 170 - ph * 120
        c.R(xx, yy, 2, 2, (255, 236, 170))
    c.amb = (1.0 + .06 * k, .94 + .08 * k, .95); c.vig = .6
    return c.render()


CUT = .5
def van(t, u): return van_wide(t, u / CUT) if u < CUT else van_med(t, u)
def house(t, u): return house_wide(t, u / CUT) if u < CUT else house_med(t, u)
def la(t, u): return la_wide(t, u / CUT) if u < CUT else la_med(t, u)
def years(t, u): return years_wide(t, u / CUT) if u < CUT else years_med(t, u)
def hill(t, u): return hill_wide(t, u / CUT) if u < CUT else hill_med(t, u)
def premiere(t, u): return premiere_wide(t, u / CUT) if u < CUT else premiere_med(t, u)
def finale(t, u): return finale_wide(t, u / .45) if u < .45 else finale_med(t, u)
