"""Historia 8 (Stephen Hawking): dos años de vida. 17 escenas; cada una con plano ancho (chibi), medio (trainer) y cercano (corte duro + zoom)."""
import math, random
import numpy as np
from PIL import Image, ImageDraw
from lib import *
import bg
import props as PR
from scenes3 import rpg, bat, place
from scenes6 import top_half

GOLD = (230, 190, 90)


def phased(*fns, cuts=(.34, .67)):
    def f(t, u):
        for i, fn in enumerate(fns):
            lo = cuts[i - 1] if i else 0.0
            hi = cuts[i] if i < len(cuts) else 1.0
            if u < hi or i == len(fns) - 1: return fn(t, max(0.0, min(1.0, (u - lo) / max(1e-6, hi - lo))))
    return f


def seated(c, who, cx, floor, scale='rpg', flip=False, t=0, blanket=(90, 96, 140)):
    """personaje en silla de ruedas: respaldo, torso (recortado a la cadera), manta y ruedas por delante."""
    r = 9 if scale == 'rpg' else 14
    back, front = PR.wheelchair_back(r), PR.wheelchair_front(r)
    spr = rpg(who, 0) if scale == 'rpg' else bat(who, 'stand')
    cut = 47 if scale == 'rpg' else 84
    top = spr.crop((0, 0, spr.width, cut))
    seat = floor - (r + 5)
    bx = int(cx - back.width / 2); by = int(floor - back.height)
    c.im.alpha_composite(back, (bx, by)) if bx >= 0 and by >= 0 else c.im.paste(back, (bx, by), back)
    place(c, top, cx, seat, flip=flip, sh=False)
    bwid = 22 if scale == 'rpg' else 34
    c.R(int(cx - bwid // 2), seat - 3, bwid, 9 if scale == 'rpg' else 12, blanket); c.R(int(cx - bwid // 2), seat - 3, bwid, 1, shade(blanket, 1.3))
    fx = int(cx - front.width / 2); fy = int(floor - front.height)
    c.im.alpha_composite(front, (fx, fy)) if fx >= 0 and fy >= 0 else c.im.paste(front, (fx, fy), front)
    bg.shadow(c, cx, floor + 1, back.width) if hasattr(bg, 'shadow') else None


def _sky(top='#060a2e', mid='#1a1a70', bot='#2a1a4a'):
    return Canvas(vgrad([(0, top), (.5, mid), (1, bot)]))


# ============================================================ 1. el cielo (gancho)
def _env_sky(c, t):
    stars(c, t, 150, 3, 230); bg.nebula(c, t, 2); bg.shooting_star(c, t, 0, 3.0); bg.shooting_star(c, t, 1, 4.1)
    c.d.ellipse([118, 40, 136, 58], fill=(248, 244, 214)); c.d.ellipse([123, 38, 141, 56], fill=(10, 16, 70))
    bg.hill(c, 206, (18, 16, 44), t)
    PR.keep(c, PR.telescope(), 108, 188)


def sky_a(t, u):
    c = _sky(); _env_sky(c, t)
    seated(c, 'hawking', 66, 232, 'rpg', t=t)
    c.light(66, 190, 60, 50, (140, 170, 255), .35); c.amb = (.92, .94, 1.1); c.vig = .65
    return c.render()


def sky_b(t, u):
    c = _sky(); _env_sky(c, t)
    seated(c, 'hawking', 70, 252, 'bat', t=t)
    c.light(70, 200, 70, 60, (140, 170, 255), .35); c.amb = (.92, .94, 1.1); c.vig = .65
    return c.render()


sky = phased(sky_a, sky_b, cuts=(.5,))


# ============================================================ 2. Oxford, 1942 (niño que mira el cielo)
def _env_oxford(c, t):
    c.d.rectangle([0, 0, WW, 120], fill=(70, 50, 120))
    bg_g = vgrad([(0, '#3a2a7a'), (.4, '#e0708a'), (.62, '#ffc880'), (1, '#4a3a30')]); c.im.paste(Image.fromarray(bg_g.astype('uint8')), (0, 0))
    stars(c, t, 50, 4, 70)
    bg.stone_college(c, 0, 96, WW, 110, seed=7, lit=.5, t=t)
    for x in (10, 148): bg.tree(c, x, 206, 52, 'round', (214, 120, 40))
    bg.cobble(c, 0, 206, WW, 94, base=(150, 130, 112), seed=9)
    c.R(0, 204, WW, 3, (190, 170, 140))


def oxford_a(t, u):
    c = Canvas(vgrad([(0, '#000000'), (1, '#000000')])); _env_oxford(c, t)
    PR.keep(c, PR.telescope(), 42, 190)
    place(c, rpg('hawking_k', int(t * 2) % 2), 74, 236)
    place(c, rpg('kid_a', 0), 106, 236); place(c, rpg('kid_b', 0), 134, 236)
    bg.sign2(c, 80, 70, '1942', (255, 230, 120), 24, plate=(50, 24, 60))
    c.amb = (1.0, .94, .94); c.vig = .65
    return c.render()


def oxford_b(t, u):
    c = Canvas(vgrad([(0, '#000000'), (1, '#000000')])); _env_oxford(c, t)
    PR.keep(c, PR.telescope(), 100, 192)
    place(c, bat('hawking_k', 'stand'), 62, 246)
    bg.sign2(c, 80, 70, 'OXFORD', (255, 230, 120), 16, plate=(50, 24, 60))
    c.amb = (1.0, .94, .94); c.vig = .65
    return c.render()


def oxford_c(t, u):
    c = Canvas(vgrad([(0, '#000000'), (1, '#000000')])); _env_oxford(c, t)
    place(c, bat('kid_b', 'stand'), 46, 246); place(c, bat('kid_a', 'stand'), 116, 246)
    place(c, bat('hawking_k', 'stand'), 80, 250)
    if u > .25: bg.bubble2(c, 94, 122, 'EINSTEIN', 8)
    c.amb = (1.0, .94, .94); c.vig = .65
    return c.render()


oxford = phased(oxford_a, oxford_b, oxford_c)


# ============================================================ 3. Cambridge
def _env_cam(c, t):
    c.im.paste(Image.fromarray(vgrad([(0, '#1a2a7a'), (.5, '#e0708a'), (.7, '#ffd090'), (1, '#2a4a2a')]).astype('uint8')), (0, 0))
    bg.stone_college(c, 0, 90, 70, 116, seed=11, lit=.4, t=t); bg.stone_college(c, 90, 90, 70, 116, seed=12, lit=.4, t=t)
    c.R(70, 120, 20, 86, (50, 36, 40)); c.d.pieslice([70, 104, 90, 136], 180, 360, fill=(50, 36, 40))                         # portón
    c.R(0, 206, WW, 94, (74, 130, 70)); c.R(0, 206, WW, 3, (130, 190, 110))
    c.R(58, 206, 44, 94, (190, 170, 130))
    for x in range(2, WW, 7): c.R(x, 214 + (x * 5) % 50, 1, 3, (110, 170, 90))
    for x in (28, 134): bg.tree(c, x, 214, 44, 'round', (60, 140, 70))


def cam_a(t, u):
    c = Canvas(vgrad([(0, '#000000'), (1, '#000000')])); _env_cam(c, t)
    bg.sign2(c, 80, 70, 'CAMBRIDGE', (255, 230, 120), 16, plate=(50, 24, 60))
    place(c, rpg('hawking_y', int(t * 4) % 2), 40 + 80 * u, 238)
    for i, f in enumerate(('prod1', 'kid_c')): place(c, rpg(f, int(t * 3 + i) % 2), 130 - 90 * u + i * 20, 262, sh=False)
    c.amb = (1.0, .96, .96); c.vig = .65
    return c.render()


def cam_b(t, u):
    c = Canvas(vgrad([(0, '#000000'), (1, '#000000')])); _env_cam(c, t)
    bg.sign2(c, 80, 70, 'CAMBRIDGE', (255, 230, 120), 16, plate=(50, 24, 60))
    place(c, bat('hawking_y', 'hold'), 80, 248 + math.sin(t * 4))
    c.amb = (1.0, .96, .96); c.vig = .65
    return c.render()


cam = phased(cam_a, cam_b, cuts=(.5,))


# ============================================================ 4. 21 años: el cuerpo empieza a fallar
def _env_fall(c, t):
    c.im.paste(Image.fromarray(vgrad([(0, '#2a1a5a'), (.5, '#c0508a'), (1, '#2a1a30')]).astype('uint8')), (0, 0))
    bg.stone_college(c, 0, 80, WW, 130, seed=13, lit=.3, t=t)
    c.R(0, 206, WW, 94, (110, 100, 96))
    for k in range(7): c.R(10 + k * 8, 206 - k * 6, 130 - k * 8, 6, (150, 140, 130)); c.R(10 + k * 8, 206 - k * 6, 130 - k * 8, 1, (200, 190, 176))


def fall_a(t, u):
    c = Canvas(vgrad([(0, '#000000'), (1, '#000000')])); _env_fall(c, t)
    x = 30 + 60 * u; y = 232 - int(u * 30)
    place(c, rpg('hawking_y', int(t * 4) % 2 if u < .7 else 0), x + (math.sin(t * 30) * 2 if u > .6 else 0), y)
    if u > .6:
        bg.wtext(c, x + 6, y - 90, '!', (255, 80, 80), 24)
        for i in range(5):
            ph = (u - .6) * 3 + i * .1; PR.keep(c, PR.stamp_paper(), x + 10 + i * 8, y - 60 - int(ph * 20) + i * 4)
    c.amb = (1.0, .94, .94); c.vig = .65
    return c.render()


def fall_b(t, u):
    c = Canvas(vgrad([(0, '#000000'), (1, '#000000')])); _env_fall(c, t)
    PR.keep(c, PR.book_stack(3), 100 + int(u * 6), 120 + int(u * 100))
    place(c, bat('hawking_y', 'hip'), 70 + math.sin(t * 24) * 1.5, 250)
    bg.sign2(c, 80, 70, '21 AÑOS', (255, 90, 90), 16, plate=(40, 10, 24))
    pulse = .3 + .3 * (math.sin(t * 8) > 0); c.light(80, 150, 90, 100, (255, 60, 60), pulse)
    c.amb = (1.0, .92, .94); c.vig = .7
    return c.render()


def fall_c(t, u):
    c = Canvas(vgrad([(0, '#000000'), (1, '#000000')])); _env_fall(c, t)
    place(c, bat('hawking_y', 'stand'), 80 + math.sin(t * 28) * 1.2, 252)
    for i in range(4): bg.wtext(c, 56 + i * 14, 108 + int(math.sin(t * 6 + i) * 4), '?', (255, 220, 90), 16)
    c.amb = (1.0, .92, .94); c.vig = .7
    return c.render()


fall = phased(fall_a, fall_b, fall_c)


# ============================================================ 5. el diagnóstico: dos años
def _env_doc(c, t):
    c.R(0, 0, WW, 206, (150, 190, 186)); c.R(0, 150, WW, 56, (120, 150, 150)); c.R(0, 150, WW, 3, (220, 240, 236))
    c.R(98, 84, 50, 56, (60, 50, 44)); c.R(100, 86, 46, 52, (200, 226, 240))
    for k in range(5): c.R(100, 88 + k * 10, 46, 5, (170, 200, 220))
    c.R(14, 92, 36, 28, (60, 50, 44)); c.R(16, 94, 32, 24, (250, 246, 232)); [c.R(20 + k * 8, 98, 5, 14, (200, 90, 90)) for k in range(3)]
    ang = t * 1.0; c.d.ellipse([60, 80, 84, 104], fill=(250, 248, 240), outline=(40, 30, 30)); c.d.line([(72, 92), (72 + 9 * math.cos(ang), 92 + 9 * math.sin(ang))], fill=(200, 40, 50))
    bg.planks(c, 0, 206, WW, 90, (126, 90, 64), seed=21, pw=9); c.R(0, 204, WW, 3, (60, 40, 32))
    c.R(22, 178, 104, 6, (130, 84, 54)); c.R(22, 178, 104, 2, (200, 150, 100)); c.R(28, 184, 92, 26, (96, 60, 40))


def doc_a(t, u):
    c = Canvas(vgrad([(0, '#000000'), (1, '#000000')])); _env_doc(c, t)
    place(c, rpg('doctor', 0), 100, 180, sh=False); c.R(22, 178, 104, 6, (130, 84, 54)); c.R(22, 178, 104, 2, (200, 150, 100))
    place(c, rpg('hawking_y', 0), 44, 234, flip=False)
    c.amb = (.98, 1.0, 1.0); c.vig = .65
    return c.render()


def doc_b(t, u):
    c = Canvas(vgrad([(0, '#000000'), (1, '#000000')])); _env_doc(c, t)
    place(c, bat('doctor', 'hold'), 106, 250)
    k = 1 + .06 * math.sin(t * 6)
    bg.sign2(c, 80, 66, '2 AÑOS', (255, 90, 90), 24, plate=(40, 10, 24))
    PR.keep(c, PR.calendar_page(), 24, 150)
    c.amb = (.98, 1.0, 1.0); c.vig = .65
    return c.render()


def doc_c(t, u):
    c = Canvas(vgrad([(0, '#000000'), (1, '#000000')])); _env_doc(c, t)
    place(c, bat('hawking_y', 'stand'), 80, 252 + math.sin(t * 2))
    c.R(0, 0, WW, 300, (0, 0, 0, 0)) if False else None
    c.light(80, 140, 90, 90, (200, 210, 255), .25); c.amb = (.84, .88, 1.0); c.vig = .85
    return c.render()


doctor = phased(doc_a, doc_b, doc_c)


# ============================================================ 7. Jane y la boda (1965)
def _env_love(c, t):
    c.im.paste(Image.fromarray(vgrad([(0, '#5a3a9a'), (.45, '#f09aa6'), (.7, '#ffe0a0'), (1, '#3a6a3a')]).astype('uint8')), (0, 0))
    for i in range(3): c.R((t * (3 + i) + i * 60) % 200 - 30, 40 + i * 14, 30, 5, (255, 220, 230))
    bg.stone_college(c, 0, 110, 60, 96, seed=15, lit=.2, t=t); bg.stone_college(c, 100, 110, 60, 96, seed=16, lit=.2, t=t)
    c.R(0, 206, WW, 94, (92, 160, 84)); c.R(0, 206, WW, 3, (150, 210, 120))
    for x in range(2, WW, 6): c.R(x, 212 + (x * 7) % 60, 1, 3, (120, 190, 100))
    # arco de flores
    c.d.arc([46, 96, 114, 196], 180, 360, fill=(120, 80, 50), width=3)
    for k in range(18):
        a = math.pi + k * math.pi / 17; px = 80 + math.cos(a) * 34; py = 164 + math.sin(a) * 66
        c.d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=((255, 150, 190), (255, 220, 120), (255, 255, 255))[k % 3])
    for i in range(18):
        ph = (t * .2 + i * .056) % 1; xx = (i * 37 + math.sin(t * 2 + i) * 8) % 150 + 4; yy = ph * 230 + 20
        c.R(xx, yy, 2, 2, (255, 200, 220))


def love_a(t, u):
    c = Canvas(vgrad([(0, '#000000'), (1, '#000000')])); _env_love(c, t)
    place(c, rpg('jane', 0), 68, 236); place(c, rpg('hawking_y', 0), 94, 236)
    for i in range(4): PR.keep(c, PR.heart(), 70 + i * 8, 140 - int(((t * .6 + i * .25) % 1) * 60))
    c.amb = (1.04, .98, .98); c.vig = .55
    return c.render()


def love_b(t, u):
    c = Canvas(vgrad([(0, '#000000'), (1, '#000000')])); _env_love(c, t)
    place(c, bat('jane', 'stand'), 56, 250); place(c, bat('hawking_y', 'stand'), 104, 250)
    bg.sign2(c, 80, 70, '1965', (255, 230, 120), 24, plate=(70, 24, 60))
    for i in range(6): PR.keep(c, PR.heart(11), 76 + (i % 3) * 6, 120 - int(((t * .6 + i * .17) % 1) * 70))
    c.amb = (1.04, .98, .98); c.vig = .55
    return c.render()


love = phased(love_a, love_b, cuts=(.5,))


# ============================================================ 8. doctorado, familia y sentido del humor
def _env_lab(c, t, prog=1.0):
    bg.wallpaper(c, 0, 0, WW, 206, (92, 70, 56), (84, 62, 50), (120, 96, 76))
    bg.blackboard(c, 8, 70, 66, 70, t, 1, prog=prog); bg.blackboard(c, 86, 70, 66, 70, t, 2, prog=prog)
    c.R(0, 150, WW, 56, (96, 60, 40)); c.R(0, 150, WW, 3, (170, 120, 84))
    bg.planks(c, 0, 206, WW, 90, (110, 78, 56), seed=33, pw=9); c.R(0, 204, WW, 3, (60, 40, 30))
    PR.keep(c, PR.lamp_table(), 132, 180)


def lab_a(t, u):
    c = Canvas(vgrad([(0, '#000000'), (1, '#000000')])); _env_lab(c, t, .3 + .7 * u)
    place(c, rpg('hawking_y', int(t * 2) % 2), 60, 236); PR.keep(c, PR.cane(), 78, 200)
    place(c, rpg('prod1', 0), 120, 236)
    bg.sign2(c, 80, 56, '1966', (255, 230, 120), 24, plate=(40, 20, 50))
    c.amb = (1.0, .96, .92); c.vig = .65
    return c.render()


def lab_b(t, u):
    c = Canvas(vgrad([(0, '#000000'), (1, '#000000')])); _env_lab(c, t, 1)
    for i, f in enumerate(('kid_a', 'kid_c', 'kid_b')):
        place(c, rpg(f, int(t * 5 + i) % 2), 20 + ((t * 24 + i * 40) % 130), 244 + i * 4, sh=False)
    place(c, bat('jane', 'stand'), 120, 250); place(c, bat('hawking_y', 'hold'), 52, 250)
    c.amb = (1.0, .96, .92); c.vig = .65
    return c.render()


def lab_c(t, u):
    c = Canvas(vgrad([(0, '#000000'), (1, '#000000')])); _env_lab(c, t, 1)
    seated(c, 'hawking', 70, 254, 'bat', t=t)
    for i in range(3):
        ph = (t * .5 + i * .33) % 1; bg.wtext(c, 108 + i * 12, 150 - int(ph * 30), 'HA', (255, 230, 120), 8)
    bg.sign2(c, 80, 56, 'MAS LEJOS', (140, 220, 255), 16, plate=(20, 24, 60))
    c.amb = (1.0, .96, .92); c.vig = .65
    return c.render()


lab = phased(lab_a, lab_b, lab_c, cuts=(.36, .56))


# ============================================================ 9. 1974: los agujeros negros brillan
def _env_space(c, t):
    stars(c, t, 220, 5, 290); bg.nebula(c, t, 4); bg.shooting_star(c, t, 0, 3.4)


def hole_a(t, u):
    c = _sky('#02030c', '#0a0830', '#150a40'); _env_space(c, t)
    bg.black_hole(c, 80, 124, 30, t); bg.hill(c, 226, (14, 12, 34))
    seated(c, 'hawking', 80, 252, 'rpg', t=t)
    bg.sign2(c, 80, 62, '1974', (255, 230, 120), 24, plate=(40, 20, 80))
    c.amb = (1.0, .96, 1.04); c.vig = .6
    return c.render()


def hole_b(t, u):
    c = _sky('#02030c', '#0a0830', '#150a40'); _env_space(c, t)
    bg.black_hole(c, 80, 110, 28, t)
    seated(c, 'hawking', 80, 262, 'bat', t=t)
    c.amb = (1.0, .96, 1.04); c.vig = .6
    return c.render()


def hole_c(t, u):
    c = _sky('#02030c', '#0a0830', '#150a40'); _env_space(c, t)
    bg.black_hole(c, 80, 140, 36, t)
    bg.sign2(c, 80, 62, 'BRILLAN', (255, 220, 140), 16, plate=(40, 20, 80)) if u > .3 else None
    c.amb = (1.0, .96, 1.04); c.vig = .6
    return c.render()


hole = phased(hole_a, hole_b, hole_c)


# ============================================================ 10. Sociedad Real y cátedra de Newton
def _env_hall(c, t):
    bg.wallpaper(c, 0, 0, WW, 206, (96, 36, 52), (88, 30, 46), (140, 76, 90))
    for x in (4, 128): 
        c.R(x, 30, 28, 176, (200, 180, 150)); c.R(x, 30, 28, 4, (240, 224, 196)); c.R(x + 2, 34, 3, 172, (230, 214, 184)); c.R(x + 24, 34, 3, 172, (150, 130, 104))
    for lx in (60, 100):
        c.R(lx, 0, 1, 30, (60, 50, 40)); c.d.polygon([(lx - 12, 44), (lx + 12, 44), (lx + 6, 30), (lx - 6, 30)], fill=(255, 214, 120)); c.light(lx, 50, 40, 36, (255, 214, 140), .7)
    bg.planks(c, 0, 206, WW, 90, (130, 92, 64), seed=47, pw=9); c.R(0, 204, WW, 3, GOLD)
    c.R(46, 220, 68, 70, (150, 24, 44)); c.R(46, 220, 68, 2, (230, 90, 100))


def royal_a(t, u):
    c = Canvas(vgrad([(0, '#000000'), (1, '#000000')])); _env_hall(c, t)
    bg.sign2(c, 80, 70, 'SOCIEDAD REAL', (255, 230, 120), 8, plate=(60, 20, 36))
    for i, f in enumerate(('prod1', 'prod2', 'mom', 'dad', 'kid_c')):
        place(c, rpg(f, int(t * 3 + i) % 2 if int(t * 2) % 2 else 0), 18 + i * 32, 262, sh=False)
    seated(c, 'hawking', 80, 236, 'rpg', t=t)
    c.amb = (1.0, .96, .96); c.vig = .65
    return c.render()


def royal_b(t, u):
    c = Canvas(vgrad([(0, '#000000'), (1, '#000000')])); _env_hall(c, t)
    PR.keep(c, PR.frame_portrait(), 63, 80)
    bg.sign2(c, 80, 64, 'NEWTON', (255, 230, 120), 16, plate=(60, 20, 36))
    seated(c, 'hawking', 80, 262, 'bat', t=t)
    c.amb = (1.0, .96, .96); c.vig = .65
    return c.render()


def royal_c(t, u):
    c = Canvas(vgrad([(0, '#000000'), (1, '#000000')])); _env_hall(c, t)
    PR.keep(c, PR.frame_portrait(), 63, 80)
    bg.sign2(c, 80, 64, '1979', (255, 230, 120), 24, plate=(60, 20, 36))
    seated(c, 'hawking', 80, 262, 'bat', t=t)
    c.amb = (1.0, .96, .96); c.vig = .65
    return c.render()


royal = phased(royal_a, royal_b, royal_c, cuts=(.42, .72))


# ============================================================ 11. 1985: neumonía, sin voz
def _env_hosp(c, t, beat=1.0):
    bg.hospital_wall(c, t)
    c.R(100, 54, 46, 56, (96, 130, 134)); c.R(102, 56, 42, 52, (24, 36, 90)); c.R(122, 56, 2, 52, (96, 130, 134)); c.R(102, 82, 42, 2, (96, 130, 134))
    PR.keep(c, PR.monitor_ecg(), 14, 110)
    xs = 18
    pts = []
    for i in range(30):
        ph = (t * 2 + i * .08) % 1; y = 128 - (8 if (beat and ph < .12) else 0) + (5 if (beat and .12 <= ph < .2) else 0)
        pts.append((xs + i, y))
    if beat: c.d.line(pts, fill=(80, 255, 140))
    else: c.d.line([(18, 128), (48, 128)], fill=(255, 80, 80))
    c.R(150, 120, 2, 86, (190, 196, 214)); c.R(144, 120, 14, 4, (190, 196, 214)); c.R(145, 124, 12, 18, (200, 230, 250))


def hosp_a(t, u):
    c = Canvas(vgrad([(0, '#000000'), (1, '#000000')])); _env_hosp(c, t)
    PR.keep(c, PR.hospital_bed(), 44, 212); place(c, rpg('hawking', 0), 72, 226, sh=False)
    place(c, rpg('nurse', 0), 132, 238)
    c.amb = (1.0, 1.0, 1.02); c.vig = .65
    return c.render()


def hosp_b(t, u):
    c = Canvas(vgrad([(0, '#000000'), (1, '#000000')])); _env_hosp(c, t, beat=int(t * 2) % 5 != 0)
    place(c, bat('nurse', 'hold'), 112, 252)
    bg.sign2(c, 80, 64, '1985', (255, 90, 90), 24, plate=(40, 10, 24))
    c.light(40, 126, 40, 30, (80, 255, 140), .5); c.amb = (.9, .96, 1.0); c.vig = .75
    return c.render()


def hosp_c(t, u):
    c = Canvas(vgrad([(0, '#000000'), (1, '#000000')])); _env_hosp(c, t)
    c.light(120, 90, 80, 80, (255, 230, 160), .5 + .4 * u)
    seated(c, 'hawking', 80, 262, 'bat', t=t)
    c.amb = (1.0, 1.0, 1.0); c.vig = .6
    return c.render()


hosp = phased(hosp_a, hosp_b, hosp_c, cuts=(.3, .56))


# ============================================================ 12. la voz de la computadora
def _env_study(c, t):
    bg.wallpaper(c, 0, 0, WW, 206, (50, 56, 100), (44, 50, 92), (80, 90, 150))
    bg.shelf(c, 6, 40, 40, 90, seed=81, rows=3)
    bg.window(c, 112, 50, 40, 60, t=t, curtain=(120, 90, 180), rain=False, seed=7)
    bg.planks(c, 0, 206, WW, 90, (100, 74, 56), seed=83, pw=9); c.R(0, 204, WW, 3, (50, 30, 24))
    c.R(18, 186, 124, 6, (130, 84, 54)); c.R(18, 186, 124, 2, (200, 150, 100)); c.R(24, 192, 112, 20, (96, 60, 40))


def _screen(c, x, y, w, h, text, t):
    c.R(x, y, w, h, (6, 24, 18)); n = int((t * 7) % (len(text) + 8))
    wtext(c, x + 3, y + 4, text[:n] + ('_' if int(t * 4) % 2 else ' '), (120, 255, 170), 8, outline=None) if False else bg.wtext(c, x + 3, y + 4, text[:n] + ('_' if int(t * 4) % 2 else ' '), (120, 255, 170), 8, outline=None)


def voice_a(t, u):
    c = Canvas(vgrad([(0, '#000000'), (1, '#000000')])); _env_study(c, t)
    seated(c, 'hawking', 56, 236, 'rpg', t=t)
    PR.keep(c, PR.computer_old(), 88, 148); _screen(c, 93, 151, 30, 14, 'HOLA', t)
    c.amb = (1.0, .98, 1.04); c.vig = .65
    return c.render()


def voice_b(t, u):
    c = Canvas(vgrad([(0, '#000000'), (1, '#000000')])); _env_study(c, t)
    PR.keep(c, PR.computer_old(), 96, 146); _screen(c, 101, 149, 30, 14, 'HOLA MUNDO', t)
    seated(c, 'hawking', 56, 262, 'bat', t=t)
    for i in range(3):
        ph = (t * 1.2 + i * .33) % 1; c.ed.arc([100 - ph * 30, 100 - ph * 30, 100 + ph * 30, 100 + ph * 30], 300, 60, fill=(120, 255, 170, int(220 * (1 - ph))), width=2)
    c.amb = (1.0, .98, 1.04); c.vig = .65
    return c.render()


def voice_c(t, u):
    c = Canvas(vgrad([(0, '#000000'), (1, '#000000')])); _env_study(c, t)
    PR.keep(c, PR.computer_old(), 40, 120); _screen(c, 45, 123, 30, 14, 'HOLA MUNDO', t)
    c.R(80, 100, 70, 80, (6, 24, 18)); c.R(80, 100, 70, 1, (60, 120, 90))
    bg.wtext(c, 84, 106, 'ASI SE HABLA', (120, 255, 170), 8, outline=None); bg.wtext(c, 84, 118, 'PALABRA POR', (120, 255, 170), 8, outline=None); bg.wtext(c, 84, 130, 'PALABRA', (120, 255, 170), 8, outline=None)
    seated(c, 'hawking', 80, 262, 'bat', t=t)
    c.amb = (1.0, .98, 1.04); c.vig = .65
    return c.render()


voice = phased(voice_a, voice_b, voice_c)


# ============================================================ 13. el libro y los 10 millones
def _env_books(c, t):
    bg.wallpaper(c, 0, 0, WW, 206, (176, 74, 120), (164, 66, 110), (210, 120, 150))
    bg.shelf(c, 4, 70, 36, 110, seed=61, rows=4); bg.shelf(c, 120, 70, 36, 110, seed=62, rows=4)
    for yy in range(206, 296, 10):
        for xx in range(-(yy // 10 % 2) * 10, WW, 20): c.R(xx, yy, 10, 10, (236, 226, 206)); c.R(xx + 10, yy, 10, 10, (150, 70, 80))
    c.R(0, 204, WW, 3, (90, 50, 40))


def books_a(t, u):
    c = Canvas(vgrad([(0, '#000000'), (1, '#000000')])); _env_books(c, t)
    for i, x in enumerate((46, 80, 114)): PR.keep(c, PR.book_stack(3 + i % 2), x - 17, 196 - (3 + i % 2) * 8 + 24)
    for i, f in enumerate(('kid_a', 'kid_b', 'mom', 'dad', 'alice')): place(c, rpg(f, int(t * 3 + i) % 2), 16 + i * 32 + (t * 4) % 6, 250, sh=False)
    seated(c, 'hawking', 80, 232, 'rpg', t=t)
    for i in range(30):
        ph = (t * .5 + i * .033) % 1; c.R((i * 53 + math.sin(t * 3 + i) * 6) % 150 + 4, ph * 280, 2, 3, ((255, 90, 120), (90, 220, 255), (255, 230, 90), (140, 255, 140))[i % 4])
    c.amb = (1.03, .98, .98); c.vig = .55
    return c.render()


def books_b(t, u):
    c = Canvas(vgrad([(0, '#000000'), (1, '#000000')])); _env_books(c, t)
    c.R(100, 90, 52, 40, (30, 26, 30)); c.R(102, 92, 48, 34, (255, 214, 60)); bg.wtext(c, 126, 100, 'SIMPSON', (60, 30, 90), 8, outline=None, center=True)
    c.d.ellipse([116, 106, 136, 124], fill=(255, 224, 80), outline=(160, 110, 30))
    PR.keep(c, PR.book_stack(4), 108, 178)
    seated(c, 'hawking', 56, 262, 'bat', t=t)
    c.amb = (1.03, .98, .98); c.vig = .55
    return c.render()


books = phased(books_a, books_b, cuts=(.5,))


# ============================================================ 14. 55 años
def _env_road(c, t, k=0.0):
    c.im.paste(Image.fromarray(vgrad([(0, '#1a1a6a'), (.4, '#c0408a'), (.6, '#ff9a50'), (.78, '#ffd080'), (1, '#3a2438')]).astype('uint8')), (0, 0))
    bg.skyline(c, 0, 176, cols=((86, 46, 110), (104, 58, 128)), seed=21, lit=.2, t=t)
    c.d.ellipse([60, 120 - 30 * k, 100, 160 - 30 * k], fill=(255, 244, 180))
    c.R(0, 190, WW, 110, (70, 50, 70)); c.R(0, 190, WW, 3, (230, 170, 120))
    for x in range(0, WW, 28): c.R(x + int(t * 20) % 28, 246, 14, 2, (240, 220, 110))


def years_a(t, u):
    c = Canvas(vgrad([(0, '#000000'), (1, '#000000')])); _env_road(c, t)
    bg.sign2(c, 80, 62, 'SIEMPRE HAY ALGO', (255, 230, 120), 8, plate=(50, 24, 60)); bg.sign2(c, 80, 84, 'QUE PUEDES HACER', (255, 230, 120), 8, plate=(50, 24, 60))
    seated(c, 'hawking', 30 + 100 * u, 240, 'rpg', t=t)
    c.amb = (1.0, .96, .98); c.vig = .6
    return c.render()


def years_b(t, u):
    c = Canvas(vgrad([(0, '#000000'), (1, '#000000')])); _env_road(c, t, u)
    yr = int(1963 + 55 * ease(u))
    for i in range(8):
        ph = (t * .6 + i * .125) % 1; PR.keep(c, PR.calendar_page(), 6 + (i * 41) % 130, int(ph * 250) - 20)
    seated(c, 'hawking', 80, 262, 'bat', t=t)
    bg.sign2(c, 80, 62, str(yr), (255, 230, 120), 24, plate=(50, 24, 60))
    c.amb = (1.0, .96, .98); c.vig = .6
    return c.render()


years = phased(years_a, years_b, cuts=(.55,))


# ============================================================ 16. mira hacia las estrellas
def stars_a(t, u):
    c = _sky('#050824', '#16146a', '#3a1a5a'); _env_sky(c, t)
    for i in range(6): place(c, rpg(('kid_a', 'kid_b', 'mom', 'dad', 'kid_c', 'alice')[i], 0), 20 + i * 26, 270, sh=False)
    seated(c, 'hawking', 80, 240, 'rpg', t=t)
    bg.sign2(c, 80, 66, '2012', (255, 230, 120), 24, plate=(30, 24, 80))
    c.amb = (.96, .96, 1.08); c.vig = .6
    return c.render()


def stars_b(t, u):
    c = _sky('#050824', '#16146a', '#3a1a5a'); _env_space(c, t); bg.hill(c, 226, (14, 12, 34))
    seated(c, 'hawking', 80, 262, 'bat', t=t)
    for i in range(5): bg.shooting_star(c, t, i, 2.5)
    c.amb = (.96, .96, 1.08); c.vig = .6
    return c.render()


def stars_c(t, u):
    c = _sky('#050824', '#16146a', '#3a1a5a'); _env_space(c, t); bg.hill(c, 236, (14, 12, 34))
    bg.nebula(c, t, 7)
    seated(c, 'hawking', 80, 270, 'bat', t=t)
    for i in range(4): bg.shooting_star(c, t, i + 5, 2.0)
    c.amb = (.96, .96, 1.08); c.vig = .6
    return c.render()


starry = phased(stars_a, stars_b, stars_c, cuts=(.34, .67))


# ============================================================ 17. final: tú, bajo el mismo cielo
def final_a(t, u):
    c = _sky(); _env_sky(c, t)
    place(c, rpg('you', int(t * 2) % 2 if u < .15 else 0), 66, 232)
    c.light(66, 190, 60, 50, (140, 170, 255), .35); c.amb = (.92, .94, 1.1); c.vig = .65
    return c.render()


def final_b(t, u):
    c = _sky(); _env_sky(c, t)
    place(c, bat('you', 'stand'), 70, 252)
    c.amb = (.92, .94, 1.1); c.vig = .65
    return c.render()


final = phased(final_a, final_b, cuts=(.5,))
