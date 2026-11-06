"""«¿Qué pasaría si mi bro finalmente jugara bien?» — categoría: amistad."""
import math
from PIL import Image, ImageDraw

from .. import audio
from ..engine import cam_at
from ..sprite import draw_char
from ..bg import room, tv, glow, light_shaft, night_grade, sparkles, cans, confetti, txt

META = dict(id="bro-juega-bien", category="amistad",
            title="¿Qué pasaría si mi bro finalmente jugara bien?",
            caption_hook="Cuando tu bro por fin juega bien… y deja de ser tu bro 💀")
T = 25.2
CUTS = [3.6, 8.0, 12.6, 16.6, 20.5, 22.0]
HOOK = "MI BRO ES EL PEOR DEL EQUIPO"

VOICES = {
    "bro": dict(label="BRO", color=(255, 226, 84), pitch=230),
    "chuy": dict(label="CHUY", color=(255, 130, 120), pitch=170),
    "nati": dict(label="NATI", color=(255, 150, 225), pitch=340),
    "memo": dict(label="MEMO", color=(120, 230, 255), pitch=270),
    "todos": dict(label="TODOS", color=(255, 255, 255), pitch=250),
}
LINES = [
    (0.1, 2.2, "chuy", "¡0 y 14, bro! ¡Ni estorbar sabes!"),
    (2.3, 3.5, "memo", "Hasta el bot te ganó."),
    (3.7, 5.2, "nati", "¿Agarras el control o lo abrazas?"),
    (5.3, 6.4, "bro", "Es que me sudan las manos…"),
    (6.5, 7.9, "chuy", "¡Estás fuera del equipo!"),
    (8.1, 9.3, "bro", "Hoy me vuelvo bueno."),
    (11.1, 12.5, "bro", "Ya entendí el juego."),
    (12.7, 13.8, "nati", "¡¡25 y 0!! ¡Bro!"),
    (13.8, 14.8, "chuy", "¡Ese es mi bro!"),
    (14.9, 16.5, "bro", "Cállense, bots. Me atrasan."),
    (16.7, 17.8, "memo", "¿Qué le pasó a mi bro?"),
    (17.9, 19.3, "bro", "Chuy, ¿ese fue tu mejor intento?"),
    (19.4, 20.4, "nati", "Era más feliz perdiendo…"),
    (20.6, 21.9, "bro", "¿Mejor volvemos a ser malos?"),
    (22.0, 23.0, "todos", "¡ESE ES MI BRO!"),
]
SEAT = dict(chuy=50, bro=135, nati=222, memo=308)
FEET = 395
PRO = dict(expr="smug", shades=True, headset=True, shirt=(36, 36, 52))


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
    talking = (name in sp or "todos" in sp) and int(t * 9) % 2 == 0
    expr = kw.get("expr", "neutral")
    if talking:
        kw["mouth"] = "big" if expr in ("angry", "happy", "shock") else "open"
    x = SEAT[name] if x is None else x
    ox = round(math.sin(t * 61) * shake) if shake else 0
    oy = round(math.sin(t * 5 + x) * 1.5) + kw.pop("oy", 0)
    draw_char(c, name, x, feet, ox=ox, oy=oy, scale=scale, **kw)


def banner(t):
    if 9.4 <= t < 12.0:
        return f"DÍA {1 if t < 10.2 else (2 if t < 11.0 else 3)}"
    return ""


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


def frame(t):
    day = t < 8.0 or t >= 12.6
    c = room(t, night=not day)
    shake = 0
    tvargs = dict(score=(0, 14), verdict="DERROTA")
    if t < 3.6:  # S1: el conflicto, ya desde el primer fotograma
        light_shaft(c)
        char(c, t, "chuy", expr="angry", pose="fist", fx=("vein",), shake=3 if t < 2.3 else 1)
        char(c, t, "bro", expr="sad", fx=("tear",), look=-1, oy=4)
        char(c, t, "nati", expr="shock", fx=("sweat",), pose="ctrl")
        char(c, t, "memo", expr="happy", pose="down", flip=True)
        keys = [(0, 40, 180, 330), (2.0, 36, 160, 330), (2.3, 26, 308, 340), (3.6, 24, 308, 340)]
        shake = 1 if t < 0.4 else 0
    elif t < 8.0:  # S2: lo corren
        light_shaft(c)
        pt = t > 6.4
        char(c, t, "chuy", expr="angry", pose="point" if pt else "ctrl", fx=("vein",), shake=2 if pt else 0)
        char(c, t, "nati", expr="angry" if t < 5.3 else "shock", pose="point" if pt else "ctrl", flip=pt)
        char(c, t, "memo", expr="angry", pose="point" if pt else "down", flip=True)
        char(c, t, "bro", expr="sad", fx=("tear", "sweat"), look=1, oy=8 if t > 5.3 else 3)
        keys = [(3.6, 26, 222, 340), (5.2, 26, 222, 340), (5.3, 24, 135, 340), (6.4, 24, 135, 340),
                (6.5, 40, 180, 330), (8.0, 34, 150, 340)]
        shake = 2 if pt else 0
    elif t < 12.6:  # S3: entrenamiento nocturno
        dn = 0 if t < 9.4 else (1 if t < 10.2 else (2 if t < 11.0 else 3))
        cans(c, [0, 3, 8, 14][dn])
        expr = ["neutral", "angry", "angry", "shock"][dn]
        night_grade(c, 0.42)
        char(c, t, "bro", x=180, feet=410, scale=3, expr=expr, pose="ctrl", bags=dn >= 2,
             fx=("sweat",) if dn >= 2 else (), shake=1 if dn >= 2 else 0)
        tvargs = dict(score=[(3, 9), (3, 9), (12, 5), (20, 1)][dn], verdict="PRÁCTICA", night=True)
        if dn:
            sparkles(c, t, 180, 300, 6, 110)
        keys = [(8.0, 36, 180, 340), (9.4, 30, 180, 340), (12.6, 24, 180, 340)]
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
            sparkles(c, t, SEAT["bro"], 300, 5, 60)
        tvargs = dict(score=(25, 0), verdict="VICTORIA")
        keys = [(12.6, 40, 180, 330), (14.8, 40, 180, 330), (14.9, 24, 135, 340), (16.6, 24, 135, 340)]
    elif t < 20.5:  # S5: se pone insoportable
        light_shaft(c)
        char(c, t, "chuy", expr="sad", fx=("tear",), oy=4 if t > 17.9 else 0, pose="down")
        char(c, t, "nati", expr="sad" if t > 19.3 else "shock", pose="down")
        char(c, t, "memo", expr="shock", fx=("sweat",), pose="down", flip=True)
        char(c, t, "bro", pose="ctrl", **PRO)
        sparkles(c, t, SEAT["bro"], 300, 4, 60)
        tvargs = dict(score=(25, 0), verdict="VICTORIA")
        keys = [(16.6, 26, 308, 340), (17.8, 26, 308, 340), (17.9, 24, 135, 340), (19.3, 24, 135, 340),
                (19.4, 26, 222, 340), (20.5, 26, 222, 340)]
    elif t < 22.0:  # S6: se arrepiente
        gone = t > 21.3
        light_shaft(c)
        for n_ in ("chuy", "nati", "memo"):
            char(c, t, n_, expr="shock", pose="down", flip=(n_ == "memo"))
        char(c, t, "bro", expr="shy", pose="down" if gone else "ctrl", look=-1, shirt=(36, 36, 52))
        tvargs = dict(score=(0, 14), verdict="DERROTA") if gone else dict(score=(25, 0), verdict="VICTORIA")
        keys = [(20.5, 24, 135, 340), (22.0, 24, 135, 340)]
    else:  # final: todos felices, bro de nuevo "malo" (cierra el bucle con el primer plano)
        light_shaft(c)
        for n_ in ("chuy", "nati", "bro", "memo"):
            char(c, t, n_, expr="happy", pose="cheer", flip=(n_ == "memo"))
        confetti(c, t)
        keys = [(22.0, 40, 180, 330), (T, 40, 180, 330)]
        shake = 1 if t < 22.4 else 0
    tv(c, t, **tvargs)
    if not day:
        c = Image.fromarray(__import__("numpy").asarray(glow(c, (104, 96, 258, 244), (80, 130, 255), 150, 26))).convert("RGBA")
    return c, cam_at(keys, t), shake


def music(track):
    audio.groove(track, 0, 3.6, 140, 57, True, True, True)
    audio.groove(track, 3.6, 5.3, 140, 57, True, False, False, 0.8)
    audio.groove(track, 6.4, 8.0, 140, 57, True, True, False)
    audio.groove(track, 8.0, 12.6, 150, 52, True, True, True)
    audio.riser(track, 9.4, 12.5)
    audio.groove(track, 12.6, 16.6, 150, 60, False, True, True)
    audio.groove(track, 16.6, 20.4, 100, 57, True, False, False, 0.7)
    audio.groove(track, 22.0, T, 150, 60, False, True, True)


def sfx(track):
    audio.powerup(track, 12.6)
    audio.scratch(track, 14.9)
    audio.trombone(track, 20.6)
    audio.jingle(track, 22.0)


EP = dict(banner=banner, hud=hud, T=T, hook=HOOK, lines=LINES, cuts=CUTS, voices=VOICES, frame=frame, music=music, sfx=sfx, meta=META)
