"""Fondos pixel-art con detalle (estilo RPG): ladrillos, adoquines, tablones, ventanas, estanterías, siluetas de ciudad."""
import math, random
import numpy as np
from PIL import Image, ImageDraw
from lib import *


def jit(c, k, rnd, amt=14):
    return tuple(max(0, min(255, int(v + rnd.randint(-amt, amt) * k))) for v in c)


def brick(c, x0, y0, w, h, base=(150, 80, 64), mortar=(70, 40, 40), seed=1, bh=6, bw=12):
    rnd = random.Random(seed)
    c.R(x0, y0, w, h, mortar)
    for r, y in enumerate(range(y0, y0 + h, bh)):
        off = (bw // 2) if r % 2 else 0
        for x in range(x0 - off, x0 + w, bw):
            xa, xb = max(x0, x + 1), min(x0 + w, x + bw)
            if xb <= xa: continue
            ya, yb = y + 1, min(y0 + h, y + bh)
            if yb <= ya: continue
            col = jit(c, 1, rnd, 18) if False else tuple(max(0, min(255, v + rnd.randint(-16, 16))) for v in base)
            c.R(xa, ya, xb - xa, yb - ya, col)
            c.R(xa, ya, xb - xa, 1, shade(col, 1.18))                      # luz arriba
            c.R(xa, yb - 1, xb - xa, 1, shade(col, .82))                   # sombra abajo
            if rnd.random() < .12: c.R(xa + 2, ya + 2, 2, 1, shade(col, .75))   # mancha


def cobble(c, x0, y0, w, h, base=(78, 80, 120), seed=2):
    rnd = random.Random(seed)
    c.R(x0, y0, w, h, shade(base, .55))
    y = y0; row = 0
    while y < y0 + h:
        rh = 3 + int((y - y0) / h * 5)
        x = x0 - rnd.randint(0, 8)
        while x < x0 + w:
            sw = rnd.randint(7, 11) + int((y - y0) / h * 6)
            col = tuple(max(0, min(255, v + rnd.randint(-14, 14))) for v in base)
            xa, xb = max(x0, x + 1), min(x0 + w, x + sw)
            if xb > xa:
                c.R(xa, y + 1, xb - xa, rh - 1, col); c.R(xa, y + 1, xb - xa, 1, shade(col, 1.25)); c.R(xa, y + rh - 1, xb - xa, 1, shade(col, .75))
            x += sw + 1
        y += rh + 1; row += 1


def planks(c, x0, y0, w, h, base=(150, 98, 62), seed=3, horizontal=True, pw=7):
    rnd = random.Random(seed)
    if horizontal:
        for y in range(y0, y0 + h, pw):
            col = tuple(max(0, min(255, v + rnd.randint(-10, 10))) for v in base)
            c.R(x0, y, w, pw - 1, col); c.R(x0, y, w, 1, shade(col, 1.2)); c.R(x0, y + pw - 1, w, 1, shade(col, .6))
            for _ in range(3):
                gx = rnd.randint(x0, x0 + w - 12); c.R(gx, y + rnd.randint(2, pw - 3), rnd.randint(5, 12), 1, shade(col, .85))
            for nx in range(x0 + rnd.randint(2, 9), x0 + w, rnd.randint(34, 52)): c.R(nx, y + pw // 2, 1, 1, shade(col, .5))
    else:
        for x in range(x0, x0 + w, pw):
            col = tuple(max(0, min(255, v + rnd.randint(-10, 10))) for v in base)
            c.R(x, y0, pw - 1, h, col); c.R(x, y0, 1, h, shade(col, 1.2)); c.R(x + pw - 1, y0, 1, h, shade(col, .6))
            for _ in range(4):
                gy = rnd.randint(y0, y0 + h - 10); c.R(x + rnd.randint(1, pw - 3), gy, 1, rnd.randint(4, 10), shade(col, .85))


def wallpaper(c, x0, y0, w, h, a=(70, 80, 130), b=(62, 72, 120), motif=(90, 104, 160)):
    for x in range(x0, x0 + w, 10):
        c.R(x, y0, 5, h, a); c.R(x + 5, y0, 5, h, b)
    for y in range(y0 + 6, y0 + h, 16):
        for x in range(x0 + 5, x0 + w, 20):
            c.R(x, y, 2, 2, motif); c.R(x - 1, y + 1, 4, 1, motif); c.R(x, y + 2, 2, 2, motif)


def window(c, x, y, w, h, t=0, night=True, curtain=None, rain=True, lights=True, seed=4, glass=((24, 36, 92), (50, 60, 130))):
    rnd = random.Random(seed)
    c.R(x - 3, y - 3, w + 6, h + 6, (110, 74, 48)); c.R(x - 3, y - 3, w + 6, 1, (190, 140, 96)); c.R(x - 3, y + h + 2, w + 6, 1, (70, 44, 30))
    for j in range(h):                                                      # cristal con degradado
        k = j / h; col = tuple(int(glass[0][i] + (glass[1][i] - glass[0][i]) * k) for i in range(3)); c.R(x, y + j, w, 1, col)
    if lights:
        for _ in range(w // 3):
            lx, ly = x + rnd.randint(1, w - 4), y + rnd.randint(h // 2, h - 4)
            c.R(lx, ly, 2, 2, (255, rnd.randint(180, 230), 110))
        c.R(x + 3, y + 3, 3, 3, (240, 240, 255)); c.R(x + w - 9, y + 5, 2, 2, (220, 230, 255))          # luna y estrellas
    if rain:
        for i in range(w // 3):
            ph = ((t * 70 + i * 17) % (h + 8)); xx = x + (i * 7) % (w - 1); yy = y + ph - 4
            if y <= yy < y + h - 3: c.R(xx, yy, 1, 4, (160, 196, 255))
    c.R(x + w // 2 - 1, y, 2, h, (110, 74, 48)); c.R(x, y + h // 2 - 1, w, 2, (110, 74, 48))           # parteluces
    c.R(x, y + h // 2 - 1, w, 1, (190, 140, 96))
    c.R(x - 5, y + h + 3, w + 10, 3, (190, 140, 96)); c.R(x - 5, y + h + 5, w + 10, 1, (90, 56, 38))      # alféizar
    if curtain:
        for sx, dx in ((x - 3, 1), (x + w + 3, -1)):
            for k in range(6):
                col = shade(curtain, 1.15 if k % 2 else .85)
                c.R(sx + (k if dx > 0 else -k - 1), y - 4, 1, h + 8, col)
        c.R(x - 8, y - 6, w + 16, 2, (60, 40, 30))


def shelf(c, x, y, w, h, seed=5, rows=None, pal=None):
    rnd = random.Random(seed)
    pal = pal or ((210, 66, 80), (66, 120, 210), (240, 196, 70), (90, 176, 110), (170, 90, 200), (240, 140, 60), (80, 190, 200))
    c.R(x - 2, y - 2, w + 4, h + 4, (90, 56, 38)); c.R(x, y, w, h, (60, 36, 28))
    rows = rows or max(1, h // 28)
    rh = h // rows
    for r in range(rows):
        by = y + (r + 1) * rh - 3
        c.R(x, by, w, 3, (150, 100, 64)); c.R(x, by, w, 1, (210, 150, 100))
        xx = x + 2
        while xx < x + w - 4:
            bw = rnd.randint(3, 7); bh = rnd.randint(rh - 17, rh - 7); col = rnd.choice(pal)
            if rnd.random() < .1:                                                  # libro inclinado
                c.d.polygon([(xx, by), (xx + bw, by), (xx + bw + 4, by - bh + 3), (xx + 4, by - bh + 3)], fill=col); xx += bw + 4; continue
            c.R(xx, by - bh, bw, bh, col); c.R(xx, by - bh, 1, bh, shade(col, 1.3)); c.R(xx + bw - 1, by - bh, 1, bh, shade(col, .7))
            c.R(xx, by - bh + 2, bw, 1, (250, 224, 150)); c.R(xx, by - 4, bw, 1, shade(col, .65))
            xx += bw + 1
            if rnd.random() < .06: c.R(xx, by - 7, 5, 7, (200, 80, 60)); c.R(xx + 1, by - 9, 3, 2, (90, 170, 100)); xx += 6     # maceta


def lamp_post(c, x, yb, t=0, h=64):
    c.R(x, yb - h, 3, h, (28, 28, 46)); c.R(x - 3, yb - 6, 9, 6, (40, 40, 66)); c.R(x - 1, yb - h + 2, 5, 3, (60, 60, 90))
    c.R(x - 8, yb - h - 2, 14, 2, (28, 28, 46)); c.d.polygon([(x - 7, yb - h - 2), (x + 8, yb - h - 2), (x + 5, yb - h - 12), (x - 4, yb - h - 12)], fill=(255, 214, 120))
    c.R(x - 4, yb - h - 14, 9, 2, (28, 28, 46))
    fl = 1.0 if int(t * 8) % 23 else .75
    c.light(x + 1, yb - h - 6, 44, 52, (255, 210, 120), .85 * fl)


def house(c, x, y0, w, h, wall, roof, seed=6, lit=.4, chimneys=True):
    rnd = random.Random(seed)
    brick(c, x, y0, w, h, base=wall, mortar=shade(wall, .55), seed=seed, bh=5, bw=10)
    c.d.polygon([(x - 3, y0), (x + w + 3, y0), (x + w // 2 + 4, y0 - 12), (x + w // 2 - 4, y0 - 12)], fill=roof)
    c.R(x - 3, y0, w + 6, 2, shade(roof, 1.3))
    for k in range(0, w, 6): c.R(x + k, y0 - 10, 1, 9, shade(roof, .8))
    if chimneys:
        cx = x + rnd.randint(3, max(4, w - 8)); c.R(cx, y0 - 20, 5, 12, shade(wall, .8)); c.R(cx - 1, y0 - 21, 7, 2, shade(wall, 1.1))
    cols = max(1, w // 15)
    for r in range(max(1, h // 22)):
        for k in range(cols):
            wx, wy = x + 4 + k * (w - 8) // cols, y0 + 5 + r * 21
            on = rnd.random() < lit
            c.R(wx - 1, wy - 1, 10, 14, (50, 30, 30)); c.R(wx, wy, 8, 12, (255, 200, 100) if on else (40, 50, 96))
            c.R(wx + 3, wy, 1, 12, (50, 30, 30)); c.R(wx, wy + 5, 8, 1, (50, 30, 30)); c.R(wx - 2, wy + 12, 12, 2, (180, 150, 120))


def castle_sil(c, base_y, col=(30, 26, 70), win=(255, 206, 110)):
    c.d.polygon([(0, base_y + 40), (14, base_y + 4), (40, base_y - 14), (74, base_y - 22), (104, base_y - 20), (132, base_y - 8), (150, base_y + 14), (160, base_y + 40)], fill=shade(col, .85))
    for x0, hh in ((44, 22), (58, 38), (76, 56), (96, 36), (112, 24)):
        c.R(x0, base_y - 22 - hh, 14, hh + 22, col)
        c.d.polygon([(x0 - 1, base_y - 22 - hh), (x0 + 7, base_y - 22 - hh - 13), (x0 + 15, base_y - 22 - hh)], fill=col)
        for k in range(0, 14, 4): c.R(x0 + k, base_y - 22 - hh - 2, 2, 2, col)
        c.R(x0 + 5, base_y - 22 - hh + 8, 3, 6, win, c.ed); 
        if hh > 30: c.R(x0 + 5, base_y - 22 - hh + 22, 3, 6, win, c.ed)
    c.R(40, base_y - 22, 90, 10, shade(col, 1.1))
    for x0 in range(42, 130, 6): c.R(x0, base_y - 25, 3, 3, shade(col, 1.1))
    c.R(78, base_y - 22 - 56 - 20, 1, 10, (200, 200, 220)); c.R(79, base_y - 22 - 56 - 20, 6, 4, (220, 60, 70))   # bandera


def puddle_reflections(c, y0, h, t, col=(120, 110, 200)):
    for i in range(14):
        x = (i * 23 + int(t * 8)) % WW; y = y0 + (i * 9) % h
        c.R(x, y, 10 + i % 7, 1, col)


# ---------------------------------------------------------------- texto pixel-art nítido dentro del mundo (Silkscreen, sin antialias)
from PIL import ImageFont
_FONTS = {}
def _font(size):
    if size not in _FONTS:
        _FONTS[size] = ImageFont.truetype('/home/user/w/tuconfia/assets/fonts/silkscreen-latin-700-normal.woff', size)
    return _FONTS[size]


def text_img(txt, col, size=16, outline=(14, 10, 26)):
    f = _font(size)
    d0 = ImageDraw.Draw(Image.new('L', (1, 1))); w = int(d0.textlength(txt, font=f)) + 4; h = int(size * 1.3) + 4
    m = Image.new('L', (w, h), 0); d = ImageDraw.Draw(m); d.fontmode = '1'; d.text((2, 2), txt, font=f, fill=255)
    a = np.array(m) > 0
    out = np.zeros((h, w, 4), np.uint8)
    if outline is not None:
        p = np.pad(a, 1); dil = np.zeros_like(p)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1): dil |= np.roll(np.roll(p, dy, 0), dx, 1)
        dil = dil[1:-1, 1:-1]
        out[dil & ~a] = (*outline, 255)
    out[a] = (*col, 255)
    return Image.fromarray(out, 'RGBA')


def wtext(c, x, y, txt, col, size=16, outline=(14, 10, 26), emissive=False, center=False):
    im = text_img(txt, col, size, outline)
    if center: x = x - im.width // 2
    tgt = c.emis if emissive else c.im
    tgt.alpha_composite(im, (int(x), int(y))) if x >= 0 and y >= 0 else tgt.paste(im, (int(x), int(y)), im)
    return im.width


def sign2(c, cx, y, txt, col, size=16, plate=(16, 12, 30), emissive=False):
    im = text_img(txt, col, size, None)
    w, h = im.width + 8, im.height + 4
    x = int(cx - w // 2)
    c.R(x, y, w, h, plate); c.R(x, y, w, 1, col); c.R(x, y + h - 1, w, 1, col); c.R(x, y, 1, h, col); c.R(x + w - 1, y, 1, h, col)
    (c.emis if emissive else c.im).alpha_composite(im, (x + 4, y + 2))
    c.light(cx, y + h // 2, w, 28, col, .4)
    return w, h


def bubble2(c, cx, y, txt, size=16, col=(30, 20, 40)):
    im = text_img(txt, col, size, None)
    w, h = im.width + 8, im.height + 4
    x = int(cx - w // 2)
    c.R(x - 1, y - 1, w + 2, h + 2, (20, 14, 30)); c.R(x, y, w, h, (252, 250, 242)); c.R(x, y, w, 1, (255, 255, 255))
    c.d.polygon([(cx - 5, y + h), (cx + 3, y + h), (cx - 1, y + h + 7)], fill=(252, 250, 242))
    c.R(cx - 6, y + h, 1, 1, (20, 14, 30))
    c.im.alpha_composite(im, (x + 4, y + 2))


def van_side(c, x, y, w, h, body=(78, 178, 172), roof=(246, 238, 214), win_lit=True, t=0):
    """furgoneta clásica de lado (se puede salir del cuadro por la derecha)."""
    c.R(x, y + h * 3 // 10, w, h * 7 // 10, body); c.R(x, y + h * 3 // 10, w, 2, shade(body, 1.25))
    c.d.polygon([(x + 4, y + h * 3 // 10), (x + w - 4, y + h * 3 // 10), (x + w - 10, y), (x + 14, y)], fill=roof)
    c.R(x + 14, y, w - 24, 2, shade(roof, .8))
    c.R(x, y + h * 6 // 10, w, h // 10, roof)                                                    # franja central
    for k in range(3):                                                                           # ventanas
        wx = x + 14 + k * (w - 36) // 3
        c.R(wx, y + 4, (w - 36) // 3 - 4, h * 3 // 10 - 2, (255, 214, 130) if win_lit else (90, 120, 150)); c.R(wx, y + 4, (w - 36) // 3 - 4, 1, (255, 240, 190))
    c.R(x, y + h - 6, w, 3, (60, 70, 76))
    for cx in (x + w // 5, x + w * 4 // 5):
        c.d.ellipse([cx - h // 6, y + h - h // 5, cx + h // 6, y + h + h // 8], fill=(30, 30, 40), outline=(100, 100, 116))
        c.d.ellipse([cx - h // 12, y + h - h // 8, cx + h // 12, y + h + h // 12], fill=(190, 190, 206))
    c.R(x + w - 6, y + h * 4 // 10, 5, 5, (255, 236, 150), c.ed)
