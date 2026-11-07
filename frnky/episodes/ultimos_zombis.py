"""«¿Qué pasaría si mi bro y yo fuéramos los últimos hombres en la tierra?» — situación ganadora, versión zombi.
Guion corto (29 s) para probar la duración de 20-35 s. Funciona en estilo pixel o kawaii (mismo guion, mismo CTA)."""
import math

from .. import audio, scenes3 as S3
from ..bg import light_shaft, sparkles, confetti, emote, speed_lines
from ..cast import make_cast
from ..engine import cam_at
from ..sprite import draw_char
from . import bro_juega_bien as B
from .bro_juega_bien import sm

K = 1.1
T = 29.0 / K                  # 29.0 s = 696 fotogramas exactos
CUTS = [7.0, 12.0, 16.0, 21.0, 23.9]
META = dict(id="ultimos-zombis", category="ultimo-hombre", topic="ultimo-hombre",
            title="¿Qué pasaría si mi bro y yo fuéramos los últimos hombres en la tierra?",
            caption_hook="¿Qué pasaría si mi bro y yo fuéramos los últimos hombres en la tierra?")
CAST = make_cast(META["id"])
SPRITE = {"bro": CAST["bro"]["sprite"], "a": CAST["a"]["sprite"], "zombi": "zombi"}
TAG = {"bro": CAST["bro"]["tag"], "a": CAST["a"]["tag"]}
VOICES = {
    "bro": dict(label=CAST["bro"]["label"], color=CAST["bro"]["color"], pitch=230, flag=CAST["bro"]["flag"]),
    "a": dict(label=CAST["a"]["label"], color=CAST["a"]["color"], pitch=300, flag=CAST["a"]["flag"]),
    "zombi": dict(label="ZOMBI", color=(150, 220, 140), pitch=110),
    "todos": dict(label="TODOS", color=(255, 255, 255), pitch=250),
}
LINES = [
    (0.1, 2.1, "bro", "Solo quedamos tú y yo… y mi bolsa de papas."),
    (2.2, 3.7, "a", f"¿Papas? ¡Yo traigo el plan, {TAG['a']}!"),
    (3.8, 5.2, "bro", "¿Cuál es el plan?"),
    (5.3, 6.9, "a", "Primero, repartimos la bolsa."),
    (7.3, 8.7, "bro", f"¿Escuchaste eso, {TAG['bro']}?"),
    (8.8, 10.2, "a", "¡Un zombi! ¡Corre!"),
    (10.3, 11.9, "bro", "¡Pero mis papas!"),
    (12.3, 13.7, "a", "¡Déjalas, bro!"),
    (13.8, 15.9, "bro", "¡Jamás! ¡Soy fiel a mis papas!"),
    (16.3, 17.7, "zombi", "Papaaas…"),
    (17.8, 19.3, "bro", "…¿Quieres una?"),
    (19.4, 20.9, "a", "¡¿Le diste la última papa?!"),
    (21.2, 22.6, "bro", "Es que ya éramos tres."),
    (22.7, 23.8, "todos", "¡LOS ÚLTIMOS TRES!"),
]
HOOKS = [(0.0, 1.7, "¿QUÉ PASARÍA SI MI BRO Y YO…"), (1.7, 3.0, "…FUÉRAMOS LOS ÚLTIMOS EN LA TIERRA?")]
B.LINES_ACTIVE[0] = LINES
M, FEET = 3, 372


def hud(t):
    return [("SOBREVIVIENTES", "2" if t < 21 or t >= 23.9 else "3"), ("PAPAS", "1" if t < 17.8 or t >= 23.9 else "0")]


def banner(t):
    if 7.0 <= t < 8.0:
        return "EN EL SÚPER…"
    if 12.0 <= t < 13.0:
        return "¡CORRE!"
    if 16.0 <= t < 17.0:
        return "FRENTE A FRENTE…"
    return ""


def ch(c, t, key, **kw):
    sp = B.speaking(t)
    expr = kw.get("expr", "neutral")
    if (key in sp or "todos" in sp) and int(t * 7) % 2 == 0:
        kw["mouth"] = "big" if expr == "happy" else ("o" if expr == "shock" else "open")
    elif expr in ("neutral", "sad", "shy") and ((t * 24 * 1.1 + kw.get("x", 100) * 0.37) % 76) < 3:
        kw["expr"] = "blink"                                   # parpadeo
    x = kw.pop("x"); feet = kw.pop("feet", FEET); sc = kw.pop("scale", M)
    shake = kw.pop("shake", 0); hop = kw.pop("hop", 0); bag = kw.pop("bag", False)
    ox = round(math.sin(t * 61) * shake) if shake else 0
    breathe = round(math.sin(t * 2.6 + x) * 1.5 + math.sin(t * 5 + x) * .6)           # respiración
    oy = breathe - (round(abs(math.sin(t * 9 + x)) * hop) if hop else 0) + kw.pop("oy", 0)
    draw_char(c, SPRITE[key], x, feet, ox=ox, oy=oy, scale=sc, **kw)
    if bag:                                                                           # bolsa de papas
        from PIL import ImageDraw
        d = ImageDraw.Draw(c)
        bx, by = x + (24 if not kw.get("flip") else -36) + ox, feet - 62 * sc // 2 + oy
        d.rectangle([bx - 1, by - 1, bx + 15, by + 21], fill=(30, 18, 44)); d.rectangle([bx, by, bx + 14, by + 20], fill=(250, 200, 70))
        d.rectangle([bx, by, bx + 3, by + 20], fill=(255, 226, 120)); d.rectangle([bx + 4, by + 8, bx + 10, by + 14], fill=(220, 60, 60))


def s1(c, t, lt):
    light_shaft(c, 10)
    ch(c, t, "bro", x=105, expr="sad", pose="down", fx=("sweat",), look=1, bag=True)
    ch(c, t, "a", x=255, expr="shy", pose="down", flip=True, look=-1)
    if 0.3 < lt < 1.6:
        emote(c, 105, 190, "!", lt - 0.3)


def frame(t):
    shake = 0
    te = t if t < 23.9 else t - T
    if t < 7.0 or t >= 23.9:
        c = S3.calle_vacia(te)
        s1(c, te, t if t < 7 else 0.0)
        keys = [(0, 40, 105, 290), (2.1, 34, 105, 270), (2.2, 30, 255, 270), (3.7, 30, 255, 270), (3.8, 30, 105, 270),
                (5.2, 30, 105, 270), (5.3, 30, 255, 270), (7.0, 40, 180, 290)]
        if t >= 23.9:
            keys = [(23.9, 40, 180, 290), (T, 40, 180, 290)]
            keys = [(23.9, 40, 105, 290), (T, 40, 105, 290)]
        keys = [(0, 40, 105, 290)] + keys[1:] if t < 7 else keys
    elif t < 12.0:
        c = S3.super_vacio(t)
        zx = 420 - 190 * sm((t - 7.3) / 2.0) if t < 10.3 else 230
        ch(c, t, "bro", x=105, expr="shock" if t > 8.8 else "neutral", pose="down", bag=True, hop=0)
        ch(c, t, "a", x=210, expr="shock" if t > 8.8 else "shy", pose="down", flip=True)
        if t > 7.5:
            ch(c, t, "zombi", x=min(420, zx + 30), feet=FEET, expr="sad", pose="point", flip=True, scale=2, walk=1 + int(t * 5) % 2)
        if 8.8 < t < 10.2:
            emote(c, 210, 190, "!", t - 8.8)
        keys = [(7.0, 40, 150, 290), (7.3, 32, 105, 268), (8.7, 32, 105, 268), (8.8, 30, 210, 268), (10.2, 30, 210, 268),
                (10.3, 30, 105, 268), (12.0, 36, 150, 290)]
    elif t < 16.0:
        c = S3.calle_vacia(t)
        u = (t - 12.0) / 4.0
        bx = 40 + 300 * u
        sh = 1
        ch(c, t, "a", x=bx - 70, feet=FEET, expr="shock", pose="cheer", walk=1 + int(t * 8) % 2, flip=False, hop=5)
        ch(c, t, "bro", x=bx, feet=FEET, expr="angry", pose="down", walk=1 + int(t * 8 + 1) % 2, bag=True, hop=5, shake=sh)
        ch(c, t, "zombi", x=bx - 150, feet=FEET, expr="sad", pose="point", scale=2, walk=1 + int(t * 6) % 2)
        speed_lines(c, bx, 260, t, 70)
        keys = [(12.0, 40, 70, 290), (16.0, 34, 340, 290)]
    elif t < 21.0:
        c = S3.calle_vacia(t)
        light_shaft(c, 10)
        give = t >= 17.8
        ch(c, t, "bro", x=105, expr="shy" if t < 17.8 else "happy", pose="down", bag=not give or t < 18.6, look=1, fx=("sweat",))
        ch(c, t, "zombi", x=250, expr="sad" if t < 17.8 else "happy", pose="point" if t < 18.6 else "cheer", flip=True)
        ch(c, t, "a", x=330, expr="shock", pose="down", flip=True, scale=2, feet=FEET - 4)
        if 17.8 < t < 19.3:
            sparkles(c, t, 250, 262, 6, 90)
        keys = [(16.0, 40, 180, 290), (16.3, 32, 250, 270), (17.7, 32, 250, 270), (17.8, 32, 105, 270), (19.3, 32, 105, 270),
                (19.4, 30, 330, 275), (20.9, 30, 330, 275), (21.0, 40, 180, 290)]
    else:
        c = S3.super_vacio(t)
        for k, (nm, x, fl) in enumerate((("bro", 90, False), ("zombi", 195, True), ("a", 300, True))):
            ch(c, t, nm, x=x, expr="happy", pose="cheer", flip=fl, hop=5)
        confetti(c, t)
        sparkles(c, t, 195, 262, 7, 120)
        keys = [(21.0, 40, 180, 290), (23.9, 40, 180, 290)]
    return c, cam_at(keys, t), shake


def music(track):
    g = lambda a, b, *x, **k: audio.groove(track, a * K, b * K, *x, **k)
    g(0, 7.0, 96, "min", layers=("bass", "pad", "arp", "lead"), mel="b")
    g(7.0, 12.0, 120, "min", layers=("bass", "pad", "arp", "drums"))
    g(12.0, 16.0, 156, "min", mel="b")
    g(16.0, 21.0, 84, "maj", layers=("bass", "pad", "lead"), vol=0.9)
    g(21.0, 23.9, 140, "maj", mel="b")
    g(23.9, T, 96, "min", layers=("bass", "pad", "arp", "lead"), mel="b", bar0=2)
    for a, b, kind in ((0, 7.0, "street"), (7.0, 12.0, "room"), (12.0, 21.0, "street"), (21.0, 23.9, "room"), (23.9, T, "street")):
        audio.ambient(track, a * K, b * K, kind, 1.0)


def sfx(track):
    A = audio
    A.airhorn(track, 0.0, 0.1); A.hit(track, 0.0)
    A.scratch(track, 5.3 * K); A.step(track, 7.05 * K)
    for k in range(5):
        A.step(track, (7.6 + 0.45 * k) * K, 0.1)
    A.dun_dun(track, 8.8 * K) if hasattr(A, "dun_dun") else None
    A.powerup(track, 12.0 * K)
    for k in range(14):
        A.step(track, (12.1 + 0.28 * k) * K, 0.12)
    A.hit(track, 16.0 * K); A.sparkle(track, 17.8 * K); A.levelup(track, 18.0 * K)
    A.crowd(track, 21.0 * K, 1.3, 0.14); A.jingle(track, 22.7 * K); A.airhorn(track, 22.7 * K, 0.1)
    A.rimshot(track, 24.0 * K)
    A.roll(track, T * K - 1.3, T * K)


PUNCHES = [(c * K, 6) for c in CUTS] + [(a * K, 2.5) for a, _, _, _ in LINES]
EP = dict(
    T=T * K, hooks=HOOKS, cuts=[c * K for c in CUTS], voices=VOICES, punches=PUNCHES,
    lines=[(a * K, b * K, w, x) for a, b, w, x in LINES],
    frame=lambda t: frame(t / K), hud=lambda t: hud(t / K), banner=lambda t: banner(t / K),
    music=music, sfx=sfx, meta=META)
