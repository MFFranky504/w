"""Video largo de Cantinflas (horizontal 320x180, ×6 = 1920x1080), estilo GBA y todo animado.
Cada escenario (kit) es una lista de PLANOS; el montaje cambia de plano en cada frase de la narración (corte cada 3-5 s).
Un plano es fn(T, tl, k): T = segundos desde que empezó el escenario, tl = segundos desde que empezó el plano, k = nº de frase dentro del escenario.
Animación: chibis que caminan (ciclo de pasos) y rebotan, brazos que cambian de pose, caras que parpadean y cambian de gesto,
fondos con nubes, luces y público que se mueven."""
import math, random
from PIL import Image, ImageDraw
from lib import WW, WH, Canvas, vgrad, ease, stars, rain
import gba as G
import bg
import props as PR
from scenes3 import rpg, bat
from scenes2 import bust

FLY = 140                       # suelo (pies de los chibis)
FB = 170                        # pies de los sprites de cuerpo entero en planos medios
_C = {}


def cached(key, fn):
    if key not in _C: _C[key] = fn()
    return _C[key]


def cv(top='#000000', bot='#000000'): return Canvas(vgrad([(0, top), (1, bot)]))


def spr(img):
    """acabado GBA de un sprite (cacheado por la imagen fuente, que ya viene cacheada)."""
    return cached(('g', id(img)), lambda: G.sprite(img))


def scaled(img, f):
    return cached(('s', id(img), f), lambda: spr(img).resize((max(1, int(spr(img).width * f)), max(1, int(spr(img).height * f))), Image.NEAREST))


def put(c, im, cx, feet, flip=False, rot=0, shadow=True):
    if flip: im = cached(('f', id(im)), lambda: im.transpose(Image.FLIP_LEFT_RIGHT))
    if rot: im = im.rotate(rot, expand=True, resample=Image.NEAREST)
    bb = im.getbbox() or (0, 0, im.width, im.height)
    if shadow:
        w = (bb[2] - bb[0]) * .6; c.d.ellipse([cx - w / 2, feet - 2, cx + w / 2, feet + 2], fill=(20, 14, 40))
    x, y = int(cx - im.width / 2), int(feet - bb[3])
    c.im.paste(im, (x, y), im)


def step(t, speed=8): return (0, 1, 0, -1)[int(t * speed) % 4]


def chibi(c, who, cx, feet, t=0, walk=False, f=.72, flip=False, bounce=0.0, rot=0, outfit=None):
    """chibi (pequeño en planos abiertos). walk: ciclo de pasos y vaivén; bounce: salto (risa, alegría)."""
    st = step(t) if walk else 0
    im = scaled(rpg(who, st, outfit), f)
    dy = (abs(math.sin(t * 8)) * 1.5 if walk else 0) + abs(math.sin(t * 9)) * bounce
    put(c, im, cx, feet - dy, flip, rot)


def body(c, who, cx, feet, pose='stand', flip=False, rot=0, f=1.0, outfit=None):
    im = bat(who, pose, outfit)
    put(c, scaled(im, f) if f != 1.0 else spr(im), cx, feet, flip, rot)


def gesture(t, poses=('stand', 'hip', 'toss', 'hold'), speed=2.5):
    """brazos animados: cambia de pose a ritmo (hablar, gesticular, saludar)."""
    return poses[int(t * speed) % len(poses)]


def face(c, who, expr, t, x=None, sc=1.6, y_off=0, bob=True):
    """primer plano con parpadeo y leve respiración."""
    b = spr(bust(who, expr, (0, 0), t, sc))
    dy = int(math.sin(t * 2.2) * 1.2) if bob else 0
    c.im.paste(b, (int((x if x is not None else WW / 2) - b.width / 2), WH - b.height + 6 + y_off + dy), b)


def talk(t, a='n', b='wow', speed=7):
    """boca que se mueve (alterna gestos)."""
    return a if int(t * speed) % 2 == 0 else b


def fin(c, mood='day', amb=(1, 1, 1), vig=.35):
    c.amb = amb; c.vig = vig
    return G.grade(c.render(), mood)


def confetti(c, t, n=40, seed=3, y1=FLY):
    rnd = random.Random(seed)
    for i in range(n):
        x = (rnd.random() * WW + math.sin(t * 2 + i) * 6) % WW; y = (rnd.random() * y1 + t * (30 + rnd.random() * 30)) % y1
        c.R(int(x), int(y), 2, 2, rnd.choice([(255, 216, 74), (240, 80, 110), (90, 200, 220), (140, 220, 120)]))


def bubble(c, x, y, w, h, tail=(0, 8), col=(252, 252, 250)):
    c.d.rounded_rectangle([x - 1, y - 1, x + w + 1, y + h + 1], radius=5, fill=(20, 14, 30))
    c.d.rounded_rectangle([x, y, x + w, y + h], radius=4, fill=col)
    tx, ty = x + w // 2 + tail[0], y + h
    c.d.polygon([(tx - 3, ty), (tx + 3, ty), (tx + tail[0] // 2, ty + tail[1])], fill=col)


def squiggle(c, x, y, w, t, col=(60, 50, 80)):
    for k in range(w):
        c.d.point((x + k, y + int(math.sin(k * .9 + t * 12) * 1.5)), fill=col)


# ================================================================ escenarios (fondos animados)
def carpa_inside(c, t, lights=True, dark=True):
    """interior de la carpa de noche: lona a rayas, escenario de madera, cortinas, foco y público en silueta."""
    for x in range(0, WW, 20):
        c.d.polygon([(x, 0), (x + 10, 0), (WW / 2 + (x + 5 - WW / 2) * 1.6, 120), (WW / 2 + (x - 5 - WW / 2) * 1.6, 120)], fill=(70, 24, 34) if dark else (150, 40, 50))
        c.d.polygon([(x + 10, 0), (x + 20, 0), (WW / 2 + (x + 15 - WW / 2) * 1.6, 120), (WW / 2 + (x + 5 - WW / 2) * 1.6, 120)], fill=(96, 84, 70) if dark else (220, 200, 160))
    for k in range(0, WW, 14):                                                   # guirnalda de bombillas
        on = (k // 14 + int(t * 4)) % 3 != 0
        y = 16 + int(math.sin(k * .2) * 3)
        c.R(k + 3, y, 3, 3, (255, 220, 120) if on else (120, 90, 60))
        if on and lights: c.light(k + 4, y + 1, 8, 6, (255, 200, 120), .25)
    bg.curtain(c, 0, 46, 120, (150, 26, 50)); bg.curtain(c, WW - 46, 46, 120, (150, 26, 50))
    bg.planks(c, 40, 112, WW - 80, 30, (140, 92, 56), seed=7, pw=6)
    c.R(40, 112, WW - 80, 2, (200, 150, 100)); c.R(40, 142, WW - 80, 4, (70, 44, 30))


def crowd_front(c, t, y=162, laugh=0.0, seed=4, eyes=False):
    rnd = random.Random(seed)
    for i in range(16):
        x = i * 22 + rnd.randint(-4, 4); h = rnd.randint(18, 26)
        dy = int(abs(math.sin(t * 10 + i)) * 4 * laugh)
        col = rnd.choice([(18, 10, 28), (26, 14, 38), (14, 8, 24)])
        c.d.ellipse([x - 8, y - h - dy, x + 8, y - h + 14 - dy], fill=col); c.d.rounded_rectangle([x - 12, min(WH + 3, y - h + 10 - dy), x + 12, WH + 4], radius=6, fill=col)
        if eyes and int(t * 2 + i) % 7: c.R(x - 4, y - h + 5 - dy, 2, 2, (240, 240, 250)); c.R(x + 2, y - h + 5 - dy, 2, 2, (240, 240, 250))
        if laugh > .3 and (i + int(t * 6)) % 3 == 0: c.R(x - 13, y - h + 2 - dy, 3, 6, col); c.R(x + 10, y - h - 2 - dy, 3, 8, col)   # brazos arriba


def spotlight(c, x, t, w=60, k=1.0):
    bg.beam(c, x + math.sin(t * .7) * 2, 0, 10, w, FLY + 2, (255, 246, 210), int(40 * k))


def world_day(c, t, cam=0.0, sunset=False):
    top, mid, low = ((60, 60, 150), (240, 140, 120), (255, 210, 150)) if sunset else ((88, 150, 238), (150, 200, 250), (236, 240, 250))
    G.sky(c, [(0, top), (.6, mid), (1, low)], 0, FLY, bands=8)
    G.clouds(c, t, 26, (255, 236, 220) if sunset else (250, 252, 255), n=5, seed=2, speed=1.6)
    G.mountains(c, int(FLY * .78), int(FLY * .42), (150, 120, 170) if sunset else (150, 176, 222), seed=4, off=cam * .2, snow=(250, 252, 255))
    G.haze(c, 0, int(FLY * .8), mid, .3)
    G.meadow(c, int(FLY * .97), int(FLY * .1), (120, 160, 100) if sunset else (120, 196, 110), seed=3, off=cam * .45)
    G.tree_line(c, int(FLY * .98), (80, 120, 90) if sunset else (72, 158, 98), seed=6, off=cam * .55, size=12)
    G.blocks(c, -int(cam % 16) - 16, FLY, WW + 48, WH - FLY + 4, (176, 124, 82) if not sunset else (160, 110, 90), tile=16, seed=11, grass=(102, 206, 86) if not sunset else (110, 170, 90), t=t)


def city_1911(c, t, cam=0.0, night=False):
    G.sky(c, [(0, (40, 40, 100) if night else (250, 190, 140)), (1, (90, 70, 130) if night else (250, 230, 190))], 0, FLY, bands=7)
    if night: stars(c, t, 40, 5, 60)
    c.d.ellipse([230, 30, 270, 70], fill=(170, 120, 110) if not night else (60, 50, 90))      # cúpula a lo lejos
    c.R(246, 18, 8, 14, (170, 120, 110) if not night else (60, 50, 90)); c.R(249, 10, 2, 9, (120, 90, 80))
    G.haze(c, 0, FLY - 30, (250, 220, 180) if not night else (70, 60, 120), .35)
    x = -int(cam) % 70 - 70
    cols = [(214, 150, 110), (190, 120, 100), (226, 190, 140), (170, 110, 90), (200, 170, 120)]
    i = 0
    while x < WW + 70:
        h = 50 + (i * 17) % 26; col = cols[i % len(cols)]
        c.R(x, FLY - h, 66, h, col); c.R(x, FLY - h, 66, 3, G.dark(col, .8))
        for wx in (x + 10, x + 40):
            c.R(wx, FLY - h + 14, 12, 16, (40, 30, 40) if not night else ((255, 210, 120) if (i + wx) % 3 else (40, 30, 40)))
            c.R(wx - 1, FLY - h + 30, 14, 2, G.dark(col, .6))
        c.R(x + 26, FLY - 28, 12, 28, (90, 60, 50))
        x += 70; i += 1
    bg.cobble(c, 0, FLY, WW, WH - FLY, (120, 110, 120) if not night else (60, 60, 90), seed=9)


# ================================================================ 0 · gancho y 3 · la noche en blanco
def _stage_wide(T, tl, k, frozen=True, laugh=0.0):
    c = cv(); carpa_inside(c, T); spotlight(c, 160, T, 70)
    jit = math.sin(T * 40) * .6 if frozen else 0
    chibi(c, 'cant_y', 160 + jit, FLY - 2, T, f=.85)
    crowd_front(c, T, laugh=laugh, eyes=frozen)
    return fin(c, 'dark' if frozen else 'day', (.9, .9, 1.05), .55)


def _stage_close(T, tl, k):
    c = cv(); carpa_inside(c, T)
    face(c, 'cant_y', 'worry', T, sc=1.75)
    for i in range(3):                                                           # gotas de sudor
        yy = (tl * 40 + i * 25) % 60
        c.R(196 + i * 3, 70 + int(yy), 2, 3, (190, 230, 255))
    return fin(c, 'dark', (.9, .92, 1.08), .7)


def _stage_eyes(T, tl, k):
    c = cv('#06040c', '#140a1c'); crowd_front(c, T, y=150, eyes=True, seed=9); crowd_front(c, T + 1, y=182, eyes=True, seed=2)
    c.light(160, 10, 120, 30, (255, 240, 200), .3)
    return fin(c, 'dark', (.85, .85, 1.0), .7)


stage = [_stage_wide, _stage_close, _stage_eyes]
freeze = [_stage_close, lambda T, tl, k: _stage_wide(T, tl, k, True), _stage_eyes, _stage_close]


def _title(T, tl, k):
    cam = T * 14; c = cv(); world_day(c, T, cam)
    chibi(c, 'cant_y', 90 + math.sin(T) * 4, FLY + 2, T, walk=True, f=.8)
    chibi(c, 'senora', 230, FLY + 2, T + .3, f=.62, flip=True); chibi(c, 'abuelo', 262, FLY + 2, T + .7, f=.62, flip=True)
    return fin(c, 'day')


def _title_b(T, tl, k):
    c = cv(); carpa_inside(c, T, dark=False); spotlight(c, 160, T, 90)
    body(c, 'cant_y', 160, FB, gesture(T, ('stand', 'toss'), 2.0))
    crowd_front(c, T, laugh=.6)
    return fin(c, 'day', (1.05, 1.0, .95), .4)


title = [_title, _title_b]


# ================================================================ 1 · el niño que no tenía nada
def _city_walk(T, tl, k):
    cam = T * 10; c = cv(); city_1911(c, T, cam)
    chibi(c, 'cant_k', 150, FLY + 6, T, walk=True, f=.6)
    if k % 2: chibi(c, 'senora', 240, FLY + 6, T + .4, walk=True, f=.6, flip=True)
    return fin(c, 'day', (1.04, 1.0, .94), .4)


def _city_close(T, tl, k):
    c = cv(); city_1911(c, T, 40, night=k % 2 == 1)
    face(c, 'cant_k', 'sad' if k % 2 == 0 else 'n', T, sc=1.7)
    return fin(c, 'dark' if k % 2 else 'day', (1, .97, .95), .5)


def _city_window(T, tl, k):
    c = cv(); city_1911(c, T, 80, night=True)
    chibi(c, 'cant_k', 120, FLY + 6, T, f=.6)
    for i in range(4):                                                           # monedas que no llegan
        x = 190 + i * 18; y = FLY - 10 - abs(math.sin(T * 3 + i)) * 10
        c.d.ellipse([x, y, x + 6, y + 6], fill=(255, 210, 80)); c.d.point((x + 2, y + 2), fill=(255, 250, 200))
    c.d.line([(178, FLY - 30), (250, FLY + 4)], fill=(220, 60, 60), width=2)
    return fin(c, 'dark', (1, .95, 1.05), .5)


city = [_city_walk, _city_close, _city_walk, _city_window]


def ring_bg(c, t):
    c.R(0, 0, WW, WH, (20, 16, 30))
    for x in range(0, WW, 40): bg.beam(c, x + 20, 0, 6, 40, 110, (255, 246, 210), 18)
    crowd_front(c, t, y=120, laugh=.4, seed=6)
    c.R(30, 112, WW - 60, 40, (60, 90, 160)); c.R(30, 112, WW - 60, 3, (120, 160, 230))
    for y in (70, 84, 98):                                                       # cuerdas
        c.R(30, y, WW - 60, 2, (230, 60, 60) if y != 84 else (250, 250, 250))
    for x in (30, WW - 32): c.R(x, 60, 4, 56, (200, 200, 210))


def _box_fight(T, tl, k):
    c = cv(); ring_bg(c, T)
    body(c, 'cant_box', 130 + math.sin(T * 5) * 3, 150, gesture(T, ('box', 'stand'), 4.0), f=.8)
    body(c, 'dueno', 200 + math.sin(T * 5 + 1) * 3, 150, gesture(T + .2, ('box', 'stand'), 4.0), flip=True, f=.8, outfit='boxer')
    if int(T * 4) % 2: c.R(160, 60, 8, 8, (255, 240, 140)); c.light(164, 64, 20, 20, (255, 240, 160), .5)
    return fin(c, 'day', (1.05, 1, .95), .45)


def _box_close(T, tl, k):
    c = cv(); ring_bg(c, T)
    face(c, 'cant_box', talk(T, 'worry', 'n', 3), T, sc=1.7)
    return fin(c, 'day', (1.05, 1, .95), .5)


boxing = [_box_fight, _box_close]


def bullring_bg(c, t):
    G.sky(c, [(0, (88, 150, 238)), (1, (236, 240, 250))], 0, 90, bands=6)
    c.R(0, 60, WW, 50, (200, 60, 50)); c.R(0, 60, WW, 3, (250, 240, 220))
    crowd_front(c, t, y=96, laugh=.5, seed=8)
    c.R(0, 96, WW, 14, (150, 40, 40)); c.R(0, 96, WW, 2, (250, 240, 220))
    c.R(0, 110, WW, WH - 110, (226, 196, 140))
    for i in range(30): c.d.point(((i * 37) % WW, 112 + (i * 23) % 60), fill=(200, 170, 120))


def _bull(c, x, y, t, flip=False):
    s = -1 if flip else 1; leg = int(math.sin(t * 16) * 2)
    c.d.ellipse([x - 16, y - 16, x + 16, y + 2], fill=(30, 24, 30))
    c.d.ellipse([x + s * 12 - 7, y - 20, x + s * 12 + 7, y - 6], fill=(30, 24, 30))
    c.d.line([(x + s * 8, y - 18), (x + s * 4, y - 24)], fill=(240, 236, 220), width=2); c.d.line([(x + s * 16, y - 18), (x + s * 20, y - 24)], fill=(240, 236, 220), width=2)
    for lx in (-10, -4, 6, 12): c.R(x + lx, y, 3, 8 + (leg if lx % 2 else -leg), (30, 24, 30))
    c.R(x + s * 14, y - 14, 2, 2, (255, 80, 80))


def _bull_run(T, tl, k):
    c = cv(); bullring_bg(c, T)
    bx = 40 + (tl * 70) % 260
    body(c, 'cant_tor', 190, 160, 'toss' if abs(bx - 190) < 40 else 'hip', f=.75, rot=12 if abs(bx - 190) < 30 else 0)
    cape = [(200, 120), (226 + math.sin(T * 6) * 6, 116), (230 + math.sin(T * 6) * 8, 150), (204, 150)]
    c.d.polygon(cape, fill=(220, 30, 50))
    _bull(c, bx, 150, T)
    if abs(bx - 190) < 40: c.R(170, 70, 20, 4, (255, 255, 255))
    return fin(c, 'day', (1.05, 1.0, .95), .4)


def _bull_close(T, tl, k):
    c = cv(); bullring_bg(c, T)
    face(c, 'cant_tor', ('wow', 'worry', 'n')[k % 3], T, sc=1.7)
    return fin(c, 'day', (1.05, 1, .95), .5)


def _alley(T, tl, k):
    c = cv(); city_1911(c, T, 200 + T * 6, night=True)
    chibi(c, 'cant_y', 100 + tl * 12, FLY + 6, T, walk=True, f=.7)
    return fin(c, 'dark', (.95, .95, 1.08), .55)


bullring = [_bull_run, _bull_close, _bull_run, _alley, _alley]


# ================================================================ 2 · la carpa
def _tent_ext(T, tl, k):
    c = cv(); G.sky(c, [(0, (16, 14, 50)), (1, (70, 40, 100))], 0, FLY, bands=6); stars(c, T, 50, 3, 70)
    bg.skyline(c, FLY - 50, FLY - 40, cols=((40, 30, 70), (54, 40, 90)), seed=4, t=T)
    c.d.polygon([(80, FLY), (160, 26), (240, FLY)], fill=(180, 40, 50))
    for i in range(8):
        a, b = 80 + i * 20, 90 + i * 20
        if i % 2: c.d.polygon([(a, FLY), (160, 26), (b, FLY)], fill=(240, 220, 180))
    c.R(150, 18, 2, 10, (70, 60, 60)); c.d.polygon([(152, 18), (166, 21), (152, 24)], fill=(255, 216, 74))
    c.R(140, FLY - 34, 40, 34, (40, 20, 30)); c.light(160, FLY - 18, 30, 24, (255, 200, 120), .6)
    for k_ in range(0, 160, 10):                                                 # cuerdas con bombillas
        for side in (-1, 1):
            x = 160 + side * k_; y = 26 + k_ * .7
            on = (k_ // 10 + int(T * 5)) % 2
            c.R(int(x), int(y), 2, 2, (255, 220, 120) if on else (120, 90, 60))
            if on: c.light(x, y, 6, 6, (255, 210, 130), .25)
    bg.wtext(c, 160, 6, 'CARPA', (255, 216, 74), size=12, center=True, emissive=True)
    G.blocks(c, -8, FLY, WW + 16, WH - FLY + 4, (110, 90, 100), tile=14, seed=21, t=T)
    for i, w in enumerate(('senora', 'abuelo', 'dueno')):
        x = (40 + i * 60 + tl * 18) % 340 - 10
        chibi(c, w, x, FLY + 4, T + i, walk=True, f=.55)
    return fin(c, 'day', (1, .95, 1.05), .45)


def _tent_show(T, tl, k):
    c = cv(); carpa_inside(c, T, dark=False); spotlight(c, 160, T, 80)
    body(c, 'cant_y', 150, FB - 26, gesture(T, ('stand', 'hip', 'toss'), 2.0), f=.8)
    crowd_front(c, T, laugh=.3 + .3 * math.sin(T))
    return fin(c, 'day', (1.05, 1, .95), .4)


def _tent_crowd(T, tl, k):
    c = cv(); carpa_inside(c, T, dark=False)
    for i, w in enumerate(('senora', 'abuelo', 'dueno', 'senora')):
        chibi(c, w, 60 + i * 66, FLY + 22, T + i, f=.7, bounce=2.0 * (k % 2), flip=i % 2 == 1)
    crowd_front(c, T, y=196, laugh=.5)
    return fin(c, 'day', (1.05, 1, .95), .4)


carpa = [_tent_ext, _tent_show, _tent_crowd, _tent_show]


def _vale_meet(T, tl, k):
    c = cv(); carpa_inside(c, T, dark=False)
    approach = min(1, tl / 2.5)
    chibi(c, 'cant_y', 110 + 24 * ease(approach), FLY - 2, T, walk=approach < 1, f=.8)
    chibi(c, 'valentina', 210 - 20 * ease(approach), FLY - 2, T + .5, walk=approach < 1, f=.8, flip=True)
    if approach >= 1:
        for i in range(3):
            y = 50 - ((tl * 20 + i * 12) % 40); x = 160 + math.sin(tl * 3 + i) * 8
            c.d.polygon([(x, y + 4), (x - 4, y), (x - 2, y - 2), (x, y), (x + 2, y - 2), (x + 4, y)], fill=(240, 80, 110))
    return fin(c, 'day', (1.06, 1, .96), .4)


def _vale_close(T, tl, k):
    c = cv(); carpa_inside(c, T, dark=False)
    face(c, 'valentina', 'smile', T, x=110, sc=1.5); face(c, 'cant_y', 'n' if k % 2 else 'smile', T + .7, x=214, sc=1.5)
    return fin(c, 'day', (1.06, 1, .96), .5)


valentina = [_vale_meet, _vale_close, _vale_meet]


# ================================================================ 3 · la noche en blanco
def _backstage(T, tl, k):
    c = cv(); c.R(0, 0, WW, WH, (40, 26, 30))
    bg.curtain(c, 180, 140, 150, (150, 26, 50))
    c.R(0, 150, WW, 30, (60, 40, 30)); bg.planks(c, 0, 150, 180, 30, (110, 74, 48), seed=2)
    for i in range(3): c.R(20 + i * 50, 40, 30, 80, (60, 50, 50)); c.R(22 + i * 50, 42, 26, 40, (120, 110, 100))     # baúles / espejos
    pace = math.sin(tl * 1.6) * 40
    body(c, 'cant_y', 100 + pace, 176, gesture(T, ('hip', 'hold'), 1.5), flip=math.cos(tl * 1.6) < 0, f=.85)
    c.light(260, 90, 70, 70, (255, 240, 200), .6)
    return fin(c, 'dark', (1, .95, .95), .6)


backstage = [_backstage, _stage_eyes]


def _babble_wide(T, tl, k):
    c = cv(); carpa_inside(c, T); spotlight(c, 160, T, 80)
    body(c, 'cant_y', 160 + math.sin(T * 3) * 6, FB - 26, gesture(T, ('toss', 'hip', 'hold', 'stand', 'box'), 6.0), f=.8)
    for i in range(3):                                                           # burbujas de palabras sin sentido
        ph = (tl * .9 + i * .33) % 1
        x, y = 60 + i * 80, 30 + int(ph * 10)
        bubble(c, x, y, 46, 16)
        squiggle(c, x + 5, y + 6, 36, T + i)
        c.d.text((x + 38, y + 3), '?' if i % 2 else '!', fill=(220, 60, 80))
    crowd_front(c, T, laugh=min(1, tl / 3))
    return fin(c, 'day', (1, .97, 1), .45)


def _babble_close(T, tl, k):
    c = cv(); carpa_inside(c, T)
    face(c, 'cant_y', talk(T, 'n', 'wow', 8), T, sc=1.75)
    bubble(c, 214, 20, 70, 22); squiggle(c, 220, 30, 58, T)
    return fin(c, 'day', (1, .97, 1), .5)


babble = [_babble_wide, _babble_close]


def _laugh_crowd(T, tl, k):
    c = cv(); carpa_inside(c, T, dark=False)
    for i, w in enumerate(('senora', 'abuelo', 'dueno', 'valentina')):
        chibi(c, w, 60 + i * 66, FLY + 22, T + i * .3, f=.7, bounce=5.0, flip=i % 2 == 1)
    crowd_front(c, T, y=196, laugh=1.0)
    confetti(c, T, 30)
    return fin(c, 'day', (1.08, 1.02, .95), .35)


def _laugh_bow(T, tl, k):
    c = cv(); carpa_inside(c, T, dark=False); spotlight(c, 160, T, 80)
    bow = 18 * max(0, math.sin(tl * 2))
    body(c, 'cant_y', 160, FB - 26, 'stand', f=.8, rot=-bow)
    crowd_front(c, T, laugh=1.0); confetti(c, T, 40, 7)
    return fin(c, 'day', (1.08, 1.02, .95), .35)


laugh = [_laugh_crowd, _laugh_bow]


def _name_shout(T, tl, k):
    c = cv(); carpa_inside(c, T, dark=False)
    body(c, 'cant_y', 110, FB - 26, gesture(T, ('stand', 'hip'), 1.5), f=.8)
    chibi(c, 'abuelo', 250, FLY + 22, T, f=.75, bounce=3.0, flip=True)
    if tl > .4:
        bubble(c, 186, 22, 112, 26, tail=(20, 10))
        bg.wtext(c, 242, 28, '¡EN LA CANTINA', (40, 30, 50), size=8, outline=None, center=True)
        bg.wtext(c, 242, 37, 'TE INFLAS!', (200, 40, 60), size=8, outline=None, center=True)
    crowd_front(c, T, y=196, laugh=.8)
    return fin(c, 'day', (1.05, 1, .95), .4)


def _name_sign(T, tl, k):
    c = cv(); carpa_inside(c, T); spotlight(c, 160, T, 120, 1.2)
    n = 'CANTINFLAS'
    vis = n[:max(1, min(len(n), int(tl * 9)))]
    c.R(60, 26, 200, 40, (30, 16, 30)); c.R(62, 28, 196, 36, (60, 24, 40))
    for i in range(0, 196, 8):
        on = (i // 8 + int(T * 8)) % 2
        c.R(62 + i, 28, 3, 2, (255, 220, 120) if on else (120, 80, 60)); c.R(62 + i, 62, 3, 2, (255, 220, 120) if not on else (120, 80, 60))
    bg.wtext(c, 160, 35, vis, (255, 216, 74), size=16, center=True, emissive=True)
    chibi(c, 'cant_y', 160, FLY + 4, T, f=.8, bounce=2.0)
    crowd_front(c, T, laugh=.9)
    return fin(c, 'day', (1.05, 1, .98), .45)


name = [_name_shout, _name_sign, _name_sign]


# ================================================================ 4 · el cine dice que no
def _cine_ext(T, tl, k):
    c = cv(); city_1911(c, T, 300, night=True)
    c.R(90, 30, 140, 110, (70, 40, 50)); c.R(90, 30, 140, 4, (120, 70, 80))
    c.R(100, 40, 120, 22, (30, 16, 30))
    bg.wtext(c, 160, 44, 'CINE', (255, 216, 74), size=12, center=True, emissive=True)
    for i in range(0, 120, 6):
        on = (i // 6 + int(T * 3)) % 2
        c.R(100 + i, 62, 3, 2, (255, 220, 120) if on else (90, 60, 50))
    c.R(110, 74, 34, 46, (240, 230, 200)); face_im = scaled(bust('cant_y', 'smile', (0, 0), 1.0, 1.0), .38)
    c.im.paste(face_im, (127 - face_im.width // 2, 118 - face_im.height), face_im)
    bg.wtext(c, 127, 108, '1936', (40, 30, 40), size=8, outline=None, center=True)
    c.R(150, 90, 40, 50, (20, 12, 20))
    chibi(c, 'abuelo', 260 - tl * 10, FLY + 6, T, walk=True, f=.55, flip=True)
    return fin(c, 'dark', (.95, .95, 1.05), .55)


def _cine_in(T, tl, k):
    c = cv('#0a0810', '#140c18')
    c.R(50, 10, 220, 90, (200, 204, 220)); c.light(160, 55, 110, 50, (220, 230, 255), .5)
    fl = 1 if int(T * 12) % 5 else .9
    sc_im = scaled(bust('cant_y', talk(T, 'n', 'wow', 3), (0, 0), T, 1.0), .7)
    c.im.paste(sc_im, (160 - sc_im.width // 2, 98 - sc_im.height), sc_im)
    for r, y in enumerate((120, 140, 160)):
        for x in range(10, WW, 22): c.R(x, y, 18, 14, (120, 24, 40)); c.R(x, y, 18, 2, (170, 50, 60))
    chibi(c, 'abuelo', 230, 158, T, f=.5)
    for i in range(3):                                                           # zzz
        y = 100 - ((tl * 10 + i * 8) % 24)
        bg.wtext(c, 244 + i * 4, int(y), 'z', (230, 230, 250), size=8, outline=None)
    return fin(c, 'dark', (fl, fl, fl * 1.05), .6)


cine = [_cine_ext, _cine_in, _cine_in, _cine_ext]


def _rain_walk(T, tl, k):
    c = cv(); city_1911(c, T, 400 + T * 8, night=True)
    bg.lamp_post(c, 220, FLY + 6, T)
    c.light(220, FLY - 60, 40, 60, (255, 220, 150), .4)
    chibi(c, 'cant_y', 90 + tl * 14, FLY + 6, T, walk=True, f=.7)
    rain(c, T, 90)
    return fin(c, 'dark', (.9, .92, 1.1), .6)


def _rain_close(T, tl, k):
    c = cv(); city_1911(c, T, 450, night=True); rain(c, T, 60)
    face(c, 'cant_y', 'sad' if tl < 1.2 else 'n', T, sc=1.75)
    return fin(c, 'dark', (.9, .92, 1.1), .6)


rain_ = [_rain_walk, _rain_close]


def _costume(T, tl, k):
    c = cv('#2a1e30', '#3c2a3a')
    bg.wallpaper(c, 0, 0, WW, 150, (90, 60, 80), (80, 54, 72), (120, 80, 100))
    c.R(0, 150, WW, 30, (90, 60, 40)); bg.planks(c, 0, 150, WW, 30, (120, 80, 50), seed=3)
    c.R(214, 30, 60, 100, (160, 120, 70)); c.R(218, 34, 52, 92, (180, 210, 230))   # espejo
    c.light(160, 30, 120, 40, (255, 240, 210), .5)
    body(c, 'cant_y', 140, 176, gesture(T, ('stand', 'hip'), 1.0), f=.9)
    labels = [('GABARDINA', 66, 92, 127, 102), ('SOGA', 80, 116, 132, 126), ('PANTALÓN CAÍDO', 62, 134, 132, 140), ('BIGOTE', 222, 80, 144, 94)]
    for i, (txt, lx, ly, ax, ay) in enumerate(labels):
        if tl > .5 + i * .7 or k > 0:
            ex = lx + (len(txt) * 3 + 2 if lx < 160 else -len(txt) * 3 - 2)
            c.d.line([(ex, ly + 4), (ax, ay)], fill=(255, 216, 74)); c.R(ax - 1, ay - 1, 3, 3, (255, 216, 74))
            bg.wtext(c, lx, ly, txt, (255, 216, 74), size=8, center=True)
    return fin(c, 'day', (1.04, 1, .96), .4)


def _costume_close(T, tl, k):
    c = cv('#2a1e30', '#3c2a3a'); bg.wallpaper(c, 0, 0, WW, 180, (90, 60, 80), (80, 54, 72), (120, 80, 100))
    face(c, 'cant_y', 'smile' if k % 2 else 'n', T, sc=1.75)
    return fin(c, 'day', (1.04, 1, .96), .45)


costume = [_costume, _costume, _costume, _costume_close]


# ================================================================ 5 · ahí está el detalle (1940)
def _premiere(T, tl, k, close=False):
    c = cv(); G.sky(c, [(0, (10, 10, 40)), (1, (60, 30, 90))], 0, FLY, bands=6); stars(c, T, 50, 3, 80)
    for i in range(3):
        a = math.sin(T * .8 + i * 2) * 50
        bg.beam(c, 60 + i * 100 + int(a), 0, 4, 30, FLY, (255, 246, 210), 22)
    c.R(40, 30, 240, 110, (70, 40, 60)); c.R(50, 36, 220, 28, (30, 16, 30))
    bg.wtext(c, 160, 40, 'AHÍ ESTÁ EL DETALLE', (255, 216, 74), size=10, center=True, emissive=True)
    for i in range(0, 220, 6):
        on = (i // 6 + int(T * 8)) % 2
        c.R(50 + i, 66, 3, 2, (255, 220, 120) if on else (120, 80, 60)); c.R(50 + i, 34, 3, 2, (255, 220, 120) if not on else (120, 80, 60))
    c.R(0, FLY, WW, WH - FLY, (150, 20, 40)); c.R(0, FLY, WW, 2, (220, 70, 80))
    if close: face(c, 'cant_y', 'smile', T, sc=1.75)
    else:
        chibi(c, 'cant_y', 160, FLY + 10, T, f=.8, bounce=1.5)
        for i, w in enumerate(('senora', 'abuelo', 'dueno', 'valentina', 'senora', 'abuelo')):
            x = 30 + i * 52 + (14 if i >= 3 else 0)
            if abs(x - 160) > 24: chibi(c, w, x, FLY + 30, T + i, f=.55, bounce=3.0, flip=x > 160)
    if (T * 1.2) % 1 < .04: c.light(160, 90, 200, 120, (255, 255, 255), .5)        # flash de cámara breve
    for i in range(4):
        if (int(T * 5) + i) % 6 == 0: c.d.ellipse([20 + i * 80, 120, 28 + i * 80, 128], fill=(255, 255, 255))
    return fin(c, 'day', (1.06, 1.02, .96), .4)


estreno = [_premiere, lambda T, tl, k: _premiere(T, tl, k, True), _premiere, lambda T, tl, k: _premiere(T, tl, k, True)]


# ================================================================ 6 · Hollywood
def _palm(c, x, yb, t, h=60):
    sw = math.sin(t * 1.2 + x) * 2
    for k in range(h):
        c.R(int(x + math.sin(k * .05) * 4), yb - k, 4, 1, (130, 90, 60) if k % 6 else (100, 70, 50))
    tx, ty = x + math.sin(h * .05) * 4 + 2, yb - h
    for a in range(0, 360, 45):
        r = math.radians(a + sw * 3)
        c.d.line([(tx, ty), (tx + math.cos(r) * 18, ty + math.sin(r) * 8 + 4)], fill=(60, 150, 80), width=3)


def hollywood_bg(c, t, cam=0):
    G.sky(c, [(0, (70, 150, 240)), (1, (250, 220, 170))], 0, FLY, bands=8)
    G.clouds(c, t, 20, (255, 255, 255), n=4, seed=5, speed=1.4)
    G.mountains(c, FLY - 30, 50, (170, 150, 120), seed=8, off=cam * .2)
    G.haze(c, 0, FLY - 20, (250, 220, 170), .3)
    for i, x in enumerate((20, 120, 220)):                                       # naves de estudio
        c.R(x, FLY - 60, 80, 60, (226, 220, 206)); c.d.polygon([(x - 4, FLY - 60), (x + 84, FLY - 60), (x + 40, FLY - 80)], fill=(200, 190, 176))
        bg.wtext(c, x + 40, FLY - 50, str(i + 1), (90, 80, 70), size=12, center=True, outline=None)
        c.R(x + 30, FLY - 24, 20, 24, (110, 100, 90))
    for x in (100, 210, 300): _palm(c, x, FLY, t)
    c.R(0, FLY, WW, WH - FLY, (120, 120, 130)); c.R(0, FLY, WW, 2, (200, 200, 210))


def _hw_walk(T, tl, k):
    c = cv(); hollywood_bg(c, T, T * 6)
    chibi(c, 'cant', 70 + tl * 18, FLY + 14, T, walk=True, f=.75)
    chibi(c, 'todd', 230, FLY + 14, T, f=.75, flip=True)
    PR.keep(c, PR.clapper(), 262, FLY + 10)
    return fin(c, 'day', (1.05, 1.02, .95), .35)


def _hw_meet(T, tl, k):
    c = cv(); hollywood_bg(c, T)
    body(c, 'todd', 210, FB + 4, gesture(T, ('hold', 'toss', 'stand'), 1.5), flip=True, f=.85)
    body(c, 'cant', 110, FB + 4, gesture(T + .3, ('stand', 'hip'), 1.2), f=.85)
    if k % 2: bubble(c, 220, 16, 40, 18); bg.wtext(c, 240, 20, '¡TÚ!', (200, 40, 60), size=8, outline=None, center=True)
    return fin(c, 'day', (1.05, 1.02, .95), .35)


hollywood = [_hw_walk, _hw_meet, _hw_meet]


def _balloon(T, tl, k):
    cam = T * 30; c = cv(); world_day(c, T, cam)
    bx, by = 160 + math.sin(T * .7) * 20, 60 + math.sin(T * 1.1) * 6
    c.d.ellipse([bx - 30, by - 50, bx + 30, by + 10], fill=(220, 60, 60))
    for i in range(-2, 3): c.d.line([(bx + i * 11, by - 48), (bx + i * 8, by + 8)], fill=(250, 210, 80), width=2)
    c.d.line([(bx - 14, by + 8), (bx - 8, by + 24)], fill=(80, 60, 40)); c.d.line([(bx + 14, by + 8), (bx + 8, by + 24)], fill=(80, 60, 40))
    if int(T * 6) % 2: c.d.polygon([(bx - 3, by + 18), (bx + 3, by + 18), (bx, by + 10)], fill=(255, 200, 60)); c.light(bx, by + 14, 10, 10, (255, 200, 120), .5)
    head = scaled(rpg('cant_pp', 0), .55); c.im.paste(head.crop((0, 0, head.width, 26)), (int(bx - head.width / 2), int(by + 6)), head.crop((0, 0, head.width, 26)))
    c.R(int(bx - 12), int(by + 24), 24, 12, (150, 100, 60)); c.R(int(bx - 12), int(by + 24), 24, 2, (200, 150, 90))
    return fin(c, 'day', (1.04, 1.02, .96), .35)


balloon = [_balloon]


def _awards(T, tl, k, close=False):
    c = cv('#140a20', '#24123a')
    bg.curtain(c, 0, 70, 150, (160, 30, 60)); bg.curtain(c, WW - 70, 70, 150, (160, 30, 60))
    c.R(0, 140, WW, 40, (60, 30, 50)); c.R(0, 140, WW, 2, (250, 210, 120))
    if not close: spotlight(c, 160, T, 90, 1.2)
    if close:
        face(c, 'cant', 'smile', T, sc=1.75)
        st = scaled(PR.statuette(40), 1.0); c.im.paste(st, (230, 150 - st.height), st); c.light(240, 120, 30, 40, (255, 220, 120), .6)
    else:
        body(c, 'cant', 160, 176, 'trophy' if k % 2 else gesture(T, ('stand', 'toss'), 1.2), f=.85)
        st = scaled(PR.statuette(30), 1.0); c.im.paste(st, (100, 140 - st.height), st)
        c.d.ellipse([214, 112, 230, 128], fill=(240, 200, 80)); c.R(220, 128, 4, 10, (200, 160, 60)); c.R(214, 138, 16, 3, (200, 160, 60))  # globo dorado
        c.light(222, 120, 20, 20, (255, 220, 120), .5)
    confetti(c, T, 40, 9, 140)
    return fin(c, 'day', (1.05, 1.0, 1.0), .4)


oscar = [_awards, lambda T, tl, k: _awards(T, tl, k, True), _awards, lambda T, tl, k: _awards(T, tl, k, True)]


# ================================================================ 7 · el tropiezo
def _pepe(T, tl, k, close=False):
    c = cv('#0a0810', '#140c18')
    c.R(40, 20, 240, 80, (150, 150, 170))
    bg.wtext(c, 160, 48, 'PEPE', (60, 60, 80), size=16, center=True, outline=None)
    for r, y in enumerate((112, 132, 152)):
        for x in range(10, WW, 22): c.R(x, y, 18, 14, (90, 24, 40)); c.R(x, y, 18, 2, (130, 40, 50))
    if close: face(c, 'cant', 'sad', T, sc=1.75)
    else:
        body(c, 'cant', 160, 178, 'stand', f=.8)
        for i in range(6):                                                       # nube de lluvia sobre la cabeza
            c.d.ellipse([140 + i * 6, 30 + (i % 2) * 3, 154 + i * 6, 42 + (i % 2) * 3], fill=(90, 90, 110))
        for i in range(8): c.R(142 + (i * 5), 44 + int((T * 60 + i * 13) % 40), 1, 3, (150, 170, 220))
    return fin(c, 'dark', (.9, .9, 1.05), .6)


pepe = [_pepe, lambda T, tl, k: _pepe(T, tl, k, True), _pepe]


def _home(T, tl, k):
    cam = T * 8; c = cv(); city_1911(c, T, cam)
    chibi(c, 'cant', 80 + tl * 16, FLY + 6, T, walk=True, f=.7)
    for i, w in enumerate(('senora', 'abuelo', 'valentina', 'dueno')):
        chibi(c, w, 200 + i * 30, FLY + 6, T + i * .2, f=.6, bounce=3.0, flip=True)
    for i in range(4):
        y = 60 - ((tl * 18 + i * 10) % 40)
        x = 230 + i * 20 + math.sin(tl * 3 + i) * 4
        c.d.polygon([(x, y + 4), (x - 4, y), (x - 2, y - 2), (x, y), (x + 2, y - 2), (x + 4, y)], fill=(240, 80, 110))
    return fin(c, 'day', (1.08, 1.0, .92), .35)


def _home_close(T, tl, k):
    c = cv(); city_1911(c, T, 60)
    face(c, 'cant', 'smile', T, sc=1.75)
    return fin(c, 'day', (1.08, 1.0, .92), .45)


home = [_home, _home_close, _home]


# ================================================================ 8 · la palabra, el adiós y el final
def _dictionary(T, tl, k, close=False):
    c = cv('#2a2030', '#1a1420')
    bg.shelf(c, 0, 0, WW, 110, seed=4)
    c.R(0, 110, WW, 70, (90, 60, 40)); c.R(0, 110, WW, 3, (140, 100, 70))
    c.d.polygon([(60, 150), (160, 140), (260, 150), (260, 100), (160, 90), (60, 100)], fill=(250, 246, 232))
    c.d.line([(160, 90), (160, 140)], fill=(200, 190, 170), width=2)
    for i in range(5):
        c.d.line([(72, 104 + i * 8), (150, 96 + i * 8)], fill=(170, 170, 180)); c.d.line([(170, 96 + i * 8), (248, 104 + i * 8)], fill=(170, 170, 180))
    word = 'cantinflear'
    n = len(word) if (k > 1 or close) else max(0, min(len(word), int((tl - .3) * 7)))
    c.R(172, 96, 76, 12, (255, 240, 150))
    bg.wtext(c, 210, 97, word[:n] + ('_' if int(T * 4) % 2 and n < len(word) else ''), (40, 30, 50), size=8, outline=None, center=True)
    c.light(160, 110, 110, 40, (255, 240, 200), .5)
    if close: face(c, 'cant_y', talk(T, 'n', 'wow', 6), T, x=60, sc=1.3)
    return fin(c, 'day', (1.04, 1, .96), .45)


dictionary = [_dictionary, _dictionary, lambda T, tl, k: _dictionary(T, tl, k, True), _dictionary, lambda T, tl, k: _dictionary(T, tl, k, True)]


def _funeral(T, tl, k):
    c = cv(); G.sky(c, [(0, (30, 26, 70)), (.7, (150, 90, 110)), (1, (240, 170, 120))], 0, FLY, bands=7)
    city_1911(c, T, 600, night=True) if False else None
    G.mountains(c, FLY - 20, 50, (60, 50, 90), seed=6)
    c.R(0, FLY, WW, WH - FLY, (50, 40, 50))
    c.R(130, 50, 60, 72, (90, 60, 40)); c.R(134, 54, 52, 64, (40, 30, 40))
    p = scaled(bust('cant_y', 'smile', (0, 0), 1.0, 1.0), .5); c.im.paste(p.crop((0, 0, p.width, 62)), (160 - p.width // 2, 56), p.crop((0, 0, p.width, 62)))
    for i in range(14):                                                          # velas y cempasúchil
        x = 20 + i * 22; fl = math.sin(T * 9 + i) * 1
        c.R(x, FLY - 10, 4, 10, (240, 236, 220)); c.d.ellipse([x, FLY - 15 + fl, x + 4, FLY - 9], fill=(255, 200, 80))
        c.light(x + 2, FLY - 12, 10, 10, (255, 190, 100), .5)
        c.d.ellipse([x + 8, FLY - 6, x + 15, FLY + 1], fill=(250, 150, 30))
    crowd_front(c, T, y=196, laugh=0.0)
    return fin(c, 'dark', (1, .95, 1), .55)


funeral = [_funeral]


def _final_walk(T, tl, k):
    cam = T * 10; c = cv(); world_day(c, T, cam, sunset=True)
    chibi(c, 'cant_y', 160, FLY + 2, T, walk=True, f=.85)
    return fin(c, 'day', (1.05, 1.0, .95), .35)


def _final_wave(T, tl, k):
    c = cv(); world_day(c, T, 200, sunset=True)
    body(c, 'cant_y', 160, FB + 4, gesture(T, ('toss', 'stand'), 2.4), f=.9)
    if tl > 1: stars(c, T, int(min(40, tl * 10)), 6, 60)
    return fin(c, 'day', (1.05, 1.0, .95), .4)


def _final_close(T, tl, k):
    c = cv(); world_day(c, T, 260, sunset=True)
    face(c, 'cant_y', 'smile', T, sc=1.75)
    return fin(c, 'day', (1.05, 1.0, .95), .45)


final = [_final_walk, _final_wave, _final_close, _final_wave]

KITS = dict(stage=stage, title=title, city=city, boxing=boxing, bullring=bullring, carpa=carpa, valentina=valentina, backstage=backstage,
            freeze=freeze, babble=babble, laugh=laugh, name=name, cine=cine, rain=rain_, costume=costume, estreno=estreno, hollywood=hollywood,
            balloon=balloon, oscar=oscar, pepe=pepe, home=home, dictionary=dictionary, funeral=funeral, final=final)
