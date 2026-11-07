"""«¿Qué pasaría si descubrieran que mi bro es el dueño de la cuenta de curis del cole?» — amistad/escuela.
Cuenta de «curis» = cuenta anónima de memes/chismes del colegio. Aquí es humor sano: memes cariñosos, nada de acoso."""
import math

from PIL import Image

from .. import audio
from ..bg import room, light_shaft, sparkles, confetti, emote, speed_lines
from ..engine import cam_at
from .bro_juega_bien import VOICES, FLAGS, char, SEAT, FEET, sm
from . import bro_juega_bien as B

META = dict(id="curis-del-cole", category="amistad",
            title="¿Qué pasaría si descubrieran que mi bro es el dueño de la cuenta de curis del cole?",
            caption_hook="Cuando descubren que tu bro es el dueño de la cuenta de curis del cole 👀")
K = 1.2
T = 30.4167                  # x1.2 = 36.5 s = 876 fotogramas exactos
CUTS = [7.4, 13.0, 19.0, 27.4]

LINES = [
    (0.1, 2.0, "chuy", "¡No manches, otro post de Curis!"),
    (2.1, 3.6, "nati", "Che, dice que Memo se durmió en mate."),
    (3.7, 5.0, "memo", "¡Fue meditación, chamo!"),
    (5.1, 6.4, "chuy", "¡Voy a encontrar al dueño, güey!"),
    (6.5, 7.3, "bro", "Qué fome… jeje."),
    (7.6, 9.0, "nati", "Posteó a las 3:07 de la mañana."),
    (9.1, 10.5, "memo", "Y siempre firma «sin estrés»."),
    (10.6, 12.0, "chuy", "Solo un bro dice «sin estrés»…"),
    (12.1, 12.9, "todos", "¿¡BRO!?"),
    (13.2, 14.6, "bro", "Un meme más y a dormir, po."),
    (14.7, 16.0, "bro", "¡Mil seguidores! ¡Soy famoso!"),
    (16.2, 18.6, "bro", "Pero nadie sabe que soy yo, cachai."),
    (19.2, 20.4, "nati", "¡Mirá vos! ¡Es Bro!"),
    (20.5, 21.8, "chuy", "¡Tú me pusiste de payaso, güey!"),
    (21.9, 23.2, "bro", "Era con cariño, cachai…"),
    (23.3, 24.6, "memo", "Burda de bueno el meme, pana."),
    (24.7, 26.0, "chuy", "¡Órale! ¡Ponme en el próximo!"),
    (26.1, 27.3, "todos", "¡PUBLÍCANOS, BRO!"),
]
B.LINES_ACTIVE[0] = LINES
HOOKS = [(0.0, 1.7, "NADIE SABE QUIÉN ES «CURIS DEL COLE»…"), (1.7, 2.9, "¡Y ES MI BRO!")]


def hud(t):
    if t < 13.0:
        sosp = min(100, int(t / 12.1 * 100)) if t < 12.1 else 100
        fol = "???"
    elif t < 19.0:
        sosp = 0
        fol = f"{int(12 + 988 * sm((t - 13.2) / 3.0))}"
    else:
        sosp = 100
        fol = "1K"
    if t >= 27.4:
        sosp, fol = 0, "???"
    return [("SOSPECHA", f"{sosp}%"), ("SEGUIDORES", fol)]


def banner(t):
    if 13.0 <= t < 14.0:
        return "ESA NOCHE…"
    if 19.0 <= t < 20.0:
        return "¡LO DESCUBRIERON!"
    return ""


def s1(c, t, lt):
    """Patio: Chuy grita con el celular (también es la escena del bucle)."""
    light_shaft(c, 14)
    char(c, t, "chuy", expr="angry", pose="phone", fx=("vein",), shake=3 if lt < 2.3 else 1)
    char(c, t, "bro", expr="shy", pose="down", fx=("sweat",), look=-1, oy=2)
    char(c, t, "nati", expr="shock", pose="phone")
    char(c, t, "memo", expr="sad", pose="down", flip=True, fx=("sweat",) if lt > 3.7 else ())
    if 0.12 < lt < 0.9:
        speed_lines(c, SEAT["chuy"], FEET - 80, t, int(110 * (1 - (lt - 0.12) / 0.78)))
    if 0.3 < lt < 1.5:
        emote(c, *B.head("nati"), "!", lt - 0.3)


def frame(t):
    shake = 0
    te = t if t < 27.4 else t - T
    if t < 7.4:
        c = room(te, kind="patio")
        if t < 3.7:
            s1(c, t, t)
            keys = [(0, 40, 180, 290), (2.0, 36, 160, 290), (2.1, 26, 222, 268), (3.7, 24, 222, 268)]
        else:
            light_shaft(c, 14)
            char(c, t, "chuy", expr="angry", pose="phone", fx=("vein",), shake=1 if t > 5.1 else 0)
            char(c, t, "nati", expr="shock", pose="phone")
            char(c, t, "memo", expr="happy" if t < 5.0 else "sad", pose="down", flip=True)
            char(c, t, "bro", expr="shy", pose="down", fx=("sweat",), look=-1, oy=2)
            if t > 6.4:
                emote(c, *B.head("bro"), "?", t - 6.4)
            keys = [(3.7, 24, 308, 268), (5.0, 24, 308, 268), (5.1, 24, 50, 268), (6.4, 24, 50, 268), (6.5, 24, 135, 268), (7.4, 22, 135, 268)]
    elif t < 13.0:
        c = room(t, kind="phone", likes=int(t))
        if 12.1 <= t:
            emote(c, 180, 40, "!", t - 12.1)
        keys = [(7.4, 40, 180, 290), (13.0, 40, 180, 290)]
        shake = 1 if t > 12.1 else 0
    elif t < 19.0:
        lt = t - 13.0
        fol = int(12 + 988 * sm((t - 13.2) / 3.0))
        big = f"{fol/1000:.1f}K" if fol >= 1000 else str(fol)
        c = room(t, kind="bedroom", verdict="PUBLICANDO", label="SEGUIDORES", big=big, score=(1, 0))
        char(c, t, "bro", x=180, expr="happy", pose="phone", oy=round(math.sin(t * 9) * 2))
        if t > 14.6:
            sparkles(c, t, 180, 262, 7, 110)
        if 16.2 < t < 17.4:
            emote(c, *B.head("bro", 180), "!", t - 16.2)
        keys = [(13.0, 40, 180, 290), (14.6, 30, 180, 268), (16.2, 26, 180, 262), (19.0, 26, 180, 262)]
    elif t < 27.4:
        c = room(t, kind="class")
        light_shaft(c, 14)
        talk_bro = 21.9 <= t < 23.2
        a, ch_, m = (t >= 19.2), (t >= 20.5), (t >= 23.3)
        char(c, t, "chuy", expr="happy" if t >= 24.7 else ("angry" if t >= 20.5 else "shock"),
             pose="cheer" if t >= 26.1 else ("point" if 20.5 <= t < 23.3 else "phone"),
             fx=("vein",) if 20.5 <= t < 23.3 else (), hop=6 if t >= 26.1 else 0, shake=2 if 20.5 <= t < 21.9 else 0)
        char(c, t, "nati", expr="happy" if t >= 26.1 else "shock", pose="cheer" if t >= 26.1 else "phone", hop=6 if t >= 26.1 else 0)
        char(c, t, "memo", expr="happy" if t >= 23.3 else "shock", pose="cheer" if t >= 26.1 else "down", flip=True, hop=6 if t >= 26.1 else 0)
        char(c, t, "bro", expr="happy" if t >= 26.1 else "shy", pose="cheer" if t >= 26.1 else "down",
             fx=("sweat",) if t < 24.7 else (), look=-1 if t < 24.7 else 0, hop=6 if t >= 26.1 else 0)
        if 19.2 < t < 20.4:
            emote(c, *B.head("bro"), "!", t - 19.2)
        if t >= 26.1:
            confetti(c, t)
        keys = [(19.0, 40, 180, 290), (19.2, 28, 135, 296), (20.4, 28, 135, 296), (20.5, 26, 50, 296), (21.8, 26, 50, 296),
                (21.9, 24, 135, 296), (23.2, 24, 135, 296), (23.3, 26, 308, 296), (24.6, 26, 308, 296),
                (24.7, 26, 50, 296), (26.0, 26, 50, 296), (26.1, 40, 180, 290), (27.4, 40, 180, 290)]
    else:
        c = room(te, kind="patio")
        s1(c, te, 0.0)
        keys = [(27.4, 40, 180, 290), (T, 40, 180, 290)]
    return c, cam_at(keys, t), shake


def music(track):
    g = lambda a, b, *x, **k: audio.groove(track, a * K, b * K, *x, **k)
    g(0, 7.4, 132, "min", mel="b")                                              # persecución de chisme
    g(7.4, 13.0, 112, "min", layers=("bass", "pad", "arp", "drums"))            # detectives
    audio.riser(track, 10.6 * K, 12.9 * K)
    g(13.0, 19.0, 96, "maj", layers=("bass", "pad", "arp", "lead"), vol=0.9, mel="b")   # cuarto: lo-fi alegre
    g(19.0, 27.4, 140, "maj", mel="b")                                          # revelación y fiesta
    g(27.4, T, 132, "min", bar0=2)                                              # compases 3-4 -> 1: bucle musical
    for a, b, kind in ((0, 7.4, "street"), (7.4, 13.0, "room"), (13.0, 19.0, "bedroom"), (19.0, 27.4, "room"), (27.4, T, "street")):
        audio.ambient(track, a * K, b * K, kind, 1.0)


def sfx(track):
    A = audio
    A.airhorn(track, 0.0); A.hit(track, 0.0)
    A.notify(track, 0.2 * K); A.notify(track, 2.0 * K)                          # notificaciones del post
    A.crowd(track, 2.1 * K, 0.9, 0.08)
    A.scratch(track, 6.5 * K)
    for k in range(5):
        A.click(track, (7.6 + 0.2 * k) * K)
    A.notify(track, 7.4 * K); A.sparkle(track, 12.1 * K); A.scratch(track, 12.1 * K); A.hit(track, 12.1 * K)
    for k in range(40):                                                         # tecleo y likes
        A.click(track, (13.2 + 0.09 * k + 0.02 * (k % 3)) * K)
    for k in range(10):
        A.coin(track, (14.7 + 0.28 * k) * K, 0.07)
    A.levelup(track, 14.7 * K); A.levelup(track, 15.5 * K)
    A.powerup(track, 19.0 * K); A.crowd(track, 19.2 * K, 1.0, 0.1)
    A.trombone(track, 20.6 * K)
    A.jingle(track, 26.1 * K); A.crowd(track, 26.1 * K, 0.9, 0.12); A.sparkle(track, 26.2 * K)
    A.rimshot(track, 27.5 * K)
    A.roll(track, T * K - 1.3, T * K)


PUNCHES = [(c * K, 6) for c in CUTS] + [(a * K, 2.5) for a, _, _, _ in LINES]

EP = dict(
    T=T * K, hooks=HOOKS, cuts=[c * K for c in CUTS], voices=VOICES, punches=PUNCHES,
    lines=[(a * K, b * K, w, x) for a, b, w, x in LINES],
    frame=lambda t: frame(t / K), hud=lambda t: hud(t / K), banner=lambda t: banner(t / K),
    music=music, sfx=sfx, meta=META)
