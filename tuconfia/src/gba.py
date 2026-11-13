"""Estilo «GBA» del canal (referencia: escenarios estilo Kirby de GBA), manteniendo los personajes anime.
- Sprites: contorno selectivo de 1 px (color oscuro del vecino, no negro puro), más saturación y contraste.
- Escenarios: cielo en bandas con tramado, nubes y montañas con contorno, árboles en capas, suelo de bloques biselados
  con contorno, pasto con mechones, marcos en primer plano y parallax por capas.
- Paleta: saturada; mood='dark' la baja y la enfría para escenas serias o nocturnas."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance
from lib import WW, WH, Canvas, vgrad

B4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
_CACHE = {}


def mix(a, b, k): return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))
def dark(c, k=.55, hue=(40, 24, 70)): return mix(tuple(int(v * k) for v in c), hue, .25)       # sombra con tono violeta (hue shift)
def lite(c, k=.35): return mix(c, (255, 250, 230), k)


# ---------------------------------------------------------------- sprites
def sprite(img, sat=1.18, con=1.06):
    """acabado GBA para un sprite RGBA: saturación + contorno selectivo de 1 px."""
    key = (id(img), img.size, sat)
    if key in _CACHE: return _CACHE[key]
    im = ImageEnhance.Contrast(ImageEnhance.Color(img.convert('RGBA')).enhance(sat)).enhance(con)
    a = np.array(im).astype(np.int32); al = a[..., 3] > 40
    H, W = al.shape; pad = np.zeros((H + 2, W + 2, 4), np.int32); pad[1:-1, 1:-1] = a
    out = np.zeros((H + 2, W + 2, 4), np.int32); out[1:-1, 1:-1] = a
    alp = np.zeros((H + 2, W + 2), bool); alp[1:-1, 1:-1] = al
    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        nb = np.roll(np.roll(alp, dy, 0), dx, 1); col = np.roll(np.roll(pad, dy, 0), dx, 1)
        edge = nb & ~alp & (out[..., 3] == 0)
        c = col[..., :3] * .32 + np.array([40, 24, 70]) * .3
        out[edge, :3] = c[edge]; out[edge, 3] = 255
    res = Image.fromarray(np.clip(out, 0, 255).astype('uint8'), 'RGBA')
    _CACHE[key] = res
    return res


def place(c, img, cx, feet, flip=False, shadow=True):
    sp = sprite(img)
    if flip: sp = sp.transpose(Image.FLIP_LEFT_RIGHT)
    bb = sp.getbbox(); x = int(cx - sp.width / 2); y = int(feet - bb[3])
    if shadow:
        w = (bb[2] - bb[0]) * .7; c.d.ellipse([cx - w / 2, feet - 2, cx + w / 2, feet + 2], fill=(20, 14, 40))
    c.im.alpha_composite(sp, (x, y)) if x >= 0 and y >= 0 else c.im.paste(sp, (x, y), sp)


# ---------------------------------------------------------------- escenario
def sky(c, stops, y0=0, y1=None, bands=7):
    """cielo en bandas planas con tramado Bayer en cada transición (como los fondos GBA)."""
    y1 = y1 or WH
    ys = np.arange(y0, y1); g = np.array(vgrad(stops))[y0:y1, 0, :3] if False else None
    cols = [np.array(s[1], float) for s in stops]; pos = [s[0] for s in stops]
    arr = np.array(c.im)
    for y in range(y0, y1):
        u = (y - y0) / max(1, y1 - y0 - 1) * (bands - 1)
        b = int(u); fr = u - b
        def band(i):
            v = i / (bands - 1)
            for k in range(len(pos) - 1):
                if pos[k] <= v <= pos[k + 1]: return cols[k] + (cols[k + 1] - cols[k]) * ((v - pos[k]) / max(1e-6, pos[k + 1] - pos[k]))
            return cols[-1]
        a_, b_ = band(b), band(min(bands - 1, b + 1))
        thr = B4[y % 4][np.arange(WW) % 4]
        row = np.where((thr < (fr - .55) / .45)[:, None] if fr > .55 else np.zeros((WW, 1), bool), b_, a_)
        arr[y, :, :3] = row; arr[y, :, 3] = 255
    c.im.paste(Image.fromarray(arr), (0, 0))


def cloud(c, x, y, w, col, t=0):
    """nube redonda: contorno, cuerpo, panza en sombra y brillos (todo dentro de la silueta)."""
    h = w * .42; ol = dark(col, .7); sh = dark(col, .9); hi = lite(col, .7)
    blobs = [(x + w * .18, y + h * .62, w * .2), (x + w * .38, y + h * .42, w * .26), (x + w * .62, y + h * .38, w * .24), (x + w * .82, y + h * .6, w * .18), (x + w * .5, y + h * .72, w * .3)]
    for bx, by, r in blobs: c.d.ellipse([bx - r - 1, by - r * .75 - 1, bx + r + 1, by + r * .75 + 1], fill=ol)
    for bx, by, r in blobs: c.d.ellipse([bx - r, by - r * .75, bx + r, by + r * .75], fill=sh)
    for bx, by, r in blobs: c.d.ellipse([bx - r, by - r * .75, bx + r * .92, by + r * .5], fill=col)
    for bx, by, r in blobs[1:3]: c.d.ellipse([bx - r * .55, by - r * .6, bx - r * .05, by - r * .3], fill=hi)


def clouds(c, t, y, col, n=5, seed=3, speed=2.0, scale=1.0):
    rnd = random.Random(seed)
    for i in range(n):
        w = rnd.randint(34, 64) * scale; x = (rnd.uniform(0, WW + 80) + t * speed * (1 + i % 2 * .4)) % (WW + 120) - 80
        cloud(c, x, y + rnd.randint(-10, 18), w, col, t)


def dither_poly(c, pts, col, density=.5):
    """rellena un polígono con tramado Bayer (mitad de los píxeles) para transiciones de sombra estilo GBA."""
    m = Image.new('L', (WW, WH), 0); ImageDraw.Draw(m).polygon(pts, fill=255)
    a = np.array(m) > 0; yy, xx = np.nonzero(a)
    keep = B4[yy % 4, xx % 4] < density
    arr = np.array(c.im); arr[yy[keep], xx[keep], :3] = col; c.im.paste(Image.fromarray(arr), (0, 0))


def mountains(c, base, h, col, seed=1, off=0.0, snow=None, n=6):
    """cordillera: cada pico con cara iluminada (izquierda) y cara en sombra (derecha), contorno y nieve opcional."""
    rnd = random.Random(seed); ol = dark(col, .62); shd = dark(col, .8); hi = lite(col, .18)
    x = -60 - (off % 90); peaks = []
    while x < WW + 90:
        w = rnd.randint(50, 90); peaks.append((x, w, base - rnd.uniform(.5, 1.0) * h)); x += int(w * .6)
    for x, w, py in peaks:
        px = x + w / 2
        c.d.polygon([(x - 1, base + 1), (px, py - 1), (x + w + 1, base + 1)], fill=ol)
    for x, w, py in peaks:
        px = x + w / 2
        c.d.polygon([(x, base), (px, py), (x + w, base)], fill=col)
        c.d.polygon([(px, py), (x + w, base), (px + w * .2, base)], fill=shd)
        dither_poly(c, [(px, py), (px + w * .2, base), (px - w * .06, base)], shd, .5)          # transición tramada
        c.d.line([(x + 2, base - 1), (px, py)], fill=hi)
        rr = random.Random(int(px))
        for _ in range(4):                                                  # vetas de roca
            vx = px + rr.uniform(-w * .25, w * .3); vy = py + rr.uniform(.25, .8) * (base - py)
            c.d.line([(vx, vy), (vx + 3, vy + 4)], fill=dark(col, .74))
        if snow and py < base - h * .62:
            sw = (base - py) * .18
            c.d.polygon([(px - sw, py + sw * 1.1), (px, py), (px + sw, py + sw * 1.1), (px + sw * .3, py + sw * .8), (px - sw * .3, py + sw * 1.2)], fill=snow)


def meadow(c, base, h, col, seed=2, off=0.0):
    """colinas suaves de plano medio con contorno y textura tramada (entre árboles y suelo)."""
    rnd = random.Random(seed); ol = dark(col, .62); pts = []; x = -40 - (off % 60)
    while x < WW + 60: pts.append((x, base - rnd.uniform(.4, 1.0) * h)); x += rnd.randint(30, 60)
    poly = [(pts[0][0], base + 20)] + pts + [(pts[-1][0], base + 20)]
    c.d.polygon(poly, fill=col); c.d.line(pts, fill=ol, width=1); c.d.line([(p[0], p[1] + 1) for p in pts], fill=lite(col, .25))
    dither_poly(c, [(pts[0][0], base + 20)] + [(p[0], p[1] + h * .55) for p in pts] + [(pts[-1][0], base + 20)], dark(col, .86), .5)


def tree_line(c, base, col, seed=5, off=0.0, size=16, trunk=(90, 60, 50)):
    """arbustos/árboles en racimos de tamaños distintos, con contorno, panza en sombra y brillo."""
    rnd = random.Random(seed); ol = dark(col, .5); sh = dark(col, .8); hi = lite(col, .28); x = -30 - (off % 46)
    while x < WW + 30:
        r = size * rnd.uniform(.55, 1.25); cx = x; tone = rnd.uniform(-.08, .08)
        cc = tuple(int(min(255, v * (1 + tone))) for v in col)
        if r > size * .9: c.R(int(cx - 2), int(base - r * .9), 4, int(r * .9), trunk); c.R(int(cx - 2), int(base - r * .9), 1, int(r * .9), dark(trunk, .7))
        parts = [(0, -r * 1.05, r), (-r * .62, -r * .55, r * .72), (r * .62, -r * .55, r * .72)]
        for dx, dy, rr in parts: c.d.ellipse([cx + dx - rr - 1, base + dy - rr - 1, cx + dx + rr + 1, base + dy + rr + 1], fill=ol)
        for dx, dy, rr in parts: c.d.ellipse([cx + dx - rr, base + dy - rr, cx + dx + rr, base + dy + rr], fill=sh)
        for dx, dy, rr in parts: c.d.ellipse([cx + dx - rr, base + dy - rr, cx + dx + rr * .8, base + dy + rr * .4], fill=cc)
        for dx, dy, rr in parts[:1]: c.d.ellipse([cx + dx - rr * .6, base + dy - rr * .7, cx + dx - rr * .05, base + dy - rr * .2], fill=hi)
        x += rnd.randint(16, 30)


def blocks(c, x0, y0, w, h, base, tile=16, seed=7, top=None, grass=None, t=0):
    """terreno orgánico: tierra con piedras redondeadas de varios tamaños (contorno, brillo arriba-izquierda,
    sombra abajo) y, opcional, franja de pasto con mechones que se mecen y caídas sobre el borde."""
    rnd = random.Random(seed); ol = dark(base, .42); dirt = dark(base, .72); dot = dark(base, .6)
    c.R(x0, y0, w, h, dirt)
    for _ in range(int(w * h / 26)):                                         # grano de la tierra
        c.d.point((x0 + rnd.randrange(w), y0 + rnd.randrange(max(1, h))), fill=dot)
    stones = []
    for j_ in range(0, h + tile, tile - 3):
        xx = x0 - rnd.randint(0, tile)
        while xx < x0 + w:
            sw, sh_ = rnd.randint(tile - 4, tile + 8), rnd.randint(tile - 6, tile)
            stones.append((xx, y0 + j_ + rnd.randint(-2, 2), sw, sh_)); xx += sw + rnd.randint(1, 4)
    for x, y, sw, sh_ in stones:
        v = rnd.uniform(-.08, .08); col = tuple(int(min(255, max(0, cc * (1 + v)))) for cc in base)
        c.d.rounded_rectangle([x - 1, y - 1, x + sw, y + sh_], radius=4, fill=ol)
        c.d.rounded_rectangle([x, y, x + sw - 1, y + sh_ - 1], radius=3, fill=dark(col, .82))
        c.d.rounded_rectangle([x, y, x + sw - 2, y + sh_ - 3], radius=3, fill=col)
        c.d.line([(x + 2, y + 1), (x + sw - 4, y + 1)], fill=lite(col, .35)); c.d.point((x + 1, y + 2), fill=lite(col, .35))
        cx_ = x + sw // 2 + rnd.randint(-3, 3); cy_ = y + sh_ // 2
        if rnd.random() < .5: c.d.line([(cx_, cy_ - 2), (cx_ + 1, cy_), (cx_ - 1, cy_ + 2)], fill=dark(col, .6))      # grieta
        else: c.d.point((cx_, cy_), fill=dark(col, .7)); c.d.point((cx_ + 2, cy_ + 1), fill=dark(col, .7))
        if grass and rnd.random() < .25: c.R(x + 1, y, rnd.randint(3, 6), 2, dark(grass, .85))                          # musgo
    if grass:
        gol = dark(grass, .45); ghi = lite(grass, .3); gsh = dark(grass, .78)
        c.R(x0, y0 - 5, w, 8, gol); c.R(x0, y0 - 4, w, 6, grass); c.R(x0, y0 - 4, w, 1, ghi); c.R(x0, y0 + 1, w, 1, gsh)
        for x in range(x0, x0 + w, 4):                                       # mechones que se mecen
            k = int(round(math.sin(t * 2.2 + x * .25)))
            hh = 5 + (x * 7) % 4
            c.d.polygon([(x - 1, y0 - 3), (x + 1 + k, y0 - 4 - hh), (x + 3, y0 - 3)], fill=gol)
            c.d.polygon([(x, y0 - 3), (x + 1 + k, y0 - 3 - hh), (x + 2, y0 - 3)], fill=grass if (x // 4) % 3 else ghi)
        for x in range(x0 + rnd.randint(0, 6), x0 + w, rnd.randint(8, 13)):  # caídas de pasto sobre la roca
            L = 2 + rnd.randint(0, 4)
            c.R(x - 1, y0 + 2, 5, L + 1, gol); c.R(x, y0 + 2, 3, L, grass)


def pillar(c, x, w, col, top=0, bottom=None, seed=3):
    """marco en primer plano: columna de roca con bloques redondeados (oscura, para enmarcar)."""
    bottom = bottom or WH; rnd = random.Random(seed); ol = dark(col, .4)
    c.R(x - 1, top, w + 2, bottom - top, ol)
    y = top
    while y < bottom:
        hh = rnd.randint(10, 18)
        c.d.rounded_rectangle([x, y, x + w - 1, y + hh - 2], radius=3, fill=col)
        c.d.line([(x + 2, y + 1), (x + w - 3, y + 1)], fill=lite(col, .2)); c.R(x + 1, y + hh - 3, w - 2, 1, dark(col, .75))
        y += hh


def grade(img, mood='day'):
    """dark: menos saturación y tono frío/violeta para escenas serias o nocturnas."""
    if mood == 'day': return img
    im = ImageEnhance.Color(img).enhance(.62)
    a = np.array(im).astype(float); a = a * np.array([.78, .82, 1.0]) + np.array([6, 4, 22])
    return Image.fromarray(np.clip(a, 0, 255).astype('uint8'))


def haze(c, y0, y1, col, k=.35):
    """perspectiva atmosférica: aclara y desatura hacia el color del cielo lo que ya está dibujado entre y0 e y1."""
    a = np.array(c.im).astype(float); a[y0:y1, :, :3] = a[y0:y1, :, :3] * (1 - k) + np.array(col) * k
    c.im.paste(Image.fromarray(a.astype('uint8')), (0, 0))


def palette(img, n=48):
    """paleta limitada (sin tramado de PIL: el tramado ya lo pone el motor)."""
    return img.convert('RGB').quantize(colors=n, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert('RGB')
