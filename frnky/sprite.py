"""Sprites chibi de cuerpo completo (56x64 px de diseño, x2 en el lienzo), con contorno automático,
rampas de color de 3 tonos, ojos grandes con brillo y poses. Todo original, dibujado por código."""
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

SW, SH, CX = 56, 64, 28
DARK = (38, 24, 56, 255)
WHITE = (255, 255, 255, 255)


def sh(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3]) + (255,)


CHARS = {
    "bro": dict(skin=(246, 198, 150), hair=(112, 66, 40), shirt=(70, 120, 224), pants=(60, 64, 110),
                shoe=(240, 240, 250), eye=(70, 150, 235), style="spiky"),
    "chuy": dict(skin=(250, 206, 160), hair=(40, 30, 40), shirt=(70, 176, 100), pants=(70, 80, 130),
                 shoe=(230, 90, 70), eye=(150, 90, 40), style="cap", cap=(232, 64, 70)),
    "nati": dict(skin=(222, 160, 116), hair=(86, 48, 150), shirt=(240, 120, 180), pants=(250, 240, 230),
                 shoe=(250, 200, 220), eye=(150, 70, 190), style="pony"),
    "memo": dict(skin=(160, 112, 78), hair=(60, 40, 32), shirt=(250, 204, 70), pants=(80, 76, 100),
                 shoe=(60, 60, 80), eye=(50, 120, 80), style="curly", glasses=True),
}
INK = (122, 52, 64, 255)


def _outline(img):
    a = np.array(img)
    m = a[..., 3] > 0
    d = np.zeros_like(m)
    d[1:] |= m[:-1]; d[:-1] |= m[1:]; d[:, 1:] |= m[:, :-1]; d[:, :-1] |= m[:, 1:]
    ring = d & ~m
    a[ring] = DARK
    return Image.fromarray(a)


@lru_cache(maxsize=4096)
def sprite(name, expr="neutral", mouth=None, pose="down", look=0, fx=(), shades=False,
           headset=False, bags=False, shirt=None):
    ch = CHARS[name]
    skin, hair = ch["skin"] + (255,), ch["hair"] + (255,)
    shirt_c = (shirt or ch["shirt"]) + (255,)
    img = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def R(x0, y0, x1, y1, c):
        d.rectangle([CX + x0, y0, CX + x1 - 1, y1 - 1], fill=c)

    def P(x, y, c):
        d.point((CX + x, y), fill=c)

    def body(x0, y0, x1, y1, c):  # bloque con luz a la izquierda y sombra a la derecha
        R(x0, y0, x1, y1, c)
        R(x1 - 3, y0, x1, y1, sh(c, 0.78)); R(x0, y0, x0 + 2, y1, sh(c, 1.14))
        R(x0, y1 - 2, x1, y1, sh(c, 0.82))

    style = ch["style"]
    if style == "pony":  # cola de caballo detrás de la cabeza
        R(11, 14, 19, 36, sh(hair, 0.9)); R(12, 14, 14, 34, sh(hair, 1.25)); R(11, 20, 19, 22, (255, 110, 170, 255))
    # piernas y zapatos
    pants = ch["pants"] + (255,)
    body(-7, 50, -1, 60, pants); body(1, 50, 7, 60, pants)
    body(-8, 59, -1, 63, ch["shoe"] + (255,)); body(1, 59, 8, 63, ch["shoe"] + (255,))
    R(-8, 62, -1, 63, sh(ch["shoe"], 0.6)); R(1, 62, 8, 63, sh(ch["shoe"], 0.6))
    # torso
    body(-9, 36, 9, 52, shirt_c)
    R(-3, 36, 3, 38, sh(shirt_c, 0.7)); R(-1, 38, 1, 46, sh(shirt_c, 0.9))
    if name == "bro":
        R(-5, 45, 5, 49, sh(shirt_c, 0.85)); R(-2, 38, -1, 44, (240, 240, 250, 255)); R(2, 38, 3, 44, (240, 240, 250, 255))
    if name == "memo":
        R(-4, 42, 4, 45, (255, 255, 255, 255))  # estampa
    # brazos
    sl = shirt_c
    hand = skin
    if pose in ("down", "fist", "point", "cheer"):
        if pose != "cheer":
            body(-12, 37, -9, 49, sl); R(-12, 49, -8, 52, hand); R(-12, 51, -8, 52, sh(hand, .85))
        if pose == "down":
            body(9, 37, 12, 49, sl); R(8, 49, 12, 52, hand); R(8, 51, 12, 52, sh(hand, .85))
        elif pose == "fist":
            body(9, 24, 13, 38, sl); R(9, 18, 14, 25, hand); R(9, 24, 14, 25, sh(hand, .8))
        elif pose == "point":
            body(9, 37, 20, 42, sl); R(20, 36, 26, 42, hand); R(24, 36, 26, 38, hand); R(20, 41, 26, 42, sh(hand, .8))
        elif pose == "cheer":
            for sx in (-1, 1):
                x0, x1 = (-13, -9) if sx < 0 else (9, 13)
                body(x0, 24, x1, 38, sl); R(x0 - (1 if sx < 0 else 0), 18, x1 + (0 if sx < 0 else 1), 25, hand)
    elif pose == "ctrl":
        body(-12, 37, -9, 46, sl); body(9, 37, 12, 46, sl)
        R(-10, 46, -5, 49, hand); R(5, 46, 10, 49, hand)
        body(-8, 44, 8, 49, (84, 88, 120, 255))
        R(-7, 45, -5, 47, (240, 70, 70, 255)); R(4, 45, 6, 47, (90, 210, 255, 255)); R(-1, 46, 1, 47, (255, 220, 90, 255))
    # cuello + cabeza
    R(-3, 33, 3, 37, sh(skin, 0.82))
    d.rounded_rectangle([CX - 14, 8, CX + 13, 35], radius=5, fill=skin)
    R(-14, 8, 14, 9, skin)
    # sombras de la cara
    R(11, 14, 14, 33, sh(skin, 0.86)); R(-12, 33, 12, 35, sh(skin, 0.84))
    R(-14, 22, -12, 28, skin); R(12, 22, 14, 28, sh(skin, 0.86))
    R(-15, 22, -14, 28, sh(skin, 0.9)); R(14, 22, 15, 28, sh(skin, 0.8))  # orejas
    # --- pelo ---
    hl = sh(hair, 1.45)
    if style == "spiky":
        d.rounded_rectangle([CX - 15, 4, CX + 14, 21], radius=6, fill=hair)
        for x0, top in ((-13, 0), (-7, -1), (-1, 0), (5, -1), (10, 2)):
            R(x0, max(top, 0), x0 + 6, 8, hair)
        R(-15, 14, -9, 30, hair); R(-9, 16, -2, 24, hair); R(-5, 24, -2, 26, hair); R(13, 14, 15, 28, sh(hair, .8))
        R(-9, 5, -3, 8, hl); R(-4, 3, 0, 5, hl); R(3, 4, 8, 7, sh(hair, 1.2))
    elif style == "cap":
        cap = ch["cap"] + (255,)
        d.rounded_rectangle([CX - 15, 3, CX + 14, 19], radius=7, fill=cap)
        R(-15, 15, 15, 21, sh(cap, .72)); R(-17, 19, 17, 22, sh(cap, 0.6))
        R(-8, 5, -3, 9, sh(cap, 1.35)); R(-1, 1, 2, 4, sh(cap, 0.8)); R(10, 6, 14, 16, sh(cap, 0.8))
        R(-14, 21, -10, 30, hair); R(10, 21, 14, 30, hair)
    elif style == "pony":
        d.rounded_rectangle([CX - 15, 4, CX + 14, 20], radius=7, fill=hair)
        R(-15, 12, -11, 38, hair); R(11, 12, 15, 38, sh(hair, .85))
        R(-12, 14, 12, 21, hair); R(-3, 18, 2, 23, hair); R(5, 18, 9, 22, hair)
        R(-9, 5, -2, 8, hl); R(-13, 20, -12, 34, hl); R(2, 10, 6, 12, sh(hair, 1.25))
        R(8, 5, 12, 9, (255, 110, 170, 255))  # moño
    elif style == "curly":
        d.rounded_rectangle([CX - 16, 6, CX + 15, 22], radius=6, fill=hair)
        for x0 in (-15, -9, -3, 3, 9):
            d.ellipse([CX + x0, 0, CX + x0 + 7, 9], fill=hair)
        R(-16, 14, -11, 28, hair); R(12, 14, 16, 28, sh(hair, .8))
        R(-11, 4, -7, 6, hl); R(-2, 2, 2, 4, hl); R(5, 4, 9, 6, hl)
    # --- ojos ---
    def eye(sx, side):  # side=-1 izquierdo, +1 derecho; el lado interno mira al centro
        top = 21
        if expr in ("happy", "blink"):
            for i, (dx, dy) in enumerate([(0, 6), (1, 5), (2, 4), (3, 4), (4, 4), (5, 5), (6, 6)]):
                R(sx + dx, 21 + dy - 1, sx + dx + 1, 21 + dy + 1, INK)
            return
        if expr == "shock":
            top = 19
        R(sx, top, sx + 7, 30, (255, 255, 255, 255))
        R(sx, top, sx + 7, top + 1, DARK)
        R(sx, 29, sx + 7, 30, sh(skin, 0.9))
        ix = max(sx, min(sx + 2, sx + 1 + look))
        ec = ch["eye"] + (255,)
        if expr == "shock":
            R(sx + 2, 22, sx + 5, 27, ec); R(sx + 3, 23, sx + 4, 26, DARK); R(sx + 2, 22, sx + 3, 23, WHITE)
        else:
            R(ix, top + 1, ix + 5, 30, sh(ec, 0.75))
            R(ix, top + 3, ix + 5, 30, ec)
            R(ix, 27, ix + 5, 30, sh(ec, 1.3))
            R(ix + 1, top + 3, ix + 4, 28, DARK)
            R(ix + 1, top + 2, ix + 3, top + 4, WHITE)
            P(ix + 4, 28, WHITE)
        inner = sx + 7 if side < 0 else sx
        if expr == "angry":
            for k in range(4):
                xx = (sx + 7 - 1 - k * 2) if side < 0 else (sx + k * 2)
                R(min(xx, xx + 2), top + 1, max(xx, xx + 2) + (0), top + 2 + (3 - k) * 0, DARK) if False else None
            for k in range(4):
                if side < 0:
                    R(sx + 7 - 2 * (k + 1), 21, sx + 7, 21 + k + 1, hair) if k == 3 else None
            for k in range(4):
                x0 = sx + 7 - (k + 1) * 2 if side < 0 else sx
                x1 = sx + 7 if side < 0 else sx + (k + 1) * 2
                R(x0, 21, x1, 21 + 1 + (3 - k) // 2 + (1 if k == 3 else 0), sh(skin, 0.7)) if False else None
            if side < 0:
                R(sx, 21, sx + 7, 23, sh(skin, 0.8)); R(sx + 3, 23, sx + 7, 25, sh(skin, 0.8))
            else:
                R(sx, 21, sx + 7, 23, sh(skin, 0.8)); R(sx, 23, sx + 4, 25, sh(skin, 0.8))
        elif expr == "sad":
            if side < 0:
                R(sx, 21, sx + 4, 24, sh(skin, 0.8))
            else:
                R(sx + 3, 21, sx + 7, 24, sh(skin, 0.8))
        elif expr in ("smug", "shy"):
            R(sx, 21, sx + 7, 25, sh(skin, 0.78)); R(sx, 25, sx + 7, 26, DARK)
        if bags:
            R(sx, 30, sx + 7, 31, (150, 100, 170, 255))
    eye(-10, -1); eye(3, 1)
    # cejas
    bc = sh(hair, 0.7) if style != "cap" else sh(hair, 1.0)
    for sx, side in ((-10, -1), (3, 1)):
        y = 17
        if expr == "angry":
            R(sx, 16 + (0 if side < 0 else 3), sx + 4, 17 + (0 if side < 0 else 3), bc)
            R(sx + 3, 19 if side < 0 else 16, sx + 7, 20 if side < 0 else 17, bc)
            R(sx + (0 if side < 0 else 0), 16 if side < 0 else 19, sx + 3, 17 if side < 0 else 20, bc) if False else None
            if side < 0:
                R(sx, 16, sx + 3, 17, bc); R(sx + 3, 18, sx + 7, 19, bc)
            else:
                R(sx + 4, 16, sx + 7, 17, bc); R(sx, 18, sx + 4, 19, bc)
        elif expr == "sad":
            if side < 0:
                R(sx, 19, sx + 3, 20, bc); R(sx + 3, 17, sx + 7, 18, bc)
            else:
                R(sx + 4, 19, sx + 7, 20, bc); R(sx, 17, sx + 4, 18, bc)
        elif expr == "shock":
            R(sx, 14, sx + 7, 15, bc)
        elif expr not in ("happy", "blink", "smug") or True:
            if expr != "angry":
                R(sx, 17 if expr != "smug" else 18, sx + 7, 18 if expr != "smug" else 19, bc)
    if "tear" in fx:
        R(-9, 30, -7, 36, (130, 210, 255, 255)); R(-9, 30, -8, 33, WHITE)
    # mejillas y nariz
    if expr in ("happy", "angry", "shy", "shock") or "blush" in fx:
        R(-12, 30, -8, 32, (255, 130, 140, 200)); R(8, 30, 12, 32, (255, 130, 140, 200))
    P(0, 29, sh(skin, 0.75)); P(1, 29, sh(skin, 0.75))
    # boca
    m = mouth or {"happy": "smile", "sad": "frown", "angry": "open", "shock": "o", "smug": "smirk", "shy": "shy"}.get(expr, "closed")
    if m == "closed":
        R(-2, 32, 2, 33, INK)
    elif m == "open":
        R(-3, 31, 3, 35, INK); R(-2, 34, 2, 35, (230, 90, 100, 255)); R(-3, 31, 3, 32, WHITE)
    elif m == "big":
        R(-4, 31, 4, 36, INK); R(-3, 34, 3, 36, (230, 90, 100, 255)); R(-4, 31, 4, 33, WHITE)
    elif m == "smile":
        R(-3, 32, 3, 33, INK); R(-4, 31, -3, 32, INK); R(3, 31, 4, 32, INK); R(-2, 33, 2, 35, INK); R(-2, 33, 2, 34, WHITE)
    elif m == "frown":
        R(-3, 33, 3, 34, INK); R(-4, 34, -3, 35, INK); R(3, 34, 4, 35, INK)
    elif m == "o":
        R(-2, 31, 2, 36, INK); R(-1, 34, 1, 36, (230, 90, 100, 255))
    elif m == "smirk":
        R(-3, 33, 2, 34, INK); R(2, 32, 4, 33, INK)
    elif m == "shy":
        R(-3, 33, 0, 34, INK); R(0, 32, 3, 33, INK)
    # accesorios
    if ch.get("glasses"):
        for sx in (-11, 2):
            R(sx, 20, sx + 9, 21, DARK); R(sx, 30, sx + 9, 31, DARK); R(sx, 20, sx + 1, 31, DARK); R(sx + 8, 20, sx + 9, 31, DARK)
            R(sx + 1, 21, sx + 3, 22, (255, 255, 255, 140))
        R(-2, 24, 2, 25, DARK)
    if shades:
        R(-13, 21, 13, 29, (24, 24, 40, 255)); R(-13, 21, 13, 23, (50, 50, 70, 255))
        R(-10, 24, -6, 25, (120, 210, 255, 255)); R(5, 24, 9, 25, (120, 210, 255, 255)); R(-10, 26, -8, 27, (120, 210, 255, 255))
    if headset:
        R(-16, 8, 16, 11, (70, 74, 96, 255)); R(-16, 9, 16, 10, (110, 116, 150, 255))
        R(-16, 10, -14, 26, (70, 74, 96, 255)); R(14, 10, 16, 26, (70, 74, 96, 255))
        body(-19, 20, -14, 31, (232, 60, 100, 255)); body(14, 20, 19, 31, (232, 60, 100, 255))
        R(-18, 31, -17, 36, (70, 74, 96, 255)); R(-18, 35, -8, 36, (70, 74, 96, 255)); R(-9, 34, -6, 37, (232, 60, 100, 255))
    if "sweat" in fx:
        R(12, 6, 15, 11, (150, 220, 255, 255)); R(13, 6, 14, 8, WHITE)
    if "vein" in fx:
        R(-14, 2, -11, 3, (240, 50, 50, 255)); R(-13, 1, -12, 5, (240, 50, 50, 255))
        R(8, 2, 11, 3, (240, 50, 50, 255)); R(9, 1, 10, 5, (240, 50, 50, 255))
    return _outline(img)


def draw_char(canvas, name, x, feet_y, flip=False, scale=2, shadow=True, ox=0, oy=0, **kw):
    """Pega el sprite sobre el lienzo RGBA; x = centro, feet_y = suelo."""
    spr = sprite(name, **kw)
    if flip:
        spr = spr.transpose(Image.FLIP_LEFT_RIGHT)
    big = spr.resize((SW * scale, SH * scale), Image.NEAREST)
    if shadow:
        from PIL import ImageDraw as D
        sh_l = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        D.Draw(sh_l).ellipse([x - 34 + ox, feet_y - 7, x + 34 + ox, feet_y + 7], fill=(10, 6, 30, 90))
        canvas.alpha_composite(sh_l)
    canvas.alpha_composite(big, (int(x - SW * scale // 2 + ox), int(feet_y - 62 * scale + oy)))
