"""«¿Qué pasaría si mi bro finalmente comenzara a josear?» (josear = trabajar, jerga venezolana). Trabajo."""
import math

import zlib

from .. import audio, scenes2 as S2, scenes3 as S3
from ..cast import make_cast
from ..bg import room, light_shaft, sparkles, confetti, emote, speed_lines
from ..engine import cam_at
from ..sprite import draw_char
from . import bro_juega_bien as B
from .bro_juega_bien import VOICES as V0, FLAGS, SEAT, sm

K = 1.15
T = 34.0 / K                  # 34.0 s = 816 fotogramas exactos
CUTS = [6.9, 11.9, 14.2, 20.4, 27.5]
META = dict(id="bro-josea", category="trabajo",
            title="¿Qué pasaría si mi bro finalmente comenzara a josear?",
            caption_hook="Cuando tu bro por fin consigue josear y ya no habla como persona 😭")
# Elenco propio de este video (cambia con cada episodio). «Josear» es venezolano: el rol c lo es siempre.
CAST = make_cast(META["id"], force={"c": "VE"})
ROLE = {"bro": "bro", "chuy": "a", "nati": "b", "memo": "c"}          # clave de subtítulos -> rol del elenco
SPRITE = {k: CAST[r]["sprite"] for k, r in ROLE.items()}
SPRITE["bro_w"] = CAST["bro"]["work"]
SPRITE["ramos"] = "vega" if zlib.crc32(META["id"].encode()) % 2 else "ramos"
BOSS = "JEFA VEGA" if SPRITE["ramos"] == "vega" else BOSS
VOICES = {k: dict(label=CAST[r]["label"], color=CAST[r]["color"], pitch=CAST[r]["pitch"], flag=CAST[r]["flag"]) for k, r in ROLE.items()}
VOICES["ramos"] = dict(label=BOSS, color=(170, 226, 150), pitch=150)
VOICES["todos"] = dict(label="TODOS", color=(255, 255, 255), pitch=250)
T_ = {k: CAST[r]["tag"] for k, r in ROLE.items()}
LINES = [
    (0.1, 2.0, "memo", "¡¿Mi bro consiguió josear?!"),
    (2.1, 3.5, "chuy", f"¿Josear? ¿Tú, {T_['chuy']}?"),
    (3.6, 5.0, "nati", f"¿Y los videojuegos, {T_['nati']}?"),
    (5.1, 6.6, "bro", f"Empiezo el lunes, {T_['bro']}."),
    (7.2, 8.8, "ramos", "Pase. Su primera junta."),
    (8.9, 10.3, "bro", "Perfecto. Quedamos pendientes."),
    (10.4, 11.8, "ramos", "Eso fue un meme, no un informe."),
    (12.2, 13.8, "bro", "Hay que alinear sinergias."),
    (14.5, 15.8, "chuy", "Bro, ¿jugamos hoy?"),
    (15.9, 17.2, "bro", "No puedo. Tengo junta."),
    (17.3, 18.6, "memo", f"¡Ya ni habla como persona, {T_['memo']}!"),
    (18.7, 20.2, "nati", f"Habla como LinkedIn, {T_['nati']}."),
    (20.7, 22.1, "bro", f"Me cayó el primer pago, {T_['bro']}."),
    (22.2, 23.5, "chuy", f"¡Ahora sí invitas, {T_['chuy']}!"),
    (23.6, 25.0, "bro", "Mejor… ¡pago los tacos de todos!"),
    (25.1, 26.4, "todos", "¡ESE ES MI BRO!"),
]
HOOKS = [(0.0, 1.7, "MI BRO CONSIGUIÓ TRABAJO…"), (1.7, 3.0, "¡Y YA NO HABLA COMO PERSONA!")]
B.LINES_ACTIVE[0] = LINES
M = 3
FEET = 372


def hud(t):
    sueldo = "$0" if t < 20.7 else ("$500" if t < 23.6 else "$0")
    sin = 0 if t < 7.2 else (60 if t < 12.2 else (100 if t < 20.7 else 0))
    if t >= 27.5:
        sueldo, sin = "$0", 0
    return [("SUELDO", sueldo), ("SINERGIA", f"{sin}%")]


def banner(t):
    if 11.9 <= t < 12.9:
        return "UNA SEMANA DESPUÉS…"
    if 20.4 <= t < 21.4:
        return "DÍA DE PAGO"
    return ""


def ch(c, t, name, spk=None, **kw):
    """Dibuja un personaje; spk = nombre con el que aparece en LINES (para animar la boca)."""
    sp = B.speaking(t)
    spk = spk or name
    if (spk in sp or "todos" in sp) and int(t * 7) % 2 == 0:
        expr = kw.get("expr", "neutral")
        kw["mouth"] = "big" if expr == "happy" else ("o" if expr == "shock" else "open")
    x = kw.pop("x", SEAT.get(name, 180))
    sc = kw.pop("scale", M)
    shake = kw.pop("shake", 0)
    hop = kw.pop("hop", 0)
    ox = round(math.sin(t * 61) * shake) if shake else 0
    oy = round(math.sin(t * 5 + x) * 1.5) - (round(abs(math.sin(t * 9 + x)) * hop) if hop else 0) + kw.pop("oy", 0)
    draw_char(c, SPRITE[name], x, kw.pop("feet", FEET), ox=ox, oy=oy, scale=sc, **kw)


def s1(c, t, lt):
    """Sala: Memo grita la noticia (escena inicial = escena del bucle)."""
    light_shaft(c, 14)
    ch(c, t, "chuy", x=50, scale=2, expr="shock", pose="down", feet=352)
    ch(c, t, "bro", x=135, scale=2, expr="shy", pose="down", fx=("sweat",), look=-1, feet=352)
    ch(c, t, "nati", x=222, scale=2, expr="shock", pose="phone", feet=352)
    ch(c, t, "memo", x=308, scale=2, expr="happy", pose="fist", flip=True, shake=2 if lt < 2.0 else 0, feet=352)
    if 0.12 < lt < 0.9:
        speed_lines(c, 308, 270, t, int(100 * (1 - (lt - 0.12) / 0.78)))
    if 0.3 < lt < 1.5:
        emote(c, 135, 196, "!", lt - 0.3)


def frame(t):
    shake = 0
    te = t if t < 27.5 else t - T
    if t < 6.9 or t >= 27.5:
        lt = t if t < 6.9 else 0.0
        c = S3.azotea(te)
        s1(c, te, lt)
        keys = [(0, 40, 180, 290), (2.0, 36, 300, 285), (2.1, 28, 50, 268), (3.5, 28, 50, 268), (3.6, 28, 222, 268),
                (5.0, 28, 222, 268), (5.1, 26, 135, 268), (6.6, 26, 135, 268), (6.9, 40, 180, 290)]
        if t >= 27.5:
            keys = [(27.5, 40, 180, 290), (T, 40, 180, 290)]
    elif t < 11.9:
        c = S3.oficina(t)
        light_shaft(c, 10)
        ch(c, t, "bro_w", spk="bro", x=105, expr="happy" if t < 8.9 else "shy", pose="phone" if 8.9 <= t < 10.4 else "down", fx=("sweat",) if t >= 10.4 else ())
        ch(c, t, "ramos", x=255, expr="neutral" if t < 10.4 else "angry", pose="point" if t >= 10.4 else "down", flip=True)
        if t > 10.4:
            emote(c, 105, 196, "?", t - 10.4)
        keys = [(6.9, 40, 180, 290), (7.2, 30, 255, 268), (8.8, 30, 255, 268), (8.9, 30, 105, 268), (10.3, 30, 105, 268),
                (10.4, 30, 255, 268), (11.9, 30, 255, 268)]
    elif t < 14.2:
        c = S3.oficina(t)
        light_shaft(c, 10)
        ch(c, t, "bro_w", spk="bro", x=180, expr="smug", pose="phone", shades=False, bags=True)
        ch(c, t, "ramos", x=300, expr="happy", pose="down", flip=True, scale=2, feet=352)
        sparkles(c, t, 180, 262, 6, 100)
        keys = [(11.9, 40, 180, 290), (12.2, 30, 180, 268), (14.2, 28, 180, 268)]
    elif t < 20.4:
        c = S3.azotea(t)
        light_shaft(c, 14)
        ch(c, t, "chuy", x=50, scale=2, expr="happy", pose="down", feet=352)
        ch(c, t, "nati", x=222, scale=2, expr="shock" if t >= 18.7 else "sad", pose="down", feet=352)
        ch(c, t, "memo", x=308, scale=2, expr="shock" if 17.3 <= t < 18.7 else "sad", pose="down", flip=True, feet=352)
        ch(c, t, "bro_w", spk="bro", x=135, scale=2, expr="smug", pose="phone", feet=352)
        if 17.3 < t < 18.6:
            emote(c, 308, 196, "?", t - 17.3)
        keys = [(14.2, 40, 180, 290), (14.5, 28, 50, 268), (15.8, 28, 50, 268), (15.9, 28, 135, 268), (17.2, 28, 135, 268),
                (17.3, 28, 308, 268), (18.6, 28, 308, 268), (18.7, 28, 222, 268), (20.2, 28, 222, 268), (20.4, 40, 180, 290)]
    elif t < 27.5:
        c = S3.taqueria(t)
        light_shaft(c, 10)
        ch(c, t, "bro_w", spk="bro", x=60 if t < 25.1 else 60, expr="happy" if t >= 20.7 else "neutral", pose="phone" if t < 23.6 else "cheer",
           hop=4 if t >= 25.1 else 0, scale=2, feet=392)
        ch(c, t, "chuy", x=150, scale=2, expr="happy", pose="cheer" if t >= 25.1 else "down", hop=5 if t >= 25.1 else 0, feet=392)
        ch(c, t, "nati", x=240, scale=2, expr="happy", pose="cheer" if t >= 25.1 else "down", hop=5 if t >= 25.1 else 0, feet=392)
        ch(c, t, "memo", x=320, scale=2, expr="happy", pose="cheer" if t >= 25.1 else "down", flip=True, hop=5 if t >= 25.1 else 0, feet=392)
        if t >= 25.1:
            confetti(c, t)
        if 20.7 < t < 23.6:
            sparkles(c, t, 60, 290, 6, 90)
        keys = [(20.4, 40, 180, 290), (20.7, 30, 60, 300), (22.1, 30, 60, 300), (22.2, 30, 150, 300), (23.5, 30, 150, 300),
                (23.6, 30, 60, 300), (25.0, 30, 60, 300), (25.1, 40, 180, 300), (27.5, 40, 180, 300)]
    return c, cam_at(keys, t), shake


def music(track):
    g = lambda a, b, *x, **k: audio.groove(track, a * K, b * K, *x, **k)
    g(0, 6.9, 132, "min", mel="b")
    g(6.9, 11.9, 110, "maj", layers=("bass", "pad", "arp", "drums"))        # oficina
    g(11.9, 14.2, 150, "maj", layers=("bass", "pad", "arp", "lead", "drums"), mel="b")
    g(14.2, 20.4, 100, "min", layers=("bass", "pad", "arp", "drums"), vol=0.9)
    g(20.4, 27.5, 142, "maj", mel="b")
    g(27.5, T, 132, "min", bar0=2)
    for a, b, kind in ((0, 6.9, "room"), (6.9, 14.2, "room"), (14.2, 20.4, "room"), (20.4, 27.5, "street"), (27.5, T, "room")):
        audio.ambient(track, a * K, b * K, kind, 1.0)


def sfx(track):
    A = audio
    A.airhorn(track, 0.0); A.hit(track, 0.0)
    A.notify(track, 0.2 * K); A.scratch(track, 3.6 * K)
    A.step(track, 6.95 * K); A.hit(track, 6.9 * K)
    for k in range(18):
        A.click(track, (7.4 + 0.18 * k) * K)                                    # teclado
    A.notify(track, 8.9 * K); A.trombone(track, 10.4 * K)
    A.powerup(track, 12.0 * K); A.sparkle(track, 12.3 * K)
    A.notify(track, 14.3 * K)
    A.scratch(track, 17.3 * K)
    for k in range(6):
        A.coin(track, (20.7 + 0.18 * k) * K, 0.1)                               # cobra
    A.levelup(track, 20.7 * K)
    A.crowd(track, 25.1 * K, 1.2, 0.14); A.jingle(track, 25.1 * K); A.airhorn(track, 25.1 * K, 0.12); A.sparkle(track, 25.2 * K)
    A.rimshot(track, 27.6 * K)
    A.roll(track, T * K - 1.3, T * K)


PUNCHES = [(c * K, 6) for c in CUTS] + [(a * K, 2.5) for a, _, _, _ in LINES]
EP = dict(
    T=T * K, hooks=HOOKS, cuts=[c * K for c in CUTS], voices=VOICES, punches=PUNCHES,
    lines=[(a * K, b * K, w, x) for a, b, w, x in LINES],
    frame=lambda t: frame(t / K), hud=lambda t: hud(t / K), banner=lambda t: banner(t / K),
    music=music, sfx=sfx, meta=META)
