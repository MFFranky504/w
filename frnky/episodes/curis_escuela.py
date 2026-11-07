"""«Yo soy Curis»: la directora se enoja con la cuenta de memes del cole y TODA la escuela se declara dueña
de la cuenta para salvar a Nico. Humor sano: nadie sale lastimado. Elenco con uniforme escolar."""
import math

from PIL import Image, ImageDraw

from .. import audio, scenes2 as S2
from ..bg import light_shaft, sparkles, confetti, emote, speed_lines, txt
from ..engine import cam_at
from ..sprite import draw_char
from . import bro_juega_bien as B
from .bro_juega_bien import char, sm

K = 1.1
T = 39.5 / K                    # 39.5 s = 948 fotogramas exactos
CUTS = [8.0, 12.45, 20.0, 32.6]
META = dict(id="curis-escuela", category="amistad",
            title="Qué pasaría si la directora quiere expulsar al dueño de la cuenta de curis y toda la escuela dice «yo soy el dueño»",
            caption_hook="Cuando la directora quiere expulsar al dueño de la cuenta de curis y toda la escuela dice «¡yo soy el dueño!» para salvar a tu bro 😭")

Y_, Bl_, R_, Wh_, SK_ = (252, 209, 22), (0, 56, 147), (206, 17, 38), (240, 240, 240), (116, 172, 223)
FLAGS = {
    "CO": [(0, 0, 1, .5, Y_), (0, .5, 1, .75, Bl_), (0, .75, 1, 1, R_)],
    "PE": [(0, 0, 1 / 3, 1, R_), (1 / 3, 0, 2 / 3, 1, Wh_), (2 / 3, 0, 1, 1, R_)],
    "UY": [(0, 0, 1, .25, Wh_), (0, .25, 1, .5, SK_), (0, .5, 1, .75, Wh_), (0, .75, 1, 1, SK_)],
}
VOICES = {
    "nico": dict(label="NICO", color=(255, 214, 90), pitch=230, flag=FLAGS["CO"]),
    "sofi": dict(label="SOFI", color=(255, 130, 130), pitch=340, flag=FLAGS["PE"]),
    "tomi": dict(label="TOMI", color=(140, 200, 255), pitch=280, flag=FLAGS["UY"]),
    "vega": dict(label="DIRECTORA", color=(214, 160, 240), pitch=300),
    "ramos": dict(label="PROFE RAMOS", color=(170, 226, 150), pitch=150),
    "todos": dict(label="TODA LA ESCUELA", color=(255, 255, 255), pitch=250),
}
LINES = [
    (0.1, 2.6, "vega", "¡LA CUENTA DE CURIS ME PUSO DE MEME!"),
    (2.7, 4.6, "vega", "¡Quien sea su dueño queda EXPULSADO!"),
    (4.7, 6.1, "tomi", "¡Uy, qué brava, bo!"),
    (6.2, 7.9, "nico", "Estoy frito, parce…"),
    (8.2, 9.8, "sofi", "¡Ese es el meme del himno!"),
    (9.9, 11.2, "tomi", "Ya lo vio todo el cole, bo."),
    (11.3, 12.4, "nico", "Ay no…"),
    (12.6, 13.9, "tomi", "¡Tengo un plan, bo!"),
    (14.0, 16.0, "tomi", "Mañana todos dicen: «¡Yo soy el dueño de la cuenta!»"),
    (16.1, 17.4, "sofi", "¿Todos? ¿Hasta el profe Ramos?"),
    (17.5, 18.7, "nico", "¿Harían eso por mí?"),
    (18.8, 19.9, "sofi", "Para eso son los bros, pues."),
    (20.2, 22.0, "vega", "¿Quién es el dueño de la cuenta de curis?"),
    (22.1, 23.4, "tomi", "¡Yo soy el dueño de la cuenta!"),
    (23.5, 24.8, "sofi", "¡Yo soy la dueña de la cuenta!"),
    (24.9, 26.5, "todos", "¡TODOS SOMOS LOS DUEÑOS!"),
    (26.6, 28.0, "ramos", "¡Yo también soy el dueño!"),
    (28.1, 29.6, "vega", "¡Basta! ¡Todos a clase!"),
    (29.7, 31.0, "nico", "Gracias, bros…"),
    (31.1, 32.4, "vega", "…Igual, el meme estuvo bueno."),
]
HOOKS = [(0.0, 1.7, "LA DIRECTORA SE ENOJÓ CON LA CUENTA DE CURIS…"), (1.7, 3.0, "¡Y TODA LA ESCUELA HIZO ESTO!")]
B.LINES_ACTIVE[0] = LINES
M = 3                      # escala de los personajes principales (antes 2: se veían chicos)
FEET = 372


def hud(t):
    if t >= 32.6 or t < 18.8:
        bros, furia = "1", 100
    elif t < 24.9:
        bros, furia = "3", 100
    elif t < 26.6:
        bros, furia = "TODOS", 60
    elif t < 28.1:
        bros, furia = "TODOS", 30
    else:
        bros, furia = "TODOS", 0
    return [("FURIA", f"{furia}%"), ("BROS", bros)]


def banner(t):
    if 12.4 <= t < 13.4:
        return "ESA TARDE, EN CLASE…"
    if 20.0 <= t < 21.0:
        return "AL DÍA SIGUIENTE…"
    if 24.9 <= t < 25.9:
        return "¡TODA LA ESCUELA!"
    return ""


def note(c, x, y, t, k):
    """Notas musicales desafinadas que salen de la directora."""
    d = ImageDraw.Draw(c)
    yy = y - ((t * 30 + k * 18) % 48)
    xx = x + math.sin(t * 5 + k) * 6
    d.ellipse([xx - 3, yy, xx + 3, yy + 5], fill=(255, 255, 255)); d.rectangle([xx + 2, yy - 10, xx + 3, yy + 2], fill=(255, 255, 255))
    d.rectangle([xx + 2, yy - 10, xx + 8, yy - 8], fill=(255, 255, 255))


def crowd(c, t, jump=0.0, phones=False, cheer=False):
    """Alumnos de uniforme en 2 filas, a escala 2 (más chicos que el elenco: profundidad)."""
    for feet, seed, step, x0 in ((296, 3, 30, 4), (334, 8, 34, 18)):
        S2.crowd(c, t, feet, x0=x0, x1=372, step=step, seed=seed, phones=phones, jump=jump, scale=2)


def patio(t, te, lt, vega_x=180):
    c = S2.finish(S2.room2(te, "patio"))
    light_shaft(c, 12)
    crowd(c, te, phones=False)
    return c


def frame(t):
    shake = 0
    te = t if t < 32.6 else t - T
    if t < 8.0 or t >= 32.6:
        lt = t if t < 8.0 else 0.0
        c = patio(t, te, lt)
        char(c, te, "vega", x=180, feet=344, scale=M, expr="angry", pose="point" if 2.7 < lt < 4.6 else "fist", fx=("red", "vein"), shake=1)
        S2.podium(c, 180, 362)
        char(c, te, "tomi", x=58, feet=FEET, scale=M, expr="shock", pose="down", flip=True)
        char(c, te, "nico", x=302, feet=FEET, scale=M, expr="shy", pose="down", fx=("sweat",), look=-1)
        if 0.12 < lt < 0.9:
            speed_lines(c, 180, 240, te, int(100 * (1 - (lt - 0.12) / 0.78)))
        if 0.3 < lt < 1.5:
            emote(c, 58, 150, "!", lt - 0.3)
        keys = [(0, 40, 180, 290), (2.6, 40, 180, 290), (2.7, 30, 180, 250), (4.6, 30, 180, 250), (4.7, 30, 58, 280),
                (6.1, 30, 58, 280), (6.2, 30, 302, 280), (7.9, 30, 302, 280), (8.0, 40, 180, 290)]
        if t >= 32.6:
            keys = [(32.6, 40, 180, 290), (T, 40, 180, 290)]
    elif t < 12.4:
        c = S2.finish(S2.room2(t, "meme"))
        sing = int(t * 6) % 2 == 0           # la directora «cantando» desafinada dentro de la foto del post
        draw_char(c, "vega", 180, 264, scale=2, expr="shock", mouth="big" if sing else "o", pose="fist")
        for k in range(3):
            note(c, 130 + k * 40, 150, t, k)
        keys = [(8.0, 40, 180, 290), (12.4, 40, 180, 290)]
    elif t < 20.0:
        c = S2.finish(S2.room2(t, "salon"))
        light_shaft(c, 12)
        char(c, t, "nico", x=64, feet=FEET, scale=M, expr="sad" if t < 17.5 else "happy", pose="down", fx=("sweat",) if t < 17.5 else ("tear",), look=1)
        char(c, t, "sofi", x=180, feet=FEET, scale=M, expr="shock" if 16.1 <= t < 17.4 else "happy", pose="down", hop=4 if t >= 18.8 else 0)
        char(c, t, "tomi", x=296, feet=FEET, scale=M, expr="happy", pose="point" if 14.0 <= t < 16.0 else "fist" if t < 14.0 else "down",
             flip=True, hop=3 if t < 14 else 0)
        if 14.0 < t < 16.0:
            sparkles(c, t, 296, 190, 5, 60)
        keys = [(12.4, 40, 180, 290), (12.6, 34, 250, 262), (16.0, 34, 250, 262), (16.1, 34, 180, 262), (17.4, 34, 180, 262),
                (17.5, 34, 110, 262), (18.7, 34, 110, 262), (18.8, 34, 180, 262), (20.0, 40, 180, 290)]
    else:
        c = patio(t, t, t - 20.0)
        full = t >= 24.9
        cheering = 22.1 <= t < 28.0
        if full and t < 28.0:     # toda la escuela salta con las manos arriba
            S2.crowd(c, t, 296, x0=4, x1=372, step=30, seed=3, jump=1.0, scale=2)
            S2.crowd(c, t, 334, x0=18, x1=372, step=34, seed=8, jump=1.0, scale=2)
        char(c, t, "vega", x=305, feet=344, scale=M,
             expr="happy" if t >= 31.1 else ("shock" if 24.9 <= t < 28.1 else "angry"),
             pose="fist" if t < 22.1 else "down", fx=("red", "vein") if t < 28.0 else (),
             shake=1 if 24.9 <= t < 28.0 else 0, flip=True)
        S2.podium(c, 305, 362)
        char(c, t, "nico", x=45, feet=FEET, scale=M, expr="shy" if t < 24.9 else "happy", pose="cheer" if 24.9 <= t < 28.0 else "down",
             fx=("sweat",) if t < 22.1 else (("tear",) if t >= 29.7 else ()), look=-1 if t < 24.9 else 0, hop=4 if 24.9 <= t < 28.0 else 0)
        char(c, t, "tomi", x=120, feet=FEET, scale=M, expr="happy" if t >= 22.1 else "shy",
             pose="fist" if 22.1 <= t < 23.5 else ("cheer" if cheering else "down"), flip=True, hop=5 if t >= 23.5 and cheering else 0)
        char(c, t, "sofi", x=195, feet=FEET, scale=M, expr="happy" if t >= 23.5 else "shy",
             pose="fist" if 23.5 <= t < 24.9 else ("cheer" if cheering else "down"), hop=5 if t >= 24.9 and cheering else 0)
        if 26.6 <= t < 28.0:
            char(c, t, "ramos", x=250, feet=FEET + 4, scale=M, expr="happy", pose="cheer", hop=5)
        if full and t < 28.0:
            confetti(c, t)
        if t >= 29.7:
            sparkles(c, t, 45, 250, 6, 90)
        keys = [(20.0, 40, 180, 290), (20.2, 30, 305, 270), (22.0, 30, 305, 270), (22.1, 30, 120, 285), (23.4, 30, 120, 285),
                (23.5, 30, 195, 285), (24.8, 30, 195, 285), (24.9, 40, 180, 290), (26.5, 40, 180, 290), (26.6, 30, 250, 285),
                (28.0, 30, 250, 285), (28.1, 30, 305, 270), (29.6, 30, 305, 270), (29.7, 30, 45, 285), (31.0, 30, 45, 285),
                (31.1, 30, 305, 270), (32.6, 30, 305, 270)]
    return c, cam_at(keys, t), shake


def music(track):
    g = lambda a, b, *x, **k: audio.groove(track, a * K, b * K, *x, **k)
    g(0, 8.0, 132, "min", mel="b")
    g(8.0, 12.4, 100, "min", layers=("bass", "pad", "arp", "drums"))
    g(12.4, 20.0, 118, "maj", layers=("bass", "pad", "arp", "lead", "drums"), vol=0.9)
    audio.riser(track, 17.5 * K, 19.9 * K)
    g(20.0, 24.9, 126, "min", layers=("bass", "pad", "arp", "drums"))
    g(24.9, 32.6, 146, "maj", mel="b")
    g(32.6, T, 132, "min", bar0=2)
    for a, b, kind in ((0, 8.0, "street"), (8.0, 12.4, "room"), (12.4, 20.0, "room"), (20.0, 32.6, "street"), (32.6, T, "street")):
        audio.ambient(track, a * K, b * K, kind, 1.0)


def sfx(track):
    A = audio
    A.airhorn(track, 0.0); A.hit(track, 0.0)
    A.crowd(track, 0.3 * K, 1.0, 0.1); A.scratch(track, 4.7 * K)
    A.notify(track, 8.1 * K)
    for k in range(3):
        A.coin(track, (8.4 + 0.5 * k) * K, 0.07)
    A.click(track, 11.5 * K); A.hit(track, 11.3 * K)
    A.powerup(track, 12.4 * K)
    for k in range(5):
        A.click(track, (14.2 + 0.2 * k) * K)
    A.sparkle(track, 17.6 * K); A.levelup(track, 18.8 * K)
    A.step(track, 20.1 * K)
    A.crowd(track, 22.1 * K, 1.0, 0.1); A.jingle(track, 22.1 * K)
    A.airhorn(track, 24.9 * K, 0.14); A.crowd(track, 24.9 * K, 1.8, 0.2); A.jingle(track, 25.0 * K)
    A.trombone(track, 28.1 * K); A.sparkle(track, 29.7 * K)
    A.rimshot(track, 32.7 * K)
    A.roll(track, T * K - 1.3, T * K)


PUNCHES = [(c * K, 6) for c in CUTS] + [(a * K, 2.5) for a, _, _, _ in LINES]
EP = dict(
    T=T * K, hooks=HOOKS, cuts=[c * K for c in CUTS], voices=VOICES, punches=PUNCHES,
    lines=[(a * K, b * K, w, x) for a, b, w, x in LINES],
    frame=lambda t: frame(t / K), hud=lambda t: hud(t / K), banner=lambda t: banner(t / K),
    music=music, sfx=sfx, meta=META)
