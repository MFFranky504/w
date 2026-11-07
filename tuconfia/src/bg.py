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


# ================================================================ escenografía (más detalle)
def curtain(c, x, w, h=200, col=(176, 30, 62), valance=True):
    """cortina de terciopelo con pliegues sombreados y recogida con borla; x..x+w."""
    for k in range(w):
        f = .72 + .38 * (0.5 + 0.5 * math.sin(k * 0.95))
        c.R(x + k, 0, 1, h, tuple(min(255, int(v * f)) for v in col))
    for k in range(0, w, 3): c.R(x + k, 0, 1, h, shade(col, 1.12))
    c.R(x, h - 3, w, 3, shade(col, .55))
    if valance:
        c.R(x - 1, 0, w + 2, 12, shade(col, .8)); c.R(x - 1, 12, w + 2, 2, (230, 190, 90))
        for k in range(x, x + w, 8): c.d.pieslice([k, 8, k + 8, 20], 0, 180, fill=shade(col, .9))
    c.R(x, 110, w, 3, (230, 190, 90)); c.R(x + w // 2 - 2, 113, 4, 10, (230, 190, 90))           # lazo y borla


def beam(c, x, y, w_top, w_bot, ybot, col=(255, 240, 200), a=34):
    """haz de luz translúcido de un foco (sobre la capa emisiva)."""
    c.ed.polygon([(x - w_top // 2, y), (x + w_top // 2, y), (x + w_bot // 2, ybot), (x - w_bot // 2, ybot)], fill=(*col, a))
    c.light(x, ybot, w_bot, 26, col, .45)


def truss(c, y, cols, t=0, x0=8, x1=152):
    c.R(x0, y, x1 - x0, 3, (70, 72, 92)); c.R(x0, y, x1 - x0, 1, (140, 144, 170))
    for k in range(x0, x1, 4): c.R(k, y + 3, 1, 3, (50, 52, 70)); c.R(k, y + 3, 4, 1, (50, 52, 70))
    n = len(cols)
    for i, col in enumerate(cols):
        px = x0 + 10 + i * (x1 - x0 - 20) // max(1, n - 1)
        c.R(px - 3, y + 4, 7, 6, (36, 38, 52)); c.R(px - 2, y + 9, 5, 2, col, c.ed)
        beam(c, px, y + 10, 5, 34, y + 170, col, 22 + int(8 * math.sin(t * 2 + i)))


def crowd(c, y, t, seed=1, cols=((18, 10, 28), (26, 14, 38), (14, 8, 24)), hands=True, phones=True):
    """público en silueta con manos y luces de móvil (primer plano oscuro)."""
    rnd = random.Random(seed)
    x = -6
    while x < WW + 8:
        w = rnd.randint(14, 20); col = rnd.choice(cols); hy = y + rnd.randint(-4, 6)
        c.d.ellipse([x, hy, x + w - 4, hy + w - 4], fill=col); c.R(x - 2, hy + w - 6, w + 2, 60, col)
        if hands and rnd.random() < .5:
            hx = x + w // 2 - 6 + int(math.sin(t * 4 + x) * 2); c.R(hx, hy - 12, 2, 12, col); c.R(hx - 1, hy - 15, 4, 4, col)
        if phones and rnd.random() < .16 and int(t * 2 + x) % 3:
            c.R(x + w // 2 - 1, hy - 6, 3, 5, (210, 230, 255), c.ed)
        x += w - 2


def speaker(c, x, y, w=20, h=34):
    c.R(x, y, w, h, (28, 28, 40)); c.R(x, y, w, 1, (90, 92, 120)); c.R(x, y + h - 1, w, 1, (14, 14, 24))
    c.d.ellipse([x + 3, y + 4, x + w - 3, y + 4 + w - 6], fill=(54, 56, 76), outline=(14, 14, 24))
    c.d.ellipse([x + w // 2 - 3, y + 4 + (w - 6) // 2 - 3, x + w // 2 + 3, y + 4 + (w - 6) // 2 + 3], fill=(110, 112, 140))
    c.d.ellipse([x + 5, y + h - 12, x + w - 5, y + h - 4], fill=(54, 56, 76), outline=(14, 14, 24))


def tree(c, x, yb, h=44, kind='round', col=(46, 110, 70), t=0):
    c.R(x - 2, yb - h // 3, 4, h // 3, (96, 62, 44))
    if kind == 'pine':
        for k in range(4):
            wk = h // 2 - k * (h // 9); yk = yb - h // 3 - k * (h // 5)
            c.d.polygon([(x - wk, yk), (x + wk, yk), (x, yk - h // 3)], fill=shade(col, .8 + k * .1))
    else:
        r = h // 3 + 2
        for dx, dy, f in ((-r // 2, 0, .85), (r // 2, 0, .85), (0, -r // 2, 1.0), (0, r // 4, .9)):
            c.d.ellipse([x + dx - r, yb - h // 2 + dy - r, x + dx + r, yb - h // 2 + dy + r], fill=shade(col, f))
        c.d.ellipse([x - r // 2 - 3, yb - h // 2 - r, x + 2, yb - h // 2 - r + 6], fill=shade(col, 1.3))


def fence(c, x0, x1, y, col=(184, 140, 96)):
    for x in range(x0, x1, 8): c.R(x, y - 12, 3, 14, col); c.R(x, y - 12, 3, 1, shade(col, 1.3)); c.R(x, y + 2, 3, 1, shade(col, .6))
    c.R(x0, y - 9, x1 - x0, 2, col); c.R(x0, y - 4, x1 - x0, 2, col)


def smoke(c, x, y, t):
    for i in range(6):
        ph = (t * .5 + i * .17) % 1
        r = 2 + int(ph * 5); c.d.ellipse([x + math.sin(t + i) * 4 + ph * 8 - r, y - ph * 50 - r, x + math.sin(t + i) * 4 + ph * 8 + r, y - ph * 50 + r], fill=(int(220 - ph * 40), int(214 - ph * 40), int(230 - ph * 30)))


def foam(c, x, y, w, h, col=(48, 54, 90)):
    """paneles acústicos de espuma (cuña en rombos)."""
    c.R(x, y, w, h, shade(col, .6))
    for j in range(0, h, 8):
        for i in range(0, w, 8):
            c.d.polygon([(x + i, y + j + 8), (x + i + 4, y + j), (x + i + 8, y + j + 8)], fill=col if (i // 8 + j // 8) % 2 else shade(col, 1.2))


def console(c, x, y, w, t=0):
    c.d.polygon([(x, y + 20), (x + 6, y), (x + w - 6, y), (x + w, y + 20)], fill=(52, 54, 72)); c.R(x, y + 20, w, 10, (34, 36, 50)); c.R(x + 6, y, w - 12, 1, (120, 124, 150))
    for k in range(6, w - 6, 5):
        c.R(x + k, y + 4, 2, 12, (20, 22, 32)); c.R(x + k, y + 6 + (k * 7) % 8, 2, 3, (220, 220, 236))
    for k in range(5): c.R(x + 8 + k * (w - 18) // 4, y + 2, 2, 2, ((255, 80, 80), (80, 255, 120), (255, 214, 80))[(k + int(t * 3)) % 3], c.ed)


def gold_record(c, x, y, w=22):
    c.R(x - 2, y - 2, w + 4, w + 4, (150, 100, 40)); c.R(x - 1, y - 1, w + 2, w + 2, (230, 190, 90)); c.R(x, y, w, w, (40, 24, 40))
    c.d.ellipse([x + 2, y + 2, x + w - 3, y + w - 3], fill=(236, 190, 70), outline=(150, 100, 30)); c.d.ellipse([x + w // 2 - 3, y + w // 2 - 3, x + w // 2 + 2, y + w // 2 + 2], fill=(40, 24, 40))
    c.R(x + w // 3, y + w + 4, w // 3, 3, (230, 190, 90))


def skyline(c, y0, base, cols=((40, 30, 80), (58, 44, 110)), seed=3, lit=.4, t=0, wmin=10, wmax=20, hmin=26, hmax=80):
    rnd = random.Random(seed); x = -4
    while x < WW:
        w = rnd.randint(wmin, wmax); h = rnd.randint(hmin, hmax); col = rnd.choice(cols)
        c.R(x, base - h, w, h, col); c.R(x, base - h, w, 1, shade(col, 1.4))
        if rnd.random() < .3: c.R(x + w // 2, base - h - 6, 1, 6, shade(col, 1.2))
        for r in range(h // 8):
            for k in range(w // 5):
                if rnd.random() < lit and int(t * 2 + r + k) % 17: c.R(x + 2 + k * 5, base - h + 3 + r * 8, 3, 4, (255, rnd.randint(190, 235), 120))
        x += w


# ================================================================ historia Hawking: ciencia y espacio
def blackboard(c, x, y, w, h, t=0, seed=1, lines=None, prog=1.0):
    """pizarra verde con fórmulas a tiza que se van escribiendo (prog 0..1)."""
    c.R(x - 2, y - 2, w + 4, h + 4, (110, 74, 48)); c.R(x, y, w, h, (34, 66, 56)); c.R(x, y, w, 1, (60, 96, 84)); c.R(x - 2, y + h + 2, w + 4, 2, (170, 130, 90))
    rnd = random.Random(seed); F = ['E=mc2', 'S=A/4', 'T~1/M', 'dS>=0', 'R=2GM/c2', 'F=ma', 'PSI', 'G=8PT', 'A+B=C', 'H=hf']
    n = int(prog * (h // 9)); 
    for i in range(n):
        txt = lines[i % len(lines)] if lines else rnd.choice(F)
        wtext(c, x + 3 + rnd.randint(0, 6), y + 3 + i * 9, txt, (230, 236, 226), 8, outline=None)
    c.R(x + w - 16, y + h - 3, 10, 2, (240, 240, 232))


def black_hole(c, cx, cy, r, t, particles=True):
    """agujero negro con disco de acreción, anillo de fotones y partículas que escapan (radiación de Hawking)."""
    for k in range(6):                                                                       # halo
        rr = r + 22 - k * 3; c.ed.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(255, 150, 60, 10 + k * 4))
    for i in range(34):                                                                      # disco en espiral
        a = t * 1.8 + i * .19; rr = r + 5 + (i % 12) * 2.6; sx = cx + math.cos(a) * rr * 1.7; sy = cy + math.sin(a) * rr * .5
        c.R(int(sx), int(sy), 3, 2, (255, int(150 + (i % 5) * 20), 70 + (i % 4) * 30))
    c.d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(2, 2, 8)); c.d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 214, 140))
    c.d.ellipse([cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2], outline=(150, 110, 70))
    if particles:
        for i in range(24):
            ph = (t * .35 + i * .0417) % 1; a = i * 2.4; rr = r + 4 + ph * 80
            c.R(int(cx + math.cos(a) * rr), int(cy + math.sin(a) * rr), 2, 2, (200, 230, 255), c.ed)
    c.light(cx, cy, r * 3, r * 3, (255, 160, 80), .55)


def nebula(c, t, seed=2, cols=((120, 60, 200), (60, 120, 220), (220, 80, 160))):
    rnd = random.Random(seed)
    for i in range(9):
        x, y, w, h = rnd.randint(0, 160), rnd.randint(20, 200), rnd.randint(40, 90), rnd.randint(20, 50)
        col = cols[i % 3]
        for k in range(4): c.ed.ellipse([x - w // 2 + k * 6, y - h // 2 + k * 3, x + w // 2 - k * 6, y + h // 2 - k * 3], fill=(*col, 12 + k * 5))


def shooting_star(c, t, seed=0, period=3.0):
    ph = ((t + seed * 1.3) % period) / period
    if ph < .22:
        x = 150 - ph * 4.5 * 130 - seed * 20; y = 30 + ph * 4.5 * 60 + seed * 14
        c.d.line([(x, y), (x + 14, y - 7)], fill=(255, 255, 255)); c.R(int(x), int(y), 2, 2, (255, 255, 230), c.ed)


def hill(c, y0, col=(20, 18, 46), t=0):
    c.d.polygon([(0, y0 + 26), (30, y0 + 6), (70, y0 + 18), (110, y0), (160, y0 + 16), (160, 300), (0, 300)], fill=col)
    c.R(0, y0 + 24, WW, 100, shade(col, .9))


def stone_college(c, x0, y0, w, h, base=(216, 182, 124), seed=5, lit=.6, t=0):
    """fachada gótica de piedra dorada con ventanas ojivales, contrafuertes y almenas."""
    brick(c, x0, y0, w, h, base=base, mortar=shade(base, .62), seed=seed, bh=7, bw=14)
    for x in range(x0, x0 + w, 5): c.R(x, y0 - 4, 3, 4, shade(base, .9))                      # almenas
    rnd = random.Random(seed)
    n = max(2, w // 26)
    for k in range(n):
        wx = x0 + 8 + k * (w - 16) // n
        for r in range(max(1, (h - 12) // 34)):
            wy = y0 + 10 + r * 34
            c.R(wx, wy + 6, 12, 20, (50, 36, 40)); c.d.pieslice([wx, wy, wx + 11, wy + 12], 180, 360, fill=(50, 36, 40))
            on = rnd.random() < lit
            c.R(wx + 2, wy + 8, 8, 17, (255, 206, 120) if on else (60, 70, 120)); c.d.pieslice([wx + 2, wy + 2, wx + 9, wy + 10], 180, 360, fill=(255, 206, 120) if on else (60, 70, 120))
            c.R(wx + 5, wy + 8, 2, 17, (50, 36, 40)); c.R(wx + 1, wy + 26, 10, 2, shade(base, 1.2))
    for k in range(0, n + 1):
        px = x0 + k * (w - 6) // n; c.R(px, y0, 6, h, shade(base, .85)); c.R(px, y0, 1, h, shade(base, 1.15))


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
            col = tuple(max(0, min(255, v + rnd.randint(-14, 14))) for v in base)
            c.R(xa, ya, xb - xa, yb - ya, col); c.R(xa, ya, xb - xa, 1, shade(col, 1.18)); c.R(xa, yb - 1, xb - xa, 1, shade(col, .82))


def hospital_wall(c, t=0):
    c.R(0, 0, WW, 206, (150, 206, 204))
    for x in range(0, WW, 16):
        for y in range(0, 150, 16): c.R(x + 1, y + 1, 14, 14, (176, 226, 224)); c.R(x + 1, y + 1, 14, 1, (210, 244, 242))
    c.R(0, 150, WW, 56, (120, 176, 178)); c.R(0, 150, WW, 3, (230, 250, 250))
    for x in range(0, WW, 40): c.R(x + 6, 158, 28, 40, (104, 160, 162)); c.R(x + 6, 158, 28, 1, (150, 206, 206))
    for yy in range(206, 296, 14):
        for xx in range(-(yy // 14 % 2) * 14, WW, 28): c.R(xx, yy, 14, 14, (228, 232, 238)); c.R(xx + 14, yy, 14, 14, (200, 208, 220))
    c.R(0, 204, WW, 3, (90, 140, 142))


# ================================================================ variantes para el mundo apaisado (320x180)
def hill_l(c, y0, col=(20, 18, 46), t=0):
    c.d.polygon([(0, y0 + 10), (60, y0 - 8), (130, y0 + 6), (200, y0 - 10), (270, y0 + 4), (320, y0 - 2), (320, 300), (0, 300)], fill=col)


def nebula_l(c, t, seed=2, cols=((120, 60, 200), (60, 120, 220), (220, 80, 160))):
    rnd = random.Random(seed)
    for i in range(10):
        x, y, w, h = rnd.randint(0, 320), rnd.randint(10, 110), rnd.randint(70, 140), rnd.randint(20, 46)
        col = cols[i % 3]
        for k in range(4): c.ed.ellipse([x - w // 2 + k * 8, y - h // 2 + k * 3, x + w // 2 - k * 8, y + h // 2 - k * 3], fill=(*col, 12 + k * 5))


def shoot_l(c, t, seed=0, period=3.0):
    ph = ((t + seed * 1.3) % period) / period
    if ph < .22:
        x = 300 - ph * 4.5 * 240 - seed * 30; y = 14 + ph * 4.5 * 50 + seed * 12
        c.d.line([(x, y), (x + 20, y - 8)], fill=(255, 255, 255)); c.R(int(x), int(y), 2, 2, (255, 255, 230), c.ed)


def hospital_wall_l(c, t=0):
    c.R(0, 0, WW, 136, (150, 206, 204))
    for x in range(0, WW, 16):
        for y in range(0, 100, 16): c.R(x + 1, y + 1, 14, 14, (176, 226, 224)); c.R(x + 1, y + 1, 14, 1, (210, 244, 242))
    c.R(0, 100, WW, 36, (120, 176, 178)); c.R(0, 100, WW, 3, (230, 250, 250))
    for x in range(0, WW, 44): c.R(x + 6, 108, 32, 26, (104, 160, 162)); c.R(x + 6, 108, 32, 1, (150, 206, 206))
    for yy in range(136, 180, 11):
        for xx in range(-(yy // 11 % 2) * 14, WW, 28): c.R(xx, yy, 14, 11, (228, 232, 238)); c.R(xx + 14, yy, 14, 11, (200, 208, 220))
    c.R(0, 134, WW, 3, (90, 140, 142))
