"""Historia 7 (Dolly Parton): el NO que valió millones. Toma ancha (chibi) + toma media (trainer) con corte duro."""
import math, random
import numpy as np
from PIL import Image, ImageDraw
from lib import *
import bg
import props as PR
from scenes3 import rpg, bat, place
from scenes6 import top_half


def _stage_bg(c, t, col1=(120, 30, 90), col2=(104, 24, 80)):
    bg.wallpaper(c, 0, 0, WW, 206, col1, col2, (170, 80, 130))
    for x in (6, 138):                                                   # cortinas de escenario
        for k in range(14): c.R(x + k, 0, 1, 200, (170, 30, 60) if k % 2 else (140, 20, 50))
    bg.planks(c, 0, 206, WW, 90, (140, 90, 60), seed=61, pw=9); c.R(0, 204, WW, 3, (230, 180, 110))


# ============================================================ 1. el NO a Elvis (hook)
def duel_wide(t, u):
    c = Canvas(vgrad([(0, '#2a1a3a'), (1, '#12081e')]))
    _stage_bg(c, t)
    for i in range(10):
        a = -math.pi / 2 + (i - 4.5) * .2
        c.d.polygon([(80, 0), (80 + 220 * math.cos(a - .05), 220 * math.sin(a - .05) + 0), (80 + 220 * math.cos(a + .05), 220 * math.sin(a + .05))], fill=(150, 70, 120)) if False else None
    c.light(80, 120, 110, 120, (255, 220, 160), .7)
    place(c, rpg('dolly', int(t * 3) % 2), 40, 214)
    place(c, rpg('elvis', 0), 120, 214, flip=True)
    if u > .35: bg.wtext(c, 80, 96 - int(2 * math.sin(t * 8)), 'NO', (255, 70, 90), 24, center=True)
    c.amb = (1.0, .94, .98); c.vig = .65
    return c.render()


def duel_med(t, u):
    c = Canvas(vgrad([(0, '#2a1a3a'), (1, '#12081e')]))
    _stage_bg(c, t)
    for i in range(14):
        a = i / 14 * math.pi * 2 + t * .25
        c.d.polygon([(80, 140), (80 + 260 * math.cos(a), 140 + 260 * math.sin(a)), (80 + 260 * math.cos(a + .12), 140 + 260 * math.sin(a + .12))], fill=(150, 56, 100))
    place(c, bat('elvis', 'stand'), 128, 216)
    place(c, bat('dolly', 'toss'), 56, 220 + abs(math.sin(t * 6)) * -2)
    if int(t * 5) % 2 == 0 or u > .8: bg.wtext(c, 76, 66, 'NO', (255, 70, 90), 24, outline=(250, 240, 230), center=True)
    c.light(80, 130, 90, 100, (255, 220, 160), .6)
    c.amb = (1.0, .94, .98); c.vig = .65
    return c.render()


# ============================================================ 2. cabaña pobre -> Nashville
def cabin_wide(t, u):
    c = Canvas(vgrad([(0, '#1a2a6a'), (.4, '#e08a6a'), (.65, '#ffc880'), (1, '#2a3a2a')]))
    for k in range(3):
        c.d.polygon([(0, 150 - k * 12), (40, 110 - k * 8), (80, 146 - k * 10), (120, 104 - k * 8), (160, 140 - k * 10), (160, 200), (0, 200)], fill=(56 - k * 10, 70 - k * 8, 100 - k * 14))
    c.R(0, 196, WW, 100, (70, 110, 60)); c.R(0, 196, WW, 3, (130, 180, 100))
    bg.planks(c, 30, 140, 100, 56, (140, 92, 58), seed=65, horizontal=False, pw=6)
    c.d.polygon([(22, 142), (138, 142), (110, 108), (50, 108)], fill=(100, 60, 44)); c.R(22, 140, 116, 3, (160, 110, 80))
    c.R(72, 160, 18, 36, (70, 44, 34)); c.R(98, 154, 20, 18, (255, 214, 130)); c.R(98, 154, 20, 1, (70, 44, 34)); c.R(107, 154, 1, 18, (70, 44, 34))
    c.light(108, 164, 40, 30, (255, 214, 130), .6)
    for i, f in enumerate(('kid_a', 'kid_b', 'kid_c', 'dolly_y')):
        place(c, rpg(f, int(t * 2 + i) % 2), 20 + i * 36, 224, sh=False)
    c.amb = (1.0, .96, .94); c.vig = .6
    return c.render()


def bus_med(t, u):
    c = Canvas(vgrad([(0, '#1a2a6a'), (.5, '#e0608a'), (.8, '#ffc880'), (1, '#2a2038')]))
    off = (t * 40) % 160
    for i in range(-1, 3):
        PR.keep(c, PR.palm(), i * 80 - off % 80 + 10, 110)
    c.R(0, 206, WW, 94, (74, 70, 96)); c.R(0, 206, WW, 3, (150, 140, 180))
    bg.sign2(c, 80, 76, 'NASHVILLE', (255, 230, 120), 16, plate=(40, 20, 60))
    PR.keep(c, PR.bus(), 30 + int(math.sin(t * 7)), 168)
    place(c, bat('dolly_y', 'stand'), 52, 220)
    PR.keep(c, PR.box_cardboard(24, 18), 90, 202)
    c.amb = (1.0, .94, .98); c.vig = .6
    return c.render()


# ============================================================ 3. la canción
def song_wide(t, u):
    c = Canvas(vgrad([(0, '#2a1a3a'), (1, '#12081e')]))
    bg.wallpaper(c, 0, 0, WW, 206, (60, 56, 110), (52, 48, 102), (90, 86, 150))
    bg.shelf(c, 6, 60, 40, 90, seed=71, rows=3)
    bg.planks(c, 0, 206, WW, 90, (110, 80, 60), seed=73, pw=9); c.R(0, 204, WW, 3, (60, 40, 30))
    PR.keep(c, PR.mic_stand(), 110, 150)
    place(c, rpg('dolly', int(t * 2) % 2), 76, 214)
    PR.keep(c, PR.guitar(), 100, 168)
    for i in range(6):
        ph = (t * .5 + i * .17) % 1; xx = 20 + (i * 29) % 120; yy = 180 - ph * 110
        c.d.ellipse([xx, yy, xx + 4, yy + 3], fill=(255, 230, 120)); c.R(xx + 3, yy - 6, 1, 7, (255, 230, 120))
    c.light(80, 140, 80, 80, (255, 214, 140), .5)
    c.amb = (1.0, .96, .98); c.vig = .65
    return c.render()


def song_med(t, u):
    c = Canvas(vgrad([(0, '#2a1a3a'), (1, '#12081e')]))
    bg.wallpaper(c, 0, 0, WW, 206, (60, 56, 110), (52, 48, 102), (90, 86, 150))
    bg.planks(c, 0, 206, WW, 90, (110, 80, 60), seed=73, pw=9); c.R(0, 204, WW, 3, (60, 40, 30))
    PR.keep(c, PR.mic_stand(), 12, 140)
    place(c, bat('dolly', 'hold'), 80, 220 + math.sin(t * 3))
    for i in range(10):
        ph = (t * .5 + i * .1) % 1; xx = 10 + (i * 31) % 140; yy = 190 - ph * 120
        c.d.ellipse([xx, yy, xx + 5, yy + 4], fill=(255, 230, 120)); c.R(xx + 4, yy - 8, 1, 9, (255, 230, 120)); c.R(xx + 4, yy - 8, 4, 2, (255, 230, 120))
    c.light(80, 140, 80, 80, (255, 214, 140), .5)
    c.amb = (1.0, .96, .98); c.vig = .65
    return c.render()


# ============================================================ 4. el manager pide la mitad
def office_wide(t, u):
    c = Canvas(vgrad([(0, '#2a2a46'), (1, '#1a1a2c')]))
    bg.wallpaper(c, 0, 0, WW, 206, (70, 90, 70), (62, 82, 62), (96, 120, 96))
    bg.planks(c, 0, 206, WW, 90, (96, 64, 48), seed=79, pw=9); c.R(0, 204, WW, 3, (50, 30, 24))
    c.R(20, 170, 120, 6, (130, 84, 54)); c.R(26, 176, 108, 30, (96, 60, 40))
    place(c, rpg('prod1', 0, 'tux'), 116, 168)
    PR.keep(c, PR.contract(), 58, 150)
    place(c, rpg('dolly', 0), 38, 214)
    c.R(20, 170, 120, 6, (130, 84, 54)); c.R(20, 170, 120, 2, (200, 150, 100))
    bg.wtext(c, 76, 100, 'MITAD', (255, 90, 90), 24, center=True)
    c.light(80, 140, 80, 70, (255, 214, 140), .4)
    c.amb = (.96, .96, .94); c.vig = .7
    return c.render()


def office_med(t, u):
    c = Canvas(vgrad([(0, '#2a2a46'), (1, '#1a1a2c')]))
    bg.wallpaper(c, 0, 0, WW, 206, (70, 90, 70), (62, 82, 62), (96, 120, 96))
    bg.planks(c, 0, 206, WW, 90, (96, 64, 48), seed=79, pw=9); c.R(0, 204, WW, 3, (50, 30, 24))
    place(c, bat('prod1', 'hold', 'tux'), 90, 218)
    PR.keep(c, PR.contract(), 30, 120 + int(math.sin(t * 4) * 2))
    bg.wtext(c, 80, 72, 'MITAD', (255, 90, 90), 24, outline=(250, 240, 230), center=True)
    c.light(80, 140, 80, 70, (255, 214, 140), .4)
    c.amb = (.96, .96, .94); c.vig = .7
    return c.render()


# ============================================================ 6. Whitney y los millones
def whitney_wide(t, u):
    c = Canvas(vgrad([(0, '#1a1a5a'), (1, '#12081e')]))
    _stage_bg(c, t, (60, 40, 140), (52, 34, 128))
    c.light(80, 100, 100, 120, (200, 200, 255), .8)
    for i in range(5): place(c, rpg(('kid_a', 'messi', 'mom', 'dad', 'kid_c')[i], int(t * 3 + i) % 2), 12 + i * 34, 252, sh=False)
    place(c, rpg('whitney', int(t * 2) % 2), 80, 214)
    PR.keep(c, PR.mic_stand(), 104, 154)
    for i in range(14):
        ph = (t * .6 + i * .07) % 1; PR.keep(c, PR.money_bill(), (i * 37) % 140 + 4, int(ph * 260) - 10)
    c.amb = (1.0, .96, 1.02); c.vig = .6
    return c.render()


def whitney_med(t, u):
    c = Canvas(vgrad([(0, '#1a1a5a'), (1, '#12081e')]))
    _stage_bg(c, t, (60, 40, 140), (52, 34, 128))
    for i in range(14):
        a = i / 14 * math.pi * 2 + t * .25
        c.d.polygon([(80, 130), (80 + 260 * math.cos(a), 130 + 260 * math.sin(a)), (80 + 260 * math.cos(a + .12), 130 + 260 * math.sin(a + .12))], fill=(84, 60, 170))
    for i in range(5):
        PR.keep(c, PR.vinyl(14), 6 + i * 30, 150 + (i % 2) * 14 + int(math.sin(t * 4 + i) * 2))
    place(c, bat('whitney', 'stand'), 80, 220 + math.sin(t * 3))
    for i in range(24):
        ph = (t * .7 + i * .04) % 1; PR.keep(c, PR.money_bill(), (i * 37) % 140 + 4, int(ph * 260) - 10)
    bg.sign2(c, 80, 66, 'MILLONES', (255, 230, 120), 16, plate=(40, 20, 80))
    c.amb = (1.0, .96, 1.02); c.vig = .6
    return c.render()


# ============================================================ 8. "NO" que vale (contrato roto)
def torn_wide(t, u):
    c = Canvas(vgrad([(0, '#1a2a6a'), (.5, '#e0608a'), (1, '#2a2038')]))
    bg.wallpaper(c, 0, 0, WW, 206, (150, 70, 110), (138, 62, 100), (190, 110, 150))
    bg.planks(c, 0, 206, WW, 90, (140, 90, 60), seed=83, pw=9)
    place(c, rpg('dolly', int(t * 3) % 2), 80, 214)
    for i in range(10):
        ph = (t * .6 + i * .1) % 1; PR.keep(c, PR.contract(), (i * 41) % 130 + 6, int(ph * 240) - 20) if False else None
    for i in range(10):
        ph = (t * .6 + i * .1) % 1; xx = (i * 41) % 130 + 6; yy = int(ph * 240) - 20
        c.R(xx, yy, 8, 10, (252, 248, 236)); c.R(xx, yy, 8, 1, (210, 206, 190))
    c.amb = (1.0, .94, .98); c.vig = .6
    return c.render()


def torn_med(t, u):
    c = Canvas(vgrad([(0, '#1a2a6a'), (.5, '#e0608a'), (1, '#2a2038')]))
    bg.wallpaper(c, 0, 0, WW, 206, (150, 70, 110), (138, 62, 100), (190, 110, 150))
    bg.planks(c, 0, 206, WW, 90, (140, 90, 60), seed=83, pw=9)
    place(c, bat('dolly', 'toss'), 80, 220 + abs(math.sin(t * 5)) * -2)
    for i in range(18):
        ph = (t * .8 + i * .055) % 1; xx = (i * 37 + math.sin(t * 3 + i) * 8) % 140 + 6; yy = int(ph * 260) - 10
        c.R(xx, yy, 9, 11, (252, 248, 236)); c.R(xx, yy, 9, 1, (210, 206, 190)); c.R(xx + 2, yy + 4, 5, 1, (150, 146, 170))
    bg.sign2(c, 80, 66, 'NO', (255, 90, 110), 24, plate=(40, 14, 40))
    c.amb = (1.0, .94, .98); c.vig = .6
    return c.render()


# ============================================================ 9. tú: ¿sí o no?
def finale_wide(t, u):
    k = ease(u * 1.1)
    c = Canvas(vgrad([(0, '#1a1a5a'), (.35, '#c0408a'), (.55, '#ff9a50'), (.75, '#ffd080'), (1, '#3a2438')]))
    sy = 130 - 30 * k
    c.d.ellipse([62, sy - 22, 98, sy + 18], fill=(255, 244, 180))
    for i in range(12):
        a = i / 12 * math.pi * 2 + t * .15
        c.d.polygon([(80, sy), (80 + 200 * math.cos(a), sy + 200 * math.sin(a)), (80 + 200 * math.cos(a + .1), sy + 200 * math.sin(a + .1))], fill=(255, 206, 140))
    c.R(0, 0, 8, 190, (120, 70, 56)); c.R(152, 0, 8, 190, (120, 70, 56))
    for kx in range(8):
        col = (200, 70, 100) if kx % 2 else (170, 50, 84)
        c.R(8 + kx, 0, 1, 190, col); c.R(151 - kx, 0, 1, 190, col)
    bg.planks(c, 0, 186, WW, 120, (110, 66, 50), seed=73, pw=8); c.R(0, 184, WW, 3, (200, 140, 100))
    c.R(14, 160, 132, 8, (176, 112, 74)); c.R(14, 160, 132, 2, (236, 176, 124)); c.R(14, 168, 132, 22, (116, 70, 50))
    PR.keep(c, PR.contract(), 70, 118); PR.keep(c, PR.contract(), 96, 120)
    bg.wtext(c, 87, 128, 'SÍ', (60, 150, 80), 16, outline=None, center=True); bg.wtext(c, 113, 130, 'NO', (200, 60, 70), 16, outline=None, center=True)
    c.light(100, 140, 70, 40, (255, 230, 150), .8)
    place(c, top_half(rpg('you', 0), .8), 36, 162, sh=False)
    c.R(14, 160, 132, 8, (176, 112, 74)); c.R(14, 160, 132, 2, (236, 176, 124))
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
    c.R(0, 0, 8, 190, (120, 70, 56)); c.R(152, 0, 8, 190, (120, 70, 56))
    for kx in range(8):
        col = (200, 70, 100) if kx % 2 else (170, 50, 84)
        c.R(8 + kx, 0, 1, 190, col); c.R(151 - kx, 0, 1, 190, col)
    bg.planks(c, 0, 190, WW, 110, (110, 66, 50), seed=73, pw=8); c.R(0, 188, WW, 3, (200, 140, 100))
    place(c, bat('you', 'hold').crop((0, 0, 86, 92)), 40, 176, sh=False)
    c.R(10, 172, 140, 8, (176, 112, 74)); c.R(10, 172, 140, 2, (236, 176, 124)); c.R(10, 180, 140, 26, (116, 70, 50))
    PR.keep(c, PR.contract(), 70, 124); PR.keep(c, PR.contract(), 108, 126)
    bg.wtext(c, 87, 136, 'SÍ', (60, 150, 80), 16, outline=None, center=True); bg.wtext(c, 125, 138, 'NO', (200, 60, 70), 16, outline=None, center=True)
    c.light(104, 146, 80, 50, (255, 230, 150), .9)
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
