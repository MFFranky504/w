"""Video largo nº2 «5 personas a las que les dijeron que no» (320x180 → 1920x1080). Reutiliza scenes19 (fondos y detalles).
Cada kit es una lista de planos fn(T, tl, j): T = s desde que empezó el escenario, tl = s desde que empezó el plano, j = nº de frase dentro del escenario."""
import math
from lib import WW, WH, stars, ease
import gba as G
import bg
import scenes18 as S
import scenes19 as S19
from scenes19 import (cv, chibi, fin, put, face, bubble, confetti, FLY, room, label, stamp, dust, clock, plant, steam, birds, cloud_window, lamp_cone)

CAST5 = ('f_spiel', 'f_seuss', 'f_dyson', 'f_blake', 'f_honda')
NUMS = (('5.127', 'INTENTOS FALLIDOS'), ('27', 'EDITORIALES DIJERON NO'), ('$5.000', 'TODOS SUS AHORROS'))


def _cards(c, x0, y0, n, T, col=(250, 246, 236), cols=8, w=18, h=12, gap=4):
    for i in range(n):
        x = x0 + (i % cols) * (w + gap); y = y0 - (i // cols) * (h + gap)
        c.R(x, y, w, h, col); c.R(x, y, w, 1, (200, 190, 170)); c.R(x + 3, y + 4, w - 6, 1, (170, 60, 60)); c.R(x + 3, y + 7, w - 9, 1, (120, 120, 130))


# ================================================================ 0 · gancho
def _n5(T, tl, j):
    if j <= 2:
        c = cv('#140a20', '#2a1448'); stars(c, T, 70, 3, 130)
        n, sub = NUMS[j]; k = ease(min(1, tl / .35))
        bg.wtext(c, 160, 40 + int((1 - k) * -30), n, (255, 216, 74), size=64, center=True, emissive=True)
        label(c, 160, 118, sub, (255, 255, 255), 12)
        for i in range(10): c.R(20 + i * 30, 150 + int(math.sin(T * 3 + i) * 3), 16, 3, (139, 92, 246))
        return fin(c, 'dark', (.95, .95, 1.05), .5)
    c = cv(); S.world_day(c, T, T * 10, sunset=True); birds(c, T, 24, 4, 3)
    if j in (3, 4):
        for i, w in enumerate(CAST5): chibi(c, w, 40 + i * 60, FLY + 4, T + i * .3, walk=True, f=.8)
    elif j == 5:
        face(c, CAST5[int(T * 1.3) % 5], 'sad', T, sc=1.7); stamp(c, 240, 30, 'NO', tl, size=34)
    else:
        for i, w in enumerate(CAST5): chibi(c, w, 40 + i * 60, FLY + 4, T + i * .3, f=.8, bounce=1.5)
    return fin(c, 'day', (1.05, 1, .95), .4)


n5 = [_n5]


# ================================================================ 1 · Spielberg
def _school(c, t):
    room(c, (110, 90, 70), ((70, 80, 110), (62, 72, 100), (96, 110, 150)))
    cloud_window(c, 20, 28, 60, 62, t); clock(c, 160, 30, t, 9); plant(c, 300, 132, t); dust(c, t, 16, 31, (0, 0, WW, 130), (255, 244, 220))
    c.R(110, 98, 100, 6, (90, 60, 40)); c.R(116, 104, 4, 36, (70, 46, 32)); c.R(200, 104, 4, 36, (70, 46, 32))
    c.R(240, 40, 50, 36, (240, 236, 224)); label(c, 265, 54, 'ESCUELA', (60, 60, 90), 7); label(c, 265, 64, 'DE CINE', (60, 60, 90), 7)


def _s_usc_a(T, tl, j):
    c = cv(); _school(c, T)
    chibi(c, 'f_spiel', 70, FLY + 4, T, f=.9); chibi(c, 'todd', 250, FLY + 6, T + .4, f=.85, flip=True)
    c.R(140, 90, 24, 14, (250, 248, 236)); c.R(143, 94, 18, 1, (90, 90, 100)); c.R(143, 98, 12, 1, (90, 90, 100))
    if j >= 1: stamp(c, 152, 54, 'RECHAZADO', tl, size=12)
    return fin(c, 'day', (1, .97, .95), .45)


def _s_usc_b(T, tl, j):
    c = cv(); _school(c, T); face(c, 'f_spiel', 'sad' if j else 'worry', T, sc=1.7)
    if j == 1 and tl > .6: label(c, 240, 24, 'POR SUS NOTAS', (255, 216, 74), 10)
    return fin(c, 'dark', (1, .97, .95), .5)


def _s_usc_c(T, tl, j):
    c = cv(); S.world_day(c, T, T * 8); u = ease(min(1, tl / 3))
    c.R(200, 56, 90, 70, (150, 130, 110)); c.R(200, 50, 90, 8, (110, 90, 76)); label(c, 245, 62, 'UNIVERSIDAD DE', (255, 255, 255), 6); label(c, 245, 72, 'LONG BEACH', (255, 216, 74), 8)
    c.R(228, 96, 18, 30, (70, 50, 40))
    chibi(c, 'f_spiel', 60 + 130 * u, FLY + 4, T, walk=u < 1, f=.9)
    return fin(c, 'day', (1.03, 1, .96), .35)


s_usc = [_s_usc_a, _s_usc_b, _s_usc_c]


def _studio_lot(c, t):
    S.world_day(c, t, t * 6)
    for i, x in enumerate((20, 130, 240)): c.R(x, 66, 70, 62, (200 - i * 20, 180 - i * 15, 150)); c.R(x, 60, 70, 8, (120, 90, 70)); c.R(x + 26, 96, 18, 32, (70, 50, 40)); c.R(x + 8, 78, 12, 12, (150, 190, 230))
    c.R(120, 30, 80, 14, (30, 36, 70)); label(c, 160, 33, 'UNIVERSAL', (255, 255, 255), 9)


def _s_uni_a(T, tl, j):
    c = cv(); _studio_lot(c, T); u = ease(min(1, tl / 3.2))
    chibi(c, 'f_spiel', 30 + 130 * u, FLY + 4, T, walk=u < 1, f=.9); chibi(c, 'senora', 270, FLY + 6, T, f=.8, flip=True)
    label(c, 160, 150 if False else 20, '21 AÑOS', (255, 216, 74), 12)
    return fin(c, 'day', (1.03, 1, .96), .35)


def _edit_room(c, t):
    room(c, (80, 64, 52), ((60, 56, 70), (54, 50, 64), (80, 76, 96)))
    clock(c, 160, 28, t, 8)
    for i in range(7):                                                                          # tiras de película colgadas
        x = 40 + i * 38; c.R(x, 0, 2, 50 + (i * 11) % 24, (30, 26, 34))
        for k in range(5 + (i * 3) % 4): c.R(x - 3, 8 + k * 9, 8, 6, (250, 220, 150)); c.R(x - 3, 8 + k * 9, 8, 1, (60, 50, 50))
    c.R(90, 100, 140, 8, (70, 46, 34)); c.R(90, 108, 140, 34, (50, 34, 26))
    c.R(120, 80, 36, 20, (30, 30, 40)); c.R(122, 82, 32, 16, (40, 90 + int(math.sin(t * 3) * 20), 120))
    for r_ in (190, 215): c.d.ellipse([r_, 74, r_ + 22, 96], fill=(40, 40, 52)); c.d.ellipse([r_ + 7, 81, r_ + 15, 89], fill=(120, 120, 140))
    dust(c, t, 16, 32, (0, 0, WW, 120), (255, 236, 180))


def _s_uni_b(T, tl, j):
    c = cv(); _edit_room(c, T); chibi(c, 'f_spiel', 160, FLY + 6, T, f=.95)
    return fin(c, 'dark', (1, .97, .95), .5)


def _s_uni_c(T, tl, j):
    c = cv('#140a20', '#24123a'); stars(c, T, 60, 3, 130)
    label(c, 160, 40, '«AMBLIN»', (255, 216, 74), 26); label(c, 160, 80, '1968  ·  26 MINUTOS', (255, 255, 255), 12)
    for i in range(8): c.R(20 + i * 38, 120, 30, 20, (30, 26, 34)); c.R(24 + i * 38, 124, 22, 12, (250, 220, 150) if (i + int(T * 3)) % 2 else (200, 170, 110))
    return fin(c, 'dark', (.95, .95, 1.05), .5)


s_uni = [_s_uni_a, _s_uni_b, _s_uni_c, _s_uni_b]


def _s_duel_a(T, tl, j):
    c = cv(); _studio_lot(c, T)
    chibi(c, 'f_spiel', 90, FLY + 4, T, f=.95); chibi(c, 'dueno', 230, FLY + 4, T + .3, f=.9, flip=True)
    c.R(140, 100, 24, 16, (250, 248, 236)); c.R(143, 104, 18, 1, (90, 90, 100)); c.d.ellipse([150, 108, 158, 116], fill=(190, 40, 50))
    if tl > .5: stamp(c, 152, 60, 'CONTRATO', tl, col=(60, 140, 90), size=12)
    return fin(c, 'day', (1.03, 1, .96), .4)


def _truck(c, x, y, t):
    c.R(x, y - 26, 44, 26, (180, 60, 50)); c.R(x + 44, y - 18, 20, 18, (150, 40, 36)); c.R(x + 48, y - 15, 12, 7, (150, 200, 230))
    for wx in (x + 10, x + 34, x + 54): c.d.ellipse([wx - 6, y - 6, wx + 6, y + 6], fill=(24, 22, 28)); c.d.ellipse([wx - 2, y - 2, wx + 2, y + 2], fill=(150, 150, 160))


def _s_duel_b(T, tl, j):
    c = cv(); G.sky(c, [(0, (230, 150, 90)), (1, (250, 220, 170))], 0, 110, bands=6)
    G.mountains(c, 110, 24, (160, 100, 70), seed=4); c.R(0, 110, WW, 70, (190, 150, 100)); c.R(0, 134, WW, 20, (70, 66, 76))
    for i in range(10): c.R((i * 40 - int(T * 160)) % 360 - 20, 144, 18, 2, (240, 230, 180))
    _truck(c, int((T * 40) % 420) - 100, 138, T)
    label(c, 160, 24, 'DUEL  ·  1971', (255, 255, 255), 14)
    return fin(c, 'day', (1.08, 1, .9), .35)


def _s_duel_c(T, tl, j):
    c = cv(); S.world_day(c, T, 60); confetti(c, T, 40, 6, 130)
    face(c, 'f_spiel_a', 'smile', T, sc=1.7)
    if tl > .4: label(c, 240, 26, 'TÍTULO 2002', (255, 216, 74), 12)
    return fin(c, 'day', (1.05, 1, .95), .4)


s_duel = [_s_duel_a, _s_duel_b, _s_duel_c, _s_duel_c]


# ================================================================ 2 · Dr. Seuss
def _nycity(c, t, night=True):
    G.sky(c, [(0, (14, 14, 50)), (1, (120, 70, 100))], 0, 110, bands=6); stars(c, t, 30, 5, 80)
    bg.skyline(c, 90, 110, cols=((30, 26, 70), (44, 36, 90)), seed=21, lit=.7, t=t, wmin=6, wmax=14, hmin=16, hmax=60)
    c.R(0, 110, WW, 70, (40, 36, 56)); c.R(0, 150, WW, 30, (60, 56, 72))
    for k in (60, 170, 280): c.R(k, 70, 2, 60, (30, 30, 40)); c.d.ellipse([k - 4, 64, k + 6, 74], fill=(255, 220, 150)); c.light(k, 70, 36, 26, (255, 210, 140), .35)


def _z_walk_a(T, tl, j):
    c = cv('#2a1c18', '#44302a'); room(c, (80, 60, 48), ((70, 50, 56), (62, 44, 50), (96, 70, 78)))
    c.R(60, 106, 200, 6, (90, 62, 44)); c.R(70, 112, 4, 28, (70, 48, 34)); c.R(246, 112, 4, 28, (70, 48, 34))
    _cards(c, 90, 100, 14 if j else 8, T, cols=7, w=20, h=6, gap=1)
    chibi(c, 'f_seuss', 160, FLY + 6, T, f=.95)
    return fin(c, 'dark', (.95, .93, 1), .55)


def _z_walk_b(T, tl, j):
    c = cv('#140a20', '#24123a'); stars(c, T, 60, 3, 130)
    n = min(27, int(tl * 12) + 1); bg.wtext(c, 160, 36, str(n), (255, 216, 74), size=64, center=True, emissive=True)
    label(c, 160, 112, 'EDITORIALES DIJERON NO', (255, 255, 255), 11)
    _cards(c, 20, 160, n, T, cols=14, w=16, h=8, gap=5)
    return fin(c, 'dark', (.95, .95, 1.05), .5)


def _z_walk_c(T, tl, j):
    c = cv(); _nycity(c, T); u = ease(min(1, tl / 4))
    c.R(222, 130, 16, 22, (90, 60, 46)); c.R(224, 128, 12, 3, (60, 40, 30))                                         # barril
    for i in range(6): ph = (T * 1.6 + i * .17) % 1; c.d.ellipse([228 + math.sin(ph * 6 + i) * 3 - 3, 126 - ph * 16 - 3, 228 + math.sin(ph * 6 + i) * 3 + 3, 126 - ph * 16 + 3], fill=(255, 150 + int(ph * 60), 60))
    c.light(230, 130, 40, 30, (255, 170, 80), .5)
    chibi(c, 'f_seuss', 30 + 150 * u, FLY + 14, T, walk=u < 1, f=.95); c.R(int(30 + 150 * u) - 4, FLY - 14, 10, 8, (250, 246, 236))
    return fin(c, 'dark', (.95, .93, 1.1), .55)


z_walk = [_z_walk_a, _z_walk_b, _z_walk_c, _z_walk_c]


def _z_meet_a(T, tl, j):
    c = cv(); _nycity(c, T)
    chibi(c, 'f_seuss', 90 + int(min(1, tl / 1.5) * 30), FLY + 14, T, f=.95); chibi(c, 'todd', 230 - int(min(1, tl / 1.5) * 30), FLY + 14, T + .3, f=.95, flip=True)
    if j == 0 and tl > 1.2: label(c, 160, 40, '¡TÚ!', (255, 216, 74), 18)
    if j == 1: c.R(222, 128, 14, 10, (120, 80, 50)); label(c, 160, 24, 'EDITOR INFANTIL', (255, 255, 255), 10)
    return fin(c, 'dark', (.95, .93, 1.1), .55)


def _z_meet_b(T, tl, j):
    c = cv(); _nycity(c, T); face(c, 'todd' if j == 2 else 'f_seuss', 'smile' if j == 2 else 'n', T, sc=1.7)
    if j == 2 and tl > .3: bubble(c, 180, 20, 110, 34, tail=(-20, 14)); label(c, 235, 32, '«ENSEÑAMELO»', (200, 40, 60), 10)
    return fin(c, 'dark', (.95, .93, 1.1), .55)


z_meet = [_z_meet_a, _z_meet_b, _z_meet_b]


def _z_book_a(T, tl, j):
    c = cv('#28183c', '#4a2c6a'); stars(c, T, 50, 3, 130); w = abs(math.cos(T * 2))
    bx = 160 - int(34 * w); c.R(bx, 46, int(68 * w) + 2, 84, (200, 60, 70)); c.R(bx, 46, int(68 * w) + 2, 4, (240, 120, 120)); c.R(bx + 4, 60, max(1, int(60 * w)), 1, (255, 240, 200))
    label(c, 160, 140, '1937', (255, 216, 74), 22); label(c, 160, 10, 'MULBERRY STREET', (255, 255, 255), 10)
    return fin(c, 'dark', (.95, .95, 1.05), .5)


def _z_book_b(T, tl, j):
    c = cv(); _nycity(c, T)
    c.R(40, 106, 90, 40, (150, 90, 70)); c.R(40, 100, 90, 8, (110, 64, 50)); label(c, 85, 112, 'TINTORERIA', (255, 255, 255), 8)
    chibi(c, 'f_seuss', 230, FLY + 14, T, f=.95)
    if tl > 1: label(c, 160, 30, 'LA OTRA ACERA', (255, 216, 74), 12)
    return fin(c, 'dark', (.95, .93, 1.1), .55)


z_book = [_z_book_a, _z_book_b]


# ================================================================ 3 · Dyson
def _shop(c, t):
    room(c, (100, 80, 60), ((90, 90, 96), (82, 82, 90), (120, 120, 130)))
    cloud_window(c, 240, 28, 60, 56, t); clock(c, 130, 28, t, 8); dust(c, t, 22, 41, (0, 0, WW, 130), (255, 244, 220))
    c.R(20, 104, 150, 8, (90, 62, 44)); c.R(26, 112, 4, 28, (70, 48, 34)); c.R(160, 112, 4, 28, (70, 48, 34))
    bg.shelf(c, 190, 30, 40, 70, seed=6)


def _cyclone(c, x, y, t):
    c.R(x - 12, y - 30, 24, 30, (220, 210, 190)); c.R(x - 12, y - 30, 24, 2, (250, 240, 220))
    for i in range(6): a = t * 6 + i; c.d.ellipse([x + math.cos(a) * 6 - 1, y - 14 + math.sin(a) * 8 - 1, x + math.cos(a) * 6 + 2, y - 14 + math.sin(a) * 8 + 2], fill=(150, 150, 170))


def _d_garage_a(T, tl, j):
    c = cv(); _shop(c, T)
    chibi(c, 'f_dyson', 120, FLY + 4, T, f=.95)
    if j == 0: c.R(210, 120, 24, 16, (110, 110, 120)); c.R(226, 100, 3, 24, (80, 80, 90)); label(c, 222, 90, 'BOLSA LLENA', (200, 40, 60), 8)
    else: _cyclone(c, 230, 130, T)
    return fin(c, 'day', (1, .98, .95), .45)


def _d_garage_b(T, tl, j):
    c = cv(); _shop(c, T); face(c, 'f_dyson', 'worry' if j < 2 else 'n', T, sc=1.7)
    if j == 1 and tl > .4: label(c, 240, 24, '1978', (255, 216, 74), 16)
    return fin(c, 'dark', (1, .98, .95), .5)


d_garage = [_d_garage_a, _d_garage_b, _d_garage_a]


def _d_count_a(T, tl, j):
    c = cv(); _shop(c, T); chibi(c, 'f_dyson', 90, FLY + 4, T, f=.9)
    for i in range(min(40, int(tl * 10) + 6 + j * 8)): _cyclone(c, 150 + (i % 10) * 15, 140 - (i // 10) * 24, T + i)
    return fin(c, 'dark', (.98, .98, 1), .5)


def _d_count_b(T, tl, j):
    c = cv('#140a20', '#2a1448'); stars(c, T, 60, 3, 130)
    n = int(5127 * ease(min(1, tl / 2.6))); bg.wtext(c, 160, 46, f'{n:,}'.replace(',', '.'), (255, 216, 74), size=58, center=True, emissive=True)
    label(c, 160, 116, 'PROTOTIPOS', (255, 255, 255), 14)
    return fin(c, 'dark', (.95, .95, 1.05), .5)


def _d_count_c(T, tl, j):
    c = cv(); _shop(c, T); face(c, 'f_dyson', 'sad' if j < 3 else 'smile', T, sc=1.7)
    return fin(c, 'dark', (1, .98, .95), .5)


d_count = [_d_count_a, _d_count_c, _d_count_b, _d_count_a, _d_count_c]


def _d_shop_a(T, tl, j):
    c = cv(); room(c, (110, 96, 80), ((60, 80, 110), (54, 72, 100), (86, 110, 150))); dust(c, T, 14, 7, (0, 0, WW, 130), (255, 244, 220))
    c.R(110, 90, 100, 50, (240, 236, 226)); c.R(110, 90, 100, 3, (200, 190, 170)); label(c, 160, 108, 'LICENCIA', (200, 40, 60), 14)
    chibi(c, 'f_dyson', 60, FLY + 4, T, f=.9); chibi(c, 'dueno', 260, FLY + 4, T, f=.9, flip=True)
    for i in range(5): c.d.ellipse([130 + i * 16, 60 - int(abs(math.sin(T * 3 + i)) * 6), 142 + i * 16, 72 - int(abs(math.sin(T * 3 + i)) * 6)], fill=(250, 200, 70))
    return fin(c, 'day', (1, .98, .95), .45)


def _d_shop_b(T, tl, j):
    c = cv(); S.world_day(c, T, 120); c.R(90, 64, 140, 66, (120, 130, 150)); c.R(90, 58, 140, 8, (70, 80, 110))
    c.R(150, 80, 20, 50, (230, 240, 250)); c.R(110, 80, 28, 50, (180, 200, 230)); c.R(182, 80, 28, 50, (180, 200, 230))
    label(c, 160, 70, 'FÁBRICA PROPIA', (255, 255, 255), 9)
    label(c, 160, 20, '1993', (255, 216, 74), 24); confetti(c, T, 30, 4, 120)
    chibi(c, 'f_dyson', 250, FLY + 4, T, f=.9, bounce=2)
    return fin(c, 'day', (1.05, 1, .95), .4)


d_shop = [_d_shop_a, _d_shop_b]


# ================================================================ 4 · Sara Blakely
def _office_fax(c, t):
    room(c, (110, 96, 84), ((120, 100, 110), (110, 90, 100), (150, 126, 138)))
    cloud_window(c, 20, 28, 56, 60, t); clock(c, 160, 28, t, 8); plant(c, 300, 132, t)
    for i in range(4): c.R(100 + i * 34, 100, 28, 18, (226, 226, 232)); c.R(104 + i * 34, 94, 20, 6, (200, 200, 210)); c.R(106 + i * 34, 106, 14, 1, (90, 90, 100)); c.R(100 + i * 34, 118, 28, 22, (200, 200, 210))
    dust(c, t, 14, 51, (0, 0, WW, 130), (255, 244, 230))


def _b_fax_a(T, tl, j):
    c = cv(); _office_fax(c, T); chibi(c, 'f_blake', 60, FLY + 4, T, f=.95)
    if j == 1:
        c.R(250, 112, 22, 28, (200, 230, 240)); c.R(248, 108, 26, 5, (180, 160, 120)); label(c, 261, 100, '$5.000', (255, 216, 74), 10)
    return fin(c, 'day', (1, .98, .96), .45)


def _b_fax_b(T, tl, j):
    c = cv(); _office_fax(c, T); face(c, 'f_blake', 'smile' if j == 0 else 'n', T, sc=1.7)
    return fin(c, 'day', (1, .98, .96), .45)


b_fax = [_b_fax_a, _b_fax_b]


def _mill(c, t):
    room(c, (90, 90, 100), ((100, 108, 120), (90, 98, 110), (130, 140, 156)))
    for i in range(3):
        x = 30 + i * 100; c.R(x, 96, 70, 30, (70, 76, 90)); c.R(x, 90, 70, 6, (50, 56, 70))
        for k in range(10): c.R(x + 4 + k * 6, 100, 2, 22, (240, 200 + (k % 3) * 10, 190))
        c.d.ellipse([x + 30, 70 + int(math.sin(t * 3 + i) * 2), x + 44, 84 + int(math.sin(t * 3 + i) * 2)], fill=(200, 200, 210))
    dust(c, t, 14, 52, (0, 0, WW, 130), (255, 244, 230))


def _b_mill_a(T, tl, j):
    c = cv(); _mill(c, T)
    chibi(c, 'f_blake', 60, FLY + 6, T, f=.9)
    for i, x in enumerate((180, 220, 260)): chibi(c, ('dueno', 'abuelo', 'todd')[i], x, FLY + 6, T + i * .4, f=.85, flip=True)
    if j == 0 and tl > .8: stamp(c, 220, 40, 'EN VANO', tl, size=14)
    return fin(c, 'day', (.98, .98, 1), .45)


def _b_mill_b(T, tl, j):
    c = cv(); _mill(c, T); face(c, 'f_blake', 'worry' if j == 0 else 'smile', T, sc=1.7)
    return fin(c, 'dark', (.98, .98, 1), .5)


b_mill = [_b_mill_a, _b_mill_b]


def _store(c, t):
    room(c, (130, 110, 100), ((150, 130, 140), (140, 120, 130), (180, 160, 170)))
    for i in range(3):
        x = 30 + i * 100; c.R(x, 60, 60, 50, (236, 230, 226)); c.R(x, 60, 60, 4, (200, 180, 160)); c.R(x + 8, 74, 12, 30, (60, 50, 60)); c.R(x + 28, 74, 12, 30, (90, 70, 80))
    dust(c, t, 16, 53, (0, 0, WW, 130), (255, 244, 230))


def _b_neiman_a(T, tl, j):
    c = cv(); _store(c, T); u = ease(min(1, tl / 3)); chibi(c, 'f_blake', 40 + 110 * u, FLY + 4, T, walk=u < 1, f=.9)
    c.R(250, 112, 40, 28, (240, 236, 226)); label(c, 270, 120, 'DALLAS', (60, 60, 90), 8)
    if j == 0: label(c, 160, 20, '10 MINUTOS', (255, 216, 74), 14)
    return fin(c, 'day', (1, .98, .98), .45)


def _b_neiman_b(T, tl, j):
    c = cv(); _store(c, T)
    for i in range(7): c.R(24 + i * 42, 40 + (i % 2) * 8, 32, 22, (255, 216, 74) if (i + int(tl * 2)) % 7 else (255, 255, 255)); label(c, 40 + i * 42, 48 + (i % 2) * 8, str(i + 1), (60, 50, 60), 10)
    label(c, 160, 14, 'SIETE TIENDAS', (255, 255, 255), 12); chibi(c, 'f_blake', 160, FLY + 4, T, f=.9, bounce=2); confetti(c, T, 20, 7, 120)
    return fin(c, 'day', (1, .98, .98), .45)


b_neiman = [_b_neiman_a, _b_neiman_b]


def _tv(c, t):
    c.R(0, 0, WW, WH, (30, 20, 50)); bg.curtain(c, 0, 20, 140, (150, 26, 70)); bg.curtain(c, WW - 30, 20, 140, (150, 26, 70))
    c.R(60, 30, 200, 90, (230, 236, 250)); c.light(160, 75, 110, 50, (220, 230, 255), .4)
    for i in range(14): c.R(10 + i * 22, 140, 16, 12, (120, 30, 60)); c.R(10 + i * 22, 140, 16, 2, (180, 60, 90))


def _b_oprah_a(T, tl, j):
    c = cv(); _tv(c, T); label(c, 160, 44, 'COSAS FAVORITAS', (140, 40, 90), 14); label(c, 160, 70, '2000', (200, 40, 60), 26)
    chibi(c, 'f_blake', 90, FLY + 4, T, f=.9, bounce=1.5)
    return fin(c, 'day', (1.03, 1, 1), .4)


def _b_oprah_b(T, tl, j):
    c = cv('#140a20', '#24123a'); stars(c, T, 60, 3, 130)
    label(c, 160, 40, 'SIN INVERSORES', (255, 216, 74), 22); label(c, 160, 92, 'según Fortune', (255, 255, 255), 10)
    face(c, 'f_blake', 'smile', T, x=160, sc=1.2)
    return fin(c, 'dark', (.95, .95, 1.05), .5)


b_oprah = [_b_oprah_a, _b_oprah_b]


# ================================================================ 5 · Honda
def _taller(c, t):
    room(c, (90, 80, 70), ((80, 84, 96), (72, 76, 88), (110, 116, 132)))
    cloud_window(c, 240, 28, 56, 56, t); clock(c, 130, 28, t, 8)
    c.R(40, 104, 140, 8, (90, 64, 46)); c.R(46, 112, 4, 28, (70, 48, 34)); c.R(170, 112, 4, 28, (70, 48, 34))
    for i in range(6): c.d.ellipse([70 + i * 16, 94, 82 + i * 16, 104], outline=(200, 200, 210), width=2)       # anillos de pistón
    dust(c, t, 16, 61, (0, 0, WW, 130), (255, 244, 220))


def _h_taller_a(T, tl, j):
    c = cv(); _taller(c, T); chibi(c, 'f_honda', 70, FLY + 6, T, f=.95)
    chibi(c, 'dueno', 250, FLY + 6, T + .3, f=.95, flip=True)
    if j == 1 and tl > .6: stamp(c, 210, 40, 'RECHAZADO', tl, size=12)
    return fin(c, 'day', (.98, .98, 1), .45)


def _h_taller_b(T, tl, j):
    c = cv(); _taller(c, T); face(c, 'f_honda', 'sad' if j == 1 else 'n', T, sc=1.7)
    return fin(c, 'dark', (.98, .98, 1), .5)


def _h_taller_c(T, tl, j):
    c = cv('#1a1830', '#2a2850'); stars(c, T, 40, 3, 100)
    c.R(80, 100, 160, 8, (90, 64, 46)); c.R(100, 60, 120, 40, (230, 240, 255)); [c.R(108, 68 + k * 8, 100 - (k * 9) % 30, 1, (60, 80, 140)) for k in range(4)]
    chibi(c, 'f_honda', 160, FLY + 6, T, f=.95); lamp_cone(c, 160, 6, T, 60, (255, 230, 170), 24)
    return fin(c, 'dark', (.95, .95, 1.05), .55)


h_taller = [_h_taller_a, _h_taller_b, _h_taller_c]


def _factory(c, t):
    room(c, (80, 80, 90), ((70, 76, 90), (62, 68, 82), (100, 108, 130)))
    c.R(0, 118, WW, 8, (50, 50, 58)); [c.R((i * 14 - int(t * 30)) % 340 - 10, 120, 10, 3, (110, 110, 124)) for i in range(26)]
    for i in range(9): c.R((i * 44 + int(t * 30)) % 360 - 20, 100, 18, 14, (200, 200, 214)); c.d.ellipse([(i * 44 + int(t * 30)) % 360 - 18, 96, (i * 44 + int(t * 30)) % 360 - 4, 106], outline=(240, 240, 250))
    for x in (40, 260): c.R(x, 20, 12, 70, (60, 60, 70)); steam(c, x + 6, 20, t)
    dust(c, t, 14, 62, (0, 0, WW, 130), (255, 240, 220))


def _h_fabrica_a(T, tl, j):
    c = cv(); _factory(c, T); chibi(c, 'f_honda', 90, FLY + 6, T, f=.95); chibi(c, 'dueno', 230, FLY + 6, T, f=.9, flip=True)
    if j == 0: label(c, 160, 20, 'AHORA TOYOTA ES CLIENTE', (255, 216, 74), 10)
    return fin(c, 'day', (1, .98, .96), .45)


def _h_fabrica_b(T, tl, j):
    c = cv(); _factory(c, T); label(c, 160, 28, '24 · SEP · 1948', (255, 216, 74), 14); label(c, 160, 52, 'HONDA MOTOR', (255, 255, 255), 18)
    chibi(c, 'f_honda', 160, FLY + 6, T, f=.95, bounce=2); confetti(c, T, 22, 6, 120)
    return fin(c, 'day', (1, .98, .96), .45)


h_fabrica = [_h_fabrica_a, _h_fabrica_b, _h_fabrica_a]


def _moto(c, x, y, t):
    for wx in (x, x + 26): c.d.ellipse([wx - 7, y - 7, wx + 7, y + 7], outline=(30, 30, 40), width=2); c.d.ellipse([wx - 1, y - 1, wx + 1, y + 1], fill=(160, 160, 170))
    c.R(x + 4, y - 14, 20, 6, (200, 40, 50)); c.R(x + 18, y - 20, 8, 8, (200, 40, 50)); c.R(x + 22, y - 24, 8, 2, (60, 60, 70)); c.R(x + 6, y - 18, 10, 4, (40, 40, 50))


def _h_moto_a(T, tl, j):
    c = cv(); S.world_day(c, T, T * 20, sunset=True); c.R(0, 150, WW, 30, (60, 56, 70))
    for i in range(8): c.R((i * 48 - int(T * 120)) % 360 - 20, 164, 22, 2, (240, 230, 180))
    _moto(c, int((T * 60) % 420) - 60, 156, T); birds(c, T, 24, 3, 8)
    label(c, 160, 20, 'HOY: EN TODO EL MUNDO', (255, 255, 255), 12)
    return fin(c, 'day', (1.08, 1, .92), .35)


h_moto = [_h_moto_a]


# ================================================================ 6 · cierre
def _cierre2_a(T, tl, j):
    c = cv(); S.world_day(c, T, T * 10, sunset=True); birds(c, T, 24, 6, 9)
    for i in range(6): c.R(int((i * 53 + T * 12) % WW), 120 + int(math.sin(T * 3 + i) * 8), 2, 2, (255, 230, 120))
    for i, w in enumerate(CAST5): chibi(c, w, 40 + i * 60, FLY + 4, T + i * .3, walk=True, f=.8)
    return fin(c, 'day', (1.05, 1, .95), .35)


def _cierre2_b(T, tl, j):
    c = cv(); S.world_day(c, T, 300, sunset=True); face(c, CAST5[j % 5], 'smile', T, sc=1.75)
    return fin(c, 'day', (1.05, 1, .95), .4)


def _cierre2_c(T, tl, j):
    c = cv('#140a20', '#24123a'); stars(c, T, 60, 3, 130)
    bg.wtext(c, 160, 36, 'NO', (230, 40, 60), size=70, center=True, emissive=True)
    if tl > 1.2: c.d.line([(100, 46), (220, 96)], fill=(255, 255, 255), width=4); bg.wtext(c, 160, 106, 'TODAVÍA NO', (255, 216, 74), size=34, center=True, emissive=True)
    return fin(c, 'dark', (.95, .95, 1.05), .5)


cierre2 = [_cierre2_a, _cierre2_b, _cierre2_c, _cierre2_b, _cierre2_a, _cierre2_b, _cierre2_a]

KITS = dict(n5=n5, s_usc=s_usc, s_uni=s_uni, s_duel=s_duel, z_walk=z_walk, z_meet=z_meet, z_book=z_book, d_garage=d_garage, d_count=d_count, d_shop=d_shop,
            b_fax=b_fax, b_mill=b_mill, b_neiman=b_neiman, b_oprah=b_oprah, h_taller=h_taller, h_fabrica=h_fabrica, h_moto=h_moto, cierre2=cierre2)
