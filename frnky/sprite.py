"""Sprites de cuerpo completo estilo JRPG 16/32 bits (proporciones de ~4 cabezas, paleta apagada).
Diseño de 56x72 px, x2 en el lienzo; contorno automático; sombras frías y luces cálidas."""
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

SW, SH, CX, FOOT = 56, 72, 28, 70
DARK = (22, 16, 34, 255)
WHITE = (238, 236, 232, 255)
INK = (96, 44, 52, 255)


def dk(c, f=0.72):   # sombra: baja valor y se enfría
    return (int(c[0] * f * 0.96), int(c[1] * f * 0.98), min(255, int(c[2] * f * 1.08)), 255)


def lt(c, f=1.16):   # luz: sube valor y se calienta
    return (min(255, int(c[0] * f + 8)), min(255, int(c[1] * f + 5)), min(255, int(c[2] * f)), 255)


CHARS = {   # Bro (Chile), Chuy (México), Nati (Argentina), Memo (Venezuela)
    "bro": dict(skin=(214, 168, 136), hair=(78, 54, 44), coat=(54, 70, 116), kind="hoodie", trim=(226, 226, 232),
                pants=(66, 86, 126), shoe=(226, 224, 222), sole=(120, 120, 140), eye=(96, 128, 160), style="spiky"),
    "chuy": dict(skin=(226, 182, 146), hair=(36, 30, 36), coat=(34, 112, 72), kind="jersey", trim=(236, 236, 232),
                 pants=(46, 52, 74), shoe=(232, 232, 232), sole=(176, 60, 66), eye=(120, 86, 56), style="cap",
                 cap=(146, 46, 54), band=True),
    "nati": dict(skin=(204, 154, 122), hair=(70, 50, 104), coat=(122, 180, 224), kind="jersey", trim=(30, 40, 90),
                 stripes=(238, 238, 242), pants=(34, 34, 46), shoe=(236, 236, 240), sole=(150, 150, 170),
                 eye=(130, 96, 160), style="pony"),
    "memo": dict(skin=(150, 108, 82), hair=(48, 36, 32), coat=(122, 34, 54), kind="jersey", trim=(214, 176, 60),
                 pants=(88, 92, 108), shoe=(52, 52, 64), sole=(220, 220, 224), eye=(70, 110, 84), style="curly",
                 glasses=True, jog=True),
}


def _chibi(img):
    """Más chibi: cuerpo más corto (borra filas del torso/piernas) y cabeza más grande (duplica filas/columnas planas)."""
    a = np.array(img)
    a = np.delete(a, [34, 44, 55, 61], axis=0)                 # torso y piernas más cortos
    a = np.insert(a, [9, 19], a[[9, 19]], axis=0)              # cabeza +2 filas (frente y mejillas)
    c = SW // 2
    a = np.insert(a, [c - 9, c, c + 8], a[:, [c - 9, c, c + 8]], axis=1)   # cabeza +3 columnas
    return Image.fromarray(a)


def _vivid(img, k=1.28):
    """Sube la saturación de los colores del sprite (el contorno oscuro se mantiene)."""
    a = np.array(img).astype("float32")
    rgb = a[..., :3]
    g = rgb.mean(axis=2, keepdims=True)
    a[..., :3] = np.clip(g + (rgb - g) * k, 0, 255)
    return Image.fromarray(a.astype("uint8"))


def _outline(img):
    a = np.array(img)
    m = a[..., 3] > 0
    d = np.zeros_like(m)
    d[1:] |= m[:-1]; d[:-1] |= m[1:]; d[:, 1:] |= m[:, :-1]; d[:, :-1] |= m[:, 1:]
    a[d & ~m] = DARK
    return Image.fromarray(a)


@lru_cache(maxsize=4096)
def sprite(name, expr="neutral", mouth=None, pose="down", look=0, fx=(), shades=False,
           headset=False, bags=False, shirt=None, walk=0):
    ch = CHARS[name]
    skin, hair = ch["skin"] + (255,), ch["hair"] + (255,)
    coat = (shirt or ch["coat"]) + (255,)
    pants = ch["pants"] + (255,)
    style = ch["style"]
    img = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def R(x0, y0, x1, y1, c):
        d.rectangle([CX + x0, y0, CX + x1 - 1, y1 - 1], fill=c)

    def P(x, y, c):
        d.point((CX + x, y), fill=c)

    def body(x0, y0, x1, y1, c):  # luz arriba-izquierda, sombra derecha y abajo
        R(x0, y0, x1, y1, c)
        R(x1 - 2, y0, x1, y1, dk(c, 0.78)); R(x0, y0, x0 + 1, y1, lt(c, 1.12))
        R(x0, y1 - 1, x1, y1, dk(c, 0.8))

    if style == "pony":  # pelo largo detrás del cuerpo
        body(-11, 10, 11, 36, hair)
    # piernas y tenis (ropa moderna)
    kind, trim = ch["kind"], ch["trim"] + (255,)
    lL, lR = (3 if walk == 1 else 0), (3 if walk == 2 else 0)   # pierna levantada al caminar
    body(-8, 48, -1, 65 - lL, pants); body(1, 48, 8, 65 - lR, pants)
    R(-7, 56 - lL, -3, 57 - lL, lt(pants, 1.25)); R(2, 56 - lR, 6, 57 - lR, lt(pants, 1.25))
    if ch.get("jog"):
        R(-8, 49, -7, 64 - lL, (236, 236, 240, 255)); R(7, 49, 8, 64 - lR, (236, 236, 240, 255))
    if name in ("bro", "chuy"):   # pantalón cargo
        R(-8, 52, -4, 57, dk(pants, 0.8)); R(4, 52, 8, 57, dk(pants, 0.8)); R(-8, 52, -4, 53, lt(pants, 1.2)); R(4, 52, 8, 53, lt(pants, 1.2))
    shoe, sole = ch["shoe"] + (255,), ch["sole"] + (255,)
    body(-9, 63 - lL, -1, 69 - lL, shoe); body(1, 63 - lR, 9, 69 - lR, shoe)
    R(-9, 68 - lL, -1, 70 - lL, sole); R(1, 68 - lR, 9, 70 - lR, sole)
    R(-9, 63 - lL, -4, 64 - lL, lt(shoe, 1.1)); R(1, 63 - lR, 6, 64 - lR, lt(shoe, 1.1))
    for x in (-5, -3, 3, 5):
        P(x, 65 - (lL if x < 0 else lR), dk(shoe, 0.6))
    # torso: hoodie o camiseta de selección
    body(-10, 26, 10, 50, coat)
    R(-10, 49, 10, 50, dk(coat, 0.7))
    if ch.get("stripes"):
        for x0 in range(-10, 8, 6):
            R(x0 + 3, 27, x0 + 6, 49, ch["stripes"] + (255,))
        R(8, 27, 10, 49, dk(coat, 0.78))
    if kind == "hoodie":
        R(-7, 25, 7, 29, dk(coat, 0.62)); R(-6, 25, 6, 27, dk(coat, 0.8))      # capucha
        R(-3, 29, -2, 37, trim); R(2, 29, 3, 36, trim)                       # cordones
        R(-6, 42, 6, 48, dk(coat, 0.8)); R(-6, 42, 6, 43, lt(coat, 1.1))     # bolsillo
    else:
        R(-4, 26, 4, 28, trim); R(-3, 28, 3, 29, trim); R(-1, 29, 1, 30, trim)  # cuello en V
        R(-10, 26, -7, 28, trim); R(7, 26, 10, 28, trim)                        # hombros con vivos
        R(5, 33, 8, 36, (236, 236, 236, 255) if name != "nati" else (30, 40, 90, 255))  # escudo
        P(6, 34, (196, 50, 60, 255))
    sleeve_end = 43 if kind == "hoodie" else 34
    hand = skin
    L = sleeve_end - 27

    def vert_arm(x0, x1, y0, y1, hang=True):
        R(x0, y0, x1, y1, hand)
        if hang:
            body(x0, y0, x1, min(y1, y0 + L), coat)
        else:
            body(x0, max(y0, y1 - L), x1, y1, coat)
        R(x0, y1 - 1, x1, y1, dk(hand, 0.8)) if hang else None

    if pose != "cheer":
        vert_arm(-13, -10, 27, 46)
        if ch.get("band"):
            R(-13, 40, -10, 41, (34, 112, 72, 255)); R(-13, 41, -10, 42, WHITE); R(-13, 42, -10, 43, (196, 50, 60, 255))
    if pose == "down":
        vert_arm(10, 13, 27, 46)
    elif pose == "fist":
        vert_arm(10, 13, 14, 30, hang=False); R(9, 9, 14, 15, hand); R(9, 14, 14, 15, dk(hand, 0.8))
    elif pose == "point":
        for i, (x0, y0) in enumerate(((10, 27), (14, 29), (18, 31))):   # brazo en escalera, apunta hacia abajo
            if i < (3 if kind == "hoodie" else 1):
                body(x0, y0, x0 + 5, y0 + 4, coat)
            else:
                R(x0, y0, x0 + 5, y0 + 4, hand); R(x0, y0 + 3, x0 + 5, y0 + 4, dk(hand, 0.8))
        R(22, 32, 27, 37, hand); R(26, 33, 28, 35, hand); R(22, 36, 27, 37, dk(hand, 0.8))
    elif pose == "cheer":
        for x0, x1 in ((-13, -10), (10, 13)):
            vert_arm(x0, x1, 14, 30, hang=False); R(x0 - 1, 9, x1 + 1, 15, hand)
    elif pose == "ctrl":
        vert_arm(10, 13, 27, 40)
        R(-13, 37, 13, 41, coat if kind == "hoodie" else hand)
        R(-7, 38, -4, 42, hand); R(4, 38, 7, 42, hand)
        body(-5, 37, 5, 43, (62, 66, 90, 255))
        R(-4, 38, -3, 39, (170, 70, 70, 255)); R(3, 38, 4, 39, (80, 150, 180, 255)); R(-1, 40, 1, 41, (200, 180, 100, 255))
    # cuello y cabeza
    R(-2, 23, 2, 27, dk(skin, 0.82))
    d.rounded_rectangle([CX - 9, 5, CX + 8, 24], radius=4, fill=skin)
    R(6, 8, 9, 23, dk(skin, 0.86)); R(-8, 22, 8, 24, dk(skin, 0.84))
    R(-10, 13, -9, 19, dk(skin, 0.92)); R(9, 13, 10, 19, dk(skin, 0.8))   # orejas
    R(-11, 16, -10, 19, (240, 240, 246, 255)); R(10, 16, 11, 19, (240, 240, 246, 255))   # AirPods
    # pelo
    if style == "spiky":
        d.rounded_rectangle([CX - 10, 2, CX + 9, 13], radius=4, fill=hair)
        for x0, top in ((-9, 0), (-4, -1), (1, 0), (5, 1)):
            R(x0, max(top, 0), x0 + 5, 6, hair)
        R(-10, 8, -6, 18, hair); R(-6, 9, -1, 13, hair); R(8, 8, 10, 16, dk(hair, 0.8))
        R(-7, 3, -2, 5, lt(hair, 1.5)); R(2, 3, 6, 4, lt(hair, 1.3))
    elif style == "cap":
        cap = ch["cap"] + (255,)
        d.rounded_rectangle([CX - 10, 2, CX + 9, 11], radius=4, fill=cap)
        R(-10, 8, 10, 12, dk(cap, 0.7)); R(-6, 3, -2, 6, lt(cap, 1.3)); R(6, 4, 9, 9, dk(cap, 0.8))
        R(-10, 12, -7, 18, hair); R(7, 12, 10, 18, hair)
    elif style == "pony":
        d.rounded_rectangle([CX - 10, 2, CX + 9, 13], radius=4, fill=hair)
        R(-11, 8, -8, 24, hair); R(8, 8, 11, 24, dk(hair, 0.85))
        R(-9, 8, 9, 12, hair); R(-2, 11, 1, 14, hair); R(4, 11, 8, 13, hair)
        R(-7, 3, -2, 5, lt(hair, 1.6)); R(-10, 10, -9, 22, lt(hair, 1.4))
    elif style == "curly":
        d.rounded_rectangle([CX - 10, 3, CX + 9, 12], radius=4, fill=hair)
        for x0 in (-10, -6, -2, 2, 6):
            d.ellipse([CX + x0, 0, CX + x0 + 5, 6], fill=hair)
        R(-10, 8, -8, 15, hair); R(8, 8, 10, 15, dk(hair, 0.8))
        R(-7, 2, -4, 3, lt(hair, 1.8)); R(2, 1, 5, 2, lt(hair, 1.6))
    # ojos (5x4, iris visible + brillo)
    ec = ch["eye"] + (255,)

    def eye(sx, side):
        y0 = 14
        if expr in ("happy", "blink"):
            for dx, dy in ((0, 3), (1, 2), (2, 2), (3, 2), (4, 3)):
                P(sx + dx, y0 + dy, INK)
            return
        if expr == "shock":
            y0 = 13
        R(sx, y0, sx + 5, y0 + (6 if expr == "shock" else 4), (236, 236, 240, 255))
        R(sx, y0, sx + 5, y0 + 1, DARK)
        ix = max(sx, min(sx + 2, sx + 1 + look))
        if expr == "shock":
            R(sx + 1, y0 + 2, sx + 4, y0 + 5, ec); R(sx + 2, y0 + 3, sx + 3, y0 + 4, DARK); P(sx + 1, y0 + 2, WHITE)
        else:
            R(ix, y0 + 1, ix + 3, y0 + 4, ec); R(ix, y0 + 3, ix + 3, y0 + 4, lt(ec, 1.35))
            P(ix + 1, y0 + 2, DARK); P(ix + 1, y0 + 3, DARK); P(ix, y0 + 1, WHITE)
        if expr == "angry":
            R(sx, y0, sx + 5, y0 + 2, dk(skin, 0.7))
            R(sx + (3 if side < 0 else 0), y0 + 2, sx + (5 if side < 0 else 2), y0 + 3, dk(skin, 0.7))
        elif expr == "sad":
            R(sx + (0 if side < 0 else 2), y0, sx + (3 if side > 0 else 5) if side > 0 else sx + 3, y0 + 2, dk(skin, 0.75))
        elif expr in ("smug", "shy"):
            R(sx, y0, sx + 5, y0 + 2, dk(skin, 0.72)); R(sx, y0 + 2, sx + 5, y0 + 3, DARK)
        if bags:
            R(sx, y0 + 5, sx + 5, y0 + 6, (130, 96, 140, 255))

    eye(-7, -1); eye(2, 1)
    bc = dk(hair, 0.8)
    for sx, side in ((-7, -1), (2, 1)):
        if expr == "angry":
            R(sx, 11 if side < 0 else 12, sx + 3, 12 if side < 0 else 13, bc); R(sx + 3, 12 if side < 0 else 11, sx + 6, 13 if side < 0 else 12, bc)
            if side < 0:
                R(sx, 11, sx + 3, 12, bc); R(sx + 3, 12, sx + 6, 13, bc)
            else:
                R(sx, 12, sx + 3, 13, bc); R(sx + 3, 11, sx + 6, 12, bc)
        elif expr == "sad":
            if side < 0:
                R(sx, 12, sx + 3, 13, bc); R(sx + 3, 11, sx + 6, 12, bc)
            else:
                R(sx, 11, sx + 3, 12, bc); R(sx + 3, 12, sx + 6, 13, bc)
        elif expr == "shock":
            R(sx, 10, sx + 6, 11, bc)
        else:
            R(sx, 12 if expr != "smug" else 13, sx + 6, 13 if expr != "smug" else 14, bc)
    if "tear" in fx:
        R(-6, 19, -5, 23, (140, 190, 220, 255)); P(-6, 19, WHITE)
    if expr in ("happy", "angry", "shy", "shock") or "blush" in fx:
        R(-8, 19, -5, 20, (196, 110, 110, 255)); R(5, 19, 8, 20, (196, 110, 110, 255))
    P(0, 18, dk(skin, 0.76)); P(1, 18, dk(skin, 0.76))
    m = mouth or {"happy": "smile", "sad": "frown", "angry": "open", "shock": "o", "smug": "smirk", "shy": "shy"}.get(expr, "closed")
    if m == "closed":
        R(-1, 21, 3, 22, INK)
    elif m == "open":
        R(-2, 20, 3, 23, INK); R(-1, 22, 2, 23, (190, 80, 90, 255))
    elif m == "big":
        R(-3, 20, 4, 24, INK); R(-2, 23, 3, 24, (190, 80, 90, 255)); R(-3, 20, 4, 21, WHITE)
    elif m == "smile":
        R(-2, 21, 3, 22, INK); P(-3, 20, INK); P(3, 20, INK); R(-1, 22, 2, 23, WHITE)
    elif m == "frown":
        R(-2, 21, 3, 22, INK); P(-3, 22, INK); P(3, 22, INK)
    elif m == "o":
        R(-1, 20, 2, 24, INK); R(0, 22, 1, 24, (190, 80, 90, 255))
    elif m == "smirk":
        R(-2, 21, 2, 22, INK); R(2, 20, 4, 21, INK)
    elif m == "shy":
        R(-2, 21, 0, 22, INK); R(0, 20, 3, 21, INK)
    if ch.get("glasses"):
        for sx in (-8, 1):
            R(sx, 13, sx + 7, 14, DARK); R(sx, 19, sx + 7, 20, DARK); R(sx, 13, sx + 1, 20, DARK); R(sx + 6, 13, sx + 7, 20, DARK)
            P(sx + 2, 15, (200, 210, 230, 255))
        R(-1, 15, 1, 16, DARK)
    if shades:
        R(-9, 13, 9, 19, (22, 24, 36, 255)); R(-9, 13, 9, 15, (48, 52, 70, 255))
        R(-7, 16, -4, 17, (120, 170, 200, 255)); R(3, 16, 6, 17, (120, 170, 200, 255))
    if headset:
        steel = (84, 90, 110, 255)
        R(-11, 4, 11, 7, steel); R(-11, 5, 11, 6, lt(steel, 1.4)); R(-11, 6, -9, 16, steel); R(9, 6, 11, 16, steel)
        body(-13, 12, -9, 21, (150, 52, 70, 255)); body(9, 12, 13, 21, (150, 52, 70, 255))
        R(-12, 21, -11, 25, steel); R(-12, 24, -5, 25, steel); R(-6, 23, -3, 26, (150, 52, 70, 255))
    if "sweat" in fx:
        R(10, 4, 12, 8, (160, 200, 225, 255)); P(10, 4, WHITE)
    if "vein" in fx:
        R(-10, 0, -7, 1, (190, 50, 50, 255)); R(-9, -1, -8, 3, (190, 50, 50, 255)) if False else R(-9, 0, -8, 3, (190, 50, 50, 255))
    return _vivid(_outline(_chibi(img)))


def draw_char(canvas, name, x, feet_y, flip=False, scale=2, shadow=True, ox=0, oy=0, **kw):
    spr = sprite(name, **kw)
    if flip:
        spr = spr.transpose(Image.FLIP_LEFT_RIGHT)
    big = spr.resize((spr.width * scale, spr.height * scale), Image.NEAREST)
    if shadow:
        sh_l = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh_l).ellipse([x - 15 * scale + ox, feet_y - 6, x + 15 * scale + ox, feet_y + 6], fill=(8, 6, 20, 110))
        canvas.alpha_composite(sh_l)
    canvas.alpha_composite(big, (int(x - big.width // 2 + ox), int(feet_y - (spr.height - 2) * scale + oy)))
