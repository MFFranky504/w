"""Sprites chibi de cuerpo completo (estilo JRPG 32 bits): cabeza ~42% de la altura, ojos grandes con brillo,
rampas de 3 tonos (luz cálida / sombra fría), contorno selectivo y ropa moderna. Diseño 48x62 px, x2 en el lienzo."""
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

SW, SH, CX = 48, 62, 24
DARK = (30, 18, 44, 255)
WHITE = (250, 248, 244, 255)
INK = (110, 46, 58, 255)


def dk(c, f=0.72):   # sombra: baja valor y se enfría
    return (int(c[0] * f * 0.96), int(c[1] * f * 0.98), min(255, int(c[2] * f * 1.08)), 255)


def lt(c, f=1.16):   # luz: sube valor y se calienta
    return (min(255, int(c[0] * f + 8)), min(255, int(c[1] * f + 5)), min(255, int(c[2] * f)), 255)


CHARS = {   # Bro (Chile), Chuy (México), Nati (Argentina), Memo (Venezuela)
    "bro": dict(skin=(244, 190, 150), hair=(110, 70, 44), coat=(58, 96, 214), kind="hoodie", trim=(236, 236, 244),
                pants=(66, 92, 150), shoe=(240, 240, 248), sole=(120, 130, 170), eye=(60, 150, 235), style="spiky"),
    "chuy": dict(skin=(246, 200, 156), hair=(40, 30, 40), coat=(32, 150, 84), kind="jersey", trim=(244, 244, 240),
                 pants=(52, 62, 100), shoe=(240, 240, 240), sole=(210, 60, 70), eye=(150, 90, 40), style="cap",
                 cap=(222, 52, 62), band=True),
    "nati": dict(skin=(226, 164, 126), hair=(100, 56, 190), coat=(110, 190, 245), kind="jersey", trim=(34, 48, 120),
                 stripes=(246, 246, 250), pants=(38, 38, 56), shoe=(246, 246, 250), sole=(160, 160, 190),
                 eye=(150, 70, 210), style="pony"),
    "memo": dict(skin=(164, 112, 80), hair=(52, 36, 30), coat=(160, 34, 62), kind="jersey", trim=(246, 200, 50),
                 pants=(96, 100, 120), shoe=(56, 56, 72), sole=(236, 236, 240), eye=(50, 150, 96), style="curly",
                 glasses=True, jog=True),
}


def _vivid(img, k=1.25):
    a = np.array(img).astype("float32")
    g = a[..., :3].mean(axis=2, keepdims=True)
    a[..., :3] = np.clip(g + (a[..., :3] - g) * k, 0, 255)
    return Image.fromarray(a.astype("uint8"))


def _outline(img):
    """Contorno selectivo: cada borde toma el color del píxel vecino, muy oscurecido (como en tu referencia)."""
    a = np.array(img).astype("float32")
    m = a[..., 3] > 0
    acc = np.zeros(a.shape[:2] + (3,), dtype="float32"); cnt = np.zeros(a.shape[:2], dtype="float32")
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        sh_m = np.roll(m, (dy, dx), axis=(0, 1)); sh_c = np.roll(a[..., :3], (dy, dx), axis=(0, 1))
        acc += np.where(sh_m[..., None], sh_c, 0); cnt += sh_m
    ring = (~m) & (cnt > 0)
    col = acc / np.maximum(cnt, 1)[..., None]
    col = col * 0.28 + np.array([14, 8, 30]) * 0.7
    out = a.copy()
    out[ring, :3] = col[ring]; out[ring, 3] = 255
    return Image.fromarray(out.astype("uint8"))


@lru_cache(maxsize=4096)
def sprite(name, expr="neutral", mouth=None, pose="down", look=0, fx=(), shades=False,
           headset=False, bags=False, shirt=None, walk=0):
    ch = CHARS[name]
    skin, hair = ch["skin"] + (255,), ch["hair"] + (255,)
    coat = (shirt or ch["coat"]) + (255,)
    pants, acc = ch["pants"] + (255,), ch["trim"] + (255,)
    style, kind = ch["style"], ch["kind"]
    img = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def R(x0, y0, x1, y1, c):
        d.rectangle([CX + x0, y0, CX + x1 - 1, y1 - 1], fill=c)

    def P(x, y, c):
        d.point((CX + x, y), fill=c)

    def body(x0, y0, x1, y1, c):  # luz arriba-izquierda, sombra derecha y abajo
        R(x0, y0, x1, y1, c)
        R(x1 - 2, y0, x1, y1, dk(c, 0.78)); R(x0, y0, x0 + 1, y1, lt(c, 1.12))
        R(x0, y1 - 1, x1, y1, dk(c, 0.82))

    hl = lt(hair, 1.6)
    if style == "pony":     # pelo largo detrás del cuerpo
        body(-15, 14, 15, 42, hair)
    # ---- piernas y tenis (chibi: cortas) ----
    lL, lR = (3 if walk == 1 else 0), (3 if walk == 2 else 0)
    body(-6, 45, -1, 55 - lL, pants); body(1, 45, 6, 55 - lR, pants)
    if ch.get("jog"):
        R(-6, 46, -5, 54 - lL, (240, 240, 244, 255)); R(5, 46, 6, 54 - lR, (240, 240, 244, 255))
    if name in ("bro", "chuy"):     # bolsillos cargo
        R(-6, 48, -3, 51, dk(pants, 0.8)); R(3, 48, 6, 51, dk(pants, 0.8)); R(-6, 48, -3, 49, lt(pants, 1.25)); R(3, 48, 6, 49, lt(pants, 1.25))
    shoe, sole = ch["shoe"] + (255,), ch["sole"] + (255,)
    body(-8, 53 - lL, -1, 59 - lL, shoe); body(1, 53 - lR, 8, 59 - lR, shoe)
    R(-8, 58 - lL, -1, 60 - lL, sole); R(1, 58 - lR, 8, 60 - lR, sole)
    R(-7, 54 - lL, -4, 55 - lL, WHITE); R(2, 54 - lR, 5, 55 - lR, WHITE)
    # ---- torso ----
    body(-8, 29, 8, 46, coat)
    R(-8, 45, 8, 46, dk(coat, 0.7))
    if ch.get("stripes"):
        for x0 in range(-8, 6, 4):
            R(x0 + 2, 30, x0 + 4, 45, ch["stripes"] + (255,))
        R(6, 30, 8, 45, dk(coat, 0.78))
    if kind == "hoodie":
        R(-6, 28, 6, 32, dk(coat, 0.62)); R(-5, 28, 5, 30, dk(coat, 0.85))
        R(-3, 32, -2, 38, acc); R(2, 32, 3, 37, acc)
        R(-5, 40, 5, 44, dk(coat, 0.82)); R(-5, 40, 5, 41, lt(coat, 1.12))
    else:
        R(-4, 29, 4, 31, acc); R(-3, 31, 3, 32, acc); R(-1, 32, 1, 33, acc)
        R(-8, 29, -6, 31, acc); R(6, 29, 8, 31, acc)
        R(3, 35, 6, 38, WHITE if name != "nati" else (34, 48, 120, 255)); P(4, 36, (210, 50, 60, 255))
    sl = 40 if kind == "hoodie" else 34
    hand = skin
    L = sl - 30

    def vert_arm(x0, x1, y0, y1):
        R(x0, y0, x1, y1, hand)
        body(x0, y0, x1, min(y1, y0 + L), coat)
        R(x0, y1 - 1, x1, y1, dk(hand, 0.8))

    def stair_arm(pts, hands_at):
        """Brazo en escalera: pts = [(x0,y0)...] bloques de 3x4; los últimos van en piel."""
        for i, (x0, y0) in enumerate(pts):
            if i < max(1, L // 4):
                body(x0, y0, x0 + 4, y0 + 4, coat)
            else:
                R(x0, y0, x0 + 4, y0 + 4, hand); R(x0, y0 + 3, x0 + 4, y0 + 4, dk(hand, 0.8))
        hx, hy = hands_at
        R(hx, hy, hx + 5, hy + 5, hand); R(hx, hy + 4, hx + 5, hy + 5, dk(hand, 0.8))

    if pose != "cheer":
        vert_arm(-11, -8, 30, 47)
        if ch.get("band"):
            R(-11, 41, -8, 42, (32, 150, 84, 255)); R(-11, 42, -8, 43, WHITE); R(-11, 43, -8, 44, (210, 50, 60, 255))
    if pose == "down":
        vert_arm(8, 11, 30, 47)
    elif pose == "fist":
        stair_arm([(8, 30), (12, 26), (16, 21)], (17, 12))
    elif pose == "point":
        stair_arm([(8, 30), (12, 32), (16, 34)], (19, 35))
    elif pose == "cheer":
        stair_arm([(-12, 30), (-16, 26), (-20, 21)], (-22, 12))
        stair_arm([(8, 30), (12, 26), (16, 21)], (17, 12))
    elif pose == "ctrl":
        vert_arm(8, 11, 30, 40)
        R(-11, 38, 11, 42, coat if kind == "hoodie" else hand)
        R(-7, 39, -4, 43, hand); R(4, 39, 7, 43, hand)
        body(-5, 38, 5, 44, (70, 74, 100, 255))
        R(-4, 39, -3, 40, (190, 70, 70, 255)); R(3, 39, 4, 40, (80, 160, 200, 255)); R(-1, 41, 1, 42, (220, 190, 100, 255))
    # ---- cuello y cabeza (grande) ----
    R(-3, 27, 3, 30, dk(skin, 0.82))
    d.rounded_rectangle([CX - 14, 4, CX + 13, 29], radius=7, fill=skin)
    R(10, 8, 14, 27, dk(skin, 0.88)); R(-11, 27, 11, 29, dk(skin, 0.84)); R(-12, 8, -10, 9, lt(skin, 1.08))
    R(-15, 16, -14, 22, dk(skin, 0.92)); R(14, 16, 15, 22, dk(skin, 0.8))          # orejas
    R(-16, 18, -14, 22, (244, 244, 250, 255)); R(14, 18, 16, 22, (244, 244, 250, 255))   # AirPods
    # ---- pelo ----
    if style == "spiky":
        d.rounded_rectangle([CX - 15, 3, CX + 14, 16], radius=6, fill=hair)
        for x0, top in ((-14, 0), (-8, -1), (-2, 0), (4, -1), (9, 1)):
            R(x0, max(top, 0), x0 + 7, 8, hair)
        R(-15, 12, -9, 24, hair); R(-9, 13, -1, 19, hair); R(-5, 19, -1, 22, hair); R(12, 12, 15, 22, dk(hair, 0.8))
        R(-12, 4, -5, 7, hl); R(-4, 2, 1, 4, hl); R(3, 3, 9, 6, lt(hair, 1.3))
    elif style == "cap":
        cap = ch["cap"] + (255,)
        d.rounded_rectangle([CX - 15, 2, CX + 14, 15], radius=7, fill=cap)
        R(-15, 11, 15, 16, dk(cap, 0.7)); R(-17, 15, 17, 18, dk(cap, 0.58))
        R(-10, 4, -3, 8, lt(cap, 1.35)); R(-1, 0, 2, 3, dk(cap, 0.8)); R(10, 5, 14, 12, dk(cap, 0.8))
        R(-14, 18, -12, 22, hair); R(12, 18, 14, 22, hair)
    elif style == "pony":
        d.rounded_rectangle([CX - 15, 2, CX + 14, 16], radius=7, fill=hair)
        R(-15, 12, -11, 30, hair); R(11, 12, 15, 30, dk(hair, 0.85))
        R(-12, 12, 12, 17, hair); R(-3, 15, 1, 19, hair); R(5, 15, 9, 18, hair)
        R(-11, 4, -3, 7, hl); R(-14, 14, -13, 28, hl); R(2, 9, 8, 11, lt(hair, 1.3))
        R(9, 4, 14, 9, (255, 100, 170, 255))     # moño
    elif style == "curly":
        d.rounded_rectangle([CX - 15, 4, CX + 14, 15], radius=6, fill=hair)
        for x0 in (-15, -9, -3, 3, 9):
            d.ellipse([CX + x0, 0, CX + x0 + 7, 9], fill=hair)
        R(-15, 12, -11, 20, hair); R(11, 12, 15, 20, dk(hair, 0.8))
        R(-11, 2, -7, 4, hl); R(-1, 1, 3, 3, hl); R(6, 2, 10, 4, hl)
    # ---- ojos grandes con iris y brillo ----
    ec = ch["eye"] + (255,)

    EW = 4     # ojos proporcionados: óvalos oscuros pequeños con brillo, como en la referencia
    EY = 17

    def eye(sx, side):
        y0 = EY
        if expr in ("happy", "blink"):
            for dx, dy in ((0, 4), (1, 3), (2, 3), (3, 4)):
                R(sx + dx, y0 + dy, sx + dx + 1, y0 + dy + 1, INK)
            return
        h = 6
        if expr == "shock":
            y0, h = EY - 1, 8
            R(sx - 1, y0, sx + EW + 1, y0 + h, (244, 244, 248, 255)); R(sx, y0 + 2, sx + EW, y0 + h - 1, dk(ec, 0.6))
            R(sx + 1, y0 + 3, sx + 3, y0 + 6, DARK); P(sx, y0 + 2, WHITE)
            return
        R(sx, y0, sx + EW, y0 + h, dk(ec, 0.55))                      # iris oscuro
        R(sx, y0 + 3, sx + EW, y0 + h, dk(ec, 0.8)); R(sx, y0 + h - 1, sx + EW, y0 + h, ec)   # degradado
        R(sx, y0, sx + EW, y0 + 1, DARK)                              # párpado
        px = max(sx, min(sx + 2, sx + 1 + look))
        R(px, y0 + 2, px + 2, y0 + h - 1, DARK)                       # pupila
        P(sx, y0 + 1, WHITE); P(sx, y0 + 2, WHITE)                    # brillo
        P(sx + 3, y0 + h - 2, lt(ec, 1.5))
        inner = side < 0
        if expr == "angry":
            R(sx, y0, sx + EW, y0 + 2, dk(skin, 0.72))
            R(sx + (2 if inner else 0), y0 + 2, sx + (EW if inner else 2), y0 + 3, dk(skin, 0.72))
        elif expr == "sad":
            R(sx + (0 if inner else 2), y0, sx + (2 if inner else EW), y0 + 2, dk(skin, 0.78))
        elif expr in ("smug", "shy"):
            R(sx, y0, sx + EW, y0 + 3, dk(skin, 0.74)); R(sx, y0 + 3, sx + EW, y0 + 4, DARK)
        if bags:
            R(sx, y0 + h, sx + EW, y0 + h + 1, (150, 100, 190, 255))

    eye(-9, -1); eye(5, 1)
    bc = dk(hair, 0.85) if style != "cap" else dk(hair, 1.0)
    for sx, side in ((-9, -1), (5, 1)):
        inner = side < 0
        if expr == "angry":
            R(sx, 14 if inner else 15, sx + 2, 15 if inner else 16, bc); R(sx + 2, 15 if inner else 14, sx + EW, 16 if inner else 15, bc)
        elif expr == "sad":
            R(sx, 15 if inner else 14, sx + 2, 16 if inner else 15, bc); R(sx + 2, 14 if inner else 15, sx + EW, 15 if inner else 16, bc)
        elif expr == "shock":
            R(sx, 13, sx + EW, 14, bc)
        else:
            y = 14 if expr not in ("smug",) else 15
            R(sx, y, sx + EW, y + 1, bc)
    if "tear" in fx:
        R(-9, 24, -7, 30, (140, 210, 255, 255)); P(-9, 24, WHITE)
    if expr in ("happy", "angry", "shy", "shock") or "blush" in fx:
        R(-12, 24, -8, 26, (255, 120, 140, 255)); R(8, 24, 12, 26, (255, 120, 140, 255))
    m = mouth or {"happy": "smile", "sad": "frown", "angry": "open", "shock": "o", "smug": "smirk", "shy": "shy"}.get(expr, "closed")
    if m == "closed":
        R(-2, 26, 3, 27, INK)
    elif m == "open":
        R(-3, 25, 4, 29, INK); R(-2, 28, 3, 29, (220, 90, 100, 255)); R(-3, 25, 4, 26, WHITE)
    elif m == "big":
        R(-4, 25, 5, 30, INK); R(-3, 28, 4, 30, (220, 90, 100, 255)); R(-4, 25, 5, 27, WHITE)
    elif m == "smile":
        R(-3, 26, 4, 27, INK); P(-4, 25, INK); P(4, 25, INK); R(-2, 27, 3, 29, INK); R(-2, 27, 3, 28, WHITE)
    elif m == "frown":
        R(-3, 26, 4, 27, INK); P(-4, 27, INK); P(4, 27, INK)
    elif m == "o":
        R(-2, 25, 3, 30, INK); R(-1, 28, 2, 30, (220, 90, 100, 255))
    elif m == "smirk":
        R(-3, 26, 2, 27, INK); R(2, 25, 5, 26, INK)
    elif m == "shy":
        R(-3, 26, 0, 27, INK); R(0, 25, 4, 26, INK)
    # ---- accesorios ----
    if ch.get("glasses"):
        for sx in (-11, 3):
            R(sx, 15, sx + 8, 16, DARK); R(sx, 25, sx + 8, 26, DARK); R(sx, 15, sx + 1, 26, DARK); R(sx + 7, 15, sx + 8, 26, DARK)
            R(sx + 1, 16, sx + 3, 18, (255, 255, 255, 110))
        R(-3, 19, 3, 20, DARK)
    if shades:
        R(-12, 16, 12, 25, (26, 28, 44, 255)); R(-12, 16, 12, 19, (56, 62, 86, 255))
        R(-9, 20, -4, 21, (130, 190, 230, 255)); R(5, 20, 10, 21, (130, 190, 230, 255)); R(-9, 22, -7, 23, (130, 190, 230, 255))
    if headset:
        steel = (90, 98, 124, 255)
        R(-12, 2, 12, 4, steel); R(-12, 2, 12, 3, lt(steel, 1.4)); R(-15, 4, -12, 7, steel); R(12, 4, 15, 7, steel)
        R(-17, 7, -15, 14, steel); R(15, 7, 17, 14, steel)
        body(-20, 14, -15, 24, (210, 56, 90, 255)); body(15, 14, 20, 24, (210, 56, 90, 255))
        R(-19, 24, -17, 28, steel); R(-19, 27, -8, 28, steel); R(-9, 26, -5, 29, (210, 56, 90, 255))
    if "sweat" in fx:
        R(13, 4, 16, 10, (160, 215, 245, 255)); P(14, 4, WHITE)
    if "vein" in fx:
        R(-14, 0, -10, 1, (230, 50, 50, 255)); R(-12, -1, -11, 4, (230, 50, 50, 255)) if False else R(-12, 0, -11, 4, (230, 50, 50, 255))
    pad = Image.new("RGBA", (SW + 16, SH + 6), (0, 0, 0, 0))
    pad.paste(img, (8, 5))
    return _vivid(_outline(pad))


def draw_char(canvas, name, x, feet_y, flip=False, scale=2, shadow=True, ox=0, oy=0, **kw):
    spr = sprite(name, **kw)
    if flip:
        spr = spr.transpose(Image.FLIP_LEFT_RIGHT)
    big = spr.resize((spr.width * scale, spr.height * scale), Image.NEAREST)
    if shadow:
        sh_l = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh_l).ellipse([x - 14 * scale + ox, feet_y - 6, x + 14 * scale + ox, feet_y + 6], fill=(8, 6, 20, 110))
        canvas.alpha_composite(sh_l)
    canvas.alpha_composite(big, (int(x - big.width // 2 + ox), int(feet_y - (spr.height - 3) * scale + oy)))
