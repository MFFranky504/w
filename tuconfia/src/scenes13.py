"""Shorts verticales (160x284): Dwayne Johnson y Tom Brady. Suelo y=206; pies chibi 232; trainer 252. Sin carteles en planos con zoom."""
import math
import numpy as np
from PIL import Image
from lib import *
import bg
import props as PR
from scenes3 import rpg, bat, place
from scenes9 import phased
from scenes12 import cv, sign, FLR, FW, FM, BLK, _dawn

GR = (40, 120, 70)


def _night(c, t, lights=True):
    c.im.paste(Image.fromarray(vgrad([(0, '#0a1030'), (1, '#1c2250')]).astype('uint8')), (0, 0))
    stars(c, t, 60, 5, 90)
    bg.crowd(c, 120, t, seed=3, cols=((20, 18, 44), (30, 24, 58), (16, 14, 36)), phones=True)
    c.R(0, 150, WW, 60, (16, 14, 36))
    if lights:
        for lx in (30, 130):
            c.R(lx - 1, 20, 3, 100, (60, 62, 90)); c.R(lx - 10, 14, 20, 8, (240, 240, 220)); c.light(lx, 40, 70, 90, (255, 250, 220), .5)


def _turf(c, t):
    bg.planks(c, 0, FLR, WW, 90, GR, seed=41, pw=11)
    for x in range(10, WW, 40): c.R(x, FLR + 6, 2, 80, (220, 236, 220))
    c.R(0, FLR - 2, WW, 3, (220, 236, 220))


def _locker(c, t):
    bg.wallpaper(c, 0, 0, WW, FLR, (70, 84, 104), (64, 78, 98), (92, 108, 132))
    for x in range(6, WW, 32): c.R(x, 50, 28, 120, (110, 124, 146)); c.R(x, 50, 28, 2, (160, 172, 192)); c.R(x + 4, 70, 20, 3, (50, 56, 76)); c.R(x + 10, 110, 8, 2, (50, 56, 76))
    bg.planks(c, 0, FLR, WW, 90, (90, 80, 76), seed=51, pw=9); c.R(0, FLR - 2, WW, 3, (40, 36, 40))
    c.R(20, 190, 120, 6, (150, 110, 70)); c.R(24, 196, 4, 14, (110, 80, 50)); c.R(132, 196, 4, 14, (110, 80, 50))


def _home(c, t):
    bg.wallpaper(c, 0, 0, WW, FLR, (96, 76, 70), (88, 68, 62), (126, 100, 90))
    bg.window(c, 52, 50, 56, 70, t=t, night=True, curtain=None, rain=False, lights=True)
    bg.planks(c, 0, FLR, WW, 90, (110, 74, 54), seed=61, pw=9); c.R(0, FLR - 2, WW, 3, (60, 38, 30))
    c.light(80, 40, 120, 100, (255, 200, 120), .25)


def _gym(c, t):
    bg.wallpaper(c, 0, 0, WW, FLR, (70, 66, 82), (64, 60, 76), (96, 92, 112))
    c.R(14, 56, 132, 70, (150, 190, 210)); c.R(14, 56, 132, 3, (230, 240, 250)); c.R(78, 56, 2, 70, (230, 240, 250))
    bg.planks(c, 0, FLR, WW, 90, (80, 64, 60), seed=71, pw=9); c.R(0, FLR - 2, WW, 3, (40, 30, 30))
    for i, x in enumerate((20, 120)): c.R(x, 190, 26, 4, (40, 40, 56)); c.R(x - 4, 184, 6, 16, (40, 40, 56)); c.R(x + 24, 184, 6, 16, (40, 40, 56))


def _arena(c, t):
    c.im.paste(Image.fromarray(vgrad([(0, '#14082a'), (1, '#2a1048')]).astype('uint8')), (0, 0))
    bg.truss(c, 40, ((180, 60, 120), (90, 70, 200), (255, 200, 90)), t)
    bg.crowd(c, 150, t, seed=8)
    c.R(0, 178, WW, 120, (22, 14, 40))
    for lx, col in ((30, (255, 120, 170)), (80, (120, 160, 255)), (130, (255, 220, 120))): c.light(lx, 60, 60, 120, col, .5)


def _ring(c, t, wide=True):
    c.R(10, 196, 140, 10, (200, 60, 70)); c.R(10, 206, 140, 40, (50, 50, 70)); c.R(10, 196, 140, 2, (240, 240, 250))
    for y in (150, 168, 184):
        c.R(14, y, 132, 2, (240, 240, 250)); c.R(14, y + 2, 132, 1, (160, 160, 190))
    for x in (14, 144): c.R(x, 140, 4, 60, (80, 80, 110)); c.R(x, 140, 4, 6, (200, 60, 70))


# ======================================================== JOHNSON
def j_field_a(t, u):
    c = cv((0, BLK), (1, BLK)); _night(c, t); _turf(c, t)
    place(c, rpg('johnson_y', int(t * 3) % 2), 40 + 80 * u, FW); c.amb = (.94, .96, 1.06); c.vig = .65
    return c.render()


def j_field_b(t, u):
    c = cv((0, BLK), (1, BLK)); _night(c, t); _turf(c, t)
    place(c, bat('johnson_y', 'stand'), 80, FM + math.sin(t * 2)); c.amb = (.94, .96, 1.06); c.vig = .65
    return c.render()


j_field = phased(j_field_a, j_field_b, cuts=(.5,))


def j_nobody_a(t, u):
    c = cv((0, BLK), (1, BLK)); _night(c, t, lights=False); _turf(c, t)
    place(c, rpg('johnson_y', 0), 80, FW); c.amb = (.7, .76, .96); c.vig = .85
    return c.render()


def j_nobody_b(t, u):
    c = cv((0, BLK), (1, BLK)); _night(c, t, lights=False); _turf(c, t)
    place(c, bat('johnson_y', 'hold'), 80, FM); c.amb = (.62, .68, .9); c.vig = .9
    return c.render()


j_nobody = phased(j_nobody_a, j_nobody_b, cuts=(.5,))


def j_cut_a(t, u):
    c = cv((0, BLK), (1, BLK)); _locker(c, t)
    place(c, rpg('coachj', 0), 118, FW); place(c, rpg('johnson_y', 0), 42, FW)
    PR.keep(c, PR.contract(), 70, 170); c.amb = (.9, .92, 1.0); c.vig = .75
    return c.render()


def j_cut_b(t, u):
    c = cv((0, BLK), (1, BLK)); _locker(c, t)
    place(c, bat('coachj', 'hold'), 112, FM); PR.keep(c, PR.contract(), 50, 150)
    c.amb = (.86, .88, 1.0); c.vig = .85
    return c.render()


def j_cut_c(t, u):
    c = cv((0, BLK), (1, BLK)); _locker(c, t)
    place(c, bat('johnson_y', 'hold'), 80, FM + 2); c.amb = (.8, .84, .98); c.vig = .9
    return c.render()


j_cut = phased(j_cut_a, j_cut_b, j_cut_c, cuts=(.34, .67))


def j_seven_a(t, u):
    c = cv((0, BLK), (1, BLK)); _home(c, t)
    place(c, rpg('johnson_y', 0), 80, FW)
    for i in range(7): PR.keep(c, PR.money_bill(), 50 + i * 8, 238 + (i % 2) * 2)
    c.amb = (.96, .94, 1.0); c.vig = .7
    return c.render()


def j_seven_b(t, u):
    c = cv((0, BLK), (1, BLK)); _home(c, t)
    place(c, bat('johnson_y', 'hold'), 80, FM)
    for i in range(7): PR.keep(c, PR.money_bill(), 36 + (i % 4) * 22, 176 + (i // 4) * 12 + int(math.sin(t * 2 + i) * 1))
    c.amb = (.9, .88, .98); c.vig = .85
    return c.render()


j_seven = phased(j_seven_a, j_seven_b, cuts=(.5,))


def j_dad_a(t, u):
    c = cv((0, BLK), (1, BLK)); _gym(c, t)
    place(c, rpg('rockyj', 0), 112, FW); place(c, rpg('johnson_y', int(t * 2) % 2 if u < .3 else 0), 48, FW)
    c.amb = (.96, .96, 1.02); c.vig = .7
    return c.render()


def j_dad_b(t, u):
    c = cv((0, BLK), (1, BLK)); _gym(c, t)
    place(c, bat('rockyj', 'stand'), 112, FM); place(c, bat('johnson_y', 'stand'), 50, FM + 1)
    c.amb = (.96, .96, 1.02); c.vig = .75
    return c.render()


j_dad = phased(j_dad_a, j_dad_b, cuts=(.5,))


def j_debut_a(t, u):
    c = cv((0, BLK), (1, BLK)); _arena(c, t); _ring(c, t)
    place(c, rpg('johnson', int(t * 3) % 2), 40 + 80 * ease(u), 196 + 10, sh=False); c.amb = (1.0, .96, 1.06); c.vig = .6
    return c.render()


def j_debut_b(t, u):
    c = cv((0, BLK), (1, BLK)); _arena(c, t); _ring(c, t)
    place(c, bat('johnson', 'stand'), 80, FM + 2 + math.sin(t * 3)); c.amb = (1.0, .96, 1.06); c.vig = .6
    return c.render()


j_debut = phased(j_debut_a, j_debut_b, cuts=(.5,))


def j_star_a(t, u):
    c = cv((0, BLK), (1, BLK)); _arena(c, t)
    c.R(0, 200, WW, 90, (30, 20, 56)); c.R(0, 198, WW, 3, (255, 220, 120))
    place(c, rpg('johnson', 0), 80, FW + 4); c.light(80, 160, 90, 110, (255, 240, 200), .3); c.amb = (1.04, .98, 1.04); c.vig = .55
    return c.render()


def j_star_b(t, u):
    c = cv((0, BLK), (1, BLK)); _arena(c, t)
    c.R(0, 200, WW, 90, (30, 20, 56)); c.R(0, 198, WW, 3, (255, 220, 120))
    place(c, bat('johnson', 'hold'), 80, FM + 2); c.light(80, 170, 100, 130, (255, 240, 200), .3)
    for i in range(16): c.R(20 + (i * 53 + math.sin(t * 3 + i) * 6) % 120, 40 + ((t * 40 + i * 19) % 150), 2, 2, (255, 230, 150))
    c.amb = (1.04, .98, 1.04); c.vig = .55
    return c.render()


j_star = phased(j_star_a, j_star_b, cuts=(.5,))

# ======================================================== BRADY
def _draft(c, t):
    bg.wallpaper(c, 0, 0, WW, FLR, (40, 44, 80), (34, 38, 74), (64, 70, 120))
    c.R(18, 40, 124, 44, (16, 16, 30)); c.R(21, 43, 118, 38, (24, 30, 70))
    for i in range(6): c.R(26 + i * 19, 50, 14, 3, (120, 150, 230)); c.R(26 + i * 19, 60, 14, 3, (80, 100, 170))
    bg.wtext(c, 80, 72, 'DRAFT', (255, 230, 120), 8, center=True)
    bg.planks(c, 0, FLR, WW, 90, (60, 50, 70), seed=81, pw=9); c.R(0, FLR - 2, WW, 3, (30, 26, 40))
    c.R(20, 180, 120, 6, (130, 84, 54)); c.R(24, 186, 4, 24, (100, 66, 44)); c.R(132, 186, 4, 24, (100, 66, 44))


def b_draft_a(t, u):
    c = cv((0, BLK), (1, BLK)); _draft(c, t)
    place(c, rpg('brady_y', 0), 80, 186, sh=False); c.R(20, 180, 120, 6, (130, 84, 54)); c.R(20, 180, 120, 2, (200, 150, 100))
    c.amb = (.94, .94, 1.04); c.vig = .7
    return c.render()


def b_draft_b(t, u):
    c = cv((0, BLK), (1, BLK)); _draft(c, t)
    place(c, bat('brady_y', 'stand'), 80, FM); c.amb = (.86, .88, 1.02); c.vig = .85
    return c.render()


b_draft = phased(b_draft_a, b_draft_b, cuts=(.5,))


def b_passed_a(t, u):
    c = cv((0, BLK), (1, BLK)); _draft(c, t)
    for i, x in enumerate((30, 130)): place(c, rpg('qb2' if i else 'coachj', 0), x, 186, sh=False)
    place(c, rpg('brady_y', 0), 80, 186, sh=False); c.R(20, 180, 120, 6, (130, 84, 54)); c.R(20, 180, 120, 2, (200, 150, 100))
    c.amb = (.8, .82, .98); c.vig = .9
    return c.render()


def b_passed_b(t, u):
    c = cv((0, BLK), (1, BLK)); _draft(c, t)
    place(c, bat('brady_y', 'hold'), 80, FM); c.amb = (.7, .74, .94); c.vig = .95
    return c.render()


b_passed = phased(b_passed_a, b_passed_b, cuts=(.5,))


def _side(c, t):
    _night(c, t); _turf(c, t)
    c.R(14, 170, 132, 6, (170, 130, 90)); c.R(20, 176, 4, 30, (110, 80, 50)); c.R(136, 176, 4, 30, (110, 80, 50))


def b_bench_a(t, u):
    c = cv((0, BLK), (1, BLK)); _side(c, t)
    place(c, rpg('brady_y', 0), 56, 176, sh=False); place(c, rpg('coachj', 0), 118, FW)
    c.R(14, 170, 132, 6, (170, 130, 90)); c.amb = (.9, .92, 1.04); c.vig = .75
    return c.render()


def b_bench_b(t, u):
    c = cv((0, BLK), (1, BLK)); _side(c, t)
    place(c, bat('brady_y', 'hold').crop((0, 0, 84, 92)), 80, 180, sh=False); c.R(14, 170, 132, 6, (170, 130, 90))
    c.amb = (.86, .88, 1.0); c.vig = .85
    return c.render()


b_bench = phased(b_bench_a, b_bench_b, cuts=(.5,))


def b_injury_a(t, u):
    c = cv((0, BLK), (1, BLK)); _night(c, t); _turf(c, t)
    place(c, rpg('qb2', 0), 100, FW); place(c, rpg('coachj', 0), 130, FW)
    place(c, rpg('brady_y', int(t * 3) % 2 if u < .5 else 0), 30 + 20 * ease(u * 2 if u < .5 else 1), FW)
    c.amb = (.94, .96, 1.06); c.vig = .65
    return c.render()


def b_injury_b(t, u):
    c = cv((0, BLK), (1, BLK)); _night(c, t); _turf(c, t)
    place(c, bat('brady_y', 'stand'), 80, FM + math.sin(t * 2)); c.light(80, 160, 100, 120, (255, 250, 220), .35)
    c.amb = (.96, .98, 1.08); c.vig = .6
    return c.render()


b_injury = phased(b_injury_a, b_injury_b, cuts=(.5,))


def _podium(c, t):
    c.im.paste(Image.fromarray(vgrad([(0, '#14082a'), (1, '#3a1860')]).astype('uint8')), (0, 0))
    bg.truss(c, 40, ((220, 60, 80), (80, 120, 255), (255, 210, 90)), t)
    bg.crowd(c, 150, t, seed=12)
    c.R(0, 178, WW, 120, (26, 16, 46)); c.R(0, 196, WW, 4, (255, 220, 120))
    for i in range(30):
        x = (i * 37 + t * 30) % WW; y = (t * 60 + i * 31) % 230
        c.R(int(x), int(y), 2, 3, [(255, 90, 120), (255, 220, 100), (110, 190, 255)][i % 3])


def b_win_a(t, u):
    c = cv((0, BLK), (1, BLK)); _podium(c, t)
    place(c, rpg('brady', 0), 80, FW + 4); PR.keep(c, PR.statuette(30), 88, 168); c.amb = (1.04, 1.0, 1.04); c.vig = .55
    return c.render()


def b_win_b(t, u):
    c = cv((0, BLK), (1, BLK)); _podium(c, t)
    place(c, bat('brady', 'hold'), 80, FM + 2); PR.keep(c, PR.statuette(34), 94, 150)
    c.amb = (1.04, 1.0, 1.04); c.vig = .55
    return c.render()


b_win = phased(b_win_a, b_win_b, cuts=(.5,))


def b_grind_a(t, u):
    c = cv((0, BLK), (1, BLK)); _night(c, t, lights=True); _turf(c, t)
    place(c, rpg('brady_y', int(t * 5) % 2), 20 + 120 * ((t * .6) % 1), FW); c.amb = (.9, .94, 1.06); c.vig = .7
    return c.render()


def b_grind_b(t, u):
    c = cv((0, BLK), (1, BLK)); _night(c, t, lights=True); _turf(c, t)
    place(c, bat('brady', 'stand'), 80, FM + math.sin(t * 5) * 2); c.amb = (.9, .94, 1.06); c.vig = .7
    return c.render()


b_grind = phased(b_grind_a, b_grind_b, cuts=(.5,))


def _you_close(who_a):
    def a(t, u):
        k = ease(u); c = cv((0, BLK), (1, BLK)); _dawn(c, t, k)
        place(c, rpg('you', int(t * 2) % 2 if u < .2 else 0), 80, FW); c.amb = (1.0 + .06 * k, .94 + .08 * k, .95); c.vig = .6
        return c.render()
    def b(t, u):
        k = ease(u); c = cv((0, BLK), (1, BLK)); _dawn(c, t, k)
        place(c, bat('you', 'stand'), 80, FM)
        for i in range(18): c.R(30 + (i * 37 + math.sin(t * 2 + i) * 5) % 100, 200 - ((t * .45 + i * .056) % 1) * 110, 2, 2, (255, 236, 170))
        c.amb = (1.0 + .06 * k, .94 + .08 * k, .95); c.vig = .6
        return c.render()
    return phased(a, b, cuts=(.5,))


close = _you_close(None)

# ======================================================== GAGA
from scenes12 import _office


def _club(c, t):
    c.im.paste(Image.fromarray(vgrad([(0, '#1a0a30'), (1, '#40164a')]).astype('uint8')), (0, 0))
    bg.truss(c, 40, ((220, 60, 140), (110, 80, 230), (255, 210, 90)), t)
    bg.crowd(c, 160, t, seed=5)
    c.R(0, 184, WW, 120, (30, 14, 44)); c.R(0, 184, WW, 3, (255, 150, 200))
    for lx, col in ((40, (255, 120, 180)), (120, (140, 140, 255))): c.light(lx, 70, 60, 120, col, .5)


def g_hook_a(t, u):
    c = cv((0, BLK), (1, BLK)); _club(c, t)
    PR.keep(c, PR.mic_stand(), 94, 176); place(c, rpg('gaga', int(t * 2) % 2), 70, 212); c.amb = (1.0, .96, 1.06); c.vig = .6
    return c.render()


def g_hook_b(t, u):
    c = cv((0, BLK), (1, BLK)); _club(c, t)
    PR.keep(c, PR.mic_stand(), 98, 196); place(c, bat('gaga', 'stand'), 70, FM + 2 + math.sin(t * 3)); c.amb = (1.0, .96, 1.06); c.vig = .6
    return c.render()


g_hook = phased(g_hook_a, g_hook_b, cuts=(.5,))


def g_label_a(t, u):
    c = cv((0, BLK), (1, BLK)); _office(c, t)
    place(c, rpg('execg', 0), 124, 172, sh=False); PR.keep(c, PR.contract(), 84, 140)
    c.R(70, 170, 80, 6, (130, 84, 54)); c.R(70, 170, 80, 2, (200, 150, 100)); place(c, rpg('gaga', 0), 40, FW + 4)
    c.amb = (.94, .94, 1.0); c.vig = .7
    return c.render()


def g_label_b(t, u):
    c = cv((0, BLK), (1, BLK)); _office(c, t)
    place(c, bat('execg', 'stand'), 112, FM); PR.keep(c, PR.contract(), 50, 150)
    c.amb = (.86, .88, 1.0); c.vig = .85
    return c.render()


g_label = phased(g_label_a, g_label_b, cuts=(.5,))


def _diner(c, t):
    bg.wallpaper(c, 0, 0, WW, FLR, (150, 70, 74), (140, 62, 66), (190, 110, 112))
    c.R(0, 120, WW, 6, (230, 230, 240)); c.R(20, 40, 50, 50, (30, 30, 46)); c.R(23, 43, 44, 44, (240, 240, 230))
    a = t * 0.5; c.d.line([(45, 65), (45 + 14 * math.cos(a), 65 + 14 * math.sin(a))], fill=(30, 30, 40))
    bg.planks(c, 0, FLR, WW, 90, (90, 90, 110), seed=95, pw=12); c.R(0, FLR - 2, WW, 3, (40, 40, 56))
    c.R(0, 176, WW, 8, (230, 230, 240)); c.R(0, 184, WW, 30, (120, 50, 56)); c.light(80, 60, 120, 80, (255, 220, 160), .3)


def g_diner_a(t, u):
    c = cv((0, BLK), (1, BLK)); _diner(c, t)
    place(c, rpg('gagaw', int(t * 2) % 2), 60 + 40 * u, 224); c.amb = (.94, .92, 1.0); c.vig = .7
    return c.render()


def g_diner_b(t, u):
    c = cv((0, BLK), (1, BLK)); _diner(c, t)
    place(c, bat('gagaw', 'hold'), 80, FM); c.amb = (.9, .88, .98); c.vig = .8
    return c.render()


g_diner = phased(g_diner_a, g_diner_b, cuts=(.5,))


def _studio_n(c, t):
    bg.wallpaper(c, 0, 0, WW, FLR, (40, 34, 70), (36, 30, 64), (62, 54, 104))
    bg.planks(c, 0, FLR, WW, 90, (70, 50, 54), seed=97, pw=9); c.R(0, FLR - 2, WW, 3, (34, 24, 30))
    bg.window(c, 100, 50, 46, 60, t=t, night=True, curtain=None, rain=False, lights=True)
    c.R(14, 176, 110, 8, (130, 84, 54)); c.R(14, 176, 110, 2, (200, 150, 100)); c.R(18, 184, 4, 28, (100, 66, 44)); c.R(116, 184, 4, 28, (100, 66, 44))
    c.light(60, 150, 70, 60, (255, 210, 130), .5)


def g_write_a(t, u):
    c = cv((0, BLK), (1, BLK)); _studio_n(c, t)
    PR.keep(c, PR.book_open(40, 22, 5), 30, 160); place(c, rpg('gaga', int(t * 2) % 2 if u < .3 else 0), 80, 188, sh=False)
    c.R(14, 176, 110, 8, (130, 84, 54)); c.R(14, 176, 110, 2, (200, 150, 100)); c.amb = (.9, .9, 1.0); c.vig = .75
    return c.render()


def g_write_b(t, u):
    c = cv((0, BLK), (1, BLK)); _studio_n(c, t)
    place(c, bat('gaga', 'hold'), 80, FM)
    for i in range(10): c.R(30 + (i * 41) % 100, 220 - ((t * 30 + i * 21) % 130), 3, 3, (255, 230, 150))
    c.amb = (.9, .9, 1.0); c.vig = .8
    return c.render()


g_write = phased(g_write_a, g_write_b, cuts=(.5,))


def g_sign_a(t, u):
    c = cv((0, BLK), (1, BLK)); _office(c, t)
    place(c, rpg('execg', 0), 124, 172, sh=False); PR.keep(c, PR.contract(), 84, 140)
    c.R(70, 170, 80, 6, (130, 84, 54)); c.R(70, 170, 80, 2, (200, 150, 100)); place(c, rpg('gaga', 0), 40, FW + 4); c.light(80, 170, 80, 60, (255, 230, 150), .5)
    c.amb = (1.0, .98, 1.0); c.vig = .65
    return c.render()


def g_sign_b(t, u):
    c = cv((0, BLK), (1, BLK)); _office(c, t)
    place(c, bat('gaga', 'hold'), 80, FM); PR.keep(c, PR.contract(), 98, 150); c.light(80, 190, 90, 90, (255, 230, 150), .4)
    c.amb = (1.0, .98, 1.0); c.vig = .65
    return c.render()


g_sign = phased(g_sign_a, g_sign_b, cuts=(.5,))


def g_one_a(t, u):
    c = cv((0, BLK), (1, BLK)); _club(c, t)
    place(c, rpg('gaga', int(t * 3) % 2), 80, 216); PR.keep(c, PR.vinyl(12), 112, 190); c.amb = (1.04, .98, 1.06); c.vig = .55
    return c.render()


def g_one_b(t, u):
    c = cv((0, BLK), (1, BLK)); _club(c, t)
    place(c, bat('gaga', 'hold'), 80, FM + 2)
    for i in range(30):
        x = (i * 37 + t * 30) % WW; y = (t * 60 + i * 31) % 230
        c.R(int(x), int(y), 2, 3, [(255, 90, 120), (255, 220, 100), (110, 190, 255)][i % 3])
    c.amb = (1.04, .98, 1.06); c.vig = .55
    return c.render()


g_one = phased(g_one_a, g_one_b, cuts=(.5,))
