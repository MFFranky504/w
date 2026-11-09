"""Escenarios de Frida Kahlo (vertical 160x284). Propios de esta historia: hospital, recámara con espejo, estudio, boda."""
import math
import numpy as np
from PIL import Image
from lib import *
import bg
import props as PR
from scenes3 import rpg, bat, place
from scenes9 import phased
from scenes12 import cv, sign, FLR, FW, FM, BLK

def _hosp(c, t):
    c.im.paste(Image.fromarray(vgrad([(0, '#c9dcdc'), (1, '#8fb0b4')]).astype('uint8')), (0, 0))
    c.R(20, 26, 40, 56, (110, 150, 160)); c.R(22, 28, 36, 52, (190, 226, 232)); c.R(40, 28, 2, 52, (110, 150, 160))
    c.R(0, 150, WW, 134, (196, 214, 214)); c.R(0, 150, WW, 3, (240, 250, 250))
    for x in range(10, WW, 30): c.R(x, 166, 1, 118, (176, 196, 196))
    c.R(0, FLR - 2, WW, 3, (120, 140, 144))

def hosp_a(t, u):
    c = cv((0, BLK), (1, BLK)); _hosp(c, t)
    c.R(40, 150, 84, 8, (232, 240, 244)); c.R(40, 158, 84, 3, (150, 170, 176))
    PR.keep(c, PR.hospital_bed(), 36, 170)
    place(c, rpg('gagaw', 0), 88, 176, sh=False)
    c.amb = (.9, .96, 1.0); c.vig = .7
    return c.render()

def hosp_b(t, u):
    c = cv((0, BLK), (1, BLK)); _hosp(c, t)
    PR.keep(c, PR.monitor_ecg(), 118, 168)
    place(c, bat('gaga', 'hold'), 70, FM)
    c.amb = (.9, .96, 1.0); c.vig = .75
    return c.render()

hosp = phased(hosp_a, hosp_b, cuts=(.5,))

def _room(c, t):
    c.im.paste(Image.fromarray(vgrad([(0, '#3a1a2a'), (1, '#6a2a3a')]).astype('uint8')), (0, 0))
    c.R(0, 0, WW, 22, (60, 30, 40)); c.R(18, 6, 124, 10, (200, 220, 240)); c.light(80, 10, 120, 40, (220, 240, 255), .35)
    bg.wallpaper(c, 0, 22, WW, FLR - 22, (96, 40, 60), (88, 36, 56), (130, 60, 80))
    c.R(0, FLR - 6, WW, 90, (96, 60, 40)); c.R(0, FLR - 6, WW, 2, (160, 110, 70))

def room_a(t, u):
    c = cv((0, BLK), (1, BLK)); _room(c, t)
    c.R(48, 120, 64, 18, (200, 60, 90)); c.R(50, 116, 60, 6, (240, 230, 220))
    PR.keep(c, PR.mirror_ceiling() if hasattr(PR, 'mirror_ceiling') else PR.frame_portrait(34, 46), 80, 30)
    place(c, rpg('gaga', 0), 80, 140, sh=False)
    c.amb = (1.0, .92, .96); c.vig = .75
    return c.render()

def room_b(t, u):
    c = cv((0, BLK), (1, BLK)); _room(c, t)
    c.R(60, 72, 40, 1, (240, 200, 120))
    for i in range(3): c.R(64 + i * 10, 80, 6, 30, (200, 60, 90))
    place(c, bat('gaga', 'stand'), 110, FM)
    c.light(110, 120, 60, 80, (255, 220, 160), .35)
    c.amb = (1.0, .92, .96); c.vig = .75
    return c.render()

room = phased(room_a, room_b, cuts=(.5,))

def _studio(c, t):
    c.im.paste(Image.fromarray(vgrad([(0, '#2a4a2a'), (1, '#1a2a1a')]).astype('uint8')), (0, 0))
    bg.wallpaper(c, 0, 0, WW, FLR, (60, 90, 60), (54, 82, 54), (86, 120, 86))
    c.R(96, 30, 56, 80, (240, 232, 214)); c.R(96, 30, 56, 2, (120, 100, 80))
    for i, col in enumerate([(220, 60, 90), (240, 180, 60), (60, 160, 200), (120, 200, 90)]):
        c.R(104 + i * 10, 50, 8, 40, col)
    c.R(0, FLR - 2, WW, 90, (120, 80, 50)); c.R(0, FLR - 2, WW, 3, (200, 150, 100))

def studio_a(t, u):
    c = cv((0, BLK), (1, BLK)); _studio(c, t)
    place(c, rpg('gaga', int(t * 2) % 2 if u < .3 else 0), 60, FW + 6); c.R(70, 100, 4, 90, (120, 80, 50)); c.R(76, 100, 4, 90, (120, 80, 50))
    c.amb = (1.02, .98, .94); c.vig = .7
    return c.render()

def studio_b(t, u):
    c = cv((0, BLK), (1, BLK)); _studio(c, t)
    place(c, bat('gaga', 'hold'), 70, FM + 2)
    for i in range(14): c.R(100 + (i * 7) % 48, 60 + (i * 11) % 60, 2, 2, [(220, 60, 90), (240, 180, 60)][i % 2])
    c.amb = (1.02, .98, .94); c.vig = .7
    return c.render()

studio = phased(studio_a, studio_b, cuts=(.5,))

def _fiesta(c, t):
    c.im.paste(Image.fromarray(vgrad([(0, '#ff9a50'), (1, '#c0408a')]).astype('uint8')), (0, 0))
    for i in range(16):
        x = i * 12; col = [(240, 60, 90), (250, 200, 60), (60, 180, 120), (60, 140, 230)][i % 4]
        c.d.polygon([(x, 0), (x + 10, 0), (x + 5, 14)], fill=col)
    c.R(0, FLR - 6, WW, 90, (150, 90, 60)); c.R(0, FLR - 2, WW, 3, (230, 170, 110))

def wed_a(t, u):
    c = cv((0, BLK), (1, BLK)); _fiesta(c, t)
    place(c, rpg('gagaw', 0), 60, FW + 6); place(c, rpg('extra', 0), 110, FW + 6) if False else None
    place(c, rpg('coachj', 0), 110, FW + 6)
    c.amb = (1.04, .98, .96); c.vig = .6
    return c.render()

def wed_b(t, u):
    c = cv((0, BLK), (1, BLK)); _fiesta(c, t)
    place(c, bat('gaga', 'hold'), 60, FM + 2); place(c, bat('coachj', 'hold'), 112, FM + 2)
    sign(c, 86, 60, 'SE CASA', (255, 230, 120), 16, (60, 20, 40))
    c.amb = (1.04, .98, .96); c.vig = .6
    return c.render()

wedding = phased(wed_a, wed_b, cuts=(.5,))
