"""«¿Qué pasaría si mi bro finalmente jugara bien?» — amistad. Bucle: el final regresa al primer plano."""
import math

from PIL import Image, ImageDraw

from .. import audio
from ..bg import room, light_shaft, sparkles, confetti, emote, speed_lines, boom
from ..engine import cam_at
from ..sprite import draw_char

META = dict(id="bro-juega-bien", category="amistad",
            title="¿Qué pasaría si mi bro finalmente jugara bien?",
            caption_hook="Cuando tu bro por fin juega bien… y deja de ser tu bro 💀")
K = 1.2                      # estiramiento del tiempo base -> real
T = 32.6                     # duración base
# Escenas (tiempo base): sala 0-8 · calle 8-11 · cuarto 11-16 · ciber 16-27.8 · sala 27.8-30.4 · repetición 30.4-T
CUTS = [8.0, 11.0, 16.0, 22.0, 27.8, 29.5, 30.4]

G, Wh, R_, Y, B, SK = (0, 104, 71), (240, 240, 240), (206, 17, 38), (252, 209, 22), (0, 56, 147), (116, 172, 223)
FLAGS = {
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
    (3.7, 5.2, "nati", "Che, ¿agarrás el control o lo abrazás?"),
    (5.3, 6.4, "bro", "Es que me sudan las manos, po…"),
    (6.5, 7.9, "chuy", "¡Estás fuera del equipo, güey!"),
    (8.3, 9.5, "bro", "Qué fome, cachai…"),
    (9.6, 10.9, "bro", "Hoy me vuelvo bueno."),
    (14.7, 15.9, "bro", "Ya entendí el juego, po."),
    (17.2, 18.3, "nati", "¡Mirá vos, 25 y 0! ¡Qué bestia!"),
    (18.4, 19.3, "chuy", "¡Órale, ese es mi bro!"),
    (19.4, 20.3, "memo", "¡Burda de bueno, pana!"),
    (20.4, 21.9, "bro", "Cállense, bots. Me atrasan."),
    (22.4, 23.6, "memo", "¿Qué le pasó a mi bro, chamo?"),
    (23.7, 25.4, "bro", "Chuy, ¿ese fue tu mejor intento? Qué fome."),
    (25.5, 26.6, "nati", "Era más feliz perdiendo, che…"),
    (26.7, 27.6, "chuy", "Neta, qué gacho."),
    (28.0, 29.4, "bro", "¿Mejor volvemos a ser malos?"),
    (29.5, 30.4, "todos", "¡ESE ES MI BRO!"),
]
SEAT = dict(chuy=50, bro=135, nati=222, memo=308)
FEET = 352
PRO = dict(expr="smug", shades=True, headset=True, shirt=(34, 34, 46))


def speaking(t):
    for t0, t1, who, _ in LINES:
        if t0 <= t < t1:
            return who.split("+")
    return []


def sm(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def char(c, t, name, x=None, shake=0, scale=2, feet=FEET, hop=0, **kw):
    sp = speaking(t)
    talking = (name in sp or "todos" in sp) and int(t * 7) % 2 == 0
    expr = kw.get("expr", "neutral")
    if talking:
        kw["mouth"] = "big" if expr == "happy" else ("o" if expr == "shock" else "open")
    x = SEAT[name] if x is None else x
    ox = round(math.sin(t * 61) * shake) if shake else 0
    oy = round(math.sin(t * 5 + x) * 1.5) + kw.pop("oy", 0)
    if hop:
        oy -= round(abs(math.sin(t * 9 + x)) * hop)
    draw_char(c, name, x, feet, ox=ox, oy=oy, scale=scale, **kw)


def head(name, x=None):
    return (SEAT[name] if x is None else x, FEET - 156)


def hud(t):
    lvl = 1
    if 11.0 <= t < 28.8:
        lvl = 1 if t < 12.2 else (25 if t < 13.0 else (60 if t < 13.8 else 99))
    vibe = 100
    if t < 8.0:
        vibe = max(0, round(100 - 100 * min(1, t / 6.5)))
    elif t < 16.0:
        vibe = 0
    elif t < 20.4:
        vibe = 100
    elif t < 27.8:
        vibe = max(0, round(100 - 100 * (t - 20.4) / 6.0))
    elif t < 29.5:
        vibe = 0
    return lvl, vibe


def banner(t):
    if 8.1 <= t < 9.2:
        return "ESPERA EL FINAL…"
    if 11.0 <= t < 12.2:
        return "ESA NOCHE…"
    if 12.2 <= t < 14.6:
        return f"DÍA {1 if t < 13.0 else (2 if t < 13.8 else 3)}"
    if 16.2 <= t < 17.4:
        return "REGRESÓ… DIFERENTE"
    if 22.2 <= t < 23.4:
        return "SE LE SUBIÓ A LA CABEZA"
    return ""


def s1(c, t, lt):
    """Escena inicial (también la del bucle final): Chuy grita, todos reaccionan."""
    light_shaft(c)
    char(c, t, "chuy", expr="angry", pose="fist", fx=("vein",), shake=3 if lt < 2.3 else 1)
    char(c, t, "bro", expr="sad", fx=("tear",), look=-1, oy=4)
    char(c, t, "nati", expr="shock", fx=("sweat",), pose="ctrl")
    char(c, t, "memo", expr="happy", pose="down", flip=True, hop=3 if lt > 2.2 else 0)
    if 0.12 < lt < 0.9:   # líneas de impacto que aparecen y se desvanecen (el primer y el último fotograma quedan limpios)
        speed_lines(c, SEAT["chuy"], FEET - 80, t, int(170 * (1 - (lt - 0.12) / 0.78)))
    if 0.3 < lt < 1.5:
        emote(c, *head("nati"), "!", lt - 0.3)


def frame(t):
    shake = 0
    if t < 8.0:
        sc = dict(score=(0, 14), verdict="DERROTA")
    elif t < 11.0:
        sc = dict(kind="street")
    elif t < 16.0:
        dn = 0 if t < 12.2 else (1 if t < 13.0 else (2 if t < 13.8 else 3))
        sc = dict(kind="bedroom", cans_n=[0, 3, 8, 14][dn], verdict="PRÁCTICA", score=[(3, 9), (3, 9), (12, 5), (20, 1)][dn])
    elif t < 27.8:
        sc = dict(kind="arcade", score=(25, 0), verdict="VICTORIA")
    elif t < 29.5:
        sc = dict(score=(0, 14), verdict="DERROTA") if t > 28.4 else dict(score=(25, 0), verdict="VICTORIA")
    else:
        sc = dict(score=(0, 14), verdict="DERROTA")
    c = room(t, **sc)

    if t < 3.6:  # S1: el conflicto, desde el primer fotograma
        s1(c, t, t)
        keys = [(0, 40, 180, 290), (2.0, 36, 160, 290), (2.3, 26, 308, 268), (3.6, 24, 308, 268)]
        shake = 1 if t < 0.4 else 0
    elif t < 8.0:  # S2: lo corren
        light_shaft(c)
        pt = t > 6.4
        char(c, t, "chuy", expr="angry", pose="point" if pt else "ctrl", fx=("vein",), shake=2 if pt else 0)
        char(c, t, "nati", expr="angry" if t < 5.3 else "shock", pose="point" if pt else "ctrl", flip=pt)
        char(c, t, "memo", expr="angry", pose="point" if pt else "down", flip=True)
        char(c, t, "bro", expr="sad", fx=("tear", "sweat"), look=1, oy=8 if t > 5.3 else 3)
        if pt:
            emote(c, *head("bro"), "?", t - 6.4)
        keys = [(3.6, 26, 222, 268), (5.2, 26, 222, 268), (5.3, 22, 135, 268), (6.4, 22, 135, 268),
                (6.5, 40, 180, 290), (8.0, 34, 150, 296)]
        shake = 2 if pt else 0
    elif t < 11.0:  # calle: Bro se va caminando y se promete mejorar
        lt = t - 8.0
        x = 40 + 150 * sm(lt / 1.9)
        walking = lt < 1.9
        w = (1 + int(t * 6) % 2) if walking else 0
        char(c, t, "bro", x=x, expr="sad" if lt < 1.8 else "angry", pose="down" if lt < 2.0 else "fist", walk=w,
             oy=-round(abs(math.sin(t * 12)) * 3) if walking else 0, feet=396 - 44,
             fx=("sweat",) if lt < 1.8 else ())
        if lt >= 1.9:
            speed_lines(c, x, 230, t, 120)
            sparkles(c, t, x, 230, 6, 100)
        keys = [(8.0, 40, 100, 290), (9.6, 36, 170, 290), (9.7, 24, 190, 268), (11.0, 22, 190, 268)]
    elif t < 16.0:  # cuarto: entrenamiento
        dn = 0 if t < 12.2 else (1 if t < 13.0 else (2 if t < 13.8 else 3))
        expr = ["neutral", "angry", "angry", "shock"][dn]
        char(c, t, "bro", x=180, expr=expr, pose="ctrl", bags=dn >= 2, fx=("sweat",) if dn >= 2 else (),
             shake=1 if dn >= 2 else 0, oy=round(math.sin(t * 14) * (1 + dn)))
        if dn:
            sparkles(c, t, 180, 262, 7, 110)
        if dn == 3:
            speed_lines(c, 180, 250, t, 100)
        keys = [(11.0, 40, 180, 290), (12.2, 30, 180, 260), (14.6, 22, 180, 268), (16.0, 20, 180, 268)]
        shake = 1 if dn >= 2 else 0
    elif t < 27.8:  # ciber: vuelve "pro" y se pone insoportable
        light_shaft(c, 18)
        lt = t - 16.0
        walk = sm(lt / 1.0)
        bx = -40 + (SEAT["bro"] + 40) * walk
        w = (1 + int(t * 7) % 2) if walk < 1 else 0
        bob = -round(abs(math.sin(t * 12)) * 5) if walk < 1 else 0
        if t < 22.0:
            char(c, t, "nati", expr="happy", pose="cheer" if t < 19.4 else "ctrl", hop=6 if t < 19.4 else 0)
            char(c, t, "chuy", expr="happy", pose="cheer" if t < 19.4 else "ctrl", hop=6 if t < 19.4 else 0)
            char(c, t, "memo", expr="happy", pose="cheer" if 19.4 <= t < 21.0 else "down", flip=True,
                 hop=6 if 19.4 <= t < 21.0 else 0)
            char(c, t, "bro", x=bx, oy=bob, pose="ctrl", walk=w, **PRO)
            if 17.2 < t < 18.0:
                emote(c, *head("nati"), "love", t - 17.2)
            if 20.4 <= t < 21.0:
                speed_lines(c, SEAT["bro"], FEET - 80, t)
                boom(c, SEAT["bro"], FEET - 175, "¡ZAS!", t - 20.4)
            if t > 17.0:
                sparkles(c, t, SEAT["bro"], 262, 6, 100)
            keys = [(16.0, 40, 180, 290), (17.1, 40, 180, 290), (17.2, 30, 222, 270), (18.3, 30, 222, 270),
                    (18.4, 28, 50, 265), (19.3, 28, 50, 265), (19.4, 28, 308, 265), (20.3, 28, 308, 265),
                    (20.4, 20, 135, 268), (22.0, 22, 135, 268)]
        else:
            char(c, t, "chuy", expr="sad", fx=("tear",), oy=4 if t > 23.7 else 0, pose="down")
            char(c, t, "nati", expr="sad" if t > 25.5 else "shock", pose="down")
            char(c, t, "memo", expr="shock", fx=("sweat",), pose="down", flip=True)
            char(c, t, "bro", pose="ctrl", **PRO)
            sparkles(c, t, SEAT["bro"], 262, 6, 100)
            if 22.4 < t < 23.4:
                emote(c, *head("memo"), "?", t - 22.4)
            keys = [(22.0, 26, 308, 268), (23.6, 26, 308, 268), (23.7, 22, 135, 268), (25.4, 22, 135, 268),
                    (25.5, 26, 222, 268), (26.6, 26, 222, 268), (26.7, 26, 50, 268), (27.8, 24, 50, 268)]
    elif t < 29.5:  # sala: se arrepiente
        light_shaft(c)
        gone = t > 28.4
        for n_ in ("chuy", "nati", "memo"):
            char(c, t, n_, expr="shock", pose="down", flip=(n_ == "memo"))
        char(c, t, "bro", expr="shy", pose="down" if gone else "ctrl", look=-1, shirt=(34, 34, 46))
        if t > 28.0:
            emote(c, *head("bro"), "?", t - 28.0)
        keys = [(27.8, 22, 135, 268), (29.5, 24, 135, 268)]
    elif t < 30.4:  # todos felices
        light_shaft(c)
        for n_ in ("chuy", "nati", "bro", "memo"):
            char(c, t, n_, expr="happy", pose="cheer", flip=(n_ == "memo"), hop=8)
        confetti(c, t)
        keys = [(29.5, 40, 180, 290), (30.4, 36, 180, 290)]
        shake = 1 if t < 29.9 else 0
    else:  # BUCLE: todo vuelve a la escena inicial (misma cámara, mismos gestos)
        s1(c, t, t - 30.4) if t < 31.6 else s1(c, t, 0.0)
        keys = [(30.4, 40, 180, 290), (T, 40, 180, 290)]
    return c, cam_at(keys, t), shake


def music(track):
    g = lambda a, b, *x, **k: audio.groove(track, a * K, b * K, *x, **k)
    g(0, 5.3, 132, "min")
    g(5.3, 6.4, 132, "min", layers=("pad",), vol=0.9)                           # momento triste
    g(6.4, 8.0, 132, "min", layers=("bass", "pad", "arp", "drums", "lead"), mel="b")
    g(8.0, 11.0, 88, "min", layers=("bass", "pad", "lead"), vol=0.9, mel="b")   # calle: melancólica
    g(11.0, 16.0, 148, "min", layers=("bass", "pad", "arp", "drums"))           # entrenamiento
    audio.riser(track, 12.2 * K, 15.9 * K)
    g(16.0, 22.0, 140, "maj", mel="b")                                          # ciber: victoria
    g(22.0, 27.8, 140, "min", layers=("bass", "pad"), vol=0.75)                 # incómodo
    g(27.8, 29.5, 140, "min", layers=("pad",), vol=0.6)
    g(29.5, 30.4, 140, "maj")
    g(30.4, T, 132, "min")                                                      # vuelve el groove del inicio
    for a, b, kind in ((0, 8, "room"), (8, 11, "street"), (11, 16, "bedroom"), (16, 27.8, "arcade"), (27.8, T, "room")):
        audio.ambient(track, a * K, b * K, kind, 1.0)


def sfx(track):
    A = audio
    A.airhorn(track, 0.0); A.hit(track, 0.0)
    A.ding(track, 1.7)
    for k in range(7):                                    # pasos en la calle
        A.step(track, (8.2 + 0.28 * k) * K)
    A.crowd(track, 8.0 * K, 0.7, 0.05)
    A.coin(track, 12.2 * K); A.levelup(track, 12.2 * K); A.levelup(track, 13.0 * K); A.levelup(track, 13.8 * K)
    A.sparkle(track, 14.1 * K)
    for k in range(40):                                   # teclado
        A.click(track, (11.2 + 0.11 * k + 0.03 * (k % 3)) * K)
    for tt in (12.2, 13.0, 13.8):
        A.put(track, tt * K, A.noise(0.25, 0.1, 0.3))     # latita: pssht
    A.powerup(track, 16.0 * K)
    for k in range(6):
        A.step(track, (16.1 + 0.16 * k) * K)
    A.crowd(track, 17.2 * K, 1.0, 0.1); A.airhorn(track, 18.4 * K, 0.12)
    A.scratch(track, 20.4 * K); A.hit(track, 20.4 * K)
    A.trombone(track, 22.4 * K)
    A.trombone(track, 28.0 * K)
    A.jingle(track, 29.5 * K); A.crowd(track, 29.5 * K, 0.9, 0.12); A.sparkle(track, 29.6 * K)
    A.rimshot(track, 30.6 * K)
    A.roll(track, T * K - 1.3, T * K)


HOOKS = [(0.0, 1.7, "LO CORRIERON POR SER MALO…"), (1.7, 3.6, "¡Y SE VOLVIÓ DEMASIADO BUENO!")]
PUNCHES = [(c * K, 6) for c in CUTS] + [(a * K, 2.5) for a, _, _, _ in LINES]

EP = dict(
    T=T * K, hooks=HOOKS, cuts=[c * K for c in CUTS], voices=VOICES, punches=PUNCHES,
    lines=[(a * K, b * K, w, x) for a, b, w, x in LINES],
    frame=lambda t: frame(t / K), hud=lambda t: hud(t / K), banner=lambda t: banner(t / K),
    music=music, sfx=sfx, meta=META)
