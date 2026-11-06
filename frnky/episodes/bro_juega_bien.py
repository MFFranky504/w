"""«¿Qué pasaría si mi bro finalmente jugara bien?» — categoría: amistad."""
import math
from PIL import Image, ImageDraw

from .. import audio
from ..engine import cam_at
from ..pixel import BRO, CHUY, NATI, MEMO, W, H, draw_char
from ..scene import room, couch_front, table_items, confetti

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
SEAT = dict(chuy=42, bro=105, nati=168, memo=231)
BY, S = 312, 3


def speaking(t):
    for t0, t1, who, _ in LINES:
        if t0 <= t < t1:
            return who.split("+")
    return []


def group(d, t, bro_kw, states, night=False):
    """states: dict nombre -> kwargs para draw_char. Dibuja de atrás hacia adelante."""
    sp = speaking(t)
    for name, ch in (("chuy", CHUY), ("nati", NATI), ("memo", MEMO), ("bro", BRO)):
        kw = dict(states.get(name, {}))
        if name == "bro":
            kw = {**bro_kw, **kw}
        if kw.get("hide"):
            continue
        kw.pop("hide", None)
        talk = name in sp or "todos" in sp
        bob = round(math.sin(t * 5 + SEAT[name]) * 1)
        kw.setdefault("oy", 0); kw["oy"] += bob
        draw_char(d, ch, SEAT[name], BY, S, talk=talk, t=t, **kw)


def frame(t):
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
    bro_old = dict(expr="neutral")
    bro_pro = dict(expr="smug", shades=True, headset=True, shirt=(34, 34, 48))
    shake = 0
    if t < 3.6:  # S1: el conflicto
        room(d, t, (0, 14), "DERROTA")
        group(d, t, bro_old, dict(
            chuy=dict(expr="angry", arms="fist", fx=("vein",), shake=1 if t < 2.3 else 0),
            bro=dict(expr="sad", fx=("tear",), look=-1),
            nati=dict(expr="shock", fx=("sweat",)),
            memo=dict(expr="happy" if t > 2.2 else "smug", arms="down")))
        couch_front(d)
        keys = [(0, 30, 135, 240), (2.0, 28, 120, 250), (2.3, 17, 231, 262), (3.6, 16, 231, 262)]
        shake = 1 if t < 0.4 else 0
    elif t < 8.0:  # S2: lo corren
        room(d, t, (0, 14), "DERROTA")
        sink = round(smooth01((t - 5.3) / 0.3) * 8) if t < 6.5 else 0
        group(d, t, bro_old, dict(
            chuy=dict(expr="angry", arms="point" if t > 6.4 else "ctrl", fx=("vein",), shake=1 if t > 6.4 else 0),
            nati=dict(expr="angry" if t < 5.3 else "shock", arms="point" if t > 6.4 else "ctrl"),
            memo=dict(expr="angry", arms="point" if t > 6.4 else "down"),
            bro=dict(expr="sad", fx=("tear", "sweat"), oy=sink if t < 6.5 else 10, look=1)))
        couch_front(d)
        keys = [(3.6, 17, 168, 262), (5.2, 17, 168, 262), (5.3, 15, 105, 262), (6.4, 15, 105, 262),
                (6.5, 28, 120, 255), (8.0, 25, 105, 260)]
        shake = 2 if t > 6.5 else 0
    elif t < 12.6:  # S3: entrenamiento nocturno
        day = 0 if t < 9.4 else (1 if t < 10.2 else (2 if t < 11.0 else 3))
        kd = [(3, 9), (3, 9), (12, 5), (20, 1)][day]
        room(d, t, kd, "PRÁCTICA", night=True, label="K / D")
        cans = [0, 2, 6, 11][day]
        table_items(d, cans)
        expr = ["neutral", "neutral", "angry", "shock"][day]
        draw_char(d, BRO, 135, BY, 4, expr=expr, t=t, talk=bool(speaking(t)), bags=day >= 2,
                  arms="ctrl", fx=("sweat",) if day >= 2 else (), oy=round(math.sin(t * 12) * (1 + day)),
                  shake=1 if day >= 2 else 0)
        couch_front(d, night=True)
        table_items(d, cans, pizza=day > 0)
        if day:
            from ..pixel import ptext
            ptext(d, (135, 352), f"DÍA {day}", 26, (255, 235, 90))
        keys = [(8.0, 24, 135, 250), (9.4, 21, 135, 258), (12.6, 17, 135, 258)]
        shake = 1 if day >= 2 else 0
    elif t < 16.6:  # S4: vuelve "pro"
        room(d, t, (25, 0), "VICTORIA")
        rise = round(40 * (1 - smooth01((t - 12.6) / 0.35)))
        group(d, t, bro_pro, dict(
            nati=dict(expr="happy", arms="cheer" if t < 13.9 else "ctrl"),
            chuy=dict(expr="happy", arms="cheer" if 13.8 <= t < 14.9 else "ctrl"),
            memo=dict(expr="happy", arms="down" if t < 14.0 else "ctrl"),
            bro=dict(oy=rise, look=0)))
        couch_front(d)
        keys = [(12.6, 30, 135, 240), (14.8, 30, 135, 240), (14.9, 15, 105, 262), (16.6, 15, 105, 262)]
    elif t < 20.5:  # S5: se pone insoportable
        room(d, t, (25, 0), "VICTORIA")
        group(d, t, bro_pro, dict(
            chuy=dict(expr="sad", fx=("tear",), oy=4 if t > 17.9 else 0),
            nati=dict(expr="sad" if t > 19.3 else "shock", arms="down"),
            memo=dict(expr="shock", fx=("sweat",), arms="down"),
            bro=dict(expr="smug", oy=0)))
        couch_front(d)
        keys = [(16.6, 17, 231, 262), (17.8, 17, 231, 262), (17.9, 15, 105, 262), (19.3, 15, 105, 262),
                (19.4, 17, 168, 262), (20.5, 17, 168, 262)]
    elif t < 22.0:  # S6: se arrepiente
        gone = t > 21.3
        room(d, t, (0, 14) if gone else (25, 0), "DERROTA" if gone else "VICTORIA")
        bro_kw = dict(expr="shy", shirt=(34, 34, 48), shades=False, headset=False, look=-1)
        group(d, t, bro_kw, dict(
            chuy=dict(expr="shock", arms="down"), nati=dict(expr="shock", arms="down"),
            memo=dict(expr="shock", arms="down"), bro=dict(arms="down" if gone else "ctrl")))
        couch_front(d)
        keys = [(20.5, 15, 105, 262), (22.0, 15, 105, 262)]
    else:  # final: todos felices, bro de nuevo "malo" (conecta con el primer plano)
        room(d, t, (0, 14), "DERROTA")
        group(d, t, dict(expr="happy"), dict(
            chuy=dict(expr="happy", arms="cheer"), nati=dict(expr="happy", arms="cheer"),
            memo=dict(expr="happy", arms="cheer"), bro=dict(expr="happy", arms="cheer", look=0)))
        confetti(d, t)
        couch_front(d)
        keys = [(22.0, 30, 135, 240), (T, 30, 135, 240)]
        shake = 1 if t < 22.4 else 0
    return img, cam_at(keys, t), shake


def smooth01(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


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


EP = dict(T=T, hook=HOOK, lines=LINES, cuts=CUTS, voices=VOICES, frame=frame, music=music, sfx=sfx, meta=META)
