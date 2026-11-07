"""Historia 8 (Stephen Hawking) en HORIZONTAL (mundo 320x180, x6 = 1920x1080). Requiere TC_LAND=1 antes de importar lib.
Planos: ancho (chibi), medio (trainer) y cercano (corte duro + zoom). Suelo en y=136; pies chibi y=148; pies trainer y=170."""
import math, random
import numpy as np
from PIL import Image, ImageDraw
from lib import *
import bg
import props as PR
from scenes3 import rpg, bat, place
from scenes9 import seated, phased, GOLD

assert WW == 320 and WH == 180, 'ejecutar con TC_LAND=1'
FL, FW, FM = 136, 148, 170          # línea de suelo, pies chibi (ancho), pies trainer (medio)


def cv(*stops): return Canvas(vgrad(list(stops)))


def sign(c, x, y, txt, col, size=16, plate=(16, 12, 30)): return bg.sign2(c, x, y, txt, col, size, plate=plate)


# ============================================================ cielo estrellado (gancho y final)
def _env_sky(c, t):
    stars(c, t, 300, 3, 130); bg.nebula_l(c, t, 2); bg.shoot_l(c, t, 0, 3.0); bg.shoot_l(c, t, 1, 4.1)
    c.d.ellipse([262, 18, 282, 38], fill=(248, 244, 214)); c.d.ellipse([268, 16, 288, 36], fill=(10, 16, 70))
    bg.hill_l(c, 138, (18, 16, 44), t)
    PR.keep(c, PR.telescope(), 108, 112)


def _sky(): return cv((0, '#060a2e'), (.5, '#1a1a70'), (1, '#2a1a4a'))


def sky_a(t, u):
    c = _sky(); _env_sky(c, t); seated(c, 'hawking', 170, 150, 'rpg', t=t)
    c.light(170, 110, 70, 40, (140, 170, 255), .35); c.amb = (.92, .94, 1.1); c.vig = .65
    return c.render()


def sky_b(t, u):
    c = _sky(); _env_sky(c, t); seated(c, 'hawking', 190, 172, 'bat', t=t)
    c.light(190, 110, 80, 50, (140, 170, 255), .35); c.amb = (.92, .94, 1.1); c.vig = .65
    return c.render()


sky = phased(sky_a, sky_b, cuts=(.5,))


# ============================================================ 2. Oxford, 1942
def _env_oxford(c, t):
    c.im.paste(Image.fromarray(vgrad([(0, '#3a2a7a'), (.4, '#e0708a'), (.62, '#ffc880'), (1, '#4a3a30')]).astype('uint8')), (0, 0))
    stars(c, t, 60, 4, 40)
    bg.stone_college(c, 0, 36, WW, 100, seed=7, lit=.5, t=t)
    for x in (16, 304): bg.tree(c, x, FL, 60, 'round', (214, 120, 40))
    bg.cobble(c, 0, FL, WW, 44, base=(150, 130, 112), seed=9); c.R(0, FL - 2, WW, 3, (190, 170, 140))


def oxford_a(t, u):
    c = cv((0, '#000000'), (1, '#000000')); _env_oxford(c, t)
    PR.keep(c, PR.telescope(), 104, 112)
    place(c, rpg('hawking_k', int(t * 2) % 2), 150, FW + 6); place(c, rpg('kid_a', 0), 190, FW + 6); place(c, rpg('kid_b', 0), 224, FW + 6)
    sign(c, 160, 8, '1942', (255, 230, 120), 24, (50, 24, 60))
    c.amb = (1.0, .94, .94); c.vig = .65
    return c.render()


def oxford_b(t, u):
    c = cv((0, '#000000'), (1, '#000000')); _env_oxford(c, t)
    PR.keep(c, PR.telescope(), 206, 122)
    place(c, bat('hawking_k', 'stand'), 140, FM)
    sign(c, 160, 8, 'OXFORD', (255, 230, 120), 24, (50, 24, 60))
    c.amb = (1.0, .94, .94); c.vig = .65
    return c.render()


def oxford_c(t, u):
    c = cv((0, '#000000'), (1, '#000000')); _env_oxford(c, t)
    place(c, bat('kid_b', 'stand'), 84, FM); place(c, bat('kid_a', 'stand'), 236, FM); place(c, bat('hawking_k', 'stand'), 160, FM + 2)
    if u > .25: bg.bubble2(c, 232, 44, 'EINSTEIN', 8)
    c.amb = (1.0, .94, .94); c.vig = .65
    return c.render()


oxford = phased(oxford_a, oxford_b, oxford_c)


# ============================================================ 3. Cambridge
def _env_cam(c, t):
    c.im.paste(Image.fromarray(vgrad([(0, '#1a2a7a'), (.5, '#e0708a'), (.7, '#ffd090'), (1, '#2a4a2a')]).astype('uint8')), (0, 0))
    bg.stone_college(c, 0, 30, 130, 106, seed=11, lit=.4, t=t); bg.stone_college(c, 190, 30, 130, 106, seed=12, lit=.4, t=t)
    c.R(130, 60, 60, 76, (50, 36, 40)); c.d.pieslice([130, 36, 190, 84], 180, 360, fill=(50, 36, 40)); c.R(136, 66, 48, 70, (110, 78, 60)); c.R(159, 66, 2, 70, (50, 36, 40))
    c.R(0, FL, WW, 44, (74, 130, 70)); c.R(0, FL, WW, 3, (130, 190, 110))
    c.R(138, FL, 44, 44, (190, 170, 130))
    for x in range(2, WW, 7): c.R(x, FL + 8 + (x * 5) % 30, 1, 3, (110, 170, 90))
    for x in (24, 296): bg.tree(c, x, FL + 8, 54, 'round', (60, 140, 70))


def cam_a(t, u):
    c = cv((0, '#000000'), (1, '#000000')); _env_cam(c, t)
    sign(c, 160, 8, 'CAMBRIDGE', (255, 230, 120), 16, (50, 24, 60))
    place(c, rpg('hawking_y', int(t * 4) % 2), 60 + 200 * u, FW + 6)
    for i, f in enumerate(('prod1', 'kid_c')): place(c, rpg(f, int(t * 3 + i) % 2), 280 - 200 * u + i * 30, FW + 18, sh=False)
    c.amb = (1.0, .96, .96); c.vig = .65
    return c.render()


def cam_b(t, u):
    c = cv((0, '#000000'), (1, '#000000')); _env_cam(c, t)
    sign(c, 160, 8, 'CAMBRIDGE', (255, 230, 120), 16, (50, 24, 60))
    place(c, bat('hawking_y', 'hold'), 160, FM + math.sin(t * 4))
    c.amb = (1.0, .96, .96); c.vig = .65
    return c.render()


cam = phased(cam_a, cam_b, cuts=(.5,))


# ============================================================ 4. 21 años: el cuerpo falla
def _env_fall(c, t):
    c.im.paste(Image.fromarray(vgrad([(0, '#2a1a5a'), (.5, '#c0508a'), (1, '#2a1a30')]).astype('uint8')), (0, 0))
    bg.stone_college(c, 0, 20, WW, 116, seed=13, lit=.3, t=t)
    c.R(0, FL, WW, 44, (110, 100, 96))
    for k in range(7): c.R(40 + k * 14, FL - k * 8 + 4, 240 - k * 28, 8, (150, 140, 130)); c.R(40 + k * 14, FL - k * 8 + 4, 240 - k * 28, 1, (200, 190, 176))


def fall_a(t, u):
    c = cv((0, '#000000'), (1, '#000000')); _env_fall(c, t)
    x = 70 + 150 * u; y = FW + 8 - int(u * 28)
    place(c, rpg('hawking_y', int(t * 4) % 2 if u < .7 else 0), x + (math.sin(t * 30) * 2 if u > .6 else 0), y)
    if u > .6:
        bg.wtext(c, x + 8, y - 90, '!', (255, 80, 80), 24)
        for i in range(5):
            ph = (u - .6) * 3 + i * .1; PR.keep(c, PR.stamp_paper(), x + 14 + i * 9, y - 60 - int(ph * 20) + i * 4)
    c.amb = (1.0, .94, .94); c.vig = .65
    return c.render()


def fall_b(t, u):
    c = cv((0, '#000000'), (1, '#000000')); _env_fall(c, t)
    PR.keep(c, PR.book_stack(3), 210 + int(u * 8), 30 + int(u * 110))
    place(c, bat('hawking_y', 'hip'), 150 + math.sin(t * 24) * 1.5, FM)
    sign(c, 160, 8, '21 AÑOS', (255, 90, 90), 24, (40, 10, 24))
    c.light(160, 90, 150, 90, (255, 60, 60), .3 + .3 * (math.sin(t * 8) > 0)); c.amb = (1.0, .92, .94); c.vig = .7
    return c.render()


def fall_c(t, u):
    c = cv((0, '#000000'), (1, '#000000')); _env_fall(c, t)
    place(c, bat('hawking_y', 'stand'), 160 + math.sin(t * 28) * 1.2, FM + 2)
    for i in range(4): bg.wtext(c, 118 + i * 24, 36 + int(math.sin(t * 6 + i) * 4), '?', (255, 220, 90), 16)
    c.amb = (1.0, .92, .94); c.vig = .7
    return c.render()


fall = phased(fall_a, fall_b, fall_c)


# ============================================================ 5. diagnóstico: dos años
def _env_doc(c, t):
    c.R(0, 0, WW, FL, (150, 190, 186)); c.R(0, 100, WW, 36, (120, 150, 150)); c.R(0, 100, WW, 3, (220, 240, 236))
    c.R(232, 24, 62, 66, (60, 50, 44)); c.R(234, 26, 58, 62, (200, 226, 240))
    for k in range(6): c.R(234, 28 + k * 10, 58, 5, (170, 200, 220))
    c.R(26, 30, 44, 36, (60, 50, 44)); c.R(28, 32, 40, 32, (250, 246, 232)); [c.R(34 + k * 10, 38, 6, 18, (200, 90, 90)) for k in range(3)]
    ang = t * 1.0; c.d.ellipse([176, 36, 208, 68], fill=(250, 248, 240), outline=(40, 30, 30)); c.d.line([(192, 52), (192 + 12 * math.cos(ang), 52 + 12 * math.sin(ang))], fill=(200, 40, 50))
    bg.planks(c, 0, FL, WW, 44, (126, 90, 64), seed=21, pw=9); c.R(0, FL - 2, WW, 3, (60, 40, 32))


def doc_a(t, u):
    c = cv((0, '#000000'), (1, '#000000')); _env_doc(c, t)
    c.R(190, 118, 100, 6, (130, 84, 54)); c.R(190, 118, 100, 2, (200, 150, 100)); c.R(196, 124, 88, 18, (96, 60, 40))
    place(c, rpg('doctor', 0), 240, 120, sh=False); c.R(190, 118, 100, 6, (130, 84, 54)); c.R(190, 118, 100, 2, (200, 150, 100))
    place(c, rpg('hawking_y', 0), 110, FW + 8)
    c.amb = (.98, 1.0, 1.0); c.vig = .65
    return c.render()


def doc_b(t, u):
    c = cv((0, '#000000'), (1, '#000000')); _env_doc(c, t)
    place(c, bat('doctor', 'hold'), 230, FM); PR.keep(c, PR.calendar_page(), 70, 108)
    sign(c, 100, 8, '2 AÑOS', (255, 90, 90), 24, (40, 10, 24))
    c.amb = (.98, 1.0, 1.0); c.vig = .65
    return c.render()


def doc_c(t, u):
    c = cv((0, '#000000'), (1, '#000000')); _env_doc(c, t)
    place(c, bat('hawking_y', 'stand'), 160, FM + 2 + math.sin(t * 2))
    c.light(160, 90, 130, 80, (200, 210, 255), .25); c.amb = (.84, .88, 1.0); c.vig = .85
    return c.render()


doctor = phased(doc_a, doc_b, doc_c)


# ============================================================ 7. Jane y la boda (1965)
def _env_love(c, t):
    c.im.paste(Image.fromarray(vgrad([(0, '#5a3a9a'), (.45, '#f09aa6'), (.7, '#ffe0a0'), (1, '#3a6a3a')]).astype('uint8')), (0, 0))
    for i in range(3): c.R((t * (3 + i) + i * 90) % 360 - 30, 16 + i * 12, 40, 5, (255, 220, 230))
    bg.stone_college(c, 0, 44, 96, 92, seed=15, lit=.2, t=t); bg.stone_college(c, 224, 44, 96, 92, seed=16, lit=.2, t=t)
    c.R(0, FL, WW, 44, (92, 160, 84)); c.R(0, FL, WW, 3, (150, 210, 120))
    for x in range(2, WW, 6): c.R(x, FL + 6 + (x * 7) % 34, 1, 3, (120, 190, 100))
    c.d.arc([112, 20, 208, 160], 180, 360, fill=(120, 80, 50), width=3)
    for k in range(22):
        a = math.pi + k * math.pi / 21; px = 160 + math.cos(a) * 46; py = 108 + math.sin(a) * 86
        c.d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=((255, 150, 190), (255, 220, 120), (255, 255, 255))[k % 3])
    for i in range(20):
        ph = (t * .2 + i * .05) % 1; xx = (i * 37 + math.sin(t * 2 + i) * 8) % 310 + 4; yy = ph * 170 + 6
        c.R(xx, yy, 2, 2, (255, 200, 220))


def love_a(t, u):
    c = cv((0, '#000000'), (1, '#000000')); _env_love(c, t)
    place(c, rpg('jane', 0), 146, FW + 8); place(c, rpg('hawking_y', 0), 176, FW + 8)
    for i in range(4): PR.keep(c, PR.heart(), 150 + i * 8, 90 - int(((t * .6 + i * .25) % 1) * 50))
    c.amb = (1.04, .98, .98); c.vig = .55
    return c.render()


def love_b(t, u):
    c = cv((0, '#000000'), (1, '#000000')); _env_love(c, t)
    place(c, bat('jane', 'stand'), 128, FM); place(c, bat('hawking_y', 'stand'), 194, FM)
    sign(c, 160, 8, '1965', (255, 230, 120), 24, (70, 24, 60))
    for i in range(6): PR.keep(c, PR.heart(11), 154 + (i % 3) * 8, 70 - int(((t * .6 + i * .17) % 1) * 50))
    c.amb = (1.04, .98, .98); c.vig = .55
    return c.render()


love = phased(love_a, love_b, cuts=(.5,))


# ============================================================ 8. doctorado, familia y humor
def _env_lab(c, t, prog=1.0):
    bg.wallpaper(c, 0, 0, WW, FL, (92, 70, 56), (84, 62, 50), (120, 96, 76))
    bg.blackboard(c, 10, 22, 92, 76, t, 1, prog=prog); bg.blackboard(c, 114, 22, 92, 76, t, 2, prog=prog); bg.blackboard(c, 218, 22, 92, 76, t, 3, prog=prog)
    c.R(0, 100, WW, 36, (96, 60, 40)); c.R(0, 100, WW, 3, (170, 120, 84))
    bg.planks(c, 0, FL, WW, 44, (110, 78, 56), seed=33, pw=9); c.R(0, FL - 2, WW, 3, (60, 40, 30))
    PR.keep(c, PR.lamp_table(), 290, 112)


def lab_a(t, u):
    c = cv((0, '#000000'), (1, '#000000')); _env_lab(c, t, .3 + .7 * u)
    place(c, rpg('hawking_y', int(t * 2) % 2), 130, FW + 8); PR.keep(c, PR.cane(), 150, 116)
    place(c, rpg('prod1', 0), 210, FW + 8)
    sign(c, 160, 4, '1966', (255, 230, 120), 24, (40, 20, 50))
    c.amb = (1.0, .96, .92); c.vig = .65
    return c.render()


def lab_b(t, u):
    c = cv((0, '#000000'), (1, '#000000')); _env_lab(c, t, 1)
    for i, f in enumerate(('kid_a', 'kid_c', 'kid_b')):
        place(c, rpg(f, int(t * 5 + i) % 2), 60 + ((t * 40 + i * 70) % 220), FW + 12 + i * 4, sh=False)
    place(c, bat('jane', 'stand'), 250, FM); place(c, bat('hawking_y', 'hold'), 90, FM)
    c.amb = (1.0, .96, .92); c.vig = .65
    return c.render()


def lab_c(t, u):
    c = cv((0, '#000000'), (1, '#000000')); _env_lab(c, t, 1)
    seated(c, 'hawking', 150, 172, 'bat', t=t)
    for i in range(3):
        ph = (t * .5 + i * .33) % 1; bg.wtext(c, 200 + i * 14, 80 - int(ph * 30), 'HA', (255, 230, 120), 8)
    sign(c, 160, 4, 'MÁS LEJOS', (140, 220, 255), 16, (20, 24, 60))
    c.amb = (1.0, .96, .92); c.vig = .65
    return c.render()


lab = phased(lab_a, lab_b, lab_c, cuts=(.36, .56))


# ============================================================ 9. 1974: agujeros negros
def _env_space(c, t):
    stars(c, t, 420, 5, 178); bg.nebula_l(c, t, 4); bg.shoot_l(c, t, 0, 3.4)


def _spc(): return cv((0, '#02030c'), (.5, '#0a0830'), (1, '#150a40'))


def hole_a(t, u):
    c = _spc(); _env_space(c, t); bg.black_hole(c, 160, 70, 32, t); bg.hill_l(c, 150, (14, 12, 34))
    seated(c, 'hawking', 160, 166, 'rpg', t=t)
    sign(c, 100, 8, '1974', (255, 230, 120), 24, (40, 20, 80))
    c.amb = (1.0, .96, 1.04); c.vig = .6
    return c.render()


def hole_b(t, u):
    c = _spc(); _env_space(c, t); bg.black_hole(c, 100, 76, 34, t)
    seated(c, 'hawking', 230, 172, 'bat', t=t)
    c.amb = (1.0, .96, 1.04); c.vig = .6
    return c.render()


def hole_c(t, u):
    c = _spc(); _env_space(c, t); bg.black_hole(c, 160, 90, 46, t)
    if u > .3: sign(c, 160, 8, 'BRILLAN', (255, 220, 140), 16, (40, 20, 80))
    c.amb = (1.0, .96, 1.04); c.vig = .6
    return c.render()


hole = phased(hole_a, hole_b, hole_c)


# ============================================================ 10. Sociedad Real y Newton
def _env_hall(c, t):
    bg.wallpaper(c, 0, 0, WW, FL, (96, 36, 52), (88, 30, 46), (140, 76, 90))
    for x in (20, 272):
        c.R(x, 10, 28, 126, (200, 180, 150)); c.R(x, 10, 28, 4, (240, 224, 196)); c.R(x + 2, 14, 3, 122, (230, 214, 184)); c.R(x + 24, 14, 3, 122, (150, 130, 104))
    for lx in (96, 224):
        c.R(lx, 0, 1, 14, (60, 50, 40)); c.d.polygon([(lx - 14, 26), (lx + 14, 26), (lx + 7, 14), (lx - 7, 14)], fill=(255, 214, 120)); c.light(lx, 30, 50, 40, (255, 214, 140), .7)
    bg.planks(c, 0, FL, WW, 44, (130, 92, 64), seed=47, pw=9); c.R(0, FL - 2, WW, 3, GOLD)
    c.R(120, FL, 80, 44, (150, 24, 44)); c.R(120, FL, 80, 2, (230, 90, 100))


def royal_a(t, u):
    c = cv((0, '#000000'), (1, '#000000')); _env_hall(c, t)
    sign(c, 160, 8, 'SOCIEDAD REAL', (255, 230, 120), 16, (60, 20, 36))
    for i, f in enumerate(('prod1', 'prod2', 'mom', 'dad', 'kid_c', 'kid_a', 'alice')):
        place(c, rpg(f, int(t * 3 + i) % 2 if int(t * 2) % 2 else 0), 36 + i * 41, FW + 24, sh=False)
    seated(c, 'hawking', 160, FW + 10, 'rpg', t=t)
    c.amb = (1.0, .96, .96); c.vig = .65
    return c.render()


def royal_b(t, u):
    c = cv((0, '#000000'), (1, '#000000')); _env_hall(c, t)
    PR.keep(c, PR.frame_portrait(), 143, 36); sign(c, 160, 4, 'NEWTON', (255, 230, 120), 16, (60, 20, 36))
    seated(c, 'hawking', 160, 172, 'bat', t=t)
    c.amb = (1.0, .96, .96); c.vig = .65
    return c.render()


def royal_c(t, u):
    c = cv((0, '#000000'), (1, '#000000')); _env_hall(c, t)
    PR.keep(c, PR.frame_portrait(), 143, 36); sign(c, 160, 4, '1979', (255, 230, 120), 24, (60, 20, 36))
    seated(c, 'hawking', 160, 172, 'bat', t=t)
    c.amb = (1.0, .96, .96); c.vig = .65
    return c.render()


royal = phased(royal_a, royal_b, royal_c, cuts=(.42, .72))


# ============================================================ 11. 1985: sin voz
def _env_hosp(c, t, beat=1.0):
    bg.hospital_wall_l(c, t)
    c.R(226, 18, 64, 62, (96, 130, 134)); c.R(228, 20, 60, 58, (24, 36, 90)); c.R(256, 20, 2, 58, (96, 130, 134)); c.R(228, 48, 60, 2, (96, 130, 134))
    PR.keep(c, PR.monitor_ecg(), 40, 76)
    if beat:
        pts = []
        for i in range(30):
            ph = (t * 2 + i * .08) % 1; y = 86 - (8 if ph < .12 else 0) + (5 if .12 <= ph < .2 else 0)
            pts.append((46 + i, y))
        c.d.line(pts, fill=(80, 255, 140))
    else: c.d.line([(46, 86), (76, 86)], fill=(255, 80, 80))
    c.R(300, 70, 2, 70, (190, 196, 214)); c.R(294, 70, 14, 4, (190, 196, 214)); c.R(295, 74, 12, 18, (200, 230, 250))


def hosp_a(t, u):
    c = cv((0, '#000000'), (1, '#000000')); _env_hosp(c, t)
    PR.keep(c, PR.hospital_bed(), 110, 124); place(c, rpg('hawking', 0), 138, 138, sh=False)
    place(c, rpg('nurse', 0), 230, FW + 12)
    c.amb = (1.0, 1.0, 1.02); c.vig = .65
    return c.render()


def hosp_b(t, u):
    c = cv((0, '#000000'), (1, '#000000')); _env_hosp(c, t, beat=int(t * 2) % 5 != 0)
    place(c, bat('nurse', 'hold'), 200, FM); sign(c, 160, 8, '1985', (255, 90, 90), 24, (40, 10, 24))
    c.light(60, 86, 50, 30, (80, 255, 140), .5); c.amb = (.9, .96, 1.0); c.vig = .75
    return c.render()


def hosp_c(t, u):
    c = cv((0, '#000000'), (1, '#000000')); _env_hosp(c, t)
    c.light(258, 50, 110, 70, (255, 230, 160), .5 + .4 * u)
    seated(c, 'hawking', 160, 172, 'bat', t=t)
    c.amb = (1.0, 1.0, 1.0); c.vig = .6
    return c.render()


hosp = phased(hosp_a, hosp_b, hosp_c, cuts=(.3, .56))


# ============================================================ 12. la voz de la computadora
def _env_study(c, t):
    bg.wallpaper(c, 0, 0, WW, FL, (50, 56, 100), (44, 50, 92), (80, 90, 150))
    bg.shelf(c, 16, 14, 70, 102, seed=81, rows=3)
    bg.window(c, 250, 20, 50, 66, t=t, curtain=(120, 90, 180), rain=False, seed=7)
    bg.planks(c, 0, FL, WW, 44, (100, 74, 56), seed=83, pw=9); c.R(0, FL - 2, WW, 3, (50, 30, 24))
    c.R(90, 118, 160, 6, (130, 84, 54)); c.R(90, 118, 160, 2, (200, 150, 100)); c.R(98, 124, 144, 24, (96, 60, 40))


def _screen(c, x, y, w, h, text, t):
    c.R(x, y, w, h, (6, 24, 18)); n = int((t * 7) % (len(text) + 8))
    bg.wtext(c, x + 3, y + 4, text[:n] + ('_' if int(t * 4) % 2 else ' '), (120, 255, 170), 8, outline=None)


def voice_a(t, u):
    c = cv((0, '#000000'), (1, '#000000')); _env_study(c, t)
    seated(c, 'hawking', 130, FW + 8, 'rpg', t=t)
    PR.keep(c, PR.computer_old(), 170, 82); _screen(c, 175, 85, 30, 14, 'HOLA', t)
    c.amb = (1.0, .98, 1.04); c.vig = .65
    return c.render()


def voice_b(t, u):
    c = cv((0, '#000000'), (1, '#000000')); _env_study(c, t)
    PR.keep(c, PR.computer_old(), 196, 76); _screen(c, 201, 79, 30, 14, 'HOLA MUNDO', t)
    seated(c, 'hawking', 130, 172, 'bat', t=t)
    for i in range(3):
        ph = (t * 1.2 + i * .33) % 1; c.ed.arc([216 - ph * 40, 60 - ph * 40, 216 + ph * 40, 60 + ph * 40], 300, 60, fill=(120, 255, 170, int(220 * (1 - ph))), width=2)
    c.amb = (1.0, .98, 1.04); c.vig = .65
    return c.render()


def voice_c(t, u):
    c = cv((0, '#000000'), (1, '#000000')); _env_study(c, t)
    c.R(172, 20, 138, 90, (6, 24, 18)); c.R(172, 20, 138, 1, (60, 120, 90))
    bg.wtext(c, 178, 28, 'ASI SE HABLA', (120, 255, 170), 16, outline=None); bg.wtext(c, 178, 52, 'PALABRA POR', (120, 255, 170), 16, outline=None); bg.wtext(c, 178, 76, 'PALABRA', (120, 255, 170), 16, outline=None)
    seated(c, 'hawking', 110, 172, 'bat', t=t)
    c.amb = (1.0, .98, 1.04); c.vig = .65
    return c.render()


voice = phased(voice_a, voice_b, voice_c)


# ============================================================ 13. libro y 10 millones
def _env_books(c, t):
    bg.wallpaper(c, 0, 0, WW, FL, (176, 74, 120), (164, 66, 110), (210, 120, 150))
    bg.shelf(c, 10, 14, 70, 104, seed=61, rows=4); bg.shelf(c, 240, 14, 70, 104, seed=62, rows=4)
    for yy in range(FL, 180, 11):
        for xx in range(-(yy // 11 % 2) * 11, WW, 22): c.R(xx, yy, 11, 11, (236, 226, 206)); c.R(xx + 11, yy, 11, 11, (150, 70, 80))
    c.R(0, FL - 2, WW, 3, (90, 50, 40))


def books_a(t, u):
    c = cv((0, '#000000'), (1, '#000000')); _env_books(c, t)
    for i, x in enumerate((96, 160, 224)): PR.keep(c, PR.book_stack(3 + i % 2), x - 17, FL - (3 + i % 2) * 8 + 6)
    for i, f in enumerate(('kid_a', 'kid_b', 'mom', 'dad', 'alice')): place(c, rpg(f, int(t * 3 + i) % 2), 40 + i * 52 + (t * 4) % 6, FW + 22, sh=False)
    seated(c, 'hawking', 160, FW + 8, 'rpg', t=t)
    for i in range(34):
        ph = (t * .5 + i * .03) % 1; c.R((i * 53 + math.sin(t * 3 + i) * 6) % 310 + 4, ph * 176, 2, 3, ((255, 90, 120), (90, 220, 255), (255, 230, 90), (140, 255, 140))[i % 4])
    c.amb = (1.03, .98, .98); c.vig = .55
    return c.render()


def books_b(t, u):
    c = cv((0, '#000000'), (1, '#000000')); _env_books(c, t)
    c.R(210, 36, 84, 60, (30, 26, 30)); c.R(213, 39, 78, 54, (255, 214, 60)); bg.wtext(c, 252, 46, 'SIMPSON', (60, 30, 90), 8, outline=None, center=True)
    c.d.ellipse([234, 56, 270, 90], fill=(255, 224, 80), outline=(160, 110, 30))
    PR.keep(c, PR.book_stack(4), 96, 116)
    seated(c, 'hawking', 150, 172, 'bat', t=t)
    c.amb = (1.03, .98, .98); c.vig = .55
    return c.render()


books = phased(books_a, books_b, cuts=(.5,))


# ============================================================ 14. 55 años
def _env_road(c, t, k=0.0):
    c.im.paste(Image.fromarray(vgrad([(0, '#1a1a6a'), (.4, '#c0408a'), (.6, '#ff9a50'), (.78, '#ffd080'), (1, '#3a2438')]).astype('uint8')), (0, 0))
    bg.skyline(c, 0, 128, cols=((86, 46, 110), (104, 58, 128)), seed=21, lit=.2, t=t, hmin=20, hmax=70)
    c.d.ellipse([140, 70 - 20 * k, 180, 110 - 20 * k], fill=(255, 244, 180))
    c.R(0, FL, WW, 44, (70, 50, 70)); c.R(0, FL, WW, 3, (230, 170, 120))
    for x in range(0, WW, 40): c.R(x + int(t * 24) % 40, 158, 20, 2, (240, 220, 110))


def years_a(t, u):
    c = cv((0, '#000000'), (1, '#000000')); _env_road(c, t)
    sign(c, 160, 6, 'SIEMPRE HAY ALGO', (255, 230, 120), 8, (50, 24, 60)); sign(c, 160, 26, 'QUE PUEDES HACER', (255, 230, 120), 8, (50, 24, 60))
    seated(c, 'hawking', 50 + 220 * u, FW + 8, 'rpg', t=t)
    c.amb = (1.0, .96, .98); c.vig = .6
    return c.render()


def years_b(t, u):
    c = cv((0, '#000000'), (1, '#000000')); _env_road(c, t, u)
    yr = int(1963 + 55 * ease(u))
    for i in range(10):
        ph = (t * .6 + i * .1) % 1; PR.keep(c, PR.calendar_page(), 10 + (i * 71) % 290, int(ph * 190) - 20)
    seated(c, 'hawking', 160, 172, 'bat', t=t)
    sign(c, 160, 8, str(yr), (255, 230, 120), 24, (50, 24, 60))
    c.amb = (1.0, .96, .98); c.vig = .6
    return c.render()


years = phased(years_a, years_b, cuts=(.55,))


# ============================================================ 16. mira hacia las estrellas
def stars_a(t, u):
    c = cv((0, '#050824'), (.5, '#16146a'), (1, '#3a1a5a')); _env_sky(c, t)
    for i in range(8): place(c, rpg(('kid_a', 'kid_b', 'mom', 'dad', 'kid_c', 'alice', 'prod1', 'prod2')[i], 0), 24 + i * 40 + (20 if i > 3 else 0), FW + 22, sh=False)
    seated(c, 'hawking', 170, FW + 8, 'rpg', t=t)
    sign(c, 160, 8, '2012', (255, 230, 120), 24, (30, 24, 80))
    c.amb = (.96, .96, 1.08); c.vig = .6
    return c.render()


def stars_b(t, u):
    c = cv((0, '#050824'), (.5, '#16146a'), (1, '#3a1a5a')); _env_space(c, t); bg.hill_l(c, 150, (14, 12, 34))
    seated(c, 'hawking', 160, 172, 'bat', t=t)
    for i in range(5): bg.shoot_l(c, t, i, 2.5)
    c.amb = (.96, .96, 1.08); c.vig = .6
    return c.render()


def stars_c(t, u):
    c = cv((0, '#050824'), (.5, '#16146a'), (1, '#3a1a5a')); _env_space(c, t); bg.hill_l(c, 158, (14, 12, 34)); bg.nebula_l(c, t, 7)
    seated(c, 'hawking', 160, 176, 'bat', t=t)
    for i in range(4): bg.shoot_l(c, t, i + 5, 2.0)
    c.amb = (.96, .96, 1.08); c.vig = .6
    return c.render()


starry = phased(stars_a, stars_b, stars_c, cuts=(.34, .67))


# ============================================================ 17. final
def final_a(t, u):
    c = _sky(); _env_sky(c, t)
    place(c, rpg('you', int(t * 2) % 2 if u < .15 else 0), 170, 150)
    c.light(170, 110, 70, 40, (140, 170, 255), .35); c.amb = (.92, .94, 1.1); c.vig = .65
    return c.render()


def final_b(t, u):
    c = _sky(); _env_sky(c, t)
    place(c, bat('you', 'stand'), 190, 172)
    c.amb = (.92, .94, 1.1); c.vig = .65
    return c.render()


final = phased(final_a, final_b, cuts=(.5,))


# ============================================================ retratos en horizontal
def portrait_land(t, who='hawking', expr='n', look=(0, 0), tone='cold'):
    from scenes2 import bust
    if tone == 'cold': g = vgrad([(0, '#0a1a2a'), (1, '#1c2c44')]); amb = (.9, .94, 1)
    else: g = vgrad([(0, '#3a1e10'), (.5, '#a05a28'), (1, '#e0a040')]); amb = (1, .95, .88)
    c = Canvas(g); base = np.array(g[90, 0])
    for i in range(14):
        a = i / 14 * math.pi * 2 + t * .15
        c.d.polygon([(160, 100), (160 + 420 * math.cos(a), 100 + 420 * math.sin(a)), (160 + 420 * math.cos(a + .18), 100 + 420 * math.sin(a + .18))], fill=tuple(int(v) for v in base * 1.12 + 6))
    b = bust(who, expr, look, t, 1.75, None)
    c.blit(b, 160 - b.width / 2, 18 + math.sin(t * 1.8) * 1.2)
    stars(c, t, 40, 9, 60) if tone == 'cold' else None
    c.light(160, 90, 130, 90, (255, 210, 150) if tone != 'cold' else (120, 160, 230), .35)
    c.amb = amb; c.vig = .8
    return c.render()
