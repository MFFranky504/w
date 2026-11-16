"""Video largo «5 famosos que lo perdieron casi todo y volvieron» (320x180 → 1920x1080). Reutiliza los ayudantes de scenes18.
Cada kit es una lista de planos fn(T, tl, k): T = s desde que empezó el escenario, tl = s desde que empezó el plano, k = nº de frase."""
import math, random
from PIL import Image
from lib import WW, WH, Canvas, vgrad, ease, stars
import gba as G
import bg
import props as PR
from sprites import dog as _dog
from scenes2 import bust
import scenes18 as S

cv, chibi, body, face, fin, put, spr, scaled = S.cv, S.chibi, S.body, S.face, S.fin, S.put, S.spr, S.scaled


def DOG(step):
    return spr(S.cached(('dograw', step % 2), lambda: _dog(1, step % 2)))   # el original se conserva: el caché de sprites usa id()
bubble, squiggle, confetti, crowd_front, FLY, FB = S.bubble, S.squiggle, S.confetti, S.crowd_front, S.FLY, S.FB
WALL = ((90, 70, 100), (80, 62, 92), (120, 96, 130))

# ================================================================ detalle animado de los fondos
def dust(c, t, n=26, seed=1, box=(0, 0, WW, 140), col=(255, 240, 200)):
    """motas de polvo que flotan (se ven en los haces de luz)."""
    rnd = random.Random(seed); x0, y0, x1, y1 = box
    for i in range(n):
        x = x0 + (rnd.random() * (x1 - x0) + math.sin(t * .6 + i) * 6) % (x1 - x0); y = y0 + (rnd.random() * (y1 - y0) - t * (3 + rnd.random() * 5)) % (y1 - y0)
        tw = .5 + .5 * math.sin(t * 3 + i)
        c.d.point((int(x), int(y)), fill=tuple(int(v * (.6 + .4 * tw)) for v in col))


def clock(c, x, y, t, r=9, fast=1.0):
    c.d.ellipse([x - r - 1, y - r - 1, x + r + 1, y + r + 1], fill=(40, 28, 24)); c.d.ellipse([x - r, y - r, x + r, y + r], fill=(246, 242, 228))
    for k in range(12): a = k * math.pi / 6; c.d.point((int(x + math.sin(a) * (r - 2)), int(y - math.cos(a) * (r - 2))), fill=(60, 50, 50))
    am, ah = t * .35 * fast, t * .03 * fast
    c.d.line([(x, y), (x + math.sin(am) * (r - 3), y - math.cos(am) * (r - 3))], fill=(40, 40, 50)); c.d.line([(x, y), (x + math.sin(ah) * (r - 6), y - math.cos(ah) * (r - 6))], fill=(40, 40, 50))
    c.d.point((x, y), fill=(200, 40, 50))


def steam(c, x, y, t, n=5):
    for i in range(n):
        ph = (t * .8 + i * .2) % 1; c.d.ellipse([x + math.sin(ph * 6 + i) * 3 - 1, y - ph * 14 - 1, x + math.sin(ph * 6 + i) * 3 + 2, y - ph * 14 + 2], fill=(255, 255, 255, 0) if False else (230, 230, 240))


def birds(c, t, y0=30, n=4, seed=2):
    rnd = random.Random(seed)
    for i in range(n):
        x = (rnd.random() * WW + t * (14 + i * 3)) % (WW + 30) - 15; y = y0 + i * 9 + math.sin(t * 2 + i) * 3; w = int(abs(math.sin(t * 8 + i)) * 3)
        c.d.line([(x - 4, y - w), (x, y)], fill=(40, 40, 60)); c.d.line([(x, y), (x + 4, y - w)], fill=(40, 40, 60))


def cloud_window(c, x, y, w, h, t, night=False, rainy=False, seed=1):
    """ventana con cielo, nubes que pasan y (opcional) lluvia."""
    c.R(x - 3, y - 3, w + 6, h + 6, (96, 64, 44)); c.R(x - 3, y - 3, w + 6, 2, (170, 130, 90))
    top, low = ((20, 22, 64), (70, 50, 100)) if night else (((120, 130, 150), (170, 180, 196)) if rainy else ((100, 160, 240), (220, 236, 250)))
    for j in range(h): c.R(x, y + j, w, 1, G.mix(top, low, j / h))
    for i in range(3):
        cx = x + (i * 38 + t * (6 + i * 2)) % (w + 30) - 15; cy = y + 8 + i * 10
        if not night: c.d.ellipse([cx - 12, cy - 4, cx + 12, cy + 4], fill=(250, 252, 255) if not rainy else (200, 206, 216))
    if rainy:
        for i in range(24): c.d.line([(x + (i * 13 + t * 18) % w, y + (i * 29 + t * 120) % h), (x + (i * 13 + t * 18) % w - 1, y + (i * 29 + t * 120) % h + 4)], fill=(170, 190, 230))
    c.R(x + w // 2 - 1, y, 2, h, (96, 64, 44)); c.R(x, y + h // 2 - 1, w, 2, (96, 64, 44))


def lamp_cone(c, x, y, t, w=70, col=(255, 230, 170), a=26):
    fl = 1 + math.sin(t * 9) * .04
    c.ed.polygon([(x - 6, y), (x + 6, y), (x + w * fl, y + 90), (x - w * fl, y + 90)], fill=(*col, a)); c.light(x, y + 70, int(w * .9), 40, col, .35)


def plant(c, x, y, t):
    c.R(x - 5, y, 10, 9, (150, 80, 60)); c.R(x - 5, y, 10, 2, (200, 120, 90))
    for k in range(5): a = -1.2 + k * .6 + math.sin(t * 1.5 + k) * .08; c.d.line([(x, y), (x + math.sin(a) * 11, y - math.cos(a) * 13)], fill=(70, 160, 90), width=3)



def room(c, floor=(120, 84, 56), wall=WALL):
    bg.wallpaper(c, 0, 0, WW, 142, *wall)
    bg.planks(c, 0, 142, WW, WH - 142, floor, seed=5, pw=8); c.R(0, 140, WW, 3, G.dark(floor, .6))


def label(c, x, y, txt, col=(255, 216, 74), size=10):
    bg.wtext(c, x, y, txt, col, size=size, center=True)


def stamp(c, x, y, txt, t, col=(230, 40, 60), size=20, delay=0):
    """sello que cae con rebote."""
    k = max(0, min(1, (t - delay) / .25))
    if k <= 0: return
    dy = int((1 - k) * -30 + math.sin(k * 3.14) * -4)
    w_ = int(len(txt) * size * .62) + 10; h_ = int(size * 1.05) + 6
    c.R(x - w_ // 2 - 1, y + dy - 1, w_ + 2, h_ + 2, (252, 244, 240)); c.R(x - w_ // 2, y + dy, w_, h_, col)
    bg.wtext(c, x, y + dy + 4, txt, (255, 255, 255), size=size, center=True, outline=None)


# ================================================================ 0 · gancho: cinco NO
CAST5 = ('f_disney', 'f_jobs85', 'f_stallone', 'f_rowling', 'f_carrey')


def _no_bg(c, T):
    for i in range(3): bg.beam(c, 60 + i * 100 + int(math.sin(T * .9 + i * 2) * 30), 0, 5, 50, FLY, (255, 246, 210), 22)
    dust(c, T, 40, 21, (0, 0, WW, 140), (255, 240, 200)); crowd_front(c, T, y=186, eyes=True, seed=31)
    for i in range(18): c.R((i * 37) % WW, 6 + (i * 11) % 30, 1, 1, (255, 255, 255) if (i + int(T * 4)) % 3 else (160, 160, 200))


def _no_a(T, tl, k):
    c = cv('#140a20', '#24123a'); _no_bg(c, T)
    for i, w in enumerate(CAST5):
        x = 36 + i * 62; b = spr(bust(w, 'worry' if i % 2 else 'n', (0, 0), T + i * .3, .85))
        c.im.paste(b, (x - b.width // 2, 36 + int(math.sin(T * 2 + i) * 2)), b)
        stamp(c, x, 118, 'NO', tl, delay=.3 + i * .45)
    return fin(c, 'dark', (1, .95, 1.05), .5)


def _no_b(T, tl, k):
    c = cv('#140a20', '#24123a'); _no_bg(c, T)
    for i, w in enumerate(CAST5):
        chibi(c, w, 40 + i * 60, FLY + 12, T + i * .2, f=.8, bounce=1.5 if tl > 1.5 else 0)
    stamp(c, 160, 40, 'NO', tl, size=40, delay=0)
    if tl > 2: stamp(c, 160, 40, 'VOLVIERON', tl, col=(60, 180, 90), size=26, delay=2.2)
    return fin(c, 'day', (1.05, 1, 1), .4)


def _no_c(T, tl, k):
    c = cv('#140a20', '#24123a'); stars(c, T, 50, 3, 120)
    bg.wtext(c, 160, 30, '?', (255, 216, 74), size=70, center=True, emissive=True)
    face(c, 'f_carrey', 'smile', T, sc=1.6, y_off=40)
    return fin(c, 'dark', (.9, .9, 1.1), .6)


no5 = [_no_a, _no_b, _no_a, _no_c, _no_b]


# ================================================================ 1 · Disney
def _oswald(c, x, y, t):
    c.d.ellipse([x - 8, y, x + 8, y + 16], fill=(20, 16, 24)); c.d.ellipse([x - 10, y - 20 + int(math.sin(t * 4) * 1), x - 4, y + 4], fill=(20, 16, 24)); c.d.ellipse([x + 4, y - 20, x + 10, y + 4], fill=(20, 16, 24))
    c.R(x - 4, y + 4, 3, 3, (255, 255, 255)); c.R(x + 2, y + 4, 3, 3, (255, 255, 255)); c.R(x - 3, y + 5, 1, 1, (20, 16, 24)); c.R(x + 3, y + 5, 1, 1, (20, 16, 24))


def _office28(c, t):
    room(c, (110, 80, 56), ((70, 90, 80), (62, 82, 72), (96, 120, 108)))
    bg.window(c, 20, 30, 50, 60, t=t, night=False, rain=False, lights=False)
    c.R(112, 96, 100, 6, (90, 60, 40)); c.R(112, 102, 100, 40, (70, 46, 32))                  # escritorio
    c.R(236, 40, 40, 56, (230, 220, 190)); c.R(238, 42, 36, 52, (240, 232, 204)); _oswald(c, 256, 64, t)   # cartel de Oswald
    label(c, 256, 100, 'OSWALD', (60, 50, 50), 8)
    clock(c, 160, 34, t, 10)                                                                                  # reloj de pared
    c.R(8, 70, 18, 72, (96, 70, 52)); [c.R(10, 74 + k * 17, 14, 14, (130, 96, 70)) for k in range(4)]         # archivador
    c.R(96, 60, 16, 24, (240, 232, 204)); c.R(98, 64, 12, 1, (150, 150, 160)); c.R(98, 68, 9, 1, (150, 150, 160))   # calendario
    lamp_cone(c, 150, 70, t, 40, (255, 226, 150), 22); dust(c, t, 22, 3, (100, 40, 220, 140), (255, 236, 180))
    for k in range(3): c.R(120 + k * 28, 96 - int(abs(math.sin(t * 2 + k)) * 2), 18, 3, (250, 248, 236))     # papeles sobre la mesa


def _d_ny_a(T, tl, k):
    c = cv(); _office28(c, T)
    chibi(c, 'f_disney', 90, FLY + 4, T, f=.85); chibi(c, 'dueno', 230, FLY + 4, T + .4, f=.85, flip=True)
    c.R(142, 90, 24, 16, (250, 248, 236)); c.R(145, 94, 18, 1, (90, 90, 100)); c.R(145, 98, 14, 1, (90, 90, 100))   # contrato
    if tl > 1.2: label(c, 154, 78, 'MENOS $', (200, 40, 60), 10)
    return fin(c, 'day', (1, .97, .95), .45)


def _d_ny_b(T, tl, k):
    c = cv(); _office28(c, T)
    face(c, 'f_disney', 'worry' if k < 4 else 'n', T, sc=1.7)
    if k >= 3: stamp(c, 240, 50, 'UNIVERSAL', tl, col=(60, 90, 170), size=12)
    return fin(c, 'dark', (1, .97, .95), .5)


def _d_ny_c(T, tl, k):
    c = cv(); _office28(c, T)
    chibi(c, 'f_disney', 100, FLY + 4, T, f=.85)
    for i, x in enumerate((180, 210, 240, 270)):                       # animadores que firman a sus espaldas
        chibi(c, ('dueno', 'todd', 'abuelo', 'senora')[i], x, FLY + 4, T + i, f=.6, flip=True)
    if tl > 1: stamp(c, 220, 30, 'FIRMARON', tl, col=(200, 40, 60), size=12)
    return fin(c, 'dark', (1, .97, .95), .5)


d_ny = [_d_ny_a, _d_ny_b, _d_ny_c, _d_ny_b, _d_ny_c, _d_ny_b]


def _train(c, t, night=True):
    c.R(0, 0, WW, WH, (30, 24, 40)); c.R(40, 20, 240, 110, (16, 14, 36))
    G.sky(c, [(0, (18, 20, 60)), (1, (120, 70, 100))], 44, 124, bands=5); stars(c, t, 20, 4, 70)
    c.d.ellipse([230, 50, 250, 70], fill=(250, 240, 200))                                                    # luna
    G.mountains(c, 112, 28, (50, 40, 90), seed=7, off=t * 14)
    for i in range(6):                                                                                      # postes de telégrafo que pasan
        px = (-int(t * 150) + i * 70) % 340 - 30; c.R(px, 70, 2, 54, (20, 16, 30)); c.R(px - 6, 74, 14, 2, (20, 16, 30)); c.d.line([(px - 6, 76), (px - 76, 80)], fill=(20, 16, 30))
    for i in range(7):                                                                                      # humo de la locomotora
        ph = (t * .7 + i * .15) % 1; sx = 50 + ph * 200; c.d.ellipse([sx, 60 - ph * 18, sx + 8 + ph * 12, 66 - ph * 18 + ph * 6], fill=(150, 140, 160))
    x = -int(t * 80) % 90 - 90
    for i in range(5):
        c.R(x + i * 90, 96, 60, 28, (30, 26, 50)); c.R(x + i * 90 + 6, 102, 8, 8, (255, 210, 120)); c.R(x + i * 90 + 24, 102, 8, 8, (255, 210, 120))
    c.R(40, 124, 240, 6, (20, 16, 30))
    c.R(0, 20, 40, 110, (90, 56, 40)); c.R(280, 20, 40, 110, (90, 56, 40)); c.R(40, 130, 240, 50, (110, 70, 48)); c.R(40, 130, 240, 3, (170, 120, 80))   # ventanilla y asiento


def _d_tren_a(T, tl, k):
    c = cv(); _train(c, T)
    chibi(c, 'f_disney', 160, 160, T, f=.9)
    return fin(c, 'dark', (.95, .95, 1.1), .55)


def _mouse(c, x, y, r, t=0):
    c.d.ellipse([x - r, y - r, x + r, y + r], fill=(20, 16, 24)); c.d.ellipse([x - r - r // 2, y - r - r // 3, x - r // 4, y - r // 4], fill=(20, 16, 24)); c.d.ellipse([x + r // 4, y - r - r // 3, x + r + r // 2, y - r // 4], fill=(20, 16, 24))
    c.d.ellipse([x - r // 2, y, x + r // 2, y + r // 1.4], fill=(252, 224, 196)); c.R(x - r // 3, y - r // 3, 3, 3, (255, 255, 255)); c.R(x + r // 6, y - r // 3, 3, 3, (255, 255, 255))


def _d_tren_b(T, tl, k):
    c = cv(); _train(c, T)
    face(c, 'f_disney', 'smile' if k > 12 else 'n', T, x=110, sc=1.5)
    if k >= 13:
        bubble(c, 190, 24, 100, 70, tail=(-30, 14)); _mouse(c, 240, 64, 16 + int(abs(math.sin(tl * 3)) * 3))
    return fin(c, 'dark', (.95, .95, 1.1), .55)


d_tren = [_d_tren_a, _d_tren_b, _d_tren_b, _d_tren_a]


def _theater(c, t, screen=True):
    c.R(0, 0, WW, WH, (24, 14, 28)); bg.curtain(c, 0, 30, 130, (150, 26, 50)); bg.curtain(c, WW - 30, 30, 130, (150, 26, 50))
    c.R(40, 20, 240, 96, (230, 232, 240)); c.light(160, 68, 110, 50, (220, 230, 255), .5)
    if screen:
        _mouse(c, 160, 70, 22)
        bg.wtext(c, 160, 28, 'STEAMBOAT WILLIE', (40, 36, 50), size=10, center=True, outline=None)
        c.d.polygon([(110, 104), (210, 104), (200, 112), (120, 112)], fill=(80, 70, 90))
    for r, y in enumerate((128, 148, 168)):
        for x in range(6, WW, 24): c.R(x, y, 20, 16, (130, 28, 44)); c.R(x, y, 20, 2, (180, 56, 70))
    c.ed.polygon([(158, 176), (162, 176), (270, 112), (50, 112)], fill=(220, 230, 255, 18)); dust(c, t, 36, 5, (60, 110, 260, 70), (230, 240, 255))   # haz del proyector con polvo
    c.R(150, 172, 20, 8, (50, 50, 60)); c.R(154, 168, 12, 5, (70, 70, 84))
    for k in range(2): c.R(8 + k * 292, 100, 14, 6, (40, 160, 90)); label(c, 15 + k * 292, 101, 'EXIT', (255, 255, 255), 4)


def _d_steam_a(T, tl, k):
    c = cv(); _theater(c, T)
    for i in range(8): chibi(c, ('senora', 'abuelo', 'dueno', 'todd')[i % 4], 24 + i * 38, 152 + (i % 2) * 14, T + i * .3, f=.55, bounce=3.0 if k > 15 else 0, flip=i > 3)
    return fin(c, 'day', (1.05, 1, 1), .45)


def _d_steam_b(T, tl, k):
    c = cv(); _theater(c, T, False)
    face(c, 'f_disney', 'smile', T, sc=1.7); confetti(c, T, 25, 5, 120)
    return fin(c, 'day', (1.05, 1, 1), .45)


d_steam = [_d_steam_a, _d_steam_b, _d_steam_a]


def _stadium(c, T):
    for x in (30, 290): c.R(x, 30, 3, 90, (90, 90, 100)); c.R(x - 12, 24, 28, 8, (230, 230, 240)); c.ed.polygon([(x - 10, 32), (x + 12, 32), (x + 70 * (1 if x < 160 else -1) + 40, 150), (x - 40, 150)], fill=(255, 250, 220, 16)); c.light(x, 30, 30, 20, (255, 250, 220), .5)
    for r in range(3):
        for i in range(60): c.R(i * 6 + (r * 3), 96 + r * 10, 4, 6, [(200, 60, 70), (60, 90, 170), (230, 190, 70), (240, 240, 244)][(i + r + int(T * 2 * ((i * 7 + r) % 3 == 0))) % 4])   # gradas con aficionados
    c.R(120, 16, 80, 22, (20, 24, 40)); c.R(122, 18, 76, 18, (30, 60, 40)); bg.wtext(c, 160, 21, 'NBC   DISNEY', (255, 220, 100), size=6, center=True, outline=None)    # marcador
    dust(c, T, 24, 23, (0, 20, WW, 150), (255, 250, 220))


def _d_osw_a(T, tl, k):
    c = cv('#0a1030', '#1c2250'); stars(c, T, 30, 3, 80); _stadium(c, T)
    c.R(0, 150, WW, 30, (40, 110, 60))
    for x in range(10, WW, 40): c.R(x, 150, 2, 30, (220, 236, 220))
    p = ease(min(1, tl / 2.2))
    _oswald(c, int(40 + 220 * p), 120, T)
    label(c, 70, 30, '1928', (255, 216, 74), 24); label(c, 250, 30, '2006', (255, 216, 74), 24)
    c.d.line([(104, 40), (216, 40)], fill=(255, 255, 255)); c.d.polygon([(216, 36), (224, 40), (216, 44)], fill=(255, 255, 255))
    return fin(c, 'dark', (1, .97, 1.05), .5)


def _d_osw_b(T, tl, k):
    c = cv('#0a1030', '#1c2250'); _stadium(c, T); c.R(0, 150, WW, 30, (40, 110, 60))
    label(c, 160, 30, '78 AÑOS', (255, 216, 74), 40)
    _oswald(c, 90, 110, T)
    c.R(214, 96, 6, 40, (90, 90, 100)); c.d.ellipse([208, 80, 226, 98], fill=(60, 60, 70))      # micrófono
    c.d.line([(110, 118), (200, 118)], fill=(255, 216, 74), width=2); c.d.polygon([(110, 118), (118, 112), (118, 124)], fill=(255, 216, 74)); c.d.polygon([(200, 118), (192, 112), (192, 124)], fill=(255, 216, 74))
    return fin(c, 'dark', (1, .97, 1.05), .5)


d_oswald = [_d_osw_a, _d_osw_b, _d_osw_b]


# ================================================================ 2 · Jobs
def _board(c, t):
    room(c, (60, 60, 76), ((50, 54, 70), (44, 48, 64), (70, 76, 100)))
    c.R(50, 100, 220, 10, (40, 28, 24)); c.R(50, 110, 220, 40, (28, 20, 18))                # mesa
    c.R(130, 22, 60, 50, (230, 232, 240)); bg.wtext(c, 160, 38, 'APPLE', (40, 40, 50), size=14, center=True, outline=None)
    cloud_window(c, 14, 26, 70, 62, t, seed=2); cloud_window(c, 236, 26, 70, 62, t, seed=3)
    clock(c, 108, 40, t, 8); plant(c, 14, 132, t); plant(c, 306, 132, t)
    for k in (70, 160, 250): c.ed.polygon([(k - 4, 6), (k + 4, 6), (k + 22, 100), (k - 22, 100)], fill=(255, 250, 220, 14)); c.R(k - 8, 4, 16, 3, (230, 226, 210))      # luces de techo
    dust(c, t, 20, 6, (0, 0, WW, 130), (255, 250, 230))
    for i, x in enumerate((70, 110, 210, 250)): chibi(c, ('todd', 'dueno', 'abuelo', 'todd')[i], x, 118, t + i, f=.6, flip=x > 160)


def _j_board_a(T, tl, k):
    c = cv(); _board(c, T)
    chibi(c, 'f_jobs85', 160, FLY + 28, T, f=.9)
    return fin(c, 'dark', (.95, .95, 1.05), .55)


def _j_board_b(T, tl, k):
    c = cv(); room(c, (60, 60, 76), ((50, 54, 70), (44, 48, 64), (70, 76, 100)))
    face(c, 'f_jobs85', 'sad', T, sc=1.7)
    return fin(c, 'dark', (.9, .9, 1.05), .6)


def _j_board_c(T, tl, k):
    c = cv(); room(c, (60, 60, 76), ((50, 54, 70), (44, 48, 64), (70, 76, 100)))
    c.R(220, 40, 50, 100, (110, 80, 56)); c.R(226, 46, 38, 88, (60, 44, 36))               # puerta
    x = 90 + 120 * ease(min(1, tl / 2.5))
    chibi(c, 'f_jobs85', x, FLY + 2, T, walk=tl < 2.5, f=.9)
    c.R(int(x) - 10, FLY - 26, 14, 10, (200, 160, 100))                                         # caja con sus cosas
    return fin(c, 'dark', (.95, .95, 1.05), .55)


j_board = [_j_board_a, _j_board_b, _j_board_c, _j_board_b]


def _lab(c, t):
    room(c, (70, 70, 84), ((30, 36, 54), (26, 32, 48), (50, 60, 90)))
    for i, x in enumerate((30, 100, 240)):
        c.R(x, 70, 44, 36, (30, 30, 40)); c.R(x + 3, 73, 38, 30, (20, 40 + int(math.sin(t * 3 + i) * 10 + 10), 80)); c.R(x + 16, 106, 12, 8, (50, 50, 60))
        for j in range(4): c.R(x + 8 + j * 8, 80 + (int(t * 8 + j * 3) % 14), 4, 2, (120, 200, 255))
    cx, cy, r = 62, 88, 11                                                                                      # cubo de alambre girando
    pts = [(math.cos(t * 2) * a + math.sin(t * 2) * b, (math.cos(t * 2) * b - math.sin(t * 2) * a) * .6 + (dz * .0)) for a, b, dz in ((-r, -r, 0), (r, -r, 0), (r, r, 0), (-r, r, 0))]
    for k in range(4): c.d.line([(cx + pts[k][0], cy + pts[k][1]), (cx + pts[(k + 1) % 4][0], cy + pts[(k + 1) % 4][1])], fill=(120, 230, 255))
    for k in range(4): c.d.line([(cx + pts[k][0], cy + pts[k][1]), (cx + pts[k][0], cy + pts[k][1] - 8)], fill=(120, 230, 255))
    for k in range(4): c.d.line([(cx + pts[k][0], cy + pts[k][1] - 8), (cx + pts[(k + 1) % 4][0], cy + pts[(k + 1) % 4][1] - 8)], fill=(120, 230, 255))
    for k in range(3):                                                                                          # rack de servidores con luces
        c.R(290, 40 + k * 30, 22, 26, (40, 44, 56)); [c.R(293 + j * 4, 44 + k * 30, 2, 2, (80, 255, 120) if (int(t * 4) + j + k) % 3 else (255, 90, 70)) for j in range(5)]
    for k in range(5): c.d.line([(300, 124), (250 - k * 18, 142)], fill=(30, 30, 40))                         # cables
    dust(c, t, 14, 8, (0, 0, WW, 120), (160, 220, 255))


def _lamp(c, x, y, t):
    c.R(x, y + 24, 22, 4, (230, 230, 236)); c.d.line([(x + 11, y + 24), (x + 4, y + 8)], fill=(230, 230, 236), width=3); c.d.line([(x + 4, y + 8), (x + 22, y + 2)], fill=(230, 230, 236), width=3)
    c.d.polygon([(x + 20, y - 2), (x + 34, y + 6), (x + 22, y + 12), (x + 16, y + 4)], fill=(240, 240, 246)); c.light(x + 28, y + 10, 16, 10, (255, 240, 180), .5)


def _j_pixar_a(T, tl, k):
    c = cv(); _lab(c, T)
    chibi(c, 'f_jobs85', 170, FLY + 6, T, f=.9)
    c.R(120, 108, 24, 24, (20, 20, 26)); c.R(121, 109, 22, 1, (90, 90, 100)); label(c, 132, 96, 'NeXT', (255, 255, 255), 10)    # cubo NeXT
    return fin(c, 'dark', (.95, .95, 1.05), .5)


def _j_pixar_b(T, tl, k):
    c = cv(); _lab(c, T); _lamp(c, 220, 80, T); label(c, 235, 30, 'PIXAR', (255, 216, 74), 34)
    face(c, 'f_jobs85', 'n', T, x=90, sc=1.4)
    return fin(c, 'dark', (.95, .95, 1.05), .5)


j_pixar = [_j_pixar_a, _j_pixar_b, _j_pixar_a, _j_pixar_b]


def _apple_logo(c, x, y, r):
    c.d.ellipse([x - r, y - r, x + r * 0.2, y + r], fill=(240, 240, 246)); c.d.ellipse([x - r * 0.2, y - r, x + r, y + r], fill=(240, 240, 246))
    c.d.ellipse([x + r * 0.3, y - r * 0.4, x + r * 1.1, y + r * 0.4], fill=(0, 0, 0, 0)); c.d.polygon([(x, y - r), (x + 4, y - r - 8), (x + 12, y - r - 6)], fill=(80, 200, 100))


def _apple_hq(c, t):
    G.sky(c, [(0, (90, 150, 240)), (1, (230, 240, 252))], 0, FLY, bands=7); G.clouds(c, t, 26, (255, 255, 255), n=4, seed=6, speed=1.2)
    c.R(40, 50, 240, 90, (226, 228, 236)); c.R(40, 50, 240, 4, (160, 164, 180))
    for i in range(6): c.R(50 + i * 38, 70, 24, 44, (70, 100, 150)); c.R(50 + i * 38, 70, 24, 2, (200, 220, 250))
    _apple_logo(c, 160, 36, 12)
    G.blocks(c, -8, FLY, WW + 16, WH - FLY + 4, (180, 176, 168), tile=16, seed=19, t=t)
    for x in (14, 300): c.R(x - 2, 96, 5, 44, (110, 80, 56)); c.d.ellipse([x - 16, 66 + int(math.sin(t + x) * 1), x + 18, 104], fill=(70, 170, 100)); c.d.ellipse([x - 10, 60, x + 12, 90], fill=(100, 200, 120))   # árboles
    c.R(284, 20, 2, 50, (150, 150, 160)); c.d.polygon([(286, 22), (308 + int(math.sin(t * 4) * 3), 28), (286, 36)], fill=(240, 240, 246))                           # bandera
    for i in range(2): chibi(c, ('senora', 'abuelo')[i], (40 + i * 150 + t * 12 * (1 if i else -1)) % 340, FLY + 16, t + i, walk=True, f=.5, flip=i == 0)   # gente caminando
    birds(c, t, 22, 4, 5)


def _j_apple_a(T, tl, k):
    c = cv(); _apple_hq(c, T)
    chibi(c, 'f_jobs', 60 + 100 * ease(min(1, tl / 3)), FLY + 6, T, walk=tl < 3, f=.9)
    return fin(c, 'day', (1.04, 1, .97), .35)


def _j_apple_b(T, tl, k):
    c = cv(); _apple_hq(c, T); face(c, 'f_jobs', 'smile', T, sc=1.7)
    return fin(c, 'day', (1.04, 1, .97), .4)


def _j_apple_c(T, tl, k):
    c = cv('#0a1030', '#1c2250'); stars(c, T, 40, 3, 100)
    label(c, 80, 60, '1985', (255, 216, 74), 40); label(c, 240, 60, '1997', (255, 216, 74), 40)
    n = min(1, tl / 2); c.d.line([(120, 80), (int(120 + 80 * n), 80)], fill=(255, 255, 255), width=3)
    label(c, 160, 110, '12 AÑOS', (255, 255, 255), 28)
    return fin(c, 'dark', (.95, .95, 1.05), .5)


def _j_apple_d(T, tl, k):
    c = cv(); G.sky(c, [(0, (70, 150, 240)), (1, (230, 240, 252))], 0, FLY, bands=7); G.clouds(c, T, 30, (255, 255, 255), n=4, seed=8, speed=1.4)
    G.blocks(c, -8, FLY, WW + 16, WH - FLY + 4, (180, 176, 168), tile=16, seed=19, t=T)
    _lamp(c, 70, 100, T); _oswald(c, 250, 112, T)
    label(c, 160, 30, '7.400 MILLONES', (255, 216, 74), 22); label(c, 160, 54, 'DISNEY COMPRA PIXAR', (255, 255, 255), 10)
    c.d.line([(120, 116), (216, 116)], fill=(255, 216, 74), width=2); c.d.polygon([(216, 110), (226, 116), (216, 122)], fill=(255, 216, 74))
    return fin(c, 'day', (1.04, 1, .97), .35)


j_apple = [_j_apple_a, _j_apple_b, _j_apple_c, _j_apple_b, _j_apple_d]


# ================================================================ 3 · Stallone
def _poor_room(c, T):
    room(c, (90, 70, 56), ((60, 56, 68), (54, 50, 62), (80, 76, 92)))
    cloud_window(c, 230, 26, 56, 70, T, night=True, rainy=True)
    fl = 1 if int(T * 7) % 23 else .55
    c.R(158, 4, 2, 26, (60, 60, 70)); c.d.ellipse([154, 30, 164, 40], fill=(255, int(220 * fl), int(150 * fl))); c.light(159, 40, 60, 50, (255, 220, 150), .5 * fl)    # foco que parpadea
    c.d.ellipse([20, 50, 36, 66], fill=(190, 40, 50)); c.R(30, 56, 8, 4, (150, 30, 40))                              # guante de boxeo colgado
    for k in range(4): c.R(250 + (k % 2), 132 - k * 5, 24, 4, (220, 214, 196))                                    # montón de periódicos
    dust(c, T, 14, 11, (0, 0, WW, 130), (255, 230, 190))


def _r_room_a(T, tl, k):
    c = cv(); _poor_room(c, T)
    c.R(60, 106, 60, 6, (100, 70, 46)); c.R(64, 112, 4, 28, (80, 56, 38)); c.R(112, 112, 4, 28, (80, 56, 38))
    c.R(76, 94, 24, 12, (230, 226, 214)); c.R(80, 98, 16, 1, (80, 80, 90)); c.R(80, 101, 12, 1, (80, 80, 90))        # máquina de escribir
    chibi(c, 'f_stallone', 150, FLY + 4, T, f=.9)
    c.light(88, 70, 40, 30, (255, 220, 150), .4)
    return fin(c, 'dark', (.95, .93, 1), .55)


def _r_room_b(T, tl, k):
    c = cv(); _poor_room(c, T)
    face(c, 'f_stallone', 'sad', T, sc=1.7)
    return fin(c, 'dark', (.95, .93, 1), .6)


def _r_room_dog(T, tl, k):
    c = cv(); _poor_room(c, T)
    c.d.ellipse([200, 126, 260, 146], fill=(70, 50, 44)); c.d.ellipse([206, 128, 254, 142], fill=(110, 80, 62))                  # cama vacía
    x = 60 + 120 * ease(min(1, tl / 2.5)); d_ = DOG(int(T * 6)); put(c, d_, x, FLY + 6)
    chibi(c, 'f_stallone', 50, FLY + 4, T, f=.9)
    if tl > 2.2: label(c, 170, 40, '¡ADIÓS, BUTKUS!', (255, 216, 74), 10)
    return fin(c, 'dark', (.95, .93, 1), .55)


r_room = [_r_room_a, _r_room_b, _r_room_dog, _r_room_b]


def _office70(c, t):
    room(c, (90, 74, 60), ((100, 70, 60), (92, 64, 54), (130, 96, 80)))
    c.R(90, 100, 140, 8, (70, 46, 34)); c.R(90, 108, 140, 34, (54, 36, 28))
    cloud_window(c, 18, 24, 60, 70, t, night=True)
    for k in range(7): c.R(20, 28 + k * 9, 56, 1, (40, 28, 30))                                                 # persiana
    clock(c, 160, 34, t, 10, 1.5); plant(c, 296, 132, t)
    for k in range(3): c.R(250 + k * 16, 70, 14, 18, (110, 110, 120)); c.d.ellipse([252 + k * 16, 74, 262 + k * 16, 84], fill=(60, 60, 70))   # latas de película
    for i in range(6):
        ph = (t * .5 + i * .17) % 1; c.d.ellipse([200 + math.sin(ph * 8 + i) * 4, 96 - ph * 40, 204 + math.sin(ph * 8 + i) * 4, 100 - ph * 40], fill=(190, 190, 200))   # humo de cigarro
    ax = 160; c.R(ax - 1, 4, 2, 10, (60, 60, 70))
    for k in range(4): a = t * 7 + k * math.pi / 2; c.d.line([(ax, 14), (ax + math.cos(a) * 26, 14 + math.sin(a) * 4)], fill=(120, 120, 130), width=2)   # ventilador de techo


def _r_pitch_a(T, tl, k):
    c = cv(); _office70(c, T)
    chibi(c, 'f_stallone', 70, FLY + 4, T, f=.9)
    chibi(c, 'todd', 230, FLY + 4, T + .3, f=.9, flip=True); chibi(c, 'dueno', 270, FLY + 8, T + .6, f=.8, flip=True)
    for i in range(6): c.R(130 + i * 9, 88 - (i % 2) * 2, 8, 14, (96, 180, 110)); c.R(130 + i * 9, 88 - (i % 2) * 2, 8, 2, (150, 230, 160))   # fajos
    return fin(c, 'day', (1.02, .97, .95), .45)


def _r_pitch_b(T, tl, k):
    c = cv(); _office70(c, T); face(c, 'f_stallone', 'worry' if k < 33 else 'n', T, sc=1.7)
    if tl > 1: stamp(c, 250, 40, 'NO', tl, size=30)
    return fin(c, 'dark', (1, .96, .95), .5)


def _r_pitch_c(T, tl, k):
    c = cv(); _office70(c, T)
    chibi(c, 'f_stallone', 70, FLY + 4, T, f=.9)
    chibi(c, 'todd', 240, FLY + 4, T, f=.9, flip=True)
    x = 150 - 40 * ease(min(1, tl / 1.5))
    for i in range(6): c.R(int(x) + i * 9, 88 - (i % 2) * 2, 8, 14, (96, 180, 110))
    stamp(c, 160, 36, 'SOLO SI SOY YO', tl, col=(60, 90, 170), size=14, delay=.4)
    return fin(c, 'day', (1.02, .97, .95), .45)


r_pitch = [_r_pitch_a, _r_pitch_b, _r_pitch_c, _r_pitch_b]


def _r_oscar_a(T, tl, k):
    c = cv('#140a20', '#24123a'); bg.curtain(c, 0, 60, 150, (160, 30, 60)); bg.curtain(c, WW - 60, 60, 150, (160, 30, 60))
    c.R(0, 140, WW, 40, (60, 30, 50)); c.R(0, 140, WW, 2, (250, 210, 120)); S.spotlight(c, 160, T, 90, 1.2)
    for k in range(3): bg.beam(c, 40 + k * 120 + int(math.sin(T * 1.3 + k * 2) * 36), 0, 4, 40, 140, (255, 230, 170), 16)                 # focos que barren
    for i in range(5):
        if (int(T * 3) + i) % 5 == 0: c.d.ellipse([20 + i * 70, 118, 28 + i * 70, 126], fill=(255, 255, 255))                                      # flashes de cámaras
    chibi(c, 'f_stallone', 150, FLY + 4, T, f=.9, bounce=1.5)
    st = scaled(PR.statuette(40), 1.0); c.im.paste(st, (210, 140 - st.height), st); c.light(220, 120, 30, 40, (255, 220, 120), .6)
    put(c, DOG(int(T * 6)), 100, FLY + 6)
    confetti(c, T, 40, 9, 130)
    return fin(c, 'day', (1.05, 1.0, 1.0), .4)


def _r_oscar_b(T, tl, k):
    c = cv('#140a20', '#24123a'); bg.curtain(c, 0, 60, 150, (160, 30, 60)); bg.curtain(c, WW - 60, 60, 150, (160, 30, 60))
    face(c, 'f_stallone', 'smile', T, sc=1.7); confetti(c, T, 30, 4, 130)
    return fin(c, 'day', (1.05, 1.0, 1.0), .45)


r_oscar = [_r_oscar_a, _r_oscar_b, _r_oscar_a]


# ================================================================ 4 · Rowling
def _cafe(c, t):
    room(c, (130, 96, 70), ((120, 96, 80), (110, 86, 72), (150, 124, 104)))
    cloud_window(c, 200, 28, 90, 70, t, rainy=True)
    for i in range(3):                                                                                           # gente con paraguas por la calle
        ux = (210 + i * 40 + t * (10 + i * 3)) % 120 + 190; c.d.pieslice([ux - 8, 64, ux + 8, 80], 180, 360, fill=((200, 60, 70), (60, 90, 170), (230, 190, 70))[i]); c.R(ux, 72, 1, 12, (40, 40, 50))
    for k in (60, 160): sw = math.sin(t * 1.4 + k) * 3; c.d.line([(k, 0), (k + sw, 22)], fill=(60, 50, 50)); c.d.ellipse([k - 8 + sw, 22, k + 8 + sw, 32], fill=(255, 220, 150)); c.light(k + sw, 30, 40, 30, (255, 210, 140), .35)
    clock(c, 120, 30, t, 8); c.R(14, 40, 40, 4, (96, 70, 52)); [c.R(18 + j * 9, 30, 7, 10, ((200, 60, 70), (60, 90, 170), (230, 190, 70), (60, 150, 100))[j % 4]) for j in range(4)]
    steam(c, 128, 104, t); c.R(120, 104, 10, 6, (240, 240, 244)); c.R(124, 104, 2, 1, (120, 70, 50))              # taza humeante
    c.R(40, 106, 100, 6, (90, 60, 40)); c.R(60, 112, 4, 30, (70, 46, 32)); c.R(116, 112, 4, 30, (70, 46, 32))
    c.R(70, 94, 22, 12, (240, 236, 224)); c.R(74, 98, 14, 1, (80, 80, 90)); c.R(74, 101, 10, 1, (80, 80, 90))


def _w_cafe_a(T, tl, k):
    c = cv(); _cafe(c, T); chibi(c, 'f_rowling', 150, FLY + 4, T, f=.9)
    for i in range(12):                                                                # cartas de rechazo
        if tl > .3 + i * .22 or k > 1:
            x = 160 + (i % 6) * 22; y = 120 - (i // 6) * 16
            c.R(x, y, 18, 12, (250, 246, 236)); c.R(x, y, 18, 1, (200, 190, 170)); c.R(x + 4, y + 4, 10, 1, (160, 60, 60))
    return fin(c, 'day', (1.02, .97, .95), .45)


def _w_cafe_b(T, tl, k):
    c = cv(); _cafe(c, T); face(c, 'f_rowling', 'sad', T, sc=1.7)
    return fin(c, 'dark', (.95, .95, 1), .55)


def _w_cafe_c(T, tl, k):
    c = cv('#140a20', '#24123a'); n = min(12, int(tl * 5) + 1)
    bg.wtext(c, 160, 36, str(n), (255, 216, 74), size=70, center=True, emissive=True)
    label(c, 160, 120, 'EDITORIALES DIJERON NO', (255, 255, 255), 12)
    for i in range(n): c.R(30 + i * 22, 140, 16, 12, (250, 246, 236)); c.R(32 + i * 22, 144, 10, 1, (200, 40, 60))
    return fin(c, 'dark', (.95, .95, 1.05), .5)


w_cafe = [_w_cafe_a, _w_cafe_b, _w_cafe_c, _w_cafe_a]


def _pub_bg(c, T):
    room(c, (110, 84, 60), ((70, 90, 110), (62, 82, 102), (96, 120, 140)))
    cloud_window(c, 20, 26, 70, 64, T); clock(c, 160, 28, T, 9); plant(c, 300, 132, T); plant(c, 120, 132, T)
    bg.shelf(c, 220, 30, 80, 60, seed=3); dust(c, T, 18, 4, (0, 0, WW, 130), (255, 244, 220))


def _w_pub_a(T, tl, k):
    c = cv(); _pub_bg(c, T)
    c.R(60, 96, 200, 8, (80, 56, 40)); c.R(70, 104, 180, 36, (60, 40, 30))
    chibi(c, 'todd', 80, FLY + 4, T, f=.9); chibi(c, 'f_alice', 190, FLY + 6, T, f=.75, bounce=0.5)
    c.R(180, 88, 18, 14, (250, 246, 236))
    return fin(c, 'day', (1.02, .98, .96), .45)


def _w_pub_b(T, tl, k):
    c = cv(); _pub_bg(c, T)
    face(c, 'f_alice', 'smile', T, sc=1.5)
    if tl > 1: bubble(c, 190, 20, 100, 24, tail=(-20, 10)); label(c, 240, 26, '¿Y EL SIGUIENTE?', (200, 40, 60), 10)
    return fin(c, 'day', (1.02, .98, .96), .45)


w_pub = [_w_pub_a, _w_pub_b, _w_pub_a]


def _w_books_a(T, tl, k):
    c = cv(); room(c, (120, 90, 64), ((90, 60, 50), (82, 54, 44), (120, 86, 70)))
    for i in range(500 // 25):
        x = 120 + (i % 5) * 16; y = 130 - (i // 5) * 8
        c.R(x, y, 14, 7, [(200, 60, 70), (60, 90, 170), (230, 190, 70), (60, 150, 100)][i % 4]); c.R(x, y, 14, 1, (255, 255, 255))
    label(c, 160, 30, '500', (255, 216, 74), 50); label(c, 160, 70, 'EJEMPLARES', (255, 255, 255), 12)
    return fin(c, 'day', (1.02, .98, .96), .45)


def _w_books_b(T, tl, k):
    c = cv(); bg.shelf(c, 0, 0, WW, 150, seed=9); c.R(0, 150, WW, 30, (90, 60, 40))
    for i in range(14):
        a = (T * 12 + i * 23) % 300 - 20; b = spr(bust('f_alice', 'smile', (0, 0), T, .3)) if i % 7 == 0 else None
    label(c, 160, 160, 'DECENAS DE IDIOMAS', (255, 216, 74), 12)
    langs = ('ES', 'EN', 'FR', 'DE', 'IT', 'PT', 'JA', 'RU')
    for i, l_ in enumerate(langs):
        x = 30 + i * 38; y = 40 + (i % 2) * 36 + int(math.sin(T * 2 + i) * 3)
        c.d.ellipse([x - 14, y - 14, x + 14, y + 14], fill=(255, 216, 74)); bg.wtext(c, x, y - 4, l_, (40, 30, 40), size=10, center=True, outline=None)
    return fin(c, 'day', (1.02, .98, .96), .45)


w_books = [_w_books_a, _w_books_b]


# ================================================================ 5 · Carrey
def _hill(c, t):
    G.sky(c, [(0, (14, 14, 50)), (1, (90, 50, 100))], 0, 110, bands=6); stars(c, t, 40, 5, 80)
    bg.skyline(c, 90, 110, cols=((30, 26, 70), (44, 36, 90)), seed=12, lit=.7, t=t, wmin=6, wmax=12, hmin=14, hmax=40)
    c.R(0, 110, WW, 70, (24, 20, 40)); G.mountains(c, 112, 20, (30, 24, 50), seed=3)
    for i in range(40): c.R((i * 17) % WW, 112 + (i * 13) % 30, 2, 2, (255, 220, 140) if (i + int(t * 3)) % 3 else (160, 130, 90))     # luces de la ciudad
    c.d.ellipse([250, 18, 276, 44], fill=(250, 244, 214)); c.d.ellipse([258, 22, 282, 44], fill=(24, 22, 60))                                        # luna creciente
    for i in range(3):                                                                                           # estrellas fugaces
        ph = (t * .35 + i * .37) % 1
        if ph < .25: sx = 40 + i * 90 + ph * 220; sy = 10 + i * 12 + ph * 80; c.d.line([(sx, sy), (sx - 16, sy - 9)], fill=(255, 255, 255)); c.d.point((int(sx), int(sy)), fill=(255, 240, 200))
    for i in range(5):                                                                                           # autos en la autopista lejana
        ax = (i * 66 + t * 24 * (1 if i % 2 else -1)) % 340 - 10; c.R(int(ax), 128 + (i % 2) * 6, 5, 2, (255, 250, 200) if i % 2 else (255, 70, 60))
    c.d.line([(0, 126), (WW, 134)], fill=(70, 60, 100)); birds(c, t, 24, 2, 7)


def _c_hill_a(T, tl, k):
    c = cv(); _hill(c, T)
    c.R(90, 140, 70, 14, (150, 40, 40)); c.R(100, 130, 36, 12, (150, 40, 40)); c.d.ellipse([100, 150, 114, 164], fill=(20, 20, 24)); c.d.ellipse([140, 150, 154, 164], fill=(20, 20, 24))   # coche
    chibi(c, 'f_carrey', 200, FLY + 14, T, f=.85)
    return fin(c, 'dark', (.95, .95, 1.1), .55)


def _c_hill_b(T, tl, k):
    c = cv(); _hill(c, T); face(c, 'f_carrey', 'n', T, sc=1.7)
    return fin(c, 'dark', (.95, .95, 1.1), .55)


c_hill = [_c_hill_a, _c_hill_b, _c_hill_a]


def _check(c, t, k):
    c.R(0, 0, WW, WH, (40, 36, 52)); c.R(30, 30, 260, 120, (250, 246, 230)); c.R(30, 30, 260, 3, (200, 190, 160)); c.R(30, 147, 260, 3, (200, 190, 160))
    bg.wtext(c, 56, 40, 'PAGUESE A: JIM CARREY', (60, 60, 80), size=9, outline=None)
    bg.wtext(c, 250, 40, 'NOV 1995', (200, 40, 60), size=9, center=True, outline=None)
    n = min(1, t / 2); val = '$10.000.000'
    bg.wtext(c, 160, 70, val[:max(1, int(len(val) * n))], (40, 90, 60), size=28, center=True, outline=None)
    bg.wtext(c, 90, 120, 'servicios de actuacion', (80, 80, 100), size=8, outline=None)
    c.d.line([(200, 138), (270, 130)], fill=(40, 40, 120), width=2)


def _c_check_a(T, tl, k): c = cv(); _check(c, tl, k); c.light(160, 90, 130, 70, (255, 240, 200), .4); return fin(c, 'day', (1, .98, .95), .5)


def _c_check_b(T, tl, k):
    c = cv('#28243c', '#38304c'); face(c, 'f_carrey', 'smile', T, x=110, sc=1.5)
    c.R(200, 60, 90, 50, (250, 246, 230)); bg.wtext(c, 245, 78, '$10 MILLONES', (40, 90, 60), size=10, center=True, outline=None)
    return fin(c, 'day', (1, .98, .95), .5)


c_check = [_c_check_a, _c_check_b, _c_check_a, _c_check_b]


# ================================================================ 6 · cierre
def _cierre_a(T, tl, k):
    c = cv(); S.world_day(c, T, T * 10, sunset=True); birds(c, T, 24, 6, 9)
    for i in range(6): c.R(int((i * 53 + T * 12) % WW), 120 + int(math.sin(T * 3 + i) * 8), 2, 2, (255, 230, 120))      # luciérnagas
    for i, w in enumerate(CAST5): chibi(c, w, 50 + i * 55, FLY + 4, T + i * .3, walk=True, f=.8)
    return fin(c, 'day', (1.05, 1.0, .95), .35)


def _cierre_b(T, tl, k):
    c = cv(); S.world_day(c, T, 300, sunset=True)
    w = CAST5[min(4, k % 7 if k % 7 < 5 else 4)]
    face(c, w, 'smile', T, sc=1.75)
    return fin(c, 'day', (1.05, 1.0, .95), .4)


def _cierre_c(T, tl, k):
    c = cv('#140a20', '#24123a'); stars(c, T, 60, 3, 130)
    bg.wtext(c, 160, 40, 'NO', (230, 40, 60), size=70, center=True, emissive=True)
    if tl > 1.5:
        c.d.line([(100, 50), (220, 100)], fill=(255, 255, 255), width=4); bg.wtext(c, 160, 110, 'SÍ', (255, 216, 74), size=70, center=True, emissive=True)
    return fin(c, 'dark', (.95, .95, 1.05), .5)


cierre = [_cierre_a, _cierre_b, _cierre_a, _cierre_b, _cierre_a, _cierre_b, _cierre_a, _cierre_c]

KITS = dict(no5=no5, d_ny=d_ny, d_tren=d_tren, d_steam=d_steam, d_oswald=d_oswald, j_board=j_board, j_pixar=j_pixar, j_apple=j_apple,
            r_room=r_room, r_pitch=r_pitch, r_oscar=r_oscar, w_cafe=w_cafe, w_pub=w_pub, w_books=w_books, c_hill=c_hill, c_check=c_check, cierre=cierre)
