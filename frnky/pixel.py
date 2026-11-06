"""Personajes y utilidades de pixel art (todo original, dibujado con rectángulos)."""
import math
from PIL import ImageFont

W, H = 270, 480          # lienzo base; se escala x4 a 1080x1920
OL = (28, 20, 44)        # contorno
WHITE = (255, 255, 255)


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


def pfont(size):
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    return f


def ptext(d, xy, text, size, fill, anchor="mm", outline=OL):
    d.fontmode = "1"
    f = pfont(size)
    x, y = xy
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        d.text((x + dx, y + dy), text, font=f, fill=outline, anchor=anchor)
    d.text((x, y), text, font=f, fill=fill, anchor=anchor)


BRO = dict(name="bro", skin=(238, 184, 136), hair=(96, 60, 38), shirt=(60, 110, 214),
           eye=(70, 130, 220), style="spiky")
CHUY = dict(name="chuy", skin=(244, 196, 150), hair=(30, 28, 36), shirt=(74, 170, 98),
            eye=(120, 80, 40), style="cap", cap=(226, 60, 60))
NATI = dict(name="nati", skin=(210, 150, 108), hair=(40, 30, 56), shirt=(236, 120, 176),
            eye=(100, 60, 140), style="pony")
MEMO = dict(name="memo", skin=(150, 104, 72), hair=(54, 36, 28), shirt=(244, 200, 60),
            eye=(40, 90, 60), style="curly", glasses=True)


def draw_char(d, ch, cx, by, s=3, expr="neutral", talk=False, t=0.0, look=0,
              arms="ctrl", fx=(), shades=False, headset=False, bags=False,
              shake=0, oy=0, shirt=None):
    """Dibuja busto de personaje. cx=centro, by=base del torso, s=tamaño de 'pixel'."""
    if shake:
        cx += round(math.sin(t * 61) * shake)
        by += round(math.cos(t * 47) * shake * 0.6)
    by += oy
    skin, hair = ch["skin"], ch["hair"]
    shirt = shirt or ch["shirt"]
    sk_d = shade(skin, 0.82)

    def R(x0, y0, x1, y1, c):
        d.rectangle([cx + math.floor(x0 * s), by + math.floor(y0 * s),
                     cx + math.floor(x1 * s) - 1, by + math.floor(y1 * s) - 1], fill=c)

    def O(x0, y0, x1, y1, c):  # rectángulo con contorno
        R(x0 - 1, y0 - 1, x1 + 1, y1 + 1, OL)
        R(x0, y0, x1, y1, c)

    style = ch["style"]
    if style == "pony":  # cola de caballo detrás
        O(10, -25, 14, -15, hair)
        R(10, -21, 14, -20, (255, 90, 150))
    # torso
    O(-9, -10, 9, 1, shirt)
    R(-9, -2, 9, 1, shade(shirt, 0.8))
    R(-3, -10, 3, -9, shade(shirt, 0.7))          # cuello de la prenda
    R(-6, -9, -5, -4, shade(shirt, 1.18))         # brillo
    # cuello
    R(-2, -12, 2, -10, sk_d)
    # brazos
    ctrl = arms in ("ctrl", "fist", "point")
    if ctrl:
        O(-11, -9, -8, -2, shirt); R(-8, -4, -5, -1, skin)
        if arms == "ctrl":
            O(8, -9, 11, -2, shirt); R(5, -4, 8, -1, skin)
        O(-6, -4, 6, 0, (70, 74, 96))            # control
        R(-5, -3, -3, -1, (230, 60, 60)); R(3, -3, 5, -1, (80, 200, 255))
        R(-1, -3, 1, -2, (255, 220, 80))
    if arms == "down":
        O(-12, -10, -9, 0, shirt); O(9, -10, 12, 0, shirt)
        R(-12, -1, -9, 1, skin); R(9, -1, 12, 1, skin)
    if arms == "fist":                              # puño arriba (grita)
        O(9, -24, 12, -9, shirt); O(8, -29, 13, -24, skin)
    if arms == "point":                             # señala al frente/lado
        O(9, -13, 21, -9, shirt); O(21, -14, 25, -9, skin)
    if arms == "cheer":
        O(-13, -25, -10, -9, shirt); O(-14, -30, -9, -25, skin)
        O(10, -25, 13, -9, shirt); O(9, -30, 14, -25, skin)
    # cabeza
    for pad, c in ((1, OL), (0, skin)):
        R(-8 - pad, -25 - pad, 8 + pad, -13 + pad, c)
        R(-7 - pad, -26 - pad, 7 + pad, -12 + pad, c)
    R(-7, -13, 7, -12, sk_d)
    R(-9, -21, -8, -17, skin); R(8, -21, 9, -17, skin)  # orejas
    # pelo
    if style == "spiky":
        R(-9, -29, 9, -23, hair); R(-8, -30, 8, -29, hair)
        for x0 in (-8, -4, 0, 4):
            R(x0, -33 + (x0 % 3), x0 + 3, -29, hair)
        R(-9, -26, -2, -22, hair); R(-9, -22, -8, -19, hair); R(8, -26, 9, -20, hair)
    elif style == "cap":
        cap = ch["cap"]
        R(-9, -30, 9, -24, cap); R(-8, -31, 8, -30, cap); R(-1, -33, 1, -31, shade(cap, .8))
        R(-9, -25, 9, -23, shade(cap, 0.7)); R(-10, -24, 10, -23, shade(cap, 0.7))
        R(-9, -23, -8, -19, hair); R(8, -23, 9, -19, hair)
    elif style == "pony":
        R(-9, -29, 9, -23, hair); R(-8, -30, 8, -29, hair)
        R(-9, -26, 9, -23, hair); R(-10, -26, -8, -15, hair); R(8, -26, 10, -15, hair)
        R(-3, -23, 1, -22, hair); R(3, -24, 6, -23, shade(hair, 1.4))
    elif style == "curly":
        R(-9, -29, 9, -23, hair)
        for x0 in (-10, -6, -2, 2, 6):
            R(x0, -32, x0 + 4, -28, hair)
        R(-10, -28, 10, -23, hair); R(-9, -23, -8, -18, hair); R(8, -23, 9, -18, hair)
        R(-5, -31, -3, -30, shade(hair, 1.5)); R(3, -31, 5, -30, shade(hair, 1.5))
    # ojos
    eyes = (-6, 1)
    e = expr
    for sx in eyes:
        mirror = 1 if sx < 0 else -1  # +1 ceja interna hacia el centro
        if e in ("happy", "blink"):
            R(sx, -19, sx + 1, -18, OL); R(sx + 1, -20, sx + 4, -19, OL); R(sx + 4, -19, sx + 5, -18, OL)
        else:
            top = -23 if e == "shock" else -22
            R(sx, top, sx + 5, -17, OL)
            R(sx, top + 1, sx + 5, -17, WHITE) if e != "shades" else None
            R(sx, top, sx + 5, top + 1, OL)
            ix = sx + 1 + (look if e != "shock" else 0)
            ix = max(sx, min(sx + 2, ix))
            if e == "shock":
                R(sx + 2, -21, sx + 3, -19, ch["eye"]); R(sx + 2, -21, sx + 3, -20, OL)
            else:
                R(ix, top + 1, ix + 3, -17, ch["eye"])
                R(ix + 1, top + 2, ix + 2, -18, OL)            # pupila
                R(ix, top + 1, ix + 1, top + 2, WHITE)          # brillo
            if e == "angry":
                inner = sx + 5 if mirror > 0 else sx
                for k in range(3):
                    xx = (sx + k * 2) if mirror > 0 else (sx + 4 - k * 2)
                    R(xx, -24 + k, xx + 2, -23 + k, OL)
                R(sx, -22, sx + 5, -21, OL)
            elif e == "sad":
                for k in range(3):
                    xx = (sx + 4 - k * 2) if mirror > 0 else (sx + k * 2)
                    R(xx, -24 + k, xx + 2, -23 + k, OL)
        if bags:
            R(sx, -16, sx + 5, -15, (120, 80, 140))
    if "tear" in fx:
        R(-5, -16, -4, -12, (120, 200, 255))
    # mejillas
    if e in ("angry", "happy", "shy"):
        R(-8, -16, -6, -14, (255, 130, 130)); R(6, -16, 8, -14, (255, 130, 130))
    if e == "angry":
        R(-8, -16, -6, -14, (240, 70, 70)); R(6, -16, 8, -14, (240, 70, 70))
    # boca
    mouth = e
    if talk and int(t * 10) % 2 == 0:
        mouth = "talk"
    if mouth in ("neutral", "blink", "smug", "shades"):
        R(-2, -15, 2, -14, OL)
    elif mouth == "talk":
        R(-2, -16, 2, -13, OL); R(-1, -14, 1, -13, (220, 80, 90))
    elif mouth in ("shock", "angry"):
        R(-3, -17, 3, -12, OL); R(-2, -14, 2, -12, (220, 80, 90)); R(-2, -17, 2, -16, WHITE)
    elif mouth in ("happy",):
        R(-3, -16, 3, -12, OL); R(-2, -14, 2, -12, (220, 80, 90)); R(-3, -16, 3, -15, WHITE)
    elif mouth == "sad":
        R(-2, -15, 2, -14, OL); R(-3, -14, -2, -13, OL); R(2, -14, 3, -13, OL)
    elif mouth == "shy":
        R(-2, -15, 1, -14, OL); R(1, -16, 3, -15, OL)
    if e == "smug":
        R(1, -16, 4, -15, OL)
    # accesorios
    if ch.get("glasses"):
        for sx in eyes:
            R(sx - 1, -23, sx + 6, -22, OL); R(sx - 1, -17, sx + 6, -16, OL)
            R(sx - 1, -23, sx, -16, OL); R(sx + 5, -23, sx + 6, -16, OL)
        R(-1, -20, 1, -19, OL)
    if shades:
        R(-8, -23, 8, -17, OL); R(-1, -21, 1, -20, OL)
        R(-6, -22, -4, -21, (120, 200, 255)); R(1, -22, 3, -21, (120, 200, 255))
        R(-8, -23, 8, -22, (40, 40, 60))
    if headset:
        R(-10, -31, 10, -29, (70, 72, 90)); R(-10, -31, -9, -20, (70, 72, 90)); R(9, -31, 10, -20, (70, 72, 90))
        O(-12, -24, -9, -16, (230, 50, 90)); O(9, -24, 12, -16, (230, 50, 90))
        R(-10, -16, -9, -13, (70, 72, 90)); R(-10, -14, -4, -13, (70, 72, 90)); R(-5, -15, -3, -12, (230, 50, 90))
    if "sweat" in fx:
        R(9, -30, 11, -27, (140, 210, 255)); R(9, -27, 11, -26, (140, 210, 255))
    if "vein" in fx:
        R(-9, -31, -6, -30, (230, 40, 40)); R(-8, -32, -7, -29, (230, 40, 40))
        R(6, -31, 9, -30, (230, 40, 40)); R(7, -32, 8, -29, (230, 40, 40))
