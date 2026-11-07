"""«Qué pasaría si la directora, los maestros y casi toda la escuela se enteran de que mi bro es el dueño de Curis?»
Elenco nuevo: Nico (Colombia), Sofi (Perú), Tomi (Uruguay), Directora Vega y Profe Ramos. Humor sano: memes con cariño."""
import math

from .. import audio, scenes2 as S2
from ..bg import light_shaft, sparkles, confetti, emote, speed_lines
from ..engine import cam_at
from ..sprite import draw_char
from . import bro_juega_bien as B
from .bro_juega_bien import char, sm

K = 1.15
T = 38.625 / K                 # 38.625 s = 927 fotogramas exactos
CUTS = [7.2, 13.4, 19.6, 24.2, 30.4]
META = dict(id="curis-escuela", category="amistad",
            title="¿Qué pasaría si la directora, los maestros y casi toda la escuela se enteran de que mi bro es dueño de Curis?",
            caption_hook="Cuando la directora, los profes y toda la escuela descubren que tu bro es el dueño de Curis 😳")

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
    "vega": dict(label="DIRECTORA VEGA", color=(214, 160, 240), pitch=300),
    "ramos": dict(label="PROFE RAMOS", color=(170, 226, 150), pitch=150),
    "todos": dict(label="TODOS", color=(255, 255, 255), pitch=250),
}
LINES = [
    (0.1, 2.0, "vega", "¡Atención! ¡Ya sé quién es Curis!"),
    (2.1, 3.4, "sofi", "¡Ay no! ¿Quién será, pues?"),
    (3.5, 4.9, "tomi", "¡Seguro fue Nico, bo!"),
    (5.0, 6.3, "nico", "¿Yo? ¡Qué va, parce!"),
    (6.4, 7.1, "vega", "¡Nicolás, a dirección!"),
    (7.4, 8.8, "vega", "Siéntese, joven. ¿Usted es Curis?"),
    (8.9, 10.3, "nico", "Fue con cariño, señora…"),
    (10.4, 11.9, "vega", "Aquí tengo todos sus memes."),
    (12.0, 13.3, "vega", "Y los profes… se mueren de risa."),
    (13.6, 15.0, "ramos", "¡Jajaja! ¿Ese soy yo roncando?"),
    (15.1, 16.4, "nico", "¿Me va a castigar, profe?"),
    (16.5, 18.0, "ramos", "¿Castigarte? ¡Hazme otro, pues!"),
    (18.1, 19.5, "vega", "Desde hoy, Curis es OFICIAL."),
    (19.8, 21.0, "sofi", "¡Llegó la notificación! ¡Es oficial!"),
    (21.1, 22.4, "tomi", "¡Todo el cole lo sabe, bo!"),
    (22.5, 24.0, "nico", "¡Qué pena, parce!"),
    (24.4, 26.0, "vega", "¡Un aplauso para el creador de Curis!"),
    (26.1, 27.4, "todos", "¡NI-CO! ¡NI-CO!"),
    (27.5, 29.0, "nico", "Gracias… ¡y ya subí el siguiente!"),
    (29.1, 30.3, "todos", "¡PUBLÍCANOS!"),
]
HOOKS = [(0.0, 1.7, "LA DIRECTORA ENCONTRÓ A «CURIS DEL COLE»…"), (1.7, 2.9, "¡Y ES MI BRO!")]
B.LINES_ACTIVE[0] = LINES


def hud(t):
    if t >= 30.4 or t < 7.2:
        ent = "1" if t < 7.2 or t >= 30.4 else ""
    elif t < 13.4:
        ent = "2"
    elif t < 19.6:
        ent = "5"
    elif t < 24.2:
        ent = "500"
    else:
        ent = "TODOS"
    ner = 100 if (t < 13.4 or t >= 30.4) else (70 if t < 19.6 else (40 if t < 24.2 else 0))
    return [("ENTERADOS", ent), ("NERVIOS", f"{ner}%")]


def banner(t):
    if 13.4 <= t < 14.3:
        return "SALA DE PROFES…"
    if 19.6 <= t < 20.6:
        return "MIENTRAS TANTO…"
    if 24.2 <= t < 25.2:
        return "¡FERIA DEL COLE!"
    return ""


def patio_scene(t, te, lt, c=None):
    """Patio con multitud (escena inicial = escena del bucle)."""
    c = S2.finish(S2.room2(te, "patio"))
    light_shaft(c, 12)
    S2.crowd(c, te, 300, step=30, seed=2, phones=True)
    S2.crowd(c, te, 322, x0=5, step=34, seed=5, phones=True)
    char(c, te, "vega", x=120, feet=318, expr="angry", pose="point" if lt > 1.0 and lt < 6.4 else "fist", fx=("vein",) if lt < 2 else (), shake=1)
    S2.podium(c, 120, 334)
    char(c, te, "tomi", x=40, feet=352, expr="shock", pose="down", flip=True)
    char(c, te, "nico", x=225, feet=352, expr="shy", pose="down", fx=("sweat",), look=-1)
    char(c, te, "sofi", x=300, feet=352, expr="shock", pose="phone")
    if 0.12 < lt < 0.9:
        speed_lines(c, 120, 240, te, int(100 * (1 - (lt - 0.12) / 0.78)))
    if 0.3 < lt < 1.5:
        emote(c, 300, 196, "!", lt - 0.3)
    return c


def frame(t):
    shake = 0
    te = t if t < 30.4 else t - T
    if t < 7.2:
        c = patio_scene(t, t, t)
        keys = [(0, 40, 180, 290), (2.0, 36, 120, 280), (2.1, 28, 300, 268), (3.4, 28, 300, 268), (3.5, 28, 50, 268),
                (4.9, 28, 50, 268), (5.0, 28, 225, 268), (6.3, 28, 225, 268), (6.4, 30, 120, 270), (7.2, 34, 120, 280)]
    elif t < 13.4:
        c = S2.finish(S2.room2(t, "oficina"))
        char(c, t, "vega", x=170, feet=300, expr="angry" if t < 12 else "happy", pose="phone" if t > 10.4 else "down")
        # frente del escritorio (tapa las piernas: ella está sentada)
        from PIL import ImageDraw
        d = ImageDraw.Draw(c)
        d.rectangle([54, 218, 282, 234], fill=(30, 18, 34)); d.rectangle([56, 220, 280, 232], fill=(196, 136, 84))
        d.rectangle([60, 234, 276, 300], fill=(132, 84, 56)); d.rectangle([60, 234, 276, 238], fill=(96, 60, 42))
        for dx in (72, 174):
            d.rectangle([dx, 246, dx + 90, 292], outline=(96, 60, 42), width=2); d.rectangle([dx + 38, 264, dx + 54, 270], fill=(250, 214, 90))
        d.rectangle([150, 222, 206, 228], fill=(250, 214, 90)); S2.txt(d, (178, 225), "DIRECCION", 9, (30, 18, 34), outline=(250, 214, 90))
        char(c, t, "nico", x=250, feet=352, expr="shy" if t < 12 else "shock", pose="down", fx=("sweat",), look=-1)
        if t > 12.0:
            emote(c, 250, 196, "?", t - 12.0)
        keys = [(7.2, 40, 180, 290), (7.4, 30, 170, 262), (8.8, 30, 170, 262), (8.9, 30, 250, 268), (10.3, 30, 250, 268),
                (10.4, 28, 170, 255), (13.4, 26, 170, 255)]
    elif t < 19.6:
        c = S2.finish(S2.room2(t, "staff"))
        light_shaft(c, 12)
        laugh = 13.6 <= t < 15.0
        char(c, t, "ramos", x=95, feet=352, expr="happy" if t < 16.4 or t >= 16.5 else "happy", pose="phone",
             hop=5 if laugh else 0, shake=1 if laugh else 0)
        char(c, t, "vega", x=175, feet=352, expr="happy", pose="phone", hop=3 if t < 15 else 0, flip=True)
        char(c, t, "nico", x=262, feet=352, expr="shy" if t < 16.5 else "happy", pose="down", fx=("sweat",) if t < 16.5 else (), look=-1)
        if 15.1 < t < 16.3:
            emote(c, 262, 196, "?", t - 15.1)
        if t >= 18.1:
            sparkles(c, t, 175, 262, 7, 110)
        keys = [(13.4, 40, 180, 290), (13.6, 28, 95, 268), (15.0, 28, 95, 268), (15.1, 28, 262, 268), (16.4, 28, 262, 268),
                (16.5, 28, 95, 268), (18.0, 28, 95, 268), (18.1, 28, 175, 268), (19.6, 32, 175, 272)]
    elif t < 24.2:
        c = S2.finish(S2.room2(t, "hall"))
        S2.walkers(c, t, 332, ["s1", "s4", "s7", "s2", "s5"], speed=50)
        S2.crowd(c, t, 310, step=46, seed=9, phones=True, jump=1.0 if t > 20.4 else 0.2)
        light_shaft(c, 12)
        char(c, t, "sofi", x=70, feet=360, expr="shock" if t < 21.1 else "happy", pose="phone", hop=4 if t > 21 else 0)
        char(c, t, "tomi", x=150, feet=360, expr="happy", pose="phone", flip=True, hop=4 if t > 21.1 else 0)
        char(c, t, "nico", x=270, feet=360, expr="shy" if t < 22.5 else "happy", pose="down", fx=("sweat",) if t < 22.5 else (), look=-1)
        if 19.8 < t < 21.2:
            emote(c, 70, 204, "!", t - 19.8)
        keys = [(19.6, 40, 180, 290), (19.8, 28, 70, 268), (21.0, 28, 70, 268), (21.1, 28, 150, 268), (22.4, 28, 150, 268),
                (22.5, 28, 270, 268), (24.2, 40, 180, 290)]
    elif t < 30.4:
        c = S2.finish(S2.room2(t, "stage"))
        S2.beams(c, t)
        light_shaft(c, 8)
        char(c, t, "vega", x=95, feet=300, expr="happy", pose="cheer" if t < 26 else "point", hop=3)
        char(c, t, "ramos", x=268, feet=300, expr="happy", pose="phone", hop=2)
        char(c, t, "nico", x=180, feet=330, expr="shy" if t < 27.5 else "happy", pose="down" if t < 29.1 else "cheer", fx=("sweat",) if t < 27.5 else (), hop=4 if t >= 29.1 else 0)
        S2.crowd(c, t, 500, x0=-4, x1=380, step=54, seed=4, jump=1.0 if t > 26.1 else 0.4, scale=2)
        if t >= 26.1:
            confetti(c, t)
        if t > 27.5:
            sparkles(c, t, 180, 262, 8, 120)
        keys = [(24.2, 40, 180, 290), (24.4, 30, 100, 262), (26.0, 30, 100, 262), (26.1, 40, 180, 290), (27.4, 40, 180, 290),
                (27.5, 28, 180, 270), (29.0, 28, 180, 270), (29.1, 40, 180, 290), (30.4, 40, 180, 290)]
    else:
        c = patio_scene(t, te, 0.0)
        keys = [(30.4, 40, 180, 290), (T, 40, 180, 290)]
    return c, cam_at(keys, t), shake


def music(track):
    g = lambda a, b, *x, **k: audio.groove(track, a * K, b * K, *x, **k)
    g(0, 7.2, 132, "min", mel="b")
    g(7.2, 13.4, 104, "min", layers=("bass", "pad", "arp", "drums"))        # dirección: tensión
    audio.riser(track, 10.4 * K, 13.3 * K)
    g(13.4, 19.6, 120, "maj", layers=("bass", "pad", "arp", "lead", "drums"), vol=0.9)   # los profes ríen
    g(19.6, 24.2, 146, "maj", mel="b")                                      # pasillo: todos se enteran
    g(24.2, 30.4, 140, "maj")                                               # feria
    g(30.4, T, 132, "min", bar0=2)                                          # bucle: compases 3-4 -> 1
    for a, b, kind in ((0, 7.2, "street"), (7.2, 13.4, "room"), (13.4, 19.6, "room"), (19.6, 24.2, "street"), (24.2, 30.4, "arcade"), (30.4, T, "street")):
        audio.ambient(track, a * K, b * K, kind, 1.0)


def sfx(track):
    A = audio
    A.airhorn(track, 0.0); A.hit(track, 0.0)
    A.crowd(track, 0.2 * K, 1.2, 0.1); A.notify(track, 0.3 * K); A.crowd(track, 2.0 * K, 0.8, 0.08)
    A.scratch(track, 6.4 * K)
    for k in range(6):
        A.step(track, (6.6 + 0.5 * k) * K, 0.1)                                  # puertas y pasos hacia dirección
    A.hit(track, 7.4 * K)
    for k in range(4):
        A.click(track, (10.4 + 0.2 * k) * K)
    A.notify(track, 10.5 * K); A.sparkle(track, 12.0 * K)
    for k in range(5):
        A.coin(track, (13.6 + 0.2 * k) * K, 0.06)                                # risas / cascabeles
    A.sparkle(track, 18.1 * K); A.levelup(track, 18.2 * K)
    for k in range(12):
        A.notify(track, (19.8 + 0.12 * k) * K, 0.08)                             # todos los celulares suenan
    A.crowd(track, 21.1 * K, 1.2, 0.12); A.powerup(track, 24.2 * K)
    A.crowd(track, 24.6 * K, 1.5, 0.16); A.airhorn(track, 26.1 * K, 0.12); A.jingle(track, 26.1 * K); A.sparkle(track, 29.1 * K)
    A.rimshot(track, 30.5 * K)
    A.roll(track, T * K - 1.3, T * K)


PUNCHES = [(c * K, 6) for c in CUTS] + [(a * K, 2.5) for a, _, _, _ in LINES]
EP = dict(
    T=T * K, hooks=HOOKS, cuts=[c * K for c in CUTS], voices=VOICES, punches=PUNCHES,
    lines=[(a * K, b * K, w, x) for a, b, w, x in LINES],
    frame=lambda t: frame(t / K), hud=lambda t: hud(t / K), banner=lambda t: banner(t / K),
    music=music, sfx=sfx, meta=META)
