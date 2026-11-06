"""«¿Qué pasaría si mi bro finalmente jugara bien?» — categoría: amistad."""
import math
from PIL import Image, ImageDraw

from .. import audio
from ..engine import cam_at
from ..sprite import draw_char
from ..bg import room, light_shaft, sparkles, confetti

META = dict(id="bro-juega-bien", category="amistad",
            title="¿Qué pasaría si mi bro finalmente jugara bien?",
            caption_hook="Cuando tu bro por fin juega bien… y deja de ser tu bro 💀")
T = 25.2
CUTS = [3.6, 8.0, 12.6, 16.6, 20.5, 22.0]
HOOK = "MI BRO ES EL PEOR DEL EQUIPO"

G, Wh, R_, Y, B, SK = (0, 104, 71), (240, 240, 240), (206, 17, 38), (252, 209, 22), (0, 56, 147), (116, 172, 223)
FLAGS = {  # (x0, y0, x1, y1, color) en 0..1
    "MX": [(0, 0, 1 / 3, 1, G), (1 / 3, 0, 2 / 3, 1, Wh), (2 / 3, 0, 1, 1, R_)],
    "AR": [(0, 0, 1, 1 / 3, SK), (0, 1 / 3, 1, 2 / 3, Wh), (0, 2 / 3, 1, 1, SK)],
    "VE": [(0, 0, 1, 1 / 3, Y), (0, 1 / 3, 1, 2 / 3, B), (0, 2 / 3, 1, 1, R_)],
    "CL": [(0, 0, 1, 0.5, Wh), (0, 0.5, 1, 1, R_), (0, 0, 0.36, 0.5, B)],
}
VOICES = {
    "bro": dict(label="BRO", color=(226, 200, 120), pitch=230, flag=FLAGS["CL"]),     # Chile
    "chuy": dict(label="CHUY", color=(222, 140, 130), pitch=170, flag=FLAGS["MX"]),   # México
    "nati": dict(label="NATI", color=(214, 150, 190), pitch=340, flag=FLAGS["AR"]),   # Argentina
    "memo": dict(label="MEMO", color=(130, 190, 210), pitch=270, flag=FLAGS["VE"]),   # Venezuela
    "todos": dict(label="TODOS", color=(255, 255, 255), pitch=250),
}
LINES = [
    (0.1, 2.2, "chuy", "¡No manches, 0 y 14, bro!"),
    (2.3, 3.5, "memo", "Hasta el bot te ganó, chamo."),
    (3.7, 5.2, "nati", "¿Agarrás el control o lo abrazás?"),
    (5.3, 6.4, "bro", "Es que me sudan las manos, po…"),
    (6.5, 7.9, "chuy", "¡Estás fuera del equipo, güey!"),
    (8.1, 9.3, "bro", "Hoy me vuelvo bueno."),
    (11.1, 12.5, "bro", "Ya entendí el juego."),
    (12.7, 13.8, "nati", "¡25 y 0! ¡Mirá vos, bro!"),
    (13.8, 14.8, "chuy", "¡Ese es mi bro!"),
    (14.9, 16.5, "bro", "Cállense, bots. Me atrasan."),
    (16.7, 17.8, "memo", "¿Qué le pasó a mi bro, chamo?"),
    (17.9, 19.3, "bro", "Chuy, ¿ese fue tu mejor intento?"),
    (19.4, 20.4, "nati", "Era más feliz perdiendo, che…"),
    (20.6, 21.9, "bro", "¿Mejor volvemos a ser malos?"),
    (22.0, 23.0, "todos", "¡ESE ES MI BRO!"),
]
SEAT = dict(chuy=50, bro=135, nati=222, memo=308)
FEET = 352
PRO = dict(expr="smug", shades=True, headset=True, shirt=(34, 34, 46))


def speaking(t):
    for t0, t1, who, _ in LINES:
        if t0 <= t < t1:
            return who.split("+")
    return []


def smooth01(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def char(c, t, name, x=None, shake=0, scale=2, feet=FEET, **kw):
    sp = speaking(t)
    talking = (name in sp or "todos" in sp) and int(t * 7) % 2 == 0
    expr = kw.get("expr", "neutral")
    if talking:
        kw["mouth"] = "big" if expr in ("angry", "happy", "shock") else "open"
    x = SEAT[name] if x is None else x
    ox = round(math.sin(t * 61) * shake) if shake else 0
    oy = round(math.sin(t * 5 + x) * 1.5) + kw.pop("oy", 0)
    draw_char(c, name, x, feet, ox=ox, oy=oy, scale=scale, **kw)


def hud(t):
    lvl = 1
    if 8.0 <= t < 21.3:
        lvl = 1 if t < 9.4 else (30 if t < 10.2 else (62 if t < 11.0 else 99))
        if t >= 12.6:
            lvl = 99
    vibe = 100
    if t < 8.0:
        vibe = max(0, round(100 - 100 * min(1, t / 6.5)))
    elif t < 12.6:
        vibe = 0
    elif t < 14.9:
        vibe = 100
    elif t < 20.5:
        vibe = max(0, round(100 - 100 * (t - 14.9) / 5.0))
    elif t < 22.0:
        vibe = 0
    return lvl, vibe


def scene_state(t):
    """Marcador de la TV, noche y latas según el momento."""
    if t < 8.0:
        return dict(score=(0, 14), verdict="DERROTA")
    if t < 12.6:
        dn = 0 if t < 9.4 else (1 if t < 10.2 else (2 if t < 11.0 else 3))
        return dict(night=True, cans_n=[0, 3, 8, 14][dn], verdict="PRÁCTICA", score=[(3, 9), (3, 9), (12, 5), (20, 1)][dn])
    if t < 20.5:
        return dict(score=(25, 0), verdict="VICTORIA")
    if t < 22.0:
        return dict(score=(0, 14), verdict="DERROTA") if t > 21.3 else dict(score=(25, 0), verdict="VICTORIA")
    return dict(score=(0, 14), verdict="DERROTA")


def frame(t):
    c = room(t, **scene_state(t))
    shake = 0
    if t < 3.6:  # S1: el conflicto, ya desde el primer fotograma
        light_shaft(c)
        char(c, t, "chuy", expr="angry", pose="fist", fx=("vein",), shake=3 if t < 2.3 else 1)
        char(c, t, "bro", expr="sad", fx=("tear",), look=-1, oy=4)
        char(c, t, "nati", expr="shock", fx=("sweat",), pose="ctrl")
        char(c, t, "memo", expr="happy", pose="down", flip=True)
        keys = [(0, 40, 180, 290), (2.0, 36, 160, 290), (2.3, 26, 308, 296), (3.6, 24, 308, 296)]
        shake = 1 if t < 0.4 else 0
    elif t < 8.0:  # S2: lo corren
        light_shaft(c)
        pt = t > 6.4
        char(c, t, "chuy", expr="angry", pose="point" if pt else "ctrl", fx=("vein",), shake=2 if pt else 0)
        char(c, t, "nati", expr="angry" if t < 5.3 else "shock", pose="point" if pt else "ctrl", flip=pt)
        char(c, t, "memo", expr="angry", pose="point" if pt else "down", flip=True)
        char(c, t, "bro", expr="sad", fx=("tear", "sweat"), look=1, oy=8 if t > 5.3 else 3)
        keys = [(3.6, 26, 222, 296), (5.2, 26, 222, 296), (5.3, 24, 135, 296), (6.4, 24, 135, 296),
                (6.5, 40, 180, 290), (8.0, 34, 150, 296)]
        shake = 2 if pt else 0
    elif t < 12.6:  # S3: entrenamiento nocturno
        dn = 0 if t < 9.4 else (1 if t < 10.2 else (2 if t < 11.0 else 3))
        expr = ["neutral", "angry", "angry", "shock"][dn]
        char(c, t, "bro", x=180, feet=366, scale=3, expr=expr, pose="ctrl", bags=dn >= 2,
             fx=("sweat",) if dn >= 2 else (), shake=1 if dn >= 2 else 0)
        if dn:
            sparkles(c, t, 180, 250, 6, 110)
        keys = [(8.0, 36, 180, 296), (9.4, 30, 180, 296), (12.6, 24, 180, 296)]
        shake = 1 if dn >= 2 else 0
    elif t < 16.6:  # S4: vuelve "pro"
        light_shaft(c)
        walk = smooth01((t - 12.6) / 1.0)
        bx = -40 + (SEAT["bro"] + 40) * walk
        bob = -abs(math.sin(t * 12)) * 5 if walk < 1 else 0
        char(c, t, "nati", expr="happy", pose="cheer" if t < 13.9 else "ctrl")
        char(c, t, "chuy", expr="happy", pose="cheer" if 13.8 <= t < 14.9 else "ctrl")
        char(c, t, "memo", expr="happy", pose="down", flip=True)
        char(c, t, "bro", x=bx, oy=bob, pose="ctrl", **PRO)
        if t > 13.6:
            sparkles(c, t, SEAT["bro"], 260, 5, 60)
        keys = [(12.6, 40, 180, 290), (14.8, 40, 180, 290), (14.9, 24, 135, 296), (16.6, 24, 135, 296)]
    elif t < 20.5:  # S5: se pone insoportable
        light_shaft(c)
        char(c, t, "chuy", expr="sad", fx=("tear",), oy=4 if t > 17.9 else 0, pose="down")
        char(c, t, "nati", expr="sad" if t > 19.3 else "shock", pose="down")
        char(c, t, "memo", expr="shock", fx=("sweat",), pose="down", flip=True)
        char(c, t, "bro", pose="ctrl", **PRO)
        sparkles(c, t, SEAT["bro"], 260, 4, 60)
        keys = [(16.6, 26, 308, 296), (17.8, 26, 308, 296), (17.9, 24, 135, 296), (19.3, 24, 135, 296),
                (19.4, 26, 222, 296), (20.5, 26, 222, 296)]
    elif t < 22.0:  # S6: se arrepiente
        gone = t > 21.3
        light_shaft(c)
        for n_ in ("chuy", "nati", "memo"):
            char(c, t, n_, expr="shock", pose="down", flip=(n_ == "memo"))
        char(c, t, "bro", expr="shy", pose="down" if gone else "ctrl", look=-1, shirt=(34, 34, 46))
        keys = [(20.5, 24, 135, 296), (22.0, 24, 135, 296)]
    else:  # final: todos felices, bro de nuevo "malo" (cierra el bucle con el primer plano)
        light_shaft(c)
        for n_ in ("chuy", "nati", "bro", "memo"):
            char(c, t, n_, expr="happy", pose="cheer", flip=(n_ == "memo"))
        confetti(c, t)
        keys = [(22.0, 40, 180, 290), (T, 40, 180, 290)]
        shake = 1 if t < 22.4 else 0
    return c, cam_at(keys, t), shake


K = 1.35   # estiramiento del tiempo: ritmo más pausado (todo lo de arriba está en tiempo base)


def banner(t):
    if 8.0 <= t < 9.3:
        return "ESA NOCHE…"
    if 9.4 <= t < 12.0:
        return f"DÍA {1 if t < 10.2 else (2 if t < 11.0 else 3)}"
    if 12.7 <= t < 14.0:
        return "REGRESÓ… DIFERENTE"
    if 16.6 <= t < 17.8:
        return "SE LE SUBIÓ A LA CABEZA"
    return ""


def music(track):
    g = lambda a, b, *x, **k: audio.groove(track, a * K, b * K, *x, **k)
    g(0, 3.6, 132, "min")                                   # arranque tenso y con energía
    g(3.6, 5.3, 132, "min", layers=("bass", "pad", "arp"))
    g(5.3, 6.4, 132, "min", layers=("pad",), vol=0.9)       # momento triste
    g(6.4, 8.0, 132, "min", layers=("bass", "pad", "arp", "drums"))
    g(8.0, 12.6, 144, "min", layers=("bass", "pad", "arp", "drums"))   # entrenamiento: sube la tensión
    audio.riser(track, 9.4 * K, 12.5 * K)
    g(12.6, 16.6, 138, "maj")                               # victoria
    g(16.6, 20.4, 138, "min", layers=("bass", "pad"), vol=0.7)       # incómodo
    g(20.4, 22.0, 138, "min", layers=("pad",), vol=0.6)
    g(22.0, T, 138, "maj")                                  # final festivo


def sfx(track):
    audio.hit(track, 0.0)
    audio.ding(track, 1.7)
    audio.powerup(track, 12.6 * K)
    audio.scratch(track, 14.9 * K)
    audio.trombone(track, 20.6 * K)
    audio.jingle(track, 22.0 * K)


HOOKS = [(0.0, 1.7, "LO CORRIERON POR SER MALO…"), (1.7, 3.6, "¡Y SE VOLVIÓ DEMASIADO BUENO!")]

EP = dict(
    T=T * K, hooks=HOOKS, cuts=[c * K for c in CUTS], voices=VOICES,
    lines=[(a * K, b * K, w, x) for a, b, w, x in LINES],
    frame=lambda t: frame(t / K), hud=lambda t: hud(t / K), banner=lambda t: banner(t / K),
    music=music, sfx=sfx, meta=META)
